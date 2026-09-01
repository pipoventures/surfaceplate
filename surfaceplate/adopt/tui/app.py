"""The Textual app, and the `Interview` implementation that runs it.

`wizard.run` stays synchronous. `App.run()` is Textual's blocking entry point - it creates its own
event loop - so the whole async surface of this package is the worker below, and `cli.py`, `wizard`
and every test remain ordinary synchronous code. That was checked against Textual's actual API
before the design was settled, not assumed (`App.run` is not a coroutine function).

The app owns screen *sequencing* because the sequence is data-dependent: `level` cannot be planned
until `mode` and `builds_user_interface` are known, and `gates` cannot be planned until `level` is.
It does not own anything else. Assembly, verification and writing stay in `wizard.py`, and the only
disk this app touches is the draft file, through the callback it is handed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from textual import work
from textual.app import App

from surfaceplate.adopt import plan
from surfaceplate.adopt.interview import Cancelled, DraftInfo
from surfaceplate.adopt.tui.screens import (
    CANCELLED,
    FormScreen,
    GatesScreen,
    LevelScreen,
    ResumeScreen,
    ReviewScreen,
)

CSS_PATH = Path(__file__).with_name("app.tcss")

# The mockup's own step labels: counted text, never a progress bar.
_STEPS = {
    "mode": "",
    "identity": "1 of 7 — ",
    "stack": "2 of 7 — ",
    "risk": "3 of 7 — ",
    "level": "4 of 7 — ",
    "controls": "5 of 7 — ",
    "gates": "6 of 7 — ",
    "adoption": "7 of 7 — ",
    "wrap": "7 of 7 — ",
}


class AdoptApp(App):
    """Sequences the sections, and hands each completed one back through `on_section_complete`."""

    CSS_PATH = CSS_PATH

    def __init__(
        self,
        *,
        repo: Path,
        resumed: dict,
        on_section_complete: Callable[[str, dict], None],
        preview: Callable[[dict], str],
    ) -> None:
        super().__init__()
        self.repo = repo
        self.state = dict(resumed)
        self._on_section_complete = on_section_complete
        self._preview = preview

    def on_mount(self) -> None:
        self._drive()

    @work
    async def _drive(self) -> None:
        for name in plan.SECTION_ORDER:
            if name in self.state:
                continue
            section = plan.section_plan(name, repo=self.repo, state=self.state)
            step = _STEPS.get(name, "")
            if name == "level":
                screen = LevelScreen(section, step=step)
            elif name == "gates":
                specs = plan.gate_plan(
                    level=self.state["level"]["conformance_level"],
                    builds_ui=bool(self.state["stack"]["builds_user_interface"]),
                    mode=self.state["mode"]["mode"],
                )
                screen = GatesScreen(specs, section, step=step)
            else:
                screen = FormScreen(section, step=step)

            result = await self.push_screen_wait(screen)
            if result == CANCELLED or result is None:
                self.exit(CANCELLED)
                return
            self.state[name] = result
            self._on_section_complete(name, result)

        # The review screen shows what `preview` produced. A refusal is displayed rather than
        # raised through the interface - and `wizard.run` verifies again before writing regardless.
        error = ""
        rendered = ""
        try:
            rendered = self._preview(self.state)
        except Exception as exc:  # WriteRefused, or anything the renderer did not expect
            error = f"This cannot be written yet: {getattr(exc, 'detail', exc)}"

        confirmed = await self.push_screen_wait(ReviewScreen(rendered, error))
        self.exit(self.state if confirmed else CANCELLED)


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
    """The real `Interview`: runs the app, returns what it collected."""

    def confirm_resume(self, info: DraftInfo) -> bool:
        return bool(ConfirmResumeApp(info).run())

    def collect(
        self,
        *,
        repo: Path,
        resumed: dict,
        on_section_complete: Callable[[str, dict], None],
        preview: Callable[[dict], str],
    ) -> dict:
        app = AdoptApp(
            repo=repo,
            resumed=resumed,
            on_section_complete=on_section_complete,
            preview=preview,
        )
        result = app.run()
        if result is None or result == CANCELLED:
            raise Cancelled()
        return result
