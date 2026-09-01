#!/usr/bin/env python3
"""Surfaceplate - installer.

Installs, or upgrades, the standard into a target repository.

Design rules, in priority order:

1. **Never destroy the adopter's own work.** The installer owns a fixed, named set of
   files. It writes those, and nothing else. It appends to the repository's own Copilot
   instructions between markers; it never rewrites the surrounding content. It creates
   the application profile only if one does not already exist, and never overwrites it.
2. **Additive layering.** The standard owns ``.github/instructions/*.instructions.md``
   and ``.github/skills/``, which GitHub Copilot reads *in addition to* the repository's
   own ``.github/copilot-instructions.md``. That file stays the adopter's.
3. **Idempotent.** Running it twice changes nothing the second time.
4. **Honest about upgrades.** Files that the previous version installed and this version
   no longer ships are removed, so a stale control cannot linger.

Usage::

    python surfaceplate/install_standard.py --target C:\\path\\to\\repo
    python surfaceplate/install_standard.py --target ../my-repo --dry-run
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import stat
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_conformance  # noqa: E402  (needs the sys.path insert above)

VENDOR_DIR = ".standards"
PROFILE_PATH = "governance/application-profile.yaml"
COPILOT_INSTRUCTIONS = ".github/copilot-instructions.md"
# The neutral canonical instruction file DR-12 committed to and never built. Read by Codex,
# Cursor and others; Claude Code reads CLAUDE.md, so an adopter using it imports @AGENTS.md.
AGENTS_FILE = "AGENTS.md"
WORKFLOW_TARGET = ".github/workflows/standards-conformance.yml"
HOOK_TARGET = ".githooks/pre-commit"

# What each installed file IS. DR-20.
#
# The payload is kept whole deliberately - an adopter must be able to read the rules of the
# version they pinned, offline, with tamper-detection, and `core/PREREQUISITE_GATES.md` has
# changed normatively across releases. But keeping it whole has one real cost: every upgrade
# shows a 27-file diff that is mostly prose, which trains a reviewer to wave installer diffs
# through - and the same diff carries the checker. Separating the report is what makes the
# review surface honest without giving up any of the properties above.
#
# ENFORCING - code that executes. A change here changes behaviour.
# CONTRACT  - machine-parsed by the checker. A change here changes what validates.
# REFERENCE - read by people. A change here changes what the rules SAY, which matters, but
#             cannot alter what runs.
#
# The contract paths are DERIVED from the checker's own constants rather than restated: the
# checker decides which schemas it parses, and a copy here would agree on the day it was
# written and quietly stop agreeing afterwards. Same principle as DR-6.
CLASS_ENFORCING = "enforcing"
CLASS_CONTRACT = "contract"
CLASS_REFERENCE = "reference"


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Split `---` front matter from the body. Values are kept verbatim, unparsed.

    Deliberately not YAML: these files carry two scalar keys, and the emitted front matter must
    reproduce the source's quoting exactly rather than round-trip through a parser that would
    normalise it. A quoting change here would rewrite every adopter's instruction files on the
    next upgrade for no reason.
    """
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        return {}, text
    front: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            front[key.strip()] = value.strip()
    return front, match.group(2)


def payload_text(src: "Path | str") -> str:
    """A payload entry is either a file to copy or already-rendered content to write.

    Rendered entries arrived with the per-agent emitters: the same instruction body is written to
    two destinations with different front matter, so there is no single file on disk to copy.
    """
    return normalise(src if isinstance(src, str) else src.read_text(encoding="utf-8"))


def classify(rel: str) -> str:
    """Which review class an installed path belongs to."""
    if rel in (f"{VENDOR_DIR}/check_conformance.py", HOOK_TARGET, WORKFLOW_TARGET):
        return CLASS_ENFORCING
    if rel in (check_conformance.SCHEMA_PATH, check_conformance.EXCEPTION_SCHEMA_PATH):
        return CLASS_CONTRACT
    return CLASS_REFERENCE

BLOCK_BEGIN = "<!-- BEGIN SURFACEPLATE -->"
BLOCK_END = "<!-- END SURFACEPLATE -->"

DEFAULT_GRACE_DAYS = 30


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalise(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def repo_root() -> Path:
    """The package's own payload root.

    A single `.parent`, not `.parent.parent`. Before ACT-019 this file lived in `scripts/`, a
    sibling of `standard/`, `schemas/` and the rest, so finding them meant stepping out one level
    first. Since the move to `surfaceplate/`, this file lives INSIDE the payload tree, so its own
    directory already IS the payload root.

    That one-line difference is also why this needed no `importlib.resources` rewrite. `DR-10`
    flagged that "`repo_root()`...resolve[s] repository-root directories that do not exist under
    a wheel install" - true of the OLD layout, where the payload sat outside any importable
    package. Now the payload is the package: `Path(__file__).resolve().parent` resolves correctly
    for a git checkout, a normal (unpacked) `pip install`, and an editable install alike, because
    pip unpacks a wheel to real files on disk in every ordinary configuration. It does not cover a
    legacy zip-safe install - recorded as a deliberate boundary in `DR-31`, not built against a
    hypothetical no adopter has asked for.
    """
    return Path(__file__).resolve().parent


def framework_anchor(source: Path) -> str | None:
    """sha256 of the source tree's MANIFEST.sha256, or None if there is no manifest.

    DR-14's distribution-identity anchor. The manifest, not the release archive: the archive's
    digest is not reproducible, because `build_release.py` writes zip entries with their mtimes,
    so the maintainer's own tooling can only re-verify an archive it already has. The manifest is
    a pure function of tree content - one line per payload file, path-sorted, LF-forced - so its
    digest is recomputable by anyone holding the tree, on a machine that is not the adopter's.
    That was the question DR-10 set and could not answer.

    Returns None rather than raising when no manifest exists, because installing from a partial
    tree is legitimate. The checker then reports that the anchor is unverifiable, which must not
    read the same as an anchor that matched.
    """
    manifest = source / "MANIFEST.sha256"
    if not manifest.is_file():
        return None
    return sha256_text(normalise(manifest.read_text(encoding="utf-8")))


def build_payload(source: Path) -> dict[str, Path]:
    """Map target-relative path -> source file. This is the complete set of files the
    standard owns in an adopting repository."""
    payload: dict[str, Path] = {}

    # ONE BODY, SEVERAL EMITTERS (F29, DR-30). The instructions live once, agent-neutrally, in
    # standard/agent-instructions/. Each agent then receives them in the file IT ACTUALLY READS,
    # with that agent's own front-matter key for path scoping.
    #
    # This was six Copilot-format files and nothing else, so every adopter using Claude Code
    # received 501 lines of governance instruction that were never loaded - and so did this
    # repository, for its entire development. The destination is the whole point; the content
    # was never the problem.
    for path in sorted((source / "standard" / "agent-instructions").glob("*.md")):
        name = path.stem
        front, body = split_front_matter(path.read_text(encoding="utf-8"))
        scope = front.get("scope", '"**"')
        description = front.get("description", "")
        # GitHub Copilot: .github/instructions/*.instructions.md, scoped with `applyTo`.
        payload[f".github/instructions/{name}.instructions.md"] = (
            f"---\napplyTo: {scope}\ndescription: {description}\n---\n{body}"
        )
        # Claude Code: .claude/rules/*.md, scoped with `paths`. Additive by design - it cannot
        # collide with an adopter's own CLAUDE.md the way writing that file would, and rules
        # without a `paths` value load at launch with the same priority as .claude/CLAUDE.md.
        paths_block = (
            "" if scope.strip('"\' ') == "**" else f"paths:\n  - {scope}\n"
        )
        payload[f".claude/rules/surfaceplate-{name}.md"] = (
            f"---\n{paths_block}description: {description}\n---\n{body}"
        )

    for skill in sorted((source / "standard" / ".github" / "skills").iterdir()):
        if skill.is_dir() and (skill / "SKILL.md").is_file():
            payload[f".github/skills/{skill.name}/SKILL.md"] = skill / "SKILL.md"

    payload[WORKFLOW_TARGET] = source / "standard" / ".github" / "workflows" / "standards-conformance.yml"

    for hook_file in sorted((source / "standard" / ".githooks").iterdir()):
        if hook_file.is_file():
            payload[f".githooks/{hook_file.name}"] = hook_file

    # The checker travels with the standard so an adopting repository needs nothing else.
    # check_conformance.py sits beside this file now, not under a scripts/ subdirectory - the
    # ACT-019 move flattened that one level of indirection along with everything else.
    payload[f"{VENDOR_DIR}/check_conformance.py"] = source / "check_conformance.py"
    payload[f"{VENDOR_DIR}/VERSION"] = source / "VERSION"
    payload[f"{VENDOR_DIR}/conformance-block.md"] = source / "standard" / "conformance-block.md"

    # The canonical, agent-neutral copies travel too. An agent this framework has never heard of
    # can be pointed at one location instead of being told to guess which emitted form applies.
    for path in sorted((source / "standard" / "agent-instructions").glob("*.md")):
        payload[f"{VENDOR_DIR}/agent-instructions/{path.name}"] = path

    for schema in sorted((source / "schemas").glob("*.yaml")):
        payload[f"{VENDOR_DIR}/schemas/{schema.name}"] = schema
    payload[f"{VENDOR_DIR}/schemas/README.md"] = source / "schemas" / "README.md"

    for doc in sorted((source / "core").glob("*.md")):
        payload[f"{VENDOR_DIR}/core/{doc.name}"] = doc

    for template in sorted((source / "templates").iterdir()):
        if template.is_file():
            payload[f"{VENDOR_DIR}/templates/{template.name}"] = template

    for example in sorted((source / "examples").iterdir()):
        if example.is_file():
            payload[f"{VENDOR_DIR}/examples/{example.name}"] = example

    for adapter in sorted((source / "adapters").glob("*.md")):
        payload[f"{VENDOR_DIR}/adapters/{adapter.name}"] = adapter

    return payload


def verify_source(source: Path, payload: dict[str, Path]) -> list[str]:
    # Rendered entries have no file to verify - they are generated from a canonical body
    # that IS verified, under its own payload key. Checking them would look for a path that
    # was never meant to exist.
    return [
        str(src)
        for src in payload.values()
        if not isinstance(src, str) and not src.is_file()
    ]


def detect_collisions(target: Path, payload: dict[str, Path], previous: dict) -> list[str]:
    """Files that already exist at a standard-owned path but were not put there by a
    previous install of this standard.

    This matters. Both reference repositories already carry hand-written skills and
    instructions with exactly the names the standard uses. Overwriting them without
    saying so would silently delete stack-specific guidance and replace it with
    stack-neutral guidance - a regression dressed up as an installation.
    """
    already_ours = set(previous.get("files", {}))
    collisions = []
    for rel in payload:
        if rel in already_ours:
            continue
        if (target / rel).is_file():
            collisions.append(rel)
    return sorted(collisions)


def write_file(target: Path, content: str, dry_run: bool) -> bool:
    """Write only if the content differs. Returns True if a change was made."""
    if target.is_file() and normalise(target.read_text(encoding="utf-8")) == content:
        return False
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
    return True


def git(target: Path, *args: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(target), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return 127, ""
    return result.returncode, result.stdout.strip()


def git_repository_available(target: Path) -> bool:
    code, top_level = git(target, "rev-parse", "--show-toplevel")
    if code != 0 or not top_level:
        return False
    return Path(top_level).resolve() == target.resolve()


def standard_hook_path_configured(target: Path, value: str) -> bool:
    expanded = Path(os.path.expanduser(value))
    configured = expanded if expanded.is_absolute() else target / expanded
    return configured.resolve() == (target / ".githooks").resolve()


def hook_configuration_conflict(target: Path) -> str | None:
    """Return a reason installation must stop before changing hook activation."""
    if not git_repository_available(target):
        return None

    code, configured = git(target, "config", "--get", "core.hooksPath")
    if code == 0 and configured:
        if standard_hook_path_configured(target, configured):
            return None
        return (
            f"the effective core.hooksPath is already {configured!r}. Setting a repository-local "
            "path would disable the existing hook system."
        )

    code, default_hooks = git(target, "rev-parse", "--git-path", "hooks")
    if code == 0 and default_hooks:
        directory = Path(default_hooks)
        if not directory.is_absolute():
            directory = target / directory
        hooks = sorted(
            path.name
            for path in directory.iterdir()
            if path.is_file() and not path.name.endswith(".sample")
        ) if directory.is_dir() else []
        if hooks:
            return (
                f"the default Git hooks directory already contains: {', '.join(hooks)}. "
                "Configuring core.hooksPath=.githooks would disable those hooks."
            )
    return None


def configure_standard_hook(target: Path, dry_run: bool) -> tuple[bool, str]:
    """Activate the tracked hook. Returns (success, action description)."""
    if not git_repository_available(target):
        return True, "warning hook file installed, but Git hook activation was not possible"

    code, configured = git(target, "config", "--get", "core.hooksPath")
    if code == 0 and standard_hook_path_configured(target, configured):
        return True, f"keep    core.hooksPath={configured}"
    if dry_run:
        return True, "configure core.hooksPath=.githooks"

    code, _ = git(target, "config", "--local", "core.hooksPath", ".githooks")
    if code != 0:
        return False, "error: could not configure core.hooksPath=.githooks"
    return True, "configure core.hooksPath=.githooks"


def upsert_conformance_block(
    target_repo: Path, block: str, dry_run: bool, rel: str = COPILOT_INSTRUCTIONS,
    header_title: str = "Copilot instructions",
) -> str:
    """Insert or refresh the conformance block. Content outside the markers is preserved.

    Used for more than one destination since DR-30. An adopter's AGENTS.md is THEIRS - Plyego's
    is 293 lines of repo-specific convention - so the standard takes a marker-delimited block
    inside it rather than owning the file. Everything outside the markers survives, and a
    re-install refreshes only what is between them.
    """
    path = target_repo / rel
    wrapped = f"{BLOCK_BEGIN}\n{block.strip()}\n{BLOCK_END}"

    if not path.is_file():
        header = (
            f"# {header_title}\n\n"
            "Repository-specific guidance goes outside the markers below. The block between the "
            "markers is managed by the Surfaceplate installer and will be "
            "overwritten on upgrade.\n\n"
        )
        new_text = header + wrapped + "\n"
        action = "created"
    else:
        existing = normalise(path.read_text(encoding="utf-8"))
        if BLOCK_BEGIN in existing and BLOCK_END in existing:
            before = existing.split(BLOCK_BEGIN, 1)[0]
            after = existing.split(BLOCK_END, 1)[1]
            new_text = before + wrapped + after
            action = "unchanged" if new_text == existing else "refreshed"
        else:
            separator = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
            new_text = existing + separator + wrapped + "\n"
            action = "appended"

    if action != "unchanged" and not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new_text, encoding="utf-8", newline="\n")
    return action


def install(
    source: Path,
    target: Path,
    grace_days: int,
    dry_run: bool,
    replace_existing: bool,
    no_hooks: bool = False,
) -> int:
    payload = build_payload(source)
    # F27. The hook is one enforcement route of three, and SP038 fires only when a gate
    # actually claims `local_hook` - so the standard has always permitted a repository with no
    # surfaceplate hook while the installer refused to produce one. Declining removes the hook
    # from the payload entirely rather than writing a file nothing will call.
    if no_hooks:
        # The WHOLE directory, not just the hook. `.githooks/` also carries a `.gitattributes`,
        # and removing only the hook left an orphan directory holding one file that governs a
        # hook which is not there - caught by the probe rather than by reading the code.
        payload = {
            rel: src for rel, src in payload.items() if not rel.startswith(".githooks/")
        }

    missing = verify_source(source, payload)
    if missing:
        print("error: the standard is incomplete; these source files are missing:", file=sys.stderr)
        for item in missing:
            print(f"  {item}", file=sys.stderr)
        return 2

    version = (source / "VERSION").read_text(encoding="utf-8").strip()
    record_path = target / VENDOR_DIR / "INSTALL.json"
    previous: dict = {}
    if record_path.is_file():
        try:
            previous = json.loads(record_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 - a corrupt record is replaced, not trusted
            previous = {}

    mode = "upgrade" if previous else "install"
    print(f"Surfaceplate {version} - {mode}{' (dry run)' if dry_run else ''}")
    print(f"source: {source}")
    print(f"target: {target}")
    if previous.get("standard_version"):
        print(f"currently installed: {previous['standard_version']}")
    print()

    # F9. Until this existed, the previously-installed version was printed as a courtesy and
    # acted on by nothing, while the checker's remediation text said "re-run the installer" with
    # no version attached. A repository whose standard-owned files were edited, repaired by
    # running a DIFFERENT version, ends up conformant against a standard it never adopted - and
    # every output along the way reads like a successful repair.
    #
    # Reported, not refused. Upgrading is the ordinary path and must not be blocked; what was
    # missing is that it was indistinguishable from restoring.
    if previous.get("standard_version") and previous["standard_version"] != version:
        print(
            f"NOTE: this is an UPGRADE, {previous['standard_version']} -> {version}, not a "
            f"restore."
        )
        print(
            "      Standard-owned files will be replaced with this version's files and the"
        )
        print(
            "      install record rewritten to match. If you came here from an SP004/SP005"
        )
        print(
            f"      integrity failure expecting to repair {previous['standard_version']}, stop:"
        )
        print(
            f"      run the {previous['standard_version']} installer instead, or accept this as"
        )
        print("      a deliberate upgrade and re-read the conformance result afterwards.")
        print()

    # Not consulted when hooks are declined: there is no conflict to have, because nothing
    # will be configured. Checking anyway would refuse an install that touches no hook at all.
    hook_conflict = None if no_hooks else hook_configuration_conflict(target)
    if hook_conflict:
        print("STOPPED - this repository already has a different Git hook configuration:")
        print(f"  {hook_conflict}")
        print()
        print("Three routes, and the third was missing until 0.17.0 (F27):")
        print("  - Reconcile the existing hooks into .githooks without losing their behaviour.")
        print("  - Remove the old hook configuration, having decided it is no longer needed.")
        print("  - Re-run with --no-hooks: install everything else, keep your hook system, and")
        print("    rely on history_audit and review. Nothing will then check staged changes")
        print("    before they are committed, and the conformance check says so on every run.")
        print("Nothing has been written.")
        return 4

    collisions = detect_collisions(target, payload, previous)
    if collisions and not replace_existing:
        print("STOPPED - this repository already has its own files at paths the standard owns:")
        for rel in collisions:
            print(f"  {rel}")
        print()
        print("Installing would overwrite them. That is a decision for the repository owner, not")
        print("for the installer, because the existing files may carry stack-specific guidance")
        print("that the stack-neutral standard does not reproduce.")
        print()
        print("Choose one:")
        print("  * Reconcile first: fold anything worth keeping from those files into the")
        print("    standard, or into content that sits outside the standard-owned paths, then")
        print("    re-run with --replace-existing.")
        print("  * Move them aside (for example to .github/instructions-local/) and re-run.")
        print("  * Re-run with --replace-existing if you have decided the standard supersedes them.")
        print()
        print("Nothing has been written.")
        return 3
    if collisions:
        print(f"Replacing {len(collisions)} pre-existing file(s) at standard-owned paths, as")
        print("instructed by --replace-existing:")
        for rel in collisions:
            print(f"  replace {rel}")
        print()

    written, changed = 0, 0
    changed_by_class = {CLASS_ENFORCING: [], CLASS_CONTRACT: [], CLASS_REFERENCE: []}
    digests: dict[str, str] = {}
    for rel, src in payload.items():
        content = payload_text(src)
        digests[rel] = sha256_text(content)
        if write_file(target / rel, content, dry_run):
            changed += 1
            changed_by_class[classify(rel)].append(rel)
            print(f"  write   {rel}")
        if rel == HOOK_TARGET and not dry_run:
            hook_path = target / rel
            hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        written += 1

    # Remove controls the previous version installed that this version no longer ships.
    stale = sorted(set(previous.get("files", {})) - set(payload))
    for rel in stale:
        path = target / rel
        if path.is_file():
            print(f"  remove  {rel}  (no longer part of the standard)")
            if not dry_run:
                path.unlink()

    block = (source / "standard" / "conformance-block.md").read_text(encoding="utf-8")
    for rel, title in ((COPILOT_INSTRUCTIONS, "Copilot instructions"),
                       (AGENTS_FILE, "Agent instructions")):
        action = upsert_conformance_block(target, block, dry_run, rel=rel, header_title=title)
        print(f"  {action:<7} {rel}")

    if no_hooks:
        print("  declined  the pre-commit hook, and core.hooksPath is left as it was")
    else:
        hook_ok, hook_action = configure_standard_hook(target, dry_run)
        print(f"  {hook_action}")
        if not hook_ok:
            return 2

    profile = target / PROFILE_PATH
    if profile.is_file():
        print(f"  keep    {PROFILE_PATH}  (yours; never overwritten)")
    else:
        template = source / "templates" / "application-profile.yaml"
        print(f"  create  {PROFILE_PATH}  (from template - you must complete it)")
        if not dry_run:
            profile.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(template, profile)

    today = _dt.date.today()
    # The first install date is never reset, so re-running the installer cannot extend
    # the grace window.
    first_installed = previous.get("first_installed_at") or today.isoformat()
    record = {
        "standard": "surfaceplate",
        "standard_version": version,
        "installed_at": today.isoformat(),
        "first_installed_at": first_installed,
        "grace_expires": (
            _dt.date.fromisoformat(first_installed) + _dt.timedelta(days=grace_days)
        ).isoformat(),
        "profile_path": PROFILE_PATH,
        "conformance_block_digest": sha256_text(block.strip()),
        # DR-14. Recorded so the profile's declared framework_digest has something to be
        # checked against; until this existed the field was shape-checked and nothing more (F7).
        "framework_digest": framework_anchor(source),
        "files": digests,
        "executable_files": [] if no_hooks else [HOOK_TARGET],
    }
    # Recorded rather than silent (F27, DR-29). A declination that leaves no trace is the shape
    # this framework exists to catch: the check would pass and nothing would distinguish "staged
    # changes are gated" from "nothing gates them". Absent means installed, so every record
    # written before 0.17.0 reads correctly without migration.
    if no_hooks:
        record["hooks"] = "declined"
    record_text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if not dry_run:
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(record_text, encoding="utf-8", newline="\n")
    print(f"  write   {VENDOR_DIR}/INSTALL.json")

    print()
    print(f"{written} standard-owned file(s); {changed} written or updated; {len(stale)} removed.")

    # Broken out so an upgrade can be reviewed proportionately (DR-20). A documentation
    # change and a change to the code that decides pass/fail are not the same event, and a
    # single combined count invites treating them as one.
    if changed:
        print()
        print("What changed, by review class:")
        for cls, label in (
            (CLASS_ENFORCING, "enforcing  (code that runs - review this closely)"),
            (CLASS_CONTRACT, "contract   (parsed by the checker - changes what validates)"),
            (CLASS_REFERENCE, "reference  (read by people - changes what the rules say)"),
        ):
            items = changed_by_class[cls]
            print(f"  {len(items):>3}  {label}")
            for rel in items:
                print(f"       {rel}")
        if not changed_by_class[CLASS_ENFORCING] and not changed_by_class[CLASS_CONTRACT]:
            print()
            print("  Nothing that executes or validates changed in this upgrade.")
    print(f"Grace window ends {record['grace_expires']}. After that the check fails.")
    print()
    print("Next steps:")
    print(f"  1. Complete {PROFILE_PATH}. Worked examples: {VENDOR_DIR}/examples/")
    print(f"  2. Run: python {VENDOR_DIR}/check_conformance.py")
    print("  3. Stage the installer output.")
    if no_hooks:
        # Found exercising this path for the first time against a real repository (ACT-024):
        # every step below was printed unconditionally, telling a --no-hooks install to activate
        # and rely on a hook that was never written. Surfaceplate's own self-install always keeps
        # the hook, so nothing had ever run this branch for real before this. The declined route
        # is real conformance (DR-29's "hooks: declined" record, checked via SP038) - its own
        # instructions should say so, not describe the other route.
        print("  4. Commit the result. No local hook was installed - history_audit and review")
        print("     are what enforces this. Nothing checks staged changes before they commit.")
        print("  5. Open a pull request.")
    else:
        print(f"  4. Run: git update-index --chmod=+x {HOOK_TARGET}")
        print("  5. Commit the result. The installed pre-commit hook checks staged changes.")
        print("  6. Open a pull request.")
    if dry_run:
        print("\nDry run: nothing was written.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install or upgrade Surfaceplate in a repository."
    )
    parser.add_argument("--target", required=True, help="Path to the repository to install into.")
    parser.add_argument(
        "--source",
        default=None,
        help="Path to the standards repository (default: the repository containing this script).",
    )
    parser.add_argument(
        "--grace-days",
        type=int,
        default=DEFAULT_GRACE_DAYS,
        help=f"Days from first install before the check hard-fails (default: {DEFAULT_GRACE_DAYS}).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would change, write nothing.")
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help=(
            "Overwrite the repository's own pre-existing files at standard-owned paths. "
            "Only use this once you have decided the standard supersedes them."
        ),
    )
    parser.add_argument(
        "--no-hooks",
        action="store_true",
        help=(
            "Do not install the pre-commit hook and do not touch core.hooksPath. For a "
            "repository with its own hook system. The declination is recorded in INSTALL.json "
            "and reported by every conformance check."
        ),
    )
    args = parser.parse_args(argv)

    source = Path(args.source).resolve() if args.source else repo_root()
    target = Path(args.target).resolve()

    if not target.is_dir():
        print(f"error: target {target} is not a directory", file=sys.stderr)
        return 2
    if target == source:
        print("error: refusing to install the standard into itself", file=sys.stderr)
        return 2
    if not git_repository_available(target):
        print(
            f"error: target {target} is not the root of a readable Git working tree",
            file=sys.stderr,
        )
        return 2

    return install(
        source,
        target,
        args.grace_days,
        args.dry_run,
        args.replace_existing,
        no_hooks=args.no_hooks,
    )


if __name__ == "__main__":
    raise SystemExit(main())
