"""What the wizard will ask, described as data rather than as control flow.

`DR-36` records why this module exists. Before it, "which questions does an `essential`-level run
with no user interface actually ask?" was answerable only by *running* `sections.ask_gates` and
watching what it did - the applicability rules (level floors, `DESIGN_GATES` auto-masking, the
`essential` short-circuit) lived inside the same functions that did the asking. That was survivable
when asking was a sequence of `Prompt` calls. It is not survivable once a screen has to render
several gates at once, because the screen needs to know the shape of the whole section *before* it
draws anything.

So the shape moves here, and three separate consumers now join against one description:

- `tui/` renders a `SectionPlan` into widgets;
- `ScriptedInterview` answers a `SectionPlan` field by field, and objects to any field it was given
  no answer for (and any answer no field asked for);
- `tests/test_adopt_tui.py` asserts each screen's field ids equal its plan's field ids.

**That third one is what makes the other two load-bearing.** A script that answers the plan proves
the plan was answered, not that the screens ask the plan; the join test is what closes the gap. See
`DR-36`'s own note on why `ScriptedPrompt` never proved what it appeared to.

Nothing here decides anything on a human's behalf. A `FieldSpec` carries a `default` where this
framework has a real example to offer (`example_answers.py`) or a suggestion the old flow already
made (today's date, `history_audit, review`), and a default is still submitted by a human before it
becomes an answer - the same "shown, must submit" contract `DR-32` established and `DR-35` extended.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field as _field
from pathlib import Path

from surfaceplate.adopt import catalogue, detect, discover, example_answers, explanations, validators

# The three controls required at every level. Fixed order, matching the profile's own layout and
# `core/CONFORMANCE_LEVELS.md`'s "The three baseline controls" section.
BASELINE_CONTROL_IDS = ("agent_work_packets", "actual_diff_review", "secret_hygiene")

# `DR-51` (3): what the checker does with each kind of implementation reference, and the cost of
# naming the wrong thing. One sentence each, reused wherever the same rule applies.
ARTEFACT_DECIDES = (
    "the file the checker requires to exist, be non-empty, carry no placeholder and be tracked "
    "by git (SP032), and to precede every change under the gated paths in history (SP035)"
)
ARTEFACT_WRONG = "a file that is not the artefact satisfies the check and guards nothing"
PATTERN_A_DECIDES = "the file the checker requires to exist, be non-empty, carry no placeholder and be tracked (SP051)"
PATTERN_B_DECIDES = "the workflow step the checker looks up by name and requires to be able to fail the job (SP053)"
PATTERN_C_DECIDES = "the directory of records the checker validates against this control's schema (SP055, SP056)"
CONTROL_WRONG = "the control fails on the next run, or something that is not the implementation passes for it"
RATIONALE_DECIDES = "why the profile says this applies here; read by reviewers and auditors, never by the checker"
RATIONALE_WRONG = "a reason nobody wrote is the framework's example standing under your name"
SCANNER_WIRED_DECIDES = (
    "the file the checker opens to confirm the named scanner runs there and can fail the build "
    "(SP046, SP047) - the one baseline control that is actually checked"
)
SCANNER_WIRED_WRONG = "the checker reports the scanner absent on its next run"
LOCK_DECIDES = PATTERN_A_DECIDES
NOT_CHECKED_WRONG = "a misleading profile; the checker never reads this"
RELEASE_ROUTE_DECIDES = "what the profile records as the human and platform controls between a merge and a release; not verified"
RELEASE_ROUTE_WRONG = "a route nobody follows is a promise the profile makes on your behalf"

# Words that mark a file as a findings register, for ranking the offer and for proposing: a
# proposal comes only from a match (`F40`'s rule, applied to controls at `DR-54` (2)).
FINDINGS_WORDS = ("finding", "assurance")

TEMPLATE_PLACEHOLDER_HELP = (
    'Type an actual value. "TBD", "TODO" and similar are template placeholders this framework\'s '
    "own checker rejects (SP020) - writing one here would fail the profile you're about to produce."
)


@dataclass(frozen=True)
class FieldSpec:
    """One thing a human is asked for.

    `id` is unique within its section; the addressable key a script uses is `f"{section}.{id}"`.
    `depends_on` is the single mechanism for conditionality anywhere in this wizard - a gate's
    follow-ups, `status_rationale`, `independent_validator` all use it, so a screen has exactly one
    rule to implement and the join test has exactly one rule to check.
    """

    id: str
    label: str
    kind: str = "text"  # text | textarea | choice | bool | select | multiselect
    help: str = ""
    default: str = ""
    choices: tuple[tuple[str, str], ...] = ()
    validate: str = "nonempty"  # a name in validators.py; "" means anything, including blank
    depends_on: tuple[str, tuple[object, ...]] | None = None
    # Candidates read out of the adopting repository (`discover.py`). On a `select` field these
    # ARE the options; on a `text` field they are offered as inline completions and constrain
    # nothing. Empty means discovery found none - the field then behaves exactly as it did before
    # discovery existed, which is the honest fallback for a repository git cannot read.
    suggestions: tuple[str, ...] = ()
    # `DR-51` (3): the stated minimum for a reader meeting the framework for the first time -
    # what the answer decides, and what a wrong answer costs. Shown beside the focused field with
    # `help`; `tests/test_adopt.py` fails on any presented field lacking either.
    decides: str = ""
    wrong: str = ""
    # `DR-51` (4): how to describe a chosen value - `gate:<id>`, `scanner:<name>`, `lock`,
    # `register`, `step` - so the help beside a dropdown can say what the chosen file is.
    context: str = ""
    # `F67`: a list whose labels must fit a row keeps each choice's full explanation here, shown
    # beside the list for the highlighted row, keyed by the choice's value.
    choice_help: tuple[tuple[str, str], ...] = ()
    # `DR-54` (1): the path of the seed this field's first row offers to create, where one is
    # free; the value of that row is the path itself, and choosing it leads to the offer.
    seed: str = ""

    def applies(self, answers: dict) -> bool:
        """Whether this field is asked at all, given what has been answered so far in its section."""
        if self.depends_on is None:
            return True
        other_id, wanted = self.depends_on
        value = answers.get(other_id)
        # A `multiselect` answers with a list, so "depends on that field" means "is among what was
        # ticked". This is the same rule generalised, not a second one: for every scalar answer the
        # behaviour is unchanged, and a screen still has one question to ask of a field.
        if isinstance(value, (list, tuple, set)):
            return any(item in value for item in wanted)
        return value in wanted


@dataclass(frozen=True)
class SectionPlan:
    name: str  # the state key: "identity", "gates", ...
    title: str  # what the frame header shows
    fields: tuple[FieldSpec, ...] = ()
    intro: str = ""  # explanatory text above the fields
    recap: tuple[str, ...] = ()  # "You told us:" lines, from earlier sections
    notes: tuple[str, ...] = ()  # detected signals and similar, shown but never acted on

    def field_ids(self) -> list[str]:
        return [f.id for f in self.fields]

    def applicable_fields(self, answers: dict) -> list[FieldSpec]:
        return [f for f in self.fields if f.applies(answers)]


@dataclass(frozen=True)
class GateSpec:
    """One gate in the catalogue screen, as a mini-section.

    A gate is the only place this wizard shows several answerable things at once, so it carries its
    own fields rather than flattening into the section: the screen draws three `GateSpec`s side by
    side and each one's follow-ups appear inside its own block.
    """

    id: str
    section: str  # the `core/PREREQUISITE_GATES.md` group heading it belongs to
    explanation: str  # already resolved for the active mode
    mandatory: bool  # the level forces `required`; status is stated, not chosen
    auto_status: str = ""  # non-empty when the status is settled by an earlier answer
    fields: tuple[FieldSpec, ...] = _field(default_factory=tuple)

    def field_ids(self) -> list[str]:
        return [f"{self.id}.{f.id}" for f in self.fields]


# ---------------------------------------------------------------------------------------------
# Sections 0-3 — mode, identity, stack, risk
# ---------------------------------------------------------------------------------------------


_YES_NO_CHOICES = (("yes", "yes"), ("no", "no"))


def decisions_plan(repo: Path, *, found: discover.Discovered, proposals: dict) -> SectionPlan:
    """The one form before the level: what only the adopter can tell us (`DR-47`, report R1).

    Eight fields, plus one for each thing discovery could not find that every level needs. Nothing
    here is a question the tool could answer on the adopter's behalf: who owns this, whether it
    builds an interface, who relies on it, how its data is classified, how it is released. The
    three yes/no questions are radio choices with nothing pre-selected (`F64`), so each is a key
    the human pressed and is recorded as typed. `application_id` is pre-filled from the directory
    name and recorded as computed unless changed.
    """
    fields: list[FieldSpec] = [
        FieldSpec(
            id="identity.application_id",
            label="application_id",
            help="short, stable, used in file paths and IDs - lowercase, digits, hyphen or underscore",
            default=str(proposals["identity.application_id"].value) if "identity.application_id" in proposals else "",
            validate="application_id",
            decides="the id every record about this repository is filed under, and the name the checker reports",
            wrong="renaming later means changing every reference; pick the stable one now",
        ),
        FieldSpec(
            id="identity.owner",
            label="owner",
            help="who is accountable for this application, not this adoption - a named human",
            decides="who the framework holds accountable for this profile, and who reviewers look to",
            wrong="accountability lands on nobody, and the checker cannot tell",
        ),
    ]
    if "stack.language" not in proposals:
        fields.append(
            FieldSpec(
                id="stack.language",
                label="Language(s) / framework",
                help="nothing recognisable was detected, so say what this is built in",
                decides="what the profile records for its reader; the checker never reads it",
                wrong=NOT_CHECKED_WRONG,
            )
        )
    fields += [
        FieldSpec(
            id="stack.builds_user_interface",
            label="Does this repository build a user interface?",
            kind="choice",
            choices=_YES_NO_CHOICES,
            help=(
                "Decides whether the four interface gates are a floor at standard and full. "
                "Answer for what this repository actually does, not what it might do later."
            ),
            decides="whether the four interface gates (component library, design authority, options, screen state) are required at standard and full",
            wrong="yes on a repository with no interface adds four gates it can never satisfy; no on one with screens leaves them unguarded",
        ),
        # `ACT-032`: the two questions the level recommendation reads, in the framework's own
        # words (`catalogue.LEVEL_BLURBS`), so the level is answerable before it is explained.
        FieldSpec(
            id="risk.relied_on_outside_team",
            label="Does anyone outside your team rely on what this produces?",
            kind="choice",
            choices=_YES_NO_CHOICES,
            help=(
                "A colleague in another team, a customer, or another system reading your "
                "output. If it is a proof of concept or internal tooling nobody else depends "
                "on, the answer is no."
            ),
            decides="the level this tool recommends: standard exists for output someone outside the team depends on",
            wrong="a recommendation pointing at the wrong level; the level itself is still yours to choose on the next screen",
        ),
        FieldSpec(
            id="risk.material_quantitative_output",
            label="Does it produce numbers or AI output that others treat as fact?",
            kind="choice",
            choices=_YES_NO_CHOICES,
            help=(
                "Figures, model outputs or AI-generated results that another system or another "
                "team consumes without re-deriving them. Not: logs, dashboards of your own "
                "activity, or output a human always checks before it is used."
            ),
            decides="the level this tool recommends: full exists for numbers or AI output that others treat as fact",
            wrong="a recommendation pointing at the wrong level; the level itself is still yours to choose on the next screen",
        ),
        FieldSpec(
            id="risk.data_classification",
            label="Data classification",
            kind="choice",
            choices=(
                ("public", "public - no restriction"),
                ("internal", "internal - not for external release"),
                ("confidential", "confidential - within the organisation"),
                ("restricted", "restricted - the strictest tier"),
            ),
            help="the most sensitive data this repository handles, in the organisation's own tiers",
            decides="what the profile states about the data here; the repository classification is proposed from it",
            wrong="a profile that understates or overstates the data's sensitivity to whoever relies on it",
        ),
        FieldSpec(
            id="wrap.release_route",
            label="Release route",
            kind="textarea",
            help="human and platform release controls, in your own words",
            decides=RELEASE_ROUTE_DECIDES,
            wrong=RELEASE_ROUTE_WRONG,
        ),
        FieldSpec(
            id="risk.risk_profile",
            label="Risk, in your own words",
            kind="textarea",
            help="optional - intended use, uncertainty, materiality. Left blank, the profile says so",
            validate="",
            decides="the profile's own statement of what could go wrong and for whom",
            wrong="left blank, the profile says \"Not stated at adoption\", which is honest; a vague sentence is worse than that",
        ),
    ]
    # One question per thing discovery could not find that every level needs. A field with no
    # honest source is asked (`DR-40`); discovery's job is to make this rare, not to invent.
    # `F83` / `DR-51` (5): asked when no workflow RUNS the scanner, not when none exists.
    if not found.scanner_workflows:
        fields.append(
            FieldSpec(
                id="controls.scanner.wired_in",
                label="Scanner workflow file",
                help=f"no workflow with a step that runs {discover.DEFAULT_SCANNER} was found; name the file where the secret scanner runs",
                validate=f"scanner_workflow:{discover.DEFAULT_SCANNER}",
                context=f"scanner:{discover.DEFAULT_SCANNER}",
                decides=SCANNER_WIRED_DECIDES,
                wrong=SCANNER_WIRED_WRONG,
            )
        )
    if not found.lock_files:
        fields.append(
            FieldSpec(
                id="controls.dependency_lock.implementation_reference",
                label="Dependency lock file",
                help="no lock file was found; name the file that pins this repository's dependencies",
                validate="tracked_path",
                context="lock",
                decides=LOCK_DECIDES,
                wrong=CONTROL_WRONG,
            )
        )
    return SectionPlan(
        name="decisions",
        title="What only you can tell us",
        intro=(
            "Everything else is proposed from this repository and this framework's own examples, "
            "and shown to you with where it came from before anything is written."
        ),
        fields=tuple(fields),
    )


def identity_plan() -> SectionPlan:
    return SectionPlan(
        name="identity",
        title="Identity",
        fields=(
            FieldSpec(
                id="application_id",
                label="application_id",
                help="short, stable, used in file paths and IDs - lowercase, digits, hyphen or underscore",
                validate="application_id",
                decides="the id every record about this repository is filed under, and the name the checker reports",
                wrong="renaming later means changing every reference; pick the stable one now",
            ),
            FieldSpec(
                id="display_name", label="display_name", help="what humans call it",
                decides="what the profile shows a reader as this application's name; not checked",
                wrong=NOT_CHECKED_WRONG,
            ),
            FieldSpec(
                id="owner",
                label="owner",
                help="who is accountable for this application, not this adoption",
                decides="who the framework holds accountable for this profile, and who reviewers look to",
                wrong="accountability lands on nobody, and the checker cannot tell",
            ),
        ),
    )


def stack_plan(repo: Path) -> SectionPlan:
    """`builds_user_interface` is asked outright and never set from detection.
    `core/CONFORMANCE_LEVELS.md` is explicit about why: "a reviewer can falsify a wrong answer in
    seconds" - which is only a meaningful check if a human, not a heuristic, gave the answer being
    checked. Detection fills the language box and nothing else."""
    languages = detect.detect_languages(repo)
    ui_hint = detect.detect_ui_hint(repo)

    notes = []
    if languages:
        notes.append(f"Detected: {', '.join(languages)}")
    if ui_hint:
        notes.append(f"Detected a UI-framework dependency: {ui_hint} - confirm it below yourself")

    return SectionPlan(
        name="stack",
        title="Stack",
        notes=tuple(notes),
        fields=(
            FieldSpec(
                id="language",
                label="Language(s) / framework",
                default=", ".join(languages) if languages else "",
                help="shown above if detected - confirm or correct it",
                decides="what the profile records for its reader; the checker never reads it",
                wrong=NOT_CHECKED_WRONG,
            ),
            FieldSpec(
                id="builds_user_interface",
                label="Does this repository build a user interface?",
                kind="bool",
                help=(
                    "Decides whether the four interface gates are a floor at standard and full. "
                    "Not descriptive - answer for what this repository actually does, not what it "
                    "might do later."
                ),
                validate="",
                decides="whether the four interface gates are required at standard and full",
                wrong="yes on a repository with no interface adds four gates it can never satisfy; no on one with screens leaves them unguarded",
            ),
        ),
    )


def risk_plan() -> SectionPlan:
    return SectionPlan(
        name="risk",
        title="Risk & materiality",
        fields=(
            FieldSpec(
                id="risk_profile",
                label="Risk profile",
                kind="textarea",
                help="intended use, uncertainty, materiality - a sentence or two, in your own words",
                decides="the profile's own statement of what could go wrong and for whom",
                wrong="a vague sentence reads as a considered one; \"Not stated at adoption\" is the honest blank",
            ),
            FieldSpec(
                id="materiality_definition",
                label="Materiality definition",
                kind="textarea",
                help="which outputs or decisions are material - what would make a wrong one matter",
                decides="what the profile counts as material, which is what every material-output rule in the standard refers back to",
                wrong="too narrow and material outputs escape the controls; too wide and everything is material and nothing is",
            ),
            # `ACT-032`. Two plain questions about the adopter's world, asked BEFORE the level, so
            # the level becomes answerable by someone who has not yet learned what a "conformance
            # level" is. They are not new criteria: `catalogue.LEVEL_BLURBS` already defines each
            # level exactly this way - *"anything whose output nobody outside the team relies on"*,
            # *"anything a colleague or a customer depends on"*, *"material quantitative or AI
            # output that other systems consume as fact"*. This asks the framework's own
            # definitions instead of asking the adopter to map themselves onto its vocabulary.
            FieldSpec(
                id="relied_on_outside_team",
                label="Does anyone outside your team rely on what this produces?",
                kind="bool",
                help=(
                    "A colleague in another team, a customer, or another system reading your "
                    "output. If it is a proof of concept or internal tooling nobody else depends "
                    "on, the answer is no."
                ),
                validate="",
                decides="the level this tool recommends: standard exists for output someone outside the team depends on",
                wrong="a recommendation pointing at the wrong level; the level itself is still yours to choose",
            ),
            FieldSpec(
                id="material_quantitative_output",
                label="Does it produce numbers or AI output that others treat as fact?",
                kind="bool",
                help=(
                    "Figures, model outputs or AI-generated results that another system or another "
                    "team consumes without re-deriving them. Not: logs, dashboards of your own "
                    "activity, or output a human always checks before it is used."
                ),
                validate="",
                decides="the level this tool recommends: full exists for numbers or AI output that others treat as fact",
                wrong="a recommendation pointing at the wrong level; the level itself is still yours to choose",
            ),
            FieldSpec(
                id="data_classification",
                label="Data classification",
                kind="choice",
                # Short enough to read beside the label column at 80 columns (`F67`).
                choices=(
                    ("public", "public - no restriction"),
                    ("internal", "internal - not for external release"),
                    ("confidential", "confidential - within the organisation"),
                    ("restricted", "restricted - the strictest tier"),
                ),
                help="the most sensitive data this repository handles, in the organisation's own tiers",
                decides="what the profile states about the data here; the repository classification is proposed from it",
                wrong="a profile that understates or overstates the data's sensitivity to whoever relies on it",
            ),
        ),
    )


# ---------------------------------------------------------------------------------------------
# Section 4 — conformance level
# ---------------------------------------------------------------------------------------------


def detected_signals(repo: Path) -> tuple[list[str], list[str]]:
    """(present, absent) - shown on the level screen so the honest cost of a level is visible
    before it is chosen, never to choose one. `DR-35`: the maintainer's own instruction was that
    the three levels stay neutral options because they are repository-dependent."""
    present: list[str] = []
    absent: list[str] = []

    ci_workflows = detect.detect_ci_workflows(repo)
    if ci_workflows:
        # Named, but not all of them: a repository with a dozen workflows would push the level
        # options off the screen, and the point of this line is the fact that CI exists, not an
        # inventory of it.
        shown = ci_workflows[0]
        extra = len(ci_workflows) - 1
        present.append(
            f"a CI workflow ({shown}" + (f" and {extra} more)" if extra else ")")
        )
    else:
        absent.append("a CI workflow")

    decisions = detect.detect_decisions_folder(repo)
    if decisions:
        present.append(f"a decisions/ADR folder ({decisions})")
    else:
        absent.append("a decisions/ADR folder")

    changelog = detect.detect_changelog(repo)
    if changelog:
        present.append(f"a CHANGELOG ({changelog})")
    else:
        absent.append("a CHANGELOG")

    return present, absent


def level_choices(builds_ui: bool) -> tuple[tuple[str, str], ...]:
    """(value, label) per level, with counts computed from the catalogue rather than written down
    - the same derivation `catalogue.level_summary` already does for the old flow."""
    out = []
    for level in ("essential", "standard", "full"):
        summary = catalogue.level_summary(level, builds_ui)
        out.append(
            (
                level,
                f"{level} - {summary['gate_count']} gate(s), {summary['control_count']} control(s). "
                f"{summary['blurb']}",
            )
        )
    return tuple(out)


def level_controls(level: str) -> tuple[str, ...]:
    """The concrete controls a level names - the mockup's amber meta line on the highlighted
    option, which is the thing that makes the choice legible rather than a number."""
    return tuple(sorted(catalogue.CONFORMANCE_LEVELS[level]))


def recommended_level(risk: dict) -> tuple[str, str]:
    """The level the adopter's own answers point at, and the sentence explaining why.

    **This is a recommendation and never an answer.** `core/CONFORMANCE_LEVELS.md:214-216` is
    explicit: *"The level is a human decision recorded in the adoption decision record. It is not
    derived automatically from the stack, the repository size, or the data classification, because
    materiality depends on intended use and reliance, which only the application owner can judge."*
    So this is shown beside the choice with its reasoning, the choice is still made, and nothing is
    pre-selected on the adopter's behalf.

    The mapping is not a heuristic of ours - it is `catalogue.LEVEL_BLURBS` read back as questions.
    """
    outside = bool(risk.get("relied_on_outside_team"))
    material = bool(risk.get("material_quantitative_output"))
    if material:
        return "full", (
            "you said this produces numbers or AI output that others treat as fact, which is what "
            "full exists for"
        )
    if outside:
        return "standard", "you said someone outside your team relies on what this produces"
    return "essential", (
        "you said nobody outside your team relies on this output, and that it produces nothing "
        "others treat as fact"
    )


def level_plan(
    repo: Path,
    *,
    builds_ui: bool,
    mode: str,
    recap: tuple[str, ...] = (),
    risk: dict | None = None,
) -> SectionPlan:
    present, absent = detected_signals(repo)
    notes = []
    if risk:
        level, because = recommended_level(risk)
        # Two rows at 80 columns, not four: `F67` found the recap and this note filling the
        # frame with the three options below the fold.
        notes.append(
            f"From your answers, {level} looks right: {because}. "
            "A recommendation, not a decision; the choice is yours."
        )
    if present:
        notes.append(f"You appear to have: {'; '.join(present)}.")
    if absent:
        notes.append(f"You don't yet have: {'; '.join(absent)}.")

    return SectionPlan(
        name="level",
        title="Conformance level",
        intro=explanations.LEVEL_CHOICE[mode],
        recap=recap,
        notes=tuple(notes),
        fields=(
            FieldSpec(
                id="conformance_level",
                label="Conformance level - a floor, not a ceiling; you may require more than the level asks",
                kind="choice",
                choices=level_choices(builds_ui),
                help="how strict this repository's own rules are; the counts beside each level are computed from the catalogue",
                decides="the floor: which gates and controls the checker requires of this repository from now on",
                wrong="too low leaves what others rely on unguarded; too high fails on gates the repository cannot yet meet",
            ),
        ),
    )


# ---------------------------------------------------------------------------------------------
# Section 5 — controls
# ---------------------------------------------------------------------------------------------


def _first_line(text: str, limit: int = 72) -> str:
    """One line of an explanation, for a tick-box label that has to fit on a row.

    The full explanation stays available as the field's help; this is the label beside the box, and
    a label that wraps to four lines makes a list of nine unreadable.
    """
    line = text.strip().split("\n", 1)[0].strip()
    if len(line) <= limit:
        return line
    return line[: limit - 1].rsplit(" ", 1)[0] + "…"


def _implementation_reference_field(
    control_id: str, *, at_floor: bool, found: discover.Discovered
) -> FieldSpec | None:
    """Pattern A/B/C controls each name where they are implemented, and the three patterns want
    different things named - a file, a CI step, a register directory (`DR-25`, `DR-26`). Pattern D
    controls name nothing."""
    labels = {
        **{c: ("File that implements", "a lock file, a findings register - whatever this control is actually checked against") for c in catalogue.PATTERN_A_CONTROLS},
        **{c: ("CI step name that implements", "the exact step name in your workflow file - matched by name, not by job") for c in catalogue.PATTERN_B_CONTROLS},
        **{c: ("Register directory for", "a directory of records validating against this control's schema - empty is a valid, honest start") for c in catalogue.PATTERN_C_CONTROLS},
    }
    if control_id not in labels:
        return None
    prefix, help_text = labels[control_id]
    decides = {
        **{c: PATTERN_A_DECIDES for c in catalogue.PATTERN_A_CONTROLS},
        **{c: PATTERN_B_DECIDES for c in catalogue.PATTERN_B_CONTROLS},
        **{c: PATTERN_C_DECIDES for c in catalogue.PATTERN_C_CONTROLS},
    }[control_id]
    # Each pattern names a different kind of thing, and each is discoverable. The CI step in
    # particular is why this packet exists: "no example for CI step name... not sure how to proceed
    # on that one" is unanswerable from a canned example and trivial from the adopter's own
    # workflow files.
    # `DR-48`: what the checker will ask of the value is asked at the field - a tracked path for
    # patterns A and C (`SP051`, `SP055`), a step name that exists for pattern B (`SP053`).
    if control_id in catalogue.PATTERN_A_CONTROLS:
        # A lock file for `dependency_lock`; for `assurance_findings`, a document whose name says
        # so. `lock_files or artefacts` offered `requirements.txt` as a findings register and, on
        # a repository with nothing else, whatever file it held first - the `F40` shape.
        if control_id == "dependency_lock":
            candidates = found.lock_files
            context = "lock"
        else:
            # `F88` / `DR-54` (2): every artefact, the name matches first - as the gates do -
            # rather than only the matches, which left a register named otherwise unofferable.
            hit = [a for a in found.artefacts if any(w in a.lower() for w in FINDINGS_WORDS)]
            candidates = tuple(hit + [a for a in found.artefacts if a not in hit])
            context = "artefact"
        validate = "tracked_path"
    elif control_id in catalogue.PATTERN_B_CONTROLS:
        candidates = found.ci_steps
        validate = "ci_step"
        context = "step"
    else:
        candidates = found.register_dirs
        validate = "tracked_path"
        context = "register"
    return _from_candidates(
        id=f"{control_id}.implementation_reference",
        label=f"{prefix} {control_id}",
        help=help_text,
        candidates=candidates,
        depends_on=None if at_floor else ("above_floor", (control_id,)),
        validate=validate,
        context=context,
        decides=decides,
        wrong=CONTROL_WRONG,
        seed=found.free_control_seeds.get(control_id, ""),
    )


def controls_plan(
    *, level: str, mode: str, found: discover.Discovered | None = None, scanner: str = discover.DEFAULT_SCANNER
) -> SectionPlan:
    """All nine controls are shown, not just the level's floor.

    The old flow asked the floor's controls and then offered a "declare another?" loop, which is a
    poor fit for a screen and a worse fit for a plan - an unbounded loop has no field ids to join
    against. Showing all nine, with the floor's own pre-marked and locked, keeps the capability a
    level being "a floor, not a ceiling" requires while making the section a fixed, describable
    shape. Nothing above the floor is declared unless a human turns it on.
    """
    found = found or discover.Discovered()
    required = catalogue.CONFORMANCE_LEVELS[level]
    fields: list[FieldSpec] = []

    for control_id in BASELINE_CONTROL_IDS:
        fields.append(
            FieldSpec(
                id=f"{control_id}.rationale",
                label=f"Why does {control_id} apply here?",
                kind="textarea",
                help=f"{explanations.explain(control_id, mode)}\n\n{TEMPLATE_PLACEHOLDER_HELP}",
                default=example_answers.rationale_example(control_id),
                decides=RATIONALE_DECIDES,
                wrong=RATIONALE_WRONG,
            )
        )

    fields.append(
        FieldSpec(
            id="scanner.name",
            label="Secret scanner",
            default=scanner,
            help="the tool that scans for secrets before they're committed",
            decides="the word the checker looks for in the workflow file, and requires a step to run (SP046)",
            wrong="the checker looks for the wrong word and reports the scanner absent",
        )
    )
    # `F83` / `DR-51` (5): the candidates are the workflows where a step RUNS the scanner, and the
    # field refuses any other file with the checker's own words.
    fields.append(
        _from_candidates(
            id="scanner.wired_in",
            label="Scanner workflow file",
            help=f"the workflow where a step runs {scanner}; that step must be able to fail the build",
            candidates=found.scanner_workflows,
            validate=f"scanner_workflow:{scanner}",
            context=f"scanner:{scanner}",
            decides=SCANNER_WIRED_DECIDES,
            wrong=SCANNER_WIRED_WRONG,
        )
    )

    # `ACT-032`: ONE opt-in, not one tick box per control. A level is a floor, and choosing it has
    # already declined everything above it - so asking the adopter to decline each one again, in
    # turn, is asking them to restate an answer they have given. For a solo maintainer at
    # `essential` that was eight separate questions out of fifteen in this section, and
    # `defaults.propose_controls` computed `False` for every one of them without asking at all.
    #
    # Above the floor stays a real choice, because a level is a floor and not a ceiling; it is now
    # a single list to tick through rather than a sequence of screens to say no to.
    above_floor = [c for c in sorted(catalogue.CONFORMANCE_LEVELS["full"]) if c not in required]
    if above_floor:
        fields.append(
            FieldSpec(
                id="above_floor",
                label=f"Declare any control beyond the {level} floor?",
                kind="multiselect",
                help=(
                    f"{level} does not require these. Tick any you want this repository held to "
                    "anyway - a level is a floor, not a ceiling. Leaving them all unticked is a "
                    "complete answer."
                ),
                # `F67`: a row is the id and a short cue that fits 60 columns; the full explanation
                # of the highlighted row is shown beside the list (`choice_help`).
                choices=tuple((c, f"{c} - {explanations.CUES[c]}") for c in above_floor),
                choice_help=tuple((c, explanations.explain(c, mode)) for c in above_floor),
                default="",
                validate="",
                decides="which controls beyond the floor this repository is held to; each ticked one asks for its rationale and reference and is then checked",
                wrong="a ticked control with nothing behind it fails the checker; an unticked one is simply not claimed",
            )
        )

    for control_id in sorted(catalogue.CONFORMANCE_LEVELS["full"]):
        at_floor = control_id in required
        fields.append(
            FieldSpec(
                id=f"{control_id}.rationale",
                label=f"Why does {control_id} apply here?",
                kind="textarea",
                help=(
                    f"{explanations.explain(control_id, mode)}\n\n{TEMPLATE_PLACEHOLDER_HELP}"
                    if at_floor
                    else TEMPLATE_PLACEHOLDER_HELP
                ),
                default=example_answers.rationale_example(control_id),
                depends_on=None if at_floor else ("above_floor", (control_id,)),
                decides=RATIONALE_DECIDES,
                wrong=RATIONALE_WRONG,
            )
        )
        reference = _implementation_reference_field(control_id, at_floor=at_floor, found=found)
        if reference is not None:
            fields.append(reference)

    return SectionPlan(
        name="controls",
        title=f"Controls, floor: {level}",
        intro=(
            "Three baseline controls apply at every level and cannot be excluded, deferred or "
            "omitted - but why each applies here is yours to state, not ours to assume. Everything "
            f"the {level} floor requires is already included; anything beyond it is one optional "
            "list at the end, because a level is a floor and never a ceiling."
        ),
        fields=tuple(fields),
    )


def locked_controls(level: str) -> set[str]:
    """Controls the level requires - shown as required, not offered as a choice, exactly as a
    level-mandatory gate is. `tui/` reads this to decide what to lock."""
    return set(catalogue.CONFORMANCE_LEVELS[level])


# ---------------------------------------------------------------------------------------------
# Section 6 — prerequisite gates
# ---------------------------------------------------------------------------------------------

def _from_candidates(
    *, id: str, label: str, help: str, candidates: tuple[str, ...], depends_on=None,
    validate: str = "nonempty", context: str = "", decides: str = "", wrong: str = "", seed: str = "",
) -> FieldSpec:
    """A field answered by picking, when there is anything to pick from.

    `DR-38`'s rule: never offer something that isn't there. So when discovery found nothing - no
    git, an unusual layout - this degrades to the plain text field it always was, rather than
    presenting an empty dropdown that cannot be answered. `DR-54` (1): where a seed's path is
    free, the first row offers to create it, and the field is a dropdown even with nothing else
    to pick from - "create it" is something that is there.
    """
    # `F75`: the cap is here, per field, after the caller has ranked for the field at hand -
    # never on the scan.
    shown = tuple(candidates)[: discover.SHOWN]
    choices = tuple((c, c) for c in shown)
    if seed:
        # Short enough for the dropdown's row at 80 columns, path included.
        choices = ((seed, f"create it: {seed}"),) + choices
        help = (
            f"{help}. The first row creates one for you, from a complete and true seed" if shown
            else f"nothing in this repository fits; the first row creates {seed} for you, from a complete and true seed"
        )
    return FieldSpec(
        id=id,
        label=label,
        kind="select" if choices else "text",
        help=help,
        choices=choices,
        suggestions=shown,
        validate=validate,
        depends_on=depends_on,
        context=context,
        decides=decides,
        wrong=wrong,
        seed=seed,
    )


_GATE_STATUS_CHOICES = (
    ("required", "required - a precondition must exist before the gated paths change"),
    ("deferred", "deferred - not yet, with an owner and a date"),
    ("not_applicable", "not applicable - with a stated reason"),
)


def _gate_fields(
    gate_id: str, *, mandatory: bool, auto_status: str, found: discover.Discovered
) -> tuple[FieldSpec, ...]:
    fields: list[FieldSpec] = []

    if not mandatory and not auto_status:
        fields.append(
            FieldSpec(
                id="status",
                label=gate_id,
                kind="choice",
                choices=_GATE_STATUS_CHOICES,
                # Short on purpose: at 80x24 this sits under three radio rows and a three-row
                # gate description, and a ten-row help pushed itself below the fold.
                help="r, d or n on this row; the three meanings are below",
                decides=(
                    "whether the checker audits this gate. required: audited from effective_from; "
                    "deferred: not until revisit_by, failing after it; not applicable: never, with the reason written"
                ),
                wrong="required without the practice fails every gated commit; not applicable where it applies hides the risk",
            )
        )

    required_when = ("required",) if not mandatory else ("required",)
    fields += [
        # `SP032` requires this artefact to exist, be non-empty and carry no placeholder - so a
        # value typed from memory is a profile that fails its own checker. Picking from what is
        # actually in the repository removes that whole class of answer.
        # `F44`. Ranking orders; it never establishes that anything is right. `rank_for_gate`
        # returns matches first and then everything else, so a gate nothing matches offered twelve
        # unrelated files under "Choose precondition artefact (12 found)" - a list that says one of
        # these is the answer. `F40` fixed the same mistake in the proposal; this is the offer.
        # Nothing is hidden - `DR-38`'s rule stands, the adopter still chooses from the whole list -
        # but the help says whether any of it actually matched this gate.
        _from_candidates(
            id="artefact",
            label="Precondition artefact",
            help=(
                "what must exist before the gated paths may change"
                if discover.matched_for_gate(found.artefacts, gate_id)
                else "nothing in this repository matches this gate"
                + (" - these are simply the files found here" if found.artefacts else "")
            ),
            candidates=tuple(discover.rank_for_gate(found.artefacts, gate_id)),
            depends_on=None if mandatory else ("status", required_when),
            validate="tracked_path",
            context=f"gate:{gate_id}",
            decides=ARTEFACT_DECIDES,
            wrong=ARTEFACT_WRONG,
            seed=found.free_seeds.get(gate_id, ""),
        ),
        # `F51`: **`effective_from` is asked, and this is the one of the four that came back.**
        # `org/RELEASE_PLAN.md` names it: *"what `effective_from` should read ... is a human
        # decision the wizard elicits and records verbatim, never one it makes on the human's
        # behalf."* `ACT-032` derived it as a consequence rather than a judgement and did not amend
        # the rule; a cross-provider reviewer found the contradiction.
        #
        # The safety argument is the stronger one. `SP033` refuses a future value and `SP034`
        # refuses moving one forward, so a human's answer can only ever WIDEN or equal the audit
        # window. Deriving "now" silently picked the narrowest value the rules permit, on the field
        # that decides how much history the gate audit examines.
        FieldSpec(
            id="effective_from",
            label="Effective from",
            help=(
                "YYYY-MM-DD, or a full instant. History before this is out of scope for the audit, "
                "so an earlier value examines MORE of your history, never less"
            ),
            default=_dt.date.today().isoformat(),
            validate="effective_from",
            depends_on=None if mandatory else ("status", required_when),
            decides="how far back the audit looks: commits before this date are out of scope (SP033 to SP035)",
            wrong="later than the artefact hides history the gate should have covered; earlier than it fails on history the artefact did not precede",
        ),
        # `ACT-032`: `precondition_description`, `gated_description` and `enforcement` remain
        # DERIVED in `sections.build_gate`. Each is
        # a consequence of an answer already given, not a judgement of its own:
        #
        #   - both descriptions restate what the gate is and which paths it covers. The framework
        #     already writes the first, in `catalogue.GATE_CATALOGUE`, and uses that same sentence
        #     to describe the gate on this very screen - so an adopter was being asked to
        #     paraphrase text sitting directly above the box;
        #   - `effective_from` is today; a gate cannot bind before it is declared, and the field
        #     was already defaulted to today with no honest reason to choose otherwise;
        #   - `enforcement` is a fixed schema enum, and `history_audit` + `review` are exactly the
        #     two that need no tooling an adopter may not have. It was already the field's default
        #     AND what `defaults.py` computed, so it was asked without ever being a live question.
        #
        # This is the borderline one: HOW a gate is enforced is a real decision for a repository
        # with CI. It is derived rather than asked because the safe pair is the honest starting
        # point, and the written profile is a file the adopter edits afterwards - which is what the
        # run's closing message already tells them to do.
        # A pathspec, not a path: `src/**` never has to exist as a file, so this stays typeable
        # and offers the repository's real top-level directories as inline completions instead of
        # constraining to them.
        FieldSpec(
            id="paths",
            label="Gated paths",
            help="a git pathspec, e.g. src/** - what may not proceed until the artefact exists",
            suggestions=found.paths,
            depends_on=None if mandatory else ("status", required_when),
            decides="which changes the gate applies to: every commit touching these paths after effective_from must come after the artefact",
            wrong="too narrow and the gate guards nothing; too wide and unrelated commits fail the audit",
        ),
    ]

    if mandatory:
        return tuple(fields)

    if auto_status == "not_applicable":
        # `builds_user_interface: false`, given earlier, already settles the status. The RATIONALE
        # is still asked - `F32`/`ACT-022` found this branch writing a fixed string with no prompt
        # call at all, and the fix was to ask for it with the old text offered as a default.
        return (
            FieldSpec(
                id="rationale",
                label=f"Rationale for {gate_id} being not applicable",
                kind="textarea",
                default="This repository has no user interface.",
                help="why this interface gate does not apply; the answer above already settled that it does not",
                decides="why the profile says this gate does not apply; read by reviewers, never by the checker",
                wrong=RATIONALE_WRONG,
            ),
        )

    fields += [
        FieldSpec(
            id="owner",
            label="Owner",
            help="who owns the deferral - a named human",
            depends_on=("status", ("deferred",)),
            decides="who the deferral is filed under, and who is asked when revisit_by arrives",
            wrong="a deferral nobody owns is never revisited",
        ),
        FieldSpec(
            id="revisit_by",
            label="Revisit by",
            help="YYYY-MM-DD. The checker fails once this date passes",
            validate="revisit_by",
            depends_on=("status", ("deferred",)),
            decides="the date the checker fails this gate unless it has been decided by then (SP054)",
            wrong="too far and the deferral is a permanent exemption; too near and the check fails before the work is done",
        ),
        FieldSpec(
            id="rationale",
            label="Why this status",
            kind="textarea",
            help="why this gate is deferred or does not apply here, in your own words",
            default=example_answers.rationale_example(gate_id),
            depends_on=("status", ("deferred", "not_applicable")),
            decides="why the profile says this gate is deferred or does not apply; read by reviewers, never by the checker",
            wrong=RATIONALE_WRONG,
        ),
    ]
    return tuple(fields)


def gate_plan(
    *, level: str, builds_ui: bool, mode: str, found: discover.Discovered | None = None
) -> tuple[GateSpec, ...]:
    """The gates this run actually asks about, in `core/PREREQUISITE_GATES.md`'s catalogue order.

    Reproduces `sections.ask_gates`'s applicability rules exactly, now as data:

    - the level's floor is `required` and not a free choice;
    - at `standard`/`full` with a user interface, the four `DESIGN_GATES` join that floor;
    - at `standard`/`full` without one, those four are settled `not_applicable` and only their
      rationale is asked;
    - at `essential`, only `work_registration` is declared at all, because the checker reads
      nothing else at that level.
    """
    found = found or discover.Discovered()
    mandatory = set(catalogue.LEVEL_REQUIRED_GATES[level])
    full_declaration = level in catalogue.LEVELS_REQUIRING_FULL_DECLARATION
    if builds_ui and full_declaration:
        mandatory |= catalogue.DESIGN_GATES

    if not full_declaration:
        return (
            GateSpec(
                id="work_registration",
                section="Work and decisions",
                explanation=explanations.explain("work_registration", mode),
                mandatory=True,
                fields=_gate_fields("work_registration", mandatory=True, auto_status="", found=found),
            ),
        )

    specs: list[GateSpec] = []
    for section_name, gate_ids in catalogue.sectioned_gates():
        for gate_id in gate_ids:
            is_design_gate = gate_id in catalogue.DESIGN_GATES
            auto_status = "not_applicable" if (is_design_gate and not builds_ui) else ""
            is_mandatory = gate_id in mandatory
            specs.append(
                GateSpec(
                    id=gate_id,
                    section=section_name,
                    explanation=explanations.explain(gate_id, mode),
                    mandatory=is_mandatory,
                    auto_status=auto_status,
                    fields=_gate_fields(
                        gate_id, mandatory=is_mandatory, auto_status=auto_status, found=found
                    ),
                )
            )
    return tuple(specs)


def gates_plan(
    *, level: str, builds_ui: bool, mode: str, found: discover.Discovered | None = None
) -> SectionPlan:
    """The gate catalogue as a `SectionPlan`, so the screen↔plan join test has one rule for every
    section including this one. Its `fields` are every gate's fields, prefixed by gate id."""
    specs = gate_plan(level=level, builds_ui=builds_ui, mode=mode, found=found)
    fields: list[FieldSpec] = []
    for spec in specs:
        for f in spec.fields:
            fields.append(
                FieldSpec(
                    id=f"{spec.id}.{f.id}",
                    label=f.label,
                    kind=f.kind,
                    help=f.help,
                    default=f.default,
                    choices=f.choices,
                    validate=f.validate,
                    suggestions=f.suggestions,
                    decides=f.decides,
                    wrong=f.wrong,
                    context=f.context,
                    choice_help=f.choice_help,
                    seed=f.seed,
                    depends_on=(
                        (f"{spec.id}.{f.depends_on[0]}", f.depends_on[1])
                        if f.depends_on is not None
                        else None
                    ),
                )
            )

    total = len(catalogue.GATE_CATALOGUE)
    intro = (
        f"At {level}, only work_registration must be declared. The other {total - 1} gates are "
        "not read by the checker at this level and are skipped."
        if level not in catalogue.LEVELS_REQUIRING_FULL_DECLARATION
        else f"All {total} gates must be decided one way or the other at {level}. "
        "not applicable is a perfectly good answer; silence is not."
    )

    return SectionPlan(name="gates", title="Prerequisite gates", intro=intro, fields=tuple(fields))


# ---------------------------------------------------------------------------------------------
# Wrap-up — adoption identity, roles, release route
# ---------------------------------------------------------------------------------------------


def adoption_plan(*, owner: str) -> SectionPlan:
    return SectionPlan(
        name="adoption",
        title="A few closing facts",
        fields=(
            FieldSpec(
                id="review_by",
                label="Review by",
                default=(_dt.date.today() + _dt.timedelta(days=180)).isoformat(),
                help="180 days is the suggested interval; the checker fails once this date passes",
                validate="review_by",
                decides="the date the checker fails this profile unless it has been reviewed by then (SP025), at most 400 days out (SP026)",
                wrong="a profile that fails on a date nobody planned for, or one that is never reviewed",
            ),
            FieldSpec(
                id="framework_maintainer",
                label="Framework maintainer",
                default=owner,
                help="the change authority for the standard in this repository - often the same as owner",
                decides="who may upgrade or change the standard's installation here",
                wrong="upgrades with nobody accountable for them",
            ),
            FieldSpec(
                id="repository_classification", label="Repository classification",
                help="how this repository is classified in the organisation's own terms; proposed from the data classification",
                decides="what the profile states about the repository; the checker never reads it",
                wrong=NOT_CHECKED_WRONG,
            ),
            FieldSpec(
                id="decision_record_id",
                label="Adoption decision record ID",
                help="if none exists yet, this is the moment to name one - it does not need to be written yet",
                decides="the record the profile cites for this adoption; the checker requires the id, not the record",
                wrong="a citation to nothing",
            ),
            FieldSpec(
                id="adoption_status",
                label="Adoption status",
                kind="choice",
                choices=(
                    ("in_progress", "in_progress"),
                    ("complete", "complete"),
                    ("blocked", "blocked"),
                    ("deferred", "deferred"),
                ),
                help="where this adoption stands today; blocked and deferred ask why",
                decides="what the profile says about this adoption's state; nothing else follows from it",
                wrong="complete before the checker passes is a claim the checker contradicts on its next run",
            ),
            FieldSpec(
                id="status_rationale",
                label="Why is adoption blocked/deferred?",
                kind="textarea",
                depends_on=("adoption_status", ("blocked", "deferred")),
                help="what stands in the way, in your own words",
                decides="why the profile says adoption is blocked or deferred; read by reviewers",
                wrong="a state with no stated reason",
            ),
            FieldSpec(
                id="needs_validator",
                label="Does independent (Level 3) review apply to this adoption?",
                kind="bool",
                validate="",
                help="whether someone independent of the team validates this adoption",
                decides="whether an independent validator is named on the profile; the checker never reads it",
                wrong="a named validator who never validated is a false claim on the record",
            ),
            FieldSpec(
                id="independent_validator",
                label="Independent validator",
                depends_on=("needs_validator", (True,)),
                help="who validates independently - a named human or body",
                decides="who the profile names as the independent validator; not checked",
                wrong="a named validator who never validated is a false claim on the record",
            ),
        ),
    )


def wrap_plan() -> SectionPlan:
    return SectionPlan(
        name="wrap",
        title="Roles and release",
        fields=(
            FieldSpec(
                id="human_roles",
                label="Human roles",
                kind="textarea",
                help='e.g. "Maintainer - Jane Doe. Sole change authority."',
                validate="",
                decides="the roles the profile records for its reader; the checker never reads them",
                wrong=NOT_CHECKED_WRONG,
            ),
            FieldSpec(
                id="release_route",
                label="Release route",
                kind="textarea",
                help="human and platform release controls, in your own words",
                decides=RELEASE_ROUTE_DECIDES,
                wrong=RELEASE_ROUTE_WRONG,
            ),
        ),
    )


# ---------------------------------------------------------------------------------------------
# The whole run
# ---------------------------------------------------------------------------------------------

# The profile's sections, in the order the builders and the provenance walk read them. This is
# the shape of the STATE, not of the screens: `DR-47`'s flow presents `decisions`, `level`, the
# gate list and a remainder form (`flow.STAGES`), and scatters their answers into these sections.
SECTION_ORDER = (
    "mode",
    "identity",
    "stack",
    "risk",
    "level",
    "controls",
    "gates",
    "adoption",
    "wrap",
)

# The screens that carry a step number, in order. The remainder form and the scaffold offer are
# conditional and unnumbered (`F45`).
FLOW = ("decisions", "level", "gates")


def recap_lines(state: dict) -> tuple[str, ...]:
    """The mockup's "You told us:" block on the level screen - earlier answers restated so the
    choice is made in front of its own context rather than from memory."""
    lines = []
    risk = state.get("risk") or {}
    stack = state.get("stack") or {}
    if risk.get("materiality_definition"):
        lines.append(str(risk["materiality_definition"]))
    if "builds_user_interface" in stack:
        lines.append(
            "This repository builds a user interface."
            if stack["builds_user_interface"]
            else "No user interface."
        )
    if risk.get("data_classification"):
        lines.append(f"Data classification: {risk['data_classification']}.")
    return tuple(lines)


def section_plan(
    name: str, *, repo: Path, state: dict, found: discover.Discovered | None = None
) -> SectionPlan:
    """The plan for one section, given everything answered before it.

    Sequencing is data-dependent - `level` needs `mode` and `builds_user_interface`, `gates` needs
    `level` - which is exactly why the app cannot be handed a flat list of screens up front and why
    this function takes the accumulated state.
    """
    # One scan serves every section. Callers that run the whole interview pass it in; a caller
    # asking for a single section (a test, a screen in isolation) gets a scan of its own.
    found = found if found is not None else discover.scan(repo)

    mode = (state.get("mode") or {}).get("mode", "simple")
    builds_ui = bool((state.get("stack") or {}).get("builds_user_interface", False))
    level = (state.get("level") or {}).get("conformance_level", "essential")
    owner = (state.get("identity") or {}).get("owner", "")

    if name == "mode":
        # Session state, never written: the register of explanation. `DR-47`'s flow has no
        # screen for it; plain English is the default and the only value the flow sets.
        return SectionPlan(name="mode", title="Explanations", fields=(
            FieldSpec(id="mode", label="register", kind="choice",
                      choices=(("simple", "plain English"), ("advanced", "precise technical terms")),
                      help="which register the explanations use", decides="only the wording of the explanations; never written",
                      wrong="nothing: it is session state"),
        ))
    if name == "identity":
        return identity_plan()
    if name == "stack":
        return stack_plan(repo)
    if name == "risk":
        return risk_plan()
    if name == "level":
        return level_plan(
            repo,
            builds_ui=builds_ui,
            mode=mode,
            recap=recap_lines(state),
            risk=state.get("risk") or {},
        )
    if name == "controls":
        scanner = str((state.get("controls") or {}).get("scanner.name") or discover.DEFAULT_SCANNER)
        return controls_plan(level=level, mode=mode, found=found, scanner=scanner)
    if name == "gates":
        return gates_plan(level=level, builds_ui=builds_ui, mode=mode, found=found)
    if name == "adoption":
        return adoption_plan(owner=owner)
    if name == "wrap":
        return wrap_plan()
    raise KeyError(f"unknown section: {name!r}")
