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

from surfaceplate.adopt import defaults, discover, plan
from surfaceplate.adopt.interview import Cancelled, DraftInfo
from surfaceplate.adopt.tui.screens import (
    CANCELLED,
    DefaultsScreen,
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
        # Scanned once, here, and handed to every section. Scanning per section worked but let the
        # gate catalogue be built from a different call that had no scan at all.
        self.found = discover.scan(repo)
        self._seeded: dict[str, dict] = {}
        self._on_section_complete = on_section_complete
        self._preview = preview

    def on_mount(self) -> None:
        self._drive()

    async def _take_the_defaults_route(self) -> bool:
        """Propose what can honestly be proposed, show it, then ask only what is left.

        Returns False if the adopter cancelled. Choosing "answer everything myself" here simply
        returns True with nothing seeded, so the ordinary section screens run as they always have -
        the fork is reversible right up to the moment it saves anyone work.
        """
        proposals = defaults.propose(self.state, found=self.found)
        outstanding = defaults.unanswered(
            self.state, proposals, repo=self.repo, found=self.found
        )
        decision = await self.push_screen_wait(DefaultsScreen(proposals, len(outstanding)))
        if decision == CANCELLED or decision is None:
            return False
        if decision == "customise":
            return True

        # Seed the remaining sections from the proposals. Anything unproposed stays absent, so the
        # section screens below still ask for it - pre-filled with what was proposed, blank where
        # nothing honest could be.
        seeded: dict[str, dict] = {}
        for proposal in proposals:
            section_name, _, field_id = proposal.field.partition(".")
            seeded.setdefault(section_name, {})[field_id] = proposal.value
        self._seeded = seeded
        return True

    @work
    async def _drive(self) -> None:
        for name in plan.SECTION_ORDER:
            if name in self.state:
                continue
            section = plan.section_plan(
                name, repo=self.repo, state=self.state, found=self.found
            )
            step = _STEPS.get(name, "")
            if name == "level":
                # The caret starts on the level the adopter's own answers point at. The note on
                # the screen already says which that is, and `F39`'s lesson is that a value the
                # plan computes has to be *handed to the screen* or the screen quietly does
                # something else - so this is passed explicitly and joined in the TUI suite.
                recommended, _ = plan.recommended_level(self.state.get("risk") or {})
                screen = LevelScreen(section, step=step, recommended=recommended)
            elif name == "gates":
                # `found=` matters and its absence cost a real adoption: without it every
                # precondition artefact fell back to a plain text box while the controls screen,
                # which goes through `section_plan`, correctly offered dropdowns. The maintainer
                # typed `asdf` into seven gates because there was nothing to pick from.
                specs = plan.gate_plan(
                    level=self.state["level"]["conformance_level"],
                    builds_ui=bool(self.state["stack"]["builds_user_interface"]),
                    mode=self.state["mode"]["mode"],
                    found=self.found,
                )
                screen = GatesScreen(specs, section, step=step)
            else:
                screen = FormScreen(
                    section, step=step, initial=self._seeded.get(name, {})
                )

            result = await self.push_screen_wait(screen)
            if result == CANCELLED or result is None:
                self.exit(CANCELLED)
                return
            self.state[name] = result
            self._on_section_complete(name, result)

            if name == "route" and result.get("route") == "defaults":
                if not await self._take_the_defaults_route():
                    self.exit(CANCELLED)
                    return

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
