# Decision Record

- Decision ID: DR-8
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision about the
  framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted — implemented in `v0.13.0`
- Risk level: 2 — "Output-affecting code, data, schema, or workflow", per the risk table in
  `core/REVIEW_AND_EVIDENCE.md`. It changes every code the conformance checker emits.
- Related work item: `v0.13.0` — strip the fabricated record, fix F1/F2/F3, rename the finding
  codes.

## Decision

Rename every conformance finding code from the `SDS` prefix to `SP`, preserving the numbers:
`SDS001` → `SP001`, through `SDS043` → `SP043`. 43 codes, 142 references across
`scripts/check_conformance.py`, `tests/test_install_and_check.py`, `core/PREREQUISITE_GATES.md`,
`CHANGELOG.md` and `DR-5`.

`SDS` abbreviated the framework's former name, which `v0.12.0` established was fabricated and
removed everywhere else. The codes were the last identifier still carrying it.

No mapping table is published, and no dual-emission period is served.

## Context and alternatives

This is a **breaking change to the checker's output contract** and is the one behaviour change in
`v0.13.0`. Every other change in that release is prose or test-harness internals. An adopter
grepping CI logs for `SDS038`, or a repository suppressing a specific code, is broken by it.

`v0.12.0` deliberately excluded this rename on exactly that ground — its work packet forbade
checker behaviour changes, so the codes were left carrying the old name and recorded as follow-up.
This record is that follow-up, taken as its own decision rather than smuggled into a rename pass.

**Rejected: dual-emit for one release** — have the checker print `SP038 (was SDS038)` through
`0.13.0` and drop the parenthetical at `0.14.0`.

Rejected because there is no adopter to protect. DR-7, recorded alongside this one, establishes
that this framework has never been installed in any repository other than this one: the three that
were recorded as adopters do not exist. A migration path is a cost paid to spare real users a real
break. With no users, dual-emission would widen the checker's output format, add a second format
to test, and require its own removal packet later — all of it to protect nobody. The window in
which a breaking rename is free is exactly the window this framework is in, and it closes with the
first genuine adopter.

**Rejected: publish a mapping table** in the changelog and a decision record. Rejected for the
same reason, and because the numbers are preserved: `SDS038` and `SP038` are the same finding, so
anyone holding an old log or an old changelog entry can map by eye without a table. A table
documenting a break that broke no one is maintenance weight.

**Rejected: keep `SDS` and redefine the letters** as a backronym. Rejected because the abbreviation
would then mean nothing in particular while looking as though it meant something — the same defect
class as a name that no longer matches what it names.

**Prefix choice.** `SP` was checked against the tree before use: no `SP\d{3}` string existed
anywhere, so the substitution could not collide with existing content. Two characters keeps the
checker's aligned output columns as they are.

## Impact

- Numerical/model output: none.
- Contracts/schemas: none. Finding codes are emitted output; they appear in no schema, and no
  schema constrains them.
- Security/data: none.
- Reproducibility/lineage: a CI log or exception record written before `0.13.0` names codes that
  the current checker no longer emits. The numbers are unchanged, so the mapping is mechanical,
  but it is a real discontinuity in the record and is stated here as one.
- Operations/release: any adopter tooling that matches on `SDS` breaks. There is no such adopter
  (DR-7).

## Evidence

- Code/configuration: the substitution across the five files named above. The `Finding` class in
  `scripts/check_conformance.py` is unchanged — it takes the code as a constructor argument, so
  only the literals moved and no rendering or control-flow logic was touched.
- Tests/checks: `git grep "SDS"` returns only the row in `org/decisions/README.md` that names the
  old prefix as part of recording this decision. `git grep -o "SP[0-9]\{3\}" | sort -u` returns
  42 distinct codes.
- Runtime evidence: the full suite passes unchanged after the rename —
  `INSTALL_CONFORMANCE=PASS (97 checks)`, which is the same count as before it. That suite asserts
  on specific codes in 40 places, so an incomplete substitution would have failed it rather than
  passing quietly.
- Independent review: none. Not reviewed by anyone beyond the session that made this change.

### An incidental finding

The rename surfaced one code that was never emitted. `SDS036` appeared exactly once in the
repository — in `org/CASE_FOR_ADOPTION.md`, one of the documents DR-7 deletes — and never in
`scripts/check_conformance.py`. The deleted document cited a finding code the checker does not
have. No action follows: the citation is gone with the file, and the checker's own codes are
contiguous apart from that gap. It is recorded because it is the same defect shape this repository
keeps finding — a claim that was written down and never checked against the thing it described.
The current code set therefore runs `SP001`–`SP035` and `SP037`–`SP043`.

## Limitations and follow-up

- Nothing enforces that a newly added finding code is unique, contiguous, or documented in
  `core/PREREQUISITE_GATES.md`. The existing catalogue check in `tests/validate_contracts.py`
  covers prerequisite-gate identifiers only, not the finding codes. `SDS036` existed as a
  documented-but-unimplemented code for an unknown number of releases without anything noticing,
  which is precisely what such a check would catch. Not added here; recorded as open.
- The prefix now matches the product name. If the product is ever renamed again, this cost recurs.
  Nothing in this decision prevents that, and nothing should: an identifier that matches its
  subject is worth the occasional rename, which is the same judgement `v0.12.0` made.

## Approval

- Technical reviewer: not assigned — see `org/decisions/README.md`. A single maintainer means no
  second technical reviewer exists.
- Method owner: not assigned, for the same reason.
- Independent validator: **not assignable.** Independence requires someone not involved in the
  work. No such person exists for this repository at present, and self-approval would not be
  independence. This is a stated constraint, not an oversight or a pending action.
- Release authority: not assigned, for the same reason.

This record does not itself constitute approval, validation, or release authorisation.
