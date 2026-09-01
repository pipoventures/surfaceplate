"""How a whole section gets asked, kept separate from what is asked and from what it becomes.

This replaces `prompting.py`'s three-method `Prompt`. `DR-36` records why: a protocol shaped
`text(message) -> str` is one call, one answer, and the approved mockup's gate catalogue shows
three gates at once, each with a chip row and follow-ups that appear only once a status is chosen.
That screen has no signature in the old vocabulary. So the collaborator gets coarser - a section at
a time instead of a question at a time - while keeping the shape that made the old one useful: one
Protocol, one real implementation (`tui/`), one scripted implementation (here), and `Cancelled`
raised at the seam so an abandoned run has exactly one exit path.

**What the scripted implementation now proves, and what it does not.** `ScriptedInterview` walks
the same `plan.SectionPlan` the screens walk, raises on any planned field it has no answer for, and
`assert_no_unused_keys()` raises on any answer no field asked for. That is the same two-sided
guarantee `ScriptedPrompt` gave, keyed rather than positional. What it still cannot prove on its own
is that the *screens* ask the plan - it proves the plan was answered. `tests/test_adopt_tui.py`
closes that with a field-id join per screen, and `tests/test_provenance.py` closes the other side by
proving no value reaches the profile that no answer supplied. All three are needed; any one alone
is the kind of partial guarantee `F32` walked through.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from surfaceplate.adopt import plan

# Bumped when the shape of a draft's `sections` changes incompatibly. Phase 1 drafts stored built
# profile fragments; Phase 2 stores raw answers keyed by `FieldSpec.id`, which are not
# interchangeable - resuming one as the other would produce a confidently wrong profile rather than
# an error, so the format is stated and checked rather than inferred from the framework version.
DRAFT_FORMAT = 2


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


class Interview(Protocol):
    def confirm_resume(self, info: DraftInfo) -> bool:
        """Whether to resume an unfinished run. Never answered on a human's behalf: a draft is
        offered, never silently reloaded."""
        ...

    def collect(
        self,
        *,
        repo: Path,
        resumed: dict,
        on_section_complete: Callable[[str, dict], None],
        preview: Callable[[dict], str],
    ) -> dict:
        """Ask every section not already in `resumed`, and return the accumulated raw answers.

        - `on_section_complete(name, answers)` is called as each section commits, so a draft is
          saved and a late failure loses at most the section in progress.
        - `preview(state)` assembles, renders and verifies without writing anything; the review
          screen shows what it returns, and a `WriteRefused` from it is shown rather than raised
          through the interface.
        - Raises `Cancelled` if the human abandons the run or declines the final write.
        """
        ...


@dataclass
class ScriptedInterview:
    """An `Interview` driven by a keyed script, for tests and for nothing else.

    `answers` is keyed `"<section>.<field id>"` - for example `"identity.application_id"` or
    `"gates.work_registration.artefact"`. Order is deliberately not significant: a screen shows a
    whole section at once, so there is no order for a script to depend on, and keying by field makes
    a failure say which field rather than which position.
    """

    answers: dict[str, object]
    cancel_before: str = ""  # section name to abandon at, for interrupt tests
    confirm_write: bool = True
    resume: bool = True  # what to answer if a draft is offered
    asked: list[str] = field(default_factory=list)
    resume_offers: list[DraftInfo] = field(default_factory=list)
    previewed: str = ""

    def confirm_resume(self, info: DraftInfo) -> bool:
        self.resume_offers.append(info)
        return self.resume

    def collect(
        self,
        *,
        repo: Path,
        resumed: dict,
        on_section_complete: Callable[[str, dict], None],
        preview: Callable[[dict], str],
    ) -> dict:
        state = dict(resumed)
        for name in plan.SECTION_ORDER:
            if name in state:
                continue
            if name == self.cancel_before:
                raise Cancelled()
            section = plan.section_plan(name, repo=repo, state=state)
            state[name] = self._answer_section(section)
            on_section_complete(name, state[name])

        self.previewed = preview(state)
        if not self.confirm_write:
            raise Cancelled()
        return state

    def _answer_section(self, section: plan.SectionPlan) -> dict:
        answers: dict = {}
        for spec in section.fields:
            if not spec.applies(answers):
                continue
            key = f"{section.name}.{spec.id}"
            self.asked.append(key)
            if key not in self.answers:
                raise AssertionError(
                    f"ScriptedInterview: the plan asks for {key!r} and the script has no answer "
                    f"for it. Fields asked so far in this section: {sorted(answers)}"
                )
            answers[spec.id] = self.answers[key]
        return answers

    def assert_no_unused_keys(self) -> None:
        """The other half of the guarantee: an answer nothing asked for is a test failure too,
        because it usually means a field was renamed or dropped and the script kept feeding it."""
        unused = sorted(set(self.answers) - set(self.asked))
        assert not unused, f"{len(unused)} scripted answer(s) were never asked for: {unused}"
