#!/usr/bin/env python3
"""What the wizard's screens actually render, asserted rather than eyeballed.

    python tests/test_render.py

`F37` is why this exists. Phase 2 shipped 87 green checks and a visibly broken interface: every
test asserted *structure* — field-id joins, widget counts, status transitions — and none asserted
what a screen puts on the terminal. Six user-visible defects passed all of them, and adding more
structural checks could only ever have confirmed the mistake, because they were answering a
different question. This suite asks the question the others could not.

**Properties, not snapshots — deliberately.** `.claude/rules/surfaceplate-tests.md` treats a golden
file as an audit trigger and warns that regenerating one to absorb a delta destroys the evidence
that something changed. A full-screen snapshot of a wizard whose copy is still being tuned would
churn on every wording change and train exactly that habit. So each check below states a property in
words - "the legend renders the keys it names" - and fails for one readable reason.

**Every assertion here has been seen to fail.** Each was written against the defect it catches while
that defect was still present, and `DR-37` records what each one caught. A property test that has
never failed is a property test nobody has calibrated.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from textual import work  # noqa: E402
from textual.app import App  # noqa: E402

from surfaceplate.adopt import flow as _flow  # noqa: E402
from surfaceplate.adopt import plan  # noqa: E402
from surfaceplate.adopt.interview import DraftInfo  # noqa: E402
from surfaceplate.adopt.tui.screens import (  # noqa: E402
    FormScreen,
    GatesScreen,
    LevelScreen,
    ResumeScreen,
    ReviewScreen,
)

FAILURES: list[str] = []
PASSES = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSES
    if condition:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


class Host(App):
    CSS_PATH = ROOT / "surfaceplate" / "adopt" / "tui" / "app.tcss"

    def __init__(self, screen) -> None:
        super().__init__()
        self._screen_under_test = screen

    def on_mount(self) -> None:
        self._drive()

    @work
    async def _drive(self) -> None:
        await self.push_screen_wait(self._screen_under_test)


def rendered(app: App) -> list[str]:
    """The visible text of the current screen, one string per terminal row.

    `Compositor.render_strips()` and `Strip.text` are the same path `App.export_screenshot` walks
    before turning the result into SVG. Textual publishes no plain-text export, so this reaches for
    a private attribute knowingly: the alternative is asserting nothing about rendering at all,
    which is precisely the gap `F37` records. If a future Textual moves it, this suite fails loudly
    on import rather than silently passing.
    """
    return [strip.text for strip in app.screen._compositor.render_strips()]


def screen_text(lines: list[str]) -> str:
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------------
# 1 & 2 — the legends render the keys they name
# ---------------------------------------------------------------------------------------------


def test_every_legend_renders_the_keys_it_names() -> None:
    """Textual markup parses `[Tab]` and `[Enter]` as style tags and swallows them, while
    symbol-bearing keys like `[Ctrl+S]` and `[↑↓]` survive - which is why this looked correct in
    review. The resume screen was the worst case: both of its keys vanished, leaving a choice with
    no visible way to make it."""

    async def _run() -> None:
        cases = [
            ("identity form", FormScreen(plan.identity_plan()), ["\u2191\u2193", "Ctrl+S", "Ctrl+Q"]),
            (
                "conformance level",
                LevelScreen(plan.level_plan(ROOT, builds_ui=False, mode="simple")),
                ["Enter", "?", "Ctrl+Q"],
            ),
            (
                "gate catalogue",
                GatesScreen(
                    plan.gate_plan(level="standard", builds_ui=False, mode="simple"),
                    plan.gates_plan(level="standard", builds_ui=False, mode="simple"),
                ),
                ["\u2191\u2193", "Ctrl+G", "Ctrl+S", "Ctrl+Q"],
            ),
            (
                "resume offer",
                ResumeScreen(
                    DraftInfo(sections=("mode", "identity"), framework_version="0.16.0",
                              framework_digest="abc", matches=True)
                ),
                ["y", "n"],
            ),
            ("review", ReviewScreen(_flow.Review(rendered="schema_version: '1.0'\n", lines=[])), ["Ctrl+S", "Ctrl+Q"]),
        ]
        for label, screen, keys in cases:
            app = Host(screen)
            async with app.run_test(size=(100, 34)) as pilot:
                await pilot.pause()
                text = screen_text(rendered(app))
            missing = [k for k in keys if f"[{k}]" not in text]
            check(
                f"{label}: every key it names is actually rendered",
                not missing,
                f"missing from the screen: {missing}",
            )

    asyncio.run(_run())


# ---------------------------------------------------------------------------------------------
# 3 — no label is printed twice
# ---------------------------------------------------------------------------------------------


def test_no_field_label_is_rendered_twice() -> None:
    """`_widget_for` used the field's label as the input's placeholder while `compose` also yielded
    a `Label` for it, so every field said its own name twice - "Precondition artefact (a real path)"
    above an input containing "Precondition artefact (a real path)"."""

    async def _run() -> None:
        section = plan.identity_plan()
        app = Host(FormScreen(section))
        async with app.run_test(size=(100, 34)) as pilot:
            await pilot.pause()
            text = screen_text(rendered(app))
        repeated = [spec.label for spec in section.fields if text.count(spec.label) > 1]
        check(
            "identity: no field label appears more than once on screen",
            not repeated,
            f"rendered twice: {repeated}",
        )

    asyncio.run(_run())


# ---------------------------------------------------------------------------------------------
# 4 — the label column is a column
# ---------------------------------------------------------------------------------------------


def test_label_and_value_share_a_rendered_line() -> None:
    """The mockup's frame 01 puts the label and its value on one row with a fixed gutter. The first
    build nested them in a `Vertical`, so `width: 34` on the label could not sit beside anything and
    three fields sprawled down the screen."""

    async def _run() -> None:
        app = Host(FormScreen(plan.identity_plan()))
        async with app.run_test(size=(100, 34)) as pilot:
            await pilot.pause()
            app.screen.query_one("#f-application_id").value = "plutos"
            await pilot.pause()
            lines = rendered(app)
        together = [ln for ln in lines if "application_id" in ln and "plutos" in ln]
        check(
            "identity: a label and its value render on the same line",
            bool(together),
            "label and value are on different rows - the column is stacked, not side by side",
        )

    asyncio.run(_run())


# ---------------------------------------------------------------------------------------------
# 5 — help belongs to the focused field only
# ---------------------------------------------------------------------------------------------


def test_help_is_shown_only_for_the_focused_field() -> None:
    """Phase 2's own plan said "help for the current field only, inline in the hint line". What
    shipped rendered every field's help at once, indented into the middle of the screen where it
    read as a layout fault."""

    async def _run() -> None:
        section = plan.identity_plan()
        helps = [spec.help for spec in section.fields if spec.help]
        app = Host(FormScreen(section))
        async with app.run_test(size=(100, 34)) as pilot:
            await pilot.pause()
            app.screen.query_one("#f-application_id").focus()
            await pilot.pause()
            text = screen_text(rendered(app))
        showing = [h for h in helps if h[:40] in text]
        check(
            "identity: exactly one field's help is on screen at a time",
            len(showing) <= 1,
            f"{len(showing)} help strings rendered at once",
        )

    asyncio.run(_run())


# ---------------------------------------------------------------------------------------------
# 6 — the gate catalogue shows several gates
# ---------------------------------------------------------------------------------------------


def test_several_gates_are_visible_at_a_standard_terminal() -> None:
    """The whole thesis of the mockup's frame 03 is several gates at once. All nineteen were on one
    scrolling surface - which is what the Phase 2 tests checked, and why they passed - but each was
    so vertically loose that only one was ever on screen."""

    async def _run() -> None:
        specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple")
        section = plan.gates_plan(level="standard", builds_ui=False, mode="simple")
        app = Host(GatesScreen(specs, section))
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            text = screen_text(rendered(app))
        visible = [spec.id for spec in specs if spec.id in text]
        check(
            "gates: at least three gates are visible in an 80x24 terminal",
            len(visible) >= 3,
            f"only {len(visible)} gate(s) on screen: {visible}",
        )

    asyncio.run(_run())


def test_a_gate_status_radio_set_renders_its_options() -> None:
    """`F59`. Every undecided gate's status radio was invisible at every terminal size.

    `.chip-row { height: 1 }` left Textual's `RadioSet`, which draws a two-row `tall` border plus
    padding, with no row for its buttons: the status row rendered as an empty bordered box, the
    keyboard still changed a value nobody could see, and the maintainer did not get past the
    gates screen again after the radio rewrite. `tests/test_adopt_tui.py` set `.value` on the
    buttons and read it back, which is the class `F37` records - structurally verified, never
    looked at. This reads the row as the terminal shows it, at the size the review used.
    """

    async def _run() -> None:
        from textual.widgets import RadioSet

        specs = plan.gate_plan(level="standard", builds_ui=False, mode="simple")
        section = plan.gates_plan(level="standard", builds_ui=False, mode="simple")
        first = next(s for s in specs if not s.mandatory and not s.auto_status)
        app = Host(GatesScreen(specs, section))
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            app.screen.query_one(f"#f-{first.id}--status", RadioSet).focus()
            await pilot.pause()
            await pilot.pause()
            text = screen_text(rendered(app))
        expected = ["( ) required", "( ) deferred", "( ) not applicable"]
        missing = [option for option in expected if option not in text]
        check(
            f"gates: the focused {first.id} status radio renders its three options at 80x24",
            not missing,
            f"not on screen: {missing}",
        )

    asyncio.run(_run())


def test_a_bracketed_heading_is_rendered_not_parsed() -> None:
    """`F68`, second half. `"[A saved draft was found]"` was consumed as markup because that
    `Static` lacked `markup=False`, so the resume prompt opened with no heading at all. The
    section headers survive only where their step prefix happens to defeat the parser - a
    screen shown with no step (`mode`, and every screen hosted without one) loses its title too.
    `F37 #1` on the screens it did not reach."""

    async def _run() -> None:
        cases = [
            (
                "resume offer",
                ResumeScreen(DraftInfo(sections=("mode",), framework_version="0.16.0",
                                       framework_digest="abc", matches=True)),
                "A saved draft was found",
            ),
            (
                "decisions form, no step prefix",
                FormScreen(plan.decisions_plan(ROOT, found=plan.discover.Discovered(), proposals={})),
                plan.decisions_plan(ROOT, found=plan.discover.Discovered(), proposals={}).title,
            ),
            (
                "conformance level, no step prefix",
                LevelScreen(plan.level_plan(ROOT, builds_ui=False, mode="simple")),
                plan.level_plan(ROOT, builds_ui=False, mode="simple").title,
            ),
            (
                "gate catalogue, no step prefix",
                GatesScreen(
                    plan.gate_plan(level="standard", builds_ui=False, mode="simple"),
                    plan.gates_plan(level="standard", builds_ui=False, mode="simple"),
                ),
                plan.gates_plan(level="standard", builds_ui=False, mode="simple").title,
            ),
        ]
        for label, screen, heading in cases:
            app = Host(screen)
            async with app.run_test(size=(80, 24)) as pilot:
                await pilot.pause()
                # The frame's own box-drawing rows are not content.
                lines = [line for line in rendered(app) if line.strip("│╭╮╰╯─ ")]
            first = lines[0] if lines else ""
            check(
                f"{label}: the first rendered line is the heading [{heading}]",
                f"[{heading}]" in first,
                f"first line: {first.strip()!r}",
            )

    asyncio.run(_run())


MUTED = "#7a827e"


def _rows_with_styles(app: App) -> list[list[tuple[str, str]]]:
    """Each terminal row as `(text, colour hex)` per segment - the colour a viewer would see."""
    rows = []
    for strip in app.screen._compositor.render_strips():
        row = []
        for segment in strip:
            colour = ""
            if segment.style is not None and segment.style.color is not None:
                colour = segment.style.color.get_truecolor().hex.lower()
            row.append((segment.text, colour))
        rows.append(row)
    return rows


def test_help_text_is_muted_and_kept_off_the_next_field() -> None:
    """`F67`, the help-text part (the maintainer's complaint 2). `.field-help` had no rule in
    `app.tcss`, so the help line under `application_id` rendered full-white - brighter than the
    label it explains - flush against the frame, with `display_name` starting on the very next
    row. Identical at 120×40, so it was styling, not width. This reads the colour of every
    segment on the help rows and the row that follows them."""

    async def _run() -> None:
        section = plan.identity_plan()
        first, second = section.fields[0], section.fields[1]
        for size in ((80, 24), (120, 40)):
            app = Host(FormScreen(section))
            async with app.run_test(size=size) as pilot:
                await pilot.pause()
                await pilot.pause()
                rows = _rows_with_styles(app)
            texts = ["".join(text for text, _ in row) for row in rows]
            opening = " ".join(first.help.split()[:3])
            help_rows = [i for i, text in enumerate(texts) if opening in text]
            next_label = next((i for i, text in enumerate(texts) if second.label in text), None)
            check(
                f"{size[0]}x{size[1]}: the focused field's help is on screen",
                bool(help_rows) and next_label is not None,
                f"help rows {help_rows}, next label row {next_label}",
            )
            if not help_rows or next_label is None:
                continue
            start = help_rows[0]
            loud = [
                (text, colour)
                for row in rows[start:next_label]
                for text, colour in row
                if text.strip() and text.strip() not in "│" and colour != MUTED
                and any(word in text for word in first.help.split())
            ]
            check(
                f"{size[0]}x{size[1]}: every word of the help renders in the muted colour {MUTED}",
                not loud,
                f"louder segments: {loud[:3]}",
            )
            gap = texts[next_label - 1].strip("│ ")
            check(
                f"{size[0]}x{size[1]}: one blank row separates the help from the next field",
                next_label - 1 > start and gap == "",
                f"row before {second.label!r}: {texts[next_label - 1].strip()!r}",
            )

    asyncio.run(_run())


# ---------------------------------------------------------------------------------------------
# The level screen's own structure
# ---------------------------------------------------------------------------------------------


def test_level_screen_numbers_its_options_and_marks_the_highlight() -> None:
    """The mockup numbers the three levels and marks the highlighted row with an amber caret, so
    the list reads as a choice rather than a paragraph. Neither was built."""

    async def _run() -> None:
        app = Host(LevelScreen(plan.level_plan(ROOT, builds_ui=False, mode="simple")))
        async with app.run_test(size=(100, 34)) as pilot:
            await pilot.pause()
            text = screen_text(rendered(app))
        numbered = all(f"{n}" in text for n in (1, 2, 3))
        check("level: the three options are numbered", numbered, text[:200])
        check("level: the highlighted row carries a marker", "▸" in text, text[:200])

    asyncio.run(_run())


def test_no_field_label_is_silently_truncated() -> None:
    """`F56`. Twenty-eight labels were clipped at the design width with nothing to say so.

    `.field-label` carried `height: 1` and `text-overflow: ellipsis`, and — exactly as `.gate-desc`
    did before `F42` — **the ellipsis never rendered**. `Why does documentation_authority apply
    here?` became a fragment, and the adopter had no way to know a question had been shortened. Most
    predate `ACT-035`: at the previous fixed `width: 32` anything longer was already cut.

    **Asked of the widget, not of the composited screen, and that took three attempts.** A label in
    a two-column row wraps to several lines with the VALUE column's text interleaved between them,
    so no join over rendered rows can reconstruct it — the first two versions of this assertion
    failed against a fix that was working. The property is "is there room for all of it", which is a
    question about the widget's own box: its height against the lines its text needs at its width.
    """

    async def _run() -> None:
        from textual.widgets import Label

        from surfaceplate.adopt import discover
        from surfaceplate.adopt.tui.screens import GatesScreen

        found = discover.Discovered(artefacts=("a/register.md",), paths=("src/**",))
        screens = [
            ("risk", FormScreen(plan.risk_plan())),
            ("adoption", FormScreen(plan.adoption_plan(owner="x"))),
            ("controls", FormScreen(plan.controls_plan(level="standard", mode="simple", found=found))),
        ]
        specs = plan.gate_plan(level="essential", builds_ui=False, mode="simple", found=found)
        screens.append((
            "gates",
            GatesScreen(specs, plan.gates_plan(level="essential", builds_ui=False, mode="simple", found=found)),
        ))

        clipped: list[str] = []
        for name, screen in screens:
            app = Host(screen)
            async with app.run_test(size=(80, 70)) as pilot:
                await pilot.pause()
                for label in app.screen.query(Label):
                    if "field-label" not in label.classes:
                        continue
                    text = str(label.renderable) if hasattr(label, "renderable") else str(label.render())
                    text = " ".join(text.split())
                    width, height = label.size.width, label.size.height
                    if not text or width <= 0:
                        continue
                    needed = -(-len(text) // width)  # ceil, in whole rows at this width
                    if height < needed:
                        clipped.append(f"{name}:{text[:34]!r} needs {needed} row(s), has {height}")

        check(
            "no field label is clipped - every one has room for all of its text",
            not clipped,
            f"{len(clipped)} clipped with nothing to say so, e.g. {clipped[:2]}",
        )

    asyncio.run(_run())


def test_the_most_consequential_choice_is_readable_at_80_columns() -> None:
    """`ACT-035`. The route screen decides how the whole rest of the run behaves, and at 80 columns
    both of its options used to end in an ellipsis - `Set defaults - propose answers f…`. An adopter
    choosing between two options they cannot finish reading is not making the choice the screen
    thinks it is offering.

    Asserted on the ROUTE screen specifically rather than on every choice everywhere: this is the
    one where the cost of mis-reading is a different run, and a blanket rule would force every
    explanatory label in the wizard to be short whether or not that helped.
    """

    async def _run() -> None:
        # `DR-47`: the route screen is gone; the consequential choices now sit on the decisions
        # form, and the property is the same - every option readable in full at 80 columns.
        section = plan.decisions_plan(ROOT, found=plan.discover.Discovered(), proposals={})
        app = Host(FormScreen(section))
        cut = []
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            for spec in section.fields:
                if spec.kind != "choice":
                    continue
                # The form scrolls; each choice is read with its own widget scrolled into view.
                widget = app.screen.query_one(f"#f-{spec.id.replace('.', '--')}")
                widget.focus()
                await pilot.pause()  # Textual's own scroll-into-view lands first
                app.screen.query_one("#frame").scroll_to_widget(widget, top=True, animate=False)
                await pilot.pause()
                await pilot.pause()
                lines = rendered(app)
                for value, label in spec.choices:
                    row = next((ln for ln in lines if label[:12] in ln), "")
                    if not row or label not in row:
                        cut.append((spec.id, value, row.strip()))
        check(
            "every decision option is readable in full at 80 columns",
            not cut,
            f"truncated on screen: {cut}",
        )

    asyncio.run(_run())


def test_a_gate_explanation_is_never_silently_cut() -> None:
    """`F42`. The explanations exist so an adopter knows what they are declaring; discarding most
    of one without saying so is worse than not showing it, because the reader has no way to know
    there was more.

    Two properties, and the second is the one that matters. Either the whole sentence is on screen,
    **or** what is shown ends in an ellipsis. `.gate-desc` declared `text-overflow: ellipsis` and it
    never rendered - the sentence just stopped - so asserting "it wraps" alone would pass on a
    layout that still lies.
    """

    async def _run() -> None:
        from surfaceplate.adopt import discover, explanations
        from surfaceplate.adopt.tui.screens import GatesScreen, _first_sentence

        found = discover.Discovered()
        specs = plan.gate_plan(level="essential", builds_ui=False, mode="simple", found=found)
        section = plan.gates_plan(level="essential", builds_ui=False, mode="simple", found=found)
        app = Host(GatesScreen(specs, section))
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            lines = rendered(app)

        want = _first_sentence(explanations.explain("work_registration", "simple"))
        # Whole-screen text, not a per-line reassembly. The first version of this rebuilt the
        # explanation from lines containing one of its first six words, and `F51` adding a field to
        # the gate block changed the wrap so the elided line no longer matched - the assertion
        # failed while the screen was correct. A property about what is ON SCREEN should be asked
        # of the screen, not of a guess about which rows the words landed on.
        flat = " ".join(" ".join(lines).split())
        complete = " ".join(want.split()) in flat
        elided = "\u2026" in flat
        check(
            "a gate explanation is shown whole, or says it was cut",
            complete or elided,
            f"{len(want)} chars of explanation, neither complete nor elided on screen",
        )

    asyncio.run(_run())


def test_a_multiselect_shows_each_row_state_in_the_text() -> None:
    """`F41`. The same property as the checkbox below, for the widget that never got the fix.

    `SelectionList` builds its tick box from `ToggleButton`'s CLASS attributes, so `_StatefulToggle`
    - which sets them on an instance - could never reach it, and every multiselect in this wizard
    rendered `[X]` on every row regardless of what was ticked. Ticked and unticked rows must differ
    in TEXT, on the same screen, at the same moment: comparing one row before and after a change
    would pass even if every row still drew the same glyph as its neighbours.
    """

    async def _run() -> None:
        spec = plan.FieldSpec(
            id="enf",
            label="Enforcement",
            kind="multiselect",
            choices=(("a", "alpha"), ("b", "beta"), ("c", "gamma")),
            default="a",  # exactly one ticked, so both states are on screen together
            validate="",
        )
        section = plan.SectionPlan(name="s", title="Multiselect", fields=(spec,))
        app = Host(FormScreen(section))
        async with app.run_test(size=(90, 24)) as pilot:
            await pilot.pause()
            lines = rendered(app)
            # Only the BUTTON, not the whole prefix. The field's label sits on the first row and
            # not the second, so comparing prefixes passed with the defect fully present - this
            # assertion was written, seen to pass against the broken widget, and narrowed. It is
            # `DR-37`'s warning happening to the test written to honour it.
            def button(line: str, option: str) -> str:
                return line.split(option)[0][-4:] if option in line else ""

            ticked = button(next((ln for ln in lines if "alpha" in ln), ""), "alpha")
            unticked = button(next((ln for ln in lines if "beta" in ln), ""), "beta")
        check(
            "a ticked multiselect row and an unticked one differ in rendered text",
            bool(ticked) and bool(unticked) and ticked != unticked,
            f"both rows draw the same box - state is colour only: {ticked!r} vs {unticked!r}",
        )

    asyncio.run(_run())


def test_a_toggle_shows_its_state_in_the_text_not_only_the_colour() -> None:
    """`F38`: *"some boxes (x) are not clearly visible so you don't know you have to click (X)."*

    Textual's `ToggleButton` draws the same three characters whatever the state and signals on/off
    purely by style - so a ticked box and an unticked one are the SAME SHAPE, and a text render
    cannot tell them apart either. That is the point: if this assertion can distinguish them, so
    can a person who is not looking closely at colour.
    """

    async def _run() -> None:
        from textual.widgets import Checkbox

        # `stack`, not `controls`: `ACT-032` collapsed the eight `<control>.declared` booleans into
        # one multiselect, so the controls section no longer contains a `bool` at all. Picking the
        # section by "wherever a bool happens to live" is what made this break, so it is named.
        section = plan.stack_plan(Path("."))
        spec = next(f for f in section.fields if f.kind == "bool")
        app = Host(FormScreen(section))
        async with app.run_test(size=(100, 40)) as pilot:
            await pilot.pause()
            box = app.screen.query_one(f"#f-{spec.id.replace('.', '--')}", Checkbox)
            label = spec.label[:24]

            def toggle_row(lines: list[str]) -> str:
                # The checkbox's OWN row, not the whole screen. Comparing whole screens passed even
                # with the glyph reverted, because unrelated things (focus, help) also differ - a
                # weak assertion that would have gone on passing forever.
                return next((ln for ln in lines if label in ln), "")

            off = toggle_row(rendered(app))
            box.value = True
            await pilot.pause()
            on = toggle_row(rendered(app))
        check(
            "a checkbox's on and off states differ in the rendered text",
            bool(off) and off != on,
            f"the box renders identically either way - state is carried by colour alone: {off!r}",
        )

    asyncio.run(_run())


def test_a_small_window_scrolls_rather_than_clipping() -> None:
    """`F38`: *"the terminal is cut if you minimise the window, it doesn't autoadjust."*

    Not a driver limitation - Textual installs a SIGWINCH handler and reflows. `Vertical` simply is
    not a scrolling container, so content taller than the window had nowhere to go. The frame is a
    `Frame(VerticalScroll)` now, non-focusable so it does not eat the arrow keys.
    """

    async def _run() -> None:
        # The controls section is long enough to overflow any small window, and its `#frame` IS
        # the scroller (the gate catalogue nests a second one inside, so it would test the wrong
        # container).
        section = plan.controls_plan(level="full", mode="simple")
        app = Host(FormScreen(section))
        async with app.run_test(size=(70, 14)) as pilot:  # deliberately cramped
            await pilot.pause()
            frame = app.screen.query_one("#frame")
            lines = rendered(app)
            check(
                "at a cramped size the frame scrolls rather than clipping",
                frame.allow_vertical_scroll and frame.virtual_size.height > frame.size.height,
                f"virtual {frame.virtual_size.height} vs visible {frame.size.height}",
            )
            check(
                "and the frame never takes focus, so the arrows still reach the fields",
                not frame.can_focus,
                "a focusable scroll container swallows up/down",
            )
            check(
                "and the hint line is still on screen at that size",
                any("Ctrl+Q" in line for line in lines),
                "\n".join(lines[-3:]),
            )

    asyncio.run(_run())


def test_an_empty_field_still_shows_where_to_type() -> None:
    """`F38`: *"difficult sometimes to follow and know where you must add text."*

    A borderless input containing nothing renders as blank space, and a background tint alone does
    not survive a monochrome terminal or a screenshot. Every input carries an underline, which is
    visible without colour - and, being a character, is visible to this assertion too.
    """

    async def _run() -> None:
        app = Host(FormScreen(plan.identity_plan()))
        async with app.run_test(size=(90, 24)) as pilot:
            await pilot.pause()
            lines = rendered(app)
        # Only rules that begin PAST the label column are field slots. Counting every run of box
        # characters also counted the frame border and the hint rule, so the check passed with the
        # underlines removed entirely - precisely the sort of assertion `DR-37` exists to catch.
        rule = "\u2500" * 8
        slots = [ln for ln in lines if rule in ln and ln.index(rule) > 20]
        expected = len(plan.identity_plan().fields)
        check(
            "an empty field renders a visible slot, not blank space",
            len(slots) >= expected,
            f"only {len(slots)} field slots rendered for {expected} fields",
        )

    asyncio.run(_run())


def main() -> int:
    print("legends render the keys they name (F37 #1, #2)")
    test_every_legend_renders_the_keys_it_names()

    print("\nnothing is printed twice (F37 #3)")
    test_no_field_label_is_rendered_twice()

    print("\nthe label column is a column (F37 #4)")
    test_label_and_value_share_a_rendered_line()

    print("\nhelp belongs to the focused field (F37 #5)")
    test_help_is_shown_only_for_the_focused_field()

    print("\nseveral gates are visible (F37 #6)")
    test_several_gates_are_visible_at_a_standard_terminal()

    print("\nF59: the status radios are visible")
    test_a_gate_status_radio_set_renders_its_options()

    print("\nF68: a bracketed heading is rendered, not parsed")
    test_a_bracketed_heading_is_rendered_not_parsed()

    print("\nF67: help text is muted and kept off the next field")
    test_help_text_is_muted_and_kept_off_the_next_field()

    print("\nthe level screen reads as a choice")
    test_level_screen_numbers_its_options_and_marks_the_highlight()

    print("\nF38: state and size")
    test_a_toggle_shows_its_state_in_the_text_not_only_the_colour()
    test_no_field_label_is_silently_truncated()
    test_the_most_consequential_choice_is_readable_at_80_columns()
    test_a_gate_explanation_is_never_silently_cut()
    test_a_multiselect_shows_each_row_state_in_the_text()
    test_a_small_window_scrolls_rather_than_clipping()
    test_an_empty_field_still_shows_where_to_type()

    print()
    if FAILURES:
        print(f"RENDER=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"RENDER=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
