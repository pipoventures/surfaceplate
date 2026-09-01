#!/usr/bin/env python3
"""End-to-end tests for `surfaceplate adopt`.

No test framework required; run it directly:

    python tests/test_adopt.py

These exist to make the binding rule checkable, not just stated: `org/RELEASE_PLAN.md` says the
wizard "asks, the human answers, the tool writes" and never selects a level, invents a rationale,
or sets a date. `ScriptedPrompt` (surfaceplate/adopt/prompting.py) is what makes that a property a
test can fail on - it raises if the wizard asks for more than the script provides, and
`assert_exhausted()` raises if the script provides more than the wizard asked for. Together: nothing
missing, nothing extra, and every value in the written profile traces to something in `answers`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAYLOAD = ROOT / "surfaceplate"  # the package itself - see surfaceplate/__init__.py

# Unlike test_install_and_check.py, which imports install_standard.py/check_conformance.py as
# flat top-level modules (they have no internal package-relative imports), this suite's target
# code uses real `surfaceplate.xxx` imports throughout (catalogue.py reads
# `from surfaceplate import check_conformance`; wizard.py does the same for its placeholder
# check). ROOT, not PAYLOAD, must be on sys.path so `import surfaceplate` resolves to the real
# package rather than failing or - worse - silently resolving to some other installed copy.
sys.path.insert(0, str(ROOT))

from surfaceplate.adopt import catalogue, wizard  # noqa: E402
from surfaceplate.adopt.prompting import Cancelled, ScriptedPrompt  # noqa: E402

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
        [sys.executable, str(PAYLOAD / "install_standard.py"), "--target", str(repo), "--no-hooks"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"fixture install failed:\n{result.stdout}\n{result.stderr}"
    return repo


class InterruptAfter:
    """A `Prompt` that answers the first `count` questions from `answers`, then cancels - for
    proving an interrupt leaves the repository untouched, regardless of where it lands."""

    def __init__(self, answers: list[object], count: int) -> None:
        self._answers = answers
        self._count = count
        self._asked = 0

    def _next(self) -> object:
        self._asked += 1
        if self._asked > self._count:
            raise Cancelled()
        return self._answers[self._asked - 1]

    def text(self, message: str, *, help: str | None = None, default: str = "") -> str:
        return self._next()  # type: ignore[return-value]

    def select(self, message: str, choices: list[tuple[str, str]], *, help: str | None = None) -> str:
        return self._next()  # type: ignore[return-value]

    def confirm(self, message: str, *, help: str | None = None, default: bool | None = None) -> bool:
        return self._next()  # type: ignore[return-value]


# ---------------------------------------------------------------------------------------------
# Fixture: an exact, hand-verified answer sequence for an `essential`-level run with no UI.
# ---------------------------------------------------------------------------------------------

ESSENTIAL_ANSWERS: list[object] = [
    "billing-reconciler", "Billing Reconciler", "Finance Platform team",  # identity
    "Python 3.12", False,  # stack, builds_user_interface
    "Reconciles daily settlement files against the ledger; no external users.",  # risk_profile
    "A reconciliation result reaching the finance team's own review queue is material.",
    "internal",  # data_classification
    "essential",  # conformance_level
    "All agent-assisted work is bounded, scoped, and reviewable.",  # agent_work_packets rationale
    "Material changes are reviewed against their actual diff content.",  # actual_diff_review rationale
    "Secrets and sensitive data must not enter uncontrolled storage.",  # secret_hygiene rationale
    "gitleaks", "workflows/secret-scan.yml",  # scanner
    "Supply-chain exposure exists regardless of output materiality.", "requirements.txt",  # dependency_lock
    False,  # declare more controls
    "docs/DEVELOPMENT_REGISTER.md",  # work_registration artefact
    "An identified, registered activity before implementation begins.",
    "src/**", "Implementation work in the source tree.",
    "2026-09-01", "history_audit, review",
    "2027-02-28", "Finance Platform team", "internal-service", "DR-FIN-001",  # adoption identity
    "in_progress", False,  # adoption_status, needs_validator
    "", "Merges to main require review; deploys are manual.",  # roles (blank), release_route
    True,  # final write confirm
]


def build_full_ui_answers() -> list[object]:
    """Generates a scripted answer sequence for a `full`-level, UI-building run by walking the
    same catalogue data the wizard itself asks against. This is a FIXTURE BUILDER, not a
    correctness oracle: the test below asserts real properties of the WRITTEN profile (every
    mandatory gate is `required`, the schema validates, counts match the catalogue) rather than
    trusting that generating the sequence this way proves anything by itself. Building it by hand
    (~150 answers) was tried first and is exactly the kind of error-prone busywork this avoids
    without weakening what the test actually checks.
    """
    answers: list[object] = [
        "payments-orchestrator", "Payments Orchestrator", "Payments team",
        "Python 3.12, React", True,  # stack, builds_user_interface
        "Routes and settles customer payments across three providers.",
        "A misrouted or double-settled payment is material to customers and to the ledger.",
        "confidential",
        "full",
        "All agent-assisted work is bounded, scoped, and reviewable.",  # agent_work_packets rationale
        "Material changes are reviewed against their actual diff content.",  # actual_diff_review rationale
        "Secrets and sensitive data must not enter uncontrolled storage.",  # secret_hygiene rationale
        "gitleaks", "workflows/secret-scan.yml",
    ]
    for control_id in sorted(catalogue.CONFORMANCE_LEVELS["full"]):
        answers.append(f"{control_id} applies because this system produces material output.")
        if (
            control_id in catalogue.PATTERN_A_CONTROLS
            or control_id in catalogue.PATTERN_B_CONTROLS
            or control_id in catalogue.PATTERN_C_CONTROLS
        ):
            answers.append(f"path/for-{control_id.replace('_', '-')}")
    answers.append(False)  # declare more controls

    mandatory = set(catalogue.LEVEL_REQUIRED_GATES["full"]) | catalogue.DESIGN_GATES
    for _section_name, gate_ids in catalogue.sectioned_gates():
        for gate_id in gate_ids:
            if gate_id in mandatory:
                answers += [
                    f"artefact-for-{gate_id}", f"precondition for {gate_id}",
                    "src/**", f"gated activity for {gate_id}",
                    "2026-09-01", "history_audit, review",
                ]
            else:
                answers.append("not_applicable")
                answers.append(f"not applicable here: {gate_id}")

    answers += [
        "2027-02-28", "Payments team", "customer-facing", "DR-PAY-001",
        "in_progress", False,  # adoption_status, needs_validator
        "", "Merges require two reviewers; deploys are automated behind a feature flag.",
        True,  # final write confirm
    ]
    return answers


def build_standard_no_ui_answers() -> list[object]:
    """A `standard`-level, no-UI run - the one combination that exercises the ACT-022 fix to the
    four `DESIGN_GATES` auto-`not_applicable` rationale, which no other fixture in this file
    reaches: `ESSENTIAL_ANSWERS` never walks the full catalogue, and `build_full_ui_answers`
    always has `builds_user_interface=True`, so the auto-mask branch never ran in either. Before
    ACT-022 this branch wrote its rationale with no `Prompt` call at all - a scripted test could
    not have caught that, because `ScriptedPrompt` only objects to a call it wasn't given an
    answer for, never to a value written without any call. See `test_adopt.py`'s own minor-finding
    note on this in `test_design_gates_rationale_is_asked`.
    """
    answers: list[object] = [
        "internal-tool", "Internal Tool", "Platform team",
        "Python 3.12", False,  # stack, builds_user_interface
        "An internal batch service with no external users.",
        "A failed batch run reaching production data is material.",
        "internal",
        "standard",
        # Deliberately worded differently from the old hardcoded strings this fixture exists to
        # prove are gone - see test_design_gates_rationale_is_asked's own docstring for why.
        "Platform team requires every agent packet to name its own scope and reviewer.",
        "Platform team's review checklist reads the diff, never a summary of it.",
        "Platform team's own scanner policy applies to every repository it owns.",
        "gitleaks", "workflows/secret-scan.yml",
    ]
    for control_id in sorted(catalogue.CONFORMANCE_LEVELS["standard"]):
        answers.append(f"{control_id} applies at the standard floor.")
        if (
            control_id in catalogue.PATTERN_A_CONTROLS
            or control_id in catalogue.PATTERN_B_CONTROLS
            or control_id in catalogue.PATTERN_C_CONTROLS
        ):
            answers.append(f"path/for-{control_id.replace('_', '-')}")
    answers.append(False)  # declare more controls

    mandatory = set(catalogue.LEVEL_REQUIRED_GATES["standard"])  # no DESIGN_GATES: no UI
    for _section_name, gate_ids in catalogue.sectioned_gates():
        for gate_id in gate_ids:
            if gate_id in catalogue.DESIGN_GATES:
                answers.append(f"not applicable: no user interface ({gate_id})")
            elif gate_id in mandatory:
                answers += [
                    f"artefact-for-{gate_id}", f"precondition for {gate_id}",
                    "src/**", f"gated activity for {gate_id}",
                    "2026-09-01", "history_audit, review",
                ]
            else:
                answers.append("not_applicable")
                answers.append(f"not applicable here: {gate_id}")

    answers += [
        "2027-02-28", "Platform team", "internal-service", "DR-INT-001",
        "in_progress", False,  # adoption_status, needs_validator
        "", "Merges require one reviewer; deploys are manual.",
        True,  # final write confirm
    ]
    return answers


# ---------------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------------


def test_catalogue_sections_sum_to_the_whole_catalogue() -> None:
    total = sum(len(ids) for _, ids in catalogue.sectioned_gates())
    check(
        "catalogue sections sum to the full 19-gate catalogue",
        total == len(catalogue.GATE_CATALOGUE),
        f"sections sum to {total}, GATE_CATALOGUE has {len(catalogue.GATE_CATALOGUE)}",
    )
    names = [name for name, _ in catalogue.sectioned_gates()]
    check(
        "sections have no duplicate gate IDs",
        len(set(g for _, ids in catalogue.sectioned_gates() for g in ids))
        == sum(len(ids) for _, ids in catalogue.sectioned_gates()),
        f"section names: {names}",
    )


def test_essential_end_to_end(tmp: Path) -> tuple[Path, dict]:
    repo = make_installed_repo(tmp, "essential-repo")
    # The dependency_lock artefact and the scanner workflow both need to exist for a clean
    # checker pass afterwards - seeded from the same answers the script above provides.
    (repo / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "DEVELOPMENT_REGISTER.md").write_text("# Register\n", encoding="utf-8")
    (repo / "workflows").mkdir()
    (repo / "workflows" / "secret-scan.yml").write_text("name: scan\n", encoding="utf-8")

    prompt = ScriptedPrompt(answers=list(ESSENTIAL_ANSWERS))
    written = wizard.run(repo, prompt)

    try:
        prompt.assert_exhausted()
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

    result = subprocess.run(
        [sys.executable, str(repo / ".standards" / "check_conformance.py"), "--repo", str(repo)],
        capture_output=True,
        text=True,
    )
    schema_findings = [ln for ln in result.stdout.splitlines() if ln.strip().startswith("[SP0") and "SP04" not in ln and "SP05" not in ln]
    check(
        "the real checker raises no schema-shape findings against the written profile",
        not schema_findings,
        "\n".join(schema_findings) or result.stdout[-600:],
    )
    return repo, data


def test_full_ui_end_to_end(tmp: Path) -> None:
    repo = make_installed_repo(tmp, "full-repo")
    answers = build_full_ui_answers()
    prompt = ScriptedPrompt(answers=list(answers))
    written = wizard.run(repo, prompt)

    try:
        prompt.assert_exhausted()
        check("full+UI run: every scripted answer was used", True)
    except AssertionError as exc:
        check("full+UI run: every scripted answer was used", False, str(exc))

    import yaml

    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    check("full+UI run: builds_user_interface recorded as typed", data.get("builds_user_interface") is True)
    check(
        "full+UI run: all 19 gates present",
        len(data.get("prerequisites", [])) == len(catalogue.GATE_CATALOGUE),
        str(len(data.get("prerequisites", []))),
    )
    mandatory = set(catalogue.LEVEL_REQUIRED_GATES["full"]) | catalogue.DESIGN_GATES
    by_id = {g["id"]: g for g in data["prerequisites"]}
    wrongly_declinable = [
        gid for gid in mandatory if by_id.get(gid, {}).get("status") != "required"
    ]
    check(
        "every level-mandatory gate is required - never deferred or not_applicable",
        not wrongly_declinable,
        str(wrongly_declinable),
    )
    check(
        "full level declares all 9 controls this level requires",
        set(data.get("control_decisions", {})) == set(catalogue.CONFORMANCE_LEVELS["full"]),
        str(set(data.get("control_decisions", {}))),
    )

    schema_path = repo / ".standards" / "schemas" / "application-profile.schema.yaml"
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    import jsonschema

    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(data))
    check("the full+UI profile validates against its own schema", not errors, "; ".join(e.message for e in errors[:5]))


def test_design_gates_rationale_is_asked(tmp: Path) -> None:
    """ACT-022: a Gemini adversarial review (ACT-021) found that `sections.py` wrote a fixed
    rationale string for the three baseline controls and for the four DESIGN_GATES it
    auto-marks `not_applicable` when `builds_user_interface` is false - none of it routed
    through `Prompt`, contradicting this package's own binding rule. Proven here by scripting
    rationale text that DIFFERS from the old hardcoded strings and asserting the written profile
    contains exactly the scripted text - a value present in the output that never matches
    anything hardcoded in the source is proof it came from the script, not a fallback."""
    repo = make_installed_repo(tmp, "standard-no-ui-repo")
    answers = build_standard_no_ui_answers()
    prompt = ScriptedPrompt(answers=list(answers))
    written = wizard.run(repo, prompt)

    try:
        prompt.assert_exhausted()
        check("standard/no-UI run: every scripted answer was used", True)
    except AssertionError as exc:
        check("standard/no-UI run: every scripted answer was used", False, str(exc))

    import yaml

    data = yaml.safe_load(written.read_text(encoding="utf-8"))

    scripted_baseline_rationales = {
        "agent_work_packets": "Platform team requires every agent packet to name its own scope and reviewer.",
        "actual_diff_review": "Platform team's review checklist reads the diff, never a summary of it.",
        "secret_hygiene": "Platform team's own scanner policy applies to every repository it owns.",
    }
    for control_id, expected in scripted_baseline_rationales.items():
        got = data["baseline_controls"][control_id]["rationale"]
        check(f"{control_id}: rationale matches the scripted answer exactly", got == expected, got)

    by_id = {g["id"]: g for g in data["prerequisites"]}
    design_gate_rationales_are_scripted = all(
        by_id[gid]["status"] == "not_applicable"
        and by_id[gid]["rationale"] == f"not applicable: no user interface ({gid})"
        for gid in catalogue.DESIGN_GATES
    )
    check(
        "all four DESIGN_GATES carry the scripted rationale, not the old fixed string",
        design_gate_rationales_are_scripted,
        str({gid: by_id.get(gid, {}).get("rationale") for gid in catalogue.DESIGN_GATES}),
    )

    schema_path = repo / ".standards" / "schemas" / "application-profile.schema.yaml"
    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    import jsonschema

    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = list(validator.iter_errors(data))
    check("the standard/no-UI profile validates against its own schema", not errors, "; ".join(e.message for e in errors[:5]))


def test_interrupt_leaves_repo_untouched(tmp: Path) -> None:
    repo = make_installed_repo(tmp, "interrupt-repo")
    before_profile = (repo / "governance" / "application-profile.yaml").read_text(encoding="utf-8")
    before_files = {p.relative_to(repo) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}

    prompt = InterruptAfter(list(ESSENTIAL_ANSWERS), count=5)  # cancels partway through section 2
    try:
        wizard.run(repo, prompt)
        check("an interrupt raises Cancelled", False, "wizard.run returned instead of raising")
    except Cancelled:
        check("an interrupt raises Cancelled", True)

    after_profile = (repo / "governance" / "application-profile.yaml").read_text(encoding="utf-8")
    after_files = {p.relative_to(repo) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}
    check("the profile is byte-for-byte unchanged after an interrupt", before_profile == after_profile)
    check(
        "no stray file was left behind by the interrupted run",
        before_files == after_files,
        f"new files: {after_files - before_files}",
    )


def test_refuses_without_install(tmp: Path) -> None:
    repo = tmp / "no-install-repo"
    repo.mkdir()
    try:
        wizard.run(repo, ScriptedPrompt(answers=[]))
        check("adopt refuses a repository without .standards/INSTALL.json", False, "no exception raised")
    except wizard.NotInstalled:
        check("adopt refuses a repository without .standards/INSTALL.json", True)


def test_refuses_to_overwrite_a_real_profile(tmp: Path) -> None:
    repo = make_installed_repo(tmp, "already-adopted-repo")
    real_profile = repo / "governance" / "application-profile.yaml"
    real_profile.write_text("application_id: already-here\nowner: Someone\n", encoding="utf-8")
    try:
        wizard.run(repo, ScriptedPrompt(answers=[]))
        check("adopt refuses to overwrite a real (non-template) profile", False, "no exception raised")
    except wizard.AlreadyAdopted:
        check("adopt refuses to overwrite a real (non-template) profile", True)
    check(
        "the existing profile was left untouched",
        real_profile.read_text(encoding="utf-8") == "application_id: already-here\nowner: Someone\n",
    )


def test_write_refused_on_placeholder_content(repo: Path, valid_profile: dict) -> None:
    """Mutates a profile that has already been proven schema-valid (the essential fixture) so
    the ONLY thing wrong with it is the placeholder token - otherwise schema validation, which
    `_verify` runs first, would refuse it for an unrelated reason and this would test nothing."""
    from surfaceplate.adopt import render
    from surfaceplate.adopt import wizard as _w

    corrupted = json.loads(json.dumps(valid_profile))  # cheap deep copy
    corrupted["owner"] = "TBD - fill this in later"
    rendered = render.render_profile(corrupted)
    try:
        _w._verify(corrupted, rendered, repo)
        check("_verify refuses a profile carrying a template placeholder token", False, "no exception raised")
    except _w.WriteRefused as exc:
        check("_verify refuses a profile carrying a template placeholder token", "placeholder" in exc.detail, exc.detail)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)

        print("catalogue")
        test_catalogue_sections_sum_to_the_whole_catalogue()

        print("\nessential-level end to end")
        essential_repo, essential_profile = test_essential_end_to_end(tmp)

        print("\nfull-level, UI-building end to end")
        test_full_ui_end_to_end(tmp)

        print("\nstandard-level, no-UI end to end (ACT-022: DESIGN_GATES rationale is asked)")
        test_design_gates_rationale_is_asked(tmp)

        print("\ninterrupt mid-flow")
        test_interrupt_leaves_repo_untouched(tmp)

        print("\nrefusals")
        test_refuses_without_install(tmp)
        test_refuses_to_overwrite_a_real_profile(tmp)
        test_write_refused_on_placeholder_content(essential_repo, essential_profile)

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
