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
