#!/usr/bin/env python3
"""End-to-end tests for `surfaceplate adopt`.

No test framework required; run it directly:

    python tests/test_adopt.py

These exist to make the binding rule checkable, not just stated: `org/RELEASE_PLAN.md` says the
wizard "asks, the human answers, the tool writes" and never selects a level, invents a rationale,
or sets a date.

**Phase 2 split that job across three suites (`DR-36`), because one was never enough.**

- This file drives whole runs through `ScriptedInterview`, which answers the same `plan.SectionPlan`
  the screens render. It raises on a planned field it has no answer for, and `assert_no_unused_keys`
  raises on an answer nothing asked for - the two-sided guarantee `ScriptedPrompt` gave, keyed by
  field rather than by position, so a failure names the field.
- `tests/test_provenance.py` proves the other direction: no string reaches a written profile that no
  answer supplied. That is the half the old suite never had, and the half `F32` walked through.
- `tests/test_adopt_tui.py` joins each screen's rendered field ids against its plan's, which is what
  stops both of the above from being satisfied by a screen that silently drops a field.
"""

from __future__ import annotations

import datetime as _dt
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAYLOAD = ROOT / "surfaceplate"  # the package itself - see surfaceplate/__init__.py

# Unlike test_install_and_check.py, which imports install_standard.py/check_conformance.py as
# flat top-level modules (they have no internal package-relative imports), this suite's target
# code uses real `surfaceplate.xxx` imports throughout. ROOT, not PAYLOAD, must be on sys.path so
# `import surfaceplate` resolves to the real package rather than some other installed copy.
sys.path.insert(0, str(ROOT))

from surfaceplate.adopt import catalogue, plan, sections, wizard  # noqa: E402
from surfaceplate.adopt.interview import Cancelled, ScriptedInterview  # noqa: E402

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


def make_installed_repo(tmp: Path, name: str) -> Path:
    """A real git repo with the standard installed - the precondition `adopt` itself enforces."""
    repo = tmp / name
    repo.mkdir(parents=True)
    for args in (
        ["init", "-q"],
        ["config", "user.email", "harness@example.invalid"],
        ["config", "user.name", "Harness"],
        ["config", "commit.gpgsign", "false"],
    ):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    result = subprocess.run(
        [
            sys.executable,
            str(PAYLOAD / "install_standard.py"),
            "--source", str(PAYLOAD),
            "--target", str(repo),
            "--no-hooks",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"fixture install failed:\n{result.stdout}\n{result.stderr}"
    return repo


# ---------------------------------------------------------------------------------------------
# Fixtures. Keyed by "<section>.<field id>", the same addresses the screens use.
# ---------------------------------------------------------------------------------------------

# Hand-written and hand-verified, deliberately: this is the one fixture that states every answer of
# a whole run explicitly, so a change to what `essential` asks shows up here as a diff rather than
# being absorbed by a generator.
ESSENTIAL_ANSWERS: dict[str, object] = {
    "mode.mode": "simple",
    "identity.application_id": "billing-reconciler",
    "identity.display_name": "Billing Reconciler",
    "identity.owner": "Finance Platform team",
    "stack.language": "Python 3.12",
    "stack.builds_user_interface": False,
    "risk.risk_profile": "Reconciles daily settlement files against the ledger; no external users.",
    "risk.materiality_definition": (
        "A reconciliation result reaching the finance team's own review queue is material."
    ),
    # `ACT-032`: the two world-facing questions the level recommendation reads. This fixture is
    # `essential`, and answers both "no" - which is what `essential` means in the framework's own
    # words: nobody outside the team relies on the output.
    "risk.relied_on_outside_team": False,
    "risk.material_quantitative_output": False,
    "risk.data_classification": "internal",
    "level.conformance_level": "essential",
    "route.route": "customise",  # these fixtures exercise the full flow, not the defaults path
    "controls.agent_work_packets.rationale": "All agent-assisted work is bounded, scoped, and reviewable.",
    "controls.actual_diff_review.rationale": "Material changes are reviewed against their actual diff content.",
    "controls.secret_hygiene.rationale": "Secrets and sensitive data must not enter uncontrolled storage.",
    "controls.scanner.name": "gitleaks",
    "controls.scanner.wired_in": "workflows/secret-scan.yml",
    "controls.dependency_lock.rationale": "Supply-chain exposure exists regardless of output materiality.",
    "controls.dependency_lock.implementation_reference": "requirements.txt",
    # `ACT-032`: one opt-in, ticked empty. This replaced eight separate `<control>.declared`
    # booleans - eight questions asking the adopter to re-decline what choosing the level had
    # already declined.
    "controls.above_floor": [],
    "gates.work_registration.artefact": "docs/DEVELOPMENT_REGISTER.md",
    "gates.work_registration.paths": "src/**",
    # `F51`: `effective_from` is asked again - the binding rule names it as a human decision, and
    # deriving it silently picked the narrowest audit window the rules permit. The two descriptions
    # and `enforcement` remain derived; `assert_no_unused_keys()` keeps this fixture honest, so
    # listing one of those here would fail.
    "gates.work_registration.effective_from": "2026-09-01",
    "adoption.review_by": "2027-02-28",
    "adoption.framework_maintainer": "Finance Platform team",
    "adoption.repository_classification": "internal-service",
    "adoption.decision_record_id": "DR-FIN-001",
    "adoption.adoption_status": "in_progress",
    "adoption.needs_validator": False,
    "wrap.human_roles": "",
    "wrap.release_route": "Merges to main require review; deploys are manual.",
}

# F36 regression: `render.py` hand-built YAML flow sequences by escaping each item as though it were
# its own document, then wrapping brackets around the result by hand - the wrong rules for an item
# inside a flow sequence. A real adopter's `what is this?` broke exactly this way and cost a
# ~20-minute session. These answers carry `?`, `,`, `[`, `]` and a leading `-` through the fields
# that are rendered as flow lists. `enforcement` is left schema-valid: its items are constrained to
# an enum with no special characters in any legal value, so a tricky value there would be rejected
# for being illegal rather than for being badly escaped, testing nothing.
TRICKY_CHARACTER_ANSWERS: dict[str, object] = {
    **ESSENTIAL_ANSWERS,
    "mode.mode": "advanced",
    "controls.scanner.wired_in": "workflows/secret-scan.yml?raw=true",
    "gates.work_registration.artefact": "-docs/DEVELOPMENT_REGISTER.md",
    "gates.work_registration.paths": "src/**, [other]?",
    "risk.materiality_definition": "A wrong result reaching the review queue is material?",
}


# F38 regression: the value that ended a real adoption run. `render._block` refused any newline, so
# pressing Enter in a rationale box produced a failure at the REVIEW screen - after the whole
# interview had been answered. Multi-line prose was always legal in the format (this repository's
# own shipped profiles use folded scalars seventeen times); only the renderer could not place it.
MULTILINE_ANSWERS: dict[str, object] = {
    **ESSENTIAL_ANSWERS,
    "risk.risk_profile": "a\nasd",
    "controls.dependency_lock.rationale": "First line.\n\nA third line after a blank one.",
    "wrap.release_route": "  leading space on the first line\nand a second",
}


def answers_for(repo: Path, *, level: str, builds_ui: bool, mode: str, overrides: dict | None = None) -> dict:
    """Walk the plan the wizard will walk, answering every applicable field.

    A FIXTURE BUILDER, not a correctness oracle: the tests below assert real properties of the
    WRITTEN profile rather than trusting that generating answers this way proves anything. Building
    the `full` set by hand (~160 answers) was tried in Phase 1 and is exactly the error-prone
    busywork this avoids without weakening what is actually checked.
    """
    overrides = overrides or {}
    seeded = {
        "mode.mode": mode,
        "stack.builds_user_interface": builds_ui,
        "level.conformance_level": level,
        "route.route": "customise",
        "risk.data_classification": "internal",
        "adoption.adoption_status": "in_progress",
        "adoption.needs_validator": False,
        "identity.application_id": "payments-orchestrator",
        **overrides,
    }
    answers: dict = {}
    state: dict = {}
    for name in plan.SECTION_ORDER:
        section = plan.section_plan(name, repo=repo, state=state)
        local: dict = {}
        for spec in section.fields:
            if not spec.applies(local):
                continue
            key = f"{name}.{spec.id}"
            if key in seeded:
                value: object = seeded[key]
            elif spec.kind == "bool":
                # Above-the-floor controls default to not declared; the level's own floor is not a
                # field at all, so nothing here can accidentally decline a required control.
                value = True if spec.id.endswith(".declared") and level == "full" else bool(spec.default)
            elif spec.id == "above_floor":
                # `ACT-032`. Sweep every above-floor control ON, so this fixture exercises the
                # branch where ticking one really does ask for its rationale and reference - a
                # sweep that always answered "nothing declared" would never reach that code.
                value = [c for c, _ in spec.choices]
            elif spec.kind == "choice":
                value = spec.choices[0][0]
            elif spec.default:
                value = spec.default
            elif spec.id.endswith("paths"):
                value = "src/**"
            else:
                value = f"answer for {name}.{spec.id}"
            local[spec.id] = value
            answers[key] = value
        state[name] = local
    return answers


def seed_referenced_files(repo: Path) -> None:
    """The artefacts an `essential` fixture names, so the real checker has something to find."""
    (repo / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "DEVELOPMENT_REGISTER.md").write_text("# Register\n", encoding="utf-8")
    (repo / "workflows").mkdir(exist_ok=True)
    (repo / "workflows" / "secret-scan.yml").write_text("name: scan\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# Catalogue and content coverage
# ---------------------------------------------------------------------------------------------


def test_catalogue_sections_sum_to_the_whole_catalogue() -> None:
    total = sum(len(ids) for _, ids in catalogue.sectioned_gates())
    check(
        "catalogue sections sum to the full 19-gate catalogue",
        total == len(catalogue.GATE_CATALOGUE),
        f"sections sum to {total}, GATE_CATALOGUE has {len(catalogue.GATE_CATALOGUE)}",
    )
    check(
        "sections have no duplicate gate IDs",
        len(set(g for _, ids in catalogue.sectioned_gates() for g in ids)) == total,
    )


def test_explanations_cover_every_catalogue_item() -> None:
    """Every item the wizard can ask about has BOTH registers, non-empty. Fails loudly on a gap
    rather than letting a screen fall back to no explanation for whatever was missed."""
    from surfaceplate.adopt import explanations

    expected = (
        set(catalogue.GATE_CATALOGUE)
        | set(catalogue.CONFORMANCE_LEVELS["full"])
        | set(plan.BASELINE_CONTROL_IDS)
    )
    covered = set(explanations.EXPLANATIONS)
    check(
        "explanations.py covers exactly the catalogue's gates, controls, and baseline controls",
        covered == expected,
        f"missing: {expected - covered}; extra: {covered - expected}",
    )
    empty = [
        f"{item}/{mode}"
        for item, registers in explanations.EXPLANATIONS.items()
        for mode in explanations.MODES
        if not registers.get(mode, "").strip()
    ]
    check("every item has a non-empty entry in both registers", not empty, f"empty: {empty}")
    check(
        "LEVEL_CHOICE also carries both registers, non-empty",
        all(explanations.LEVEL_CHOICE.get(m, "").strip() for m in explanations.MODES),
    )


def test_example_answers_cover_every_reachable_rationale_field() -> None:
    """Derives the reachable gate set the same way `plan.gate_plan` decides which gates are a free
    choice, rather than a hand-copied list that could drift from what the wizard asks."""
    from surfaceplate.adopt import example_answers

    reachable_gates = {
        spec.id
        for spec in plan.gate_plan(level="standard", builds_ui=False, mode="simple")
        if not spec.mandatory and not spec.auto_status
    }
    expected = (
        set(plan.BASELINE_CONTROL_IDS) | set(catalogue.CONFORMANCE_LEVELS["full"]) | reachable_gates
    )
    covered = set(example_answers.RATIONALE_EXAMPLES)
    check(
        "example_answers.py covers exactly the reachable rationale fields",
        covered == expected,
        f"missing: {expected - covered}; extra: {covered - expected}",
    )
    blank = [k for k, v in example_answers.RATIONALE_EXAMPLES.items() if not v.strip()]
    check("no example answer is blank", not blank, f"blank: {blank}")


def test_mode_selects_the_register_the_plan_carries() -> None:
    """The mode choice reaches the text a human is shown. `tests/test_adopt_tui.py` proves the
    screen renders what the plan carries; this proves the plan carries the right register."""
    from surfaceplate.adopt import explanations

    simple = plan.controls_plan(level="essential", mode="simple")
    advanced = plan.controls_plan(level="essential", mode="advanced")
    field = "agent_work_packets.rationale"
    simple_help = next(f.help for f in simple.fields if f.id == field)
    advanced_help = next(f.help for f in advanced.fields if f.id == field)
    check(
        "mode=simple carries the plain-English register",
        explanations.explain("agent_work_packets", "simple") in simple_help
        and explanations.explain("agent_work_packets", "advanced") not in simple_help,
    )
    check(
        "mode=advanced carries the technical register",
        explanations.explain("agent_work_packets", "advanced") in advanced_help,
    )


def test_detected_signals_are_stated_both_ways(tmp: Path) -> None:
    """The level screen states what it found AND what it did not - never picking a level."""
    repo = make_installed_repo(tmp, "signals-repo")
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\n", encoding="utf-8")

    section = plan.level_plan(repo, builds_ui=False, mode="simple")
    notes = " ".join(section.notes)
    check(
        "the real CI workflow is named as present",
        "You appear to have" in notes and ".github/workflows/ci.yml" in notes,
        notes,
    )
    check(
        "the absent decisions folder and CHANGELOG are named as absent",
        "You don't yet have" in notes and "decisions/ADR folder" in notes and "CHANGELOG" in notes,
        notes,
    )
    check(
        "the level choice itself stays a neutral list of all three levels",
        [value for value, _ in section.fields[0].choices] == ["essential", "standard", "full"],
    )


# ---------------------------------------------------------------------------------------------
# Whole runs
# ---------------------------------------------------------------------------------------------


def test_essential_end_to_end(tmp: Path) -> tuple[Path, dict]:
    repo = make_installed_repo(tmp, "essential-repo")
    seed_referenced_files(repo)

    interview = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS))
    written = wizard.run(repo, interview)

    try:
        interview.assert_no_unused_keys()
        check("essential run: every scripted answer was used", True)
    except AssertionError as exc:
        check("essential run: every scripted answer was used", False, str(exc))

    check("essential run: wrote governance/application-profile.yaml", written.is_file())

    import yaml

    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    check("written application_id matches what was typed", data.get("application_id") == "billing-reconciler")
    check("written owner matches what was typed", data.get("owner") == "Finance Platform team")
    check("written conformance_level matches what was typed", data.get("conformance_level") == "essential")
    check(
        "essential run declares exactly the one mandatory gate",
        [g["id"] for g in data.get("prerequisites", [])] == ["work_registration"],
        str(data.get("prerequisites")),
    )
    check(
        "the mandatory gate was recorded as required, never anything else",
        data["prerequisites"][0]["status"] == "required",
    )
    check(
        "essential declares exactly its floor control, nothing above it",
        sorted(data["control_decisions"]) == ["dependency_lock"],
        str(sorted(data["control_decisions"])),
    )

    result = subprocess.run(
        [sys.executable, str(repo / ".standards" / "check_conformance.py"), "--repo", str(repo)],
        capture_output=True,
        text=True,
    )
    schema_findings = [
        ln for ln in result.stdout.splitlines()
        if ln.strip().startswith("[SP0") and "SP04" not in ln and "SP05" not in ln
    ]
    check(
        "the real checker raises no schema-shape findings against the written profile",
        not schema_findings,
        "\n".join(schema_findings) or result.stdout[-600:],
    )
    return repo, data


def test_tricky_characters_round_trip(tmp: Path) -> None:
    """F36: an answer containing YAML-flow-sequence-special characters must survive the full flow -
    written, re-parsed, and equal to exactly what was typed. Before the fix this failed at the write
    step itself (`WriteRefused`, nothing on disk), so the first check is that it writes at all."""
    repo = make_installed_repo(tmp, "tricky-characters-repo")
    interview = ScriptedInterview(answers=dict(TRICKY_CHARACTER_ANSWERS))
    try:
        written = wizard.run(repo, interview)
    except wizard.WriteRefused as exc:
        check("tricky-character answers: wizard writes successfully (not refused)", False, exc.detail)
        return
    check("tricky-character answers: wizard writes successfully (not refused)", True)

    import yaml

    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    gate = next(g for g in data["prerequisites"] if g["id"] == "work_registration")
    scanner = data["baseline_controls"]["secret_hygiene"]["scanner"]
    check(
        "tricky artefact round-trips exactly, leading `-` included",
        gate["precondition"]["artefacts"] == ["-docs/DEVELOPMENT_REGISTER.md"],
        str(gate["precondition"]["artefacts"]),
    )
    check(
        "tricky paths round-trips exactly, `,`, `[`, `]` and `?` included",
        gate["gated_activity"]["paths"] == ["src/**, [other]?"],
        str(gate["gated_activity"]["paths"]),
    )
    check(
        "tricky scanner wired_in round-trips exactly, `?` included",
        scanner["wired_in"] == ["workflows/secret-scan.yml?raw=true"],
        str(scanner["wired_in"]),
    )
    check(
        "a `?` in a plain scalar round-trips too",
        data["materiality_definition"].endswith("material?"),
        data["materiality_definition"],
    )


def test_multiline_prose_survives_the_whole_flow(tmp: Path) -> None:
    """F38: a multi-line answer writes as a literal block scalar and round-trips byte-for-byte.

    The awkward cases are deliberate: a blank line inside the prose, and a first line beginning with
    a space (which YAML can only represent with an explicit indentation indicator, `|2-`). Both are
    PyYAML's problem to solve and this test's job to prove it did.
    """
    repo = make_installed_repo(tmp, "multiline-repo")
    interview = ScriptedInterview(answers=dict(MULTILINE_ANSWERS))
    try:
        written = wizard.run(repo, interview)
    except Exception as exc:
        check("multi-line answers: the wizard writes rather than refusing", False, f"{type(exc).__name__}: {exc}")
        return
    check("multi-line answers: the wizard writes rather than refusing", True)

    import yaml

    raw = written.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    check(
        "a two-line answer round-trips exactly",
        data["risk_profile"] == "a\nasd",
        repr(data["risk_profile"]),
    )
    check(
        "a blank line inside prose is preserved",
        data["control_decisions"]["dependency_lock"]["rationale"]
        == "First line.\n\nA third line after a blank one.",
        repr(data["control_decisions"]["dependency_lock"]["rationale"]),
    )
    check(
        "a first line beginning with a space round-trips",
        data["release_route"] == "  leading space on the first line\nand a second",
        repr(data["release_route"]),
    )
    check(
        "and it is written as a readable block scalar, not an escaped one-liner",
        "|-" in raw or "|2-" in raw,
        raw[:200],
    )


def test_the_profile_says_which_controls_are_actually_checked() -> None:
    """`F53`. A cross-provider reviewer read a profile and could not tell.

    `actual_diff_review` (nothing checks it) and `dependency_lock` (`SP051` checks it) rendered as
    structurally identical objects. An adopter reading their own profile is the person most likely
    to over-read it, and that file is what they read.

    **The label is joined to the checker, not restated.** If it were a list in this suite it could
    say "checked" about a control the checker had stopped checking, which is the failure it exists
    to prevent. The second assertion is why the join matters: `VERIFIED_CONTROLS` omitted
    `secret_hygiene` when this was written, so a label derived from it would have called a genuinely
    checked control trusted.
    """
    from surfaceplate.check_conformance import VERIFIED_CONTROLS

    from surfaceplate.adopt import render

    wrong = []
    for control_id in sorted(catalogue.CONFORMANCE_LEVELS["full"] | set(plan.BASELINE_CONTROL_IDS)):
        note = render._assurance_note(control_id)
        says_checked = "checked against this repository" in note
        if says_checked != (control_id in VERIFIED_CONTROLS):
            wrong.append((control_id, note.strip()))
    check(
        "every control's label agrees with the checker's own VERIFIED_CONTROLS",
        not wrong,
        f"labels disagreeing with the checker: {wrong}",
    )
    check(
        "secret_hygiene is labelled checked, because SP046/SP047 check it",
        "checked against this repository" in render._assurance_note("secret_hygiene"),
        render._assurance_note("secret_hygiene").strip(),
    )
    check(
        "and the two the framework admits it cannot check say so",
        all(
            "DECLARED ONLY" in render._assurance_note(c)
            for c in ("agent_work_packets", "actual_diff_review")
        ),
        "an unverified control is not labelled as such",
    )


def test_the_tool_does_not_set_effective_from() -> None:
    """`F51`. The binding rule names this field, and the tool was setting it anyway.

    `org/RELEASE_PLAN.md` does not merely say "never sets a date" - it says *"what `effective_from`
    should read ... is a human decision the wizard elicits and records verbatim, never one it makes
    on the human's behalf."* `ACT-032` derived it as a consequence rather than a judgement, and did
    not amend the rule. A cross-provider reviewer found the contradiction.

    **The safety argument is stronger than the rule.** `SP033` refuses a future value and `SP034`
    refuses moving one forward, so a human's answer can only ever WIDEN or equal the audit window.
    Deriving "now" silently picks the narrowest value the rules permit, on the field that decides how
    much history the gate audit examines.
    """
    found = plan.discover.Discovered(artefacts=("activity/register.md",), paths=("src/**",))
    specs = plan.gate_plan(level="essential", builds_ui=False, mode="simple", found=found)
    spec = next(s for s in specs if s.id == "work_registration")
    asked = {f.id for f in spec.fields}
    check(
        "a required gate asks the human for effective_from",
        "effective_from" in asked,
        f"fields asked: {sorted(asked)}",
    )

    # And nothing is written for it when nobody answered. The old fallback made this impossible to
    # observe: a missing answer and an answer of today produced the same profile.
    built = sections.build_gate(spec, {"artefact": "activity/register.md", "paths": "src/**"})
    check(
        "and with no answer, the tool writes no effective_from of its own",
        "effective_from" not in built or not built["effective_from"],
        f"the tool supplied {built.get('effective_from')!r} on the human's behalf",
    )
    answered = sections.build_gate(
        spec,
        {"artefact": "activity/register.md", "paths": "src/**", "effective_from": "2026-08-31"},
    )
    check(
        "while a supplied answer is recorded verbatim",
        answered["effective_from"] == "2026-08-31",
        str(answered.get("effective_from")),
    )


def test_the_level_is_recommended_and_never_chosen() -> None:
    """`ACT-032`. Two plain questions make the level answerable; they must not answer it.

    `core/CONFORMANCE_LEVELS.md:214-216` forbids deriving the level automatically, so the two
    properties here are equally load-bearing: the recommendation must agree with the framework's own
    definition of each level, AND the level field must still be a choice with nothing pre-selected.
    A recommendation that quietly became the default would breach that document while looking like
    a convenience.
    """
    cases = [
        ({"relied_on_outside_team": False, "material_quantitative_output": False}, "essential"),
        ({"relied_on_outside_team": True, "material_quantitative_output": False}, "standard"),
        ({"relied_on_outside_team": True, "material_quantitative_output": True}, "full"),
        # Material output nobody outside the team reads is still `full`: materiality is about what
        # the numbers are treated as, not about the size of the audience.
        ({"relied_on_outside_team": False, "material_quantitative_output": True}, "full"),
    ]
    wrong = [
        (answers, expected, plan.recommended_level(answers)[0])
        for answers, expected in cases
        if plan.recommended_level(answers)[0] != expected
    ]
    check(
        "the recommendation matches the framework's own definition of each level",
        not wrong,
        str(wrong),
    )

    section = plan.level_plan(
        ROOT,
        builds_ui=False,
        mode="simple",
        risk={"relied_on_outside_team": True, "material_quantitative_output": True},
    )
    spec = next(f for f in section.fields if f.id == "conformance_level")
    check(
        "the recommendation and its reasoning are shown to the adopter",
        any("full" in note and "recommendation" in note for note in section.notes),
        str(section.notes),
    )
    check(
        "but the level field pre-selects nothing, so the tool never makes the choice",
        spec.kind == "choice" and not spec.default,
        f"kind={spec.kind} default={spec.default!r}",
    )


def test_derived_gate_fields_are_correct_and_still_overridable() -> None:
    """`ACT-032`. Removing a question only helps if the derived value is right.

    The four fields dropped from the gate screen are checked here at their source: the precondition
    description must be the framework's OWN sentence for that gate - not a neighbouring gate's, and
    not a generic one - and the gated description must name the paths actually answered. The
    override half matters as much: a saved draft written before this change supplies all four, and
    an answer that exists must still win over the derived value.
    """
    spec = next(
        s
        for s in plan.gate_plan(level="essential", builds_ui=False, mode="simple")
        if s.id == "work_registration"
    )
    gate = sections.build_gate(spec, {"artefact": "activity/register.md", "paths": "src/**"})

    check(
        "the precondition description is this gate's own definition from the catalogue",
        gate["precondition"]["description"] == catalogue.GATE_CATALOGUE["work_registration"],
        gate["precondition"]["description"],
    )
    check(
        "the gated description names the paths that were actually answered",
        "src/**" in gate["gated_activity"]["description"],
        gate["gated_activity"]["description"],
    )
    check(
        "enforcement derives to the two that need no extra tooling",
        gate["enforcement"] == sections.DERIVED_ENFORCEMENT,
        str(gate["enforcement"]),
    )
    # `F51` superseded `ACT-032` here. This asserted that `effective_from` DERIVED to today, which
    # was the behaviour a cross-provider reviewer identified as contradicting the binding rule. The
    # field is asked again, so the property is now the opposite one: nothing is written unless a
    # human answered. Kept as a replacement rather than a deletion, because the old assertion is
    # the record of what was believed and the new one is what superseded it.
    check(
        "effective_from is NOT derived - absent unless answered (F51)",
        not gate.get("effective_from"),
        f"the tool supplied {gate.get('effective_from')!r} with no answer given",
    )

    supplied = sections.build_gate(
        spec,
        {
            "artefact": "activity/register.md",
            "paths": "src/**",
            "precondition_description": "A register entry, written first.",
            "gated_description": "Everything under src.",
            "effective_from": "2026-01-01",
            "enforcement": "ci",
        },
    )
    check(
        "an answer that was supplied still wins over every derived value",
        supplied["precondition"]["description"] == "A register entry, written first."
        and supplied["gated_activity"]["description"] == "Everything under src."
        and supplied["effective_from"] == "2026-01-01"
        and supplied["enforcement"] == ["ci"],
        str(supplied),
    )


def test_the_opt_in_removed_questions_not_answers() -> None:
    """`ACT-032`. The load-bearing property of collapsing eight tick boxes into one list.

    A reduction is only honest if the profile is unchanged for an adopter who answers the same way.
    So: build the controls fragment from the OLD per-control shape and from the NEW list, with
    nothing declared either way, and require them to be identical. If they ever diverge, the packet
    removed an answer rather than a question, and the profile quietly says something different from
    what it said before.

    The second half is the one that could rot silently: ticking a control in the list must declare
    it exactly as setting its boolean did.
    """
    base = {
        f"{c}.rationale": f"rationale for {c}"
        for c in catalogue.CONFORMANCE_LEVELS["full"] | set(plan.BASELINE_CONTROL_IDS)
    }
    base |= {
        f"{c}.implementation_reference": f"ref/{c}" for c in sorted(catalogue.CONFORMANCE_LEVELS["full"])
    }
    base |= {"scanner.name": "gitleaks", "scanner.wired_in": "workflows/scan.yml"}

    old_shape = base | {
        f"{c}.declared": False
        for c in sorted(catalogue.CONFORMANCE_LEVELS["full"])
        if c not in catalogue.CONFORMANCE_LEVELS["essential"]
    }
    new_shape = base | {"above_floor": []}

    check(
        "declaring nothing above the floor writes an identical profile either way",
        sections.build_controls(old_shape, level="essential")
        == sections.build_controls(new_shape, level="essential"),
        "the opt-in changed the written profile, so it removed an answer, not a question",
    )

    ticked = sections.build_controls(base | {"above_floor": ["provenance"]}, level="essential")
    by_boolean = sections.build_controls(base | {"provenance.declared": True}, level="essential")
    check(
        "ticking a control in the list declares it exactly as its boolean did",
        ticked == by_boolean and "provenance" in ticked["control_decisions"],
        str(sorted(ticked["control_decisions"])),
    )
    check(
        "and an unticked control is still absent",
        "run_lineage" not in ticked["control_decisions"],
        str(sorted(ticked["control_decisions"])),
    )


def test_defaults_propose_but_never_decide(tmp: Path) -> None:
    """`DR-40`: the defaults route proposes; a human still submits.

    The two properties that keep the binding rule true, checked rather than asserted: every
    proposal traces to discovery, a worked example, or a computed fact - never to invention - and
    a field with no honest source is left for the adopter rather than filled in.
    """
    from surfaceplate.adopt import defaults, discover

    repo = make_installed_repo(tmp, "defaults-repo")
    seed_referenced_files(repo)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "seed"], capture_output=True)

    found = discover.scan(repo)
    state = {
        "mode": {"mode": "simple"},
        "identity": {"owner": "Finance Platform team"},
        "stack": {"builds_user_interface": False},
        "level": {"conformance_level": "standard"},
    }
    proposals = defaults.propose(state, found=found)

    check("the defaults route proposes something to work from", len(proposals) > 20, str(len(proposals)))
    check(
        "every proposal declares an honest origin",
        all(p.origin in {"discovered", "example", "computed"} for p in proposals),
        str(sorted({p.origin for p in proposals})),
    )
    # "Discovered" covers two kinds of thing - a path in the repository, and a CI step name read
    # out of its workflow YAML. Both must come from the scan; neither may be invented.
    discovered = [p for p in proposals if p.origin == "discovered"]
    from_scan = set(found.artefacts) | set(found.paths) | set(found.lock_files) | set(
        found.register_dirs
    ) | set(found.ci_steps)
    invented = [p.value for p in discovered if p.value not in from_scan]
    check(
        "every discovered value came from the scan, never from invention",
        discovered and not invented,
        f"not found by the scan: {invented[:3]}",
    )
    paths = [p for p in discovered if p.value in from_scan and (repo / str(p.value)).exists()]
    check(
        "and the ones that are paths really exist on disk",
        bool(paths),
        "no discovered value resolved to a real file",
    )

    # The honest half: a judgement nobody can compute is NOT proposed.
    proposed = {p.field for p in proposals}
    check(
        "a gate's own description is left for the adopter, not invented",
        "gates.work_registration.precondition_description" not in proposed,
        "the tool proposed prose it has no source for",
    )
    check(
        "the adoption decision record id is never invented",
        "adoption.decision_record_id" not in proposed,
    )
    outstanding = defaults.unanswered(state, proposals, repo=repo, found=found)
    check(
        "and the wizard knows exactly what it still has to ask",
        "adoption.decision_record_id" in outstanding and len(outstanding) > 0,
        str(outstanding[:4]),
    )


def test_full_ui_end_to_end(tmp: Path) -> None:
    repo = make_installed_repo(tmp, "full-ui-repo")
    answers = answers_for(repo, level="full", builds_ui=True, mode="advanced")
    interview = ScriptedInterview(answers=answers)
    written = wizard.run(repo, interview)

    try:
        interview.assert_no_unused_keys()
        check("full/UI run: every scripted answer was used", True)
    except AssertionError as exc:
        check("full/UI run: every scripted answer was used", False, str(exc))

    import yaml

    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    check(
        "full/UI run declares every gate in the catalogue",
        len(data["prerequisites"]) == len(catalogue.GATE_CATALOGUE) == 19,
        str(len(data["prerequisites"])),
    )
    mandatory = set(catalogue.LEVEL_REQUIRED_GATES["full"]) | catalogue.DESIGN_GATES
    wrong = [
        g["id"] for g in data["prerequisites"] if g["id"] in mandatory and g["status"] != "required"
    ]
    check(
        "every gate the level (and the UI floor) requires is recorded as required",
        not wrong,
        f"not required: {wrong}",
    )
    check(
        "full declares all nine controls",
        len(data["control_decisions"]) == len(catalogue.CONFORMANCE_LEVELS["full"]) == 9,
        str(sorted(data["control_decisions"])),
    )
    check("the full profile validates against its own schema", _schema_ok(repo, written))


def test_design_gates_are_asked_not_invented(tmp: Path) -> None:
    """`standard` with no UI is the one combination that reaches the four `DESIGN_GATES`
    auto-`not_applicable` branch. Before `ACT-022` it wrote a fixed rationale with no prompt call at
    all. The rationale is still a real answer here - and now `tests/test_provenance.py` would catch
    a regression structurally, which no scripted test could."""
    repo = make_installed_repo(tmp, "standard-no-ui-repo")
    distinctive = "Platform team's own wording, not the framework's."
    overrides = {
        f"gates.{gate}.rationale": f"{distinctive} ({gate})" for gate in catalogue.DESIGN_GATES
    }
    answers = answers_for(repo, level="standard", builds_ui=False, mode="simple", overrides=overrides)
    interview = ScriptedInterview(answers=answers)
    written = wizard.run(repo, interview)
    interview.assert_no_unused_keys()

    import yaml

    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    by_id = {g["id"]: g for g in data["prerequisites"]}
    for gate in sorted(catalogue.DESIGN_GATES):
        check(
            f"{gate}: carries the scripted rationale, not a fixed string",
            by_id[gate]["status"] == "not_applicable" and distinctive in by_id[gate]["rationale"],
            str(by_id[gate]),
        )
    check("the standard/no-UI profile validates against its own schema", _schema_ok(repo, written))


def _schema_ok(repo: Path, written: Path) -> bool:
    import yaml
    import jsonschema

    schema = yaml.safe_load(
        (repo / ".standards" / "schemas" / "application-profile.schema.yaml").read_text(encoding="utf-8")
    )
    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(data))
    if errors:
        print("      schema errors:", "; ".join(e.message for e in errors[:3]))
    return not errors


# ---------------------------------------------------------------------------------------------
# Interrupt, resume, and refusals
# ---------------------------------------------------------------------------------------------


def test_interrupt_leaves_repo_untouched(tmp: Path) -> None:
    repo = make_installed_repo(tmp, "interrupt-repo")
    before_profile = (repo / "governance" / "application-profile.yaml").read_text(encoding="utf-8")
    before_files = {p.relative_to(repo) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}

    interview = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="risk")
    try:
        wizard.run(repo, interview)
        check("an interrupt raises Cancelled", False, "wizard.run returned instead of raising")
    except Cancelled:
        check("an interrupt raises Cancelled", True)

    after_profile = (repo / "governance" / "application-profile.yaml").read_text(encoding="utf-8")
    after_files = {p.relative_to(repo) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}
    check("the profile is byte-for-byte unchanged after an interrupt", before_profile == after_profile)

    new_files = after_files - before_files
    check(
        "the only new file after an interrupt is the resumable draft",
        new_files == {Path(wizard.DRAFT_FILENAME)},
        f"new files: {new_files}",
    )
    draft = json.loads((repo / wizard.DRAFT_FILENAME).read_text(encoding="utf-8"))
    check(
        "the draft records only the sections completed before the interrupt",
        set(draft["sections"]) == {"mode", "identity", "stack"},
        str(set(draft["sections"])),
    )
    check(
        "the draft states its own format, so a differently-shaped one is never misread",
        draft.get("format") == 2,
        str(draft.get("format")),
    )
    check(
        "the draft's completed sections carry the real scripted answers",
        draft["sections"]["identity"]["application_id"] == "billing-reconciler",
        str(draft["sections"]["identity"]),
    )


def test_resume_from_draft(tmp: Path) -> None:
    """A second invocation offers the draft, does not re-ask what was already answered, and the
    resumed answers reach the written profile."""
    repo = make_installed_repo(tmp, "resume-repo")
    seed_referenced_files(repo)

    first = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="controls")
    try:
        wizard.run(repo, first)
        check("resume fixture: the first attempt is interrupted as designed", False, "did not raise")
    except Cancelled:
        check("resume fixture: the first attempt is interrupted as designed", True)

    draft_path = repo / wizard.DRAFT_FILENAME
    check("resume fixture: a draft exists after the interrupt", draft_path.is_file())
    completed = set(json.loads(draft_path.read_text(encoding="utf-8"))["sections"])
    check(
        "resume fixture: the draft completed everything up to the interrupt",
        completed == {"mode", "identity", "stack", "risk", "level", "route"},
        str(completed),
    )

    # The second interview is given ONLY the answers for the sections still outstanding. Because
    # ScriptedInterview raises on any planned field it has no answer for, a resumed section that was
    # re-asked would fail here rather than pass quietly.
    remaining = {
        key: value
        for key, value in ESSENTIAL_ANSWERS.items()
        if key.split(".")[0] not in completed
    }
    second = ScriptedInterview(answers=remaining)
    written = wizard.run(repo, second)
    try:
        second.assert_no_unused_keys()
        check("resume run: every remaining answer was used, and none extra", True)
    except AssertionError as exc:
        check("resume run: every remaining answer was used, and none extra", False, str(exc))

    check("resume run: the human was actually offered the draft", len(second.resume_offers) == 1)
    check(
        "resume run: the offer stated it matches the installed framework",
        second.resume_offers[0].matches,
    )
    check("resume run: the draft is cleared after a successful write", not draft_path.is_file())

    import yaml

    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    check(
        "resume run: the resumed identity answers reached the final profile",
        data.get("application_id") == "billing-reconciler" and data.get("owner") == "Finance Platform team",
    )
    check(
        "resume run: the resumed conformance-level answer reached the final profile",
        data.get("conformance_level") == "essential",
    )


def test_declining_a_resume_starts_fresh(tmp: Path) -> None:
    repo = make_installed_repo(tmp, "decline-resume-repo")
    seed_referenced_files(repo)
    first = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="risk")
    try:
        wizard.run(repo, first)
    except Cancelled:
        pass

    second = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), resume=False)
    written = wizard.run(repo, second)
    check(
        "declining the draft re-asks every section from the start",
        {key.split(".")[0] for key in second.asked} == set(plan.SECTION_ORDER),
        str(sorted({key.split(".")[0] for key in second.asked})),
    )
    check("declining the draft still produces a profile", written.is_file())


def test_quitting_at_the_resume_prompt_keeps_the_draft(tmp: Path) -> None:
    """`F68`, first half. `ConfirmResumeApp.run()` returns `None` on `Ctrl+Q` or a closed
    terminal; `confirm_resume` returned `bool(None)`; `_resume_or_start` read `False` as "start
    fresh" and deleted the draft. Three answers, three outcomes: `True` resumes, `False` deletes,
    `None` - the human quit - cancels the run and leaves the draft where it was."""
    repo = make_installed_repo(tmp, "quit-at-resume-repo")
    seed_referenced_files(repo)
    try:
        wizard.run(repo, ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="risk"))
    except Cancelled:
        pass
    draft = repo / wizard.DRAFT_FILENAME
    check("precondition: the interrupted run left a draft", draft.is_file())

    class QuitsAtThePrompt:
        """An `Interview` whose resume answer is neither yes nor no: the human quit."""

        def confirm_resume(self, info):
            return None

        def collect(self, **kwargs):
            raise AssertionError("collect must not run after the human quit at the prompt")

    try:
        wizard.run(repo, QuitsAtThePrompt())
        outcome = "ran on"
    except Cancelled:
        outcome = "cancelled"
    except AssertionError as exc:
        outcome = str(exc)
    check("quitting at the resume prompt cancels the run", outcome == "cancelled", outcome)
    check("and the draft is still on disk", draft.is_file())

    second = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), resume=False)
    wizard.run(repo, second)
    check("an explicit no still discards it and completes a fresh run",
          not draft.is_file() and len(second.resume_offers) == 1)


def test_refuses_without_install(tmp: Path) -> None:
    repo = tmp / "no-install-repo"
    repo.mkdir()
    try:
        wizard.run(repo, ScriptedInterview(answers={}))
        check("adopt refuses a repository without .standards/INSTALL.json", False, "no exception")
    except wizard.NotInstalled:
        check("adopt refuses a repository without .standards/INSTALL.json", True)


def test_refuses_to_overwrite_a_real_profile(tmp: Path) -> None:
    repo = make_installed_repo(tmp, "already-adopted-repo")
    real_profile = repo / "governance" / "application-profile.yaml"
    real_profile.write_text("application_id: already-here\nowner: Someone\n", encoding="utf-8")
    try:
        wizard.run(repo, ScriptedInterview(answers={}))
        check("adopt refuses to overwrite a real (non-template) profile", False, "no exception")
    except wizard.AlreadyAdopted:
        check("adopt refuses to overwrite a real (non-template) profile", True)
    check(
        "the existing profile was left untouched",
        real_profile.read_text(encoding="utf-8") == "application_id: already-here\nowner: Someone\n",
    )


def test_a_real_profile_that_mentions_the_token_is_not_the_template(tmp: Path) -> None:
    """`F63`. The guard tested `"replace-me" in text` over the whole file, so a completed profile
    whose `risk_profile` said "Never type replace-me into a rationale." was taken for the untouched
    template and overwritten with no prompt - the one finding in the review that destroys work
    rather than blocking it. The token has to be looked for where the template puts it, in the
    identifying scalars, not in the byte stream."""
    import yaml

    repo = make_installed_repo(tmp, "prose-mentions-token-repo")
    profile = yaml.safe_load(
        (PAYLOAD / "examples" / "application-profile.essential.example.yaml").read_text(encoding="utf-8")
    )
    profile["risk_profile"] = "Never type replace-me into a rationale."
    target = repo / "governance" / "application-profile.yaml"
    before = yaml.safe_dump(profile, sort_keys=False, allow_unicode=True)
    target.write_text(before, encoding="utf-8")
    try:
        wizard.run(repo, ScriptedInterview(answers={}))
        outcome = "no exception"
    except wizard.AlreadyAdopted:
        outcome = "refused"
    except Exception as exc:  # noqa: BLE001 - past the guard, the empty script fails in its own way
        outcome = f"got past the guard: {type(exc).__name__}"
    check("a completed profile whose prose mentions replace-me is refused as already adopted",
          outcome == "refused", outcome)
    check("and it is byte-identical afterwards",
          target.read_text(encoding="utf-8") == before)


def test_the_untouched_template_is_still_fair_game(tmp: Path) -> None:
    """The other direction, so the guard cannot pass by refusing everything: the installer's own
    template, every identifying scalar still `replace-me`, is what `adopt` exists to fill in."""
    repo = make_installed_repo(tmp, "untouched-template-repo")
    template = (repo / "governance" / "application-profile.yaml").read_text(encoding="utf-8")
    check("precondition: the installed profile is the untouched template",
          "application_id: replace-me" in template)
    try:
        wizard._refuse_if_already_adopted(repo)
        check("the untouched template is not refused", True)
    except wizard.AlreadyAdopted as exc:
        check("the untouched template is not refused", False, str(exc))


def test_write_refused_on_placeholder_content(repo: Path, valid_profile: dict) -> None:
    """Mutates a profile already proven schema-valid so the ONLY thing wrong with it is the
    placeholder token - otherwise schema validation, which `_verify` runs first, would refuse it for
    an unrelated reason and this would test nothing."""
    from surfaceplate.adopt import render

    corrupted = json.loads(json.dumps(valid_profile))  # cheap deep copy
    corrupted["owner"] = "TBD - fill this in later"
    rendered = render.render_profile(corrupted)
    try:
        wizard._verify(corrupted, rendered, repo)
        check("_verify refuses a profile carrying a template placeholder token", False, "no exception")
    except wizard.WriteRefused as exc:
        check(
            "_verify refuses a profile carrying a template placeholder token",
            "placeholder" in exc.detail,
            exc.detail,
        )


def test_validators_refuse_what_the_checker_rejects(tmp: Path) -> None:
    """`F66` / `DR-48`. The wizard accepted a future `effective_from`, a 401-day and a past
    `review_by`, a one-character `application_id`, basic-ISO dates the schema refuses, and an
    untracked path - each of which the checker's first run rejects. One rules module now holds
    the rules and both sides import it; this asserts the wizard's side refuses each input."""
    import datetime as _dt

    from surfaceplate.adopt import validators

    repo = make_installed_repo(tmp, "parity-inputs-repo")
    (repo / "tracked.md").write_text("# tracked\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "tracked.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "tracked"], check=True)
    (repo / "untracked.md").write_text("# here, but not committed\n", encoding="utf-8")

    today = _dt.date.today()
    tomorrow = (today + _dt.timedelta(days=1)).isoformat()
    yesterday = (today - _dt.timedelta(days=1)).isoformat()
    far = (today + _dt.timedelta(days=401)).isoformat()
    near = (today + _dt.timedelta(days=180)).isoformat()

    refused = [
        ("effective_from", tomorrow, "SP033: a future effective_from"),
        ("effective_from", "20260101", "the schema's date form, not basic ISO"),
        ("review_by", far, "SP026: review_by beyond 400 days"),
        ("review_by", yesterday, "SP025: review_by in the past"),
        ("review_by", "20270101", "SP024: review_by not YYYY-MM-DD"),
        ("revisit_by", yesterday, "SP054: revisit_by in the past"),
        ("date", "20270101", "basic ISO is not the schema's date"),
        ("application_id", "a", "the schema's pattern needs two characters"),
        ("nonempty", "TBD", "SP020: a placeholder is not an answer"),
        ("nonempty", "please replace-me", "SP020: a placeholder inside prose"),
        ("tracked_path", "untracked.md", "SP051: exists but not tracked by git"),
        ("tracked_path", "missing.md", "SP032/SP051: does not exist"),
    ]
    for name, value, why in refused:
        check(
            f"validators refuse {name}={value!r} ({why})",
            validators.check(name, value, repo=repo) is not None,
        )
    accepted = [
        ("effective_from", today.isoformat()),
        ("effective_from", f"{today.isoformat()}T00:00:00+00:00"),
        ("review_by", near),
        ("revisit_by", near),
        ("date", today.isoformat()),
        ("application_id", "ab"),
        ("nonempty", "a real answer"),
        ("tracked_path", "tracked.md"),
    ]
    for name, value in accepted:
        problem = validators.check(name, value, repo=repo)
        check(f"and accept {name}={value!r}", problem is None, str(problem))


def test_every_checker_code_has_a_validator_or_an_exemption(tmp: Path) -> None:
    """`DR-48` (4): for every `SP` code the checker emits, the wizard refuses the same input at
    the field, or an exemption names the reason. The table is compared against the codes the
    checker actually emits, both ways, so a new code cannot arrive without a row here."""
    import datetime as _dt
    import re

    from surfaceplate.adopt import validators

    repo = make_installed_repo(tmp, "parity-table-repo")
    (repo / "untracked.md").write_text("x\n", encoding="utf-8")
    yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
    far = (_dt.date.today() + _dt.timedelta(days=401)).isoformat()
    tomorrow = (_dt.date.today() + _dt.timedelta(days=1)).isoformat()

    V = "validator"
    X = "exempt"
    PARITY: dict[str, tuple] = {
        "SP001": (X, "reads the install record, not a profile field"),
        "SP002": (X, "reads the install record, not a profile field"),
        "SP003": (X, "reads the install record, not a profile field"),
        "SP004": (X, "reads the vendored files, not a profile field"),
        "SP005": (X, "reads the vendored files, not a profile field"),
        "SP006": (X, "reads the agent instruction files, not a profile field"),
        "SP007": (X, "reads the conformance block, not a profile field"),
        "SP008": (X, "reads the conformance block, not a profile field"),
        "SP009": (X, "reads the installed workflow, not a profile field"),
        "SP010": (X, "the wizard writes the profile it is about to check"),
        "SP011": (X, "wizard._verify re-parses the rendered profile before writing"),
        "SP012": (X, "wizard._verify re-parses the rendered profile before writing"),
        "SP013": (X, "wizard._verify refuses to write without the vendored schema"),
        "SP014": (X, "wizard._verify refuses to write without a readable schema"),
        "SP015": (X, "wizard._verify validates against the schema before writing"),
        "SP016": (X, "wizard._verify validates against the schema before writing"),
        "SP017": (X, "the level is a closed choice of three; an empty choice is refused (F64)"),
        "SP018": (X, "sections.build_adoption writes the block unconditionally"),
        "SP019": (V, "nonempty", ""),
        "SP020": (V, "nonempty", "TBD"),
        "SP021": (X, "control decisions are computed from the level by sections.build_controls"),
        "SP022": (X, "control decisions are computed from the level by sections.build_controls"),
        "SP023": (X, "no control decision can be deferred through the wizard (DR-32)"),
        "SP024": (V, "review_by", "20270101"),
        "SP025": (V, "review_by", yesterday),
        "SP026": (V, "review_by", far),
        "SP027": (X, "sections.build_gates writes every gate the plan declares"),
        "SP028": (X, "sections.build_gates writes the schema's shape from the plan"),
        "SP029": (X, "a level-mandatory gate is stated by the plan, never chosen"),
        "SP030": (X, "a level-mandatory gate is stated by the plan, never chosen"),
        "SP031": (V, "revisit_by", ""),
        "SP032": (V, "tracked_path", "missing.md"),
        "SP033": (V, "effective_from", tomorrow),
        "SP034": (X, "history-only: compares against git history (DR-48)"),
        "SP035": (X, "history-only: compares against git history (DR-48)"),
        "SP037": (X, "builds_user_interface is a closed yes/no the form refuses empty; the design gates follow it"),
        "SP038": (X, "enforcement is derived as history_audit + review; the wizard never writes local_hook"),
        "SP039": (X, "reads the staged snapshot, not the profile the wizard writes"),
        "SP040": (X, "reads the staged snapshot, not the profile the wizard writes"),
        "SP041": (X, "reads the staged snapshot, not the profile the wizard writes"),
        "SP042": (X, "a pathspec is validated by git at check time; the field offers discovered pathspecs"),
        "SP043": (X, "reads gate exception records, which the wizard does not write"),
        "SP046": (V, "tracked_path", "untracked.md"),
        "SP047": (X, "reads the workflow step's shell semantics, not a profile field"),
        "SP048": (X, "written from the install record, never asked"),
        "SP049": (X, "written from the install record, never asked"),
        "SP050": (X, "the wizard writes no placeholder-scan exemptions"),
        "SP051": (V, "tracked_path", "untracked.md"),
        "SP052": (X, "authority_map is mandatory at every level that requires documentation_authority"),
        "SP053": (V, "ci_step", "No such step"),
        "SP054": (V, "revisit_by", yesterday),
        "SP055": (V, "tracked_path", "missing-register"),
        "SP056": (X, "reads the records inside a register, which the wizard does not write"),
        "SP057": (X, "reads the records inside a register, which the wizard does not write"),
        "SP058": (X, "reads the records inside a register, which the wizard does not write"),
    }
    source = (PAYLOAD / "check_conformance.py").read_text(encoding="utf-8")
    emitted = set(re.findall(r'Finding\(\s*"(SP\d{3})"', source))
    check(
        "every emitted SP code has a parity row, and every row is an emitted code",
        emitted == set(PARITY),
        f"unmapped: {sorted(emitted - set(PARITY))}; stale rows: {sorted(set(PARITY) - emitted)}",
    )
    for code, row in sorted(PARITY.items()):
        if row[0] == V:
            _, name, bad = row
            check(
                f"{code}: validators.check({name!r}, {bad!r}) refuses it",
                validators.check(name, bad, repo=repo) is not None,
            )
    exemptions = sum(1 for row in PARITY.values() if row[0] == X)
    check("every exemption names a reason", all(len(r) == 2 and r[1] for r in PARITY.values() if r[0] == X))
    print(f"  ({len(PARITY) - exemptions} codes met by a validator, {exemptions} exempt by name)")


def test_scripted_interview_objects_in_both_directions(tmp: Path) -> None:
    """The two-sided guarantee itself, checked rather than assumed."""
    repo = make_installed_repo(tmp, "two-sided-repo")

    short = dict(ESSENTIAL_ANSWERS)
    short.pop("identity.owner")
    try:
        wizard.run(repo, ScriptedInterview(answers=short))
        check("a missing answer for a planned field is a failure", False, "no exception")
    except AssertionError as exc:
        check("a missing answer for a planned field is a failure", "identity.owner" in str(exc), str(exc))

    extra = dict(ESSENTIAL_ANSWERS)
    extra["identity.nonexistent_field"] = "nobody asks for this"
    interview = ScriptedInterview(answers=extra)
    try:
        wizard.run(repo / "nonexistent", interview)
    except Exception:
        pass
    interview_2 = ScriptedInterview(answers=extra)
    repo2 = make_installed_repo(tmp, "two-sided-repo-2")
    seed_referenced_files(repo2)
    wizard.run(repo2, interview_2)
    try:
        interview_2.assert_no_unused_keys()
        check("an answer nothing asked for is a failure", False, "assert_no_unused_keys passed")
    except AssertionError as exc:
        check("an answer nothing asked for is a failure", "nonexistent_field" in str(exc), str(exc))


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)

        print("catalogue and content coverage")
        test_catalogue_sections_sum_to_the_whole_catalogue()
        test_explanations_cover_every_catalogue_item()
        test_example_answers_cover_every_reachable_rationale_field()
        test_mode_selects_the_register_the_plan_carries()
        test_detected_signals_are_stated_both_ways(tmp)

        print("\nessential-level end to end")
        essential_repo, essential_profile = test_essential_end_to_end(tmp)

        print("\nF36 regression: flow-sequence-special characters through the real flow")
        test_tricky_characters_round_trip(tmp)

        print("\nF38 regression: multi-line prose survives the whole flow")
        test_multiline_prose_survives_the_whole_flow(tmp)

        print("\nDR-40: the defaults route proposes, and says where each value came from")
        test_the_profile_says_which_controls_are_actually_checked()
        test_the_tool_does_not_set_effective_from()
        test_the_level_is_recommended_and_never_chosen()
        test_derived_gate_fields_are_correct_and_still_overridable()
        test_the_opt_in_removed_questions_not_answers()
        test_defaults_propose_but_never_decide(tmp)

        print("\nfull-level, UI-building end to end")
        test_full_ui_end_to_end(tmp)

        print("\nstandard-level, no-UI (ACT-022: DESIGN_GATES rationale is asked)")
        test_design_gates_are_asked_not_invented(tmp)

        print("\ninterrupt and resume")
        test_interrupt_leaves_repo_untouched(tmp)
        test_resume_from_draft(tmp)
        test_declining_a_resume_starts_fresh(tmp)
        test_quitting_at_the_resume_prompt_keeps_the_draft(tmp)

        print("\nrefusals, and the guarantee itself")
        test_refuses_without_install(tmp)
        test_refuses_to_overwrite_a_real_profile(tmp)
        test_a_real_profile_that_mentions_the_token_is_not_the_template(tmp)
        test_the_untouched_template_is_still_fair_game(tmp)
        test_write_refused_on_placeholder_content(essential_repo, essential_profile)
        test_scripted_interview_objects_in_both_directions(tmp)

        print("\nDR-48: one set of rules for the wizard and the checker")
        test_validators_refuse_what_the_checker_rejects(tmp)
        test_every_checker_code_has_a_validator_or_an_exemption(tmp)

    print()
    if FAILURES:
        print(f"ADOPT_CONFORMANCE=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"ADOPT_CONFORMANCE=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
