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

import dataclasses
import textwrap
from typing import Callable

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, HorizontalGroup, Vertical, VerticalScroll
from textual.screen import Screen
from textual.suggester import SuggestFromList
from textual.widgets import (
    Button,
    Checkbox,
    Input,
    Label,
    OptionList,
    RadioButton,
    RadioSet,
    Select,
    SelectionList,
    Static,
    TextArea,
)
from textual.widgets.selection_list import Selection
from textual.widgets.option_list import Option, OptionDoesNotExist
from textual.strip import Strip
from rich.segment import Segment

from surfaceplate.adopt import discover
from surfaceplate.adopt import flow as _flow
from surfaceplate.adopt import plan, scaffold, validators

CANCELLED = "__cancelled__"


class Frame(VerticalScroll):
    """The outer frame: scrolls, but never takes focus.

    Both halves matter and they pull against each other. `Vertical` does not scroll, so content
    taller than the window was clipped - which is what *"the terminal is cut if you minimise the
    window"* actually was. But `VerticalScroll` is focusable by default, and a focused scroll
    container swallows the arrow keys, so simply swapping one for the other stopped `\u2191`/`\u2193`
    ever reaching a field. Found by driving it, not by reading about it.
    """

    can_focus = False

    def on_mount(self) -> None:
        """Open at the top, whatever the initially focused widget wants.

        Textual scrolls the focused widget into view on mount. Where that widget sits below a long
        intro - the conformance-level screen with its recommendation, the scaffold offer with its
        previews - the frame opened already scrolled, so the screen's own title and the first words
        of its explanation were off the top and the adopter began mid-sentence. Deferred, because
        that scrolling happens after this returns.

        Fixed here rather than on each screen because it had already appeared twice; a third
        instance would have been three copies of the same three lines.
        """
        self.call_after_refresh(lambda: self.scroll_home(animate=False))


# The muted ink of the stylesheet, for the brackets of a control (`F67`).
SIDE_INK = "#7a827e"


class _StatefulToggle:
    """Mixin: draw a DIFFERENT character for on and off.

    `ToggleButton` renders `BUTTON_INNER` whatever the state and distinguishes on from off purely
    by style, at low contrast - which is what *"some boxes (x) are not clearly visible so you don't
    know you have to click (X) there"* was about.

    Setting `BUTTON_INNER` to a tick was the obvious fix and was WRONG in a worse way: the class
    variable is drawn in both states, so an UNCHECKED box rendered a tick and looked answered.
    That shipped past a whole-screen comparison and was only caught once the assertion was narrowed
    to the checkbox's own row - `DR-37`'s point about calibrating a property test, demonstrated
    against this packet's own code.
    """

    # ASCII brackets, not the default half-block frame. `▐✔▌` put a tick between two half-block
    # characters: the maintainer reported *"the tick mark doesn't fit in the box and it's really
    # not properly visible"*, and the same for an unselected radio. `[X]` and `[ ]` render
    # identically in every terminal and font, which is the point - this is a control surface, not
    # a place to be clever with glyphs.
    LEFT = "["
    RIGHT = "]"
    ON = "X"
    OFF = " "

    def watch_value(self) -> None:  # type: ignore[override]
        # `ToggleButton.watch_value` takes no argument in Textual 8; Textual inspects the
        # signature and calls it accordingly, so this must match rather than forward a value.
        self._apply_glyphs()
        super().watch_value()  # type: ignore[misc]
        self.refresh()

    def on_mount(self) -> None:
        self._apply_glyphs()
        self.refresh()

    def _apply_glyphs(self) -> None:
        self.BUTTON_LEFT = self.LEFT
        self.BUTTON_RIGHT = self.RIGHT
        self.BUTTON_INNER = self.ON if self.value else self.OFF

    @property
    def _button(self):  # type: ignore[override]
        """`F67`: Textual's `_button` paints the two side characters in the button's *background*
        colour, to fake half-block edges; with real brackets that made an unpressed control dark
        brackets on a black ground. The brackets are painted in the muted ink instead, and the
        inner glyph keeps the component style, so on and off differ in shape and both are visible."""
        from textual.color import Color as _Color
        from textual.content import Content
        from textual.style import Style as _Style

        button_style = self.get_visual_style("toggle--button")
        side_style = _Style(foreground=_Color.parse(SIDE_INK), background=self.background_colors[1])
        return Content.assemble(
            (self.LEFT, side_style),
            (self.ON if self.value else self.OFF, button_style),
            (self.RIGHT, side_style),
        )


class VisibleCheckbox(_StatefulToggle, Checkbox):
    pass


class VisibleRadioButton(_StatefulToggle, RadioButton):
    LEFT = "("
    RIGHT = ")"
    ON = "\u25cf"   # ●
    OFF = " "


class VisibleSelectionList(SelectionList):
    """`F41`. The same fix as `_StatefulToggle`, which structurally could not reach this widget.

    `SelectionList.render_line` composes its tick box from `ToggleButton.BUTTON_LEFT`,
    `BUTTON_INNER` and `BUTTON_RIGHT` read off the **`ToggleButton` class**, and distinguishes
    selected from unselected by style alone. `_StatefulToggle` sets those names on the *instance* of
    a `Checkbox` or `RadioButton`, so it fixed both of those and left every `SelectionList` in the
    wizard rendering `[X]` on every row whatever was actually ticked - which is the `F38` defect
    (*"some boxes (x) are not clearly visible"*) surviving in the one widget nobody re-checked.

    Textual offers no hook for this, so `render_line` is overridden: take the strip the base class
    built and rewrite its three button segments from the row's real state, keeping their styles so
    colour still agrees with the glyph rather than replacing it. `_selected` is private; that is
    stated rather than hidden, and `tests/test_render.py` asserts the two states differ in TEXT, so
    the day Textual changes this the test fails rather than the wizard quietly lying again.
    """

    LEFT = "["
    RIGHT = "]"
    ON = "X"
    OFF = " "

    def render_line(self, y: int) -> Strip:
        strip = super().render_line(y)
        segments = list(strip)
        if len(segments) < 3:
            return strip
        _, scroll_y = self.scroll_offset
        try:
            selection = self.get_option_at_index(scroll_y + y)
        except OptionDoesNotExist:
            # The base class returns the bare prompt for these rows and draws no button, so there
            # is nothing here to correct.
            return strip
        from rich.style import Style

        ticked = selection.value in self._selected
        # `F67`: the side characters in the muted ink, not the button's background colour.
        side = Style(color=SIDE_INK)
        if segments[0].style is not None and segments[0].style.bgcolor is not None:
            side = Style(color=SIDE_INK, bgcolor=segments[0].style.bgcolor)
        segments[0] = Segment(self.LEFT, style=side)
        segments[1] = Segment(self.ON if ticked else self.OFF, style=segments[1].style)
        segments[2] = Segment(self.RIGHT, style=side)
        return Strip(segments)


class OneClickSelect(Select):
    """A dropdown that opens on the first click, not the second.

    Textual focuses a `Select` on the first click and opens it on the next, so the maintainer
    reported *"for dropdown list you need to click twice for it to show"*. Opening on focus would
    be worse - arrowing through a form would fling menus open - so this opens on the click itself
    and leaves keyboard behaviour exactly as Textual defines it.
    """

    def on_click(self, event) -> None:  # noqa: ANN001 - Textual event type
        if not self.expanded:
            self.expanded = True


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

    def on_key(self, event: events.Key) -> None:
        """Up and down move to the next field rather than doing nothing.

        Handled here rather than by a screen-level binding with `priority=True`, which would have
        been simpler and wrong: a priority binding fires before the focused widget, so it would
        also steal the arrows from the option list, the radio set and the text area, where they
        legitimately move a cursor or a highlight. A single-line text box is the one widget with
        no use for them.
        """
        if event.key == "down":
            event.stop()
            event.prevent_default()
            self.screen.focus_next()
        elif event.key == "up":
            event.stop()
            event.prevent_default()
            self.screen.focus_previous()


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
        return VisibleCheckbox(spec.label, value=initial, id=widget_id)
    if spec.kind == "choice":
        buttons = [
            VisibleRadioButton(
                label,
                value=(value == choice_value),
                id=f"r-{spec.id.replace('.', '--')}--{choice_value}",
            )
            for choice_value, label in spec.choices
        ]
        return RadioSet(*buttons, id=widget_id)
    if spec.kind == "select":
        # Discovered candidates, and nothing pre-selected: `Select.BLANK` keeps the same rule the
        # level screen states out loud - a value nobody picked is not an answer.
        widget = OneClickSelect(
            [(label, choice_value) for choice_value, label in spec.choices],
            prompt=f"Choose {spec.label.lower()} ({len(spec.choices)} found)",
            allow_blank=True,
            id=widget_id,
        )
        if isinstance(value, str) and any(value == v for v, _ in spec.choices):
            widget.value = value
        return widget
    if spec.kind == "multiselect":
        chosen = {v.strip() for v in str(spec.default).split(",") if v.strip()}
        return VisibleSelectionList(
            *[
                Selection(label, choice_value, choice_value in chosen)
                for choice_value, label in spec.choices
            ],
            id=widget_id,
        )
    if spec.kind == "textarea":
        return TextArea(str(value if value is not None else spec.default), id=widget_id)
    # No `placeholder=spec.label`. It duplicated the label the row already renders, so every field
    # printed its own name twice - `F37` #3, visible as "Precondition artefact (a real path)"
    # stacked directly above an input containing the same words.
    # Where candidates exist but must not constrain (a pathspec is a pattern, not a path), they
    # are offered as inline ghost text: type to filter, `\u2192` to accept, or ignore them entirely.
    return EditableInput(
        value=str(value if value is not None else spec.default),
        id=widget_id,
        suggester=SuggestFromList(spec.suggestions) if spec.suggestions else None,
    )


def help_text_for(spec: plan.FieldSpec, value: object, repo, highlighted: str | None = None) -> str:
    """The text beside a focused field (`DR-51` (3), (4)): what is asked, what the answer
    decides, what a wrong answer costs, and - for a value picked from the repository - what the
    chosen thing is, as discovery saw it and the checker's rules judge it."""
    parts: list[str] = []
    if spec.help:
        parts.append(spec.help)
    if spec.decides:
        parts.append(f"Decides: {spec.decides}.")
    if spec.wrong:
        parts.append(f"If wrong: {spec.wrong}.")
    if highlighted is not None and spec.choice_help:
        # `F67`: the full explanation of the highlighted row of a list whose labels had to fit.
        full = dict(spec.choice_help).get(highlighted)
        if full:
            parts.append(f"{highlighted}: {full}")
    if spec.context and repo is not None and isinstance(value, str) and value.strip():
        kind, _, detail = spec.context.partition(":")
        if kind == "gate":
            parts.append("Chosen: " + discover.describe(repo, value.strip(), gate_id=detail))
        elif kind == "scanner":
            parts.append("Chosen: " + discover.describe(repo, value.strip(), scanner=detail))
        elif kind in ("lock", "register", "artefact"):
            parts.append("Chosen: " + discover.describe(repo, value.strip()))
    return "\n".join(parts)


def reveal(field, slot) -> None:
    """Keep the focused field on screen with its help beneath it (`DR-51` (3)).

    Focus scrolls the field into view and nothing else; the help under it fell below the fold at
    80x24. Scrolling the help into view instead pushed the field's first rows off the top, which
    `F59`'s regression test refuses, and deciding between the two from widget regions proved
    unreliable at the moment the slot has just been shown. So the field goes to the top of its
    scroll container, and the help takes the rows beneath: the thing being answered and what it
    means, always together, whatever else has to scroll.
    """
    container = field.parent
    while container is not None and not isinstance(container, VerticalScroll):
        container = container.parent
    if container is None:
        return
    container.scroll_to_widget(field, top=True, animate=False)


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


GATE_SUMMARY_CHARS = 150


def _first_sentence(text: str, limit: int = GATE_SUMMARY_CHARS) -> str:
    """The opening sentence of an explanation, for a short gate summary.

    The full text is not lost - it is shown in the hint line while that gate has focus, the same
    way a form field's help is. Rendering all five lines of it inside every gate block is what made
    the catalogue unreadable (`F37` #6).

    **`F42`: the cut happens HERE, in the text, and never in CSS.** `.gate-desc` carried
    `height: 1` with `text-overflow: ellipsis`, and the ellipsis never rendered - so a 184- to
    248-character sentence simply stopped, mid-word at some widths, with nothing telling the reader
    there had been more. A budget applied to the string cannot fail that way: whenever anything is
    dropped the `…` is part of the value, so it survives whatever the layout does to it.
    """
    head = text.split(". ")[0].strip()
    if not head.endswith("."):
        head += "."
    if len(head) <= limit:
        return head
    return head[: limit - 1].rsplit(" ", 1)[0] + " …"


def _widget_kind(widget) -> str:
    """The `FieldSpec.kind` a rendered widget corresponds to - the other half of the join."""
    if isinstance(widget, SelectionList):
        return "multiselect"
    if isinstance(widget, Select):
        return "select"
    if isinstance(widget, (RadioSet, OptionList)):
        return "choice"
    if isinstance(widget, Checkbox):
        return "bool"
    if isinstance(widget, TextArea):
        return "textarea"
    if isinstance(widget, Horizontal):  # the gate chip row
        return "choice"
    return "text"


def _read_widget(widget) -> object:
    if isinstance(widget, SelectionList):
        return list(widget.selected)
    if isinstance(widget, Select):
        # `is_blank()`, not a comparison against a constant: `Select` exposes BOTH `BLANK` and
        # `NULL` and they are different objects, so `value is Select.BLANK` is silently always
        # false and would hand the sentinel back as though a human had chosen it. Caught by a test
        # asserting nothing is pre-selected, which is exactly the sort of thing that assertion is
        # for.
        return None if widget.is_blank() else widget.value
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
        # `F38`: "not obvious how tab and control+S work. Using the arrows would be easier."
        # A focused `Input` lets these through (its inherited scroll action raises `SkipAction`
        # when there is nothing to scroll), so they reach the screen. `TextArea` legitimately
        # consumes them for cursor movement - Tab is the way out of one.
        Binding("down", "focus_next", "next field", show=False),
        Binding("up", "focus_previous", "previous field", show=False),
    ]

    def __init__(
        self,
        section: plan.SectionPlan,
        *,
        step: str = "",
        initial: dict | None = None,
        repo=None,
    ) -> None:
        super().__init__()
        self.section = section
        self.step = step
        # `DR-48`: the validators that ask git whether a path is tracked need the repository.
        # A screen hosted without one (a test) skips those two checks, and says so in the
        # parity table beside the codes that read them.
        self.repo = repo
        # Proposed values, when the adopter chose to start from defaults. A pre-filled field is
        # still answered by them: it is shown, and it is submitted, exactly as a shown default in
        # a text box always has been.
        self.initial = initial or {}

    def field_ids(self) -> list[str]:
        """Every field id this screen actually renders."""
        return [key for key, _kind in self.field_shape()]

    def field_shape(self) -> list[tuple[str, str]]:
        """Every rendered field as `(id, kind)`.

        The id alone was not enough, and a real adoption paid for it. `tui/app.py` built the gate
        catalogue from a plan that had never been given the repository scan, so every precondition
        artefact rendered as a plain text box instead of a dropdown of real files - and the join
        test passed, because the ids are identical either way. Only the KIND differed. The
        maintainer typed `asdf` into seven gates because there was nothing to pick from.

        That is `F37`'s shape one level up: the right questions, asked in the wrong form. Comparing
        kind is what makes this join able to see it.
        """
        shape: list[tuple[str, str]] = []
        for widget in self.query(".field-widget"):
            if widget.id and widget.id.startswith("f-"):
                shape.append((widget.id[2:].replace("--", "."), _widget_kind(widget)))
        return shape

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
        with Frame(id="frame"):
            yield Static(f"[{self.step}{self.section.title}]", classes="section-header", markup=False)
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
                        widget = _widget_for(spec, self.initial.get(spec.id))
                        widget.add_class("field-widget")
                        yield widget
                    # Beside the field, shown only while that field has focus. `F37` moved this to
                    # the docked hint line to stop every field's help rendering at once; that
                    # fixed the clutter and buried the text - *"the explanations are at the very
                    # bottom, took me a while to realise they were there"*. Reversed on evidence:
                    # one help line, next to the thing it explains.
                    yield Static("", classes="field-help", id=f"help-{spec.id.replace('.', '--')}")
        yield Static("", id="hint", markup=False)

    def on_mount(self) -> None:
        # `F74`: an error reported by `action_commit` is held here until the next commit, because
        # the focus move that reports it arrives as a later `DescendantFocus` event whose handler
        # rewrites the hint - and rewrote it without the error, so the error was on screen for
        # one frame. Held on the screen, it survives every focus move until the human tries again.
        self._pending_error = ""
        self._refresh_visibility()
        self._focus_first_field()
        self._show_help_for_focused()
        self._set_hint()

    def _focus_first_field(self) -> None:
        """Start in the first field rather than nowhere.

        With the frame no longer focusable, nothing claimed focus on mount, so the arrow keys had
        nothing to move from and the first keystroke went nowhere. Focusing the first field also
        means its help is on screen immediately, which is the point of moving help back beside it.
        """
        for spec in self.section.fields:
            try:
                widget = self.query_one(f"#f-{spec.id.replace('.', '--')}")
            except Exception:
                continue
            if widget.display:
                widget.focus()
                return

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self._show_help_for_focused()
        self._set_hint(getattr(self, "_pending_error", ""))

    def _highlighted_choice(self, spec: plan.FieldSpec) -> str | None:
        """The value of the highlighted row of a `multiselect`, for `choice_help`."""
        if not spec.choice_help:
            return None
        try:
            widget = self.query_one(f"#f-{spec.id.replace('.', '--')}", SelectionList)
        except Exception:
            return None
        index = widget.highlighted
        if index is None:
            return None
        try:
            return str(widget.get_option_at_index(index).value)
        except OptionDoesNotExist:
            return None

    def _show_help_for_focused(self) -> None:
        focused = self._focused_spec()
        answers = self._answers() if focused is not None and focused.context else {}
        for spec in self.section.fields:
            try:
                slot = self.query_one(f"#help-{spec.id.replace('.', '--')}", Static)
            except Exception:
                continue
            active = focused is not None and spec.id == focused.id
            text = help_text_for(spec, answers.get(spec.id), self.repo, self._highlighted_choice(spec)) if active else ""
            slot.display = bool(text)
            slot.update(text)
            if text:
                self.call_after_refresh(lambda f=self.focused, s=slot: reveal(f, s))

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

    @on(Select.Changed)
    def _on_select_changed(self, event: Select.Changed) -> None:
        """A chosen file is described the moment it is chosen (`F80`)."""
        self._refresh_visibility()
        self._show_help_for_focused()

    @on(SelectionList.SelectionHighlighted)
    def _on_selection_highlighted(self, event: SelectionList.SelectionHighlighted) -> None:
        """The highlighted row of a list explains itself beside the list (`F67`)."""
        self._show_help_for_focused()

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
                # Arrows first, because they are what people reach for: `F38` began with "it's not
                # obvious how tab and control+S work. Using the arrows would be easier."
                keys="[↑↓] move between fields  [Ctrl+S] continue  [Ctrl+Q] cancel",
                error=error,
            )
        )

    def action_commit(self) -> None:
        self._pending_error = ""
        answers = self._answers()
        for spec in self.section.fields:
            if not spec.applies(answers):
                answers.pop(spec.id, None)
                continue
            problem = validators.check(spec.validate, answers.get(spec.id, ""), repo=self.repo)
            # `F64`: a choice field carries no text validator, and an unpressed radio set reads
            # as `None`, so `mode: None` committed and the run died three screens later. A
            # choice is an answer only when it is one of the choices.
            if not problem and spec.kind == "choice":
                if answers.get(spec.id) not in {value for value, _ in spec.choices}:
                    problem = "Choose one of the options."
            if problem:
                # Focus first, then report - and keep the report, because the focus event that
                # follows redraws the hint (`F74`).
                try:
                    self.query_one(f"#f-{spec.id.replace('.', '--')}").focus()
                except Exception:
                    pass
                self._pending_error = f"{spec.label}: {problem}"
                self._set_hint(self._pending_error)
                return
        self.dismiss(answers)


class LevelScreen(_SectionScreenBase):
    """The mockup's frame 02. Highlighting is not choosing, and the screen says so."""

    BINDINGS = [
        Binding("ctrl+q", "cancel", "quit", show=True),
        Binding("question_mark", "why", "why does this matter", show=True),
    ]

    def __init__(
        self,
        section: plan.SectionPlan,
        *,
        step: str = "",
        recommended: str | None = None,
        repo=None,
    ) -> None:
        super().__init__(section, step=step, repo=repo)
        self.spec = section.fields[0]
        self._why_shown = False
        # `ACT-032`: start the CARET on the recommended level. The screen's note says which level
        # the adopter's own answers point at, and leaving the cursor on the first row made the
        # screen point somewhere else while saying so. This moves where the cursor sits, not what
        # is chosen: `nothing is chosen yet` still shows, `Enter` is still required, and
        # `tests/test_adopt_tui.py` holds that distinction.
        self._start = next(
            (i for i, (value, _) in enumerate(self.spec.choices) if value == recommended), 0
        )

    def compose(self) -> ComposeResult:
        with Frame(id="frame"):
            yield Static(f"[{self.step}{self.section.title}]", classes="section-header", markup=False)
            # `F67`: one row for the recap and no rule row, so the three options fit 24 rows.
            if self.section.recap:
                yield Static("You told us: " + " ".join(self.section.recap), classes="recap", markup=False)
            for note in self.section.notes:
                yield Static(f"  {note}", classes="note", markup=False)
            widget = OptionList(*self._options(self._start), id=f"f-{self.spec.id}")
            widget.add_class("field-widget")
            widget.highlighted = self._start
            yield widget
            yield Static("", classes="level-meta", id="level-meta", markup=False)
            yield Static("", classes="intro", id="why")
        yield Static("", id="hint", markup=False)

    def on_mount(self) -> None:
        self.query_one("#why", Static).display = False
        # `F45`: set the highlight HERE, once the widget is mounted, rather than relying on the
        # assignment in `compose`. Set there it does not fire `OptionHighlighted`, so `_update_meta`
        # ran against the default index and the meta line described `essential` while the caret sat
        # on `full`. It self-corrected on the first arrow press, which is exactly why only a
        # first-paint assertion catches it.
        self.query_one(OptionList).highlighted = self._start
        # The index is passed rather than read back: during `on_mount` the widget has not settled
        # on it yet, so reading it here returned 0 whatever had been assigned. Passing the value
        # makes the first paint deterministic instead of dependent on Textual's mount ordering.
        self._update_meta(self._start)
        self._set_hint()
        # The frame opens at its own top - see `Frame.on_mount`, which handles this for every
        # screen now that it had appeared here and on the scaffold offer.

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

    def _update_meta(self, index: int | None = None) -> None:
        if index is None:
            index = self.query_one(OptionList).highlighted
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
        chooses nothing - the caret marks where you are, and the hint line says so.

        **`F46`: the prompts are replaced IN PLACE, never cleared and re-added.**
        `clear_options()` resets the highlight to 0 and posts an `OptionHighlighted`, which arrives
        back here and rebuilds again. With the caret starting at 0 that settled immediately, because
        the reset landed on the value it already had. `ACT-032` started the caret on the recommended
        level, and from any non-zero index the two events alternated 2, 0, 2, 0 forever - an
        unbounded loop on a screen every adopter sees.

        The `_caret_at` guard could not stop it: the events alternate, so the incoming value never
        matches the last one. Guarding harder was the wrong instinct; not generating the events is
        the fix. `replace_option_prompt_at_index` mutates the prompt and leaves the highlight alone.
        """
        option_list = self.query_one(OptionList)
        if getattr(self, "_caret_at", None) == highlighted:
            return
        self._caret_at = highlighted
        for index, option in enumerate(self._options(highlighted)):
            option_list.replace_option_prompt_at_index(index, option.prompt)

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
        # `DR-47` (4): the one explicit bulk command. A human making every remaining scope
        # decision in one act, recorded as such with its count - never the tool pre-marking.
        Binding("ctrl+n", "bulk_not_applicable", "declare every undecided gate not applicable", show=True),
        Binding("down", "focus_next", "next field", show=False),
        Binding("up", "focus_previous", "previous field", show=False),
    ]

    # Single keys per row (report R3). Handled in `on_key` rather than as bindings, because a
    # focused text field consumes printable characters and a bare-letter binding would be typed
    # into a rationale instead of choosing a status.
    _STATUS_KEYS = {"r": "required", "d": "deferred", "n": "not_applicable"}

    def __init__(
        self,
        specs: tuple[plan.GateSpec, ...],
        section: plan.SectionPlan,
        *,
        step: str = "",
        initial: dict | None = None,
        repo=None,
    ) -> None:
        # `F60`: this screen took no `initial`, so the defaults route proposed thirty-odd gate
        # values, showed them, and then opened every gate blank. `initial` is keyed
        # `"<gate id>.<field id>"`, the same addresses `_answers` returns.
        super().__init__(section, step=step, initial=initial, repo=repo)
        self.specs = specs
        self._chosen: dict[str, str] = {}
        self.bulk_gates: set[str] = set()  # gates whose status the bulk command set

    def compose(self) -> ComposeResult:
        with Frame(id="frame"):
            yield Static(f"[{self.step}{self.section.title}]", classes="section-header", markup=False)
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
                    suggestions=field_spec.suggestions,
                    decides=field_spec.decides,
                    wrong=field_spec.wrong,
                    context=field_spec.context,
                )
                seed = self.initial.get(key)
                with HorizontalGroup(classes="followups", id=f"row-{key.replace('.', '--')}"):
                    if field_spec.kind == "choice":
                        # A radio set, not a row of buttons. The mockup drew chips and this
                        # rendered them faithfully - but it made the gate catalogue a THIRD
                        # interaction model alongside tick boxes and dropdowns, and the maintainer
                        # asked the obvious question: *"why radio buttons sometimes and other times
                        # ticks and other times double click on the word."* Fidelity to a drawing
                        # is worth less than one rule an adopter can learn once: `[X]` for yes/no,
                        # `(\u25cf)` for pick-one, a dropdown for pick-one-from-many.
                        row = RadioSet(
                            *(
                                VisibleRadioButton(
                                    label.split(" - ")[0],
                                    value=(seed == value),
                                    id=f"chip-{spec.id}--{value}",
                                )
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
                        widget = _widget_for(prefixed, seed)
                        widget.add_class("field-widget")
                        yield widget
                # `DR-51` (3), (4): beside the focused field, what it decides and what was chosen.
                yield Static("", classes="field-help", id=f"help-{key.replace('.', '--')}")

    def on_mount(self) -> None:
        self._refresh_visibility()
        self._set_hint()

    def _focused_key(self) -> str | None:
        """`"<gate>.<field>"` for whichever field widget has focus, if any."""
        node = self.focused
        while node is not None:
            node_id = getattr(node, "id", None) or ""
            if node_id.startswith("f-"):
                return node_id[2:].replace("--", ".")
            node = node.parent
        return None

    def _show_help_for_focused(self) -> None:
        focused = self._focused_key()
        answers = self._answers() if focused else {}
        for spec in self.specs:
            for field_spec in spec.fields:
                key = f"{spec.id}.{field_spec.id}"
                try:
                    slot = self.query_one(f"#help-{key.replace('.', '--')}", Static)
                except Exception:
                    continue
                if key != focused:
                    slot.display = False
                    slot.update("")
                    continue
                prefixed = dataclasses.replace(field_spec, id=key)
                text = help_text_for(prefixed, answers.get(key), self.repo)
                slot.display = bool(text)
                slot.update(text)
                if text:
                    self.call_after_refresh(lambda f=self.focused, s=slot: reveal(f, s))

    def _answers(self) -> dict:
        answers: dict = {}
        for spec in self.specs:
            for field_spec in spec.fields:
                key = f"{spec.id}.{field_spec.id}"
                if field_spec.kind == "choice":
                    # Nothing pre-selected, so a gate nobody decided has no status - the same rule
                    # the level screen states out loud.
                    try:
                        widget = self.query_one(f"#f-{key.replace('.', '--')}", RadioSet)
                    except Exception:
                        answers[key] = None
                        continue
                    pressed = widget.pressed_button
                    answers[key] = (
                        pressed.id.split("--")[-1] if pressed is not None and pressed.id else None
                    )
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

    def _may_be_scaffolded(self, spec: plan.GateSpec, field_spec: plan.FieldSpec, value: object) -> bool:
        """A blank artefact on a gate this wizard can create one for is not a refusal: the
        scaffold offer follows this screen, and the review refuses to write if it is declined.
        `ACT-033` offered the artefact; the screen it followed never let the field be blank."""
        if field_spec.id != "artefact" or (value is not None and str(value).strip()):
            return False
        if spec.id not in scaffold.SEEDABLE or self.repo is None:
            return False
        return not (self.repo / scaffold.SEEDABLE[spec.id][0]).exists()

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
            if self._may_be_scaffolded(spec, field_spec, answers.get(key)):
                continue
            if validators.check(field_spec.validate, answers.get(key, ""), repo=self.repo):
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

    @on(RadioSet.Changed)
    def _on_status_chosen(self, event: RadioSet.Changed) -> None:
        """Choosing a status reveals whatever that status calls for, inside the gate's own block."""
        self._refresh_visibility()

    @on(Input.Changed)
    @on(Checkbox.Changed)
    def _on_change(self, event: events.Event) -> None:
        self._set_hint()

    @on(Select.Changed)
    def _on_select_changed(self, event: Select.Changed) -> None:
        """A chosen artefact is described the moment it is chosen (`F80`)."""
        self._refresh_visibility()
        self._show_help_for_focused()

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self._refresh_visibility()
        self._show_help_for_focused()

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self._refresh_visibility()

    def _answered_count(self, answers: dict | None = None) -> int:
        """`F43`: complete, not merely status-bearing.

        This counted `self._status_of(...)`, and a level-mandatory gate's status is `required` from
        the moment it appears - fixed by the level, not supplied by anyone - so at `essential` the
        hint read `1 of 1 answered` with the precondition dropdown empty and `Gated paths` blank.
        `_gate_is_complete` is the predicate that was already right, and already used to decide
        whether a gate may collapse; the counter was the one place asking the weaker question.
        """
        answers = self._answers() if answers is None else answers
        return sum(1 for spec in self.specs if self._gate_is_complete(spec, answers))

    def _set_hint(self, error: str = "") -> None:
        """`F43` and R3: the counter says what matters - how many gates will be audited, how
        many are still undecided, and how many are complete (a status and every field it needs)."""
        total = len(self.specs)
        answers = self._answers()
        statuses = [self._status_of(spec, answers) for spec in self.specs]
        audited = sum(1 for s in statuses if s == "required")
        undecided = sum(1 for s in statuses if s is None)
        done = self._answered_count(answers)
        keys = (
            f"{audited} will be audited · {undecided} undecided · {done} of {total} complete\n"
            "[r/d/n] status  [Ctrl+N] all undecided → not applicable  [Ctrl+G] jump to section\n"
            "[\u2191\u2193] move  [Ctrl+S] continue  [Ctrl+Q] cancel"
        )
        self.query_one("#hint", Static).update(hint_line(keys=keys, error=error))

    def _press_status(self, gate_id: str, value: str) -> bool:
        try:
            button = self.query_one(f"#chip-{gate_id}--{value}", RadioButton)
        except Exception:
            return False
        button.value = True
        return True

    def on_key(self, event: events.Key) -> None:
        """`r`, `d`, `n` on the focused gate, unless a text field or an open dropdown has the key."""
        value = self._STATUS_KEYS.get(event.key)
        if value is None:
            return
        focused = self.focused
        if isinstance(focused, (Input, TextArea)):
            return
        if isinstance(focused, Select) and focused.expanded:
            return
        gate_id = self._focused_gate_id()
        if gate_id and self._press_status(gate_id, value):
            event.stop()
            event.prevent_default()
            self.bulk_gates.discard(gate_id)

    def action_bulk_not_applicable(self) -> None:
        """Every gate still undecided becomes `not_applicable`, as one recorded human act."""
        answers = self._answers()
        pressed = 0
        for spec in self.specs:
            if self._status_of(spec, answers) is None and self._press_status(spec.id, "not_applicable"):
                self.bulk_gates.add(spec.id)
                pressed += 1
        self._refresh_visibility()
        self._set_hint(
            f"{pressed} gate(s) declared not applicable in one act; it is recorded as yours."
            if pressed
            else "Nothing is undecided."
        )

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
                if self._may_be_scaffolded(spec, field_spec, answers.get(key)):
                    answers.pop(key, None)  # left blank: the offer to create it follows
                    continue
                problem = validators.check(
                    field_spec.validate, answers.get(key, ""), repo=self.repo
                )
                if problem:
                    self._set_hint(f"{spec.id} · {field_spec.label}: {problem}")
                    return
        # Statuses that were settled rather than chosen are recorded explicitly, so the answers
        # this screen returns describe the whole section rather than only its free choices.
        for spec in self.specs:
            if spec.mandatory or spec.auto_status:
                answers.pop(f"{spec.id}.status", None)
        self.dismiss({k: v for k, v in answers.items() if v is not None})


class EditLineScreen(Screen):
    """Change one value on the review. The edit is recorded as typed, with a timestamp."""

    BINDINGS = [
        Binding("ctrl+s", "save", "use this value", show=True),
        Binding("ctrl+q", "cancel", "keep it as it was", show=True),
    ]

    def __init__(self, path: str, current: object, spec: plan.FieldSpec | None) -> None:
        super().__init__()
        self.path = path
        self.current = current
        self.spec = spec

    def compose(self) -> ComposeResult:
        with Frame(id="frame"):
            yield Static(f"[Change {self.path}]", classes="section-header", markup=False)
            if self.spec is not None:
                text = help_text_for(self.spec, None, None)
                if text:
                    yield Static(text, classes="field-help", markup=False)
            kind = self.spec.kind if self.spec is not None else "text"
            if kind == "bool":
                current = "yes" if self.current else "no"
                spec = plan.FieldSpec(id="value", label="", kind="choice", choices=(("yes", "yes"), ("no", "no")))
                widget = _widget_for(spec, current)
            elif kind in ("choice", "multiselect", "select"):
                # The same widget the form would show, addressed as `f-value` here.
                widget = _widget_for(dataclasses.replace(self.spec, id="value"), self.current)
            elif kind == "textarea":
                widget = TextArea(str(self.current or ""), id="f-value")
            else:
                widget = EditableInput(value=str(self.current or ""), id="f-value")
            widget.add_class("field-widget")
            yield widget
        yield Static(
            "[Ctrl+S] use this value  [Ctrl+Q] keep it as it was", id="hint", markup=False
        )

    def on_mount(self) -> None:
        self.query_one("#f-value").focus()

    def action_save(self) -> None:
        value = _read_widget(self.query_one("#f-value"))
        if self.spec is not None and self.spec.kind == "bool":
            value = value == "yes"
        self.dismiss(value)

    def action_cancel(self) -> None:
        self.dismiss(None)


TAG_WIDTH = 12


class ReviewScreen(Screen):
    """Every line of the profile with where its value came from, and Enter to change any of them.

    `DR-47` (1): a value is asked when it is presented with its origin and the human can change it
    before the profile is written; this screen is where most values are asked. `F65`: an error
    names the line, `Ctrl+E` goes to it, and "write it" is not offered while an error stands.
    Nothing is written before this screen, and nothing is written by it: it returns an edit or an
    approval, and `wizard.run` does the writing.
    """

    BINDINGS = [
        Binding("ctrl+q", "cancel", "quit", show=True),
        Binding("ctrl+s", "confirm", "write", show=True),
        Binding("ctrl+e", "go_to_error", "go to the line", show=True),
    ]

    def __init__(
        self,
        review: _flow.Review,
        creating: list | None = None,
        highlight: int | None = None,
    ) -> None:
        super().__init__()
        self.review = review
        self.creating = list(creating or [])
        self.highlight = highlight
        self._by_line = {entry.line: entry for entry in review.lines}

    def _composed(self, width: int = 0) -> list[str]:
        """One row per line of the profile, never wrapped: a wrapped continuation loses its
        origin gutter and reads as a line of its own. A line too long for `width` ends in an
        ellipsis, and Enter shows the whole value."""
        out = []
        for index, text in enumerate(self.review.rendered.splitlines()):
            entry = self._by_line.get(index)
            tag = (entry.origin if entry else "")[:TAG_WIDTH]
            line = f"{tag:<{TAG_WIDTH}}│ {text}"
            if width and len(line) > width:
                line = line[: width - 1] + "…"
            out.append(line)
        return out

    def _fit(self) -> None:
        """Rebuild the rows for the terminal's width, keeping the highlight where it was."""
        body = self.query_one("#review-body", OptionList)
        width = max(20, self.size.width - 6)
        if getattr(self, "_fitted_width", None) == width:
            return
        self._fitted_width = width
        highlighted = body.highlighted
        body.clear_options()
        body.add_options([Option(line, id=str(i)) for i, line in enumerate(self._composed(width))])
        body.highlighted = highlighted

    def on_resize(self, event: events.Resize) -> None:
        self._fit()

    def compose(self) -> ComposeResult:
        # A plain `Vertical`, not the scrolling `Frame`: the list below is the thing that scrolls,
        # and it takes every row the heading and notes leave, which a `1fr` inside a scroll
        # container does not (two rows of profile per page at 80x24, found by taking the image).
        with Vertical(id="review-frame"):
            yield Static("[Review — nothing has been written yet]", classes="section-header", markup=False)
            if self.review.error:
                where = "  Ctrl+E goes to the line." if self.review.error_line is not None else ""
                yield Static(self.review.error + where, id="review-error", markup=False)
            if self.creating:
                # One wrapped line, not one row per file: at 80x24 every row here is a row of
                # profile the review cannot show. The point-of-execution disclosure stands.
                yield Static(
                    f"Writing this will also CREATE {len(self.creating)} file(s): "
                    + ", ".join(offer.path for offer in self.creating),
                    classes="note",
                    id="review-creating",
                    markup=False,
                )
            counts = self.review.counts()
            yield Static(
                "where each value came from: "
                + " · ".join(f"{n} {kind}" for kind, n in sorted(counts.items(), key=lambda kv: -kv[1])),
                classes="recap",
                markup=False,
            )
            # One row per line of the profile, never wrapped: a wrapped continuation loses its
            # origin gutter and reads as a line of its own. A line too long for the terminal ends
            # in an ellipsis, and Enter shows the whole value.
            widget = OptionList(
                *[Option(line, id=str(i)) for i, line in enumerate(self._composed())],
                id="review-body",
            )
            yield widget
        yield Static("", id="hint", markup=False)

    def on_mount(self) -> None:
        self._fit()
        body = self.query_one("#review-body", OptionList)
        body.focus()
        if self.highlight is not None:
            body.highlighted = self.highlight
        elif self.review.error_line is not None:
            body.highlighted = self.review.error_line
        self._set_hint()

    def _set_hint(self, note: str = "") -> None:
        # `F79`: while an error stands the hint names the way forward - the key that reaches the
        # line and the key that writes once it is fixed - rather than only dropping "write it".
        if self.review.error:
            reach = "[Ctrl+E] go to the error  " if self.review.error_line is not None else ""
            keys = f"[↑↓] move  [Enter] change this line  {reach}fix it, then Ctrl+S writes  [Ctrl+Q] cancel, keeping your draft"
        else:
            keys = "[↑↓] move  [Enter] change this line  [Ctrl+S] write it  [Ctrl+Q] cancel, keeping your draft"
        self.query_one("#hint", Static).update(hint_line(keys=keys, help_text=note))

    @on(OptionList.OptionSelected)
    def _on_selected(self, event: OptionList.OptionSelected) -> None:
        entry = self._by_line.get(event.option_index)
        if entry is None:
            self._set_hint("That line carries no value to change.")
            return
        if not entry.editable:
            self._set_hint(f"{entry.path}: {entry.note}.")
            return
        self.dismiss({"edit": entry.path, "line": event.option_index})

    def action_go_to_error(self) -> None:
        if self.review.error_line is not None:
            self.query_one("#review-body", OptionList).highlighted = self.review.error_line

    def action_confirm(self) -> None:
        if self.review.error:
            self._set_hint("Fix the error first; Ctrl+E goes to the line.")
            return
        self.dismiss({"approve": True})

    def action_cancel(self) -> None:
        self.dismiss(None)


class WelcomeScreen(Screen):
    """The tool introduces itself before it asks anything (`F81`, `DR-51` (2)).

    What a stranger needs on one screen: what this is, which release is running against which
    installed release, where it will write, that nothing is written before the review, and the
    keys. The version comparison has already passed (`wizard.InstallMismatch`); the line here
    says so rather than leaving the two digests for the reader to compare.
    """

    BINDINGS = [
        Binding("enter", "begin", "begin", show=True),
        Binding("ctrl+q", "cancel", "quit", show=True),
    ]

    def __init__(self, welcome) -> None:
        super().__init__()
        self.welcome = welcome

    def compose(self) -> ComposeResult:
        w = self.welcome
        with Frame(id="frame"):
            yield Static(f"[{w.tool_name} {w.tool_version} · adopt]", classes="section-header", markup=False)
            yield Static(
                f"{w.tool_name} is {w.tagline}. adopt writes the one file that checker reads about "
                "this repository: its application profile.",
                classes="intro",
                markup=False,
            )
            same = w.tool_anchor == w.installed_anchor
            # Every row fits 76 columns, so nothing wraps at 80 and the whole screen fits 24 rows
            # with the draft note; `tests/test_render.py` holds both.
            rows = (
                ("tool", f"{w.tool_name} {w.tool_version} · {w.tool_anchor[:10]}…"),
                ("licence", f"{w.licence} · {w.publisher}"),
                ("installed", f"{w.installed_version} · {w.installed_anchor[:10]}… on {w.installed_at}"
                              + (" · the same release" if same else " · NOT the same release")),
                ("repository", w.repo),
                ("writes", f"{w.profile_path} + its provenance record"),
            )
            for label, value in rows:
                yield Static(f"  {label:<11}{value}", classes="recap", markup=False)
            yield Static("", classes="recap")
            yield Static(
                "Next: three screens ask what only you can answer, the conformance level, and the "
                "gates. Everything else is proposed from this repository and this framework's own "
                "examples, and every line is shown with where it came from on a review. Nothing is "
                "written before you approve that review.",
                classes="recap",
                markup=False,
            )
            if w.draft is not None:
                yield Static(
                    "  A saved draft was found; the next screen asks whether to resume it.",
                    classes="note",
                    markup=False,
                )
            elif w.draft_note:
                yield Static(f"  {w.draft_note}", classes="error", markup=False)
        yield Static("[Enter] begin  [Ctrl+Q] quit, nothing is written", id="hint", markup=False)

    def action_begin(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ResumeScreen(Screen):
    """Offered, never silent - `DR-35`'s rule, and a version mismatch is stated, not hidden."""

    BINDINGS = [
        Binding("y", "resume", "resume", show=True),
        Binding("n", "fresh", "start fresh", show=True),
        # `F73`: the apps no longer carry Textual's priority quit, so this screen answers the key
        # itself - and `None` still means "quit, draft kept" (`F68`).
        Binding("ctrl+q", "cancel", "quit, keeping the draft", show=True),
    ]

    def __init__(self, info) -> None:
        super().__init__()
        self.info = info

    def compose(self) -> ComposeResult:
        with Frame(id="frame"):
            yield Static("[A saved draft was found]", classes="section-header", markup=False)
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
            "[y] resume it  [n] start fresh (the draft is discarded)  [Ctrl+Q] quit, keeping it",
            id="hint", markup=False,
        )

    def action_resume(self) -> None:
        self.dismiss(True)

    def action_fresh(self) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ScaffoldScreen(Screen):
    """The files this run could create, and the one thing creating them does not do.

    `ACT-033`. Every packet before this made the wizard better at saying it did not know; this is
    the first that offers to do something about it. A repository with nothing in it could be told
    honestly that nothing matched its gates, and then go no further.

    The screen exists rather than a silent write because creating files in someone else's
    repository is a different class of action from filling in a profile, and because of the thing
    printed at the bottom of it: **a register that exists is not a register anyone keeps**. The
    gate's structural check would pass either way, so the only defence against that becoming a
    false green is that the adopter is told, at the point of choosing, exactly what they are and
    are not getting.

    Everything is ticked on arrival - the adopter reached here by having a gate with nothing to
    point at, so the offer is the answer to a problem they already have - and any line can be
    unticked. Nothing is written from this screen: it selects, and the profile review that has
    always ended this run commits.
    """

    BINDINGS = [
        Binding("ctrl+s", "accept", "create the ticked files", show=True),
        Binding("ctrl+q", "cancel", "quit", show=True),
    ]

    def __init__(self, offers: list, step: str = "") -> None:
        super().__init__()
        self.offers = offers
        self.step = step

    def compose(self) -> ComposeResult:
        with Frame(id="frame"):
            yield Static(
                f"[{self.step}Missing artefacts - shall I create them?]", classes="section-header"
            )
            yield Static(
                f"{len(self.offers)} gate(s) you must declare have nothing in this repository to "
                "point at. These are real, complete files - not templates to fill in - and each is "
                "written only if it is ticked. Anything already present is not offered at all.",
                classes="intro",
            )
            yield VisibleSelectionList(
                *[
                    Selection(f"{o.path}  -  {o.why}", index, True)
                    for index, o in enumerate(self.offers)
                ],
                id="f-scaffold",
            )
            for offer in self.offers:
                yield Static(f"  {offer.path}  ({offer.gate_id})", classes="gate-name")
                yield Static(offer.preview(3), classes="gate-desc")
            yield Static(
                "  Creating these files does not do the work they are for. A register that exists "
                "and stays empty while work happens around it is a finding about your repository, "
                "not a satisfied control - and the checker cannot tell the difference, because it "
                "checks that the file is there.",
                classes="note",
            )
        yield Static("", id="hint", markup=False)

    def on_mount(self) -> None:
        self.query_one("#hint", Static).update(
            hint_line(keys="[space] tick  [Ctrl+S] create the ticked files  [Ctrl+Q] cancel")
        )

    def action_accept(self) -> None:
        chosen = set(self.query_one("#f-scaffold", VisibleSelectionList).selected)
        self.dismiss([o for index, o in enumerate(self.offers) if index in chosen])

    def action_cancel(self) -> None:
        self.dismiss(None)
