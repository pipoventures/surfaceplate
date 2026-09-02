"""The Textual app, and the `Interview` implementation that runs it.

`wizard.run` stays synchronous. `App.run()` is Textual's blocking entry point - it creates its own
event loop - so the whole async surface of this package is the worker below, and `cli.py`, `wizard`
and every test remain ordinary synchronous code.

The app owns nothing but the screens. The sequence, the answers, their origins and the proposals
live in `flow.Flow` (`DR-47`), which the scripted interview drives through the same stages: the
app asks the flow what comes next, shows the screen for it, and hands the answers back. Assembly,
verification and writing stay in `wizard.py`, and the only disk this app touches is the draft
file, through the callback it is handed.
"""

from __future__ import annotations

from typing import Callable

from textual import work
from textual.app import App
from textual.binding import Binding

from surfaceplate.adopt import flow as _flow
from surfaceplate.adopt import plan, provenance
from surfaceplate.adopt.interview import Cancelled, Welcome
from surfaceplate.adopt.tui.screens import (
    CANCELLED,
    EditLineScreen,
    FormScreen,
    GatesScreen,
    LevelScreen,
    ResumeScreen,
    ReviewScreen,
    ScaffoldScreen,
    WelcomeScreen,
)

from pathlib import Path

CSS_PATH = Path(__file__).with_name("app.tcss")


def _step_labels() -> dict[str, str]:
    """`F45`: derived from `plan.FLOW`, never written down beside it. The remainder form and the
    scaffold offer are conditional and unnumbered: a screen that is not always shown has no
    position in a fixed sequence, and says so by claiming none."""
    total = len(plan.FLOW)
    labels = {"remainder": "", "scaffold": ""}
    for position, name in enumerate(plan.FLOW, start=1):
        labels[name] = f"{position} of {total} — "
    return labels


_STEPS = _step_labels()


# `F73`: `App.BINDINGS` in Textual 8.2.8 carries `Binding("ctrl+q", "quit", priority=True)`,
# which fired before any screen saw the key, so every screen's `action_cancel` was dead code and
# `push_screen_wait` never resolved. An empty `BINDINGS` on a subclass is MERGED with the base
# class's (found by the test: the quit survived it), so both apps opt out of inheritance and
# keep only Ctrl+C's "press Ctrl+Q to quit" notice. Every screen binds `ctrl+q` to its own
# cancel; the outcome is the same sentinel, now reached through the code that says what it means.
_APP_BINDINGS = [Binding("ctrl+c", "help_quit", "quit", show=False, priority=True)]


class AdoptApp(App, inherit_bindings=False):
    """Shows one screen per stage of the flow, and hands each stage's answers back to it."""

    CSS_PATH = CSS_PATH
    BINDINGS = _APP_BINDINGS

    def __init__(self, *, flow: _flow.Flow, on_progress: Callable[[], None]) -> None:
        super().__init__()
        self.flow = flow
        self.repo = flow.repo
        self.found = flow.found
        self._on_progress = on_progress
        self.approved_at: str | None = None

    def on_mount(self) -> None:
        self._drive()

    @work
    async def _drive(self) -> None:
        flow = self.flow
        while True:
            stage = flow.next_stage()
            if stage == "review":
                break
            step = _STEPS.get(stage, "")
            if stage == "decisions":
                section = flow.decisions_plan()
                initial = {spec.id: spec.default for spec in section.fields if spec.default}
                result = await self.push_screen_wait(
                    FormScreen(section, step=step, initial=initial, repo=self.repo)
                )
                if result == CANCELLED or result is None:
                    self.exit(CANCELLED)
                    return
                flow.answer_decisions(result)
            elif stage == "level":
                # The caret starts on the level the adopter's own answers point at (`ACT-032`).
                screen = LevelScreen(
                    flow.level_plan(), step=step, recommended=flow.recommended_level(), repo=self.repo
                )
                result = await self.push_screen_wait(screen)
                if result == CANCELLED or result is None:
                    self.exit(CANCELLED)
                    return
                flow.answer_level(result)
            elif stage == "gates":
                screen = GatesScreen(
                    flow.gate_specs(), flow.gates_plan(), step=step, initial=flow.gate_seeds(), repo=self.repo,
                    level=flow.state["level"]["conformance_level"],
                )
                result = await self.push_screen_wait(screen)
                if result == CANCELLED or result is None:
                    self.exit(CANCELLED)
                    return
                bulk = ("not_applicable", set(screen.bulk_gates)) if screen.bulk_gates else None
                flow.answer_gates(result, bulk=bulk)
            elif stage == "remainder":
                section = flow.remainder_plan()
                initial = {spec.id: spec.default for spec in section.fields if spec.default}
                result = await self.push_screen_wait(
                    FormScreen(section, step=step, initial=initial, repo=self.repo)
                )
                if result == CANCELLED or result is None:
                    self.exit(CANCELLED)
                    return
                flow.answer_remainder(result)
            elif stage == "scaffold":
                accepted = await self.push_screen_wait(ScaffoldScreen(flow.scaffold_offers(), step=step))
                if accepted is None:
                    self.exit(CANCELLED)
                    return
                flow.accept_scaffold(accepted)
            self._on_progress()

        # The review, until it is approved or abandoned. Every edit is a typed value with a
        # timestamp, and the review is rebuilt after each so the human sees what will be written.
        highlight: int | None = None
        while True:
            review = flow.review()
            result = await self.push_screen_wait(
                ReviewScreen(review, creating=flow.accepted_scaffold, highlight=highlight)
            )
            if result is None or result == CANCELLED:
                self.exit(CANCELLED)
                return
            if result.get("approve"):
                self.approved_at = flow.approve()
                self.exit(self.approved_at)
                return
            path = result["edit"]
            highlight = result["line"]
            key, _fixed = provenance.answer_key_for(path, flow.assemble())
            section, _, field_id = (key or "").partition(".")
            current = (flow.state.get(section) or {}).get(field_id)
            value = await self.push_screen_wait(EditLineScreen(path, current, flow.field_spec(key or "")))
            if value is not None:
                flow.edit(path, value)
                self._on_progress()


class OpeningApp(App, inherit_bindings=False):
    """The opening screen and, where a draft exists, the resume prompt - before the main app, so
    a draft is never resumed silently and the tool has introduced itself before asking anything
    (`DR-51` (2)). Returns `True` to begin, `False` to begin fresh, `None` when the human quit."""

    CSS_PATH = CSS_PATH
    BINDINGS = _APP_BINDINGS

    def __init__(self, welcome: Welcome) -> None:
        super().__init__()
        self.welcome = welcome

    def on_mount(self) -> None:
        self._ask()

    @work
    async def _ask(self) -> None:
        begin = await self.push_screen_wait(WelcomeScreen(self.welcome))
        if begin is None:
            self.exit(None)
            return
        if self.welcome.draft is None:
            self.exit(True)
            return
        self.exit(await self.push_screen_wait(ResumeScreen(self.welcome.draft)))


class TextualInterview:
    """The real `Interview`: runs the app, returns the approval it collected."""

    def open(self, welcome: Welcome) -> bool | None:
        # `True` to begin, `False` on `n` at the resume prompt, and `None` when the app ended
        # without either - `Ctrl+Q` is Textual's own priority quit binding and returns `None`
        # from `run()`. `F68`: wrapping this in `bool()` turned a quit into "start fresh".
        return OpeningApp(welcome).run()

    def collect(self, flow: _flow.Flow, *, on_progress: Callable[[], None]) -> str:
        app = AdoptApp(flow=flow, on_progress=on_progress)
        result = app.run()
        if result is None or result == CANCELLED:
            raise Cancelled()
        return str(result)
