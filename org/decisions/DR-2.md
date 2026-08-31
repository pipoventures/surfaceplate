# Decision Record

- Decision ID: DR-2
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision
  about the framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted (decision only — not implemented; see Limitations and follow-up)
- Risk level: 3 — a methodology decision, per the risk table in `core/REVIEW_AND_EVIDENCE.md`
  ("Methodology, material model or numerical output, material AI output/reasoning, security
  boundary, or externally relied-on output").
- Related work item: `v0.11.0` (commit `22728e770dbd018305744b9ae5785fe04dbe2a36`)

## Decision

The mnemosyne kernel — the tier-architected doctrine bundle (kernel plus the communication,
working-method and automation layers) — is sole behavioural canon for AI-assisted work under this
standard. `core/AI_OPERATING_MODEL.md` becomes a repository-scoped **projection** of that canon: a
derived view expressed in this repository's own terms, not a second, independently authoritative
document. Where the projection and the kernel appear to disagree, the kernel governs, automatically
and without case-by-case adjudication.

## Context and alternatives

Rejected: merging the two into one flat document, or otherwise treating `core/AI_OPERATING_MODEL.md`
as co-equal canon alongside the kernel. Rejected because the kernel is tier-architected — invariant
(Tier 1), conditional gate (Tier 2), operating default (Tier 3) — with an explicit precedence order
and an override mechanism scoped to Tier 3 only. A flat merge collapses that structure: merged prose
has no tier, so a reader cannot tell whether a given sentence is an invariant that never yields or a
default a user may consciously override. Losing that distinction is a structural defect, not a
stylistic one — it directly determines what a later reader or agent is permitted to do.

## Impact

- Numerical/model output: none directly; governs AI-assisted working behaviour generally.
- Contracts/schemas: none directly.
- Security/data: the kernel's Tier 1 invariants and Tier 2 gates become the binding floor for this
  repository, superseding anything in `core/AI_OPERATING_MODEL.md` that would state something
  weaker.
- Reproducibility/lineage: the projection must record its own provenance — which kernel version it
  projects — so a reader can tell whether it is current.
- Operations/release: `core/AI_OPERATING_MODEL.md` requires a rewrite to become an explicit,
  dated projection. Not yet done.

## Evidence

- Code/configuration: not applicable — this decision concerns documentation authority, not code.
- Tests/checks: none exist to enforce this; not schema-validated.
- Runtime evidence: none yet; the rewrite has not happened.
- Independent review: none.

Two specific passages must survive the rewrite as repository-specific content that belongs in the
projection, not the kernel, because they are not universal claims about all AI-assisted work but
specific to this standard's own tests-and-evidence discipline:

- "do not weaken, delete, skip, bypass or rewrite tests merely to obtain a passing result";
- "a changed-file list alone is insufficient — evidence must contain the actual diff."

## Limitations and follow-up

Decided, not implemented. `core/AI_OPERATING_MODEL.md` has not been rewritten. Until it is, this
repository carries two documents whose relationship this record states but whose text does not yet
reflect. This record's own principle applies to itself here: a stated correction that the target
document's own wording does not yet carry is not a completed correction. Rewriting
`core/AI_OPERATING_MODEL.md` into an explicit, dated projection is the required follow-up, and is
not scoped to this record.

## Approval

- Technical reviewer: not yet assigned.
- Method owner: not yet assigned.
- Independent validator: not yet assigned.
- Release authority: not yet assigned.

This record does not itself constitute approval, validation, or release authorisation.
