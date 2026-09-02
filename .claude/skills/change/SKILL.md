---
name: change
description: "Default workflow for implementing a feature, enhancement, refactor, or test-coverage change under Surfaceplate."
---

# Change

The default implementation workflow. Use this unless a more specific skill applies
(`bug-fix`, `dependency-update`, `fix-ci`, `release`, `review`, `security-review`).

## Required inputs

Do not start without these. Ask if any is missing:

- the requested outcome, stated as a behaviour;
- acceptance criteria;
- the bounded scope — which files or areas may change, and which may not;
- the registered activity ID (see `activity.instructions.md`);
- any known ambiguity or open decision.

## Workflow

1. **Classify.** Decide whether the change is output-affecting, methodology-affecting,
   contract-affecting, or security-affecting. This determines review depth. When in doubt, classify
   upward.
2. **Resolve authority.** Identify the canonical authority for the behaviour being changed. If
   authorities contradict, stop — that is a blocking defect.
3. **Plan.** State the target files, the mechanism, the tests you will add or update, and the
   documentation you will update. Present the plan before broad edits.
4. **Implement** the smallest coherent change that satisfies the acceptance criteria.
5. **Test.** Run the focused subset for the touched area after each substantive edit, then widen.
6. **Update documentation and the register** in the same change.
7. **Inspect the actual diff** before reporting. Read what you changed, not what you intended.

## Gates

- focused tests for the changed area — green;
- contract or schema conformance tests where present — green;
- deterministic replay, golden, or reference tests where the change could affect output — green;
- lint, format, type, and build checks for the stack — green;
- documentation impact addressed, or a documentation-impact decision recorded;
- register updated with status, evidence, and any human-review requirement.

## Mandatory stops

Stop and put the decision to a human when the change would touch:

- methodology, or the meaning of a material numerical or model output;
- a public contract, schema, or API consumed outside this repository;
- provenance, lineage, or approval state;
- a security or authorisation boundary;
- irreversible data migration;
- release or production authorisation;
- architecture beyond the authorised scope.

## Completion report

Report: the activity ID; changed files, plus the actual diff for material changes; each command run
and its result; test output including warnings and skips; documentation and register updates;
assumptions; evidence gaps; and the human decisions still required.

Do not state that the change is approved, validated, or ready for release.
