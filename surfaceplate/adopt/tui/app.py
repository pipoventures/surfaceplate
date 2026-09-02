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

import datetime as _dt
from pathlib import Path
from typing import Callable

from textual import work
from textual.app import App

from surfaceplate.adopt import defaults, discover, plan, scaffold
from surfaceplate.adopt.wizard import SCAFFOLD_KEY
from surfaceplate.adopt.interview import Cancelled, DraftInfo
from surfaceplate.adopt.tui.screens import (
    ScaffoldScreen,
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
def _step_labels() -> dict[str, str]:
    """`F45`: derived from `SECTION_ORDER`, never written down beside it.

    Hand-written, this table drifted from the wizard it describes: `route` had no entry at all so
    that screen showed no step; `adoption` and `wrap` both read `7 of 7`, so an adopter answered
    "7 of 7" and was handed another "7 of 7"; and the total said seven while `SECTION_ORDER` held
    ten sections. A progress counter is read as a promise about how much is left, and one that
    cannot be trusted is worse than none.

    `mode` is deliberately unnumbered: it is asked before the run proper and chooses how the run
    explains itself, so counting it would make the total depend on a question about the wizard
    rather than about the repository.
    """
    counted = [name for name in plan.SECTION_ORDER if name != "mode"]
    total = len(counted)
    # `mode` and `scaffold` are deliberately UNNUMBERED, for the same reason and not the same one.
    # `mode` is asked before the run proper and chooses how the run explains itself. `scaffold` is
    # conditional - it appears only where a required gate has no artefact - so numbering it either
    # duplicates the gates screen's number (which is `F45` exactly, and was the first attempt) or
    # makes every run claim a total it will not reach. A screen that is not always shown has no
    # position in a fixed sequence, and says so by claiming none.
    labels = {"mode": "", "scaffold": ""}
    for position, name in enumerate(counted, start=1):
        labels[name] = f"{position} of {total} — "
    return labels


_STEPS = _step_labels()


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


    async def _offer_missing_artefacts(self) -> bool:
        """`ACT-033`. Where a gate the profile will DECLARE AS REQUIRED has no artefact, offer one.

        Every clause of that sentence was a defect in the first version, found by an adversarial
        review of this method:

        - **"the profile will declare"** - it iterated `scaffold.SEEDABLE` instead of the gate plan,
          so at `essential`, where only `work_registration` is asked at all, the other three were
          absent from the answers, read as blank, and were offered with everything pre-ticked under
          the heading *"gate(s) you must declare"*. Accepting wrote three files that no gate in the
          profile referenced, because `sections.build_gates` walks the plan and drops answers for
          gates it does not contain.
        - **"as required"** - a gate answered `deferred` or `not_applicable` never collects an
          artefact, so it also looked blank and was offered one, contradicting this method's own
          promise not to second-guess a gate the adopter had answered.
        - **and it runs HERE, before the review, rather than immediately after the gates section** -
          a run cancelled at the review and then resumed skips every completed section, so the offer
          never re-ran while the artefact path it had written into the gate answers was still in the
          draft. The profile was then written naming an artefact nobody created: a guaranteed
          `SP032` failure, produced by the very code whose comment says it exists to prevent one.
        """
        gates = self.state.get("gates") or {}
        specs = plan.gate_plan(
            level=self.state["level"]["conformance_level"],
            builds_ui=bool(self.state["stack"]["builds_user_interface"]),
            mode=self.state["mode"]["mode"],
            found=self.found,
        )
        needs_artefact = []
        for spec in specs:
            if spec.id not in scaffold.SEEDABLE:
                continue
            status = "required" if spec.mandatory else (spec.auto_status or gates.get(f"{spec.id}.status"))
            if status != "required":
                continue
            answer = str(gates.get(f"{spec.id}.artefact") or "").strip()
            seed_path = scaffold.SEEDABLE[spec.id][0]
            # **The condition is about the FILE, not the answer**, and getting that wrong is how
            # the first fix for this failed. Moving the offer before the review was necessary and
            # not sufficient: a resumed run carries the artefact ANSWER in its draft while the file
            # it names was never created, so testing "is the answer blank?" skipped the gate and
            # the profile still named a file that did not exist.
            #
            # An adopter who typed their OWN path is not second-guessed even if it is missing:
            # writing this framework's seed at somebody else's chosen path would be inventing an
            # answer. `SP032` reports that case, which is the correct outcome.
            if answer and answer != seed_path:
                continue
            if (self.repo / seed_path).exists():
                continue
            needs_artefact.append(spec.id)

        offers = scaffold.offers(self.repo, needs_artefact)
        if not offers:
            return True

        accepted = await self.push_screen_wait(ScaffoldScreen(offers, step=_STEPS.get("scaffold", "")))
        if accepted is None:
            return False
        # `F47`: the gate binds from the INSTANT the artefact was created, not from that midnight.
        # A date could only say "today", which put every commit made earlier the same working day
        # inside a window where the precondition was absent - true by the letter of a date, and
        # useless to an adopter who cannot do anything about this morning. `DR-44` widened
        # `effective_from` to accept an instant precisely so this can be said accurately.
        moment = _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
        for offer in accepted:
            self.state.setdefault("gates", {})[f"{offer.gate_id}.artefact"] = offer.path
            self.state["gates"][f"{offer.gate_id}.effective_from"] = moment
            # `effective_from` stays TODAY, and cannot be anything else: `SP033` rejects a gate
            # dated in the future, so binding from tomorrow - which is what the artefact's actual
            # history would justify - is not available. `F47` records what that costs.
        if accepted:
            self.state[SCAFFOLD_KEY] = list(accepted)
            self._on_section_complete("gates", self.state["gates"])
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
                # `F60`: seeded like every other section. Without `initial=` here the defaults
                # route showed its gate proposals and then opened every gate blank.
                screen = GatesScreen(
                    specs, section, step=step, initial=self._seeded.get(name, {})
                )
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

        if not await self._offer_missing_artefacts():
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

        confirmed = await self.push_screen_wait(
            ReviewScreen(rendered, error, creating=self.state.get(SCAFFOLD_KEY) or [])
        )
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

    def confirm_resume(self, info: DraftInfo) -> bool | None:
        # `True` on `y`, `False` on `n`, and `None` when the app ended without either - `Ctrl+Q`
        # is Textual's own priority quit binding and returns `None` from `run()`. `F68`: wrapping
        # this in `bool()` turned a quit into "start fresh", and the draft was deleted.
        return ConfirmResumeApp(info).run()

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
