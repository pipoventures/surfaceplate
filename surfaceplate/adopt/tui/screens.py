"""The screens, one per kind of thing the mockup shows.

Three of these are the mockup's own frames, reproduced rather than reinterpreted (`DR-36`):

- `FormScreen` is frame 01 - every field of a section on screen at once, a fixed label column,
  answered values staying visible as plain text rather than re-entry chrome.
- `LevelScreen` is frame 02 - a recap of what earlier sections established, then a numbered list in
  which **highlighting an option is explicitly not choosing it**, with the highlighted option
  revealing the concrete controls that level names.
- `GatesScreen` is frame 03 - several gates on screen at once, chip rows, and follow-up fields that
  appear inside a gate's own block only once its status calls for them.

`ReviewScreen` and `ResumeScreen` are this packet's own: the mockup deliberately stopped short of
the confirmation screen ("Neither render writes anything - `surfaceplate adopt` only touches disk
after a final confirmation screen, not shown here").

**One behaviour worth knowing about, found by probing rather than assumed.** Textual's `Input`
starts with its whole value selected, so the first keystroke *replaces* a preset value. That would
have silently destroyed Phase 1's editable example answers - the "recognition over recall" feature
`DR-35` added - the moment anyone typed. `EditableInput` below collapses the selection to the end on
mount, so a shown example is genuinely edited rather than wiped.
"""

from __future__ import annotations

from typing import Callable

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Input,
    Label,
    OptionList,
    RadioButton,
    RadioSet,
    Static,
    TextArea,
)
from textual.widgets.option_list import Option

from surfaceplate.adopt import plan, validators

CANCELLED = "__cancelled__"


class EditableInput(Input):
    """An `Input` whose preset value is editable rather than replaced by the first keystroke.

    Textual selects an `Input`'s whole value and re-selects it on focus, so the first keystroke
    overwrites it. For a blank field that is invisible - but every example answer
    `example_answers.py` offers is a preset value, and losing one to a stray keypress would quietly
    undo the reason those examples exist (`DR-35`'s recognition-over-recall).

    `select_on_focus=False` is the supported way to turn that off; collapsing the selection in
    `on_mount` was tried first and does not hold, because focus re-selects afterwards. Both the
    behaviour and the fix were found by driving the real widget, and
    `tests/test_adopt_tui.py::test_example_defaults_survive_being_typed_into` is the regression.
    """

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("select_on_focus", False)
        super().__init__(**kwargs)

    def on_mount(self) -> None:
        self.action_end()


def _widget_for(spec: plan.FieldSpec, value: object = None):
    """One field, as the widget its kind calls for. `id` carries the field id so a screen's widgets
    and its plan's fields can be joined by `tests/test_adopt_tui.py`.

    A `choice` field becomes a `RadioSet` with **nothing pre-selected**. That is deliberate and is
    the same rule the level screen states out loud: a value nobody picked is not an answer, so
    `mode`, `data_classification` and `adoption_status` all start genuinely empty rather than
    quietly defaulting to whichever option happens to be listed first.
    """
    widget_id = f"f-{spec.id.replace('.', '--')}"
    if spec.kind == "bool":
        initial = bool(value) if value is not None else bool(spec.default)
        return Checkbox(spec.label, value=initial, id=widget_id)
    if spec.kind == "choice":
        buttons = [
            RadioButton(label, value=(value == choice_value), id=f"r-{spec.id.replace('.', '--')}--{choice_value}")
            for choice_value, label in spec.choices
        ]
        return RadioSet(*buttons, id=widget_id)
    if spec.kind == "textarea":
        return TextArea(str(value if value is not None else spec.default), id=widget_id)
    return EditableInput(
        value=str(value if value is not None else spec.default),
        placeholder=spec.label,
        id=widget_id,
    )


def _read_widget(widget) -> object:
    if isinstance(widget, Checkbox):
        return bool(widget.value)
    if isinstance(widget, RadioSet):
        pressed = widget.pressed_button
        if pressed is None or not pressed.id:
            return None
        return pressed.id.split("--")[-1]
    if isinstance(widget, TextArea):
        return widget.text
    return widget.value


class _SectionScreenBase(Screen):
    """Shared chrome: a framed body, a docked hint line, and quit-is-cancel."""

    BINDINGS = [
        Binding("ctrl+q", "cancel", "quit", show=True),
        Binding("ctrl+s", "commit", "continue", show=True),
    ]

    def __init__(self, section: plan.SectionPlan, *, step: str = "") -> None:
        super().__init__()
        self.section = section
        self.step = step

    def field_ids(self) -> list[str]:
        """Every field id this screen actually renders. `tests/test_adopt_tui.py` joins this
        against the section's own plan - the check that makes the scripted interview's guarantee
        mean something about the screens, not only about the plan."""
        ids = []
        for widget in self.query(".field-widget"):
            if widget.id and widget.id.startswith("f-"):
                ids.append(widget.id[2:].replace("--", "."))
        return ids

    def action_cancel(self) -> None:
        self.dismiss(CANCELLED)

    def action_commit(self) -> None:  # overridden
        pass


class FormScreen(_SectionScreenBase):
    """The mockup's frame 01, generalised: a whole section on one screen.

    Conditional fields (`FieldSpec.depends_on`) are rendered but hidden until their condition
    holds, and re-evaluated whenever anything changes - which is how `status_rationale` and
    `independent_validator` appear exactly when they apply.
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="frame"):
            yield Static(f"[{self.step}{self.section.title}]", classes="section-header")
            if self.section.intro:
                yield Static(self.section.intro, classes="intro")
            for line in self.section.recap:
                yield Static(f"  {line}", classes="recap")
            for note in self.section.notes:
                yield Static(f"  {note}", classes="note")
            with VerticalScroll():
                for spec in self.section.fields:
                    with Vertical(classes="field-row", id=f"row-{spec.id.replace('.', '--')}"):
                        if spec.kind != "bool":
                            yield Label(spec.label, classes="field-label")
                        widget = _widget_for(spec)
                        widget.add_class("field-widget")
                        yield widget
                        if spec.help:
                            yield Static(spec.help, classes="field-help")
        yield Static("", id="hint")

    def on_mount(self) -> None:
        self._refresh_visibility()
        self._set_hint()

    def _answers(self) -> dict:
        answers: dict = {}
        for spec in self.section.fields:
            try:
                widget = self.query_one(f"#f-{spec.id.replace('.', '--')}")
            except Exception:
                continue
            answers[spec.id] = _read_widget(widget)  # type: ignore[arg-type]
        return answers

    def _refresh_visibility(self) -> None:
        answers = self._answers()
        for spec in self.section.fields:
            row = self.query_one(f"#row-{spec.id.replace('.', '--')}")
            row.display = spec.applies(answers)

    @on(Checkbox.Changed)
    @on(Input.Changed)
    @on(RadioSet.Changed)
    def _on_change(self, event: events.Event) -> None:
        self._refresh_visibility()

    def _set_hint(self, error: str = "") -> None:
        hint = self.query_one("#hint", Static)
        keys = "[Tab] next  [⇧Tab] back  [Ctrl+S] continue  [Ctrl+Q] cancel"
        hint.update(f"[b]{error}[/b]\n{keys}" if error else keys)

    def action_commit(self) -> None:
        answers = self._answers()
        for spec in self.section.fields:
            if not spec.applies(answers):
                answers.pop(spec.id, None)
                continue
            problem = validators.check(spec.validate, answers.get(spec.id, ""))
            if problem:
                self._set_hint(f"{spec.label}: {problem}")
                try:
                    self.query_one(f"#f-{spec.id.replace('.', '--')}").focus()
                except Exception:
                    pass
                return
        self.dismiss(answers)


class LevelScreen(_SectionScreenBase):
    """The mockup's frame 02. Highlighting is not choosing, and the screen says so."""

    BINDINGS = [
        Binding("ctrl+q", "cancel", "quit", show=True),
        Binding("question_mark", "why", "why does this matter", show=True),
    ]

    def __init__(self, section: plan.SectionPlan, *, step: str = "") -> None:
        super().__init__(section, step=step)
        self.spec = section.fields[0]
        self._why_shown = False

    def compose(self) -> ComposeResult:
        with Vertical(id="frame"):
            yield Static(f"[{self.step}{self.section.title}]", classes="section-header")
            if self.section.recap:
                yield Static("You told us:", classes="recap")
                for line in self.section.recap:
                    yield Static(f"  {line}", classes="recap")
            yield Static("─" * 60, classes="rule")
            for note in self.section.notes:
                yield Static(f"  {note}", classes="note")
            options = [
                Option(label, id=value) for value, label in self.spec.choices
            ]
            widget = OptionList(*options, id=f"f-{self.spec.id}")
            widget.add_class("field-widget")
            yield widget
            yield Static("", classes="level-meta", id="level-meta")
            yield Static("", classes="intro", id="why")
        yield Static("", id="hint")

    def on_mount(self) -> None:
        self.query_one("#why", Static).display = False
        self._update_meta()
        self._set_hint()

    def _set_hint(self) -> None:
        self.query_one("#hint", Static).update(
            "nothing is chosen yet · [↑↓] move  [Enter] choose  [?] why does this matter  "
            "[Ctrl+Q] cancel"
        )

    def _update_meta(self) -> None:
        option_list = self.query_one(OptionList)
        index = option_list.highlighted
        meta = self.query_one("#level-meta", Static)
        if index is None:
            meta.update("")
            return
        level = self.spec.choices[index][0]
        meta.update("  " + " · ".join(plan.level_controls(level)))

    @on(OptionList.OptionHighlighted)
    def _on_highlight(self, event: OptionList.OptionHighlighted) -> None:
        self._update_meta()

    @on(OptionList.OptionSelected)
    def _on_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss({self.spec.id: self.spec.choices[event.option_index][0]})

    def action_why(self) -> None:
        why = self.query_one("#why", Static)
        self._why_shown = not self._why_shown
        why.display = self._why_shown
        why.update(self.section.intro)


class GatesScreen(_SectionScreenBase):
    """The mockup's frame 03: several gates at once, browsable, with inline follow-ups.

    Every gate is rendered - the screen scrolls rather than paging - so `Tab`/`⇧Tab` move between
    gates, an answered gate keeps its lit chip and stays editable, and `[g]` jumps to the next
    section heading. The bottom line counts what has been answered, which is the mockup's
    substitute for a progress bar.
    """

    # `ctrl+g`, not a bare `g`: a focused text field consumes printable characters, so a bare
    # letter binding would be typed into a rationale instead of jumping. Found by building it -
    # the mockup's `[g]` legend assumes a keystroke the real widget tree never sees.
    BINDINGS = [
        Binding("ctrl+q", "cancel", "quit", show=True),
        Binding("ctrl+s", "commit", "continue", show=True),
        Binding("ctrl+g", "jump_section", "jump to section", show=True),
    ]

    def __init__(self, specs: tuple[plan.GateSpec, ...], section: plan.SectionPlan, *, step: str = "") -> None:
        super().__init__(section, step=step)
        self.specs = specs
        self._chosen: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        with Vertical(id="frame"):
            yield Static(f"[{self.step}{self.section.title}]", classes="section-header")
            yield Static(self.section.intro, classes="intro")
            with VerticalScroll(id="gate-list"):
                current_section = ""
                for spec in self.specs:
                    if spec.section != current_section:
                        current_section = spec.section
                        yield Static(
                            f"{current_section} · gates in this group",
                            classes="section-subline",
                            id=f"sec-{current_section.replace(' ', '-').lower()}",
                        )
                    yield from self._compose_gate(spec)
        yield Static("", id="hint")

    def _compose_gate(self, spec: plan.GateSpec) -> ComposeResult:
        with Vertical(classes="gate", id=f"gate-{spec.id}"):
            yield Static(spec.id, classes="gate-name")
            yield Static(spec.explanation, classes="gate-desc")
            if spec.mandatory:
                yield Static(
                    "  [required] — the level requires this gate; its precondition is yours to state",
                    classes="gate-locked",
                )
            elif spec.auto_status:
                yield Static(
                    f"  [{spec.auto_status.replace('_', ' ')}] — settled by an earlier answer",
                    classes="gate-locked",
                )
            for field_spec in spec.fields:
                key = f"{spec.id}.{field_spec.id}"
                prefixed = plan.FieldSpec(
                    id=key,
                    label=field_spec.label,
                    kind=field_spec.kind,
                    help=field_spec.help,
                    default=field_spec.default,
                    choices=field_spec.choices,
                    validate=field_spec.validate,
                )
                with Vertical(classes="followups", id=f"row-{key.replace('.', '--')}"):
                    if field_spec.kind == "choice":
                        # The mockup's chip row: horizontal, compact, and the chosen one inverts to
                        # amber fill. A vertical list would have been easier and would not have been
                        # what was approved.
                        row = Horizontal(
                            *(
                                Button(label.split(" - ")[0], id=f"chip-{spec.id}--{value}", classes="chip")
                                for value, label in field_spec.choices
                            ),
                            classes="chip-row",
                            id=f"f-{key.replace('.', '--')}",
                        )
                        row.add_class("field-widget")
                        yield row
                    else:
                        if field_spec.kind != "bool":
                            yield Label(field_spec.label, classes="field-label")
                        widget = _widget_for(prefixed)
                        widget.add_class("field-widget")
                        yield widget

    def on_mount(self) -> None:
        self._refresh_visibility()
        self._set_hint()

    def _answers(self) -> dict:
        answers: dict = {}
        for spec in self.specs:
            for field_spec in spec.fields:
                key = f"{spec.id}.{field_spec.id}"
                if field_spec.kind == "choice":
                    # A chip row shows three options and no default. Until one is pressed the gate
                    # has no status - the same "nothing is chosen yet" rule the level screen states
                    # out loud, applied where it matters most: a gate nobody decided must not
                    # silently acquire the first status in the list.
                    answers[key] = self._chosen.get(spec.id)
                    continue
                try:
                    widget = self.query_one(f"#f-{key.replace('.', '--')}")
                except Exception:
                    continue
                answers[key] = _read_widget(widget)  # type: ignore[arg-type]
        return answers

    def _status_of(self, spec: plan.GateSpec, answers: dict) -> str | None:
        if spec.mandatory:
            return "required"
        if spec.auto_status:
            return spec.auto_status
        return answers.get(f"{spec.id}.status")  # type: ignore[return-value]

    def _refresh_visibility(self) -> None:
        answers = self._answers()
        for spec in self.specs:
            for field_spec in spec.fields:
                key = f"{spec.id}.{field_spec.id}"
                row = self.query_one(f"#row-{key.replace('.', '--')}")
                if field_spec.depends_on is None:
                    row.display = True
                    continue
                other, wanted = field_spec.depends_on
                row.display = answers.get(f"{spec.id}.{other}") in wanted
        self._set_hint()

    @on(Button.Pressed)
    def _on_chip(self, event: Button.Pressed) -> None:
        """A chip press records that gate's status and lights the chip."""
        button_id = event.button.id or ""
        if not button_id.startswith("chip-"):
            return
        gate_id, _, status = button_id[len("chip-"):].partition("--")
        self._chosen[gate_id] = status
        for chip in self.query(".chip"):
            chip_id = chip.id or ""
            if chip_id.startswith(f"chip-{gate_id}--"):
                chip.set_class(chip_id.endswith(f"--{status}"), "chip-selected")
        self._refresh_visibility()

    @on(Input.Changed)
    @on(Checkbox.Changed)
    def _on_change(self, event: events.Event) -> None:
        self._set_hint()

    def _answered_count(self, answers: dict | None = None) -> int:
        answers = self._answers() if answers is None else answers
        return sum(1 for spec in self.specs if self._status_of(spec, answers))

    def _set_hint(self, error: str = "") -> None:
        total = len(self.specs)
        done = self._answered_count()
        keys = "[Tab] move  [Ctrl+G] jump to section  [Ctrl+S] continue  [Ctrl+Q] cancel"
        line = f"{done} of {total} answered · {keys}"
        self.query_one("#hint", Static).update(f"[b]{error}[/b]\n{line}" if error else line)

    def action_jump_section(self) -> None:
        headings = list(self.query(".section-subline"))
        if not headings:
            return
        scroll = self.query_one("#gate-list", VerticalScroll)
        current = getattr(self, "_jump_index", -1) + 1
        if current >= len(headings):
            current = 0
        self._jump_index = current
        scroll.scroll_to_widget(headings[current], top=True)

    def action_commit(self) -> None:
        answers = self._answers()
        for spec in self.specs:
            status = self._status_of(spec, answers)
            if status is None:
                self._set_hint(f"{spec.id}: choose a status before continuing.")
                return
            for field_spec in spec.fields:
                key = f"{spec.id}.{field_spec.id}"
                if field_spec.depends_on is not None:
                    other, wanted = field_spec.depends_on
                    if answers.get(f"{spec.id}.{other}") not in wanted:
                        answers.pop(key, None)
                        continue
                problem = validators.check(field_spec.validate, answers.get(key, ""))
                if problem:
                    self._set_hint(f"{spec.id} · {field_spec.label}: {problem}")
                    return
        # Statuses that were settled rather than chosen are recorded explicitly, so the answers
        # this screen returns describe the whole section rather than only its free choices.
        for spec in self.specs:
            if spec.mandatory or spec.auto_status:
                answers.pop(f"{spec.id}.status", None)
        self.dismiss({k: v for k, v in answers.items() if v is not None})


class ReviewScreen(Screen):
    """The confirmation the mockup deliberately did not draw. Nothing is written before it."""

    BINDINGS = [
        Binding("ctrl+q", "cancel", "quit", show=True),
        Binding("ctrl+s", "confirm", "write", show=True),
    ]

    def __init__(self, rendered: str, error: str = "") -> None:
        super().__init__()
        self.rendered = rendered
        self.error = error

    def compose(self) -> ComposeResult:
        with Vertical(id="frame"):
            yield Static("[Review — nothing has been written yet]", classes="section-header")
            if self.error:
                yield Static(self.error, id="review-error")
            with VerticalScroll(id="review-body"):
                yield Static(self.rendered)
        yield Static(
            "[Ctrl+S] write it  [Ctrl+Q] cancel, keeping your draft", id="hint"
        )

    def action_confirm(self) -> None:
        if self.error:
            return
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class ResumeScreen(Screen):
    """Offered, never silent - `DR-35`'s rule, and a version mismatch is stated, not hidden."""

    BINDINGS = [
        Binding("y", "resume", "resume", show=True),
        Binding("n", "fresh", "start fresh", show=True),
    ]

    def __init__(self, info) -> None:
        super().__init__()
        self.info = info

    def compose(self) -> ComposeResult:
        with Vertical(id="frame"):
            yield Static("[A saved draft was found]", classes="section-header")
            yield Static(
                f"It has answers for: {', '.join(self.info.sections)}.", classes="intro"
            )
            if self.info.matches:
                yield Static(
                    "It was answered against the framework version installed here now.",
                    classes="note",
                )
            else:
                yield Static(
                    "It was started against a different framework version or digest than what is "
                    "installed here now - resuming may carry answers into a wizard that no longer "
                    "asks for them the same way.",
                    classes="error",
                )
        yield Static("[y] resume it  [n] start fresh (the draft is discarded)", id="hint")

    def action_resume(self) -> None:
        self.dismiss(True)

    def action_fresh(self) -> None:
        self.dismiss(False)
