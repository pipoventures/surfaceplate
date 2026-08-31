"""Positive and negative conformance checks for the JSON Schema contracts."""
from copy import deepcopy
from pathlib import Path
import re
import sys

import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLES_DIR = ROOT / "examples"
NAMESPACE_DOC = ROOT / "NAMESPACE.md"
FORMAT_CHECKER = FormatChecker()

# The schema identity namespace is DECLARED in NAMESPACE.md and DERIVED here. There is
# deliberately no namespace literal in this file.
#
# Until 0.12.0 this module held its own copy of the base. That copy agreed with the
# schemas by construction and so could never disagree with the document that governs
# them: NAMESPACE.md claimed the version segment was the framework version and drifted
# four releases from the schemas without this check noticing. Reading the declaration
# instead of restating it means a divergence between the rule and the schemas fails here
# rather than passing.

# Executed-check count. Reported on success so that "everything passed" is distinguishable
# from "nothing ran" -- finding F3 in DR-5. A conformance script whose output cannot tell
# those two apart is not evidence of anything.
CHECKS = 0

BASE_GRAMMAR = re.compile(r"^urn:[a-z0-9][a-z0-9-]*(?::[a-z0-9][a-z0-9-]*)+:\d+\.\d+\.\d+:$")
TEXT_BLOCK = re.compile(r"^```text\n(.*?)\n```$", re.MULTILINE | re.DOTALL)


def read_declared_namespace() -> str:
    """Return the schema namespace base that NAMESPACE.md declares.

    NAMESPACE.md states the base twice: as a pattern carrying `<placeholder>` segments,
    and as the concrete current value. Both are read, and they must agree. Every failure
    below is raised, never tolerated: a source of truth this module cannot parse is not a
    reason to fall back on an assumption, because an assumption is exactly the blindness
    this function exists to remove.
    """
    if not NAMESPACE_DOC.is_file():
        raise AssertionError(f"{NAMESPACE_DOC.name} is missing; the namespace is undeclared")

    blocks = [b.strip() for b in TEXT_BLOCK.findall(NAMESPACE_DOC.read_text(encoding="utf-8"))]
    if len(blocks) != 2:
        raise AssertionError(
            f"{NAMESPACE_DOC.name} must declare exactly two ```text blocks - the base "
            f"pattern and the current base - but declares {len(blocks)}. The namespace "
            f"cannot be derived from it."
        )
    pattern, current = blocks

    if "<" not in pattern:
        raise AssertionError(
            f"{NAMESPACE_DOC.name}: the first ```text block should be the base pattern, "
            f"carrying <placeholder> segments, but is '{pattern}'"
        )
    prefix = pattern.split("<", 1)[0]

    if not BASE_GRAMMAR.match(current):
        raise AssertionError(
            f"{NAMESPACE_DOC.name} declares the current base '{current}', which is not a "
            f"URN of the form urn:<org>:<product>:<schema-contract-version>: - see the "
            f"'Version in the identifier' section."
        )
    if not current.startswith(prefix):
        raise AssertionError(
            f"{NAMESPACE_DOC.name} contradicts itself: the current base '{current}' does "
            f"not follow its own declared pattern '{pattern}'."
        )
    return current


NAMESPACE_BASE = read_declared_namespace()

# Controls each conformance level requires, beyond the three baseline controls.
# See core/CONFORMANCE_LEVELS.md. Levels are cumulative.
CONFORMANCE_LEVELS = {
    "essential": {"dependency_lock"},
    "standard": {
        "dependency_lock",
        "deterministic_tests",
        "contract_tests",
        "documentation_authority",
    },
    "full": {
        "dependency_lock",
        "deterministic_tests",
        "contract_tests",
        "documentation_authority",
        "provenance",
        "run_lineage",
        "method_registry",
        "overrides",
        "assurance_findings",
    },
}


def load_schema(name: str) -> dict:
    with (SCHEMA_DIR / name).open(encoding="utf-8") as handle:
        schema = yaml.safe_load(handle)
    Draft202012Validator.check_schema(schema)
    return schema


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(name), format_checker=FORMAT_CHECKER)


def assert_valid(name: str, instance: dict) -> None:
    global CHECKS
    CHECKS += 1
    validator(name).validate(instance)


def assert_invalid(name: str, instance: dict) -> None:
    global CHECKS
    CHECKS += 1
    try:
        validator(name).validate(instance)
    except ValidationError:
        return
    raise AssertionError(f"Expected {name} instance to be invalid")


# --- Semantic rules the schema cannot express -------------------------------------
# A JSON Schema cannot check a value in one field against a set of keys in another.
# These rules are therefore enforced here. A schema file is not enforcement; this is.


class SemanticError(AssertionError):
    """A profile is schema-valid but breaks a cross-field control rule."""


def check_conformance_level(profile: dict) -> None:
    """The declared level's controls must all be present and decided `required`."""
    global CHECKS
    CHECKS += 1
    level = profile["conformance_level"]
    decisions = profile.get("control_decisions", {})
    for control_id in sorted(CONFORMANCE_LEVELS[level]):
        entry = decisions.get(control_id)
        if entry is None:
            raise SemanticError(
                f"conformance_level '{level}' requires control '{control_id}', "
                f"which is absent from control_decisions"
            )
        if entry.get("decision") != "required":
            raise SemanticError(
                f"conformance_level '{level}' requires control '{control_id}' to be "
                f"'required', found '{entry.get('decision')}'"
            )


def check_deferrals_recorded(profile: dict) -> None:
    """Every control decided `deferred` must appear in adoption.deferrals with an owner."""
    global CHECKS
    CHECKS += 1
    deferred = {
        cid
        for cid, entry in profile.get("control_decisions", {}).items()
        if entry.get("decision") == "deferred"
    }
    recorded = {d["control_id"] for d in profile.get("adoption", {}).get("deferrals", [])}
    missing = deferred - recorded
    if missing:
        raise SemanticError(
            f"controls deferred without an owned entry in adoption.deferrals: "
            f"{sorted(missing)}"
        )


def check_profile(profile: dict) -> None:
    assert_valid("application-profile.schema.yaml", profile)
    check_conformance_level(profile)
    check_deferrals_recorded(profile)


def assert_semantically_invalid(profile: dict) -> None:
    global CHECKS
    CHECKS += 1
    try:
        check_profile(profile)
    except (SemanticError, ValidationError):
        return
    raise AssertionError("Expected profile to be rejected by a semantic control rule")


# --- Namespace identity -----------------------------------------------------------

schema_files = sorted(SCHEMA_DIR.glob("*.schema.yaml"))
assert schema_files, "no schemas found"
for schema_path in schema_files:
    CHECKS += 1
    declared = load_schema(schema_path.name).get("$id", "")
    expected = NAMESPACE_BASE + schema_path.name
    if declared != expected:
        raise AssertionError(
            f"{schema_path.name} declares $id '{declared}', but NAMESPACE.md declares the "
            f"base '{NAMESPACE_BASE}', which requires '{expected}'. Either the schema or "
            f"NAMESPACE.md is wrong; NAMESPACE.md is the source of truth. See its "
            f"'Changing the base later' section."
        )
    if "example.invalid" in declared:
        raise AssertionError(f"{schema_path.name} still uses a placeholder namespace")


validation_evidence = {
    "schema_version": "1.0",
    "evidence_id": "E-VAL-001",
    "evidence_type": "independent_validation",
    "outcome": "passed",
    "reviewer_role": "independent_validator",
    "reviewer_identity": "validator@example.invalid",
    "reviewed_at": "2026-08-21T00:00:00Z",
    "scope": "method contract",
    "reference": "review/validation-001",
    "independence_basis": "Not involved in implementation.",
}
approval_evidence = {
    "schema_version": "1.0",
    "evidence_id": "E-APP-001",
    "evidence_type": "approval",
    "outcome": "passed",
    "reviewer_role": "method_owner",
    "reviewer_identity": "owner@example.invalid",
    "reviewed_at": "2026-08-21T00:00:00Z",
    "scope": "method contract",
    "reference": "decision/approval-001",
}

method = {
    "schema_version": "1.0",
    "method_id": "METHOD-001",
    "method_version": "1.0.0",
    "method_kind": "deterministic_method",
    "name": "Example method",
    "intended_use": "Contract test only",
    "owner": "team",
    "lifecycle_status": "active",
    "validation_status": "passed",
    "approval_status": "approved",
    "input_contracts": ["input-v1"],
    "output_contracts": ["output-v1"],
    "assurance_evidence": [validation_evidence, approval_evidence],
}
assert_valid("method-registry-entry.schema.yaml", method)

failed_evidence = deepcopy(method)
failed_evidence["assurance_evidence"] = [
    {**approval_evidence, "outcome": "failed", "evidence_type": "test"}
]
assert_invalid("method-registry-entry.schema.yaml", failed_evidence)

irrelevant_evidence = deepcopy(method)
irrelevant_evidence["assurance_evidence"] = [approval_evidence]
assert_invalid("method-registry-entry.schema.yaml", irrelevant_evidence)

independent_without_basis = deepcopy(validation_evidence)
del independent_without_basis["independence_basis"]
assert_invalid("assurance-evidence.schema.yaml", independent_without_basis)

conditional_without_detail = {**approval_evidence, "outcome": "passed_with_conditions"}
assert_invalid("assurance-evidence.schema.yaml", conditional_without_detail)
conditional_with_detail = {
    **conditional_without_detail,
    "limitations": ["Approval is limited to the documented scope."],
}
assert_valid("assurance-evidence.schema.yaml", conditional_with_detail)

conditional_method = deepcopy(method)
conditional_method["validation_status"] = "passed_with_conditions"
conditional_method["approval_status"] = "approved_with_conditions"
conditional_method["assurance_evidence"] = [
    {**conditional_with_detail, "evidence_type": "technical_review"},
    {**approval_evidence, "outcome": "passed_with_conditions", "limitations": ["Limited scope."]},
]
assert_valid("method-registry-entry.schema.yaml", conditional_method)

unqualified_with_conditions = deepcopy(method)
unqualified_with_conditions["assurance_evidence"] = [
    {**conditional_with_detail, "evidence_type": "technical_review"},
    approval_evidence,
]
assert_invalid("method-registry-entry.schema.yaml", unqualified_with_conditions)

run = {
    "schema_version": "1.0",
    "run_id": "RUN-001",
    "application_id": "example-app",
    "method_id": "METHOD-001",
    "method_version": "1.0.0",
    "method_kind": "ai_reasoning",
    "started_at": "2026-08-21T00:00:00Z",
    "completed_at": "2026-08-21T00:01:00Z",
    "run_status": "completed",
    "materiality": "high",
    "input_references": ["input/001"],
    "input_hash": "a" * 64,
    "implementation_revision": "git:abc123",
    "configuration_version": "1.0",
    "configuration_hash": "b" * 64,
    "ai_provider": "provider",
    "ai_model": "model",
    "prompt_version": "prompt-1",
    "output_references": ["output/001"],
    "output_hash": "c" * 64,
}
assert_valid("method-run-lineage.schema.yaml", run)

null_ai_provenance = deepcopy(run)
null_ai_provenance["ai_provider"] = None
null_ai_provenance["ai_model"] = None
null_ai_provenance["prompt_version"] = None
assert_invalid("method-run-lineage.schema.yaml", null_ai_provenance)

null_completion = deepcopy(run)
null_completion["completed_at"] = None
assert_invalid("method-run-lineage.schema.yaml", null_completion)

failed_run = {
    "schema_version": "1.0",
    "run_id": "RUN-FAILED",
    "application_id": "example-app",
    "method_id": "METHOD-001",
    "method_version": "1.0.0",
    "method_kind": "deterministic_method",
    "started_at": "2026-08-21T00:00:00Z",
    "run_status": "failed",
    "materiality": "high",
    "input_references": ["input/failed"],
    "output_references": [],
    "error_summary": "Input rejected.",
}
assert_valid("method-run-lineage.schema.yaml", failed_run)

override = {
    "schema_version": "1.0",
    "override_id": "OVR-001",
    "application_id": "example-app",
    "method_run_id": "RUN-001",
    "classification": "parameter_override",
    "affected_method": "METHOD-001",
    "affected_scope": "calculation",
    "original_value": 1,
    "override_value": 2,
    "description": "Example pending override",
    "rationale": "Contract test only",
    "evidence_reference": "review/002",
    "calculation_impact": "changes parameter",
    "output_impact": "changes result",
    "materiality": "high",
    "approval_required": True,
    "approval_status": "pending",
    "owner": "team",
    "reviewer_or_approver": None,
    "created_at": "2026-08-21T00:00:00Z",
    "review_or_expiry_trigger": "2026-12-31",
    "closure_condition": "approved or rejected",
    "rollback_approach": "restore original",
}
assert_valid("override-record.schema.yaml", override)

approved_override = deepcopy(override)
approved_override["approval_status"] = "approved"
approved_override["reviewer_or_approver"] = "method_owner@example.invalid"
approved_override["approval_evidence_reference"] = "approval:decision-001"
approved_override["approval_at"] = "2026-08-21T00:02:00Z"
assert_valid("override-record.schema.yaml", approved_override)

high_without_approval = deepcopy(override)
high_without_approval["approval_required"] = False
high_without_approval["approval_status"] = "not_required"
assert_invalid("override-record.schema.yaml", high_without_approval)

approved_without_approver = deepcopy(override)
approved_without_approver["approval_status"] = "approved"
approved_without_approver["reviewer_or_approver"] = None
assert_invalid("override-record.schema.yaml", approved_without_approver)

approved_without_evidence = deepcopy(approved_override)
approved_without_evidence["approval_evidence_reference"] = "not-an-approval-record"
assert_invalid("override-record.schema.yaml", approved_without_evidence)

adoption_block = {
    "framework_version": "0.7.0",
    "framework_digest": "1f895dd8f2646fabb878da01c83bd5aaabf1d0c2881661d00b1f06d9f5daec76",
    "adoption_date": "2026-08-27",
    "review_by": "2027-02-23",
    "framework_maintainer": "Named Maintainer",
    "repository_classification": "internal",
    "decision_record_id": "DR-0001",
    "adoption_status": "in_progress",
    "independent_validator": None,
    "deferrals": [
        {
            "control_id": "x-example-independent-validation",
            "rationale": "Out of scope for the current risk profile.",
            "owner": "Named Owner",
            "revisit_by": "2027-03-31",
        }
    ],
}

profile = {
    "schema_version": "1.0",
    "application_id": "example-app",
    "display_name": "Example",
    "owner": "team",
    "stack": {},
    "risk_profile": "Material quantitative outputs.",
    "materiality_definition": "High means externally relied upon.",
    "data_classification": "internal",
    "conformance_level": "essential",
    "adoption": adoption_block,
    "baseline_controls": {
        "agent_work_packets": {"decision": "required", "rationale": "Bounded work."},
        "actual_diff_review": {"decision": "required", "rationale": "Material changes."},
        "secret_hygiene": {"decision": "required", "rationale": "Sensitive data."},
    },
    "control_decisions": {
        "dependency_lock": {"decision": "required", "rationale": "Supply chain."},
        "provenance": {"decision": "required", "rationale": "Replayability."},
        "x-example-independent-validation": {"decision": "deferred", "rationale": "B1 scope."},
    },
}
check_profile(profile)

# --- Adoption identity (F1): the fields the Setup Guide mandates must be enforced ---

no_adoption = deepcopy(profile)
del no_adoption["adoption"]
assert_invalid("application-profile.schema.yaml", no_adoption)

for field in (
    "framework_version",
    "framework_digest",
    "adoption_date",
    "review_by",
    "framework_maintainer",
    "repository_classification",
    "decision_record_id",
    "adoption_status",
):
    missing_field = deepcopy(profile)
    del missing_field["adoption"][field]
    assert_invalid("application-profile.schema.yaml", missing_field)

bad_digest = deepcopy(profile)
bad_digest["adoption"]["framework_digest"] = "not-a-sha256"
assert_invalid("application-profile.schema.yaml", bad_digest)

bad_version = deepcopy(profile)
bad_version["adoption"]["framework_version"] = "v0.7"
assert_invalid("application-profile.schema.yaml", bad_version)

bad_date = deepcopy(profile)
bad_date["adoption"]["adoption_date"] = "27-08-2026"
assert_invalid("application-profile.schema.yaml", bad_date)

bad_review_date = deepcopy(profile)
bad_review_date["adoption"]["review_by"] = "23-02-2027"
assert_invalid("application-profile.schema.yaml", bad_review_date)

unknown_adoption_field = deepcopy(profile)
unknown_adoption_field["adoption"]["approved"] = True
assert_invalid("application-profile.schema.yaml", unknown_adoption_field)

# A blocked or deferred adoption must say why.
blocked_without_rationale = deepcopy(profile)
blocked_without_rationale["adoption"]["adoption_status"] = "blocked"
assert_invalid("application-profile.schema.yaml", blocked_without_rationale)

blocked_with_rationale = deepcopy(blocked_without_rationale)
blocked_with_rationale["adoption"]["status_rationale"] = "Awaiting independent validator."
check_profile(blocked_with_rationale)

deferral_without_owner = deepcopy(profile)
deferral_without_owner["adoption"]["deferrals"] = [
    {"control_id": "run_lineage", "rationale": "No runs.", "revisit_by": "2027-03-31"}
]
assert_invalid("application-profile.schema.yaml", deferral_without_owner)

deferral_unknown_control = deepcopy(profile)
deferral_unknown_control["adoption"]["deferrals"] = [
    {
        "control_id": "made_up_control",
        "rationale": "x",
        "owner": "Named Owner",
        "revisit_by": "2027-03-31",
    }
]
assert_invalid("application-profile.schema.yaml", deferral_unknown_control)

# --- Conformance levels: semantic enforcement (core/CONFORMANCE_LEVELS.md) ---------

missing_level_control = deepcopy(profile)
del missing_level_control["control_decisions"]["dependency_lock"]
assert_semantically_invalid(missing_level_control)

level_control_not_required = deepcopy(profile)
level_control_not_required["control_decisions"]["dependency_lock"]["decision"] = "deferred"
level_control_not_required["adoption"]["deferrals"].append(
    {
        "control_id": "dependency_lock",
        "rationale": "Deferred.",
        "owner": "Named Owner",
        "revisit_by": "2027-03-31",
    }
)
assert_semantically_invalid(level_control_not_required)

# Claiming `full` without implementing the full control set must fail.
overclaimed_level = deepcopy(profile)
overclaimed_level["conformance_level"] = "full"
assert_semantically_invalid(overclaimed_level)

invalid_level = deepcopy(profile)
invalid_level["conformance_level"] = "gold"
assert_invalid("application-profile.schema.yaml", invalid_level)

# A control deferred silently, with no owned entry in adoption.deferrals, must fail.
silent_deferral = deepcopy(profile)
silent_deferral["adoption"]["deferrals"] = []
assert_semantically_invalid(silent_deferral)

# --- Golden examples (F4): shipped examples must stay valid as schemas change ------

essential_example = load_yaml(EXAMPLES_DIR / "application-profile.essential.example.yaml")
check_profile(essential_example)
assert essential_example["conformance_level"] == "essential"

full_example = load_yaml(EXAMPLES_DIR / "application-profile.full.example.yaml")
check_profile(full_example)
assert full_example["conformance_level"] == "full"

override_example = load_yaml(EXAMPLES_DIR / "override-record.approved.example.yaml")
assert_valid("override-record.schema.yaml", override_example)

method_example = load_yaml(EXAMPLES_DIR / "method-registry-entry.example.yaml")
assert_valid("method-registry-entry.schema.yaml", method_example)

run_example = load_yaml(EXAMPLES_DIR / "method-run-lineage.example.yaml")
assert_valid("method-run-lineage.schema.yaml", run_example)

# The three worked records are ONE SET, and SP057 makes that structural rather than editorial:
# the conformance checker requires these references to resolve in any repository that declares
# the registers. Asserted here so the set cannot drift apart in an edit to one file, which is
# exactly how the override example came to name two records that did not exist (DR-27).
CHECKS += 1
assert override_example["method_run_id"] == run_example["run_id"], (
    "the override example must name the run example"
)
CHECKS += 1
assert (run_example["method_id"], run_example["method_version"]) == (
    method_example["method_id"], method_example["method_version"]
), "the run example must name the method example at its registered version"
CHECKS += 1
assert override_example["override_id"] in run_example["overrides"], (
    "the run example must carry the override example back"
)
CHECKS += 1
assert (
    override_example["application_id"]
    == run_example["application_id"]
    == full_example["application_id"]
), "all three worked records must belong to the application the full example describes"

# --- Prerequisite gates (core/PREREQUISITE_GATES.md) -------------------------------

gate = {
    "id": "work_registration",
    "status": "required",
    "effective_from": "2026-08-27",
    "precondition": {"artefacts": ["docs/DEVELOPMENT_REGISTER.md"]},
    "gated_activity": {"paths": ["src/**"]},
    "enforcement": ["history_audit", "review"],
}
with_gates = deepcopy(profile)
with_gates["prerequisites"] = [gate]
assert_valid("application-profile.schema.yaml", with_gates)

for bad in (
    {**gate, "id": "Work Registration"},          # ids are snake_case
    {**gate, "status": "optional"},               # not one of the three statuses
    {**gate, "effective_from": "27-08-2026"},     # not an ISO date
    {**gate, "enforcement": ["magic"]},           # enforcement vocabulary is closed
    {**gate, "invented_field": "x"},              # additionalProperties: false
    {k: v for k, v in gate.items() if k != "id"},
    {k: v for k, v in gate.items() if k != "status"},
):
    invalid = deepcopy(profile)
    invalid["prerequisites"] = [bad]
    assert_invalid("application-profile.schema.yaml", invalid)

# The gate catalogue in the checker and the one in the standard must not drift apart.
#
# ANCHORED TO THE CATALOGUE BLOCK, not to a line shape. This originally matched every
# four-space-indented `"key": "value"` line anywhere in the checker, which silently absorbed the
# first unrelated module-level dict of that shape to be added - PATTERN_C_CONTROLS, in ACT-014.
# It failed loudly that time, on the count, which is the only reason it was noticed. It does not
# always: drop one gate and add a ONE-entry dict of the same shape and the count is 19 either way,
# so the assertion passes while the set it iterates has silently lost a real gate and gained a
# fake one. That was constructed and run, not reasoned about. A guard whose negative result does
# not establish what it appears to is this project's most-repeated defect, and this was an
# instance of it inside a guard. Recorded as F23.
CHECKER = (ROOT / "scripts" / "check_conformance.py").read_text(encoding="utf-8")
GATES_DOC = (ROOT / "core" / "PREREQUISITE_GATES.md").read_text(encoding="utf-8")
CATALOGUE_BLOCK = re.search(
    r"^GATE_CATALOGUE: dict\[str, str\] = \{$(.*?)^\}$",
    CHECKER,
    re.MULTILINE | re.DOTALL,
)
assert CATALOGUE_BLOCK, "GATE_CATALOGUE is not where this guard expects it in the checker"
catalogue_ids = re.findall(r'^    "([a-z0-9_]+)": "', CATALOGUE_BLOCK.group(1), re.MULTILINE)
assert len(catalogue_ids) == 19, f"expected 19 catalogue gates, found {len(catalogue_ids)}"
for gate_id in catalogue_ids:
    assert f"`{gate_id}`" in GATES_DOC, f"gate {gate_id} is not documented in PREREQUISITE_GATES.md"

# Every gate the full example declares must be a catalogue gate or explicitly custom.
for declared in full_example["prerequisites"]:
    assert (
        declared["id"] in catalogue_ids or declared.get("catalogue_id") == "custom"
    ), f"full example declares uncatalogued gate {declared['id']}"
assert {g["id"] for g in full_example["prerequisites"]} == set(catalogue_ids), (
    "the 'full' example must decide every catalogue gate"
)

# builds_user_interface decides whether the interface gates are a floor, so it is a boolean
# and nothing else. A string "true" would be read as truthy by something, somewhere.
ui_true = deepcopy(profile)
ui_true["builds_user_interface"] = True
assert_valid("application-profile.schema.yaml", ui_true)
ui_bad = deepcopy(profile)
ui_bad["builds_user_interface"] = "true"
assert_invalid("application-profile.schema.yaml", ui_bad)

# The examples must sit on opposite sides of the interface floor, or the pair stops
# demonstrating the decision the field exists to force.
assert essential_example["builds_user_interface"] is True
assert full_example["builds_user_interface"] is False
assert {
    g["id"] for g in full_example["prerequisites"] if g["status"] == "not_applicable"
} >= {"component_library", "design_authority", "options_before_build", "prerequisite_state_ui"}

exception_record = {
    "gate_id": "work_registration",
    "commits": ["a1b2c3d4"],
    "owner": "Named Owner",
    "rationale": "Emergency fix raised retrospectively.",
    "raised_on": "2026-09-01",
}
assert_valid("gate-exception.schema.yaml", exception_record)
for bad_exception in (
    {**exception_record, "commits": []},                  # must name specific commits
    {**exception_record, "commits": ["not-a-sha"]},
    {**exception_record, "owner": ""},
    {k: v for k, v in exception_record.items() if k != "rationale"},
):
    assert_invalid("gate-exception.schema.yaml", bad_exception)

# Every template this framework ships must be DETECTABLE as a template.
#
# This closes the false negative found by the audit behind DR-17. Before it, two of the five
# templates -- decision-record.md and work-packet.md -- carried no marker of any kind: they
# used an empty value after a colon, which neither branch of PLACEHOLDER_PATTERN matched. A
# gate naming either as its precondition artefact would have passed SP032 while pointing at a
# blank form, which is the exact condition SP032 exists to catch.
#
# The pattern is IMPORTED from the checker rather than restated here, per DR-6: a copy would
# agree on the day it was written and stop agreeing afterwards. This test then guards the
# checker's remaining branches from being narrowed until they detect nothing.
sys.path.insert(0, str(ROOT / "scripts"))
from check_conformance import PLACEHOLDER_PATTERN  # noqa: E402

template_dir = ROOT / "templates"
templates = sorted(p for p in template_dir.rglob("*") if p.is_file())
assert templates, "templates/ is empty; the detectability check would pass vacuously"
for template in templates:
    body = template.read_text(encoding="utf-8")
    assert PLACEHOLDER_PATTERN.search(body), (
        f"templates/{template.relative_to(template_dir)} is not detectable as a template. "
        "A gate naming it as a precondition artefact would pass SP032 while pointing at a "
        "blank form. Give it a replace-me marker."
    )
    CHECKS += 1

# ...and the same check must not be satisfiable by a completed artefact that merely documents
# syntax. This is the negative control for the branch DR-17 removed; without it, someone could
# restore the shape-based branch and every assertion above would still pass.
for notation in (
    "Records are numbered `DR-<n>`, sequential, never reused.",
    "Usage: python scripts/verify_release.py <path-to-zip>",
    "The audit runs `git log --since=<effective_from>` over the gated paths.",
):
    assert not PLACEHOLDER_PATTERN.search(notation), (
        f"PLACEHOLDER_PATTERN matches notation, not a placeholder: {notation!r}. "
        "See F14 and DR-17 before widening it again."
    )
    CHECKS += 1

# The install report's review classes must keep meaning what they say (DR-20).
#
# The risk is not that classify() throws - it cannot, it has a default. The risk is that a
# file quietly lands in the wrong class and an upgrade diff then understates what changed.
# The `contract` class is the one that can rot silently, because it is derived from the
# checker's constants: if the checker starts parsing a third schema, the installer must
# follow, and nothing else would notice.
import check_conformance  # noqa: E402  (ROOT/scripts is already on sys.path)
import install_standard  # noqa: E402

payload_paths = set(install_standard.build_payload(ROOT))

# NOT asserted here: that the installer's `contract` class equals the checker's constants.
# That assertion was written first and removed, because it cannot fail. `classify()` DERIVES
# from those same constants, so both sides of the comparison move together -- pointing the
# checker at a different schema changes the expected value and the actual value identically,
# and the test passes. It was verified to pass under exactly that mutation. Derivation is
# what removes the drift; a test that both sides agree is then a tautology, and a tautology
# that looks like a control is worse than no control.
#
# What IS asserted is falsifiable: every schema the checker parses must actually be shipped.
# That catches a real bug the derivation does not prevent -- the checker expecting a file the
# installer never installs, which fails in the adopter's repository and nowhere else.
for parsed in (check_conformance.SCHEMA_PATH, check_conformance.EXCEPTION_SCHEMA_PATH):
    assert parsed in payload_paths, (
        f"the checker parses {parsed}, but the installer does not ship it. An adopting "
        f"repository would install a checker that cannot find its own schema."
    )
    assert install_standard.classify(parsed) == install_standard.CLASS_CONTRACT, (
        f"{parsed} is parsed by the checker but does not classify as `contract`"
    )
    CHECKS += 1

# The three things that execute in an adopting repository. A change to any of them changes
# behaviour, and an upgrade that reports them as `reference` would invite the wrong review.
for executable in (
    f"{install_standard.VENDOR_DIR}/check_conformance.py",
    install_standard.HOOK_TARGET,
    install_standard.WORKFLOW_TARGET,
):
    assert executable in payload_paths, f"{executable} is not in the payload"
    assert install_standard.classify(executable) == install_standard.CLASS_ENFORCING, (
        f"{executable} executes in an adopting repository but does not classify as "
        f"`enforcing`; an upgrade would understate what it changes."
    )
    CHECKS += 1

# Everything in the payload must land in one of the three declared classes -- there is no
# fourth, unnamed bucket that the install report would silently omit.
for rel in payload_paths:
    assert install_standard.classify(rel) in (
        install_standard.CLASS_ENFORCING,
        install_standard.CLASS_CONTRACT,
        install_standard.CLASS_REFERENCE,
    ), f"{rel} classifies as nothing the install report prints"
    CHECKS += 1

# The dependency pin has exactly one source of truth (F21, DR-25).
#
# pyproject.toml declares the versions; the workflows install them. Two places stating the same
# fact is the drift defect this register has recorded repeatedly - F4 (namespace vs schemas),
# F5 (organisation identifier), F12 (source vs vendored checker). So the workflows are checked
# AGAINST the declaration rather than trusted to match it.
#
# Parsed with a regex rather than `tomllib`, which is standard library only from Python 3.11
# while this project's declared floor is 3.9. The file is ours and its shape is known.
pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
deps_block = re.search(r"(?ms)^dependencies\s*=\s*\[(.*?)\]", pyproject)
assert deps_block, "pyproject.toml declares no dependencies array"
declared_deps = sorted(re.findall(r'"([^"]+)"', deps_block.group(1)))
assert declared_deps, "pyproject.toml declares an empty dependencies array"
CHECKS += 1

for dep in declared_deps:
    assert "==" in dep, (
        f"{dep} is not pinned to an exact version. A range reintroduces exactly the exposure "
        f"F21 recorded: a breaking release reaching every adopting repository at once."
    )
    CHECKS += 1

for workflow in (
    ROOT / ".github" / "workflows" / "standard-self-check.yml",
    ROOT / ".github" / "workflows" / "standards-conformance.yml",
    ROOT / "standard" / ".github" / "workflows" / "standards-conformance.yml",
):
    body = workflow.read_text(encoding="utf-8")
    install = [ln for ln in body.splitlines() if "pip install" in ln]
    assert install, f"{workflow.name} has no pip install line"
    for dep in declared_deps:
        assert any(dep in ln for ln in install), (
            f"{workflow.name} does not install {dep} as pyproject.toml declares it. The pin has "
            f"one source of truth; a workflow that names its own versions is a second."
        )
    CHECKS += 1

print(f"CONTRACT_CONFORMANCE=PASS  ({CHECKS} checks)")
