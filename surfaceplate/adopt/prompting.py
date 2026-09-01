"""How a question gets asked, kept separate from what the wizard asks.

Every section module calls methods on a `Prompt` object rather than `questionary` directly. In
production that object is `InteractivePrompt`, a thin wrapper over `questionary`. In tests it is
`ScriptedPrompt`, which returns pre-set answers in order and records exactly what was asked.

This is what makes the binding rule testable rather than merely stated. "The tool never invents a
value" is a claim about *data flow* - every field in the written profile must trace to something a
`Prompt.text`/`.select`/`.confirm` call returned - and that is only checkable if asking and doing are
different objects. `ScriptedPrompt` also raises if the wizard asks something no answer was queued
for, or leaves an answer unconsumed - the two-sided version of "nothing was invented": nothing
missing, and nothing extra.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class Cancelled(Exception):
    """Raised when the human backs out - Ctrl-C, Esc, or an explicit quit.

    Caught once, at the top level (`wizard.run`), which is what makes "an interrupt leaves the
    repository untouched" true by construction rather than by every section remembering to check:
    nothing downstream of a question ever runs unless the question was actually answered.
    """


class Prompt(Protocol):
    def text(self, message: str, *, help: str | None = None, default: str = "") -> str: ...

    def select(
        self, message: str, choices: list[tuple[str, str]], *, help: str | None = None
    ) -> str:
        """`choices` are (value, label) pairs. Nothing is pre-selected; returns the chosen value."""
        ...

    def confirm(self, message: str, *, help: str | None = None, default: bool | None = None) -> bool:
        """`default=None` means no default - the human must actually answer, not just press Enter."""
        ...


@dataclass
class InteractivePrompt:
    """The real thing: a terminal, driven by `questionary`."""

    def text(self, message: str, *, help: str | None = None, default: str = "") -> str:
        import questionary

        if help:
            print(f"  {help}")
        answer = questionary.text(message, default=default).ask()
        if answer is None:
            raise Cancelled()
        return answer

    def select(
        self, message: str, choices: list[tuple[str, str]], *, help: str | None = None
    ) -> str:
        import questionary

        if help:
            print(f"  {help}")
        answer = questionary.select(
            message, choices=[questionary.Choice(title=label, value=value) for value, label in choices]
        ).ask()
        if answer is None:
            raise Cancelled()
        return answer

    def confirm(self, message: str, *, help: str | None = None, default: bool | None = None) -> bool:
        import questionary

        if help:
            print(f"  {help}")
        # questionary's own `default` is a plain bool, not Optional - there is no such thing as a
        # cursor with nothing highlighted in a terminal prompt. `default=None` here means "this is
        # a genuine decision, not a convenience default" - honoured by defaulting the CURSOR to
        # the refusing answer, so a distracted Enter fails closed rather than silently proceeding,
        # which is what actually matters for the write-confirmation this exists to protect.
        answer = questionary.confirm(message, default=bool(default)).ask()
        if answer is None:
            raise Cancelled()
        return answer


@dataclass
class ScriptedPrompt:
    """A `Prompt` driven by a pre-written script, for tests and for nothing else.

    `answers` is consumed strictly in order. Asking past the end of the script, or finishing a run
    with answers left unconsumed, is a test failure - both directions of "the tool asked for exactly
    what it used, and used exactly what it asked for."
    """

    answers: list[object]
    asked: list[str] = field(default_factory=list)
    _index: int = 0

    def _next(self, message: str) -> object:
        self.asked.append(message)
        if self._index >= len(self.answers):
            raise AssertionError(
                f"ScriptedPrompt: asked {message!r} but the script has no more answers "
                f"({len(self.asked)} questions asked so far)."
            )
        value = self.answers[self._index]
        self._index += 1
        return value

    def text(self, message: str, *, help: str | None = None, default: str = "") -> str:
        value = self._next(message)
        assert isinstance(value, str), f"{message!r} expected a text answer, script had {value!r}"
        return value

    def select(
        self, message: str, choices: list[tuple[str, str]], *, help: str | None = None
    ) -> str:
        value = self._next(message)
        valid = {v for v, _ in choices}
        assert value in valid, f"{message!r}: {value!r} is not one of {sorted(valid)}"
        return value  # type: ignore[return-value]

    def confirm(self, message: str, *, help: str | None = None, default: bool | None = None) -> bool:
        value = self._next(message)
        assert isinstance(value, bool), f"{message!r} expected a bool, script had {value!r}"
        return value

    def assert_exhausted(self) -> None:
        remaining = len(self.answers) - self._index
        assert remaining == 0, f"{remaining} scripted answer(s) were never asked for."
