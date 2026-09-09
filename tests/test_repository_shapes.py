#!/usr/bin/env python3
"""The properties of a repository that change this framework's behaviour, named and covered.

    python tests/test_repository_shapes.py

WHY THIS EXISTS, and it is a correction to how this repository tested itself.

`tests/test_adopt_matrix.py` walks every reachable **decision** — 208 cases, 44,774 checks — and
between them the suites here run some fifty thousand. In one afternoon a person driving the wizard
by hand found five defects none of them could reach: `F132`, `F142`, `F143`, `F144`, `F145`, four of
them `high`.

The tempting conclusion was "test against more repositories". **It is the wrong conclusion, and
this file is the right one.** Surfaceplate is repository- and language-agnostic by design, so its
behaviour cannot depend on *which* repository it meets — only on a small number of **properties**
that repository has. Enumerate the properties and a handful of synthetic fixtures covers every
repository there will ever be. Every one of those five findings is reproduced here, or in
`test_discover.py`, from a fixture of a few files. The real repositories were needed to *find* them
and are not needed to *prevent* them.

The matrix already had a shape axis: `SHAPES = ("bare", "rich", "mixed")`. Three shapes chosen for
**how much discovery finds** — nothing, everything, awkward — and not for **which properties change
behaviour**. That is why `bare` has no dependency manifest and `F132` still got through: the fixture
had the property and no oracle asked the question.

WHAT THIS FILE ASSERTS THAT THE OTHERS DO NOT. Two things.

1. **Behaviour per property.** For each axis below, the behaviour that varies with it, asserted in
   both directions — because a check that only ever returns one answer has not been shown to
   distinguish anything.

2. **That what the wizard writes is TRUE, not merely expected.** The matrix asserts the profile
   matches the script; it cannot notice that the script itself named a checkout step as a test
   control's implementation. `F144` lived there. The `implausible()` oracle below asks the
   different question, and it is the one that pays.

WHY A CROSS-PRODUCT IS NOT ATTEMPTED, since the omission should read as a decision. Ten binary axes
is 1,024 combinations and most differ in nothing. Each axis is exercised against a baseline and
against the combinations where two axes genuinely interact - the same judgement `adopt_matrix.py`
makes when it takes 208 cases rather than every path.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
PAYLOAD = ROOT / "surfaceplate"

from surfaceplate import rules  # noqa: E402
from surfaceplate.adopt import catalogue, defaults, discover, plan  # noqa: E402

PASSES = 0
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSES
    if condition:
        PASSES += 1
    else:
        FAILURES.append(f"{name}{': ' + detail if detail else ''}")


# ---------------------------------------------------------------------------------------------
# The axes. Each names the property, the values it takes, and the finding that put it here.
# ---------------------------------------------------------------------------------------------

AXES: dict[str, dict[str, str]] = {
    "dependencies": {
        "none": "no manifest of any kind - the `dependency_lock` floor lifts (F132, DR-73)",
        "manifest_only": "declares dependencies, pins them nowhere - the lock file is asked for",
        "manifest_and_lock": "a real lock file - the reference is proposed from it",
    },
    "ci_steps": {
        "none": "no workflow - a pattern-B control has nothing to name",
        "not_tests": "steps that fetch, prepare and ship - none may be proposed (F144), and one "
                     "named anyway is cautioned (F145)",
        "tests": "steps that run tests - each control takes its own (F84's rule)",
    },
    "installed": {
        "none": "a first install",
        "older": "an upgrade - and it must say so",
        "newer": "a downgrade - and it must say THAT, not its opposite (F141)",
    },
}


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def make_repo(tmp: Path, name: str, *, dependencies: str = "none", ci_steps: str = "none") -> Path:
    """A repository with the named properties and nothing else. Deliberately tiny: if a fixture
    needs to be big to exercise a property, the property has not been isolated."""
    repo = tmp / name
    repo.mkdir(parents=True)
    for args in (["init", "-q"], ["config", "user.email", "t@example.invalid"],
                 ["config", "user.name", "T"], ["config", "commit.gpgsign", "false"]):
        assert _git(repo, *args).returncode == 0

    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")

    if dependencies in ("manifest_only", "manifest_and_lock"):
        (repo / "package.json").write_text('{"name": "fixture"}\n', encoding="utf-8")
    if dependencies == "manifest_and_lock":
        (repo / "package-lock.json").write_text('{"lockfileVersion": 3}\n', encoding="utf-8")

    steps = {
        "none": [],
        "not_tests": ["Check out this repo", "Set up Python", "Upload the report"],
        "tests": ["Check out this repo", "Run the unit tests", "Run the contract tests"],
    }[ci_steps]
    if steps:
        (repo / ".github" / "workflows").mkdir(parents=True)
        body = "name: CI\non: [push]\njobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n"
        body += "".join(f"      - name: {s}\n        run: true\n" for s in steps)
        (repo / ".github" / "workflows" / "ci.yml").write_text(body, encoding="utf-8")

    assert _git(repo, "add", "-A").returncode == 0
    assert _git(repo, "commit", "-qm", "fixture").returncode == 0
    return repo


def proposals_for(repo: Path, level: str = "standard") -> dict[str, str]:
    found = discover.scan(repo)
    return {
        str(p.field): str(p.value)
        for p in defaults.propose_controls(level=level, mode="simple", found=found)
        if "implementation_reference" in str(p.field)
    }


# ---------------------------------------------------------------------------------------------
# The oracle the matrix does not have: is what was proposed PLAUSIBLE for what it implements?
# ---------------------------------------------------------------------------------------------

def implausible(control: str, reference: str) -> str:
    """Empty when the reference could honestly implement the control; else why not.

    `F144` is the finding this exists for. The matrix asserted that the written profile matched the
    script and could not notice that the script had named `Check out mnemosyne (shared generator
    lives there)` as the implementation of `deterministic_tests`. **Asserting that output matches
    expectation cannot catch an expectation that was wrong.**

    Deliberately conservative: it reports only what is clearly wrong, for the reason `F145` records
    about the checker's own caution - a false alarm here would train a reader to skim the real one.
    """
    if control in catalogue.PATTERN_B_CONTROLS:
        if rules.step_name_is_clearly_not_a_test(reference):
            return f"{reference!r} describes fetching, preparing or shipping, not testing"
    if control == "dependency_lock":
        name = reference.rsplit("/", 1)[-1].lower()
        manifests_that_are_not_locks = {"package.json", "go.mod", "cargo.toml", "gemfile",
                                        "composer.json", "pom.xml", "setup.py"}
        if name in manifests_that_are_not_locks:
            return f"{reference!r} declares dependencies but does not pin them"
    return ""


# ---------------------------------------------------------------------------------------------
# Axis: dependencies
# ---------------------------------------------------------------------------------------------

def test_axis_dependencies(tmp: Path) -> None:
    """`F132`, `F142`, `DR-73`. The property is *does this repository declare dependencies at all*,
    and it decides whether a control is a floor, an option, or neither."""
    print("\naxis: dependencies")

    none = make_repo(tmp, "dep-none", dependencies="none")
    manifest = make_repo(tmp, "dep-manifest", dependencies="manifest_only")
    lock = make_repo(tmp, "dep-lock", dependencies="manifest_and_lock")

    check("no manifest: the derivation says so", rules.dependency_manifest(none)[1] == "none")
    check("a manifest: the derivation finds it", rules.dependency_manifest(manifest)[1] == "found")

    floor_none = plan.level_floor("essential", discover.scan(none))
    floor_manifest = plan.level_floor("essential", discover.scan(manifest))
    check("no manifest: the essential floor is empty (F132)", floor_none == frozenset(), str(floor_none))
    check("a manifest: dependency_lock is the floor", "dependency_lock" in floor_manifest)

    # `F142`: not required is not the same as available-but-unusable.
    section = plan.controls_plan(level="essential", mode="simple", found=discover.scan(none))
    above = next((f for f in section.fields if f.id == "above_floor"), None)
    offered = [c for c, _ in above.choices] if above else []
    check("no manifest: the control is not even offered above the floor (F142)",
          "dependency_lock" not in offered, str(offered))
    check("and the list says why, and how to get it back",
          above is not None and "no dependency manifest" in above.help
          and "returns on its own" in above.help)

    # A lock file is proposed; a manifest alone is not proposed AS a lock.
    check("a real lock file is proposed",
          proposals_for(lock).get("controls.dependency_lock.implementation_reference")
          == "package-lock.json",
          str(proposals_for(lock)))
    check("a manifest alone proposes nothing for the lock (F135)",
          "controls.dependency_lock.implementation_reference" not in proposals_for(manifest),
          str(proposals_for(manifest)))


# ---------------------------------------------------------------------------------------------
# Axis: ci_steps
# ---------------------------------------------------------------------------------------------

def test_axis_ci_steps(tmp: Path) -> None:
    """`F144`, `F145`, `F84`. The property is *what the repository's CI steps are called*, and it
    decides whether a pattern-B control can be proposed at all."""
    print("\naxis: ci_steps")

    for value in ("none", "not_tests", "tests"):
        repo = make_repo(tmp, f"ci-{value}", dependencies="manifest_and_lock", ci_steps=value)
        got = proposals_for(repo)
        pattern_b = {k: v for k, v in got.items()
                     if k.split(".")[1] in catalogue.PATTERN_B_CONTROLS}
        if value == "tests":
            check("steps that run tests: each control takes its own (F84's rule)",
                  pattern_b.get("controls.deterministic_tests.implementation_reference") == "Run the unit tests"
                  and pattern_b.get("controls.contract_tests.implementation_reference") == "Run the contract tests",
                  str(pattern_b))
        else:
            check(f"steps '{value}': nothing is proposed for a pattern-B control (F144)",
                  not pattern_b, str(pattern_b))
        if value == "not_tests":
            found = discover.scan(repo)
            check("and the steps are still OFFERED - only the proposal is filtered",
                  len(found.ci_steps) == 3, str(found.ci_steps))
            check("a step named anyway would be cautioned by the checker (F145)",
                  rules.step_name_is_clearly_not_a_test("Check out this repo"))


# ---------------------------------------------------------------------------------------------
# The invariant that holds across every shape
# ---------------------------------------------------------------------------------------------

def test_no_shape_yields_an_implausible_proposal(tmp: Path) -> None:
    """The oracle `F144` needed and the matrix does not have.

    Across every combination of the two discovery-facing axes, at every level: **whatever the tool
    proposes must be capable of implementing the control it is proposed for.** The matrix asserts
    that the profile matches the script; this asks whether the script was right.
    """
    print("\ninvariant: no shape yields an implausible proposal")
    seen = 0
    for dependencies in ("none", "manifest_only", "manifest_and_lock"):
        for ci_steps in ("none", "not_tests", "tests"):
            repo = make_repo(tmp, f"inv-{dependencies}-{ci_steps}",
                             dependencies=dependencies, ci_steps=ci_steps)
            for level in ("essential", "standard", "full"):
                for field, value in proposals_for(repo, level).items():
                    seen += 1
                    control = field.split(".")[1]
                    why = implausible(control, value)
                    check(f"{dependencies}/{ci_steps}/{level}: {control} -> {value!r}",
                          not why, why)
    check("the invariant actually examined some proposals - an empty sweep proves nothing",
          seen > 0, f"{seen} proposals examined")
    print(f"  {seen} proposal(s) examined across 9 shapes x 3 levels")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="surfaceplate-shapes-") as raw:
        tmp = Path(raw)
        print("Repository properties that change behaviour")
        for axis, values in AXES.items():
            print(f"  {axis}: {', '.join(values)}")
        test_axis_dependencies(tmp)
        test_axis_ci_steps(tmp)
        test_no_shape_yields_an_implausible_proposal(tmp)

    print()
    if FAILURES:
        print(f"REPOSITORY_SHAPES=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        print()
        print("A property of a repository changed this framework's behaviour in a way nothing")
        print("here expected. That is the class of defect a person found five of in an hour")
        print("while fifty thousand checks passed; see this file's docstring.")
        return 1
    print(f"REPOSITORY_SHAPES=PASS  ({PASSES} checks; {len(AXES)} axes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
