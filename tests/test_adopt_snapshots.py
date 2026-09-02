#!/usr/bin/env python3
"""What every screen looks like at 80x24, held as golden SVG snapshots.

    .venv/bin/python tests/test_adopt_snapshots.py          # runs pytest on this file, prints a count
    .venv/bin/python -m pytest tests/test_adopt_snapshots.py --snapshot-update   # ONLY with a recorded cause

`DR-50` (4) and the review's R6. The twelve hand-rolled suites assert properties; none of them
looked at a whole screen, and every defect the adversarial review found was visual (`F59`'s
invisible radios passed a suite that set `.value` and read it back). This suite renders each
screen on the real stylesheet at the terminal size the review used and compares the SVG with the
one under `tests/__snapshots__/`.

**Snapshots are golden files under the installed tests rule.** A difference is an audit trigger:
investigate the cause before touching the fixture. A deliberate interface change carries its
cause, the delta and a reviewer in the change that regenerates the snapshot, and
`--snapshot-update` is never used to absorb a difference nobody can explain. The suite was seen
to fail on a one-character stylesheet change before it was trusted (`ACT-046`).

Everything rendered here is fixed data - no repository is scanned, no date is today's - so two
runs on two machines produce the same bytes (the spike measured this, report Part II §II.1).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402
from textual import work  # noqa: E402
from textual.app import App  # noqa: E402
from textual.widgets import RadioSet  # noqa: E402

from surfaceplate.adopt import flow as _flow  # noqa: E402
from surfaceplate.adopt import plan, scaffold  # noqa: E402
from surfaceplate.adopt.interview import DraftInfo, Welcome  # noqa: E402
from surfaceplate.adopt.tui.screens import (  # noqa: E402
    EditLineScreen,
    FormScreen,
    GatesScreen,
    LevelScreen,
    ResumeScreen,
    ReviewScreen,
    ScaffoldScreen,
    WelcomeScreen,
)

SIZE = (80, 24)

# A repository as discovery would describe one, fixed rather than scanned.
FOUND = plan.discover.Discovered(
    artefacts=("activity/register.md", "docs/decisions/DR-1.md", "CHANGELOG.md"),
    register_dirs=("governance",),
    lock_files=("requirements.txt",),
    paths=("src/**", "**"),
    ci_steps=("Run the tests",),
)


class Host(App):
    """Hosts one screen so it can be photographed in isolation."""

    CSS_PATH = ROOT / "surfaceplate" / "adopt" / "tui" / "app.tcss"

    def __init__(self, screen) -> None:
        super().__init__()
        self._screen_under_test = screen

    def on_mount(self) -> None:
        self._show()

    @work
    async def _show(self) -> None:
        await self.push_screen_wait(self._screen_under_test)


def _empty_repo() -> Path:
    """A directory with nothing in it, so the level screen's detected signals are fixed."""
    path = Path(tempfile.mkdtemp(prefix="surfaceplate-snapshot-")) / "repo"
    path.mkdir()
    return path


# ---------------------------------------------------------------------------------------------
# the screens, in the order the flow shows them
# ---------------------------------------------------------------------------------------------



def test_welcome_screen(snap_compare) -> None:
    """`DR-51` (2): the opening screen, before the first question."""
    welcome = Welcome(
        repo="/home/someone/github/plutos", tool_name="Surfaceplate", tool_version="0.16.0",
        tool_anchor="01cb1b5892379eef" + "0" * 48, licence="Apache-2.0", publisher="Pipo Ventures Ltd",
        homepage="https://github.com/pipoventures/surfaceplate",
        tagline="a software delivery standard that installs into a repository and checks it against what it publishes",
        installed_version="0.16.0", installed_anchor="01cb1b5892379eef" + "0" * 48, installed_at="2026-09-02",
        profile_path="governance/application-profile.yaml", provenance_path="governance/application-profile.provenance.yaml",
        draft=None,
    )
    assert snap_compare(Host(WelcomeScreen(welcome)), terminal_size=SIZE)


def test_decisions_form(snap_compare) -> None:
    section = plan.decisions_plan(Path("repo"), found=FOUND, proposals={})
    assert snap_compare(Host(FormScreen(section, step="1 of 3 — ")), terminal_size=SIZE)


def test_level_screen(snap_compare) -> None:
    section = plan.level_plan(
        _empty_repo(),
        builds_ui=False,
        mode="simple",
        recap=("No user interface.", "Data classification: internal."),
        risk={"relied_on_outside_team": True, "material_quantitative_output": False},
    )
    assert snap_compare(Host(LevelScreen(section, step="2 of 3 — ", recommended="standard")), terminal_size=SIZE)


def test_gates_list_with_a_focused_status(snap_compare) -> None:
    """The one the review said was missing: a gate's status row, focused, at 80x24 (`F59`)."""
    specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple", found=FOUND)
    section = plan.gates_plan(level="standard", builds_ui=False, mode="simple", found=FOUND)
    first = next(s for s in specs if not s.mandatory and not s.auto_status)

    async def focus_the_status(pilot) -> None:
        pilot.app.screen.query_one(f"#f-{first.id}--status", RadioSet).focus()
        await pilot.pause()

    assert snap_compare(
        Host(GatesScreen(specs, section, step="3 of 3 — ", initial={"work_registration.artefact": "activity/register.md", "work_registration.paths": "src/**", "work_registration.effective_from": "2026-09-01"})),
        terminal_size=SIZE,
        run_before=focus_the_status,
    )


def test_remainder_form(snap_compare) -> None:
    section = plan.SectionPlan(
        name="remainder",
        title="A few things this repository did not answer",
        intro="Nothing in this repository answered these, so they are yours.",
        fields=(
            plan.FieldSpec(id="controls.above_floor", label="Declare any control beyond the essential floor?", kind="multiselect",
                           choices=(("contract_tests", "contract_tests - tests of the contracts"), ("provenance", "provenance - lineage")), validate=""),
            plan.FieldSpec(id="adoption.decision_record_id", label="Adoption decision record ID", help="the record in your decisions directory"),
        ),
    )
    assert snap_compare(Host(FormScreen(section)), terminal_size=SIZE)


def test_scaffold_offer(snap_compare) -> None:
    offers = [
        scaffold.Offer(gate_id="work_registration", path="activity/register.md", seed="activity-register.md", why="a register for naming work before it starts"),
        scaffold.Offer(gate_id=scaffold.DECISION_RECORD_GATE, path=scaffold.DECISION_RECORD[0], seed=scaffold.DECISION_RECORD[1], why=scaffold.DECISION_RECORD[2]),
    ]
    assert snap_compare(Host(ScaffoldScreen(offers)), terminal_size=SIZE)


_RENDERED = """\
# Application Profile — Example
#
# Written by `surfaceplate adopt` on 2026-09-01. The origin of every value below is recorded in
# application-profile.provenance.yaml beside this file.

schema_version: "1.0"
application_id: example
display_name: Example
owner: Owner Person

risk_profile: Not stated at adoption.
materiality_definition: Not stated at adoption.
data_classification: internal

conformance_level: standard

adoption:
  framework_version: 0.16.0
  review_by: 2027-03-01
  framework_maintainer: Owner Person
  decision_record_id: DR-0001
"""


def _review() -> _flow.Review:
    origins = {
        5: ("schema_version", "computed", False, ""),
        6: ("application_id", "computed: = the directory name", True, ""),
        7: ("display_name", "computed: = the directory name", True, ""),
        8: ("owner", "typed", True, ""),
        10: ("risk_profile", "computed", True, ""),
        11: ("materiality_definition", "computed", True, ""),
        12: ("data_classification", "typed", True, ""),
        14: ("conformance_level", "typed", False, "chosen on the level screen"),
        17: ("adoption.framework_version", "fact of record", False, ""),
        18: ("adoption.review_by", "computed", True, ""),
        19: ("adoption.framework_maintainer", "computed: = owner", True, ""),
        20: ("adoption.decision_record_id", "scaffolded", True, ""),
    }
    lines = [_flow.ReviewLine(line=n, path=p, origin=o, editable=e, note=note) for n, (p, o, e, note) in origins.items()]
    return _flow.Review(rendered=_RENDERED, lines=lines)


def test_review(snap_compare) -> None:
    creating = [scaffold.Offer(gate_id=scaffold.DECISION_RECORD_GATE, path=scaffold.DECISION_RECORD[0], seed=scaffold.DECISION_RECORD[1], why="")]
    assert snap_compare(Host(ReviewScreen(_review(), creating=creating, highlight=8)), terminal_size=SIZE)


def test_review_with_an_error(snap_compare) -> None:
    review = _review()
    review.error = "adoption.review_by: This cannot be blank."
    review.error_path = "adoption.review_by"
    assert snap_compare(Host(ReviewScreen(review)), terminal_size=SIZE)


def test_edit_line(snap_compare) -> None:
    spec = plan.FieldSpec(id="review_by", label="Review by", help="180 days is the suggested interval", validate="review_by")
    assert snap_compare(Host(EditLineScreen("adoption.review_by", "2027-03-01", spec)), terminal_size=SIZE)


def test_resume_prompt(snap_compare) -> None:
    info = DraftInfo(sections=("identity", "stack", "risk"), framework_version="0.16.0", framework_digest="abc", matches=False)
    assert snap_compare(Host(ResumeScreen(info)), terminal_size=SIZE)


# ---------------------------------------------------------------------------------------------
# the runner: pytest on this file, with a count on success like every other suite
# ---------------------------------------------------------------------------------------------


class _Count:
    def __init__(self) -> None:
        self.passed = 0
        self.failed: list[str] = []

    def pytest_runtest_logreport(self, report) -> None:
        if report.when != "call":
            return
        if report.passed:
            self.passed += 1
        elif report.failed:
            self.failed.append(report.nodeid)


def main() -> int:
    count = _Count()
    code = pytest.main([__file__, "-q", "-p", "no:cacheprovider", *sys.argv[1:]], plugins=[count])
    print()
    if code != 0 or count.failed:
        print(f"SNAPSHOTS=FAIL  ({len(count.failed)} failed, {count.passed} passed)")
        for name in count.failed:
            print(f"  - {name}")
        print("A changed snapshot is an audit trigger: find the cause before regenerating it.")
        return 1
    print(f"SNAPSHOTS=PASS  ({count.passed} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
