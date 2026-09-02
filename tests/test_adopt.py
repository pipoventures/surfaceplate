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
import re
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

import yaml  # noqa: E402

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
    # `DR-47`: every key below that the flow PROPOSES (a rationale, a review date, a maintainer)
    # is an override of that proposal, recorded as typed the way a review edit would be; every
    # key the flow PRESENTS (the decisions form, the gate list, the remainder) is the answer.
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


def _commit_all(repo: Path, message: str = "fixture") -> None:
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", message], capture_output=True)


def answers_for(repo: Path, *, level: str, builds_ui: bool, mode: str, overrides: dict | None = None) -> dict:
    """Walk the flow the wizard will walk, answering every field it presents and overriding
    every proposal, so a run exercises every branch.

    A FIXTURE BUILDER, not a correctness oracle: the tests below assert real properties of the
    WRITTEN profile rather than trusting that generating answers this way proves anything. Since
    `DR-48` a path field refuses anything git does not track, so this creates and commits a real
    file for each such field rather than typing a plausible string into it - which is exactly
    the answer `F66` found the wizard accepting and the checker rejecting.
    """
    from surfaceplate.adopt import flow as _flow

    overrides = overrides or {}
    seeded = {
        "stack.builds_user_interface": builds_ui,
        "level.conformance_level": level,
        "risk.data_classification": "internal",
        "adoption.adoption_status": "in_progress",
        "adoption.needs_validator": False,
        "identity.application_id": "payments-orchestrator",
        **overrides,
    }
    answers: dict = {}
    workflow_steps: list[str] = []

    def real_file(key: str) -> str:
        rel = "docs/fixtures/" + re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-") + ".md"
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# {key}\n\nA real file for the fixture.\n", encoding="utf-8")
        return rel

    def value_for(key: str, spec: plan.FieldSpec) -> object:
        if key in seeded:
            return seeded[key]
        if spec.kind == "bool":
            return bool(spec.default)
        if spec.id.endswith("above_floor") or key.endswith("above_floor"):
            # `ACT-032`. Sweep every above-floor control ON, so this fixture exercises the branch
            # where ticking one really does ask for its rationale and reference.
            return [c for c, _ in spec.choices]
        if spec.kind == "choice":
            return spec.choices[0][0]
        if spec.validate == "tracked_path":
            return real_file(key)
        if spec.validate.startswith("scanner_workflow"):
            scanner = spec.validate.partition(":")[2] or "gitleaks"
            rel = ".github/workflows/fixture-secret-scan.yml"
            target = repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(f"jobs:\n  scan:\n    steps:\n      - name: Run {scanner}\n        run: {scanner} detect\n", encoding="utf-8")
            return rel
        if spec.validate == "ci_step":
            name = f"Step for {key.split('.')[-2]}"
            workflow_steps.append(name)
            return name
        if spec.default:
            return spec.default
        if key.endswith("paths"):
            return "src/**"
        return f"answer for {key}"

    flow = _flow.Flow(repo, {"standard_version": "0.0.0", "framework_digest": "0"})
    for spec in flow.decisions_plan().fields:
        answers[spec.id] = value_for(spec.id, spec)
    flow.answer_decisions(dict(answers))
    answers["level.conformance_level"] = level
    flow.answer_level({"conformance_level": level})
    gate_answers: dict = {}
    for gate in flow.gate_specs():
        local: dict = {}
        for f in gate.fields:
            if not f.applies(local):
                continue
            key = f"gates.{gate.id}.{f.id}"
            local[f.id] = value_for(key, f)
            answers[key] = local[f.id]
            gate_answers[f"{gate.id}.{f.id}"] = local[f.id]
    flow.answer_gates(gate_answers)
    remainder = flow.remainder_plan()
    local = {}
    for spec in remainder.fields:
        if not spec.applies(local):
            continue
        local[spec.id] = value_for(spec.id, spec)
        answers[spec.id] = local[spec.id]
    # Every proposal, overridden, so the run's written values are the fixture's own.
    for key, proposal in flow.proposals.items():
        if key not in answers and key.split(".")[0] != "gates":
            spec = flow.field_spec(key)
            answers[key] = value_for(key, spec) if spec is not None else proposal.value
    if workflow_steps:
        workflow = repo / ".github" / "workflows" / "fixture-tests.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        steps = "".join(f"      - name: {n}\n        run: echo {n!r}\n" for n in dict.fromkeys(workflow_steps))
        workflow.write_text("jobs:\n  tests:\n    steps:\n" + steps, encoding="utf-8")
    _commit_all(repo, "fixture files")
    return answers


def seed_referenced_files(repo: Path, *, ci: bool = False) -> None:
    """The artefacts an `essential` fixture names, so the real checker has something to find -
    committed, because since `DR-48` the field itself refuses an untracked path. The decisions
    directory makes `decision_record_id` a question rather than a scaffolded record. With `ci`,
    a workflow with a named step, so pattern-B references are discovered rather than asked."""
    if ci:
        workflow = repo / ".github" / "workflows" / "ci.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text(
            "jobs:\n  t:\n    steps:\n      - name: Run the tests\n        run: pytest\n",
            encoding="utf-8",
        )
        # `DR-51` (5): a workflow where a step RUNS the scanner is what `scanner.wired_in` is
        # proposed from; `ci.yml` above runs pytest and is rightly not it.
        (repo / ".github" / "workflows" / "secret-scan.yml").write_text(
            "jobs:\n  scan:\n    steps:\n      - name: Run gitleaks\n        run: gitleaks detect\n",
            encoding="utf-8",
        )
    (repo / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "DEVELOPMENT_REGISTER.md").write_text("# Register\n", encoding="utf-8")
    (repo / "docs" / "decisions").mkdir(exist_ok=True)
    (repo / "docs" / "decisions" / "README.md").write_text("# Decisions\n", encoding="utf-8")
    (repo / "workflows").mkdir(exist_ok=True)
    # A file the checker's SP046 accepts: it mentions the scanner and a step runs it. `DR-51` (5)
    # made the field refuse what the checker refuses, so "name: scan" is no longer an answer.
    (repo / "workflows" / "secret-scan.yml").write_text(
        "name: scan\njobs:\n  scan:\n    steps:\n      - name: Run gitleaks\n        run: gitleaks detect\n",
        encoding="utf-8",
    )
    _commit_all(repo, "seed")


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
    # Since `DR-48` a path field refuses anything git does not track, so the awkward names are
    # real files here: the property under test is that the renderer escapes them, not that the
    # wizard accepts a path that does not exist.
    for rel in ("workflows/secret-scan.yml?raw=true", "-docs/DEVELOPMENT_REGISTER.md", "requirements.txt"):
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# real\n", encoding="utf-8")
    # `DR-51` (5): the scanner field applies SP046's rule, so the awkwardly named workflow must
    # also be one where a step runs the scanner. The property under test is unchanged.
    (repo / "workflows" / "secret-scan.yml?raw=true").write_text(
        "# real\njobs:\n  s:\n    steps:\n      - name: Run gitleaks\n        run: gitleaks detect\n", encoding="utf-8"
    )
    (repo / "docs" / "decisions").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "decisions" / "README.md").write_text("# Decisions\n", encoding="utf-8")
    _commit_all(repo, "tricky names")
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
    seed_referenced_files(repo)
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
    """`DR-40`, re-read under `DR-47`: the wizard proposes; a human still decides.

    Every proposal traces to discovery, a worked example, or a computed fact - never to invention;
    a field with no honest source is left for the adopter; and no gate STATUS is ever proposed,
    `not_applicable` included, because a scope decision is a key a human presses.
    """
    from surfaceplate.adopt import defaults, discover
    from surfaceplate.adopt import flow as _flow

    repo = make_installed_repo(tmp, "defaults-repo")
    seed_referenced_files(repo)

    found = discover.scan(repo)
    state = {
        "mode": {"mode": "simple"},
        "identity": {"owner": "Finance Platform team"},
        "stack": {"builds_user_interface": False},
        "risk": {"data_classification": "internal"},
        "level": {"conformance_level": "standard"},
    }
    proposals = defaults.propose_after_level(state, found=found, adoption_date="2026-09-02")

    check("the wizard proposes something to work from", len(proposals) > 20, str(len(proposals)))
    check(
        "every proposal declares an honest origin",
        all(p.origin in {"discovered", "example", "computed"} for p in proposals),
        str(sorted({p.origin for p in proposals})),
    )
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
    proposed = {p.field for p in proposals}
    check(
        "no gate status is proposed, not_applicable included (DR-47)",
        not any(f.endswith(".status") for f in proposed),
        str(sorted(f for f in proposed if f.endswith(".status"))),
    )
    check(
        "a gate's own description is left for the adopter, not invented",
        "gates.work_registration.precondition_description" not in proposed,
    )
    check("the adoption decision record id is never invented", "adoption.decision_record_id" not in proposed)
    check(
        "effective_from is proposed as the adoption date, as computed (DR-47 (5))",
        any(p.field == "gates.work_registration.effective_from" and p.value == "2026-09-02" and p.origin == "computed" for p in proposals),
    )

    flow = _flow.Flow(repo, {"standard_version": "0.0.0", "framework_digest": "0"}, state=state, done=("decisions", "level"))
    remainder = {f.id for f in flow.remainder_plan().fields}
    check(
        "and the wizard knows exactly what it still has to ask: the record id, since a decisions directory exists, and nothing it proposed",
        "adoption.decision_record_id" in remainder and not (remainder & proposed - {"controls.above_floor"}),
        str(sorted(remainder)),
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

    interview = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="level")
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
        "the draft records only the stages completed before the interrupt",
        draft["done"] == ["decisions"] and "level" not in draft["sections"],
        f"done={draft.get('done')} sections={sorted(draft['sections'])}",
    )
    check(
        "the draft states its own format, so a differently-shaped one is never misread",
        draft.get("format") == 3,
        str(draft.get("format")),
    )
    check(
        "and the draft carries an origin for every answer it holds (DR-47)",
        all(f"{s}.{f}" in draft["origins"] for s, fields in draft["sections"].items() for f in fields if s != "mode"),
        str(sorted(set(f"{s}.{f}" for s, fs in draft["sections"].items() for f in fs) - set(draft["origins"]))),
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

    first = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="gates")
    try:
        wizard.run(repo, first)
        check("resume fixture: the first attempt is interrupted as designed", False, "did not raise")
    except Cancelled:
        check("resume fixture: the first attempt is interrupted as designed", True)

    draft_path = repo / wizard.DRAFT_FILENAME
    check("resume fixture: a draft exists after the interrupt", draft_path.is_file())
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    check(
        "resume fixture: the draft completed everything up to the interrupt",
        draft["done"] == ["decisions", "level"] and "level" in draft["sections"],
        f"done={draft.get('done')}",
    )
    answered = {f"{s}.{f}" for s, fields in draft["sections"].items() for f in fields}

    # The second interview is given ONLY the answers for the fields still outstanding. Because
    # ScriptedInterview raises on any presented field it has no answer for, a resumed stage that
    # was re-asked would fail here rather than pass quietly.
    remaining = {key: value for key, value in ESSENTIAL_ANSWERS.items() if key not in answered}
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
    first = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="level")
    try:
        wizard.run(repo, first)
    except Cancelled:
        pass

    second = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), resume=False)
    written = wizard.run(repo, second)
    check(
        "declining the draft re-asks every stage from the start",
        second.stages[:3] == ["decisions", "level", "gates"],
        str(second.stages),
    )
    check("declining the draft still produces a profile", written.is_file())


def test_the_draft_lives_under_standards_and_an_old_one_is_migrated(tmp: Path) -> None:
    """`DR-50` (3). The draft sat at the repository root, untracked, with nothing ignoring it, and
    gitignoring it would have meant the installer editing an adopter-owned file. It now lives
    under `.standards/`, which the install record already governs; a draft at the old location
    is offered once and moved."""
    repo = make_installed_repo(tmp, "draft-home-repo")
    seed_referenced_files(repo)
    try:
        wizard.run(repo, ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="level"))
    except Cancelled:
        pass
    check(
        "the draft is written under .standards/",
        (repo / ".standards" / "adopt-draft.json").is_file() and not (repo / ".surfaceplate-adopt-draft.json").exists(),
        str(sorted(p.name for p in repo.iterdir())),
    )
    # A draft from before the move, at the old location.
    old = repo / ".surfaceplate-adopt-draft.json"
    old.write_text((repo / ".standards" / "adopt-draft.json").read_text(encoding="utf-8"), encoding="utf-8")
    (repo / ".standards" / "adopt-draft.json").unlink()
    second = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="gates")
    try:
        wizard.run(repo, second)
    except Cancelled:
        pass
    check("a draft at the old location is offered", len(second.resume_offers) == 1)
    check(
        "and migrated to the new one",
        (repo / ".standards" / "adopt-draft.json").is_file() and not old.exists(),
        str(sorted(p.name for p in repo.iterdir())),
    )


def test_quitting_at_the_resume_prompt_keeps_the_draft(tmp: Path) -> None:
    """`F68`, first half. `ConfirmResumeApp.run()` returns `None` on `Ctrl+Q` or a closed
    terminal; `confirm_resume` returned `bool(None)`; `_resume_or_start` read `False` as "start
    fresh" and deleted the draft. Three answers, three outcomes: `True` resumes, `False` deletes,
    `None` - the human quit - cancels the run and leaves the draft where it was."""
    repo = make_installed_repo(tmp, "quit-at-resume-repo")
    seed_referenced_files(repo)
    try:
        wizard.run(repo, ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="level"))
    except Cancelled:
        pass
    draft = repo / wizard.DRAFT_FILENAME
    check("precondition: the interrupted run left a draft", draft.is_file())

    class QuitsAtThePrompt:
        """An `Interview` whose answer at the opening is neither yes nor no: the human quit.
        (`DR-51` (2) folded the resume prompt into the opening screen; the seam is `open`.)"""

        def open(self, welcome):
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


def test_every_presented_field_states_what_it_decides_and_what_a_wrong_answer_costs(tmp: Path) -> None:
    """`F82` / `DR-51` (3). The framework's author, running its wizard, could not always say what a
    question was for. Every field the flow presents - at every level, with and without an
    interface - and every field an edit on the review can reach carries three things: what is
    asked (`help`), what the answer decides (`decides`) and what a wrong answer costs (`wrong`).
    Presence is what this proves; the text is judged by reading it."""
    from surfaceplate.adopt import flow as _flow

    repo = make_installed_repo(tmp, "minimum-repo")
    seed_referenced_files(repo, ci=True)
    gaps: list[str] = []
    seen: set[str] = set()

    def look(where: str, spec: plan.FieldSpec) -> None:
        seen.add(f"{where}:{spec.id}")
        for attr in ("help", "decides", "wrong"):
            if not getattr(spec, attr).strip():
                gaps.append(f"{where}: {spec.id} has no {attr}")

    for level in ("essential", "standard", "full"):
        for ui in (False, True):
            flow = _flow.Flow(repo, {"standard_version": "0.0.0", "framework_digest": "0"})
            for spec in flow.decisions_plan().fields:
                look("decisions", spec)
            flow.answer_decisions({
                "identity.application_id": "app", "identity.owner": "Owner", "stack.builds_user_interface": "yes" if ui else "no",
                "risk.relied_on_outside_team": "no", "risk.material_quantitative_output": "no", "risk.data_classification": "internal",
                "wrap.release_route": "manual", "risk.risk_profile": "",
            })
            for spec in flow.level_plan().fields:
                look("level", spec)
            flow.answer_level({"conformance_level": level})
            for gate in flow.gate_specs():
                for spec in gate.fields:
                    look(f"gate:{gate.id}", spec)
            flow.state["gates"] = {}
            flow.done.append("gates")
            for spec in flow.remainder_plan().fields:
                look("remainder", spec)
    for name in plan.SECTION_ORDER:
        for spec in plan.section_plan(name, repo=repo, state={"identity": {"owner": "x"}, "stack": {"builds_user_interface": True}, "level": {"conformance_level": "full"}, "mode": {"mode": "simple"}}).fields:
            look(name, spec)
    check(f"every presented field carries help, decides and wrong ({len(seen)} field ids across three levels, both interface answers, and the review's edit path)",
          not gaps, "; ".join(gaps[:8]) + (f" (and {len(gaps) - 8} more)" if len(gaps) > 8 else ""))


def test_a_schema_refusal_names_the_profile_line(tmp: Path) -> None:
    """`F79` / `DR-51` (6). The maintainer's review read "(root): Additional properties are not
    allowed ('risk' was unexpected)" and took `risk` for his own free-text answer. A refusal
    is reported with the profile path it concerns, in the review's words, and the review can
    point Ctrl+E at it."""
    from surfaceplate.adopt import flow as _flow

    repo = make_installed_repo(tmp, "schema-refusal-repo")
    seed_referenced_files(repo)
    # The state that stopped the run: an installed schema older than the tool, with no `risk`.
    schema_path = repo / ".standards" / "schemas" / "application-profile.schema.yaml"
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    schema["properties"].pop("risk")
    schema_path.write_text(yaml.safe_dump(schema, sort_keys=False), encoding="utf-8")

    interview = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), confirm_write=False)
    try:
        wizard.run(repo, interview)
    except Cancelled:
        pass
    review = interview.review
    check("the review refuses", review is not None and review.error, getattr(review, "error", None))
    check("in the review's words, naming the line", "risk" in review.error and "installed" in review.error and "Additional properties" not in review.error, review.error)
    check("and the error path resolves to a line Ctrl+E can reach",
          review.error_path is not None and review.error_path.startswith("risk") and review.error_line is not None, f"{review.error_path} -> {review.error_line}")
    line = review.rendered.splitlines()[review.error_line] if review.error_line is not None else ""
    check("which is the risk block's first line", line.strip().startswith("risk:") or "relied_on_outside_team" in line, line)


def test_the_profile_is_written_atomically(tmp: Path) -> None:
    """`F77`, the non-atomic write. A failure between opening the profile and finishing it left
    a truncated file that `_refuse_if_already_adopted` then refused forever. The profile and its
    record are written to a temporary file beside the target and moved into place, so the target
    is either absent or complete."""
    import os

    repo = make_installed_repo(tmp, "atomic-repo")
    seed_referenced_files(repo)
    template = (repo / wizard.PROFILE_PATH).read_bytes()
    real_replace = os.replace

    def failing_replace(src, dst):
        if str(dst).endswith("application-profile.yaml"):
            raise OSError(28, "No space left on device")
        return real_replace(src, dst)

    os.replace = failing_replace
    try:
        try:
            wizard.run(repo, ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS)))
            outcome = "wrote"
        except wizard.PartialWrite as exc:
            outcome = f"partial: {exc}"
    finally:
        os.replace = real_replace
    check("a failure at the move is reported, not swallowed", outcome.startswith("partial") and "No space left" in outcome, outcome[:160])
    check("the target is untouched: still the template, byte for byte", (repo / wizard.PROFILE_PATH).read_bytes() == template)
    leftovers = [p.name for p in (repo / "governance").iterdir() if p.name not in ("application-profile.yaml",)]
    check("and no temporary file is left beside it", not leftovers, str(leftovers))
    wizard.run(repo, ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS)))
    check("the same run then completes", (repo / wizard.PROFILE_PATH).is_file() and (repo / "governance" / "application-profile.provenance.yaml").is_file())


def test_a_draft_with_stale_ids_is_not_resumed_into_a_crash(tmp: Path) -> None:
    """`F77`, a draft with stale ids. A draft naming a level or a gate no longer in the catalogue
    resumed and failed later with a bare KeyError (exit 4). It is now checked on load against
    the catalogue: a draft the flow cannot honour is not offered, is left in place, and the run
    starts fresh and says so."""
    repo = make_installed_repo(tmp, "stale-draft-repo")
    seed_referenced_files(repo)
    draft = repo / wizard.DRAFT_FILENAME
    draft.parent.mkdir(parents=True, exist_ok=True)
    record = json.loads((repo / wizard.INSTALL_RECORD).read_text(encoding="utf-8"))
    stale = {
        "format": 3, "framework_version": record["standard_version"], "framework_digest": record["framework_digest"],
        "sections": {"identity": {"owner": "O"}, "level": {"conformance_level": "extreme"}, "gates": {"no_such_gate.status": "required"}},
        "origins": {}, "done": ["decisions", "level"], "bulk": [],
    }
    draft.write_text(json.dumps(stale), encoding="utf-8")
    interview = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS))
    try:
        wizard.run(repo, interview)
        outcome = "completed"
    except Exception as exc:  # noqa: BLE001 - the whole point is that nothing escapes
        outcome = f"{type(exc).__name__}: {exc}"
    check("the run completes rather than dying on a KeyError", outcome == "completed", outcome[:200])
    check("the stale draft was not offered", not interview.resume_offers and interview.welcomes and interview.welcomes[0].draft is None)
    check("and the opening screen was told why", interview.welcomes and "extreme" in (interview.welcomes[0].draft_note or ""), getattr(interview.welcomes[0], "draft_note", None))
    check("the written profile carries the fixture's level, not the stale one", yaml.safe_load((repo / wizard.PROFILE_PATH).read_text(encoding="utf-8"))["conformance_level"] == "essential")


def test_the_create_it_row_leads_to_a_scaffold_for_gates_and_controls(tmp: Path) -> None:
    """`F87`, `F88` / `DR-54` (1). A seedable field's dropdown opens with "create it from the
    framework's seed"; choosing that row leads to the offer, and the value is recorded as
    scaffolded and written by the run - for a gate and for the assurance_findings control."""
    from surfaceplate.adopt import flow as _flow
    from surfaceplate.adopt import scaffold

    repo = make_installed_repo(tmp, "create-it-repo")
    (repo / "main.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / "scan.yml").write_text("jobs:\n  s:\n    steps:\n      - name: Run gitleaks\n        run: gitleaks detect\n", encoding="utf-8")
    _commit_all(repo, "fixture")
    flow = _flow.Flow(repo, {"standard_version": "0.16.0", "framework_digest": "x"})
    flow.answer_decisions({"identity.application_id": "app", "identity.owner": "O", "stack.builds_user_interface": "no",
                           "risk.relied_on_outside_team": "no", "risk.material_quantitative_output": "no",
                           "risk.data_classification": "internal", "wrap.release_route": "manual", "risk.risk_profile": ""})
    flow.answer_level({"conformance_level": "essential"})
    gate = next(s for s in flow.gate_specs() if s.id == "work_registration")
    artefact = next(f for f in gate.fields if f.id == "artefact")
    seed_path = scaffold.SEEDABLE["work_registration"][0]
    check("the gate's artefact field is a dropdown even with nothing to pick from", artefact.kind == "select", artefact.kind)
    check("whose first row creates the seed", artefact.choices[0][0] == seed_path and "create it" in artefact.choices[0][1], str(artefact.choices[:1]))
    check("and the field knows its seed", artefact.seed == seed_path, artefact.seed)
    flow.answer_gates({"work_registration.artefact": seed_path, "work_registration.paths": "**", "work_registration.effective_from": "2026-09-01"})
    remainder = flow.remainder_plan()
    above = next(f for f in remainder.fields if f.id == "controls.above_floor")
    answers = {f.id: (f.default if f.default else "") for f in remainder.fields}
    answers["controls.above_floor"] = ["assurance_findings"]
    ref = next(f for f in remainder.fields if f.id == "controls.assurance_findings.implementation_reference")
    control_seed = scaffold.SEEDABLE_CONTROLS["assurance_findings"][0]
    check("the control's reference dropdown opens with its seed", ref.kind == "select" and ref.choices[0][0] == control_seed and ref.seed == control_seed, str(ref.choices[:2]))
    answers["controls.assurance_findings.implementation_reference"] = control_seed
    answers["controls.assurance_findings.rationale"] = "Known limitations are written down."
    for spec in remainder.fields:
        if spec.validate and not answers.get(spec.id) and spec.kind in ("text", "textarea"):
            answers[spec.id] = "an answer"
    flow.answer_remainder(answers)
    offers = flow.scaffold_offers()
    check("both seeds are offered", {o.path for o in offers} >= {seed_path, control_seed}, str([o.path for o in offers]))
    flow.accept_scaffold(offers)
    check("the control's reference is recorded as scaffolded", flow.origins["controls.assurance_findings.implementation_reference"].kind == "scaffolded")
    review = flow.review()
    check("the review has nothing to refuse", not review.error, review.error)


def test_adopt_edit_rewrites_one_line_and_records_it(tmp: Path) -> None:
    """`F86` / `DR-54` (4). After the write, `adopt --edit <path> <value>` changes one line
    through the same renderer and verification as the wizard, and the sidecar records it as
    typed with a timestamp and the reason. A path the profile lacks is refused with the nearest
    named; a line the review marks as not editable is refused."""
    from surfaceplate import cli
    from surfaceplate.adopt import provenance

    repo = make_installed_repo(tmp, "edit-repo")
    seed_referenced_files(repo)
    wizard.run(repo, ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS)))
    before = yaml.safe_load((repo / wizard.PROFILE_PATH).read_text(encoding="utf-8"))
    written = wizard.edit(repo, "owner", "Platform Guild", because="the team was renamed")
    after = yaml.safe_load(written.read_text(encoding="utf-8"))
    check("the one line changed", after["owner"] == "Platform Guild" and before["owner"] != "Platform Guild")
    after["owner"] = before["owner"]
    check("and nothing else", after == before)
    record = yaml.safe_load((repo / provenance.PROVENANCE_PATH).read_text(encoding="utf-8"))
    entry = record["fields"]["owner"]
    check("the sidecar records the edit as typed, with a timestamp and the reason",
          entry["origin"] == "typed" and entry.get("typed_at") and "renamed" in entry.get("detail", ""), str(entry))
    check("and keeps a history of edits", record.get("edits") and record["edits"][-1]["path"] == "owner", str(record.get("edits")))
    wizard.edit(repo, "baseline_controls.secret_hygiene.scanner.wired_in[0]", "workflows/secret-scan.yml", because="same file, by index")
    check("a list element is addressed by index", yaml.safe_load((repo / wizard.PROFILE_PATH).read_text(encoding="utf-8"))["baseline_controls"]["secret_hygiene"]["scanner"]["wired_in"] == ["workflows/secret-scan.yml"])
    for path, value, why in (("ownr", "x", "a path the profile lacks"), ("conformance_level", "full", "a line the review marks not editable"), ("prerequisites[0].status", "deferred", "a gate's status")):
        try:
            wizard.edit(repo, path, value)
            outcome = "edited"
        except wizard.WriteRefused as exc:
            outcome = exc.detail
        check(f"refused: {why}", outcome != "edited" and (path.split(".")[-1].split("[")[0] in outcome or "owner" in outcome), outcome)
    code = cli.main(["adopt", "--target", str(repo), "--edit", "display_name", "Billing", "--because", "shorter"])
    check("the CLI flag exits 0 and applies", code == 0 and yaml.safe_load((repo / wizard.PROFILE_PATH).read_text(encoding="utf-8"))["display_name"] == "Billing", str(code))
    check("the profile still passes the checker", _schema_ok(repo, repo / wizard.PROFILE_PATH))


def test_the_run_opens_with_the_tool_and_the_install_named(tmp: Path) -> None:
    """`F81` / `DR-51` (2). Before the first question the interview is handed what the opening
    screen shows: the tool's name, version, licence and publisher, the installed version and
    anchor, where the profile and its record will be written, and the draft if there is one."""
    from surfaceplate import about
    from surfaceplate.adopt import provenance

    repo = make_installed_repo(tmp, "welcome-repo")
    seed_referenced_files(repo)
    record = json.loads((repo / wizard.INSTALL_RECORD).read_text(encoding="utf-8"))
    first = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS), cancel_before="level")
    try:
        wizard.run(repo, first)
    except Cancelled:
        pass
    check("the interview was opened once before the first stage", len(first.welcomes) == 1 and first.stages[:1] == ["decisions"])
    w = first.welcomes[0]
    check("the welcome names the tool", (w.tool_name, w.tool_version, w.licence, w.publisher) == (about.NAME, about.version(), about.LICENCE, about.PUBLISHER), str(w))
    check("and the install", w.installed_version == record["standard_version"] and w.installed_anchor == record["framework_digest"] and w.installed_at == record["installed_at"])
    check("and where it will write", w.profile_path == wizard.PROFILE_PATH and w.provenance_path == provenance.PROVENANCE_PATH and w.repo == str(repo))
    check("a first run carries no draft", w.draft is None)

    second = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS))
    wizard.run(repo, second)
    w2 = second.welcomes[0]
    check("a resumed run's welcome carries the draft", w2.draft is not None and "identity" in w2.draft.sections and w2.draft.matches, str(w2.draft))
    check("and the resume offer is the same object", second.resume_offers == [w2.draft])


def test_refuses_when_the_tool_and_the_install_differ(tmp: Path) -> None:
    """`F78` / `DR-51` (1). The maintainer's run validated against the schema installed in
    Plutos, which predated the tool, and refused at the review in the validator's words. The
    comparison belongs before the first question: the tool's framework anchor against the
    install record's, both named, the upgrade command given, and nothing asked."""
    from surfaceplate import about

    repo = make_installed_repo(tmp, "mismatch-repo")
    seed_referenced_files(repo)
    record_path = repo / wizard.INSTALL_RECORD
    record = json.loads(record_path.read_text(encoding="utf-8"))
    check("precondition: a fresh install matches the tool", record["framework_digest"] == about.anchor())
    record["framework_digest"] = "0" * 64
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")

    interview = ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS))
    try:
        wizard.run(repo, interview)
        outcome = "ran"
    except wizard.InstallMismatch as exc:
        outcome = str(exc)
    check("adopt refuses before asking anything", outcome != "ran" and not interview.stages, outcome[:120])
    check("the refusal names both digests", "000000000000" in outcome and about.anchor()[:12] in outcome, outcome[:200])
    check("and the upgrade command", "surfaceplate install" in outcome and "--target" in outcome and "--no-hooks" in outcome, outcome)
    try:
        wizard.propose(repo, level="essential")
        proposed = "wrote"
    except wizard.InstallMismatch:
        proposed = "refused"
    check("--propose refuses the same way", proposed == "refused" and not (repo / wizard.ANSWERS_PATH).exists())

    record["framework_digest"] = about.anchor()
    record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    wizard.run(repo, ScriptedInterview(answers=dict(ESSENTIAL_ANSWERS)))
    check("restored, the same run completes", (repo / wizard.PROFILE_PATH).is_file())


def test_package_metadata_agrees_with_pyproject() -> None:
    """`DR-51` (2): the opening screen shows the tool's name, version, licence and publisher
    from one module, and that module is held to `pyproject.toml` here so it cannot drift."""
    import tomllib

    from surfaceplate import about

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    check("about.version() is pyproject's version", about.version() == project["version"], about.version())
    check("about.LICENCE is pyproject's license", about.LICENCE == project["license"], about.LICENCE)
    check("about.PUBLISHER is pyproject's author", about.PUBLISHER in [a.get("name") for a in project.get("authors", [])], about.PUBLISHER)
    check("about.NAME is the package name, capitalised", about.NAME.lower() == project["name"], about.NAME)
    check("about.anchor() is the anchor the installer records", about.anchor() == wizard.install_standard.framework_anchor(about.PACKAGE_DIR))


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


def test_proposing_writes_the_same_profile_as_typing_the_same_values(tmp: Path) -> None:
    """The prototype's claim, reproduced on the real code (report Part II §II.1): the profile a
    run writes with every proposal left standing is line-for-line the profile written when the
    same values are typed. Proposing changes nothing about what is written; and since a value
    submitted unchanged is recorded under its proposal's origin (`DR-47` (3)), the two
    provenance records are the same document too."""
    from surfaceplate.adopt import provenance

    base = {
        "identity.owner": "Owner Person",
        "stack.builds_user_interface": "no",
        "risk.relied_on_outside_team": "yes",
        "risk.material_quantitative_output": "no",
        "risk.data_classification": "internal",
        "wrap.release_route": "Merged to main by the maintainer.",
        "level.conformance_level": "standard",
        "adoption.decision_record_id": "DR-1",
        "controls.scanner.wired_in": "workflows/secret-scan.yml",  # asked: not under .github
    }
    # The same directory NAME in two places, because the id and the display name are proposed
    # from it.
    repo_a = make_installed_repo(tmp / "proposed", "equal")
    seed_referenced_files(repo_a, ci=True)
    proposed = ScriptedInterview(answers=dict(base), bulk_not_applicable=True)
    written_a = wizard.run(repo_a, proposed)
    assert proposed.flow is not None
    typed_values = {
        key: (proposed.flow.state[key.split(".")[0]][key.split(".", 1)[1]])
        for key, origin in proposed.flow.origins.items()
        if origin.kind != "typed" and key.split(".", 1)[1] in proposed.flow.state.get(key.split(".")[0], {})
        # The two prose fields the form leaves optional are "Not stated at adoption." only by
        # being left blank; typing that sentence is a different act and is recorded as one.
        and key not in ("risk.risk_profile", "risk.materiality_definition")
    }
    check("the first run proposed a good share of the profile", len(typed_values) > 15, str(len(typed_values)))

    repo_b = make_installed_repo(tmp / "typed", "equal")
    seed_referenced_files(repo_b, ci=True)
    typed = ScriptedInterview(answers={**typed_values, **base}, bulk_not_applicable=True)
    written_b = wizard.run(repo_b, typed)

    # A scaffolded artefact binds from the instant it was created, which differs between the
    # two runs by however long the first took: a fact of record, normalised for the comparison.
    instant = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}")
    profile_a = instant.sub("INSTANT", written_a.read_text(encoding="utf-8"))
    profile_b = instant.sub("INSTANT", written_b.read_text(encoding="utf-8"))
    check(
        "proposing and typing the same values write the same profile, line for line",
        profile_a == profile_b,
        "\n".join(l for l in profile_a.splitlines() if l not in profile_b.splitlines())[:300],
    )
    record_a = yaml.safe_load((repo_a / provenance.PROVENANCE_PATH).read_text(encoding="utf-8"))
    record_b = yaml.safe_load((repo_b / provenance.PROVENANCE_PATH).read_text(encoding="utf-8"))
    check(
        "and a value submitted unchanged is recorded under its proposal's origin either way",
        {p: f["origin"] for p, f in record_a["fields"].items()} == {p: f["origin"] for p, f in record_b["fields"].items()},
        str([p for p in record_a["fields"] if record_a["fields"][p]["origin"] != record_b["fields"].get(p, {}).get("origin")][:5]),
    )
    check(
        "the record names typed, discovered, example, computed and fact of record among its origins",
        {"typed", "discovered", "example", "computed", "fact of record"} <= {f["origin"] for f in record_a["fields"].values()},
        str(sorted({f["origin"] for f in record_a["fields"].values()})),
    )


def test_fields_presented_before_the_review_are_measured(tmp: Path) -> None:
    """`DR-47`'s budget, measured on the two fixtures the prototype used rather than estimated:
    a repository with things to discover at standard, and a bare one at essential. The count is
    the fields presented as a form before the review; the gate list is counted separately
    (report Part II §II.4). Phase 3 turns the numbers into the budget test; this records them."""
    from surfaceplate.adopt import flow as _flow
    from surfaceplate.adopt.interview import ScriptedInterview

    def measure(repo: Path, level: str, relied: str) -> tuple[int, int, list[str]]:
        flow = _flow.Flow(repo, {"standard_version": "0.16.0", "framework_digest": "x"})
        interview = ScriptedInterview(
            answers={
                "identity.owner": "O", "stack.builds_user_interface": "no",
                "risk.relied_on_outside_team": relied, "risk.material_quantitative_output": "no",
                "risk.data_classification": "internal", "wrap.release_route": "R",
                "level.conformance_level": level,
            },
            bulk_not_applicable=True,
        )
        original = interview._answer

        def answer_everything(section, prefix=""):
            # The script answers whatever a form presents - a real path where git is asked,
            # a word otherwise - so the run reaches the review and every presented field counts.
            for spec in section.fields:
                key = f"{prefix}{spec.id}"
                if key in interview.answers or spec.default or not spec.validate or spec.kind not in ("text", "textarea"):
                    continue  # a pre-filled proposal is submitted unchanged
                if spec.validate.startswith("scanner_workflow"):
                    # `DR-51` (5): the field applies SP046's rule, so the answer is a real
                    # workflow where a step runs the scanner, committed.
                    scan = repo / ".github" / "workflows" / "budget-scan.yml"
                    scan.parent.mkdir(parents=True, exist_ok=True)
                    scan.write_text("jobs:\n  s:\n    steps:\n      - name: Run gitleaks\n        run: gitleaks detect\n", encoding="utf-8")
                    _commit_all(repo, "scan workflow")
                    interview.answers[key] = ".github/workflows/budget-scan.yml"
                    continue
                interview.answers[key] = "main.py" if spec.validate == "tracked_path" else f"answer for {key}"
            return original(section, prefix)

        interview._answer = answer_everything  # type: ignore[method-assign]
        interview.collect(flow, on_progress=lambda: None)
        presented = [k for k in interview.asked if not k.startswith("gates.")]
        gate_keys = [k for k in interview.asked if k.startswith("gates.")]
        return len(presented), len(gate_keys), presented

    rich = make_installed_repo(tmp, "budget-standard")
    seed_referenced_files(rich)
    (rich / "src").mkdir(); (rich / "src" / "app.py").write_text("x=1\n", encoding="utf-8")
    (rich / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (rich / ".github" / "workflows" / "ci.yml").write_text(
        "jobs:\n  t:\n    steps:\n      - name: Run the tests\n        run: pytest\n", encoding="utf-8")
    _commit_all(rich, "rich")
    bare = make_installed_repo(tmp, "budget-bare")
    (bare / "main.py").write_text("x = 1\n", encoding="utf-8")
    _commit_all(bare, "bare")
    (rich / "main.py").write_text("x = 1\n", encoding="utf-8")
    _commit_all(rich, "main")

    n_std, g_std, fields_std = measure(rich, "standard", "yes")
    n_ess, g_ess, fields_ess = measure(bare, "essential", "no")
    print(f"      measured: standard/discoverable {n_std} fields before the review ({g_std} gate fields); essential/bare {n_ess} ({g_ess})")
    print(f"      standard: {fields_std}")
    print(f"      essential/bare: {fields_ess}")
    # `ACT-046` (plan item 3.2): the budget test asserts the MEASURED numbers, not an estimate.
    # Measured on 2026-09-02 on these two fixtures: 11 and 12, both within DR-47's eight to twelve.
    # A change to either is a change to what the wizard asks, and belongs in a decision record.
    # `DR-51` (5), the same day: the scanner workflow is asked when no workflow RUNS the scanner,
    # not when none exists. The rich fixture's `ci.yml` runs pytest, not gitleaks, so it is now
    # asked there too: 11 became 12 (re-measured; the bare fixture already asked it).
    check("standard with things to discover: twelve fields before the review, as measured under DR-51 (5)", n_std == 12, str(n_std))
    check("essential on a bare repository: twelve fields before the review, as measured", n_ess == 12, str(n_ess))


def test_propose_writes_a_proposal_and_never_the_profile(tmp: Path) -> None:
    """`DR-49` (3) / R4. `adopt --propose` runs discovery and writes the proposed profile and the
    answers record with every undecided decision marked `needs-human`; it never writes the
    profile, so the checker never reads a tool-authored declaration."""
    from surfaceplate.adopt import provenance

    repo = make_installed_repo(tmp, "propose-repo")
    seed_referenced_files(repo, ci=True)
    template = (repo / "governance" / "application-profile.yaml").read_text(encoding="utf-8")
    written = wizard.propose(repo, level="standard")
    check(
        "--propose writes the proposed profile and the answers record",
        written.proposed.is_file() and written.answers.is_file(),
        str(written),
    )
    check(
        "and never the profile itself",
        (repo / "governance" / "application-profile.yaml").read_text(encoding="utf-8") == template
        and not (repo / provenance.PROVENANCE_PATH).exists(),
    )
    record = yaml.safe_load(written.answers.read_text(encoding="utf-8"))
    answers = record["answers"]
    needs = [k for k, v in answers.items() if v == wizard.NEEDS_HUMAN]
    check(
        "every decision only a human can make is marked needs-human",
        {"identity.owner", "stack.builds_user_interface", "risk.data_classification", "wrap.release_route"} <= set(needs)
        and all(k.endswith(".status") for k in needs if k.startswith("gates.") and k.endswith(".status")),
        str(sorted(needs)[:8]),
    )
    check(
        "no gate status is proposed - each undecided gate is a needs-human line",
        any(k.startswith("gates.") and k.endswith(".status") for k in needs)
        and not any(k.endswith(".status") and v != wizard.NEEDS_HUMAN for k, v in answers.items()),
    )
    proposed = {k: v for k, v in answers.items() if isinstance(v, dict)}
    check(
        "every proposal carries its value and origin",
        proposed and all({"value", "origin"} <= set(v) for v in proposed.values())
        and all(v["origin"] != "typed" for v in proposed.values()),
        str(list(proposed.items())[:2]),
    )
    check("the level given on the command line is the human's and is recorded as the level", record["level"] == "standard", str(record.get("level")))
    text = written.proposed.read_text(encoding="utf-8")
    check("the proposed profile says what it is at the top", "PROPOSED" in text.splitlines()[0].upper(), text.splitlines()[0])


def test_answers_replays_a_completed_record_through_the_same_code(tmp: Path) -> None:
    """`DR-49` (3): `adopt --answers <file>` replays a human-completed record through the same
    `plan`, `sections` and `_verify` code as the interface and writes the profile; a record with
    a `needs-human` line left in it refuses to write anything."""
    from surfaceplate.adopt import provenance

    repo = make_installed_repo(tmp, "answers-repo")
    seed_referenced_files(repo, ci=True)
    proposal = wizard.propose(repo, level="standard")
    record = yaml.safe_load(proposal.answers.read_text(encoding="utf-8"))
    try:
        wizard.replay(repo, proposal.answers)
        outcome = "wrote"
    except wizard.NeedsHuman as exc:
        outcome = f"refused: {exc}"
    check("a record with needs-human lines is refused", outcome.startswith("refused"), outcome)
    check("and nothing was written", not (repo / provenance.PROVENANCE_PATH).exists())

    # A human completes the record.
    human = {
        "identity.owner": "Owner Person",
        "stack.builds_user_interface": "no",
        "risk.relied_on_outside_team": "yes",
        "risk.material_quantitative_output": "no",
        "risk.data_classification": "internal",
        "wrap.release_route": "Merged to main by the maintainer.",
        "adoption.decision_record_id": "DR-1",
        "create_missing_artefacts": "yes",
    }
    for key, value in record["answers"].items():
        if value == wizard.NEEDS_HUMAN:
            if key in human:
                record["answers"][key] = human[key]
            elif key.endswith(".status"):
                record["answers"][key] = "not_applicable"
            else:
                record["answers"][key] = f"answer for {key}"
    record["level"] = "standard"
    completed = repo / "answers-completed.yaml"
    completed.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True), encoding="utf-8")
    written = wizard.replay(repo, completed)
    check("a completed record writes the profile", written.is_file())
    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    check(
        "with the human's answers and the proposals both in it",
        data["owner"] == "Owner Person" and data["conformance_level"] == "standard"
        and data["adoption"]["decision_record_id"] == "DR-1",
        str({k: data.get(k) for k in ("owner", "conformance_level")}),
    )
    sidecar = yaml.safe_load((repo / provenance.PROVENANCE_PATH).read_text(encoding="utf-8"))
    check(
        "and the provenance record says which values were typed by the human and which were proposed",
        sidecar["fields"]["owner"]["origin"] == "typed"
        and sidecar["fields"]["adoption.framework_maintainer"]["origin"] == "computed",
        str({k: sidecar["fields"][k] for k in ("owner", "adoption.framework_maintainer")}),
    )
    # The same values through the scripted interview write the same profile: one code path.
    repo_b = make_installed_repo(tmp / "b", "answers-repo")
    seed_referenced_files(repo_b, ci=True)
    scripted = {k: v for k, v in record["answers"].items() if not isinstance(v, dict)}
    scripted = {k: v for k, v in scripted.items() if not k.endswith(".status") and k != "create_missing_artefacts"}
    scripted["level.conformance_level"] = record["level"]
    interview = ScriptedInterview(answers=scripted, bulk_not_applicable=True)
    written_b = wizard.run(repo_b, interview)
    instant = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}")
    check(
        "replay and the interface write the same profile from the same answers",
        instant.sub("I", written.read_text(encoding="utf-8")) == instant.sub("I", written_b.read_text(encoding="utf-8")),
        "\n".join(l for l in written.read_text(encoding="utf-8").splitlines() if l not in written_b.read_text(encoding="utf-8").splitlines())[:300],
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
    (repo / "empty.md").write_text("", encoding="utf-8")
    (repo / "unfinished.md").write_text("# Register\n\nTODO: fill in\n", encoding="utf-8")
    (repo / "ci.yml").write_text("jobs:\n  t:\n    steps:\n      - name: Tests\n        run: pytest\n", encoding="utf-8")
    (repo / "comment.yml").write_text("# gitleaks runs elsewhere\njobs:\n  t:\n    steps:\n      - name: Tests\n        run: pytest\n", encoding="utf-8")
    (repo / "scan.yml").write_text("jobs:\n  s:\n    steps:\n      - name: Run gitleaks\n        run: gitleaks detect\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "tracked.md", "empty.md", "unfinished.md", "ci.yml", "comment.yml", "scan.yml"], check=True)
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
        ("tracked_path", "empty.md", "SP032: exists but is empty"),
        ("tracked_path", "unfinished.md", "SP032: still carries a placeholder"),
        ("scanner_workflow:gitleaks", "ci.yml", "SP046: the workflow never mentions the scanner"),
        ("scanner_workflow:gitleaks", "comment.yml", "SP046: mentioned in a comment, no step runs it"),
        ("scanner_workflow:gitleaks", "untracked.md", "SP046: not tracked"),
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
        ("scanner_workflow:gitleaks", "scan.yml"),
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
    # `DR-51` (5): a tracked workflow that never mentions the scanner, and a tracked artefact
    # that still carries a placeholder - each is what the checker rejects and the field now refuses.
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("jobs:\n  t:\n    steps:\n      - name: Tests\n        run: pytest\n", encoding="utf-8")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "unfinished.md").write_text("# Register\n\nTBD\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "install"], check=True)
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
        "SP032": (V, "tracked_path", "docs/unfinished.md"),
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
        "SP046": (V, "scanner_workflow:gitleaks", ".github/workflows/ci.yml"),
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
        "SP059": (V, "tracked_path", ".standards/VERSION"),
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

        print("\nDR-47: the wizard proposes, and says where each value came from")
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
        test_the_draft_lives_under_standards_and_an_old_one_is_migrated(tmp)

        print("\nrefusals, and the guarantee itself")
        test_every_presented_field_states_what_it_decides_and_what_a_wrong_answer_costs(tmp)
        test_a_schema_refusal_names_the_profile_line(tmp)
        test_the_profile_is_written_atomically(tmp)
        test_a_draft_with_stale_ids_is_not_resumed_into_a_crash(tmp)
        test_the_create_it_row_leads_to_a_scaffold_for_gates_and_controls(tmp)
        test_adopt_edit_rewrites_one_line_and_records_it(tmp)
        test_the_run_opens_with_the_tool_and_the_install_named(tmp)
        test_refuses_when_the_tool_and_the_install_differ(tmp)
        test_package_metadata_agrees_with_pyproject()
        test_refuses_without_install(tmp)
        test_refuses_to_overwrite_a_real_profile(tmp)
        test_a_real_profile_that_mentions_the_token_is_not_the_template(tmp)
        test_the_untouched_template_is_still_fair_game(tmp)
        test_write_refused_on_placeholder_content(essential_repo, essential_profile)
        test_scripted_interview_objects_in_both_directions(tmp)

        print("\nDR-47: proposing writes what typing writes; the budget, measured")
        test_proposing_writes_the_same_profile_as_typing_the_same_values(tmp)
        test_fields_presented_before_the_review_are_measured(tmp)

        print("\nDR-49: adoption without a terminal - propose, then replay the human's answers")
        test_propose_writes_a_proposal_and_never_the_profile(tmp)
        test_answers_replays_a_completed_record_through_the_same_code(tmp)

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
