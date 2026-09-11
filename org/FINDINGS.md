# Findings — register and convention

The single register of findings against this repository and the framework it publishes. Before this
file existed, findings were scattered across three documents using two colliding `F1`–`F4`
sequences, plus an `F4` named only in prose and an `F5` with no heading of its own. This file is the
one place to look.

`assurance_findings` — *"Limitations must be recorded rather than smoothed away"*
(`core/CONFORMANCE_LEVELS.md:61`) — is one of the controls this framework requires of others at the
`full` level. Until this file existed the publisher did not implement it. Creating the register did
not by itself discharge that control: per `core/CONFORMANCE_LEVELS.md:73-76`, a declaration without
an invoked check is not enforcement. That gap closed with `DR-13` item 0 — this repository now
carries an application profile declaring `assurance_findings` as met, above the floor its level
obliges, and `check_conformance.py` runs against it in CI.

---

## Numbering convention

> `F<n>`, sequential, never reused. The register assigns a new number **only** to a finding first
> raised here. A finding that originated elsewhere keeps its original code, is cited
> document-qualified, and is never renumbered.

**Why not renumber.** Two constraints make renumbering the wrong answer, not merely the harder one.
`org/decisions/README.md:74-77` explicitly freezes `DR-5`: *"It is left as written — its severity
assessments and its raw evidence are the historical record of what was found at `v0.11.0`, and
rewriting them would destroy the record rather than update it."* And the live `F1`–`F5` codes are
cited in `DR-5`, `DR-6`, `DR-9`, `CHANGELOG.md`, `tests/validate_contracts.py:26` and
`tests/test_install_and_check.py:152`. Renumbering breaks every one of those citations and gains
nothing; namespacing the live series breaks the same citations for a cosmetic tidy.

So the collision is resolved by **qualification, not renumbering**: a bare `F<n>` always means the
live series indexed below. The historical series are always cited with their document prefix.

**Codes that are not findings, listed so nobody merges them later:**

| Namespace | What it is |
|---|---|
| `SP<n>` | Checker *output* codes emitted at runtime against an adopting repository — not durable records with severity or lifecycle. `DR-8.md:64`. The exact space is declared below, and checked. |
| `DR-<n>` | Decision records. `org/decisions/README.md`. |
| `ACT-<n>` | Activities. `activity/register.md`, which begins 2026-08-31 and records why earlier work being unregistered is not a gap. |

### The `SP` code space, declared

`tests/check_code_registers.py` parses the block below and compares it against the codes
`scripts/check_conformance.py` actually emits. Prose alone is what allowed this very section to
state, until 2026-08-31, that the space ended at `SP043` — after `SP046` and `SP047` had been
added and while the person adding them was editing this file.

```text
emitted:  SP001-SP035, SP037-SP043, SP046-SP060
gap:      SP036
reserved: SP044-SP045
```

`SP036` is a deliberate gap (`DR-8`). `SP044` and `SP045` are reserved by `DR-11.md:49` and are
emitted by nothing until a generator exists; the check asserts they stay unemitted, so a
reservation cannot quietly become a code in use. It also asserts the space has no **undeclared**
hole — the defect `DR-8` originally found, where `SDS036` sat documented-but-unimplemented across
an unknown number of releases with nothing noticing.

---

## Status convention (`DR-86`)

Three states, because two could not answer the question this register exists for.

| Status | Means | Example |
|---|---|---|
| **Open** | Outstanding. Work is pending and someone can do it | `F6` |
| **Accepted** | Decided, no action pending, **and the condition persists** | `F55`, `F131` |
| **Closed** | Fixed. The condition is gone | everything else |

**Why `Accepted` exists.** `Open` overstates a decided limitation — it implies work outstanding,
and a reader scanning for what to do next is misled. `Closed` understates it — in the index column
an accepted, still-shipping CVE reads exactly like a defect that was repaired. Neither answers
*"what is still wrong here?"*, which is the only question this file exists to answer, and
`CONTROL_PRINCIPLES.md:7` is explicit that limitations are recorded rather than smoothed away.

**An `Accepted` finding must say what would reopen it**, or it is an abandonment wearing a
decision's clothes. `tests/check_code_registers.py` refuses one that does not.

**This is this register's own convention, not the standard's.** `assurance_findings` is a
pattern-A control: the checker requires the register to exist, be tracked, be non-empty and carry
no placeholder, and never reads its contents. No adopter inherits these three words. Whether the
standard should prescribe them is a separate question and is not answered here.

---

## Live register

| ID | Title | Severity | Status |
|---|---|---|---|
| F1 | Test suite pass conditional on an unstated environment fact | high | Closed — v0.13.0 |
| F2 | Documented install line fails on a PEP 668 interpreter | medium | Closed — v0.13.0 |
| F3 | `validate_contracts.py` reported no executed-check count | low | Closed — v0.13.0 |
| F4 | Namespace rule and schemas drifted; the test could not detect it | not assessed | Closed — v0.12.0 |
| F5 | Three spellings of the organisation identifier; one does not resolve | medium | Closed — corrected, verified live |
| F6 | Every integrity anchor sits inside the boundary being checked | high | **Open** |
| F7 | `adoption.framework_digest` is never checked against anything | medium | Closed — `SP048`/`SP049`, `DR-14` |
| F8 | The CI detector is inside the artefact it protects | medium | Closed — ruleset applied and demonstrated |
| F9 | Remediation text names no pinned version | low | Closed — text scoped, installer reports upgrades |
| F10 | The producer evidence record describes an artefact that no longer exists | medium | Closed — `DR-21` |
| F11 | Nothing checks finding-code uniqueness or contiguity | low | Closed — `tests/check_code_registers.py` |
| F12 | Source and vendored checker copies can diverge, and nothing detects it | medium | Closed — `DR-20` |
| F13 | A wired CI check can never have run, inside a green pipeline | medium | Closed — requirement shipped to adopters |
| F14 | The placeholder heuristic cannot distinguish notation from an unfilled template | medium | Closed — `DR-17` |
| F15 | Two shipped templates were undetectable as templates | medium | Closed — obligation shipped; detection still not possible |
| F16 | Placeholder detection cannot separate mentioning a token from containing one | low | Closed — `DR-22`, by declaration |
| F17 | The identifier check reads every GitHub URL as a claim about this organisation | low | Closed — declared third parties |
| F18 | Inherited product and methodology names throughout the public tree | medium | Closed — redacted, disclosed |
| F19 | A licence decision recorded in another repository, never implemented in this one | medium | Closed — `DR-24` |
| F20 | A control is checked against itself, never against reality | high | Closed — all 9 controls checked; `DR-26` completes pattern C |
| F21 | `dependency_lock` declared with nothing pinned, and CI not recording what it used | medium | Closed — `pyproject.toml`, `SP051` |
| F22 | A deferral's revisit date was required to exist and never read again | medium | Closed for deferrals — `SP054`; **open** for gate exceptions |
| F23 | A drift guard matched on line shape rather than on the thing it guards | medium | Closed — anchored to the block; the false green constructed and run |
| F24 | A schema clause that could never add an obligation, grading the wrong axis | low | Closed — removed; `materiality` grades approval, not completeness |
| F25 | Declaring a placeholder-scan exemption made the profile fail the placeholder scan | medium | Closed — the exemption's own rationale is excluded; found in Plyego |
| F26 | `SP032`'s placeholder remedy was wrong for 17 of 19 gates and named no remedy | low | Closed — generic wording that names the exemption route |
| F27 | The installer forbade what the standard permits: no way to adopt without the hook | high | Closed — `--no-hooks`, recorded and announced |
| F28 | `SP038` accepted any pre-commit hook as satisfying a `local_hook` claim | high | Closed — the active hook is compared against the one installed |
| F29 | The agent instructions the framework ships are not read by the agent that uses it | high | Closed — emitted per agent; surfaceplate finally subject to its own |
| F30 | The history audit resolves a precondition by its current path, so a rename falsifies the whole history | medium | Closed — `ACT-030`; the audit follows renames, and says which chain it followed |
| F31 | The history audit ran against a depth-1 clone in CI and reported nothing wrong | high | Closed — `fetch-depth: 0`, and a shallow clone is now reported |
| F32 | The wizard invented rationale text for baseline controls and auto-masked UI gates | high | Closed — `ACT-022`, routed through `Prompt`; found by the review `ACT-021` requested |
| F33 | An all-digit commit SHA silently fails a gate exception, and the lesson never propagated | medium | Closed — `ACT-024`; template, checker message, and test all fixed |
| F34 | The release manifest could name a file that exists on no machine but the one that built it | high | Closed — `ACT-024`; `payload_files()` now intersects against `git ls-files` |
| F35 | A refusal named three routes; only one was a route a reader could actually take | medium | Closed — `ACT-025`; scope named, each route made a real step |
| F36 | A hand-built flow list escaped each item for the wrong YAML context, and lost a real ~20-minute session | high | Closed — `ACT-026`; `render.py` dumps the whole list, not each item alone |
| F37 | An interface was verified structurally and never looked at, so six rendering defects passed 87 green checks | high | Closed — `ACT-028`; rendering asserted as named properties over the compositor's own lines |
| F38 | A multi-line answer could not be written, and four interface faults made the wizard error-prone | high | Closed — `ACT-029`; block scalars, and structural answers picked from the repository |
| F39 | The gate catalogue never received the repository scan, so a completed adoption produced seven unusable gates | high | Closed — `ACT-031`; the app scans once, and the join now compares field kind |
| F40 | The wizard proposed `README.md` as the precondition for `work_registration`, producing a gate that passes while guarding nothing | high | Closed — `ACT-032`; a proposal now comes only from a candidate that actually matched the gate |
| F41 | Every multiselect drew a ticked box on every row; `_StatefulToggle` sets instance attributes and `SelectionList` reads them off the class | medium | Closed — `ACT-032`; `VisibleSelectionList` rewrites the button from each row's real state |
| F42 | Gate explanations were forced onto one line and cut mid-sentence, with the declared ellipsis never rendering | medium | Closed — `ACT-034`; the summary is budgeted in text and carries its own `…` |
| F43 | The gate screen counted a gate as answered when it merely had a status, reporting `1 of 1 answered` with every field empty | medium | Closed — `ACT-034`; it now uses the completeness predicate that already existed |
| F44 | A precondition dropdown offered twelve unrelated files as candidates when none matched the gate | low | Closed — `ACT-034`; the help says when nothing matched |
| F45 | The step counter had no entry for `route`, gave two sections the same number, and claimed seven steps for ten sections | low | Closed — `ACT-034`; derived from `SECTION_ORDER` |
| F46 | The conformance-level screen span in an unbounded redraw loop whenever the caret did not start at index 0 | high | Closed — `ACT-034`; prompts are replaced in place instead of cleared and re-added |
| F47 | A repository adopted on a day it already had commits reports a gate violation it cannot clear: the artefact is created today, `effective_from` binds by DATE, and `SP033` forbids a future date | medium | Closed — `ACT-035`; `effective_from` accepts an instant, so adoption binds from the moment |
| F48 | The prerequisite history audit's window slid forward with the clock: `git log --since=<bare date>` means that date at the CURRENT TIME, so a violation visible in the morning was gone by evening | high | Closed — `ACT-035`; a date-only `effective_from` resolves to midnight explicitly |
| F49 | `DR-23`'s standing policy on the former organisation has no automated check, and cannot have one that carries the token | low | Closed — 2026-09-02, by the maintainer's own search (`H5`); see the body |
| F50 | The adversarial-review hand-off command referenced a file deleted three packets earlier, so item 9 could not have been run as documented | medium | Closed — `ACT-037`; the command is corrected, guarded, and reproduces the list the prompt declares |
| F51 | The wizard set `effective_from` itself, contradicting the binding rule that names that field as a human decision — and silently chose the narrowest audit window the rules permit | high | Closed — `ACT-038`; asked again, and the rule made precise about what the tool may supply |
| F52 | `CONFORMANCE_LEVELS.md` claimed both that two baseline controls are unchecked and that nothing is declared-only | medium | Closed — `ACT-038`; the absolute claim was the false one |
| F53 | An adopter could not tell a machine-verified control from a declared one by reading their own profile; `VERIFIED_CONTROLS` was itself incomplete | medium | Closed — `ACT-038`; each control is labelled from the checker's own set, and the set corrected |
| F54 | The review packet omitted the artefacts its own question depended on, and asked a text-only reviewer to compute a SHA-256 digest | medium | Closed — `ACT-038`; seeds attached, and the recomputation scoped to a reviewer that can execute |
| F55 | Narrative docstrings can drift from the code beneath them, and twice did | low | Accepted — `ACT-102`, 2026-09-11. Recorded as a habit rather than remedied; not mechanically enforceable, so nothing is pending |
| F56 | Field labels were clipped at the design width with no ellipsis — 28 of them, including every control's rationale prompt | medium | Closed — `ACT-039`; labels wrap, and the property is asserted of the widget rather than the screen |
| F58 | Seven skill documents install only to `.github/skills/`. `AGENTS.md` calls their gates "not optional" — and Claude Code loads `.claude/skills/`, which no adopter received | high | Closed — `ACT-041`; `DR-30`'s emitter pattern applied to the half it had missed |
| F57 | The README, `INSTALL.md` and the tool itself instruct an adopter to `pip install surfaceplate`, which 404s — and the README repeats the binding-rule claim `F51` proved false | high | Closed — `ACT-040`; every live instruction names a command that was run before it was written down |

| F59 | Every undecided gate's status radio is invisible at every terminal size: `.chip-row { height: 1 }` leaves no row for Textual's bordered `RadioSet` | high | Closed — `ACT-043`; `.chip-row` is `height: auto` with no border or padding, and `tests/test_render.py` reads the three options off the screen at 80×24 |
| F60 | The defaults route discards its gate proposals: `GatesScreen` is built without `initial`, and the "N more" count excludes what it will re-ask | high | Closed — `ACT-043`; `GatesScreen` takes `initial` and the app passes the seeded proposals; the "N more" figure is asserted equal to what the remaining screens present unfilled at all three levels |
| F61 | Discovery proposes the framework's own installed files and CI step as the adopter's preconditions, and the checker passes them | high | Closed — `ACT-044`; discovery excludes the install record's files, the profile and the installed workflow's steps, the field refuses them, and `SP059` reports them on any profile |
| F62 | The profile header asserts every value was typed by a human above canned rationales, computed dates and derived text | high | Closed — `ACT-044`; the header states what the provenance record contains, and the record beside the profile carries every value's origin, read by `tests/test_provenance.py` |
| F63 | A real profile whose prose mentions "replace-me" is mistaken for the template and overwritten without a prompt | critical | Closed — `ACT-043`; the guard looks for the token in the template's identifying scalars, not the byte stream, and both directions are asserted in `tests/test_adopt.py` |
| F64 | `validators.check` passes any non-string, so an unpressed radio set and a blank dropdown commit; one path ends in a black screen, the other in an unactionable `KeyError` | high | Closed — `ACT-043`; `None` is blank in `validators.check`, a choice must be one of its choices at commit, and both paths are refused at the field in `tests/test_adopt_tui.py` |
| F65 | A placeholder is accepted at the field and refused at the review, where nothing but cancel works, and a resumed draft lands on the same refusal | medium | Closed — `ACT-044`; every string validator refuses a placeholder at the field, the review's error names the line and `Ctrl+E` goes to it, and "write it" is hidden while an error stands |
| F66 | The wizard accepts dates and paths the checker rejects, so a profile can pass the wizard and fail its first check | medium | Closed — `ACT-044`; `surfaceplate/rules.py` holds the rules once, both sides import it, and `tests/test_adopt.py` refuses each input and maps every `SP` code to a validator or a named exemption |
| F67 | The 80×24 pass looked at the wrong screens: the level options below the fold, help text unstyled and flush, off-state controls near-invisible, labels and text areas clipped | medium | Closed — `ACT-049`; see the body |
| F68 | Quitting at the resume prompt deletes the draft, and the prompt's heading is swallowed as markup | medium | Closed — `ACT-043`; a quit cancels the run with the draft kept, and the four bracketed headings are `markup=False`, both asserted in `tests/test_adopt.py` and `tests/test_render.py` |
| F69 | The route screen says the rest is four gates while the next screen says all nineteen | low | Closed — `ACT-044`; there is no route screen |
| F70 | The front door: two incompatible install paths, a stale version line, two dead links, a pointer to an uninstalled file, and a global hooks path that stops the first command undocumented | medium | Closed — `ACT-045`; the bounded README and `INSTALL.md` pass, `check_code_registers.py` resolving every link and path and pinning the version, and `scripts/front_door.sh` run on a clean container with a global hooks path |
| F71 | The standard's documents contradict themselves on what is checked, which principle limits a tool, whether Actions is enabled, how many gates are asked, and which evidence labels to use | medium | Closed — five of six by `ACT-045`; the Actions claim by `H10`, 2026-09-02; see the body |
| F72 | Ten findings say Open in the body and Closed in the index, and `check_code_registers.py` never compares status | low | Closed — `ACT-046`; the ten status lines reconciled with a reason each, and `check_code_registers.py` compares body and index status for every finding |
| F73 | Every `action_cancel` is unreachable: Textual's priority quit binding fires first | low | Closed — `ACT-049`; see the body |
| F74 | A validation error is erased by the focus move that reports it | medium | Closed — `ACT-043`; the error is held on the screen until the next commit and re-shown on every focus move, asserted after six pauses in `tests/test_adopt_tui.py` |
| F75 | Candidates are capped at 200 before any gate ranking, so a large `docs/` pushes the register out; the comment says the opposite | high | Closed — `ACT-044`; the scan keeps everything and each field cuts to `SHOWN` after ranking, asserted with 300 documents ahead of the register in `tests/test_discover.py` |
| F76 | Resuming a draft that chose the defaults route never offers defaults again | medium | Closed — `ACT-044`; the draft carries every answer with its origin and which stages are done, and a resumed run lands on the review with its proposals, asserted in `tests/test_adopt_tui.py` |
| F77 | Hygiene: non-atomic profile write; a draft with the wrong shape or stale ids kills the run; non-UTF-8 paths quoted; `is_empty` never true; `human_roles: null` as `['None']`; unescaped enums; `KeyboardInterrupt` uncaught; `adopt` exits 0 on findings; the two reliance answers discarded | medium | Closed — `ACT-049`; see the body |
| F78 | `adopt` validates against the adopter's installed schema but writes the tool's own shape, and notices the mismatch only at the review, in the validator's words | high | Closed — `ACT-048` (`DR-51` (1)); see the body |
| F79 | A schema refusal on the review quotes the validator instead of naming the profile line and the key that writes | low | Closed — `ACT-048` (`DR-51` (6)); see the body |
| F80 | The gate artefact choices carry no explanation of what each file is, what adopting it costs or what it buys | high | Closed — `ACT-048` (`DR-51` (4)); see the body |
| F81 | No opening screen: the wizard starts at the first question with no name, version, owner or account of what it will do | low | Closed — `ACT-048` (`DR-51` (2)); see the body |
| F82 | The wizard explains its fields, not the framework: a reader who does not know Surfaceplate cannot adopt it from the wizard alone | high | Closed — `ACT-048` (`DR-51` (3)); see the body |
| F83 | The scanner workflow is proposed without the checker's own test: discovery offered `ci.yml`, which never mentions gitleaks, while two workflows that run it were not proposed | high | Closed — `ACT-048` (`DR-51` (5)); see the body |
| F84 | An artefact is proposed on a keyword match with no relevance floor and without the checker's content rules: a work inventory quoting `TODO` and `TBD` was proposed as the authority map | high | Closed — `ACT-048` (`DR-51` (5)); see the body |
| F85 | The closing report says the checker "passes" on a graced WARN with findings | medium | Closed — `ACT-048` (`DR-51` (6)); see the body |
| F86 | A hand edit to the profile after the write leaves the provenance record asserting the old origin; nothing records a post-write edit | low | Closed — `ACT-052` (`DR-54`); see the body |
| F87 | A seedable artefact is created only when the field is left blank, and nothing says so: the dropdown forces a choice among existing files | medium | Closed — `ACT-052` (`DR-54`); see the body |
| F88 | A control's implementation reference offers only files whose names carry fixed words, from fixed directories; a repository with the file elsewhere gets a text box, and one without it has no path to create one | medium | Closed — `ACT-052` (`DR-54`); see the body |
| F89 | The opening screen is text only; the maintainer asked for a mark | low | Closed — `ACT-051` (`DR-53`); see the body |
| F90 | A render test read the screen before the deferred scroll had run, and turned `main` red on the runner while passing locally | low | Closed — `ACT-051`; see the body |
| F91 | The conformance level barely changes the screens that follow: every gate is listed at standard and full alike, and the above-floor controls read the same, so the level tells the reader nothing | medium | Closed — `ACT-055` (`DR-56`); see the body |
| F92 | `SP034` prints an instant as a bare date, so "moved forward" reads as the same date twice; whether a later instant on the same day is a forward move at all is undecided | low | Closed — message fixed at `ACT-054`; the rule kept as it is by `DR-60`, 2026-09-02 |
| F93 | A record-directory control's reference is proposed from any directory holding YAML: four controls were proposed `config/accounts` and the checker rejected every record in it | high | Closed — `ACT-054`; see the body |
| F94 | An archived document is proposed as a gate's artefact on a keyword match: two gates were proposed files under `docs/archive/` | medium | Closed — `ACT-054`; see the body |
| F95 | A focus-driven scroll is animated, and the scrollbar keeps a fractional thumb position from the animation's last frame, so a golden of a scrolled screen differed one run in four | low | Closed — `ACT-055`; see the body |
| F96 | With the gates beyond the floor folded, Ctrl+S refused by naming a folded gate: an optional gate read as required | medium | Closed — `ACT-056` (`DR-57`); see the body |
| F97 | At `essential` the above-floor list offered `documentation_authority`, and a profile declaring it fails `SP052` on its first check: the wizard wrote a combination it knew the checker faults | medium | Closed — `ACT-057` (`DR-59`); see the body |
| F98 | A run cancelled after the scaffold stage and resumed never created the adoption decision record: the profile named `DR-0001` and the sidecar said "created" for a file that did not exist | high | Closed — `ACT-057`; see the body |
| F99 | `--propose` marked every above-floor control's rationale and reference `needs-human`, so a human had to invent lines for controls they never declared before `--answers` would write | medium | Closed — `ACT-057`; see the body |
| F100 | `--edit` applied no field validator, so an artefact edited to an untracked path was written and failed `SP032` on the next run | medium | Closed — `ACT-057`; see the body |
| F101 | A run that fails after the scaffold has written its seeds leaves them on disk and reports them rather than removing them (pass-2 CRIT-01) | medium | Closed — `ACT-059`, 2026-09-02, the maintainer having chosen the rollback (`H13`); see the body |
| F102 | A seed satisfies `SP032` on the day it is written, so a repository can pass every seeded gate with no practice behind it (pass-2 CRIT-02; the risk `DR-43` states) | medium | Closed — `ACT-059`, 2026-09-03, the maintainer having chosen the seed advisory (`H13`); see the body |
| F103 | `--answers` writes every proposal the human left standing, so a record completed by filling only the needs-human lines carries the framework's example rationales under the adopter's name (pass-2 MAT-01) | medium | Closed — `ACT-059`, 2026-09-03, the maintainer having chosen the acceptance line (`H13`); see the body |
| F104 | The schema's `effective_from` pattern admits impossible dates and a fraction without seconds; the checker rejects them, so the pattern documents a form it does not enforce (pass-2 MAT-02) | low | Closed — `ACT-059` (`DR-63`), 2026-09-03; see the body |
| F105 | `adoption_status: complete` needs no rationale and no evidence reference to validate (pass-2 MAT-03) | low | Closed — `ACT-059` (`DR-63`), 2026-09-03; see the body |
| F106 | This repository's own profile declares `agent_work_packets` required as a practice while deferring `work_contract` because the packets are not committed: two rationales that contradict each other (pass-2 MAT-04) | medium | Closed — `ACT-059`, 2026-09-02, approved by the maintainer (`H13`); see the body |
| F107 | The template test treats a profile as the untouched template when any one identifying scalar is still `replace-me`, so a half-completed profile can be overwritten (pass-2 MIN-01) | medium | Closed — `ACT-059`, 2026-09-02, authorised by the maintainer (`H13`); see the body |
| F108 | The wizard writes `notes: Blocking.` under the adopter's scanner without asking or verifying it (pass-2 MIN-02) | low | Closed — `ACT-059`, 2026-09-02, the maintainer having chosen to omit the note (`H13`); see the body |
| F109 | This repository's own profile mirrors two gate deferrals as `x-…-gate` control deferrals under `adoption.deferrals`, duplicating what `prerequisites` already records (pass-2 MIN-03) | low | Closed — `ACT-059`, 2026-09-02, approved by the maintainer (`H13`); see the body |
| F110 | This repository's own hand-written profile carries none of the checked/declared labels the wizard writes since `F53`, so its reader cannot tell a verified control from a declared one (pass-2 §7) | low | Closed — `ACT-059`, 2026-09-02, approved by the maintainer (`H13`); see the body |
| F111 | The reviewer holds the narrative docstrings and the size of the governance apparatus to be a maintenance risk and disproportionate for a CLI tool (pass-2 §9) | low | Closed — 2026-09-03, the maintainer keeping the practice (`H13`); see the body |
| F112 | The matrix's `advanced` case compared two profiles assembled seconds apart without normalising the scaffolded instant, and failed on the runner once | low | Closed — `ACT-057` follow-up, 2026-09-02; see the body |
| F113 | A validator check built "today at midnight UTC" and expected it to be in the past, which is false for the first hour of the day on a UTC+1 machine (the `F48` shape) | low | Closed — `ACT-059`, 2026-09-03; see the body |
| F114 | The audit hand-off stated the bundle's file count in four places and only one was checked, so three read "15" after the bundle grew to 27, and the full prompt still said "five" suites | low | Closed — `ACT-060`, 2026-09-03; see the body |
| F115 | The `v0.16.0` tag points at a tree 235 commits older than the commit published to PyPI as 0.16.0, with the manifest at a different path, so "check out the tag" yields a different framework anchor | medium | Closed — `H14` taken 2026-09-03: the `pypi/0.16.0` and `pypi/0.16.1` tags ratified; see the body |
| F116 | The README's front door said "no adopting repositories" after Plutos had adopted, and "does not install its own standard on itself" weeks after it did and passed | medium | Closed — `ACT-061`, 2026-09-03; see the body |
| F117 | `README.md` said "this is not published to PyPI yet" after `0.16.0` and `0.16.1` were both on the index | medium | Closed — `ACT-062`, 2026-09-03; see the body |
| F118 | `SECURITY.md` said the repository "is currently private" and that private vulnerability reporting "cannot be enabled" for it, weeks after the repository was made public | medium | Closed — `ACT-062`, 2026-09-03; see the body |
| F119 | Nowhere a user actually reads — the installer's Next steps, the post-`adopt` failure output, `INSTALL.md`'s two "Raise it" sentences, SP005's own remedy text — named an issue tracker, and no local, offline way to assemble a problem report existed | medium | Closed — `ACT-062`, 2026-09-03; see the body |
| F120 | The agent instructions are not graded by conformance level, while every control is | medium | Closed — `ACT-068` (`DR-69`), 2026-09-08; see the body |
| F121 | `owner_role` and `reviewer_role` are required of a solo adopter, for whom both are constant | medium | Closed — `ACT-068` (`DR-69`), 2026-09-08; see the body |
| F122 | The installer creates a Copilot instruction channel unconditionally, including in repositories that do not use Copilot | low | Closed — `ACT-066` (`DR-67`), 2026-09-08; see the body |
| F123 | `authority.md` names one vendor's file as the place the authority hierarchy must be stated | medium | Closed — `ACT-066` (`DR-67`), 2026-09-08; see the body |
| F124 | The checker verifies that an install is unedited and has no notion of whether it is current | high | Closed — `ACT-075` (`DR-72`), 2026-09-08; see the body |
| F125 | No adopter-facing precedence rule exists between this standard and a co-resident governance system | medium | Closed — `ACT-068`/`ACT-069` (`DR-69`, `DR-71`), 2026-09-08; see the body |
| F126 | A recorded `effective_from` instant can sit ahead of the clock the checker reads moments later, so a gate created seconds ago reads as dated in the future | medium | Closed — `ACT-070`, 2026-09-08; see the body |
| F127 | `SECURITY.md` went stale a second time about the same feature: it said private vulnerability reporting was *"not enabled today"*, citing an API check, after the setting had been turned on | medium | Closed — `ACT-070`, 2026-09-08; see the body |
| F128 | A skill shipped to every adopter pointed at `activity.instructions.md`, a filename the twelve-topic restructure stopped writing and a Copilot-only emitted name before that; nothing checked what the payload says about itself | medium | Closed — `ACT-073`, 2026-09-08; see the body |
| F129 | `F123`'s ruling was applied to the document it was found in and nowhere else: Topic 7 still told every agent that stack-specific commands and test areas belong in `copilot-instructions.md` | medium | Closed — `ACT-073`, 2026-09-08; see the body |
| F130 | The same dependency version is pinned in five places — `pyproject.toml`, two workflows, the payload's copy of one of them, and `INSTALL.md` — and nothing compared them, so a dependency change was judged green by a CI run that installed the old version | high | Closed — `ACT-074`, 2026-09-08; see the body |
| F131 | `CVE-2025-71176` in pytest cannot be remediated within the pinned test set: `pytest-textual-snapshot` pins `syrupy==4.8.0`, which caps `pytest<9.0.0`, and the fix is only in `9.0.3` | medium | Accepted — the maintainer took route (1) at `H21`, 2026-09-08; recorded as `Accepted` by `ACT-102`. **The CVE is still shipped**; the periodic check is `H26` |
| F132 | A repository with no dependency manifest of any kind cannot produce a conformant profile at any level, and the wizard dead-ends on the first screen: `dependency_lock` is the sole `essential` floor control and `SP051` requires it to name a real tracked file | high | Closed — `ACT-078` (`DR-73`), 2026-09-09; see the body |
| F133 | The history audit accepts the installed **seed** as a former name of any artefact `adopt` scaffolded from it, so deleting the artefact never registers as a gate violation — and the seed can never be deleted | high | Closed — `ACT-080` (`DR-74`), 2026-09-09; raised as `PW-01`; confirmed at `HEAD` by the maintainer's session |
| F134 | A refused `--answers` replay writes `.standards/adopt-draft.json` while printing *"Nothing was written"*, and that draft then makes a corrected record fail with the old value's error | high | Closed — `ACT-080` (`DR-74`), 2026-09-09; raised as `PW-02`; confirmed on the sweep's controlled isolation |
| F135 | `pyproject.toml` is offered and proposed as a dependency **lock** file, and `SP051` accepts any tracked non-empty file as one — a manifest is not a lock | high | Closed — `ACT-080` (`DR-74`), 2026-09-09; raised as `PW-03`; confirmed at `HEAD` |
| F136 | The pathway sweep's remaining fifteen findings (`PW-04` to `PW-18`), held as one entry so none was lost and none was given a verified finding's status before it had been reproduced here | medium | Closed — `ACT-094`/`ACT-095`, 2026-09-11. All adjudicated: eight confirmed as `F148`–`F156`, `PW-18` as `H25`, two refuted and issued no code |
| F137 | The natural completion of a shipped template is invalid: an unquoted `YYYY-MM-DD` parses as a YAML date and every schema here says `type: string` — it defeats the FAQ's own remedy for a bypassed gate, and `adoption_date` for anyone filling the profile by hand | medium | Closed — `ACT-081` (`DR-75`), 2026-09-09; see the body |
| F138 | There was no way to remove the standard from a repository — no command, no flag, no document | medium | Closed — `ACT-081` (`DR-75`), 2026-09-09; see the body |
| F139 | `adopt --edit` against the installer's template profile ended in `KeyError: 'scanner'`, exit 4 — a crash where a refusal belongs | medium | Closed — `ACT-083` (`DR-78`), 2026-09-09; see the body |
| F140 | `adopt --edit` without `--because` was accepted and recorded with boilerplate that reads like a reason, and the CLI said the change was recorded *"with the reason"* | medium | Closed — `ACT-083` (`DR-78`), 2026-09-09; see the body |
| F141 | Installing an older tool over a newer install announced *"an UPGRADE"*, and `doctor` printed two different installed versions in one run | medium | Closed — `ACT-083` (`DR-78`), 2026-09-09; see the body |
| F142 | `F132` returned through the door `DR-73` left open: `dependency_lock` stayed *offerable* above the floor on a repository with no manifest, and ticking it demanded a lock file that cannot exist | high | Closed — `ACT-085`, 2026-09-09; see the body |
| F143 | Ticking a control in the above-floor list never revealed the fields it makes required: the screen listened for every widget's change event except the multiselect's, so the wizard demanded a value for a field it did not show and no key could reach | high | Closed — `ACT-086`, 2026-09-09; see the body |
| F144 | Any CI step was proposed as the implementation of `deterministic_tests` and `contract_tests`: on the maintainer's walkthrough a **checkout** step was written into the profile as `discovered`, and the checker reported the control verified against it | high | Closed — `ACT-087`, 2026-09-09; see the body |
| F145 | `F144` fixed the proposal and not the profiles already carrying a bad one: the only real adopter had two controls credited to a checkout step and passed every run | medium | Closed — `ACT-088`, 2026-09-09; see the body |
| F146 | An upgrade leaves `framework_version` and `framework_digest` stale by construction, so every upgrading adopter is handed `SP048` and `SP049` and must hand-copy a 64-character digest | medium | Closed — `ACT-092` (`DR-81`), 2026-09-09; see the body |
| F147 | A dropdown of discovered candidates was the only answer a human could give, though nothing but the widget held that rule: the validator was always the real gate and a scripted adoption could name any tracked file. The list was also truncated 12-of-30 while claiming to be the finding | high | Closed — `ACT-093` (`DR-82`), 2026-09-09; see the body |
| F148 | `README.md`'s contributor block cannot be completed as written: its venv omits `textual`, so the suite it runs fails and `build_release.py` refuses to build | medium | Closed — `ACT-094`, 2026-09-11; see the body |
| F149 | `doctor` and `doctor --report` crash with `UnicodeEncodeError` on an ASCII stdout — and `doctor --report` is the command `SUPPORT.md` names for reporting a problem | medium | Closed — `ACT-094`, 2026-09-11; see the body |
| F150 | The answers record says what a gate artefact is and nothing about what a control's implementation reference is, though one wants a file and the other a CI step name; `F144` made adopters meet the unexplained field far more often | medium | Closed — `ACT-094`, 2026-09-11; see the body |
| F151 | Declining an agent channel left eight empty directories and reported the files as "no longer part of the standard" when they are still part of it | low | Closed — `ACT-094`, 2026-09-11; see the body |
| F152 | `uninstall` and `_prune_empty` sat below `install_standard.py`'s `__main__` block, so they are unbound when the file runs as a script — a `NameError` after one file had already been deleted | medium | Closed — `ACT-094`, 2026-09-11; see the body |
| F153 | `RECONCILIATION.md` claimed the standard owns `.github/instructions/*.instructions.md` as a glob; it owns twelve named files and seven named skills, and the adopter's own files were never at risk | low | Closed — `ACT-094`, 2026-09-11; see the body |
| F154 | Three documented things that were not true: `SP001`'s remedy named an internal script, the documented `pip install` resolves to `@main` rather than a release, and the install block did not say what to do when it stops on a global `core.hooksPath` | low | Closed — `ACT-094`, 2026-09-11; see the body |
| F155 | `RECONCILIATION.md`'s first command assumed a clone of this repository beside the adopter's; a pip adopter gets `No such file or directory` on step 1 | low | Closed — `ACT-094`, 2026-09-11; see the body |
| F157 | `SP038` reported a negative it could not establish: a fresh clone has no hook by construction, so every adopter claiming `local_hook` would have failed CI 30 days after install. `DR-74`'s rule, applied to the case `DR-74` missed | high | Closed — `ACT-096` (`DR-84`), 2026-09-11; answers `H24`; see the body |
| F162 | The built distribution declared no `readme`, so the PyPI project page would have rendered the summary line and then blank space — and `pyproject.toml` carried a comment asserting that PyPI rendered the README | medium | Closed — `ACT-103`, 2026-09-11; see the body |
| F163 | `requires-python = ">=3.9"` was **false**, not merely untested: `jsonschema==4.26.0` is a hard dependency requiring `>=3.10`, so the package could never install on 3.9 — and the wrong declaration gave the reader a worse error than the right one would have | medium | Closed — `ACT-104`, 2026-09-11. Raised `low`/`Accepted` hours earlier and reassessed; see the body |
| F174 | The agent recorded a public forum posting that never happened, in the one table whose entire purpose is that a drafted invitation cannot be mistaken for a sent one — from a one-word message read as confirmation rather than checked | medium | Closed — `ACT-111`, 2026-09-11; see the body |
| F173 | `DR-14` rejected PEP 740 attestations because *"key custody and a signing process are infrastructure"* — and trusted publishing has been producing them automatically, with neither, since `0.16.0`. The rejection's premise is void, no document says the attestations exist, and the review packet sent to two reviewers on 2026-09-11 omits them | medium | Open — `ACT-110` records it and qualifies `F6`; whether to ADOPT them is a decision (`H28`) |
| F171 | `DR-67` narrowed the payload to the chosen agent channels and left the conformance block's **prose** naming both vendors — so a repository installed with `--agents copilot` was told four times not to edit `.claude/rules/` and `.claude/skills/`, directories it does not have, in the one file every adopter reads first | medium | Closed — `ACT-107`, 2026-09-11; see the body |
| F172 | The `--agents` refusal said *"To install no agent instructions at all, do not install the standard"* — **which is false**: `AGENTS.md` and `.standards/topics/` are agent instructions and are installed whichever channel is chosen, as `DR-67` (3) states | low | Closed — `ACT-107`, 2026-09-11; see the body |
| F170 | `CLAUDE.md` gave the release ritual's trigger as "after changing anything the standard ships" — the payload — while the manifest covers **every tracked file outside a short excluded set**, `scripts/` and `tests/` included. Followed exactly, the instruction leaves the manifest stale, and CI then fails with every suite green | medium | Closed — `ACT-106`, 2026-09-11; see the body |
| F165 | `stack.builds_user_interface` could not be answered `yes` on the non-interactive route at all — the answers record told the reader to write it into the file and re-propose, and `--propose` rebuilds from the repository and discarded it — so a repository that builds an interface could not be adopted through `--propose`/`--answers` | high | Closed — `ACT-106`, 2026-09-11 (`DR-87`); see the body |
| F166 | `F47`'s remedy was applied at one of two sites: a gate binds from the instant of adoption when a scaffold created its artefact, and from that **midnight** when the adopter named one — so `F47`'s original symptom returned for the adopter who supplies their own artefacts, and the obvious correction is foreclosed by `SP034` | high | Closed — `ACT-106`, 2026-09-11 (`DR-87`); see the body. `F47` stays `Closed`; this is the half its closure did not cover |
| F167 | An answer written as a YAML list where one value belongs reached the profile assembly and failed with `KeyError: "no provenance rule reaches profile path 'baseline_controls.secret_hygiene.scanner.wired_in[0][0]'"` — exit 4, nothing written, and nothing in that sentence addressed to the adopter | medium | Closed — `ACT-106`, 2026-09-11; see the body |
| F168 | A gate naming the artefact **another** gate's accepted offer will create was refused with "Nothing exists at that path in this repository", for a path the same run was about to write — so the pairing `core/PREREQUISITE_GATES.md` recommends could not be completed in one pass | high | Closed — `ACT-106`, 2026-09-11; see the body |
| F169 | `.standards/seeds/` — the only escape from `F168`, and the material the wizard writes gate artefacts from — was named in no document an adopter receives | medium | Closed — `ACT-106`, 2026-09-11; see the body |
| F164 | `scripts/front_door.sh` wrote its stranger identity and its global `core.hooksPath` into the **invoking user's real `~/.gitconfig`**, then deleted the directory it had pointed the hooks at — so every git hook on the machine was silently skipped, and later commits in any repository without a local identity were authored by "A stranger" | high | Closed — `ACT-105`, 2026-09-11; see the body. The machine repair is `H27` |
| F161 | The gates screen rebuilt each `FieldSpec` by hand and dropped every field added since, and its `Ctrl+S` refusal was wiped by the next keypress — `F74`'s defect, fixed on the other screen only | medium | Closed — `ACT-099`, 2026-09-11; see the body |
| F160 | `SP047` read a `run:` block line by line, so a scan disarmed across continuation lines was invisible to the check built to find it — while a step that merely READ the scanner's report was reported as the scan command | high | Closed — `ACT-098`, 2026-09-11; see the body |
| F159 | `--repin` refused a profile that had not been written yet by listing six lines it does not write, so the command read as broken when the profile was simply unfinished | medium | Closed — `ACT-097`, 2026-09-11; see the body |
| F158 | The history audit's window was inclusive at second granularity, so a commit made moments BEFORE adoption was reported as crossing a gate that did not yet exist — and could never be remediated | low | Closed — `ACT-096`, 2026-09-11; decided at `H25`; see the body |
| F156 | No wizard-written profile ever claimed `local_hook`, so `SP038` and `DR-66`'s verification-by-effect could not fire for any adopter; a `--chain` install never declared the delegation it had deliberately chosen | medium | Closed for the chained case — `ACT-095` (`DR-83`), 2026-09-11; the wider case is `H24`; see the body |
Closed entries are indexed here and left in their original records; they are not restated.
`F1`–`F3` — `org/decisions/DR-5.md:53,75,87`, fixed per `CHANGELOG.md:490-508`.
`F4` — stated in prose at `org/decisions/DR-6.md:34-39`, never given a heading or a severity;
implemented by the release that named it. This register gives it an index entry without editing
`DR-6`.
`F5` — `org/decisions/DR-9.md:17-19,56-61`. **Closed.** The live instruction was corrected:
`INSTALL.md:29` now reads the declared `github-org`, and `git ls-remote` against it resolves while
the old spelling still returns a hard 404. Every remaining occurrence of the broken spelling is a
*quotation inside a record* — `DR-9` documenting the finding, and the exemption pairs in
`ORGANISATION.md` that permit those quotations. `tests/check_identifiers.py` verifies this on every
run rather than it being asserted here.

**What was never a defect, stated so it is not re-raised.** The three declared identifiers still
differ from one another — a GitHub slug, a URN authority segment, and a registered legal name. That
is three namespaces with different grammars naming one organisation, not drift. Each is declared in
`ORGANISATION.md`, each is checked against its own contexts, and `NAMESPACE.md` governs whether the
URN authority ever changes. `F5` was about a spelling that *resolved to nothing*, and that is fixed.

*This entry was itself stale until 2026-08-31,* asserting that `INSTALL.md:29` "still reads" the
broken URL long after it had been corrected. It is one of the three false statements this register
was carrying, and part of the evidence behind `F11` below.

---

## F6 — Every integrity anchor sits inside the boundary being checked

**Severity: high. Open.**

> **Precision added 2026-09-11 (`F173`), and the title is left as it stands because it is quoted in
> the published release notes and in the invitations already sent.** The title is now imprecise as
> written: since `0.16.0`, PyPI has held a Sigstore-signed PEP 740 attestation for every published
> artefact, naming the repository, workflow and environment that built it, with the artefact digest
> as its subject. That is an integrity anchor held by an independent party, and `DR-14:213` names
> its absence as a limitation — *"not a record held by an independent party the way PyPI holds a
> per-file hash… which is real but is not third-party attestation."* It now is.
>
> **The finding's substance is untouched, for the reason `DR-14` itself gives.** An attestation
> establishes *authenticity* — who published this — and not *honesty*. A party with write access
> commits a payload and a manifest that agree, the workflow faithfully builds it, and PyPI
> faithfully attests that it did. Every signature in that chain is valid and the contents are still
> whatever that party chose. `F6` is about the second thing, and no attestation reaches it. What the
> attestation does close is a different branch — a substituted upload — and the register should have
> said so rather than implying it had nothing external at all.

**The finding is not that `INSTALL.json` is unprotected.** That is the symptom. The finding is
structural: every value the integrity check trusts is held inside the repository the check is
supposed to be judging, so the check can only ever establish internal self-consistency. A party with
write access edits the artefact and the record together, and both checks pass.

`FACT FROM PACKAGE`, read directly:

- `.standards/INSTALL.json` is not an entry in its own `files` map and structurally cannot be:
  `build_payload` (`scripts/install_standard.py:62-103`) admits only files that already exist in the
  source tree, and the record is generated at install time. Nothing else hashes it.
- `check_integrity` (`scripts/check_conformance.py:277-292`) iterates `record["files"]` — a map read
  out of the very file whose integrity is in question.
- `check_staged_integrity` (`:833-963`) compares the staged record against the **working-tree**
  record (`:862-865`), then staged blobs against digests held **inside that same staged record**
  (`:883-894`). One untrusted local copy against another.

**Consequence.** The check is sound against drift, accident, and casual modification, and that is
worth having. It is not, and cannot be, evidence against a party with write access. `README.md` now
says so; this finding is why.

**Not closed by DR-14, now that DR-14 is implemented.** `DR-14` gives distribution identity an
externally recomputable anchor, and `SP049` now checks the profile's declaration against the install
record. That narrows this finding twice over — a third party can establish which release a claim
refers to, and a profile can no longer name a version it was not installed from. It does not close
it, and the reason is unchanged by the implementation: **both values compared live inside the
repository being checked.** A party with write access edits the profile and the install record
together, and both checks pass.

One further limit found while implementing it: `MANIFEST.sha256` is not part of the install payload,
so an adopter cannot recompute the anchor from their own repository — only compare against what the
installer wrote for them. Recomputing it independently requires the published tree. `DR-14`'s
implementation note records this and leaves installing the manifest as an open question for whoever
revisits `DR-20`'s payload principle.

## What would actually close `F6`

Recorded because "structural, stays open" is not a plan, and because two things that look like
remedies are not.

**Closure requires a party other than this repository to hold the value.** Everything compared today
— the files, their digests, the install record, the profile — is writable by whoever holds commit
access. No arrangement of those four closes it, because the problem is not which values are
compared but that one party controls all of them.

**Signing does not close it, and was considered.** A signed tag proves the tag came from a
particular key. The holder of that key is the same person with commit access, so it establishes
provenance, not honesty. It is worth doing once there is a public repository where a stranger
verifying that release *n* came from the same key as release *n−1* has some value — but it would be
a mistake to record it as closing this, and a green *Verified* badge invites exactly that reading.
Decided 2026-08-31: not now, and recorded rather than left as an unexamined omission.

**A ruleset does not close it either.** That is `F8` — it stops the *check* being deleted; it does
not give the check an external anchor.

So what closes `F6` is release plan **items 9 and 10**: a cross-provider adversarial review, and an
independent audit. Concretely, someone who is not the maintainer recomputes `sha256(MANIFEST.sha256)`
from a published tree, compares it against what an adopting repository records, and attests to the
result. Until then this finding is open, and any claim that the integrity check establishes anything
against a party with write access is false.

## Narrowed by `ACT-036`, and still open

`DR-45` shipped `MANIFEST.sha256` into the payload and made `SP049` **recompute** the anchor from it
rather than compare two values the installer wrote. That removes the limit recorded above -
*"an adopter cannot recompute the anchor from their own repository"* - and it is the prerequisite
for the external step, because until now there was nothing local to compare a published manifest
against.

**It closes nothing, and the distance left is exactly the same distance.** The manifest is a file
inside the repository being checked. A party with write access edits it, the install record and the
profile together, and all three agree. What changed is that the value is now *derived from bytes*
rather than copied from a record, so the one comparison that would settle it - this manifest against
the published one - is available to anybody who wants to make it.

Two things deliberately **not** done, both already ruled out above and re-examined on 2026-09-01
when the repository became public: **signing**, which the public repository now makes worth doing on
its own merits and which still establishes provenance rather than honesty; and treating the maintainer's
own recomputation as attestation, which is the party this finding excludes by name.

---

## F7 — `adoption.framework_digest` is never checked against anything

**Severity: medium. Closed.**

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed by implementing `DR-14`, as the body's own closing paragraph records (`SP048`/`SP049`); the body still said Open.*

**The finding is not that a check is missing.** It is that the field's presence, its name, its
`^[A-Fa-f0-9]{64}$` constraint and its description — *"SHA-256 of the pinned release archive"*
(`schemas/application-profile.schema.yaml:59-62`) — together create the appearance of a verified pin
for a value that is only ever shape-checked. A reader of a conformant profile has no way to tell the
difference from the artefact alone.

`FACT FROM PACKAGE`: exhaustive grep of `scripts/check_conformance.py` (1882 lines) returns **zero**
occurrences of `framework_digest` or `framework_version`. The only code anywhere that touches the
field is a negative shape test, `tests/validate_contracts.py:458-459`. `MANIFEST.sha256` and `zip`
likewise appear nowhere in the checker.

`DR-7.md:117-120` already records that the digest shipped in `examples/*.yaml` *"is unverifiable now
and is very likely fabricated too"* — an instance of exactly this finding, recorded before the
finding itself was.

`DR-10.md:239-241` records the gap as known and out of its own scope. This entry is where it was
tracked.

**Closed by implementing `DR-14`.** The installer now records
`sha256(MANIFEST.sha256)` in `.standards/INSTALL.json`, and the checker compares the profile's
declaration against it: `SP048` when the declared version is not the one installed, `SP049` when the
digest disagrees or when the record carries no anchor to compare against. Both graceable, because
`DR-14` *changes what the field means* — every profile written under the previous definition carries
an archive digest and would fail the day this shipped.

**Why the manifest and not the archive**, since the field's old description said archive: the zip
embeds file mtimes, so nobody — including the maintainer — can recompute the digest of an archive
they did not keep. `MANIFEST.sha256` is a pure function of tree content, so a third party holding
the published tree can recompute the anchor on a machine that is not the adopter's. That is the
question `DR-10` set and could not answer.

**A case worth stating because it is the one that silently passed before.** An install record with
no anchor now raises `SP049` rather than being skipped. "Nothing to compare" and "the values match"
must not summarise the same way — the defect shape this register keeps recording.

**What is NOT closed.** Both values compared live inside the repository being checked, so this
establishes that the profile agrees with the install record, not that either is true. A party with
write access edits both. That is `F6`, which stays open, and `DR-14` says so itself rather than
claiming the anchoring gap is closed. What narrowed is real but bounded: a profile claiming a
version it was not installed from now fails, where before it passed in silence.

*One consequence peculiar to this repository:* its own profile sits inside the tree its manifest
covers, so the recorded anchor can never equal `sha256` of the **current** `MANIFEST.sha256` —
writing the value changes the manifest. The anchor records the tree installed *from*, which is a
historical fact rather than a live invariant, and an adopter's anchor behaves the same way with
respect to the framework's later changes.

---

## F8 — The CI detector is inside the artefact it protects

**Severity: medium. Closed.**

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed 2026-08-31 on demonstration of the ruleset, as the body records; the body still said Open.*

**The finding is not "the workflow can be edited".** Everything in an adopter's repository can be
edited. The finding is that the workflow file is *itself* one of the digest-protected `files`
entries, while being the thing that invokes the check that would report its own modification — and
that the fallback this repository documents for exactly this case does not cover this class of
tampering.

`FACT FROM PACKAGE`:

- The workflow is vendored and digest-protected: `scripts/install_standard.py:41,74`, digests at
  `:312-314`, recorded as `files` at `:366`.
- It is what runs the checker in CI: `standard/.github/workflows/standards-conformance.yml:32-33`,
  `run: python .standards/check_conformance.py --repo .`
- **Independent detection exists, and is real, when the hook is active.**
  `standard/.githooks/pre-commit:9-26` invokes `.standards/check_conformance.py --repo … --staged`
  directly. It reads nothing from `.github/workflows/`. A staged edit to the workflow is reported by
  name as a modified `files` entry (`SP040`, `scripts/check_conformance.py:883-894`) and separately
  as `SP005` on the working tree (`:303-315`) — both `graceable=False`, both blocking.
- **But hook activation is the exception, not the default.** It is repository-*local* Git config,
  written only by the installer (`scripts/install_standard.py:210`,
  `git config --local core.hooksPath .githooks`). Local config is neither cloned nor pushed;
  `INSTALL.md:66-68` states that every later clone must run the installer again to activate it.
- **The documented fallback does not apply.** `README.md` states that "the history audit remains the
  durable detector after a bypass". That is true for prerequisite gates and false for `files`
  integrity: `audit_gate_history` (`scripts/check_conformance.py:1264-1280`) is scoped exclusively to
  a gate's own declared `gated_activity.paths` with a precondition-artefact test, and has no
  relationship to `record["files"]`. There is no history-based integrity audit anywhere in the
  checker. That imprecision in `README.md` is recorded here rather than edited, per this packet's
  "record, do not fix".

**Consequence.** Where the hook is active there are two genuinely independent detectors and a CI
bypass alone does not neuter the control. Where it is not — the default state of any clone but the
installer's — a party who edits the workflow to stop invoking the checker is caught by nothing until
someone runs the checker by hand. `DR-15` addresses the remedy and does not implement it.

**The documentation half is discharged (2026-08-31); the finding stays open.**

This entry recorded `README.md`'s imprecision *"rather than edited, per this packet's 'record, do not
fix'"*. That packet closed weeks ago, and the sentence was still on the adopter-facing surface
overstating a control — the exact failure this repository has spent the surrounding work removing.
An expired instruction is not a reason.

Three passages corrected, all carrying the same over-broad reading:

- the claim that the history audit *"exposes a bypass after the commit exists"*, which is true of
  prerequisite gates and false of `files` integrity;
- *"a guarantee that survives Actions being switched off"*, now scoped to gates;
- *"the history audit remains the durable detector after a bypass"* — the sentence this finding
  named — now stating plainly that no history-based integrity check exists, that a modified
  standard-owned file is detected only when the checker runs, and that in a clone where the hook was
  never activated nobody is watching until a human looks.

**Why the finding is still open.** The structural remedy is `DR-15`'s ruleset posture, and it cannot
be demonstrated: `/branches/main/protection` and `/rulesets` both return HTTP 403 on this
repository's plan. Correcting the description of a control is not the same as fixing the control,
and closing this on a documentation fix would be the overclaim the finding is about.

**A route to closure is now decided.** `DR-23` decides to publish surfaceplate as a new public
repository, where rulesets are available at no cost, and to move development there — which matters,
because a ruleset must guard the repository where work happens rather than an archive. The intended
end state is all four status checks and a pull request required before merge on `main`.

That is a decision, not a control. This finding closes when the ruleset **exists and is shown to
block a merge that fails a check** — not when it is configured. The gap between enabling something
and demonstrating it is one this register has recorded repeatedly, most directly in `F13`.

**Closed 2026-08-31, on demonstration.**

`DR-23` was executed: surfaceplate is published at `github.com/pipoventures/surfaceplate`, and a
ruleset `main-required-checks` targets the default branch. Read back from the API rather than
trusted from the request that created it:

- `enforcement: active`
- **`bypass_actors: 0`** — nobody is exempt, including the maintainer
- rules: `deletion`, `non_fast_forward`, `pull_request` (0 approvals), `required_status_checks`
- contexts: `check`, `gitleaks`, `Contract and installer tests`, `Conformance check`
- `strict_required_status_checks_policy: true`

**Zero required approvals is deliberate, not an oversight.** A single maintainer cannot approve
their own pull request, so requiring one would lock the repository rather than protect it. The
control here is the checks; the pull request is what makes them run.

**Demonstrated, twice, because a configured control is not a control:**

| Probe | Result |
|---|---|
| Direct push to `main` | Refused — *"Changes must be made through a pull request"*, *"4 of 4 required status checks are expected"* |
| Pull request with a deliberately corrupted manifest digest | `Contract and installer tests` **FAILURE**; merge refused — *"the base branch policy prohibits the merge"*; `main` unchanged |

The probe branch was deleted immediately afterwards.

**What this does and does not fix.** The finding was that the detector lives inside the artefact it
protects — delete the workflow file and the check disappears. It now cannot: the requirement is held
in the forge's settings, so deleting the workflow makes the merge impossible rather than making the
check vanish. That is the structural change.

**One limit, untested and stated rather than glossed.** Whether an explicit administrator override
(`gh pr merge --admin`) is refused was **not** exercised. GitHub documents rulesets as binding
administrators when the bypass list is empty, and the ordinary merge path *was* refused for the
repository owner — but the override flag itself was not tried, because testing it would have meant
merging a knowingly broken tree to a public branch to find out. Recorded as unverified rather than
assumed either way. If it matters later, the safe test is a trivially revertible failure, not a
corrupted manifest.

**And what stays open regardless.** This protects *this* repository. It requires nothing of any
adopting repository, which must apply its own ruleset. It also does nothing for `F6`: a ruleset
stops the check being deleted; it does not give the check an anchor outside the repository.

---

## F9 — Remediation text names no pinned version

**Severity: low today, rising under any ambient-installer distribution. Closed.**

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed in both halves, as the body records; the body still said Open.*

**The finding is not that today's behaviour is wrong.** Today it is correct. The finding is that the
correctness rests on a property of the *operator's environment* that no code establishes, and the
remediation text is written as though the code establishes it.

`scripts/check_conformance.py:308-311` tells an adopter to *"Revert the local edits and re-run the
installer"*. Nothing scopes "the installer" to a version:

- `repo_root()` (`scripts/install_standard.py:58-59`) resolves the source to wherever the running
  copy of the script physically sits.
- `build_payload` re-reads and re-hashes every file fresh from that source on every run
  (`:313-316`); the run **rewrites** the record rather than restoring toward the previous one.
- Nothing compares the source's `VERSION` against the previously recorded `standard_version`, or
  refuses on mismatch. `:271-272` prints the previous value as a courtesy and acts on nothing.

So "re-run the installer" restores the original bytes only because the operator's checkout is a
fixed artefact they have not moved. That is operator discipline, not a property of the code. Under a
distribution where the installer is an ambient upgradeable package, the same sentence would restore
*different* bytes and call it a repair. `DR-10.md:42-48` already commits to keeping the checker
vendored per-adopter for exactly this reason.

**Closed, in both halves.**

*The text.* `SP004` and `SP005` now name the version from the install record and say why it matters:
the installer rewrites the record from whatever source it runs from, so a different version restores
different bytes. The advice is no longer correct-by-coincidence.

*The behaviour.* `install_standard.py` now reports when its source `VERSION` differs from the
recorded `standard_version`, in the words that matter — **this is an upgrade, not a restore** — and
tells an operator who arrived from an integrity failure to stop and run the recorded version
instead. Reported, deliberately **not** refused: upgrading is the ordinary path and blocking it
would trade one defect for a worse one. What was missing was never that upgrading is wrong, only
that it was indistinguishable from repairing.

Seen to fail: silent on a fresh install, silent on a re-run at the same version, and firing with the
old and new versions named when the source `VERSION` differs.

**What remains true and is not this finding.** `repo_root()` still resolves the source to wherever
the script sits, and item 1 of `org/RELEASE_PLAN.md` will change that under a wheel install. The
notice makes the change visible; it does not make an ambient installer safe.

---

## F10 — The producer evidence record describes an artefact that no longer exists

**Severity: medium. Closed.**

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed by `DR-21`, the file retired, as the body records; the body still said Open.*

**The finding is not that a file is out of date.** It is that a document whose stated purpose is to
be *evidence of package checks* (`audit/VALIDATION_RESULTS.md:3-4`) describes a different artefact
than the one shipped, and asserts as PASS a rule this repository deliberately abolished. An evidence
record that does not describe the thing it ships with is not weak evidence; it is a false claim.

`FACT FROM PACKAGE`, against `VERSION` = `0.14.0`:

- `:6` — `Current release: 0.7.0`. Seven releases stale.
- `:13`, `:15` — `PASS - 5/5` schemas. There are **6** (`schemas/*.schema.yaml`).
- `:54` — instructs verifying `dist/surfaceplate-0.7.0.zip`, which does not exist.
- `:16` — `| Version consistency | VERSION matches the namespace base version segment | PASS |`.
  **`DR-6` explicitly decoupled these.** The claim is now false on its face — `VERSION` is `0.14.0`
  and the namespace segment is `0.7.0` (`NAMESPACE.md:12`) — and, more importantly, it reports a
  passing check for a rule that was removed on purpose. `DR-6.md:26-30` records the replacement.

This is the pre-audit's own `PRE-AUDIT-0.6.0/F2` — *"Producer validation record is stale"* — recurring
in the same file that F2 was raised against, which is why it is recorded rather than quietly fixed.

**Closed by `DR-21`: the file is retired, not regenerated.**

The recurrence is the whole argument. `CHANGELOG.md:75` records fixing `PRE-AUDIT-0.6.0/F2` by
regenerating this exact file; seven releases later it was stale again. Applying the same remedy
twice and expecting a different result would be the register failing to learn from itself. The
structural reason is that a hand-written evidence document depends on a human updating it every
release and nothing fails when they do not — an artefact whose accuracy rests entirely on
discipline, in a repository whose thesis is that discipline is not a control.

Its function is now genuinely served: five suites run on every push and pull request, each reporting
the count of checks it executed, and the workflow confirms each step produced a result. That is
better evidence than a table — re-runnable, dated by the commit, and unable to go stale without
going red.

The file is **kept, marked historical, with every stale or abolished row annotated inline** rather
than only under a banner, because a correction that depends on reading order is not one: a grep for
`Version consistency` lands on the row, not the header. It is kept rather than deleted because its
"Checks NOT performed" and "Outstanding" sections are still true, and `F6` and `F8` cite the latter
by line.

One further thing the audit turned up, fixed in the same change: `audit/AUDIT_README.md` pointed an
auditor at this file as *"the producer's current check record"* and told them to attach
`engineering-control-kit.zip` — the pre-`0.12.0` product name, for an archive not produced under
that name since the rename.

---

## F11 — Nothing checks finding-code uniqueness or contiguity

**Severity: low. Closed.**

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed by `tests/check_code_registers.py`, as the body records; the body still said Open.*

Migrated from `org/decisions/DR-8.md:99-103`, which recorded it as open and never gave it a code:

> *"Nothing enforces that a newly added finding code is unique, contiguous, or documented in
> `core/PREREQUISITE_GATES.md`. The existing catalogue check in `tests/validate_contracts.py` covers
> prerequisite-gate identifiers only, not the finding codes. `SDS036` existed as a
> documented-but-unimplemented code for an unknown number of releases without anything noticing,
> which is precisely what such a check would catch. Not added here; recorded as open."*

The register is the first thing this applies to, and the colliding `F1`–`F4` series this file exists
to resolve is a second instance of the same defect shape.

**Closed by `tests/check_code_registers.py`**, which runs as its own CI step.

The case for a check rather than more care is that care demonstrably did not work. On 2026-08-31
this register carried **four** false statements at once, each written by someone reading the file:

| Claim | Reality |
|---|---|
| `F5`'s entry: `INSTALL.md:29` "still reads" a non-resolving clone URL | Corrected some releases earlier |
| The code table: the checker emits `SP001`–`SP043` | `SP046` and `SP047` existed, added by the session editing this file |
| The `ACT-<n>` row: "no register behind it" | `activity/register.md` existed |
| The header: "this repository still carries no application profile" | It had one, and CI was checking it |

None is a typo. Each was true when written and became false when something else changed — the class
of error a careful reader cannot catch, because nothing about a stale sentence looks different from
a current one.

The check compares **declarations against reality**: the `SP` space declared above against the codes
`check_conformance.py` actually constructs, and the `F` table against its own body sections. Seen to
fail on all five assertions, including a reproduction of the real error — a code added to the
checker and not declared here.

**What it does not do, since three of the four claims above would have survived it.** It cannot
judge whether a finding's prose is still accurate; that is not mechanically decidable. It makes one
narrower thing impossible: a code that exists in one register and not the other.

---

## F12 — Source and vendored checker copies can diverge, and nothing detects it

**Severity: medium. Closed.** Raised by `org/decisions/DR-16.md` during self-conformance work.

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed by `DR-20` (`ACT-003`), as the body records; the body still said Open.*

The finding is **not** that two copies exist. That is deliberate design, recorded at
`org/decisions/DR-10.md:42-48`. The finding is that `org/decisions/DR-11.md:143-152`'s load-bearing
guarantee — *"the code that recorded a digest is guaranteed … to be the code now checking it"* — is
**scoped to the adopter boundary**, where exactly one copy exists and there is no source tree. A
publisher that has installed into itself holds both, and neither `DR-10` nor `DR-11` considers that
case. The guarantee still holds pointwise; that is precisely what makes the self-check answer
questions about a checker that is no longer the one under development.

Mechanically:

- **Every automated route runs the vendored copy.** The hook resolves
  `"$repo_root/.standards/check_conformance.py"` and `exec`s it
  (`standard/.githooks/pre-commit:9,17`); the installed workflow does the same
  (`standard/.github/workflows/standards-conformance.yml:33`). Both hard-fail if it is absent.
  Neither falls back to `scripts/`.
- **The staleness is real, not theoretical.** `check_integrity` digests `repo / rel` where `rel` is
  `.standards/check_conformance.py` (`scripts/check_conformance.py:281-291`).
  `scripts/check_conformance.py` is not a key in `files` and is never opened — the checker contains
  zero references to `scripts/` in its entire length. Editing the source therefore leaves the
  vendored digest matching, and `SP004`/`SP005` stay silent.
- **Consequence.** Add a finding code to source that this repository violates, do not reinstall, and
  the hook and the installed workflow run the *old* vendored checker, which cannot emit it, and
  report **PASS** — while `python scripts/check_conformance.py --repo .` would **FAIL**.
- **`--verify-manifest` is the near miss and must not be mistaken for a remedy.** After
  self-install the two files are separate manifest entries, so editing source does make the manifest
  stale — but the remedy is to regenerate it, after which it records two different digests for two
  files and passes. It detects *"manifest stale"*, never *"the copies differ"*, and by design cannot
  become a drift detector. It **masks** the divergence rather than revealing it.

Adjacent but distinct: `F9` is the installer being ambient-upgradeable — the reverse asymmetry,
adopter-framed. `F8` is the CI detector sitting inside the artefact it protects — the same
self-reference shape, a different mechanism.

**Closed by `DR-20` (`ACT-003`).** The original mitigation — CI running the **source** copy, while
the hook and installed workflow run the vendored one — is kept, because the two routes serve
different purposes and both are wanted. But a mitigation that ensures one route is current is not a
detector, and this finding is about the *absence of detection*.

`tests/check_vendored_current.py` now compares every payload path's source against its installed
copy, deriving the set from `install_standard.build_payload` rather than restating it, and runs as
its own CI step. It reports the review class of anything that differs, so
`[enforcing] .standards/check_conformance.py` reads differently from `[reference] core/…`.

**It was not written speculatively.** The condition occurred twice on 2026-08-31 while implementing
`DR-18`: `schemas/application-profile.schema.yaml` was edited and the checker rejected the new
profile field as unknown, because it was parsing the stale vendored schema. Nothing reported drift.
The symptom was a confusing `SP016` that took a reinstall to explain.

Seen to fail three ways: an edited checker, an edited normative document, and a deleted install
record — the last reporting that self-conformance is gone rather than that there is nothing to
compare, since "no baseline" and "matches baseline" must not summarise the same way.

**What stays open, and it is not this finding.** The check is publisher-only, because an adopter
holds one copy and has no source tree to compare against. An adopter whose vendored copy is stale
relative to a newer *published release* is a different problem, governed by `adoption.review_by`
and `framework_version` — and `F7` records that the digest anchor meant to detect it is checked
against nothing.

---

## F13 — A wired CI check can never have run, inside a green pipeline

**Severity: medium. Closed.** Found while diagnosing this repository's own red CI.

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed when the requirement shipped to adopters, as the body records; the body still said Open.*

`tests/check_identifiers.py` was added, committed, wired into
`.github/workflows/standard-self-check.yml`, and had **never executed in CI** since being added. An
earlier step failed, GitHub Actions short-circuits the remaining steps by default, and the step's
conclusion was recorded as `skipped`. Nothing in the run summary distinguishes *"this check passed"*
from *"this check never produced a result"* unless the per-step conclusion is read individually.

This is distinct from `F1`. `F1` was a result **conditional on an unstated environment fact** — the
check ran and its answer depended on something nobody had declared. This is a result that was
**never produced at all**, while every artefact that would suggest otherwise — the workflow file,
the commit, the step name — was present and correct.

It belongs to the defect shape this register keeps meeting: *an instrument whose negative result
does not establish what it appears to*. It was not caught by reading output more carefully; the
output was internally consistent and wrong. It was caught by comparing one instrument against
another.

**Mitigated in this repository, not fixed in the standard.** The self-check workflow now carries
`if: ${{ !cancelled() }}` on each *check* step, so every check runs regardless of a prior failure
while each step keeps its own pass/fail and the job stays red if any failed. Deliberately **not**
`continue-on-error`, which would mark a failed step as tolerated — that would be weakening a control
to obtain a pass. A final step then confirms each check produced a result, because a mitigation that
reports on itself is what this finding was about.

**Demonstrated, not asserted.** Two runs, both read per-step from the API rather than from the job's
green tick — the artefact that concealed this finding in the first place:

| Run | What it shows |
|---|---|
| `33386896054` (`pull_request`) | All six check steps `success`, none `skipped`. |
| `33387146079` (`workflow_dispatch`) | The **first** check step deliberately failed, and every later check step still executed. |

The second run is the one that matters. Its per-step conclusions read `failure`, `success`,
`failure`, `success`, `success` across the five checks, and the confirm step printed
`ran, FAILED : contracts` / `ran, passed : installer` / `ran, FAILED : manifest` / `ran, passed :
identifiers` / `ran, passed : conformance` before failing the job. **Two independent failures
surfaced in one run.** Under the previous behaviour the first would have appeared and the other four
steps would have reported `skipped` — which is exactly how this finding stayed invisible.

*A limitation found while demonstrating it:* the workflow triggers on `pull_request` and pushes to
`main` only, so a pushed branch with no pull request runs nothing at all. The demonstration used
`workflow_dispatch`. This is not a defect — it is the intended trigger set — but it means a branch
can carry a failing check indefinitely without any run existing to reveal it, and "no failing run"
is therefore not evidence of a passing branch.

**Closed: the requirement now ships.** `core/REVIEW_AND_EVIDENCE.md`'s failure-discipline section
states it for every adopting repository — a pipeline must not silently skip its checks, something
must confirm each check produced a result, and a green run is evidence only for the steps that
actually executed, so cite the step rather than the job.

**It is an obligation, not an enforced control, and the standard says so where it states it.** This
framework inspects a declared profile and a git history, not the semantics of an adopter's
pipelines. Recording the difference is the point: the failure this finding describes is invisible
precisely because everything around it looks correct, and a reader who assumed the framework
checked it would be in the same position the finding describes.

---

## F14 — The placeholder heuristic cannot distinguish notation from an unfilled template

**Severity: medium. Closed.** Found by running the check against this repository (DR-13 item 0).

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed by `DR-17`, as the body records; the body still said Open.*

`SP032` fails a prerequisite gate whose precondition artefact *"still contains template
placeholders"*. The test is `PLACEHOLDER_PATTERN.search(text)` over the whole file
(`scripts/check_conformance.py:1547`), and the pattern's fourth branch is
`<[a-z0-9_\- ]{1,30}>` (`:63-66`). That branch matches **any** angle-bracketed lowercase token, so it
cannot tell an unfilled template slot from a metavariable in prose.

Measured against this repository's own content, the branch has a **100% false-positive rate**. Seven
occurrences across six files; not one is an unfilled placeholder:

| File | Line | Text | What it is |
|---|---|---|---|
| `org/decisions/README.md` | 33 | ``DR-<n>``, sequential, never reused | numbering convention |
| `org/FINDINGS.md` | 19, 31, 40, 41, 286 | ``F<n>``, ``DR-<n>``, ``ACT-<n>`` | numbering conventions |
| `core/PREREQUISITE_GATES.md` | 67 | `git log --since=<effective_from>` | command template |
| `CHANGELOG.md` | 418 | `urn:…:0.7.0:<schema-file-name>` | historical URN form |
| `scripts/verify_release.py` | 10 | `python scripts/verify_release.py <path-to-zip>` | CLI usage line |

Three of those are normative documents this framework publishes. The defect is therefore **not**
publisher-specific: any adopter whose governed artefact contains a usage line or a naming convention
gets a spurious `SP032` on a gate that is a **floor at `standard`**.

**No principled narrowing is available.** A real unfilled slot (`<your-org>`) and a metavariable
(`<schema-file-name>`) are lexically identical — both lowercase, hyphenated, angle-bracketed.
Excluding matches inside Markdown code spans would clear five of the seven but not the `.py` usage
line, and would be a Markdown-specific rule inside a general check. The other three branches
(`replace-me`, `TBD`/`TBC`, `TODO`) fire on nothing here and are not implicated.

**Live effect on this repository while it stood.** It was what stood between this repository and a
clean `check_conformance.py --repo .` — five `SP032` findings, all graceable, giving `WARN` with
grace expiring 2026-09-30.

**Closed by `DR-17`.** The branch was removed rather than narrowed, and the removal was measured
rather than asserted: no test depended on it, and the only shipped template carrying an
angle-bracket slot also carries `replace-me`, so file-level detection is unchanged.
`tests/validate_contracts.py` now pins the negative direction — the three notation strings above
must **not** match — and that guard was seen to fail by reinstating the branch in a scratch copy.

**On the sequencing, since it is the part worth preserving.** This finding was raised inside the
work whose objective was making this same check pass, and was deliberately *not* fixed there:
changing a published control's behaviour inside that work is indistinguishable, in the diff, to a
reviewer later, from adjusting the control to obtain a pass. It was registered as `ACT-004` with no
dependency on `ACT-001` and given its own decision record, and the maintainer directed that the
instrument be fixed **before** self-conformance landed, on the grounds that conformance established
through a known-wrong instrument is not worth establishing. `DR-17` records the reasoning; the
seen-to-fail guards are what make the claim checkable rather than merely stated.

---

## F15 — Two shipped templates were undetectable as templates

**Severity: medium. Closed for the templates this framework ships (`DR-17`); open in general.**

Found while auditing `F14` — specifically, while establishing what the branch being removed was
actually worth. This is the reason that audit had to enumerate rather than reason: the defect is a
**false negative**, and a false negative leaves no output to read.

`SP032` exists to catch a gate whose precondition artefact is still a blank form. Of the five
templates under `templates/`, two — `decision-record.md` and `work-packet.md` — marked their blanks
with a key and an empty value (`- Decision ID:`), which matches no branch of `PLACEHOLDER_PATTERN`,
before or after `DR-17`. An adopter copying either to satisfy a gate and leaving it blank would have
passed `SP032` while pointing at an empty form.

Note the direction of the error relative to `F14`. `F14` made the check fire on correct work;
`F15` made it stay silent on exactly the condition it exists to catch. They were present
simultaneously, in the same four lines of code, and the loud one concealed the quiet one — the
branch's noise made the check feel more sensitive than it was.

**Fixed in the templates, not in the checker.** Both now carry a visible `replace-me` marker.
Teaching the checker to detect empty-value-after-colon was rejected in `DR-17`: it is a second
shape-based heuristic of the kind being removed, and it would misfire on ordinary prose. The
convention belongs where it is chosen.

**Closed, by shipping the obligation rather than by gaining the detection.** The distinction is the
whole content of this closure. `tests/validate_contracts.py` asserts that every file under
`templates/` is detectable, seen to fail by stripping the marker from `templates/work-packet.md` —
but that protects only what this framework ships.

For an adopter's own templates, detection is **not available**: the only general way to recognise a
blank form by its shape was removed under `DR-17` after producing seven false positives and no true
ones, and reinstating it would undo a decision made on measurement. So
`core/PREREQUISITE_GATES.md` now states it as a requirement on the adopting repository — mark your
own templates with one of the tokens, because the framework will not guess — and explains why the
guessing was removed.

An adopter who ignores that requirement still gets a blank form passing `SP032`. That residue is
real and is not closed by this entry; what is closed is the framework's silence about it.

---

## F16 — Placeholder detection cannot separate mentioning a token from containing one

**Severity: low. Closed by declaration (`DR-22`); the detection limit itself is not closable by choosing a better token vocabulary, and stays stated below.**

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed by `DR-22`'s declared exemption, which the body describes this repository using on itself; the body still said Open.*

Found the way findings of this shape are always found — by tripping it. The `CHANGELOG.md` entry
documenting `DR-17` spelled out the four placeholder tokens it had just made canonical, and
`CHANGELOG.md` is a precondition artefact for two gates. The entry describing the fix failed the
check it was describing.

`PLACEHOLDER_PATTERN` is matched against whole file text, so a document that **mentions** a token
is indistinguishable from one that **contains** an unfilled slot. `DR-17` removed the
shape-based branch precisely because it could not draw a distinction its input did not carry; this
is the same defect, narrowed. Four fixed tokens is a far smaller surface than any angle-bracketed
string — which is why this is `low` where `F14` was `medium` — but the surface is not zero, and no
choice of token removes it. A living record that discusses its own controls will always risk
quoting them.

**This is the third instance of one shape in this project**, and the pattern is worth naming
because it keeps arriving disguised as three unrelated bugs:

| Where | What quoted itself |
|---|---|
| `.gitleaksignore` | a comment naming the finding it suppressed became a finding |
| `ORGANISATION.md` | the source of truth for the identifiers failed its own identifier check |
| `CHANGELOG.md` | the entry documenting placeholder detection tripped placeholder detection |

The remedy adopted for the first two was *describe, do not reproduce*, and the same remedy applies
here: `core/PREREQUISITE_GATES.md` is the single document that spells the tokens out, and every
other document refers to it. The first two also needed a second remedy — excluding a source-of-truth
document's own declaration blocks from its own scan — which has no equivalent here, because the
scan belongs to a published control rather than to a local test.

**Closed by `DR-22`, by declaration rather than by detection.** An artefact may now be declared
exempt from the placeholder scan in the profile, with a mandatory rationale. Three properties make
that an exemption and not a hole, and each is tested: it suppresses the *token branch only*, so an
exempt artefact must still exist and still be non-empty; it is declared in the **profile**, never
inside the artefact, because a template able to exempt itself would be exactly the condition
`SP032` exists to catch; and every exemption is reported as an advisory on every run, so a narrowed
control says it was narrowed. `SP050` fires on an exemption naming an artefact that does not exist,
since a stale exemption outlives the thing it was written for.

**The underlying defect is not solved, and the closure does not claim it is.** Whole-file matching
still cannot separate mention from use. What changed is who decides: a human can now say which
artefacts legitimately mention the tokens, in a place a reviewer reads and a diff shows. An adopter
can exempt an artefact that really is unfinished, and nothing prevents that —
`core/CONTROL_PRINCIPLES.md` principle 9 already places the quality of a human declaration outside
what this framework may verify.

This repository uses the mechanism on itself: `CHANGELOG.md` is a precondition artefact for two
gates and documents this very control, so it necessarily contains the tokens. The previous
workaround was to avoid naming them, and that was worse — a changelog that cannot describe a
control is a poorer artefact than one that needs an exemption.

*Note on this entry:* `org/FINDINGS.md` is not a precondition artefact for any gate, which is the
only reason it may discuss this at all. If it ever becomes one, this section is why it will fail.

---

## F17 — The identifier check reads every GitHub URL as a claim about this organisation

**Severity: low. Closed by a declaration mechanism; the underlying rule is unchanged.**

Found by adding the first third-party GitHub URL to a payload file. `tests/check_identifiers.py`
rule 1 asserts that every `github.com/<owner>/` in the shipped tree equals the declared
`github-org`. The secret-scan workflow fetches its scanner from `github.com/gitleaks/gitleaks`, and
the check reported that as organisation drift.

The rule is right for a URL that is *meant* to point at this organisation and wrong for one that is
not. A repository linking to a tool, an action, or somebody's documentation is not misspelling its
own identity. This is the same defect class as `F14` — a rule broader than the thing it means to
detect — and it is the **second** time this check has produced a false positive of that shape: the
first was a regex that matched any host ending in `github.com`, so `docs.github.com/en/...` scored
as an organisation named `en`.

**Closed by declaration, not by weakening the rule.** `ORGANISATION.md` gains a fifth block naming
other people's organisations, and `check_identifiers.py` derives the exemption from it rather than
holding a list — the `DR-6` principle. Rule 1 still asks its question of every owner not declared.

Unlike the quoted-evidence block, third-party entries are **not** paired to a path. The asymmetry
is deliberate: a quoted drift is a wrong spelling of *this* organisation that one record has reason
to reproduce, so scoping it keeps that spelling caught elsewhere. A third party is legitimately
referenced anywhere, and pairing would cost maintenance for no detection.

**Seen to fail both ways.** Removing `gitleaks` from the block restores the failure; deleting the
block makes the parser refuse to start rather than silently exempting nothing.

**What remains open.** The rule cannot distinguish the two cases by itself and still cannot; it now
asks a human to declare which owners are third parties. A third party added to a payload file
without being declared still fails, which is the intended direction — the check fails loudly rather
than tolerating silently — but it is friction, not detection.

---

## F18 — Inherited product and methodology names throughout the public tree

**Severity: medium. Closed 2026-08-31.**

Found while assessing the framework against two target adopter profiles, which is worth noting: it
was invisible for as long as the only readers were people who knew what the names meant.

The tree carried internal product and methodology names from the private repository this framework
grew out of — in `adapters/r.md`, `adapters/typescript.md`, `SETUP_GUIDE.md`, four documents under
`audit/`, `CHANGELOG.md`, `RECONCILIATION.md` and `org/decisions/DR-7.md`. `SETUP_GUIDE.md` was
**titled** with the pre-`0.12.0` product name, and the adoption wizard prompt still called the
product by it in live text.

**Not a brand-policy breach** — these are product and methodology names, not the organisation. It
is a comprehensibility defect, and it landed hardest exactly where an evaluating reader looks
first: `adapters/r.md` is three lines long and spent a third of its length warning against copying
a product the reader has never heard of.

**What was done.** Every inherited name is replaced with a generic description. Live guidance was
rewritten outright; historical records under `audit/` were redacted **with the redaction
disclosed** in a note at the top of each, because the substance of what was checked and found is
unchanged and only the proper nouns are.

An earlier draft of this fix left the historical records untouched under a note explaining the
names, on the reasoning that `DR-23` gives for not rewriting history. The maintainer overruled it:
remove the references everywhere. Recorded because the reasoning matters and was not
wrong — it was outweighed. The compromise that survives is disclosure: nothing was altered
silently, and each redacted document says so.

**What deliberately remains, and why:**

| Retained | Reason |
|---|---|
| `Shiny` in `adapters/r.md` | A public R framework, named the way `pytest` or `React` would be. *"Keep calculation logic outside Shiny server orchestration"* is genuine R guidance, not inherited jargon |
| The pre-rename product name in `CHANGELOG.md` | It records **this** product's own rename. Removing it would erase the record of the rename itself |
| The same name in a historical `audit/` document title | This project's own history, in a record marked historical |
| *"tool-agnostic"* lowercase | Ordinary English used as an adjective, not a product name |

The line drawn: **someone else's names go; this product's own former name stays where it records
history and goes from live guidance.** `SETUP_GUIDE.md`'s title and the wizard prompt were live
guidance and were corrected.

**Two things this does not fix.** The adapters remain 3 and 5 lines — thin for the audience they
serve, and a quantitative team writing R would rely on `adapters/r.md`. And nothing prevents the
same residue recurring; `tests/check_identifiers.py` guards the *organisation* identifier, not
inherited product names, and no check was added here.

---

## F19 — A licence decision recorded in another repository, never implemented in this one

**Severity: medium. Closed by `DR-24`.**

Found by a pre-check demanded during a scope review, not by anything in this repository. That is the
finding's whole shape: nothing here could have caught it, because the decision was never here.

On 2026-08-30 a Class C decision was recorded in `hermes` licensing surfaceplate **by artefact
type** — Apache-2.0 for software, and a separate licence for the documents, amended the same day
from CC BY 4.0 to CC0-1.0 on the reasoning that attribution and change-indication duties are real
friction on files copied into a corporate repository. It required a `LICENSE-DOCS`, a `NOTICE`, and
a README statement of which licence covers what.

**None of it existed.** The root `LICENSE` carried Apache-2.0 correctly; `LICENSE-DOCS` and `NOTICE`
were absent, and `README.md` contained no occurrence of the word "licence" at all. **The repository
was made public in that state**, so every template and agent skill shipped under a code licence the
decision says should not govern prose.

**This is the fourth instance of one shape**, and the register should say so plainly: a decision
recorded in one place and not implemented where it applies. `DR-14` stood decided-not-implemented
until `F7` forced it; `DR-15`'s remedy is still unimplemented; `DR-11` reserved codes for a
generator that does not exist. Those three were at least visible *inside* this repository. This one
was not, and no check here could have found it — the decision lives in a repository this one does
not read.

**A near miss recorded alongside it, because it was luck rather than method.** The same pre-check
asked whether publication had violated a locked sequencing control. It had not — a same-day entry
discharged the cross-provider review requirement. But `DR-23` was written and publication carried
out **without ever consulting `hermes`**, where a Class C decision with an explicit publication
precondition was sitting. The answer came out clean by accident. Had it not, a locked control would
have been breached by an agent that never looked for it.

**What is not fixed.** Nothing checks that decisions recorded elsewhere are implemented here.
`governance/authority-map.yaml` maps paths to governing documents *within* this repository; it has
no concept of an external authority. Whether that is worth building is not decided — but the
absence is now recorded rather than assumed away.

---

## F20 — A control is checked against itself, never against reality

**Severity: high. Closed 2026-08-31**, when the last of `DR-25`'s four patterns was built (`DR-26`).

**Demonstrated, not argued.** This repository was made to claim `full` and declare `provenance`,
`run_lineage`, `method_registry` and `overrides`, in a tree containing no such records. **The
checker raised zero objections about any of them.** Every finding it produced concerned gates.

`SP021` and `SP022` verify exactly two things about a control: that it appears in
`control_decisions`, and that it reads `required`. Nothing asks whether the thing exists.

**The asymmetry, stated in the terms that matter:**

| | What the checker does |
|---|---|
| **A gate** | Looks at reality — does the artefact exist, is it blank, is it still a template, and did anyone touch the gated paths while it was missing |
| **A control** | Looks at the declaration — is it listed, does it say `required` |

**This is uniform across levels, which is why it is severity high rather than a `full`-only
problem.** `dependency_lock` at `essential` is as unverified as `provenance` at `full`. An adopter
at any level can declare every control it requires, possess none of them, and pass.

**Why it is not simply a false claim.** `core/CONFORMANCE_LEVELS.md` already states that *"a schema
file is not enforcement"*, and some controls genuinely cannot be tool-checked — *"we review actual
diffs"* is a promise about human behaviour, and `core/CONTROL_PRINCIPLES.md` principle 9 places that
beyond what this framework may assert. The defect is narrower and real: a reader who sees that
`full` requires `run_lineage` may reasonably infer that something checks run lineage, and the levels
documentation did nothing to prevent that inference.

**Four of them ship a schema and are never read.** `override-record`, `method-registry-entry`,
`method-run-lineage` and `assurance-evidence` describe precisely the records these controls demand.
The checker references **none** of them. The framework wrote down what the evidence should look like
and then never looked.

**How it was closed, in four packets rather than one.** `DR-25` fixed four patterns and made
`implementation_reference` — a field already in the schema and used by nothing — the place an
adopter says where a control lives.

| Packet | Pattern | Controls | Codes |
|---|---|---|---|
| `ACT-011` | D — already a gate; A — declared artefact | `documentation_authority`, `dependency_lock`, `assurance_findings` | `SP051`, `SP052` |
| `ACT-012` | B — declared CI step | `deterministic_tests`, `contract_tests` | `SP053` |
| `ACT-014` | C — declared records | `overrides`, `method_registry`, `run_lineage`, `provenance` | `SP055`, `SP056` |

The four schemas noted above as written and never read are now read: `override-record`,
`method-registry-entry` and `method-run-lineage` validate the registers, and `assurance-evidence` is
consumed within the method-registry schema that embeds it.

**Two claims in this entry did not survive being built**, and are corrected here rather than left
standing:

- *"is current"* — appears twice above. It is **not** provable for these record types, because no
  record schema carries an expiry or review date. `DR-25` is amended in place; `DR-26` records why.
- *"Only the records validator is new"* was right about the code and wrong about the difficulty.
  The judgement in pattern C is not the validation — it is that an **empty register must pass**,
  because a check demanding records is a check rewarding invented ones.

**What is still not provable, now stated at its real width.** That a record is **true**: a lineage
record can carry an input hash computed over nothing. And that a register is **complete**: nothing
detects a run that happened and went unrecorded, so an adopter who files nothing passes forever.
`DR-25` records the first as a permanent boundary; `DR-26` adds the second.

---

## F21 — `dependency_lock` declared with nothing pinned, and CI not recording what it used

**Severity: medium. Closed.**

The first thing `F20`'s architecture was pointed at, and it landed on the framework itself before a
single validator existed.

**Surfaceplate declared `dependency_lock: required` and had no lock of any kind.** No
`requirements.txt`, no `pyproject.toml`, nothing pinned anywhere. All three workflows ran
`pip install pyyaml jsonschema`, unpinned, resolving whatever was newest that morning.

**Worse than unpinned: unrecorded.** `pip --quiet` suppressed the resolution output, so a green CI
run could not tell you which `jsonschema` had validated the schemas. Local carried `pyyaml 6.0.1`
and `jsonschema 4.10.3`; CI had been resolving something newer for months. The two had never
matched, and nothing noticed because nothing looked.

**The rationale described the absence as though it were the control.** It read: *"the runtime set is
two packages, named in every documented install line and in CI."* Naming is not locking. That
sentence is what a declared-but-unverified control looks like from the inside — it sounds like
diligence and commits to nothing.

**Not merely paperwork.** A breaking `jsonschema` release would have broken the checker in every
adopting repository simultaneously, with no record of which version had ever worked.

**Closed by:** `pyproject.toml` pinning both runtime dependencies to exact versions, resolved in a
clean virtual environment with all five suites run against them **before** pinning — not copied from
whatever happened to be installed on a developer machine, which was older and had never matched CI.
The workflows install those exact versions and no longer pass `--quiet`, so the resolution is
recorded in the run. `SP051` verifies the profile's `implementation_reference` points at a file that
exists, is non-empty, is not a template, and is tracked by git.

`tests/validate_contracts.py` asserts the workflows install what `pyproject.toml` declares, and that
every dependency is pinned with `==` rather than a range. Both seen to fail: a drifted workflow
version, and a pin loosened to `>=`. One source of truth, checked rather than trusted — the remedy
this register has now applied to the namespace (`F4`), the organisation identifier (`F5`), the
vendored checker (`F12`) and now the dependency set.

**What is still not proven.** That the pinned versions are *good*, only that they are fixed and
recorded. And pinning a version is not pinning an artefact: there are no hashes here, so this
protects against an unexpected new release rather than a compromised re-upload of the same version.
PyPI does not permit re-uploading a version, which makes that largely theoretical — but it is a
weaker guarantee than a hash-bearing lock, and `pyproject.toml` says so rather than implying
otherwise.

---

## F51 — The wizard set the one field the binding rule names as the human's

**Severity: high. Closed.**

Found by the first cross-provider adversarial review (`RELEASE_PLAN` item 9), and it is the finding
that justifies the item.

`org/RELEASE_PLAN.md` did not merely say the tool never sets a date. It named the field:

> *"what `effective_from` should read — is a human decision the wizard elicits and records verbatim,
> **never one it makes on the human's behalf**."*

`ACT-032` derived it anyway, classing it a consequence rather than a judgement, and **did not amend
the rule**. `sections.build_gate` read
`answers.get("effective_from") or _dt.date.today().isoformat()`.

**The safety argument is stronger than the rule, and nobody had made it.** `SP033` refuses a future
value and `SP034` refuses moving one forward, so a human's answer can only ever *widen or equal* the
audit window. Deriving "now" silently selected **the narrowest value the rules permit**, on the field
that decides how much history the gate audit examines. The fallback also made the substitution
unobservable: a missing answer and an answer of today produced an identical profile.

**The rule was already narrowly false before `ACT-032`**, which is why it was amended rather than
merely obeyed. `adoption_date` has been a tool-supplied date since the first version of this wizard,
disclosed in `sections.build_adoption`'s docstring and named in `tests/test_provenance.py`'s
allow-list — but not in the rule, which read as absolute over a documented carve-out. Obeying an
inaccurate rule would have left the next person to trip on the same gap.

**Remedy** (`ACT-038`): the field is asked again; the fallback is gone; `defaults.py` proposes today
as a `computed` value on the defaults route, which a human approves. The rule now states exactly
what the tool may write unasked — a fact of record, a value from the install record, the framework's
own published prose — and what it never may: a level, a rationale, or a scope decision.

**The transferable part: a rule and its implementation drifted, and the tests could not see it**,
because they were written against the implementation. What caught it was a reader with no stake
comparing the two documents.

---

## F52 — A normative document asserted both halves of a contradiction

**Severity: medium. Closed.**

Found by the same review. `core/CONFORMANCE_LEVELS.md` contained, thirty-eight lines apart and
neither statement scoped:

- line 29 — *"`agent_work_packets` and `actual_diff_review` remain declarations that nothing checks.
  That is not an oversight to be read past: a repository can declare both, do neither, and pass."*
- line 67 — *"**Every control this framework defines is now checked**, at every level. Nothing is
  declared-only."*

A governance standard cannot claim absolute enforcement and honour-system enforcement for the same
controls. `.claude/rules/surfaceplate-authority.md` calls contradictory authority a **blocking
defect**, and this repository publishes that rule to others.

**Remedy:** line 67 replaced with what is true — ten of twelve controls are checked, the two that are
not are named — and the superseded sentence is quoted in place, marked as superseded, so a reader who
lands there sees what changed rather than only the correction.

---

## F53 — A profile could not tell its own reader which controls were real

**Severity: medium. Closed.**

The sharpest finding of the review, and the one nothing internal had noticed. `actual_diff_review`
(nothing checks it) and `dependency_lock` (`SP051` checks it) rendered as structurally identical
objects:

```yaml
actual_diff_review:  {decision: required, rationale: ...}
dependency_lock:     {decision: required, rationale: ..., implementation_reference: pyproject.toml}
```

An adopter reading their own profile — the person most likely to over-read it — had no way to tell
which of their controls the machine enforces. That cuts against
`.claude/rules/surfaceplate-provenance.md`'s own rule that assurance states stay distinct, in the one
file an adopter actually reads.

**A second defect was found while building the fix, and it is the more interesting one.**
`VERIFIED_CONTROLS` — the checker's own declaration of what it verifies — **omitted
`secret_hygiene`**, which `check_secret_hygiene` genuinely verifies through `SP046` and `SP047`. By
that set's own definition (*"controls this checker actually verifies against the repository, as
opposed to verifying that they were declared"*) it qualified. So the checker under-reported itself,
and a label derived from the set would have called a checked control trusted — the exact
mislabelling the fix existed to remove.

**Remedy:** `VERIFIED_CONTROLS` corrected, then each control in the rendered profile carries an
inline comment saying whether the framework checks it, **derived from that set rather than restated**
so it cannot claim a control is checked after the checker stops checking it. A comment and not a
field: adding it as a value would put framework-supplied prose into the profile, which the binding
rule forbids.

---

## F54 — The review packet omitted its own evidence, and asked for a computation

**Severity: medium. Closed.**

Two defects in the hand-off, both the maintainer's, both visible only once a reviewer had used it.

**It asked a question whose evidence it withheld.** The prompt asked whether creating a governance
artefact makes a gate pass while the practice does not exist — and did not attach
`surfaceplate/seeds/*`, the four documents `scaffold.py` writes. The reviewer inferred "empty files"
and reported it as fact. They are 852 to 2,396 bytes of prose, each opening by stating that its own
existence is not the practice. **A reasonable inference from an incomplete bundle: a packet defect,
not a reviewer error**, and the concern underneath it was legitimate.

**It asked for something a text-only reviewer cannot do.** The recomputation of
`sha256(MANIFEST.sha256)` was the entire reason the manifest was attached, and it is the step `F6`
names as its closing condition. The reviewer answered honestly — *"I am unable to mathematically
compute the raw SHA-256 byte digest"* — and was right to. **So `F6` was not narrowed by this review
at all**, and the packet was asking for a fabricated hash from anyone less careful.

**Remedy:** the seeds are attached; the recomputation is scoped to a reviewer with code execution,
with everyone else told to report an evidence gap in one line and explicitly told not to estimate.

**The transferable part: a review packet's defects are invisible until somebody uses it**, and both
of these survived a rewrite made one day earlier specifically to bring it up to date.

---

## F78 — `adopt` validates against the adopter's installed schema but writes the tool's own shape, and notices the mismatch only at the review, in the validator's words

**Severity: high. Closed.**

Recorded under `ACT-047` from the maintainer's first `H1` run of `adopt` against Plutos on 2026-09-02, in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z); the maintainer agreed the finding in the same session. Closes by the activity the maintainer authorises once `H11`'s decision is taken.

Plutos was upgraded to `main` on the morning of 2 September, before phases 1 to 3 merged, so its
`.standards/` carries digest `135c5b6d…` and a schema with no `risk` block. The wizard ran from
this repository's virtualenv at `main` after phase 3 (`19799af0…`). It asked every question,
assembled a profile carrying `risk` (`DR-50` (2)), and validated it at `wizard.py:233` against
`<repo>/.standards/schemas/application-profile.schema.yaml`: the adopter's copy, not the tool's.
The review's hint then read *"This cannot be written yet: the assembled profile does not satisfy
its own schema: (root): Additional properties are not allowed ('risk' was unexpected)"*, and the
maintainer read `risk` as the free-text risk profile he had just typed: *"the reason for the error
seems odd as the risk field was free text"*.

Nothing compares the tool's version and digest with the install record before the first
question. `doctor`'s digest line compares the vendored manifest with its own install record
(`doctor.py:113-130`), so it passes on exactly this state. The draft survives, which is why this
is high and not critical: the interview is lost as an afternoon, not as answers.

**Remedy hypothesis:** compare at start and refuse with the two versions and digests named and
the upgrade command given; `doctor` reports the same comparison; the opening screen `F81` asks for
is where both belong. Validating against the tool's own schema instead would write a profile the
adopter's installed checker then rejects, so the comparison, not the schema choice, is the fix.

**Closed by `ACT-048` (`DR-51` (1)), 2026-09-02.** adopt refuses before the first question when the install is not this tool's release: `wizard._refuse_if_mismatched` compares the install record's anchor with `about.anchor()` and raises `InstallMismatch` naming both versions and digests and the upgrade command, for the interactive run, `--propose` and `--answers` alike; `doctor` gains a `tool vs installed` line that compares the install with the tool rather than with its own record. `tests/test_adopt.py::test_refuses_when_the_tool_and_the_install_differ` and `tests/test_install_and_check.py::test_doctor_reports_a_tool_that_differs_from_the_install`, both seen to fail first.

## F79 — A schema refusal on the review quotes the validator instead of naming the profile line and the key that writes

**Severity: low. Closed.**

Recorded under `ACT-047` from the maintainer's first `H1` run of `adopt` against Plutos on 2026-09-02, in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z); the maintainer agreed the finding in the same session. Closes by the activity the maintainer authorises once `H11`'s decision is taken.

The refusal in `F78` is reported in the validator's vocabulary (`(root)`, `Additional
properties`) rather than the review's own, which already annotates every line with its origin.
`Ctrl+E` goes to the offending line, but the hint does not say so, and it does not name `Ctrl+S`
as the key that writes once the refusal clears. The maintainer's screenshot ends above the footer
and he reported *"I don't see a command to implement the configuration"*. Low because the footer
carries both keys and the review is already correct in refusing; the cost is confusion, not a
wrong profile.

**Remedy hypothesis:** the hint names the line in the review's words and the key that goes to it,
and the review's hint always names the key that writes.

**Closed by `ACT-048` (`DR-51` (6)), 2026-09-02.** a schema refusal is reported in the review's words with the profile path it concerns (`wizard._describe_schema_error`), the review resolves that path to its first line so `Ctrl+E` reaches a block as well as a leaf, and the hint names `Ctrl+E` and says `Ctrl+S` writes once it is fixed. `tests/test_adopt.py::test_a_schema_refusal_names_the_profile_line` reproduces the maintainer's exact sentence by removing `risk` from a fixture's installed schema, and `tests/test_render.py::test_the_review_hint_names_the_way_forward_while_an_error_stands` holds the hint; both seen to fail first.

## F80 — The gate artefact choices carry no explanation of what each file is, what adopting it costs or what it buys

**Severity: high. Closed.**

Recorded under `ACT-047` from the maintainer's first `H1` run of `adopt` against Plutos on 2026-09-02, in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z); the maintainer agreed the finding in the same session. Closes by the activity the maintainer authorises once `H11`'s decision is taken.

The maintainer's words: *"when selecting the files from the dropdown list. Sometimes it's not
clear what each file/parameter actually means or even better what is the actual benefit and cost
of adopting it."* The gate list's per-field help (`F67`, help-text part, closed at `ACT-043`)
explains the field; the choices themselves, the discovered candidate paths and the scaffold
offers, are shown as bare paths. This answer shapes `prerequisites`, the profile's most
consequential section: it decides what the checker audits and what a failed gate blocks. High
because an answer given without knowing its cost is the kind of answer the provenance record was
built to make visible, and it is invisible here at the moment it is made.

**Remedy hypothesis:** one sentence per choice: what the file is (for a discovered path, what
was seen in it; for a scaffold, what the seed contains), what the gate then requires of the team,
and what it buys (which check, which failure it prevents). Under `DR-47` a change to what is shown
beside an asked value is a change to the interview and needs a decision record: `H11`.

**Closed by `ACT-048` (`DR-51` (4)), 2026-09-02.** every value picked from the repository is described the moment it is chosen (`discover.describe`): what discovery saw in the file, whether it matched the gate's words, whether the checker's rules would reject it, and for a workflow which step runs the scanner; a gate's status row states what each status commits the team to. `tests/test_discover.py::test_the_wizard_proposes_nothing_the_checker_rejects` (the descriptions) and `tests/test_adopt_tui.py::test_the_help_beside_a_field_states_what_it_decides_and_describes_the_chosen_file`, seen to fail first.

## F81 — No opening screen: the wizard starts at the first question with no name, version, owner or account of what it will do

**Severity: low. Closed.**

Recorded under `ACT-047` from the maintainer's first `H1` run of `adopt` against Plutos on 2026-09-02, in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z); the maintainer agreed the finding in the same session. Closes by the activity the maintainer authorises once `H11`'s decision is taken.

The maintainer's words: *"Maybe a logo or name of the software in terms of branding in the
terminal at the top? Like a welcoming page or similar with the key package information, metadata,
author, and owner"*. The first screen is the decisions form. Nothing before it says what the tool
is, which version is running against which installed version (`F78`'s comparison has no home
without it), who maintains the framework, what the run will write, that nothing is written before
the review, or which keys move through it.

**Remedy hypothesis:** one screen before the first question, drawn from `pyproject.toml` (name,
version, licence, authors) and the install record (installed version, digest, maintainer), stating
what will be written and where, and carrying the version comparison. Low on its own; it is the
natural host for `F78` and the first page of `F82`.

**Closed by `ACT-048` (`DR-51` (2)), 2026-09-02.** an opening screen before the first question (`WelcomeScreen`, `OpeningApp`): the tool's name, version, anchor, licence and publisher from `about.py`, held to `pyproject.toml` by test; the installed version, anchor and date and whether they are the same release; the repository; what will be written; that nothing is written before the review; and the keys. The resume prompt folds into the opening app. `tests/test_adopt.py::test_the_run_opens_with_the_tool_and_the_install_named`, `tests/test_render.py::test_the_opening_screen_names_the_tool_the_install_and_what_will_be_written`, `tests/test_adopt_tui.py::test_the_opening_app_returns_the_three_answers` and the golden `test_welcome_screen.svg`, seen to fail first.

## F83 — The scanner workflow is proposed without the checker's own test: discovery offered `ci.yml`, which never mentions gitleaks, while two workflows that run it were not proposed

**Severity: high. Closed.**

Recorded under `ACT-048` from the maintainer's completed `H1` run of `adopt` against Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by `ACT-048` under `DR-51`.

The profile Plutos's run wrote carries `wired_in: [.github/workflows/ci.yml]`, recorded in the
provenance sidecar as *discovered: found: .github/workflows/ci.yml*. The checker then reported
`SP046`: *".github/workflows/ci.yml is named as where the scanner runs, but the file never
references it."* Plutos has `secret-scan.yml` and `secret-scan-history.yml`, both with a step
that runs gitleaks; neither was proposed. `plan.controls_plan` builds the candidates as every
artefact whose path contains `workflow` (`plan.py:605`), `defaults.propose_controls` takes the
first (`defaults.py:161-164`), and the field's validator is `tracked_path`, which never reads
the file. `SP046`'s rule — the file mentions the scanner and a step runs it
(`check_conformance.py:1847-1890`) — has no counterpart on the wizard's side, so the parity
`DR-48` established is missing exactly where the maintainer's run failed. High because the
value is proposed, shown as discovered, and accepted through a dropdown that says nothing about
it (`F80`); the profile is then wrong about the repository's only checked baseline control.

**Remedy (`DR-51` (5)):** candidates are the workflows where a step runs the named scanner;
the field's validator refuses any other file with the checker's own words; the parity table's
`SP046` row names it.

**Closed by `ACT-048` (`DR-51` (5)), 2026-09-02.** `scanner.wired_in` is offered and proposed only from workflows where a step runs the named scanner (`discover.scanner_workflows`), the decisions form asks for it when no such workflow exists rather than when no workflow exists, and `validators.scanner_workflow:<name>` refuses any other file in `SP046`'s words. The parity table's `SP046` row names it. `tests/test_discover.py::test_the_wizard_proposes_nothing_the_checker_rejects` and the parity rows in `tests/test_adopt.py`, seen to fail first. The budget test's rich fixture re-measured at 12 (was 11) because its `ci.yml` runs pytest, not gitleaks, and the field is now asked there.

## F84 — An artefact is proposed on a keyword match with no relevance floor and without the checker's content rules: a work inventory quoting `TODO` and `TBD` was proposed as the authority map

**Severity: high. Closed.**

Recorded under `ACT-048` from the maintainer's completed `H1` run of `adopt` against Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by `ACT-048` under `DR-51`.

The `authority_map` gate's artefact was written as
`docs/implementation/owed_work_inventory_2026-08-24.md`, recorded as *discovered: the closest
match in this repository*. The checker reported `SP032`: *"still contains template
placeholders"* — the file discusses a grep for `TODO` and `TBD`. Two defects. The match was on
the word `inventory` (`discover.GATE_KEYWORDS["authority_map"]`), which is a word in the seed's
own path and in a work inventory alike, and Plutos has no authority map at all; a proposal was
made where the honest answer was that nothing matched. And `matched_for_gate` never reads the
candidate, so the checker's own rules for an artefact — non-empty, no placeholder token
(`check_conformance.py:2960-3045`) — were not applied before proposing it. `F40` closed the
"README as register" case by requiring a keyword match; this is the same shape one step on.
High for the same reason as `F83`: proposed, shown as discovered, accepted without a way to
know (`F80`), and the gate is mandatory at `standard`.

**Remedy (`DR-51` (5)):** an artefact the checker would reject is never proposed and is
described as such in the list; `tracked_path` refuses it with the checker's words; the
`authority_map` words drop `inventory`.

**Closed by `ACT-048` (`DR-51` (5)), 2026-09-02.** discovery records every artefact the checker's content rules would reject (`Discovered.rejected`, from `discover.content_problem`), never proposes one, describes it as such in the list, and `validators.tracked_path` refuses an empty file or one carrying a placeholder token in `SP032`'s words; `authority_map`'s words drop `inventory`. `tests/test_discover.py::test_the_wizard_proposes_nothing_the_checker_rejects` and the parity rows in `tests/test_adopt.py`, seen to fail first.

## F85 — The closing report says the checker "passes" on a graced WARN with findings

**Severity: medium. Closed.**

Recorded under `ACT-048` from the maintainer's completed `H1` run of `adopt` against Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by `ACT-048` under `DR-51`.

The run's closing lines, verbatim: *"WARN - adoption is incomplete, but grace expires
2026-10-01 (29 day(s) remaining). ... The checker passes against what you just wrote."*
`cli._report_written` prints the second sentence whenever the checker's exit code is 0
(`cli.py:184-185`), and `DR-49` (2) gives 0 to both a pass and a graced WARN. Two findings
stood on the screen above the word "passes". Medium: nothing is written wrongly, but the
sentence contradicts the checker directly beneath it, in the tool that exists to stop that.

**Remedy (`DR-51` (6)):** the report states the verdict as the checker gave it — a pass, or
the count of graced findings and the date the grace ends — read from the report rather than
inferred from the code.

**Closed by `ACT-048` (`DR-51` (6)), 2026-09-02.** `cli._report_written` evaluates the checker and prints `cli.verdict_sentence`, read from the report: a pass with nothing outstanding, N findings under grace until the date the install record names, or the checker's own explanation of a failure. `tests/test_install_and_check.py::test_the_closing_report_states_the_checkers_verdict_as_given`, seen to fail first.

## F87 — A seedable artefact is created only when the field is left blank, and nothing says so: the dropdown forces a choice among existing files

**Severity: medium. Closed.**

Recorded under `ACT-050` from the maintainer's second run of `adopt`, against a scratch copy of Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by an activity the maintainer authorises; each changes what is asked, so a decision record precedes it (`DR-47`).

The maintainer's words: *"for authority_map, it forces me to select one file in my repo. What if
I have none and has to be created from scratch?"* The scaffold offer exists for four gates
(`scaffold.SEEDABLE`) and follows the gate list when the artefact field is left blank and the
seed's path is free; the screen never says that a blank is allowed, let alone that it leads to an
offer, and the field is a dropdown of existing files whose prompt reads "Choose precondition
artefact (N found)". A reader who has none picks the least wrong file, which is `F84`'s shape from
the other side. Medium because it produces a wrong artefact on a mandatory gate at `standard`.

**Remedy hypothesis:** an explicit first choice in the dropdown for a seedable gate - "create
one from the framework's seed (path)" - recorded as scaffolded exactly as the offer is today, and
the help saying so; the offer screen then confirms rather than surprises.

**Closed by `ACT-052` (`DR-54`), 2026-09-02.** a field whose artefact has a free seed opens its dropdown with "create it: <path>"; choosing it is recorded as scaffolded exactly as the blank was, the offer screen confirms before the write, and the help says what the seed begins with. The field is a dropdown even with nothing else to pick from. `tests/test_adopt.py::test_the_create_it_row_leads_to_a_scaffold_for_gates_and_controls` and `tests/test_adopt_tui.py::test_choosing_the_create_it_row_commits_without_a_refusal`, seen to fail first; the gate list with the row chosen rendered at 80×24 and read.

## F88 — A control's implementation reference offers only files whose names carry fixed words, from fixed directories; a repository with the file elsewhere gets a text box, and one without it has no path to create one

**Severity: medium. Closed.**

Recorded under `ACT-050` from the maintainer's second run of `adopt`, against a scratch copy of Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by an activity the maintainer authorises; each changes what is asked, so a decision record precedes it (`DR-47`).

The maintainer's words: *"When selecting extra controls (like assurance) it asks for a file name.
However what if I don't have any? Also, if I have one there is no dropdown list."*
`plan._implementation_reference_field` offers, for `assurance_findings`, only artefacts whose path
contains "finding" or "assurance" (`plan.py`), and artefacts come only from the directories in
`discover._ARTEFACT_DIRS` and the root. A register at `org/FINDINGS.md` in this very repository
would not be offered. With no match the field degrades to a text box that refuses anything not
tracked, and there is no seed for a findings register, so a repository without one cannot
declare the control at all. Medium because it blocks declaring a control the reader has just
chosen to be held to.

**Remedy hypothesis:** offer every artefact ranked with the matches first, as the gates do;
widen the artefact directories or drop the restriction in favour of ranking; a seed for the
findings register (`assurance_findings`) and the same "create it" choice as `F87`.

**Closed by `ACT-052` (`DR-54`), 2026-09-02.** discovery offers every tracked Markdown or YAML file of the adopter's own, ranked by directory, never a CI workflow; a control's implementation reference offers them all with the name matches first and proposes only from a match (`F40`'s rule); `assurance_findings` gains a seed at `docs/FINDINGS.md` (`seeds/findings-register.md`, no findings and saying so) offered through the same row and written by the same offer. The wider offer surfaced a workflow file being proposed as a findings register, fixed in the same change. `tests/test_discover.py::test_every_artefact_is_offered_and_free_seeds_are_known`, `tests/test_scaffold.py::test_a_control_can_be_seeded_and_the_seed_is_true_on_creation` and the flow test above, seen to fail first.

## F91 — The conformance level barely changes the screens that follow: every gate is listed at standard and full alike, and the above-floor controls read the same, so the level tells the reader nothing

**Severity: medium. Closed.**

Recorded under `ACT-054` from the maintainer's third run of `adopt`, at `full` on a fresh scratch copy of Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by an activity the maintainer authorises after a decision record.

The maintainer's words: *"haven't seen much difference between standard and full. I'd say
conformance levels should result in a very large difference in parameters in the next window.
If we leave all the ones selected as optional the conformance level tells us nothing."* At
`standard` and `full` the gate list shows all nineteen gates, the level's floor marked required
and the rest undecided; the above-floor list on the remainder form shows the same nine controls
with a different floor. The difference is in which rows are locked, which is not what a reader
sees. Medium: the level is the profile's most consequential choice and the screens do not show
its consequence.

**Remedy hypothesis:** the gate list opens with the floor expanded and the rest collapsed under
one heading ("beyond the {level} floor, not required: N gates"), so `standard` shows four gates
and `full` eleven before anything is opened; the hint counts the floor; the above-floor list on
the remainder form says how many the level already requires. Under `DR-47` a change to what is
shown beside an asked value is a change to the interview: a decision record.

**Closed by `ACT-055` (`DR-56`), 2026-09-02.** The gate list opens with the level's floor expanded under a heading that names the level and its count, and every other gate folded under one counted heading ("Beyond the standard floor: 15 gates, not required · [Ctrl+O] open"); the counter names the floor; the above-floor list on the remainder form says how many controls the level already requires. Nothing is hidden and nothing decided: the fold opens on one key and the bulk command still covers every undecided gate. `gates_plan` lists the floor first as the screen shows it, while the profile keeps catalogue order. `tests/test_render.py::test_the_gate_list_opens_with_the_floor_and_folds_the_rest` and `tests/test_adopt.py::test_the_above_floor_list_says_how_many_the_level_requires`, seen to fail first; two older render tests and the gate-list snapshot open the fold before reaching a gate beyond the floor, and the several-gates-visible test seeds the floor so its property is asserted on the screen a reader now meets. The golden regenerated for cause.

## F92 — `SP034` prints an instant as a bare date, so "moved forward" reads as the same date twice; whether a later instant on the same day is a forward move at all is undecided

**Severity: low. Closed.**

Recorded under `ACT-054` from the maintainer's third run of `adopt`, at `full` on a fresh scratch copy of Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). The message is fixed by `ACT-054`; the rule's question is the maintainer's.

The blocking finding on the run read: *"effective_from is 2026-09-02, but this gate previously
declared 2026-09-02 in the profile's own history."* The gate's value was the instant
`2026-09-02T18:43:40+01:00`, set by the scaffold at the moment it created the artefact (`F47`);
the copy's earlier profile, still in its git history, declared the date `2026-09-02`, which the
checker reads as midnight. The instant is later, so the audit window narrowed by eighteen hours
and `SP034` fired, blocking and never graced - and its message rendered both values through
`isoformat()` of the parsed date, hiding the only difference. Low for the message, which is
plainly wrong; the rule's question is real: a re-adoption on the same day as a previous
declaration cannot avoid this without the wizard reading the profile's history.

**Remedy:** the message prints each value as declared. The rule stays as it is until decided.

**Message fixed by `ACT-054`, 2026-09-02; the rule's question stays open.** `SP034` prints each value as declared, so a later instant on the same day reads as what it is. `tests/test_install_and_check.py`, the `moved` fixture extended with a same-day instant, seen to fail on the old message. Whether a same-day instant should count as a forward move, and whether the wizard should read the profile's history when it scaffolds, is for the maintainer.

**Closed by `DR-60`, 2026-09-02.** The maintainer kept the rule as it is: a later instant on the
same day is a forward move and stays blocked; the two alternatives and their costs are in the
record. Decided in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z).

## F93 — A record-directory control's reference is proposed from any directory holding YAML: four controls were proposed `config/accounts` and the checker rejected every record in it

**Severity: high. Closed.**

Recorded under `ACT-054` from the maintainer's third run of `adopt`, at `full` on a fresh scratch copy of Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by `ACT-054`.

`method_registry`, `overrides`, `run_lineage` and `provenance` were all written as
`config/accounts`, recorded as *discovered: found: config/accounts*. `propose_controls` takes the
first candidate for any implementation reference, and for a pattern-C control the candidates are
every directory of the adopter's holding a YAML file, ranked by directory but never matched
against the control. `DR-51` (5) applied the checker's rules to artefacts and scanner workflows;
`DR-54` (2) applied a name match to pattern-A references; pattern C was left with neither. The
checker then rejected `config/accounts/wrappers.yaml` four times over. High: four controls
declared on a directory of account configuration, shown as discovered, and the seed row that
would have been right sat one row above.

**Remedy hypothesis:** a pattern-C reference is proposed only from a directory whose name
matches the control (registry, method, override, lineage, run, provenance); a directory whose
records fail the control's schema is never proposed; otherwise nothing is proposed and the
field is asked with its seed row first.

**Closed by `ACT-054` (`DR-51` (5)), 2026-09-02.** a record directory is proposed only where its name carries the control's words and every YAML record in it passes the control's schema (`discover.register_dirs_that_fit`, judged against the vendored schema, which is why `adopt` runs only on an installed repository); otherwise nothing is proposed and the field is asked with its seed row first; the fitting directories lead the offer. Found on the way: a directory named for a control that holds no records yet - which is what every seeded directory is - was not offered at all, so a seed would have vanished from the offer the moment it was created; such a directory is offered now. `tests/test_discover.py::test_record_directories_and_archived_documents_are_never_proposed`, seen to fail on all four controls.

## F174 — A fact of record was written from an inference, in the file that exists to stop exactly that

**Severity: medium. Closed — `ACT-111`, 2026-09-11.**

`audit/REVIEW_INVITATION.md` opens by stating why it exists: *"a drafted invitation that was never
sent looks, from the register, exactly like one that was — so the sending is recorded here with its
date."* Under `ACT-110` the agent added a row to that table recording a `discuss.python.org` posting
on 2026-09-11. **No posting took place.**

### How

The maintainer replied *"published. what now?"* to a message that had just handed over a drafted
forum post. The agent read it as confirmation the post was live and wrote it into the register. The
word was ambiguous — the package had been published to PyPI an hour earlier, and the same word
covered it — and the agent resolved the ambiguity by assuming, then recorded the assumption as a
dated fact and merged it.

**Nothing checked it, and nothing could have.** A forum posting leaves no trace in this repository;
there is no artefact to hash, no command to re-run, no suite that could disagree. It is precisely
the class of claim this register exists to hold *because* no automated control can, which is what
makes writing one from an inference worse here than it would be almost anywhere else in the project.

### The asymmetry that produced it

Every technical claim in the same packet of work was verified by effect: the attestation fetched and
parsed for three versions, the subject digest compared against an independently derived sdist digest,
the packet's omission established by `grep` rather than assumed. The one claim taken on inference was
the one about what a person had done — because it did not look like the kind of claim that needs
checking. The same session had already produced `F165`–`F172`, every one of which is a check that was
real and not pointed at the thing that was wrong.

### Closed

The row is **removed, not annotated** — an entry recording an event that did not occur cannot be
repaired by a note beside it, because the table is read as a list of things that happened. The
paragraph that discussed the posting is replaced by one stating that nothing has been posted to any
public channel, and `ACT-110`'s activity row is corrected in place.

**`H16` was never closed by this and is unchanged**, which is the one piece of luck: the error
inflated what had been done without advancing anything, so no decision rests on it.

### What would prevent the next one

Nothing mechanical. The standing rule already covers it — *a negative or a fact of record is
established, not inferred* — and it was not applied to a sentence about a person. The honest remedy
is the register's own convention: **the maintainer's own words are quoted in the row**, so a reader
can see what the record rests on. Where there are no words to quote, there is no row.

## F173 — A rejection was taken on a cost that has since gone to zero, and nobody noticed because the benefit arrived by itself

**Severity: medium. Open** — `ACT-110` records the fact and corrects what the register claims;
whether to *adopt* attestations formally is a decision, raised as `H28`.

**Found while preparing a `discuss.python.org` post**, by checking whether PyPI held attestations
before writing a sentence about them. It does:

```
predicateType : https://docs.pypi.org/attestations/publish/v1
subject       : surfaceplate-0.18.0.tar.gz
subject sha256: 6bdcacc9b8f815550131dba09b17a293b2696237ae191f833bf607bca1445125
publisher     : GitHub · pipoventures/surfaceplate · publish.yml · environment pypi
```

The subject digest is byte-identical to the sdist digest verified independently from the download.
`0.16.0` and `0.16.1` carry one too, so this has been true since **3 September**.

### Why this is a finding and not a pleasant surprise

`DR-14` considered exactly this and rejected it:

> *"**Rejected: sign the manifest, or adopt PEP 740 attestations.** These add authenticity — who
> published this — on top of the identity this record settles… Rejected here because **key custody
> and a signing process are infrastructure**, which `DR-12`'s permanent boundary forecloses."*

**Trusted publishing supplies them with no key custody and no signing process.** The cost the
rejection turned on is zero and has been zero since the first publish. The decision was right when
taken and its premise no longer holds, which is a different thing from the decision being wrong.

`DR-14` also wrote, of this project's own anchor:

> *"`MANIFEST.sha256` is a file in this repository's own published tree, **not a record held by an
> independent party the way PyPI holds a per-file hash**… which is real but **is not third-party
> attestation**."*

That sentence names precisely the thing that now exists, and the register went eight days without
noticing.

### What it does and does not change

- **`F6`'s title is imprecise** and is qualified in place rather than rewritten, because it is quoted
  in the published `pypi/0.18.0` release notes and in invitations already sent.
- **`F6`'s substance is untouched**, for the reason `DR-14` gives: an attestation establishes
  authenticity, not honesty. A party with write access commits payload and manifest together, the
  workflow faithfully builds, PyPI faithfully attests. Every signature is valid; the contents are
  still whatever that party chose.
- **What it genuinely closes is a branch `F6` never separated out** — a substituted upload. Anyone
  can now establish, without trusting this project at all, that the bytes on PyPI are the bytes that
  workflow produced.

### The part with a consequence already in the world

**The review packet sent on 2026-09-11 does not mention any of this** — `grep` finds no occurrence of
`attestation`, `sigstore`, `trusted publish` or `PEP 740` in `scripts/build_review_packet.py`, in the
generated page, or in `audit/AUDIT_SCOPE.md`. Two reviewers are holding a document that understates
the assurance that exists, and one of them was asked precisely to think about provenance.

The packet is **not** being regenerated: it has been sent, its digest is quoted in both emails and in
the release notes, and silently replacing a document someone was asked to hash is worse than the
omission. A short follow-up note is the remedy, and the packet generator should carry it for the next
release.

### What would close it

A decision on whether to adopt attestations as a *stated* part of this framework's integrity story —
surfaced by `doctor`, described in the packet, named in `DR-14`'s successor. That is `H28`. Until
then this stays open, because the register currently describes an assurance position weaker than the
real one, and under-claiming is still mis-stating.

## F171 — The installer narrowed what it wrote and not what it said, so a Copilot-only adopter was told about Claude Code four times

**Severity: medium. Closed — `ACT-107`, 2026-09-11.**

**Raised by the maintainer, before publication:** *"the `.standards` folder that is installed reads
`.claude/` but I wanted this to be provider agnostic."*

Checked by effect rather than against the design intent, and the answer has two halves.

**The canon is provider-agnostic, and that is demonstrable.** `install --agents copilot` on a real
repository produces no `.claude/` anywhere, its `INSTALL.json` contains zero references to it,
records `agents: ['copilot']`, and the repository still passes the conformance check. `AGENTS.md`
and `.standards/topics/` are written whichever channel is chosen — `DR-67` (3) says so and the
install proves it. Nothing in this standard requires Claude Code.

**The block an adopter reads first says otherwise.** The managed block written into their
`AGENTS.md` carried, verbatim, in a copilot-only install:

```
Do not edit anything under `.standards/`, `.claude/rules/`,
`.claude/skills/`, `.github/instructions/`, or `.github/skills/` …
…in the location that agent actually loads: `.claude/rules/surfaceplate-*.md` for Claude Code,
…`.claude/skills/*/SKILL.md` for Claude Code,
```

Four references to directories that are not in their repository. It also read *"Same body, same
gates, two paths"*, which is simply false at one channel — a hardcoded count of the kind this
register has a habit of finding.

**This is `DR-67`'s own principle, unapplied at the site `DR-67` itself flagged.** That record
states the filter is applied *"once, over the assembled payload"*, precisely because a filter to be
remembered at several sites will be forgotten at the next — `F58`. It went further and caught that
the block upsert **creates** `.github/copilot-instructions.md` outside the payload, calling that
*"the half this decision nearly missed"*. It narrowed **whether that file is created**. It did not
narrow **what the block says**. The sixth instance of one-site-updated this release.

**Closed by rendering the block from `rules.AGENT_BLOCK_PROSE` at the single point it is read**, so
each install names only the channels it is getting. The digest recorded in `INSTALL.json` is taken
from the rendered text, so the checker still compares an adopter's block against what was actually
written to them — no byte-comparison against the payload file exists to break.

### Evidence

- By effect at all three channel sets. `--agents copilot` renders *"`.standards/`,
  `.github/instructions/` and `.github/skills/`"*; `--agents claude` the mirror; the default both,
  joined as prose.
- Negative control: disabling the narrowing fails the suite and names the strays —
  *"AGENTS.md still points at ['.github/instructions', '.github/skills']"*, and the mirror.
- `tests/check_code_registers.py` asserts `AGENT_CHANNELS` and `AGENT_BLOCK_PROSE` name the same
  channels, so a third agent cannot be added to one table and forgotten in the other.

### A coverage loss this created, and where it was put back

Those four paths used to sit in `conformance-block.md` as prose, where `payload_pointer_checks`
resolved them against the installer's destinations. Moving them into a Python table took them out
of that check's reach — `check_code_registers` went 170 → 169, which is how it was noticed. The
resolution now runs against `AGENT_BLOCK_PROSE` directly, so the **table** is checked rather than
the sentence it happens to produce, and a path the installer never writes fails the suite by name.
Stated rather than banked: a gain bought with a silent loss is the trade this project exists to
notice.

## F172 — The `--agents` refusal told the reader something untrue about this framework's own neutrality

**Severity: low. Closed — `ACT-107`, 2026-09-11.**

Declining every agent channel is refused, deliberately and under test (`DR-67`'s evidence: *"an
unknown channel and an empty list are refused"*). The refusal said:

```
error: --agents needs at least one channel. To install no agent instructions
at all, do not install the standard.
```

**The second sentence is false.** `AGENTS.md` and the twelve canonical topic documents under
`.standards/topics/` are agent instructions; they are installed whichever channel is chosen;
`DR-67` (3) says so in as many words — *"`AGENTS.md` is written either way. It is agent-neutral."*
A reader following that message would conclude the standard cannot be adopted without taking a
named vendor's directory, which is the opposite of what the design does.

Low severity because it misleads rather than breaks. Recorded anyway, because it is a false
statement in a public interface belonging to a framework whose subject is claims that do not hold,
and because it misdescribes precisely the property the maintainer was asking about.

**Closed.** The message names the known channels, states that `AGENTS.md` and `.standards/topics/`
arrive either way and that an agent reading neither vendor's directory is expected to load them,
and says plainly that there is no way to install the vendor mirrors for no vendor — with the issue
tracker as the route for an agent that needs a channel of its own.

### What this does not change, deliberately

**The floor of one channel stands.** It is `DR-67`'s decision, not an oversight, and overriding a
recorded decision to add an option nobody has asked for is the speculative generality Topic 5
forbids — *"a tool built for a process observed once or twice is a maintenance obligation bought
against a guess"*. `DR-67` also leaves the extension path open: *"A third agent is a new entry in
`rules.AGENT_CHANNELS` and its emitter, not a change to this decision."*

**What would revisit it is evidence, and the instrument already exists.** `H18` — watching real
people install this — is where a Cursor, Zed or Aider user balking at carrying a vendor directory
they do not use would show up as a fact rather than a guess. That is now named in `H18`'s row.

## F170 — The release ritual's documented trigger is narrower than the manifest it protects

**Severity: medium. Closed — `ACT-106`, 2026-09-11.**

**Found by following the instruction and failing CI.** `ACT-105` changed `scripts/front_door.sh` and
`tests/check_code_registers.py`, neither of which the standard ships. `CLAUDE.md` said the ritual is
run *"after changing anything the standard ships"*, so it was not run, the fifteen suites were run
instead, all fifteen passed, and the change was reported verified. CI then failed:

```
OUTCOMES: contracts=success installer=success adopt=success provenance=success
adopt_tui=success render=success snapshots=success matrix=success discover=success
shapes=success scaffold=success audit_packet=success manifest=failure
identifiers=success registers=success vendored=success conformance=success
```

One failure out of seventeen, and it was the one the instruction had excused.

**The manifest is not scoped to the payload.** `build_release.py`'s `EXCLUDED_DIRS` names `.git`,
`dist`, `__pycache__`, `.venv`, `.ruff_cache`, `.scratch`, `.pytest_cache` and `.standards`.
Everything else tracked in the repository is hashed into `surfaceplate/MANIFEST.sha256` —
`scripts/`, `tests/`, `org/`, this file. So the set of changes that invalidate the manifest is very
nearly *all of them*, and the document named a small subset.

**The second half is the more useful one.** `CLAUDE.md` opens by naming **fifteen suites** and says
`standard-self-check.yml` "is the authority for the full set". The workflow reports **seventeen**
outcomes: the fifteen, plus `manifest` and `conformance`. "I ran the fifteen suites" therefore
sounds like "I ran what CI runs" and is not, and nothing in the document said so.

This is an agent-facing instruction in a repository whose subject is instructions that outrun their
evidence, so it belongs in the register rather than being quietly edited.

**Closed.** The trigger reads "after changing any tracked file outside the excluded set", with the
excluded set named; the superseded wording is kept beside it as the record of what it cost. A second
bullet states that the fifteen suites are not what CI runs, and names the two extra outcomes.

**Not remedied: nothing enforces this.** The instruction is prose, and an agent that skips the
ritual still discovers it from CI rather than locally. A pre-push hook or a suite that shells out to
`--verify-manifest` would close that, and both are larger than this packet; the honest position is
that CI catches it, one round trip later than it should.

## F165 — A repository that builds a user interface could not be adopted through the file-based route, and the record told the reader to do the thing that does not work

**Severity: high. Closed — `ACT-106`, 2026-09-11 (`DR-87`).**

**Found by reviewing an AI-assisted adoption transcript against the code**, at the maintainer's
request to identify what had succeeded *"just because we used AI"*. This is the clearest case of it.

The answers record `--propose` writes carried this in its own header:

```
# Proposed at level full, and as though this repository builds no user interface;
# answer stack.builds_user_interface and run --propose --level again to see the interface gates.
```

`wizard.propose(repo, *, level)` takes a repository and a level. **It never reads the answers
record.** An answer written into that line was discarded on the next run, without a word, and there
was no flag either — so the instruction printed in the file was the one thing that could not work.

**And there was no other way round it.** `stack.builds_user_interface` is decisive rather than
descriptive: `true` makes `component_library`, `design_authority`, `options_before_build` and
`prerequisite_state_ui` all `required`, and `false` makes all four `not_applicable`; a contradiction
is `SP037`. Of the four, only `options_before_build` has a seed in `scaffold.SEEDABLE`, so the other
three cannot be scaffolded either, and they never appear as `needs-human` lines while the proposal
is being built as no-UI. **A repository with an interface had no route through
`--propose`/`--answers` at all** — which is the whole of `DR-49`'s no-terminal path and the whole of
what `agent-prompt` points an agent at.

The walkthrough diagnosed this by reading `wizard.py`. An adopter has the same file on disk and no
reason on earth to open it.

**Closed by `--builds-ui {yes,no}`**, honoured by `--propose` and recorded as the human's own answer
rather than left as a line they must write again. The header now names the flag and states plainly
that editing the line and re-proposing will not do it — the correction has to include the warning,
because the old sentence is the obvious next thing to try.

**Evidence.** By effect on a real repository: with `--builds-ui yes`, the four interface gates
appear in the record (15 mentions where there were none) and `stack.builds_user_interface` is
recorded as `'yes'` rather than `needs-human`.

## F166 — `F47` was fixed at one of its two sites, so the adopter who supplies their own artefacts got the defect and the one who accepts every scaffold did not

**Severity: high. Closed — `ACT-106`, 2026-09-11 (`DR-87`).**

`F47` in this register reads **Closed by `ACT-035`**, *"`effective_from` accepts an instant, so
adoption binds from the moment"*. The walkthrough reproduced `F47`'s original symptom, against a
build where it reads closed, and the checker's output matched the sample quoted inside `F47`'s own
body almost word for word.

Two sites write a gate's `effective_from`:

| Site | Value |
|---|---|
| `flow.py:answer_scaffold` — artefact the **tool scaffolded** | `provenance.now_iso()` — an instant |
| `defaults.py:propose_gates` — artefact the **adopter named** | `adoption_date` — a bare date, i.e. midnight |

`ACT-035` changed the first. The second kept the date for five months. In the walkthrough's profile
that produced eight gates safe and seven flagged, all seven with:

```
[SP035] Gate 'work_contract' was crossed without its precondition
        1 commit(s) since 2026-09-11T00:00:00 changed a gated path while a required
        artefact was absent: 32c33e1 2026-09-11 Initial commit
```

**The inversion is the part worth naming.** A gate whose artefact the tool created binds from the
instant and is safe. A gate whose artefact the adopter supplied binds from midnight and is not. The
adopter who does more of the work is the one the check reports on.

### Why it is worse than a returning symptom

The obvious correction — normalise the dates to the instant the others carry — is **permanently
foreclosed once the profile is committed.** `SP034` reads any forward move of `effective_from` as
gate-widening, and is never graced. The walkthrough did exactly this, turned a graced `WARN` into an
ungraced `FAIL`, and recovered only because it had not committed the bare dates first. An adopter
who commits first has no way back but an exception record per gate.

`SP034` is right to be unforgiving: a good-faith correction of this defect and a bad-faith erasure
of a violation produce an identical diff. That is exactly why the proposal has to be right the
first time, and why this is `high` rather than `medium`.

### Why no test caught it

Two reasons, and both are the same shape.

- `tests/test_scaffold.py::test_a_bare_repository_can_reach_a_passing_check` asserts
  *"no gate reports a violation over commits made before the artefact existed (F47)"* — and
  **supplies `gates.work_registration.effective_from` itself**, as an instant, in its own answers
  dict. It never let the tool propose, so it could not have observed the proposal.
- `tests/adopt_matrix.py` asserted `("gate:<id>.effective_from", flow.adoption_date)` for the
  non-scaffold branch. The matrix's 208 runs and 44,774 checks were **enforcing the defect as the
  expected value.**

**Closed.** `Flow` carries `adoption_moment` beside `adoption_date` — the date is for the profile's
"written on" line, the moment is what a gate binds from — and `propose_gates` proposes the moment.
The matrix expectation becomes `INSTANT`, the sentinel the scaffold branch already used.

`F47` itself stays `Closed`: its remedy was right and is now applied everywhere. Its body still
carries the pre-remedy sentence *"Not remedied here, deliberately"* under a `Closed` heading, which
is superseded prose left standing; that is corrected in the same change.

**Evidence.** Reinstating the date fails the suite and names it —
*"and every one is an instant, not a bare date (F166): bound from midnight:
['gates.work_registration.effective_from', 'gates.work_contract.effective_from', …]"*. The matrix
report regenerates and the diff is read rather than absorbed.

**Cost, stated rather than buried.** One existing assertion no longer covers `effective_from`:
`test_adopt.py`'s comparison of a proposing run against a typing run, which replays the first run's
values into a second. A time-valued proposal cannot be "submitted unchanged" across two runs,
because the second run's proposal is necessarily later. No single adoption exhibits the case — the
run that proposes the instant is the run that accepts it — but the comparison is two fields
narrower than it was.

## F167 — A wrong-shaped answer failed with an internal profile path and nothing addressed to the adopter

**Severity: medium. Closed — `ACT-106`, 2026-09-11.**

The walkthrough answered `controls.scanner.wired_in` as a YAML list. That is a reasonable reading:
the **profile** stores `wired_in` as a list, and the record's `choices:` block says nothing about
shape for a free-text field. `sections.build_profile` wraps the answer in a list itself, so a list
answer became a list of lists, and the provenance walk then failed on a path no rule reaches:

```
The wizard could not finish: KeyError: "no provenance rule reaches profile path
'baseline_controls.secret_hygiene.scanner.wired_in[0][0]'"
```

Exit 4, nothing written. The `[0][0]` is the entire diagnosis and it is not addressed to the person
who has to fix it. The walkthrough recovered by reading `sections.py:135`.

`gates.<id>.precondition.artefacts` is wrapped the same way and would have failed identically.

**Closed.** `wizard.replay` refuses a list where one value belongs, at the point the record is read,
naming the adopter's own line: *"wrap.release_route takes a single value, not a list. Write it as
`wrap.release_route: Merged to main.` The profile stores some of these as lists, so the wizard is
what wraps your answer — writing the brackets yourself nests it one level too deep."* The answers
that really do take several values (`controls.above_floor`, anything ending `.enforcement`) are
unaffected.

**Evidence.** A regression test takes a complete, valid record, wraps one scalar answer in a list,
and asserts both that the refusal names that line and that it hands back no internal profile path.

## F168 — A gate could not name the artefact another gate's offer was about to create, which is the pairing the catalogue recommends

**Severity: high. Closed — `ACT-106`, 2026-09-11.**

`core/PREREQUISITE_GATES.md` says of `authority_map` and `authority_same_change`: *"The two are
almost always adopted together."* Follow that advice — name one gate's artefact as the other's,
where the first is one the tool offers to create — and the review refused:

```
Refusing to write: gates.authority_same_change.artefact:
Nothing exists at that path in this repository.
```

For a path the same run was about to write.

`flow._first_problem` already exempts an artefact that is *"created when the profile is written, not
before"* — but keyed the exemption on **that field's own origin**. The gate that accepted the offer
has origin `scaffolded` and was exempt. The gate that reused the identical path has origin `typed`
and was not.

`STAGES = ("decisions", "level", "gates", "remainder", "scaffold", "review")`, so nothing about the
ordering can be inferred from the stage names either: the artefact genuinely does not exist yet when
the review runs.

**The escape was undocumented**, which is what made the refusal a dead end rather than an
inconvenience: copy the seed out of `.standards/seeds/` by hand and commit it — a directory named in
no adopter-facing document at the time (`F169`). The walkthrough found it by reading `scaffold.py`,
then *predicted* that `register_currency` would fail identically and pre-empted it. A person meets
one opaque refusal per gate.

**Closed.** The exemption is keyed on the path rather than on the field: any value among the paths
an accepted offer will create is exempt, whichever field names it.

**Evidence.** A regression test adopts at `standard` with `register_currency` `required` and naming
the register `work_registration`'s offer creates, and asserts the profile carries that path twice.
Reverting the fix fails it with the walkthrough's exact sentence: *"the review refuses to write:
gates.register_currency.artefact: Nothing exists at that path in this repository."*

## F169 — The seeds an adopter needs were named in no document an adopter receives

**Severity: medium. Closed — `ACT-106`, 2026-09-11.**

`.standards/seeds/` is installed into every adopting repository and holds the material
`surfaceplate adopt` writes gate artefacts from. Searched across `surfaceplate/standard/`,
`surfaceplate/core/`, `README.md`, `INSTALL.md` and `SUPPORT.md`, the string `seeds/` appeared
**nowhere**. The directory was discoverable only by reading `scaffold.py` or by listing
`.standards/`.

That is a documentation gap on its own and was the load-bearing one for `F168`, whose only remedy
was to copy a seed by hand.

**Closed.** `core/PREREQUISITE_GATES.md` gains *"Where an artefact comes from when you have none"*:
what `SP032` demands of a precondition artefact, why pointing a gate at the closest existing file is
`F40`, the seeds' location with a worked `cp`, why copying by hand is sometimes worth it, and — the
part that must stay — that **not every gate has a seed, deliberately**, because an
equivalence-evidence protocol cannot be created empty and remain true. A gate that offers nothing is
the framework declining to write a claim on the adopter's behalf.

## F164 — The front-door script rewrote the operator's own git configuration, and the damage was invisible from inside this repository

**Severity: high. Closed — `ACT-105`, 2026-09-11.**

**Reported by another agent session working in `plyego`, not found here.** It observed that every
git hook on this machine had stopped running and traced the cause back to this repository's script.
The report was verified by effect before being acted on, and verification found it understated: the
script clobbers **three** global settings, not one.

`scripts/front_door.sh` opened with, unconditionally and at global scope:

```sh
git config --global user.email stranger@example.invalid
git config --global user.name "A stranger"
git config --global core.hooksPath "$work/global-hooks"     # the machine the review met
```

`$work` is a `mktemp -d` directory. The script does not remove it, but the system does, so what
remains after a run is a **global `core.hooksPath` pointing at a directory that does not exist**.

### Why that is worse than a broken path

`core.hooksPath` **replaces** `.git/hooks`; it does not add to it. A hook that no longer runs
therefore produces no error, no warning, and no diff — the hook file is still on disk, still
tracked, still executable, and git simply never calls it. Every reader's check for "is the gate
installed?" answers *yes*. This repository's own concurrency topic states exactly this hazard
(`.claude/rules/surfaceplate-11-concurrency.md`: *"a repo-local hook can stop running the moment a
hooks path is set, with no error and no diff to show for it"*). The script that caused it was
written after that text.

### Established state, at the time of the fix

```
$ git config --show-origin --get-all core.hooksPath
file:/home/mps2210/.gitconfig   /tmp/tmp.EUkPfcFmMb/global-hooks     <- does not exist
file:.git/config                …/surfaceplate/.git/hooks-chain

$ git config --global --get user.name ; git config --global --get user.email
A stranger
stranger@example.invalid
```

Of the seven repositories under `~/github`, **only `surfaceplate` sets `core.hooksPath` and
`user.email` locally**. A local value wins over a global one, so this repository's pre-commit gate
kept running and its commits kept Mario's authorship throughout — **the defect was undetectable
from inside the repository that caused it.** The six that carry no local override lost both:
`mnemosyne` and `plyego` have `pre-commit` hooks, and all seven have `post-commit`.

The authorship damage is measurable and is on `main`:

| Repository | Commits authored `A stranger <stranger@example.invalid>` |
|---|---|
| `plyego` | 165 (83 on 09-09, 4 on 09-10, 78 on 09-11), plus 13 earlier |
| `actually-using-ai` | 7 |

Recovered from history, the identity the script overwrote was `mps2210 <mps2210@outlook.com>`.
**The 13 earlier commits date this defect to before 9 September** — it has been present since
`ACT-045` created the script, not since the run the other session noticed.

### The fix, and what it deliberately does not change

**The global settings stay global.** `F70` — the finding this script exists to hold closed — is
precisely *a stranger meeting a machine with a global `core.hooksPath`*. Making the setting
repository-local would have quietly retired that coverage while appearing to fix a bug. What was
wrong was never *that* the scope was global; it was **which file the global scope was**.

`GIT_CONFIG_GLOBAL` moves the global scope itself into `$work`. Git still reads and writes it as
the global scope, so `F70`'s condition is reproduced exactly rather than approximated, and
`~/.gitconfig` is never opened. `GIT_CONFIG_NOSYSTEM=1` goes with it.

**This is the second site of a fix this repository already made.**
`tests/test_install_and_check.py:neutralise_ambient_git_config` has done exactly this since 0.13.0,
for exactly this reason, and its docstring argues the case. The shell script never received it —
`F58`, `F143`, `F157` and `F161`'s class, and the fourth this release: *two sites, one updated*.

### The guard, because the failure mode was silence

A git older than 2.32 does not know `GIT_CONFIG_GLOBAL`. It would ignore the variable and write to
`~/.gitconfig` exactly as before, silently, which is how this survived. The script therefore
**establishes that the redirection took effect before writing anything**, by a read rather than a
write: it plants a key in the sandbox file and asks git, at global scope, to read it back. If the
answer is wrong the script refuses to run.

### Evidence

- **Both directions on the static check.** `tests/check_code_registers.py` now requires every
  script under `scripts/` that writes global git config to export `GIT_CONFIG_GLOBAL` *above* the
  first such write — checked by line position, because an export below the write protects nothing.
  Removing the export makes the suite fail and name it: *"front_door.sh redirects the global git
  scope before writing to it: first write at line 36, no export"*.
- **The runtime guard, by effect, against a simulated old git.** The real, unmodified script was
  run with a `git` shim earlier on `PATH` that unsets `GIT_CONFIG_GLOBAL` and execs the real git —
  emulating a git that ignores the variable. It refused, exited 1, and `~/.gitconfig` was byte
  identical afterwards (sha256 compared before and after).
- **The whole script, by effect.** `sh scripts/front_door.sh .` → `FRONT_DOOR=PASS`, `~/.gitconfig`
  sha256 unchanged, and `core.hooksPath (global)` still the pre-existing value rather than a fresh
  temp directory.

### What this finding does not fix

**The machine is still in the damaged state and this repository cannot repair it.** The settings
live in `~/.gitconfig`, outside any repository, and the correct previous value of `core.hooksPath`
(most likely unset) is not recoverable from evidence — only the identity is. Raised as `H27`.
**The 172 misattributed commits are not repairable either**: they are pushed history on `main` in
two other repositories, and rewriting that is a destructive operation on repositories outside this
one's scope. Recorded as fact, not remedied.

## F163 — `requires-python` was not merely untested; it was false

**Severity: medium. Closed — `ACT-104`, 2026-09-11.**

**Raised as `low`/`Accepted` on the same day and reassessed within hours**, when acting on it
turned up something worse than the gap it described. The original framing — *"admits five versions
and CI tests one"* — was accurate and incomplete, and the incompleteness was in the dangerous
direction: **the package could not install on Python 3.9 at all.**

`pyproject.toml` declared `requires-python = ">=3.9"`. `jsonschema==4.26.0` — a **hard dependency,
not an extra** — itself requires `>=3.10`. Verified by resolving the real dependency set against
each interpreter rather than by reading metadata:

```
python 3.9   FAILS: No matching distribution found
python 3.10  runtime deps resolve
python 3.11  runtime deps resolve
python 3.12  runtime deps resolve
python 3.13  runtime deps resolve
```

**And the false claim made the failure worse, not just wrong.** `requires-python` is what pip uses
to say plainly *"this package requires a different Python"*. Declaring `>=3.9` told pip the package
was compatible, so a 3.9 user would instead have met a dependency-resolution error naming
`jsonschema` — a message that points at the wrong thing.

**Closed by `ACT-104`**: the floor is `>=3.10`, corrected in `pyproject.toml` and `INSTALL.md`; the
classifiers now name 3.10–3.13; and a `compatibility` job installs the real package with its extra
on each of those four and exercises it. The claim is now true *and* checked, which is the only
combination this framework accepts from anyone else.

**What the matrix deliberately does not do**, stated so the job's name is not read as more than it
is: it runs an install, a version and help check, an import sweep over every module, and
`test_install_and_check.py`. It does **not** run `tests/test_adopt.py`, because that suite imports
`tomllib` (3.11+) for a metadata check — a property of this repository's development tooling, not
of the package. The wizard's modules are verified to import on every version; its behaviour is
verified on one.

**The lesson is about my own severity call.** `low`/`Accepted` was assigned on the reading that the
declaration was probably right and merely unverified. *Probably right* is exactly what this
framework refuses from adopters, and the check that would have settled it took one command.

---

### The original entry, as raised

**Severity: low. Accepted — `ACT-103`, 2026-09-11. The declaration stands; nothing verifies it.**

`pyproject.toml` declares `requires-python = ">=3.9"`, so pip will install this package on 3.9
through 3.13. `.github/workflows/standard-self-check.yml` runs **`ubuntu-latest`, Python 3.12**,
and nothing else. Four of the five admitted versions have never run a single suite, and no
platform other than Linux ever has.

**Found while fixing `F162`**, by asking whether a `Programming Language :: Python :: 3.9`
classifier would be true. It would not be, so it is not there — `pyproject.toml` lists only
`3` and `3.12`, with the omission and its reason written beside it.

This is `SP021`'s own defect shape turned on this repository's packaging: **a declaration with
nothing behind it.** It is recorded rather than removed because `>=3.9` is probably correct — the
code uses nothing newer, and `from __future__ import annotations` is used throughout — but
"probably correct" is what this framework exists to refuse from everyone else.

**What would reopen it:** a report that the package fails to install or run on an admitted
version. The remedy either way is a CI matrix across 3.9–3.13, which would make the declaration
true and let the classifiers follow; that is a workflow change and its own activity.

## F162 — The package's PyPI page would have been empty, and the file said otherwise

**Severity: medium. Closed — `ACT-103`, 2026-09-11.**

Found by building the real sdist and reading its `PKG-INFO` rather than reading `pyproject.toml`:

```
Metadata-Version: 2.5
Name: surfaceplate
...
Requires-Dist: syrupy==4.8.0; extra == 'test'
```

**Twenty-four lines, every one a header, no body.** `readme` was never declared, so the
distribution carried no `Description` and no `Description-Content-Type`. The PyPI project page
would have rendered the one-line summary and then blank space — for a project whose entire claim
is that a stranger can pick it up and adopt it.

**And `pyproject.toml` asserted the opposite, in the file that would have had to declare it.** The
comment above `[project.urls]` read *"until then the README, which PyPI renders, carries them in
prose"*. PyPI did not render it. A statement about this package, in this package, contradicted by
this package.

Three smaller gaps in the same place: **one classifier** (`Development Status`), where PyPI filters
and ranks on them; **no keywords**; and **ten relative links** in `README.md` — `](INSTALL.md)` and
the like — which GitHub resolves and PyPI resolves against `pypi.org`, producing ten 404s on the
page.

**Closed by `ACT-103`.** `readme = "README.md"` declared; eight classifiers, each one true (see
`F163` for the four deliberately absent); ten keywords; the README's file links made absolute.

**The link change kept a property it could have lost.** `check_code_registers.py` skipped any
target containing `://`, so absolute links would have traded a 404 on PyPI for a link to a deleted
file that nothing checks. It now resolves this repository's own blob URLs by their path, so a
target that stops existing still fails the suite — verified by pointing one at a file that does
not exist.

**Verified by effect, both before and after**: the rebuilt sdist carries
`Description-Content-Type: text/markdown` and a 406-line `PKG-INFO` whose body begins
`# Surfaceplate`.

## F161 — The gates screen dropped every field added to `FieldSpec`, and wiped its own refusal

**Severity: medium. Closed — `ACT-099`, 2026-09-11.** Two defects in one screenshot, from the
maintainer's `A-stranger` walkthrough. Both are "two sites, one updated".

**The refusal lasted one frame.** `Ctrl+S` on a gates screen with three blank artefacts reported
`component_library · Precondition artefact: This cannot be blank.` — and the next keypress erased
it. The adopter presses `Ctrl+S`, sees nothing change, moves to look for the problem, and the
message is gone. Reported as *"Can't progress here clicking Control + S"*, and reproduced exactly:
the hint survives until a Tab or an arrow, then the focus handler redraws it with no error.

**`F74` is this defect, fixed on the decisions form and never applied here.** That fix holds the
error on the screen (`_pending_error`) so a later focus event redraws it rather than clearing it.
The gates screen had no such hold, and its `_set_hint(error="")` default meant every other caller
wiped it.

**And the gates screen rebuilt each `FieldSpec` by hand.** `_compose_gate_fields` constructed a new
one listing **eleven named fields**, so every field added to `FieldSpec` since was silently dropped
on this screen alone — `seed`, and then `found_total`, which is why a gate's dropdown read
`(12 found)` where the controls form read `(12 of 30 found)` for the same repository. The correct
form, `dataclasses.replace`, was already in use **ten lines below** in the same class.

**A copy that must be updated whenever the thing it copies grows is a copy that will not be.** That
is the finding, not the two fields: `F147` added `found_total` and the omission was invisible
because nothing compared the rendered widget against what the plan built. The regression now does,
over every `select` field, so the next field is covered without anyone remembering.

**This repository keeps finding this shape** — `F58` (the per-agent pattern applied to instructions
and not skills), `F143` (one of two screens wired), `F157` (`DR-74` applied to `doctor` and not the
checker), and now both halves of this. The hazard is the duplication, not the individual omissions.

## F160 — `SP047` missed every disarmed scan written across lines, and blamed a step that reads the report

**Severity: high. Closed — `ACT-098`, 2026-09-11.** Found on the maintainer's `A-stranger`
walkthrough, and it is two defects that concealed each other.

`SP047` exists to catch a secret scan that cannot fail the build. On a real adopter's workflow it
reported:

```
[SP047] The scan command in .github/workflows/secret-scan.yml discards its exit code
        what: 'Summarise findings' runs the scanner on a line that swallows a non-zero status
```

**`Summarise findings` does not run the scanner.** It runs `python3` to read a report, on this line:

```
count="$(python3 -c "... json.load(open('gitleaks-report.json')) ..." 2>/dev/null || echo 0)"
```

The scanner's name is in a *filename*; the `|| echo 0` defaults the count when the report is absent.
The check matched the scanner's name **anywhere on the line** — filename, message text, comment —
and any neutralising token anywhere on the same line. That is `DR-74`'s rule again: a negative
reported without being in a position to establish it, and the position it lacked was knowing which
command the line runs.

**And the scan that WAS disarmed went undetected**, which is the half that matters. The step read:

```
- name: Run gitleaks (report-only — exit-code 0)
  run: |
    ./gitleaks detect \
      --source . \
      --exit-code 0 \
      --verbose
```

`SP047` iterated `run.splitlines()`. **The line naming the scanner carries no neutralising token,
and the line carrying one does not name the scanner** — they are one command and the check saw two
lines. On top of that, `--exit-code 0` was not in `NEUTRALISING_SUFFIXES` at all, so even joined it
would not have matched.

**So the finding was right by accident and wrong in its detail**, and the true condition — a
deliberately report-only secret scan, announced in the step's own name — was invisible to the check
built to find it. A long shell command written across continuation lines is the normal way to write
one; this check has never seen inside one.

**Closed by three changes**, each verified: `shell_commands()` joins backslash continuations before
scanning; `line_invokes()` requires the scanner to BE a command in the line rather than appear
in it; and `--exit-code 0` / `--exit-code=0` join the neutralising tokens.

**Both directions on the real workflow.** With `--exit-code 0` reinstated, `SP047` fires and names
`'Run gitleaks'` — the step that runs it. With the scan armed, the repository reports `PASS`.

**The false negative was found by the negative control, not by the fix.** Repairing the false
positive alone would have left `SP047` silent on the case it exists for, and the repository would
have gone green with a disarmed scanner and a checker that had just been made *more* precise about
it. Testing that a fix still fails where it should is what separated the two.

## F159 — `--repin` blamed six lines it does not write

**Severity: medium. Closed — `ACT-097`, 2026-09-11.**

Found by the maintainer on his own walkthrough, running `--repin` against `A-stranger` — a
repository still carrying the installer's template:

```
Refusing to write: the schema installed here does not accept the line `adoption.adoption_date`:
'replace-me' is not a 'date'; the line `adoption.review_by`: ...; the line
`builds_user_interface`: ...; the line `prerequisites.0.effective_from`: ...; the line
`risk.material_quantitative_output`: ...; the line `risk.relied_on_outside_team`: ...
```

**`--repin` writes two lines. None of those six is either of them.** The substitution had worked
and both values read back correctly; what refused was `_verify`, which validates the *whole*
profile — and the template's twenty placeholders fail it.

**Two entirely different facts shared one refusal**: *this profile has not been written yet* and
*re-pinning it broke something*. The adopter was told the second when the first was true, and the
message reads as though the command is defective.

**The advice already existed, on the wrong branch.** `repin()`'s `moved != 2` path — the rarer
failure, where the lines cannot be found at all — says *"...or run `surfaceplate adopt` if this
profile has not been written yet."* Exactly right, five lines above the branch people actually meet.

**Closed** by establishing which of the two facts is true before refusing: the profile is validated
**as it was, before any substitution**, and a profile that was already invalid gets a refusal naming
that and pointing at `adopt`. `_verify` is untouched — on `adopt`'s own write path a schema failure
genuinely is the wizard's fault, and must keep saying so.

**Both directions verified**: `A-stranger`'s template is refused with the new message; a complete
profile with a deliberately staled digest still re-pins.

**The fix found a latent unrealism in `ACT-092`'s own fixture, and it is the more interesting half.**
`test_repin_clears_the_two_findings_an_upgrade_guarantees` built its "complete but stale" profile by
writing `"0" * 64` as the previous digest — and **sixty-four unquoted zeros parse as the integer 0**,
not a string, so that profile had never satisfied its own schema. It passed for a day because nothing
validated the profile before re-pinning it; **the moment something did, the fixture was the thing
that broke**, and for a moment it looked as though the new guard was too strict. An upgrade leaves an
old *valid* digest. The fixture now uses one, and asserts that it is a string.

The same YAML trap caught the agent twice in one hour — once staling a fixture by hand, once here —
which is what a constant that is all digits does in a format with implicit typing.

**And the agent's instruction was wrong before the tool was.** The walkthrough commands handed over
told the maintainer to expect `--repin` to clear `SP048`/`SP049` — on a repository the agent had
checked minutes earlier and seen to hold *twenty* placeholders. The install step was dry-run first;
the re-pin step was not. A sequence verified in part reads exactly like one verified whole.

## F158 — The history audit accused commits made before the gate existed

**Severity: low. Closed — `ACT-096`, 2026-09-11.** `F136`'s `PW-18`, decided at `H25`.

`git log --since` is inclusive at second granularity and a Git commit timestamp is whole seconds, so
a commit made in the same second as `effective_from` — **whether just before it or just after** — is
indistinguishable from one made at it. Left inclusive, a commit made moments *before* adoption was
reported as crossing a gate that did not yet exist.

Verified directly rather than read: `git log --since=<a commit's exact instant>` returns that commit,
and one second later returns nothing. And this repository's own matrix fixture already back-dates its
commits *"so a gated commit made in the same second as a seed's instant never reads as crossing a
gate"* — a workaround for this, in this tree, written by someone who met it and routed around it.

**What decided it is which error the adopter can act on.** A commit that predates adoption **cannot
be remediated**: they cannot rewrite history from before they adopted, so their only route is a gate
exception for a commit that did nothing wrong — which teaches them to record exceptions for
non-events and devalues the mechanism. The cost of the fix is that a commit made in that same second
*after* the gate took effect goes unaudited. One second of silence against a ceremony that erodes a
real control.

**Closed** by opening the window at the first second Git can distinguish from the declaration. For a
date-only `effective_from` this excludes only the midnight second and leaves the whole day audited,
so `F48`'s fix is untouched.

**A correction to this register's own costing.** `H25` as first written offered a route (b) —
*"filter the boundary commit by comparing timestamps after `git log` returns, which is exact"*. **It
does not exist.** Git stores commit times as whole seconds, so there is no sub-second information to
compare and no exact filter to write. The recommendation was re-costed before it was taken.

## F157 — `SP038` reported a negative it was not in a position to establish, and would have failed every adopter's CI

**Severity: high. Closed — `ACT-096` (`DR-84`), 2026-09-11.** Answers `H24`; corrects `ACT-095`.

`local_hook` is a property of a **developer's checkout**. `core.hooksPath` is local Git
configuration and is **never tracked**, so a fresh clone has no hook by construction — and a CI
runner is a fresh clone, which also has no staged changes to gate. Asking there whether the local
hook is in place has no answer. `SP038` answered it anyway, with `False`.

Reproduced on a runner-shaped checkout of this repository:

```
[SP038] Gate 'work_registration' claims hook enforcement that is not in place
FAIL - adoption is incomplete and grace disabled by --no-grace
```

`SP038` is `graceable`, so this is **masked for 30 days after install and then fails**. This
repository's own profile claims `local_hook` and its own CI was on that clock.

**This is `DR-74`'s rule — *a check may not report a negative it was not in a position to
establish* — which this repository wrote for `F133`, applied to `doctor`, and never swept across the
checker.** `SP038` is the case it missed.

**It also explains `F156`'s silence.** The wizard never claimed `local_hook`, and that omission was
load-bearing without anyone knowing: claiming it was unsafe, so the derivation that never claimed it
was accidentally protecting every adopter from a check that cannot hold in CI. `ACT-095` removed that
accidental protection for chained adopters a day before this was found — **a regression introduced by
the previous activity and caught by the decision this one answers.**

**Closed** by giving the hook three states where it had two. A hook that reaches the gate passes; a
hook that **is present and does not reach it** is still `SP038`, because that is a negative the check
genuinely establishes; **nothing at the resolved path at all** is reported as *not established*, in an
advisory line printed on every run so the control still says it ran. All three verified by effect.

**The honest cost, stated rather than implied.** A deleted hook and a fresh clone are
**indistinguishable from inside the checkout**, because the configuration that would tell them apart
is untracked. So this trades *catches a deleted hook, breaks every CI* for *never breaks CI, cannot
catch a deleted hook*. The local hook is one of three enforcement routes and the other two still run.

With `SP038` safe, the claim became safe: `local_hook` is now derived for `installed` **and**
`chained` — never for `declined` — so the control finally reaches the adopters it was built for.

## F156 — A chained install never declared its delegation, so `SP038` could not fire for anyone

**Severity: medium. Closed — `ACT-095` (`DR-83`), 2026-09-11.** Adjudicated from `F136`'s `PW-05`.

Reproduced at `HEAD` on a `--chain` install: every gate was written `enforcement: [history_audit,
review]` and **no `hook_chain` block was written at all**. `grep hook_chain surfaceplate/adopt/*.py`
returned nothing — the wizard had no concept of chaining — and `local_hook` appeared only as a
permitted enum value in `validators.ENFORCEMENT_VALUES` that nothing ever proposed.

**Wider than reported, and the wider form is the real finding.** Every one of the checker's hook
checks is gated on `"local_hook" in gate["enforcement"]` — `SP038` at two sites, and the staged-gate
check. `sections.DERIVED_ENFORCEMENT` was `["history_audit", "review"]` for **every gate of every
adopter**, so **no wizard-written profile has ever claimed `local_hook`**, and `DR-66`'s
verification-by-effect was unreachable through the documented adoption path for everybody, not only
for chained installs. The sweep reached it only by hand-editing a profile, which is why it read as a
`--chain` problem.

**Closed by `ACT-095`.** `discover.installed_hooks` reads the install record's own `hooks` value —
a fact about the tree, never a question, on `DR-73`'s reasoning. A chained install is asked one
thing: *why* it keeps its own hook system. `delegates_to` is derived, because the adopter chose to
chain and did not choose where this standard installs its gate — `DR-81`'s claim/clerk split, one
field along. Gates then claim `local_hook`, and `SP038` engages.

**Scope held deliberately.** A normal (`installed`) adoption still does not claim `local_hook`, so
this closes the chained case and leaves the wider one open as a decision: whether an adopter whose
hook *is* the standard's should claim it too. That is more assurance for every adopter and a larger
blast radius, and it is not an agent's call. **Recorded as `H24`.**

**Evidence — both directions, on a real repository.** With the chain declared and no delegating hook
in place, `SP038` fires naming the gate and the hook Git would actually run. With a delegating hook
at the *resolved* hooks path, it clears and the checker reports `PASS`. The first attempt at that
second half was wrong — a hook was placed in `.git/hooks` on a machine whose **global**
`core.hooksPath` means Git never looks there, and the checker correctly said so; the fixture was at
fault, not the check. `tests/test_adopt.py::test_a_chained_install_declares_the_chain_and_claims_local_hook`
asserts both directions plus the two negatives: an unchained profile carries no `hook_chain` key,
and is never asked the question.

**Three things the round-trip guard and the suites caught mid-implementation**, recorded because
each was a real defect in the first attempt: `test_provenance` refused the two new derived strings
until they were declared; the provenance **router** had no rule for `adoption.hook_chain.*` and the
real command failed where the suite had passed (the allow-list check and the router are different
mechanisms, and only the first had been updated); and `render_profile` did not write `hook_chain`,
so the round-trip guard refused to write anything — the same guard that caught `DR-81`'s re-render
flaw.

## F155 — `RECONCILIATION.md` could not be followed by an adopter who installed with pip

**Severity: low. Closed — `ACT-094`, 2026-09-11.** Adjudicated from `F136`'s `PW-13`.

Step 1 of the procedure — the first command an adopter runs when the installer has stopped — read:

```bash
diff .github/skills/change/SKILL.md ../surfaceplate/surfaceplate/standard/.github/skills/change/SKILL.md
```

That path assumes a clone of this repository sitting beside theirs. An adopter who installed with
`pip` gets `No such file or directory`, on the first step of the document they were sent to.

**Closed** by asking the installed package where its own copy is, which works for both install
routes. Step 6 is corrected in the same change: it said to note the reconciliation *"in the
application profile's decision record"*, and `adoption.decision_record_id` is a **pointer**, not
somewhere to write prose.

**`PW-13`'s other half was `F138`** and closed separately — there was no removal procedure at all,
and `surfaceplate uninstall` now exists.

## F154 — Three documented things that were not true

**Severity: low. Closed — `ACT-094`, 2026-09-11.** Adjudicated from `F136`'s `PW-17`, which bundled
four sub-claims; three were checked and confirmed here.

1. **`SP001`'s remedy named an internal script.** *"Run install_standard.py from the surfaceplate
   repository"* — a file a pip adopter does not have, sending them to a clone they have no reason to
   make. It now names `surfaceplate install --target <repository>`, the command the tool installs.
2. **The documented `pip install` resolves to `@main`, not a release.** Two people running the
   documented line a week apart may not get the same code. There is no versioned install to point at
   — the PyPI name is reserved and unused, and the published tags stop at `0.16.1` — so this is
   **stated** rather than repointed, with the commit-pinning form given for anyone who needs two
   machines to agree. Creating a release tag is a publication decision and is not one this change
   takes.
3. **The install block stops on a machine with a global `core.hooksPath`** and did not say what to
   do about it. `doctor` predicted it; the block then ran `install`, which refused. The two supported
   answers (`--chain`, `--no-hooks`) are now named at the point the reader meets the problem.

## F153 — `RECONCILIATION.md` claimed the standard owns files it does not

**Severity: low. Closed — `ACT-094`, 2026-09-11.** Adjudicated from `F136`'s `PW-14`.

The page said *"The standard owns fixed paths: `.github/instructions/*.instructions.md`"* — a glob,
which claims every file in the directory. The installer owns only its **twelve named topic documents
and seven named skills**, per channel: an adopter's own `team.instructions.md` is neither overwritten
nor listed as a conflict.

**The behaviour was always the narrower and better one; only the page was wrong** — which is the
uncomfortable direction, because an adopter who believed it would have moved a file that never
needed moving, on this document's authority. Corrected to a table of what is actually owned, with
`surfaceplate install --dry-run` named as the authority over any sentence in the page. The Claude
channel, which the page omitted entirely, is included in the same correction.

## F152 — Code below a module's entry point is unbound when the file runs as a script

**Severity: medium. Closed — `ACT-094`, 2026-09-11.** Found in this session while fixing `F151`, not
reported by the sweep.

`ACT-081` appended the removal section — `uninstall`, `_prune_empty`, some 125 lines — **below**
`install_standard.py`'s `if __name__ == "__main__": raise SystemExit(main())`. Imported, the module
executes fully and everything binds. Run as a script, `main()` is called before the interpreter
reaches those lines, so they do not exist.

**It showed no symptom for two reasons, and both are the interesting part.** `uninstall` is only
ever reached by import (`surfaceplate uninstall`), so it always worked. And the file reads perfectly
normally: **the defect is a relationship between two line numbers, not anything wrong at either
one**, so no amount of reading either function finds it.

It surfaced when `install()` — which *is* run as a script — first called `_prune_empty` as part of
`F151`'s fix: `NameError: name '_prune_empty' is not defined`, **after one file had already been
deleted**. A half-completed removal is the worst shape this could have taken.

**Closed** by moving the entry point to the end of the file, where it belongs, and by
`tests/check_code_registers.py::nothing_is_defined_below_the_entry_point`, which refuses any
definition below that block in any shipped module. Verified against the version that carried the
defect: it reports both `uninstall` and `_prune_empty`.

**This also corrects a verification failure of my own, recorded because the shape matters.** `F151`
was reported here as fixed and verified — *"0 empty directories"* — from a run that had **crashed**.
The check grepped for `remove` lines and counted empty directories without reading the exit code, so
"no empty directories" meant "it died before making any", not "it pruned them". A negative finding
must establish that the observation was capable of succeeding, and that one was not.

## F151 — Declining an agent channel left empty directories and misstated why

**Severity: low. Closed — `ACT-094`, 2026-09-11.** Adjudicated from `F136`'s `PW-15`.

Worse at `HEAD` than reported: **eight** empty directories, not two — `.claude/rules` plus seven
empty `.claude/skills/<name>` folders. An empty `.claude/rules` reads as *"the standard is installed
here"* to anyone looking, and to any tool that tests a path rather than its contents.

And the message was wrong. Every removal printed `(no longer part of the standard)`, which for a
declined channel is simply untrue: `.claude/rules/surfaceplate-01-authority.md` is still very much
part of the standard — it is no longer part of *this repository's chosen channels*. An adopter
reading that line and later wondering where Topic 1 went has been told the wrong thing about their
own repository.

**Closed** by distinguishing the two causes in the output, and by reusing `_prune_empty` — the same
function `uninstall` already used, which stops at anything the adopter still owns. Verified in both
directions: nineteen files removed with no directory left behind, and an adopter's own `NOTES.md`
and `skills/ours/SKILL.md` untouched with their directories intact.

## F150 — The answers record never said what kind of value a control's reference takes

**Severity: medium. Closed — `ACT-094`, 2026-09-11.** Adjudicated from `F136`'s `PW-10`, first half.

The record's `choices:` block told an adopter that `gates.<id>.artefact` wants *a file git tracks in
this repository*, and said **nothing at all** about `controls.contract_tests.implementation_reference`
or `controls.deterministic_tests.implementation_reference`, which want something else entirely: the
name of a step in a CI workflow. The only place that was written down was `adopt/validators.py`. The
record's own header says *"complete them all"*.

**`F144` made this bite harder, and that interaction is the uncomfortable part.** Since a CI step is
proposed only where its name says it runs tests, the two test controls are now left blank far more
often than when this was reported — so the fix in `ACT-087` increased the reach of this defect.

**Closed** generally rather than for the two reported fields: the sentence is keyed on
`FieldSpec.context`, which `DR-51` (4) already maintains for exactly this purpose, so all four
control patterns and the scanner field gained one and a new picked field inherits it by carrying a
context. `tests/test_adopt.py` asserts the property over every field answered by picking, not over
the two that were reported.

## F149 — `doctor` died on a narrow terminal, and it is the command for reporting problems

**Severity: medium. Closed — `ACT-094`, 2026-09-11.** Adjudicated from `F136`'s `PW-11`.

Both `doctor` and `doctor --report` crash with
`UnicodeEncodeError: 'ascii' codec can't encode character '…'` when stdout cannot represent the
truncation ellipsis in the digest columns. Reached by `PYTHONCOERCECLOCALE=0` or `PYTHONUTF8=0` on an
ASCII locale; plain `LANG=C` is coerced by Python and was never affected.

**The failing command is the one `SUPPORT.md` tells people to run when something is already wrong**,
so the diagnostic died exactly where it was needed.

**Fixed at the boundary, not at the nine glyphs.** The glyph is not the defect: any future one would
reintroduce it, and a rule that must be remembered at every print site is a rule that will be
forgotten at one. The CLI entry reconfigures stdout and stderr with `errors="replace"`; a decoration
degrades to `?` and the output survives. A report a human can read imperfectly beats a traceback they
cannot use at all.

**A verification note worth keeping.** The first check of this reported `rc=0` and looked clean —
because the command was piped to `tail`, which returns its own exit status. The crash was real and
the check could not see it.

## F148 — The documented way to work on the standard does not work

**Severity: medium. Closed — `ACT-094`, 2026-09-11.** Adjudicated from `F136`'s `PW-06` — and
**independently rediscovered in this session before the report was re-read**, which is the strongest
form of corroboration available here.

`README.md`'s *"Working on the standard itself"* block creates a virtual environment with
`pyyaml jsonschema` and then runs `tests/test_install_and_check.py`, which asserts that `adopt`
without a terminal exits 3 naming `--propose`. On an interpreter with no `textual` the command exits
2 saying the dependency is missing instead — a different, also-correct answer to a different
question. The suite fails, and `scripts/build_release.py` then refuses to build on it.

So the first and only documented path for a contributor ends in a failing suite and a refused build,
with nothing in the block explaining why. This is the standard's own `S3` — a documented path that
cannot be completed as documented — in this repository's own README.

**Closed** by installing `textual` in that block, pinned to match `pyproject.toml`'s `adopt` extra,
with the reason stated inline: it is optional for *using* the standard and not optional for
*checking* it. `tests/check_code_registers.py` already compares pins in `README.md` against
`pyproject.toml` (`F130`), so the two cannot drift.

## F147 — A discovered list was offered as the only permitted answer

**Severity: high. Closed — `ACT-093` (`DR-82`), 2026-09-09.**

Found by the maintainer, driving the wizard by hand against `A-stranger`, a real 30-document
repository. At the `prerequisite_state_ui` gate: *"I only see as options for files the ACTIVITY XXX
ones. No options for creating new file."*

Reproduced exactly:

```
total candidate artefacts: 30
prerequisite_state_ui   matched: []          seed: (none)
                        offered: activity/ACT-001.md … activity/ACT-012.md   (12 rows)
```

**Three faults, one class.**

1. **No answer could be given that was not on the list.** `plan._from_candidates` set
   `kind="select"` whenever discovery found anything, and a Textual `Select` cannot be typed into.
   `prerequisite_state_ui` is one of the four interface gates `scaffold.SEEDABLE` deliberately
   excludes (`DR-55`), so there was no *"create it"* row either. The only exits were to declare the
   gate `not_applicable` — a different answer from the true one — or to abandon the run.
2. **The offer was truncated and the count misstated it.** `discover.SHOWN` cut 30 candidates to 12
   while the dropdown read `Choose precondition artefact (12 found)`. Thirty were found.
   `activity/register.md` — the repository's actual governance artefact — sat at index 16, behind
   sixteen `activity/ACT-nnn.md` files, and was never shown.
3. **A second, undeclared cap made the first invisible.** `rank_for_gate` cut to `SHOWN` as well as
   `_from_candidates`, whose own comment claimed to be the only cut (`F75`). With the total already
   discarded upstream, the field could not have reported what it was hiding even had it tried.

**The class: the widget's rule was stricter than the standard's, and the standard's rule was
already enforced elsewhere.** Nothing in the model held the constraint the interface imposed —
`flow.py` never checks an answer against `spec.choices`, and every field `_from_candidates` builds
carries a validator that re-checks the repository independently (`tracked_path` requires the path to
exist, be tracked, be non-empty, carry no placeholder and not be one this framework installed;
`ci_step` and `scanner_workflow:<name>` likewise). So **a scripted adoption (`--answers`) could
always name any tracked file, and a human at the keyboard could not.**

`DR-38` decided *never offer something that isn't there*. What shipped was *never accept anything
else* — a different and much stronger rule, which nobody decided and no record states.

**Why no suite could see it.** `test_adopt_matrix.py` walks every reachable decision — 208 cases,
44,774 checks — through `flow`, and never renders a widget. `test_adopt_tui.py`'s `F143` invariant
asserts every field is *displayed and reachable*; neither of those is *answerable*, and the gap
between them is exactly where this lived. The same blind spot as `F143`, one layer along.

**A second defect fell out of the same code.** `_widget_for` silently dropped a pre-filled value
that was not among the choices, so `adopt --edit` on a hand-maintained profile lost an off-list
artefact path and re-asked for it as though it had never been given.

**Closed by `ACT-093` (`DR-82`).** Every dropdown carries `plan.TYPE_A_PATH`, a row that reveals a
text box; the field's own validator still rules, so a typed path that does not exist is refused in
the checker's own words. The count states both numbers whenever they differ. `rank_for_gate` ranks
and no longer cuts.

**`SHOWN` stays at 12, and the reasoning is recorded because raising it was proposed and
declined.** The agent recommended 40 on the stated ground that 12 had been sized for an 80×24
terminal. **That ground was wrong**: `F38` set it at twelve on this maintainer's own Plutos
evidence — *"too many options to know which one is the right one"*, about forty candidates.
Measurement then settled it against both positions: the four trial repositories hold 30, 186, 239
and 267 candidates, so forty would have shown all of one and 40 of 267 on another — moving the
truncation rather than removing it, while re-creating the complaint that set the number. Keyword
ranking does not rescue it either: `work_registration`'s keywords match 205 of 239 candidates on
`B-no-deps`. **No cap is the mechanism for naming a file the list omits; the escape row is.**

## F146 — An upgrade guarantees two findings the adopter must fix by hand

**Severity: medium. Closed — `ACT-092` (`DR-81`), 2026-09-09.**

Observed on the maintainer's walkthrough, upgrading a real adopter from `0.16.0` to `0.18.0`. The
installer reports `keep governance/application-profile.yaml (yours; never overwritten)` — correct,
and then the very next command says:

```
[SP048] adoption.framework_version is 0.16.0, but .standards/INSTALL.json records 0.18.0
[SP049] adoption.framework_digest is 7d5b7a44…, but the installed standard anchors to 84aa014d…
```

**Every upgrade produces exactly these two, every time**, and the adopter clears them by hand-copying
a 64-character digest out of a JSON file. The installer knew both values; it wrote them into the
profile at first install, from the template, and declines to touch them afterwards. This session hit
it twice on this framework's own repository.

**Why it is not simply a bug to fix.** The two fields are arguably *not* decisions — they are the
installer's own record of what it installed — which argues for re-pinning them automatically. But
`DR-45` gives `framework_digest` a stronger reading: it is **the adopter's claim** about which
distribution they assessed against, and `SP049` exists to catch a profile claiming an install that
is not present. On that reading, re-pinning silently would let a version change through without
anyone re-reading the profile, which is the assertion `review_by` exists to make.

**Three routes, none applied:**

1. **The installer re-pins both fields on upgrade and says it did.** Removes the friction entirely.
   `SP048`/`SP049` still catch a hand-edited profile, which is the case they are actually for.
2. **A `surfaceplate adopt --repin` (or an installer flag)** that does it on request. The adopter
   acts deliberately; the digest is never typed by hand.
3. **Leave it and document it** — the upgrade's "Next steps" names the two fields and where the
   values are, instead of the generic *"Complete governance/application-profile.yaml"*.

**Recommendation: (2).** It keeps `DR-45`'s reading — the claim stays the adopter's, made
deliberately — while removing the part that is merely clerical and error-prone. (1) is defensible
and quietly weakens an assertion; (3) leaves a guaranteed two-finding tax on every upgrade forever.

**Not decided here**, because it changes what a profile asserts and `DR-45` is the record it would
be read against.

**Closed by `ACT-092` (`DR-81`), 2026-09-09 — the maintainer chose route (2).**
`surfaceplate adopt --repin` reads `.standards/INSTALL.json` and sets both fields. **The act stays
deliberate and only the typing goes**: a person runs it, which is the assertion `DR-45` wants, and
nobody copies a 64-character digest by hand, which was never a claim about anything.

The sidecar records both as **`fact of record`, not `typed`** — the adopter chose to re-pin and did
not choose the value — with a reason naming what moved and where it was read from. Running it again
changes nothing and says so.

Verified on the real adopter that produced this finding: `WARN` with `SP048` and `SP049` → one
command → `PASS`.

## F145 — The fix stopped new bad references and left the existing one passing

**Severity: medium. Closed — `ACT-088`, 2026-09-09.**

`F144` stopped the wizard **proposing** a CI step whose name says nothing about tests. It did
nothing about the profiles already carrying one — and the only real adopter of this standard had
**two** controls credited to `Check out mnemosyne (shared generator lives there)`, written at
`0.16.0`, carried through the upgrade untouched, passing every run. `SP053` establishes that the
named step exists; `DR-25` fixes that boundary deliberately.

Verified as pre-existing rather than assumed: `git show HEAD:governance/application-profile.yaml`
carries the same two references, so the upgrade neither introduced nor repaired them.

**Remedy: the checker says so, as an advisory and never a failure.** The note that already reads
`contract_tests: verified against step 'X'` now adds a caution where `X` describes fetching,
preparing or shipping.

**Two lists, and the asymmetry is the whole design.** Proposing needs confidence the step **is** a
test, so a narrow positive list is right: a step it misses is asked for instead, and a question
costs nothing. Cautioning needs confidence the step is **not** one — and the same list read
backwards accuses the innocent. This framework's own contract-test step is called *"Validate the
control contracts"*, which contains neither *test* nor *spec*. **A checker that told its own author
a control was passing while not holding would be the false alarm that trains a reader to skim the
real one.** So the caution fires only on names that clearly describe something else, and ambiguous
names — *"Run activity/register.md --check"* — are left alone on purpose.

Both lists live in `rules.py`, so the wizard's filter and the checker's caution are one answer to
one question (`DR-48`).

## F144 — A control was verified against a checkout step

**Severity: high. Closed — `ACT-087`, 2026-09-09.**

Found on the maintainer's completed walkthrough, in the profile the wizard wrote. `deterministic_tests`
was recorded as:

```yaml
  deterministic_tests:  # checked against this repository by the conformance checker
    decision: required
    rationale: Outputs must be reproducible before they can be reviewed.
    implementation_reference: Check out mnemosyne (shared generator lives there)
```

and the checker then reported `deterministic_tests: verified against step 'Check out mnemosyne
(shared generator lives there)'`. **A repository credited with deterministic tests on the strength
of a `git checkout`.** The provenance sidecar records the value's origin as `discovered` — the tool
presented it as a fact about the repository, not as a question.

The workflow held eleven steps. Not one of them ran tests, and the one proposed was not even the
plausible candidate (`Run activity/register.md --check`) but the second of four checkouts.

**Cause, and it is the same gap for the third time.** `defaults.propose_controls` filters proposals
per pattern: pattern A by a word match (`F40`, `F84`), pattern C by schema fit (`F93`) — and
**pattern B by nothing**, so the first CI step discovered was proposed. `F93` wrote the sentence
about pattern C: *"`DR-51` (5) applied the checker's rules to artefacts and scanner workflows;
`DR-54` (2) applied a name match to pattern-A references; pattern C was left with neither."* It was
then true of pattern B, and stayed true through two more releases.

**Reach: high, and it is the ordinary case rather than a corner.** `deterministic_tests` and
`contract_tests` are both pattern B and both in the `standard` floor, so this reaches every adopter
at `standard` or `full` who has any CI workflow at all.

**Remedy.** A CI step is proposed only where its **name says it runs tests**
(`plan.TEST_STEP_WORDS`), and within those, the control's own words rank first
(`plan.CONTROL_STEP_WORDS`) — `F84`'s rule, *"the name matches first, as the gates do"*. Without the
second half both test controls took the same first matching step, so a repository with a
"Run the contract tests" and a "Run the unit tests" was offered the contract one for
`deterministic_tests`: a test step, and still the wrong test step.

**Deliberately narrow, and the safe direction is to propose nothing.** A step this misses is
**asked** for instead, which is exactly what pattern A does when its word match finds nothing.
Asking is never the failure mode that puts a wrong answer into a profile under the word
*"discovered"*. Every step remains **offered** — only the proposal is filtered.

**Verified in both directions.** The maintainer's repository proposes nothing for either control and
still offers all eleven steps; a repository with real test steps gets each control its own.

## F143 — The wizard demanded a value for a field it did not show

**Severity: high. Closed — `ACT-086`, 2026-09-09.**

Found by the maintainer on the next screen after `F142`, and unrelated to it. Ticking any control in
the above-floor list made its rationale and implementation-reference **required** and left them
**invisible**: `Ctrl+S` refused the section for their being blank, and no key could reach them. The
report was *"blocked again"*, and it was exact — there was no progressing.

**Established by effect before being explained.** Driving the real interface with real keypresses:
after `space` on `method_registry`, `row-method_registry--rationale` and
`row-method_registry--implementation_reference` are both `display=False`, and the screen's focus
chain holds six widgets, none of them those. Tab from the list goes to the scroll container and
then wraps to the first field.

**Cause, read after it was measured.** `FormScreen._on_change` is decorated
`@on(Checkbox.Changed)`, `@on(Input.Changed)`, `@on(RadioSet.Changed)` — and **not**
`@on(SelectionList.SelectedChanged)`. It is the one widget on that screen whose answer reveals
other fields. `FieldSpec.applies` had already been generalised for it, with a comment explaining
that *"depends on that field"* means *"is among what was ticked"* for a multiselect: **the plan side
was finished and the screen was never wired to the event.**

**Why nothing caught it, and it is the same boundary three findings running.**
`tests/test_adopt.py` and `tests/test_adopt_matrix.py` answer the plan directly — a
`ScriptedInterview` never renders a row, so a row that is never shown is invisible to 45,000 checks.
`F132` was a repository shape no fixture had; `F142` was an offer no test tried to take; this is an
event no scripted path emits. **The suites cover what the wizard decides and not what it displays**,
and every one of the three was found in minutes by a person using it.

**Remedy.** `SelectionList.SelectedChanged` is added to the handler, and to the gates screen's
equivalent — where no field depends on a multiselect today, so it changes nothing now and stops the
two screens differing in a way the next conditional field would have to rediscover.

**Verified in both directions.** With the handler, the rows display, both fields enter the focus
chain, and Tab from the list lands on the first of them. With it removed again the new test fails,
naming the two rows and their `display=False` — the state the maintainer was looking at.

## F142 — An option that cannot be completed is not an option

**Severity: high. Closed — `ACT-085`, 2026-09-09.**

Found by the maintainer on the **third screen of the walkthrough**, one day after `F132` was closed,
on the same repository — and this one is the framework's own doing rather than an old defect
resurfacing.

`DR-73` lifted the `dependency_lock` **floor** for a repository that declares no dependency
manifest, and deliberately kept the control **offerable** above the floor, on the principle that
*a waiver removes an obligation, not an option*. **The principle is right. The consequence was not
checked.** Ticking the offer asks for its `implementation_reference`; `SP051` requires that file to
exist, be non-empty and be tracked; and on such a repository there is nothing to name. The offer
dead-ends on the same screen, in the same way, as `F132` did before `DR-73` — the maintainer's
report was verbatim *"I can't progress"*, twice, one day apart.

**The test that should have caught it is the one I wrote for `F132`.** It asserted the control was
still *offered* above the floor, and that its fields were gated behind the `above_floor` tick. Both
were true. **It never asserted the offer could be taken.** Asserting that a door exists is not
asserting that it opens, and the gap between those two is exactly where this lived.

**Remedy — the mechanism already existed.** `F97`/`DR-59` built exactly this for
`documentation_authority` at `essential`: a control the checker verifies through a gate the level
does not declare is **withheld from the list, and the help says why**. `dependency_lock` on a
repository with no manifest is now withheld the same way, with its own reason — including the part
that makes it a state rather than a refusal: *"Add one — a `package.json`, a `pyproject.toml`, a
`go.mod` — and the control returns on its own, with no edit here."*

That the mechanism was already there, and was not reached for, is the more useful half of this
finding. `DR-73` reasoned about whether the control should remain *available* and never asked what
taking it would do.

**Verified in both directions**: the no-manifest repository does not offer it and says why; the
repository with a `package-lock.json` still has it **required in the floor**, which is a different
exclusion from the same list for the opposite reason.

## F141 — A downgrade was announced as an upgrade

**Severity: medium. Closed — `ACT-083` (`DR-78`), 2026-09-09.**

From the pathway sweep (`PW-08`). Installing over a newer recorded version printed
`NOTE: this is an UPGRADE, 99.0.0 -> 0.17.0, not a restore.` **The tool noticed the difference and
not its direction**, and then replaced the newer files with older ones while saying the opposite of
what it was doing.

`doctor` had the matching half: its *"tool vs installed"* line printed `both 0.17.0` — true of the
**digests** — while the currency line two rows below printed `installed 99.0.0`. Two different
installed versions in one run, neither wrong on its own terms.

**Remedy.** The installer orders the versions with `rules.currency_state`, the same comparison the
currency check uses (`DR-72`), so this payload has one answer to *"is 0.9.0 newer than 0.17.0"* and
not two. A downgrade says `a DOWNGRADE`, and adds what installing anyway would do. `doctor` reports
the disagreement rather than picking a side: the digest is the reliable half, and a recorded version
that contradicts it has been edited or written by something else — which `SP005` already catches.

Both directions asserted: an older recorded version still reads as an upgrade.

## F140 — An edit with no reason was recorded as though it had one

**Severity: medium. Closed — `ACT-083` (`DR-78`), 2026-09-09.**

From the pathway sweep (`PW-07`). `adopt --edit` without `--because` was accepted, and the
provenance sidecar gained `reason: edited after the write with \`surfaceplate adopt --edit\``. The
CLI then said the change was recorded *"with the reason"*.

That is a sentence in a governance record that **reads like a reason and is not one** — the exact
objection `SP031` makes to a gate deferred without a reason, and `DR-72` restates about
`currency_check`: *an unexplained value is an omission wearing a decision's clothes*. This framework
was making it about itself, in the record it asks adopters to trust.

**Remedy, and where it lives is the point.** The invariant is *"an edit to a governance profile is
recorded with a reason"*, so it belongs with the **writer** — `wizard.edit` refuses a blank or
whitespace reason — and not only in the argument parser, where it would bind one caller out of
however many there turn out to be. The CLI keeps a friendlier message and exit 3 for the usage
case. The fallback string, now unreachable from the CLI, says `NO REASON GIVEN` rather than
impersonating one.

**Two existing tests had to supply a reason** to keep testing what they are named for — they
exercise *other* refusals and would otherwise all stop at this one. That is supplying a
now-required argument, not weakening a test, and it is noted in both.

## F139 — An internal error where a refusal belongs

**Severity: medium. Closed — `ACT-083` (`DR-78`), 2026-09-09.**

From the pathway sweep (`PW-12`). `adopt --edit` against the **installer's template profile** —
the documented alternative to running the wizard — ended as
`The wizard could not finish: KeyError: 'scanner'`, exit 4.

`--edit` re-renders the whole file, so it needs the shape `adopt` writes; the template does not
carry a `scanner` block. **The adopter did nothing wrong, and an internal error tells them nothing
about what to do instead** — it also leaves a draft and invites a resume that will fail the same way.

**Remedy.** The renderer's `KeyError` becomes a `WriteRefused` naming the missing block, explaining
that `--edit` re-renders the whole file, and saying the two things that do work: edit the file
directly, or run `adopt` so it is written from answers first.

## F138 — There was no way to remove the standard from a repository

**Severity: medium. Closed — `ACT-081` (`DR-75`), 2026-09-09.**

Raised from the pathway sweep (`PW-13`) and adjudicated here. **The absence of an answer is the
finding**: there was no `uninstall` command, no installer flag, and no document anywhere describing
how an adopter takes this standard back out. Established rather than assumed — the search that
found nothing did find the installer's own *"remove … (no longer part of the standard)"* line, so it
was capable of finding a removal path had one existed.

**Why it is worth more than its severity suggests.** This programme's stated purpose is that the
product be adoptable by strangers. A standard a repository cannot leave is a harder thing to adopt
than one it can, and *"you can get out"* is part of what makes *"try it"* a reasonable ask. It also
had a sharper edge here: every installed file is integrity-checked, so an adopter who deleted them
by hand would fail their own conformance check on the way out.

**Remedy — `surfaceplate uninstall [--target] [--dry-run]`.**

**The install record is the authority, not the current payload.** `.standards/INSTALL.json` already
recorded every file the installer wrote, with its digest. Removal reads that, so it takes out
exactly what was installed — including files a newer payload no longer ships, and excluding
anything the adopter added since. Deriving the list from `build_payload()` would have deleted by
guess.

Three things are never removed, and each is stated in the output rather than left to be noticed:

- **The adopter's own content.** `AGENTS.md` and `.github/copilot-instructions.md` have the managed
  block stripped and keep everything else, verbatim.
- **`governance/application-profile.yaml`.** Their control decisions are theirs, not this
  framework's, and nothing here deletes the record of what they decided.
- **Anything not in the record.** A file the standard never wrote is never touched.

`core.hooksPath` is unset only where it points at `.githooks`. A file edited since install is
removed — it is standard-owned by contract — but is **named in the report**, so anything of theirs
that ended up inside it can be recovered from git.

**Verified by effect**, 17 checks: every recorded file gone and `.standards/` with it; the
adopter's source, manifest, profile and their own words in `AGENTS.md` all intact; the checker then
reports not-installed with exit 2; removing what is not there is exit 2 rather than an error; and
the standard installs again afterwards. `INSTALL.md` and `SUPPORT.md` now say so, which is the half
`PW-13` was actually about.

## F137 — The natural completion of a shipped template is invalid

**Severity: medium. Closed — `ACT-081` (`DR-75`), 2026-09-09.**

Raised from the pathway sweep (`PW-09`), and **larger than reported** once adjudicated here.

The shipped gate-exception template says `raised_on: replace-me  # YYYY-MM-DD`. An adopter who does
exactly that writes `raised_on: 2026-09-09`, which is a valid YAML date scalar, which
`yaml.safe_load` returns as `datetime.date`, which the schema rejects:

```
[SP043] Gate exception '...' is invalid: raised_on: datetime.date(2026, 9, 9) is not of type 'string'
```

**The template warns about quoting a SHA and not about quoting a date**, and that asymmetry is the
tell: the case was thought about once and not generalised.

**What the sweep did not reach: the application profile has the same trap.** Confirmed here —
setting `adoption_date` to an unquoted date produces
`adoption.adoption_date: datetime.date(...) is not of type 'string'`. That is the path of an adopter
who fills the profile template **by hand**, the documented alternative to running the wizard. The
wizard's own output is unaffected, because it quotes; so the defect fell precisely on the adopter
who did it the manual way, and the fixture-based suites never saw it.

**Remedy: normalise, do not merely document.** `rules.dates_as_strings` converts `date`/`datetime`/
`time` to ISO 8601 text, applied at all four points where the checker loads a hand-written YAML
record — immediately after parsing, before anything looks at it. Nothing is lost: a `datetime.date`
can only have come from a date-shaped scalar, and `.isoformat()` is exactly the value the schema's
`format: date` wanted.

**The templates are deliberately left unquoted.** Quoting them would work and would rely on the
adopter reading a comment; the normaliser does not. The `commits:` entry keeps its quoting warning,
because that one is a different defect — an all-digit SHA prefix parses as a number — and is not
fixed by this.

## F136 — The pathway sweep's remaining fifteen findings, held pending adjudication

**Severity: medium (the holding entry; individual severities below are the reporter's).
Closed — `ACT-094` and `ACT-095`, 2026-09-11. All ten remaining were adjudicated by reproduction
against `HEAD`; eight stand and carry their own codes, two were refuted.**

### The adjudication, 2026-09-11

| | Claimed | Verdict at `HEAD` | Now |
|---|---|---|---|
| `PW-05` | medium | confirmed, **wider than reported** | `F156` |
| `PW-06` | medium | confirmed, **rediscovered independently** the same day | `F148` |
| `PW-10` | medium | **split** — first half confirmed, second refuted | `F150` |
| `PW-11` | medium | confirmed | `F149` |
| `PW-13` (reconciliation half) | low | confirmed | `F155` |
| `PW-14` | low | confirmed | `F153` |
| `PW-15` | low | confirmed, **worse than reported** | `F151` |
| `PW-16` | low | **refuted** | — |
| `PW-17` | low | confirmed (3 of its 4 sub-claims checked) | `F154` |
| `PW-18` | low | confirmed | `H25` |

**The two refutations are recorded here and issued no code, deliberately.** A finding that was never
true of this repository is not a finding of this register; a number issued and closed the same day
would sit in the sequence forever describing a non-defect, indistinguishable on inspection from the
eight that are real. That is the property this holding entry was created to protect, and it paid:
adjudicating rather than transcribing removed two entries that would otherwise have been permanent.

- **`PW-16` — refuted.** It described `--propose` substituting silent defaults where the record said
  `needs-human`, and an empty-list sentence. At `HEAD` `risk.data_classification`,
  `relied_on_outside_team` and `material_quantitative_output` all read `needs-human` with explicit
  option notes, there is no empty-list sentence and no double full stop. **The preview it describes
  no longer exists** — `--propose` writes an answers record instead. Fixed by later work
  (`ACT-081`/`DR-75`'s neighbourhood) without anyone connecting the two.
- **`PW-10`, second half — refuted.** *"A gate answered `not_applicable` still demands an artefact
  path."* Replayed with five gates `not_applicable` and every one of their artefacts blank: the
  profile wrote cleanly and `check_conformance` reported `PASS`. The first two attempts at this
  refused on `controls.scanner.wired_in` and `dependency_lock` — confounds in the fixture, not the
  finding — and neither refusal ever mentioned a gate artefact.

**`PW-18` is confirmed and not fixed here**, because the fix changes audit semantics rather than a
document: `git log --since=<instant>` is inclusive at second granularity, so a commit made in the
same second as `effective_from` falls inside the audit window and is judged as crossing the gate.
Verified directly — `--since` at a commit's exact instant returns it, one second later returns
nothing — and this repository's own matrix fixture already back-dates its commits *"so a gated
commit made in the same second as a seed's instant never reads as crossing a gate"*, a workaround
for exactly this, in this tree. Narrowing the window is a change to what every adopter's history
audit examines. **Recorded as `H25`.**

### The original entry, as raised

**Raised 2026-09-09.**

`audit/PATHWAY_SWEEP_REPORT_2026-09-09.md` reports eighteen findings from 35 scenarios executed by a
separate session against `30bba44`, with raw logs under
`audit/validation/pathway-sweep-2026-09-09/`. Three were adjudicated here and carry their own
numbers — `F133` (`PW-01`), `F134` (`PW-02`), `F135` (`PW-03`). **The other fifteen are recorded, not
verified.**

**Why one entry and not fifteen.** Writing fifteen bodies from a report this session has not
reproduced would put unverified claims in this register at the same status as verified ones, and the
register's whole value is that a reader cannot tell them apart only by looking harder. Each becomes
its own `F<n>` when it has been reproduced or refuted here, and this entry closes when the last one
has. **The claimed severity below is the reporter's, not this register's.**

**A standing caveat on all fifteen: they were observed against `30bba44`, and `ACT-078` landed
after.** Anything touching `dependency_lock`, the `essential` floor, or `control_decisions` may have
moved. Re-testing against `HEAD` is part of adjudicating each, not an optional extra —
`PW-03`'s two halves already behaved differently before and after that commit.

| | Claimed | Reported |
|---|---|---|
| `PW-05` | medium | Under `--chain`, `adopt` proposes no `local_hook` enforcement, so a declared `hook_chain` is never verified and `SP038` cannot fire |
| `PW-06` | medium | `README.md`'s "Working on the standard itself" block fails as written: its venv lacks `textual` and `build_release.py` then refuses |
| `PW-10` | medium | The answers record does not say that `contract_tests`/`deterministic_tests` want a *workflow step name*; a gate answered `not_applicable` still demands an artefact path |
| `PW-11` | medium | `doctor` crashes with `UnicodeEncodeError` when C-locale coercion is disabled |
| `PW-13` | low | `RECONCILIATION.md` cannot be followed literally by a pip adopter. **Its removal half left this table as `F138`** |
| `PW-14` | low | `RECONCILIATION.md` overstates what the standard owns under `.github/instructions/` |
| `PW-15` | low | Changing `--agents` leaves empty `.claude/rules` and `.claude/skills` directories |
| `PW-16` | low | The `--propose` preview substitutes silent defaults for undecided answers |
| `PW-17` | low | Documentation drift in the install block, `SP001`'s `fix`, and the documented `pip install` resolving to `main` rather than a release |
| `PW-18` | low | The history audit's window includes commits made in the same second as `effective_from` |

**`PW-04` has left this table.** It was adjudicated with `F133` under `DR-74` as an instance of the
same class — a negative asserted from an observation that could not have found the thing — and
`doctor` now reports an unanswerable hooks path as unanswerable. `PW-09` has left it as `F137`, and
`PW-13`'s removal half as `F138`, and `PW-07`, `PW-08` and `PW-12` as `F140`, `F141` and `F139`.
**Ten remain**, `PW-13`'s reconciliation half among them.

*(This sentence said "nine" until it was counted. The table below is the authority and the prose was
wrong — which is the defect this register exists to catch, so it is corrected in place and the
error noted rather than quietly overwritten. `check_code_registers.py` counts `F` codes and `SP`
codes and does not count these, because they are not codes this register has issued.)*

**Two of these deserve flagging now, before adjudication, because they are not what their severity
suggests.** `PW-13`'s second half — *no removal procedure exists anywhere* — is the packet's own
"the absence of an answer is the finding", and it is an adoption question rather than a defect: a
standard a repository cannot leave is a harder thing to adopt than one it can. And `PW-04` is the
same shape as `F133` one layer out: a diagnostic reporting a negative it was not in a position to
establish.

## F135 — A dependency manifest is offered, and accepted, as a dependency lock

**Severity: high. Closed — `ACT-080` (`DR-74`), 2026-09-09.**

Two halves, both confirmed against `HEAD` (`0d5612e`) by the maintainer's session rather than taken
from the report.

**`discover._LOCK_FILES` contains `pyproject.toml`.** Read directly:

```
('requirements.txt', 'requirements.lock', 'poetry.lock', 'Pipfile.lock', 'package-lock.json',
 'yarn.lock', 'pnpm-lock.yaml', 'Cargo.lock', 'go.sum', 'gemfile.lock', 'pyproject.toml')
```

A `pyproject.toml` is a **manifest**: it declares dependency *ranges*. A lock file records the exact
resolved versions. The wizard therefore proposes it — the sweep observed `value: pyproject.toml /
origin: discovered / detail: 'found: pyproject.toml'` — and, because it was *discovered* rather than
asked, the adopter is shown it as a fact about their repository rather than a question. `SP051` then
confirms the file exists, is tracked, is non-empty and holds no placeholder, and the control reports
verified. **Nothing at any point asks whether the named file pins anything.**

`requirements.txt` sits in the same list and is genuinely ambiguous — often a pin file, often a
range list. `pyproject.toml` is not ambiguous.

**The second half: `SP051` accepts any tracked non-empty file.** The sweep completed a record with
`controls.dependency_lock.implementation_reference: docs/guide.md` and the checker printed
`dependency_lock: verified against docs/guide.md` and `PASS`. `DR-25` records that boundary as
permanent and deliberate — this framework checks that a named artefact exists, never that its
contents are honest — so this half is **not** a defect against the design. What is a defect is the
combination: a control whose evidence is unconstrained *and* whose value is proposed as discovered.
One or the other is defensible; together they mean the tool can put the wrong file in front of an
adopter, call it discovered, and then verify it.

**`DR-73` makes it sharper, and this is the part that must be fixed regardless of anything else.**
`rules.dependency_manifest` — added yesterday — classifies `pyproject.toml` as a **manifest**, and
`discover.candidate_lock_files` classifies it as a **lock**. Two modules in one payload answer the
same question about the same file two different ways. That is precisely the drift `DR-48` created
`rules.py` to prevent, and it was introduced by the change that closed `F132`.

**Not yet remedied.** The narrow fix — remove `pyproject.toml` from the lock list, and reconcile the
two classifications in `rules.py` — is available and small. Whether `SP051` should also constrain
what *kind* of file a lock may be is a larger question against `DR-25`, and is the maintainer's.

**Closed by `ACT-080` (`DR-74`), 2026-09-09**, on the narrow fix, and **not** by banning the file.
`rules.LOCK_FILES` is now the single list and `pyproject.toml` is not in it, so a repository whose
only pins are in its manifest is **asked** rather than told. It remains typeable, because naming it
can be correct — this repository names it, and is right to: its dependencies are pinned exactly
there and it has no separate lock. A name cannot distinguish a `pyproject.toml` that pins from one
that declares ranges, and a tool that cannot distinguish them must ask.

**`SP051` is deliberately unchanged**, so naming a Markdown page still passes. `DR-25` records that
boundary as permanent. What is fixed is the tool proposing the wrong file as a *discovered fact*;
what an adopter deliberately declares remains theirs.

## F134 — A refused `--answers` replay writes a draft while saying nothing was written, and the draft then blocks the corrected record

**Severity: high. Closed — `ACT-080` (`DR-74`), 2026-09-09.**

The documented `--propose` → complete → `--answers` path cannot be completed after one wrong answer,
and the message that results is about a value the adopter has already corrected.

**Half one, confirmed independently.** A refusal prints:

> `This is the wizard's own safety check, not the checker. Nothing was written.`

and `.standards/adopt-draft.json` is on disk immediately afterwards. Reproduced from a clean start in
the maintainer's session: install, `--propose`, complete the record with one path that does not
exist, replay → refused with that text → `ls .standards/adopt-draft.json` → present. **The sentence
is false**, and it matters because the file it denies writing is the one that changes the next run.

**Half two, confirmed on the sweep's controlled isolation.** In `a1-repro2` the *only* thing that
changed between a failing run and a passing one was the draft:

```
--answers answers-ii-nonexistent.yaml        → refused: "Nothing exists at that path"; draft written
--answers answers-iii-tracked-nonmanifest.yaml → refused with answers-ii's error, about a path
                                                  answers-iii does not contain
rm .standards/adopt-draft.json
--answers answers-iii-tracked-nonmanifest.yaml → WRITTEN; checker PASS          (record unchanged)
```

The tool's own advice — *"Run `surfaceplate adopt --propose` for a complete record"* — does not clear
the draft, so following the instruction the refusal gives does not recover the situation.

**An attempt to reproduce half two in the maintainer's session did not show the difference, and that
is recorded rather than dropped.** That attempt's record still carried an unrelated genuine failure
(a blank gate artefact), so both runs failed for a real reason and the draft could never have been
the deciding variable. The observation was incapable of returning the other answer — the negative
result establishes nothing, which is the rule this repository applies to its own checks and applies
here to its own adjudication.

**Not yet remedied.** Two candidate treatments, neither chosen: do not persist the draft on a
refusal that wrote nothing else, or have `--answers` ignore any draft and read only the record it was
given. The second is probably right — a replay is meant to be a pure function of its record — but it
interacts with the resume-from-draft behaviour the interactive wizard depends on, which is why this
is recorded rather than patched in passing.

**Closed by `ACT-080` (`DR-74`), 2026-09-09**, with the second treatment: `wizard.run` takes
`use_draft`, and the `--answers` path passes `False`, so a replay neither reads nor writes a draft.
Not "clear it afterwards" but "never involve it" — a draft protects a human mid-interview from
losing an hour of answers, and a replay has nothing to protect, its answers already being in a file
the adopter wrote and still holds. The same reasoning that keeps `sections.build_profile` pure.
Verified on the sweep's own sequence: the refusal now leaves no draft, so its *"Nothing was
written"* is true, and the next replay's error moves on rather than repeating the last attempt's.

## F133 — The history audit treats the installed seed as a former name of the artefact scaffolded from it

**Severity: high. Closed — `ACT-080` (`DR-74`), 2026-09-09.**

**Confirmed by effect at `HEAD` in the maintainer's session**, reproducing from a clean start rather
than reading the report:

```
$ git log --follow --name-status --format= -- activity/register.md
C100    .standards/seeds/activity-register.md   activity/register.md

>>> historical_paths(repo, "activity/register.md")
['activity/register.md', '.standards/seeds/activity-register.md']

>>> blob_exists(repo, "HEAD", "activity/register.md")            False
>>> blob_exists(repo, "HEAD", ".standards/seeds/activity-register.md")   True
```

The scaffolded register is byte-identical to the seed it was copied from, and the copy lands in a
*later* commit than the seed. Git's copy detection reports `C100`; `F30`'s rename-following accepts
it; and the audit then treats presence under **any** historical name as satisfying the gate. The
artefact was deleted and a gated path changed, and the gate reports satisfied.

**What makes this high rather than a curiosity: the seed can never be deleted.** It is installed
payload under `.standards/`, integrity-checked, and an adopter who removes it fails `SP` integrity
instead. So this is not a former name that happens to still exist — it is a permanent alias,
guaranteed present, for every artefact `adopt` scaffolds: the activity register, the risk
classification, the decision log, the authority map, the test conventions, the data sources, the
output validation and dependency review documents, the release checklist.

**It falsifies a safety property the code states about itself.** `historical_paths`'s docstring
argues the function is safe because *"it only ever ADDS paths to look for, so it can clear a false
violation and can never hide a commit where nothing existed under any name."* For a scaffolded
artefact, something always exists under one of those names. The invariant does not hold, and the
docstring is the strongest available evidence that the case was not anticipated.

**And it makes a published claim false.** `INSTALL.md`'s FAQ states that *"a bypassed prerequisite
violation remains in the commit graph and causes later conformance checks to fail until a specific,
attributable exception is recorded."* For a scaffolded artefact it does not: `--no-verify` past the
hook, delete the artefact, and the history audit never reports it.

**Reach: every adopter who let the wizard scaffold their gate artefacts**, which is the path the
wizard offers by default and the one the two trial installs took.

**Not yet remedied**, and the remedy needs a decision rather than a patch. The obvious narrowing —
never accept a `.standards/`-owned path as a historical name of an adopter's artefact — is small,
correct as far as it goes, and does not address the general case of a byte-identical file elsewhere
in the tree. Whether `historical_paths` should require the historical name to be *absent now* as
well as present then, or should disable copy detection entirely and accept only renames, is a change
to what `F30`'s remedy means, and belongs to the maintainer.

## F132 — A repository with no dependency manifest cannot adopt this standard at any level

**Severity: high. Closed — `ACT-078` (`DR-73`), 2026-09-09.**

Found on 2026-09-08 by the maintainer, **on the first screen of the first walkthrough**, against a
real repository. This is `H18`'s method producing `H18`'s result before `H18` had formally begun,
which is worth recording as its own small vindication of watching someone use the thing.

`dependency_lock` is the **only** control in `CONFORMANCE_LEVELS["essential"]`. `SP021`/`SP022`
require every control a level names to be decided `required` — `deferred` and `excluded` both raise
`SP022`. `SP051` then requires its `implementation_reference` to name a file that exists, is
non-empty, carries no placeholder, and is tracked by git. The adoption wizard implements this
faithfully: when discovery finds no lock file it asks for one, with `validate="tracked_path"`.

**So a repository with nothing to name has no way forward.** The wizard refuses to continue — which
is correct behaviour, not the defect. It is refusing to write a profile that its own checker would
reject. **The defect is upstream of it: the standard's one universal control assumes a property not
every repository has.**

The repository this was found on is a documentation and knowledge repository — 316 Markdown files,
16 YAML, 2 Python, **no `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Gemfile`,
`pom.xml`, `Cargo.toml` or `composer.json` of any kind**, verified by listing its tracked files. It
has no dependencies to pin. The class is not exotic: documentation repositories, configuration and
policy repositories, infrastructure-as-data repositories, monorepo subtrees whose dependencies are
resolved a level up, and repositories whose runtime comes entirely from a base image all share it.
The schema's own `stack` field says *"The kit does not require a UI, API, or specific language"* —
a claim this floor contradicts.

**Why 45,266 matrix checks did not catch it, which is the transferable part.** `test_adopt_matrix.py`
walks every reachable decision of the wizard across 208 cases, and one of its three repository
shapes is called `bare` — *"no language, no lock file, no workflow, no artefact matching any gate"*.
It reaches this very field. But **"there is no valid answer" is not a decision — it is a property of
the repository**, and every fixture in every suite answers a `tracked_path` field with a path that
exists in it (`main.py`, `activity/register.md`, and the matrix's own seeded files). A suite that
walks decisions exhaustively can still never reach a state that is not a decision. That is not a
gap in the matrix's coverage of what it covers; it is the boundary of what walking decisions can
establish, and it took a real repository to cross it.

**Proposed remedies, none applied — `H22`.**

1. **Derive applicability, and check it.** `dependency_lock` becomes not applicable where the
   repository contains no dependency manifest at all — a fact the checker can establish from the
   tracked file list, the same way `discover.candidate_lock_files` already does. If a manifest ever
   appears, the control snaps back to required and the check fails until a lock file is named.
   Nothing is declared and so nothing can be misdeclared. **Recommended.**
2. **Declare it and verify the declaration.** A `not_applicable` decision with a mandatory
   rationale, accepted **only** when the checker independently confirms no manifest exists — a new
   finding code for "declared not applicable, but a manifest is present". This is the
   `hook_chain` / `adopter_canon` idiom: the adopter states it, the checker verifies it by effect.
   More audit trail than (1), one more code and one more schema key.
3. **Allow `excluded` with a rationale, unchecked.** Rejected on sight: it lets any adopter with
   real dependencies write a sentence and drop the one control this standard applies to everyone.
   *"Supply-chain exposure exists regardless of output materiality"* is `dependency_lock`'s own
   stated rationale, and (3) would make it advisory.

Either (1) or (2) is a change to a published contract and to `core/CONFORMANCE_LEVELS.md`, which
this standard reserves to a human. The wizard change follows the standard's, not the other way
round — fixing the wizard alone would let it write a profile the checker still rejects, which is
`F66`'s defect exactly.

**Closed by `ACT-078` (`DR-73`), 2026-09-09 — the maintainer chose route (1).** The floor is lifted
by the checker, from the repository's own tracked files, and never by a declaration. Only the floor
moves: a repository that decides `dependency_lock` required anyway is checked by `SP051` exactly as
before, and the report says on every run that the waiver applied and why.

**What makes it a waiver rather than a hole is the second direction, and it is asserted.** Adding a
`package.json` restores the floor with no edit to the profile, and `SP021` fires naming the control.
Both directions are in `tests/test_adopt.py::test_a_repository_with_no_dependencies_can_still_conform`,
which fails without the fix in exactly the way the maintainer's run failed.

**Three consequences that were not obvious when this was raised:**

- **`control_decisions` may now be empty**, because at `essential` the waived control was the whole
  floor. `minProperties` moves `1` → `0` — a relaxation, so no existing profile becomes invalid —
  and the renderer writes `{}` rather than a bare key, which YAML reads as `null`.
- **`SP021`'s remedy told an `essential` adopter to "declare a lower level".** There is not one.
  This finding is precisely the case where that advice sent a reader nowhere, and it is corrected.
- **The shared test fixture had been in this finding's state all along**, and every scripted answer
  supplied a lock-file path pointing at a file that did not exist. The suite was green because the
  script answered a question no repository of that shape could answer. That is the same shape as
  the finding itself, one layer in, and it is recorded in `DR-73`'s Limitations rather than quietly
  fixed.

## F131 — A security advisory in a pinned test dependency has no satisfiable remedy, because a plugin pins the package that caps it

**Severity: medium. Accepted — by the maintainer at `H21`, 2026-09-08; recorded as `Accepted` by
`ACT-102` (`DR-86`), 2026-09-11. Not remediated; the CVE is still shipped.**

Recorded on 2026-09-08 in this session, from GitHub's Dependabot alert 1 on `main`.
**`GHSA-6w46-j5rx-g56g` / `CVE-2025-71176`** — *"pytest through 9.0.2 on UNIX relies on directories
with the `/tmp/pytest-of-{user}` name pattern, which allows local users to cause a denial of service
or possibly gain privileges."* First patched version: **9.0.3**. This repository pins
`pytest==8.4.2`.

**There is no version of pytest that both fixes this and satisfies the rest of the set.** Verified
by running the resolver rather than by reading metadata:

```
$ pip install --dry-run pytest==9.0.3 pytest-textual-snapshot==1.1.0 syrupy==4.8.0
ERROR: Cannot install pytest-textual-snapshot==1.1.0, pytest==9.0.3 and syrupy==4.8.0
       because these package versions have conflicting dependencies.
ERROR: ResolutionImpossible
```

The chain, each link read from the installed distribution's own metadata:

| Package | Declares |
|---|---|
| `pytest-textual-snapshot 1.1.0` (latest) | `syrupy == 4.8.0` — an **exact** pin |
| `syrupy 4.8.0` | `pytest >= 7.0.0, < 9.0.0` |
| `pytest 9.0.3` | the first version carrying the fix |

`syrupy 6.0.0` exists and requires only `pytest >= 8.0.0`, so syrupy is not the obstacle — the
plugin's exact pin on an old syrupy is. `pytest-textual-snapshot 1.1.0` was released **2025-01-23**
and is the latest, so "wait for upstream" is not a plan with a date attached.

**Dependabot's own PR (#83) does not work**, which is worth stating because it looked as though it
did. It bumps `pytest` in `pyproject.toml` alone; every suite passed; and the reason they passed is
`F130` below — CI installed 8.4.2 from its own hard-coded line and never saw the change. Applying
that PR to a real environment produces the `ResolutionImpossible` above, or, forced past the
resolver, an environment `pip check` rejects:

```
syrupy 4.8.0 requires pytest<9.0.0,>=7.0.0, but you have pytest 9.0.3 which is incompatible.
```

**Exposure, stated so the decision can be taken on facts.** `pytest` is in the `test` extra, which
`pyproject.toml` already records as *"Test-only, so an extra: no adopter's CI installs these"* —
**no adopting repository installs pytest because of this standard.** The advisory describes a
**local** attack: it needs an unprivileged user with shell access on the same host, racing a
predictable `/tmp/pytest-of-{user}` path while a test run is in progress. The two places this
repository runs pytest are an ephemeral single-tenant GitHub-hosted runner and the maintainer's own
workstation. `INFERENCE`, not `FACT`: on that reading the practical exposure is very low. It is
still a real advisory and the reading is a judgement, which is why the decision is not an agent's.

**Why this stays open rather than being fixed or dismissed here.** Three routes exist and all three
are the maintainer's:

1. **Accept and defer**, dismissing the alert as *"no fix available"* with a stated review trigger
   (a `pytest-textual-snapshot` release that permits `syrupy >= 5`). Accepting a security risk is
   explicitly reserved to a human by this standard's own Topic 9, and suppressing an alert in
   `.github/dependabot.yml` is weakening a control — an agent may recommend it and may not do it.
2. **Remove `pytest-textual-snapshot`** and drive `syrupy 6` directly, which frees `pytest 9`. That
   deletes a dependency `DR-50` (4) chose deliberately and touches the golden-SVG comparison, so it
   is a documented-control change, not a refactor.
3. **Leave it open**, which is the same exposure as (1) with a permanently red security tab and an
   alert that re-fires on every push.

**Recommendation: (1)**, on the exposure reading above and on the absence of any upstream date. Not
a decision this session can take. Recorded as **`H21`**.

**Decided 2026-09-08: route (1), accept and defer.** The maintainer accepted the residual risk on
the reading above. **This finding therefore stays `Open`, and the distinction is not pedantry: an
accepted risk and a fixed defect are different states, and a register that recorded them the same
way would be unable to answer "what is still wrong here?" — which is the only question it exists
to answer.** `pytest 8.4.2` is still pinned and still carries `CVE-2025-71176`. What changed is that
someone with the authority to accept it has, on the record, with a reason.

**What would reopen it:** a `pytest-textual-snapshot` release that permits `syrupy >= 5`. At that
point the whole chain unblocks in one bump and this finding closes by remediation rather than by
acceptance. **Checking for it is `H26`, not a reason this stays open** — the maintainer's own
correction on 2026-09-11: *"if it is something I need to check periodically [that] is an action
that I should have in my calendar but not a finding."* Right about the check, and the limitation
still belongs here: an independent reviewer at `H6` must meet a shipped, unpatched CVE as a
recorded limitation rather than infer it from a dependency pin.

**What the acceptance does not extend to.** It covers this advisory, in this dependency, at this
severity, on this exposure reading. A new advisory in the same package, or a change that puts
`pytest` on a path an adopter installs, is a new decision — not one this record has already taken.

**Corrected in the same change (`ACT-076`):** the costing offered to the maintainer said the
suppression would be *"three lines in `.github/dependabot.yml`"*. That file does not exist, and
creating one requires an `updates:` block that would **enable scheduled version-update pull
requests** this repository has never had — a behaviour change nobody asked for, offered as though it
were a formality. The alert came from Dependabot **security updates**, a repository setting, so the
instrument is dismissing the alert with a recorded reason. Stated here because the wrong instrument
was in the costing the decision was taken on, even though the decision itself is unaffected.

## F130 — The same dependency version is pinned in five places, and nothing compared them

**Severity: high. Closed — `ACT-074`, 2026-09-08.**

Recorded on 2026-09-08 in this session, found while establishing why Dependabot's pytest bump
(PR #83) showed thirteen green suites and one failure.

`pyproject.toml` is the authority for what this package depends on. The same versions are also
written out, by hand, in four other places:

| Where | What it pins |
|---|---|
| `pyproject.toml` | the authority — runtime, `adopt`, and `test` |
| `.github/workflows/standard-self-check.yml` | all six, hard-coded on the install line |
| `.github/workflows/standards-conformance.yml` | the two runtime pins |
| **`surfaceplate/standard/.github/workflows/standards-conformance.yml`** | the same two, **in the payload** — installed into every adopting repository |
| `INSTALL.md` | `textual`, in the command a reader is told to run |

**Nothing compared any of them to the authority.** The consequence is not theoretical: PR #83
edited `pyproject.toml` and *nothing else*, and the self-check workflow then installed
`pytest==8.4.2` from its own line and ran fourteen suites against it. Thirteen reported green. **A
dependency change was one merge away from being accepted on the evidence of a run that never
installed it** — the working method's *wrong artefact* failure exactly: a right answer about the
wrong object, which no amount of re-running the check would have exposed, because every re-run
would have tested 8.4.2 again.

The payload row is why this is `high` rather than `medium`. That workflow is installed into every
adopting repository and is integrity-checked there, so a runtime pin that moves in `pyproject.toml`
without moving in the payload copy has every adopter's CI installing a set the package does not
declare — and the adopter cannot correct it, because editing an installed file fails their own
conformance check.

**Remedy, `ACT-074`.** `tests/check_code_registers.py` gains `dependency_pin_checks`: it reads
`pyproject.toml`'s exact pins — runtime and every extra — and requires every `name==version` written
in any workflow (this repository's and the payload's), `INSTALL.md`, `README.md`, `CONTRIBUTING.md`
or `scripts/front_door.sh` to agree with it for any package `pyproject.toml` declares. The
authority is read, never restated, so adding a dependency extends the check with no edit.

**Its limit, stated rather than implied:** a pin for a package `pyproject.toml` does not declare
(`build==1.2.2` in `publish.yml`, a publish-time tool) has no authority here to be compared
against, and is skipped. Making `publish.yml`'s toolchain a declared extra would close that too and
is not done here, because it changes what the package declares to the index for a build-time
concern.

**Verified by effect.** With Dependabot's exact change applied to `pyproject.toml` alone, the check
fails — `.github/workflows/standard-self-check.yml: pytest==8.4.2 matches pyproject.toml:
pyproject.toml pins 9.0.3` — exit 1. Restored, it passes at 105 checks. The failure names the file
that disagrees, so the reader is not left to find which of the five is wrong.

## F129 — `F123`'s ruling was applied to the document it was found in, and to no other

**Severity: medium. Closed — `ACT-073`, 2026-09-08.**

Recorded on 2026-09-08 in this session, found while chasing `F128` with a grep that was wider than
the defect it was looking for. `F123` established, four days earlier, that an agent-neutral
standard must not name one vendor's file as the place a repository states something — an agent
reading the rules in a directory that vendor does not use is told to consult a file it never loads.
Topic 1 carries that remedy, in the careful form the finding earned: *"whichever file this
repository has told your agent to read — `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`,
or another"*.

Topic 7 said, twice: *"Stack-specific commands belong in the repository's own
`copilot-instructions.md`"* and *"Declare the repository's test areas in its own
`copilot-instructions.md`"*. Both survived the twelve-topic restructure untouched, because the
restructure moved the sentences and did not re-read them against a ruling made about a different
file.

**Its reach, stated precisely rather than at its worst.** Both sentences sit in Topic 7's
**normative** half, which `DR-69`'s emitter does not ship to `.claude/rules/` or
`.github/instructions/` — those carry the imperative section only, and it names no vendor's file.
So no agent was handed this in the file it loads. What every adopter does receive is the canonical
copy at `.standards/topics/07-testing.md`, which carries the whole document and which `DR-30`
designates for the human reader and for *"any agent not emitted for"* — the two audiences least able
to notice that the instruction assumes a vendor they may not use.

**The finding is the sweep, not the sentence.** `F123` was closed by correcting the site where it
was noticed. Nothing then asked *where else does this repository say the same thing*, and the answer
was: twice in the testing topic. A remedy applied to an instance leaves the class open, and the
class is what a later reader meets.

**Remedy, `ACT-073`.** Both sentences now say "the repository's own agent instruction file", the
first citing Topic 1 where the full form of the rule lives. No new mechanism: this is not
mechanically checkable — "names a vendor's file" is a judgement about prose, and a regex banning the
string would fail on Topic 1's own correct usage, which names all three deliberately. What is
mechanically checkable is the narrower thing `F128`'s check now covers.

## F128 — A skill shipped to every adopter named an instruction file the installer had stopped writing

**Severity: medium. Closed — `ACT-073`, 2026-09-08.**

Recorded on 2026-09-08 in this session, found by grepping the payload for references to the retired
`agent-instructions/` names while resolving `H17`. `standard/.github/skills/change/SKILL.md`
required, among a change's inputs, *"the registered activity ID (see `activity.instructions.md`)"*.
That file has not existed since `ACT-068` replaced the seven-document split with twelve topic
documents: the Copilot destination is now `04-work-tracking.instructions.md`. The skill is emitted
to **both** `.github/skills/change/SKILL.md` and `.claude/skills/change/SKILL.md`, so every adopter
of either agent received a pointer that resolves to nothing.

It was already half-wrong before the restructure, which is the more useful half of this finding.
`activity.instructions.md` is a **Copilot-emitted filename** — `DR-31` recorded exactly that
observation about exactly that name in another document, and `DR-30` had dropped the suffix from the
canonical body precisely because it was vendor-shaped. A Claude Code adopter has never had a file
by that name. So the restructure did not create the defect; it removed the last agent for whom the
pointer happened to work, and turned a wrong-for-half-of-them pointer into a wrong-for-everyone one.

`activity/register.md`'s opening sentence carried the same stale path, and is corrected in the same
change. That one is this repository's own document rather than payload, and it is recorded here
rather than separately because it is the identical sentence with an identical cause.

**Why nothing caught it.** `tests/check_code_registers.py` resolves every path-like span in
`README.md` and `INSTALL.md` against the installer's payload — the `F70`/`F71` remedy, and a good
one. **It had never been pointed at the payload itself.** The front door was checked and the thing
behind it was not, so a document that ships to every adopter could name a destination the installer
does not write, and every suite stayed green. `F50` is the same defect one layer further out: a
hand-off command naming a file deleted three packets earlier, caught only when a person ran it.

**Remedy, `ACT-073`.** Two parts, and the second is the one that matters.

1. The skill now says *"see Topic 4, Work tracking"* — the topic, not the file. A topic number
   survives a rename of the emitted filenames, which is the property the old pointer lacked. The
   register's sentence names the topic and all three of its installed paths, and marks the old
   wording as history in place.
2. `check_code_registers.py` gains `payload_pointer_checks`: every Markdown file in
   `build_payload()` — the canonical topics, both emitted copies of each, and both copies of each
   skill — has its `.standards/…`, `.claude/rules/…`, `.claude/skills/…`, `.github/instructions/…`,
   `.github/skills/…` and bare `*.instructions.md` spans resolved against the payload's own
   destinations. Deliberately narrow: a payload document naming `README.md` or a stack's own file is
   naming the *adopter's* tree, which this cannot resolve and must not pretend to.

**Verified by effect, both directions.** With the old wording reinstated the check fails naming both
emitted copies (`payload .claude/skills/change/SKILL.md: 'activity.instructions.md' names a file the
installer writes: no installed destination matches it`, and the `.github` twin), exit 1; with the fix
in place it passes, 93 checks. A check that could not have failed here would have been the false
green this repository exists to find.

## F127 — `SECURITY.md` went stale a second time about the same feature, in a sentence that cited its own verification

**Severity: medium. Closed — `ACT-070`, 2026-09-08.**

Recorded on 2026-09-08 in this session, while clearing `H17`. `SECURITY.md` asserted that private
vulnerability reporting *"is not enabled today — verified directly against GitHub's API
(`GET /repos/pipoventures/surfaceplate/private-vulnerability-reporting` currently answers
`enabled: false`), not assumed"*. Queried before acting on `H17`, the same endpoint answered
`{"enabled": true}`. The document had been telling readers there was no confidential channel while
one existed, and pointing them instead at public Issues with advice to hold back specifics — the
opposite of what it should have said, in the one file where being wrong about the reporting route
matters most.

**This is `F118` repeating, in the same file, about the same feature, after `F118` was closed.**
That is the finding. `F118`'s remedy corrected the *value* — the paragraph was rewritten to say the
repository was public and reporting not yet enabled — and it did so scrupulously, adding the API
call as evidence. What it did not change is the property that produced `F118` in the first place:
**the sentence describes state that lives in GitHub's settings, which this repository cannot read,
cannot check, and is not notified about.** Every check this project runs is offline and reads the
tree; none of them can fail when a setting changes under a document that describes it. So the
corrected paragraph was exactly as capable of going stale as the one it replaced, and it did,
within five days.

The aggravating detail is `not assumed`. A claim that cites its own verification reads as *more*
reliable than a bare assertion, so a reader who noticed the sentence at all had extra reason to
believe it. Evidence of a past check is not evidence of a present fact, and writing it in the
present tense (*"currently answers"*) silently converts one into the other. This is the same shape
as `S3`'s rule — a document is read for sense rather than run — one level up: here the document
*was* run, once, and the result was then written down as though it were permanent.

**Remedy, `ACT-070`.** Two changes, and one deliberate non-change.

1. The paragraph now states the observation **with the date it was made** and says plainly that it
   describes a setting a person can change, giving the reader the falsifier: if the Security tab
   offers no such button, the line is stale. A dated observation cannot silently become a false
   standing claim, because its scope is written into it.
2. The two superseded readings are kept, marked explicitly historical, because the pattern is worth
   more to a later reader than the correction is — this is the supersession rule the standard
   itself now ships (Topic 1), applied to the file that has twice demonstrated why it exists.
3. **No check was added, and that is the honest answer rather than a gap left open.** A check for
   this would have to call GitHub's API from CI, needs a token with the right scope, fails closed
   on a fork and on any adopter, and would assert a fact about *this* repository from code that
   ships to *others*. `S3` already records the parallel case (`F57`): where a check would not
   reliably catch the defect it is named for, adding one buys a false green rather than a gate. The
   remedy here is a writing rule — date a claim about external state, or do not make it — not a
   mechanism.

**What closes it:** the paragraph as rewritten, and `H17` closed in `org/HUMAN_ACTIONS.md` with
both API responses quoted. The narrower fact `F118` was raised against — the repository's
visibility — is settled and cannot recur; the reporting setting can, and the document now tells a
reader how to tell.

## F126 — A recorded `effective_from` instant can sit ahead of the clock that judges it

**Severity: medium. Closed — `ACT-070`, 2026-09-08.**

*Originally recorded under the title "`test_adopt_matrix.py`'s edit-route case intermittently fails
`SP033`, reproducibly on a clean checkout". That named the symptom in the test suite. The finding
is retitled to name the defect, which is in the shipped comparison and reaches adopters, not only
this repository's own matrix.*

**What was measured, and it is the whole finding.** An instrumented matrix run logged every call
the checker made to `rules.effective_is_future`, capturing the raw field, the parsed day, the
`today` it was given, and the real clock at the moment of the verdict. Six verdicts looked like
this:

```
raw = 2026-09-08T21:25:30+01:00      the effective_from as written
clock = 2026-09-08T21:25:28.594430   the clock when the checker judged it
```

**The recorded instant was ~1.4 seconds ahead of the clock that judged it.** That is impossible on
a single monotonic clock: `provenance.now_iso()` truncates microseconds *downward*, so a value it
mints can never exceed a later reading. `SP033` was arithmetically correct and the timestamp was
wrong. A seventh verdict in the same run was the deliberate `effective-from-future` negative case
(a date of tomorrow against a today), working exactly as designed.

**`FACT` / `INFERENCE`, kept apart.** That the recorded instant led the checking clock is `FACT`,
measured directly. *Why* the clock moved is `INFERENCE`: NTP steps, VM suspend/resume and WSL2's
periodic resync against its Windows host all move the wall clock backward by roughly this much, and
this machine is WSL2. It was never forced to reproduce — 20,000 tight write-then-check cycles were
clean, an idle clock showed no drift over twelve seconds, and a second full matrix run produced
zero future verdicts. Recorded as an inference rather than dressed up as a diagnosis.

**Remedy: make the comparison robust to the class, rather than repair a cause not observed.**
`rules.FUTURE_INSTANT_TOLERANCE` (60 seconds) applies to the **instant** branch only. Nobody defers
a gate by a minute, so the control keeps its whole meaning: a gate genuinely dated in the future is
hours or days out. `F47`/`DR-44`'s deliberate decision — *"an instant later today is genuinely in
the future and must still be refused"* — survives untouched, because an instant later today is
hours ahead, not seconds. The date branch is unchanged, where a one-day error needs a midnight
crossing rather than a clock nudge, and where a tolerance would weaken the "dated tomorrow"
refusal for nothing.

Held in `rules.py` so the wizard's validator and the checker move together, per `DR-48`.

**Verified in four directions** (`tests/test_adopt.py`): an instant two seconds ahead is no longer
future; an instant an hour ahead still is; a date of tomorrow still is; an instant in the past is
not. A fifth assertion pins the tolerance below five minutes, so that widening it to hours — which
would silently reverse `F47` by editing a constant rather than by writing a record — fails the
suite instead.

**A second consequence this closes.** While open, this defect made `audit/validation/ADOPT_MATRIX.md`
impossible to regenerate on the affected machine: `--write` embeds a *"N case(s) failed… must not be
committed in that state"* guard. It also made the matrix's own report-comparison useless as
evidence for anything else, because it reported "differs" whether or not the change under test had
altered the report — a check returning the same answer for both outcomes it was being asked to
distinguish.

Found on 2026-09-08 during `ACT-068`'s Step 1 prototype, while running `test_adopt_matrix.py` as
part of that step's own verification. Not caused by anything in this session's changes — isolated
by re-running the identical suite against `main` at `f871cad` with `git stash`, before any prototype
file existed, and the failure reproduced identically: **`4 failed, 45262 passed; 208 runs`**, all
four inside the `standard`-level, `route="edit"` matrix case (`adopt_matrix.py:287-288`), each
reading:

```
- T6-195: after the string edit the checker still passes: WARN ['SP033', 'SP033']
- T6-195: after the bool edits the checker still passes: WARN ['SP033', ...×10]
- T6-195: after the list-element edit the checker still passes: WARN ['SP033', ...×10]
```

`SP033` fires when a gate's `effective_from` is later than the date the checker is told is
"today". `tests/adopt_matrix.py:1148` calls `check_conformance.evaluate(repo, TODAY, False, False)`
with `TODAY = _dt.date.today()`, a module-level constant **captured once at import time**
(`adopt_matrix.py:48`). The profile the edit-route case writes and then re-checks is produced by
the wizard's own write path, which computes "today" independently, and not once: `defaults.py:233`,
`sections.py:226`, `flow.py:93`, `plan.py:938` and `plan.py:1139` each call
`_dt.date.today()` or `_dt.datetime.now()` separately, rather than deriving from one instant passed
through. **This is the architectural fragility, established by direct read; it is not yet proven to
be the trigger for this specific failure.**

**What was checked and ruled out.** Local time and UTC agree on the calendar date at the moment of
investigation (`2026-09-08` both ways) — a naive UTC/local mismatch is not live right now, so the
defect is not simply "some call uses UTC and another uses local time" caught mid-difference. The
matrix run takes roughly three minutes; a real-time midnight rollover mid-run cannot be ruled out
in general but was not observed directly in this instance.

**Corroborated on 2026-09-08 by a clean control: the same suite PASSES in CI.** The run for
`ACT-068` reported `matrix=success` on GitHub Actions while failing locally on the same commit,
with different case IDs failing between two consecutive local runs (`T6-195`, then `T2-003`/
`T2-064`). Three facts together — passes in CI, fails locally, and picks different cases each local
run — place the cause in the **local environment's clock or timing**, not in the repository's
content. That is a narrowing, not a closure: it says where to look, not what is wrong.

**A second consequence, found on 2026-09-08 while doing unrelated work: the tracked matrix report
cannot be regenerated on the affected machine.** `test_adopt_matrix.py --write` embeds a line
reading *"N case(s) failed on the last run that wrote this file; this file must not be committed
in that state"* — the report guarding itself, correctly. So while this defect is live locally, any
change that legitimately alters `audit/validation/ADOPT_MATRIX.md` cannot have that report
regenerated here; the regeneration must happen where the suite passes, which today means CI. This
is a real operational consequence, not a second defect, and it is recorded so a later session that
needs to regenerate the report understands why it cannot rather than concluding the report is
broken.

**`EVIDENCE GAP`:** the exact triggering sequence — which of the five independent clock reads
disagreed with `adopt_matrix.py`'s frozen `TODAY`, and under what condition — has not been isolated.
Establishing it needs either a reproduction harness that controls the clock (freezing or mocking
`_dt.date.today()`) or catching the suite failing again with the wall-clock time recorded at the
moment of the affected wizard write.

**Not investigated further here, deliberately.** Root-causing and fixing this is unrelated to the
topic restructure this session is doing (`ACT-068`) and was not blocking its decision gate — that
gate concerns the emitter/`DR-45` manifest interaction alone, which held cleanly and independently
of this failure. Recorded rather than silently worked around, per this repository's own rule that a
defect found here is recorded here, including a defect in the framework's own test suite.

**Proposed remedy, not yet decided:** derive every date computation in the wizard's write path from
one instant, injected once per run (the pattern `flow.py:93`'s `today or _dt.date.today()` parameter
already partially uses), so a run spanning a clock boundary is internally consistent even if it
disagrees with a separately-frozen test constant.

## F125 — No adopter-facing precedence rule exists between this standard and a co-resident governance system

**Severity: medium. Closed — `ACT-068`/`ACT-069` (`DR-69`, `DR-71`), 2026-09-08.**

**Remedy, in two halves, because the finding had two.** Topic 1 (Authority) now states the
**default** in adopter-facing text: this standard governs the surfaces it specifies, the
repository's own instructions govern the rest, and a contradiction on a surface this standard does
specify is the blocking defect the same document already described. And `adopter_canon` in the
application profile is the **mechanism** by which a repository declares a different order — binding
the repository that declares it and no other, checked by `SP060` for existence and tracking so the
declaration is verified rather than decorative.

Both halves were needed. A rule with no mechanism would have been advice; a mechanism with no
stated default would have left every repository that declares nothing in exactly the position this
finding describes.

Raised at `ACT-063` from a portfolio operating-model review outside this repository (`mnemosyne/reviews/2026-09-04_operating-model-plan-v3.md`, where it is numbered `SP-F6`). That review proposed it; it is recorded here only after being re-verified against this repository on 2026-09-08, and where the re-verification disagreed with the review the disagreement is stated rather than smoothed away. Nothing in `mnemosyne` is part of this standard or a condition of adopting it; it is the origin of the observation, not an authority over the remedy.

An adopting repository may already carry its own standing instructions — a `CLAUDE.md`, a house
style, a parent organisation's engineering policy — and this standard installs alongside them
without saying which wins. `standard/agent-instructions/authority.md` §*Contradictions are blocking
defects* tells an agent that contradictory authority is a blocking defect and to stop; the standard
then creates exactly that condition on install and supplies no rule for resolving it. Nothing in
the payload states whether the installed rules govern, are governed by, or are subordinate to
instructions the repository already had.

**The review's evidence for this is half wrong, and the correction matters.** It asserted
*"Surfaceplate does not mention mnemosyne."* Re-checked on 2026-09-08: true of the installed
standard — `grep -ril mnemosyne .standards/` returns **0 files** — and false of this repository,
where `git grep -ril mnemosyne` returns **5 tracked files**, among them `DR-2` (2026-08-30), which
declares that kernel *"sole behavioural canon"* for AI-assisted work under this standard. So a
precedence statement about that particular pair does exist; what does not exist is any rule an
adopter receives. Recording the finding on the review's original wording would have made it
falsifiable by a thirty-second grep and closable by pointing at `DR-2`, which would close the wrong
thing.

**What the finding actually is, stated so the remedy is aimed correctly:** the standard ships no
mechanism by which an adopter can declare what governs their repository when this standard and
something else disagree. That is the same gap `WI-2`'s adopter-declared canon addresses, and it is
why this finding rides the application-profile schema change rather than being answered by a
paragraph of prose.

## F124 — The checker verifies that an install is unedited and has no notion of whether it is current

**Severity: high. Closed — `ACT-075` (`DR-72`), 2026-09-08.**

Raised at `ACT-063` from a portfolio operating-model review outside this repository (`mnemosyne/reviews/2026-09-04_operating-model-plan-v3.md`, where it is numbered `SP-F5`). That review proposed it; it is recorded here only after being re-verified against this repository on 2026-09-08, and where the re-verification disagreed with the review the disagreement is stated rather than smoothed away. Nothing in `mnemosyne` is part of this standard or a condition of adopting it; it is the origin of the observation, not an authority over the remedy.

`check_conformance.py` establishes, through `MANIFEST.sha256` and `SP049`'s recomputation of the
anchor, that the installed standard is byte-for-byte the version recorded at install time. It has
no way to ask whether that version is the current one, and structurally cannot: it runs inside the
adopting repository with no network. `DR-45` is explicit that the anchor *"records the manifest of
the tree installed FROM, which is a historical fact, not a live invariant"* — correct, and exactly
the reason nothing surfaces staleness.

The consequence is that a repository can sit an arbitrary number of versions behind, indefinitely,
while its conformance check passes and says nothing. Integrity and currency are different
properties and only one of them is checked. This is the highest-severity of the six because it
scales with adoption: every repository that installs the standard acquires a control that is silent
in exactly the case where it would be most useful.

**Corroborating fact, and its evidence level.** The review reports `plutos` running `.standards`
`0.16.0` against a published `0.16.1` with nothing surfacing the gap. **`FACT` as to the published
version** — PyPI carries `0.16.0` and `0.16.1`, read directly on 2026-09-08. **`EVIDENCE GAP` as to
`plutos`** — that is a separate repository and this session has not run the checker in it. The
finding does not depend on that reading: the absence of any currency notion is established from
this repository's own code.

**Narrowed, not closed, by `ACT-067` (`DR-68`), 2026-09-08.** `surfaceplate doctor --online`
now reports installed-versus-published as an advisory, verified by effect against the live index
in all three directions: `0.16.0` against a published `0.16.1` warns — the case this finding names,
reproduced exactly; `0.16.1` against `0.16.1` reports `ok` and **produces no signal**; and `0.17.0`
against `0.16.1` reports *ahead* rather than an instruction to upgrade, because the publisher's own
repository is always ahead by construction. The middle row is what makes the first worth anything.
Unreachable reports `warn`, not `ok` — an unanswered question is not a passing one.

**What remains open, and it is the half that matters to an adopter.** The mechanism exists and
**nothing triggers it**. A repository whose maintainer never runs `doctor --online` is in exactly
the position this finding describes. The obvious trigger is a step in the installed conformance
workflow, which runs in every adopter's CI where a network exists — and it is not built, because it
would make every adopting repository's CI call out to `pypi.org` on every run, and would be
uneditable by the adopter, the installed workflow being integrity-checked. A repository that did
not want the call could not remove it without failing its own check. That is a change to adopters'
infrastructure and to an outbound network boundary, which this standard's own rules reserve to a
human. Recorded as `H20`; `DR-68` states it as an explicit limitation rather than leaving the gap
to be discovered.

**Closed by `ACT-075` (`DR-72`), 2026-09-08 — the maintainer answered `H20` and chose the option
that keeps the adopter a say.** The step exists and is on by default; the adopter declines it in the
one installed file that is theirs.

- `check_conformance.py --currency` makes the one request and reports *current*, *ahead*, *behind*
  or *unknown*. The installed workflow passes the flag; nothing else does, so a local check and the
  pre-commit hook still open no socket.
- **It is an advisory and can never be a finding** — not blocking and not graceable either, because
  a graceable finding fails once the grace window ends, and a check that eventually failed on this
  would call a deliberate version pin a defect.
- `adoption.currency_check: {enabled: false, rationale: …}` suppresses the request entirely. Absent
  means enabled, so `schema_version` stays `"1.0"` and no existing profile is invalid. The opt-out
  had to live in the profile because the workflow is integrity-checked: without it, *"on by
  default"* would have meant *"compulsory"*.
- The comparison moved to `rules.py` (`DR-48`), so `doctor --online` and the checker cannot answer
  *"is 0.9.0 newer than 0.17.0"* two different ways — a comparison with a known wrong answer when
  written as a string comparison.

**What the closure does and does not claim.** It claims the gap this finding names is now reported
wherever a network exists: a repository sitting versions behind is told so on every CI run. It does
not claim the report is unmissable — an advisory line is quieter than a failure, deliberately — nor
that the index is trustworthy. `DR-72`'s Limitations state both.

## F123 — `authority.md` names one vendor's file as the place the authority hierarchy must be stated

**Severity: medium. Closed — `ACT-066` (`DR-67`), 2026-09-08.**

**Remedy.** The paragraph names *the repository's own agent instruction file* and then says what
that means — `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, or whatever the
repository has told the agent to read — rather than one vendor's filename. Kept deliberately
non-exhaustive: an agent this framework has never heard of should not be excluded by a list.

Raised at `ACT-063` from a portfolio operating-model review outside this repository (`mnemosyne/reviews/2026-09-04_operating-model-plan-v3.md`, where it is numbered `SP-F4`). That review proposed it; it is recorded here only after being re-verified against this repository on 2026-09-08, and where the re-verification disagreed with the review the disagreement is stated rather than smoothed away. Nothing in `mnemosyne` is part of this standard or a condition of adopting it; it is the origin of the observation, not an authority over the remedy.

`standard/agent-instructions/authority.md:20,22` instructs every agent that where an authority map
is absent, *"the repository's `copilot-instructions.md` must state the ordered authority hierarchy
explicitly. An unstated hierarchy is a control gap; report it."* Verified in place on 2026-09-08.
The document is otherwise agent-neutral and is emitted to four destinations by `DR-30`'s
one-body-several-emitters pattern — so an adopter reading it in `.claude/rules/` is told to consult
a file their agent does not read, and, if they follow it literally, to report a control gap for not
having written one.

This is the same root as `F122`: a channel-specific assumption surviving inside content that
`DR-30` made channel-neutral. The remedy is to name the repository's *declared* instruction file,
whatever it is, rather than one vendor's.

## F122 — The installer creates a Copilot instruction channel unconditionally, including in repositories that do not use Copilot

**Severity: low. Closed — `ACT-066` (`DR-67`), 2026-09-08.**

**Remedy, and it is deliberately wider than this finding asked for.** `surfaceplate install
--agents claude,copilot` narrows the per-agent destinations; omitting the flag installs every
channel, so no existing adopter's install changes. This finding's proposed remedy was to make the
**Copilot** channel opt-in specifically; building that literally would make one vendor's channel
opt-in while the other stayed default, which is the same neutrality breach one layer along in a
framework whose `DR-30` exists to prevent exactly that. `DR-67` records the divergence rather than
leaving it to be discovered. The declining is recorded in `INSTALL.json` and reported on every
conformance run, and the checker does not then demand a file it was told not to write.

Raised at `ACT-063` from a portfolio operating-model review outside this repository (`mnemosyne/reviews/2026-09-04_operating-model-plan-v3.md`, where it is numbered `SP-F3`). That review proposed it; it is recorded here only after being re-verified against this repository on 2026-09-08, and where the re-verification disagreed with the review the disagreement is stated rather than smoothed away. Nothing in `mnemosyne` is part of this standard or a condition of adopting it; it is the origin of the observation, not an authority over the remedy.

Every install writes a full GitHub Copilot instruction channel whether or not the adopter uses
Copilot: **13 of the 82 installed paths** are Copilot-specific — seven
`.github/instructions/*.instructions.md` and seven `.github/skills/*/SKILL.md` — plus
`.github/copilot-instructions.md`, created outside the payload by the block upsert, for **14
artefacts** in total. There is no flag to decline them, and `DR-29`'s `--no-hooks` precedent shows
the project already accepts that an adopter may decline a channel provided the declining leaves a
trace. The symmetry matters for the remedy: the Claude Code channel is the same size, so a fix
that makes only one of them declinable would breach the agent neutrality `DR-30` established.

**The review's named artefact was right, and this entry said otherwise for a few hours.**
`.github/copilot-instructions.md` is **created by the installer** in every adopting repository
that lacks it, and its block is refreshed on every upgrade — `upsert_conformance_block`
(`install_standard.py:557`) writes a header and the marker block when the file is not there.
Verified by effect on 2026-09-08 against a repository installed into from scratch: the file
exists afterwards, and `.standards/INSTALL.json` does **not** list it. So the Copilot channel an
adopter receives is **14 artefacts, not 13** — the 13 payload paths plus this created file.

**What this entry claimed until 2026-09-08, and why the error is worth keeping.** It said the file
is *"not written by the installer"*, citing `install_standard.py:15` — *"`.github/copilot-instructions.md`
and `CLAUDE.md` stay the adopter's, untouched"*. That comment is true of the **payload**: the file
is not payload-owned, so it is neither overwritten wholesale nor integrity-checked. It is not true
of the **installer**, which creates the file by a different route. Reading a comment about one
mechanism as though it governed the whole program is the same wrong-object error this entry was
raised to correct in the review, made in the opposite direction while correcting it. Two
mechanisms write into an adopting repository — the payload and the block upsert — and checking one
of them is not checking what an adopter receives.

Severity is low rather than medium because the cost is unwanted files rather than a false claim:
nothing about the extra channel makes the repository's conformance result wrong. It is recorded
because unwanted artefacts in someone else's repository are a real adoption cost, and because a
stranger cannot be expected to know which of the two per-agent channels they are receiving.

## F121 — `owner_role` and `reviewer_role` are required of a solo adopter, for whom both are constant

**Severity: medium. Closed — `ACT-068` (`DR-69`), 2026-09-08.**

**Remedy.** Topic 4 (Work tracking) grades the register by conformance level: at `essential`, a
two-value status and a bare dependency pointer satisfy it, and `owner_role`/`reviewer_role` are
declared once at the repository level rather than repeated per entry. The full field set is what
`standard` and `full` ask for, where a named reviewer is doing real work.

**This finding then earned its keep a second time, hours later, on a different surface.** `DR-69`
had specified nesting the twelve controls under topics in the application profile. `DR-71` rejected
that using *this finding's own reasoning* — a control's topic is decided by the framework, so
nesting it into every adopter's file would restate a fact the framework owns, in a field that could
only be redundant when right or wrong when not. "A constant column carries no information", one
level up. The programme's only breaking change was removed on the strength of it.

Raised at `ACT-063` from a portfolio operating-model review outside this repository (`mnemosyne/reviews/2026-09-04_operating-model-plan-v3.md`, where it is numbered `SP-F2`). That review proposed it; it is recorded here only after being re-verified against this repository on 2026-09-08, and where the re-verification disagreed with the review the disagreement is stated rather than smoothed away. Nothing in `mnemosyne` is part of this standard or a condition of adopting it; it is the origin of the observation, not an authority over the remedy.

A sub-case of `F120`, recorded separately because it is the sharpest instance and has its own
remedy. `standard/agent-instructions/activity.md:37-38` requires every register entry to carry
`owner_role` and `reviewer_role`, at every conformance level. For a single-maintainer repository
both columns are constant, and `reviewer_role` implies a second person who does not exist — which
in turn makes the `waiting_for_review` status either unreachable or self-referential.

**This repository is its own evidence.** Every one of the 62 rows in `activity/register.md` reads
`maintainer` in both columns. The framework's reference implementation demonstrates the defect in
the product.

**Proposed remedy, not yet decided:** at `essential`, satisfy both by a repository-level declaration
rather than a per-entry field. Note what this must not do — it must not remove the fields at
`standard` or `full`, where a named reviewer is doing real work, and it must not make
`waiting_for_review` meaningless for adopters who do have a second person.

## F120 — The agent instructions are not graded by conformance level, while every control is

**Severity: medium. Closed — `ACT-068` (`DR-69`), 2026-09-08.**

**Remedy, and it is narrower than the finding's own proposal.** The finding proposed grading every
agent-instruction rule file by level. What shipped grades the instance that mattered: Topic 4
(Work tracking) states what `essential` requires of a register versus what `standard` and `full`
do, which is the case this finding named as its sharpest and the one that imposed a real cost on a
small adopter.

**The general mechanism landed with the restructure rather than as a separate control.** The topic
axis is what makes grading expressible at all — class, audience and level become properties stated
in a rule's own document rather than of the directory it sat in — and the topic documents state
their floors in their own text. What is deliberately *not* built is a machine-checked per-rule
level field: no check reads one, and inventing an enforcement mechanism for a documentation
property would be a control with no reader, which `core/CONTROL_PRINCIPLES.md` principle 12
declines.

Raised at `ACT-063` from a portfolio operating-model review outside this repository (`mnemosyne/reviews/2026-09-04_operating-model-plan-v3.md`, where it is numbered `SP-F1`). That review proposed it; it is recorded here only after being re-verified against this repository on 2026-09-08, and where the re-verification disagreed with the review the disagreement is stated rather than smoothed away. Nothing in `mnemosyne` is part of this standard or a condition of adopting it; it is the origin of the observation, not an authority over the remedy.

`core/CONFORMANCE_LEVELS.md` grades every control by level and states plainly why: *"Without graded
levels, a two-person proof of concept and a client-reported quantitative model face the same
control surface. In practice that produces one of two failures: small teams reject the framework as
disproportionate, or they claim adoption while implementing very little of it."*

**The agent instructions escaped that grading.** All six carry `scope: "**"` and state flat,
ungraded requirements — `activity.md` alone imposes eleven minimum register fields, a seven-value
status vocabulary, and two required role fields, verified in place on 2026-09-08. An adopter at
`essential` receives `essential` controls — three baselines plus `dependency_lock` — and
`full`-weight agent instructions. The framework's own `core/CONTROL_PRINCIPLES.md` principle 12,
*"Defer controls that do not reduce a demonstrated risk to a material output, its data, or its
release"*, is not applied to the framework's own instruction layer.

**Why this one is load-bearing for the topic restructure.** Grading a rule by level means class,
audience and enforcement become **fields on the rule** rather than properties of the file it sits
in — which is the topic restructure's central mechanism, not a separate piece of work. The remedy
is therefore scheduled to land with that change rather than ahead of it, and this finding is the
reason the restructure is not merely a rearrangement.

**Proposed remedy, not yet decided:** grade the agent-instruction rules by level as the controls
are. At `essential`, a two-value status and a bare dependency pointer satisfy `activity.md`.

## F119 — Nowhere a user actually reads named an issue tracker, and no offline way to assemble a problem report existed

**Severity: medium. Closed.**

Recorded on 2026-09-03 in this session (https://claude.ai/code/session_01QAovBCSt2UGXo3KZn3WtFW)
while designing a feedback surface for adopters (`ACT-062`). The installer's "Next steps:" block
(`install_standard.py`), the post-`adopt` failure branch (`cli._report_written`), `INSTALL.md`'s two
"Raise it against the standard" / "Raise it" sentences, and SP005's own remedy text ("raise it
against the standard so every repository gets it") all told a user to raise something without ever
saying where. `CONTRIBUTING.md` covered DCO sign-off only. `SUPPORT.md` and
`.github/ISSUE_TEMPLATE/` did not exist. Discussions were disabled. The practical effect: an
adopter who hit a defect and wanted to report it had to find the GitHub repository and its Issues
tab unassisted, and one who wanted to report it *without* first finding and reading several source
files by hand had no way to state what version, digest, or environment they were on.

**Remedy in `ACT-062`:** `about.ISSUES` added beside `about.HOMEPAGE` (`DR-51` (2)'s single-module
convention) and threaded to the installer's Next steps, `cli._report_written`'s failure branch,
`INSTALL.md`'s two sentences, `CONTRIBUTING.md`, and `README.md`'s Maintenance section.
`surfaceplate doctor --report` assembles a paste-ready report entirely on the caller's own machine —
tool version and anchor, the installed standard's version and digest, Python and OS, which optional
dependencies import, and the checker's verdict — and states plainly that nothing is sent; it is
explicitly incompatible with `--online` so the one network-capable path in this module and the
one that must never open a socket stay provably disjoint. `SUPPORT.md` and two issue forms route a
report to the right place. Repository settings this remedy could not itself touch (enabling
Discussions, enabling private vulnerability reporting) are listed in `org/HUMAN_ACTIONS.md`.

## F118 — `SECURITY.md` said the repository was private and private vulnerability reporting could not be enabled, weeks after the repository was made public

**Severity: medium. Closed.**

Recorded on 2026-09-03 in this session (https://claude.ai/code/session_01QAovBCSt2UGXo3KZn3WtFW).
`SECURITY.md` asserted *"This repository is currently private. Private vulnerability reporting is a
GitHub feature for public repositories and cannot be enabled while it stays private — verified
directly against GitHub's own API and documentation, not assumed."* That was true when written; the
repository has since been made public (see `F116`, the same session's front-door fix, for the same
underlying change of state). The document's own claimed verification made the error worse, not
better — a stale fact stated as freshly checked reads as more reliable than it is. This is exactly
the failure mode the working-method's supersession rule names: a statement that was true when
written and became false is left standing rather than corrected, distinguished from the current
state only by a reader noticing the date.

**Remedy in `ACT-062`:** the paragraph rewritten to state the repository is now public, that private
vulnerability reporting is therefore available to enable but is verified — via
`GET /repos/pipoventures/surfaceplate/private-vulnerability-reporting`, which currently answers
`enabled: false` — not enabled today, with enabling it listed in `org/HUMAN_ACTIONS.md`, and that
until it is, there is no confidential channel here.

**That remedy went stale in turn, on 2026-09-08: `F127`.** The quoted `enabled: false` above is
preserved as the record of what was written and verified on 3 September — it is not the current
state, and has not been since the setting was turned on. `F127` records why correcting the value
was not enough.

## F117 — `README.md` said the package was not published to PyPI after `0.16.0` and `0.16.1` were both on the index

**Severity: medium. Closed.**

Recorded on 2026-09-03 in this session (https://claude.ai/code/session_01QAovBCSt2UGXo3KZn3WtFW).
`README.md:63` read *"Not `pip install surfaceplate` — this is not published to PyPI yet."*
`DR-61`/`H8` record that `0.16.0` was uploaded on 2026-09-03 by the maintainer's own dispatch of
*Publish to PyPI*, and `0.16.1` followed the same day; the sentence had been true when written and
was overtaken by that action without being revisited — the same supersession shape as `F118`, found
in the same pass because the two documents make opposite-direction mistakes about the same
underlying fact (one claims public when it was private; this one claims unpublished when it is
published).

**Remedy in `ACT-062`:** the sentence rewritten to state that the name is reserved and both
versions are on the index, each carrying the `Development Status :: 3 - Alpha` classifier, while
preserving `DR-61`'s actual intent — every instruction here still names the git form until 1.0, so
"not independently audited" is not contradicted by anything an adopter is told to run.

## F116 — The README's front door said "no adopting repositories" after Plutos had adopted, and "does not install its own standard on itself" weeks after it did and passed

**Severity: medium. Closed.**

Recorded on 2026-09-03 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) while preparing the package's public links (`ACT-061`).
The status line and two bullets under "Status and limitations" described a repository that no
longer existed: no adopters (Plutos adopted on 2 September and was upgraded to the published
release on 3 September), and a publisher not installed on itself (closed by `DR-13`'s work, checked
on every pull request since). Both are the front door PyPI renders, and both understated in the
direction that reads as modesty, which is why nobody caught them: a stale claim that flatters is
found fast, one that undersells is left alone. Medium: the `F57`/`F70` shape on the most-read file.

**Closed by `ACT-061`, 2026-09-03.** The status line says one adopting repository, the owner's own;
the adopter bullet names Plutos and says what one owner's use is and is not evidence of; the
self-installation bullet says what is true and what passing one's own check establishes.
`tests/check_code_registers.py`'s front-door checks read the README and pass; the sentence about
adopters is prose and stays a reading matter, recorded here so the next reader of this file knows
the front door has been wrong twice.

## F115 — The `v0.16.0` tag points at a tree 235 commits older than the commit published to PyPI as 0.16.0, with the manifest at a different path, so "check out the tag" yields a different framework anchor

**Severity: medium. Closed.**

Recorded on 2026-09-03 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) while designing the independent review packet
(`ACT-060`). `git tag` puts `v0.16.0` at `1b0df98` (31 August); the release published to PyPI on
2 September was built from `b60cb5bbbe5e…`, 235 commits later, and at the tag the manifest sat at
the repository root. A reviewer told "check out the tag" would hash a different manifest and report
a mismatch that is not one, or worse, attest to a tree nobody shipped. Medium: the version string
is the same on both trees, so nothing warns.

**Remedy in `ACT-060`:** the packet names the published commit and says not to use the tag.
**State on 2026-09-03:** annotated tags `pypi/0.16.0` (at `b60cb5bbbe5e…`, run 33697386488) and
`pypi/0.16.1` (at `3231f3a8851c…`, run 33734780614, the release that carries the PyPI links) are on
`origin`, pushed by the agent after the 0.16.1 publish and verified with `git ls-remote --tags`.
`v0.16.0` was not moved; it stays as a record of what it was. The push was provisional until
the maintainer ratified both tags the same day (`H14`, closed), which closes this finding: a
reviewer told "check out `pypi/<version>`" now lands on the published tree. Not done, and left as a
note rather than a finding: a refusal in the publish workflow when the version's tag does not point
at the commit being published.

## F114 — The audit hand-off stated the bundle's file count in four places and only one was checked, so three read "15" after the bundle grew to 27, and the full prompt still said "five" suites

**Severity: low. Closed.**

Recorded on 2026-09-03 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) while designing the independent review packet
(`ACT-060`). `tests/check_audit_packet.py` checked the count in the one sentence it parsed; the
README's "curated 15-file subset", the curated prompt's "these 15 files" and "Verdict on the 15
files reviewed", and the full prompt's "the five test suites" were not read by anything and stayed
where `ACT-052` and `DR-55` left them. The `F50` shape again: a document read for sense rather than
run.

**Closed by `ACT-060`, 2026-09-03.** All four corrected; the check now reads every place the file
count is stated and holds each to the command's list, seen to fail first on three of them. The
suite count in the full prompt is prose and stays a reading matter.

## F113 — A validator check built "today at midnight UTC" and expected it to be in the past, which is false for the first hour of the day on a UTC+1 machine (the `F48` shape)

**Severity: low. Closed.**

Recorded on 2026-09-03 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z), found when the clock crossed midnight during
`ACT-059`: `tests/test_adopt.py::test_validators_refuse_what_the_checker_rejects` accepted
`effective_from` as `<today>T00:00:00+00:00` and expected the validator to accept it; at 00:20 BST
that instant is forty minutes in the future, and the validator was right to refuse it. `F48` found
the same shape in the checker; this is the same shape in a test, which is where `S1`'s habit of
checking a claim about time against the clock it runs on applies. Low: one check, one hour a day,
one timezone.

**Closed 2026-09-03.** The check uses an instant one minute in the past, in the local offset,
which is in the past wherever and whenever it runs. Seen to fail first, by the clock.

## F112 — The matrix's `advanced` case compared two profiles assembled seconds apart without normalising the scaffolded instant, and failed on the runner once

**Severity: low. Closed.**

Recorded on 2026-09-02 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) from PR #65's self-check: `T5-150` failed "advanced and
simple registers assemble the same profile" on the runner after passing locally and on three earlier
runner runs. The case assembles the profile twice, once per explanation register, and a scaffolded
gate binds from the instant of its creation (`F47`); when the second flow crosses a second boundary
the two instants differ. Every other route equality in the suite normalises instants; this one did
not. Low: a false red on a harness comparison, found on its fourth run.

**Closed 2026-09-02.** The comparison normalises instants as the others do, and prints the differing
lines. `T5-150` re-run green; the report is unchanged (the case has one check either way).

## F111 — The reviewer holds the narrative docstrings and the size of the governance apparatus to be a maintenance risk and disproportionate for a CLI tool (pass-2 §9)

**Severity: low. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

The reviewer's two points: module docstrings in `sections.py`, `defaults.py`, `scaffold.py` and
`wizard.py` carry the history of past defects and decisions, which will drift from the code (as
`F52` and `S1` already record); and nineteen gates, twelve controls, fifty-six codes, two adoption
routes and sixteen seeds are a heavy apparatus for a local tool. **Assessment:** the first is a
real cost this repository chose knowingly - `S1` names the drift and the habit that meets it, and
the docstrings are where a reader of the code meets the reason a line exists - and the second is
a judgement about the product's purpose rather than a defect in it. Both are the maintainer's to
weigh (`H13`); the recommendation is to keep the practice and record the choice.

**Closed 2026-09-03, the maintainer having decided to keep the practice (`H13`).** The docstrings stay: they are where a reader of the code meets the reason a line exists, and `S1` names the drift they risk and the habit that meets it - a docstring's claim is checked when the code beneath it is touched, which `F55` and `F52` record happening. The size of the apparatus is the product's purpose, not a defect in it; each gate, control and code is there because a reviewed defect put it there, and the registers say which. Recorded as considered and declined, with the reviewer's text kept verbatim in the review.

## F110 — This repository's own hand-written profile carries none of the checked/declared labels the wizard writes since `F53`, so its reader cannot tell a verified control from a declared one (pass-2 §7)

**Severity: low. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

`F53` gave the wizard a label per control - "checked against this repository" or "DECLARED ONLY" -
derived from the checker's own `VERIFIED_CONTROLS`, written as a comment beside each control. This
repository's profile predates that and was written by hand; it carries no such label, so the
reviewer's point holds for the one profile in the bundle. **Remedy proposed (`H13`):** add the same
labels, from the same table, as comments beside each control in `governance/application-profile.yaml`.

**Closed by `ACT-059`, 2026-09-02, approved by the maintainer (`H13`).** Every control in this repository's profile carries the label the wizard writes, produced by the same `render._assurance_note` from the checker's own `VERIFIED_CONTROLS`: six checked against this repository, two declared only.

## F109 — This repository's own profile mirrors two gate deferrals as `x-…-gate` control deferrals under `adoption.deferrals`, duplicating what `prerequisites` already records (pass-2 MIN-03)

**Severity: low. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

`adoption.deferrals` holds `x-surfaceplate-work-contract-gate` and `x-surfaceplate-risk-classification-gate`,
each restating a gate that `prerequisites` already records as `deferred` with an owner and a date.
The schema's `deferral` is for a *control*; the `x-` prefix is the extension escape, used here to
name a gate. Two records of one deferral is two places for them to disagree. **Remedy proposed
(`H13`):** remove the two entries, leaving the gates' own deferrals as the record.

**Closed by `ACT-059`, 2026-09-02, approved by the maintainer (`H13`).** The two `x-…-gate` entries are removed and `adoption.deferrals` is empty; each gate's deferral is recorded once, under `prerequisites`, with its owner and date. A comment at the field says why.

## F108 — The wizard writes `notes: Blocking.` under the adopter's scanner without asking or verifying it (pass-2 MIN-02)

**Severity: low. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

`sections.SCANNER_NOTES = "Blocking."` is written under every profile's scanner; the provenance
allow-list admits it as the one sentence the tool contributes, and the sidecar records it as
computed, "the framework's own note". The reviewer is right that it is a statement about the
adopter's scanner, not about the framework: `SP047` checks that the step can fail the build, but
the note is written before that check runs. **Remedy proposed (`H13`):** omit the note (the schema
does not require it) and let `SP047` say what it verified.

**Closed by `ACT-059`, 2026-09-02, the maintainer having chosen to omit the note (`H13`).** The builders write a scanner with a name and where it runs, and nothing else; the renderer prints a note only where a profile already carries one; the provenance allow-list admits no framework prose beyond the gate definitions. Regression: `tests/test_adopt.py::test_the_tool_writes_no_note_about_the_adopters_scanner`, seen to fail first. The matrix report regenerated: one `computed` origin fewer per case, nothing else.

## F107 — The template test treats a profile as the untouched template when any one identifying scalar is still `replace-me`, so a half-completed profile can be overwritten (pass-2 MIN-01)

**Severity: medium. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

`F63` moved the test from the whole file to five identifying scalars, and made *any one* of them
still reading `replace-me` mean "the template". A profile a human has filled by hand but for one
of those scalars is then overwritten without a prompt - the class of loss `F63` was closing.
**Remedy proposed (`H13`):** the template is the file in which *every* identifying scalar still
reads `replace-me`; anything else is refused as already adopted, and the message says which scalar
still carries the token so the human can finish or move it aside.

**Closed by `ACT-059`, 2026-09-02, the maintainer having authorised the fix (`H13`).** The template
is the file in which every identifying scalar still reads `replace-me`; anything else is refused,
and the message names the scalars that still carry the token. Regression:
`tests/test_adopt.py::test_a_half_completed_profile_is_not_the_template`, seen to fail first on both
checks; the matrix's refusal cases unchanged.

## F106 — This repository's own profile declares `agent_work_packets` required as a practice while deferring `work_contract` because the packets are not committed: two rationales that contradict each other (pass-2 MAT-04)

**Severity: medium. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

The baseline rationale says every packet "arrives as a bounded packet with stated done-criteria
... the register now records it"; the gate's rationale says the packets "are not committed here,
so there is no artefact for the gate to check". Both are true and the first over-reads the second:
the packets exist in operator conversations and their *outcomes* are registered; the packets
themselves are not in git, which is exactly why the gate is deferred and why `CONFORMANCE_LEVELS.md`
lists the control as declared, not checked. **Proposed wording for the baseline rationale (`H13`):**
*"Every change arrives as a bounded packet with stated done-criteria, given in the operator
conversation that authorises it; the packets are not committed, so this control is declared and
not checked, and the `work_contract` gate is deferred until they are. The activity register records
each packet's outcome."*

**Closed by `ACT-059`, 2026-09-02, the wording approved by the maintainer (`H13`).** The baseline rationale now says the packets are given in the operator conversation and not committed, that the control is declared and not checked, and that the gate is deferred until they are; the gate's rationale is unchanged and the two agree.

## F105 — `adoption_status: complete` needs no rationale and no evidence reference to validate (pass-2 MAT-03)

**Severity: low. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

True as stated: the schema requires `status_rationale` for `blocked` and `deferred` only, and
`independent_validator` may be null. **Assessment:** `adoption_status` is the profile's lifecycle
field - is the adoption catalogued and current - and the standard keeps lifecycle, validation and
approval distinct on purpose (principle 7, `REVIEW_AND_EVIDENCE.md`); the evidence the reviewer
asks for lives in assurance-evidence records, which this repository now keeps under
`governance/assurance/`. Requiring a rationale for `complete` is cheap and would make the claim
explain itself; requiring an evidence reference would fold two states into one field. A schema
change is a public contract: the maintainer decides (`H13`).

**Closed by `ACT-059` under `DR-63`, 2026-09-03.** `complete` requires `status_rationale` as `blocked` and `deferred` do; the wizard asks it for `complete`; no evidence reference is required, since evidence lives in the assurance-evidence records. Seen to fail first in the contracts suite.

## F104 — The schema's `effective_from` pattern admits impossible dates and a fraction without seconds; the checker rejects them, so the pattern documents a form it does not enforce (pass-2 MAT-02)

**Severity: low. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

Verified: the pattern matches `2026-02-31`; `rules.effective_from_state` reports it unreadable, so
the checker refuses it and the wizard's validator refuses it at the field. The pattern is a shape
check, as every date pattern in the schema is; calendar validity is the checker's. The fraction
without seconds (`14:30.500`) is admitted by the pattern and parsed by the rules; tightening the
pattern so the fraction follows seconds only is one character and a public-contract change
(`H13`). The second half of the finding - a same-day date, gated commits earlier that day, and an
instant that then cannot be moved forward - is `F92`, decided by `DR-60` yesterday: the rule stays,
and the wizard proposes the adoption date so that a human can only widen the window from it.

**Closed by `ACT-059` under `DR-63`, 2026-09-03.** The pattern admits a fraction only after seconds, in the schema and in `rules._ISO_INSTANT` alike; calendar validity stays the checker's, which already refused an impossible date. Eleven contract cases, seen to fail first.

## F103 — `--answers` writes every proposal the human left standing, so a record completed by filling only the needs-human lines carries the framework's example rationales under the adopter's name (pass-2 MAT-01)

**Severity: medium. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

`DR-49` designed the non-terminal route so: the record shows every proposal with its origin, the
human changes what is wrong, and the interactive route is the same act - proposals presented on
the review and approved once (`DR-47` (3)). The sidecar then records each such value as `example`
or `computed`, never as typed, so the profile does not claim the adopter wrote them. The reviewer's
point is that a record needs no acknowledgement that the proposals were read. **Alternative
(`H13`):** one line in the record, `accept_proposals: needs-human`, that must be set to `yes` before
replay writes - one human act for the document, as the review's approval is.

**Closed by `ACT-059`, 2026-09-03, the maintainer having chosen the acceptance line (`H13`).** The answers record carries `accept_proposals: needs-human`, the header says what setting it to yes means, and `replay` refuses until it is set - one act for the document, as the review's approval is. Regression: `tests/test_adopt.py::test_replay_writes_nothing_until_the_proposals_are_accepted_as_one_act`, seen to fail first; the matrix's nine propose-and-replay cases each assert the refusal before acceptance.

## F102 — A seed satisfies `SP032` on the day it is written, so a repository can pass every seeded gate with no practice behind it (pass-2 CRIT-02; the risk `DR-43` states)

**Severity: medium. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

This is the risk `DR-43` names in its own text and `scaffold.py` carries in its docstring: a
register that exists satisfies the gate's structural check while the practice it stands for may
not happen, and the three mitigations are prose. The reviewer's remedy - a placeholder in the
seeds so `SP032` fails until the adopter writes - is the design `DR-43` rejected: it makes the
wizard create a file that fails the checker on the next run, which is what `F15` made the
templates do. **Alternative (`H13`):** the checker can tell a seed from a kept register, because it
ships the seeds: an artefact byte-identical to a shipped seed earns an advisory, "seeded, holds no
entries yet", on every run until it changes. Verifiable, honest, and not a failure; the maintainer
decides between that, the reviewer's remedy, and leaving `DR-43` as it stands.

**Closed by `ACT-059`, 2026-09-03, the maintainer having chosen the seed advisory (`H13`); `DR-43` stands.** The seeds now travel with the checker (`.standards/seeds/`), and a gate artefact or a pattern-A reference byte-identical to one earns an advisory on every run - "seeded, holds no entries of this repository's own yet" - until the file changes; never a finding. `core/PREREQUISITE_GATES.md` states it beside the rule it qualifies. Regression: `tests/test_install_and_check.py`, the seeded-register case, seen to fail first; the advisory goes when a line is added.

## F101 — A run that fails after the scaffold has written its seeds leaves them on disk and reports them rather than removing them (pass-2 CRIT-01)

**Severity: medium. Closed.**

Recorded on 2026-09-02 from the second cross-provider adversarial review (`audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md`, `H3`, run by the maintainer with the curated prompt and reproduced verbatim there; provider and model as the maintainer states), assessed in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z) against the code and this repository's profile.

The reviewer reads the module docstring's "a cancelled run leaves the repository untouched" as a
claim about failure; it is about cancellation, which holds - nothing is written before the review
is approved. What the reviewer describes is real all the same: the seeds are written before the
profile (so the profile never names a file that does not exist), and a failure at the profile
write raises `PartialWrite` naming every created file, by the decision at code item 7 of the
first review, rather than deleting them. **Alternative (`H13`):** delete the files this run created
- and only those, created with `open(..., "x")` seconds earlier - when the profile write fails,
and say so; the draft still holds the answers. Reporting stays the fallback where a deletion
itself fails.

**Closed by `ACT-059`, 2026-09-02, the maintainer having chosen the rollback (`H13`).** A failure at the profile or sidecar write now removes the files this run created (`scaffold.rollback`: the files, then the directories they left empty), and `PartialWrite` names what was removed and anything it could not remove; the CLI prints both. The draft keeps the answers. Regression: `tests/test_adopt.py::test_a_failed_write_removes_the_seeds_this_run_created`, seen to fail first; the scaffold suite's assertion that the file "really is on disk" - the first review's code item 7 - is replaced by the removal, with the reason beside it.

## F100 — `--edit` applied no field validator, so an artefact edited to an untracked path was written and failed `SP032` on the next run

**Severity: medium. Closed.**

Recorded under `ACT-057` on 2026-09-02 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z), predicted from reading
`wizard.edit` while the matrix was designed and confirmed by its edit cases (`T6-194`, `T6-195` in the tracked report)
before the fix: the edit went through, the checker then reported `SP032` against the profile.

`edit` verified the rendered profile against the schema and the placeholder scan - the write-time
checks - and applied none of the field validators `DR-48` gave the wizard so that it refuses what
the checker rejects. An artefact edited to a path nothing tracks, an `effective_from` in the
future, a `review_by` beyond the horizon, a scanner file that never mentions the scanner: each is
refused at the field during a run and was accepted by `--edit` after it. Medium: the profile then
fails its next check with a code, so nothing is hidden; but the command exists so a human can fix
one line without a run, and it let them break the line the same way the run would have stopped.

**Closed by `ACT-057`, 2026-09-02.** `edit` rebuilds the `FieldSpec` behind the edited line from
the profile's own level, interface answer and scanner name (`wizard._spec_behind`) and applies
`validators.check` before rendering, refusing with the field's own words and the path. Regression:
`tests/test_adopt.py::test_adopt_edit_applies_the_fields_own_validator`, seen to fail first on all
four classes; the matrix's edit cases assert the refusal and an unchanged profile. The pre-fix output
is preserved verbatim in `audit/validation/ADOPT_MATRIX_FIRST_RUN.md`.

## F99 — `--propose` marked every above-floor control's rationale and reference `needs-human`, so a human had to invent lines for controls they never declared before `--answers` would write

**Severity: medium. Closed.**

Recorded under `ACT-057` on 2026-09-02 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z), from the matrix's propose-then-replay
cases (`T6-162` to `T6-167` in the tracked report): at `essential` and `standard` the answers record carried up to
thirteen `needs-human` lines for controls beyond the floor, and `--answers` refused until every one
was filled, whether or not the control was listed in `controls.above_floor`.

`propose` walked the remainder plan's fields without regard to `depends_on`, so the conditional
fields - a rationale and a reference that apply only when their control is ticked - were written
as decisions outstanding. The existing replay test filled every `needs-human` line with a stock
sentence, which is exactly how the defect survived it: a human doing the same would put invented
rationales under their own name for controls the profile then does not even declare. Medium: no
wrong profile results, but the non-terminal route demanded answers to questions the interactive
route never asks.

**Closed by `ACT-057`, 2026-09-02.** The record holds those lines apart under
`if_declared_above_floor`, the header says they apply only to a control listed in
`controls.above_floor`, and `replay` applies them to the listed controls and no other; a listed
control's line left `needs-human` is refused by name. Regression:
`tests/test_adopt.py::test_propose_does_not_demand_rationales_for_controls_nobody_declared`, seen
to fail first. The pre-fix output is preserved verbatim in `audit/validation/ADOPT_MATRIX_FIRST_RUN.md`.

## F98 — A run cancelled after the scaffold stage and resumed never created the adoption decision record: the profile named `DR-0001` and the sidecar said "created" for a file that did not exist

**Severity: high. Closed.**

Recorded under `ACT-057` on 2026-09-02 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z), predicted from reading `Flow.draft()`
and `scaffold_offers()` while the matrix was designed and confirmed by its resume-after-review cases
(`T6-182`, `T6-187`, `T6-192` in the tracked report) before the fix: the created-file set lacked
`docs/decisions/DR-0001-adopt-surfaceplate.md` while the profile cited the id and the sidecar
recorded it as scaffolded, "created: docs/decisions/DR-0001-adopt-surfaceplate.md".

The draft drops `scaffold` from the stages done, so a resumed run offers the scaffold again; every
gate and control seed is re-offered because the offer is keyed on the seed path being named and the
file being absent. The decision record's offer was keyed on the id being **unanswered**, and the
cancelled attempt had answered it as scaffolded. High: a profile and a machine-owned provenance
record both asserting a file exists that does not, produced by the ordinary act of quitting at the
review and coming back - and the checker does not read the record, so nothing would have said so.

**Closed by `ACT-057`, 2026-09-02.** The offer stands while the id's recorded origin is
`scaffolded` and the file is absent (`Flow.scaffold_offers`), as a gate's seed does. Regression:
`tests/test_adopt.py::test_resuming_after_the_scaffold_stage_still_creates_the_decision_record`,
seen to fail first; the matrix asserts the exact created-file set on every resume. The pre-fix output
is preserved verbatim in `audit/validation/ADOPT_MATRIX_FIRST_RUN.md`.

## F97 — At `essential` the above-floor list offered `documentation_authority`, and a profile declaring it fails `SP052` on its first check

**Severity: medium. Closed.**

Recorded under `ACT-057` on 2026-09-02 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z), from the matrix's above-floor cases at
`essential` (four cases before the fix; after it the control has no case to tick, and `T4-115` and
`T4-123` tick every control that remains): ticking `documentation_authority` at `essential`, alone
or with every other control, wrote a profile the checker met with `WARN` and `SP052`
"documentation_authority is required without the gate that verifies it".

The checker's rule is deliberate and documented (`core/CONFORMANCE_LEVELS.md`): the control is
verified through the `authority_map` gate, and `SP052` closes the seam a level being a floor would
otherwise open. The wizard reads the same catalogue and offered the combination anyway, on the one
level whose gate list does not declare the gate. Medium: the finding is graced and named, so the
adopter is told at once; but the wizard had written a profile it could have known the checker
faults, which is the class `DR-48` exists to remove.

**Closed by `ACT-057` (`DR-59`), 2026-09-02.** A control verified through a gate the level does
not declare is withheld from the above-floor list (`plan.WITHHELD_ABOVE_FLOOR`) and the field's
help names the gate and the code. Regression:
`tests/test_adopt.py::test_a_control_verified_through_an_undeclared_gate_is_not_offered_above_the_floor`,
seen to fail first; matrix tier T4 green at every level. The pre-fix output is preserved verbatim in
`audit/validation/ADOPT_MATRIX_FIRST_RUN.md`.

## F96 — With the gates beyond the floor folded, Ctrl+S refused by naming a folded gate: an optional gate read as required

**Severity: medium. Closed.**

Recorded under `ACT-056` from the maintainer's fourth run, at `standard` with a user interface,
on 2026-09-02 in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by `ACT-056` under `DR-57`.

The maintainer's words, on the screenshot: *"work_contract is required to progress although it
should be optional."* The screen showed the eight-gate floor complete and "Beyond the standard
floor: 11 gates, not required · [Ctrl+O] open"; Ctrl+S answered "work_contract: choose a status
before continuing." The rule is `DR-47` (4): a gate beyond the floor is undecided until a human
declares it, singly or in one bulk act, and the key legend named the bulk command. But `DR-56`
folded those gates away, so the refusal named something the reader could not see and read as a
requirement. Medium: the first thing a reader meets after the fold is a contradiction between
"not required" and "choose a status before continuing".

**Remedy (`DR-57`):** at Ctrl+S with folded undecided gates, one question naming the count:
declare them all not applicable as one recorded act, or open them and decide each.

**Closed by `ACT-056` (`DR-57`), 2026-09-02.** Ctrl+S with the fold closed and gates behind it undecided pushes `FoldedUndecidedScreen`, which names the level and the count and offers two keys: `y` runs the bulk command (recorded as one act with its count, as before) and continues; `n` opens the fold on the first undecided gate; Ctrl+Q returns to the list unchanged. With the fold open an undecided gate still refuses by name, because the reader can see it. `tests/test_adopt_tui.py::test_continuing_past_the_folded_gates_asks_once`, seen to fail first on all three outcomes.

## F95 — A focus-driven scroll is animated, and the scrollbar keeps a fractional thumb position from the animation's last frame, so a golden of a scrolled screen differed one run in four

**Severity: low. Closed.**

Recorded under `ACT-055` on 2026-09-02, in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z), from the gate-list golden
failing one local run in four after `DR-56`'s fold, with CI green on the same commit.

The two end states differed in two cells: the scrollbar's thumb glyph. The list's measured size
and scroll offset were identical; the scrollbar's own `position` was `56.125`, `55.5`, `55.875`
across runs. Textual animates the scroll that follows a focus, and the scrollbar widget keeps
whichever intermediate value its last frame saw, so the thumb's eighth-block glyph varied with
timing. `F90`'s two-pass reveal did not touch it: that scroll is immediate, the focus's own is
not. Low: two cells of a scrollbar; but a golden that differs one run in four is a red build
waiting to happen, and the cause would have been invisible from the runner.

**Closed by `ACT-055`, 2026-09-02.** Both apps set `animation_level = "none"`, as do the three
test hosts, so every scroll lands exactly; on a 24-row form the animation bought nothing. The
gate-list golden regenerated from the converged state and the suite run six times unchanged.
Found by capturing the frame sequence across runs and diffing the two end states, then reading
the scrollbar's own position.

## F94 — An archived document is proposed as a gate's artefact on a keyword match: two gates were proposed files under `docs/archive/`

**Severity: medium. Closed.**

Recorded under `ACT-054` from the maintainer's third run of `adopt`, at `full` on a fresh scratch copy of Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by `ACT-054`.

`equivalence_evidence` was proposed `docs/archive/investingos_repo_review_protocol.md` and
`dependency_output_delta` `docs/archive/investingos_codex_repo_review_prompt_pack.md`, both
recorded as *discovered: the closest match*, both matched on the words `protocol` and `review`.
Both are archived: the path says so. An archived document is not the precondition a live gate
audits against, and the checker later followed each through a rename it had already had. Medium:
the same shape as `F84`, the proposal made where the honest answer was no match, with archive
paths as the tell.

**Remedy hypothesis:** paths under an `archive` directory are never proposed and are ranked
last; they stay offered.

**Closed by `ACT-054` (`DR-51` (5)), 2026-09-02.** a path with an archive component (`archive`, `archived`, `attic`, `deprecated`) is never proposed for a gate or a control reference and ranks last among the matches; it stays offered. The same test, seen to fail on the archived-only match.

## F90 — A render test read the screen before the deferred scroll had run, and turned `main` red on the runner while passing locally

**Severity: low. Closed.**

Recorded under `ACT-051` on 2026-09-02, in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z), from the self-check run of
`main` at `a6ebca6` (PR #51's merge) and PR #52's first run, both `RENDER=FAIL (4 failed)` on
`test_every_classification_option_is_on_screen_and_a_text_area_shows_three_lines`, while PR #51's
own run and three local runs passed.

`ACT-049` made a focused field scroll to the top of its container after the next refresh
(`screens.reveal`). The test paused twice after focusing and read the screen. The first
diagnosis was timing - the refresh had not happened on a loaded runner - and a bounded wait was
added; the runner failed the same way with the wait, so that diagnosis was wrong. The runner's
own rendered screen, read from the failing check's detail, showed what had happened: the scroll
had gone past the radio set by exactly its height, leaving the field's help at the top of the
frame and its four options above the fold. The scroll ran against a layout in which the field's
rows were not yet measured; locally the layout had settled first. Low: a false red, no defect in
what the wizard writes, but a real one in what it shows on a slow machine.

**Closed by `ACT-051`, 2026-09-02.** `reveal` runs twice: once when the help is shown and once
after the next refresh, through `Widget.scroll_visible` so every scrolling ancestor takes part;
the second pass is a no-op when the first was right and the correction when it was not. The test
also waits, bounded, until the layout has settled. Two earlier attempts are recorded in the
branch's commits: an immediate single scroll (undone by the relayout that follows) and the wait
alone (the runner failed identically). The runner passed on the third push.


## F89 — The opening screen is text only; the maintainer asked for a mark

**Severity: low. Closed.**

Recorded under `ACT-050` from the maintainer's second run of `adopt`, against a scratch copy of Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). Closes by an activity the maintainer authorises; each changes what is asked, so a decision record precedes it (`DR-47`).

The maintainer's words: *"Home page is not visual enough. Something resembling a logo or something
more visual (like a geometry) would be nice there."* The opening screen (`F81`, `DR-51` (2)) is a
title row and prose. A mark has to fit the same 24 rows at 80 columns, render in any monospace
font, and take the title row's place rather than add to it. Low: nothing is wrong, and the choice
of mark is the maintainer's.

**Remedy hypothesis:** a four-row mark in box-drawing characters above the tool line, chosen by
the maintainer from alternatives, held by the opening screen's snapshot.

**Closed by `ACT-051` (`DR-53`), 2026-09-02.** The slab, generated from its geometry in `tui/mark.py` with the monogram on its top face, the tool line and tagline beside it; the screen's frame without vertical padding so it fits 24 rows with the draft note. Chosen by the maintainer from four alternatives and corrected twice on rendered previews (the right face was one row too deep and the slant too short by hand; the generator cannot get that wrong). `tests/test_render.py::test_the_slab_is_drawn_from_its_geometry` and the extended opening-screen test, seen to fail first on every slab row; the golden regenerated for cause.

## F86 — A hand edit to the profile after the write leaves the provenance record asserting the old origin; nothing records a post-write edit

**Severity: low. Closed.**

Recorded under `ACT-048` from the maintainer's completed `H1` run of `adopt` against Plutos on 2026-09-02, reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z). No closing activity yet; it needs a decision of its own.

The closing report tells the adopter to *"edit application-profile.yaml directly from here"*,
and Plutos's two checker findings are fixed exactly that way. The sidecar then still says
`discovered` beside a value a human typed, and its header says it is machine-owned and not to be
edited by hand. `DR-47` records origins for the wizard's write and is silent on what comes
after. Low because the checker does not read the sidecar; it matters to whoever reads the record
to know what was asked and what was typed, which is the record's only purpose.

**Remedy hypothesis:** an `adopt --edit <path> <value>` that records the edit as typed with a
timestamp, or a checker note when the profile is newer than its record. A decision, not
`DR-51`'s.

**Closed by `ACT-052` (`DR-54`), 2026-09-02.** `surfaceplate adopt --edit <path> <value> [--because <reason>]` changes one line of the written profile through the same renderer and verification as the wizard and records it in the sidecar as typed with a timestamp and the reason, under a history of edits the header now describes; a path the profile lacks is refused with the nearest named, and a line the review marks as not editable is refused. `tests/test_adopt.py::test_adopt_edit_rewrites_one_line_and_records_it` (a scalar, a list element by index, three refusals, the CLI flag, the checker still passing), seen to fail first.

**Evidence after the fact, 2026-09-02 (recorded under `ACT-056`'s closure).** The hand edit this finding was written about broke the record it was made in: the two `detail` values written by hand into Plutos's sidecar that afternoon held a colon and were not quoted, so the file did not parse as YAML from plutos#6 until Surfaceplate's own verification of the adoption, run read-only against the repository, tried to read it (repaired as plutos#7, values unchanged). The checker never reads the sidecar, so CI stayed green throughout. The path that avoids this, `adopt --edit`, is the remedy above.

## F82 — The wizard explains its fields, not the framework: a reader who does not know Surfaceplate cannot adopt it from the wizard alone

**Severity: high. Closed.**

Recorded under `ACT-047` from the maintainer's first `H1` run of `adopt` against Plutos on 2026-09-02, in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z); the maintainer agreed the finding in the same session. Closes by the activity the maintainer authorises once `H11`'s decision is taken.

The maintainer's words, after calling the rebuilt wizard *"a massive improvement"*: *"I still feel
that is missing something in terms of UX and UI but I'm not sure yet. It's just a feeling. Main
issue is that I'm implementing a package that applies my own framework and I still don't know
100% what everything is. Imagine someone new to it? I can help with package documentation, the
surfaceplate.org website maybe, but I want someone going directly to the adoption to make it easy
for them."*

The framework's author, running its wizard against his own repository, could not always say what
a question was for. The wizard is the path most adopters will take, and it presumes the reader
has read `core/`: each screen states what it asks, and none states what the answer decides
downstream (which controls, which gates, which check fails), what the default is and why, or what
a wrong answer costs. `F80` and `F81` are two concrete instances. This finding holds the general
defect so the remedy is designed once rather than screen by screen, and records the maintainer's
unresolved feeling as an open hypothesis rather than smoothing it into the two concrete items.

**Remedy hypothesis:** a stated minimum for every screen, for a reader meeting the framework for
the first time: why this is asked, what it decides, the default and its reason, and what a wrong
answer costs, drawn from the plain-English register in `explanations.py` so the wizard and the
documentation say the same thing. Whether that minimum is met is then a snapshot question
(`ACT-046`'s suite) rather than a feeling. A design decision, not a code fix: `H11`.

**Closed by `ACT-048` (`DR-51` (3)), 2026-09-02.** every field the flow presents, at every level and both interface answers, and every field a review edit can reach, carries what is asked, what the answer decides and what a wrong answer costs (`FieldSpec.decides`, `FieldSpec.wrong`), shown beside the focused field with the field kept at the top of its scroll container so the two are always on screen together. `tests/test_adopt.py::test_every_presented_field_states_what_it_decides_and_what_a_wrong_answer_costs` fails on any presented field lacking either; seen to fail first on every field. Presence is what the test proves; the text is judged by reading it, which is the maintainer's review of the PR.

## F77 — Hygiene: non-atomic profile write; a draft with the wrong shape or stale ids kills the run; non-UTF-8 paths quoted; `is_empty` never true; `human_roles: null` as `['None']`; unescaped enums; `KeyboardInterrupt` uncaught; `adopt` exits 0 on findings; the two reliance answers discarded

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-044`, `ACT-045`, `ACT-046`; see `org/REMEDIATION_PLAN.md`.

From the review's read-only correctness pass (report §7), each probed against throwaway directories: `wizard.py:321-324` writes the profile non-atomically and a truncated profile then fails `_refuse_if_already_adopted` forever; a JSON-valid draft whose `sections` is not a dict raises at `wizard.py:231-247` (exit 4) against the docstring's promise; a draft naming a level or gate no longer in the catalogue resumes and fails later with a bare `KeyError`; `_tracked_files` keeps `git ls-files`'s C-quoting, so `"docs/**` is offered as a pathspec and `docs/café.md` is dropped; `Discovered.is_empty()` can never be true because `candidate_paths` always appends `**`, and its documented fallback has no callers; `sections.build_wrap` renders `human_roles: null` as `['None']`; `render.py:203, 218, 221, 231, 256` interpolate enum values without `_scalar`; `cli.py:88`'s `except Exception` lets `KeyboardInterrupt` through as a traceback and the trailing check runs outside every handler; `adopt` exits 0 when the check it runs reports findings; `relied_on_outside_team` and `material_quantitative_output` are asked, validated, drafted and never written. Nine dead functions and twelve docstring-versus-code discrepancies are listed in the report.

**Two items closed by `ACT-044`, item 1.4 (2026-09-02); the rest stay open.** `_tracked_files`
runs `git ls-files -z`, so a non-ASCII path is offered verbatim
(`tests/test_discover.py::test_a_non_ascii_path_is_offered_verbatim`, `docs/café-register.md`);
and `candidate_paths` returns nothing when git can read nothing of the adopter's, so
`Discovered.is_empty()` is true on a non-git tree and its docstring describes a case that exists
(`::test_is_empty_is_true_when_git_cannot_answer`). Both seen to fail before and pass after.

**Five more items closed by `ACT-045` (2026-09-02); the rest stay open for `ACT-046`.** Code item 7:
a failure after the scaffold wrote raises `PartialWrite` naming the created files, and the CLI
prints them. Item 12: a parent that is a file is named as such, not as a race. Item 13: a missing
directory, a file and an uninstalled repository each get their own message and code (3, 3, 2).
Item 14: `KeyboardInterrupt` prints one line, keeps the draft, exits 130, and the trailing check
does not run. Item 17: `adopt` returns the checker's own exit code after a write, and exit 2 no
longer covers four conditions (`DR-49` (2)). Still open: the non-atomic profile write, a draft of
the wrong shape or with stale ids, `human_roles: null`, unescaped enums, and the two reliance
answers (`DR-50`, `ACT-046`).

**Three more items closed by `ACT-046` (2026-09-02).** Item 16: `sections.build_wrap` reads
`human_roles: null` as no roles and the renderer writes `[]`. Item 19: every enum-valued field -
`data_classification`, `conformance_level`, `adoption_status`, a gate's id and status, a control's
decision - is rendered through `_scalar`, and a value carrying a newline is refused rather than
written. Item 18: the two reliance answers are written under `risk` and recorded in the provenance
record (`DR-50` (2)); the schema admits them, both examples and the template carry them, and
`tests/validate_contracts.py` asserts they round-trip and that a non-boolean is refused. Still
open: the non-atomic profile write, and a draft of the wrong shape or with stale ids.

**The last two items closed by `ACT-049`, 2026-09-02.** The profile and its provenance record are written to a temporary file beside the target and moved into place (`wizard._write_atomically`), so the target is absent or complete, never truncated; `tests/test_adopt.py::test_the_profile_is_written_atomically` fails the move and asserts the template is untouched byte for byte and no temporary file remains. A draft naming a level or a gate the catalogue does not have, or whose sections are not answer maps, is not offered, is left in place, and the opening screen says why (`Welcome.draft_note`); `::test_a_draft_with_stale_ids_is_not_resumed_into_a_crash` seeds such a draft and asserts the run completes fresh. Both seen to fail first. Every item of this finding is now closed.

## F76 — Resuming a draft that chose the defaults route never offers defaults again

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-044`; see `org/REMEDIATION_PLAN.md`.

`_drive` skips any section already in `self.state` (`tui/app.py:203-204`) and runs `_take_the_defaults_route()` only in the tail of the `route` iteration (`:241-244`). Cancel at the proposals screen or anywhere after `route` commits, and the next run resumes into the full manual flow with every proposal gone. Probed headlessly: `resumed={…, "route": {"route": "defaults"}}` opens on `FormScreen`, no `DefaultsScreen`. Closed by `DR-47`'s flow, which has no route.

**Closed by `ACT-044`, items 1.1 and 1.7 (2026-09-02).** The draft (`DRAFT_FORMAT` 3) carries every
answer with its origin and which stages are done; `flow.Flow` re-proposes after the level on
resume and keeps whatever the draft holds. `tests/test_adopt_tui.py::test_resuming_a_draft_keeps_its_proposals`
resumes a draft cancelled before the scaffold offer and asserts the review still shows the
discovered artefact under its origin. A format-2 draft is not offered; it is left in place and
overwritten by the first completed stage.

## F75 — Candidates are capped at 200 before any gate ranking, so a large `docs/` pushes the register out; the comment says the opposite

**Severity: high. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-044`; see `org/REMEDIATION_PLAN.md`.

`discover._capped` (`discover.py:94`) cuts the artefact list to 200 at `:215`, `:232`, `:239` before `matched_for_gate` runs. A repository with 300 files under `docs/` and a real `activity/register.md`: the register is not in `found.artefacts` and `matched_for_gate` returns nothing, so the adopter gets no proposal, a dropdown of unrelated files, and the help "expect to create the artefact" for a repository that has it. The comment at `discover.py:168-171` says "Cut AFTER ranking, never before: capping first threw away the register and the CHANGELOG"; the cut moved one level up — `F55`'s class. The scan itself is fast (5,000 files in 18 ms).

**Closed by `ACT-044`, item 1.4 (2026-09-02).** `discover.scan` no longer caps anything:
`_capped` became `_dedupe`, and the only cut is per field, after ranking - `rank_for_gate`'s
`[:limit]` and `plan._from_candidates`' `[:discover.SHOWN]`. The comment that described the cut
as "after ranking" is true again, and says why it was not.
`tests/test_discover.py::test_ranking_happens_before_the_cap` commits 300 files under
`docs/archive/` ahead of `activity/register.md` and asserts the register is proposed and ranked
first; `::test_the_cap_is_on_the_offer_not_on_the_answer` now asserts every dropdown is at most
`SHOWN` long and the ranked-first candidate survives it. Seen to fail before (no proposal; the
first three offers were `docs/archive/note-00*.md`) and to pass after (`DISCOVER=PASS (29
checks)`).

## F74 — A validation error is erased by the focus move that reports it

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-043`; see `org/REMEDIATION_PLAN.md`.

On the real identity screen, with `application_id` blank and focus on `owner`, `Ctrl+S` moves focus to the blank field, does not dismiss the screen, and leaves the hint showing only the key legend at every pause afterwards (`vanish/identity-after-ctrl-s-from-owner-80x24`). `FormScreen.action_commit` writes the error into the hint and then focuses the field; `on_descendant_focus` calls `_set_hint()` with no error and overwrites it. The review's earlier image of that error was taken with focus already on the failing field, the one case where it survives. Found while driving the review's prototype.

**Closed by `ACT-043`, item 0.5 (2026-09-02).** `FormScreen.action_commit` now focuses the
failing field first, then records the error in `self._pending_error` and shows it;
`on_descendant_focus` re-shows the pending error rather than an empty hint, and the next
`action_commit` clears it. Focusing first alone would not have been enough: the `DescendantFocus`
event arrives after `action_commit` returns, so whatever the hint held at that moment was
overwritten. `tests/test_adopt_tui.py::test_a_validation_error_survives_the_focus_move_that_reports_it`
re-drives the review's sequence at 80×24 - `application_id` blank, focus on `owner`, `Ctrl+S`,
six pauses - and asserts the screen stays, focus is on the blank field, and the hint still
carries "This cannot be blank.". Seen to fail before (`ADOPT_TUI=FAIL (1 failed, 63 passed)`, the
hint reduced to the key legend) and to pass after (`ADOPT_TUI=PASS (64 checks)`). The vanish
image re-taken: before, the legend alone; after, the error above it.

## F73 — Every `action_cancel` is unreachable: Textual's priority quit binding fires first

**Severity: low. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-043`; see `org/REMEDIATION_PLAN.md`.

`App.BINDINGS` in Textual 8.2.8 carries `Binding('ctrl+q', 'quit', priority=True)`, so after `Ctrl+Q` on any screen `push_screen_wait` never resolves and `_SectionScreenBase.action_cancel`, `ReviewScreen.action_cancel`, `ScaffoldScreen.action_cancel` and `DefaultsScreen.action_cancel` are dead code. The net effect is still a cancel (`run()` returns `None`), so it costs nothing today except that "keeping your draft" on the review hint is true by accident of the CLI's exception handling.

**Not closed by `ACT-043` (2026-09-02).** This finding is recorded as closing by `ACT-043`, but
`org/REMEDIATION_PLAN.md` §4 phase 0 has no item for it: its eight items do not touch
`action_cancel` reachability. Item 0.6 handled one consequence of the same binding - a quit at
the resume prompt no longer deletes the draft - and nothing else. Left open rather than fixed
unplanned; the maintainer decides which activity closes it.

**Closed by `ACT-049`, 2026-09-02.** Both apps are declared with `inherit_bindings=False` and carry only Ctrl+C's notice, so Textual's priority `ctrl+q -> quit` no longer fires before a screen sees the key (an empty `BINDINGS` on the subclass is merged with the base class's, which the test found); every screen binds `ctrl+q` to its own cancel, the resume prompt included, which had none. `tests/test_adopt_tui.py::test_ctrl_q_reaches_the_screens_own_cancel` spies on `action_cancel` for the decisions form and the resume prompt and holds `F68`'s outcome at the prompt; seen to fail first with no cancel called and the app ending on `None`.

## F72 — Ten findings say Open in the body and Closed in the index, and `check_code_registers.py` never compares status

**Severity: low. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-046`; see `org/REMEDIATION_PLAN.md`.

`grep -nE '^\*\*Severity:.*Open'` against the index rows: `F7`, `F8`, `F9`, `F10`, `F11`, `F12`, `F13`, `F14`, `F16`, `F30` say Open in the body and Closed in the index; `F12` says both inside one section (`:541`, `:577`). `tests/check_code_registers.py` asserts uniqueness and index/body presence only (`:127-149`). `F11`'s shape recurring in the guard built for it. The review's first version also claimed nothing compares the digest anchor to what it anchors; that was wrong — `SP049` recomputes the vendored manifest's hash, and the vendored and source manifests cannot be equal by construction (`DR-45`); that half is withdrawn and the comparison that matters is `F6`.

**Closed by `ACT-046`, item 3.3 (2026-09-02).** `tests/check_code_registers.py` now reads every
index row's status column and every body's `**Severity: … <status>.**` line and fails when they
disagree on Open versus Closed, and when a body's status line leads with neither word. Seen to
fail on the ten (`F7`, `F8`, `F9`, `F10`, `F11`, `F12`, `F13`, `F14`, `F16`, `F30`) before they were
reconciled - each body already carried its own closing paragraph, or, for `F30`, the remedy
(`ACT-030`) that its last paragraph awaited had since been built - and each status line now
carries one italic sentence saying what the index had recorded and that the body still said Open,
so the correction does not depend on reading order. `CODE_REGISTERS=PASS (74 checks)` after.

## F71 — The standard's documents contradict themselves on what is checked, which principle limits a tool, whether Actions is enabled, how many gates are asked, and which evidence labels to use

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-045`; see `org/REMEDIATION_PLAN.md`.

`CONFORMANCE_LEVELS.md:68` "Ten of the twelve controls this framework defines are checked" against `:155` "Every control is checked", with an apology at `:72-76` for having made the mistake before; `:33` and `:70` cite "principle 9" for the limit on what a tool may claim, and `CONTROL_PRINCIPLES.md:11` principle 9 is change control (principle 11 is meant); principle 12 refers to a "B1 risk" defined nowhere; `PREREQUISITE_GATES.md:30-32` states GitHub Actions "is disabled at organisation level" while the README's opening demonstrates the opposite for this repository; `README.md:72` "all 19 prerequisite gates" is false at `essential`; `REVIEW_AND_EVIDENCE.md:30-36` and `ai-workflow.md:61-66` install two different evidence-label vocabularies; the checker emits 55 `SP` codes and the only catalogue an adopter is pointed at documents 20 (`SP038` is used in `INSTALL.md:35` and catalogued nowhere). About 17,000 words at `essential`, 63 defined terms, fourteen used before definition.

**Five of six corrected by `ACT-045`, item 2.5 (2026-09-02); one waits for `H10`.**
`CONFORMANCE_LEVELS.md:155` now agrees with `:68` (ten of the twelve are checked), and
`check_code_registers.py` asserts that sentence against the checker's own `VERIFIED_CONTROLS`
and refuses the contradicted form; `:33` and `:70` cite principle 11; `CONTROL_PRINCIPLES.md`
principle 12 names the risk it means instead of "B1"; `README.md:72` no longer says all 19 gates
are asked; `REVIEW_AND_EVIDENCE.md` uses the four labels `ai-workflow` installs, one vocabulary;
and every code the checker emits - 56 - is catalogued in a generated block at the end of
`CONFORMANCE_LEVELS.md`, written by `check_code_registers.py --write` and checked in CI. The
`PREREQUISITE_GATES.md:30-32` claim that GitHub Actions is disabled at organisation level is an
external fact only the account holder can read (`H10`); it is left as it stands, and this finding
stays open on that one item. The volume the review measured is the release plan's item 8.

**Closed by `H10`, 2026-09-02.** The maintainer read the organisation's Actions policy
(Settings, Actions, General) and showed it in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z): **enabled for all repositories,
all actions and reusable workflows allowed**, no pinning requirement. The README's description of
this repository was therefore the true one, and every pull request since publication had already
run the four checks. `PREREQUISITE_GATES.md`'s paragraph is rewritten rather than annotated: the
hook is client-side and bypassable; a server-side check exists only where the repository's owner
enables Actions and requires the check in a ruleset, which this repository does and an adopter must
do for itself. `DR-5` and `DR-7`, which recorded the disabled state as it was on 2026-08-30 and
2026-08-31, stand as history; `DR-13`'s "flagged not fixed" note is now fixed here.

## F70 — The front door: two incompatible install paths, a stale version line, two dead links, a pointer to an uninstalled file, and a global hooks path that stops the first command undocumented

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-045`; see `org/REMEDIATION_PLAN.md`.

Run as a stranger in a fresh venv: `surfaceplate install --dry-run` exited 4 with "STOPPED - Git hooks for this repository already run from somewhere else" because the machine sets `core.hooksPath` globally — a good message the README never anticipates; `surfaceplate`, `--help` and `--version` all print the same two-line usage to stderr and exit 2; `adopt` has no path without a terminal. `README.md:29` and `:166` link to a root `core/` that does not exist; `README.md:216` says 0.13.0 against 0.16.0 everywhere else; `INSTALL.md` never mentions `surfaceplate install` or `check` while asserting their dependency footprint, and `:128` hands the reader to `prompts/copilot-implementation-assistant.prompt.md`, which the payload does not carry; `INSTALL.md:57`'s `python -m pip` fails on a system Python without pip; `SETUP_GUIDE.md` calls itself "the exact adoption sequence", is linked from nowhere, is not installed, and puts the profile at `config/governance/` where the checker never looks. `S3`'s class, one release after `ACT-040`.

**Closed by `ACT-045`, items 2.2, 2.3 and 2.5 (2026-09-02), implementing `DR-49`.** The README
now shows `--version`, `doctor`, `install`, `check` and `adopt`, the version line reads 0.16.0,
the two `core/` links point at `surfaceplate/core/`, the extras form is `surfaceplate[adopt] @
git+…`, and a sentence says what a global `core.hooksPath` does and what to run. `INSTALL.md`
leads with the console script, drops the pointer to the uninstalled prompt file, and names the
exit codes and formats. `surfaceplate --help` and `--version` exist; `adopt --propose` is the
path without a terminal, named by the TTY refusal; `doctor` reports the five facts.
`tests/check_code_registers.py` now resolves every link and path-like span in both documents
(against this repository, or the installer's payload for an installed checkout), pins the
README's version to `surfaceplate/VERSION`, and checks the stated gate count; it failed on the
two dead links, the version and the prompt pointer before the pass. `scripts/front_door.sh`
runs every documented command with a global hooks path set, from `.github/workflows/front-door.yml`
in a clean container and by hand; run locally in `python:3.12-slim`: `FRONT_DOOR=PASS`.

## F69 — The route screen says the rest is four gates while the next screen says all nineteen

**Severity: low. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-044`; see `org/REMEDIATION_PLAN.md`.

`plan.route_plan` (`plan.py:162-199`) writes "At standard the rest of this profile is 4 gate(s) and 4 control(s)" from the level's mandatory count; two screens later the gates intro reads "All 19 gates must be decided one way or the other at standard" (`std-def-14`, `-35`). Closed by `DR-47`'s flow, which has no route screen.

**Closed by `ACT-044`, item 1.1 (2026-09-02).** `plan.route_plan` and the route section are gone;
the flow is decisions, level, the gate list, whatever the proposal could not fill, and the review
(`flow.STAGES`), asserted on the real `AdoptApp` in
`tests/test_adopt_tui.py::test_the_flow_is_decisions_level_gates_review`.

## F68 — Quitting at the resume prompt deletes the draft, and the prompt's heading is swallowed as markup

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-043`; see `org/REMEDIATION_PLAN.md`.

`ConfirmResumeApp.run()` returns `None` on `Ctrl+Q` or a closed terminal; `TextualInterview.confirm_resume` returns `bool(None)`; `_resume_or_start` treats `False` as "start fresh" and calls `_clear_draft` (`surfaceplate/adopt/wizard.py:244-246`). Verified against the real function: the draft existed before and not after. The screen's own heading `Static("[A saved draft was found]")` lacks `markup=False` and renders as an empty string in Textual 8.2.8 (image `resume-open-80x24`; the spike confirmed the other headers survive only because their step prefix defeats the parser) — `F37 #1` on a screen it did not reach.

**First half closed by `ACT-043`, item 0.6 (2026-09-02).** `TextualInterview.confirm_resume`
returns what `ConfirmResumeApp.run()` returns - `True` on `y`, `False` on `n`, `None` when the
app ended without either - and `_resume_or_start` raises `Cancelled` on `None`, deleting the
draft only on an explicit `False`. The `Interview` protocol's annotation and docstring in
`interview.py` say so; that is the one edit outside the phase's owning files.
`tests/test_adopt.py::test_quitting_at_the_resume_prompt_keeps_the_draft` drives all three
answers: seen to fail before (`ADOPT_CONFORMANCE=FAIL (3 failed, 93 passed)`: the quit ran on
and the draft was gone) and to pass after (`ADOPT_CONFORMANCE=PASS (96 checks)`). The real prompt
driven under `run_test` with `y`, `n` and `ctrl+q` returned `True`, `False`, `None`; the draft
existed before and after `y` and `ctrl+q`, and before but not after `n`.

**Second half closed by `ACT-043`, item 0.7 (2026-09-02).** The resume heading and the three
step-prefixed section headers (`FormScreen`, `LevelScreen`, `GatesScreen`) are `markup=False`.
`tests/test_render.py::test_a_bracketed_heading_is_rendered_not_parsed` hosts each at 80×24 with
no step prefix and asserts the first content line is the bracketed heading: seen to fail before
(`RENDER=FAIL (3 failed, 22 passed)` - the resume, level and gates headings absent; the mode title
survived only because its question mark defeats the parser) and to pass after (`RENDER=PASS (25
checks)`). Image at 80×24: before, the prompt opens on "It has answers for"; after, on
"[A saved draft was found]". Observed and left alone, being outside the plan's item: the
`ReviewScreen`, `ScaffoldScreen` and `DefaultsScreen` headings are bracketed without
`markup=False` too, and survive today only by their wording.

## F67 — The 80×24 pass looked at the wrong screens: the level options below the fold, help text unstyled and flush, off-state controls near-invisible, labels and text areas clipped

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-043`, `ACT-044`; see `org/REMEDIATION_PLAN.md`.

At 80×24 (the size `F41`, `F46` and `F56` appeared at, and `run_test`'s own default, which no suite uses): the level screen's recap and recommendation fill the frame and the three options sit below the fold, so the recommended option is not on screen and `?` appears to do nothing (`std-def-11`, `-12`); `.field-help` has no stylesheet rule, so help renders full-white, brighter than its label, flush against the next field, and a rationale's help runs off the frame (`std-def-03`, `-21`, same at 120×40); unticked boxes and unselected radios are dark brackets on a black ground, and an unpressed first radio is highlighted as if chosen (`std-def-01`, `-07`); mode and `above_floor` options end in "…", data classification shows two of four options, text areas show one line of a value, and the review shows nine lines of a 130-line profile per page. The maintainer's complaints 2 and 3 are these.

**Help-text part closed by `ACT-043`, item 0.8 (2026-09-02); the rest stays open for `ACT-044`.**
`app.tcss` gains `.field-help { color: #7a827e; margin: 0 0 1 2; }`.
`tests/test_render.py::test_help_text_is_muted_and_kept_off_the_next_field` hosts the identity
screen at 80×24 and 120×40 and reads the colour of every segment on the help rows: seen to fail
before (`RENDER=FAIL (4 failed, 27 passed)`: the help in `#dce0dd`, the screen's full ink, and
`display_name` on the very next row) and to pass after (`RENDER=PASS (31 checks)`). Images at both
sizes: before, the help full-white from the frame's edge with the next label touching it; after,
muted, indented under its field, one clear row before the next. The level options below the fold,
the off-state contrast of unticked boxes and unpressed radios (visible again in `F59`'s after
image, where the focused but unpressed first option is highlighted), and the clipping remain.

**The remainder closed by `ACT-049`, 2026-09-02, each item with a test in `tests/test_render.py` seen to fail first.** The level options: the recap is one row, the rule row is gone and the recommendation is two rows, so all three options and the caret are on the 24 rows with the recommendation above them (`::test_the_level_options_are_all_on_screen_at_80x24`). Off-state and focus: the toggle's `_button` paints its brackets in the muted ink rather than the button's background colour, and focus on a radio - the button's own, the set's cursor button, focused or blurred - is the accent colour on the label rather than Textual's filled block, so the glyph alone says chosen (`::test_off_state_and_focus_are_told_apart_from_chosen`). The four classification rows were already on screen since `F59`'s chip-row rule and are now asserted; a text area shows three rows of its value (`::test_every_classification_option_is_on_screen_and_a_text_area_shows_three_lines`). The above-floor rows carry the control id and a short cue that fits sixty columns (`explanations.CUES`, one per level control, asserted complete), and the full explanation of the highlighted row appears beside the list (`::test_an_above_floor_row_explains_itself_when_highlighted`). The review's page depth was closed by `ACT-044`'s review frame. Goldens regenerated for cause: the level screen, the decisions form, the remainder form, the gate list.

## F66 — The wizard accepts dates and paths the checker rejects, so a profile can pass the wizard and fail its first check

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-044`; see `org/REMEDIATION_PLAN.md`.

`validators.check` accepts `effective_from` tomorrow and a year out (`SP033` rejects a future date), `review_by` 401 days out and yesterday (`SP026`, `SP024`), a one-character `application_id` and basic-ISO dates the schema refuses, and typed paths for the scanner workflow and lock file without checking they exist or are tracked (`SP046`, `SP051`). A 401-day review date went through the adoption screen and the review; `surfaceplate check` on the result: `[SP026] The profile review date is beyond the permitted horizon`, `FAIL`. Remedy per `DR-48`: one rules module for both.

**Closed by `ACT-044`, item 1.6 (2026-09-02), implementing `DR-48`.** `surfaceplate/rules.py`
holds the `effective_from`, `review_by` and `revisit_by` rules, the `application_id` and
placeholder patterns, and "a named path is tracked by git"; `check_conformance.py` imports it as a
sibling (so the vendored copy works from `.standards/`) and `adopt/validators.py` imports it as
`surfaceplate.rules`. The module is install payload (`install_standard.build_payload`, classed
enforcing), the vendored copy is held current by `check_vendored_current.py` (65 files compared),
and this repository was reinstalled from the built release with the digest re-pinned.
Validators gained `review_by`, `revisit_by`, `tracked_path` and `ci_step`; `date` refuses basic
ISO; every string validator refuses a placeholder (`F65`'s field half); the plan names them on the
fields the checker reads. `tests/test_adopt.py::test_validators_refuse_what_the_checker_rejects`
refuses the twelve inputs the review listed and accepts their good forms;
`::test_every_checker_code_has_a_validator_or_an_exemption` maps all 55 emitted `SP` codes -
13 met by a validator, 42 exempt by a named reason (`SP034`, `SP035` history-only among them) -
and fails if the checker gains a code without a row. Seen to fail before (the suite could not
call `check(..., repo=)`) and to pass after (`ADOPT_CONFORMANCE=PASS (131 checks)`).

## F65 — A placeholder is accepted at the field and refused at the review, where nothing but cancel works, and a resumed draft lands on the same refusal

**Severity: medium. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-044`; see `org/REMEDIATION_PLAN.md`.

`TBD` typed into a rationale passes the controls screen (`validators.check("nonempty", "TBD")` is `None`). The review then shows the placeholder refusal, an empty profile pane and a hint still reading "[Ctrl+S] write it"; `Ctrl+S`, `Tab`, `Escape`, `Backspace` do nothing; `Ctrl+Q` cancels and keeps the draft. On the next run, resuming skips every completed section (`tui/app.py:203-204`) and lands on the same review with the same error (`shots-bad2/deadlock-01`). The exits are discarding the whole draft or hand-editing the JSON. Remedy: refuse the placeholder where it is typed, and give the review a way to the offending line.

**Closed by `ACT-044`, items 1.6 and 1.8 (2026-09-02).** `validators.check` refuses a template
placeholder for every string validator, so `TBD` stops at the field; `flow.Flow.review` validates
every answered field before rendering and names the first refusal with its profile path; the
review screen shows the error, `Ctrl+E` moves the highlight to that line, Enter opens it for
editing, and "write it" is not in the legend while an error stands.
`tests/test_adopt_tui.py::test_a_placeholder_is_refused_at_the_field_and_the_review_names_the_line`
drives both halves. A resumed draft lands on the same review, now with a way out.

## F64 — `validators.check` passes any non-string, so an unpressed radio set and a blank dropdown commit; one path ends in a black screen, the other in an unactionable `KeyError`

**Severity: high. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-043`; see `org/REMEDIATION_PLAN.md`.

`validators.check` returns `None` for any non-`str` (`surfaceplate/adopt/validators.py:111-113`). `_read_widget` returns `None` for an unpressed `RadioSet` and for an untouched `Select`. So `Ctrl+S` on the first screen with nothing chosen advances with `mode: None`, and three screens later `plan.py:998` looks up `LEVEL_CHOICE[None]` inside the `@work` worker: the terminal goes black with no message (image `nochoice-11`). On the gates screen the artefact dropdown left blank counts as answered ("1 of 1 answered"), commits, and the review shows `This cannot be written yet: 'artefact'` with no way back. Same hole for `scanner.wired_in` and every `implementation_reference`. The module's docstring says "an empty string is never a decision"; `None` is.

**Closed by `ACT-043`, item 0.3 (2026-09-02).** `validators.check` now treats `None` as `""`
before applying a named validator, so a blank dropdown fails `nonempty` where it is made and
`GatesScreen._gate_is_complete` no longer counts it; and `FormScreen.action_commit` refuses a
`choice` field whose answer is not one of its choices ("Choose one of the options."). Booleans
and lists still pass, as before. `tests/test_adopt_tui.py::test_an_empty_choice_is_refused_at_the_field`
and `::test_a_blank_dropdown_is_refused_at_the_field` drive both paths: seen to fail before
(`ADOPT_TUI=FAIL (5 failed, 44 passed)`, the mode screen committing `{'mode': None}` and the
gate committing without its artefact) and to pass after (`ADOPT_TUI=PASS (49 checks)`). The
review's sequence re-driven on the real `AdoptApp`: `Ctrl+S` on the mode screen with nothing
chosen now stays on that screen with the refusal in the hint line, where before it advanced to
Identity. Taken out of the plan's order, before item 0.2, because 0.2's test of the gates hint
could not pass while a blank dropdown still counted as answered.

## F63 — A real profile whose prose mentions "replace-me" is mistaken for the template and overwritten without a prompt

**Severity: critical. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-043`; see `org/REMEDIATION_PLAN.md`.

`wizard._refuse_if_already_adopted` (`surfaceplate/adopt/wizard.py:119-128`) tests `"replace-me" in text` over the whole file. A completed profile whose `risk_profile` reads "Never type replace-me into a rationale." makes the guard return, and `wizard.run` reaches `target.write_text(rendered, …)` at `:323` and destroys the adopter's profile with no prompt. Probed in the review session against a throwaway directory: the guard returned. Unrecoverable data loss; the only finding in the review that destroys work rather than blocking it. Remedy: check the required scalars for the token, not the byte stream.

**Closed by `ACT-043`, item 0.4 (2026-09-02).** `wizard._refuse_if_already_adopted` parses the
file and treats it as the template only when one of five identifying scalars - `application_id`,
`owner`, `adoption.framework_version`, `adoption.framework_digest`, `adoption.adoption_date`, the
ones the shipped template leaves as `replace-me` - is still literally that token; anything else,
including a file that does not parse as a mapping, is refused and left alone. Prose fields are
not consulted. `tests/test_adopt.py::test_a_real_profile_that_mentions_the_token_is_not_the_template`
writes the shipped essential example with `risk_profile: Never type replace-me into a rationale.`
into a scratch installed repository and asserts `wizard.run` raises `AlreadyAdopted` and the
file is byte-identical; `::test_the_untouched_template_is_still_fair_game` asserts the installer's
own template is not refused. Seen to fail before (`ADOPT_CONFORMANCE=FAIL (1 failed, 91 passed)`:
the run got past the guard) and to pass after (`ADOPT_CONFORMANCE=PASS (92 checks)`).

## F62 — The profile header asserts every value was typed by a human above canned rationales, computed dates and derived text

**Severity: high. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-044`; see `org/REMEDIATION_PLAN.md`.

`surfaceplate/adopt/render.py:205-206` writes *"Every value below was typed by a human answering a question; nothing here was inferred, defaulted silently, or chosen by the wizard"* on every profile. On the defaults route the profile beneath it carries five rationales that are the framework's worked examples verbatim ("The API is consumed by a separate frontend and would break silently." — Plutos has no separate frontend), a computed `review_by`, a pre-filled `effective_from`, `framework_maintainer` copied from `owner`, and every gate's descriptions and enforcement derived. The maintainer's real first attempt carries the same header above seven gates whose artefacts, paths and descriptions read `asdf`. The `DefaultsScreen` knows each value's origin and the profile throws it away. Remedy per `DR-47`: a true header and a provenance record beside the profile.

**Closed by `ACT-044`, items 1.1 and 1.2 (2026-09-02), implementing `DR-47`.** `render.render_profile`
writes a header that states what the provenance record contains and no more; the sentence quoted
above is withdrawn. `surfaceplate/adopt/provenance.py` traces every leaf of the assembled profile
to an origin by a rule table from profile path to answer, and `wizard.run` writes
`governance/application-profile.provenance.yaml` beside the profile: origin per field, the
framework version, one document-level approval with its timestamp, and any bulk gate decision as
one human act with its count. `flow.Flow` records the origin of every answer as it is given - a
value submitted unchanged keeps its proposal's origin, a review edit is typed with a timestamp -
and `tests/test_provenance.py` drives the flow at essential, standard and full and asserts every
leaf has an origin, nothing is typed that the human did not type, a typed value reappears under
another origin only as a recorded copy, and the approval carries a timestamp; two negative
controls show the walk objecting to a promoted proposal and to an unreached profile path.
`tests/test_adopt.py::test_proposing_writes_the_same_profile_as_typing_the_same_values`
reproduces the prototype's equality on the real code.

## F61 — Discovery proposes the framework's own installed files and CI step as the adopter's preconditions, and the checker passes them

**Severity: high. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-044`; see `org/REMEDIATION_PLAN.md`.

`defaults.propose` on the Plutos copy proposes `gates.authority_map.artefact = '.github/instructions/authority.instructions.md'` and `gates.change_record_before_completion.artefact = '.github/skills/change/SKILL.md'` as "the closest match in this repository", and `controls.contract_tests.implementation_reference = 'Check conformance to Surfaceplate'`, the installed workflow's own step; the register-directory candidates include `.standards/examples`, `.standards/schemas`, `.standards/templates`. On a bare repository with one file and a fresh install, the level screen says "You appear to have: a CI workflow (.github/workflows/standards-conformance.yml)". `SP032` and `SP053` then pass, which is `F40`'s shape with the framework's own footprint as the false green. `discover.py:97-100` says framework-owned paths are offered "never ahead of the adopter's own documents"; `matched_for_gate` (`:185-203`) sorts by keyword score and ignores that ranking — `F55`'s class. The maintainer's own draft of 2026-09-02 carries the CI-step value. Note: on a fresh install the installer's output is untracked and invisible to `git ls-files`, so this bites once the install is committed.

**Closed by `ACT-044`, items 1.4 and 1.5 (2026-09-02).** On the wizard's side,
`discover.framework_paths` reads the install record's file list, the profile path and the
installed workflow's step names, and every candidate list, every proposal and the level screen's
"you appear to have" exclude them; `validators.tracked_path` refuses a framework-installed path
typed by hand. `tests/test_discover.py::test_discovery_cannot_find_the_framework_in_the_mirror`
installs the payload into an otherwise empty repository, commits it, and asserts no candidate, no
discovered proposal and no CI-workflow signal. On the checker's side, new `SP059` reports a
required gate whose artefact is in the install record and a control whose CI step belongs to the
installed workflow, whether or not a provenance record exists, so every existing profile is
covered; `tests/test_install_and_check.py` drives both directions and the negative.
`org/FINDINGS.md`'s declared code space now ends at `SP059` and `check_code_registers.py` agrees
(56 codes). All seen to fail before and pass after.

## F60 — The defaults route discards its gate proposals: `GatesScreen` is built without `initial`, and the "N more" count excludes what it will re-ask

**Severity: high. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-043`; see `org/REMEDIATION_PLAN.md`.

The proposals screen says "59 values proposed … 5 more can only be answered by you" and lists artefact, paths and effective date for every required gate; the gates screen that follows opens blank and refuses `Ctrl+S` with "Gated paths: This cannot be blank" (images `std-def-15`, `-35`, `-36`). `tui/app.py:228-231` passes `initial=` only to `FormScreen`; `GatesScreen(specs, section, step=step)` at `:227` takes none and `screens.py:712` has no parameter for one. `defaults.unanswered` counts fields with no proposal, so "5 more" is 5 at every level while the gates section re-asks 38 fields at standard and 53 at full with a UI. No test asserts that any screen is seeded.

**Closed by `ACT-043`, item 0.2 (2026-09-02).** `GatesScreen.__init__` gains `initial`, keyed
`"<gate>.<field>"`; `_compose_gate_fields` builds each widget from it and pre-presses the seeded
status; `tui/app.py` passes `initial=self._seeded.get("gates", {})` as it already did for every
`FormScreen`. `defaults.unanswered` is unchanged: once the gates screen is seeded, its figure is
the number of fields the remaining screens present unfilled, which is what the test asserts.
`tests/test_adopt_tui.py::test_the_defaults_route_seeds_the_gates_screen_and_counts_what_is_left`
drives the real `AdoptApp` from the route screen through the proposals to the gates screen at
essential, standard and full on a fixture repository holding `activity/register.md` and
`src/main.py`, and asserts the first proposed artefact is what the dropdown holds, the gates
hint counts the seeded gates, and "N more" equals the unfilled fields measured on the screens the
app builds. Seen to fail with the seeding line alone reverted (`ADOPT_TUI=FAIL (6 failed, 55
passed)`: the dropdown held `Select.NULL`; "6 more" against 8 unfilled, "11" against 27, "22"
against 38) and to pass with it (`ADOPT_TUI=PASS (61 checks)`: 6 = 6, 11 = 11, 22 = 22; the
gates hint 1 of 1, 16 of 19, 9 of 19). The review's "5 more" was measured on Plutos, where more
gates matched; on this fixture the figure was never 5, and the defect was the seeding, not the
arithmetic.

## F59 — Every undecided gate's status radio is invisible at every terminal size: `.chip-row { height: 1 }` leaves no row for Textual's bordered `RadioSet`

**Severity: high. Closed.**

Recorded under `ACT-042` from `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, the adversarial product review of 2026-09-02, authorised by the maintainer in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs). Closes by `ACT-043`; see `org/REMEDIATION_PLAN.md`.

Driving standard/defaults on a copy of Plutos at 80×24, 100×30 and 120×40, the status row of every non-mandatory gate rendered as an empty blue-bordered box; choosing a status with the keyboard worked, but nothing showed the options or the choice (images `std-def-38-*` in the review's scratchpad, read). `surfaceplate/adopt/tui/app.tcss:185-188` forces `.chip-row { height: 1 }`; Textual 8.2.8's `RadioSet` default stylesheet draws a two-row `tall` border plus padding, so a one-row widget has no row left for its buttons. `tests/test_adopt_tui.py:188-201` sets `.value` on the buttons and reads it back; nothing renders the row — `F37`'s class again. The maintainer's first-attempt profile predates the radio rewrite (`96a2efe`) by 24 minutes and today's draft stops before the gates section; he has not got past that screen since. The spike proved `.chip-row { height: auto; border: none; padding: 0 }` renders the three radios in three rows.

**Closed by `ACT-043`, item 0.1 (2026-09-02).** `surfaceplate/adopt/tui/app.tcss` now carries
`.chip-row { height: auto; border: none; padding: 0; margin: 0 }`, and the dead `.chip` and
`.chip-selected` rules are gone. `tests/test_render.py::test_a_gate_status_radio_set_renders_its_options`
hosts a standard `GatesScreen` at 80×24, focuses the first undecided gate's status and asserts
`( ) required`, `( ) deferred` and `( ) not applicable` are in the rendered text. Seen to fail
before the change (`RENDER=FAIL (1 failed, 20 passed)`, all three options missing) and to pass
after (`RENDER=PASS (21 checks)`). The image re-taken at 80×24 shows the three options in three
rows under `work_contract`, matching the spike's `height_auto_compact.png`.

## F58 — `F29` again, in the half `DR-30` did not finish

**Severity: high. Closed.**

Found while researching `H7` (forge neutrality) — counting which installed files assume GitHub, not
looking for this.

`AGENTS.md` is installed into every adopting repository and tells every agent, in its binding-rules
block:

> `.github/skills/` defines the workflow for each kind of task. Use the matching skill. Its required
> inputs, gates and mandatory stops are not optional.

The payload wrote those seven skills to `.github/skills/` **only**. Claude Code loads
`.claude/skills/`, which did not exist in the payload, in this repository, or in any adopter:

```
$ ls .claude/
rules  scheduled_tasks.lock
```

So an adopter running Claude Code was told a set of gates was mandatory and handed them in a
directory their agent does not read. **No Claude Code session in this repository has ever loaded a
SKILL** — including every packet from `ACT-032` onward, all of which were performed by an agent
working from instructions it had, under a workflow it did not.

**This is `F29` exactly, one layer along.** `F29` recorded 501 lines of agent instruction sitting in
a location Claude Code does not load. `DR-30`'s remedy was *one body, several emitters* — and it was
applied to the six **instruction** documents and stopped there. The seven **skills** were left with
a single emitter, and nothing noticed, because every test asked whether the skills installed
correctly rather than whether the agent reading `AGENTS.md` could find them.

**Remedy** (`ACT-041`): `build_payload` emits each `SKILL.md` to both paths. No transformation is
needed, unlike the instructions — a `SKILL.md` already carries the `name` and `description` front
matter both agents want, so the body stays one file with two destinations. The conformance block's
prose is corrected in the same change: it named one directory and now names the pattern, matching
how it already describes the instructions.

**Seen to fail, and calibrated on a *partial* break.** With the fix reverted the assertions reported
*"0 under `.claude/skills/` against 7 under `.github/skills/`"*; with one skill deliberately withheld
they named it — *"claude=[... missing `release`]"*. A total break would have passed any check that
merely asked whether the directory existed, which is the weakness `tests/check_audit_packet.py`
already records about globs that tolerate a missing member.

**The transferable part: a remedy applied to one instance of a class is not applied to the class.**
`DR-30` fixed the emitter problem for the artefact that had failed and did not ask what else shipped
on the same assumption. The check that would have caught it is not "did the skills install" but
**"can the agent this document addresses reach every file this document calls mandatory"** — a
question asked from the reader's chair, which is the same move that produced `F53`.

**The remaining half of `H7` is untouched.** The conformance workflow is still the one genuinely
forge-specific installed file, and that is a scope decision, not a defect.

---

## F57 — The first command an adopter runs cannot work

**Severity: high. Closed.**

Found during a bounded README pass, by checking a claim rather than reading it.

`README.md`, `INSTALL.md` and **`cli.py` itself** tell an adopter to run
`pip install surfaceplate[adopt]`. The package is not published:

```
https://pypi.org/pypi/surfaceplate/json  ->  HTTP 404
```

So the instruction fails for every reader, and the third instance is the worst: `cli.py` prints it
as the **remedy** when `adopt` is run without the optional dependency. A tool that answers a missing
dependency with a command that 404s has replaced one dead end with another — and that path is
`F35`'s remedy, which exists precisely so a refusal names a route the reader can take.

**A second false claim on the same page.** `README.md` still advertised the wizard as *"It never
picks a level, invents a rationale, or sets a date for you"* — the wording `F51` proved false and
`DR-46` formally amended one day earlier. The correction had been made in `org/RELEASE_PLAN.md` and
not on the public front door, so the repository was publishing a claim its own findings register had
already retracted.

**Remedy** (`ACT-040`): every live instruction now names
`pip install git+https://github.com/pipoventures/surfaceplate@main`, **which was run into a clean
virtualenv before being written down** — it installs, the console script works, and the payload
arrives complete (`MANIFEST.sha256` present, four seeds). The rule claim is replaced with what
`DR-46` actually says. Historical mentions in decision records and `CHANGELOG.md` are left alone:
they are accurate records of what was decided when.

**Publishing to PyPI is not done here.** It is a release decision with credentials attached, and an
agent may not take it — recorded in `org/HUMAN_ACTIONS.md`. When it happens, the instruction becomes
`pip install surfaceplate` and this finding is the reason the interim form exists.

**The transferable part: a document's instructions are executable claims, and nobody had executed
them.** `F50` was the same shape one layer out — a hand-off command naming a deleted file. Both
survived because a document is read for sense rather than run, and both were found the moment
somebody ran it. Every check in this repository verifies what the code does; nothing verified what
the documentation tells a stranger to do.

---

## F56 — Twenty-eight field labels were cut, and none of them said so

**Severity: medium. Closed.**

Found by re-rendering every screen at 80x24 after nine packets landed in one day — the discipline
that has produced `F41`, `F46` and the scaffold screen's missing header, every one of them after the
suites were green.

`.field-label` carried `height: 1` with `text-overflow: ellipsis`, and **the ellipsis never
rendered** — the same fact `F42` established for `.gate-desc` and which had not been generalised.
Twenty-eight labels were silently shortened at the design width:

```
Why does documentation_authority apply here?   ->   Why does documentation_a
Precondition artefact                          ->   Precondition
Adoption decision record ID                    ->   Adoption decision
```

Every control's rationale prompt is in that list. An adopter at `standard` was asked to justify a
control by a question they could not finish reading.

**Ownership is split and worth being exact about.** Most predate `ACT-035`: at the previous fixed
`width: 32`, anything longer was already cut, and that has been true since the wizard's first
Textual build. `ACT-035` made the column proportional so the route screen's two options became
readable — a real fix for a real defect — and in doing so widened the blast radius to shorter labels
like `Precondition artefact`. **A fix that improves one thing and quietly degrades a neighbour is
not visible in the suite that verified the fix**, which is the argument for a whole-interface render
pass after a run of packets rather than after each one.

**Remedy:** `height: auto`. `F42`'s remedy applied to labels: wrap rather than clip, in a frame that
already scrolls. Nothing is lost and no copy was edited.

**The assertion took three attempts, and the failures are the interesting part.** The first two
asked whether the label's text appeared in the composited screen, and **both failed against a
working fix** — a wrapped label in a two-column row has the frame's border between its halves, and
then the VALUE column's text interleaved between its rows, so no join over rendered lines can ever
reconstruct it. The property is not "does this string appear" but "is there room for all of it",
which is a question about the widget's own box: its height against the rows its text needs at its
width. Asked that way it passes, and fails with all sixteen offenders named when `height: 1` is
restored.

**Two things to carry forward.** `text-overflow: ellipsis` does not work in this interface — it has
now failed silently in two separate rules, and any future truncation must put its ellipsis in the
text, as `_first_sentence` does. And when an assertion fails against a fix you have watched work,
suspect the assertion: the third version here was not a better string match, it was a different
question.

---

## F55 — Narrative docstrings can drift from the code beneath them

**Severity: low. Accepted — `ACT-102`, 2026-09-11. Not remediable; nothing is pending.**

Raised by the review as an over-engineering finding: the Python files carry multi-paragraph essays
citing `DR-*`, `ACT-*` and `F*` codes, and the reviewer's argument is that they will drift.

**Recorded rather than remedied, and the reasons for both halves are worth stating.**

The argument has evidence. Two docstrings were found wrong about their own code on 2026-09-01:
`scaffold.write` described its `exists()` check as a guarantee when it was a check-then-write race,
and `check_vendored_current` described a comparison it was no longer making. Both were corrected in
the same session. **Twice in one day is not an abstract risk.**

The counter-argument is the register itself. Those comments have repeatedly carried the reasoning
that prevented a repeat — `F41`'s note is why `F46` was recognised as the same shape, and `F39`'s is
why the app-wiring test exists at all. Stripping them to decision records alone would move the
reasoning away from the code that has to honour it, and this project has already recorded what that
costs: `F29` is 501 lines of agent instruction that no agent read because they sat where nobody
looked.

**So the remedy is a habit, not a deletion: verify a docstring's claim when touching the code beneath
it, and treat a comment describing a guarantee as a claim to be checked rather than a fact.** That is
not mechanically enforceable, which is why it cannot close with a test.

**Moved from `Open` to `Accepted` on 2026-09-11 (`DR-86`), at the maintainer's prompting:** *"close
F55 if it can't be fixed."* He was right that `Open` was wrong — it implies work pending, and there
is none — and `Accepted` is the word for a decision taken about a condition that persists. The
limitation is unchanged: a docstring here can still be wrong about the code beneath it.

**What would reopen it:** a third docstring found wrong about its own code. Twice in one day was
evidence the risk is real and the habit is the answer; a third, after this record, would be
evidence the habit is not working and something mechanical is needed after all.

---

## F50 — The review packet for item 9 could not have been run as written

**Severity: medium. Closed.**

Found when the maintainer asked for the packet to be refreshed before running it — *"the packet is
from this morning, a lot has changed"* — which is the only reason anyone read it again.

`RELEASE_PLAN` item 9 hands an external reviewer two attachments: a curated prompt and an
`EVIDENCE_BUNDLE.md` built by a shell command in `audit/AUDIT_README.md`. That command listed
`surfaceplate/adopt/prompting.py`. **`DR-36` deleted that file three packets earlier**, when the
wizard's interaction layer was rebuilt on Textual.

So the command would have failed at `cat`, and — because it had no guard and redirected the whole
loop — produced a **truncated bundle** rather than an error anyone would notice. The prompt's own
section 2 was worse than stale: it asked the reviewer to trace the binding rule through
`prompting.py` and to assess a `ScriptedPrompt` mechanism that no longer exists. An external
reviewer would have reported an evidence gap against a file the maintainer believed they had sent.

**Nothing detected this**, and `audit/AUDIT_README.md` had even anticipated the failure mode in
prose: *"this command must match it; if the two drift, the prompt's text is authoritative and the
command is wrong."* Both had drifted, so the stated tie-breaker resolved to a file that did not
exist either.

**Remedy** (`ACT-037`): the packet is rebuilt against the framework as it is; the command is
corrected, given a `[ -f "$f" ] || exit 1` guard so a missing file is loud, and **run**, producing
exactly the 11 files the prompt declares.

**The transferable part: a hand-off is a derived artefact, and this one had no reader.** `DR-6` and
`F12` are both about generated content drifting from its source, and this repository applies that
lesson thoroughly to its manifest, its vendored copy and its identifiers — each with a `--check`
mode that runs in CI. The audit packet is the same shape: content derived from a file list that
lives somewhere else. It had no check, and more tellingly **no reader** — a document nobody opens
between the day it is written and the day it is used cannot drift *visibly*, only silently. The
prompt is prose and cannot be mechanically verified against the repository the way a manifest can;
what closed the gap here was a person asking whether it was still true.

---

## F49 — The standing policy that decided publication has no automated guard

**Severity: low. Closed.**

Recorded when `ACT-007` was closed, so that an activity marked `done` does not imply coverage that
does not exist.

`DR-23` establishes a **standing, unconditional policy**: no reference to the former organisation on
any brand-facing or public-adjacent surface, no exception process, and public git history counts as
such a surface. Nothing checks it.

**It cannot be checked the obvious way, and that is by design rather than by omission.** A test would
have to carry the token, and `DR-23` deliberately does not write it down - *"writing it out here
would put it back on the public surface the whole decision exists to keep clear"*. A check that
committed the token would defeat the policy it enforced.

**What IS covered, and it is the part that mattered.** `tests/check_identifiers.py` Rules 1-3 assert
that every URN authority and GitHub organisation in the tree equals the declared one, and reject an
undeclared token sharing the organisation's stem. `DR-23` says the token was embedded as a URN
authority *"in every schema `$id`"*, so the dominant form is guarded. The public repository's history
carries none of it by construction: its first commit is the clean tree.

**What is not covered** is a bare prose mention sharing no stem and appearing in neither form. That
is the residue `ACT-007` was closed over.

**Remedy sketch, not built.** A check could read the token from an untracked local file or an
environment variable and skip cleanly when absent - full strength for the maintainer, silent for
everyone else, and nothing committed. That is a real design and it has a real cost: a check that
usually skips is a check whose green means almost nothing, and this register already carries `F3`
about exactly that shape. Deciding between them is a judgement, not an omission, and it is recorded
here rather than taken quietly.

**One thing worth carrying forward.** Two attempts to verify the residue mechanically were made and
both produced false alarms - one from a regex matching inside the word `return:`, one from
recovering a redaction marker out of the archive and reporting fifteen ordinary English words as
hits. Neither found anything; both looked as though they had. **A policy whose subject cannot be
named resists tooling**, and the failure mode is a confident false positive rather than a silent
miss.

**Closed by `H5`, 2026-09-02.** The maintainer ran `git grep -Iil -- '<the name>' | wc -l` in his own
terminal against the working tree at `main`, with the former organisation's name in place, and
reported **0**. A first attempt had searched the literal placeholder and returned the one file that
quotes the command; the second, with the name, returned nothing. The look was capable of finding
the thing: `git grep -I -i -l` reads every tracked text file, case-insensitively, and the same
command finds the placeholder when the placeholder is what is searched for. Scope: the tracked tree
at `main`, not history - the public repository has no prior history by `DR-23`'s construction. No
instrument was built, per the register's own warning. Reported in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z).

---

## F48 — The gate history audit answered differently depending on the time of day

**Severity: high. Closed.**

Found while calibrating `F47`'s fix, and it inverted the premise `F47` was written on. `F47` assumed
a date-only `effective_from` meant midnight. It never did.

`commits_touching` passes `--since={date}` to `git log`, and git parses that with **approxidate**,
which fills a missing time from the **current clock**. So `effective_from: 2026-09-01` did not mean
*"from that date"*, as the schema has always said. It meant *"from that date, at whatever time you
happen to run the check"*.

Measured on git 2.43.0, four commits on one day at 01:00, 10:00, 19:00 and 23:00, checked at 22:3x:

```
--since=2026-09-01           -> 1 commit
--since=2026-09-01T00:00:00  -> 4 commits
--since=2026-09-01T20:00:00  -> 1 commit     # identical to the bare date
```

**What that means for a published control.** The audit window slid forward all day. A violation
visible at 09:00 was gone by 23:00, for no reason but the hour, and the later the check ran the less
history it examined. Two people checking the same repository on the same day got different answers,
and neither had reason to suspect it. Against this repository's own adoption-day fixture the bare
form saw **0 of 4** same-day commits.

This is `SP035` being **silently permissive**, which is the worst direction for a gate to fail in:
nothing reports, nothing looks wrong, and the control appears to be working.

**Remedy** (`ACT-035`): `parse_effective_from` resolves a date-only value to an explicit
`T00:00:00`. The window becomes deterministic and acquires the meaning the schema always claimed.
It **widens** the window, which is the safe direction — it can surface a violation that was being
hidden and cannot hide one that was being surfaced.

**Two things worth carrying forward.**

**It also explains a flake that had already been seen and written off.** `ACT-033`'s end-to-end test
failed about one run in five; I attributed that to a fragile stdout capture, replaced the assertion,
watched it pass eight times, and moved on. The capture was fragile. It was also sitting on top of
this: the run's result genuinely depended on the minute it started. **A flake explained is not a
flake diagnosed**, and stability under repetition is not evidence that the cause was found.

**The defect is in a borrowed vocabulary, not in this code's logic.** `--since` is a git interface
whose date parsing is deliberately loose, and every line of the surrounding code was correct about
its own intent. Nothing in a review of this repository's logic would have found it; it needed the
question *"what does the tool we are calling actually do with this string?"* asked out loud, and
answered with a controlled experiment rather than a reading of the documentation.

---

## F47 — A freshly adopted repository violates its own gate on the first check

**Severity: medium. Closed by `ACT-035`.** Its stated cause was also **wrong**, and `F48` records
what was actually happening: a date-only `effective_from` never meant midnight, so the window this
finding describes was not the window the checker was using. The remedy below is still the right one
— a gate adopted midway through a day must be able to say so — but it was chosen against a
mis-stated mechanism, and `F48` is the correction.

Found by writing `ACT-033`'s end-to-end test - the one asserting that a repository with a README and
one Python file can adopt and then pass. **It cannot**, and the finding is what stopped that
assertion from being written as though it could.

The wizard now creates `activity/register.md` where a repository has none. `effective_from` for the
gate is today. The history audit then asks, of every commit since that date touching a gated path,
whether the artefact existed - and any commit made **earlier the same day**, including the ones the
adopter pushed before running `adopt`, was made when it did not:

```
[SP035] Gate 'work_registration' was crossed without its precondition
        1 commit(s) since 2026-09-01 changed a gated path while a required
        artefact was absent: 3e161a9 2026-09-01 bare (missing activity/register.md)
```

**The obvious remedy is closed off by the standard itself.** Binding the gate from *tomorrow* is
what the artefact's real history would justify - it demonstrably did not exist during any of today -
and `SP033` rejects a gate dated in the future. That was tried during `ACT-033` and the checker
refused it, correctly: a gate that binds later than now is not yet a gate.

So the two rules are jointly unsatisfiable for a repository with same-day activity:

- `effective_from` may not be in the future (`SP033`);
- `effective_from` binds by **date**, so same-day history before the artefact existed is in scope.

**Who this hits.** Every adopter whose repository saw a commit on the day they adopt, which is most
people, because running `adopt` is usually part of a working session rather than the first thing on
a quiet morning. It resolves itself the next day - the violation is bounded to commits from the
adoption date - so it is a poor first impression rather than a lasting defect.

**Remedied by `ACT-035`: `effective_from` carries a time, so a gate binds from the instant of
adoption.** Of the three candidates `DR-43` recorded — comparing commit *timestamps* rather than
dates, treating the commit that introduces an artefact as the boundary, or letting `effective_from`
carry a time — the third was chosen, in its own packet with its own decision.

> *Historical, superseded by the paragraph above and kept as the record of what was decided when.*
> As first recorded under `ACT-033`: **"Not remedied here, deliberately.** The candidates all touch
> a published control's semantics and none is obviously right… Choosing between them is a change to
> `SP033`/`SP035` and belongs in its own packet with its own decision, not as a side effect of
> adding scaffolding."

**`ACT-035`'s remedy reached one of the two sites that write the value**, and the other kept the
bare date until `ACT-106`. That is `F166`, which carries the reproduction, the inversion it caused,
and why no test here could see it.

**What `ACT-033` did instead:** its test asserts the true outcome - the artefact exists, the gate
names it, and the only outstanding finding is this one - rather than asserting a clean check and
being quietly satisfied by the adoption grace window, which returns success regardless.

---

## F46 — The conformance-level screen redrew itself forever

**Severity: high. Closed.**

Found by tracing `_update_meta` while chasing a wrong label, during the full-path audit the
maintainer asked for. The label was the symptom; this is the cause, and it is a regression
**`ACT-032` introduced and its own tests passed**.

`_move_caret` redrew the three level prompts so the caret sits on the highlighted row. It did that
with `clear_options()` followed by `add_options()`. `clear_options()` resets the highlight to 0 and
posts an `OptionHighlighted`, which arrives back in `_move_caret` and redraws again. While the caret
started at index 0 this settled immediately, because the reset landed on the value it already had.

`ACT-032` started the caret on the **recommended** level. From any non-zero index the two events
alternate and never converge:

```
_move_caret ran 4484 times for one paint: [0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2]
```

Every repository whose answers recommend `standard` or `full` met this. It does not crash — Textual
keeps servicing the queue — so it presents as a screen that renders, with a meta line describing
whichever level the oscillation last touched.

**Why `ACT-032`'s tests passed.** They asserted `OptionList.highlighted == 2` after a single
`pause()`, and it *is* 2 on half the iterations. Reading state cannot see a loop; only counting the
work can. The regression test counts `_move_caret` calls.

**The guard was there and could not work.** `_move_caret` already returned early when the incoming
index matched the last one. The events alternate, so the incoming value never matches. Two attempts
to fix this by adjusting *when* the meta was updated both failed before the loop was found — the
working method's loop-breaker applies exactly: a second failed patch means the approach is wrong,
not the implementation.

**Remedy** (`ACT-034`): `replace_option_prompt_at_index` mutates each prompt in place and leaves the
highlight alone, so no event is generated and there is nothing to feed back.

**The transferable part: a fix that suppresses a symptom downstream of a feedback loop cannot
work.** Guarding `_move_caret` harder, or making `_update_meta` deterministic, both treat the last
value written as the problem. The problem was that writing produced another write.

---

## F45 — The wizard misreported where you were in it

**Severity: low. Closed.**

`_STEPS` in `tui/app.py` was hand-written beside the `SECTION_ORDER` it describes, and had drifted:

- `route` had no entry, so that screen showed no step at all;
- `adoption` and `wrap` both read `7 of 7 — `, so an adopter answered "7 of 7" and was handed
  another "7 of 7";
- the total said seven while `SECTION_ORDER` holds ten sections.

A progress counter is read as a promise about how much is left. **Remedy:** derived from
`SECTION_ORDER`, so the two cannot disagree. `mode` stays unnumbered deliberately — it is asked
before the run proper and chooses how the run explains itself.

---

## F44 — A dropdown offered twelve files that matched nothing

**Severity: low. Closed.**

Raised by the maintainer mid-run: *"why 10 candidates in each dropdown list."*

`discover.rank_for_gate` returns matches first and then everything else, so the whole list is
offered and the adopter still chooses — `DR-38`'s rule. `F40` fixed `defaults.py` taking the top of
that ranking as a **proposal** when nothing had matched. The **offer** was left alone, so a gate
nothing matched still presented `Choose precondition artefact (12 found)` above twelve unrelated
files, which reads as *one of these is the answer*.

**Remedy:** the field's help states whether anything actually matched, and says to expect to create
the artefact when nothing did. Nothing is hidden.

---

## F43 — The gate screen counted unanswered gates as answered

**Severity: medium. Closed.**

At `essential` the hint line read `1 of 1 answered` while the precondition dropdown was empty and
`Gated paths` was blank. `_answered_count` counted a gate whenever `_status_of` returned anything,
and a level-mandatory gate's status is `required` from the moment it appears — fixed by the level,
supplied by nobody.

**The right predicate already existed.** `_gate_is_complete` — *"a gate is finished when it has a
status AND every field that status calls for validates"* — was written for collapse-when-complete
and its docstring says explicitly that "has a status" is too weak. One call site asked the weaker
question, and it was the one the adopter reads.

---

## F42 — Two thirds of every gate explanation was discarded silently

**Severity: medium. Closed.**

Reported by the maintainer as *"the explanations many times overlap the text in the next line"*.

`.gate-desc` carried `height: 1` with `text-overflow: ellipsis`. The explanations are **184 to 248
characters**; one line survived. **The ellipsis never rendered** — grepped across the output, zero
occurrences — so the sentence simply stopped, mid-word at some widths.

| Width | `work_registration` (184) | `work_contract` (248) |
|---|---|---|
| ~200 cols | cut after *"what \"done\" looks like."* | cut mid-sentence at *"and what"* |
| 80 cols, the design size | ~78 chars survive | ~78 chars survive |

`ACT-026` wrote dual-register explanations for all 31 catalogue items so an adopter would understand
what they are declaring; at the design width most of every one was thrown away without telling the
reader there had been more. It is `F37`'s remedy over-corrected — help was rendering everywhere at
once, so it was pinned to a single line.

**Remedy:** the cut happens in the **text**, in `_first_sentence`, with a 150-character budget and
its own `…`. A budget applied to a string cannot fail the way a CSS overflow rule did: whenever
anything is dropped the ellipsis is part of the value, so it survives whatever the layout does.

---

## F41 — Every multiselect drew a ticked box on every row, whatever was ticked

**Severity: medium. Closed.**

Found by rendering the controls screen while building `ACT-032` — not by a test, which is the point
of the entry.

`F38` recorded the maintainer's complaint that *"some boxes (x) are not clearly visible"* and
`ACT-031` fixed it with `_StatefulToggle`, a mixin that draws `[X]` for on and `[ ]` for off. It
fixed `Checkbox` and `RadioButton`. It never reached `SelectionList`, and **could not have**:
`SelectionList.render_line` composes its box from `ToggleButton.BUTTON_LEFT`, `BUTTON_INNER` and
`BUTTON_RIGHT` read off the **`ToggleButton` class**, while `_StatefulToggle` sets those names on
the **instance** of the widget it is mixed into. Two different objects; no error either way.

So every multiselect in the wizard rendered `▐X▌` on every row and signalled its real state by
colour alone. On the gate catalogue that meant `enforcement` showing five ticked-looking options
when two were selected — shipped, in the version the maintainer used.

```
before:  ▐X▌ history_audit   ▐X▌ local_hook   ▐X▌ review   ▐X▌ ci   ▐X▌ unenforced
after:   [X] history_audit   [ ] local_hook   [X] review   [ ] ci   [ ] unenforced
```

**Remedy** (`ACT-032`): `VisibleSelectionList` overrides `render_line`, taking the strip the base
class built and rewriting its three button segments from the row's real state while keeping their
styles, so colour still agrees with the glyph instead of replacing it.

**Two things worth carrying forward.**

**A fix is scoped to the widgets it was applied to, and nothing announces the ones it missed.**
`ACT-031` verified `_StatefulToggle` against a checkbox and a radio button, both of which it fixed.
The suite went green, the finding was closed, and a third widget with the identical defect was never
looked at. The property was right; its coverage was assumed.

**The test written for this finding passed against the unfixed widget, and was only caught because
it was deliberately re-broken.** It compared each row's whole prefix, and the field's label sits on
the first row and not the second — so the two prefixes differed for a reason that had nothing to do
with the box. Narrowed to the four characters of the button itself, it fails as it should. `DR-37`
required every new render property to be seen to fail; this is the first time that requirement
caught a defect in a test written to honour it, which is the strongest argument for keeping it.

---

## F40 — The wizard proposed a README as the precondition for registering work

**Severity: high. Closed.**

Found by walking four adopter personas through every route of the wizard, after the maintainer
challenged whether the package is itself easy enough to be worth adopting.

For a repository with nothing in place — a solo maintainer, one Python file, a README — the `Set
defaults` route proposed `README.md` as the precondition artefact for `work_registration`, the gate
meaning *no work begins until it is registered as an identified activity*.

```
gates.work_registration.artefact = 'README.md'
  (the closest match in this repository for this gate)
```

**Why this is worse than an excessive question.** A README satisfies every test `SP032` applies:
it exists, it is non-empty, it carries no placeholder token. So the gate would have **passed while
guarding nothing** — a green check over a practice that does not exist. The framework's whole
argument is that a gate means something; this shipped a gate that means nothing, and labelled it
`discovered`, which is the origin an adopter is most likely to trust.

**Cause.** `discover.rank_for_gate` returns `hit + rest` — candidates that matched a gate keyword,
then everything else — so the dropdown can offer the full list and let the adopter choose. That is
correct, and it is `DR-38`'s rule. But `defaults.propose_gates` took `ranked[0]` as a **proposal**.
Ranking answers *"which of these is most plausible?"*; it never answers *"is any of these right?"*
With nothing relevant in the repository, the top of the ranking is simply the only file there is,
and the accompanying detail said *"the closest match in this repository for this gate"* about a file
that matched nothing.

**This is `DR-40`'s own standard, missed in one place.** That record was careful about what must
*not* be proposed — no gate descriptions, no invented decision-record id — on the principle that *a
field with no honest source is left unanswered and still asked*. An unmatched file is not an honest
source. The rule was right; one call site did not apply it.

**Remedy** (`ACT-032`): `discover.matched_for_gate()` exposes the matched subset `rank_for_gate`
already computed, and `propose_gates` proposes only from it. No match → no proposal, and
`unanswered()` asks the question. The dropdown is unchanged and still offers everything.

**The transferable part: offering is not proposing.** The same list can be honest as an offer and
dishonest as a proposal, because an offer says *"here is what I found"* while a proposal says
*"this is the answer"*. Any ranking used for both needs to carry whether anything actually matched —
ordering alone cannot distinguish the best candidate from the only one.

---

## F39 — The gate catalogue never received the repository scan

**Severity: high. Closed.**

Found by the maintainer completing the first adoption this framework has ever finished end to end.
The wizard wrote a real profile. The profile is unusable: seven gates name `asdf`, `sadf` or
`safdsa` as their precondition artefact, and the checker rejects every one of them.

```
[SP032] Gate 'work_registration' requires an artefact that does not exist
        what: asdf is named as a precondition but is not present.
```

**Cause.** `tui/app.py` built the gate catalogue by calling `plan.gate_plan(...)` **without passing
the repository scan**, while the controls screen went through `section_plan()`, which scans. So the
controls screen offered dropdowns of real files and the gate catalogue offered blank text boxes.
There was nothing to pick from, so placeholder text got typed - which is the correct behaviour from
a person facing an empty required field, and the wrong behaviour from the wizard.

**The join test could not have caught it, and that is the transferable part.** `ACT-028` added a
screen-to-plan join and `DR-37` called it load-bearing. It compared field **ids**, and the ids are
identical whether a field renders as a dropdown or a text box; only the **kind** differs. That is
`F37`'s shape one level up: not "the wrong questions" but *the right questions asked in the wrong
form*.

Strengthening the join to compare `(id, kind)` was necessary and **still not sufficient**, which is
worth recording plainly. The join builds both sides itself - it constructs a plan and a screen from
that same plan - so it can never see the app wiring two screens from *different* sources, which is
exactly what happened. Only a test that drives the real `AdoptApp` catches it, and
`test_the_app_itself_gives_every_screen_the_repository_scan` now does; with the defect reintroduced
it reports *"rendered as EditableInput - the scan did not reach this screen"*.

**Four interface faults reported in the same run**, all closed here:

| Reported | Cause |
|---|---|
| *"the tick mark doesn't fit in the box and it's really not properly visible"* | `▐✔▌` put a tick between two half-block characters. Now `[X]` / `[ ]` and `(●)` / `( )`, which render identically everywhere |
| *"why radio buttons sometimes and other times ticks and other times double click on the word"* | Three interaction models. The gate catalogue's chip row - faithful to the mockup - was the third; it is a radio set now |
| *"for dropdown list you need to click twice for it to show"* | Textual focuses a `Select` on the first click and opens on the second |
| *"too many options to know which one is the right one"* | Forty alphabetical candidates. Now ranked per gate and cut to twelve **after** ranking - capping first threw away the register and the CHANGELOG before ranking could promote them |

**And the run ended with no confirmation.** *"I finished the wizard, clicked on write (Ctrl+S) but
not sure if something happened."* A full-screen app closes, the terminal is restored, and two short
lines are easy to miss. The ending now states the path it wrote and runs the checker against it, so
the question actually being asked gets an actual answer.

## F38 — A multi-line answer could not be written, and four interface faults made the wizard error-prone

**Severity: high. Closed.**

Found by the maintainer, running the phase-3 build against Plutos for the first time and being
unable to finish. He typed a two-line rationale and the review screen refused it; his verdict on
the rest was about the interaction model rather than any single defect: *"overall this wizard is
prone to user errors... I believe the wizard should do a discovery of the repo first to identify
what is the potential candidate for each question before asking it, and all decisions should be
select. Free text is confusing and really prone to errors."*

**The blocker was worse than the symptom shown.** `render._block` refused any newline, so pressing
Enter in a rationale box produced a failure at the *review* screen - after the whole interview had
been answered. The message he saw came from the TUI's broad `except`; the second, authoritative
render in `wizard.run` sits outside any handler, and `cli.py` caught only four exception types, so
the same value could have surfaced as a raw traceback. He was protected only because the review
screen refused first. **The restriction was never in the format** - this repository's own shipped
profiles use folded scalars seventeen times - only in a renderer that interpolates values after a
`key: ` prefix and had nowhere to put a second line.

**Two of the four interface faults were this project's own code, not the framework's:**

| Reported | Cause |
|---|---|
| *"the terminal is cut if you minimise the window, it doesn't autoadjust"* | Textual installs a `SIGWINCH` handler and reflows automatically. `Vertical` is simply not a scrolling container, and every screen used one as its frame |
| *"some boxes (x) are not clearly visible"* | `ToggleButton` draws the same glyph in both states and signals on/off **by colour alone** |
| *"not obvious how tab and control+S work"* | Only `Tab` was bound; the arrow keys did nothing in a text field |
| *"the explanations are at the very bottom, took me a while to realise"* | `F37`'s own remedy. Help was moved to the docked hint line to stop it rendering for every field at once; that fixed the clutter and buried the text |

**Closed by discovery, not by more free-text validation.** `discover.py` reads the repository -
git-tracked only - and offers what is actually there: real files for a precondition artefact, real
directories for a register, real step names out of the workflow YAML for a CI-step reference, the
schema's own enum as tick boxes for `enforcement`. `DR-38` records why this reconciles rather than
reverses `example_answers.py`'s refusal to invent plausible paths: a file that exists in the
adopter's own repository is a different kind of thing from an invented one, and the rule underneath
that refusal - never offer something that isn't there - is the one this keeps.

**Three defects were found by tightening this packet's own assertions, and are worth recording
because they were invisible to the loose versions:**

- Setting `BUTTON_INNER` to a tick - the obvious fix for the invisible checkbox - was wrong in a
  worse way: the class variable is drawn in **both** states, so an **unchecked** box rendered a
  tick and looked answered. A whole-screen comparison passed it; narrowing the assertion to the
  checkbox's own row caught it.
- `Input:focus { border: none }` stripped the underline from the one field being typed in.
- `Select` exposes both `BLANK` and `NULL` and they are **different objects**, so
  `value is Select.BLANK` was silently always false and would have returned the sentinel as though
  a human had chosen it. `is_blank()` is the supported test.

Swapping the frame to `VerticalScroll` also introduced a regression it took driving the app to see:
a scrollable container is focusable by default, so it swallowed the arrow keys before any field saw
them. The frame scrolls and refuses focus.

## F37 — An interface was verified structurally and never looked at

**Severity: high. Closed.**

Found by the maintainer, opening the wizard `ACT-027` had just shipped and sending three
screenshots. `ACT-027` closed with 87 passing checks, a decision record, and a published artefact
captioned *"the three frames from the approved mockup, now captured from the running wizard rather
than drawn"*. The interface in the screenshots is not the one any of that describes.

**The defect is in the verification, not in the widgets.** Every Phase 2 test asserted structure -
field-id joins between screen and plan, widget counts, status transitions, chip selection, focus
behaviour - and each was sound. None asserted what a screen puts on the terminal. So six
user-visible faults passed all of them, and the agent then published screenshots as evidence of
fidelity **without looking at the images**.

This is the failure mode `working-method.md` names as the one that does not present as an error at
all: *validated a reconstruction, a draft, or an intermediate rather than the thing actually
delivered*. The other three shapes it lists yield a wrong answer; this one yields **a right answer
about the wrong object**, so every instinct for catching a bad check - repeat it, re-derive it, add
another assertion - confirms it. Adding a tenth structural check could not have found any of these.

**What was actually wrong, each measured rather than inferred:**

| | Defect | Cause |
|---|---|---|
| 1 | `[Tab]` and `[Enter]` rendered as nothing, so legends read `next  [⇧Tab] back` and `move   choose` | Textual markup parses them as style tags. `Content.from_markup("[Tab] next").plain` is `" next"`; symbol-bearing keys like `[Ctrl+S]` and `[↑↓]` survive, which is exactly why it looked right |
| 2 | The resume screen offered a choice with **no visible keys at all** | Same cause, worst instance: `[y]` and `[n]` were its only affordance |
| 3 | Every field printed its own name twice | The label was rendered *and* passed as the input's `placeholder` |
| 4 | Labels stacked above values instead of forming the mockup's column | The row was a `Vertical`, so a width on the label could not place it beside anything |
| 5 | Every field's help rendered at once, indented into mid-screen | Phase 2's own plan said "help for the current field only, inline in the hint line"; the opposite shipped |
| 6 | One gate visible where the mockup's whole thesis is several | Per-field margins and full-height inputs. All nineteen *were* mounted on one surface - which is what the tests checked, and why they passed |

**Closed by making rendering checkable, not by fixing six things.** `tests/test_render.py` reads the
compositor's own rendered lines (`[strip.text for strip in screen._compositor.render_strips()]` -
the path `App.export_screenshot` already walks) and asserts named properties over them: every legend
renders the keys it names; no label appears twice; a label and its value share a line; one field's
help at a time; at least three gates visible at 80x24; the level list is numbered and marked.

`DR-37` records why these are **properties rather than a snapshot**: this project treats a golden
file as an audit trigger, and a full-screen capture of a wizard whose copy is still being tuned
would churn on every wording change and train exactly the regenerate-to-green habit
`.claude/rules/surfaceplate-tests.md` warns against.

**Each assertion was seen to fail before it was trusted.** All eleven failed against the unfixed
code, one per defect; afterwards three were re-broken deliberately - the placeholder restored, a
legend sent back through markup, gate collapse disabled - and each caught its own defect again. A
property test that has never failed is a property test nobody has calibrated.

**Two further faults were found by then reading the rendered output**, which is the practice this
finding exists to establish: the level list's wrapped lines began at column 0 and broke the
numbering into a paragraph, and the detected-signals line listed four full workflow paths across
three rows. Neither was in the original six; both were visible the moment anyone looked.

## F36 — A hand-built flow list escaped each item for the wrong YAML context, and lost a real ~20-minute session

**Severity: high. Closed.**

Found by the maintainer, running `surfaceplate adopt` against Plutos for real, not a probe — the
first time this exact code path had a human's own answers behind it rather than a scripted fixture.
Roughly twenty minutes into a `standard`-level, 19-gate walk, the final write step refused: the
wizard's own round-trip check (`wizard.py`'s `_verify()`, which re-parses `render.py`'s output
before anything reaches disk — see that module's docstring) could not parse what `render.py` had
produced, and there was no way to recover the already-answered questions. His own words, from the
same session that raised `F35`: *"Extremely long and difficult... really bad experience."* The
data loss compounds a design gap the same session raised separately — see `DR-35` for the wizard's
wider remediation, of which this fix is the correctness half.

**`FACT FROM PACKAGE`, read against the exact parser error.** The literal answer `what is this?`
had been typed for a gate's precondition artefact. PyYAML's own error named the column: `expected
',' or ']', but got '?'`, inside a flow sequence `render.py` had built by hand as
`f"artefacts: [{_scalar(value)}]"`.

**The root cause is a context mismatch, not a missing escape.** `render.py`'s `_scalar()` is
correct for what it was written to do: it asks PyYAML to escape a value as though that value were
its own standalone document (`yaml.safe_dump(value, default_flow_style=True)`), which is exactly
right when the result is placed after a `key: ` prefix — a bare `what is this?` needs no quoting
there. A YAML flow sequence has stricter rules for what one *item* inside `[...]` needs quoted
than a value has as a whole document, and `render.py` never asked PyYAML to escape for that
context — it escaped each item alone, then wrapped hand-written brackets around the result. The
same pattern, discovered while fixing this and not previously flagged, also affected `enforcement`
— rendered with no escaping call at all (`", ".join(gate["enforcement"])`), which happens to be
unreachable through a schema-valid answer today (`enforcement`'s items are a fixed schema enum with
no special characters in any legal value) but was still a raw, unescaped string interpolation on
the same class of structure.

**A pattern that looked identical was checked, not assumed safe.** `_render_list_block()` (used
for `human_roles`/`exclusions`) also calls `_scalar()` per item, composed into a block list
(`- {value}`) rather than a flow sequence. Tested directly against the same tricky characters
(`?`, `,`, `[bracket]`, `-leading-dash`, `trailing:colon`, `{brace}`) before deciding whether it
needed the same fix: it round-trips correctly for all of them, because a block-sequence item's
plain-scalar escaping rules happen to coincide with a standalone document's, unlike a flow-sequence
item's. Left unchanged, on that evidence rather than on the pattern merely looking similar.

**Closed by rendering the whole list, not each item alone.** A new `_flow_list()` helper hands
PyYAML the real Python list — `yaml.safe_dump(values, default_flow_style=True, width=...)` — so it
escapes each item for the flow-sequence structure it is actually going into, the same discipline
the module's docstring already states for every other value it emits. Replaces all four sites:
`precondition.artefacts`, `gated_activity.paths`, `enforcement`, and the baseline
`secret_hygiene.scanner.wired_in`. A new regression test
(`tests/test_tricky_characters_round_trip` in `tests/test_adopt.py`) scripts the exact failure
shape — `?`, `,`, `[`, `]`, and a leading `-` across the four affected fields — through the real
wizard flow and asserts the written profile round-trips to exactly what was typed, not merely that
`render.py`'s own functions parse in isolation.

## F35 — A refusal named three routes; only one was a route a reader could actually take

**Severity: medium. Closed.**

Found by the maintainer, not by a probe or a review — the first time anyone but the agent that
built this framework ran the installer against a real repository and had to act on what it said.
Running `surfaceplate install --target plutos --dry-run` hit the hook-configuration refusal
immediately, and his own words are the finding: *"I run it and didn't understand what was
happening... we don't give the user any alternative or way out. It just stops."*

`FACT FROM PACKAGE`, read against the message as it stood: it named the conflicting
`core.hooksPath` value and stated three routes — reconcile, remove, or `--no-hooks`. Only the
third was something a reader could type. "Reconcile the existing hooks into `.githooks` without
losing their behaviour" and "Remove the old hook configuration" each described an *outcome*, never
a *step*. And nothing in the message said whether the conflicting value was set for this one
repository or for every repository on the machine — confirmed directly to be knowable
(`git config --local --get core.hooksPath` exits 1 on the maintainer's real case;
`git config --global --get core.hooksPath` prints the value) but never checked.

**`F27` closed the first half of this and left the second half looking closed when it wasn't.**
`F27` gave this refusal a third route where before there were only two — a genuine fix, and this
finding does not reopen it. What `F27` did not establish, because nothing had tested it against a
real human's real decision, is that *naming* a route and *reaching* it are different bars. Every
probe this session ran past this refusal used `--no-hooks` programmatically; none of them stood in
the position of a reader trying to act on "reconcile" or "remove" with nothing but that sentence.

**Closed by making both the fact and each route actionable, not by rewording.** A new
`hooks_path_scope()` checks `core.hooksPath` at `--local`, `--global`, and `--system`
individually (deliberately not `--worktree`: an intermediate version of this fix checked it first,
and without `extensions.worktreeConfig` enabled — the common case — git reads `--worktree` from
the same file as `--local`, so checking it first misattributed every plain local setting as
worktree-scoped; caught in this project's own manual testing before it shipped, and dropped rather
than special-cased, since only `--local`/`--global`/`--system` are ever genuinely distinct
storage). The rewritten message states what `core.hooksPath` does before naming the conflicting
value, names the scope and its blast radius explicitly (a global or system value: *"every
repository on this machine, not just this one"*), gives the exact, scope-correct
`git config --<scope> --unset core.hooksPath` for "remove," and for "reconcile" — genuinely harder
to reduce to one command, since it depends on what the existing hook does — points at the actual
delegation pattern this exact machine's own conflicting hook already uses (found while diagnosing
the case that prompted this) as a worked model rather than a vague instruction to merge behaviour.

## F34 — The release manifest could name a file that exists on no machine but the one that built it

**Severity: high. Closed.**

Found by CI, not by anything run locally, directly after `F33` landed on the same branch:
`scripts/build_release.py --verify-manifest` passed on the machine that built the release, then
`MANIFEST_CURRENT=FAIL` in CI on the exact same commit — *"in manifest but not on disk:
surfaceplate-0.16.0/.claude/scheduled_tasks.lock"*.

`FACT FROM PACKAGE`. `payload_files()` walked `ROOT.rglob("*")`, filtered only by `EXCLUDED_DIRS`,
`EXCLUDED_FILES`, and `installed_paths()` — never asking git anything. `.claude/scheduled_tasks.lock`
is a Claude Code harness runtime artefact, present on the machine that built the release because a
session on it had scheduled a wakeup, and excluded from this repository only by the machine-local
`.git/info/exclude` — a file that lives outside the repository entirely and travels with no clone,
no CI checkout, nothing but that one machine. Nothing in `build_release.py` ever consulted it.

**The manifest was, without anyone deciding this, only ever as trustworthy as the working tree of
whoever last ran the build.** Any local, uncommitted, non-`.gitignore`d file sitting in the tree at
build time — a scratch note, an editor swap file, a session artefact from whatever tool built the
release — would enter the payload silently, hashed and named as though it were a real part of the
standard, on no evidence stronger than "it happened to be present." `.claude/rules/*.md` — genuine,
git-tracked payload content shipped from the same directory — is why a blanket exclusion of `.claude/`
was never the right fix; the problem was never that directory, it was that nothing distinguished
what belonged to the repository from what belonged to the machine.

**Closed by asking git, not by naming one more file.** `payload_files()` now intersects its
filesystem walk against `git ls-files --cached --others --exclude-standard` — every path git
considers part of this repository, tracked or not-yet-added, honouring `.gitignore`,
`.git/info/exclude`, and the global excludes file together, the same set a plain `git status` would
call clean. Deliberately not restricted to tracked-only: this project's own packet order builds the
manifest *before* staging and committing, so a brand-new file not yet `git add`ed still has to enter
the release built from it, or every packet this session has run would have silently dropped its own
new files from the manifest it just built.

**The general shape, not a one-off.** A build process that trusts "what the filesystem currently
holds" instead of "what the repository actually is" will re-admit whatever the filesystem happens to
be holding on whichever machine runs it next — a scratch file, a different tool's cache, anything
`.gitignore` was never asked to name. This is the same failure mode `F1` recorded for the test suite
(a pass conditional on an unstated environment fact) and `F31` recorded for the history audit (a
clone shallow enough to make a real check pass by never looking), in a third artefact: the release
manifest.

## F33 — An all-digit commit SHA silently fails a gate exception, and the lesson never propagated

**Severity: medium. Closed.**

Found chasing an intermittent test failure during `ACT-024` (the Plutos exercise): roughly one run
in forty of `tests/test_install_and_check.py`'s history-audit section failed with `SP043`, *"Gate
exception ... is invalid: commits/0: 3516272 is not of type 'string'"* — a commit SHA the test had
itself just written, rejected as not being a string.

`FACT FROM PACKAGE`. A commit SHA is hexadecimal, and roughly one seven-character prefix in
forty-three (`(10/16)^7 ≈ 2.3%`) consists entirely of digits, no `a`–`f`. Written unquoted in YAML —
`commits: [3516272]` — a value in that shape parses as an integer, not a string, because it also
satisfies YAML's plain-scalar-integer grammar. `schemas/gate-exception.schema.yaml` correctly types
`commits[*]` as `string`; the schema was never wrong. The trap is upstream of it, in how a value
gets *written*.

**This was not a new discovery — it was a lesson that failed to propagate.**
`governance/exceptions/GX-0001.yaml`'s own comment already documents catching it, verbatim: *"an
abbreviated SHA that happens to be all digits - 7547482 here - parses as an integer and the schema
rejects it."* Someone hit this for real, quoted the value, and left a note explaining why — but the
note lived only in that one record. It reached neither `templates/gate-exception.yaml` (the
adopter-facing template, which showed the commit list unquoted), nor `tests/test_install_and_check.py`
(which wrote its own probe SHA unquoted, and so intermittently rediscovered the same trap on
whichever run happened to draw an all-digit prefix), nor the checker's own error message (a bare
jsonschema `"is not of type 'string'"`, giving no reader who has not already found `GX-0001`'s
comment any reason to suspect YAML's numeric grammar rather than their own SHA being wrong).

**Closed three ways, not one, because a single fix would have left the shape to recur elsewhere:**

- The template now shows the commit entry quoted, with the reason stated inline.
- `check_conformance.py`'s `validated_exception` detects a `commits` entry that failed validation
  specifically because it parsed as an integer, and appends a targeted remediation sentence — the
  first time this project has customised a schema-validation message for one specific value shape
  rather than reporting the generic jsonschema text alone.
- The test now quotes its own probe SHA, so it tests the mechanism the way an adopter who read the
  template would actually use it, rather than intermittently testing an unrelated failure mode by
  accident.

**The shape, named because it recurs across this register in different clothes.** A fix applied
once, in one artefact, that never reaches the sibling artefacts a reader would actually consult —
`F26` (a remedy that existed since `DR-22` and the finding that most needed it never mentioned it),
`DR-28`'s own account of `F25` and `F26` (defects invisible from inside because the fix could not be
used without causing it). This one is sharper only in how it was found: not by an adopter, and not
by a reviewer, but by this project's own test suite drawing the unlucky case by chance, on a
completely unrelated packet.

**Severity: high. Closed.**

Found by the review `ACT-021` requested — item 9 of `org/RELEASE_PLAN.md`, the first time this
framework has been read by a party other than the maintainer and the agent that built it, and the
first thing it found was real.

`surfaceplate/adopt/`'s own binding rule, stated in its `__init__.py` docstring before any of the
package was written: *"No module here selects a conformance level, invents a rationale, or sets a
date."* `sections.py`'s `ask_controls` hardcoded the rationale for all three baseline controls
(`agent_work_packets`, `actual_diff_review`, `secret_hygiene`) as Python string constants, never
routed through a `Prompt` call. `ask_gates` did the same for the four `DESIGN_GATES` it
auto-marks `not_applicable` when `builds_user_interface` is false. Both wrote a rationale to the
profile the human never saw asked — a direct violation of the rule stated to govern the whole
package, undetected by `ACT-020`'s own 23-check test suite, which proved every *asked* question
was answered and nothing more, but never proved every *written* value traced to a question.

`FACT FROM PACKAGE`, read directly, before accepting the report: `sections.py:149-176` (as it stood
before this finding) constructed `baseline_controls` from a module-level `_BASELINE_RATIONALES`
dict and a second inline string for `secret_hygiene`, none reachable from any `prompt.text` call;
`sections.py:255-260` wrote `"rationale": "This repository has no user interface."` inside a loop
with no `Prompt` argument at all.

**Not every finding in the same report survived the same check.** Two others were verified against
the code and found not to hold: `adoption.deferrals = []` is a disclosed limitation
(`org/decisions/DR-32.md`'s "Limitations and follow-up"), not an invented claim — it asserts
nothing false, unlike a fabricated rationale. And the report's over-engineering finding — that a
non-UI repository must manually justify all four UI gates — is wrong about the code: `ask_gates`
already auto-masks them; the reviewer had not traced that branch. Accepting a review's findings
without independently checking each one against the artefact would have been exactly the "wrong
artefact" failure this project's own working-method doctrine names — validating the *report about*
the code rather than the code itself.

**A third finding in the same report was neither confirmed nor dismissed here — it was a genuine
design question, decided separately.** The report's material finding — that the schema alone
cannot detect a profile declaring `full` while omitting required controls — is accurate as far as
it goes. Whether adding conditional schema logic to close it was worth the cost is `org/decisions/DR-33.md`'s
question, not this entry's: decided against, on the finding that the scenario described does not
occur in this project's actual pipeline (the checker already runs schema validation as part of
itself), and that the proposed remedy would duplicate `CONFORMANCE_LEVELS` a second time by hand.

**Closed at `ACT-022`, in the same session the finding arrived.** `ask_controls` now asks for each
baseline control's rationale exactly as it already asked for every level-required control's; the
`DESIGN_GATES` auto-mask now asks per gate, with the old fixed string offered as an editable
default rather than a silent write, so the "no UI" fact already given earlier is not re-litigated
four times over — an answer with a default is still a `Prompt` call a human confirmed, the same
pattern `review_by` and `enforcement` already use elsewhere in the same file. A new test
(`tests/test_adopt.py::test_design_gates_rationale_is_asked`) scripts rationale text that matches
none of the old hardcoded strings and asserts the written profile contains exactly that text — a
regression here would misalign the scripted answer sequence and fail loudly, not silently pass.

---

## F31 — The history audit ran against a depth-1 clone and reported nothing wrong

**Severity: high. Closed.**

`actions/checkout@v4` fetches **one commit** unless told otherwise, and neither this repository's
self-check workflow nor the one it installs into adopters said otherwise.

`git_history_available()` verifies `HEAD` and returns true, because a shallow clone has a perfectly
good `HEAD`. So the audit ran, examined the single commit it had been given, found no gate
violations, and said nothing — while `SP035` and `SP036` were, in CI, incapable of firing at all.

**Every green CI run this project has ever had reported a clean history audit from a look that
could not have found anything.** The advisory written for exactly this situation — *"This is an
absence of evidence, not evidence of conformance"* — never fired, because history *was* available.
Just almost none of it.

**How it surfaced**, and it is worth recording because nothing was going to surface it otherwise:
`GX-0001` names nine historical commits, and CI could not resolve one of them —
`'1b0df98': fatal: Needed a single revision`. The exception mechanism failed loudly on a shallow
clone, and that failure is the only reason the audit's silence was examined. A control that fails
closed exposed one that had been failing open.

**Closed** two ways, because either alone leaves the defect somewhere:

- `fetch-depth: 0` in both this repository's self-check workflow **and** the one installed into
  every adopter. Without the second, every adopter inherits the same false green.
- The checker now detects a shallow clone with `git rev-parse --is-shallow-repository` and says so,
  in the same terms as the unavailable-history note. A workflow is configuration an adopter can
  change; the checker saying what it could and could not see is not.

**The shape, and its worst form.** An instrument whose negative result does not establish what it
appears to — `F12`, `F14`, `F21`, `F23`, `F25`, `F28`. This instance is the most complete: the
control was present, configured, running, and green, in the repository that publishes the control,
for its entire history. Nothing failed. The audit's silence was indistinguishable from success, and
only an unrelated check refusing to pass on the same missing data made anyone look.

## F30 — A renamed precondition artefact makes a gate's entire history read as non-compliant

**Severity: medium. Closed.** Cleared for this instance by `governance/exceptions/GX-0001.yaml`.

*Status line reconciled with the index under `ACT-046` (`F72`, 2026-09-02): the index had recorded this as closed by `ACT-030`, which built the deferred remedy the body's last paragraph awaited: the audit follows renames, and the conformance advisory now reports `test_convention` followed through two; the body still said Open.*

The history audit resolves a gate's precondition artefact by its **current** path, then asks
whether that path existed at each commit that touched a gated path. So renaming the artefact —
without changing a word of it — retroactively reports every earlier commit as having crossed the
gate without its precondition.

Observed here, immediately and unavoidably. `test_convention` names a testing-convention document
that has existed continuously since `0.9.0`. At `0.17.0` it moved from
`standard/.github/instructions/tests.instructions.md` to `standard/agent-instructions/tests.md`
so the instructions could be emitted per agent (`DR-30`, `F29`). The audit then reported **nine
commits** as violations, back to the repository's first:

```
[SP035] Gate 'test_convention' was crossed without its precondition
  9 commit(s) since 2026-08-31 changed a gated path while a required artefact was absent
```

Not one of them crossed anything. The convention was in force throughout, under a different name.

**Why the obvious remedies do not apply**, which is what makes this a finding rather than a
nuisance:

- **Moving `effective_from` forward** is refused by `SP034`, deliberately and correctly — it would
  erase every violation between the old date and the new one.
- **Listing both the old and new path** fails `SP032`, which requires every named artefact to
  exist; the old path is gone.
- **Not renaming** is not available: the rename was the fix for `F29`.

So the only route is a gate exception, which is the designed escape hatch and leaves a permanent
mark. That is the right outcome for *this* instance and the wrong shape as a general answer: an
adopter who reorganises their documentation will be asked to file exceptions for work that never
violated anything, and `DR-22`'s warning applies — *"a growing pile of these records is evidence
that the gate is wrongly scoped or the process is wrong."*

**The candidate remedy is to follow renames**, which git can do (`--follow`), resolving the
precondition's path *as at each commit* rather than as at HEAD. It is not built, and it is not a
small change: `--follow` is heuristic, single-path, and its results would have to be trusted by a
control. Left open rather than half-built.

**Closed at `ACT-030` (`DR-39`), and the heuristic objection was answered rather than waved past.**
`historical_paths()` collects every name an artefact has had and the audit looks for it under all of
them. Two properties make a heuristic safe to put inside a control:

- **It can only ever add names to look for.** So it can clear a false violation and can never hide
  a commit where nothing existed under any name. Verified: an artefact that never existed still
  resolves to itself alone, and a genuine violation after a rename is still reported.
- **Every rename it follows is stated on the run.** This repository's own output now reads
  *"test_convention: precondition ... followed through 2 rename(s): ... <- ... <- ..."* - the exact
  chain `DR-30` and `DR-31` created. An adopter sees which chain was trusted rather than watching a
  check go quiet.

Where git cannot answer - a directory rather than a file, no history - it falls back to the strict
pre-`F30` behaviour, which errs toward reporting. The directory case was found by driving it:
`--follow` pointed at a directory silently traces some file *inside* it and reports that as the
directory's former name. Harmless in effect, since a file existing implies its directory did, but
accidental rather than designed, so directories now keep the strict check explicitly.

`GX-0001` and `GX-0002` are **kept and marked superseded**, not deleted. They cover violations that
no longer occur, but they are the record of what was decided and when, and deleting an exception
record is precisely the retrospective edit `core/PREREQUISITE_GATES.md` says an exception must never
be able to make invisibly.

**A trap found on the way, worth its own line.** The exception record listed abbreviated SHAs
unquoted, and `7547482` — seven digits, no letters — parsed as an **integer**. `SP043` rejected the
record. The check did its job; the trap will catch any adopter whose abbreviated SHA happens to be
all digits, roughly one in every few dozen.

**It fired again, immediately, on the next rename.** `ACT-019` moved
`standard/agent-instructions/tests.md` to `surfaceplate/standard/agent-instructions/tests.md` when
the payload was packaged for pip (`DR-31`). The same mechanism reported the `DR-30` commit as a
violation, for the same reason, and was cleared by a second exception,
`governance/exceptions/GX-0002.yaml`. Two occurrences of the same defect in one session, both from
renames this project chose for its own good reasons, is stronger evidence than this finding had when
first written that the deferred remedy deserves higher priority. Not built in either packet:
building it as a side effect of an unrelated change would be the scope creep this project's own
working method exists to catch. Severity and status unchanged; this is evidence added to an open
finding, not a reopening of a closed one.

## F29 — The agent instructions the framework ships are not read by the agent that uses it

**Severity: high. Closed.**

Surfaceplate shipped 501 lines of agent instruction as six
`.github/instructions/*.instructions.md` files, each declaring `applyTo: "**"` and opening
*"Installed by Surfaceplate. Do not edit this file in an adopting repository."*

**That is GitHub Copilot's format.** Claude Code loads managed policy, `~/.claude/CLAUDE.md`,
`./CLAUDE.md` or `./.claude/CLAUDE.md`, `./CLAUDE.local.md`, and `.claude/rules/*.md`.
`.github/instructions/` is not on that list. `.github/copilot-instructions.md` is read **only by
`/init`**, as a one-time generation step rather than session loading.

So the instructions reached one agent and no other — and surfaceplate has no `CLAUDE.md`, so they
reached **nothing at all in the repository that publishes them**. Every packet of governance work
done here has been done by an agent that never read a line of them.

**Established on two independent lines of evidence**, because assuming behaviour from a filename is
the error that produced this finding:

- **Direct observation.** Across a long working session in this repository, none of that content
  entered context, while `~/.claude/CLAUDE.md` and its four imports did. The positive control
  matters: instruction loading demonstrably works here and simply never reaches `.github/`.
- **The published documentation**, which lists the loaded locations exhaustively and states
  plainly: *"Claude Code reads `CLAUDE.md`, not `AGENTS.md`."*

That last sentence also disposes of the remedy `DR-12` had planned. It committed to *"`AGENTS.md`
as the canonical emitted instruction file"* — which would have been **equally inert** for Claude
Code without a `CLAUDE.md` importing it. The commitment was right about neutrality and wrong about
mechanism, and it was never built, so the error was never discovered.

**Fourteen of forty-five installed files — 31% of the payload — were GitHub-specific**, in a
framework whose `DR-12` promises forge and agent neutrality.

**Closed** by one canonical body in `standard/agent-instructions/` and per-agent emitters: the
Copilot form byte-for-byte as before, plus `.claude/rules/surfaceplate-*.md` carrying `paths:`
where Copilot carries `applyTo:`. `.claude/rules/` is additive, so it cannot collide with an
adopter's own `CLAUDE.md` the way writing that file would. `AGENTS.md` receives the conformance
block through the existing marker mechanism, so an adopter's own 293 lines survive untouched.

**And surfaceplate now has a `CLAUDE.md` importing `@AGENTS.md`.** That is what makes this closable
rather than merely recorded: the framework is finally subject to the instructions it publishes.

**What is not claimed.** That the instructions were subsequently *read*. Files existing in
documented locations is not the same as content entering a context window, and the difference is
this finding. It is observable in a later session via `/context` under **Memory files**, and it has
not been observed yet. Whether Copilot reads its own form is likewise untested here.

**The shape.** An instrument whose negative result does not establish what it appears to — the
register's most-repeated defect — with one aggravation the others lack: **nothing failed.** No check
went red, no adopter complained, no test broke. The files were present, correctly formatted, and
comprehensively ignored. It surfaced only when an adopter's own conventions forced the question of
which instructions govern.

## F28 — `SP038` accepted any pre-commit hook as satisfying a `local_hook` claim

**Severity: high. Closed.**

`active_pre_commit_hook` asked one question: **is there an executable `pre-commit` in the active
hooks directory?** Any hook, from anyone, doing anything.

So a gate could declare `enforcement: [local_hook, ...]` and be satisfied by a hook that formats
code, prints a message, or does nothing at all. `SP038`'s own text was *"Gate claims hook
enforcement, but there is no hook"* — and what its silence established was **"a hook exists"**, not
**"staged changes are checked before they are committed"**, which is the whole content of the
enforcement claim.

Demonstrated: a repository with the standard installed, `core.hooksPath` pointed at an unrelated
hook, and every gate claiming `local_hook`. **Zero findings.**

**This predates the hook opt-out and was exposed by it.** Declining hooks leaves `core.hooksPath`
pointing at the adopter's own system, which satisfied the old test perfectly — so the first probe
written to prove that a false `local_hook` claim is still caught found that it is not.

**Closed** by comparing the active hook against the one this standard installed. The remedy needed
no new data: `.standards/INSTALL.json` has always carried the digest of `.githooks/pre-commit`, and
a record with no such entry — because hooks were declined — cannot support the claim, which is the
correct answer rather than a special case. Three failure modes are now distinguished and each is
asserted: no hook at all, a hook that is not this standard's, and hooks declined at install. The
finding's title changed with them, because *"there is no hook"* is plainly wrong against a
repository that has one.

**The shape, again.** An instrument whose negative result does not establish what it appears to —
`F12`, `F14`, `F21`, `F23`, `F25`. What is different here is *where it was found*: not by reading
the code, but by writing a probe to demonstrate a property the plan had asserted, and watching the
probe fail. The assertion in the approved plan — *"`SP038` is untouched and still catches a gate
claiming a hook that was declined"* — was **false when written**.

## F27 — The installer forbade what the standard permits

**Severity: high. Closed.**

Surfaceplate would not install into Plyego at all:

```
STOPPED - this repository already has a different Git hook configuration:
  the effective core.hooksPath is already '<the adopter's own hooks directory>'.
Nothing has been written.                                        (exit 4)
```

The refusal is *correct*: setting `core.hooksPath=.githooks` would silently stop the adopter's
existing hook running. The installer detects this thoroughly — effective local, worktree, global and
system configuration, every hook type — and fails closed and atomically.

**The defect is that there was no third route.** `SP038` fires only when a gate's `enforcement` list
claims `local_hook`, so a profile declaring `enforcement: [history_audit, review]` has always been
fully conformant with no surfaceplate hook anywhere. **The standard said the hook was optional and
the installer said it was mandatory** — two parts of one framework disagreeing about the same
obligation, which is the defect this register names more often than any other, found in itself.

Three things made it more than a nuisance:

- Both offered remedies — *reconcile the existing hooks* or *remove the old hook configuration* —
  assume the adopter wants surfaceplate's hook. Neither contemplates keeping their own.
- The blocked case is **any repository with existing commit-time automation**, which is the target
  rather than an edge case. The first real adopter hit it immediately.
- The refusal is at the wrong layer: forty-five files of standard, schemas and checker withheld over
  one optional **25-line shim** whose entire body is
  `exec python3 "$checker" --repo "$repo_root" --staged`.

**Closed** by `--no-hooks`, which is **recorded and announced** rather than silent. The declination
is stored in `.standards/INSTALL.json` and reported by every conformance check, because the
alternative is the shape this framework exists to catch: nothing would distinguish *"staged changes
are gated"* from *"nothing gates them"*, in the profile or in a passing check alike. Every other
narrowing here announces itself — `DR-22`'s exemptions, deferral dates, `DR-27`'s unchecked-reference
notes — and a silent opt-out would have been conspicuous by inconsistency.

Chaining the adopter's hook from surfaceplate's was considered and rejected: `.githooks/pre-commit`
is standard-owned and integrity-checked, so delegation logic would ship to every adopter and have to
work for arbitrary hooks; and once `core.hooksPath=.githooks`, the displaced hook is reachable only
if surfaceplate calls it, making the framework the permanent owner of another system's hook.

## F26 — `SP032`'s placeholder remedy was wrong for most gates, and named no remedy

**Severity: low. Closed.**

`SP032`'s placeholder branch hard-coded *"Complete the artefact. A template is not a design
policy."* — for **every one of the nineteen gates**. The wording was written for `design_authority`
and copied into the generic path, where it says nothing sensible about a work register, a changelog,
or a dependency review. Seventeen of the nineteen gates are not about design policy.

The larger half is that it **named no remedy**. `placeholder_scan_exemptions` has existed since
`DR-22`, and the finding that most often needs it never mentioned it. Plyego is the evidence: the
remedy had to be recalled from a decision record, because the finding gave nothing to act on.

**Closed** with generic wording — following `SP051`'s existing *"A template is not an implemented
control"* — plus a sentence naming the exemption route and stating what it does not suppress.

## F25 — Declaring a placeholder-scan exemption made the profile fail the placeholder scan

**Severity: medium. Closed.**

`SP020` walked **every string in the application profile** and raised a finding on any placeholder
token. `SP032` does the same for a gate's precondition artefacts, and `DR-22` gave that one a
remedy: declare `placeholder_scan_exemptions` with a rationale saying why the artefact legitimately
contains the token.

**The remedy could not be used.** A rationale explaining why an artefact contains a token has to
quote it — and the rationale is a string in the profile, so `SP020` fired on the exemption itself.

Observed end to end, and not here. Plyego's `activity/register.md` line 401:

```
| ACT-395 | debt | F080 appendix-card chapter_archetype always "tbd" in S2 — RESOLVED | Closed | |
```

A **closed** work item whose title quotes the literal string because that string *was* the defect,
inside a 590-line live register. `SP032` flags the file. Declaring the exemption then failed
`SP020`. A `PASS` was only obtained by wording around the token — precisely the workaround `DR-22`
names as bad: *"a changelog that cannot describe a control is a worse artefact than one needing an
exemption."*

**This is the fifth instance of the self-quotation shape in this register, and the first that is
structurally unavoidable.** The earlier four — `.gitleaksignore`, `ORGANISATION.md`, `CHANGELOG.md`,
`DR-23` — were documents that happened to describe a defect and so reproduced it; each could be
reworded or exempted. Here the **mechanism built to fix the defect cannot be used without causing
it**. That is a different class of problem, and it is why this one is a finding rather than another
instance of `F16`.

**Why it was invisible from inside.** Surfaceplate declares two exemptions of its own, for
`org/FINDINGS.md` and `CHANGELOG.md`, and both rationales *describe* the tokens without reproducing
them — a habit formed by `F14` and `F15`. The trap needed an adopter who wrote the natural sentence.

**Closed** by excluding `placeholder_scan_exemptions[*].rationale` from the profile walk, and
nothing else. One field, not one record: the `artefact` path beside it is still scanned, as is every
other rationale in the profile. Three negative controls hold that line.

**What it costs.** A rationale reading only `TODO` now passes. That is `DR-22`'s already-recorded
limitation — *"nothing checks that a rationale is a real one"* — and is cited rather than restated
as new.

## F24 — A schema clause that could never add an obligation, grading the wrong axis

**Severity: low. Closed.**

`schemas/method-run-lineage.schema.yaml` carried three `allOf` branches. The third required
`input_hash`, `implementation_revision`, `configuration_hash` and `output_hash` of completed runs at
medium or high materiality. **Both its condition and its consequent are subsets of the first
branch's**, which requires those fields — and three more — of *every* completed run. It could never
add an obligation to any instance.

Inert, and not harmless. A schema is a **contract people read to learn what is required of them**,
and this one told a reader that a low-materiality completed run escapes fields it does not escape.
That is a contradictory-authority defect — the one this framework names most often — living inside a
published schema rather than between two documents.

**Which branch was the leftover could not be settled from history.** The public repository is one
squashed commit (`DR-23`), and `CHANGELOG.md` had never mentioned materiality at all. The design
evidence settled it:

> `schemas/override-record.schema.yaml:45-48` is the **only** live use of `materiality` in any
> schema, and it grades **approval** — a material override requires approval. It does not relax
> record completeness: `evidence_reference`, `rollback_approach` and `calculation_impact` are
> required of every override at every materiality.

So where the framework actually expresses this principle, **materiality decides who must sign off,
not how complete a record must be.** The run-lineage branch graded the wrong axis.

**Closed by removing it**, not by making it real. Narrowing the first branch so low-materiality runs
genuinely need less would loosen a published contract against the only place the principle is
stated, and would grade completeness by a **self-declared** field — an incentive to classify
everything `low`. No instance's validity moves, so the change is not breaking and the `$id` version
segment stays at `0.7.0`.

**What this says about the schemas generally**, and it is the reusable part: `materiality` is
required on both record types and, after this change, is consequential in exactly one of them.
Together with `F22` — where the only date on a gate exception records its creation and not its
expiry — the pattern is that **these schemas collect a field far more readily than they give it
force.** Worth checking before adding another.

## F23 — A drift guard matched on line shape rather than on the thing it guards

**Severity: medium. Closed.**

`tests/validate_contracts.py` asserts that the gate catalogue in the checker and the one in
`core/PREREQUISITE_GATES.md` do not drift apart. It found the catalogue with:

```python
re.findall(r'^    "([a-z0-9_]+)": "', CHECKER, re.MULTILINE)
```

That matches any four-space-indented `"key": "value"` line **anywhere in the file**. It was not
reading the gate catalogue; it was reading a line shape that the gate catalogue happened to have
exclusively. Adding `PATTERN_C_CONTROLS` — an unrelated module-level dictionary of the same shape —
put four non-gates into "the gate catalogue".

**It failed, and that is the only reason it was noticed**: the count went 19 → 23 and the assertion
tripped. The failure was luck, not design. Constructed and run rather than reasoned about:

| Mutation | Old guard | New guard |
|---|---|---|
| Drop one gate, add a **one-entry** dict of the same shape | **19 — passes** | 18 — fails |

The set the old guard then iterates has silently lost `component_library` and gained `not_a_gate`,
and every assertion downstream — including *"every catalogue gate is documented"* — runs against it
and passes. A false green on the guard whose whole purpose is to prevent silent divergence.

**Closed** by anchoring the search to the `GATE_CATALOGUE` block itself, so a dictionary elsewhere
in the file cannot be absorbed and a renamed or moved block fails loudly rather than matching
nothing. Verified in both directions: the real tree still reads 19 with `PATTERN_C_CONTROLS`
present, a removed gate reads 18, and a decoy dictionary changes nothing.

**Why it is recorded rather than quietly fixed.** This is the register's most-repeated shape — an
instrument whose negative result does not establish what it appears to — and this instance was
*inside an instrument*, in a guard written specifically to stop something drifting. `F14` was the
same shape in the placeholder check, `F21` in a control that named its own absence, `F12` in the
vendored-copy comparison. The lesson that generalises: **a check anchored on incidental syntax is
measuring a coincidence**, and it keeps passing after the coincidence ends.

## F22 — A deferral's revisit date was required to exist and never read again

**Severity: medium. Closed for deferrals; open for gate exceptions.**

`SP031` refuses a deferred control or gate that carries no `revisit_by`, on the stated grounds that
*"a deferral with no owner and no date is an omission wearing a decision's clothes."* Nothing then
ever read the date. Demonstrated before the fix:

```
revisit_by: "2020-01-01"   ->   PASS - all conformance checks satisfied.
```

Six years expired. The control that exists to prevent a permanent exclusion was creating one.

**Closed by `SP054`** for `adoption.deferrals[].revisit_by` and for deferred prerequisite gates. A
date that has passed raises a finding; a date within 30 days produces an advisory, mirroring how
`adoption.review_by` has always been treated; a malformed date fails, because a date that cannot be
parsed is not a deadline and the deferral would be permanent by accident.

**Why this is recording rather than judging.** The date was declared by the adopter. Comparing it
against today establishes whether a stated commitment has come due — it decides nothing on their
behalf. That distinction is what kept `I` (per-change risk classification) deferred and what keeps
gate exceptions out of scope below.

**Open: gate exceptions have no expiry mechanism at all.** `schemas/gate-exception.schema.yaml`
carries `raised_on`, and it is **optional** — a creation date, not a deadline. So an exception is
permanent by construction, and no amount of checking fixes that, because there is nothing declared
to check against. Giving exceptions an expiry means adding a field to a published contract, which is
a decision rather than an implementation detail, and it is not taken here.

That is the sharper version of this finding: deferrals were unenforced, exceptions are
**unenforceable**. The first was a gap in the checker; the second is a gap in the schema.

**Recorded about the sequence, not the code.** The scope review kept this item unconditionally and
ordered it *before* the first record validator. Patterns D, A and B were a larger substitution for
`G′` than that review anticipated, and this was overlooked in the process — an agreed sequence
departed from without anyone deciding to.

---

## Historical series — closed, cross-referenced, not renumbered

### `PRE-AUDIT-0.6.0/F1`–`F4` — `audit/PRE_AUDIT_FINDINGS_0.6.0.md`

Technical pre-audit of `0.6.0`, severity carried in each heading (`:45,66,78,88`): F1 HIGH
(application profile could not record adoption identity), F2 MEDIUM (producer validation record
stale), F3 MEDIUM (schema `$id`s used `https://example.invalid/`), F4 LOW (shipped templates did not
validate against their own schemas).

**All four remediated at `0.7.0`** — `CHANGELOG.md:60-82`. Carry the caveat the closure itself
records, `audit/VALIDATION_RESULTS.md:62-64`: the pre-audit *"was performed by a coding agent at the
maintainer's request. It was not independent, and it does not discharge the audit gate."*

### `PRIOR-AUDIT/C1`–`C4`, `M1`–`M7`, `O1`–`O4` — `audit/PRIOR_AUDIT_REMEDIATION.md`

Fifteen findings from the audit supplied 2026-08-21, severity carried in the prefix
(Critical / Material / Other). **Twelve are remediated. Three are not, and nothing was tracking
them until this register:**

| Code | Disposition as recorded | Status here |
|---|---|---|
| `PRIOR-AUDIT/M6` | *"Partially remediated: … native enforcement remains application-owned."* (`:16`) | **Open — partial** |
| `PRIOR-AUDIT/M7` | *"Partially remediated: … Formal release ownership remains a human adoption decision."* (`:17`) | **Open — partial** |
| `PRIOR-AUDIT/O4` | *"Clarified: …"* — clarified, not remediated (`:21`) | **Open — clarified only** |

They keep their original codes and are not renumbered. The re-audit that would close them remains
outstanding (`audit/VALIDATION_RESULTS.md:59-60`), and
`audit/CHATGPT_ENTERPRISE_AUDIT_PROMPT.md:94` still asks a future auditor to disposition all fifteen.

### Uncoded historical items

Recorded so they are not lost, without retrospective codes — assigning numbers to items nobody has
ever cited would manufacture citations for no benefit:

- `org/decisions/DR-8.md:87-95` — the `SDS036` incidental: a finding code cited in a deleted document
  and emitted by nothing. No action followed; the citation went with the file.
- `org/decisions/DR-5.md:100-143` — *"Unassigned — not yet a numbered finding"*: raised, investigated,
  and **withdrawn** (`:113-114`), with the residual question answered at `0.13.0` in an annotation
  left in place rather than rewritten. Not a finding; recorded as raised-and-withdrawn.
- `audit/PRIOR_AUDIT_REMEDIATION.md:27-32` and `:38-44` — fourteen remediation bullets across two
  batches, never individually coded by the audits that produced them.

---

## Observations — not findings

- **A bare `python3` can carry package versions older than this project's own pins, with no error
  until something is actually run against them.** Discovered while building `ACT-020`
  (`org/decisions/DR-32.md`): the machine used had no `pip` at all, and apt-installed
  `jsonschema==4.10.3`/`PyYAML==6.0.1` — both older than `4.26.0`/`6.0.3`. This is not `F21` again —
  the pin is correctly declared, and every workflow correctly installs it — it is the same class of
  divergence one layer closer to the developer, on a machine nothing in CI ever touches. Not a
  finding, because nothing in the framework failed: a repository-local `.venv`, built once with the
  pinned versions, is the ordinary remedy and is what every verification command in `DR-32` used
  once this was noticed. Recorded so the next session on a fresh machine checks rather than assumes.
- **`ACT-<n>` identifiers have no register.** `ACT-200` and `ACT-201` appear in commit subjects and
  in **no tracked file**. The activity register that would give them meaning is unlanded work
  (`org/RELEASE_PLAN.md`, item 0; `DR-13`). This is the `SDS036` shape — an identifier cited before
  the thing it names exists — and is recorded here as an observation rather than a finding, because
  the register it points at is already scheduled.

## Limitations of this register

- **The external review's own output was not available to the session that built this register.**
  `F6`–`F9` are recorded from the claims named in the work packet and verified independently against
  the code. The review raised seven items; four are represented here. **Anything it raised beyond
  those is not in this register**, and this file does not claim otherwise.
- **The review did not report what it tried and failed to break.** A review that reports only its
  hits gives no basis for judging coverage: a reader cannot distinguish "these are the weaknesses"
  from "these are the weaknesses that happened to be found". Recorded as a limitation of the review,
  not as a finding about the code.
- **No finding here has been independently confirmed.** Every entry was verified against the source
  by the same party that maintains it. `org/decisions/README.md:16-18` applies: no independent
  validator exists for this repository.
- **Severity is a judgement, not a measurement.** Each entry states its reasoning so the judgement
  can be disagreed with.
