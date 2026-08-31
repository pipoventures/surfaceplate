# Decision Record

- Decision ID: DR-6
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision about the
  framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted — implemented in `v0.12.0` (this is the release that implements it, not a record
  of intent; see Evidence)
- Risk level: 2 — "Output-affecting code, data, schema, or workflow", per the risk table in
  `core/REVIEW_AND_EVIDENCE.md`. It changes the `$id` of every schema in `schemas/` and changes a
  contract test.
- Related work item: `v0.12.0` — internal rename and namespace decision.

## Decision

The version segment of the schema namespace URN is the **schema contract version**: the version of
the contract that the schemas in `schemas/` collectively express. It is bumped **only on a breaking
schema change** — a field removed, a type narrowed, a previously optional field made required, an
enum value withdrawn, or any other change that can invalidate an instance that was valid before.

It is **independent of the framework version** recorded in `VERSION`. A framework release that
changes no schema, or changes one additively, leaves every `$id` untouched.

This replaces the rule in force up to `0.11.0`, under which the segment was the framework version.
`NAMESPACE.md` is updated to state the new rule, and is designated the single source of truth from
which `tests/validate_contracts.py` derives the expected namespace.

The current value stays at `0.7.0`, carried forward unchanged.

## Context and alternatives

The old rule was not merely superseded; it had already failed in practice. `NAMESPACE.md` declared
the segment to be the framework version. The framework advanced 0.7.0 → 0.8.0 → 0.9.0 → 0.10.0 →
0.11.0. Every schema `$id` stayed at `0.7.0` throughout. The document and the schemas disagreed for
four consecutive releases and the contract test passed on every one of them, because the test held
its own hardcoded copy of the base string. It agreed with the schemas by construction, so it could
never disagree with the document that governed them. That is finding F4.

Two things were therefore wrong and only one of them was the drift. The drift was the symptom; the
instrument that could not detect it was the defect. Correcting the identifiers without correcting
the instrument would have restored agreement and left in place the exact arrangement that let the
disagreement run for four releases undetected.

**Rejected: bump the `$id` on every framework release** — retaining the pre-0.11.0 rule and bringing
the schemas into line with it, i.e. moving every `$id` to `0.12.0` at this release and again at
every release after.

Rejected because it breaks adopter pins on releases where the schema is unchanged. An adopter that
validates against `urn:…:0.11.0:application-profile.schema.yaml` is invalidated by 0.12.0 even
though not one byte of any schema has changed in a way that affects them. The cost is paid by every
adopter, on every release, and buys nothing: what actually reproduces a validation result is the
release digest recorded in `adoption.framework_digest`, which already changes on every release
whether or not any schema does. The `$id` was duplicating that signal badly rather than carrying one
of its own. Under the accepted rule the `$id` carries the information the digest cannot: whether the
contract itself has changed in a way that can break an instance.

**Also rejected: renumber the segment to `1.0.0` at this release**, to mark the segment's changed
meaning. Rejected for the same reason: it would change every `$id` without a single schema having
changed — precisely the cost the accepted rule exists to avoid. A rule whose first act is to violate
itself is not worth adopting. `0.7.0` is retained instead, which also means no adopter pin changes
on account of the version segment at 0.12.0.

The rule is retrospective in effect. Every schema change between 0.7.0 and 0.11.0 was additive. Under
the old rule the schemas were four releases adrift; under this rule they were correct all along and
the document was what was wrong. This record adopts the reading that makes the schemas' actual
state correct, rather than one that would require rewriting six identifiers to vindicate a rule
already judged not worth keeping.

## Impact

- Numerical/model output: none. No schema constrains a numerical output differently as a result.
- Contracts/schemas: the `$id` of all six schemas in `schemas/` changes at this release — but from
  the **rename**, which replaced the organisation and product segments, not from this decision,
  which leaves the version segment at `0.7.0`. The two changes are deliberately separable and are
  separated in `NAMESPACE.md`: a rename is a change of identity, a version bump is a change of
  contract.
- Security/data: none.
- Reproducibility/lineage: improved. A pinned `$id` now changes only when the contract behind it
  changes, so an adopter can tell those two events apart. It could not before.
- Operations/release: `tests/validate_contracts.py` now reads `NAMESPACE.md` at run time. A release
  cannot be built while the document and the schemas disagree, because `scripts/build_release.py`
  refuses to build on a failing contract test.

## Evidence

- Code/configuration: `NAMESPACE.md` — the "Version in the identifier" section states the rule and
  the two `text` blocks are designated the source of truth. `tests/validate_contracts.py` — the
  `NAMESPACE_BASE` literal is deleted and replaced by `read_declared_namespace()`, which parses the
  declaration out of `NAMESPACE.md`; the per-schema assertion now requires `$id` to equal the
  derived base plus the schema's own file name.
- Tests/checks: `tests/validate_contracts.py` passes on the released tree
  (`CONTRACT_CONFORMANCE=PASS`), and was **observed to fail** under four deliberately introduced
  divergences before release: the document's version segment moved while the schemas were left
  alone (the F4 shape); the document's pattern block contradicting its own current-base block; the
  declaration made unparseable; and, by construction, a schema `$id` naming the wrong file. Each
  raised a named `AssertionError` identifying the divergence. Under the previous hardcoded
  arrangement the first three of those passed. A check that has not been seen to fail is not
  evidence that it can; these were run and their output recorded in the release evidence.
- Runtime evidence: the full installer and checker suite passes unchanged at 97 checks, confirming
  the namespace change does not reach the checker — which resolves schemas by file path, never by
  `$id`.
- Independent review: none. Not yet reviewed by anyone beyond the session that made this change.

## Limitations and follow-up

- The rule states when to bump the segment but nothing enforces that judgement. Nothing in this
  repository detects that a breaking schema change was made and the segment was *not* bumped. The
  check closed here is between the document and the schemas; the check between a schema's content
  and its declared contract version remains open, and is harder. It is recorded as unsolved rather
  than claimed as solved.
- "Breaking" is defined here by enumeration, not by a decision procedure. A change that is
  additive in form but breaking for a real adopter — a new optional field an adopter's own
  `additionalProperties: false` extension rejects, for instance — is not covered by the list.
- The rename that accompanies this decision changes every `$id` once. Any repository that installed
  Surfaceplate at `0.11.0` or earlier and upgrades will also receive a **second** conformance block
  in `.github/copilot-instructions.md`, because the installer's block markers were renamed and
  `upsert_conformance_block` locates an existing block by exact marker match. The old block is left
  behind, unmanaged. This is recorded, not fixed: the code's behaviour is unchanged, only its
  marker constant, and the sole current adopter is on `0.9.0`, which this release does not reach.
- F1, F2 and F3 as recorded in [DR-5](DR-5.md) remain open. This release deliberately does not
  touch them.

## Approval

- Technical reviewer: not assigned — see `org/decisions/README.md`. A single maintainer means no
  second technical reviewer exists.
- Method owner: not assigned, for the same reason.
- Independent validator: **not assignable.** Independence requires someone not involved in the
  work. No such person exists for this repository at present, and self-approval would not be
  independence. This is a stated constraint, not an oversight or a pending action.
- Release authority: not assigned, for the same reason.

This record does not itself constitute approval, validation, or release authorisation.
