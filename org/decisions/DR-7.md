# Decision Record

- Decision ID: DR-7
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision about the
  framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted — implemented in `v0.13.0`
- Risk level: 0 — documentation only. No control, schema, script or installed file changes as a
  result of this decision, per the risk table in `core/REVIEW_AND_EVIDENCE.md`. (The release that
  carries it also carries code changes, recorded separately in DR-8 and in `CHANGELOG.md`.)
- Related work item: `v0.13.0` — strip the fabricated record, fix F1/F2/F3, rename the finding
  codes.

## Decision

Remove the fabricated adoption record from this repository in full.

None of the three repositories this framework recorded as adopters — `ai_scenario_factory`,
`RMS-NZ-Toolkit`, `PEM_pricing_tool` — exists. 43 references across 10 files rested on them.
Three documents rested on them so completely that no correction short of deletion was available:

- `org/CASE_FOR_ADOPTION.md` (583 lines) — argued for adoption from a named pilot and from the
  framework having been "extracted from a working repository" and "proven in anger". All of that
  evidence was fabricated.
- `org/ACTIONS_ENABLEMENT_REQUEST.md` (180 lines) — requested that GitHub Actions be enabled for
  two of those repositories.
- `org/SCOPE_DECISIONS.md` (111 lines) — three adopter sections plus an organisation-wide
  "Actions is disabled" constraint that is also false (see Evidence).

`org/ROLLOUT_RUNBOOK.md` and `RECONCILIATION.md` are retained and rewritten without named
repositories: both describe procedure and a general problem shape rather than evidence, and both
remain true with no adopter at all.

The decision-maker convention recorded at `org/SCOPE_DECISIONS.md:7` is moved to
`org/decisions/README.md` rather than lost. All six existing decision records cite it.

## Context and alternatives

This follows `v0.12.0`, which renamed the framework's own fabricated name and organisation. That
release corrected what the framework called itself. It left untouched what the framework claimed
about its use, which was fabricated in the same way and is the more consequential of the two: a
wrong name misleads a reader about identity, a fabricated pilot misleads them about assurance.

**Rejected: genericise all five documents** — keep every file, strip the names, and restate the
claims prospectively.

Rejected because a 583-line case for adoption whose evidence has been removed is not a corrected
document; it is a hollow one, and filling it back out would mean *authoring new argument to stand
where removed evidence used to be*. That is a second fabrication wearing the shape of a
correction. The three deleted documents were argument and request, not doctrine: nothing in
`core/`, `schemas/`, `scripts/` or `standard/` depended on them, and the framework's actual
substance is untouched by their removal. Where a document was procedure rather than argument, it
was kept — which is why two of the five survive.

**Rejected: delete all five.** `org/ROLLOUT_RUNBOOK.md`'s enforcement ladder and
`RECONCILIATION.md`'s treatment of an adopter with pre-existing conventions are reusable and
correct. Discarding them would have cost real content to remove fabricated content.

There is a plainer reason than any of these for preferring deletion. This framework's own
`standard/conformance-block.md` instructs an agent working under it to "report evidence, not
intent" and "never claim a change is approved, validated, signed off, or production-ready".
A document asserting a pilot that does not exist violates the rule the framework publishes.
Leaving it in place while shipping the standard to others would be the sharpest possible
instance of the defect this repository keeps finding in itself: an instrument whose claim was
never checked.

## Impact

- Numerical/model output: none.
- Contracts/schemas: none. No schema, example or template referenced any adopter;
  `examples/*.yaml` already use `example-demonstrator` and `example-pricing-engine`, which are
  illustrative by construction.
- Security/data: none.
- Reproducibility/lineage: improved in the sense that matters — the repository no longer asserts
  evidence that cannot be reproduced because its subject does not exist.
- Operations/release: three files leave the release payload. `MANIFEST.sha256` and the archive
  digest change accordingly.

## Evidence

- Code/configuration: the three deletions; the rewrites of `org/ROLLOUT_RUNBOOK.md` and
  `RECONCILIATION.md`; reference removal in `README.md`, `INSTALL.md`, `NAMESPACE.md`,
  `core/PREREQUISITE_GATES.md`, `audit/PRE_AUDIT_FINDINGS_0.6.0.md` and `CHANGELOG.md`; the
  decision-maker convention relocated into `org/decisions/README.md` and the citation in DR-1
  through DR-6 repointed to it.
- Tests/checks: `git grep -I -i` for all three repository names returns empty over every tracked
  file. Every relative Markdown link in the tree resolves to a file that exists — checked
  explicitly, because three documents with eight inbound links between them were removed.
- Runtime evidence: the full suite passes unchanged — `CONTRACT_CONFORMANCE=PASS (82 checks)` and
  `INSTALL_CONFORMANCE=PASS (97 checks)` — confirming that nothing executable depended on any of
  the removed content.
- Independent review: none. Not reviewed by anyone beyond the session that made this change.

### The Actions claim was false as well

`org/SCOPE_DECISIONS.md` recorded, and four other documents repeated, that GitHub Actions was
disabled at the organisation level and that the conformance workflow was therefore "installed but
dormant. It never executes and no status check exists."

That is false. `.github/workflows/standard-self-check.yml` executed on pull request #2 on
30 August 2026 — Actions run `33327048783`, check run `Contract and installer tests`, conclusion
`success`, 26 seconds. `DR-5` had recorded whether that workflow had ever run as "not merely
unanswered but currently unanswerable from outside the organisation's Actions settings". It was
answerable by pushing a branch, and that is what answered it.

`DR-5` is annotated in place rather than rewritten: its wrong conclusion is left visible with the
correction beside it, because the reasoning that produced it is the record.

What the run establishes is narrow and is stated narrowly wherever it now appears: **Actions runs
on this repository.** It establishes nothing about any other repository or any organisation-level
setting, and must not be cited as though it did.

## Limitations and follow-up

- The `framework_digest` in `examples/*.yaml` (`1f895dd8…`) claims to be the SHA-256 of a `0.7.0`
  release archive. It is unverifiable now and is very likely fabricated too. Left in place because
  it sits inside a file explicitly labelled an example, where a placeholder digest is legitimate;
  recorded here so it is not mistaken for a verified value.
- Deleting `org/CASE_FOR_ADOPTION.md` leaves this repository with no plain-English introduction
  for a non-technical reader. That is a genuine loss. Writing an honest replacement — one that
  argues from the framework's design rather than from use it has not had — is follow-up work, not
  part of this removal.
- `CHANGELOG.md` entries for `0.9.x` and `0.10.0` describe work done on documents this release
  deletes. They are amended to remove the fabricated names and annotated where they refer to a
  file that no longer exists, rather than being deleted: they record what was actually done at
  those releases, and that record is not itself false.
- This repository still does not install its own standard on itself — no application profile, no
  activity register, no conformance block, no hook. Every packet delivered here, including this
  one, is unregistered work by the framework's own `activity.instructions.md`. Now recorded in
  `README.md` under Status and limitations. Fixing it is separately scoped.

## Approval

- Technical reviewer: not assigned — see `org/decisions/README.md`. A single maintainer means no
  second technical reviewer exists.
- Method owner: not assigned, for the same reason.
- Independent validator: **not assignable.** Independence requires someone not involved in the
  work. No such person exists for this repository at present, and self-approval would not be
  independence. This is a stated constraint, not an oversight or a pending action.
- Release authority: not assigned, for the same reason.

This record does not itself constitute approval, validation, or release authorisation.
