#!/usr/bin/env python3
"""The adversarial-review hand-off names files that exist, and names the same ones twice.

    python tests/check_audit_packet.py

`F50` is why this exists. `RELEASE_PLAN` item 9 hands an external reviewer two attachments: a curated
prompt and an `EVIDENCE_BUNDLE.md` built by a shell command in `audit/AUDIT_README.md`. That command
listed `surfaceplate/adopt/prompting.py` for three packets after `DR-36` deleted it. The command had
no guard and redirected the whole loop, so it would have produced a **truncated bundle rather than an
error** — and the prompt asked the reviewer to trace the binding rule through that same missing file.

**Nothing detected it, and `AUDIT_README.md` had anticipated the failure mode in prose:** *"this
command must match it; if the two drift, the prompt's text is authoritative and the command is
wrong."* Both had drifted, so the stated tie-breaker resolved to a file that did not exist either.

This repository applies `DR-6`'s lesson rigorously to its manifest, its vendored copy and its
identifiers — each with a `--check` mode that runs in CI. The audit packet is the same shape:
content derived from a file list that lives somewhere else. It had no check and, more tellingly, **no
reader** — a document nobody opens between the day it is written and the day it is used cannot drift
visibly, only silently.

What is checkable here is narrow and worth being honest about: that the paths named exist, and that
the prompt and the command name the same set. Whether the *questions* are still the right ones is
prose, and no check can hold that — `ACT-037` rewrote them because a person read them, which remains
the only mechanism for that half.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "audit" / "AUDIT_README.md"
PROMPT = ROOT / "audit" / "GEMINI_ADVERSARIAL_REVIEW_PROMPT_CURATED.md"

FAILURES: list[str] = []
PASSES = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSES
    if condition:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


def command_file_list() -> list[str]:
    """The paths the bundle command actually cats, read out of the fenced block itself.

    Parsed rather than restated here: a copy in this file would be a third place the list lives, and
    a third place to drift. The block is located by its `for f in` line and ends at `; do`.
    """
    text = README.read_text(encoding="utf-8")
    match = re.search(r"for f in (.*?);\s*do", text, re.S)
    if not match:
        raise SystemExit("could not find the bundle command's `for f in ... ; do` list in AUDIT_README.md")
    body = match.group(1).replace("\\\n", " ")
    return [token for token in body.split() if "/" in token or token.endswith(".md")]


def prompt_included_paths() -> set[str]:
    """Paths the prompt's own "What is included" section names, which is the authoritative side.

    Bounded to that section deliberately: the prompt also names files it deliberately EXCLUDES, and
    reading those as required would invert the check.
    """
    text = PROMPT.read_text(encoding="utf-8")
    start = text.index("**What is included, and why:**")
    end = text.index("**What is deliberately not included", start)
    section = text[start:end]
    return {
        path
        for path in re.findall(r"`([a-zA-Z0-9_./*-]+\.(?:py|md|yaml|sha256)|[a-zA-Z0-9_./-]+/\*)`", section)
        if "/" in path
    }


PACKET_SOURCE = ROOT / "audit" / "INDEPENDENT_REVIEW_PACKET.md"
PACKET_BUILDER = ROOT / "scripts" / "build_review_packet.py"
SCOPE = ROOT / "audit" / "AUDIT_SCOPE.md"


def review_packet_checks() -> None:
    """`ACT-060` / `DR-64`: the packet the maintainer hands an independent reviewer is generated from
    a tracked source. What is checkable: the source and every path it names exist; the generator
    runs on this tree and leaves no placeholder blank; the page carries this tree's anchor, the
    version, one row per scope criterion and the audit prompt; and the generator refuses an
    archive built from a different tree - the archive in `dist/` on the day this was written was
    exactly that, and would have gone to a reviewer as the release."""
    import hashlib
    import subprocess
    import sys
    import tempfile
    import zipfile

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import install_standard  # noqa: E402
    from surfaceplate import rules  # noqa: E402

    check("the packet source exists", PACKET_SOURCE.is_file())
    text = PACKET_SOURCE.read_text(encoding="utf-8")
    named = {
        m for m in re.findall(r"`([a-zA-Z0-9_./-]+\.(?:py|md|yaml|sha256))`", text)
        if "/" in m and "{{" not in m and "<" not in m and not m.startswith("surfaceplate-")
        and not m.startswith("governance/assurance/AE-000") and "INDEPENDENT_REVIEW_" not in m
    }
    missing = sorted(p for p in named if not (ROOT / p).exists())
    check(f"every repository path the packet names exists ({len(named)} named)", not missing, str(missing))

    tmp = Path(tempfile.mkdtemp(prefix="surfaceplate-packet-"))
    out = tmp / "packet.html"
    result = subprocess.run([sys.executable, str(PACKET_BUILDER), "--out", str(out)], capture_output=True, text=True, cwd=str(ROOT))
    check("the generator runs on this tree", result.returncode == 0 and out.is_file(), (result.stdout + result.stderr)[-400:])
    if out.is_file():
        page = out.read_text(encoding="utf-8")
        anchor = install_standard.framework_anchor(ROOT / "surfaceplate")
        version = (ROOT / "surfaceplate" / "VERSION").read_text(encoding="utf-8").strip()
        check("the page carries this tree's anchor", bool(anchor) and anchor in page)
        check("and the version", f"Surfaceplate {version}" in page)
        check("and leaves no placeholder unresolved", "{{" not in page)
        check("and carries no template token the checker would reject", not rules.PLACEHOLDER_PATTERN.search(page))
        criteria = [ln for ln in SCOPE.read_text(encoding="utf-8").splitlines() if ln.strip().startswith("- ")]
        check(f"and one form row per scope criterion ({len(criteria)})", page.count('data-crit="') == len(criteria), str(page.count('data-crit="')))
        check("and the audit prompt, from its evidence-handling section", "Required evidence handling" in page and "Over-engineering test" in page)
        check("and no external resource", "http" not in re.sub(r'href="https?://[^"]*"|https?://\S+', "", page).replace("http-equiv", ""),
              "an external script, style or image would make the page depend on the network")
        printed = re.search(r"Page SHA-256:\s+([0-9a-f]{64})", result.stdout)
        check("the generator prints the page's own digest", bool(printed) and printed.group(1) == hashlib.sha256(out.read_bytes()).hexdigest())
    # The guard: an archive whose inner manifest is not this tree's is refused.
    wrong = tmp / "wrong.zip"
    with zipfile.ZipFile(wrong, "w") as z:
        z.writestr("surfaceplate-x/surfaceplate/MANIFEST.sha256", "0" * 64 + "  surfaceplate-x/README.md\n")
    refused = subprocess.run([sys.executable, str(PACKET_BUILDER), "--zip", str(wrong), "--out", str(tmp / "never.html")], capture_output=True, text=True, cwd=str(ROOT))
    check("an archive built from a different tree is refused", refused.returncode != 0 and "REFUSING" in (refused.stdout + refused.stderr) and not (tmp / "never.html").exists(),
          (refused.stdout + refused.stderr)[-300:])


def main() -> int:
    print("the bundle command names files that exist")
    listed = command_file_list()
    check("the command's file list was parsed", len(listed) >= 10, f"parsed {len(listed)} entries")

    missing = [p for p in listed if not (ROOT / p).is_file()]
    check(
        "every file the bundle command cats exists in this repository",
        not missing,
        f"the command would fail at `cat` on: {missing}",
    )

    print("\nand the prompt and the command name the same set")
    declared = prompt_included_paths()
    listed_set = set(listed)
    # A glob in the prompt (`surfaceplate/seeds/*`) means EVERY file in that directory, and is
    # expanded against the DISK rather than against the command. Checking it against the command was
    # the first version and it was too weak to be worth having: dropping one of four seeds left
    # three still listed, so "the command lists files under seeds/" passed and only the count
    # noticed. A glob that tolerates a missing member is not checking the glob.
    expanded: set[str] = set()
    for path in declared:
        if path.endswith("/*"):
            directory = ROOT / path[:-2]
            on_disk = {
                str(f.relative_to(ROOT)) for f in sorted(directory.glob("*")) if f.is_file()
            }
            check(
                f"the command cats every file under {path} ({len(on_disk)} on disk)",
                on_disk and on_disk <= listed_set,
                f"in the directory but not in the command: {sorted(on_disk - listed_set)}",
            )
            expanded |= on_disk
        else:
            expanded.add(path)

    absent = sorted(expanded - listed_set)
    check(
        "every file the prompt says is attached is one the command cats",
        not absent,
        f"declared in the prompt, missing from the command: {absent}",
    )

    stated = re.search(r"attached here \(`EVIDENCE_BUNDLE\.md`\) are (\d+)", PROMPT.read_text(encoding="utf-8"))
    check(
        "the prompt's stated file count matches what the command builds",
        bool(stated) and int(stated.group(1)) == len(listed),
        f"prompt says {stated.group(1) if stated else '?'}, command lists {len(listed)}",
    )

    # `F114`: the count was right in one sentence of the prompt and stale in three other places -
    # the README's "curated 15-file subset" and the prompt's own "these 15 files" and "the 15 files
    # reviewed" - after `ACT-052` and `DR-55` widened the bundle to 27. Every place that states the
    # number is read here, so the sentence that was checked cannot be the only one that is right.
    readme_text = README.read_text(encoding="utf-8")
    prompt_text = PROMPT.read_text(encoding="utf-8")
    for label, text, pattern in (
        ("AUDIT_README.md's 'curated N-file subset'", readme_text, r"curated (\d+)-file subset"),
        ("the prompt's 'these N files'", prompt_text, r"these (\d+) files"),
        ("the prompt's 'Verdict on the N files reviewed'", prompt_text, r"Verdict on the (\d+) files reviewed"),
    ):
        found = re.findall(pattern, text)
        check(
            f"{label} states the command's count ({len(listed)})",
            bool(found) and all(int(n) == len(listed) for n in found),
            f"states {found or 'nothing'}, command lists {len(listed)}",
        )

    print("\nand the independent review packet builds from its source (ACT-060, DR-64)")
    review_packet_checks()

    print()
    if FAILURES:
        print(f"AUDIT_PACKET=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"AUDIT_PACKET=PASS  ({PASSES} checks; {len(listed)} files in the bundle)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
