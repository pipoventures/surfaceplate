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

from surfaceplate.adopt import flow as _flow
from surfaceplate.adopt import plan, provenance
from surfaceplate.adopt.interview import Cancelled, DraftInfo
from surfaceplate.adopt.tui.screens import (
    CANCELLED,
    EditLineScreen,
    FormScreen,
    GatesScreen,
    LevelScreen,
    ResumeScreen,
    ReviewScreen,
    ScaffoldScreen,
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


class AdoptApp(App):
    """Shows one screen per stage of the flow, and hands each stage's answers back to it."""

    CSS_PATH = CSS_PATH

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
                    flow.gate_specs(), flow.gates_plan(), step=step, initial=flow.gate_seeds(), repo=self.repo
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


class ConfirmResumeApp(App):
    """A single question, asked before the main app so a draft is never resumed silently."""

    CSS_PATH = CSS_PATH

    def __init__(self, info: DraftInfo) -> None:
        super().__init__()
        self.info = info

    def on_mount(self) -> None:
        self._ask()

    @work
    async def _ask(self) -> None:
        self.exit(await self.push_screen_wait(ResumeScreen(self.info)))


class TextualInterview:
    """The real `Interview`: runs the app, returns the approval it collected."""

    def confirm_resume(self, info: DraftInfo) -> bool | None:
        # `True` on `y`, `False` on `n`, and `None` when the app ended without either - `Ctrl+Q`
        # is Textual's own priority quit binding and returns `None` from `run()`. `F68`: wrapping
        # this in `bool()` turned a quit into "start fresh", and the draft was deleted.
        return ConfirmResumeApp(info).run()

    def collect(self, flow: _flow.Flow, *, on_progress: Callable[[], None]) -> str:
        app = AdoptApp(flow=flow, on_progress=on_progress)
        result = app.run()
        if result is None or result == CANCELLED:
            raise Cancelled()
        return str(result)
