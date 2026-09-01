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

import textwrap
from typing import Callable

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, Vertical, VerticalScroll
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
    # No `placeholder=spec.label`. It duplicated the label the row already renders, so every field
    # printed its own name twice - `F37` #3, visible as "Precondition artefact (a real path)"
    # stacked directly above an input containing the same words.
    return EditableInput(
        value=str(value if value is not None else spec.default),
        id=widget_id,
    )


def hint_line(*, keys: str, help_text: str = "", error: str = "") -> str:
    """One legend, assembled as literal text.

    `F37` #1 and #2: Textual parses `[Tab]` and `[Enter]` as style tags and swallows them, while
    symbol-bearing keys such as `[Ctrl+S]` and `[↑↓]` survive - so a legend could lose its two most
    important keys and still look plausible in review. The resume screen lost both of its only keys
    and offered a choice with no visible way to make it. Every widget this string reaches is
    constructed with `markup=False`, which is the supported way to keep it literal
    (`textual/widgets/_static.py`).
    """
    parts = [p for p in (error, help_text) if p]
    parts.append(keys)
    return "\n".join(parts)


def _first_sentence(text: str) -> str:
    """The opening sentence of an explanation, for a one-line gate summary.

    The full text is not lost - it is shown in the hint line while that gate has focus, the same
    way a form field's help is. Rendering all five lines of it inside every gate block is what made
    the catalogue unreadable (`F37` #6).
    """
    head = text.split(". ")[0].strip()
    if not head.endswith("."):
        head += "."
    return head


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
                    # `HorizontalGroup`, not `Horizontal`: the latter is `height: 1fr` and would
                    # give one row the whole screen. This is what makes the label a column beside
                    # its value rather than a line stacked above it (`F37` #4).
                    with HorizontalGroup(
                        classes="field-row", id=f"row-{spec.id.replace('.', '--')}"
                    ):
                        if spec.kind != "bool":
                            yield Label(spec.label, classes="field-label")
                        widget = _widget_for(spec)
                        widget.add_class("field-widget")
                        yield widget
        # Help is not rendered per field. It belongs to whichever field has focus, and it lives in
        # the hint line - which is what the mockup drew and what Phase 2's own plan specified
        # before shipping the opposite (`F37` #5).
        yield Static("", id="hint", markup=False)

    def on_mount(self) -> None:
        self._refresh_visibility()
        self._set_hint()

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
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

    def _focused_spec(self) -> plan.FieldSpec | None:
        """The `FieldSpec` behind whichever widget currently has focus, if any."""
        focused = self.focused
        if focused is None or not focused.id or not focused.id.startswith("f-"):
            return None
        field_id = focused.id[2:].replace("--", ".")
        return next((s for s in self.section.fields if s.id == field_id), None)

    def _set_hint(self, error: str = "") -> None:
        spec = self._focused_spec()
        self.query_one("#hint", Static).update(
            hint_line(
                keys="[Tab] next  [⇧Tab] back  [Ctrl+S] continue  [Ctrl+Q] cancel",
                help_text=spec.help if spec and spec.help else "",
                error=error,
            )
        )

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
            widget = OptionList(*self._options(), id=f"f-{self.spec.id}")
            widget.add_class("field-widget")
            yield widget
            yield Static("", classes="level-meta", id="level-meta", markup=False)
            yield Static("", classes="intro", id="why")
        yield Static("", id="hint", markup=False)

    def on_mount(self) -> None:
        self.query_one("#why", Static).display = False
        self._update_meta()
        self._set_hint()

    def _options(self, highlighted: int | None = 0) -> list[Option]:
        """Numbered, with a caret on the highlighted row.

        Textual has no built-in marker gutter short of overriding `_get_left_gutter_width` and
        `render_line` the way `SelectionList` does. With three fixed options, rebuilding the
        prompts on each move is cheaper than that machinery and keeps the caret in the rendered
        text, where `tests/test_render.py` can see it.
        """
        options = []
        for index, (value, label) in enumerate(self.spec.choices):
            caret = "▸" if index == highlighted else " "
            head, _, blurb = label.partition(". ")
            prompt = f"{caret} {index + 1}  {head}."
            if blurb:
                # Wrapped here rather than left to the widget: an OptionList continuation line
                # starts at column 0, which breaks the list into a paragraph and loses the
                # structure the numbering exists to give it.
                wrapped = textwrap.wrap(blurb, width=66) or [blurb]
                prompt += "".join(f"\n      {line}" for line in wrapped)
            options.append(Option(prompt, id=value))
        return options

    def _set_hint(self) -> None:
        self.query_one("#hint", Static).update(
            hint_line(
                keys="nothing is chosen yet · [↑↓] move  [Enter] choose  "
                "[?] why does this matter  [Ctrl+Q] cancel"
            )
        )

    def _update_meta(self) -> None:
        option_list = self.query_one(OptionList)
        index = option_list.highlighted
        meta = self.query_one("#level-meta", Static)
        if index is None:
            meta.update("")
            return
        level = self.spec.choices[index][0]
        # Anchored to the highlighted option and labelled, rather than floating under the whole
        # list where it read as belonging to the last row (`F37`).
        meta.update(f"  {level} checks: " + " · ".join(plan.level_controls(level)))

    @on(OptionList.OptionHighlighted)
    def _on_highlight(self, event: OptionList.OptionHighlighted) -> None:
        self._update_meta()
        self._move_caret(event.option_index)

    def _move_caret(self, highlighted: int | None) -> None:
        """Redraw the three prompts so the caret sits on the highlighted row. Highlighting still
        chooses nothing - the caret marks where you are, and the hint line says so."""
        option_list = self.query_one(OptionList)
        if getattr(self, "_caret_at", None) == highlighted:
            return
        self._caret_at = highlighted
        option_list.clear_options()
        option_list.add_options(self._options(highlighted))
        if highlighted is not None:
            option_list.highlighted = highlighted

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
                        first = self.specs.index(spec) + 1
                        last = first + sum(
                            1 for g in self.specs if g.section == current_section
                        ) - 1
                        yield Static(
                            f"{current_section} · gates {first}\u2013{last} of {len(self.specs)}",
                            classes="section-subline",
                            id=f"sec-{current_section.replace(' ', '-').lower()}",
                            markup=False,
                        )
                    yield from self._compose_gate(spec)
        yield Static("", id="hint", markup=False)

    def _compose_gate(self, spec: plan.GateSpec) -> ComposeResult:
        with Vertical(classes="gate", id=f"gate-{spec.id}"):
            # A finished gate collapses to this single line so the list shortens as you work
            # through nineteen of them; focusing it expands it again. `F37` #6: all nineteen were
            # always mounted, which is what the Phase 2 tests checked and why they passed - but
            # each was so tall that only one was ever on screen.
            yield Static("", classes="gate-summary", id=f"summary-{spec.id}", markup=False)
            with Vertical(classes="gate-body", id=f"body-{spec.id}"):
                yield Static(spec.id, classes="gate-name")
                yield Static(_first_sentence(spec.explanation), classes="gate-desc")
                if spec.mandatory:
                    yield Static(
                        "  required — the level requires this gate; its precondition is yours to state",
                        classes="gate-locked",
                    )
                elif spec.auto_status:
                    yield Static(
                        f"  {spec.auto_status.replace('_', ' ')} — settled by an earlier answer",
                        classes="gate-locked",
                    )
                yield from self._compose_gate_fields(spec)

    def _compose_gate_fields(self, spec: plan.GateSpec) -> ComposeResult:
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
                with HorizontalGroup(classes="followups", id=f"row-{key.replace('.', '--')}"):
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

    def _gate_is_complete(self, spec: plan.GateSpec, answers: dict) -> bool:
        """A gate is finished when it has a status AND every field that status calls for validates.

        Deliberately stricter than "has a status": a level-mandatory gate is `required` from the
        moment it appears, and collapsing it on that basis alone would hide the precondition fields
        it still needs - work the human cannot then see to do.
        """
        if self._status_of(spec, answers) is None:
            return False
        for field_spec in spec.fields:
            key = f"{spec.id}.{field_spec.id}"
            if field_spec.depends_on is not None:
                other, wanted = field_spec.depends_on
                if answers.get(f"{spec.id}.{other}") not in wanted:
                    continue
            if validators.check(field_spec.validate, answers.get(key, "")):
                return False
        return True

    def _focused_gate_id(self) -> str | None:
        node = self.focused
        while node is not None:
            node_id = getattr(node, "id", None) or ""
            if node_id.startswith("gate-"):
                return node_id[len("gate-"):]
            node = node.parent
        return None

    def _refresh_visibility(self) -> None:
        answers = self._answers()
        focused_gate = self._focused_gate_id()
        for spec in self.specs:
            for field_spec in spec.fields:
                key = f"{spec.id}.{field_spec.id}"
                row = self.query_one(f"#row-{key.replace('.', '--')}")
                if field_spec.depends_on is None:
                    row.display = True
                    continue
                other, wanted = field_spec.depends_on
                row.display = answers.get(f"{spec.id}.{other}") in wanted

            collapsed = self._gate_is_complete(spec, answers) and spec.id != focused_gate
            status = self._status_of(spec, answers)
            self.query_one(f"#body-{spec.id}").display = not collapsed
            summary = self.query_one(f"#summary-{spec.id}", Static)
            summary.display = collapsed
            if collapsed:
                summary.update(f"  {spec.id}  ·  {str(status).replace('_', ' ')}")
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

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self._refresh_visibility()

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self._refresh_visibility()

    def _answered_count(self, answers: dict | None = None) -> int:
        answers = self._answers() if answers is None else answers
        return sum(1 for spec in self.specs if self._status_of(spec, answers))

    def _set_hint(self, error: str = "") -> None:
        total = len(self.specs)
        done = self._answered_count()
        keys = (
            f"{done} of {total} answered · [Tab] move  [Ctrl+G] jump to section  "
            "[Ctrl+S] continue  [Ctrl+Q] cancel"
        )
        self.query_one("#hint", Static).update(hint_line(keys=keys, error=error))

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
            "[Ctrl+S] write it  [Ctrl+Q] cancel, keeping your draft", id="hint", markup=False
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
        yield Static(
            "[y] resume it  [n] start fresh (the draft is discarded)", id="hint", markup=False
        )

    def action_resume(self) -> None:
        self.dismiss(True)

    def action_fresh(self) -> None:
        self.dismiss(False)
