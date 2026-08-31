# Decision Record

- Decision ID: DR-9
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision about the
  framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted — implemented in `v0.14.0`
- Risk level: 2 — "Output-affecting code, data, schema, or workflow", per the risk table in
  `core/REVIEW_AND_EVIDENCE.md`. It adds a checked file to the release payload, a new CI step, and a
  new declared source of truth.
- Related work item: `v0.14.0` — tag the tip, record F5, add the derived-identifier control.

## Decision

Record **F5**: three spellings of the organisation identifier are live in this repository, and one
of them does not resolve. Add `ORGANISATION.md` as the declared source of truth for the
organisation identifier, and `tests/check_identifiers.py` as a derived check against it — the same
declare/derive shape `DR-6` established for the schema namespace, extended to a second identifier.

The check is **not** fixed to pass. It fails today because F5 is real, and its failing output is
the evidence recorded below. No fix to the drift itself is made here; that is a separate decision,
because the fix touches the URN authority, which `DR-6` governs.

## Context and alternatives

**F5.** A case-insensitive search for every token sharing the organisation's stem, plus a manual
GitHub lookup, established three disagreeing spellings and one broken one:

| Spelling | Occurrences | Where | Kind |
|---|---|---|---|
| `pipo-ventures` | 10 | `NAMESPACE.md:6,12`; `schemas/*.schema.yaml:2` (×6 — `application-profile`, `assurance-evidence`, `gate-exception`, `method-registry-entry`, `method-run-lineage`, `override-record`); `CHANGELOG.md:73,418` | URN authority — internally consistent, governed by `DR-6` |
| `Pipo-Ventures-Ltd` | 1 | `INSTALL.md:29` | GitHub clone URL — **does not resolve** |
| `pipoventures` | 1 | `CHANGELOG.md:527` (pre-`0.14.0`) | the maintainer's email domain, `mario@pipoventures.com` — coincides with the GitHub organisation slug but is a distinct fact |
| `Pipo Ventures Ltd` | 1 | `standard/conformance-block.md:3` | prose legal-entity name |
| bare `Pipo` | 12 | `org/decisions/DR-1.md`–`DR-8.md:7`; `README.md:164`; `org/decisions/README.md:10`; `audit/PRE_AUDIT_FINDINGS_0.6.0.md:6` | the maintainer's surname — not the organisation |

No underscore-separated or camel-case variant of the organisation name occurs anywhere in the
tree, and no filename contains it. `LICENSE:189` is unfilled Apache-2.0 boilerplate — no copyright
line names any entity.

The broken one, reproduced directly:

```
$ git ls-remote --heads https://github.com/pipoventures/surfaceplate.git
46547ba212ff05799044a7faae3a2d1680d584ad	refs/heads/main

$ git ls-remote --heads https://github.com/Pipo-Ventures-Ltd/surfaceplate.git
remote: Repository not found.
fatal: repository 'https://github.com/Pipo-Ventures-Ltd/surfaceplate.git/' not found
```

`FACT FROM PACKAGE`, directly reproduced against the live remote. `pipoventures` serves this
repository's `main`. `Pipo-Ventures-Ltd` returns a hard 404-equivalent, with no GitHub
organisation-rename redirect in effect. `INSTALL.md`'s only clone command — the documented first
step of installing this framework anywhere — names the owner that does not resolve.

**Severity: medium.** Not low: the command as documented cannot work, which is a hard failure of
the documented install path, not a cosmetic inconsistency. Not high: `DR-7` establishes there are
zero adopters, so nothing is broken for anyone today, and the repair is a one-line change once
scoped. A reader weighting "adoption is the framework's entire purpose" more heavily could reasonably
argue high; the reasoning is stated here so the judgement is reviewable rather than asserted.

This is the **third** instance of identifier drift in this repository: the namespace version
segment (`DR-6`, which states the finding in prose as "F4" but never gave it a register entry — not
corrected retroactively here, `DR-6` stands as written), and the `SDS`/`SP` finding-code prefix
(`DR-8`). Three occurrences of the same defect shape earns a control rather than a fourth one-off
repair, which is the decision this record makes alongside recording F5 itself.

**Rejected: put the check inside `tests/validate_contracts.py`.** That would match `DR-6`'s own
precedent most directly, but `scripts/build_release.py` refuses to build unless
`validate_contracts.py` passes, and that build is the only sanctioned way to regenerate
`MANIFEST.sha256`. A failing check inside it would leave the manifest permanently stale at the tip
and the tree un-releasable for as long as F5 stands — reconstructing, one call deeper, the exact
defect the `v0.14.0` citation repair exists to close. Rejected for that reason, not because the
check is weaker standalone: it is not; only its wiring into the *release* gate is deferred.

**Rejected: fix the drift as part of recording it.** Rejected for the same reason `DR-5` gives for
F1–F3: a fix bundled into a findings record reads as remediation evidence for something not
verified end-to-end, and this work was scoped to the check, not the reconciliation. The fix also
touches the URN authority specifically, which `DR-6` reserves to its own governance.

## Impact

- Numerical/model output: none.
- Contracts/schemas: none. `ORGANISATION.md` declares no schema `$id`; `tests/check_identifiers.py`
  reads schema `$id`s to verify their URN authority but writes nothing.
- Security/data: none.
- Reproducibility/lineage: improved for the same reason `DR-6` records — a declared value that is
  actually enforced can be trusted; a declared value nothing derives from can drift silently, which
  is exactly how F5 accumulated across three releases without detection.
- Operations/release: `.github/workflows/standard-self-check.yml` gains a fourth step,
  `python tests/check_identifiers.py`, placed last so the three existing steps still run and report
  before it fails. CI is red on this step, and only this step, until F5 is fixed.
  `scripts/build_release.py` is unchanged; a release still builds and verifies while F5 stands.

## Evidence

- Code/configuration: `ORGANISATION.md` (new) — the declared source of truth, in the same
  pattern/current/exclusions shape `NAMESPACE.md` uses for the schema namespace, plus a third block
  naming tokens that share the stem but are not the organisation. `tests/check_identifiers.py`
  (new) — `read_declared_organisation()` mirrors `validate_contracts.py`'s
  `read_declared_namespace()`: the literal lives only in the document, both blocks are parsed and
  cross-checked, every parse failure raises, and error messages name the governing document and
  section.
- Tests/checks: the check was run against this repository and observed to fail, and separately
  against a synthetic tree in which the identifiers agree and observed to pass. The two lines that
  are the actual, load-bearing defect:

  ```
  $ python tests/check_identifiers.py
  IDENTIFIER_CONFORMANCE=FAIL  (N failed, M passed)
    - github-url:INSTALL.md:29: github.com/Pipo-Ventures-Ltd/ does not match declared github-org 'pipoventures'
    - undeclared-token:INSTALL.md:29:Pipo-Ventures-Ltd: 'Pipo-Ventures-Ltd' is not a declared
      identifier or a declared exclusion in ORGANISATION.md
    ... every remaining failure line names org/decisions/DR-9.md, not a second site ...
  ```

  Every failure beyond those two names this file — `org/decisions/DR-9.md` — as the site, because
  this record's inventory table and its literal reproduction of the broken clone command, both
  above, are themselves occurrences of the undeclared spelling once this file is part of the
  checked tree. `N` and `M` are deliberately not fixed numbers here: each time this record is
  edited, its own quotation count changes, which changes what the next run reports about this
  record — a moving target this record cannot describe a single correct snapshot of without going
  stale the next time it is edited. That is not a second defect: the check cannot distinguish a live
  instruction from a quoted historical fact (stated as a limitation below), and a findings record
  quoting the exact text of the finding it records is expected, not itself wrong — `DR-8` quotes
  `SDS036` the same way. What does not move: exactly one site outside this record fails —
  `INSTALL.md:29` — under both rules, and it is the only failure a fix would need to touch.

  Against a synthetic copy of the tree with `Pipo-Ventures-Ltd` mechanically replaced by
  `pipoventures` in `INSTALL.md` and in this record:

  ```
  $ python tests/check_identifiers.py --root /path/to/synthetic-agreeing-copy
  IDENTIFIER_CONFORMANCE=PASS  (N+M checks)
  ```

  Verified directly, for one such pair of runs: the passing run's check count equalled the failing
  run's total (failed + passed) exactly — the synthetic tree passes the *same* checks the live tree
  fails, not a smaller set that happens not to trip anything.
- Runtime evidence: `tests/validate_contracts.py` and `tests/test_install_and_check.py` both pass
  unchanged after these additions, confirming the new files do not reach either existing suite.
- Independent review: none. Not yet reviewed by anyone beyond the session that made this change.

## Limitations and follow-up

- The check is a text scan, not a semantic parser. It cannot tell a live instruction (a command
  someone will run) from a quoted historical fact (a decision record citing the wrong spelling as
  evidence of itself) — both register identically as occurrences. See "Tests/checks" above for the
  concrete instance: this record's own evidence.
- It establishes *that* the identifiers disagree, not *which* one is correct. That determination —
  `pipoventures` is the live GitHub organisation, established by `git ls-remote` — is deliberately
  not encoded in the check itself, because a network call would make a CI step non-hermetic. The
  check instead treats `ORGANISATION.md`'s declared value as authoritative by construction, the same
  way `NAMESPACE.md`'s declared base is authoritative for the namespace check regardless of how that
  value was chosen.
- The check is not wired into `scripts/build_release.py`'s build gate (see "Rejected" above). A
  release can therefore still be built and tagged while F5 stands. This is a deliberate, stated
  trade-off, not an oversight.
- F5 is not fixed by this record. Fixing it requires reconciling three spellings to one, which
  touches the URN authority `DR-6` governs, and is separately scoped work.
- `DR-6`'s own "F4" — stated in that record's prose but never given a register entry — remains
  unregistered. Not corrected here: `org/decisions/README.md` requires `DR-5` be left as written,
  and `DR-6` is not `DR-5`, but retrofitting a register entry into an already-accepted record for a
  finding this record did not itself investigate is out of scope.

## Approval

- Technical reviewer: not assigned — see `org/decisions/README.md`. A single maintainer means no
  second technical reviewer exists.
- Method owner: not assigned, for the same reason.
- Independent validator: **not assignable.** Independence requires someone not involved in the
  work. No such person exists for this repository at present, and self-approval would not be
  independence. This is a stated constraint, not an oversight or a pending action.
- Release authority: not assigned, for the same reason.

This record does not itself constitute approval, validation, or release authorisation.
