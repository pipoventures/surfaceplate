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
from textual.widgets import RadioButton  # noqa: E402

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
            check("the hint counts what has been answered", "of 19 answered" in hint, hint)

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

            # `ACT-032`: these four are derived by `sections.build_gate`, so the screen must not
            # ask for them. Asserted against the real screen rather than the plan, because `F39`
            # established that a plan and the screen built from it can disagree.
            derived = [
                "precondition_description",
                "gated_description",
                "effective_from",
                "enforcement",
            ]
            still_asked = [
                name
                for name in derived
                if screen.query(f"#f-work_registration--{name}")
            ]
            check(
                "the four derived gate fields are not asked on the gate screen",
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

            # Resume straight into the gates section so the app builds that screen for real.
            resumed = {
                "mode": {"mode": "simple"},
                "identity": {"application_id": "x", "display_name": "X", "owner": "O"},
                "stack": {"language": "Python", "builds_user_interface": False},
                "risk": {"risk_profile": "r", "materiality_definition": "m",
                         "data_classification": "internal"},
                "level": {"conformance_level": "standard"},
                "route": {"route": "customise"},
                "controls": {},
            }
            app = AdoptApp(
                repo=repo, resumed=resumed,
                on_section_complete=lambda *_: None,
                preview=lambda _state: "",
            )
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
    missing = [n for n in plan.SECTION_ORDER if n not in tui_app._STEPS]
    check(
        "every section in SECTION_ORDER has a step label",
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
            "0 of 1 answered" in empty_hint,
            f"hint claimed completion with nothing supplied: {empty_hint!r}",
        )
        check(
            "and it IS counted once its artefact and paths are supplied",
            "1 of 1 answered" in filled_hint,
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
                "route": {"route": "customise"},
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
                repo=repo, resumed=resumed,
                on_section_complete=lambda *_: None,
                preview=lambda _state: "",
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
            app = AdoptApp(
                repo=repo, resumed=resumed,
                on_section_complete=lambda *_: None,
                preview=lambda _state: "",
            )
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


def main() -> int:
    print("the join: screens render exactly what their plan declares")
    test_every_screen_renders_its_whole_plan()

    print("\nconformance level (mockup frame 02)")
    test_highlighting_a_level_does_not_choose_it()

    print("\ngate catalogue (mockup frame 03)")
    test_gate_catalogue_behaviour()
    test_mandatory_and_masked_gates_are_stated_not_asked()

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
