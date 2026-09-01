"""Recognition-over-recall defaults for rationale fields: a real example to react to, not a blank
box to stare at.

`DR-35` records the design principle: every rationale field a real adopter answers offers an
editable example, shown as the prompt's `default=` - the same "shown, must be explicitly
submitted" pattern `review_by` and `enforcement` already use elsewhere in this wizard. Accepting a
default is still answering; nothing here is written unless a human's actual keystroke (even just
Enter) submits it.

Sourced, not invented: every string below is drawn from `examples/application-profile.essential
.example.yaml` or `examples/application-profile.full.example.yaml` - this framework's own two
worked, schema-valid example profiles - or, where those don't cover an item, composed directly
from that item's own rule text in `core/PREREQUISITE_GATES.md`.

**Deliberately scoped, not complete over every field.** Only rationale fields get an example - not
a gate's precondition artefact, gated paths, or effective date, which are too repository-specific
to usefully example and where a plausible-looking example risks being copied unedited. Within
rationale fields, only items whose rationale prompt is genuinely reachable get an entry here:

- The three baseline controls and the nine conformance-level controls: every one is covered, since
  `ask_controls` always asks a rationale for each.
- Of the nineteen gates, only the eleven whose `required`/`deferred`/`not_applicable` choice is
  ever actually asked. `work_registration`, `authority_map`, `decision_before_implementation`, and
  `change_record_before_completion` are mandatory `required` at every level that asks about them at
  all (`sections.py`'s `_ask_one_gate` skips the choice entirely when `mandatory=True`), and the
  four interface gates (`catalogue.DESIGN_GATES`) are either forced `required` (a UI-building
  repository) or auto-filled `not_applicable` with their own existing default (a repository with no
  UI) before `_ask_one_gate` is ever reached for them. None of those eight ever shows the
  `not_applicable`/`deferred` rationale prompt this module's gate examples are for.
  `tests/test_adopt.py` derives this eleven-gate set the same way `sections.py` itself decides
  which gates are optional - `GATE_CATALOGUE` minus `DESIGN_GATES` minus
  `LEVEL_REQUIRED_GATES["standard"]` - rather than a hand-copied list, so it cannot silently drift
  from what the wizard actually asks.
"""

from __future__ import annotations

# --- Baseline controls (all three; always asked) -----------------------------------------------
# Sourced from application-profile.essential.example.yaml, which states each in its punchiest form.

_BASELINE_CONTROL_RATIONALE: dict[str, str] = {
    "agent_work_packets": "All agent work is bounded, scoped, and reviewable.",
    "actual_diff_review": "Material changes require actual diff content, not a file list.",
    "secret_hygiene": "No secrets or customer data may enter the repository or fixtures.",
}

# --- Conformance-level controls (all nine; always asked when required at the chosen level) ------
# Sourced from application-profile.full.example.yaml (essential.example.yaml for dependency_lock,
# which full.example.yaml does not declare at all - full already exceeds essential's own floor).

_LEVEL_CONTROL_RATIONALE: dict[str, str] = {
    "dependency_lock": "Supply-chain exposure exists regardless of output materiality.",
    "deterministic_tests": "Outputs must be reproducible before they can be reviewed.",
    "contract_tests": "The API is consumed by a separate frontend and would break silently.",
    "documentation_authority": "Contradictory specification authority is treated as a blocking defect.",
    "provenance": "Every material figure must be traceable to its inputs and parameter version.",
    "run_lineage": "Material calculations must be reproducible from a recorded execution.",
    "method_registry": "Governed rules carry lifecycle, validation, and approval state.",
    "overrides": "A manual adjustment must never be hidden in calculation code.",
    "assurance_findings": "Limitations are recorded rather than smoothed away.",
}

# --- Gates whose status is ever a genuine choice (eleven of nineteen; see module docstring) ------
# Composed from each gate's own rule text and group description in core/PREREQUISITE_GATES.md,
# phrased as a plausible not_applicable-leaning rationale an early-stage adopter might actually
# give - editable, and deliberately not phrased as an endorsement that the reasoning is sound for
# every repository.

_GATE_RATIONALE: dict[str, str] = {
    "work_contract": (
        "No AI-assisted implementation happens in this repository yet; every change is made by a "
        "human contributor directly."
    ),
    "risk_classification": (
        "Risk classification is not yet a formal step in this repository's workflow; changes are "
        "reviewed informally through code review today."
    ),
    "register_currency": (
        "This repository's work register is small enough to check manually at each handover; no "
        "generated view exists yet to gate against."
    ),
    "test_convention": (
        "No formal, written test-naming or location convention exists yet; tests are added ad hoc "
        "and their placement is reviewed in code review."
    ),
    "authority_same_change": (
        "This repository has no authority_map gate declared, so there is no controlling document "
        "for a change to keep in step with yet."
    ),
    "regression_before_merge": (
        "No logic in this repository is critical enough yet to name a dedicated regression suite; "
        "ordinary test coverage runs on every change instead."
    ),
    "equivalence_evidence": (
        "This repository has not yet made a performance or refactoring change on a critical path; "
        "nothing has needed equivalence evidence so far."
    ),
    "data_source_lifecycle": (
        "This repository selects from a fixed, small set of data sources chosen at build time; "
        "there is no runtime selection step for this gate to guard."
    ),
    "output_validation_before_external_use": (
        "Nothing this repository generates leaves the delivery team today; outputs are consumed "
        "only by the team that produced them."
    ),
    "dependency_output_delta": (
        "This repository's dependencies do not influence its output - they support the build and "
        "test process only."
    ),
    "records_before_release": (
        "This repository has not yet prepared a release; there is no release process for this gate "
        "to guard yet."
    ),
}

RATIONALE_EXAMPLES: dict[str, str] = {
    **_BASELINE_CONTROL_RATIONALE,
    **_LEVEL_CONTROL_RATIONALE,
    **_GATE_RATIONALE,
}


def rationale_example(item_id: str) -> str:
    """The example rationale for `item_id`, or `""` if none exists - the same "no default" shape
    `_nonempty_text`'s own `default=""` already uses everywhere this module doesn't apply. Never
    raises: unlike `explanations.explain`, an absent example is an expected, scoped state for the
    eight gates the module docstring names, not a coverage gap."""
    return RATIONALE_EXAMPLES.get(item_id, "")
