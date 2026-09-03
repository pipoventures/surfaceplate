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
emitted:  SP001-SP035, SP037-SP043, SP046-SP059
gap:      SP036
reserved: SP044-SP045
```

`SP036` is a deliberate gap (`DR-8`). `SP044` and `SP045` are reserved by `DR-11.md:49` and are
emitted by nothing until a generator exists; the check asserts they stay unemitted, so a
reservation cannot quietly become a code in use. It also asserts the space has no **undeclared**
hole — the defect `DR-8` originally found, where `SDS036` sat documented-but-unimplemented across
an unknown number of releases with nothing noticing.

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
| F55 | Narrative docstrings can drift from the code beneath them, and twice did | low | Open — recorded as a habit rather than remedied by deletion |
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

**Severity: low. Open.**

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
not mechanically enforceable, which is why this stays open rather than closing with a test.

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

**Not remedied here, deliberately.** The candidates all touch a published control's semantics and
none is obviously right: making the audit compare commit *timestamps* rather than dates; treating
the commit that introduces an artefact as the boundary; or letting `effective_from` carry a time.
`DR-43` records them. Choosing between them is a change to `SP033`/`SP035` and belongs in its own
packet with its own decision, not as a side effect of adding scaffolding.

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
