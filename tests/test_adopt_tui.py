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
    _read_widget,
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


class Host(App, inherit_bindings=False):  # as the wizard's own apps (`F73`): Ctrl+Q is the screen's
    """Hosts one screen so it can be driven in isolation."""

    CSS_PATH = ROOT / "surfaceplate" / "adopt" / "tui" / "app.tcss"

    def __init__(self, screen) -> None:
        super().__init__()
        self.animation_level = "none"  # `F95`: as the wizard's own apps; scrolls land exactly
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


def test_every_field_the_plan_asks_for_is_displayed_and_reachable() -> None:
    """The general invariant behind `F143`, asserted for every conditional field on every screen.

    `F143` was one missing `@on(...)` decorator, and the specific test beside this one guards that
    one case. **This asserts the property the decorator was in service of**, so the next
    conditional field cannot rediscover it:

        for every field, on every screen, at every value of the widget that gates it -
        `spec.applies(answers)` must equal *the row is displayed* must equal *the widget is
        reachable*.

    All three, together. A field the plan asks for and the screen hides is `F143`: required, blank,
    invisible, unreachable, and `Ctrl+S` refusing the section for it. A field the plan does not ask
    for and the screen shows is the opposite defect and would be caught by the same equality.

    THE TWO GATING WIDGETS DIFFER, WHICH IS THE POINT. The controls screen's conditional fields are
    gated by a **multiselect** (15 of them at `essential`) and the gates screen's by a **radio set**
    (66 across 19 gates). `F143` existed because the screen listened for one kind of change and not
    the other; an invariant that only tested the kind that worked would have proved nothing.
    """
    import subprocess
    import tempfile

    repo = Path(tempfile.mkdtemp(prefix="surfaceplate-reach-")) / "repo"
    repo.mkdir()
    for args in (["init", "-q"], ["config", "user.email", "h@example.invalid"],
                 ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "package.json").write_text('{"name": "fixture"}\n', encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True,
                   capture_output=True)
    found = plan.discover.scan(repo)

    async def agree(section, gate_id: str, choose) -> tuple[dict, dict, list]:
        """Answer the gating widget, then read back what the screen displays and what it focuses."""
        app = Host(FormScreen(section, repo=repo))
        async with app.run_test(size=(140, 80)) as pilot:
            await pilot.pause()
            gate = app.screen.query_one(f"#f-{gate_id.replace('.', '--')}")
            gate.focus()
            await pilot.pause()
            await choose(pilot, gate)
            await pilot.pause()
            await pilot.pause()
            shown = {
                w.id[len("row-"):].replace("--", "."): w.display
                for w in app.screen.query("*") if w.id and w.id.startswith("row-")
            }
            chain = [w.id[len("f-"):].replace("--", ".")
                     for w in app.screen.focus_chain if getattr(w, "id", "") and w.id.startswith("f-")]
            answers = {gate_id: list(getattr(gate, "selected", []))}
            return shown, dict.fromkeys(chain, True), answers

    async def tick(pilot, widget, index: int):
        for _ in range(index):
            await pilot.press("down")
            await pilot.pause()
        await pilot.press("space")

    checked = 0
    for level in ("essential", "standard"):
        section = plan.controls_plan(level=level, mode="simple", found=found)
        above = next((f for f in section.fields if f.id == "above_floor"), None)
        if above is None:
            continue
        for index, (control, _label) in enumerate(above.choices):
            shown, reachable, answers = asyncio.run(
                agree(section, "above_floor", lambda p, w, i=index: tick(p, w, i))
            )
            for spec in section.fields:
                if spec.depends_on is None or not spec.id.startswith(f"{control}."):
                    continue
                wanted = spec.applies(answers)
                checked += 1
                check(f"{level}/{control}: {spec.id} displayed == the plan asks for it",
                      shown.get(spec.id) == wanted, f"asks={wanted} displayed={shown.get(spec.id)}")
                check(f"{level}/{control}: {spec.id} reachable == the plan asks for it",
                      (spec.id in reachable) == wanted,
                      f"asks={wanted} reachable={spec.id in reachable}")

    # THE OTHER GATING WIDGET. The gates screen's conditional fields hang off a RadioSet, not a
    # multiselect, and `F143` existed precisely because the screen listened for one kind of change
    # and not the other. An invariant that only tested the kind that worked would have proved
    # nothing, so it is asserted here too rather than only claimed in this docstring.
    specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple")
    gates = plan.gates_plan(level="standard", builds_ui=False, mode="simple", found=found)

    async def choose_status(status: str) -> tuple[dict, set, str]:
        app = Host(GatesScreen(specs, gates, repo=repo, level="standard"))
        async with app.run_test(size=(140, 100)) as pilot:
            await pilot.pause()
            # `F91`/`DR-56`: the level's floor opens and the rest is FOLDED under a counted
            # heading. A folded gate's body is hidden, so its fields are legitimately unreachable
            # until `Ctrl+O` opens it - which is the state an adopter answering a beyond-floor
            # gate is actually in. Without this the invariant compared `applies()` against a
            # different visibility axis and reported six failures that were the test's fault.
            await pilot.press("ctrl+o")
            await pilot.pause()
            # DISCOVER the gate to drive rather than naming one, because which gates carry a
            # status choice is not obvious and guessing it twice already produced a test that
            # examined nothing. A gate the LEVEL mandates has no status widget at all - its status
            # is not a choice - and a design gate has none either when the repository builds no
            # interface. What is wanted is a gate that has both a status radio on screen and
            # fields conditional on it.
            gate = next(
                (s for s in specs
                 if any(f.depends_on for f in s.fields) and app.screen.query(f"#f-{s.id}--status")),
                None,
            )
            if gate is None:
                return {}, set(), ""
            radio = app.screen.query(f"#f-{gate.id}--status").first()
            radio.focus()
            await pilot.pause()
            labels = [str(b.label) for b in radio.query("RadioButton")]
            if status not in labels:
                return {}, set(), ""
            for _ in range(labels.index(status)):
                await pilot.press("down")
                await pilot.pause()
            await pilot.press("space")
            await pilot.pause()
            await pilot.pause()
            shown = {
                w.id[len("row-"):].replace("--", "."): w.display
                for w in app.screen.query("*")
                if w.id and w.id.startswith(f"row-{gate.id}--")
            }
            chain = {w.id[len("f-"):].replace("--", ".")
                     for w in app.screen.focus_chain
                     if getattr(w, "id", "") and w.id.startswith(f"f-{gate.id}--")}
            return shown, chain, gate.id

    gate_checked = 0
    for status in ("required", "deferred", "not_applicable"):
        shown, chain, gate_id = asyncio.run(choose_status(status))
        if not gate_id:
            continue
        answers = {"status": status}
        for spec in next(s for s in specs if s.id == gate_id).fields:
            if spec.depends_on is None:
                continue
            wanted = spec.applies(answers)
            key = f"{gate_id}.{spec.id}"
            gate_checked += 1
            check(f"gates/{status}: {key} displayed == the plan asks for it",
                  shown.get(key) == wanted, f"asks={wanted} displayed={shown.get(key)}")
            check(f"gates/{status}: {key} reachable == the plan asks for it",
                  (key in chain) == wanted, f"asks={wanted} reachable={key in chain}")

    check("the invariant examined some fields - an empty sweep proves nothing", checked > 0,
          f"{checked} conditional field(s)")
    check("and it examined BOTH gating widgets, not only the one that worked",
          gate_checked > 0, f"{gate_checked} radio-gated field(s)")
    print(f"  {checked} multiselect-gated and {gate_checked} radio-gated conditional field(s) checked")


def test_every_select_field_can_be_answered_off_the_list() -> None:
    """`F147`. The invariant above asserts every field is DISPLAYED and REACHABLE. Neither of those
    is *answerable*, and that gap is the whole defect.

        for every `select` field, on every screen that renders one, a value the field's own
        validator accepts must be givable - whether or not discovery offered it.

    The maintainer reached `prerequisite_state_ui` on a real repository and could not name the file
    they meant. Thirty candidates existed; twelve were offered; the one they wanted was the
    thirteenth. Textual's `Select` cannot be typed into, that gate is one of the four
    `scaffold.SEEDABLE` deliberately excludes, so there was no "create it" row either - and the
    only remaining exits were to declare the gate `not_applicable`, which is a different answer
    from the true one, or to abandon the run.

    **The constraint was never the standard's.** `flow.py` does not check an answer against
    `spec.choices`; the only gate is the field's validator, and `tracked_path` independently
    requires the path to exist, be tracked, be non-empty, carry no placeholder and not be one this
    framework installed. A scripted adoption (`--answers`) could always name any tracked file. A
    human driving the interface could not. `DR-38`'s rule was *never offer something that isn't
    there*; it had been implemented as the much stronger *never accept anything else*.

    **Why no scripted suite could see it.** The matrix drives `flow`, not the screens - 44,774
    checks, none of which renders a widget. Same blind spot as `F143`, one layer along.

    Both directions, because an escape that accepts anything is a hole and not an escape: a real
    tracked file off the list is accepted, and a path that does not exist is refused in
    `tracked_path`'s own words.
    """
    import subprocess
    import tempfile

    from surfaceplate.adopt import discover

    # More candidates than the cap, so truncation genuinely bites, and a target that sorts BEYOND
    # it: `_ARTEFACT_RANK` puts `docs/` first, and a root-level file after every ranked directory.
    repo = Path(tempfile.mkdtemp(prefix="surfaceplate-offlist-")) / "repo"
    (repo / "docs").mkdir(parents=True)
    for args in (["init", "-q"], ["config", "user.email", "h@example.invalid"],
                 ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    for index in range(discover.SHOWN + 5):
        (repo / "docs" / f"note-{index:03d}.md").write_text(f"# Note {index}\n", encoding="utf-8")
    target = "the-file-they-actually-meant.md"
    (repo / target).write_text("# The register\n\nReal content.\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True,
                   capture_output=True)
    found = discover.scan(repo)

    specs = plan.gate_plan(level="essential", builds_ui=False, mode="simple", found=found)
    section = plan.gates_plan(level="essential", builds_ui=False, mode="simple", found=found)
    artefact = next(f for s in specs if s.id == "work_registration" for f in s.fields if f.id == "artefact")

    check("the fixture truncates - the target is genuinely not among what is offered",
          target not in [value for value, _label in artefact.choices],
          f"{len(artefact.choices)} offered of {len(found.artefacts)} found")

    # THE PLAN SIDE. Every field answered by picking carries the escape, on every section, so the
    # property cannot hold for the one field this test drives and quietly fail for the rest.
    escaped = 0
    for name, built in (
        ("gates", section),
        ("controls", plan.controls_plan(level="full", mode="simple", found=found)),
    ):
        for spec in built.fields:
            if spec.kind != "select":
                continue
            escaped += 1
            check(f"{name}/{spec.id} offers a way off the list",
                  plan.TYPE_A_PATH in [value for value, _label in spec.choices],
                  f"choices: {[v for v, _l in spec.choices][:3]}")
    check("the sweep examined some dropdowns - an empty sweep proves nothing", escaped > 0,
          f"{escaped} select field(s)")

    # AND THE COUNT IT STATES. The prompt said "(12 found)" while thirty were found, and the help
    # said "these are simply the files found here" while showing twelve of them.
    check("the field records how many were found, not only how many it shows",
          artefact.found_total == len(found.artefacts),
          f"found_total={getattr(artefact, 'found_total', None)} found={len(found.artefacts)}")

    async def drive(typed: str) -> tuple[object, object, str]:
        app = Host(GatesScreen(specs, section, repo=repo))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            widget = app.screen.query_one("#f-work_registration--artefact")
            widget.focus()
            await pilot.pause()
            widget.value = plan.TYPE_A_PATH
            await pilot.pause()
            await pilot.pause()
            box = app.screen.query_one("#typed-work_registration--artefact")
            reachable = bool(box.display) and box in app.screen.focus_chain
            box.value = typed
            await pilot.pause()
            read_back = _read_widget(widget) if reachable else "(the box was not reachable)"
            app.screen.query_one("#f-work_registration--paths").value = "**"
            await pilot.pause()
            await pilot.press("ctrl+s")
            for _ in range(3):
                await pilot.pause()
            committed = app.result
            hint = ""
            if isinstance(app.screen, GatesScreen) and committed is None:
                hint = str(app.screen.query_one("#hint").content)
                app.exit(None)
            return committed, read_back, hint

    committed, read_back, _hint = asyncio.run(drive(target))
    check("choosing the escape row reveals a box that reads back what was typed",
          read_back == target, f"read back {read_back!r}")
    check("and Ctrl+S commits the off-list value the validator accepts",
          isinstance(committed, dict) and committed.get("work_registration.artefact") == target,
          repr(committed)[:200])

    # THE NEGATIVE CONTROL. The escape must be an escape, not a hole - the validator still rules.
    committed, _read_back, hint = asyncio.run(drive("nowhere/at/all.md"))
    check("a typed path that does not exist is refused, not committed",
          committed is None, repr(committed)[:200])
    check("and the refusal is the checker's own reason, at the field",
          "nothing exists at that path" in hint.lower(), f"hint: {hint!r}")


def test_the_welcome_screen_offers_both_routes() -> None:
    """`ACT-101`. The AI-assisted route is offered where the choice is actually made.

    A subcommand nobody knows exists is barely a feature, and the person this route is for - the
    one the terminal is an obstacle for - is the least likely to find it in `--help`.

    Asserted in both directions: `[A]` leaves with the agent sentinel, `[Enter]` still begins as
    it always did. Without the second, adding a route could have replaced one.
    """
    from textual.widgets import Static

    from surfaceplate.adopt import wizard
    from surfaceplate.adopt.tui.screens import WelcomeScreen

    welcome = wizard._welcome(
        Path("."),
        {"standard_version": "0.18.0", "framework_digest": "a" * 64, "installed_at": "2026-09-11"},
        None,
        "",
    )

    async def press(key: str) -> tuple[str, object]:
        app = Host(WelcomeScreen(welcome))
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            hint = str(app.screen.query_one("#hint", Static).content)
            await pilot.press(key)
            for _ in range(3):
                await pilot.pause()
            return hint, app.result

    hint, chose = asyncio.run(press("a"))
    check("the welcome screen offers the AI-assisted route in its key line",
          "AI-assisted" in hint, f"hint: {hint!r}")
    check("and it still offers the manual one first", "set it up here" in hint, f"hint: {hint!r}")
    check("[A] leaves with the agent sentinel", chose == WelcomeScreen.AGENT, repr(chose))

    _hint, began = asyncio.run(press("enter"))
    check("[Enter] still begins, unchanged", began is True, repr(began))


def test_the_gates_screen_renders_the_spec_the_plan_built() -> None:
    """`F161`. `_compose_gate_fields` rebuilt each `FieldSpec` with a hand-written constructor
    listing eleven named fields, so every field added to `FieldSpec` since was silently dropped on
    this screen alone - `seed`, and then `found_total`, which is why a gate's dropdown read
    `(12 found)` where the controls form read `(12 of 30 found)` for the same repository.

    **A copy that must be updated whenever the thing it copies grows is a copy that will not be**,
    so this asserts the rendered widget against what the plan built rather than against a literal.
    Any future field `_select_prompt` reads is covered without anyone remembering to add a case.
    """
    import subprocess
    import tempfile

    from textual.widgets import Select

    from surfaceplate.adopt import discover
    from surfaceplate.adopt.tui.screens import _select_prompt

    repo = Path(tempfile.mkdtemp(prefix="surfaceplate-gatespec-")) / "repo"
    (repo / "docs").mkdir(parents=True)
    for args in (["init", "-q"], ["config", "user.email", "h@e.invalid"],
                 ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    # More candidates than the cap, so `found_total` and the shown count genuinely differ - the
    # fixture has to truncate or the assertion cannot tell the two prompts apart.
    for index in range(discover.SHOWN + 6):
        (repo / "docs" / f"note-{index:03d}.md").write_text(f"# {index}\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True,
                   capture_output=True)
    found = discover.scan(repo)
    specs = plan.gate_plan(level="standard", builds_ui=True, mode="simple", found=found)
    section = plan.gates_plan(level="standard", builds_ui=True, mode="simple", found=found)

    async def prompts() -> dict:
        app = Host(GatesScreen(specs, section, repo=repo, level="standard"))
        async with app.run_test(size=(140, 80)) as pilot:
            await pilot.pause()
            await pilot.press("ctrl+o")  # `F91`: beyond-floor gates are folded until opened
            await pilot.pause()
            out = {}
            for widget in app.screen.query(Select):
                if widget.id and widget.id.startswith("f-"):
                    out[widget.id[len("f-"):].replace("--", ".")] = str(widget.prompt)
            return out

    shown = asyncio.run(prompts())
    wanted = {
        f"{spec.id}.{field.id}": _select_prompt(field)
        for spec in specs for field in spec.fields if field.kind == "select"
    }
    checked = 0
    for key, prompt in wanted.items():
        if key not in shown:
            continue
        checked += 1
        check(f"gates screen renders the plan's prompt for {key}", shown[key] == prompt,
              f"screen={shown[key]!r} plan={prompt!r}")
    check("the sweep examined some dropdowns - an empty sweep proves nothing", checked > 0,
          f"{checked} of {len(wanted)} select field(s) on screen")
    check("and the fixture truncates, so the two prompt forms differ",
          any("of" in p for p in wanted.values()), str(list(wanted.values())[:1]))


def test_a_gates_refusal_survives_the_keypress_that_follows_it() -> None:
    """`F161`, the other half. `F74` fixed exactly this on the decisions form and never reached
    the gates screen: `action_commit` reported the refusal, the next keypress moved focus, the
    focus handler redrew the hint **with no error**, and the refusal was on screen for one frame.

    From the adopter's side `Ctrl+S` did nothing. That is how the maintainer reported it.
    """
    import subprocess
    import tempfile

    from textual.widgets import Static

    from surfaceplate.adopt import discover

    repo = Path(tempfile.mkdtemp(prefix="surfaceplate-gatehint-")) / "repo"
    repo.mkdir(parents=True)
    for args in (["init", "-q"], ["config", "user.email", "h@e.invalid"],
                 ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    (repo / "src.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True,
                   capture_output=True)
    found = discover.scan(repo)
    specs = plan.gate_plan(level="standard", builds_ui=True, mode="simple", found=found)
    section = plan.gates_plan(level="standard", builds_ui=True, mode="simple", found=found)

    async def press_then_move() -> tuple[str, str, str]:
        app = Host(GatesScreen(specs, section, repo=repo, level="standard"))
        async with app.run_test(size=(140, 80)) as pilot:
            await pilot.pause()
            await pilot.press("ctrl+s")           # the fold question, if gates are undecided
            for _ in range(3):
                await pilot.pause()
            if not isinstance(app.screen, GatesScreen):
                await pilot.press("y")            # declare the folded ones not applicable
                for _ in range(4):
                    await pilot.pause()
            await pilot.press("ctrl+s")           # the refusal under test
            for _ in range(4):
                await pilot.pause()
            def line() -> str:
                return str(app.screen.query_one("#hint", Static).content).splitlines()[0]
            after = line()
            await pilot.press("tab")
            for _ in range(3):
                await pilot.pause()
            tabbed = line()
            await pilot.press("down")
            for _ in range(3):
                await pilot.pause()
            arrowed = line()
            app.exit(None)
            return after, tabbed, arrowed

    after, tabbed, arrowed = asyncio.run(press_then_move())
    check("Ctrl+S reports why it refused", "cannot be blank" in after.lower() or ":" in after,
          f"hint: {after!r}")
    check("and the refusal survives the Tab that follows it (F74's rule, this screen)",
          tabbed == after, f"before={after!r} after={tabbed!r}")
    check("and survives an arrow key too", arrowed == after,
          f"before={after!r} after={arrowed!r}")


def test_ticking_a_control_reveals_the_fields_it_makes_required() -> None:
    """`F143`. The wizard demanded a value for a field it did not show.

    `FormScreen._on_change` listened for `Checkbox.Changed`, `Input.Changed` and
    `RadioSet.Changed` - and not for `SelectionList.SelectedChanged`, which is the one widget whose
    answer reveals other fields. `FieldSpec.applies` had already been generalised so that
    "depends on a multiselect" means "is among what was ticked": the plan side was done and the
    screen was never wired to the event.

    So ticking a control in the above-floor list left its rationale and reference rows
    `display=False` - out of the focus chain, unreachable by any key - while `Ctrl+S` refused the
    section for their being blank. The adopter's report was "I can't progress", and they were
    right: there was no progressing.

    **No scripted suite could have caught this.** `test_adopt.py` and the matrix answer the plan
    directly and never render a row, which is why this test lives here and drives real keypresses.
    """
    import subprocess
    import tempfile

    repo = Path(tempfile.mkdtemp(prefix="surfaceplate-reveal-")) / "repo"
    repo.mkdir()
    for args in (["init", "-q"], ["config", "user.email", "h@example.invalid"],
                 ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True,
                   capture_output=True)
    found = plan.discover.scan(repo)
    section = plan.controls_plan(level="essential", mode="simple", found=found)

    async def tick_one(control: str) -> tuple[list, list]:
        app = Host(FormScreen(section, repo=repo))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            listing = app.screen.query_one("#f-above_floor")
            listing.focus()
            await pilot.pause()
            names = [str(getattr(o, "prompt", o)) for o in listing.options]
            index = next(i for i, n in enumerate(names) if n.startswith(control))
            for _ in range(index):
                await pilot.press("down")
                await pilot.pause()
            await pilot.press("space")          # a real keypress, as an adopter makes it
            await pilot.pause()
            await pilot.pause()
            rows = [(w.id, w.display) for w in app.screen.query("*")
                    if w.id and w.id.startswith(f"row-{control}--")]
            chain = [w.id for w in app.screen.focus_chain if getattr(w, "id", None)]
            return rows, chain

    rows, chain = asyncio.run(tick_one("method_registry"))
    check("ticking a control shows the rows it makes required",
          rows and all(shown for _, shown in rows), str(rows))
    check("and puts them in the focus chain, so a key can reach them",
          [c for c in chain if "method_registry" in c], str(chain))
    check("both of its fields, not only the first",
          len([c for c in chain if "method_registry" in c]) == 2, str(chain))


def test_the_help_beside_a_field_states_what_it_decides_and_describes_the_chosen_file() -> None:
    """`F82` and `F80` / `DR-51` (3), (4). Beside the focused field: what is asked, what the
    answer decides, what a wrong answer costs; and for a field answered by picking a file, what
    that file is, as seen by discovery and judged by the checker's rules."""
    import subprocess
    import tempfile

    from textual.widgets import Select, Static

    repo = Path(tempfile.mkdtemp(prefix="surfaceplate-help-")) / "repo"
    repo.mkdir()
    for args in (["init", "-q"], ["config", "user.email", "h@example.invalid"], ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    (repo / "docs").mkdir()
    (repo / "docs" / "register.md").write_text("# Activity register\n\n| id | title |\n", encoding="utf-8")
    (repo / "docs" / "notes.md").write_text("# Notes\n\nTODO tidy\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "fixture"], check=True, capture_output=True)
    found = plan.discover.scan(repo)

    section = plan.decisions_plan(repo, found=found, proposals={})

    async def form() -> tuple[str, str]:
        app = Host(FormScreen(section, repo=repo))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            app.screen.query_one("#f-stack--builds_user_interface").focus()
            await pilot.pause()
            slot = app.screen.query_one("#help-stack--builds_user_interface", Static)
            first = str(slot.content)
            return first, ""

    text, _ = asyncio.run(form())
    check("the decisions form shows what the answer decides and what a wrong one costs",
          "Decides:" in text and "If wrong:" in text and "interface gates" in text, text[:300])

    specs = plan.gate_plan(level="essential", builds_ui=False, mode="simple", found=found)
    gates = plan.gates_plan(level="essential", builds_ui=False, mode="simple", found=found)

    async def gate() -> tuple[str, str, str]:
        app = Host(GatesScreen(specs, gates, repo=repo))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            select = app.screen.query_one("#f-work_registration--artefact", Select)
            select.focus()
            await pilot.pause()
            before = str(app.screen.query_one("#help-work_registration--artefact", Static).content)
            select.value = "docs/register.md"
            await pilot.pause()
            await pilot.pause()
            chosen = str(app.screen.query_one("#help-work_registration--artefact", Static).content)
            select.value = "docs/notes.md"
            await pilot.pause()
            await pilot.pause()
            rejected = str(app.screen.query_one("#help-work_registration--artefact", Static).content)
            return before, chosen, rejected

    before, chosen, rejected = asyncio.run(gate())
    check("a gate's artefact field states what it decides before anything is chosen", "Decides:" in before and "If wrong:" in before, before[:300])
    check("choosing a file describes it: its heading and its match", "Activity register" in chosen and "matched" in chosen, chosen[:300])
    check("choosing a file the checker would reject says so", "reject" in rejected and "placeholder" in rejected, rejected[:300])

    specs_std = plan.gate_plan(level="standard", builds_ui=False, mode="simple", found=found)
    gates_std = plan.gates_plan(level="standard", builds_ui=False, mode="simple", found=found)
    first = next(s for s in specs_std if not s.mandatory and not s.auto_status)

    async def status() -> str:
        app = Host(GatesScreen(specs_std, gates_std, repo=repo))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            app.screen.query_one(f"#f-{first.id}--status", RadioSet).focus()
            await pilot.pause()
            return str(app.screen.query_one(f"#help-{first.id}--status", Static).content)

    text = asyncio.run(status())
    check("a gate's status row states what each status commits the team to",
          "required" in text and "deferred" in text and "not applicable" in text and "Decides:" in text, text[:400])


def test_ctrl_q_reaches_the_screens_own_cancel() -> None:
    """`F73`. Textual's `App.BINDINGS` carries a priority `ctrl+q -> quit`, so every screen's
    `action_cancel` was dead code and the app simply ended with `None`. The apps now own that
    key, so a screen's cancel runs - the resume prompt included, which had no binding for it."""
    import tempfile

    from surfaceplate.adopt.interview import DraftInfo, Welcome
    from surfaceplate.adopt.tui.app import AdoptApp, OpeningApp
    from surfaceplate.adopt.tui import screens as _screens

    calls: list[str] = []
    originals = {}
    for cls in (_screens.FormScreen, _screens.ResumeScreen, _screens.WelcomeScreen):
        originals[cls] = cls.action_cancel

        def spy(self, _cls=cls):
            calls.append(_cls.__name__)
            return originals[_cls](self)

        cls.action_cancel = spy  # type: ignore[method-assign]
    try:
        repo = Path(tempfile.mkdtemp(prefix="surfaceplate-cancel-")) / "repo"
        repo.mkdir()
        flow = _a_flow(repo, {})

        async def in_adopt_app():
            app = AdoptApp(flow=flow, on_progress=lambda: None)
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.pause(); await pilot.pause()
                await pilot.press("ctrl+q")
                await pilot.pause(); await pilot.pause()
            return app.return_value

        result = asyncio.run(in_adopt_app())
        check("Ctrl+Q on the decisions form runs FormScreen.action_cancel", "FormScreen" in calls, str(calls))
        check("and the app returns the cancel sentinel, which the wizard reads as Cancelled", result == _screens.CANCELLED, repr(result))

        welcome = Welcome(repo="/r", tool_name="Surfaceplate", tool_version="0.16.0", tool_anchor="a" * 64, licence="Apache-2.0",
                          publisher="P", homepage="h", tagline="t", installed_version="0.16.0", installed_anchor="a" * 64,
                          installed_at="2026-09-02", profile_path="governance/application-profile.yaml",
                          provenance_path="governance/application-profile.provenance.yaml",
                          draft=DraftInfo(sections=("identity",), framework_version="0.16.0", framework_digest="a" * 64, matches=True))

        async def at_the_prompt():
            app = OpeningApp(welcome)
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.pause()
                await pilot.press("enter")
                await pilot.pause(); await pilot.pause()
                await pilot.press("ctrl+q")
                await pilot.pause(); await pilot.pause()
            return app.return_value

        result = asyncio.run(at_the_prompt())
        check("Ctrl+Q at the resume prompt runs ResumeScreen.action_cancel", "ResumeScreen" in calls, str(calls))
        check("and still means quit with the draft kept (None), as F68 requires", result is None, repr(result))
    finally:
        for cls, original in originals.items():
            cls.action_cancel = original  # type: ignore[method-assign]


def test_choosing_the_create_it_row_commits_without_a_refusal() -> None:
    """`F87` / `DR-54` (1): on the gate list and on a form, the seed row is the first choice, its
    help says what the seed contains, and choosing it commits - the offer follows, the field's
    validator does not refuse a file that is about to be created."""
    import tempfile

    from textual.widgets import Select, Static

    from surfaceplate.adopt import scaffold

    repo = Path(tempfile.mkdtemp(prefix="surfaceplate-seed-")) / "repo"
    repo.mkdir()
    found = plan.discover.Discovered(free_seeds={"work_registration": scaffold.SEEDABLE["work_registration"][0]},
                                     free_control_seeds={"assurance_findings": scaffold.SEEDABLE_CONTROLS["assurance_findings"][0]})
    specs = plan.gate_plan(level="essential", builds_ui=False, mode="simple", found=found)
    gates = plan.gates_plan(level="essential", builds_ui=False, mode="simple", found=found)

    async def on_gates():
        app = Host(GatesScreen(specs, gates, repo=repo))
        async with app.run_test(size=(120, 60)) as pilot:
            await pilot.pause()
            select = app.screen.query_one("#f-work_registration--artefact", Select)
            select.focus(); await pilot.pause()
            first = [v for _l, v in select._options][0] if hasattr(select, "_options") else None
            select.value = scaffold.SEEDABLE["work_registration"][0]
            await pilot.pause(); await pilot.pause()
            help_text = str(app.screen.query_one("#help-work_registration--artefact", Static).content)
            app.screen.query_one("#f-work_registration--paths").value = "**"
            await pilot.pause()
            await pilot.press("ctrl+s")
            await pilot.pause(); await pilot.pause()
        return help_text, app.result

    help_text, result = asyncio.run(on_gates())
    check("the help says the seed will be created and what it contains", "create" in help_text.lower() and "register" in help_text.lower(), help_text[:300])
    check("Ctrl+S commits with the seed chosen (the offer follows)", isinstance(result, dict) and result.get("work_registration.paths") == "**", repr(result)[:200])

    section = plan.controls_plan(level="essential", mode="simple", found=found)
    ref = next(f for f in section.fields if f.id == "assurance_findings.implementation_reference")
    check("the control's reference is a dropdown whose first row is the seed", ref.kind == "select" and ref.choices[0][0] == ref.seed, str(ref.choices[:1]))


def test_continuing_past_the_folded_gates_asks_once() -> None:
    """`F96` / `DR-57`. With the floor complete and the gates beyond it folded and undecided,
    Ctrl+S asks one question naming the count. `y` declares them all not applicable as one
    recorded act and continues; `n` opens the fold on the first undecided gate; Ctrl+Q at the
    question changes nothing."""
    from surfaceplate.adopt.tui.screens import CANCELLED, GatesScreen

    found = plan.discover.Discovered(artefacts=("activity/register.md",), paths=("src/**",))
    specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple", found=found)
    section = plan.gates_plan(level="standard", builds_ui=False, mode="simple", found=found)
    floor = {}
    for spec in specs:
        if spec.mandatory:
            floor[f"{spec.id}.artefact"] = "activity/register.md"
            floor[f"{spec.id}.paths"] = "src/**"
            floor[f"{spec.id}.effective_from"] = "2026-09-01"
    beyond = [s.id for s in specs if not s.mandatory and not s.auto_status]

    async def drive(keys):
        screen = GatesScreen(specs, section, initial=floor, level="standard")
        app = Host(screen)
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause(); await pilot.pause()
            await pilot.press("ctrl+s")
            await pilot.pause(); await pilot.pause()
            asked = type(app.screen).__name__, " ".join(s.text for s in app.screen._compositor.render_strips())
            for key in keys:
                await pilot.press(key)
                await pilot.pause(); await pilot.pause()
            state = (type(app.screen).__name__, getattr(screen, "_folded", None), screen._focused_gate_id(), set(screen.bulk_gates))
        return asked, state, app.result

    asked, state, result = asyncio.run(drive(["y"]))
    check("Ctrl+S with folded undecided gates asks a question naming the count",
          asked[0] == "FoldedUndecidedScreen" and f"{len(beyond)} gates" in asked[1] and "not applicable" in asked[1], asked[1][:300])
    check("y declares them all not applicable as one act and continues",
          isinstance(result, dict) and all(result.get(f"{g}.status") == "not_applicable" for g in beyond) and state[3] == set(beyond), repr(result)[:200])

    asked, state, result = asyncio.run(drive(["n"]))
    check("n opens the fold on the first undecided gate, nothing decided",
          state[0] == "GatesScreen" and state[1] is False and state[2] == beyond[0] and not state[3] and result is None, str(state))

    asked, state, result = asyncio.run(drive(["ctrl+q"]))
    check("Ctrl+Q at the question changes nothing: the list is back, still folded, nothing decided",
          state[0] == "GatesScreen" and state[1] is True and not state[3] and result is None, str(state))

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
            # The escape row is an ACTION, not a file, so it is excluded here rather than the rule
            # being loosened to admit it (`F147`). `DR-38`'s "never offer something that isn't
            # there" governs what is offered as a candidate; typing a path is not an offer.
            offered = [
                v for _prompt, v in artefact._options
                if isinstance(v, str) and v != plan.TYPE_A_PATH
            ]
            check(
                "and every file it offers actually exists in the repository",
                bool(offered) and all((ROOT / str(v)).exists() for v in offered),
                str(offered[:3]),
            )
            check(
                "and the escape from the list is offered alongside them (F147)",
                plan.TYPE_A_PATH in [v for _prompt, v in artefact._options],
                str([v for _prompt, v in artefact._options][:2]),
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
    test_ctrl_q_reaches_the_screens_own_cancel()
    test_choosing_the_create_it_row_commits_without_a_refusal()
    test_continuing_past_the_folded_gates_asks_once()
    test_every_field_the_plan_asks_for_is_displayed_and_reachable()
    test_ticking_a_control_reveals_the_fields_it_makes_required()
    test_the_help_beside_a_field_states_what_it_decides_and_describes_the_chosen_file()

    print("\nconformance level (mockup frame 02)")
    test_highlighting_a_level_does_not_choose_it()

    print("\ngate catalogue (mockup frame 03)")
    test_gate_catalogue_behaviour()
    test_mandatory_and_masked_gates_are_stated_not_asked()

    print("\nF147: a discovered list is an offer, not the only permitted answer")
    test_every_select_field_can_be_answered_off_the_list()

    print("\nACT-101: the welcome screen offers both routes")
    test_the_welcome_screen_offers_both_routes()

    print("\nF161: the gates screen renders the plan, and keeps its refusal on screen")
    test_the_gates_screen_renders_the_spec_the_plan_built()
    test_a_gates_refusal_survives_the_keypress_that_follows_it()

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
