"""The screen-driving half of the matrix (`ACT-057`, T7): the real `AdoptApp` driven headlessly
through a whole run, choosing what a scripted case chooses, so the profile the screens write can be
compared with the profile the flow writes from the same answers.

Values are set on the widgets the way typing leaves them (an `Input`'s value, a `TextArea`'s text,
a `Select`'s value, a radio pressed); decisions are pressed as keys where the screen binds one
(`r`/`d`/`n` on a gate, `Ctrl+O` to open the fold, `Ctrl+S` to continue, Enter on the level). The
run goes through `wizard.run` with an `Interview` whose `collect` runs the app under Textual's
pilot, so assembly, verification and writing are the wizard's own. Needs `textual`.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Input, OptionList, RadioButton, RadioSet, Select, SelectionList, TextArea

from surfaceplate.adopt import flow as _flow
from surfaceplate.adopt import wizard
from surfaceplate.adopt.interview import Cancelled
from surfaceplate.adopt.tui.app import AdoptApp
from surfaceplate.adopt.tui.screens import (
    CANCELLED,
    FoldedUndecidedScreen,
    FormScreen,
    GatesScreen,
    LevelScreen,
    ReviewScreen,
    ScaffoldScreen,
)

SIZE = (80, 24)


def _wid(field_id: str) -> str:
    return field_id.replace(".", "--")


async def _until(app, pilot, *types, limit: int = 80):
    for _ in range(limit):
        await pilot.pause()
        if isinstance(app.screen, types):
            return app.screen
    raise AssertionError(f"never reached {[t.__name__ for t in types]}; on {type(app.screen).__name__}")


async def _settled(pilot, limit: int = 12) -> None:
    previous = None
    for _ in range(limit):
        await pilot.pause()
        current = [s.text for s in pilot.app.screen._compositor.render_strips()]
        if current == previous:
            return
        previous = current


def _set(screen, field_id: str, value) -> None:
    widget = screen.query_one(f"#f-{_wid(field_id)}")
    if isinstance(widget, RadioSet):
        screen.query_one(f"#r-{_wid(field_id)}--{value}", RadioButton).value = True
    elif isinstance(widget, SelectionList):
        widget.deselect_all()
        for item in value:
            widget.select(item)
    elif isinstance(widget, Select):
        widget.value = value
    elif isinstance(widget, TextArea):
        widget.text = "" if value is None else str(value)
    elif isinstance(widget, Input):
        widget.value = "" if value is None else str(value)
    else:
        raise AssertionError(f"no way to set {type(widget).__name__} for {field_id}")


async def _fill_form(screen: FormScreen, pilot, answers: dict, *, lazy=None) -> None:
    if lazy is not None and screen.section.name == "remainder":
        lazy()
    for spec in screen.section.fields:
        if spec.id in answers:
            _set(screen, spec.id, answers[spec.id])
            await pilot.pause()
    await pilot.pause()
    await pilot.press("ctrl+s")


async def _drive_gates(screen: GatesScreen, pilot, s) -> None:
    if screen._folded:
        await pilot.press("ctrl+o")
        await _settled(pilot)
    for spec in screen.specs:
        if spec.mandatory or spec.auto_status:
            pass
        else:
            status = s.answers.get(f"gates.{spec.id}.status")
            if status is not None:
                screen.query_one(f"#f-{spec.id}--status", RadioSet).focus()
                await pilot.pause()
                await pilot.press({"required": "r", "deferred": "d", "not_applicable": "n"}[status])
                await pilot.pause()
        for f in spec.fields:
            key = f"gates.{spec.id}.{f.id}"
            if f.id == "status" or key not in s.answers:
                continue
            _set(screen, f"{spec.id}.{f.id}", s.answers[key])
            await pilot.pause()
    if s.bulk:
        await pilot.press("ctrl+n")
        await _settled(pilot)
    await pilot.press("ctrl+s")


class DrivenInterview:
    """An `Interview` that runs the real app under the pilot and answers as the script does."""

    def __init__(self, s, repo: Path) -> None:
        self.s = s
        self.repo = repo

    def open(self, welcome) -> bool | None:
        return True

    def collect(self, flow: _flow.Flow, *, on_progress) -> str:
        return asyncio.run(self._collect(flow, on_progress))

    async def _collect(self, flow: _flow.Flow, on_progress) -> str:
        s = self.s
        app = AdoptApp(flow=flow, on_progress=on_progress)

        def lazy() -> None:
            if s.lazy_workflow_steps:
                from adopt_matrix import write_lazy_workflow

                write_lazy_workflow(self.repo, s.lazy_workflow_steps)

        async with app.run_test(size=SIZE) as pilot:
            decisions = await _until(app, pilot, FormScreen)
            await _fill_form(decisions, pilot, s.answers)
            level = await _until(app, pilot, LevelScreen)
            options = level.query_one(f"#f-{level.spec.id}", OptionList)
            options.highlighted = ("essential", "standard", "full").index(s.answers["level.conformance_level"])
            await pilot.pause()
            await pilot.press("enter")
            gates = await _until(app, pilot, GatesScreen)
            await _drive_gates(gates, pilot, s)
            for _ in range(60):
                await pilot.pause()
                screen = app.screen
                if isinstance(screen, FoldedUndecidedScreen):
                    await pilot.press("y")
                elif isinstance(screen, FormScreen) and screen.section.name == "remainder":
                    await _fill_form(screen, pilot, s.answers, lazy=lazy)
                elif isinstance(screen, ScaffoldScreen):
                    if not s.accept_scaffold:
                        screen.query_one("#f-scaffold", SelectionList).deselect_all()
                    await pilot.press("ctrl+s")
                elif isinstance(screen, ReviewScreen):
                    break
                elif isinstance(screen, GatesScreen):
                    hint = str(screen.query_one("#hint").content)
                    raise AssertionError(f"the gate list did not continue: {hint[:200]}")
            review = await _until(app, pilot, ReviewScreen)
            if review.review.error:
                raise AssertionError(f"the review refuses: {review.review.error}")
            await pilot.press("ctrl+s")
            await pilot.pause()
        result = app.return_value
        if result is None or result == CANCELLED:
            raise Cancelled()
        return str(result)


def run_screens(s, repo: Path):
    """Run the case through the screens; returns what `wizard.run` returns."""
    return wizard.run(repo, DrivenInterview(s, repo))
