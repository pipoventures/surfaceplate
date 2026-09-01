#!/usr/bin/env python3
"""Creating an artefact a required gate needs.

    python tests/test_scaffold.py

Three properties, and they are not equally interesting.

The **load-bearing** one is that a seed survives `SP032`. `surfaceplate/templates/` all carry
placeholder tokens deliberately (`F15`), so the obvious design - copying a template into place -
would have produced a gate artefact that fails on the very next run.

**Stated precisely, because the first version of this docstring overstated it:** the seeds are
checked with `check_conformance.PLACEHOLDER_PATTERN`, the checker's own regex, imported rather than
copied. Only `work_registration` at `essential` is additionally driven through the real checker end
to end; the other three seeds are regex-checked, not exercised by `SP032` itself. That is a weaker
claim than "asserted against the checker", and it is the true one.

The second is that an existing file is **never** offered. This module may create and may never
replace, and the failure it would otherwise cause - an adopter's real register overwritten with an
empty one - is not recoverable from inside this tool.

The third is that declining writes nothing at all, asserted by hashing the tree rather than by
checking the paths this module happens to know about.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from surfaceplate import check_conformance  # noqa: E402
from surfaceplate.adopt import plan, scaffold  # noqa: E402

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


def tree_digest(root: Path) -> str:
    """Every file's path and bytes, so a write anywhere at all is visible - including one this
    suite does not know to look for."""
    parts = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git/" not in str(p)):
        parts.append(str(path.relative_to(root)).encode())
        parts.append(path.read_bytes())
    return hashlib.sha256(b"\0".join(parts)).hexdigest()


def bare_repo(tmp: Path) -> Path:
    """A repository that was worked on EARLIER TODAY, which is the case `F47` is about.

    The commit is backdated a few hours deliberately. Committing in the same second as the adoption
    instant makes `git log --since=<that instant>` include it - git's boundary is inclusive - so a
    fixture that commits and adopts together tests a coincidence rather than the scenario.
    """
    repo = tmp / "bare"
    repo.mkdir(parents=True)
    (repo / "README.md").write_text("# a small tool\n", encoding="utf-8")
    (repo / "main.py").write_text("x = 1\n", encoding="utf-8")
    for args in (
        ["init", "-q"],
        ["config", "user.email", "h@example.invalid"],
        ["config", "user.name", "H"],
        ["config", "commit.gpgsign", "false"],
    ):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    earlier = (_dt.datetime.now().astimezone() - _dt.timedelta(hours=3)).replace(microsecond=0)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-qm", "bare"],
        check=True,
        env={
            **os.environ,
            "GIT_AUTHOR_DATE": earlier.isoformat(),
            "GIT_COMMITTER_DATE": earlier.isoformat(),
        },
    )
    return repo


def test_a_seed_survives_the_real_checker(tmp: Path) -> None:
    """The constraint that killed the template approach, asserted against the checker itself."""
    repo = bare_repo(tmp)
    written, _problems = scaffold.write(repo, scaffold.offers(repo, list(scaffold.SEEDABLE)))

    check(
        "every seedable gate produced a file in a repository that had none",
        len(written) == len(scaffold.SEEDABLE),
        f"wrote {[p.name for p in written]}",
    )

    bad = [
        p.relative_to(repo)
        for p in written
        if check_conformance.PLACEHOLDER_PATTERN.search(p.read_text(encoding="utf-8"))
    ]
    check(
        "no seed carries a placeholder token the checker rejects (SP032)",
        not bad,
        f"these would fail SP032 the moment they were written: {bad}",
    )
    empty = [p.relative_to(repo) for p in written if not p.read_text(encoding="utf-8").strip()]
    check(
        "and none is empty, which SP032 rejects separately",
        not empty,
        str(empty),
    )
    # The templates are the counterexample, and the reason seeds exist as a separate idea. If this
    # ever stops being true the packet's whole premise is worth re-examining.
    templated = [
        p.name
        for p in sorted((ROOT / "surfaceplate" / "templates").glob("*"))
        if check_conformance.PLACEHOLDER_PATTERN.search(p.read_text(encoding="utf-8"))
    ]
    shipped = list((ROOT / "surfaceplate" / "templates").glob("*"))
    check(
        "while the shipped templates DO carry them, which is why they cannot be scaffolded",
        # `len(a) == len(b)` alone is `0 == 0` if the directory is ever empty or moved - a vacuous
        # pass on the premise the whole packet rests on. The count is asserted non-zero too.
        len(shipped) >= 4 and len(templated) == len(shipped),
        f"{len(shipped)} template(s) shipped; without placeholders: "
        f"{sorted(set(p.name for p in shipped) - set(templated))}",
    )


def test_an_existing_file_is_never_offered(tmp: Path) -> None:
    repo = bare_repo(tmp)
    (repo / "activity").mkdir()
    mine = repo / "activity" / "register.md"
    mine.write_text("# my own register\n\n- ACT-1 something real\n", encoding="utf-8")
    before = mine.read_text(encoding="utf-8")

    offered = [o.path for o in scaffold.offers(repo, list(scaffold.SEEDABLE))]
    check(
        "a path that already exists is absent from the offer entirely",
        "activity/register.md" not in offered,
        f"offered anyway: {offered}",
    )

    # And the second refusal, at the point of writing: a file that appeared between the offer and
    # the write must still not be replaced.
    stale = scaffold.Offer(
        gate_id="work_registration",
        path="activity/register.md",
        seed="activity-register.md",
        why="stale offer built before the file existed",
    )
    scaffold.write(repo, [stale])
    check(
        "and an offer built before the file existed still cannot overwrite it",
        mine.read_text(encoding="utf-8") == before,
        "the adopter's own register was replaced",
    )


def test_declining_writes_nothing(tmp: Path) -> None:
    repo = bare_repo(tmp)
    before = tree_digest(repo)
    scaffold.offers(repo, list(scaffold.SEEDABLE))  # building the offer must not write
    scaffold.write(repo, [])
    check(
        "building an offer and accepting none leaves the repository byte-identical",
        tree_digest(repo) == before,
        "something was written when nothing was accepted",
    )


def test_a_bare_repository_can_reach_a_passing_check(tmp: Path) -> None:
    """**The point of the packet, and what it does and does not achieve.**

    A repository with a README and one Python file adopts at `essential`, accepts the offer, and
    ends with a gate naming a register that really exists. Before this it had nothing to name, so
    the adopter left it blank or pointed it at the closest wrong file - which is `F40`.

    **It does not reach a clean check, and this test says so rather than implying otherwise.**
    `check_conformance.main` returns 0 inside the adoption grace window regardless, so asserting on
    its exit code would assert on the grace period rather than on the profile - a green test resting
    on a grace period is the false green this project exists to find. What is asserted instead: the
    artefact exists, the gate names it rather than the closest wrong file, and the artefact itself
    satisfies every condition `SP032` imposes. That the adoption day's earlier commits still report
    a violation is `F47`, recorded rather than asserted.
    """
    from surfaceplate.adopt import wizard
    from surfaceplate.adopt.interview import ScriptedInterview

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import install_standard  # noqa: E402

    repo = bare_repo(tmp)
    assert install_standard.main(
        ["--source", str(ROOT / "surfaceplate"), "--target", str(repo), "--no-hooks"]
    ) == 0

    answers = {
        "mode.mode": "simple",
        "identity.application_id": "small-tool",
        "identity.display_name": "Small Tool",
        "identity.owner": "Sole maintainer",
        "stack.language": "Python 3.12",
        "stack.builds_user_interface": False,
        "risk.risk_profile": "A local utility; nobody else consumes its output.",
        "risk.materiality_definition": "Nothing it produces is relied on outside this machine.",
        "risk.relied_on_outside_team": False,
        "risk.material_quantitative_output": False,
        "risk.data_classification": "internal",
        "level.conformance_level": "essential",
        "route.route": "customise",
        "controls.agent_work_packets.rationale": "Agent work is briefed before it starts.",
        "controls.actual_diff_review.rationale": "Changes are read as diffs before merging.",
        "controls.secret_hygiene.rationale": "No secrets belong in this repository.",
        "controls.scanner.name": "gitleaks",
        "controls.scanner.wired_in": ".github/workflows/secret-scan.yml",
        "controls.dependency_lock.rationale": "Dependencies are pinned regardless of materiality.",
        "controls.dependency_lock.implementation_reference": "requirements.txt",
        "controls.above_floor": [],
        # The artefact is NOT answered: this is the adopter who has nothing to name, and the
        # scaffold offer is what closes it.
        "gates.work_registration.paths": "**",
        # `F51`: asked again, and answered as the instant of adoption - which is what
        # `app._offer_missing_artefacts` records when the offer is accepted, and what keeps this
        # morning's commits out of scope.
        "gates.work_registration.effective_from": _dt.datetime.now()
        .astimezone()
        .replace(microsecond=0)
        .isoformat(),
        "adoption.review_by": "2027-03-01",
        "adoption.framework_maintainer": "Sole maintainer",
        "adoption.repository_classification": "internal-tool",
        "adoption.decision_record_id": "DR-ADOPT-001",
        "adoption.adoption_status": "in_progress",
        "adoption.needs_validator": False,
        "wrap.human_roles": "Maintainer - sole change authority.",
        "wrap.release_route": "Merged to main by the maintainer.",
    }
    (repo / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    scan = repo / ".github" / "workflows" / "secret-scan.yml"
    scan.parent.mkdir(parents=True, exist_ok=True)
    scan.write_text(
        "jobs:\n  scan:\n    steps:\n      - name: gitleaks\n        run: gitleaks detect\n",
        encoding="utf-8",
    )

    interview = ScriptedInterview(answers)
    offered = scaffold.offers(repo, ["work_registration"])
    check("the bare repository is offered a register", len(offered) == 1, str(offered))

    # What the interface does when the human ticks the offer: the path becomes the gate's answer,
    # and the files travel to `wizard.run` under its own key.
    interview.answers["gates.work_registration.artefact"] = offered[0].path

    # Exactly what `app._offer_missing_artefacts` records on acceptance (`F47`): the gate binds
    # from the INSTANT the artefact was created, so this morning's commits are not inside a window
    # where the precondition was absent.
    state_extra = {wizard.SCAFFOLD_KEY: offered}
    written = wizard.run(repo, _WithScaffold(interview, state_extra))

    check(
        "the register was created where the gate now names it",
        (repo / offered[0].path).is_file(),
        f"missing: {offered[0].path}",
    )
    check("and the run reports it as created", list(written.created) != [], str(written.created))

    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "adopt"], check=True)
    # **Stated as it is, not as hoped.** `check_conformance.main` returns 0 inside the adoption
    # grace window whether or not anything is outstanding, so asserting on its exit code would be
    # asserting on the grace period. The profile is inspected directly instead.
    findings = check_conformance.main(["--repo", str(repo)])
    check(
        "the run produced a profile the checker can read without erroring",
        findings == 0,
        f"check_conformance exited {findings}",
    )
    profile = (repo / "governance" / "application-profile.yaml").read_text(encoding="utf-8")
    check(
        "and the gate names the register that now exists, not the closest wrong file",
        "activity/register.md" in profile and "README.md" not in profile,
        "the gate points somewhere else",
    )
    # `F47`: what is NOT yet true. Asserted on the ARTEFACT rather than on the checker's printed
    # report - the first version of this scraped stdout for "SP035" and failed roughly one run in
    # five with an empty capture, so it was testing the capture as much as the behaviour. What the
    # packet actually contributes is that the thing the gate names satisfies SP032's three
    # conditions; that the adoption-day history does not is `F47`, recorded rather than asserted
    # through a fragile channel.
    register = repo / offered[0].path
    body = register.read_text(encoding="utf-8")
    # `F47` closed: with the gate bound to the instant of adoption rather than to that midnight,
    # the morning's commits are genuinely out of scope and the checker has nothing to report.
    import io, contextlib

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        check_conformance.main(["--repo", str(repo)])
    report = buffer.getvalue()
    check(
        "no gate reports a violation over commits made before the artefact existed (F47)",
        "SP035" not in report,
        "SP035 still fires: " + "; ".join(l.strip() for l in report.splitlines() if "SP035" in l),
    )
    check(
        "the created artefact satisfies every condition SP032 imposes on it",
        register.is_file()
        and body.strip() != ""
        and not check_conformance.PLACEHOLDER_PATTERN.search(body),
        "the artefact the gate now names would itself be rejected",
    )


class _WithScaffold:
    """Wraps a `ScriptedInterview` so the collected state carries the accepted offers, the way the
    real interface does. Kept here rather than in `interview.py`: the scripted interview exists to
    answer *fields*, and teaching it about scaffolding would blur what it proves."""

    def __init__(self, inner, extra: dict) -> None:
        self._inner = inner
        self._extra = extra

    def confirm_resume(self, info) -> bool:
        return self._inner.confirm_resume(info)

    def collect(self, **kwargs) -> dict:
        state = self._inner.collect(**kwargs)
        for key, value in self._extra.items():
            if isinstance(value, dict) and isinstance(state.get(key), dict):
                state[key].update(value)
            else:
                state[key] = value
        return state


def test_a_dangling_symlink_is_not_an_empty_slot(tmp: Path) -> None:
    """Found by adversarial review, and it breached the module's one hard rule.

    `Path.exists()` follows symlinks and returns **False for a dangling one**, so a repository whose
    `CHANGELOG.md` was a broken symlink got an offer - and `write_text` then followed the link and
    created the file **outside the repository**, while the run reported writing it inside. Both
    halves are asserted: nothing is offered, and if an offer is forced through anyway the write
    refuses rather than following the link.
    """
    repo = bare_repo(tmp)
    outside = tmp / "OUTSIDE.txt"
    (repo / "CHANGELOG.md").symlink_to(outside)

    offered = [o.path for o in scaffold.offers(repo, ["change_record_before_completion"])]
    check(
        "a path occupied by a dangling symlink is not offered as empty",
        offered == [],
        f"offered anyway: {offered}",
    )

    forced = scaffold.Offer(
        gate_id="change_record_before_completion",
        path="CHANGELOG.md",
        seed="CHANGELOG.md",
        why="forced past the offer",
    )
    written, problems = scaffold.write(repo, [forced])
    check(
        "and writing through it is refused, so nothing lands outside the repository",
        written == [] and not outside.exists() and problems,
        f"wrote {written}; outside exists: {outside.exists()}",
    )


def test_a_parent_that_is_a_file_does_not_abort_the_run(tmp: Path) -> None:
    """A regular file where a directory is needed used to raise `NotADirectoryError` out of `write`,
    after earlier offers were already on disk and before the profile was written - a half-finished
    adoption ending in a traceback. It is reported and the rest continues."""
    repo = bare_repo(tmp)
    (repo / "docs").write_text("not a directory\n", encoding="utf-8")

    offers = scaffold.offers(repo, ["decision_before_implementation", "work_registration"])
    written, problems = scaffold.write(repo, offers)
    check(
        "an impossible path is reported rather than raised",
        len(problems) == 1 and "decision-log" in problems[0],
        f"problems: {problems}",
    )
    check(
        "and the offers that CAN be created still are",
        [p.name for p in written] == ["register.md"],
        f"written: {[p.name for p in written]}",
    )


def test_only_gates_the_profile_will_require_are_offered() -> None:
    """The narrowing the adversarial review forced, asserted at the level that showed the defect.

    The first version iterated `scaffold.SEEDABLE` and treated any gate with no artefact answer as
    blank. At `essential` the plan asks about ONE gate, so the other three were absent from the
    answers, read as blank, and were offered - pre-ticked, under a heading calling them gates the
    adopter must declare. Accepting wrote three files no gate in the profile referenced.
    """
    from surfaceplate.adopt import discover

    specs = plan.gate_plan(
        level="essential", builds_ui=False, mode="simple", found=discover.Discovered()
    )
    asked = {s.id for s in specs}
    seedable_but_unasked = [g for g in scaffold.SEEDABLE if g not in asked]
    check(
        "at essential, three seedable gates are not asked about at all",
        sorted(seedable_but_unasked)
        == ["authority_map", "change_record_before_completion", "decision_before_implementation"],
        str(seedable_but_unasked),
    )
    check(
        "so the only gate that may be offered a seed there is work_registration",
        asked & set(scaffold.SEEDABLE) == {"work_registration"},
        str(asked & set(scaffold.SEEDABLE)),
    )


def test_only_honestly_seedable_gates_are_offered(tmp: Path) -> None:
    """`full` requires eleven gates; only four can be created as a true statement. The rest are
    left to a human who actually has one, which is the honest half of this feature."""
    repo = bare_repo(tmp)
    offered = {o.gate_id for o in scaffold.offers(repo, ["work_registration", "equivalence_evidence"])}
    check(
        "a gate with no honest seed is not offered one",
        offered == {"work_registration"},
        str(offered),
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        print("a seed is valid the moment it is written")
        test_a_seed_survives_the_real_checker(tmp / "a")
        print("\nand this module may create, never replace")
        test_an_existing_file_is_never_offered(tmp / "b")
        test_declining_writes_nothing(tmp / "c")
        print("\nand only where something true can be created")
        test_only_honestly_seedable_gates_are_offered(tmp / "d")
        test_only_gates_the_profile_will_require_are_offered()

        print("\nand the ways an offer could go wrong (adversarial review)")
        test_a_dangling_symlink_is_not_an_empty_slot(tmp / "f")
        test_a_parent_that_is_a_file_does_not_abort_the_run(tmp / "g")
        print("\nand a bare repository can now finish")
        test_a_bare_repository_can_reach_a_passing_check(tmp / "e")

    print()
    if FAILURES:
        print(f"SCAFFOLD=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"SCAFFOLD=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
