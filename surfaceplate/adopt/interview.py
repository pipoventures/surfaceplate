"""How a whole run gets asked, kept separate from what is asked and from what it becomes.

`DR-36` split asking from the shape of the answers; `DR-47` fixes the sequence of asking as the
stages `flow.Flow` holds: decisions, level, the gate list, whatever the proposal could not fill,
the scaffold offer, and an annotated review. An `Interview` drives a `Flow` through those stages.
There is one real implementation (`tui/`) and one scripted one (here), and `Cancelled` is raised
at the seam so an abandoned run has exactly one exit path.

**What the scripted implementation proves, and what it does not.** `ScriptedInterview` answers
every field a stage presents, raises on a presented field it has no answer for, and
`assert_no_unused_keys()` raises on an answer nothing asked for and nothing proposed. It cannot
prove the *screens* present what the flow presents - `tests/test_adopt_tui.py` closes that with a
field-id join per screen - and `tests/test_provenance.py` closes the other side: every value in
the written profile traces to an answer, a proposal or the allow-list, with its origin recorded.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Protocol

from surfaceplate.adopt import flow as _flow
from surfaceplate.adopt import plan, scaffold

# Bumped when the shape of a draft changes incompatibly. Format 2 held raw answers by section;
# format 3 adds the origin of every answer and which stages are done (`DR-47`). A format-2 draft
# is offered a fresh start rather than resumed into a flow that would record its values with no
# origin.
DRAFT_FORMAT = 3


class Cancelled(Exception):
    """Raised when the human backs out - a quit key, or declining the final write.

    Caught once, at the top level (`wizard.run`), which is what makes "an interrupt leaves the
    repository untouched" true by construction rather than by every screen remembering to check.
    """


@dataclass(frozen=True)
class DraftInfo:
    """What a human is told before being asked whether to resume an unfinished run.

    `matches` is false when the draft was written against a different installed framework version
    or digest. `DR-35` decided that case is *flagged, not silently trusted and not refused* - the
    human still decides, with the mismatch stated.
    """

    sections: tuple[str, ...]
    framework_version: str
    framework_digest: str
    matches: bool


@dataclass(frozen=True)
class Welcome:
    """What the opening screen shows before the first question (`F81`, `DR-51` (2)): the tool,
    the install it is about to write against, where it will write, and the draft if one exists.
    The version comparison has already passed by the time this is built (`wizard.InstallMismatch`)."""

    repo: str
    tool_name: str
    tool_version: str
    tool_anchor: str
    licence: str
    publisher: str
    homepage: str
    tagline: str
    installed_version: str
    installed_anchor: str
    installed_at: str
    profile_path: str
    provenance_path: str
    draft: DraftInfo | None = None


class Interview(Protocol):
    def open(self, welcome: Welcome) -> bool | None:
        """Show the opening screen and, where `welcome.draft` is set, the resume prompt. `True`
        begins (resuming the draft if there is one); `False` discards the draft and begins fresh;
        `None` means the human quit: the run is cancelled and any draft is kept (`F68`). A draft
        is offered, never silently reloaded."""
        ...

    def collect(self, flow: _flow.Flow, *, on_progress: Callable[[], None]) -> str:
        """Drive `flow` from wherever it stands to an approved review, and return the approval
        timestamp. `on_progress()` is called as each stage completes, so a draft is saved and a
        late failure loses at most the stage in progress. Raises `Cancelled` if the human
        abandons the run or declines the final write."""
        ...


@dataclass
class ScriptedInterview:
    """An `Interview` driven by a keyed script, for tests and for nothing else.

    `answers` is keyed `"<section>.<field id>"` - `"identity.owner"`, `"gates.work_registration.artefact"`.
    A key for a field a stage presents is used as the answer; a key for a field the flow proposed
    but did not present overrides the proposal (and is recorded as typed, as a review edit would
    be). Gate statuses are presented as decisions and must be scripted, one per undecided gate,
    unless `bulk_not_applicable` is set - the scripted form of the one explicit bulk command.
    """

    answers: dict[str, object]
    cancel_before: str = ""  # stage name to abandon at, for interrupt tests
    confirm_write: bool = True
    resume: bool | None = True  # what to answer if a draft is offered
    bulk_not_applicable: bool = False
    accept_scaffold: bool = True
    edits: dict[str, object] = field(default_factory=dict)  # review edits, by profile path
    asked: list[str] = field(default_factory=list)
    resume_offers: list[DraftInfo] = field(default_factory=list)
    welcomes: list[Welcome] = field(default_factory=list)
    review: _flow.Review | None = None
    stages: list[str] = field(default_factory=list)
    flow: _flow.Flow | None = None

    def open(self, welcome: Welcome) -> bool | None:
        self.welcomes.append(welcome)
        if welcome.draft is None:
            return True
        self.resume_offers.append(welcome.draft)
        return self.resume

    def collect(self, flow: _flow.Flow, *, on_progress: Callable[[], None]) -> str:
        self.flow = flow  # kept so a test can read what the run proposed and recorded
        while True:
            stage = flow.next_stage()
            if stage == self.cancel_before:
                raise Cancelled()
            self.stages.append(stage)
            if stage == "decisions":
                flow.answer_decisions(self._answer(flow.decisions_plan()))
            elif stage == "level":
                flow.answer_level(self._answer(flow.level_plan(), prefix="level."))
            elif stage == "gates":
                gate_answers, bulk = self._answer_gates(flow)
                flow.answer_gates(gate_answers, bulk=bulk)
            elif stage == "remainder":
                flow.answer_remainder(self._answer(flow.remainder_plan()))
            elif stage == "scaffold":
                offers = flow.scaffold_offers()
                flow.accept_scaffold(offers if self.accept_scaffold else [])
            else:
                break
            on_progress()
        # Overrides for proposed values nothing presented: recorded as typed, like a review edit.
        for key, value in self.answers.items():
            if key not in self.asked and key in flow.proposals:
                flow._record_answer(key, value)
                self.asked.append(key)
        for path, value in self.edits.items():
            flow.edit(path, value)
        self.review = flow.review()
        if not self.confirm_write:
            raise Cancelled()
        if self.review.error:
            raise AssertionError(f"ScriptedInterview: the review refuses to write: {self.review.error}")
        return flow.approve()

    def _answer(self, section: plan.SectionPlan, prefix: str = "") -> dict:
        answers: dict = {}
        for spec in section.fields:
            if not spec.applies(answers):
                continue
            key = f"{prefix}{spec.id}"
            self.asked.append(key)
            if key in self.answers:
                answers[spec.id] = self.answers[key]
            elif spec.kind == "multiselect":
                answers[spec.id] = [c.strip() for c in str(spec.default).split(",") if c.strip()]
            elif spec.default and spec.kind not in ("choice",):
                answers[spec.id] = spec.default
            elif not spec.validate and spec.kind in ("text", "textarea"):
                answers[spec.id] = ""
            else:
                raise AssertionError(
                    f"ScriptedInterview: the flow asks for {key!r} and the script has no answer "
                    f"for it. Fields asked so far in this section: {sorted(answers)}"
                )
        return answers

    def _answer_gates(self, flow: _flow.Flow) -> tuple[dict, tuple[str, set[str]] | None]:
        seeds = flow.gate_seeds()
        answers: dict = {}
        bulk: set[str] = set()
        for spec in flow.gate_specs():
            local: dict = {}
            for gate_field in spec.fields:
                key = f"gates.{spec.id}.{gate_field.id}"
                short = f"{spec.id}.{gate_field.id}"
                if not gate_field.applies(local):
                    continue
                self.asked.append(key)
                if (
                    gate_field.id == "artefact"
                    and spec.id in scaffold.SEEDABLE
                    and self.answers.get(key, seeds.get(short)) == scaffold.SEEDABLE[spec.id][0]
                    and not (flow.repo / scaffold.SEEDABLE[spec.id][0]).exists()
                ):
                    # The seed path named before the file exists: as on the screen, left blank so
                    # the scaffold offer supplies it (or the review refuses if declined).
                    continue
                if key in self.answers:
                    local[gate_field.id] = self.answers[key]
                elif short in seeds:
                    local[gate_field.id] = seeds[short]
                elif gate_field.id == "status" and self.bulk_not_applicable:
                    local[gate_field.id] = "not_applicable"
                    bulk.add(spec.id)
                elif gate_field.default and gate_field.kind != "choice":
                    local[gate_field.id] = gate_field.default
                elif (
                    gate_field.id == "artefact"
                    and spec.id in scaffold.SEEDABLE
                    and not (flow.repo / scaffold.SEEDABLE[spec.id][0]).exists()
                ):
                    # As on the screen: a seedable gate's artefact may stay blank, and the
                    # scaffold offer that follows this stage supplies it or the review refuses.
                    continue
                else:
                    raise AssertionError(
                        f"ScriptedInterview: the gate list asks for {key!r} and the script has no "
                        f"answer for it (and nothing was proposed)."
                    )
            for field_id, value in local.items():
                answers[f"{spec.id}.{field_id}"] = value
        return answers, (("not_applicable", bulk) if bulk else None)

    def assert_no_unused_keys(self) -> None:
        """The other half of the guarantee: an answer nothing asked for and nothing proposed is a
        test failure too, because it usually means a field was renamed or dropped and the script
        kept feeding it."""
        unused = sorted(set(self.answers) - set(self.asked))
        assert not unused, f"{len(unused)} scripted answer(s) were never asked for: {unused}"
