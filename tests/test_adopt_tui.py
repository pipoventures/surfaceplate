#!/usr/bin/env python3
"""Pilot tests for the Textual interface.

    python tests/test_adopt_tui.py

No test framework: Textual's `App.run_test()` is an async context manager yielding a `Pilot`, and
`asyncio.run` drives it perfectly well from a plain script, which is what lets these live alongside
this repository's other hand-rolled suites. (Checked against Textual's real API before the design
was settled, not assumed - `App.run` is not a coroutine function, and `run_test` defaults to an
80x24 viewport.)

**The load-bearing test here is the join.** `ScriptedInterview` proves the *plan* was fully
answered; `test_provenance.py` proves nothing was written that no answer supplied. Neither proves
that the *screens ask the plan* - a screen that silently dropped a field would satisfy both. The
`field_ids()` join below closes that, and without it the other two suites quietly weaken.

The rest are the things only real keystrokes can establish: that highlighting a conformance level
is not choosing one, that a gate's follow-ups appear only once its status calls for them, and that
an example answer offered as a default survives being typed into rather than being wiped.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from textual.app import App  # noqa: E402
from textual import work  # noqa: E402
from textual.widgets import RadioButton, RadioSet  # noqa: E402

from surfaceplate.adopt import plan  # noqa: E402
from surfaceplate.adopt.tui.screens import (  # noqa: E402
    FormScreen,
    GatesScreen,
    LevelScreen,
)

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


class Host(App):
    """Hosts one screen so it can be driven in isolation."""

    CSS_PATH = ROOT / "surfaceplate" / "adopt" / "tui" / "app.tcss"

    def __init__(self, screen) -> None:
        super().__init__()
        self._screen_under_test = screen
        self.result = None

    def on_mount(self) -> None:
        self._drive()

    @work
    async def _drive(self) -> None:
        self.result = await self.push_screen_wait(self._screen_under_test)
        self.exit(self.result)


def _a_flow(repo: Path, state: dict, done: tuple[str, ...] = ()):
    """A `Flow` resumed at a given point, with every answer it holds given an origin."""
    from surfaceplate.adopt import flow as _flow
    from surfaceplate.adopt.provenance import TYPED, Origin

    origins = {
        f"{section}.{field}": Origin(TYPED)
        for section, fields in state.items()
        for field in fields
    }
    return _flow.Flow(repo, {"standard_version": "0.0.0", "framework_digest": "0"}, state=state, origins=origins, done=done)


# ---------------------------------------------------------------------------------------------
# The join: every screen renders exactly the fields its plan declares
# ---------------------------------------------------------------------------------------------


async def _join_for(screen, section: plan.SectionPlan):
    """`(id, kind)` on both sides. Comparing ids alone let a screen full of text boxes pass against
    a plan of dropdowns - see `screens.field_shape`."""
    app = Host(screen)
    async with app.run_test(size=(120, 60)) as pilot:
        await pilot.pause()
        rendered = app.screen.field_shape()
    return rendered, [(f.id, f.kind) for f in section.fields]


def test_every_screen_renders_its_whole_plan() -> None:
    async def _run() -> None:
        cases = [
            ("identity", FormScreen(plan.identity_plan()), plan.identity_plan()),
            ("risk", FormScreen(plan.risk_plan()), plan.risk_plan()),
            ("adoption", FormScreen(plan.adoption_plan(owner="x")), plan.adoption_plan(owner="x")),
            ("wrap", FormScreen(plan.wrap_plan()), plan.wrap_plan()),
        ]
        controls = plan.controls_plan(level="standard", mode="simple")
        cases.append(("controls", FormScreen(controls), controls))

        level = plan.level_plan(ROOT, builds_ui=False, mode="simple")
        cases.append(("level", LevelScreen(level), level))

        gates_section = plan.gates_plan(level="standard", builds_ui=False, mode="simple")
        gate_specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple")
        cases.append(("gates", GatesScreen(gate_specs, gates_section), gates_section))

        for name, screen, section in cases:
            rendered, planned = await _join_for(screen, section)
            missing = sorted(set(planned) - set(rendered))
            extra = sorted(set(rendered) - set(planned))
            check(
                f"{name}: the screen renders exactly the fields its plan declares, in the form it "
                f"declares them ({len(planned)} fields)",
                rendered == planned,
                f"missing from screen: {missing[:4]}; not in plan: {extra[:4]}",
            )

    asyncio.run(_run())



def test_the_opening_app_returns_the_three_answers() -> None:
    """`DR-51` (2) and `F68`: Enter on the opening screen begins; with a draft the resume prompt
    follows and `y`/`n` answer it; `Ctrl+Q` anywhere returns `None`, which the wizard reads as
    "cancel, draft kept"."""
    from surfaceplate.adopt.interview import DraftInfo, Welcome
    from surfaceplate.adopt.tui.app import OpeningApp

    def welcome(draft=None) -> Welcome:
        return Welcome(
            repo="/r", tool_name="Surfaceplate", tool_version="0.16.0", tool_anchor="a" * 64,
            licence="Apache-2.0", publisher="Pipo Ventures Ltd", homepage="h", tagline="t",
            installed_version="0.16.0", installed_anchor="a" * 64, installed_at="2026-09-02",
            profile_path="governance/application-profile.yaml",
            provenance_path="governance/application-profile.provenance.yaml", draft=draft,
        )

    draft = DraftInfo(sections=("decisions",), framework_version="0.16.0", framework_digest="a" * 64, matches=True)

    async def drive(w: Welcome, keys: list[str]):
        app = OpeningApp(w)
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            for key in keys:
                await pilot.press(key)
                await pilot.pause()
                await pilot.pause()
        return app.return_value

    check("Enter with no draft begins (True)", asyncio.run(drive(welcome(), ["enter"])) is True)
    check("Ctrl+Q on the opening screen quits (None)", asyncio.run(drive(welcome(), ["ctrl+q"])) is None)
    check("with a draft, Enter then y resumes (True)", asyncio.run(drive(welcome(draft), ["enter", "y"])) is True)
    check("with a draft, Enter then n starts fresh (False)", asyncio.run(drive(welcome(draft), ["enter", "n"])) is False)
    check("with a draft, Enter then Ctrl+Q quits (None)", asyncio.run(drive(welcome(draft), ["enter", "ctrl+q"])) is None)

# ---------------------------------------------------------------------------------------------
# Highlight is not selection (mockup frame 02: "nothing is chosen yet")
# ---------------------------------------------------------------------------------------------


def test_highlighting_a_level_does_not_choose_it() -> None:
    async def _run() -> None:
        section = plan.level_plan(ROOT, builds_ui=False, mode="simple", recap=("No user interface.",))
        app = Host(LevelScreen(section))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            screen = app.screen
            hint = str(screen.query_one("#hint").content)
            meta_first = str(screen.query_one("#level-meta").content)
            await pilot.press("down")
            await pilot.press("down")
            await pilot.pause()
            meta_later = str(screen.query_one("#level-meta").content)
            check("the level screen says nothing is chosen yet", "nothing is chosen yet" in hint, hint)
            check(
                "moving the highlight reveals that level's own controls",
                meta_first != meta_later and meta_later.strip(),
                f"{meta_first!r} -> {meta_later!r}",
            )
            # Leave without pressing Enter. Nothing may have been recorded.
            await pilot.press("ctrl+q")
            await pilot.pause()
        check(
            "moving the highlight without choosing records no level",
            app.result in (None, "__cancelled__"),
            f"result was {app.result!r}",
        )

    asyncio.run(_run())


# ---------------------------------------------------------------------------------------------
# The gate catalogue (mockup frame 03)
# ---------------------------------------------------------------------------------------------


def test_gate_catalogue_behaviour() -> None:
    async def _run() -> None:
        specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple")
        section = plan.gates_plan(level="standard", builds_ui=False, mode="simple")
        app = Host(GatesScreen(specs, section))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            screen = app.screen

            check(
                "every gate in the catalogue is on screen at once, not paged",
                len(screen.query(".gate")) == len(specs) == 19,
                f"{len(screen.query('.gate'))} gate blocks for {len(specs)} specs",
            )

            answers = screen._answers()
            check(
                "a gate whose status is a free choice starts with no status",
                answers.get("test_convention.status") is None,
                str(answers.get("test_convention.status")),
            )

            owner_row = screen.query_one("#row-test_convention--owner")
            check("a deferred gate's owner field is hidden until it is deferred", not owner_row.display)

            screen.query_one("#chip-test_convention--deferred").value = True
            await pilot.pause()
            check(
                "choosing deferred reveals that gate's own follow-ups, inline",
                owner_row.display,
            )
            check(
                "and records the status it was given",
                screen._answers().get("test_convention.status") == "deferred",
            )
            check(
                "the chosen option is the only one selected",
                screen.query_one("#chip-test_convention--deferred").value
                and not screen.query_one("#chip-test_convention--required").value,
                "a radio set must hold exactly one selection",
            )

            hint = str(screen.query_one("#hint").content)
            check("the hint counts what is complete", "of 19 complete" in hint, hint)

            # `ctrl+g`, not a bare `g`: a focused text field would swallow a printable key.
            before = screen.query_one("#gate-list").scroll_offset.y
            await pilot.press("ctrl+g")
            await pilot.press("ctrl+g")
            await pilot.pause()
            after = screen.query_one("#gate-list").scroll_offset.y
            check("ctrl+g jumps between section headings", after != before, f"{before} -> {after}")

            await pilot.press("ctrl+q")
            await pilot.pause()

    asyncio.run(_run())


def test_an_empty_choice_is_refused_at_the_field() -> None:
    """`F64`. `validators.check` returned `None` for any non-string, and an unpressed `RadioSet`
    reads as `None` - so `Ctrl+S` on the first screen with nothing chosen advanced with
    `mode: None`, and three screens later `plan.py` looked up `LEVEL_CHOICE[None]` inside the
    worker: a black terminal with no message. The module's own docstring says an empty string is
    never a decision; `None` was."""

    async def _run() -> None:
        section = plan.SectionPlan(
            name="choice", title="A choice",
            fields=(plan.FieldSpec(id="pick", label="Pick one", kind="choice",
                                   choices=(("a", "a - the first"), ("b", "b - the second"))),),
        )
        app = Host(FormScreen(section))
        async with app.run_test(size=(100, 34)) as pilot:
            await pilot.pause()
            await pilot.press("ctrl+s")
            for _ in range(3):
                await pilot.pause()
            still_there = isinstance(app.screen, FormScreen) and app.result is None
            hint = str(app.screen.query_one("#hint").content) if still_there else ""
            check(
                "mode: Ctrl+S with no option chosen does not leave the screen",
                still_there,
                f"the screen committed {app.result!r}",
            )
            check(
                "and the hint says which field refused",
                section.fields[0].label in hint,
                f"hint: {hint!r}",
            )
            if still_there:
                app.exit(None)
                await pilot.pause()

    asyncio.run(_run())


def test_a_validation_error_survives_the_focus_move_that_reports_it() -> None:
    """`F74`. On the identity screen with `application_id` blank and focus on `owner`, `Ctrl+S`
    moved focus to the blank field, did not dismiss the screen, and left the hint showing only the
    key legend: `action_commit` wrote the error into the hint and then focused the field, and
    `on_descendant_focus` called `_set_hint()` with no error and erased it. The review's earlier
    image of that error was taken with focus already on the failing field, the one case where it
    survived."""

    async def _run() -> None:
        section = plan.identity_plan()
        app = Host(FormScreen(section))
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            app.screen.query_one("#f-owner").focus()
            await pilot.pause()
            await pilot.press("ctrl+s")
            for _ in range(6):
                await pilot.pause()
            still_there = isinstance(app.screen, FormScreen) and app.result is None
            hint = str(app.screen.query_one("#hint").content) if still_there else ""
            focused = app.screen.focused.id if still_there and app.screen.focused else None
            check("identity: Ctrl+S with application_id blank does not leave the screen", still_there)
            check(
                "and focus has moved to the blank field",
                focused == "f-application_id",
                f"focused: {focused!r}",
            )
            check(
                "and after six pauses the hint still carries the error",
                "This cannot be blank." in hint,
                f"hint: {hint!r}",
            )
            if still_there:
                app.exit(None)
                await pilot.pause()

    asyncio.run(_run())


def test_a_blank_dropdown_is_refused_at_the_field() -> None:
    """`F64`, the other path. A blank `Select` reads as `None`, so a required gate whose artefact
    was never chosen counted as answered, committed, and the review then showed
    `This cannot be written yet: 'artefact'` - a `KeyError` with no way back."""

    async def _run() -> None:
        found = plan.discover.Discovered(artefacts=("activity/register.md",), paths=("src/**",))
        specs = plan.gate_plan(level="essential", builds_ui=False, mode="simple", found=found)
        section = plan.gates_plan(level="essential", builds_ui=False, mode="simple", found=found)
        app = Host(GatesScreen(specs, section))
        async with app.run_test(size=(100, 40)) as pilot:
            await pilot.pause()
            screen = app.screen
            screen.query_one("#f-work_registration--paths").value = "src/**"
            screen.query_one("#f-work_registration--effective_from").value = "2026-01-01"
            await pilot.pause()
            screen._set_hint()
            await pilot.pause()
            hint_before = str(screen.query_one("#hint").content)
            await pilot.press("ctrl+s")
            for _ in range(3):
                await pilot.pause()
            still_there = isinstance(app.screen, GatesScreen) and app.result is None
            hint_after = str(app.screen.query_one("#hint").content) if still_there else ""
            check(
                "a gate whose artefact dropdown is blank is not counted as answered",
                "0 of 1 complete" in hint_before,
                hint_before.splitlines()[-2:],
            )
            check(
                "and Ctrl+S with it blank does not leave the screen",
                still_there,
                f"the screen committed {app.result!r}",
            )
            check(
                "and the hint names the artefact field",
                "artefact" in hint_after.lower() and "blank" in hint_after.lower(),
                f"hint: {hint_after!r}",
            )
            if still_there:
                app.exit(None)
                await pilot.pause()

    asyncio.run(_run())


def test_mandatory_and_masked_gates_are_stated_not_asked() -> None:
    async def _run() -> None:
        specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple")
        section = plan.gates_plan(level="standard", builds_ui=False, mode="simple")
        app = Host(GatesScreen(specs, section))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            screen = app.screen
            answers = screen._answers()
            check(
                "a level-mandatory gate is recorded as required without being offered a choice",
                screen._status_of(next(s for s in specs if s.id == "work_registration"), answers)
                == "required"
                and not screen.query(f"#chip-work_registration--deferred"),
            )
            check(
                "an interface gate in a repository with no UI is settled, not asked",
                screen._status_of(next(s for s in specs if s.id == "component_library"), answers)
                == "not_applicable"
                and not screen.query(f"#chip-component_library--required"),
            )
            await pilot.press("ctrl+q")
            await pilot.pause()

    asyncio.run(_run())


# ---------------------------------------------------------------------------------------------
# The Phase 1 feature this rebuild could have silently destroyed
# ---------------------------------------------------------------------------------------------


def test_example_defaults_survive_being_typed_into() -> None:
    """Textual's `Input` starts with its whole value selected, so a first keystroke replaces it.
    Every example answer `example_answers.py` offers is a preset value, so without `EditableInput`
    this rebuild would have quietly undone `DR-35`'s recognition-over-recall feature. Found by
    probing the widget, not by reading about it."""

    async def _run() -> None:
        section = plan.controls_plan(level="essential", mode="simple")
        spec = next(f for f in section.fields if f.id == "scanner.name")
        app = Host(FormScreen(section))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            screen = app.screen
            widget = screen.query_one("#f-scanner--name")
            check("the example default is shown in the field", widget.value == spec.default == "gitleaks")
            widget.focus()
            await pilot.pause()
            await pilot.press("2")
            check(
                "typing edits the shown example rather than wiping it",
                widget.value == "gitleaks2",
                f"value became {widget.value!r}",
            )
            await pilot.press("ctrl+q")
            await pilot.pause()

    asyncio.run(_run())


def test_a_choice_field_starts_genuinely_empty() -> None:
    async def _run() -> None:
        section = plan.risk_plan()
        app = Host(FormScreen(section))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            screen = app.screen
            radios = screen.query_one("#f-data_classification")
            pressed = [b for b in radios.query(RadioButton) if b.value]
            check(
                "a data-classification option is never pre-selected on the human's behalf",
                not pressed,
                f"pre-selected: {[b.id for b in pressed]}",
            )
            await pilot.press("ctrl+q")
            await pilot.pause()

    asyncio.run(_run())


def test_discovered_candidates_are_offered_as_choices() -> None:
    """`DR-38`: a structural answer is picked from what is really in the repository."""

    async def _run() -> None:
        from textual.widgets import Select, SelectionList

        from surfaceplate.adopt import discover

        found = discover.scan(ROOT)
        specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple", found=found)
        section = plan.gates_plan(level="standard", builds_ui=False, mode="simple", found=found)
        app = Host(GatesScreen(specs, section))
        async with app.run_test(size=(110, 50)) as pilot:
            await pilot.pause()
            screen = app.screen

            artefact = screen.query_one("#f-work_registration--artefact")
            check(
                "the precondition artefact is a dropdown of real files, not a blank box",
                isinstance(artefact, Select),
                type(artefact).__name__,
            )
            offered = [v for _prompt, v in artefact._options if isinstance(v, str)]
            check(
                "and every file it offers actually exists in the repository",
                offered and all((ROOT / str(v)).exists() for v in offered),
                str(offered[:3]),
            )
            check(
                "nothing is pre-selected, so a value nobody picked is not an answer",
                artefact.is_blank(),
                str(artefact.value),
            )

            # `ACT-032`: derived by `sections.build_gate`, so the screen must not ask for them.
            # Asserted against the real screen rather than the plan, because `F39` established that
            # a plan and the screen built from it can disagree.
            #
            # `effective_from` was on this list and came OFF it at `F51`: the binding rule names it
            # as a human decision, and deriving it picked the narrowest audit window the rules
            # allow. It is asked again, and asserted as asked below.
            derived = [
                "precondition_description",
                "gated_description",
                "enforcement",
            ]
            still_asked = [
                name
                for name in derived
                if screen.query(f"#f-work_registration--{name}")
            ]
            check(
                "effective_from IS asked on the gate screen (F51)",
                bool(screen.query("#f-work_registration--effective_from")),
                "the field the binding rule reserves to the human is not on the screen",
            )
            check(
                "the three derived gate fields are not asked on the gate screen",
                not still_asked,
                f"still rendered as fields: {still_asked}",
            )

            paths = screen.query_one("#f-work_registration--paths")
            check(
                "a pathspec stays typeable, with real directories offered as completions",
                paths.suggester is not None,
                "no suggester attached",
            )
            await pilot.press("ctrl+q")
            await pilot.pause()

    asyncio.run(_run())


def test_the_app_itself_gives_every_screen_the_repository_scan() -> None:
    """The join tests build both sides themselves, so they cannot see the app wiring two screens
    from different sources - which is exactly what happened.

    `tui/app.py` built the gate catalogue from `plan.gate_plan(...)` with no scan while the
    controls screen went through `section_plan`, which scans. Every gate artefact became a text
    box, the ids matched, every test passed, and a real adoption produced seven gates reading
    `asdf`. This drives the REAL `AdoptApp` and asserts what the gates screen actually renders.
    """

    async def _run() -> None:
        import subprocess
        import tempfile

        from textual.widgets import Select

        from surfaceplate.adopt.tui.app import AdoptApp
        from surfaceplate.adopt.tui.screens import GatesScreen

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / "docs").mkdir(parents=True)
            (repo / "docs" / "REGISTER.md").write_text("# register\n", encoding="utf-8")
            for args in (
                ["init", "-q"], ["config", "user.email", "h@e.i"],
                ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"],
            ):
                subprocess.run(["git", "-C", str(repo), *args], check=True)
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "seed"], check=True)

            # Resume straight into the gates stage so the app builds that screen for real.
            resumed = {
                "mode": {"mode": "simple"},
                "identity": {"application_id": "x", "display_name": "X", "owner": "O"},
                "stack": {"language": "Python", "builds_user_interface": False},
                "risk": {"risk_profile": "r", "materiality_definition": "m",
                         "data_classification": "internal"},
                "level": {"conformance_level": "standard"},
            }
            app = AdoptApp(flow=_a_flow(repo, resumed, done=("decisions", "level")), on_progress=lambda: None)
            async with app.run_test(size=(120, 60)) as pilot:
                await pilot.pause()
                for _ in range(6):
                    if isinstance(app.screen, GatesScreen):
                        break
                    await pilot.pause()
                gates_screen = app.screen
                is_gates = isinstance(gates_screen, GatesScreen)
                artefact = (
                    gates_screen.query_one("#f-work_registration--artefact") if is_gates else None
                )
                check(
                    "the app reaches the gate catalogue",
                    is_gates,
                    type(gates_screen).__name__,
                )
                check(
                    "and the app's own gate screen offers discovered files, not a blank text box",
                    isinstance(artefact, Select),
                    f"rendered as {type(artefact).__name__} - the scan did not reach this screen",
                )
                app.exit(None)
                await pilot.pause()

    asyncio.run(_run())


def test_the_level_screen_settles_instead_of_looping() -> None:
    """`F46`. The level screen span in an unbounded event loop whenever the caret did not start at 0.

    `_move_caret` rebuilt the options with `clear_options()`, which resets the highlight to 0 and
    posts an `OptionHighlighted`; that arrived back in `_move_caret` and rebuilt again. Starting at
    0 it settled, because the reset landed on the value it already had. `ACT-032` started the caret
    on the recommended level, and from any non-zero index the events alternated 2, 0, 2, 0 forever.

    **Every `ACT-032` assertion passed against this**, because they read `highlighted` after a
    single `pause()` and it is 2 on half the iterations. Counting the work is what sees it, so this
    counts `_move_caret` calls rather than inspecting state.
    """

    async def _run() -> None:
        from surfaceplate.adopt.tui import screens as screens_module

        calls: list[object] = []
        original = screens_module.LevelScreen._move_caret

        def counted(self, highlighted):
            calls.append(highlighted)
            return original(self, highlighted)

        screens_module.LevelScreen._move_caret = counted
        try:
            risk = {"relied_on_outside_team": True, "material_quantitative_output": True}
            section = plan.level_plan(ROOT, builds_ui=False, mode="simple", risk=risk)
            app = Host(LevelScreen(section, recommended="full"))
            async with app.run_test(size=(80, 30)) as pilot:
                await pilot.pause()
                await pilot.pause()
                meta = str(app.screen.query_one("#level-meta").content)
        finally:
            screens_module.LevelScreen._move_caret = original

        check(
            "showing the level screen does not loop redrawing itself",
            len(calls) <= 4,
            f"_move_caret ran {len(calls)} times for one paint: {calls[:12]}",
        )
        check(
            "and it settles describing the level the caret is on",
            "full checks:" in meta,
            f"settled on the wrong level: {meta.strip()[:60]!r}",
        )

    asyncio.run(_run())


def test_the_step_counter_agrees_with_the_sections() -> None:
    """`F45`. The progress indicator was hand-written and disagreed with the wizard it describes.

    `route` had no entry at all, so that screen showed no step; `adoption` and `wrap` both read
    `7 of 7`, so an adopter answered "7 of 7" and was handed another "7 of 7"; and the total said
    seven while `SECTION_ORDER` holds ten. A counter that cannot be trusted about where you are is
    worse than none, because it is read as a promise about how much is left.
    """
    from surfaceplate.adopt.tui import app as tui_app

    labelled = {name: step for name, step in tui_app._STEPS.items() if step}
    missing = [n for n in plan.FLOW if n not in tui_app._STEPS]
    check(
        "every screen in FLOW has a step label",
        not missing,
        f"no step label for: {missing}",
    )
    duplicates = sorted({s for s in labelled.values() if list(labelled.values()).count(s) > 1})
    check(
        "no two sections claim the same step",
        not duplicates,
        f"shared by more than one section: {duplicates}",
    )
    totals = {step.split(" of ")[1].split(" ")[0] for step in labelled.values() if " of " in step}
    check(
        "every step names the same total",
        len(totals) == 1,
        f"the run claims more than one total: {sorted(totals)}",
    )


def test_a_gate_with_nothing_supplied_is_not_counted_as_answered() -> None:
    """`F43`. The counter told the adopter a section was complete before anything was supplied.

    `_answered_count` counted a gate whenever it HAD a status, and a mandatory gate's status is
    fixed by the level, not chosen by the human - so at `essential` the hint read `1 of 1 answered`
    with the precondition dropdown empty and `Gated paths` blank. A status the level settled is not
    an answer anyone gave.

    Both directions are asserted, because a counter stuck at zero would pass the first half.
    """

    async def _run() -> None:
        found = plan.discover.Discovered(artefacts=("activity/register.md",), paths=("src/**",))
        specs = plan.gate_plan(level="essential", builds_ui=False, mode="simple", found=found)
        section = plan.gates_plan(level="essential", builds_ui=False, mode="simple", found=found)
        app = Host(GatesScreen(specs, section))
        async with app.run_test(size=(100, 40)) as pilot:
            await pilot.pause()
            screen = app.screen
            empty_hint = str(screen.query_one("#hint").content)

            screen.query_one("#f-work_registration--artefact").value = "activity/register.md"
            screen.query_one("#f-work_registration--paths").value = "src/**"
            await pilot.pause()
            screen._set_hint()
            await pilot.pause()
            filled_hint = str(screen.query_one("#hint").content)

        check(
            "an untouched required gate is not counted as answered",
            "0 of 1 complete" in empty_hint,
            f"hint claimed completion with nothing supplied: {empty_hint!r}",
        )
        check(
            "and it IS counted once its artefact and paths are supplied",
            "1 of 1 complete" in filled_hint,
            f"hint never counts a completed gate: {filled_hint!r}",
        )

    asyncio.run(_run())


def test_a_resumed_run_still_offers_an_artefact_that_was_never_created() -> None:
    """`ACT-035`, closing the hole `ACT-033` left. The defect the adversarial review found, and the
    first fix for it, which did not work.

    Accepted scaffold offers travel under `wizard.SCAFFOLD_KEY`, which is not persisted to the
    draft; the artefact PATH is written into the gate answers, which is. So a run cancelled at the
    review and resumed used to skip the completed gates section, never re-run the offer, and write a
    profile naming a file nobody had created - the `SP032` failure the code above it claims to
    prevent.

    **Moving the offer before the review fixed only half of it.** The condition still asked whether
    the artefact ANSWER was blank, and on resume it is not - it holds the path from the cancelled
    run. The gate was skipped and the file stayed missing. The condition has to ask about the FILE.
    That second failure was found by reproducing the first, which is the whole argument for
    reproducing rather than reasoning.
    """

    async def _run() -> None:
        import subprocess
        import tempfile

        from surfaceplate.adopt import scaffold
        from surfaceplate.adopt.tui.app import AdoptApp
        from surfaceplate.adopt.tui.screens import ScaffoldScreen

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir(parents=True)
            (repo / "main.py").write_text("x = 1\n", encoding="utf-8")
            for args in (
                ["init", "-q"], ["config", "user.email", "h@e.i"],
                ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"],
            ):
                subprocess.run(["git", "-C", str(repo), *args], check=True)
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "seed"], check=True)

            seed_path = scaffold.SEEDABLE["work_registration"][0]
            # Exactly the state a cancelled-then-resumed run carries: the gates section is complete
            # and names the artefact, and the file does not exist because the run never got to the
            # write.
            resumed = {
                "mode": {"mode": "simple"},
                "identity": {"application_id": "x", "display_name": "X", "owner": "O"},
                "stack": {"language": "Python", "builds_user_interface": False},
                "risk": {
                    "risk_profile": "r", "materiality_definition": "m",
                    "relied_on_outside_team": False, "material_quantitative_output": False,
                    "data_classification": "internal",
                },
                "level": {"conformance_level": "essential"},
                "controls": {},
                "gates": {
                    "work_registration.artefact": seed_path,
                    "work_registration.paths": "**",
                },
                # Every remaining section too: the run must reach the OFFER, and a section left out
                # here would stop it on that form instead - which is a fixture stopping the run,
                # not the product doing so.
                "adoption": {
                    "review_by": "2027-03-01", "framework_maintainer": "O",
                    "repository_classification": "internal-tool",
                    "decision_record_id": "DR-1", "adoption_status": "in_progress",
                    "needs_validator": False,
                },
                "wrap": {"human_roles": "Maintainer - O.", "release_route": "Direct to main."},
            }
            check(
                "precondition: the artefact the resumed draft names does not exist",
                not (repo / seed_path).exists(),
                "fixture is wrong - the file is already there",
            )

            app = AdoptApp(
                flow=_a_flow(repo, resumed, done=("decisions", "level", "gates", "remainder")),
                on_progress=lambda: None,
            )
            reached_offer = False
            async with app.run_test(size=(120, 60)) as pilot:
                await pilot.pause()
                for _ in range(12):
                    if isinstance(app.screen, ScaffoldScreen):
                        reached_offer = True
                        break
                    await pilot.pause()
                app.exit(None)
                await pilot.pause()

        check(
            "a resumed run still reaches the offer for an artefact that was never created",
            reached_offer,
            "the run went straight to review and would have written a profile naming a missing file",
        )

    asyncio.run(_run())


def test_the_app_hands_the_level_recommendation_to_the_screen() -> None:
    """`ACT-032`, guarded the way `F39` taught. The plan can compute a recommendation and the app
    can still fail to pass it, in which case the note advises one level while the caret sits on
    another - so this drives the REAL `AdoptApp` rather than constructing `LevelScreen` here.

    The second assertion is the one that keeps this honest: moving the caret must not choose. A
    recommendation that quietly became the answer would breach `core/CONFORMANCE_LEVELS.md`.
    """

    async def _run() -> None:
        import subprocess
        import tempfile

        from surfaceplate.adopt.tui.app import AdoptApp
        from surfaceplate.adopt.tui.screens import LevelScreen

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir(parents=True)
            (repo / "main.py").write_text("x = 1\n", encoding="utf-8")
            for args in (
                ["init", "-q"], ["config", "user.email", "h@e.i"],
                ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"],
            ):
                subprocess.run(["git", "-C", str(repo), *args], check=True)
            subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "seed"], check=True)

            # Answered up to and including `risk`, so the app builds the level screen for real.
            # These two answers mean `full` in the framework's own words.
            resumed = {
                "mode": {"mode": "simple"},
                "identity": {"application_id": "x", "display_name": "X", "owner": "O"},
                "stack": {"language": "Python", "builds_user_interface": False},
                "risk": {
                    "risk_profile": "r",
                    "materiality_definition": "m",
                    "relied_on_outside_team": True,
                    "material_quantitative_output": True,
                    "data_classification": "internal",
                },
            }
            app = AdoptApp(flow=_a_flow(repo, resumed, done=("decisions",)), on_progress=lambda: None)
            async with app.run_test(size=(120, 60)) as pilot:
                await pilot.pause()
                for _ in range(6):
                    if isinstance(app.screen, LevelScreen):
                        break
                    await pilot.pause()
                screen = app.screen
                is_level = isinstance(screen, LevelScreen)
                options = screen.query_one("#f-conformance_level") if is_level else None
                check(
                    "the app reaches the conformance-level screen",
                    is_level,
                    type(screen).__name__,
                )
                check(
                    "and its caret starts on the level the adopter's answers point at",
                    is_level and options.highlighted == 2,  # full
                    f"caret at {getattr(options, 'highlighted', None)}, expected 2 (full)",
                )
                check(
                    "while nothing is chosen, so the recommendation is not the answer",
                    is_level and not screen.section.fields[0].default,
                    "the level field carries a default, which pre-selects on the human's behalf",
                )
                # `F45`: the meta line described `essential` while the caret sat on `full`, because
                # `_update_meta` ran on mount before the programmatic highlight fired an event. It
                # corrected itself on the first arrow press, so only a first-paint check sees it.
                meta = str(screen.query_one("#level-meta").content) if is_level else ""
                check(
                    "and the meta line describes the level the caret is actually on",
                    "full checks:" in meta,
                    f"meta describes a different level than the caret: {meta.strip()!r}",
                )
                app.exit(None)
                await pilot.pause()

    asyncio.run(_run())


def _git_repo_with_a_register(tmp: Path) -> Path:
    """A small repository with things to discover: a register, a source directory, a workflow
    with a named step, and a lock file."""
    import subprocess

    repo = tmp / "repo"
    (repo / "activity").mkdir(parents=True)
    (repo / "activity" / "register.md").write_text("# register\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "main.py").write_text("print(1)\n", encoding="utf-8")
    (repo / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "jobs:\n  build:\n    steps:\n      - name: Run the unit tests\n        run: pytest\n"
        "      - name: gitleaks\n        run: gitleaks detect\n",
        encoding="utf-8",
    )
    for args in (
        ["init", "-q"], ["config", "user.email", "h@e.i"],
        ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"],
        ["add", "-A"], ["commit", "-qm", "seed"],
    ):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    return repo


_RECORD = {"standard_version": "0.0.0", "framework_digest": "0"}

_PRESENTED_KINDS = ("text", "textarea", "select", "choice")


def _unfilled_on(screen) -> list[str]:
    """Fields a screen presents with nothing in them: a visible text box, text area, dropdown or
    radio set holding no value. A tick box and a tick list always show a state."""
    from surfaceplate.adopt.tui.screens import _read_widget

    if isinstance(screen, GatesScreen):
        pairs = [(f"{spec.id}.{f.id}", f.kind) for spec in screen.specs for f in spec.fields]
    else:
        pairs = [(spec.id, spec.kind) for spec in screen.section.fields]
    blank: list[str] = []
    for field_id, kind in pairs:
        if kind not in _PRESENTED_KINDS:
            continue
        row = screen.query_one(f"#row-{field_id.replace('.', '--')}")
        if not row.display:
            continue
        value = _read_widget(screen.query_one(f"#f-{field_id.replace('.', '--')}"))
        if value is None or value == "":
            blank.append(field_id)
    return blank


def _fill_blanks(screen, blank: list[str]) -> None:
    """What a human does with a field nothing could propose: answers it, with something the
    fixture repository really holds where the field checks git."""
    from textual.widgets import Select, TextArea

    real = {"tracked_path": "activity/register.md", "ci_step": "Run the unit tests"}
    specs = {spec.id: spec for spec in screen.section.fields}
    for field_id in blank:
        widget = screen.query_one(f"#f-{field_id.replace('.', '--')}")
        answer = real.get(getattr(specs.get(field_id), "validate", ""), "answered by the driver")
        if isinstance(widget, Select):
            widget.value = widget._options[1][1] if len(widget._options) > 1 else widget._options[0][1]
        elif isinstance(widget, RadioSet):
            widget.query(RadioButton).first().value = True
        elif isinstance(widget, TextArea):
            widget.text = answer
        else:
            widget.value = answer




async def _until(app, pilot, screen_type, *, name: str | None = None, limit: int = 60):
    """Pause until the app shows `screen_type` (and, for a form, the section `name`)."""
    for _ in range(limit):
        await pilot.pause()
        screen = app.screen
        if isinstance(screen, screen_type) and (name is None or getattr(getattr(screen, "section", None), "name", None) == name):
            return screen
    raise AssertionError(f"never reached {screen_type.__name__} {name or ''}; on {type(app.screen).__name__}")


async def _fill_decisions(screen, pilot, *, relied: str = "yes", material: str = "no") -> None:
    from textual.widgets import TextArea

    screen.query_one("#f-identity--owner").value = "Owner Person"
    for field, value in (
        ("stack.builds_user_interface", "no"),
        ("risk.relied_on_outside_team", relied),
        ("risk.material_quantitative_output", material),
        ("risk.data_classification", "internal"),
    ):
        screen.query_one(f"#r-{field.replace('.', '--')}--{value}", RadioButton).value = True
    screen.query_one("#f-wrap--release_route", TextArea).text = "Merged by the maintainer."
    await pilot.pause()
    await pilot.press("ctrl+s")


def test_the_flow_is_decisions_level_gates_review() -> None:
    """`DR-47` / R1 / R3, driven on the real `AdoptApp` at 80x24.

    The screens are the decisions form, the level, the gate list and the review; there is no
    route screen and no proposals screen. On the gate list an unmandated gate starts with no
    status; `n` offers the example rationale; `Ctrl+N` declares every remaining gate not
    applicable as one recorded act with its count. On the review every value carries its origin,
    Enter changes a line and the changed line becomes typed with a timestamp, and `Ctrl+S`
    approves the document once. `F69`, `F62`, `F76` and the question count are what this holds.
    """

    async def _run() -> None:
        import tempfile

        from textual.widgets import Input, OptionList, TextArea

        from surfaceplate.adopt import example_answers, flow as _flow, provenance
        from surfaceplate.adopt.tui.app import AdoptApp
        from surfaceplate.adopt.tui.screens import EditLineScreen, ReviewScreen, ScaffoldScreen

        with tempfile.TemporaryDirectory() as tmp:
            repo = _git_repo_with_a_register(Path(tmp))
            flow = _flow.Flow(repo, _RECORD)
            saves: list[str] = []
            app = AdoptApp(flow=flow, on_progress=lambda: saves.append(flow.next_stage()))
            seen: list[str] = []
            async with app.run_test(size=(80, 24)) as pilot:
                decisions = await _until(app, pilot, FormScreen, name="decisions")
                seen.append("decisions")
                check(
                    "the first screen is the decisions form, pre-filled from the directory name",
                    decisions.query_one("#f-identity--application_id", Input).value == "repo",
                    decisions.query_one("#f-identity--application_id", Input).value,
                )
                presented = [spec.id for spec in decisions.section.fields]
                check(
                    "the decisions form presents the eight fields and nothing discovery answered",
                    len(presented) == 8 and "controls.scanner.wired_in" not in presented,
                    str(presented),
                )
                await _fill_decisions(decisions, pilot)
                level = await _until(app, pilot, LevelScreen)
                seen.append("level")
                await pilot.press("enter")  # the caret starts on the recommendation: standard
                gates = await _until(app, pilot, GatesScreen)
                seen.append("gates")
                undecided = [s for s in gates.specs if not s.mandatory and not s.auto_status]
                first = undecided[0]
                radios = gates.query_one(f"#f-{first.id}--status", RadioSet)
                check(
                    "an unmandated gate starts with no status - nothing is pre-marked (DR-47 (4))",
                    radios.pressed_button is None,
                    str(radios.pressed_button),
                )
                check(
                    "a required gate's artefact holds the discovered proposal",
                    gates.query_one("#f-work_registration--artefact").value == "activity/register.md",
                    str(gates.query_one("#f-work_registration--artefact").value),
                )
                radios.focus()
                await pilot.pause()
                await pilot.press("n")
                await pilot.pause()
                rationale = gates.query_one(f"#f-{first.id}--rationale", TextArea)
                check(
                    "n on the focused gate chooses not applicable and offers the example rationale",
                    radios.pressed_button is not None
                    and radios.pressed_button.id.endswith("not_applicable")
                    and rationale.text == example_answers.rationale_example(first.id),
                    f"pressed={radios.pressed_button and radios.pressed_button.id} text={rationale.text[:40]!r}",
                )
                await pilot.press("ctrl+n")
                await pilot.pause()
                hint = str(gates.query_one("#hint").content)
                check(
                    "Ctrl+N declares every remaining undecided gate not applicable, and says how many",
                    len(gates.bulk_gates) == len(undecided) - 1 and "0 undecided" in hint,
                    f"bulk={len(gates.bulk_gates)} of {len(undecided)}; hint={hint.splitlines()[0]!r}",
                )
                await pilot.press("ctrl+s")
                # The remainder form, if anything was left; then the scaffold offer.
                for _ in range(40):
                    await pilot.pause()
                    screen = app.screen
                    if isinstance(screen, FormScreen) and screen.section.name == "remainder":
                        seen.append("remainder")
                        _fill_blanks(screen, _unfilled_on(screen))
                        await pilot.pause()
                        await pilot.press("ctrl+s")
                    elif isinstance(screen, ScaffoldScreen):
                        seen.append("scaffold")
                        await pilot.press("ctrl+s")
                    elif isinstance(screen, ReviewScreen):
                        break
                review_screen = await _until(app, pilot, ReviewScreen)
                seen.append("review")
                review = review_screen.review
                origins = {entry.path: entry.origin for entry in review.lines}
                index = {g.id: i for i, g in enumerate(flow.gate_specs())}
                artefact_path = f"prerequisites[{index['work_registration']}].precondition.artefacts[0]"
                check(
                    "the review shows every line with its origin: typed, discovered, example, computed",
                    origins.get("owner") == "typed"
                    and origins.get("adoption.framework_maintainer", "").startswith("computed")
                    and origins.get(artefact_path) == "discovered"
                    and any(o == "example" for o in origins.values()),
                    str({k: v for k, v in origins.items() if k in ("owner", "adoption.framework_maintainer", artefact_path)})
                    + f"; kinds={sorted(set(origins.values()))}",
                )
                check(
                    "the bulk decision shows as typed on every gate it decided",
                    all(origins.get(f"prerequisites[{index[g]}].status") == "typed" for g in gates.bulk_gates),
                    str({g: origins.get(f"prerequisites[{index[g]}].status") for g in list(gates.bulk_gates)[:3]}),
                )
                target = next(e for e in review.lines if e.path == "adoption.review_by")
                body = review_screen.query_one("#review-body", OptionList)
                body.highlighted = target.line
                await pilot.pause()
                await pilot.press("enter")
                editor = await _until(app, pilot, EditLineScreen)
                editor.query_one("#f-value", Input).value = "2027-01-15"
                await pilot.press("ctrl+s")
                review_screen = await _until(app, pilot, ReviewScreen)
                edited = next(e for e in review_screen.review.lines if e.path == "adoption.review_by")
                check(
                    "editing a line on the review changes the value and its origin becomes typed",
                    edited.origin == "typed" and flow.state["adoption"]["review_by"] == "2027-01-15"
                    and flow.origins["adoption.review_by"].at != "",
                    f"origin={edited.origin} value={flow.state['adoption']['review_by']} at={flow.origins['adoption.review_by'].at!r}",
                )
                await pilot.press("ctrl+s")
                await pilot.pause()
            check(
                "the flow is decisions, level, gates, (remainder, scaffold,) review - and nothing else",
                seen[:3] == ["decisions", "level", "gates"] and seen[-1] == "review" and "route" not in seen,
                str(seen),
            )
            check("approving the review ends the run with a document-level timestamp", isinstance(app.return_value, str) and "T" in app.return_value, str(app.return_value))
            traced = provenance.trace(flow.assemble(), flow.state, flow.origins)
            record = provenance.record(traced, framework_version="0.0.0", approved_at=str(app.return_value), bulk=flow.bulk)
            check(
                "the provenance record carries one bulk decision with its count, and the approval",
                record["bulk_decisions"] == [{"status": "not_applicable", "count": len(gates.bulk_gates), "at": flow.bulk[0].at}]
                and record["approved_at"] == app.return_value,
                str(record.get("bulk_decisions")),
            )
            check("a draft was saved at every stage boundary", len(saves) >= 3, str(saves))

    asyncio.run(_run())


def test_a_placeholder_is_refused_at_the_field_and_the_review_names_the_line() -> None:
    """`F65`. `TBD` typed into a rationale passed the field and was refused at the review, where
    nothing but cancel worked. Now the field refuses it; and where the review does refuse, the
    error names the line, `Ctrl+E` goes to it, and "write it" is not offered."""

    async def _run() -> None:
        import tempfile

        from textual.widgets import OptionList

        from surfaceplate.adopt import flow as _flow
        from surfaceplate.adopt.interview import ScriptedInterview
        from surfaceplate.adopt.provenance import TYPED, Origin
        from surfaceplate.adopt.tui.screens import ReviewScreen

        # At the field.
        app = Host(FormScreen(plan.identity_plan()))
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            screen = app.screen
            screen.query_one("#f-application_id").value = "ok-id"
            screen.query_one("#f-display_name").value = "TBD"
            screen.query_one("#f-owner").value = "O"
            await pilot.pause()
            await pilot.press("ctrl+s")
            await pilot.pause()
            hint = str(screen.query_one("#hint").content) if isinstance(app.screen, FormScreen) else ""
            check(
                "a placeholder is refused where it is typed",
                isinstance(app.screen, FormScreen) and "placeholder" in hint.lower(),
                f"hint={hint!r}",
            )
            app.exit(None)
            await pilot.pause()

        # At the review.
        with tempfile.TemporaryDirectory() as tmp:
            repo = _git_repo_with_a_register(Path(tmp))
            flow = _flow.Flow(repo, _RECORD)
            interview = ScriptedInterview(
                answers={
                    "identity.owner": "O", "stack.builds_user_interface": "no",
                    "risk.relied_on_outside_team": "no", "risk.material_quantitative_output": "no",
                    "risk.data_classification": "internal", "wrap.release_route": "R",
                    "level.conformance_level": "essential",
                },
            )
            interview.collect(flow, on_progress=lambda: None)
            flow._set("adoption.review_by", "", Origin(TYPED))
            review = flow.review()
            check(
                "a blank required value makes the review name the line",
                review.error.startswith("adoption.review_by") and review.error_line is not None,
                f"error={review.error!r} line={review.error_line}",
            )
            app = Host(ReviewScreen(review))
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.pause()
                screen = app.screen
                hint = str(screen.query_one("#hint").content)
                check("and 'write it' is not offered while the error stands", "write it" not in hint, hint)
                body = screen.query_one("#review-body", OptionList)
                body.highlighted = 0
                await pilot.press("ctrl+e")
                await pilot.pause()
                check("Ctrl+E goes to the line", body.highlighted == review.error_line, f"{body.highlighted} vs {review.error_line}")
                await pilot.press("ctrl+s")
                await pilot.pause()
                check("and Ctrl+S does not write", isinstance(app.screen, ReviewScreen) and app.result is None)
                app.exit(None)
                await pilot.pause()

    asyncio.run(_run())


def test_resuming_a_draft_keeps_its_proposals() -> None:
    """`F76`. A draft written after the proposals were made resumed into the full manual flow
    with every proposal gone. The draft now carries every answer and its origin, and a resumed
    run lands where it left off, proposals intact."""

    async def _run() -> None:
        import tempfile

        from surfaceplate.adopt import flow as _flow
        from surfaceplate.adopt.interview import ScriptedInterview
        from surfaceplate.adopt.tui.app import AdoptApp
        from surfaceplate.adopt.tui.screens import ReviewScreen, ScaffoldScreen

        with tempfile.TemporaryDirectory() as tmp:
            repo = _git_repo_with_a_register(Path(tmp))
            first = _flow.Flow(repo, _RECORD)
            interview = ScriptedInterview(
                answers={
                    "identity.owner": "O", "stack.builds_user_interface": "no",
                    "risk.relied_on_outside_team": "no", "risk.material_quantitative_output": "no",
                    "risk.data_classification": "internal", "wrap.release_route": "R",
                    "level.conformance_level": "essential",
                },
                cancel_before="scaffold",
            )
            try:
                interview.collect(first, on_progress=lambda: None)
            except Exception:
                pass
            draft = first.draft()
            resumed = _flow.Flow(repo, _RECORD, state=draft["sections"], origins=_flow.Flow.origins_from(draft), done=tuple(draft["done"]))
            proposed = [k for k, o in resumed.origins.items() if o.kind != "typed"]
            check("the resumed flow still holds every proposed value with its origin", len(proposed) > 10, str(len(proposed)))
            app = AdoptApp(flow=resumed, on_progress=lambda: None)
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.pause()
                screen = app.screen
                for _ in range(10):
                    if isinstance(screen, ScaffoldScreen):
                        await pilot.press("ctrl+s")
                    if isinstance(app.screen, ReviewScreen):
                        break
                    await pilot.pause()
                    screen = app.screen
                on_review = isinstance(app.screen, ReviewScreen)
                origins = {e.path: e.origin for e in app.screen.review.lines} if on_review else {}
                check(
                    "a resumed run lands on the review with the proposals still in it",
                    on_review and origins.get("prerequisites[0].precondition.artefacts[0]") == "discovered",
                    f"{type(app.screen).__name__} {origins.get('prerequisites[0].precondition.artefacts[0]')}",
                )
                app.exit(None)
                await pilot.pause()

    asyncio.run(_run())


def main() -> int:
    print("the join: screens render exactly what their plan declares")
    test_every_screen_renders_its_whole_plan()
    test_the_opening_app_returns_the_three_answers()

    print("\nconformance level (mockup frame 02)")
    test_highlighting_a_level_does_not_choose_it()

    print("\ngate catalogue (mockup frame 03)")
    test_gate_catalogue_behaviour()
    test_mandatory_and_masked_gates_are_stated_not_asked()

    print("\nF64: an empty choice or dropdown is refused where it is made")
    test_an_empty_choice_is_refused_at_the_field()
    test_a_blank_dropdown_is_refused_at_the_field()

    print("\nF74: the error survives the focus move that reports it")
    test_a_validation_error_survives_the_focus_move_that_reports_it()

    print("\ndiscovery (DR-38)")
    test_discovered_candidates_are_offered_as_choices()
    test_the_app_itself_gives_every_screen_the_repository_scan()
    test_the_level_screen_settles_instead_of_looping()
    test_the_step_counter_agrees_with_the_sections()
    test_a_gate_with_nothing_supplied_is_not_counted_as_answered()
    test_a_resumed_run_still_offers_an_artefact_that_was_never_created()
    test_the_app_hands_the_level_recommendation_to_the_screen()

    print("\ndefaults and pre-selection")
    test_example_defaults_survive_being_typed_into()
    test_a_choice_field_starts_genuinely_empty()

    print("\nDR-47: decisions, level, gates, review - proposals shown with their origin")
    test_the_flow_is_decisions_level_gates_review()
    test_a_placeholder_is_refused_at_the_field_and_the_review_names_the_line()
    test_resuming_a_draft_keeps_its_proposals()

    print()
    if FAILURES:
        print(f"ADOPT_TUI=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"ADOPT_TUI=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
