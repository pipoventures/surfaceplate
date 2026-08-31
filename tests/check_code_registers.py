#!/usr/bin/env python3
"""Fail if the identifier registers disagree with reality.

This is the remedy for F11, which `DR-8` raised and left open: *"Nothing enforces that a newly
added finding code is unique, contiguous, or documented."*

The case for a check rather than more care is that care demonstrably did not work. On
2026-08-31, `org/FINDINGS.md` carried **three** false statements at once, all written by people
reading the file at the time:

- `F5`'s entry said `INSTALL.md:29` still held a non-resolving clone URL. It had been corrected.
- The code-space table said the checker emitted `SP001`-`SP043`. `SP046` and `SP047` existed,
  added by the same session that was editing the file.
- The `ACT-<n>` row said there was "no register behind it". `activity/register.md` existed.

None of these is a typo. Each was true when written and became false when something else
changed, which is precisely the class of error a reader cannot catch by being careful: nothing
about a stale sentence looks different from a current one.

WHAT THIS CHECKS, and equally what it does not: it compares *declarations against reality*. It
cannot tell whether a finding's prose is still accurate - that is not mechanically decidable,
and `F5`'s stale entry would have survived this check. What it makes impossible is a code that
exists in one register and not the other.

Usage:
    python tests/check_code_registers.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "org" / "FINDINGS.md"
CHECKER = ROOT / "scripts" / "check_conformance.py"

# A code is emitted where a Finding is constructed. Deliberately not "any SPnnn literal in the
# file": the checker names other codes in remedy prose ("see SP034"), and counting those would
# report codes that are documented rather than emitted - the opposite of what this checks.
EMITTED = re.compile(r"Finding\(\s*\"(SP\d+)\"")

DECLARATION = re.compile(r"```text\n(emitted:.*?)```", re.DOTALL)
RANGE = re.compile(r"SP(\d+)(?:-SP(\d+))?")

CHECKS = 0
FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(f"{label}{': ' + detail if detail else ''}")


def parse_codes(spec: str) -> set[int]:
    """Expand 'SP001-SP035, SP037' into the integers it names."""
    codes: set[int] = set()
    for lo, hi in RANGE.findall(spec):
        start = int(lo)
        end = int(hi) if hi else start
        if end < start:
            raise SystemExit(f"declared range SP{lo}-SP{hi} runs backwards")
        codes.update(range(start, end + 1))
    return codes


def declared_space(text: str) -> dict[str, set[int]]:
    match = DECLARATION.search(text)
    if not match:
        raise SystemExit(
            "org/FINDINGS.md has no ```text block declaring the SP code space. The check "
            "derives the expected codes from that block rather than restating them; without "
            "it there is nothing to compare the checker against."
        )
    space: dict[str, set[int]] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, _, spec = line.partition(":")
        space[key.strip()] = parse_codes(spec)
    for required in ("emitted", "gap", "reserved"):
        if required not in space:
            raise SystemExit(f"the SP declaration block has no '{required}:' line")
    return space


def main() -> int:
    findings_text = FINDINGS.read_text(encoding="utf-8")
    checker_text = CHECKER.read_text(encoding="utf-8")

    # ---- SP codes: declaration against the code that emits them ----
    space = declared_space(findings_text)
    emitted = {int(code[2:]) for code in EMITTED.findall(checker_text)}

    check(
        "every emitted SP code is declared",
        emitted <= space["emitted"],
        ", ".join(f"SP{n:03d}" for n in sorted(emitted - space["emitted"])),
    )
    check(
        "every declared SP code is emitted",
        space["emitted"] <= emitted,
        ", ".join(f"SP{n:03d}" for n in sorted(space["emitted"] - emitted)),
    )
    # The SDS036 defect: a code documented but implemented by nothing, for releases, unnoticed.
    check(
        "no reserved SP code is quietly in use",
        not (space["reserved"] & emitted),
        ", ".join(f"SP{n:03d}" for n in sorted(space["reserved"] & emitted)),
    )
    check(
        "no declared gap is in use",
        not (space["gap"] & emitted),
        ", ".join(f"SP{n:03d}" for n in sorted(space["gap"] & emitted)),
    )
    # An undeclared hole is the thing that hides a code nobody remembers removing.
    whole = space["emitted"] | space["gap"] | space["reserved"]
    holes = set(range(1, max(whole) + 1)) - whole
    check(
        "the SP space has no undeclared hole",
        not holes,
        ", ".join(f"SP{n:03d}" for n in sorted(holes)),
    )

    # ---- F codes: the register against itself ----
    rows = [int(m) for m in re.findall(r"^\| F(\d+) \|", findings_text, re.MULTILINE)]
    bodies = [int(m) for m in re.findall(r"^## F(\d+) ", findings_text, re.MULTILINE)]

    check("the live register is not empty", bool(rows))
    check(
        "no F code is indexed twice",
        len(rows) == len(set(rows)),
        ", ".join(f"F{n}" for n in sorted({n for n in rows if rows.count(n) > 1})),
    )
    check(
        "no F code has two body sections",
        len(bodies) == len(set(bodies)),
        ", ".join(f"F{n}" for n in sorted({n for n in bodies if bodies.count(n) > 1})),
    )
    check(
        "F codes are contiguous from F1",
        set(rows) == set(range(1, max(rows) + 1)) if rows else False,
        ", ".join(f"F{n}" for n in sorted(set(range(1, max(rows) + 1)) - set(rows))) if rows else "",
    )
    # A body with no index entry is a finding that exists but cannot be found from the table -
    # the register's own summary would understate what it holds.
    check(
        "every body section is indexed in the table",
        set(bodies) <= set(rows),
        ", ".join(f"F{n}" for n in sorted(set(bodies) - set(rows))),
    )

    if FAILURES:
        print("CODE_REGISTERS=FAIL")
        print()
        for failure in FAILURES:
            print(f"  {failure}")
        print()
        print("Update org/FINDINGS.md, or the checker, so the two agree. A register that")
        print("describes a code space it does not have is worse than none: it reads as")
        print("authoritative and is not.")
        return 1

    # Reported so that "the registers agree" is distinguishable from "nothing was compared",
    # the defect recorded as F3.
    print(
        f"CODE_REGISTERS=PASS  ({CHECKS} checks; "
        f"{len(space['emitted'])} SP codes, {len(rows)} F codes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
