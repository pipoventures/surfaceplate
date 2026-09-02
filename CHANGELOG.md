# Changelog

## 0.2.0 - first audit remediation draft

- Replaced the undocumented custom schema dialect with JSON Schema Draft 2020-12 expressed as YAML.
- Added typed assurance evidence and override schemas with conditional approval rules.
- Removed `approved` from method lifecycle status and coupled final validation/approval states to evidence.
- Strengthened completed, material, and AI run-lineage provenance requirements.
- Removed mandatory frontend/backend/test-runner topology and predecessor-application-specific assumptions from universal contracts.
- Removed scenario/package fields from universal run lineage; applications must own domain extensions.
- Coupled final assurance states to qualifying evidence type and outcome, including independence basis.
- Made AI/completed provenance non-null when required, allowed failed runs without outputs, and corrected override approval lifecycle rules.
- Made control decisions a single keyed authority and expanded semantic negative conformance tests with date-time checking.
- Made application control selection explicit instead of preselecting every control.
- Made actual diff evidence mandatory for material or audit-triggered work.
- Added package ownership/version/change notes and a cross-platform ZIP requirement to the audit prompt.

This release has not been approved for production or broad adoption. It requires re-audit.

## 0.3.0 - second-audit remediation draft

- Coupled `passed` and `approved` method states to qualifying evidence types and outcomes.
- Required independence basis for independent-validation evidence.
- Made completed timestamps and completed AI provenance values non-null when required.
- Allowed failed/blocked/cancelled runs to have no outputs.
- Separated override approval requirement from lifecycle outcome and required approval for high/material-impacting overrides.
- Made application control decisions a single keyed authority.
- Removed predecessor-application-specific fields from universal run lineage.
- Added semantic negative conformance cases, format checking, security baseline, and producer validation record.
- Added conditional limitation/condition details, approval-specific override evidence and timestamp, mandatory baseline control IDs, execution-eligibility guidance, and canonical maintainer requirements.

This release remains pending ChatGPT Enterprise re-audit and human adoption decisions.

## 0.4.0 - third-audit remediation draft

- Added explicit `passed_with_conditions` and `approved_with_conditions` statuses so conditional evidence cannot appear as unqualified assurance.
- Added approval-specific override evidence references and timestamps.
- Added mandatory baseline control IDs and stable selectable control IDs with namespaced application extensions.
- Defined lifecycle `active` as catalogue state only, never execution authority.
- Corrected historical release wording and documented canonical kit maintainer responsibility.

This release remains pending ChatGPT Enterprise re-audit and human adoption decisions.

## 0.5.0 - adoption setup guide

- Added `SETUP_GUIDE.md` with the complete repository adoption sequence, implementation boundaries, validator wiring, execution eligibility, override handling, CI/security gates, human review, and definition of done.

This release remains pending ChatGPT Enterprise re-audit and human adoption decisions.

## 0.6.0 - Copilot adoption wizard

- Added `prompts/github-copilot-adoption-wizard.prompt.md`, a reusable GitHub Copilot Chat prompt for discovery, human questioning, profile setup, bounded implementation, validation, review gates, and completion reporting.

This release remains pending ChatGPT Enterprise re-audit and human adoption decisions.
## 0.7.0 - adoption identity, namespace, and conformance levels

Renamed from "Tool-Agnostic AI Engineering Control Kit" to **Surfaceplate** to
reflect use as a business-unit standard covering all software, not only AI-assisted projects.

Remediates findings F1-F4 from the technical pre-audit of 0.6.0
(`audit/PRE_AUDIT_FINDINGS_0.6.0.md`).

- **F1 (high).** Added a required `adoption` object to the application profile: `framework_version`,
  `framework_digest`, `adoption_date`, `framework_maintainer`, `repository_classification`,
  `decision_record_id`, `adoption_status`, optional `status_rationale`, `independent_validator`,
  and owned `deferrals`. `SETUP_GUIDE.md` Step 1 and the Definition of Done mandated these facts,
  but the schema had no fields for them, and `additionalProperties: false` prevented adopters from
  adding them. Adoption state is now machine-queryable across a portfolio of applications.
- **F1 follow-on.** `adoption_status` of `blocked` or `deferred` now requires `status_rationale`.
  Every control decided `deferred` must have an owned entry in `adoption.deferrals` with a
  `revisit_by` date; silent deferral now fails the conformance tests.
- **F3 (medium).** Replaced the placeholder `https://example.invalid/` schema `$id` base with
  `urn:pipo-ventures:surfaceplate:0.7.0:`. The base is declared once, documented in
  `NAMESPACE.md` with a migration procedure, and asserted by the conformance tests.
- **F2 (medium).** Regenerated `audit/VALIDATION_RESULTS.md`, which described release 0.5.0 and 26
  files while 0.6.0 actually shipped 28 files, leaving the 13 KB adoption wizard prompt covered by
  no recorded producer check.
- **F4 (low).** Added `examples/` with golden valid instances for the `essential` and `full`
  application profiles and an approved override record, all asserted by the conformance tests.
  Rewrote `templates/application-profile.yaml` so the `control_decisions` placeholder is no longer
  an invalid *key*, and stated explicitly that templates are fill-in forms that do not validate
  until completed.
- **New.** Added graded conformance levels `essential`, `standard`, and `full`
  (`core/CONFORMANCE_LEVELS.md`), with `conformance_level` required in the application profile.
  Levels are enforced semantically in `tests/validate_contracts.py`, because a JSON Schema cannot
  check one field's value against another field's keys. Overclaiming a level now fails.
- **New.** Added `scripts/build_release.py` and `scripts/verify_release.py` to support the pinned
  release distribution model. The builder refuses to produce an archive when the conformance tests
  fail.

Adds 30 new positive and negative conformance cases.

This release has **not** been independently audited. The ChatGPT Enterprise audit in
`audit/CHATGPT_ENTERPRISE_AUDIT_PROMPT.md` remains outstanding and is required before rollout
beyond the initial adopting repositories.

## 0.8.0

Turns the framework from a document set into something that can be installed into any repository
and verified afterwards. The control contract is unchanged; this release adds the distribution and
enforcement machinery around it.

- **New.** `standard/` holds the portable payload: six stack-neutral instruction files and seven
  task skills (`change`, `bug-fix`, `review`, `fix-ci`, `dependency-update`, `security-review`,
  `release`), written stack-neutral: no language, framework or host specifics.
- **New.** `scripts/install_standard.py` installs or upgrades the standard in a target repository.
  It is idempotent, removes controls dropped by a newer version, never overwrites the adopter's
  application profile, and appends to the adopter's Copilot instructions between markers rather
  than rewriting the file. It **refuses to run**, writing nothing, when the target already has its
  own files at standard-owned paths.
- **New.** `scripts/check_conformance.py` is the enforcement point: presence, byte-level integrity
  of every standard-owned file, integrity of the conformance block, and schema plus semantic
  validation of the application profile. Vendored into adopting repositories so they need nothing
  but Python.
- **New.** A 30-day adoption grace window for profile completeness only. Integrity findings are
  never graced. The window is measured from first install and independently capped, so re-running
  the installer or hand-editing the recorded expiry does not extend it.
- **New.** `org/ruleset-standards-conformance.json` and `org/ROLLOUT_RUNBOOK.md` prepare
  organisation-level enforcement, in evaluation mode first. Neither has been applied.
- **New.** `tests/test_install_and_check.py` — 37 end-to-end checks covering install, upgrade,
  idempotency, tamper evidence, repair, grace-window integrity, collision safety, additive
  layering, and stale-control removal. `build_release.py` now refuses to build unless these pass
  too, and gained `--verify-manifest`.
- **New.** `INSTALL.md` and `RECONCILIATION.md`; `README.md` rewritten.
- **Fixed.** `build_release.py` excluded neither scratch nor cache directories, so a manifest built
  on a working machine could have included files that were never part of the standard.

Known limitation, stated plainly: without the organisation ruleset, a repository administrator can
delete the workflow and the check stops running. Layer 2 of 4 on the enforcement ladder. This
release remains **not independently audited**.

## 0.8.1

Fixes a defect in 0.8.0 found by challenge rather than by testing: *how do we know the three
conformance levels actually work?* They did not, in the place that matters.

- **Fixed (material).** `scripts/check_conformance.py` recognised the three conformance level
  *names* but never checked that the declared level's controls were present and decided
  `required`. `tests/validate_contracts.py` enforced this rule inside the standards repository, so
  the framework's own examples were held to it — but the checker installed into adopting
  repositories was not. An adopting repository could therefore declare `full` while deciding
  nothing, and pass. The level was a label, not a commitment.

  Ported the rule and the level-to-controls map into the installed checker, as findings `SP021`
  (required control absent) and `SP022` (present but decided something other than `required`).
- **Fixed.** The installed checker also did not enforce that a control decided `deferred` appears
  in `adoption.deferrals` with an owner and a revisit date. A deferral nobody owns is an
  exclusion. Added as `SP023`.
- **New tests.** Nine end-to-end cases covering all three levels: each level's worked example
  passes at its own level; an `essential` profile relabelled `standard` or `full` is rejected and
  the missing control is named; a `full` profile may declare a lower level, because a level is a
  floor and not a ceiling; a required control present but decided `excluded` is rejected; and an
  unrecognised level does not silently pass. 46 checks in total.

The general lesson, worth recording: the same rule was written twice, in the repository's own test
suite and in the checker it distributes, and only one copy was complete. Duplicated enforcement
logic drifts. Any future control rule belongs in the installed checker first, with the repository's
own tests exercising that same code path.

---

## 0.9.0 — enforcement described honestly, and profiles that expire

Two changes, both prompted by evidence rather than by design review.

### GitHub Actions is disabled at organisation level

Discovered 2026-08-28, on checking whether the pilot repository's conformance workflow had ever
actually run. It had not, and it never can while the setting stands.

This invalidated claims made throughout the documentation. The README said the conformance check
"verifies in CI"; `INSTALL.md` described CI staying green; `ROLLOUT_RUNBOOK.md` placed the project
at rung 2 of a four-rung enforcement ladder and described rung 3 as merely unapplied. None of that
was true. Rung 2 requires a workflow that runs. Rung 3 requires a status check for a ruleset to
demand, and no status check can exist while no workflow runs, so rung 3 is unreachable rather than
pending.

- **Added rung 0 to the enforcement ladder** — "adopted but dormant" — and placed the project on
  it. Rung 0 sits *below* rung 1 deliberately: a published-but-unadopted standard makes no claim,
  whereas an adopted-but-dormant one invites a reader to assume a check is running when none is.
  The second state is worse than the first, and naming it is the only way to stop it being read as
  the third.
- **Rewrote the enforcement claims** in `README.md`, `INSTALL.md` and `ROLLOUT_RUNBOOK.md`. Added
  "Where this check actually runs" to `INSTALL.md`. The constraint is now the first thing the
  runbook says.
- **Separated the two halves of what this repository delivers.** The instructions and skills work
  today, in any repository, on any host, because Copilot reads them from the workspace and no CI
  is involved. The conformance check and the ruleset do not run at all. Conflating them overstated
  the assurance by a wide margin.
- **Recorded the constraint** in the organisation governance documents, with the workflow quoted
  in full, its permissions enumerated, and four named ways the answer could be "no".

The README also still declared itself version 0.7.0 while `VERSION` read 0.8.1. Corrected.

### Profiles now expire

The pilot repository completed most of its Phase 0 work in the week after adopting. Its own
adoption decision record named the conditions that would require its conformance level to be
raised, and those conditions were met. Nothing noticed, and nothing could have: the files were
intact, the schema was satisfied, and the declared level was simply no longer the right one.

An integrity check cannot detect that a repository has outgrown its own judgement. Only a human
re-reading the profile can, and only if something makes them.

- **`adoption.review_by` is now a required field**, enforced in `check_conformance.py` before it is
  enforced in the schema — per the lesson recorded under 0.8.1.
  - `SP024` — no review date, or one that is not a readable ISO date. Graceable.
  - `SP025` — the review date has passed. Graceable, though the grace window will long since have
    closed in any realistic case.
  - `SP026` — the review date is more than `MAX_REVIEW_HORIZON_DAYS` (400) ahead. **Never
    graced**, for the same reason `MAX_GRACE_DAYS` caps the grace window independently of what the
    install record claims: a control an adopter can defer to 2099 is decorative.
- **Advisory output.** A review falling due within 30 days prints an `Advisory` section and still
  exits 0. Warning before failing is the point; a control that fails without notice gets worked
  around.
- **Schema, template and both worked examples** carry the field. 180 days is the suggested
  interval.

**Breaking for adopters.** An existing profile lacking `review_by` will report `SP024` after
upgrading. The fix is one line.

Six new end-to-end cases: absent, unreadable, overdue, beyond the horizon while inside the grace
window, falling due soon, and live. 52 checks in total.

## 0.9.1 — the case for adoption, written down

Documentation only. **No change to any control, schema, script or installed file.** An adopter on
0.9.0 gains nothing by upgrading and loses nothing by not.

- **An adoption case document** — a plain-English account of what the standard is for, what the AI
  operating model actually requires, exactly which files an adopting repository receives, what
  changes day to day, and what adoption costs. (Deleted at 0.13.0; see below.)

Three things about it are deliberate and worth recording, because the temptation was to write the
document without them:

- **The organisation-level disablement of GitHub Actions is stated in the opening section**, not in
  a limitations note at the end. A benefits paper that mentions the blocker last is a paper whose
  reader discovers the blocker last.
- **It carries a costs section.** Half a day to adopt, an hour or two per review cycle, and the
  loss of the quiet shortcut of weakening a test to unblock yourself. That last one is listed as a
  cost, because it is one.
- **It argues against itself where the argument is sound.** If Actions is never enabled, the
  document says the right answer is probably local pre-commit hooks rather than keeping a
  CI-shaped framework alive out of optimism.

The release is versioned rather than the manifest being regenerated in place, because `org/` is
inside the release payload and 0.9.0's archive digest is recorded as provenance. Rebuilding a
released artefact so that a new file fits inside it is the exact
tamper pattern `SP004` and `SP005` exist to detect. Doing it for our own convenience would be the
worst precedent available to us.

## 0.9.2 — what this is a subset of

Documentation only. **No change to any control, schema, script or installed file.**

- **The adoption case** gains "What was deliberately left behind": an explicit table of what
  this standard does not carry, why each was left out, and the intended direction of travel
  labelled as intent rather than commitment.
- **The Actions enablement request and the adoption case are reconciled.** The one-line ask is
  now identical in both; each points at the other; and the request states that the two
  accompanying asks — a 90-day pilot and an independent reviewer — are not decisions for the
  organisation owner and are not conditions of it.

The subset section exists because the omission was material in both directions: a reader would
otherwise have had no way to tell what this standard covers from what it does not.

(Both documents were deleted at 0.13.0; see below.)

Two asymmetries are now stated rather than left to be discovered:

- **NZ enforces at commit time; this standard does not enforce at all.** Seventeen hooks
  that block, including a gate gating any change to mapped code or data on the governing
  document being updated in the same commit, against 26 rules that presently run only when
  a human runs them. `secret_hygiene` is required by this standard at every level and has
  no check of any kind; NZ has a working one.
- **NZ's operating model carries a recorded approval** — an approver, a date, and an
  explicit statement of what the approval does not cover. This standard's carries none.

## 0.10.0 - Prerequisite gates

**The first control in this framework that works with GitHub Actions disabled.**

Every existing control describes what a repository *does*. A prerequisite gate describes
what a repository *may not do yet*: *X must exist before Y may begin*. The evidence for a
gate is not an artefact but the **order of events**, and the order of events is permanent
in git history. So the check reads the commit graph rather than the working tree.

The resulting guarantee is narrower than prevention and survives the thing that has
neutered layers 2 and 3 since adoption began:

> No repository state containing a violation can pass the check, whenever that check runs.

A developer can bypass a gate - `--no-verify` defeats any hook, and no server-side check
runs. What they cannot do is bypass it *and* have the repository pass afterwards, because
repairing the file later does not repair the history.

### Added

- **`core/PREREQUISITE_GATES.md`** - the 19-gate catalogue in six groups, the enforcement
  claim stated honestly, and the reasoning for `effective_from` and for exceptions.
- **`prerequisites` block** in the application profile, with a `prerequisite_gate` schema
  definition. Each gate carries a status of `required`, `deferred` or `not_applicable`,
  its precondition artefacts, the paths it gates, and how it is enforced. `unenforced` is
  a permitted value of `enforcement`, and saying so is required rather than optional.
- **Git-history audit** in `scripts/check_conformance.py`. For each required gate it walks
  every commit since `effective_from` that touched a gated path and asks whether the
  precondition existed in that commit's tree.
- **`schemas/gate-exception.schema.yaml`** and **`templates/gate-exception.yaml`**. A
  control with no legitimate escape route gets bypassed illegitimately instead. An
  exception names specific commits, an accountable human and a rationale, and clears
  exactly those commits.
- **Findings `SP027`-`SP035`, and `SP037`.**

### The interface floor

The four interface gates - `component_library`, `design_authority`, `options_before_build`,
`prerequisite_state_ui` - are a **floor** at `standard` and `full` for any repository
declaring the new `builds_user_interface: true`.

They are not an absolute floor, because the checker cannot tell whether a repository has a
user interface and an unconditional requirement would leave a headless service able to
conform only by declaring paths it does not have. That is a fake pass, and worse than an
honest exemption. So the repository declares the fact in one boolean, and the two answers
are held to be consistent with the four gate statuses in both directions.

Note what this removes. Under the declare-or-justify scheme this release first shipped, a
team building screens could write "we will define the design policy next sprint"
indefinitely and pass. That option no longer exists: at `standard` and above, a repository
that builds interfaces either has decided its component library, its design policy and its
page templates before starting, or it fails. `builds_user_interface: false` is a claim about
the world that a reviewer can falsify in seconds, which is a better control than a rationale
nobody reads.

### Changed

- **Levels now carry a gate floor as well as a control floor.** `essential` requires
  `work_registration`; `standard` and `full` require progressively more, and additionally
  require that **every** catalogue gate is declared one way or the other. A repository with
  no user interface should record that the four interface gates do not apply to it. Silence
  is not a decision.
- Both worked examples declare gates. The `full` example decides all nineteen, four of them
  `not_applicable` because the application is a headless API.
- Test coverage rises from 52 checks to 74, including a real git repository exercising the
  history audit end to end: a compliant crossing, a bypass, the bypass being caught after
  the file was restored, an exception record clearing it, and a forward-moved
  `effective_from` being rejected inside the grace window.

### `effective_from` can never move forward

A gate binds from a date, so that adopting one does not require rewriting the past. The
obvious way to game that is to move the date forward, silently discarding every violation
in between. The checker therefore reads the profile's own git history, recovers the
earliest date each gate has ever declared, and fails if the current value is later.

`SP034` is **never graced**, for the same reason the review-horizon cap is never graced:
a control whose anti-gaming rule can itself be deferred is not a control.

### Where this came from

The catalogue articulates roughly twenty rules of this form and supplies an enforcing check
for each, which is the opposite of the direction the previous release described.

What is **not** carried across is NZ's design language. The rule being ported is *"decide
your component library, your design policy and your page templates before building any
interface"* - not *"use these components"*. The answers stay local; the requirement to have
answered before starting does not.

## 0.11.0 - Local pre-commit enforcement

The standard now ships a real local enforcement layer rather than merely permitting
`local_hook` as a profile claim.

- Added a tracked `.githooks/pre-commit` installed into every adopting repository, plus a nested
  `.gitattributes` rule that preserves the shell script's LF line endings across platforms.
- The installer configures repository-local `core.hooksPath=.githooks`, sets the executable bit,
  and stops before writing if an existing hook path or default pre-commit hook would be disabled.
- Added `--staged` to the conformance checker. It reads Git's index, matches staged paths against
  gates declaring `local_hook`, and raises non-graceable `SP039` when a prerequisite is absent,
  empty or unfinished in the staged snapshot.
- Added non-graceable `SP040` and `SP041`. The hook validates standard-owned files, the install
  record, managed Copilot block, executable mode and application profile from the index; a valid
  working tree cannot hide a staged broken control or malformed profile.
- Hook-time prerequisite validation now reads every required artefact from the index, including
  staged deletions where an unstaged working copy still exists. Unstaged profile edits do not
  reject a valid staged snapshot.
- Gate path matching delegates to Git, preserving the pathspec semantics used by the history audit.
  Git query failures raise non-graceable `SP042` rather than becoming a false empty result.
  Exception records are also loaded from the index, so unstaged records cannot suppress a finding.
- Gate exceptions are schema-validated before use and abbreviated SHAs are resolved by Git to a
  unique full commit. Invalid, ambiguous or unresolved records raise non-graceable `SP043` and
  provide no coverage.
- Strengthened `SP038`: a hook claim now requires a pre-commit hook in Git's active hooks
  directory and, on POSIX, an executable file. A hook-shaped file elsewhere is not evidence of
  activation.
- Hook collision detection now reads the effective Git configuration, including global and
  worktree values, and protects every existing hook type rather than only `pre-commit`.
- Clone activation is documented through the collision-aware installer only; the previous raw
  `git config core.hooksPath` instruction could have overridden an inherited hook path.
- The installer now requires the target to be the exact Git working-tree root, preventing an
  install into a subdirectory from reconfiguring an enclosing repository.
- The hook selects only a Python interpreter that can import both PyYAML and `jsonschema`; these
  runtime dependencies are now explicit installation requirements.
- Restored the four `local_hook` declarations in the full worked example now that the claimed
  mechanism exists.
- Kept the enforcement boundary explicit: `git commit --no-verify` can bypass the local hook, and
  GitHub Actions remains disabled. `core.hooksPath` must also be activated in each clone because it
  is local Git configuration. The history audit remains the durable detector after bypass.

## 0.12.0 - internal rename and namespace decision

Mechanical and locally reversible. No behaviour change to the checker, the hook, or the installer.

- Renamed every internal identifier to match this repository's name. The URN namespace base, the
  release archive name and its top-level directory, every `MANIFEST.sha256` path, the installer's
  `INSTALL.json` `standard` field, the conformance-block markers, the GitHub ruleset name, the
  product name in prose, and the organisation name throughout. Verified by search, not by memory.
- Schema `$id`s move to `urn:pipo-ventures:surfaceplate:0.7.0:<schema-file-name>`. Only the
  organisation and product segments changed; the version segment did not — see below. The checker
  resolves schemas by file path and never by `$id`, so no checker behaviour depends on this.
- **The URN version segment now tracks the schema contract version**, bumped only on a breaking
  schema change and independent of the framework version in `VERSION`. This replaces the previous
  rule, under which the segment was the framework version. Recorded as
  [DR-6](org/decisions/DR-6.md), with the rejected alternative — bumping `$id` on every framework
  release — and why: it breaks adopter pins on releases where the schema is unchanged. The current
  value stays `0.7.0`, carried forward, so no adopter's pinned identifier changes on account of the
  version segment at this release.
- `tests/validate_contracts.py` **derives** the expected namespace from `NAMESPACE.md` instead of
  holding its own copy of it. The previous hardcoded `NAMESPACE_BASE` agreed with the schemas by
  construction and so could never disagree with the document governing them: `NAMESPACE.md` claimed
  the segment was the framework version and drifted four releases from the schemas while the check
  passed on every release. The check now fails when the document and the schemas diverge, when the
  document contradicts itself, and when the declaration cannot be parsed at all. Each of those was
  observed to fail before release; a check that has not been seen to fail is not evidence that it
  can. The per-schema assertion also tightened from "begins with the base" to "equals the base plus
  the schema's own file name".
- **Upgrade note.** A repository that installed at `0.11.0` or earlier and upgrades to `0.12.0` will
  receive a *second* conformance block in `.github/copilot-instructions.md`. The block markers were
  renamed, and `upsert_conformance_block` locates an existing block by exact marker match, so it
  will not find the old one and appends a new one instead, leaving the old block in place and no
  longer managed by the installer. Remove the stale block by hand after upgrading. The installer's
  logic is unchanged; only its marker constant is. The sole current adopter is on `0.9.0` and is not
  reached by this release.
- F1, F2 and F3 as recorded in [DR-5](org/decisions/DR-5.md) remain open and are deliberately
  untouched. In particular `tests/validate_contracts.py` still prints no executed-check count (F3),
  and the installer/checker suite still requires `core.hooksPath` to be neutralised for the
  invocation (F1).

## 0.13.0 - remove the fabricated record; fix F1, F2, F3; rename the finding codes

One behaviour change, in the checker's emitted finding codes. Everything else is prose or
test-harness internals.

### The adoption record was fabricated, and is removed

None of the three repositories this framework recorded as adopters exists. 43 references across
10 files rested on them. Recorded as [DR-7](org/decisions/DR-7.md).

- **Deleted** `org/CASE_FOR_ADOPTION.md`, `org/ACTIONS_ENABLEMENT_REQUEST.md` and
  `org/SCOPE_DECISIONS.md`. Each was argument or request resting entirely on repositories that do
  not exist. The rejected alternative — genericise them instead — would have meant authoring new
  argument to stand where removed evidence used to be, which is a second fabrication wearing the
  shape of a correction.
- **Kept and rewritten without named repositories:** `org/ROLLOUT_RUNBOOK.md` and
  `RECONCILIATION.md`. Both describe procedure and a general problem shape, and both remain true
  with no adopter at all.
- **The decision-maker convention** recorded in `org/SCOPE_DECISIONS.md` is moved to
  `org/decisions/README.md` rather than lost — all eight decision records cite it.
- Historical `CHANGELOG.md` entries are amended to remove the fabricated names and annotated where
  they refer to a file that no longer exists. They are not deleted: they record what was actually
  done at those releases, and that record is not itself false.
- **This repository still does not install its own standard on itself** — no application profile,
  no activity register, no conformance block, no installed hook. Now stated plainly in `README.md`
  under Status and limitations, where it had never been admitted.

### GitHub Actions is not disabled

`.github/workflows/standard-self-check.yml` executed on pull request #2 on 30 August 2026 — run
`33327048783`, conclusion `success`, 26 seconds. Five documents stated the opposite in roughly 19
places, and one existed solely to request what was already available.

`DR-5` had recorded whether that workflow had ever run as "not merely unanswered but currently
unanswerable from outside the organisation's Actions settings". It was answerable by pushing a
branch. `DR-5` is annotated in place rather than rewritten: the wrong conclusion stays visible with
the correction beside it, because the reasoning that produced it is the record.

What the run establishes is stated narrowly wherever it now appears: **Actions runs on this
repository.** It establishes nothing about any other repository or any organisation-level setting.

### F1, F2 and F3 are fixed

All three were recorded in [DR-5](org/decisions/DR-5.md) at `0.11.0` and deferred.

- **F1** — `tests/test_install_and_check.py` neutralises the ambient Git configuration for the
  whole run (`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_NOSYSTEM`), extending the isolation its own
  global-`hooksPath` case already used. The suite no longer depends on an unstated property of the
  machine running it. Verified both ways: with a hostile `core.hooksPath` set globally, the
  previous version died with `FileNotFoundError` on `.github/skills` after 79 checks; the current
  version passes all 97. Running it no longer requires a `GIT_CONFIG_GLOBAL=/dev/null` prefix.
- **F2** — the PEP 668 case is documented rather than left to be discovered. `INSTALL.md` and
  `README.md` give the virtual-environment and distribution-package routes, and name the
  consequence the hook actually has: it resolves an interpreter from `PATH` and **fails closed**
  when it cannot find one with both dependencies. The hook's own error message now says the same.
  `referencing` is dropped from the documented install line — `jsonschema` pulls it in.
- **F3** — `tests/validate_contracts.py` reports an executed-check count on success:
  `CONTRACT_CONFORMANCE=PASS  (82 checks)`, matching the format
  `tests/test_install_and_check.py` already used. `CONTRACT_CONFORMANCE=PASS` remains a prefix of
  that line, so `scripts/build_release.py`'s build gate still recognises it — verified.

### Finding codes: `SDS` → `SP` (breaking)

`SDS001`…`SDS043` become `SP001`…`SP043`, numbers preserved. 142 references. Recorded as
[DR-8](org/decisions/DR-8.md).

**This breaks the checker's output contract.** Anything matching on `SDS` stops matching. No
mapping table and no dual-emission period are provided, because there is no adopter to protect —
DR-7 establishes the framework has never been installed anywhere but here, and that is exactly the
window in which a breaking rename is free. It closes with the first genuine adopter.

One incidental finding: `SDS036` was cited in `org/CASE_FOR_ADOPTION.md` and emitted by nothing.
The deleted document named a finding code the checker does not have. The current set is
`SP001`–`SP035` and `SP037`–`SP043`.

## 0.14.0 - repair citations from the authorship rewrite; record F5; add the identifier control

Two changes: the citation repair that had sat unreleased since `v0.13.0`, and new work responding
to a third instance of identifier drift.

### Citations repaired after the authorship rewrite

Every commit and tag in this repository's history had its author and committer identity rewritten
to Mario Pipo Sanchez `<mario@pipoventures.com>`. The prior history mixed four distinct identities
across 18 commits, nine of them under a corporate address that does not belong on this repository.
Content is unchanged: the pre- and post-rewrite tree of the tip is byte-identical except for the
`v0.13.0` changelog entry describing the rewrite and the six SHA citations below. Commit dates,
ordering, and message text are unchanged; only author/committer name, email, and (for tags) tagger
identity changed.

**Every pre-rewrite commit and tag SHA is now dead.** They were purged from this repository's
local object store and were never pushed to the republished remote — no pre-rewrite object exists
anywhere. The six citations of the pre-rewrite `v0.11.0` commit SHA
(`org/decisions/DR-1.md` through `DR-5.md`, and `org/decisions/README.md`) have been updated to
the corresponding rewritten SHA. `v0.11.0` was recreated as an annotated tag (previously
lightweight), carrying the release archive SHA-256 and the conditional 97/97 test result that were
previously recorded only in the commit message.

Two references remain stale by design, because they live in commit messages rather than tracked
files, and no commit in this repository is reworded: `2ceed68`'s original message cites `426ec11`,
and `e4e134d`'s original message cites GitHub Actions run `33327048783` and PR `#2`. Both citations
predate the rewrite and refer to identifiers from the destroyed remote's PR history; they are left
as a historical record of what was true when written, not a live reference.

This repair sat one commit ahead of `v0.13.0`, unreleased, for the reason a release built at that
tip would have been named `surfaceplate-0.13.0.zip` while not matching the SHA-256 the `v0.13.0`
tag message records — that digest describes the tag's own commit, not a later one. `0.14.0` closes
that gap: it is tagged at the tip that includes this repair, and its own tag message carries the
digest of the archive built from it.

### F5 recorded: three spellings of the organisation identifier, one of them broken

The GitHub organisation is `pipoventures`. `v0.12.0`'s internal rename moved every internal
identifier to the `Ltd`-suffixed, hyphen-separated spelling. The URN authority declared in
`NAMESPACE.md` and used in every schema `$id` is `pipo-ventures`. `INSTALL.md`'s only clone
command names the `v0.12.0` spelling as the GitHub owner, and that owner does not resolve —
`git ls-remote` against it returns "Repository not found", with no rename redirect. Recorded as
[DR-9](org/decisions/DR-9.md), severity medium, with the full occurrence inventory and the exact
reproduced command. **Not fixed here** — the fix touches the URN base, which
[DR-6](org/decisions/DR-6.md) governs, and is deliberately left to separately scoped work.

### A derived-identifier control, extending the DR-6 principle

Three instances of identifier drift have now been found in this repository: the namespace version
segment (F4, `DR-6`), the `SDS`/`SP` finding-code prefix (`DR-8`), and F5 above. `DR-6` already
established the pattern for the first — declare the value once in a document, derive it in the
check, hold no copy of the literal in the check itself. This release extends that pattern to the
organisation identifier.

`ORGANISATION.md` is added as the declared source of truth, alongside `NAMESPACE.md`, stating the
GitHub organisation slug, the URN authority, and the registered legal name, plus which stray tokens
are known not to be the organisation (the maintainer's surname, the personal email domain).

`tests/check_identifiers.py` is added, deriving its expectations from `ORGANISATION.md` exactly as
`tests/validate_contracts.py` derives the namespace from `NAMESPACE.md`. It is a standalone script,
run as a fourth CI step, and is **deliberately not** wired into `validate_contracts.py` or into
`scripts/build_release.py`'s build gate: either would make a release un-buildable and its own
manifest un-regenerable for as long as F5 stands, recreating the exact defect the citation repair
above exists to close. It is seen to fail against this tree (`IDENTIFIER_CONFORMANCE=FAIL`,
raw output in `DR-9`) and seen to pass against a synthetic tree in which the identifiers agree
(`IDENTIFIER_CONFORMANCE=PASS`, same evidence).

## 0.15.0 - self-conformance, and corrections to the instruments that measure it

### What changes for a repository already running 0.14.0

Read this before upgrading. Two new findings will appear against a profile that passed yesterday,
and **both are graceable** — they warn inside the grace window rather than failing:

- **`SP046`** — `baseline_controls.secret_hygiene` now has to name a scanner and where it is wired.
  Every existing profile names none, because the field did not exist. Add the `scanner` block; the
  worked examples under `examples/` show the shape.
- **`SP049`** — **`adoption.framework_digest` has changed meaning.** It was the release archive's
  SHA-256; it is now `sha256(MANIFEST.sha256)`, recorded for you in `.standards/INSTALL.json` when
  you install. An existing value will not match. Copy the new one from the install record after
  upgrading. The reason for the change is that the archive embeds file mtimes, so nobody —
  including the maintainer — could recompute a digest they had recorded (`DR-14`).

Nothing else in the schema changed incompatibly: `scanner` is optional in the schema on purpose,
because a required property would have been an un-graceable failure for every adopter on day one.

`SP048` also arrives, and fires only if your profile names a `framework_version` you did not
install from.

### The rest of this release

### `SP032`'s placeholder detection is token-based, not shape-based

`PLACEHOLDER_PATTERN` in `scripts/check_conformance.py` no longer matches
`<[a-z0-9_\- ]{1,30}>`. Detection is now by token only — the four tokens are named in
`core/PREREQUISITE_GATES.md`, which is their single source of truth and is deliberately the only
document here that spells them out. See the note on `F16` below for why.

The removed branch could not do what it was written for. An unfilled slot and a metavariable are
the same string shape, so nothing lexical separates them. Measured against this repository it
produced **seven matches across six files and not one was a placeholder** — two numbering
conventions, a command template inside `core/PREREQUISITE_GATES.md` itself, a CLI usage line, and a
historical URN form. Three of the six were normative documents this framework publishes, so the
same spurious failure reached any adopter whose governed artefact contained a usage line, on a gate
that is a floor at `standard`. Recorded as `F14`, decided in [DR-17](org/decisions/DR-17.md).

Nothing detectable was lost: the only shipped template carrying an angle-bracket slot also carries
a token marker, and no test depended on the branch.

**This narrows coverage, and the narrowing is documented rather than implied.** An artefact marking
its blanks by any other convention is not detected. `core/PREREQUISITE_GATES.md` now states that
limit plainly instead of describing detection an adopter would wrongly rely on.

### Two shipped templates were not detectable as templates

Establishing what the removed branch was worth required enumerating what the framework's own
templates contain, and that exposed a false negative the branch had been masking the absence of.
`templates/decision-record.md` and `templates/work-packet.md` marked their blanks with a key and an
empty value, matching no branch at all. A gate naming either as its precondition artefact would have
passed `SP032` while pointing at a blank form. Both now carry a visible token marker.
Recorded as `F15`, closed for shipped templates and open in general.

Fixed in the templates rather than in the checker: detecting empty-value-after-colon would be a
second shape-based heuristic of exactly the kind being removed.

### A living record cannot quote the tokens it describes

Found by this changelog entry failing the check it documents. Token detection reads whole file
text, so it cannot distinguish a document that **mentions** a placeholder token from one that
**contains** an unfilled slot. Writing the four tokens into this entry made `CHANGELOG.md` — a
precondition artefact for two gates — fail `SP032`.

This is the same shape as `F14`, narrowed rather than eliminated: four fixed tokens instead of any
angle-bracketed string, but the same inability to separate mention from use. It is recorded as
`F16` and is **not** fixed, because no token vocabulary avoids it. The convention adopted here is
that `core/PREREQUISITE_GATES.md` is the one document that spells the tokens out, and everything
else refers to it. That is a working convention, not a control: nothing enforces it, and an
adopter whose changelog legitimately records *"removed a stale marker from the parser"* will hit
the same false failure.

### Guards, both seen to fail

`tests/validate_contracts.py` now asserts that every file under `templates/` is detectable as a
template, and that the pattern does **not** match three notation strings taken from this
repository's own documents. It imports the pattern from the checker rather than restating it, per
`DR-6`. `tests/test_install_and_check.py` pins both directions of `SP032` end to end.

Asserting that a test passes is not evidence it can fail. Each guard was made to fail before being
trusted: reinstating the removed branch fails the notation assertions; stripping the marker from
`templates/work-packet.md` fails the detectability assertion. Suite counts move 82 → 90 and
97 → 101, accounted for by five templates, three notation strings and four new `SP032` cases.

### Surfaceplate now declares conformance against the standard it publishes

`DR-13` item 0. `governance/application-profile.yaml` (level `standard`, all nineteen catalogue
gates declared with reasons), `governance/authority-map.yaml` and `activity/register.md` are added,
and `.standards/` is installed by the installer — not hand-authored, because `INSTALL.json` is the
artefact whose trustworthiness `F6` and `F7` concern.

`scripts/build_release.py` excludes the installed set from the release payload, derived from
`install_standard.build_payload` rather than restated, per [DR-16](org/decisions/DR-16.md).

The self-check workflow now carries `if: ${{ !cancelled() }}` on every check step and a final step
that confirms each one produced a result. This is the remedy for `F13`: `tests/check_identifiers.py`
had never executed in CI since being added, because an earlier step failed and its conclusion was
recorded as `skipped`, which nothing distinguished from `passed`. It is deliberately not
`continue-on-error`, which would mark a failure as tolerated. The workflow also runs the **source**
checker against this repository, mitigating `F12`: the hook and the installed workflow both resolve
the vendored copy by path, so without this nothing exercises the checker actually under development.

### `secret_hygiene` gains verification (release plan item 4)

`core/CONFORMANCE_LEVELS.md` has required `secret_hygiene` at every conformance level since it was
written, and nothing verified it. The gap was wider than that one control: the checker never
referenced `baseline_controls` at all, so **none** of the three baseline controls was verified —
they were schema-shaped declarations and nothing more.

`baseline_controls.secret_hygiene` now carries a `scanner` block naming the tool and the file(s)
that run it. Two codes check it, both graceable:

- **`SP046`** — no scanner named, or wiring that is absent, never mentions the scanner, or is a
  workflow in which no step invokes it.
- **`SP047`** — the invoking step cannot fail the job.

`SP047` exists because of an observed failure, not a hypothesis. A run in a sibling repository
printed both `leaks found: 4` and a summary line reporting no findings, because the summary step
discarded a non-zero status; eleven consecutive "clean" runs meant nothing. A control that merely
confirmed a scan step existed would have passed that workflow — it would measure the presence of a
control rather than its effect.

**What a pass means, stated narrowly because the temptation is to read it wider:** a scanner is
named and wired somewhere that can fail. It is **not** a statement that the repository contains no
secrets. This standard ships no scanner, recommends none, and reads no file looking for
credentials. `core/CONFORMANCE_LEVELS.md` now also says plainly that `agent_work_packets` and
`actual_diff_review` remain unverified, so a reader who learns one baseline control is checked does
not infer the others are.

`scanner` is optional in the schema and required by the checker. That asymmetry is deliberate: a
schema violation cannot be graced, so making it a required property would hard-fail every existing
profile the day it shipped. A new obligation has to arrive through the grace mechanism or it is one
nobody can adopt.

Both worked examples under `examples/` are updated to show the shape. Decided in
[DR-18](org/decisions/DR-18.md); registered as `ACT-005`.

### Surfaceplate satisfies its own new control

`.github/workflows/secret-scan.yml` is added: blocking, scoped to the pushed range with a
full-history fallback wherever the range cannot be determined. It deliberately does **not** share
the portfolio's tuned scanner configuration, which lives in a private repository behind a secret —
a framework whose own security workflow cannot run in a stranger's checkout demonstrates the wrong
thing. The cost is recorded rather than glossed: this repository does not inherit those tuned rules.

The scheduled full-history sweep the sibling repositories carry is not copied here. The reason
first recorded — that no `schedule` event had ever been observed to fire — was falsified within
hours and is corrected in `DR-18` rather than left standing. Measured on Monday 2026-08-31 at
12:19 UTC, with five due runs at `0 6 * * 1`: one fired six hours late, four were overdue. The
decision stands on the measurement, not the original claim — a trigger that fires for one in five
due runs cannot bound a detection interval, so adopting it would buy the appearance of a weekly
sweep rather than a weekly sweep.

### Guards, both directions, both seen to fail

`tests/test_install_and_check.py` pins five failure modes and one pass. Removing the control from
the checker fails all five positives; sabotaging it to fire unconditionally fails the negative.
Without that last one, five passing assertions would be consistent with a control that fires on
everything. Suite counts move 101 → 107; `validate_contracts.py` is unchanged at 90.

### The identifier check learns that other organisations exist (`F17`)

Adding the first third-party GitHub URL to a payload file exposed a false positive in
`tests/check_identifiers.py`: rule 1 asserts every `github.com/<owner>/` matches the declared
`github-org`, so fetching the scanner from `github.com/gitleaks/gitleaks` read as organisation
drift. The rule is right for a URL meant to point here and wrong for one that is not.

`ORGANISATION.md` gains a fifth ```text block naming other people's organisations, and the check
derives the exemption from it rather than holding a list — the `DR-6` principle again. Rule 1 still
asks its question of every owner not declared, and the parser refuses to start if the block is
missing, so the exemption cannot be lost silently.

Third-party entries are deliberately **not** paired to a path, where quoted-evidence entries are.
A quoted drift is a wrong spelling of *this* organisation that one record has reason to reproduce,
so scoping it keeps that spelling caught elsewhere; a third party is legitimately referenced
anywhere. Both directions seen to fail. Suite moves 78 → 82.

### The contributor framework is decided: DCO, no CLA (release plan item 6)

[DR-19](org/decisions/DR-19.md) records what the sign-off work was already commissioned under —
*sign-off only, no signature-collection service* — and closes item 6, whose original wording still
called for a contributor licence agreement. The contradiction is resolved in favour of the later,
explicit instruction, and the release plan is edited rather than left disagreeing with the record.

The trade is stated rather than glossed. Apache-2.0 §5 already places contributions under the
licence's terms, carrying the §3 patent grant, so the usual CLA justifications are substantially
covered. What is **not** covered is relicensing: under DCO alone, moving away from Apache-2.0 needs
every contributor's agreement. Today that is one person and costs nothing; the cost grows with each
external contributor and cannot be fixed retroactively, because a CLA adopted later binds only
those who sign it afterwards.

Recorded as untested: the DCO check has only ever seen commits by the maintainer, who also wrote
the check. That is not evidence it behaves correctly for a stranger.

### A falsified premise, corrected where it was stated

`DR-18` justified omitting a scheduled history sweep on the grounds that no `schedule` event had
ever been observed to fire in this account. **That was true when written and false within hours.**
Measured on Monday 2026-08-31 at 12:19 UTC, with five workflows across four repositories all
carrying `0 6 * * 1` and therefore all due at 06:00: one fired, six hours late; four were still
overdue.

The decision stands, on a different footing. Schedules are unreliable, not disabled — and a trigger
firing for roughly one in five due runs cannot bound a detection interval, so a sweep described as
weekly would be an appearance rather than a control. Corrected in `DR-18`, in this changelog, and
in the workflow comment that repeated it, rather than annotated in one place and left standing in
the other two.

### The vendored set is kept, governed, and its drift detected (`ACT-002`, `ACT-003`)

[DR-20](org/decisions/DR-20.md) settles what an adopting repository receives.

**`ACT-002`'s framing had to be corrected before it could be answered.** It asked whether the
vendored set should shrink "to what is mechanically read" — but `check_integrity` digests every
file in the install record, so all 27 are mechanically read. Only **four** have their content
interpreted. Shrinking would not have removed unused files; it would have removed 23 files from
integrity protection, which is a different act with a different cost.

The set is kept, on evidence rather than preference. `core/PREREQUISITE_GATES.md` has seven
revisions, one of them normative — at 0.10.0 the interface gates became a conditional floor — so an
adopter pinned at an older version who reads the published documentation instead of their vendored
copy gets a rule they never adopted. Version-scoped conformance is not meaningful without the rules
for that version being retrievable, tamper-detected and readable offline. The footprint argument
does not survive measurement: 264K.

**The real cost of keeping is the review surface, and that is what changed.** A 27-file upgrade
diff, mostly prose, trains a reviewer to wave installer diffs through — and the same diff carries
the checker. The installer now reports what changed by review class (*enforcing* / *contract* /
*reference*) and says so explicitly when nothing that executes or validates changed. The
classification is derived from the checker's own path constants rather than restated.

Membership now follows a stated principle, so a future addition is a decision rather than an edit
to `build_payload`. Whether the payload should move into package data is recorded as an **input to
release plan item 1**, not left as an open activity.

### `F12` is closed: drift between the two checker copies is now detected

`tests/check_vendored_current.py` compares every payload path's source against its installed copy
and runs as its own CI step. The previous mitigation — CI running the source copy — is kept, but
ensuring one route is current is not detection, and this finding was about the absence of detection.

Neither existing control covers it, and each looks as though it might. The integrity check digests
the vendored files against a record written by the same install, so editing source afterwards
leaves it matching perfectly; it answers *has this been tampered with*, never *is this current*.
`--verify-manifest` is the near miss: editing source does make the manifest stale, but regenerating
it records two digests for two files and passes, so it detects *manifest stale* and **masks** the
divergence.

Not written speculatively — the condition occurred twice while implementing `DR-18`, presenting as
a confusing `SP016` that took a reinstall to explain. Seen to fail three ways, including a deleted
install record, which reports that self-conformance is gone rather than that there is nothing to
compare.

A guard written for the classification was removed before landing, and the reason is recorded in
`DR-20` rather than quietly dropped. It asserted that the installer's `contract` class equalled the
checker's constants — which cannot fail, because the class derives from those constants and both
sides move together. It was verified to pass under exactly the mutation it claimed to catch. What
replaced it is falsifiable and covers a bug the derivation does not prevent: every schema the
checker parses must actually be shipped, or an adopter installs a checker that cannot find its own
schema.

### `F5` closed, and `F11` closed by a check that the registers match reality

`F5` was the organisation-identifier drift: three spellings, one of which resolved to nothing.
**The live instruction was corrected some releases ago** — `INSTALL.md:29` reads the declared
`github-org`, `git ls-remote` against it resolves, and the old spelling still returns a hard 404.
Every remaining occurrence is a quotation inside a record, and `tests/check_identifiers.py`
verifies that on every run.

What was never a defect is stated so it is not re-raised: the three declared identifiers still
differ from one another, because a GitHub slug, a URN authority segment and a registered legal name
are three namespaces with different grammars naming one organisation.

**`F11` is closed by `tests/check_code_registers.py`**, and the reason it needed a check rather than
more care is that care demonstrably did not work. On 2026-08-31 `org/FINDINGS.md` was carrying
**four false statements at once**, each written by someone reading the file:

- `F5`'s own entry said `INSTALL.md:29` "still reads" the broken URL. It had been corrected.
- The code table said the checker emits `SP001`–`SP043`. `SP046` and `SP047` existed, added by the
  same session that was editing the file.
- The `ACT-<n>` row said there was "no register behind it". `activity/register.md` existed.
- The header said "this repository still carries no application profile". It had one, and CI was
  checking it.

None is a typo. Each was true when written and became false when something else changed — the class
of error a careful reader cannot catch, because nothing about a stale sentence looks different from
a current one. All four are corrected.

The `SP` code space is now **declared** in a parseable block in `org/FINDINGS.md` and compared
against the codes `check_conformance.py` actually constructs — emitted, deliberate gap, and
reserved-but-unemitted, with no undeclared hole permitted. That last assertion is the one that
would have caught `DR-8`'s original defect, where `SDS036` sat documented-but-unimplemented across
releases with nothing noticing. The `F` table is checked against its own body sections. Seen to fail
on all five `SP` assertions, including a reproduction of the real error.

Stated plainly, because three of the four false statements above would have survived it: this check
compares declarations against reality. It cannot judge whether a finding's prose is still accurate,
and does not claim to.

### `F7` closed: the declared pin is now checked against what is installed

`DR-14` had stood as decided-not-implemented. It is implemented, and `adoption.framework_digest`
stops being a field that only looks verified.

`scripts/install_standard.py` records `sha256(MANIFEST.sha256)` in `.standards/INSTALL.json`, and
the checker compares the profile against it:

- **`SP048`** — the declared `framework_version` is not the version installed.
- **`SP049`** — the declared digest disagrees with the record, **or the record carries no anchor to
  compare against**. That second case matters: "nothing to compare" and "the values match" must not
  summarise the same way, and before this the field was skipped in silence.

Both graceable, because `DR-14` *changes what the field means*. Every profile written under the
previous definition carries an archive digest and would fail on the day this shipped; an obligation
arriving without grace is one nobody can adopt.

**Why the manifest rather than the archive.** The zip embeds file mtimes, so nobody — including the
maintainer — can recompute the digest of an archive they did not keep. `MANIFEST.sha256` is a pure
function of tree content, so a third party holding the published tree can recompute the anchor on a
machine that is not the adopter's. That was the question `DR-10` set and could not answer.

**A gap in `DR-14` found by implementing it, recorded rather than papered over.** `MANIFEST.sha256`
is not part of the install payload, so an adopter cannot recompute the anchor from their own
repository — only compare against what the installer wrote for them. Independent recomputation needs
the published tree. `DR-14` claimed external verifiability as though the adopter's own checkout would
suffice; it does not. Installing the manifest would fix it and is left as an open question against
`DR-20`'s payload principle rather than smuggled in alongside an implementation.

**What is still not closed.** Both compared values live inside the repository being checked, so this
establishes that the profile agrees with the install record, not that either is true. That is `F6`,
which stays open. `DR-14` said so before this work and it is still true after it.

### `F10` closed: the producer evidence record is retired, not regenerated

`audit/VALIDATION_RESULTS.md` claimed to record checks *"for the current release"*. It described
`0.7.0` while `0.14.0` shipped, counted 5 schemas where there are 6, told a reader to verify an
archive that does not exist, and — the reason it ranked first among open findings — reported **PASS
for a version-consistency rule `DR-6` deliberately abolished**. That is not staleness; it is a
passing result for a check that no longer exists. It also reported a secret-pattern scan as passing
in a repository that had no automated secret scanner until `DR-18`.

[DR-21](org/decisions/DR-21.md) retires it. The argument is a measurement, not a preference:
`CHANGELOG.md:75` records fixing the identical defect at 0.6.0 **by regenerating this same file**,
and seven releases later it was stale again. A hand-written evidence document depends on a human
updating it every release, and nothing fails when they do not — an artefact whose accuracy rests on
discipline, in a repository whose thesis is that discipline is not a control.

Its function is now served by five suites that run on every push and pull request, each reporting
the count of checks it executed, with a step confirming each produced a result. Re-runnable, dated
by the commit, and unable to go stale without going red.

The file is **kept**, marked historical, with each stale or abolished row annotated **inline** — not
only under a banner, because a grep for `Version consistency` lands on the row rather than the
header, and a correction that depends on reading order is not a correction. Kept rather than deleted
because its "Checks NOT performed" and "Outstanding" sections remain true and `F6`/`F8` cite the
latter by line.

`audit/AUDIT_README.md` pointed auditors at that file as *"the producer's current check record"* and
told them to attach `engineering-control-kit.zip` — the pre-`0.12.0` product name, for an archive
not produced under that name since the rename. Both corrected; it now names the suites and the
per-step CI run.

### `F9` closed: remediation text names a version, and upgrades announce themselves

`SP004` and `SP005` said *"re-run the installer"* with nothing scoping which one. That advice was
correct only because the operator's checkout happens to be a fixed artefact: `repo_root()` resolves
the source to wherever the running script sits, `build_payload` re-hashes from there every run, and
the run **rewrites** the record rather than restoring toward the previous one.

Both halves are fixed. The remediation text now names the recorded `standard_version` and says why
it matters. `install_standard.py` now reports when its source `VERSION` differs from the recorded
one — *this is an upgrade, not a restore* — and tells an operator who arrived from an integrity
failure to stop and run the recorded version instead.

Reported, deliberately **not** refused: upgrading is the ordinary path, and blocking it would trade
one defect for a worse one. What was missing was never that upgrading is wrong, only that it was
indistinguishable from repairing. Seen to fail: silent on a fresh install and on a same-version
re-run, firing with both versions named when they differ.

### `F8`'s documentation half is discharged; the finding stays open

`F8` recorded that `README.md` overstated the history audit, and left it *"per this packet's 'record,
do not fix'"*. That packet closed weeks ago; an expired instruction is not a reason to leave a false
claim on the adopter-facing surface.

Three passages corrected. The history audit is scoped to **prerequisite gates only** — it asks
whether a gate's precondition artefacts existed in each commit that touched its paths, and has no
relationship to the file digests in `INSTALL.json`. **There is no history-based integrity audit.** A
modified standard-owned file is detected when the checker runs and by nothing else; in a clone where
the hook was never activated, that may be nobody.

The finding stays open. Correcting the description of a control is not fixing the control, and
`DR-15`'s remedy cannot be demonstrated while rulesets return HTTP 403 on this plan.

## 0.16.0 - publication, and the last of the closable findings

### What changes for a repository already running 0.15.0

Nothing breaks. One optional field is added; no existing profile becomes invalid, and no new
finding fires against a profile that passed yesterday.

### `F16` closed: an artefact may declare itself exempt from the placeholder scan

Placeholder detection reads whole file text, so it cannot tell a document that *mentions* a token
from one that *contains* an unfilled slot. A changelog documenting the control failed the control.

[DR-22](org/decisions/DR-22.md) adds `placeholder_scan_exemptions` to the profile. Three properties
make it an exemption rather than a hole, and each is tested:

- **narrow** — it suppresses the token branch of `SP032` and nothing else; an exempt artefact must
  still exist and still be non-empty, and both remain checked;
- **declared in the profile, never inside the artefact** — a template able to exempt itself would be
  exactly the condition `SP032` exists to catch;
- **announced** — every exemption is reported as an advisory on every run, so a control that has
  been narrowed says it was narrowed.

`SP050` fires on an exemption naming an artefact that does not exist, because a stale exemption
outlives the thing it was written for.

**The underlying defect is not solved and the closure does not claim it is.** What changed is who
decides. An adopter can exempt an artefact that really is unfinished, and nothing prevents that.

This repository uses the mechanism on itself — its changelog documents the control and therefore
contains the tokens. The previous workaround was to avoid naming them, which was worse: a changelog
that cannot describe a control is a poorer artefact than one that needs an exemption.

### `F13` and `F15` closed by shipping obligations the standard had kept to itself

Both were fixed for surfaceplate months ahead of being stated for anyone else.

`core/REVIEW_AND_EVIDENCE.md` now states, for every adopting repository, that **a check that did not
run is not a check that passed** — a pipeline must not silently skip its checks, something must
confirm each produced a result, and a green run is evidence only for the steps that executed, so
cite the step rather than the job. It also says plainly that this framework cannot check any of it
for you: it inspects a declared profile and a git history, not the semantics of your pipelines.

`core/PREREQUISITE_GATES.md` now requires an adopter to mark their own templates. Detection is not
available — the only general way to recognise a blank form by shape was removed under `DR-17` after
seven false positives and no true ones — so the framework asks rather than guesses, and explains why.

### Publication

[DR-23](org/decisions/DR-23.md) decides to publish surfaceplate as a **new public repository with no
prior git history**, keeping the existing one private, archived and intact.

The reason is `F8`: the conformance check lives in a workflow file inside the repository it checks,
so deleting the file removes the check. The remedy is a branch ruleset, held in the forge's settings
rather than in the repository — and rulesets are unavailable on this repository's plan, verified
live at both endpoints.

Rewriting history to scrub the former namespace was chosen first and then rejected on preparation.
It would have destroyed the verifiability of four releases whose digests cannot be recomputed by
design, invalidated the SHA citations a second time, and still produced a visibly-redacted and
suggestive history — the full cost without the goal. `DR-23` records all of it.

**`F8` is not closed by that decision.** It closes when the ruleset exists and is shown to block a
merge that fails a check. Deciding to enable a control is not the control.

### `F6` — what would actually close it, recorded

`F6` stays open, and the entry now says what closure requires rather than leaving "structural" as a
plan. Two things that look like remedies are not: **signing** proves a tag came from a key held by
the same person with commit access, and a **ruleset** stops the check being deleted without giving
it an external anchor. Closure needs a party other than this repository to hold the value — release
plan items 9 and 10.

### Sanitisation

The worked examples were written in professional-services language — pricing engines, blended rates,
engagements, client proposals. They are now a generic forecast service. One changelog line naming a
corporate email domain is described rather than reproduced. `workflow_dispatch` is added to the
secret-scan workflow so a full-history sweep can be run on demand; this repository ships no
scheduled sweep, so previously there was no way to scan history at all.

## Unreleased

### Every reachable decision of `adopt`, run and recorded (`ACT-057`, `DR-58`, `DR-59`)

Before launch the maintainer asked for every combination of the wizard's parameters and choices to
be run against a real repository and the output checked, and for the testing to be documented so a
complaint can be answered by pointing at it. `DR-58` fixes what "every combination" means - every
level × interface answer × repository shape in full; every free gate in every status, in bulk and
cycled; every artefact field found, seeded and typed; every above-floor control on and off; every
route (interactive, `--propose` then `--answers`, resume after every stage, `--edit` per leaf class,
cancel at every point, every refusal); the screens driven headlessly at every configuration - and the
form of the record: a generated report under `audit/validation/` compared byte for byte in CI, and an
assurance-evidence record under `governance/assurance/` whose outcome is the maintainer's.
`tests/test_adopt_matrix.py` is the fourteenth suite and the sixteenth CI step: 208 cases, 45,257
checks, judged by a property oracle (the profile, the sidecar, the files created, the real checker)
rather than a second profile builder. It found four defects, fixed test-first: an `essential` adopter
could tick `documentation_authority` and write a profile the checker faults with `SP052` (`F97`,
withheld under `DR-59`); a run cancelled after the scaffold stage and resumed never created the
adoption decision record it named (`F98`); `--propose` demanded rationales for controls nobody
declared (`F99`); `--edit` applied no field validator (`F100`).

### The adversarial product review of 2 September, and `adopt` rebuilt for a first-time reader (`ACT-042` to `ACT-048`)

A cross-provider adversarial review of the product (`audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`)
recorded nineteen findings (`F59` to `F77`) and four decisions (`DR-47` to `DR-50`), and four phases
remediated them: the eight defects that made the wizard unfinishable or destructive (`ACT-043`);
proposal-first adoption with a provenance record beside the profile, one gate list, validator parity
with the checker, and discovery that excludes the framework's own files (`ACT-044`); non-interactive
adoption with `--propose` and `--answers`, `doctor`, JSON and SARIF output, an exit-code contract,
and a clean-machine front-door job (`ACT-045`); an 80×24 snapshot suite as golden files, register
parity, the `risk` block in the schema, and the draft moved under `.standards/` (`ACT-046`).

The maintainer's first run of the rebuilt wizard against a real repository then found eight more
(`F78` to `F85`), recorded under `ACT-047` and answered by `DR-51` and `ACT-048`:

- `adopt` refuses before the first question when the installed copy of the standard is not this
  tool's release, naming both and the upgrade command; `doctor` reports the same comparison.
- An opening screen: the tool's name, version, licence and publisher; the installed version and
  digest; what will be written and where; that nothing is written before the review; the keys.
- Every field carries what is asked, what the answer decides and what a wrong answer costs, beside
  the focused field, and a test fails on any that lacks them.
- Every file picked from the repository is described when chosen: what discovery saw in it,
  whether it matched the gate, whether the checker would reject it, which step runs the scanner.
- The wizard proposes nothing the checker rejects: scanner workflows only where a step runs the
  scanner (`SP046`); no empty or placeholder-bearing artefact (`SP032`); `authority_map` no longer
  matches on the word "inventory".
- A refusal on the review names the profile line and the keys; the closing report states the
  checker's verdict as the checker gave it, rather than "passes" on a graced WARN.

`ACT-049` then closed what an agent could close before 1.0: the level options fit 24 rows, an
unpressed control's brackets are visible and focus no longer reads as chosen, a text area shows
three rows, the above-floor rows explain themselves when highlighted (`F67`); Ctrl+Q reaches each
screen's own cancel (`F73`); the profile is written atomically and a draft with stale ids starts a
fresh run rather than a crash (`F77`). `DR-52` records that release-plan item 5 is met with one
adopter, Plutos, and that Plyego is deliberately left alone.

`ACT-051` gave the opening screen its mark: a surface plate in isometric with the `SP` monogram
on its top face, generated from its geometry, chosen by the maintainer on rendered previews
(`F89`, `DR-53`); and fixed a render test that read the screen before a deferred scroll had run
and turned `main` red on the runner (`F90`).

`ACT-052` (`DR-54`): a field whose artefact has a seed opens with "create it" instead of a hidden
blank; every tracked document is offered with the matches first, and the findings register gains a
seed; `adopt --edit <path> <value> --because <reason>` changes one line after the write and records
it beside the profile (`F86`, `F87`, `F88`).

`ACT-053` (`DR-55`): the "create it" row wherever a seed can be honest - seven more gates (an options
log, the risk classification with the standard's scale and this repository's meanings left to declare,
the test conventions, a data-source register, an output-validation log, a dependency-review log, the
release checklist) and the four record-directory controls, whose seed is a note in an otherwise empty
directory. A `full` run choosing every row ends with the checker passing in full.

`ACT-054`: from the maintainer's third run - a record directory is proposed only where its name and its
records fit the control, an archived document is never proposed, a seeded directory stays offered, and
`SP034`'s message prints each date as declared (`F92` message, `F93`, `F94`). Recorded for a decision:
the conformance level barely changes the screens that follow (`F91`), and whether a same-day instant is
a forward move (`F92`).

`ACT-055` (`DR-56`): the gate list opens with the level's floor expanded and every other gate folded
under one counted heading, so `standard` shows four gates and `full` eleven before anything is opened;
the counter and the above-floor list name the floor (`F91`).

`ACT-056` (`DR-57`): continuing past the folded gates asks once - declare them all not applicable as
one recorded act, or open them - instead of refusing by naming a gate the reader could not see (`F96`).

### `F58` closed: every agent now receives the skills, not only Copilot

`AGENTS.md` tells every adopting repository that the skills' *"required inputs, gates and mandatory
stops are not optional"*. It named `.github/skills/`, and that was the only place they installed.
Claude Code loads `.claude/skills/`, which no adopter ever received — including this repository,
where `ls .claude/` returned `rules` and nothing else.

This is `F29` a second time. `DR-30` answered *"instructions sitting where no agent loads them"*
with one body and several emitters, applied it to the six instruction documents, and stopped. The
seven skills kept a single emitter for four months and nothing caught it, because every test asked
whether the skills installed correctly rather than whether the agent reading `AGENTS.md` could
reach them.

`build_payload` now emits each `SKILL.md` to both paths. Unlike the instructions there is no
transformation to make — a `SKILL.md` already carries the `name` and `description` front matter both
agents want — so the body remains one file and gains a destination. The conformance block's prose
named one directory and now names the pattern, matching how it already described the
instructions.

**It also narrowed a human decision it was not looking for.** Forge neutrality had been measured as
*"`.github/skills/` and the conformance workflow, 8 of 57 installed files"*. Seven of those eight
were never a forge question. What is left is **one file of 64** — the conformance workflow, which
genuinely assumes GitHub Actions.

### `F8` closed: the check can no longer be deleted to make it stop

Surfaceplate is published at `github.com/pipoventures/surfaceplate`, and a branch ruleset named
`main-required-checks` requires a pull request and all four status checks on the default branch,
with **no bypass actors** — so it binds the maintainer too.

The finding was that the conformance check lives in a workflow file inside the repository it
checks, so deleting the file removes the check. It now cannot: the requirement is held in the
forge's settings, and deleting the workflow makes the merge impossible rather than making the check
disappear.

**Demonstrated, not merely configured** — the distinction this register has insisted on since
`F13`:

- a direct push to `main` was refused: *"Changes must be made through a pull request"*;
- a pull request with a deliberately corrupted manifest digest failed `Contract and installer
  tests`, and the merge was refused: *"the base branch policy prohibits the merge"*.

Zero required approvals is deliberate: a single maintainer cannot approve their own pull request,
so requiring one would lock the repository rather than protect it. The control is the checks.

**Unverified and recorded as such:** whether an explicit administrator override is refused. GitHub
documents rulesets as binding admins when the bypass list is empty, and the ordinary merge path was
refused for the owner — but the override flag was not exercised, because testing it would have
meant merging a knowingly broken tree to a public branch.

**It protects this repository and requires nothing of any adopter**, who must apply their own. And
it does nothing for `F6`: stopping the check being deleted is not the same as giving it an anchor
outside the repository.

`README.md` is corrected in three places that said no ruleset had ever been applied.

### `F18`: inherited product and methodology names removed from the public tree

The tree carried internal product and methodology names from the private repository this framework
grew out of — in both adapters, `SETUP_GUIDE.md` (which was **titled** with the pre-`0.12.0`
product name), four documents under `audit/`, this changelog, `RECONCILIATION.md` and `DR-7`. The
adoption wizard prompt still called the product by its old name in live text.

Not a brand-policy matter — these are product and methodology names, not an organisation. It is a
comprehensibility defect, and it was invisible for as long as the only readers were people who knew
what the names meant. It landed hardest where an evaluating reader looks first: `adapters/r.md` is
three lines and spent a third of its length warning against copying a product the reader has never
heard of.

Every inherited name is replaced with a generic description. Live guidance was rewritten outright;
historical records under `audit/` were redacted **with the redaction disclosed** in a note at the
top of each — the substance of what was checked and found is unchanged, only the proper nouns are.

**What deliberately remains:** `Shiny` in `adapters/r.md`, which is a public R framework named the
way `pytest` would be; and this product's own pre-rename name where it records the rename, because
removing that would erase the record of the rename itself. The line: someone else's names go, and
this product's own former name stays where it records history and goes from live guidance.

**Not fixed:** the adapters are still 3 and 5 lines, which is thin for the audience they serve; and
nothing prevents recurrence, since `check_identifiers.py` guards the organisation identifier rather
than inherited product names.

### `F19`: the dual licence is implemented, not just decided

A Class C decision recorded in another repository on 2026-08-30 licensed surfaceplate **by artefact
type** — Apache-2.0 for software, a separate licence for documents, amended the same day to
CC0-1.0. **None of it had been implemented here.** The root `LICENSE` was correct; `LICENSE-DOCS`
and `NOTICE` did not exist, and `README.md` contained no occurrence of the word "licence". The
repository was made public in that state, so every template and agent skill shipped under a code
licence the decision says should not govern prose.

`LICENSE-DOCS` now carries CC0-1.0, `NOTICE` is present as Apache-2.0 requires, and `README.md` has
a Licensing section naming which paths fall on which side.

**The split, and the one part that surprises:** `core/`, `templates/`, the agent instructions and
skills, and the conformance block are **documents** under CC0-1.0 — copy them and you owe nothing,
no attribution, no licence link, no indication of changes. Everything else is **software** under
Apache-2.0, and that deliberately includes `schemas/` and `adapters/` even though both install
alongside the documents and are written in YAML and Markdown. A schema is a contract a program
parses, not prose a human reads.

**A boundary correction worth recording.** It was first drawn as a path rule — `standard/` plus
`templates/` — which mapping onto the real payload showed to be wrong in both directions: it put
`core/`, the standard's own normative text, under the software licence, and put a shell script and
CI workflows into the public domain. The source decision splits by artefact type, not by directory,
and the two disagree here.

**The CC0 text was fetched, not written from memory** — from creativecommons.org, and diffed
byte-for-byte against the SPDX copy. Identical at 7048 bytes. Legal text is where reproducing from
recall fails silently.

`F19` also records a near miss found by the same check: `DR-23` was written and publication carried
out without ever consulting the repository holding a Class C decision with an explicit publication
precondition. That precondition had in fact been discharged, so nothing was breached — but the
answer came out clean by accident rather than by method.

### `F20`: a pass no longer reads as verification it did not perform

Claiming a conformance level proved nothing about the controls it demanded. **Demonstrated:** this
repository was made to claim `full` and declare `provenance`, `run_lineage`, `method_registry` and
`overrides` in a tree containing none of them, and the checker raised **zero** objections about any
of them. Every finding it produced concerned gates.

`SP021` and `SP022` verify two things about a control — that it is listed, and that it reads
`required`. Nothing asks whether the thing exists. **A gate is checked against the repository; a
control is checked against itself.** That is uniform: `dependency_lock` at `essential` was as
unverified as `provenance` at `full`.

Two changes, and neither is verification:

`core/CONFORMANCE_LEVELS.md` now states the distinction **before** the level tables, where a reader
meets them, rather than in an enforcement section further down.

The checker now reports it in the result itself:

```
level     : full - 8 of 9 required controls are DECLARED, not checked
            assurance_findings, contract_tests, dependency_lock, ...
            A pass does not establish these exist. See F20.
```

The false claim above still passes — nothing was verified — but it can no longer be read as
evidence.

[DR-25](org/decisions/DR-25.md) decides the architecture that changes it: four patterns by which a
control becomes provable, with `implementation_reference` — a field already in the schema and used
by nothing — as the place an adopter says where a control lives. **Three of the four patterns are
existing working code**, reused from `SP032`, `SP046`/`SP047` and the `authority_map` gate. Only the
records validator is new.

**No new schema is needed.** `provenance` appeared to require its own record type; it does not.
`method-run-lineage.schema.yaml` already requires `input_references` and `input_hash`, so
`provenance` and `run_lineage` are two properties of one record — traceability and reproducibility —
and one validator serves both.

**What will still not be provable when all of it is built:** that a record is true. Verification
establishes that a record exists, is well-formed, is current and is linked. It never establishes
that the run happened the way its lineage record says. `DR-25` records that as a boundary, not a gap
to close later.

`VERIFIED_CONTROLS` currently holds one member. Each later packet moves a control into it and the
reporting shrinks by a line, so the output is derived from what is true rather than maintained
beside it.

### Three controls become checked, and `F21`: surfaceplate had no lock

`DR-25` predicted that surfaceplate would have to satisfy its own controls under the new patterns,
and that failing would be evidence against the design rather than grounds for an exemption. It
failed immediately, and before a single validator was written.

**`F21`: `dependency_lock` was declared `required` with nothing pinned anywhere.** No
`requirements.txt`, no `pyproject.toml`. All three workflows ran `pip install pyyaml jsonschema`
unpinned — and `--quiet` suppressed the resolution, so a green run could not say which `jsonschema`
had validated the schemas. Local carried `jsonschema 4.10.3`; CI had been resolving something newer
for months. The two had never matched.

The profile's own rationale read *"the runtime set is two packages, named in every documented install
line and in CI."* **Naming is not locking.** That sentence is what a declared-but-unverified control
looks like from the inside: it sounds like diligence and commits to nothing.

`pyproject.toml` now pins both dependencies to exact versions — resolved in a clean virtual
environment with all five suites run against them **before** pinning, not copied from a developer
machine. The workflows install those versions and no longer pass `--quiet`.

**Three controls move from declared to checked:**

| Control | How |
|---|---|
| `dependency_lock` | `SP051` — the named file exists, is non-empty, is not a template, is tracked by git |
| `assurance_findings` | `SP051`, same way |
| `documentation_authority` | The `authority_map` gate, plus `SP052` requiring that gate whenever the control is required |

`SP052` closes a seam that a level being *a floor, not a ceiling* opens: an adopter could require
`documentation_authority` at `essential`, where the gate is not part of the floor, and be back to a
control verified by nothing.

**The banner is the evidence.** `level : standard` read *3 of 4 required controls are DECLARED, not
checked* before this change and reads *2 of 4* after. The remaining two are `deterministic_tests`
and `contract_tests` — pattern B, packet 3.

**Two things found while building it.** Pattern A applied the placeholder scan without honouring the
declared exemptions that gates honour, so `org/FINDINGS.md` — which documents those very tokens in
`F14`, `F15` and `F16` — failed as "unfinished". One mechanism behaving two ways depending on which
check reached the file. Fixed, and the exemption set is now computed once and shared; computing it
per consumer had duplicated every advisory, which is noise that trains a reader to skim exactly the
output saying a control was narrowed.

**What is still not proven:** that the pinned versions are *good*, only that they are fixed and
recorded. And a version pin is not an artefact pin — there are no hashes, so this guards against an
unexpected new release rather than a compromised re-upload. `pyproject.toml` says so rather than
implying otherwise.

`pyproject.toml` begins item 1's *declaration* half ahead of the adoption gate. Its hard part —
`repo_root()` under a wheel, package data, entry points — is untouched, and `org/RELEASE_PLAN.md`
records the early start so the sequence does not drift silently.

### Pattern B: `standard` becomes the first fully checked level

`deterministic_tests` and `contract_tests` move from declared to checked. Every control the
`standard` level requires is now verified against the repository rather than against its own
declaration, and the banner that reported otherwise no longer prints.

`SP053` verifies that a control's `implementation_reference` names a CI step which exists, runs
something, and **can fail** — reusing the mechanism `SP046`/`SP047` already use for the secret
scanner. That bypass half is the point: a suite can run, report success and leave the job green if
its exit code is discarded, which is an observed failure in this project's history rather than a
hypothesis.

**`DR-25` is amended in place, not footnoted.** It predicted the reference would be a *status-check
name*; implementation showed step granularity is correct. A status check is a job, one job here runs
every suite, so both controls would have named it and received an identical check — losing the
distinction between them. Whether a job is a *required* check also lives in forge settings rather
than the repository, and reading it would make the checker forge-aware, which `DR-12` forbids.
`DR-25` states that a pattern which does not fit means the record is wrong, so it was corrected
rather than worked around.

**What this does not prove**, stated in `core/CONFORMANCE_LEVELS.md` beside the control: that the
tests are deterministic, that they are contract tests, or that they assert anything. **A step
running `true` would pass.** Same boundary as the scanner check — wired, never effective.

Seen to fail four ways — no reference, a step that does not exist, a step that runs nothing, and a
step neutralised by `continue-on-error` and separately by a swallowed exit code — and to pass once,
without which the four failures would be consistent with a check that fires on everything.

`F20` now reads 5 of 9 controls checked. The four that remain are `provenance`, `run_lineage`,
`method_registry` and `overrides` — pattern C, the only genuinely new mechanism, and the next packet.

### `F22`: a deferral now expires on the date its author gave it

`SP031` has always refused a deferred control or gate carrying no `revisit_by`, on the stated
grounds that *"a deferral with no owner and no date is an omission wearing a decision's clothes."*
Nothing then ever read the date:

```
revisit_by: "2020-01-01"   ->   PASS - all conformance checks satisfied.
```

Six years expired. The control that exists to prevent a permanent exclusion was creating one.

`SP054` reads it. A passed date is a finding; a date within 30 days is an advisory, mirroring how
`adoption.review_by` has always been treated; a malformed date fails, because a deadline nobody can
parse is not a deadline.

**Why this is recording rather than judging:** the date was declared by the adopter. Comparing it
against today establishes whether a stated commitment has come due — it decides nothing for them.
That is the same line that keeps per-change risk classification deferred.

**Gate exceptions are deliberately out of scope, and the reason is the sharper half of the
finding.** `schemas/gate-exception.schema.yaml` carries `raised_on` — optional, and a *creation*
date rather than a deadline. So an exception is permanent by construction and no checking fixes it,
because there is nothing declared to check against. Deferrals were unenforced; exceptions are
**unenforceable**. The first was a gap in the checker, the second is a gap in the contract, and
closing it means changing a published schema — a decision, not an implementation detail.

Also recorded: this item was kept unconditionally by the scope review and ordered *before* the first
record validator. Patterns D, A and B were a larger substitution for `G′` than that review
anticipated, and this was overlooked — an agreed sequence departed from without anyone deciding to.

`SP051` to `SP054` are now listed in `core/PREREQUISITE_GATES.md`'s code table, which had not been
updated since `SP047`.

### `F20` closed: every control is now checked

`DR-25`'s last pattern is built. `overrides`, `method_registry`, `run_lineage` and `provenance`
name a **register** — a directory — in `implementation_reference`. `SP055` requires it to exist, to
be a directory rather than a file, and to hold no untracked records. `SP056` requires every `.yaml`
in it to validate against the schema this framework already ships for that record type. Non-YAML
files are ignored, so a register may carry a `README.md`.

With this, **no control at any level is declared-only.** The banner that reported how many were is
now unable to fire.

**An empty register passes, and that is the decision this packet exists to make.** A check that
demanded records would be a check that rewarded inventing them. A repository that has made no
overrides has an empty overrides register, and that is the correct state. So a pass establishes
that **no unvalidated record exists in that register** — never that records exist. The cost is
stated rather than minimised: an adopter who files nothing passes forever, and nothing here detects
a run that happened and went unrecorded.

**Two of `DR-25`'s claims did not survive implementation**, and that record is amended in place:

- **Currency is not provable.** No record schema carries an expiry or a review date;
  `revalidation_trigger` is a free-text condition, not a deadline. Nothing is declared to check
  against — the same shape as the gate exceptions `F22` left open, found again one packet later in
  a different contract. Twice in two packets is worth naming: **this framework's schemas record
  when something was created far more often than when it stops being good.**
- **`provenance` and `run_lineage` would have collapsed into one control.** One record type serves
  both; one *check* serving both does not follow, and would have made declaring either
  indistinguishable from declaring the other. They are separated in the next packet.

**The first thing the new check caught was this project's own golden example**, which declares all
four controls and named no register.

`schemas/method-run-lineage.schema.yaml`, `override-record` and `method-registry-entry` are read by
the checker for the first time. `exception_validator` is generalised into `record_validator` rather
than copied, because the `jsonschema`-absent path is the one that must not fall silent.

### `F23`: a drift guard was matching on line shape, not on the thing it guards

Found while building the above. `tests/validate_contracts.py` located the checker's gate catalogue
with `^    "([a-z0-9_]+)": "` — every four-space-indented `"key": "value"` line **anywhere in the
file**. The new `PATTERN_C_CONTROLS` dictionary has that shape, so four non-gates joined "the gate
catalogue" and the count went 19 → 23.

It tripped, and that was luck rather than design. Constructed and run:

| Mutation | Old guard | New guard |
|---|---|---|
| Drop one gate, add a **one-entry** dictionary of the same shape | **19 — passes** | 18 — fails |

The set it then iterates has silently lost a real gate and gained a fake one, and every assertion
downstream passes against it. Fixed by anchoring to the `GATE_CATALOGUE` block, so a renamed block
fails loudly instead of matching nothing.

This is the register's most-repeated shape — an instrument whose negative result does not establish
what it appears to — and this instance was inside an instrument written to prevent exactly that.

### `C2`: records must reference what they describe

A JSON Schema sees one record at a time, so a run-lineage record naming a method nobody registered
validates perfectly, and so does an override naming a run that never happened. `SP057` reads across
the registers; `SP058` covers register integrity — no two records under one identity, no record
carrying another application's `application_id`.

**`provenance` and `run_lineage` are separated by reference direction**, and the first answer had to
be withdrawn to get here. `DR-26` predicted they would be split by which optional fields each
obliges. Re-reading the schema disproved it: `method-run-lineage` already requires `completed_at`,
`input_hash`, `implementation_revision`, `configuration_version`, `configuration_hash` and
`output_hash` on **every** completed run, and non-empty `input_references` on every run at all.
There were no optional fields left to divide, so both controls would have obliged nothing — the
collapse the split existed to prevent. `run_lineage` now requires a run to resolve to the method
that ran it; `provenance` requires it to resolve to every override that adjusted the result.

**A reference is checked only where the register it points into is declared here**, because
obliging otherwise would make declaring one control silently require another. And a conditional
check that falls silent is indistinguishable from one that passed, so the run **says** when a
reference was not checked.

**A defect the probe caught, in the design rather than the code.** The plan said records failing
`SP056` are excluded from the index *"so one malformed record does not cascade"*. Excluding them is
what causes the cascade: when the broken record is the reference **target**, a perfectly correct run
suddenly resolves to nothing. The remedy is knowing the register is incomplete, not omitting a row —
a reference into a register that could not be fully read is reported as **unchecked**, never as
unresolved.

Two worked examples now exist because they had to. `override-record.approved.example.yaml` has
always named `RUN-2026-000412` and `METHOD-SEASONALITY-001`, and both were **dangling** — the
example set was designed as a whole and a third of it was never written. Nothing noticed, because
nothing read across records.

### `F24`: a schema clause that could never add an obligation

`method-run-lineage.schema.yaml`'s third `allOf` branch required four fields of completed runs at
medium or high materiality. Both its condition and its consequent are **subsets** of the first
branch's, which requires those fields — and three more — of every completed run.

Inert, and not harmless: a schema is a contract people read to learn what is required of them, and
this one implied a low-materiality completed run escapes fields it does not escape.

History could not say which branch was the leftover — the repository is one squashed commit and the
changelog had never mentioned materiality. The design evidence could: `override-record.schema.yaml`
is the only live use of `materiality` in any schema, and it grades **approval**, not record
completeness. So **materiality decides who must sign off, not how complete a record must be**, and
the branch graded the wrong axis. Removed rather than made real; narrowing the first branch instead
would loosen a published contract and grade completeness by a self-declared field.

No instance's validity moves, so this is not breaking and the `$id` version segment is unchanged.

Worth carrying forward: with `F22`, where a gate exception's only date records its creation rather
than its expiry, the pattern is that **these schemas collect a field far more readily than they give
it force.**

### The Plyego gate: the framework met a repository it did not write, and passed

Installed into a throwaway clone of a 3,049-file repository — Python and TypeScript, a user
interface, 1,092 markdown files, its own governance conventions — and returned:

```
PASS - all conformance checks satisfied.
```

At `essential`. Working without being tuned for it: `SP046`/`SP047` found the repository's real
blocking `gitleaks` step and confirmed its exit code is not discarded, `SP051` verified its lock
file, `SP030` refused `standard` on six gates, and `SP052` caught `documentation_authority`
declared without the gate that verifies it. **The four interface gates ran for the first time** —
surfaceplate sets `builds_user_interface: false`, so nothing here could ever have exercised them.

Nothing was written to that repository, and it is not adopted. `DR-28` records both the result and
what adoption would cost it.

### `F25`: declaring a placeholder-scan exemption made the profile fail the placeholder scan

`SP020` scanned every string in the application profile. An exemption's rationale must say why an
artefact legitimately contains a placeholder token — which means quoting it. **So declaring the
exemption failed the profile: the remedy for the defect could not be used without causing it.**

Fifth instance of the self-quotation shape in this register, and the first that is *structurally
unavoidable* rather than incidental. The earlier four were documents that happened to describe a
defect; each could be reworded or exempted. Here the mechanism built to fix the defect was itself
the trigger.

It was invisible from inside: this repository's own two exemptions describe the tokens without
reproducing them, a habit formed by `F14` and `F15`. The trap needed an adopter who wrote the
natural sentence.

Fixed by excluding `placeholder_scan_exemptions[*].rationale` from the profile walk — one field, not
one record. The artefact path beside it and every other rationale stay scanned, and three negative
controls hold that line. A rationale reading only `TODO` now passes, which is `DR-22`'s already
recorded limitation rather than a new one.

### `F26`: a remedy line that was wrong for seventeen of nineteen gates

`SP032`'s placeholder branch read *"Complete the artefact. A template is not a design policy"* for
every gate — wording written for `design_authority` and copied into the generic path, where it says
nothing about a work register or a changelog. It also **named no remedy**, though one has existed
since `DR-22`, so an adopter meeting a legitimate mention had nothing to act on. Now generic, and it
names the exemption route.

`org/RELEASE_PLAN.md` item 5 said no adopter had ever been exercised. That is now false in part, so
it is **rewritten rather than annotated**: one has been exercised, none has adopted.

### `F27`: the installer forbade what the standard permits

Surfaceplate would not install into a repository that already has a hook system. The refusal is
correct — setting `core.hooksPath=.githooks` would silently stop the existing hook running — and the
detection is thorough, reading effective local, worktree, global and system configuration and every
hook type, then failing closed and atomically.

**The defect is that there was no third route.** `SP038` fires only when a gate's `enforcement` list
claims `local_hook`, so a profile declaring `enforcement: [history_audit, review]` has always been
fully conformant with no hook anywhere. **The standard said the hook was optional and the installer
said it was mandatory** — two parts of one framework disagreeing about the same obligation, which is
the defect this register names more often than any other, found in itself.

The blocked case is any repository with existing commit-time automation, which is the target rather
than an edge case, and forty-five files were withheld over one optional 25-line shim.

`--no-hooks` installs everything else, leaves `core.hooksPath` alone, and **records the
declination** in `.standards/INSTALL.json` so every check reports it. Recorded rather than silent
because the alternative is the shape this framework exists to catch: nothing would distinguish
"staged changes are gated" from "nothing gates them". Every other narrowing here announces itself.

Chaining the adopter's hook from surfaceplate's was rejected: the delegation logic would ship to
every adopter and have to work for arbitrary hooks, and the framework would become the permanent
owner of another system's hook.

### `F28`: `SP038` accepted any pre-commit hook as satisfying a `local_hook` claim

Found by writing a probe to demonstrate a property the plan asserted, and watching it fail.

`active_pre_commit_hook` asked whether **an** executable `pre-commit` existed in the active hooks
directory. Any hook, doing anything. So a gate could claim `local_hook` and be satisfied by a hook
that formats code — and the finding's silence established *"a hook exists"*, never *"the conformance
check runs before commit"*.

It predates the opt-out and was exposed by it: declining leaves `core.hooksPath` pointing at the
adopter's own hook, which passed the old test perfectly.

The remedy needed no new data. `.standards/INSTALL.json` has always carried the digest of
`.githooks/pre-commit`, so the active hook is now compared against the one installed. Three failure
modes are distinguished and each is asserted: no hook, a hook that is not this standard's, and hooks
declined. The finding's title changed with them — *"there is no hook"* is plainly wrong against a
repository that has one.

The approved plan for this packet said `SP038` was untouched and still caught a false claim. That
was false when written, and fixing it was inside the packet's promise rather than added to it.

### `F29`: the agent instructions this framework ships were read by nothing

Surfaceplate shipped 501 lines of agent instruction as six `.github/instructions/*.instructions.md`
files, each declaring `applyTo: "**"` and opening *"Installed by Surfaceplate. Do not edit this file
in an adopting repository."*

**That is GitHub Copilot's format.** Claude Code loads managed policy, `~/.claude/CLAUDE.md`,
`./CLAUDE.md` or `./.claude/CLAUDE.md`, `./CLAUDE.local.md`, and `.claude/rules/*.md`.
`.github/instructions/` is on no list; `.github/copilot-instructions.md` is read only by `/init`.

And this repository has no `CLAUDE.md`, so its own instructions reached **nothing at all in the
repository that publishes them**. Every packet of governance work here was done by an agent that
never read a line of them.

Established twice, because inferring behaviour from a filename is what caused this: by direct
observation across a working session, with `~/.claude/CLAUDE.md` loading as the positive control;
and against the documentation, which is exhaustive about the loaded locations.

**`DR-12` was right about neutrality and wrong about mechanism.** It committed to `AGENTS.md` as the
canonical emitted file — and *"Claude Code reads `CLAUDE.md`, not `AGENTS.md`"*, so that remedy would
have been equally inert. The error survived because the commitment was never built: an unimplemented
decision cannot be falsified by contact with reality.

One canonical body in `standard/agent-instructions/` now emits per agent — Copilot's form
**byte-identical to before**, `.claude/rules/surfaceplate-*.md` carrying `paths:` where Copilot
carries `applyTo:`, and a canonical copy for agents not emitted for. `AGENTS.md` receives the
conformance block through the existing marker mechanism, so an adopter's own content survives in
full. The installer **never writes `CLAUDE.md`** — that file belongs to the adopter.

**And surfaceplate now has a `CLAUDE.md` importing `@AGENTS.md`.** The framework is finally subject
to the instructions it publishes.

**Not claimed:** that the instructions are now *read*. Files existing in documented locations is not
content entering a context window, and that distinction is the finding. It is observable in a later
session and has not been observed yet.

### `F30`: renaming a precondition artefact falsifies a gate's whole history

Found by `F29`'s own fix. The history audit resolves a gate's precondition by its **current** path,
so moving `standard/.github/instructions/tests.instructions.md` to
`standard/agent-instructions/tests.md` — without changing a word of it — made the audit report
**nine commits**, back to the repository's first, as having crossed `test_convention` without its
precondition. None of them had. The convention was in force throughout, under a different name.

None of the obvious remedies applies: `SP034` refuses to move `effective_from` forward, and
correctly; `SP032` requires every named artefact to exist, so listing the old path alongside the new
one fails; and not renaming was not available, since the rename *was* the fix.

So the route is a gate exception — `governance/exceptions/GX-0001.yaml`, this repository's first,
naming all nine commits with a rationale. Right for this instance, wrong as a general answer:
`DR-22` already warns that *"a growing pile of these records is evidence that the gate is wrongly
scoped or the process is wrong."* Following renames through git is the candidate remedy, is not
small, and is left open rather than half-built.

**A trap found on the way.** The exception listed abbreviated SHAs unquoted, and `7547482` — seven
digits, no letters — parsed as an integer. `SP043` rejected the record. The check did its job, and
the trap waits for any adopter whose abbreviated SHA happens to be all digits.

### `F31`: the history audit had been running against one commit

`actions/checkout@v4` fetches a **depth-1 clone** unless told otherwise, and neither this
repository's self-check workflow nor the one it installs into adopters told it otherwise.

`git_history_available()` verifies `HEAD`, and a shallow clone has a perfectly good `HEAD`. So the
prerequisite-gate audit ran, examined the single commit it had, found nothing, and said nothing —
while `SP035` and `SP036` were incapable of firing in CI at all. **Every green run this project has
had reported a clean history audit from a look that could not have found anything.** The advisory
written for precisely this case never fired, because history *was* available; just almost none of
it.

It surfaced only because `GX-0001` names nine historical commits and CI could not resolve one:
`'1b0df98': fatal: Needed a single revision`. **A control that fails closed exposed one that had
been failing open.**

Fixed in both places, because either alone leaves the defect somewhere: `fetch-depth: 0` in this
repository's workflow *and* in the one installed into adopters, plus the checker now detecting a
shallow clone via `git rev-parse --is-shallow-repository` and reporting it in the same terms as the
unavailable-history note. A workflow is configuration an adopter can change; the checker saying what
it could and could not see is not.

### Item 1: pip packaging, and the precondition `DR-10` left unsolved

`DR-10` flagged, and left unsolved, that `install_standard.py`'s file-location mechanism does not
survive pip distribution: `repo_root()` and `build_payload()` resolved repository-root directories
that sit outside any importable package. No sibling repository had attempted this before — checked
exhaustively before design began.

**A correction found before any design started.** `DR-10`'s pinning mechanism — a wheel-file digest
disambiguated by `adoption.distribution_channel` — was already superseded by `DR-14`, accepted and
implemented: `framework_digest` is `sha256(MANIFEST.sha256)`, channel-neutral by construction,
identical whether the code arrived by git clone or `pip install`. `DR-12`'s prose still cited the
superseded mechanism; corrected in place rather than left standing.

**The payload physically moved under one package directory, `surfaceplate/`** — `standard/`,
`schemas/`, `core/`, `templates/`, `examples/`, `adapters/`, `VERSION`, `MANIFEST.sha256`, and the
installer and checker themselves. `repo_root()`'s fix turned out to be one line
(`.parent.parent` → `.parent`), not the `importlib.resources` rewrite anticipated going in: because
`install_standard.py` now lives inside the tree it locates, `Path(__file__).resolve().parent`
resolves correctly for a git checkout, a normal pip install, and an editable install alike.

**Proven, not assumed.** A real wheel was built and its contents listed directly — 54 entries, every
one under `surfaceplate/` or its own dist-info, nothing from `tests/`, `org/`, or anywhere
`.git`-adjacent. Installed into a clean virtualenv with no surfaceplate source tree reachable, and
from that virtualenv alone, `python -m surfaceplate.install_standard --target <fresh repo>`
installed the standard successfully and the resulting repository checked out correctly.

Every internal reference in this repository was swept and corrected where necessary: five test
suites, the self-check workflow, `README.md`, `INSTALL.md`, `NAMESPACE.md`, `ORGANISATION.md`,
`RECONCILIATION.md`, `governance/authority-map.yaml`, and eight prerequisite-gate declarations in
this repository's own profile.

**Two pre-existing defects were found and fixed along the way, neither created by this change.**
`governance/authority-map.yaml` pointed `activity/**`'s authority at a Copilot-emitted filename
(`activity.instructions.md`) rather than the canonical one, stale since `DR-30` dropped that suffix.
The same file also claimed `DR-14`'s pinning mechanism was *"decided but not implemented"* — false
since its own acceptance.

**`F30` fired again, immediately, on the next rename of the same file.** The precondition artefact
for `test_convention` moved a second time in one session, and the history audit reported the
previous rename's commit as a violation, for the same reason `GX-0001` already exists. Cleared by a
second exception, `governance/exceptions/GX-0002.yaml`. Two occurrences of the same defect from two
renames this project chose for its own reasons is stronger evidence than the finding had when first
written — the deferred remedy is not built here regardless, because building it as a side effect of
a packaging packet would be exactly the scope creep this project's own working method exists to
catch.

**Not built:** the `surfaceplate` console-script entry point (item 2, deliberately kept separate)
and the content-based self-install guard `DR-10` also flagged (still deferred; no console script
exists yet to make the footgun real).

### Item 2: the CLI and the wizard, and resolving the "wizard" naming collision

`surfaceplate` is now a real console-script: `install` and `check` (unchanged behaviour, thin
wrappers) and `adopt` — a new interactive terminal wizard that fills in
`governance/application-profile.yaml`. Bound by one rule stated in `org/RELEASE_PLAN.md` before any
of it was built and held to throughout: **it asks, the human answers, the tool writes.** It never
selects a conformance level, invents a rationale, or sets a date.

**Terminal, not a browser form — decided collaboratively, not assumed.** Three moments of the flow
were mocked up as a clickable comparison artifact rendering both a terminal and a web form, walked
through with the maintainer before any code was written. The maintainer's own framing —
*"how does someone answer in a prompt back"* — is why that artifact exists. `questionary` was
chosen over raw prompts; `DR-32` records the reasoning.

**`prompts/github-copilot-adoption-wizard.prompt.md` retired**, replaced by
`prompts/copilot-implementation-assistant.prompt.md`. Its Phases 1–3 (discovery, questions, profile
authoring) are exactly what `surfaceplate adopt` now does deterministically; its Phases 4–7
(bounded implementation, validation, review gates, completion report) are kept, rewritten to
*consume* a profile the CLI already produced. A repository-wide sweep confirms the renamed file
claims the word "wizard" for nothing but the CLI command itself.

**The profile is verified before it touches disk, and that verification is not decorative.** The
wizard re-parses its own rendered YAML, checks it round-trips to the dict that produced it,
validates it against the schema, and scans for template placeholder tokens — refusing to write on
any failure. Two of four defects found during development were caught exactly this way: PyYAML
appends a `\n...` document-end marker to a bare scalar that plain `.strip()` does not remove, and
PyYAML wraps long plain scalars at 80 columns with a continuation indent that is wrong once
embedded in hand-built structure. `DR-32` records all four and the fix for each.

**`questionary` is an optional extra** (`pip install surfaceplate[adopt]`), not a hard dependency —
found while wiring CI, not assumed: the existing dependency-lock check would otherwise have
required it in the workflow this project installs into every adopter, which never runs `adopt`.

**Proven, not assumed.** `tests/test_adopt.py` (23 checks): a scripted `essential`-level run
produces a profile the real checker raises zero schema-shape findings against; a `full`-level,
UI-building run declares all 19 gates and all 9 controls with every level-mandatory gate
`required` and never anything else; an interrupt mid-flow leaves the repository byte-for-byte
unchanged; `adopt` refuses a missing install and refuses to overwrite a real profile. All six test
suites pass together for the first time under this name.

**A fifth defect, unrelated to the wizard, found by the same discipline.** Reinstalling from a
clean release archive — required by this repository's own working instructions after any payload
change — surfaced a pre-existing bug in `scripts/build_release.py`: the ZIP's `MANIFEST.sha256`
entry still used its pre-`ACT-019` archive path, placing it beside `surfaceplate/` instead of
inside it, so `framework_anchor()` found nothing there and every fresh reinstall from a real
release archive produced `SP049`. Fixed with the same `relative_to(ROOT)` pattern every other
payload file already uses; this repository's own `framework_digest` re-pinned to match.

**An environment finding, recorded rather than smoothed over.** The machine this was built on has
no `pip` on its bare `python3` and apt-installed `jsonschema`/`PyYAML` older than this project's own
pins — `F21`'s divergence, reproduced live on the maintainer's own machine. Recorded as an
observation in `org/FINDINGS.md`, not a new finding: nothing in the framework failed, and a
repository-local `.venv` is the ordinary remedy.

**Not built:** `--web` mode, resumability, and a `deferred` path through `control_decisions` — all
disclosed in `DR-32` as evidence-led deferrals, not silent gaps.

### `F32`: the wizard invented rationale text, found by the review it produced (`ACT-022`)

Item 9's first finding, and it was real. `sections.py`'s `ask_controls` hardcoded rationale text
for all three baseline controls, and `ask_gates` did the same for the four UI gates it
auto-marks `not_applicable` when `builds_user_interface` is false — neither routed through
`Prompt`, contradicting the package's own stated rule that nothing here invents a rationale.
`ACT-020`'s 23-check test suite never caught it: it proved every *asked* question was answered,
never that every *written* value traced to one.

Not every finding in the same report survived independent verification against the code before
being accepted. `adoption.deferrals = []` is a disclosed limitation (`DR-32`), not an invented
claim. The report's over-engineering finding — that a non-UI repository must manually justify
each UI gate — is wrong about the code, which already auto-masks them; the reviewer had not
traced that branch.

Fixed: both hardcoded paths now ask, the UI-gate one with the old text offered as an editable
default rather than a silent write. A new test scripts rationale text matching none of the old
hardcoded strings and asserts the written profile contains exactly that text — a regression here
misaligns the scripted answer sequence and fails loudly.

### Item 5, phase 1: Plutos exercised, Plyego paused for its own migration (`ACT-024`, `DR-34`)

Plyego is mid-migration to Google Cloud — real operational risk, and the wrong moment to install
anything into it regardless of what a throwaway clone can and cannot affect. Plutos took its place
for this round: surveyed read-only first (Python-only, hash-locked dependencies, CI that actually
runs its test suite, secret scanning already blocking) and exercised the same way `DR-28` exercised
Plyego — a local clone, installed, checked, nothing written to the real repository.

**Passed cleanly at `essential` on the first attempt** — no defect needed fixing to reach it, unlike
Plyego's first honest probe, which needed two (`F25`, `F26`). One defect was found regardless:
`install_standard.py`'s `--no-hooks` path told every adopter to activate and rely on a pre-commit
hook it never installed, because nothing had ever exercised that branch's own messaging for real —
surfaceplate's own self-install always keeps the hook. Fixed: the "Next steps" text is now
conditional, naming `history_audit` and `review` when the hook was declined. A positive control was
added alongside the negative one, proving both branches of the conditional, not just the one that
was wrong.

**A second defect this packet's own verification found, unrelated to Plutos (`F33`)**:
`tests/test_install_and_check.py` failed intermittently — an abbreviated commit SHA that happens to
be all digits parses as a YAML integer unless quoted, failing the gate-exception schema.
`governance/exceptions/GX-0001.yaml`'s own comment already documented this trap once; it never
reached the adopter-facing template, this test, or the checker's error message. Fixed in all three,
confirmed with a 40-iteration reproduction and 10 further clean runs.

**A third, found by CI itself minutes after `F33` landed (`F34`)**: the release manifest named a
file — a Claude Code harness runtime artefact — that existed on the machine that built it and
nowhere else, because `scripts/build_release.py`'s payload walk never asked git anything and could
not see the machine-local `.git/info/exclude` that kept the file out of the repository proper. Fixed
at the actual boundary: the walk now intersects against `git ls-files --cached --others
--exclude-standard`, deliberately including not-yet-added new files so this project's own
build-then-stage-then-commit packet order keeps working.

**Plutos is not adopted.** The same principle `DR-28` established still holds: gate and control
decisions are the maintainer's to make with the per-gate cost in front of him, not an agent's to
infer from a probe. `DR-34` carries the full cost table, including a genuine open question this
record does not resolve — Plutos already runs its own 75-activity register, in a different shape
from this framework's own convention; whether `work_registration` should point at it as-is or treat
it as a second, parallel system is the maintainer's call when adoption is actually decided.

### The hook-conflict refusal explains itself now (`ACT-025`, `F35`)

Found by the maintainer, not by a probe: running the installer against a real repository for the
first time and hitting the hook-configuration refusal, his own words are the finding — *"I run it
and didn't understand what was happening... we don't give the user any alternative or way out. It
just stops."* Checked against the actual message: true on both counts. Nothing said whether the
conflicting `core.hooksPath` value was set for this one repository or the whole machine, and two
of the three named "routes" described an outcome with no step to reach it — only `--no-hooks` was
something a reader could type.

Fixed together, not reworded separately: a new `hooks_path_scope()` checks `--local`, `--global`,
and `--system` individually (deliberately not `--worktree` — an earlier version of this fix
checked it first and, without `extensions.worktreeConfig` enabled, misattributed every plain local
setting as worktree-scoped, caught in this project's own testing before it shipped). The
rewritten message explains what `core.hooksPath` does, names the scope and its blast radius
plainly, gives the exact scope-correct command for "remove," and for "reconcile" points at the
actual delegation pattern this machine's own conflicting hook already uses rather than a vague
instruction to merge behaviour. Verified against the exact scenario that prompted it, plus fixture
coverage for both local and global scope and the separate default-hooks-directory conflict shape.

### `adopt` remediation, phase 1: a real data-loss bug, and a wizard that presumed knowledge (`ACT-026`, `DR-35`, `F36`)

Found by the maintainer running the real wizard against Plutos, not a probe: roughly twenty minutes
into a `standard`-level walk, the final write refused outright, and the answers were unrecoverable.
His own words — *"Extremely long and difficult... really bad experience"* — described both a
correctness bug and a genuine fit gap, and he set an explicit condition before any of it was coded:
*"Until we don't have a complete remediation plan that I approve you don't implement anything."*

**The bug (`F36`).** `render.py` hand-built `artefacts: [...]`, `paths: [...]`, `enforcement: [...]`,
and `wired_in: [...]` by escaping each value as though it were its own standalone document, then
wrapping brackets around the result by hand — the wrong escaping rules for an item inside an
existing YAML flow sequence, which is stricter. The maintainer's own answer, `what is this?`, broke
exactly this way. Fixed by handing PyYAML the real Python list (`yaml.safe_dump(values,
default_flow_style=True, ...)`) so it escapes for the structure it is actually part of, rather than
composing the two contexts by hand. A structurally similar block-list pattern
(`human_roles`/`exclusions`) was tested against the same tricky characters before deciding it did
not need the same fix — it didn't; block-sequence and standalone-document escaping happen to
coincide, unlike flow-sequence escaping.

**The fit gap.** Read back frame-by-frame against the originally approved mockup, the shipped
sequential-prompt wizard could never render the persistent, richly-formatted interface that was
actually agreed — a genuine revision of `DR-32`'s own reasoning, not new scope. Addressed in two
phases: this one ships on the existing architecture — a `simple`/`advanced` mode choice asked once
and threaded through every explanation shown; dual-register content authored for all thirty-one
things the wizard can ask about (three baseline controls, nine conformance-level controls, all
nineteen gates), grounded in this framework's own core documents; detected signals (existing CI, a
decisions folder, a CHANGELOG) shown before the level choice without the tool ever picking a level;
an editable, sourced example on every rationale field; and basic resumability, so a late failure now
loses at most the section in progress rather than the whole session. A second phase — rebuilding the
rendering layer on Textual to deliver the persistent multi-item interface the mockup showed — is
scoped in `DR-35` but not started; it is designed against this phase's real content, not a guess.

Re-run against the exact scenario that prompted this — a fresh Plutos clone, `essential` level,
`simple` mode this time — and it wrote cleanly on the first pass, with every control and the one
required gate explained in plain English before being asked, and the level screen naming Plutos's
real detected CI workflows without steering the choice.

### `adopt` remediation, phase 2: the interface that was actually approved (`ACT-027`, `DR-36`)

Phase 1 fixed what the wizard *said*. This rebuilds how it *asks*. Read back frame by frame, the
approved mockup shows an interface sequential prompts cannot produce at any level of polish: earlier
answers staying on screen, a conformance-level list where highlighting an option is explicitly not
choosing it, and a gate catalogue showing several gates at once with chip rows and follow-ups that
appear inside a gate's own block only once its status calls for them. `questionary` is replaced by
`textual`; `InteractivePrompt` and `prompting.py` are gone.

**The dependency replacement is a recorded human decision, not an agent's.**
`.github/skills/dependency-update/SKILL.md` makes replacing a dependency fixed by a decision record
a mandatory stop, and `questionary` was fixed by `DR-32`. The maintainer chose replacement over
keeping a fallback, on the grounds that a second interface nobody exercises is the same shape `F34`
had just found in the `--no-hooks` branch. Cost recorded rather than buried: seven transitive
packages against `questionary`'s two, landing only on the `[adopt]` extra and never on an adopting
repository's CI. `pip-audit` reports no known vulnerabilities for either set.

**The part that outlives the interface: the binding rule is now provable.** This repository's own
test file has said since `ACT-022` that `ScriptedPrompt` *"only objects to a call it wasn't given an
answer for, never to a value written without any call"* — which is precisely how `F32` (rationale
invented for seven controls and gates) passed every scripted test it had. `sections.py` is now pure
`build_*(answers) -> fragment` functions, so `tests/test_provenance.py` can assemble a whole profile
from answers in which every free-text field carries a unique sentinel and assert that every string
in the result either carries one or appears on an explicit 48-entry allow-list of what the framework
contributes. That allow-list is the honest answer to "what does this tool write on its own?", and
its own negative control injects a plausible fabricated rationale and confirms the walk objects.
Two further suites close the remaining gaps: a keyed `ScriptedInterview` (a planned field with no
answer, or an answer nothing asked for, both fail) and a screen↔plan join proving each screen
renders exactly the fields its plan declares — 138 of them on the gate catalogue alone.

Three defects that only building it revealed, each recorded in `DR-36`: Textual's `Input` starts
with its whole value selected, which would have silently wiped Phase 1's editable example answers on
the first keystroke; the mockup's `[g] jump to section` cannot work as drawn, because a focused text
field eats printable keys, so it is `Ctrl+G` and the hint says so; and a control the level requires
must be stated rather than offered as an untickable box, or the wizard would happily produce a
profile its own checker rejects.

### `adopt` remediation, phase 3: the interface, actually looked at (`ACT-028`, `DR-37`, `F37`)

Phase 2 closed with 87 passing checks, a decision record, and a published artefact captioned "the
three frames from the approved mockup, now captured from the running wizard". The maintainer opened
the wizard and sent three screenshots of something else.

**The defect was in the verification, not the widgets.** Every Phase 2 test asserted structure —
field-id joins, widget counts, status transitions — and each was sound. None asserted what a screen
puts on the terminal, so six user-visible faults passed all of them, and the screenshots were
published as evidence of fidelity without being looked at. `F37` records it as the failure mode
`working-method.md` names as the one that does not present as an error at all: a right answer about
the wrong object, where repeating the check only confirms it.

What was wrong: Textual markup parsed `[Tab]` and `[Enter]` as style tags and swallowed them, so
every legend lost its two most important keys while symbol-bearing ones like `[Ctrl+S]` survived —
and the resume screen, whose only affordance is `[y]`/`[n]`, offered a choice with no visible way to
make it. Every field printed its own name twice, because the label was rendered *and* passed as the
input's placeholder. Labels stacked above values instead of forming the mockup's column, because the
row was a `Vertical`. Every field's help rendered at once, mid-screen, when the plan had specified
one field's at a time in the hint line. And one gate was visible where the mockup's whole thesis is
several — all nineteen *were* mounted on one surface, which is exactly what the tests checked.

**Closed by making rendering checkable rather than by fixing six things.** `tests/test_render.py`
reads the compositor's own rendered lines and asserts named properties over them — every legend
renders the keys it names, no label appears twice, a label and its value share a line, one help line
at a time, at least three gates visible at 80×24, the level list numbered and marked. `DR-37`
records why these are properties and not a snapshot: this project treats a golden file as an audit
trigger, and a full-screen capture of a wizard whose copy is still being tuned would churn on every
wording change and train exactly the regenerate-to-green habit the rule exists to prevent.

All eleven assertions were seen to fail against the unfixed code, and three were re-broken
deliberately afterwards to confirm they still catch their own defect. Two further faults were then
found by simply reading the rendered output — the level list wrapping to column 0 and losing its
numbering, and the detected-signals line listing four full workflow paths across three rows. Neither
was in the original six; both were obvious on sight, which is the point `DR-37` closes on: the
property suite is the regression net, and looking is still the discovery method.

### `adopt` remediation, phase 4: discover first, then offer choices (`ACT-029`, `DR-38`, `F38`)

The maintainer ran the phase-3 build against Plutos and could not finish it: a two-line rationale
was refused at the review screen, after the whole interview had been answered. His verdict on the
rest was about the interaction model, not any single defect — *"free text is confusing and really
prone to errors... the wizard should do a discovery of the repo first to identify what is the
potential candidate for each question."*

**The blocker was worse than the symptom.** `render._block` refused any newline, and while the TUI
caught that and showed a message, the second authoritative render in `wizard.run` sits outside any
handler — the same value could have surfaced as a raw traceback. The restriction was never in the
format: this repository's own profiles use folded scalars seventeen times. Prose is now written as a
literal block scalar, with PyYAML handling the awkward parts (`|2-` for a leading space, a quoted
fallback where a literal could not round-trip), and `cli.py` guards the rest.

**Two of the four interface faults were this project's own code.** *"The terminal is cut if you
minimise the window"* was not a driver limitation — Textual reflows on `SIGWINCH`; `Vertical` is
simply not a scrolling container, and every screen used one as its frame. *"Some boxes (x) are not
clearly visible"* is `ToggleButton` drawing the same glyph in both states and signalling on/off by
colour alone. Arrow keys now move between fields, and help returns beside the field it explains —
reversing half of `F37`'s own remedy on evidence, since moving it to the hint line fixed the clutter
and buried the text.

**Discovery is the substance.** `discover.py` reads the repository, git-tracked only, and offers what
is really there: files for a precondition artefact, directories for a register, lock files, top-level
directories as pathspecs, and the real step names out of the workflow YAML — the field the maintainer
could not answer at all. `DR-38` records why this reconciles rather than reverses
`example_answers.py`'s refusal to invent plausible paths: the rule underneath that refusal is *never
offer something that isn't there*, and a file in the adopter's own repository is not an invented one.
The load-bearing half of `tests/test_discover.py` is the negative half — a gitignored file, an
untracked file and an ignored directory are never offered.

It also forced a correction to the provenance guarantee. The allow-list is built from every field's
choices, and a discovered `select` field's choices come from the repository — so the first run
admitted twenty-two CI step names into it. An allow-list that grows with the adopter's repository is
not an allow-list; it is narrowed to closed enums, with `select` fields answered by sentinel like any
other human answer.

**Two of this packet's own assertions turned out to be too weak, and tightening them exposed three
more defects**: setting `BUTTON_INNER` to a tick — the obvious fix for the invisible checkbox — is
drawn in *both* states, so an **unchecked** box rendered a tick and looked answered; `Input:focus`
stripped the underline from the one field being typed in; and `Select` exposes both `BLANK` and
`NULL` as different objects, so the blank test was silently always false. All three were invisible
to the loose versions, which is `DR-37`'s point demonstrated against this packet's own code.

### The history audit follows renames (`ACT-030`, `DR-39`, `F30` closed)

`F30` has been open since `ACT-018`. The audit resolved a gate's precondition artefact by its
**current** path and asked whether that path existed in each historical commit — so renaming a file,
without changing a word of it, retroactively reported every earlier commit as having crossed the
gate uncovered. It fired twice on this repository's own renames (`DR-30` making the agent
instructions agent-neutral, `DR-31` packaging the payload for pip) and cost two exception records
for work that violated nothing, which is exactly what `DR-22` names as evidence a gate is wrongly
scoped.

It was left unbuilt through four packets on a real objection, recorded at the time: *"`--follow` is
heuristic, single-path, and its results would have to be trusted by a control."* `DR-39` answers
that rather than waving it past. The lookup can only ever **add** names to search, so it can clear a
false violation and can never hide a commit where the artefact was absent under every name it has
ever had; and every followed rename is **stated on the run**, so a cleared violation is never
silent. This repository's own output now carries the chain: *"test_convention: precondition … followed
through 2 rename(s)…"*.

Two things worth recording. The directory case was found by driving it, not by reading: `--follow`
pointed at a directory does not error — it silently traces some file *inside* it and reports that as
the directory's former name. Harmless in effect, accidental rather than designed, and the first
implementation's docstring claimed a fallback the code did not have; directories now keep the strict
check explicitly. And `GX-0001`/`GX-0002` are **kept and marked superseded** rather than deleted:
they cover violations that no longer occur, but deleting an exception record is the retrospective
edit the standard says an exception must never be able to make invisibly.

### `adopt` remediation, phase 5: the scan that never reached the gates (`ACT-031`, `DR-40`, `F39`)

**The wizard completed a real adoption for the first time, and produced an unusable profile.** Seven
gates name `asdf` as their precondition. `tui/app.py` built the gate catalogue from
`plan.gate_plan(...)` without passing the repository scan, while the controls screen went through
`section_plan()`, which scans — so controls offered dropdowns of real files and gates offered blank
boxes. Facing an empty required field, placeholder text is the correct human response and the wrong
wizard behaviour.

**The join test added at `ACT-028` could not have caught it, and strengthening it was still not
enough.** It compared field *ids*, which are identical whether a field renders as a dropdown or a
text box; only the *kind* differs — `F37`'s shape one level up, the right questions asked in the
wrong form. Comparing `(id, kind)` was necessary and insufficient: the join builds both sides
itself, so it can never see the app wiring two screens from different sources. Only a test that
drives the real `AdoptApp` catches it, and it is seen to fail with the defect reintroduced. A join
test proves the parts agree; it says nothing about the assembly.

**The wizard's shape changed on the maintainer's own proposal.** It asks the minimum first —
identity, stack, risk, level, the four nobody can answer on an adopter's behalf — then offers **Set
defaults** or **Customise adoption**. Defaults propose from three honest sources only: *discovered*
(a real path or CI step read from the repository), *example* (worked prose this framework already
ships), *computed* (today's date, the review horizon, the owner already given). A field with none of
those is **not proposed and still asked** — a gate's description, an adoption decision-record id.
Against real Plutos that is 63 proposals with 17 left over, and `work_registration` proposes
`activity/register.md`, which `DR-34` had independently identified as Plutos's real register.

`DR-40` records why this does not breach *it asks, the human answers, the tool writes*: a proposal is
a suggestion until a human passes a screen showing it and its origin, so an accepted proposal is an
answer — and the provenance walk needed no change at all.

The opening question also stopped asking which register of explanation you want, which is a question
about the tool's output asked before any has been seen, and now asks about experience instead.

Four interface faults from the same run: the tick that did not fit its box (`[X]` / `[ ]` and
`(●)` / `( )` now), three interaction models on one screen (the gate chip row is a radio set), a
dropdown that needed two clicks, and forty alphabetical candidates — now ranked per gate and cut to
twelve **after** ranking, since capping first buried the register beneath `docs/archive/`. And the
run no longer ends in silence: it states the path it wrote and runs the checker against it.
