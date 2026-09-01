#!/usr/bin/env python3
"""Proves the binding rule: nothing reaches a written profile that no human answered.

    python tests/test_provenance.py

`org/RELEASE_PLAN.md` states the rule as "it asks, the human answers, the tool writes". Until now
that was checked by `ScriptedPrompt`, and this repository's own test file recorded exactly how far
that fell short: it "only objects to a call it wasn't given an answer for, never to a value written
without any call." `F32`/`ACT-022` walked straight through that gap - seven controls and gates were
given rationale text no prompt ever asked for, and every scripted test passed.

This closes it from the other side. `sections.py`'s `build_*` functions are pure, so the whole
profile can be assembled from answers in which **every free-text field carries a unique sentinel**.
Any string in the result that carries no sentinel was not typed by anyone: it was contributed by the
tool. Some of that is legitimate and unavoidable - the schema version, a gate's own id, the statuses
the schema allows - so those are enumerated in an allow-list below.

**The allow-list is the point.** It is the honest, reviewable statement of everything this wizard
writes on its own behalf. Adding an entry to it is a code-review event, and a change that starts
inventing prose again cannot be made without either failing this test or visibly widening the list.
"""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from surfaceplate.adopt import catalogue, plan, sections, wizard  # noqa: E402

FAILURES: list[str] = []
PASSES = 0

FRAMEWORK_VERSION = "0.0.0-sentinel-version"
FRAMEWORK_DIGEST = "0000-sentinel-digest"


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSES
    if condition:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


def _all_choice_values() -> set[str]:
    """Every value any choice field in any plan can legally take.

    Derived from the plans themselves rather than typed out, so a new option added to a dropdown
    does not silently need a hand-edit here - the same discipline `catalogue.py` applies to gate and
    control data (`DR-6`).
    """
    values: set[str] = set()
    for level in ("essential", "standard", "full"):
        for builds_ui in (True, False):
            state = {
                "mode": {"mode": "simple"},
                "stack": {"builds_user_interface": builds_ui},
                "level": {"conformance_level": level},
                "identity": {"owner": "x"},
                "risk": {},
            }
            for name in plan.SECTION_ORDER:
                section = plan.section_plan(name, repo=ROOT, state=state)
                for spec in section.fields:
                    # ONLY closed enums. A `select` field's options are discovered from the
                    # repository (`DR-38`), so admitting them here would let the allow-list absorb
                    # arbitrary file paths and CI step names - and an allow-list that grows with
                    # the adopter's repository is not an allow-list. Select fields are answered
                    # with sentinels below, exactly like the free-text ones, so they never need to
                    # appear here. If that stops being true this test has stopped proving anything.
                    if spec.kind not in ("choice", "multiselect"):
                        continue
                    for value, _label in spec.choices:
                        values.add(value)
    return values


def sentinel_answers(repo: Path, *, level: str, builds_ui: bool, mode: str = "simple") -> tuple[dict, set[str]]:
    """A full set of answers in which every free-text field is a unique, traceable sentinel."""
    state: dict = {}
    sentinels: set[str] = set()
    counter = 0

    seeded = {
        "mode.mode": mode,
        "stack.builds_user_interface": builds_ui,
        "level.conformance_level": level,
    }

    for name in plan.SECTION_ORDER:
        section = plan.section_plan(name, repo=repo, state=state)
        local: dict = {}
        for spec in section.fields:
            if not spec.applies(local):
                continue
            key = f"{name}.{spec.id}"
            if key in seeded:
                local[spec.id] = seeded[key]
            elif spec.kind == "bool":
                local[spec.id] = bool(spec.default)
            elif spec.kind == "choice":
                local[spec.id] = spec.choices[0][0]
            elif spec.kind == "multiselect":
                local[spec.id] = [spec.choices[0][0]]
            else:
                # `select` lands here deliberately, alongside text and textarea: its value is
                # chosen by a human from real candidates, so it must be traceable like any other
                # answer rather than waved through as a known constant.
                counter += 1
                token = f"SENTINEL-{counter:04d}"
                sentinels.add(token)
                local[spec.id] = token
        state[name] = local
    return state, sentinels


def unexplained(profile: dict, sentinels: set[str], allowed: set[str]) -> list[tuple[str, str]]:
    """Every string in `profile` that neither carries a sentinel nor is an allowed constant."""
    offenders = []
    for path, value in wizard._walk_strings(profile):
        if any(token in value for token in sentinels):
            continue
        if value in allowed:
            continue
        offenders.append((path, value))
    return offenders


def allow_list() -> set[str]:
    """Everything this wizard legitimately contributes without anyone typing it.

    Read this list as the answer to "what does the tool write on its own?" - it should stay short,
    and every entry should be a fact about the framework rather than a judgement about the adopter.
    """
    allowed = {
        sections.SCHEMA_VERSION,  # "1.0"
        sections.SCANNER_NOTES,  # "Blocking."
        sections.DECISION_REQUIRED,  # "required"
        FRAMEWORK_VERSION,  # both read from .standards/INSTALL.json, never from an answer
        FRAMEWORK_DIGEST,
        _dt.date.today().isoformat(),  # adoption_date
    }
    allowed |= set(catalogue.GATE_CATALOGUE)  # a gate's own id
    allowed |= set(catalogue.CONFORMANCE_LEVELS["full"])  # a control's own id
    allowed |= {"required", "deferred", "not_applicable"}  # gate statuses
    allowed |= _all_choice_values()  # every value a dropdown can take
    return allowed


def test_no_value_is_invented(level: str, builds_ui: bool) -> None:
    state, sentinels = sentinel_answers(ROOT, level=level, builds_ui=builds_ui)
    profile = sections.build_profile(
        state, framework_version=FRAMEWORK_VERSION, framework_digest=FRAMEWORK_DIGEST
    )
    offenders = unexplained(profile, sentinels, allow_list())
    check(
        f"{level}{'/UI' if builds_ui else ''}: every string traces to an answer or the allow-list",
        not offenders,
        "; ".join(f"{p} = {v!r}" for p, v in offenders[:6]),
    )


def test_the_walk_can_fail() -> None:
    """The negative control. A test that only ever passes proves nothing, so a value nobody
    supplied is injected and the walk must object to it - the exact shape of the `F32` defect."""
    state, sentinels = sentinel_answers(ROOT, level="essential", builds_ui=False)
    profile = sections.build_profile(
        state, framework_version=FRAMEWORK_VERSION, framework_digest=FRAMEWORK_DIGEST
    )
    profile["baseline_controls"]["agent_work_packets"]["rationale"] = (
        "All agent work is bounded, scoped, and reviewable."  # plausible, and nobody typed it
    )
    offenders = unexplained(profile, sentinels, allow_list())
    check(
        "a fabricated rationale is caught by the walk",
        any("agent_work_packets" in path for path, _ in offenders),
        f"offenders: {offenders}",
    )


def test_allow_list_is_small_and_declared() -> None:
    """The allow-list should be facts about the framework, not prose about an adopter. Nothing
    enforces brevity, but a sudden jump in size is worth a reviewer's attention, so the count is
    reported rather than left implicit."""
    prose = [
        value
        for value in allow_list()
        if " " in value and value not in {sections.SCANNER_NOTES}
    ]
    check(
        "no free prose entered the allow-list unnoticed",
        not prose,
        f"prose-like entries: {prose}",
    )


def main() -> int:
    print("provenance: nothing is written that nobody answered")
    for level, builds_ui in (("essential", False), ("standard", False), ("full", True)):
        test_no_value_is_invented(level, builds_ui)

    print("\nnegative controls")
    test_the_walk_can_fail()
    test_allow_list_is_small_and_declared()

    print(f"\n  (allow-list carries {len(allow_list())} entries)")
    print()
    if FAILURES:
        print(f"PROVENANCE=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"PROVENANCE=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
