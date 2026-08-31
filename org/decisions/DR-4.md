# Decision Record

- Decision ID: DR-4
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision
  about the framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted (decision only — not implemented; see Limitations and follow-up)
- Risk level: 2 — a distribution/dependency mechanism decision (contracts/schemas, security/data),
  per the risk table in `core/REVIEW_AND_EVIDENCE.md`. Structurally similar to why
  `core/CONFORMANCE_LEVELS.md` requires `dependency_lock` at every level, including `essential`.
- Related work item: `v0.11.0` (commit `22728e770dbd018305744b9ae5785fe04dbe2a36`)

## Decision

Doctrine is vendored into this product as a versioned bundle with a recorded digest, and its
presence and digest are verified by the conformance checker. The product must never depend on
reading a private repository at runtime or at check time.

## Context and alternatives

Rejected: having the checker, the installer, or any script in this repository read doctrine content
live from a private source repository at run time — for example, resolving an absolute filesystem
path or a private remote to fetch canon text on demand. Rejected for two independent reasons:

1. It makes conformance results depend on something outside this repository's own version control,
   so the same commit could pass or fail depending on what happens to be present on the machine or
   account running the check — a form of non-determinism `core/CONTROL_PRINCIPLES.md` principle 2
   (Determinism) exists to prevent.
2. It makes distribution to any adopter without access to that private source impossible in
   principle, not merely inconvenient — directly contradicting this standard's stated intent to be
   adoptable across repositories under a single owner and, eventually, more widely.

## Impact

- Numerical/model output: none.
- Contracts/schemas: a new artefact (the vendored doctrine bundle) and a digest field the checker
  verifies. Neither exists yet.
- Security/data: closes a supply-chain-shaped exposure structurally similar to the reason
  `core/CONFORMANCE_LEVELS.md` already requires `dependency_lock` at every level, including
  `essential` — "supply-chain exposure exists regardless of output materiality."
- Reproducibility/lineage: a pinned digest makes it possible to state exactly which doctrine version
  a given conformance result was checked against, which a live, unpinned dependency cannot.
- Operations/release: not yet implemented; no release currently ships a vendored doctrine bundle.

## Evidence

- Code/configuration: not applicable — nothing built yet.
- Tests/checks: none written.
- Runtime evidence: none.
- Independent review: none.

Consequence recorded as part of this decision, not as a separate finding: the doctrine bundle this
product ships as its default is necessarily a reference kernel — a generic, unopinionated starting
point — not any individual maintainer's personal, machine-specific doctrine. A personal kernel, with
an individual's own tier choices and overrides, becomes an example of an adopter profile: a worked
example the product can point to, not the thing every adopter receives by default.

## Limitations and follow-up

Decided, not implemented. No vendoring mechanism, bundle format, digest field, or checker rule
exists yet in this repository. Designing the bundle format and the verification rule is the
required follow-up, and is not scoped to this record.

## Approval

- Technical reviewer: not yet assigned.
- Method owner: not yet assigned.
- Independent validator: not yet assigned.
- Release authority: not yet assigned.

This record does not itself constitute approval, validation, or release authorisation.
