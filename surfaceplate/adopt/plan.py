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

    def applies(self, answers: dict) -> bool:
        """Whether this field is asked at all, given what has been answered so far in its section."""
        if self.depends_on is None:
            return True
        other_id, wanted = self.depends_on
        return answers.get(other_id) in wanted


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


def mode_plan() -> SectionPlan:
    """Ask about the person, not about the prose.

    This used to ask which register of explanation you wanted, which is a question about the
    tool's output and hard to answer before seeing any. Asking about experience is answerable
    immediately and the wizard derives the register from it - the maintainer's own suggestion after
    finishing a run: *"we should suggest simple or advanced explanations by asking what level of
    experience does the user have."*
    """
    return SectionPlan(
        name="mode",
        title="How much should this explain?",
        intro=(
            "Everything gets a real explanation before you are asked about it. This chooses the "
            "vocabulary those explanations use, and nothing else."
        ),
        fields=(
            FieldSpec(
                id="mode",
                label="Your experience with software delivery and governance",
                kind="choice",
                choices=(
                    (
                        "simple",
                        "standard - explain in plain English, assuming no background in either",
                    ),
                    (
                        "advanced",
                        "advanced - use precise technical terms, and explain this framework's own "
                        "vocabulary where it is unusual",
                    ),
                ),
            ),
        ),
    )


def route_plan(state: dict) -> SectionPlan:
    """The fork: finish quickly from proposed answers, or answer everything yourself.

    Placed after the minimum - identity, stack, risk, level - because none of the proposals are
    possible until the level is known, and because those four are the questions nobody can answer
    on an adopter's behalf.
    """
    level = (state.get("level") or {}).get("conformance_level", "essential")
    summary = catalogue.level_summary(
        level, bool((state.get("stack") or {}).get("builds_user_interface", False))
    )
    return SectionPlan(
        name="route",
        title="How would you like to finish?",
        intro=(
            f"At {level} the rest of this profile is {summary['gate_count']} gate(s) and "
            f"{summary['control_count']} control(s). You can answer them one at a time, or start "
            "from proposed answers and change what you disagree with."
        ),
        notes=(
            "Either way nothing is written until you approve a full review of the profile.",
        ),
        fields=(
            FieldSpec(
                id="route",
                label="How to complete the remaining sections",
                kind="choice",
                choices=(
                    (
                        "defaults",
                        "Set defaults - propose answers from this repository and the worked "
                        "examples, then show me every one before anything is written",
                    ),
                    (
                        "customise",
                        "Customise adoption - ask me each control and each gate in turn",
                    ),
                ),
            ),
        ),
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
            ),
            FieldSpec(id="display_name", label="display_name", help="what humans call it"),
            FieldSpec(
                id="owner",
                label="owner",
                help="who is accountable for this application, not this adoption",
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
            ),
            FieldSpec(
                id="materiality_definition",
                label="Materiality definition",
                kind="textarea",
                help="which outputs or decisions are material - what would make a wrong one matter",
            ),
            FieldSpec(
                id="data_classification",
                label="Data classification",
                kind="choice",
                choices=(
                    ("public", "public - no restriction"),
                    ("internal", "internal - not for external release"),
                    ("confidential", "confidential - restricted within the organisation"),
                    ("restricted", "restricted - the strictest tier this framework recognises"),
                ),
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


def level_plan(repo: Path, *, builds_ui: bool, mode: str, recap: tuple[str, ...] = ()) -> SectionPlan:
    present, absent = detected_signals(repo)
    notes = []
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
            ),
        ),
    )


# ---------------------------------------------------------------------------------------------
# Section 5 — controls
# ---------------------------------------------------------------------------------------------


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
    # Each pattern names a different kind of thing, and each is discoverable. The CI step in
    # particular is why this packet exists: "no example for CI step name... not sure how to proceed
    # on that one" is unanswerable from a canned example and trivial from the adopter's own
    # workflow files.
    if control_id in catalogue.PATTERN_A_CONTROLS:
        candidates = found.lock_files or found.artefacts
    elif control_id in catalogue.PATTERN_B_CONTROLS:
        candidates = found.ci_steps
    else:
        candidates = found.register_dirs
    return _from_candidates(
        id=f"{control_id}.implementation_reference",
        label=f"{prefix} {control_id}",
        help=help_text,
        candidates=candidates,
        depends_on=None if at_floor else (f"{control_id}.declared", (True,)),
    )


def controls_plan(
    *, level: str, mode: str, found: discover.Discovered | None = None
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
            )
        )

    fields.append(
        FieldSpec(
            id="scanner.name",
            label="Secret scanner",
            default="gitleaks",
            help="the tool that scans for secrets before they're committed",
        )
    )
    fields.append(
        _from_candidates(
            id="scanner.wired_in",
            label="Scanner workflow file",
            help="a step naming this scanner must be able to fail the build",
            candidates=tuple(a for a in found.artefacts if "workflow" in a),
        )
    )

    for control_id in sorted(catalogue.CONFORMANCE_LEVELS["full"]):
        at_floor = control_id in required
        if not at_floor:
            # Above the floor, declaring it is a real choice and gets a real question. At the floor
            # it is not a choice at all, so no field is emitted - the same treatment a
            # level-mandatory gate's status gets, for the same reason: offering a control the level
            # requires as a tick box invites producing a profile the checker will reject.
            fields.append(
                FieldSpec(
                    id=f"{control_id}.declared",
                    label=f"{control_id} - above the floor here; declare it?",
                    kind="bool",
                    help=explanations.explain(control_id, mode),
                    validate="",
                )
            )
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
                depends_on=None if at_floor else (f"{control_id}.declared", (True,)),
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
            "omitted - but why each applies here is yours to state, not ours to assume. The rest "
            "are shown with your level's floor already marked; a level is a floor, never a ceiling."
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
    validate: str = "nonempty",
) -> FieldSpec:
    """A field answered by picking, when there is anything to pick from.

    `DR-38`'s rule: never offer something that isn't there. So when discovery found nothing - no
    git, an unusual layout - this degrades to the plain text field it always was, rather than
    presenting an empty dropdown that cannot be answered.
    """
    return FieldSpec(
        id=id,
        label=label,
        kind="select" if candidates else "text",
        help=help,
        choices=tuple((c, c) for c in candidates),
        suggestions=candidates,
        validate=validate,
        depends_on=depends_on,
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
            )
        )

    required_when = ("required",) if not mandatory else ("required",)
    fields += [
        # `SP032` requires this artefact to exist, be non-empty and carry no placeholder - so a
        # value typed from memory is a profile that fails its own checker. Picking from what is
        # actually in the repository removes that whole class of answer.
        _from_candidates(
            id="artefact",
            label="Precondition artefact",
            help="what must exist before the gated paths may change",
            candidates=tuple(discover.rank_for_gate(found.artefacts, gate_id)),
            depends_on=None if mandatory else ("status", required_when),
        ),
        FieldSpec(
            id="precondition_description",
            label="Why it must exist first",
            kind="textarea",
            depends_on=None if mandatory else ("status", required_when),
        ),
        # A pathspec, not a path: `src/**` never has to exist as a file, so this stays typeable
        # and offers the repository's real top-level directories as inline completions instead of
        # constraining to them.
        FieldSpec(
            id="paths",
            label="Gated paths",
            help="a git pathspec, e.g. src/** - what may not proceed until the artefact exists",
            suggestions=found.paths,
            depends_on=None if mandatory else ("status", required_when),
        ),
        FieldSpec(
            id="gated_description",
            label="What it gates",
            kind="textarea",
            depends_on=None if mandatory else ("status", required_when),
        ),
        FieldSpec(
            id="effective_from",
            label="Effective from",
            help="YYYY-MM-DD. History before this date is out of scope for the audit",
            default=_dt.date.today().isoformat(),
            validate="date",
            depends_on=None if mandatory else ("status", required_when),
        ),
        # A fixed schema enum, and it should never have been a comma-separated string: a typo
        # here produced a profile the schema rejects, after the whole interview was answered.
        FieldSpec(
            id="enforcement",
            label="Enforcement",
            kind="multiselect",
            help="how this gate is enforced - pick every one that applies",
            choices=tuple((v, v) for v in validators.ENFORCEMENT_VALUES),
            default="history_audit,review",
            validate="",
            depends_on=None if mandatory else ("status", required_when),
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
            ),
        )

    fields += [
        FieldSpec(
            id="owner",
            label="Owner",
            depends_on=("status", ("deferred",)),
        ),
        FieldSpec(
            id="revisit_by",
            label="Revisit by",
            help="YYYY-MM-DD. The checker fails once this date passes",
            validate="date",
            depends_on=("status", ("deferred",)),
        ),
        FieldSpec(
            id="rationale",
            label="Why this status",
            kind="textarea",
            default=example_answers.rationale_example(gate_id),
            depends_on=("status", ("deferred", "not_applicable")),
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
                validate="date",
            ),
            FieldSpec(
                id="framework_maintainer",
                label="Framework maintainer",
                default=owner,
                help="the change authority for the standard in this repository - often the same as owner",
            ),
            FieldSpec(id="repository_classification", label="Repository classification"),
            FieldSpec(
                id="decision_record_id",
                label="Adoption decision record ID",
                help="if none exists yet, this is the moment to name one - it does not need to be written yet",
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
            ),
            FieldSpec(
                id="status_rationale",
                label="Why is adoption blocked/deferred?",
                kind="textarea",
                depends_on=("adoption_status", ("blocked", "deferred")),
            ),
            FieldSpec(
                id="needs_validator",
                label="Does independent (Level 3) review apply to this adoption?",
                kind="bool",
                validate="",
            ),
            FieldSpec(
                id="independent_validator",
                label="Independent validator",
                depends_on=("needs_validator", (True,)),
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
            ),
            FieldSpec(
                id="release_route",
                label="Release route",
                kind="textarea",
                help="human and platform release controls, in your own words",
            ),
        ),
    )


# ---------------------------------------------------------------------------------------------
# The whole run
# ---------------------------------------------------------------------------------------------

# The minimum first - the four nobody can answer on an adopter's behalf - then the fork, then the
# rest. `route` decides whether `controls` and `gates` are asked or proposed.
SECTION_ORDER = (
    "mode",
    "identity",
    "stack",
    "risk",
    "level",
    "route",
    "controls",
    "gates",
    "adoption",
    "wrap",
)

MINIMUM_SECTIONS = ("mode", "identity", "stack", "risk", "level")


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
        return mode_plan()
    if name == "identity":
        return identity_plan()
    if name == "stack":
        return stack_plan(repo)
    if name == "risk":
        return risk_plan()
    if name == "level":
        return level_plan(repo, builds_ui=builds_ui, mode=mode, recap=recap_lines(state))
    if name == "route":
        return route_plan(state)
    if name == "controls":
        return controls_plan(level=level, mode=mode, found=found)
    if name == "gates":
        return gates_plan(level=level, builds_ui=builds_ui, mode=mode, found=found)
    if name == "adoption":
        return adoption_plan(owner=owner)
    if name == "wrap":
        return wrap_plan()
    raise KeyError(f"unknown section: {name!r}")
