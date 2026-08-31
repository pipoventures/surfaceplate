# Decision Record

- Decision ID: DR-3
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision
  about the framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted (decision only — not started; see Limitations and follow-up)
- Risk level: 1 — a low-risk scoping/documentation decision with no expected output impact, per the
  risk table in `core/REVIEW_AND_EVIDENCE.md`.
- Related work item: `v0.11.0` (commit `22728e770dbd018305744b9ae5785fe04dbe2a36`); depends on DR-2.

## Decision

The control-by-control comparison between the mnemosyne doctrine bundle and this standard's own
operating model is scoped to exactly two documents: `core/CONTROL_PRINCIPLES.md` (its 12
principles) and `core/CONFORMANCE_LEVELS.md`. No other document in this repository is crosswalked
control-by-control; everything else is governed by DR-2's blanket kernel-precedence rule instead.

## Context and alternatives

Rejected: crosswalking every `core/*.md` document individually (`core/AI_OPERATING_MODEL.md`,
`core/PREREQUISITE_GATES.md`, `core/REVIEW_AND_EVIDENCE.md`, `core/SECURITY_BASELINE.md`, and so
on) against the kernel bundle. Rejected because DR-2 already resolves those: they either become
explicit projections of kernel content (`core/AI_OPERATING_MODEL.md`), or they concern ground the
kernel does not address at all, in which case a control-by-control comparison would be comparing
against a document that says nothing on the topic. Restricting the crosswalk avoids duplicating a
resolution DR-2 already provides.

## Impact

- Numerical/model output: none.
- Contracts/schemas: none directly; the crosswalk itself is documentation.
- Security/data: none directly.
- Reproducibility/lineage: the crosswalk, once produced, becomes the record of which of this
  standard's controls are additive to the kernel and which are redundant with it — relevant to a
  future maintainer deciding what to keep when the two are reconciled further.
- Operations/release: no release impact; scoping decision only.

## Evidence

- Code/configuration: not applicable.
- Tests/checks: none; the crosswalk itself has not been produced.
- Runtime evidence: none.
- Independent review: none.

The rationale for choosing these two documents specifically: FACT FROM PACKAGE, read directly.
`core/CONTROL_PRINCIPLES.md` states, among its 12 principles: principle 2, Determinism ("Prefer
deterministic processing, explicit inputs, stable outputs..."); principle 4, Materiality ("Scale
tests, review, validation, and approval to output impact..."); principle 5, Lineage ("A material
result should be traceable to an application, scenario/package or input version, method/tool
version, configuration, code revision, execution/run ID, timestamp, and output"); and principle 6,
Overrides ("Never hide a manual adjustment in UI or calculation code. Record classification,
before/after values, rationale, evidence, owner, impact, approval, review/expiry, closure, and
rollback"). `core/CONFORMANCE_LEVELS.md` separately defines a three-level, floor-not-ceiling
materiality scale (`essential` / `standard` / `full`) tied to those same principles, and states
explicitly that enforcement is a deliberate split from the schema ("a schema file is not
enforcement"). These mechanisms — lineage, override recording, determinism, materiality-scaled
review — are the operational detail the kernel's tier structure does not itself specify, which is
the basis for calling them genuinely additive rather than restatements.

## Limitations and follow-up

Decided, not started. The crosswalk document itself does not yet exist anywhere in this repository.
Producing it — a control-by-control table mapping each of the 12 principles and each conformance
level requirement to the kernel provision it corresponds to, is additive to, or has no kernel
counterpart for — is the required follow-up and is not scoped to this record.

## Approval

- Technical reviewer: not yet assigned.
- Method owner: not yet assigned.
- Independent validator: not yet assigned.
- Release authority: not yet assigned.

This record does not itself constitute approval, validation, or release authorisation.
