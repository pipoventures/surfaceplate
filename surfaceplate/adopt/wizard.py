"""Orchestration: run the sections in order, assemble, verify, and only then write.

`run()` is the one function anything outside this package should call. It is deliberately thin -
every real decision already happened inside a `sections.py` function, driven by a `Prompt` a caller
supplies. This module's own job is narrow: hold the pieces together, verify what they produced
before it reaches disk, and guarantee that a cancelled run leaves nothing behind.
"""

from __future__ import annotations

import json
from pathlib import Path

from surfaceplate.adopt import render, sections
from surfaceplate.adopt.prompting import Cancelled, Prompt

PROFILE_PATH = "governance/application-profile.yaml"
INSTALL_RECORD = ".standards/INSTALL.json"

# DR-35: basic resumability. A name distinct from anything the standard itself ships (never
# `.standards/...`, never `governance/...`) so it can never be mistaken for payload, and a leading
# dot so it reads as scratch state rather than a file this framework is asking anyone to commit.
# This lives only in an ADOPTING repository's working tree - never in surfaceplate's own source
# tree - so it has no interaction with this project's own release manifest.
DRAFT_FILENAME = ".surfaceplate-adopt-draft.json"


class NotInstalled(Exception):
    """The standard has not been installed here yet - `adopt` has nothing to attach a profile to."""


class AlreadyAdopted(Exception):
    """A real (non-template) profile already exists - `adopt` will not overwrite it silently."""


class WriteRefused(Exception):
    """The assembled profile failed its own verification. Nothing was written. Carries `detail`."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


def _read_install_record(repo: Path) -> dict:
    path = repo / INSTALL_RECORD
    if not path.is_file():
        raise NotInstalled(
            f"{INSTALL_RECORD} does not exist. Run `surfaceplate install` first - `adopt` fills in "
            "the profile the installer creates; it does not install the standard itself."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _refuse_if_already_adopted(repo: Path) -> None:
    """Refuses only on a REAL profile, not the untouched template.

    The installer already never overwrites an existing profile (`install_standard.py`'s own rule);
    this is the same protection applied one step later, to the wizard that is much more likely to
    be run against a repository someone has already been working in.
    """
    path = repo / PROFILE_PATH
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "replace-me" in text:
        return  # the untouched template - fair game
    raise AlreadyAdopted(
        f"{PROFILE_PATH} already exists and does not look like the untouched template. "
        "Edit it directly, or move it aside before running `adopt` again."
    )


def _verify(profile: dict, rendered: str, repo: Path) -> None:
    """Round-trips the rendered text and validates it against the schema. Raises `WriteRefused`
    with the exact problem rather than letting a malformed profile reach disk."""
    import yaml

    try:
        reparsed = yaml.safe_load(rendered)
    except yaml.YAMLError as exc:
        raise WriteRefused(f"the rendered YAML does not parse: {exc}") from None

    if reparsed != profile:
        # A structural diff a human could act on, not just "they differ".
        import difflib

        left = json.dumps(profile, indent=2, sort_keys=True, default=str).splitlines()
        right = json.dumps(reparsed, indent=2, sort_keys=True, default=str).splitlines()
        diff = "\n".join(difflib.unified_diff(left, right, "assembled", "rendered", lineterm=""))
        raise WriteRefused(
            "the rendered YAML does not round-trip to what was assembled - the renderer has a "
            f"bug, and nothing is written while that is true:\n{diff}"
        )

    schema_path = repo / ".standards" / "schemas" / "application-profile.schema.yaml"
    if not schema_path.is_file():
        raise WriteRefused(f"{schema_path} is missing - cannot validate before writing.")
    import jsonschema

    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(reparsed), key=lambda e: list(e.path))
    if errors:
        detail = "; ".join(
            f"{'/'.join(str(p) for p in e.path) or '(root)'}: {e.message}" for e in errors[:8]
        )
        raise WriteRefused(f"the assembled profile does not satisfy its own schema: {detail}")

    from surfaceplate import check_conformance

    hits = [
        path_str
        for path_str, value in _walk_strings(reparsed)
        if check_conformance.PLACEHOLDER_PATTERN.search(value)
    ]
    if hits:
        raise WriteRefused(
            "an answer still contains a template placeholder token (TBD/TODO/replace-me/…) at: "
            + ", ".join(hits)
        )


def _draft_path(repo: Path) -> Path:
    return repo / DRAFT_FILENAME


def _save_draft(repo: Path, record: dict, state: dict) -> None:
    """Called after every section completes - a late failure loses at most the section in
    progress, not the whole run. `framework_version`/`framework_digest` travel with the draft so a
    later resume can tell whether the install underneath it has changed since (`_resume_or_start`),
    flagged rather than silently trusted."""
    payload = {
        "framework_version": record.get("standard_version", ""),
        "framework_digest": record.get("framework_digest", ""),
        "sections": state,
    }
    _draft_path(repo).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _load_draft(repo: Path) -> dict | None:
    path = _draft_path(repo)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A corrupt or unreadable draft is treated as no draft, never as a reason to fail the run
        # it would otherwise only have helped.
        return None


def _clear_draft(repo: Path) -> None:
    _draft_path(repo).unlink(missing_ok=True)


def _resume_or_start(repo: Path, record: dict, prompt: Prompt) -> dict:
    """Never resumes silently. A version/digest mismatch is flagged - shown to the human, who
    still decides - rather than either trusted or refused outright."""
    draft = _load_draft(repo)
    if draft is None:
        return {}

    matches = draft.get("framework_version") == record.get(
        "standard_version", ""
    ) and draft.get("framework_digest") == record.get("framework_digest", "")

    print("A saved draft from an earlier, unfinished run was found here.")
    if matches:
        print("It was answered against the framework version currently installed in this repository.")
    else:
        print(
            "It was started against a different framework version or digest than what's "
            "installed here now - resuming may carry answers into a wizard that no longer asks "
            "for them the same way."
        )
    resume = prompt.confirm("Resume it?", default=matches)
    if not resume:
        _clear_draft(repo)
        return {}
    return dict(draft.get("sections", {}))


def _walk_strings(node: object, path: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(node, dict):
        for k, v in node.items():
            out.extend(_walk_strings(v, f"{path}.{k}" if path else str(k)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(_walk_strings(v, f"{path}[{i}]"))
    elif isinstance(node, str):
        out.append((path, node))
    return out


def run(repo: Path, prompt: Prompt) -> Path:
    """Runs the whole wizard. Returns the path written. Raises `Cancelled`, `NotInstalled`,
    `AlreadyAdopted`, or `WriteRefused` - every one of them leaves the repository untouched, except
    that `Cancelled` (and any other failure) may leave a resumable draft behind - see
    `_save_draft`. A completed write clears it (below)."""
    _refuse_if_already_adopted(repo)
    record = _read_install_record(repo)

    state = _resume_or_start(repo, record, prompt)

    def step(name: str, compute):
        """One section: return it from a resumed draft if already answered, otherwise ask and
        persist. `compute` is a zero-arg closure so a resumed section costs nothing - the
        `sections.ask_*` call it wraps is never invoked at all when the answer is already in
        `state`, which is what makes resuming actually skip re-asking rather than merely
        skip re-writing."""
        if name in state:
            print("  (already answered in the saved draft)")
            return state[name]
        value = compute()
        state[name] = value
        _save_draft(repo, record, state)
        return value

    print("[Before section 1 — how should this be explained?]")
    mode = step("mode", lambda: sections.ask_mode(prompt))

    print("\n[1 of 7 — Identity]")
    identity = step("identity", lambda: sections.ask_identity(prompt))

    print("\n[2 of 7 — Stack]")
    stack = step("stack", lambda: sections.ask_stack(prompt, repo))

    print("\n[3 of 7 — Risk & materiality]")
    risk = step("risk", lambda: sections.ask_risk(prompt))

    print("\n[4 of 7 — Conformance level]")
    level = step(
        "level",
        lambda: sections.ask_conformance_level(
            prompt, repo, builds_user_interface=stack["builds_user_interface"], mode=mode
        ),
    )

    print(f"\n[5 of 7 — Controls, floor: {level}]")
    controls = step("controls", lambda: sections.ask_controls(prompt, level=level, mode=mode))

    print("\n[6 of 7 — Prerequisite gates]")
    gates = step(
        "gates",
        lambda: sections.ask_gates(
            prompt, level=level, builds_user_interface=stack["builds_user_interface"], mode=mode
        ),
    )

    print("\n[Before the review — a few closing facts]")
    adoption = step(
        "adoption",
        lambda: sections.ask_adoption_identity(
            prompt,
            framework_version=record.get("standard_version", ""),
            framework_digest=record.get("framework_digest", ""),
            owner=identity["owner"],
        ),
    )
    adoption["deferrals"] = []  # v1: control_decisions offers required only; see DR-32.

    wrap = step("wrap", lambda: sections.ask_roles_and_release(prompt))

    profile = {
        "schema_version": "1.0",
        **identity,
        **stack,
        **risk,
        "conformance_level": level,
        "adoption": adoption,
        **controls,
        "prerequisites": gates,
        **wrap,
    }

    rendered = render.render_profile(profile)
    _verify(profile, rendered, repo)

    print("\n[7 of 7 — Review]")
    print(rendered)
    if not prompt.confirm("Write this to " + PROFILE_PATH + "?", default=None):
        raise Cancelled()

    target = repo / PROFILE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8", newline="\n")
    _clear_draft(repo)  # a completed run leaves no draft behind - it exists only to protect one
    return target
