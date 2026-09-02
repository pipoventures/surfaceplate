# Remediation plan — acting on the adversarial product review of 2026-09-02

**Source:** `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md` (Part I findings F-A to F-R and code
items 1 to 19; Part II recommendations R1 to R14 as revised by the second pass). This plan
implements all of them. Where a recommendation was withdrawn in the second pass (pre-marked
`not_applicable`, a `--yes` flag, comments-as-provenance, a digest template guard) the withdrawn
form is not planned; the corrected form is.

**Who does what.** The plan was drafted by an agent in the review session. The maintainer takes
the decisions in section 2 and authorises the activities in section 3; nothing below proceeds
without that. Each phase is then implemented by a **fresh session** given only this file, the
report and the repository, on its own branch, with tests written first, all fourteen CI steps
green, and one pull request per phase which a separate fresh session reviews with the `review`
skill before the maintainer merges. That is the working method's single-writer rule and this
repository's `decision_before_implementation` gate applied to itself.

**Binding on every implementing session:** the installed instructions under `.claude/rules/`
and the skills under `.claude/skills/`; the binding rule in `org/RELEASE_PLAN.md` ("it asks, the
human answers, the tool writes"); no test weakened, no golden regenerated to absorb an
unexplained change; `surfaceplate/build_release.py` then reinstall, re-pin, rebuild the manifest
last, as `CLAUDE.md` describes; British English; evidence, not intent, in every completion record.

---

## 1. Phases at a glance

| Phase | Activity | Content | Starts when |
|---|---|---|---|
| 0 | `ACT-043` | Stop the bleeding: the eight defects that make the wizard unfinishable or destructive, each with its regression test first | `ACT-043` authorised. No rule changes. |
| 1 | `ACT-044` | Proposal-first adoption with a provenance record; one gate list with human decisions; validator parity; discovery that excludes the framework | `DR-47`, `DR-48` accepted; `ACT-044` authorised; phase 0 merged |
| 2 | `ACT-045` | Non-interactive `--propose`/`--answers`; `doctor`; output formats and exit codes; the bounded front-door pass; generated numbers and link checks | `DR-49` accepted; `ACT-045` authorised; phase 1 merged |
| 3 | `ACT-046` | The 80×24 snapshot suite and measured budget test; register parity; optional-field schema change; docstring style | `DR-50` accepted; `ACT-046` authorised; phase 2 merged |
| — | `ACT-042` | Record the review, this plan, the decisions and the findings (the review session's own output) | `ACT-042` authorised |
| — | `H1` | The maintainer runs `adopt` against Plutos for real | Phase 0 merged |

Effort words are deliberately absent. The previous plan's "days" and "weeks" were estimates
presented as a plan, and the second reviewer said so.

---

## 2. Decisions the maintainer takes before implementation

Each is stated as the decision record it becomes, with the recommended option first. An agent
drafted these; a human decides. "Accept" means the drafted record is written to
`org/decisions/` with the maintainer as decision owner and this plan as the evidence reference.

### D1 — `DR-47`: what "asked" means, and a provenance record beside the profile

*Needed by phase 1 (R1, R2, R3).* `DR-46` made `effective_from` a question again because the
tool had chosen the narrowest value silently. The review found the same rule, implemented as one
widget per field, produced a profile whose header claimed human authorship over canned prose.

**Decision proposed.** (1) A value is *asked* when it is presented to the human with its origin
and the human can change it before the profile is written; a form field is one way to present
it and the annotated review is another. (2) The tool may propose any value from the three
sources `defaults.py` already names (discovered, example, computed) plus a fact of record and a
scaffolded artefact, and must record the origin of every value it wrote in
`governance/application-profile.provenance.yaml`, a machine-owned file beside the profile. (3)
The tool never records a proposed value as typed or accepted; it records typed values as typed,
edits on the review as typed with a timestamp, and approval at document level with a timestamp.
(4) The tool never supplies a scope decision, including `not_applicable`; a human presses a key
per gate, or invokes an explicit bulk command that the provenance record writes as one human act
with its count. (5) `effective_from` is proposed as the adoption date and shown on the review,
where changing it is one edit; it is recorded as computed unless changed. (6) The profile header
states what the provenance record contains and no more. (7) `tests/test_provenance.py` remains
the enforcement, extended to the provenance record: every non-typed value carries an origin; no
origin says typed for a value the human did not type.

**Alternatives.** Keep `DR-46`'s per-field reading (the review measured its cost at 32 to 96
fields and a false header); or drop the rule (rejected: the rule is what makes the profile
worth reading).

**Risk level:** 4, it amends the rule every packet is measured against.

### D2 — `DR-48`: a shared rules module joins the install payload

*Needed by phase 1 (R8).* The wizard and the checker disagree on dates, ids, placeholders and
whether a named path is tracked; a profile can pass the wizard and fail its first check.

**Decision proposed.** Create `surfaceplate/rules.py` holding the date rules (`effective_from`
not in the future, `review_by` between today and today plus 400 days, `revisit_by` not past),
the `application_id` pattern, the placeholder pattern, and "named path is tracked by git";
`check_conformance.py` and `adopt/validators.py` both import it; it is added to the install
payload as `DR-20` requires for any payload addition, and `tests/check_vendored_current.py`
covers it. A parity test asserts that for every `SP` code reading a profile field, a wizard
validator refuses the same input or an exemption names the reason; history-only codes
(`SP034`, `SP035`) are exempt.

**Alternative.** Duplicate the rules in both places with a test that they agree (rejected: the
duplication is the defect).

**Risk level:** 3, it changes the payload every adopter receives.

### D3 — `DR-49`: exit codes, output formats and the front door

*Needed by phase 2 (R4, R10, R11).* Exit codes are read by the installed hook and workflow, so
they are a public contract; the release plan bounds the documentation pass.

**Decision proposed.** (1) `surfaceplate check` gains `--format text|json|sarif`; JSON first,
SARIF 2.1.0 with `partialFingerprints` and a rules list. (2) Exit codes become: 0 pass, 1 findings
that fail, 2 not installed, 3 usage or no terminal, 4 internal error; graced `WARN` exits 0 with
a printed summary. (3) `adopt` gains `--propose` (writes `governance/application-profile.proposed.yaml`
and the answers record, never the profile) and `--answers <file>` (replays a human-completed
answers record through the same code as the interface); no `--yes`. (4) `surfaceplate doctor`,
offline by default, `--online` for anything needing a token. (5) A real argument parser with
`--version` and `--help`. (6) The README pass now is bounded to: the three commands, the version
line, the two dead links, the extras form `surfaceplate[adopt] @ git+…`, a sentence on the
global hooks path; `INSTALL.md` gains `install`/`check` and loses the pointer to the uninstalled
prompt file. The restructure and any retirement of `SETUP_GUIDE.md` wait for the release plan's
item 8.

**Alternative.** Keep the current codes and add formats only (rejected: exit 2 covering four
conditions is what stops any wrapper from distinguishing them).

**Risk level:** 3, a public contract and the installed hook's reading of it.

### D4 — `DR-50`: the profile schema, the draft's home, and test dependencies

*Needed by phase 3 (R6, R9, R13).*

**Decision proposed.** (1) Fields the checker never reads become optional in the schema and are
stamped `# not checked` when present: `display_name`, `repository_classification`,
`human_roles`, `exclusions`, `independent_validator` at `essential`; the two gate descriptions
stay, because humans and auditors read them. (2) Two optional fields are added under `risk`,
`relied_on_outside_team` and `material_quantitative_output`, so the reason a level was chosen is
recorded. (3) The draft moves under `.standards/adopt-draft.json`, which the install record
already governs, instead of the installer editing an adopter-owned `.gitignore`. (4)
`pytest==8.4.2`, `pytest-textual-snapshot==1.1.0` and `syrupy==4.8.0` are added as a `test`
extra; snapshots are golden files under the tests rule. (5) Docstrings describe current
behaviour in a sentence and point at the decision record for history; existing essays move to
`org/decisions/` or the changelog as they are touched, not in one sweep.

**Alternatives.** Drop the never-read fields (rejected: breaks every existing profile and both
shipped examples); keep the draft where it is and gitignore it (an installer writing outside
`.standards/`).

**Risk level:** 3, a schema change and a new test dependency.

### D5 — authorise the activities and record the findings

`ACT-042` to `ACT-046` as drafted in section 3, and findings `F59` to `F77` as drafted in
section 5, recorded in the registers by the review session under `ACT-042`.

---

## 3. Activities, drafted for `activity/register.md`

Owner and reviewer are `maintainer` throughout, as every existing row. Status on recording is
`planned`, except `ACT-042` which is `in_progress` while the review session records and `done`
when the maintainer merges its pull request.

| Activity | Title | Depends on | Type | Material? | Judgement | Definition of done | Evidence required |
|---|---|---|---|---|---|---|---|
| `ACT-042` | Record the adversarial product review of 2026-09-02, its remediation plan, decisions and findings | `ACT-041` | — | yes — it records nineteen findings, four decision records and the plan every later activity cites | medium — the review's verdict is the reviewer's; which findings and decisions are recorded is the maintainer's, taken in the review session | The report, this plan, `DR-47` to `DR-50`, `F59` to `F77` and rows `ACT-042` to `ACT-046` are in the tree, `check_code_registers.py` passes, and the maintainer has merged the pull request | The maintainer's authorisation in the review session for each decision and activity, cited in each record; the fourteen CI steps green |
| `ACT-043` | Remediate `adopt`, phase 8: the eight defects that make the wizard unfinishable or destructive | `ACT-042` | hard | yes — it changes what every adopter sees on the gates screen and whether a real profile can be overwritten | low — every remedy is fixed by the finding; no rule changes | The gate status radios render at 80×24; the gates screen is seeded on the defaults route; an empty choice is refused at the field; a real profile is never mistaken for the template; `None` is blank; a validation error survives the focus move; quitting at the resume prompt keeps the draft; the resume header renders; help text is styled | Each regression test seen to fail before its fix and pass after; the eight images from the review re-taken and read; `H1` re-run by the maintainer |
| `ACT-044` | Remediate `adopt`, phase 9: proposal-first adoption with a provenance record, one gate list, validator parity, discovery that excludes the framework | `ACT-043`, `DR-47`, `DR-48` | hard | yes — it changes what every adopter is asked, what the profile says about its own origin, and what discovery may propose | high — bounded by `DR-47` and `DR-48`; the level stays a human decision; no scope decision is ever supplied by the tool | Eight to twelve fields before the review on the two fixtures the prototype used; the provenance record written and read by `test_provenance.py`; the header true; a gate list with no pre-marked statuses and a recorded bulk command; a profile that passes the wizard passes its first check; no framework-owned path proposed | The persona budget measured, not estimated; the prototype's profile equality reproduced on the real code; `SP` parity test green; a repository containing only the install payload yielding no proposals |
| `ACT-045` | Remediate `adopt` and `check`, phase 10: non-interactive adoption, `doctor`, output formats and exit codes, the bounded front-door pass, generated numbers and link checks | `ACT-044`, `DR-49` | hard | yes — a public exit-code contract, a new command, and the first sentence a stranger reads | medium — bounded by `DR-49` and the release plan's item 8 | `adopt --propose` and `--answers` round-trip the prototype's answers to the same profile; `doctor` reports the five facts that stopped the stranger install; `check --format json` and `sarif` validate; exit codes as decided; README and `INSTALL.md` as bounded; every number and link in the documents checked by `check_code_registers.py` in both this repository and an installed checkout | A clean-container run of every documented command, on a machine with a global `core.hooksPath`; a SARIF file accepted by a validator; the answers file replayed by CI |
| `ACT-046` | Remediate the evidence machinery, phase 11: the 80×24 snapshot suite and budget test, register parity, the schema change, docstring style | `ACT-045`, `DR-50` | hard | yes — a schema change and a new golden suite | medium — bounded by `DR-50`; snapshots are goldens and never regenerated to absorb an unexplained diff | Every screen snapshot-tested at 80×24 including a focused gate status; the budget test asserting the measured numbers; `check_code_registers.py` asserting body-versus-index status; the schema change with both examples updated; the suite count in `CLAUDE.md` and the workflow's "every step ran" loop updated in the same change | The snapshot suite seen to fail on a one-character stylesheet change; the parity check seen to fail on one deliberately contradicted status in a scratch copy |

---

## 4. The work, phase by phase

Each item: the finding it closes, the test written first, the change, and the evidence to put
in the completion record. File references are to `main` at `178ba2c`; a fresh session verifies
them before editing, because `F55` records that this codebase's own comments have been wrong
about it.

### Phase 0 — `ACT-043`

Work packet: objective, make the wizard finishable and non-destructive on the route the
maintainer uses; in scope, the eight items below only; out of scope, any change to what is
asked, written or proposed; owning files, `surfaceplate/adopt/tui/app.tcss`,
`surfaceplate/adopt/tui/app.py`, `surfaceplate/adopt/tui/screens.py`,
`surfaceplate/adopt/validators.py`, `surfaceplate/adopt/wizard.py`, `tests/test_adopt_tui.py`,
`tests/test_render.py`, `tests/test_adopt.py`; risk level 2; reviewer, maintainer; escalation,
any change that would alter a written value.

| # | Closes | Test first | Change | Evidence |
|---|---|---|---|---|
| 0.1 | F-A / `F59` | `tests/test_render.py`: the rendered lines of a `GatesScreen` at 80×24 with a focused non-mandatory gate contain `( ) required`, `( ) deferred`, `( ) not applicable` | `app.tcss:185-188` `.chip-row { height: auto; border: none; padding: 0; margin: 0 }`; delete the dead `.chip`/`.chip-selected` rules | Image before and after, read; the spike's `height_auto_compact.png` is the target |
| 0.2 | F-B / `F60` | `tests/test_adopt_tui.py`: drive `AdoptApp` through the defaults route at standard and assert the first artefact widget on the gates screen holds the proposal and the hint reads the proposed count | `screens.py` `GatesScreen.__init__` gains `initial`; `app.py:227` passes `self._seeded.get("gates", {})`; `defaults.unanswered` counts fields that will be presented unfilled | The "5 more" figure replaced by the true one on all three levels |
| 0.3 | F-E, code 2 / `F64` | `tests/test_adopt_tui.py`: `Ctrl+S` on `mode` with nothing chosen leaves the screen and shows an error; a blank `Select` on the gates screen is refused | `validators.check` treats `None` and non-strings as blank for `nonempty`, `date`, `effective_from`; `choice` fields validate "one of the choices" | The black-screen sequence re-driven and seen to stop at the first screen |
| 0.4 | code 1 / `F63` | `tests/test_adopt.py`: a completed profile whose prose contains "replace-me" is refused as already adopted; the untouched template is not | `wizard._refuse_if_already_adopted` checks required scalars for the token, not the whole text | Both directions seen in a scratch copy |
| 0.5 | F-R / `F74` | `tests/test_adopt_tui.py`: commit with a blank field while another has focus; after six pauses the hint still carries the error | `FormScreen.action_commit` focuses first, then sets the hint; or `on_descendant_focus` preserves a pending error | The vanish image re-taken |
| 0.6 | F-L / `F68` | `tests/test_adopt.py`: an interview whose `confirm_resume` returns `None` leaves the draft on disk; `False` deletes it | `TextualInterview.confirm_resume` returns a three-valued answer; `_resume_or_start` deletes only on an explicit "n" | Draft existence before and after each of `y`, `n`, `ctrl+q` |
| 0.7 | F-L second half, spike / `F68` | `tests/test_render.py`: the resume screen's first rendered line contains "A saved draft was found" | `screens.py` `ResumeScreen` header `markup=False`; the three step-prefixed headers likewise | Image |
| 0.8 | F-I / `F67` | `tests/test_render.py`: the help line for the focused field renders in the muted colour with one blank row before the next field | `app.tcss` gains `.field-help { color: #7a827e; margin: 0 0 1 2; }` | Image at 80×24 and 120×40 |

After phase 0 merges: **`H1`**. The maintainer runs `adopt` against Plutos. That run is the
acceptance test; its residue (draft, first attempt) is what `H1`'s entry already describes.

### Phase 1 — `ACT-044`

Work packet: objective, the wizard proposes and the human decides, with the origin of every
value recorded; in scope, R1, R2, R3, R7, R8 and code items 3, 6, 8, 9; out of scope, any
non-interactive mode, any document outside `surfaceplate/adopt/` except the two the binding rule
lives in; owning files, `surfaceplate/adopt/*`, `surfaceplate/rules.py` (new),
`surfaceplate/check_conformance.py` (imports only, plus one new `SP` code), `surfaceplate/install_standard.py`
(payload list), `tests/test_provenance.py`, `tests/test_adopt.py`, `tests/test_adopt_tui.py`,
`tests/test_discover.py`, `org/RELEASE_PLAN.md` (the rule's wording, per `DR-47`); risk level 3;
escalation, any value the tool would write that `DR-47` does not permit.

| # | Closes | Test first | Change | Evidence |
|---|---|---|---|---|
| 1.1 | R1, F-M / `F69` | `tests/test_adopt_tui.py`: the flow is decisions, level, review; no route screen exists; editing a line on the review changes the written value and its origin | `plan.decisions_plan` (the prototype's eight fields plus one per undiscovered control); `app._drive` builds the proposal after the level and pushes an annotated review; `DefaultsScreen` and `route` removed; drafts from the old shape resumed or refused by `DRAFT_FORMAT` | The prototype's images reproduced on the real code |
| 1.2 | R2, F-D / `F62` | `tests/test_provenance.py`: every non-typed value in a written profile has an origin in the provenance record; no origin says typed for a proposed value; approval is document-level with a timestamp | `defaults.Proposal.origin` gains `fact of record`, `scaffolded`; `sections` carries origin per field; `render` writes the true header; `wizard.run` writes `application-profile.provenance.yaml` | The record for the prototype's two personas, read |
| 1.3 | R3, F-A, F-K | `tests/test_adopt_tui.py`: a gates list with no pre-marked status on an unmandated gate; `n` offers the example rationale; the bulk command records one human act with its count | `GatesScreen` rebuilt as a list with single-key statuses and the bulk command; counter "N will be audited; M undecided" | Image at 80×24; provenance record showing the bulk act |
| 1.4 | R7, F-C, code 3, 8, 9 / `F61`, `F75` | `tests/test_discover.py`: a repository containing only the install payload yields no proposals and no "you appear to have"; 300 docs do not push the register out; a C-quoted path is offered verbatim; `is_empty` is true on a non-git tree | `discover` reads the exclusion list from `.standards/INSTALL.json`'s `files`; rank then cap, per field; `git ls-files -z`; `is_empty` fixed or removed | The three negative controls seen to fail first |
| 1.5 | R2 checker side, F-C / `F61` | `tests/test_install_and_check.py`: a required gate whose artefact is in the install record's file list, or a control whose CI step is the installed workflow's, is a finding | New `SP059` in `check_conformance.py`; code register updated | Both directions in a scratch copy |
| 1.6 | R8, F-G, code 5 / `F66` | parity test as `DR-48` describes; `validators` refuse a future `effective_from`, a 401-day `review_by`, a one-character id, basic-ISO dates, an untracked path | `surfaceplate/rules.py`; both importers; payload list; `check_vendored_current` | A profile that passes the wizard passing its first check on the two fixtures |
| 1.7 | code 6 / `F76` | `tests/test_adopt_tui.py`: resuming a draft that already chose proposals still reaches the review with proposals | Falls out of 1.1; assert it | — |
| 1.8 | F-F / `F65` | `tests/test_adopt_tui.py`: a placeholder is refused at the field; the review's error names the line and Enter goes to it; "write it" is hidden while an error stands | Placeholder pattern from `rules.py` applied at field commit; review error navigation | The deadlock sequence re-driven and seen to be escapable |

### Phase 2 — `ACT-045`

Work packet: objective, adoption without a terminal, a checker people can build on, and a front
door whose every instruction runs; in scope, R4, R10, R11, F-N, F-O's document corrections,
code items 7, 12, 13, 14, 17; out of scope, the documentation restructure the release plan
defers; owning files, `surfaceplate/cli.py`, `surfaceplate/adopt/wizard.py`,
`surfaceplate/adopt/interview.py`, `surfaceplate/check_conformance.py` (output and exit codes),
`surfaceplate/doctor.py` (new), `README.md`, `INSTALL.md`, `surfaceplate/core/*.md` (the six
corrections in F-O), `tests/check_code_registers.py`, `.github/workflows/*.yml`; risk level 3;
escalation, any exit code or format not in `DR-49`.

| # | Closes | Test first | Change | Evidence |
|---|---|---|---|---|
| 2.1 | R4 | `tests/test_adopt.py`: `--propose` writes the proposed profile and answers record and not the profile; `--answers` on the prototype's answers writes the prototype's profile; a `needs-human` line refuses replay | `cli.py` argument parser; `wizard.propose()`, `wizard.replay()`; `ScriptedInterview` promoted | The two files for both personas, replayed by CI |
| 2.2 | R10, code 13, 14, 17 | `tests/test_install_and_check.py`: exit codes per `DR-49`; `WARN` exits 0; a missing directory, a file, and an uninstalled repository each get their own message; `KeyboardInterrupt` prints one line and keeps the draft | `cli.py`, `check_conformance.main`; `--format json|sarif` | A SARIF file validated against the 2.1.0 schema |
| 2.3 | R10 `doctor` | `tests/test_install_and_check.py`: `doctor` reports Python and pip, `core.hooksPath` at every scope, terminal, venv on `PATH`, vendored digest; exits non-zero on a problem | `surfaceplate/doctor.py`; `--online` guarded | Run on this machine, whose global hooks path is the case that stopped the stranger install |
| 2.4 | code 7, 12 | `tests/test_scaffold.py`: files created before a later failure are reported; a parent that is a file is named as such | `wizard.run` reports scaffold results on any exception; `scaffold.write` catches `FileExistsError` around `open` only | Both in a scratch copy |
| 2.5 | F-N, F-O / `F70`, `F71` | `tests/check_code_registers.py`: every relative link in `README.md` and `INSTALL.md` resolves in this repository and in an installed checkout; the version line equals `surfaceplate/VERSION`; gates and controls per level in the documents equal `catalogue`; every `SP` code the checker emits is catalogued | The bounded README pass; `INSTALL.md` corrections; the six `F-O` corrections in `core/`, each a one-line edit with the authority named; the `SP` catalogue generated | The clean-container job in `.github/workflows/` running every documented command, with a global hooks path set |
| 2.6 | F-O Actions claim | — | **Done 2026-09-02 (`H10`):** the maintainer showed the organisation policy, Actions enabled for all repositories; the README wins and `PREREQUISITE_GATES.md` is rewritten; `F71` closed | The maintainer's statement, dated |

### Phase 3 — `ACT-046`

Work packet: objective, the tests look at what the adopter sees, the registers cannot
contradict themselves, and the schema records what is asked; in scope, R6, R9, R12, F-P, code
items 16, 18, 19, F55's habit; owning files, `tests/test_adopt_snapshots.py` (new),
`tests/__snapshots__/`, `tests/check_code_registers.py`, `surfaceplate/schemas/application-profile.schema.yaml`,
both examples, `surfaceplate/templates/application-profile.yaml`, `pyproject.toml` (test extra),
`.github/workflows/standard-self-check.yml`, `CLAUDE.md`; risk level 3; escalation, any
`--snapshot-update` whose cause is not written down.

| # | Closes | Test first | Change | Evidence |
|---|---|---|---|---|
| 3.1 | R6 | every screen snapshot at 80×24, including a gates list with a focused status; the suite prints its count | `tests/test_adopt_snapshots.py`; the workflow's "every step ran" loop gains one row; `CLAUDE.md` says thirteen | The suite seen to fail on a one-character stylesheet change |
| 3.2 | R6 budget | `test_budget`: fields presented before the review ≤ 12 on the two fixtures; the gate list counted separately | Fixtures checked in as the prototype used them | The measured numbers, recorded |
| 3.3 | F-P / `F72` | `check_code_registers.py`: body status equals index status for every `F` code | Fix the ten contradictions as the check dictates, one at a time, each with its reason | The check seen to fail on a deliberately contradicted scratch copy |
| 3.4 | R9, code 18 / `F77` | `validate_contracts.py`: the optional fields validate present and absent; the two reliance fields round-trip | Schema, both examples, template, `sections.build_risk` | — |
| 3.5 | code 16, 19 | `tests/test_render.py`: `human_roles: null` renders `[]`; an enum value with a newline is refused | `sections.build_wrap`; `render` routes enums through `_scalar` | — |
| 3.6 | F55 habit, R12 | — | Docstrings touched in this phase reduced to current behaviour plus a pointer; the rest as they are touched | — |

---

## 5. Findings, drafted for `org/FINDINGS.md`

Index rows first, then one body each in the register's own form. Status on recording is `Open`
for all; each closes by the activity named.

| Code | Title | Severity | Closes by |
|---|---|---|---|
| F59 | Every undecided gate's status radio is invisible at every terminal size: `.chip-row { height: 1 }` leaves no row for Textual's bordered `RadioSet` | high | `ACT-043` |
| F60 | The defaults route discards its gate proposals: `GatesScreen` is built without `initial`, and the "N more" count excludes what it will re-ask | high | `ACT-043` |
| F61 | Discovery proposes the framework's own installed files and CI step as the adopter's preconditions, and the checker passes them | high | `ACT-044` |
| F62 | The profile header asserts every value was typed by a human above canned rationales, computed dates and derived text | high | `ACT-044` |
| F63 | A real profile whose prose mentions "replace-me" is mistaken for the template and overwritten without a prompt | critical | `ACT-043` |
| F64 | `validators.check` passes any non-string, so an unpressed radio set and a blank dropdown commit; one path ends in a black screen, the other in an unactionable `KeyError` | high | `ACT-043` |
| F65 | A placeholder is accepted at the field and refused at the review, where nothing but cancel works, and a resumed draft lands on the same refusal | medium | `ACT-044` |
| F66 | The wizard accepts dates and paths the checker rejects, so a profile can pass the wizard and fail its first check | medium | `ACT-044` |
| F67 | The 80×24 pass looked at the wrong screens: the level options below the fold, help text unstyled and flush, off-state controls near-invisible, labels and text areas clipped | medium | `ACT-043`, `ACT-044` |
| F68 | Quitting at the resume prompt deletes the draft, and the prompt's heading is swallowed as markup | medium | `ACT-043` |
| F69 | The route screen says the rest is four gates while the next screen says all nineteen | low | `ACT-044` |
| F70 | The front door: two incompatible install paths, a stale version line, two dead links, a pointer to an uninstalled file, and a global hooks path that stops the first command undocumented | medium | `ACT-045` |
| F71 | The standard's documents contradict themselves on what is checked, which principle limits a tool, whether Actions is enabled, how many gates are asked, and which evidence labels to use | medium | `ACT-045` |
| F72 | Ten findings say Open in the body and Closed in the index, and `check_code_registers.py` never compares status | low | `ACT-046` |
| F73 | Every `action_cancel` is unreachable: Textual's priority quit binding fires first | low | `ACT-043` |
| F74 | A validation error is erased by the focus move that reports it | medium | `ACT-043` |
| F75 | Candidates are capped at 200 before any gate ranking, so a large `docs/` pushes the register out; the comment says the opposite | high | `ACT-044` |
| F76 | Resuming a draft that chose the defaults route never offers defaults again | medium | `ACT-044` |
| F77 | Hygiene: non-atomic profile write; a draft with the wrong shape or stale ids kills the run; non-UTF-8 paths quoted; `is_empty` never true; `human_roles: null` as `['None']`; unescaped enums; `KeyboardInterrupt` uncaught; `adopt` exits 0 on findings; the two reliance answers discarded | medium | `ACT-044`, `ACT-045`, `ACT-046` |

Each body follows the register's form: severity and status line; how it was found (the
adversarial review of 2026-09-02, with the image or command that showed it); what the code
does, with file and line; what it costs an adopter; the remedy, naming the activity. The review
report is the evidence reference for every one.

---

## 6. Human actions, drafted for `org/HUMAN_ACTIONS.md`

- `H1` is amended: "Do not run until `ACT-043` has merged; on the current build the gates
  screen cannot be completed (`F59`, `F60`)."
- `H9` (new): take decisions `D1` to `D4` and authorise `ACT-042` to `ACT-046`. Prepared: this
  plan. Taken in the review session on 2026-09-02 if section 2 records it so.
- `H10` (new): verify the organisation-level Actions claim in `PREREQUISITE_GATES.md:30-32`
  and say which document wins (phase 2, item 2.6).

---

## 7. The prompt for each implementing session

Give a fresh session exactly this, with the phase filled in:

> Work on activity `ACT-04N` in `/home/mps2210/github/surfaceplate`. Read `CLAUDE.md`,
> `AGENTS.md`, the installed rules and skills, then `org/REMEDIATION_PLAN.md` section 4 phase
> N and the findings it names in `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`. Use the
> `change` skill. Create branch `claude/act-04N-phase-N` from `main`. For each item: write the
> regression test first and show it failing, make the change, show it passing, and take and
> read the image the plan names where it names one. Do not change what is asked, written or
> proposed beyond what the plan and its decision records permit. Run all fourteen CI steps from
> `.venv/bin/python` before handing back and quote each count. Update `activity/register.md`
> and the findings this phase closes in the same commits. Open a pull request; do not merge.
> If anything in the plan does not match the code you find, stop and report the mismatch
> rather than improvising.

And for the reviewing session:

> Review pull request #N in `/home/mps2210/github/surfaceplate` with the `review` skill against
> `org/REMEDIATION_PLAN.md` phase N: every item present, every test seen to fail first, every
> image named in the plan taken and read, no test weakened, no snapshot regenerated without a
> recorded cause, every write inside `DR-47` to `DR-50`. Report; do not approve.

---

## 8. What this plan does not decide

Whether to publish to PyPI (`H8`); forge neutrality (`H7`); the documentation restructure and
`SETUP_GUIDE.md` (release plan item 8); the second cross-provider review and the independent
audit (`H3`, `H6`). None of them blocks phases 0 to 3.
