# Adversarial product review — `surfaceplate adopt` and its front door

**Date:** 2026-09-02. **Reviewed:** `main` at `178ba2c`, version 0.16.0, textual 8.2.8, Python 3.12.3.
**Reviewer:** Claude (Fable 5.1), driving the real `AdoptApp` under `run_test` against a copy of
Plutos and against a bare one-file repository. **Written to:** an uncommitted working branch; the
maintainer decides whether it is committed and under which activity.

**Evidence conventions.** `FACT` was verified here, in this repository's code or in an image I
looked at. `INFERENCE` is reasoned, not observed. `RECOMMENDATION` is a proposed treatment.
`EVIDENCE GAP` is something I could not establish. Every interface claim cites a PNG under
`SHOTS = /tmp/claude-1000/-home-mps2210-github-surfaceplate/a1a25dce-2569-414f-ab0e-f52e6d7bed75/scratchpad`
that I read in this session; nothing below describes a screen from its source. Commands are
quoted with their result as `PASS`, `FAIL - CODE`, `FAIL - ENVIRONMENT/DEPENDENCY` or `NOT RUN`.
Nothing under `.standards/`, `.claude/` or `.github/instructions/` was touched; no test or golden
was changed; `/home/mps2210/github/plutos` was never written to (its `git status` and its draft
file were byte-compared before and after: unchanged).

---

## 1. Verdict

**Not fit to put in front of a stranger.** The single strongest reason: **on the route the
maintainer actually chose (standard level, "Set defaults"), the wizard cannot be finished as
built.** The proposals screen says "5 more can only be answered by you, and are asked next", the
gates screen that follows is blank because the proposals for it are thrown away, and the status
radio that every one of the fifteen undecided gates needs is drawn as an empty box at every
terminal size I tried. A stranger reaches screen 7 of 9, sees nineteen gates with no way to
answer them, and leaves. `FACT`, images `std-def-15`, `std-def-35`, `std-def-38` at 80×24 and
`std-def-38` at 120×40.

Close behind it, and worse in kind: a completed profile whose prose mentions "replace-me"
anywhere is mistaken for the untouched template and overwritten without a prompt (section 7,
item 1). That one has not happened to anyone yet; it is the only finding here that destroys
work rather than blocking it.

Two things are worth saying before the list. First, the project's own honesty is real: the
refusal messages, the dry-run, the "DECLARED ONLY" stamps and the README's status section are
better than most governance tooling, and every finding below was easier to make because the
project writes down what it was trying to do. Second, the green suites are not lying; they are
measuring the wrong thing. Twelve suites, 810 checks, all `PASS` (section 6), and the product
still stops a real user at screen 7, because no suite renders a gate's status row, seeds a screen
on the defaults route, or counts what a persona has to type.

---

## 2. Findings, ranked by damage to a real adopter

Ranking is by how much each costs an adopter who is trying to finish, not by how hard it is to
fix. Several are one-line fixes; that does not lower them.

### F-A. Every undecided gate's status radio is invisible `FACT`

**What I did.** Drove standard/defaults on the Plutos copy at 80×24, 100×30 and 120×40; focused
the first non-mandatory gate (`work_contract`); chose `required` with the keyboard, then
`not_applicable`; screenshot after each.
**What I saw.** `SHOTS/shots/std-def-37-gates-focus-work_contract-80x24.png`,
`std-def-38-gates-work_contract-required-80x24.png`,
`std-def-38-gates-work_contract-required-120x40.png`: the status row is a blue-bordered empty
box. No `( ) required ( ) deferred ( ) not applicable` is drawn at any size. The selection
*works* (the follow-up "Why this status" row appears after choosing, `std-def-39`), but nothing
tells the adopter that there is a choice, what the options are, or which one is chosen.
**Why.** `surfaceplate/adopt/tui/app.tcss:185-188` forces `.chip-row { height: 1 }`. Textual's
`RadioSet` default stylesheet draws `border: tall` (one row above, one below) plus padding, so a
one-row widget has no row left for its buttons. `tests/test_adopt_tui.py:188-201` sets
`.value = True` on the buttons and reads `.value` back; nothing renders the row. This is the class
`F37` and `F41` already recorded: structurally verified, never looked at.
**Timing.** `INFERENCE`: the radio-chip rewrite landed at 17:01 on 2026-09-01 (`96a2efe`,
ACT-031). The maintainer's first-attempt profile is timestamped 16:37 that day; today's draft
(09:43) stops before the gates section. He has not got past the gates screen since the chips
became invisible, which is consistent with "extremely complicated" being, in part, "I cannot
see the control I am supposed to use".
**Remedy.** Drop the fixed height (`height: auto`) or add `compact` to the `RadioSet`; add a
rendered-line assertion for one chip row to `tests/test_render.py`, in the style it already uses
for the checkbox.

### F-B. The defaults route discards its own gate proposals and mis-states what is left `FACT`

**What I did.** Standard/defaults on the Plutos copy. Read the proposals screen, accepted it,
read the gates screen, pressed `Ctrl+S` with nothing changed.
**What I saw.** `std-def-15-defaults-open-80x24.png`: "59 values proposed: 23 computed, 17
discovered, 19 example. **5 more** can only be answered by you, and are asked next." The list
includes `gates.work_registration.artefact = activity/register.md`, `.paths = src/**`,
`.effective_from = 2026-09-02` and thirty-four other gate proposals.
`std-def-35-gates-open-80x24.png`: the gates screen opens with "4 of 19 answered" (the four
auto-settled design gates) and `work_registration` blank.
`std-def-36-gates-ctrl-s-nothing-80x24.png`: "work_registration · Gated paths: This cannot be
blank." With a user interface declared (`std-def-ui-35-gates-open-80x24.png`) it opens at
"0 of 19 answered". The controls screen *is* seeded (`std-def-21`), so the adopter has just seen
seeding work and now sees it silently stop.
**Why.** `tui/app.py:228-231` passes `initial=self._seeded.get(name, {})` only in the
`FormScreen` branch; `GatesScreen(specs, section, step=step)` at `:227` takes no `initial`, and
`screens.py:712` has no parameter for one. The "N more" count in `defaults.unanswered` counts
fields with no proposal, so it is 5 at every level (`ess-def-15`, `full-def-15` both say 5)
while the gates section then re-asks 38 fields at standard and 53 at full with a UI (my
re-measure, section 5). No test asserts that any screen is seeded (`grep -n 'seeded\|initial=' tests/`
finds nothing).
**Remedy.** Give `GatesScreen` an `initial` and pass it; make "N more" count fields that will
actually be presented unfilled; add one Pilot test that accepts defaults and asserts the gates
screen's first artefact widget holds the proposal.

### F-C. Discovery proposes Surfaceplate's own installed files as the adopter's controls, and the checker will pass them `FACT`

**What I did.** Ran `defaults.propose()` and `discover.scan()` against the Plutos copy with the
maintainer's answers; read the rendered profile from the standard/defaults run; ran the wizard
on a bare repository that had nothing in it but `main.py` and a fresh install.
**What I saw.**
- Proposals (verbatim from `defaults.propose`): `[discovered] gates.authority_map.artefact =
  '.github/instructions/authority.instructions.md' -- the closest match in this repository for
  this gate`; `[discovered] gates.change_record_before_completion.artefact =
  '.github/skills/change/SKILL.md'`; `[discovered] controls.contract_tests.implementation_reference
  = 'Check conformance to Surfaceplate'`; same for `deterministic_tests`. `found.register_dirs`
  includes `.standards/examples`, `.standards/schemas`, `.standards/templates`.
- The maintainer's own draft from this morning carries `contract_tests.implementation_reference:
  "Check conformance to Surfaceplate"` — so this reached him, not only me.
- On the bare repository: `SHOTS/shots-stranger/scaffold-12-level-open-80x24.png` says "You
  appear to have: a CI workflow (.github/workflows/standards-conformance.yml)". That workflow
  was installed by `surfaceplate install` sixty seconds earlier.
**Why it matters.** A gate whose precondition artefact is a file the framework installed is
satisfied the moment the framework is installed; `SP032` checks that the file exists, and it
does. A `contract_tests` control whose CI step is the conformance check itself is verified by
`SP053` against a step that runs the checker, not the adopter's tests. This is `F40`'s shape
("a gate that passes while guarding nothing") with the framework's own footprint as the false
green. `discover.py:97-100` says framework-owned paths "are still offered - but never ahead of
the adopter's own documents"; `matched_for_gate` (`:185-203`) sorts by keyword score and
ignores that ranking, so `authority.instructions.md` wins `authority_map` on the word
"authority". That is `F55`'s class: a comment wrong about the code beneath it.
**Remedy.** Exclude `_FRAMEWORK_OWNED` and the installed workflow from every candidate list
(artefacts, register dirs, CI steps, "you appear to have"), not merely rank them last; add a
negative test in `tests/test_discover.py` that a repository containing only the install payload
yields no proposals.

### F-D. The written profile asserts a provenance it does not have `FACT`

**What I did.** Read the header the renderer writes (`surfaceplate/adopt/render.py:205-206`) and
the profile the standard/defaults run produced; read the maintainer's first-attempt profile.
**What I saw.** Every profile begins: *"Every value below was typed by a human answering a
question; nothing here was inferred, defaulted silently, or chosen by the wizard."*
(`std-def-46-review-open-80x24.png`, and the file). Under it, on the defaults route: five
rationales that are the framework's worked examples verbatim ("The API is consumed by a
separate frontend and would break silently." — Plutos has no separate frontend); `review_by`
computed; `effective_from` pre-filled; `framework_maintainer` copied from `owner`; every gate's
two `description` fields and its `enforcement` list derived. The maintainer's real first
attempt has the same header above `asdf` in seven gates, `repository_classification: Gool` and
`release_route: lovvely`.
**Why it matters.** This is the centre of the question-count argument (section 3). The rule
"it asks, the human answers, the tool writes" was enforced by adding text boxes, and the result
is a document that claims more human authorship than it has, sitting on top of values a human
typed only to escape. Provenance honesty was not purchased by the extra questions; it was
spent. The `DefaultsScreen` already knows each value's origin (`[disc]`, `[exam]`, `[comp]`);
the profile throws that away and writes a false sentence instead.
**Remedy.** Replace the header with a true one and carry origin per value (a trailing comment
per line is enough: `# example, accepted 2026-09-02`, `# discovered`, `# typed`). That is the
`F53` remedy applied to values instead of controls, and it makes the defaults route *more*
honest than the answer-everything route rather than less.

### F-E. Committing an empty choice ends in a black screen `FACT`

**What I did.** Pressed `Ctrl+S` on the first screen without choosing; continued through
identity, stack and risk; pressed `Ctrl+S` on risk with no data classification chosen.
**What I saw.** `nochoice-02-mode-ctrl-s-nothing-chosen-80x24.png`: the wizard advanced to
Identity with `mode: None`. `nochoice-11-after-risk-nochoice-80x24.png`: the entire terminal is
black. Under `run_test` the worker reports `WorkerFailed: KeyError(None)`; in a real terminal
the app dies inside its `@work` worker and the `cli.py:88-100` message never prints.
**Why.** `validators.check` returns `None` for any non-string (`validators.py:111-112`), so a
`RadioSet` with nothing pressed passes validation; `plan.py:998` then looks up
`LEVEL_CHOICE[None]`. Same shape for `route`, `data_classification`, `adoption_status`.
**Remedy.** Validate `choice` fields as "must be one of the choices"; the screen already has the
hint line to say so.

### F-F. A placeholder typed on screen 6 is refused on screen 9, and the draft then traps you `FACT`

**What I did.** Typed `TBD` into the first rationale; continued to the review; then resumed a
draft holding that state.
**What I saw.** The controls screen accepted `TBD` (`validators.check("nonempty","TBD") -> None`).
`bad-42-review-open-80x24.png`: the review shows "This cannot be written yet: an answer still
contains a template placeholder token … at: baseline_controls.agent_work_packets.rationale", an
empty profile pane, and a hint line that still reads "[Ctrl+S] write it". `Ctrl+S`, `Tab`,
`Escape`, `Backspace` do nothing (deadlock.py output). `Ctrl+Q` returns `None`, which the CLI
reports as cancelled with the draft kept. On the next run the draft is offered; resuming skips
every completed section (`tui/app.py:203-204`) and lands on the same review with the same
error (`shots-bad2/deadlock-01-resume-lands-on-review-80x24.png`). The only exits are "n" at the
resume prompt (discarding everything) or hand-editing the JSON.
**Remedy.** Run the placeholder scan per field at commit time (the pattern is already imported
in `wizard.py`); on the review, give a key that returns to the offending section; hide
"[Ctrl+S] write it" when there is an error.

### F-G. The wizard's validators disagree with the checker, so a profile can pass the wizard and fail its first check `FACT`

**What I did.** Probed `validators.check` directly; typed a review date 401 days out during a
run; ran the checker over a valid profile with that date.
**What I saw.**
```
effective_from tomorrow   -> None     (accepted; SP033 rejects a future date)
effective_from +1 year    -> None
review_by 401 days        -> None     (accepted; SP026 rejects beyond 400)
review_by yesterday       -> None     (accepted; SP024 rejects overdue)
nonempty 'asdf' / 'TBD'   -> None
```
The 401-day date went through the adoption screen and the review (`shots-bad2/bad-80x24-state.json`).
`surfaceplate check` on the resulting profile: `[SP026] The profile review date is beyond the
permitted horizon` → `FAIL`. Neither `scanner.wired_in` nor `implementation_reference` is
checked for existence when typed by hand (`SP046`/`SP051` fire on the first check instead).
**Remedy.** Import the three date rules from `check_conformance` into `validators`; check
typed paths exist against the repository at commit time, with the same "create it?" offer the
scaffold screen already has.

### F-H. At 80×24 the level screen hides the choice it exists to make `FACT`

**What I did.** Opened the level screen at 80×24, pressed `?`, and at 100×30.
**What I saw.** `std-def-11-level-open-80x24.png`: recap, recommendation and "you appear to
have" fill the frame; only "1 essential" and half its blurb are visible; the caret sits on
"standard", below the fold, and the recommendation the screen is announcing is not on screen.
`std-def-12-level-why-80x24.png` is pixel-identical to `-11`: the "why" text is also below
the fold, so `?` appears to do nothing. `std-def-11-level-open-100x30.png` shows all three.
Same screen also says "You told us: Input data from APIs and calculations" — the materiality
answer with no label and no risk profile, which reads as nonsense.
**Remedy.** Put the option list before the prose or cap the prose; scroll the highlighted
option into view on mount; label the recap lines.

### F-I. Help text is louder than the field it explains and touches the next field (complaint 2) `FACT`

**What I saw.** `std-def-03-identity-open-80x24.png` and `-120x40.png`: the help line under
`application_id` is full-brightness white, brighter than the grey label, starts at the frame's
left edge, and `display_name` begins on the very next row with no gap; the amber focus rule on
the row does not extend to its help. `std-def-21-controls-open-80x24.png`: the help for a
rationale is a six-line paragraph that runs to the bottom of the frame and is cut mid-sentence.
`std-def-42-adoption-open-80x24.png`, `-44-wrap-open`: same. Identical at 120×40, so this is
styling, not width.
**Why.** `.field-help` has no rule in `app.tcss`; it renders as a bare `Static` (default
colour, zero margin) and is a sibling of `.field-row` (`screens.py:444-457`), so the row's
focus styling cannot reach it.
**Remedy.** `.field-help { color: #7a827e; margin: 0 0 1 2; }` or render it inside the row.

### F-J. Unticked boxes and unselected radios are near-invisible (complaint 3) `FACT`

**What I saw.** `std-def-07-risk-open-80x24.png`: the two boxes beside "Does anyone outside your
team rely on what this produces?" and "Does it produce numbers or AI output that others treat
as fact?" are dark brackets around a darker block on a black ground; `std-def-05-stack-open`
and `std-def-42-adoption-filled` (Level 3 box) are the same. Once ticked, `[X]` is green and
clear (`std-def-09`). The mode and route radios (`std-def-01`, `std-def-14`) show the same
dark rings, and the first option is highlighted in bold blue although nothing is chosen, which
reads as a selection. The maintainer's "(anyone relying on AI output)" is a paraphrase of these
two lines; the string itself is not in the source.
**Remedy.** Give `.toggle--button` an off-state colour with contrast; do not highlight an
unpressed first radio.

### F-K. 80×24 clipping and truncation elsewhere `FACT`

- Data classification shows two of its four options (`std-def-07`); the adopter must know to
  scroll inside a radio set.
- Mode options end in "…" (`std-def-01`: "standard - explain in plain English, assumin…"), as
  do all five `above_floor` rows (`std-def-27`), so neither choice can be read in full.
- Rationale text areas are two rows high and show one line of the value ("Supply-chain
  exposure exists regardless of" — `std-def-31`).
- The gate list scrolls to a fragment ("merged", with …) as its first visible line
  (`std-def-40`).
- The review shows nine lines of a 130-line profile per page (`std-def-46`).

### F-L. Quitting at the resume prompt deletes the draft `FACT`

`resume.py`: `Ctrl+Q` (and closing the terminal) makes `ConfirmResumeApp.run()` return `None`;
`TextualInterview.confirm_resume` returns `bool(None)`; `_resume_or_start` treats that as "n"
and calls `_clear_draft` (`wizard.py:244-246`). Verified against the real function: the draft
file existed before and did not after. The prompt's own heading is also missing
(`shots/resume-open-80x24.png`): `"[A saved draft was found]"` is consumed as markup because that
`Static` lacks `markup=False`, the `F37 #1` defect on a screen it did not reach.

### F-M. The route screen and the gates screen disagree about the job `FACT`

`std-def-14-route-open-80x24.png`: "At standard the rest of this profile is 4 gate(s) and 4
control(s)." Two screens later (`std-def-35`): "All 19 gates must be decided one way or the
other at standard." The route text counts level-mandatory gates only (`plan.py:162-199`).

### F-N. The front door: two incompatible install paths, stale version, dead links, an undocumented refusal `FACT`

Run as a stranger in a fresh venv (`SHOTS/logs/stranger-install.log`, `-2.log`):

| Instruction | Result |
|---|---|
| `pip install 'git+https://github.com/pipoventures/surfaceplate@main'` | PASS (pip 24.0) |
| `surfaceplate` / `--help` / `--version` | all print the same two-line usage to stderr, exit 2; there is no help or version |
| `surfaceplate install --target target --dry-run` | **exit 4, "STOPPED - Git hooks for this repository already run from somewhere else"** because this machine sets `core.hooksPath` globally. The message is excellent; the README never mentions the case, and the first command a stranger runs on such a machine fails |
| `surfaceplate install --target target --no-hooks` | PASS |
| `surfaceplate check --repo target` | WARN, 13 findings, all from the untouched template |
| `pip install 'git+…#egg=surfaceplate[adopt]'` | PASS on pip 24.0 (`EVIDENCE GAP`: not tested on pip 26, which the maintainer's venv carries) |
| `surfaceplate adopt --target target </dev/null` | exit 2 with a clear TTY refusal; there is no non-interactive route at all |
| README:29 and :166 links to `core/` | `ls: cannot access 'core': No such file or directory` |
| README:216 "Version 0.13.0" | `surfaceplate/VERSION`, `pyproject.toml`, `.standards/VERSION` all say 0.16.0 |
| INSTALL.md:57 `python -m pip install pyyaml jsonschema` | `FAIL - ENVIRONMENT/DEPENDENCY`: `/usr/bin/python3: No module named pip` on this Ubuntu |
| INSTALL.md:128 "hand the repository to `prompts/copilot-implementation-assistant.prompt.md`" | that file is not in the install payload; it does not exist in an adopting repository |

INSTALL.md never mentions `surfaceplate install` or `surfaceplate check` while asserting their
dependency footprint (`:127`); README front-doors the console script; `SETUP_GUIDE.md` calls
itself "the exact adoption sequence" (`:3`), is linked from neither, is not installed, and tells
the reader to put the profile at `config/governance/` (`:65`) where the checker will never look
(`install_standard.py:45`).

### F-O. The standard's documents contradict themselves on the questions an adopter must answer `FACT`

Verified by reading the lines named:
- `CONFORMANCE_LEVELS.md:68` "Ten of the twelve controls this framework defines are checked"
  versus `:155` "Every control is checked" — in one file, with an apology at `:72-76` for having
  made this mistake before.
- `CONFORMANCE_LEVELS.md:33,70` cite "principle 9" for the limit on what a tool may claim;
  `CONTROL_PRINCIPLES.md:11` principle 9 is change control; principle 11 is the one meant.
  Principle 12 refers to a "B1 risk" defined nowhere.
- `PREREQUISITE_GATES.md:30-32` states "GitHub Actions is disabled at organisation level, so no
  server-side check runs at all"; README:7-8 and :144-145 demonstrate the opposite for this
  repository.
- README:72 "all 19 prerequisite gates" is false at `essential`, where the wizard's own intro
  says only `work_registration` is asked (`scaffold-30-gates-open-80x24.png`).
- Two normative evidence-label vocabularies (`REVIEW_AND_EVIDENCE.md:30-36` `FACT FROM PACKAGE`
  / `FACT FROM RECEIVING REPOSITORY`; `ai-workflow.md:61-66` `FACT`), both installed.
- The checker emits 55 `SP` codes; the only catalogue an adopter is pointed at documents 20.
  `SP038` is used in INSTALL.md:35 and catalogued nowhere.
Reading volume before an adopter can act: about 17,000 words at `essential`, with 63 defined
terms, fourteen of them used before they are defined (cold-read report, section 7).

### F-P. The findings index and its guard disagree; the digest anchor is a known, open limit `FACT`

- `org/FINDINGS.md`: index says Closed, body says Open for F7, F8, F9, F10, F11, F12, F13, F14,
  F16, F30 (`grep -nE '^\*\*Severity:.*Open'` versus the index rows). F12 says both inside one
  section (`:541` and `:577`). `tests/check_code_registers.py` checks uniqueness and index/body
  presence, never status.
- Digest anchor, **corrected after the second pass**: `SP049` does recompute
  `sha256(.standards/MANIFEST.sha256)` and compare it with the install record and the profile.
  The vendored manifest cannot equal the source manifest's hash by construction, because the
  source manifest hashes the profile that carries the vendored digest; `DR-45` records this and
  says the comparison that matters is against the published manifest, which is `F6`, open, and
  a human action. The first version of this finding said "nothing compares the anchor to what it
  anchors"; that was wrong at the level `SP049` covers and is withdrawn.

### F-Q. `Ctrl+Q` cancel handlers are dead code `FACT`, minor

Textual's own priority `quit` binding fires first; every `action_cancel` is unreachable from
the keyboard. Net effect is still a cancel (`deadlock.py`: `return_value None` on a form), so
this costs nothing today except that "keeping your draft" on the review hint is true only by
accident of the CLI's exception handling.


### F-R. A validation error is erased by the focus move that reports it `FACT`

**What I did.** On the real identity screen, left `application_id` blank, focused `owner`,
pressed `Ctrl+S`.
**What I saw.** `SHOTS/vanish/identity-after-ctrl-s-from-owner-80x24.png`: focus moved to the
blank field, the screen was not dismissed, and the hint shows only the key legend; the error
"application_id: This cannot be blank." never stays on screen. The audit's earlier image of that
error (`bad-04`) was taken with focus already on the failing field, the one case where it
survives.
**Why.** `FormScreen.action_commit` writes the error into the hint and then focuses the field;
`on_descendant_focus` calls `_set_hint()` with no error and overwrites it (`screens.py`,
`_set_hint` and `on_descendant_focus`). Found while driving the prototype in Part II.
**Remedy.** Focus first, then set the hint; or carry the error in screen state until the next
commit.

---

## 3. The question count: a direct answer

**The dichotomy is not real.** It was manufactured by implementing "it asks" as "one widget per
field" and "the human answers" as "a keystroke per widget". The binding rule
(`org/RELEASE_PLAN.md:99-130`) requires that a level, a rationale and a scope decision be
*elicited and approved*, not that each be typed into its own box. The `DefaultsScreen` already
shows proposals with their origin and asks for approval; that *is* asking. What breaks the
rule today is not the count but two other things: the proposals for the largest section are
discarded (F-B), and the written profile lies about where its values came from (F-D). Fix
those two, and the wizard can ask far less while being more honest than it is now.

**Measured today** (re-measured in this session from the live plan, Plutos copy; the register's
57 at `ACT-032` is now 32):

| Persona | Fields presented | of which gate fields | of which free text in gates |
|---|---|---|---|
| essential | 32 | 3 | 2 |
| standard, no UI | 72 | 38 | 23 |
| standard, UI | 80 | 46 | 27 |
| full, UI | 96 | 53 | 34 |
| standard, every optional gate `required` | 94 | 60 | 34 |

The defaults route presents the same number; it pre-fills the first 11 sections and nothing
after (F-B).

**What it should ask.** The test I applied to every field: (1) does the checker read it, (2)
can the tool supply it as a fact of record, install-record value, or the framework's own prose
(the three things the rule permits), (3) is it a level, a rationale or a scope decision (the
three things the rule forbids the tool to write unasked). Fields that fail (1) and (3) are
dropped; fields that pass (2) are written with an origin tag and shown once for approval;
only fields that are (3) are asked as questions, and even those start from a proposal.

Essential, today 32 → **11 human answers**:

| Field | Today | Proposed | Provenance cost |
|---|---|---|---|
| `mode` | choice | drop; make it a CLI flag or `?` toggle | none, it is about the wizard |
| `application_id` | text | ask, proposed from the directory name | none |
| `display_name` | text | derive from id, editable at review | none (never read) |
| `owner` | text | ask | none |
| `language` | text, detected | write as `discovered`, approve at review | none |
| `builds_user_interface` | bool | ask (scope) | none |
| `risk_profile`, `materiality_definition` | two text areas | one optional text area, "in your own words"; never read by any check | none |
| `relied_on_outside_team`, `material_quantitative_output` | 2 bools | ask; they drive the level | none, they are the questionnaire |
| `data_classification` | choice | ask | none |
| `conformance_level` | choice | ask, caret on recommendation; keep | none, `CONFORMANCE_LEVELS.md:222` forbids deriving it |
| `route` | choice | drop; defaults are always proposed, `c` on the proposals screen is the customise route | none |
| three baseline rationales | 3 text areas | write the framework's example with `# example` tag; editable at review | **this is where honesty is bought**: today the same text is written under a header saying a human typed it |
| `scanner.name`, `scanner.wired_in` | text + select | discover; ask only if nothing found | none |
| `above_floor` | multiselect | keep but collapse to one line "declare more? [n]" | none |
| `dependency_lock.rationale`, `.implementation_reference` | text area + select | example + discovered; approve | as above |
| `work_registration.artefact` | select/text | proposed if matched, else scaffold offer; approve | none, the human approves the path |
| `work_registration.effective_from` | text pre-filled today | write the adoption date as a fact of record, tag `# adoption date`; ask only if the adopter wants to widen it | **DR-46 chose to ask this**; a value the human sees and approves at the review satisfies "asked"; what must not happen is a silent fallback, and there is none since `F51` |
| `work_registration.paths` | text | proposed `src/**`; approve | scope decision, approved not typed |
| `review_by` | text pre-filled | fact of record (adoption + 180); approve | none |
| `framework_maintainer` | text pre-filled | fact of record (= owner); approve | none |
| `repository_classification` | text | drop from the wizard; never read by the checker; keep in schema as optional | none |
| `decision_record_id` | text | ask only if a decisions directory exists; else scaffold `DR-1` and write that | the rule allows a fact about an artefact the tool created |
| `adoption_status` | choice | write `in_progress` as a fact of record at adoption time | none |
| `needs_validator`, `independent_validator` | bool + text | ask only at `full` | none |
| `human_roles` | text area, optional | drop at essential | none |
| `release_route` | text area | ask | none, it is a scope decision |

The eleven that remain as questions: `application_id`, `owner`, `builds_user_interface`, the two
risk booleans, `data_classification`, `conformance_level`, `work_registration` artefact
(pick or scaffold), `paths` (approve), `release_route`, and one optional free-text "risk in your
own words". Everything else is written with an origin and approved once at the review.

Standard and full follow the same rule, and the gates section is where it pays: nineteen
statuses become one list, pre-marked `required` for what the level mandates and
`not_applicable` for the rest with the framework's example rationale tagged `# example`, and
the adopter ticks the ones that differ. That is what `defaults.propose` already computes and
what the binding rule already permits on the defaults route. The three free-text fields per
required gate (artefact, paths, effective date) stay proposal-plus-approve. My estimate for
standard with a UI is **11 questions plus one gate list**, against 80 fields today.
`INFERENCE`: the maintainer's "the package must make decisions for the user" and the
project's "the human decides" are the same design once "decide" means "approve a shown
proposal", which is what he did on the defaults screen and what the tool then threw away.

**What each removal costs in provenance honesty.** Nothing, provided the header changes (F-D)
and each written value carries its origin. The only field where DR-46's argument still bites
is `effective_from`, because a narrower date silently chosen shrinks the audit window; the
remedy is to show it and let the adopter widen it, not to make them retype today's date once
per gate. Where a repository has no decisions directory the tool creates one and records the
id it created, which the rule already classes as a fact of record.

---

## 4. What I could not assess `EVIDENCE GAP`

- **A real terminal.** Everything was driven under Textual's `run_test`; colours, key
  handling and the black-screen crash may differ in a real emulator. The maintainer's terminal
  size is unknown; 80×24 was tested as the floor.
- **Mouse interaction.** `OneClickSelect` and the radio sets were driven by keyboard only.
- **pip 26.** The `#egg=` extra was tested on the fresh venv's pip 24.0 only.
- **A non-Python repository, a non-git tree, thousands of files.** Delegated to the code review
  (section 7) and reported there as far as it got.
- **Whether the maintainer hit F-A.** Timestamps are consistent with it; nobody told me.
- **The external claims in the documents** (GitHub ruleset behaviour, organisation-level
  Actions settings). Read, not exercised.

---

## 5. Commands run and results

Suites, in CI order, from `.venv/bin/python` (`SHOTS/logs/suite-*.log`):

| Command | Result |
|---|---|
| `python tests/validate_contracts.py` | PASS, `CONTRACT_CONFORMANCE=PASS (180 checks)` |
| `python tests/test_install_and_check.py` | PASS, `INSTALL_CONFORMANCE=PASS (195 checks)` |
| `python tests/test_adopt.py` | PASS, `ADOPT_CONFORMANCE=PASS (88 checks)` |
| `python tests/test_provenance.py` | PASS, `PROVENANCE=PASS (6 checks)` |
| `python tests/test_adopt_tui.py` | PASS, `ADOPT_TUI=PASS (44 checks)` |
| `python tests/test_render.py` | PASS, `RENDER=PASS (20 checks)` |
| `python tests/test_discover.py` | PASS, `DISCOVER=PASS (18 checks)` |
| `python tests/test_scaffold.py` | PASS, `SCAFFOLD=PASS (21 checks)` |
| `python tests/check_audit_packet.py` | PASS, `AUDIT_PACKET=PASS (5 checks; 15 files in the bundle)` |
| `python scripts/build_release.py --verify-manifest` | PASS, `MANIFEST_CURRENT=PASS (172 files)` |
| `python tests/check_identifiers.py` | PASS, `IDENTIFIER_CONFORMANCE=PASS (203 checks)` |
| `python tests/check_code_registers.py` | PASS, `CODE_REGISTERS=PASS (10 checks; 55 SP codes, 58 F codes)` |
| `python tests/check_vendored_current.py` | PASS, `VENDORED_CURRENT=PASS (64 files compared, 1 checked by SP049 instead)` |
| `python surfaceplate/check_conformance.py --repo .` | PASS, `PASS - all conformance checks satisfied.` |

**What these suites are structurally unable to see** (all of section 2 passed them): a widget
that is present in the DOM and zero rows tall (F-A); a screen that is constructed without the
argument that seeds it (F-B); a proposal that names the framework's own file (F-C: the
discover tests use synthetic trees with no install payload); a header sentence (F-D); a
validator that returns `None` for `None` (F-E); a validation rule the checker has and the
wizard lacks (F-G); geometry at 80×24 (F-H, F-K: the TUI suite runs at 120×60 and 100×40,
`run_test`'s default 80×24 is never used); colour contrast (F-J); a status column in a
markdown table (F-P); and, above all, how many things a person has to type.

Harness: `SHOTS/shot.py` (routes: ess-cust, ess-def, std-cust, std-def, std-def-ui, full-cust,
full-def, scaffold, cancel, bad, nochoice; sizes 80×24, 100×30, 120×40), `resume.py`,
`deadlock.py`. 569 PNGs under `SHOTS/shots`, 93 under `shots-stranger`, `shots-scaffold`,
`shots-bad2`. Rendered profiles: `SHOTS/shots/<route>-rendered-profile.yaml`.

---

## 6. Register entries

*Recorded on 2026-09-02 under `ACT-042`, after the maintainer authorised them in the review
session: findings `F59` to `F77`, decision records `DR-47` to `DR-50`, activities `ACT-042` to
`ACT-046`, and human actions `H9` and `H10`. The plan that carries them is
`org/REMEDIATION_PLAN.md`. The paragraph below is the proposal as it stood before that.*

- A finding for F-A (high), F-B (high), F-C (high), F-D (high), F-E (medium), F-F (medium),
  F-G (medium), F-H/I/J/K (medium, one finding: "the 80×24 pass looked at the wrong screens"),
  F-L (low), F-M (low), F-N (medium), F-O (medium), F-P (low), F-Q (low).
- An activity to act on this review, with the decision on section 3 recorded as a decision
  record amending `DR-46`'s reading of "asked".
- A human action: run `adopt` again on Plutos only after F-A and F-B are fixed; the current
  build cannot be finished on the route he uses.

---

## 7. Code-correctness review

A delegated read-only pass over `surfaceplate/adopt/` and `cli.py`, probing with throwaway
repositories under the scratchpad (`SHOTS/probe/`). I re-ran the four most consequential probes
myself before including them (`SHOTS/verify/`); those four are `FACT`. The rest are reported as
the pass found them and are marked `INFERENCE` where I did not repeat the probe.

Ranked by damage:

1. **A real profile that mentions "replace-me" anywhere is treated as the untouched template
   and overwritten** `FACT`. `wizard.py:119-128` tests `"replace-me" in text` over the whole
   file. A rationale saying "never type replace-me here" disarms the guard and `wizard.run`
   writes over the adopter's profile with no prompt. Critical; unrecoverable. Remedy: compare
   against the shipped template's digest, or require the token in a structural position.
2. **A blank dropdown passes every validator** `FACT`. `validators.check` returns `None` for any
   non-string (`validators.py:111-113`); `_read_widget` returns `None` for an untouched `Select`.
   On the gates screen the artefact dropdown left blank counts as answered ("1 of 1 answered"),
   commits, and the review then shows `This cannot be written yet: 'artefact'`, a `KeyError`
   from `sections.py:164`, with no way back. Same hole for `scanner.wired_in` and every
   `implementation_reference` select. This is distinct from F-E (radio sets).
3. **Candidates are capped at 200 before any gate ranking** `FACT`. `discover._capped`
   (`:94`) cuts the artefact list before `matched_for_gate` runs; with 300 files under `docs/`
   the repository's real `activity/register.md` is not in the list and no proposal is made. The
   comment at `discover.py:168-171` says "Cut AFTER ranking, never before"; the cut moved one
   level up. The scan itself is fast (5,000 files in 18 ms).
4. **A JSON-valid draft with the wrong shape kills the run** `INFERENCE`. `_load_draft` catches
   only parse errors; a `sections` that is a list or string raises at `wizard.py:231-247`,
   exit 4, against the docstring's promise that a corrupt draft is treated as no draft.
5. **Validators accept what the checker rejects** `FACT` (also F-G): a future `effective_from`,
   a past or 401-day `review_by`, a one-character `application_id`, basic-ISO dates the schema
   refuses. Each is caught only at the review or the first check.
6. **Resuming a draft that chose the defaults route never offers defaults again** `FACT`.
   `_drive` skips sections already in the state; the fork runs only in the tail of the `route`
   iteration (`tui/app.py:203, 241`). Cancel after `route` and the next run is the full manual flow.
7. **"Nothing was written" is printed after scaffold files were written** `INFERENCE`.
   `scaffold.write` runs before the profile write (`wizard.py:319` before `:323`); a failure
   between them leaves created files and the CLI's message denies it.
8. **Non-UTF-8 filenames become garbage pathspecs** `INFERENCE`. `git ls-files` C-quotes them;
   `_tracked_files` keeps the quotes, so `"docs/**` is offered as a gated path and the real file
   is dropped. Spaces are handled correctly. Remedy: `git ls-files -z`.
9. **`Discovered.is_empty()` can never be true** `INFERENCE`; `candidate_paths` always appends
   `**`. The documented "fall back to plain text fields" has no callers.
10. **A draft carries no repository identity** `INFERENCE`: a draft copied from another
    repository resumes silently with the reassuring "answered against the framework version
    installed here now". The installer does not gitignore the draft file `FACT`.
11. A draft naming a level or gate that no longer exists resumes and fails later with a bare
    `KeyError`; unknown gate keys are dropped without notice `INFERENCE`.
12. `scaffold.write` misreports a parent-is-a-file failure as a race ("it appeared while this
    run was deciding") `INFERENCE`.
13. A missing directory, a file, and an uninstalled repository all produce the same
    "INSTALL.json does not exist" message `INFERENCE`.
14. `KeyboardInterrupt` escapes `cli.py:88`'s `except Exception`: raw traceback, exit 130, and
    the trailing conformance check runs outside every handler `INFERENCE`.
15. The profile write is not atomic; a truncated profile locks the adopter out of `adopt`
    forever, since it no longer contains "replace-me" `INFERENCE`.
16. `human_roles: null` in a draft renders as the literal `['None']` `INFERENCE`.
17. `adopt` exits 0 even when the checker it runs afterwards reports findings; exit 2 covers
    four unrelated conditions `INFERENCE`.
18. The two risk questions are asked, validated, drafted and never written anywhere; the reason
    a level was chosen is discarded `FACT` (section 3 keeps them, as the questionnaire).
19. Latent: several enum-valued fields are interpolated into the YAML without escaping
    (`render.py:203, 218, 221, 231, 256`); unreachable from the TUI, reachable from a draft.

Docstring-versus-code discrepancies found (F55's class), each with the line: `discover.py:305`
(`is_empty` "callers fall back", none exist), `:20-22`, `:168-171` (the cap comment above),
`wizard.py:209-211` (corrupt draft), `:113-118` (real profile), `:274-277` (return type and
"leaves the repository untouched"), `sections.py:10-13` ("pure and total", three `KeyError`
sites), `validators.py:5-8, :33` ("an empty string is never a decision"; `None` is), 
`scaffold.py:160-163` (`seed_texts` "used by test_provenance", zero callers), `plan.py:604-607`
(`locked_controls` "tui reads this", never imported), `screens.py:393` (`field_ids`, no callers),
`tui/app.py:191-194` (comment contradicts the F47 fix two lines above it).

Dead code: `sections.build_mode`, `plan.locked_controls`, `plan.MINIMUM_SECTIONS`,
`SectionPlan.field_ids/applicable_fields`, `GateSpec.field_ids`, `scaffold.seed_texts`,
`detect.detect_git_state`, `Discovered.is_empty`; both arms of `plan.py:658` are identical;
the `.declared` back-compat readers in `defaults.py:69` and `sections.py:110` read a key no
plan emits.

What the pass could not probe: a real interactive session and real `Ctrl+C` delivery; running
the installer into its probe repository (the machine's global `core.hooksPath` refuses it, as in
F-N); a read-only mount; a `git ls-files` slow enough to hit the 10-second timeout.

---

# Part II — Recommendations, second pass: what best-in-class would look like

The first pass of this section was written in one sitting from Part I's evidence and ran
nothing. The maintainer asked for a fuller pass, and this is it. Four things were done that the
first pass did not do, and every recommendation below has been rewritten against what they
found:

1. **A throwaway prototype of proposal-first adoption**, built on the wizard's own `FormScreen`,
   `LevelScreen`, `plan`, `defaults`, `sections`, `render` and `_verify`, driven at 80×24 on the
   Plutos copy and on a bare one-file repository (`SHOTS/proto/proto.py`, images
   `SHOTS/proto/shots/`). Nothing in the repository was changed.
2. **An engineering spike** in a separate virtual environment: the phase-0 chip fix, snapshot
   testing with `pytest-textual-snapshot`, and the markup probe (`SHOTS/spike/`).
3. **A sourced survey of comparable tools**, fetched from primary documentation today
   (`SHOTS/research/prior-art-verified.md`). Where a claim below cites a tool, the source is
   named; where the survey could not verify something it says so.
4. **A second reviewer** reading the first-pass recommendations against Part I and against the
   project's own rules. Its five ranked gaps are answered in section II.6, and it changed the
   recommendations materially: two of them, as first written, breached the binding rule that
   Part I invoked.

Labels are as in Part I. `FACT` here means measured in the prototype or spike, or quoted from a
primary source. Where a recommendation changes a published rule, a schema, an exit code or the
install payload, it names the decision a human has to take.

## II.1 What the fuller pass established

**The prototype** (`FACT`, `SHOTS/proto/shots/proto-standard-*.png`, `proto-essential-*.png`):

| Persona | Questions before the review | Keys pressed | Typed characters | Result |
|---|---|---|---|---|
| standard, Plutos copy | 8 | 74 | 58 | profile of 158 lines; passes `_verify` unchanged |
| essential, bare repository | 10 | 89 | 74 | profile of 72 lines; passes `_verify` unchanged |

The eight at standard were: application id (proposed from the directory name, accepted),
owner, builds a user interface, the two reliance questions, data classification, release
route, and the conformance level (caret on the recommendation, Enter). The two extra at
essential on the bare repository were the secret-scanner workflow file and the lock file,
because discovery found neither and the proposal engine has nothing honest to propose. That is
the shape the rule requires: a field with no honest source is asked.

**The standard profile the prototype produced is line-for-line identical to the one the
current wizard produced through 72 fields** (`diff` of the two rendered profiles, ignoring
identity and the two optional free-text lines that the prototype leaves as "Not stated at
adoption."). Eight questions bought the same document.

The prototype's review screen shows every line of the rendered profile with an origin beside
it, taken from the field's path rather than its value (`typed`, `discovered`, `example`,
`computed: = owner`, `fact of record`, `scaffolded record`), and Enter on a line opens an
editor; the edited line's origin becomes `typed` (`proto-standard-11-review-edit-modal`,
`-12-review-after-edit`). At 80×24 the review shows twelve lines of profile per page.

Two things the prototype did not do, stated so they are not mistaken for done: it did not
change `render.py`, so its output still carries the false header; and it did not write the
provenance anywhere, only displayed it.

**The spike** (`FACT`, `SHOTS/spike/`):

- `.chip-row { height: auto; border: none; padding: 0 }` makes the three status radios
  visible in three rows at 80×24 (`height_auto_compact.png`, which I read); `height: auto` alone
  costs five rows and Textual's blue border. `RadioSet(compact=True)` exists in Textual 8.2.8
  (added in 3.2.0). Two side observations: the `( )` glyphs stay low-contrast (F-J), and the
  `.chip`/`.chip-selected` rules in the stylesheet match nothing, so the amber selected style
  never applies.
- `pytest-textual-snapshot` 1.1.0 installs against textual 8.2.8 (it requires `textual>=0.28.0`
  with no upper bound) and pins `syrupy==4.8.0` exactly. One snapshot of the real identity
  screen at 80×24 is a 25 KB SVG; the test runs in 0.22 s; two runs produce byte-identical
  snapshots; a one-character CSS change fails it with an HTML report showing expected, actual
  and diff. A gotcha for anyone iterating: an edit that keeps a test file's size and lands in the
  same second as the previous edit is served from pytest's bytecode cache.
- `Static("[A saved draft was found]")` renders as an empty string in Textual 8.2.8. The
  form, level and gates headers survive only because their step prefix ("[1 of 9 — …") defeats
  the markup parser. That confirms F-L's second half and is now finding F-R in Part I.

**The survey** (`FACT` where quoted; the notes file carries every URL):

- Renovate does nothing to a repository until its onboarding pull request is merged; that PR
  contains a proposed `renovate.json`, lists the detected package files by manager, summarises
  what the configuration will do, and says how many pull requests to expect. Edits on the
  onboarding branch update the PR description. This is the direct precedent for proposal-first.
- Copier keeps a machine-owned answers file (`.copier-answers.yml`, headed "NEVER EDIT
  MANUALLY") separate from the generated output, replays it on update, and offers `--defaults`,
  `--data` and `--data-file` to answer without a prompt. Cookiecutter has `--no-input` and
  `--replay`. Copier documents that a hand-edited answers file produces "unpredictable
  behaviour" on update, which is the argument for a machine-owned provenance record rather than a
  comment in the profile.
- The initialisers people run without thinking ask between zero and ten questions and each has
  one flag that answers all of them: `npm init` asks ten and has `-y`; `poetry init` asks nine and
  has `-n`; `cargo init` asks none. Surfaceplate's 32 to 96 fields with no such flag is outside
  that range by a factor of three or more.
- OpenSSF Scorecard reports each check as score, reason, details and a remediation link; its
  CLI has SARIF output but behind a feature flag, and its README advertises only text and JSON.
  `ruff` emits SARIF among twelve formats. GitHub code scanning ingests SARIF 2.1.0 from any
  tool, requiring `partialFingerprints` and a rules list, with a 10 MB limit.
- `pre-commit`, the most widely adopted config-driven gate tool, has no wizard at all: it
  prints a sample config and validates what you wrote.
- `git ls-files -z` outputs paths verbatim regardless of `core.quotePath`; without it,
  non-ASCII paths are C-quoted by default (code item 8).
- Per-value provenance precedents: `git config --show-origin` and `--show-scope` per key;
  `pip-compile` writes `# via <package>` per pin and an "autogenerated by … the following
  command" header; TypeScript 5.9 abandoned the "every option commented out" `tsc --init` file
  because users deleted it. The lesson is to annotate chosen values, not enumerate the universe.
- `brew doctor`, `npm doctor`, `flutter doctor`, `gh auth status`: named checks, one line each
  with pass, warn or fail and a remediation hint, non-zero exit when anything is wrong, a
  verbose flag, and in `gh`'s case a JSON mode that decouples exit code from findings.
- Docs generated from code and gated in CI: cargo's `validate-man.sh` regenerates the man pages
  and fails on a dirty tree with the command to run; `uv` and `ruff` run their generators with a
  `--mode check`. This is the same shape as `build_release.py --verify-manifest`.

## II.2 The bar, restated against the evidence

The tools people adopt without being told to share five properties, and each is now a sourced
observation rather than a slogan: they do something useful before asking anything (Renovate's
onboarding PR); a plain default is always available and safe (`npm init -y`, `copier
--defaults`); every question they ask is one the user can answer from their own head (the
initialisers' ten); they explain each verdict with a reason and a remedy (Scorecard); and
everything they do by hand they can also do unattended (Cookiecutter `--replay`). Surfaceplate
already has the hard part most of those tools lack, a checker that turns declarations into
findings. What it lacks is the first five minutes.

**The target, corrected by the measurements:** from `pip install` to a reviewable pull request
containing a complete, honest profile in under five minutes; between eight and twelve typed
answers at `essential` and `standard` (eight measured on a repository with things to discover,
ten on a bare one, twelve if the adopter declares controls above the floor and has a decisions
directory to name a record in); on an 80×24 terminal; and the same result obtainable with no
terminal at all, from a human-authored answers file.

## II.3 The recommendations

### R1. Proposal-first adoption `FACT` that it works; a decision that it may

Decisions first, then a proposal, then an editable review. The order matters and the first
pass had it wrong: the level decides which gates and controls exist, so the proposal cannot be
built until the decisions screen and the level screen are done. The prototype's flow is:

1. One form, "What only you can tell us": application id (proposed from the directory), owner,
   builds a user interface, the two reliance questions, data classification, release route, an
   optional "risk in your own words", plus one question per thing discovery could not find.
2. The existing level screen, caret on the recommendation.
3. The review: every line of the profile with its origin, Enter to change any line, Ctrl+S to
   write. There is no route screen and no "answer everything myself"; editing the review is
   how you answer everything yourself.

What this costs, stated properly this time: origin has to flow through `sections` and `render`,
not only the interface, and `tests/test_provenance.py`'s allow-list changes. `org/RELEASE_PLAN.md`
names that test as the rule's enforcement, so the decision record comes before the code. This
repository's own profile requires a decision record before a material change to
`surfaceplate/`, so the same is true of every phase below.

### R2. A provenance record beside the profile, not comments inside it

The first pass proposed a comment per value. The second reviewer showed why that fails: the
checker loads profiles with `yaml.safe_load`, which drops comments; any YAML round-trip by the
adopter drops them; and a comment is deleted in one keystroke. The precedent that survives all
three is Copier's answers file: a machine-owned sidecar.

- Write `governance/application-profile.provenance.yaml` beside the profile: for every field,
  its origin (`typed`, `discovered:<path>`, `example`, `computed:<rule>`, `fact of record`,
  `scaffolded`), the framework version, and one document-level line saying when the review was
  approved. It is what `adopt --answers` replays (R4), so it is also the answers record.
- The profile header becomes true: "Written by `surfaceplate adopt` on <date>. Values marked in
  the provenance record as typed were entered by <owner>; the rest were proposed by the tool
  from the sources recorded there and approved as a document at the review."
- **Do not record per-value "accepted".** The reviewer's point stands: at twelve lines a page,
  scrolling past is not a recorded promotion, and the provenance rule says promotion between
  kinds is a human decision that must be recorded. Record what actually happened: typed per
  value, approved per document, and every edit on the review as a typed value with a timestamp.
- The checker closes F-C on the path, not the tag: a required gate whose artefact is in the
  install record's 65-entry file list, or whose CI step is the installed workflow's, is a
  finding whether or not a provenance record exists. That is backward compatible with every
  existing profile. A new `SP` code changes the code register, so it is a recorded change.
- `Proposal.origin` today holds three values; `typed`, `fact of record` and `scaffolded` are new.

### R3. One gate list, with the decisions still the human's

The first pass proposed pre-marking undecided gates `not_applicable` with the example rationale
and letting the adopter tick exceptions. That has the tool writing a scope decision and a
rationale, which the binding rule forbids, and it would make fifteen example rationales true by
assertion, which is F-D again with better labels. Withdrawn.

What is recommended instead keeps every decision with the human and removes the forms:

- One list of the catalogue. Gates the level mandates are marked `required` (that is the
  level's rule, which the tool may state). Design gates follow `builds_user_interface`. Every
  other gate is **undecided** and shown as such, with a single key per row: `r`, `d`, `n`.
  Choosing `n` offers the example rationale as an editable default, exactly as the rationale
  box does today; choosing `r` expands the three proposed fields.
- One explicit command, "declare every remaining gate not applicable", which the human
  invokes deliberately and which the provenance record writes as a bulk human decision with
  the count. This is a human making fifteen scope decisions in one act, not the tool making
  them; the difference is who pressed the key and whether it was recorded.
- The counter says what matters: "3 of 19 will be audited; 12 undecided".
- The status radios must be visible before any of this (F-A); the compact fix is three rows.

DR-46 costed asking `effective_from` per required gate at +1/+4/+15 fields. Under R1 those
fields are proposed with the adoption date and shown on the review, where changing one is one
edit; the count of fields a human is *presented with* before the review drops to zero for
them, and the rule's "asked" is met by the review, provided R2 records them as computed and
not as typed. That reading needs the decision record R1 already needs.

### R4. Non-interactive adoption, without a flag that writes decisions

`--yes` is withdrawn: a run with no human answering that writes a level, rationales and scope
decisions breaches the rule by flag. What remains is the Copier and Cookiecutter shape:

- `surfaceplate adopt --propose` runs discovery and writes two files without a terminal:
  `governance/application-profile.proposed.yaml` and the answers record with every proposal
  and every undecided decision marked `needs-human`. It never writes the profile, so the
  checker never reads a tool-authored declaration. Exit 0.
- `surfaceplate adopt --answers <file>` replays a human-completed answers record through the
  same `plan`, `sections` and `_verify` code as the interface and writes the profile. The
  decisions in that file were made by whoever completed it, and the provenance record says so.
- The agent path is therefore: an agent runs `--propose` and opens a pull request containing
  the proposal and the answers file with its `needs-human` lines; a human completes them; the
  human, or CI on the human's commit, runs `--answers`. The agent never authors a control
  decision, which is what the installed instructions require.
- The TTY refusal stays for the interactive command and names `--propose`.

### R5. Design at 80×24 first, and name the mechanisms

Unchanged in substance from the first pass, with the mechanisms the reviewer asked for:

- A per-screen layout budget: heading, one intro line, the control, one help line, the hint.
  Prose that does not fit goes behind `?`, and `?` scrolls what it reveals into view (F-H).
- Off-state contrast on `.toggle--button`; no bold highlight on an unpressed first radio; the
  focused row and its help share one background and one left rule; a `.field-help` rule
  (F-I, F-J). The prototype's override (`color: #7a827e; margin: 0 0 1 2`) is in its images.
- Truncated labels readable in full on focus (F-K).
- A way back from every screen; the review offers "go to the line" for its error and hides
  "write it" while there is one (F-F).
- **The error must survive the focus move.** `FormScreen.action_commit` sets the error in the
  hint, focuses the failing field, and `on_descendant_focus` then rewrites the hint without the
  error (F-R). Pass the error through, or set it after focusing.
- **Cancelling at the resume prompt keeps the draft.** `confirm_resume` turns `None` into
  `False`, and `_resume_or_start` treats `False` as "start fresh" and deletes (F-L). Return a
  three-valued answer, and only `n` discards.
- Every bracketed `Static` gets `markup=False`; a compose-tree lint in the render tests can
  assert it. The resume header is the production casualty today.

### R6. Make the interface what the tests look at, and cost it honestly

- `pytest-textual-snapshot` at `terminal_size=(80, 24)` for every screen, including a gates
  screen with a focused status radio. It works against the pinned Textual (spike). It is a new
  test dependency with an exact `syrupy` pin, so it is a dependency review under the security
  rule and an addition to the test extra in `pyproject.toml`, and it needs a rasteriser if
  PNGs are to be attached in CI. Snapshots are golden files: under the tests rule a deliberate
  interface change carries cause, delta and reviewer, and `--snapshot-update` is never used to
  absorb an unexplained diff. That is a real cost and the right one for a product whose
  defects were all visual.
- Keep the rendered-line property tests for the properties that must hold at any size: the
  status row of an unmandated gate contains `( )`; the first artefact widget after accepting
  proposals holds the proposal; the help line for the focused field is on screen.
- A persona budget test that asserts **the measured numbers, not the estimate**: fields
  presented before the review ≤ 12 at essential and standard on the two fixtures the prototype
  used, and the gate list counted separately. The first pass proposed freezing eleven; the
  prototype measured eight and ten.
- The suites' count-on-success property is kept: if pytest becomes the runner for the snapshot
  suite, it prints its count and the workflow's "every suite ran" loop gains one row, and the
  `CLAUDE.md` count is updated in the same change.

### R7. Discovery that cannot find the framework in the mirror

- Exclude every path in the install record's `files` list and the installed workflow's step
  names from every candidate list and from "you appear to have". Rank first, cap last, cap per
  field. `git ls-files -z`. Delete `is_empty` or make it true.
- **When exclusion leaves nothing, ask.** On the bare repository the prototype had no honest
  scanner workflow or lock file to propose and asked for both; that is the correct outcome, and
  discovery's job is to make it rare, not to invent an answer.
- Note for the record: on a fresh install the installer's output is untracked, so discovery
  does not see it; F-C bites once the install is committed, which is the normal case.
- Widen what discovery looks for, because each hit removes a question: pre-commit config,
  gitleaks config, lock files, ADR directories, changelog, CODEOWNERS, test naming convention,
  release workflow.

### R8. One set of rules for the wizard and the checker, as a recorded payload change

- Move the date rules, the id pattern, the placeholder pattern and the "named path is
  tracked by git" rule (`SP051` requires tracked, not merely present) into one module both
  import. That module becomes install payload, and DR-20 requires a recorded decision for a
  payload addition; F12's source-versus-vendored surface grows by one file and
  `check_vendored_current` must cover it.
- A parity test: for every `SP` code that reads a profile field, a wizard validator refuses the
  same input, or an exemption names the reason. History-only codes (`SP034`, `SP035`) are exempt.
- `validators.check` treats `None` as blank.

### R9. The written profile as a reader's document

- For each field the checker never reads, the compatible choice is "optional in the schema,
  stamped `# not checked` when present"; dropping breaks every existing profile and both shipped
  examples. Which fields, and whether the two gate descriptions stay (humans and auditors read
  them, even if the checker does not), is a decision.
- Write the two reliance answers into the profile, as optional fields, because they are the
  reason a level was chosen and today they are asked and discarded (code item 18). A schema
  change, so a decision.
- `surfaceplate explain <profile>`: for each line, which `SP` code reads it or "declared only".

### R10. A checker people can build on

- `check --format json|sarif`. SARIF 2.1.0 with `partialFingerprints` and a rules list is
  what GitHub ingests; Scorecard's flag-gated SARIF is a warning that the format is a second
  path even where it exists, so JSON first, SARIF when there is a consumer.
- Distinct exit codes, with graced `WARN` distinguished from `FAIL`. `adopt` exiting non-zero on
  findings must not fail every first adoption, since a fresh adoption of an existing repository
  produces graced findings by design; exit non-zero on `FAIL`, zero with a printed summary on
  `WARN`. Exit codes are read by the installed hook and workflow, so this is a public contract
  and a stop-and-ask.
- `surfaceplate doctor`, offline by default: Python and pip, `core.hooksPath` at every scope,
  a terminal or not, the venv on `PATH` or not, the vendored copy's digest. "Actions enabled"
  needs the GitHub API and a token, so it is `doctor --online`, and a trust-boundary review.
- A real argument parser with `--version` and `--help`.

### R11. One front door, in the order the release plan allows

- `org/RELEASE_PLAN.md` sequences the documentation pass after adopters and permits a bounded
  README front-door pass now. So: now, the README's three commands, the version line, the two
  dead links, the `#egg=` form replaced by `surfaceplate[adopt] @ git+…`, and a sentence on
  `core.hooksPath`; INSTALL.md gains `surfaceplate install` and `check`, and its pointer to a
  prompt file that is not in the payload is removed or the file is shipped. The
  reference-versus-guide restructure and any retirement of `SETUP_GUIDE.md` wait for the plan's
  item 8 and a decision.
- Numbers and lists generated or checked: gates and controls per level from `catalogue`, the
  `SP` code catalogue from the checker's registry, the version from one file, every relative
  link resolved both in this repository and in an installed checkout (INSTALL.md's broken
  pointer breaks only in the latter). `check_code_registers.py` already runs in CI and is the
  home. The pattern is cargo's `validate-man.sh` and `uv`'s `--mode check`.
- Standing practice `S3` is not mechanisable for the half that needs a human's machine; a
  clean-container CI job can cover the other half, including a global `core.hooksPath`.

### R12. Documents that cannot contradict themselves, and one correction

- One authority per claim, quoted by reference elsewhere; one evidence-label vocabulary;
  principles cited by anchor. Register parity: body status equals index status, enforced in
  `check_code_registers.py`.
- **Correction to Part I, F-P.** `SP049` does recompute `sha256(.standards/MANIFEST.sha256)`
  against the install record, so "nothing compares the anchor to what it anchors" was wrong at
  that level. The vendored manifest can never equal the source manifest's hash, because the
  source manifest hashes the profile that carries the vendored digest. DR-45 records exactly
  that, and says the comparison that matters is against the *published* manifest, which is F6,
  open, and a human action. F-P's digest half is withdrawn; its status-parity half stands.
- Docstrings that describe current behaviour and point to the record for history: a change to
  a recorded house style, so a decision, not a hygiene item.
- The Actions-disabled sentence in `PREREQUISITE_GATES.md` is an external fact; a human verifies
  it and one document wins.

### R13. Code hygiene, with the compatibility costs named

- **Template guard:** not a digest of the current template, which would lock out anyone who
  installed an older template untouched and then upgraded. Check the structural token instead:
  a required scalar still equal to `replace-me` means "untouched template"; prose mentioning
  the token does not.
- Atomic profile write (`os.replace`). Draft validated against a schema and carrying an identity
  fingerprint (`application_id` plus the install digest, never a remote URL), with unknown
  section or gate keys offered a fresh start rather than a bare `KeyError`. The draft already
  records the framework version and digest and flags a mismatch; the reviewer's note that it
  does not was wrong. Gitignoring the draft means the installer editing an adopter-owned file,
  so it is a scope decision; the alternative is writing the draft under `.standards/`.
- `KeyboardInterrupt` handled; scaffold results reported before a later failure, and the
  scaffold step's parent-is-a-file error named correctly; `human_roles: null` rendered as an
  empty list; enum values escaped through `_scalar`; dead functions and the dead `Ctrl+Q`
  handlers removed or the screens' binding given priority.
- The existing scripts stay the runner for the twelve suites; pytest is added for the snapshot
  suite only, preserving count-on-success.

### R14. Sequence, corrected

Every phase changes `surfaceplate/`, and this repository's own profile requires a decision
record before a material change begins, so each phase opens with its record and an activity.
The estimates are estimates.

| Phase | Content | Answers | Decision needed |
|---|---|---|---|
| 0 | Regression tests first, then: chip row compact; `GatesScreen` seeded; choice and `None` validation; error survives focus; resume quit keeps draft; template guard by token; help styled; `markup=False` on the resume header | F-A, F-B, F-E, F-I, F-L, F-R, code 1, 2 | an activity; no rule changes |
| 1 | Provenance record beside the profile; proposal-first flow; gate list with human decisions; validator parity module; discovery exclusions and rank-then-cap; editable review with a way back | F-C, F-D, F-F, F-G, F-M, section 3 | DR amending DR-46's reading of "asked"; DR for the payload module (DR-20); new `SP` code |
| 2 | `adopt --propose` and `--answers`; `doctor`; `--format`; exit codes with `WARN`/`FAIL`; bounded README pass; generated numbers and code catalogue; link check in an installed checkout | F-N, F-O, R4, R10, R11 | exit-code contract (stop-and-ask); README pass within the release plan's bound |
| 3 | 80×24 snapshot suite and measured budget test; register parity; optional-field schema change; docstring style | suites' blind spots, F-P, code 18, F55 | dependency review; schema change; house-style decision |

Then the Plutos re-run, after phase 0, as the human action that closes H1; and the register
entries in section 6, which this review drafts and a human records.

## II.4 The question count, settled by measurement

The first pass said eleven and the reviewer showed the table did not add up to it. The
prototype replaces the estimate with a measurement and a rule for counting. **Rule:** a field
counts as a question if it is presented as a form field before the review, whether or not it
is pre-filled; a line on the review counts as zero unless the human edits it, and an edit is
recorded as typed.

| Persona | Measured | What made the difference |
|---|---|---|
| standard, repository with things to discover | 8 | scanner, lock file, artefacts, paths all proposed |
| essential, bare repository | 10 | scanner workflow and lock file asked because nothing was found |
| either, declaring controls above the floor | +1 | one multiselect |
| either, with a decisions directory | +1 | the record id is asked rather than scaffolded |

So eight to twelve, against 32 to 96 today, producing the same profile. The gate list is
counted separately and honestly: at standard, fifteen single-key decisions, or one explicit
bulk decision, with the required gates' three fields proposed and reviewed. That is where
DR-46's +4 and +15 live now, as keystrokes on one screen rather than as forms.

## II.5 What each change costs in provenance honesty

Nothing, on three conditions the first pass did not state: the provenance record exists and
is machine-owned (R2); no tool-supplied value is ever recorded as typed or accepted, only as
proposed and reviewed as part of a document (R2); and no default ever stands in for a scope
decision, including `not_applicable`, which a human presses `n` for, singly or in one recorded
bulk act (R3). Under those conditions the profile is more honest than today's, whose header
claims human authorship over canned prose.

## II.6 The second reviewer's five gaps, and what changed

1. *R3 and R4 breached the rule Part I invoked.* Accepted in full. Pre-marked `not_applicable`
   and `--yes` are withdrawn; R3 keeps every decision with the human and adds a recorded bulk
   act; R4 writes proposals and replays human answers only.
2. *No backwards-compatibility story.* Accepted. R2 is a sidecar that leaves every existing
   profile valid; R13's guard is a token check, not a digest; R9's changes are optional fields;
   the draft's shape is validated but its version check already exists.
3. *The eleven is not eleven.* Accepted. Replaced by the measured eight to twelve and a counting
   rule; the budget test asserts the measurement.
4. *Coverage holes and a mis-aimed remedy.* Accepted. F-Q, F-L's mechanism, F-R, and code items
   6, 7, 12, 16, 18, 19 are now in R5, R9 and R13; R12's digest claim is withdrawn and Part I
   corrected. The reviewer's own error on the draft's version field is noted in R13.
5. *Authority and sequencing conflicts.* Accepted. R14 names the decision each phase needs; R8
   names DR-20; R10 names the exit-code contract; R11 is bounded by the release plan; R13 keeps
   the count-on-success property; R6 treats snapshots as goldens.

## II.7 What remains inference

- That eight to twelve questions *feel* like eight to twelve. The prototype was driven by a
  script at 80×24; no human has used it.
- That the sidecar provenance record is the right file shape; Copier's precedent supports the
  idea, not the schema.
- That the five properties in II.2 are the properties that matter; the sources show that the
  named tools have them, not that they cause adoption.
- The effort estimates in R14.
- Everything section 4 of Part I lists as a gap still stands: a real terminal, a mouse, pip 26.
