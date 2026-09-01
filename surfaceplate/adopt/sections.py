"""Turning answers into profile fragments. Pure functions: no prompting, no I/O, no defaults.

Every function here takes a flat dict of answers - keyed by the `FieldSpec.id`s that `plan.py`
declared for that section - and returns the piece of `governance/application-profile.yaml` it
fills. `wizard.py` assembles the fragments; `render.py` writes them out.

**Why this module stopped asking questions (`DR-36`).** Until Phase 2 these were `ask_*` functions
that called a `Prompt` one question at a time. That coupled three separable things: which questions
exist (now `plan.py`), how they get asked (now `tui/` and `interview.py`), and what shape the answers
take (here). Splitting them is what makes the binding rule provable rather than merely asserted:
because these functions are pure and total, `tests/test_provenance.py` can feed every free-text
field a unique sentinel, assemble a whole profile, and assert that **every string in the result is
either sentinel-derived or on an explicit allow-list of things the tool contributes**.

That allow-list is the honest statement of what this wizard writes on its own behalf, and adding to
it is a code-review event. It is a strictly stronger guarantee than the old `ScriptedPrompt` gave:
this repository's own test file records that the old one "only objects to a call it wasn't given an
answer for, never to a value written without any call" - which is exactly how `F32`/`ACT-022`
(rationale text invented for seven controls and gates) escaped every scripted test it had.
"""

from __future__ import annotations

import datetime as _dt

from surfaceplate.adopt import catalogue, plan

# Values this module supplies on nobody's behalf but the framework's. Every one of these appears in
# `tests/test_provenance.py`'s allow-list, and that test fails if this module writes a string that
# is neither one of these nor traceable to an answer.
SCHEMA_VERSION = "1.0"
SCANNER_NOTES = "Blocking."
DECISION_REQUIRED = "required"


def build_mode(answers: dict) -> dict:
    """Session state, not profile content - the chosen register is never written to disk."""
    return {"mode": answers["mode"]}


def build_identity(answers: dict) -> dict:
    return {
        "application_id": answers["application_id"],
        "display_name": answers["display_name"],
        "owner": answers["owner"],
    }


def build_stack(answers: dict) -> dict:
    return {
        "stack": {"language": answers["language"]},
        "builds_user_interface": bool(answers["builds_user_interface"]),
    }


def build_risk(answers: dict) -> dict:
    return {
        "risk_profile": answers["risk_profile"],
        "materiality_definition": answers["materiality_definition"],
        "data_classification": answers["data_classification"],
    }


def build_level(answers: dict) -> dict:
    return {"conformance_level": answers["conformance_level"]}


def build_controls(answers: dict, *, level: str) -> dict:
    """Baseline controls, the scanner, and every control this profile declares.

    A control at the level's floor is written because the level requires it - it is never offered
    as a tick box, exactly as a level-mandatory gate's status is never offered as a choice. Above
    the floor it is written only when a human ticked it in `above_floor`. Either way its *rationale*
    is always answered, never supplied here.

    `ACT-032` replaced eight separate `<control>.declared` booleans with that one list. The older
    per-control key is still honoured, because a saved draft or a script written against the
    previous shape supplies it and silently dropping a declared control would lose an answer a human
    gave.
    """
    baseline_controls: dict = {}
    for control_id in plan.BASELINE_CONTROL_IDS:
        baseline_controls[control_id] = {
            "decision": DECISION_REQUIRED,
            "rationale": answers[f"{control_id}.rationale"],
        }

    baseline_controls["secret_hygiene"]["scanner"] = {
        "name": answers["scanner.name"],
        "wired_in": [answers["scanner.wired_in"]],
        "notes": SCANNER_NOTES,
    }

    floor = catalogue.CONFORMANCE_LEVELS[level]
    control_decisions: dict = {}
    for control_id in sorted(catalogue.CONFORMANCE_LEVELS["full"]):
        ticked = answers.get("above_floor") or ()
        if isinstance(ticked, str):
            ticked = [c.strip() for c in ticked.split(",") if c.strip()]
        declared = (
            control_id in floor
            or control_id in ticked
            or bool(answers.get(f"{control_id}.declared"))
        )
        if not declared:
            continue
        entry: dict = {
            "decision": DECISION_REQUIRED,
            "rationale": answers[f"{control_id}.rationale"],
        }
        reference = answers.get(f"{control_id}.implementation_reference")
        if reference:
            entry["implementation_reference"] = reference
        control_decisions[control_id] = entry

    return {"baseline_controls": baseline_controls, "control_decisions": control_decisions}


def _enforcement_list(value: object) -> list[str]:
    """`enforcement` is a fixed schema enum, and since `DR-38` it is answered by ticking boxes, so
    it arrives as a list. A string is still accepted and split: it is what every profile written
    before that change contains, and what a hand-written script may still supply."""
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(item) for item in value]


def build_gate(spec: plan.GateSpec, answers: dict) -> dict:
    """One gate's entry, from the answers given for it.

    `answers` is keyed without the gate-id prefix - `{"status": ..., "artefact": ...}` - so this
    function is testable against a single gate in isolation.
    """
    if spec.mandatory:
        status = "required"
    elif spec.auto_status:
        status = spec.auto_status
    else:
        status = answers["status"]

    if status == "required":
        return {
            "id": spec.id,
            "status": "required",
            "effective_from": answers["effective_from"],
            "precondition": {
                "artefacts": [answers["artefact"]],
                "description": answers["precondition_description"],
            },
            "gated_activity": {
                "paths": [answers["paths"]],
                "description": answers["gated_description"],
            },
            "enforcement": _enforcement_list(answers["enforcement"]),
        }

    if status == "deferred":
        return {
            "id": spec.id,
            "status": "deferred",
            "owner": answers["owner"],
            "revisit_by": answers["revisit_by"],
            "rationale": answers["rationale"],
        }

    return {"id": spec.id, "status": "not_applicable", "rationale": answers["rationale"]}


def build_gates(answers: dict, *, level: str, builds_ui: bool, mode: str) -> list[dict]:
    """Every gate this run asked about, in catalogue order.

    Walks the same `plan.gate_plan` the screens walked, so a gate the plan did not include cannot
    appear here and a gate it did include cannot be silently dropped.
    """
    gates = []
    for spec in plan.gate_plan(level=level, builds_ui=builds_ui, mode=mode):
        prefix = f"{spec.id}."
        gate_answers = {
            key[len(prefix):]: value for key, value in answers.items() if key.startswith(prefix)
        }
        gates.append(build_gate(spec, gate_answers))
    return gates


def build_adoption(answers: dict, *, framework_version: str, framework_digest: str) -> dict:
    """`adoption_date` is today's date, and `framework_version`/`framework_digest` come from the
    install record - the three values in this profile the tool legitimately supplies, each named in
    the provenance allow-list rather than left to be noticed."""
    result: dict = {
        "framework_version": framework_version,
        "framework_digest": framework_digest,
        "adoption_date": _dt.date.today().isoformat(),
        "review_by": answers["review_by"],
        "framework_maintainer": answers["framework_maintainer"],
        "repository_classification": answers["repository_classification"],
        "decision_record_id": answers["decision_record_id"],
        "adoption_status": answers["adoption_status"],
        "independent_validator": (
            answers["independent_validator"] if answers.get("needs_validator") else None
        ),
        # v1: `control_decisions` offers `required` only, so there is nothing to defer. Disclosed
        # in `DR-32` and untouched by Phase 2.
        "deferrals": [],
    }
    # The KEY is absent when there is no rationale, not present-with-null: the schema does not
    # require this field outside blocked/deferred, so an absent key is the correct representation -
    # unlike `independent_validator`, which the schema types as [string, "null"].
    if answers.get("status_rationale"):
        result["status_rationale"] = answers["status_rationale"]
    return result


def build_wrap(answers: dict) -> dict:
    roles = [line.strip() for line in str(answers.get("human_roles", "")).splitlines() if line.strip()]
    return {
        "human_roles": roles,
        "release_route": answers["release_route"],
        "exclusions": [],
    }


def build_profile(state: dict, *, framework_version: str, framework_digest: str) -> dict:
    """The whole profile, from every section's answers. Pure - the same state always produces the
    same dict, apart from `adoption_date`, which is today's."""
    level = state["level"]["conformance_level"]
    builds_ui = bool(state["stack"]["builds_user_interface"])
    mode = state["mode"]["mode"]

    identity = build_identity(state["identity"])
    stack = build_stack(state["stack"])
    risk = build_risk(state["risk"])
    controls = build_controls(state["controls"], level=level)
    gates = build_gates(state["gates"], level=level, builds_ui=builds_ui, mode=mode)
    adoption = build_adoption(
        state["adoption"],
        framework_version=framework_version,
        framework_digest=framework_digest,
    )
    wrap = build_wrap(state["wrap"])

    return {
        "schema_version": SCHEMA_VERSION,
        **identity,
        **stack,
        **risk,
        "conformance_level": level,
        "adoption": adoption,
        **controls,
        "prerequisites": gates,
        **wrap,
    }
