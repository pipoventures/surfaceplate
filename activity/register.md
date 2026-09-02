# Activity register — surfaceplate

The register of identified work in this repository. Required by
`.github/instructions/activity.instructions.md`, which states that work begins by naming a
registered activity and that an agent may draft an entry but a human authorises it.

## Where this register starts, and why that is not a gap

**This register begins on 2026-08-31.** Every packet of work delivered in this repository before
that date was unregistered work by the framework's own rule — `DR-13` records this plainly and
declares establishing self-conformance "the last ungoverned work in this repository". The
`work_registration` gate in `governance/application-profile.yaml` therefore takes
`effective_from: 2026-08-31`, and history before that date is out of scope. That is the mechanism
`core/PREREQUISITE_GATES.md` provides for exactly this case: *"A gate binds from a date. History
before that date is out of scope. Without this, adopting a gate would require rewriting the past,
and no real repository would ever adopt one."*

The date can move backward freely and can never move forward (`SP034`, never graced). Choosing
2026-08-31 is therefore a one-way commitment to at most that much retroactive scope.

## Status vocabulary

`planned`, `in_progress`, `blocked`, `waiting_for_review`, `external_dependency`, `deferred`,
`done`. Status is derived from dependencies, not asserted: an unsatisfied hard dependency is
`blocked`, an unsatisfied review dependency is `waiting_for_review`, an unsatisfied external
dependency is `external_dependency`.

`done` requires the definition of done to be met **and** the required evidence to exist. Human
approval, independent validation, risk acceptance and release readiness are never marked complete
on an agent's authority.

## Register

| Activity | Title | Owner | Reviewer | Status | Depends on | Type | Material? | Judgement | Definition of done | Evidence required |
|---|---|---|---|---|---|---|---|---|---|---|
| `ACT-001` | Self-conformance: surfaceplate conforms to what it publishes | maintainer | maintainer | `done` | — | — | yes — it becomes this repository's principal claim about itself | high — the conformance level and every gate declaration are human judgements | `check_conformance.py --repo .` passes on the real tree, the check is shown capable of failing, and CI runs it without any step being skippable | The pre-change `SP001` failure; a break/fail/restore/pass cycle in a scratch copy; a passing run on the real tree; CI green with every step shown to have executed |
| `ACT-002` | Decide whether the vendored `.standards/` set should shrink to what is mechanically read | maintainer | maintainer | `done` | `ACT-001` | review | yes — changes what every future adopter receives | high — trades adopter convenience against payload weight | A decision record deciding it either way, with both sides stated | Cited counts of which vendored files have a reader in the checker and which do not; evidence on whether the normative documents move between releases |
| `ACT-003` | Resolve `F12`: source-vs-vendored checker drift | maintainer | maintainer | `done` | `ACT-001` | hard | yes — a stale vendored checker can pass a self-check the current source would fail | medium — the mechanism is understood; the remedy is not chosen | Either a check that detects divergence, or a recorded decision that the CI mitigation is sufficient and why | A demonstration that divergence is detected, or a record explaining why detection is not warranted |
| `ACT-004` | Resolve `F14`: `SP032`'s placeholder heuristic misreads notation | maintainer | maintainer | `done` | — | hard | yes — changes the behaviour of a published control that gates a `standard` floor | high — no principled narrowing was available, so the branch was removed rather than tuned | A decision record deciding it, and a change that clears the seven measured false positives without ceasing to catch a genuinely unfilled artefact | `DR-17`; the seven occurrences cleared; both guards seen to fail in a scratch copy; `F15` raised and closed for shipped templates; `check_conformance.py --repo .` moving to `PASS` as a consequence, not as the objective |
| `ACT-005` | Item 4: `secret_hygiene` gains an actual check | maintainer | maintainer | `done` | `ACT-001` | hard | yes — it adds a control every adopting repository must satisfy at every conformance level | high — the control must verify a scanner is wired without ever implying that no secrets are present | A new finding code that fires when no scanner is declared and when a declared scanner cannot fail; surfaceplate itself passes it; the standard's own documents updated in the same change | A decision record; both directions seen to fail in a scratch copy; suite counts accounted for; `check_conformance.py --repo .` still `PASS` on both copies after reinstalling |

| `ACT-006` | Close `F9` and `F10`; discharge `F8`'s documentation half | maintainer | maintainer | `done` | — | hard | yes — `F10` removes a false claim from an evidence document, and `F9` changes adopter-facing remediation text | medium — the `F10` decision (retire vs regenerate) is a judgement about what producer evidence is for | `audit/VALIDATION_RESULTS.md` no longer asserts anything untrue; the `SP005` remedy names a version; the installer reports a version mismatch; `README.md`'s history-audit claim is corrected | A decision record for the `F10` outcome; the version-mismatch report seen to fire and seen to stay silent; suites and manifest accounted for |
| `ACT-007` | Publication pass: sanitise, close `F13`/`F15`/`F16`, decide publication | maintainer | maintainer | `done` | — | hard | yes — it changes a published control (`SP032`), ships two new obligations to adopters, and decides where the project lives | high — publication is not reversible, and the history question had three plausible answers with very different costs | The working tree carries no reference to the former organisation; `F13`, `F15` and `F16` are closed or their obligations shipped; `DR-22` and `DR-23` recorded; the full-history sweep is runnable | Seen-to-fail probes in both directions for the exemption mechanism; the 403s read live; the former organisation's footprint counted across all commits; a full backup bundle taken before any of it |
| `ACT-008` | Remove inherited internal jargon from the public tree (`F18`) | maintainer | maintainer | `done` | — | hard | yes — `adapters/**` and `SETUP_GUIDE.md` are adopter-facing, and `adapters/` is in the install payload | low for the live guidance; the judgement is in what NOT to touch — the audit records are true statements about a repository that had that name | No inherited product or methodology name remains in live guidance; historical audit records keep their text under an explanatory note | A grep showing the remaining occurrences are confined to `audit/`, each under a note; suites and manifest accounted for; both checker copies PASS after reinstall |
| `ACT-009` | Implement the dual licence decided in `hermes` (`F19`) | maintainer | maintainer | `done` | — | hard | yes — it changes the terms under which every copied file is licensed, on a published artefact | low on mechanism, and the boundary is already locked; the judgement was made in `hermes` and is cited rather than retaken here | `LICENSE-DOCS` carries CC0-1.0, `NOTICE` exists, and `README.md` states which licence covers which paths | The CC0 text fetched from creativecommons.org and diffed byte-for-byte against the SPDX copy; suites and manifest accounted for; both checker copies PASS |
| `ACT-010` | Architecture for provable controls, and say which are checked (`F20`) | maintainer | maintainer | `done` | — | hard | yes — it fixes the shape every future control validator must follow, and changes what a passing check reports | high — the architecture constrains eight validators that follow it, and the boundary between what can and cannot be proven is a judgement the whole design rests on | `DR-25` records four patterns and the meaning of `implementation_reference`; `CONFORMANCE_LEVELS.md` and the checker's output distinguish a checked control from a declared one | The demonstration reproduced — a profile claiming `full` with no records still passes, and the output now says why; suites and manifest accounted for |
| `ACT-011` | Patterns D and A: three controls become checked; surfaceplate acquires a lock (`F21`) | maintainer | maintainer | `done` | `ACT-010` | hard | yes — it changes what a conformance result establishes, and pins the runtime for every adopting repository | medium — the patterns were fixed by `DR-25`; the judgement here was which versions to pin and whether to record the early start on item 1 | `dependency_lock`, `assurance_findings` and `documentation_authority` verified rather than declared; `pyproject.toml` pins both runtime dependencies; the level banner shrinks from 3 of 4 to 2 of 4 | Versions resolved in a clean environment with all five suites run against them before pinning; `SP051` and `SP052` seen to fail in five ways and pass in one; the drift guard seen to fail both ways |
| `ACT-012` | Pattern B: `deterministic_tests` and `contract_tests` become checked | maintainer | maintainer | `done` | `ACT-011` | hard | yes — it adds an obligation on every adopter at `standard` and above, and amends a published decision | medium — the mechanism is `SP046`/`SP047` reused; the judgement was step versus job granularity, which amends `DR-25` | Both controls verified rather than declared; the level banner disappears at `standard`; `DR-25` amended in place | `SP053` seen to fail four ways and pass one; the banner absent afterwards, which is the packet's own scoreboard |
| `ACT-013` | `H`: deferrals and deferred gates expire (`F22`) | maintainer | maintainer | `done` | — | hard | yes — a deadline that adopters declared starts being enforced | medium — the mechanism is small; the judgement is what is IN scope, and gate exceptions are deliberately out | A deferral or deferred gate whose `revisit_by` has passed raises `SP054`; one dated in the future does not | `2020-01-01` fails and surfaceplate's own `2027-02-27` passes — the second mattering more, since a check firing on every deferral would pass the first test too |
| `ACT-014` | Pattern C1: the four record-based controls acquire a register that is checked (`F20`) | maintainer | maintainer | `done` | `ACT-010` | hard | yes — it adds a real obligation on every adopter at `full`, and closes the half of `F20` that has been open since the architecture was written | medium — the mechanism reuses the gate-exception record loader; the judgement is that an EMPTY register must pass, and that `DR-25`'s claim about currency is wrong | Each of the four controls names a directory that exists, is tracked, and holds nothing that fails its schema; `full` becomes fully checked | The four negative controls carry the evidence — an empty register passes, a `README.md` beside a record is ignored, a valid record passes, and a valid record of the WRONG type fails |
| `ACT-015` | Pattern C2: records must reference what they describe; `provenance` and `run_lineage` separated | maintainer | maintainer | `done` | `ACT-014` | hard | yes — it adds cross-register obligations at `full` and edits a published schema | medium — the mechanism is an index over records already loaded; the judgements are how the two controls are separated after the first answer was disproved, and whether a redundant contract clause is removed or made real | A run naming an unregistered method, an override naming a run that never happened, a duplicated identity and a foreign `application_id` are all rejected | The three negative controls carry the evidence — the worked example set passes, an undeclared target register raises nothing, and a record that failed its schema produces no reference cascade |
| `ACT-016` | What the Plyego gate found: the exemption catch-22 and a misleading remedy (`F25`, `F26`) | maintainer | maintainer | `done` | `ACT-015` | medium | yes — it changes what the profile scan accepts, in every adopting repository | low — the mechanism mirrors `DR-22` exactly; the judgement is how narrow the exclusion is | An exemption may state its own rationale without failing the profile, and `SP032` names the remedy it has always had | Three negative controls — the scan still fires on `owner`, on a gate's rationale and on a deferral's — plus the Plyego probe re-run against the fixed checker |
| `ACT-017` | The installer forbids what the standard permits: a recorded hook opt-out (`F27`) | maintainer | maintainer | `done` | `ACT-016` | medium | yes — it changes what the installer will do in every adopting repository | medium — the mechanism is small; the judgement is that declining must leave a trace rather than being a silent flag | A repository with its own hook system can adopt without surrendering it, and the check says on every run that nothing gates staged changes | Three negative controls — the default install still refuses a foreign hooks path and writes nothing, and `SP038` still catches a gate claiming a hook that was declined |
| `ACT-018` | Agent neutrality: emit the instructions where each agent actually reads them (`F29`) | maintainer | maintainer | `done` | `ACT-017` | hard | yes — it changes what every adopting repository receives, and gives this repository its own instructions for the first time | medium — the emitter design follows the documented loading rules; the judgement is a block in `AGENTS.md` rather than owning the file | The instructions land in `.claude/rules/` and `AGENTS.md` as well as the Copilot paths, and surfaceplate is finally governed by its own | Three negative controls — Copilot emission unchanged, an adopter's `AGENTS.md` content preserved verbatim, and their `CLAUDE.md` never written |
| `ACT-019` | `RELEASE_PLAN` item 1: pip packaging, and the precondition `DR-10` left unsolved | maintainer | maintainer | `done` | `ACT-018` | hard | yes — it decides the payload's on-disk shape for every future distribution channel, and moves files every internal reference depends on | high — the layout choice was surfaced and decided by the maintainer rather than taken silently; `repo_root()`'s fix turned out simpler than either research pass anticipated, and that simplification is itself a judgement worth recording | A wheel built from the new layout installs into a clean virtualenv with no git checkout present and successfully installs the standard into a fresh target repository | The negative control: the acceptance test runs from the pip-installed package alone, nothing borrowed from the source tree it was built from; suites and manifest accounted for; both checker copies `PASS` after reinstalling from the new location |
| `ACT-020` | `RELEASE_PLAN` item 2: the CLI and the wizard, and resolving the "wizard" naming collision | maintainer | maintainer | `done` | `ACT-019` | hard | yes — it decides how every future adopter fills in `governance/application-profile.yaml`, and retires the discovery/authoring phases of an existing prompt in favour of it | high — the binding rule ("it asks, the human answers, the tool writes") constrains the whole design, and the terminal-vs-form choice was tested with a clickable comparison artifact and agreed with the maintainer before this packet's plan was written, not assumed | A scripted end-to-end run of `surfaceplate adopt` produces a profile that validates against the schema and matches the answers exactly, for a `full`-level walk of all 19 gates | The negative controls: an interrupt mid-flow leaves the repository untouched; a level-mandatory gate cannot be declined; nothing in the assembled profile traces to anything other than a typed answer; the renamed prompt no longer claims the word "wizard" anywhere in its own text |
| `ACT-021` | `RELEASE_PLAN` item 9: the Gemini cross-provider adversarial review packet | maintainer | maintainer | `done` | `ACT-020` | hard | yes — it is the request sent to a party outside this repository, and this packet's own text is what stops that party's findings from being mistaken for an independent audit (item 10) or a claim that `F6` is closed | medium — the mechanism follows the existing `AUDIT_README.md` handoff shape and the `CHATGPT_ENTERPRISE_AUDIT_PROMPT.md` structural pattern exactly; the judgement is what changed since that prompt was written (the gate catalogue, pip packaging, the CLI/wizard) and what to deliberately drop (re-testing a *different* provider's *prior* named findings against a differently-named predecessor product) | `audit/GEMINI_ADVERSARIAL_REVIEW_PROMPT.md` exists, is committed, and a freshly built `dist/surfaceplate-<version>.zip` plus that prompt are both readable at the confirmed Desktop hand-off path | The negative control: the new prompt is read back and confirmed to claim nowhere in its own text that approval, independent validation, or `F6` closure has occurred; the zip's own contents are listed directly and confirmed to carry no `.git`, no `.standards/`, no secrets |
| `ACT-022` | Gemini's first finding: `adopt` invents rationale text for baseline controls and auto-masked UI gates | maintainer | maintainer | `done` | `ACT-021` | hard | yes — it is the framework's own binding rule for its own wizard, found violated by the review the framework requested of itself | medium — the mechanism is routing existing hardcoded strings through `Prompt.text` calls already used elsewhere in the same file; the judgement was which of Gemini's five findings were real (verified against the code directly, not accepted on the report's authority alone) | Every rationale written to a profile by `agent_work_packets`, `actual_diff_review`, `secret_hygiene`, and the four UI gates traces to a `Prompt` call a human actually answered, with the existing scripted-answer test suite updated to prove it | The negative control: a scripted run with the old hardcoded strings removed from the source fails loudly if any code path still writes a rationale `ScriptedPrompt` was never asked for |
| `ACT-023` | Decide Gemini's material finding: should the schema enforce per-level control presence? | maintainer | maintainer | `done` | `ACT-021` | review | yes — it decides whether `application-profile.schema.yaml`, a published contract, gains conditional logic duplicating `check_conformance.py`'s own `CONFORMANCE_LEVELS` data | medium — the checker already runs schema validation as its own first step, so no separate schema-only bypass exists in this project's real pipeline; the judgement is whether the residual defense-in-depth value is worth a second, hand-maintained copy of the same rule | A decision record either way, reasoned rather than asserted, so a future reviewer raising the same idea finds the answer already worked through | The two things checked before recommending against it: that `check_conformance.py` validates against the schema before its own semantic checks (so nothing bypasses the schema alone), and that `CONFORMANCE_LEVELS` has no generator feeding the schema, meaning any schema-side copy would need hand-kept sync |
| `ACT-024` | `RELEASE_PLAN` item 5, phase 1: exercise Plutos (Plyego deferred — mid-migration) | maintainer | maintainer | `done` | `ACT-020` | hard | yes — it is the second time this framework has been run against a repository it did not write, and any defect it exposes is unreachable from self-check alone, the same shape `F25`/`F26` were | medium — the mechanism repeats `DR-28`'s own probe exactly; the judgement is scoped deliberately narrow, per `DR-28`'s own principle that gate decisions are the maintainer's to make with the per-gate cost in front of them, not an agent's to infer from a probe | A throwaway clone of Plutos installed and checked at `essential`, any newly-exposed surfaceplate defect fixed with tests, and a decision record carrying the cost table — with nothing written to the real Plutos repository | The negative control: `git status` on the real Plutos checkout shows no changes; the clone's own history and objects are shared read-only, never a checkout of the real working tree |
| `ACT-025` | The hook-conflict `STOPPED` message names routes without making two of them actionable | maintainer | maintainer | `done` | `ACT-024` | hard | yes — it changes what every adopter sees the first time this specific refusal fires, on a path `F27` already made this framework's stated policy | medium — the mechanism is a new git-scope-detection helper and a rewritten message; the judgement is what each route needs to become a genuine next step rather than a description of an outcome | The message names which git config scope set the conflict and its blast radius, and each of the three routes is a real, copy-pasteable or concretely-pointed-at next step, not a description | Read back against the exact scenario that prompted this — a global `core.hooksPath` conflict on Plutos — and confirmed it would have made this session's manual explanation unnecessary; two fixture scopes (global, local) asserted in the test suite |
| `ACT-026` | Remediate `adopt`, phase 1: a real data-loss bug, and a wizard that presumes knowledge its stated audience doesn't have | maintainer | maintainer | `done` | `ACT-025` | hard | yes — it fixes a correctness bug that destroyed a real 20-minute session, and changes what every future adopter is asked and how, across all 19 gates and every control | high — the whole shape was worked out with the maintainer directly against a real, failed live session and the originally-approved mockup read back frame by frame, not assumed; three worked examples of the new dual-register content were drafted and approved before authoring the other ~32 | A scripted answer containing `?` writes successfully; a mode choice changes which register of explanation is shown for every one of ~35 items with no gap; the level screen shows detected signals without picking a level; every rationale field offers an editable example; an interrupted run leaves a resumable draft | The negative controls: the exact flow-sequence characters (`?`, `,`, `[`, `]`, a leading `-`) round-trip correctly; a coverage test fails loudly if any catalogue item is missing either register rather than silently falling back; a completed run leaves no stale draft behind |
| `ACT-027` | Remediate `adopt`, phase 2: rebuild the interaction layer on Textual, and make the binding rule genuinely provable | maintainer | maintainer | `done` | `ACT-026` | hard | yes — it replaces a dependency fixed by a decision record (`DR-32`), changes every screen an adopter sees, and rewrites the mechanism by which this project proves its own binding rule | high — the interaction model was chosen against the originally-approved mockup read back frame by frame, and the dependency replacement hits `dependency-update`'s own mandatory stop, so it proceeds on a recorded human decision rather than an agent's judgement | Every screen the approved mockup specifies is delivered — answered fields staying visible, a level screen where highlight is not selection, and three gates on screen at once with chip rows, inline follow-ups and free `Tab`/`⇧Tab`/`[g]` movement; `questionary` is gone; the sentinel provenance walk passes with a reviewed allow-list | The negative controls: a value written that no answer supplied fails the provenance walk; a field dropped from a screen fails the screen↔plan join; highlighting a level without choosing it records nothing; and the packet is read back by driving a real terminal against a real Plutos clone, which is the one thing phase 1 could not do |
| `ACT-028` | Remediate `adopt`, phase 3: fix what the rebuilt interface actually renders, and make rendering checkable | maintainer | maintainer | `done` | `ACT-027` | hard | yes — it changes every screen an adopter sees, and it closes a verification gap that let six user-visible defects through a green suite | medium — the defects and their causes are each measured rather than inferred; the judgement is that rendering is asserted as named properties rather than captured as a snapshot, because this project treats a golden file as an audit trigger and a wizard whose copy is still being tuned would churn one | Every hint line renders the keys it names; no label is printed twice; a label and its value share a rendered line; help shows only for the focused field; at 80x24 at least three gate names are visible; the level screen renders its numbering and highlight marker | The negative controls: each new assertion is seen to fail against the defect it exists to catch, by reintroducing that defect deliberately — a property test that has never failed is one nobody has calibrated |
| `ACT-029` | Remediate `adopt`, phase 4: discover the repository's own candidates, and offer them instead of asking for free text | maintainer | maintainer | `done` | `ACT-028` | hard | yes — it changes what every adopter is asked to supply, and fixes a blocker that made an adoption impossible to finish | high — the direction came from the maintainer's own failed run ("free text is confusing and really prone to errors"); the boundary between what becomes a picker and what stays prose was put to him rather than inferred | A multi-line answer writes as a block scalar and round-trips; no renderer error can reach a user as a traceback; every structural field offers candidates read from the repository itself; a toggle's on and off states differ in rendered text; a window smaller than the content scrolls rather than clipping | The negative controls: a gitignored file is never offered as a candidate; each new render property re-broken deliberately; the provenance walk still holds, or the packet has broken its own guarantee |
| `ACT-030` | Build `F30`'s deferred remedy: the history audit follows renames instead of resolving a precondition at its current path | maintainer | maintainer | `done` | `ACT-029` | hard | yes — it changes what `SP035` reports in every adopting repository, which is a published control's behaviour, not an internal detail | high — the remedy rests on git's rename detection, which is a heuristic, and a control may not silently trust one; the judgement is that following a rename must be disclosed on the run rather than quietly clearing a violation | A gate whose precondition artefact was renamed no longer reports its pre-rename history as violations, and the rename it followed is stated on the run | The negative controls: a genuine violation is still reported after a rename; an artefact that never existed is still a violation; and a rename that git cannot follow falls back to the strict check rather than passing |
| `ACT-031` | Remediate `adopt`, phase 5: the discovery that never reached the gates, one interaction model, and a defaults path | maintainer | maintainer | `done` | `ACT-030` | hard | yes — it changes the wizard's opening structure for every adopter and fixes a defect that made a completed adoption unusable | high — the restructure came from the maintainer's own finished run; what `Set defaults` may write was put to him explicitly, because a tool filling in answers is the one thing this package's binding rule forbids | Gate artefacts offer the repository's own files; a field's kind is visible before it is touched; one interaction model across field types; the run ends by saying what it wrote and whether it passes; and `Set defaults` proposes values on a review screen rather than writing them | The negative controls: the screen-to-plan join compares field KIND as well as id, so a screen built from an un-discovered plan fails it; and the provenance walk still holds, since a proposed default is only written once submitted |
| `ACT-032` | Remediate `adopt`, phase 6: ask what only a human holds, derive what follows from it | maintainer | maintainer | `done` | `ACT-031` | hard | yes — it changes what every adopter is asked, removes prose the adopter used to author in favour of the framework's own, and fixes a proposal that would produce a gate passing while guarding nothing | high — the direction came from the maintainer's own challenge that the package must itself be easy; the boundary between what may be derived and what must stay a human decision is bounded by `core/CONFORMANCE_LEVELS.md`, which forbids deriving the level automatically, so the level is proposed and confirmed rather than computed | A control above the declared level's floor is offered once as an opt-in, not asked field by field; a gate's descriptions, effective date and enforcement are derived rather than prompted; the level is proposed from two world-facing questions and confirmed by the adopter; and no artefact is proposed for a gate it does not match; a multiselect row shows its own state in text (`F41`) | The negative controls: an adopter who declares nothing above the floor writes a byte-identical profile, proving questions were removed rather than answers; the provenance allow-list grows by the `GATE_CATALOGUE` sentences and nothing else, or the packet has broken its own guarantee; and a repository whose only file is `README.md` yields no precondition proposal at all |
| `ACT-033` | Scaffold the artefacts an adopter does not have, instead of asking them to name one | maintainer | maintainer | `done` | `ACT-032` | hard | yes — it would make `adopt` write files into an adopting repository beyond the profile, which is a new class of action for this tool | high — creating a governance artefact does not create the practice it stands for, so what is written and how it is labelled is the whole question | An adopter with no register is offered one built from a shipped template, and the gate then points at a real artefact rather than the closest wrong file | Committed to by `DR-41`; not started. The framework currently ships no register or change-log template, so this packet must author what it scaffolds rather than merely place it |
| `ACT-034` | Remediate `adopt`, phase 7: stop the interface presenting itself as more settled than it is | maintainer | maintainer | `done` | `ACT-032` | hard | yes — it changes what every adopter reads on every screen, and three of its findings are the interface making claims its evidence does not support | medium — the defects are each reproduced at the design width rather than inferred, and the judgement is about what a display may assert, not about what the profile records | A truncated explanation says it was truncated; a gate with no answer is not counted as answered; a candidate list with no match says so; the step counter agrees with the sections; and a value the wizard already computed is proposed rather than asked | The negative controls: each finding re-broken deliberately and seen to fail first, because `F41`'s test passed against the unfixed widget on its first writing; and the provenance allow-list may not grow, or the packet has broken its own guarantee |
| `ACT-035` | Close the gaps left open by `ACT-033` and `ACT-034`, including `F47`'s date granularity | maintainer | maintainer | `done` | `ACT-033` | hard | yes — it widens a published schema field and changes how two published controls read it, in every adopting repository | high — the remedy was put to the maintainer explicitly rather than chosen, because all three candidates change what `SP033`/`SP035` mean and an agent may not decide a control's semantics | `effective_from` accepts an instant as well as a date and existing profiles stay valid; a run cancelled at the review and resumed still reaches the scaffold offer; the review screen names the files it is about to create; and the defaults screen is readable at 80 columns | The negative controls: the resume defect reproduced against the pre-fix code before the test is trusted; every existing date-only profile still validates; and `SP033` still refuses a genuinely future instant |
| `ACT-036` | Do everything that can be done for `ACT-007` and `F6` without a party outside this repository | maintainer | maintainer | `done` | `ACT-035` | hard | yes — it adds a file to the payload every adopter receives, and it touches what the integrity check establishes, which is the subject of this repository's oldest open finding | high — the judgement is about what may be CLAIMED: `F6` names the maintainer as the party who cannot close it, so the work is narrowing what is left for an external party, and any wording that reads as closure would be the fabricated-validation failure this framework polices | An adopter can recompute the framework digest from a file they hold rather than only compare two values the installer wrote; `ACT-007`'s checkable clauses are verified and recorded; and `F6` remains OPEN with its remaining distance stated | The negative controls: the new check is seen to fail against a tampered manifest; and `F6`'s entry still says open, because nothing here gives the check an external anchor |
| `ACT-037` | Rebuild `RELEASE_PLAN` item 9's review packet against the framework as it now is | maintainer | maintainer | `done` | `ACT-036` | hard | yes — it is the request sent to a party outside this repository, and its own text is what stops that party's findings from being over-read or under-scoped | high — what a reviewer is pointed at determines what the review can find, and the surfaces that changed most since the packet was written are the ones carrying the newest and least-examined risk | The packet names only files that exist, its evidence-bundle command reproduces the set the prompt declares, and its questions test the claims the framework makes today rather than the ones it made in August | The negative controls: the regeneration command is run and its output checked against the declared list; and the packet states what a same-provider review already covered, so its findings are not read as independent of that |
| `ACT-038` | Act on the cross-provider adversarial review: every finding accepted or partly accepted | maintainer | maintainer | `done` | `ACT-037` | hard | yes — it changes the wizard's most-cited binding rule, corrects a normative document that contradicted itself, and changes what an adopting repository's profile discloses about its own controls | high — the reviewer returned FAIL, and the judgement is which findings hold: the verdict is theirs, the response is the maintainer's, and a finding is neither accepted because a reviewer asserted it nor dismissed because its evidence was imperfect | `effective_from` is asked again and the binding rule states exactly what the tool may supply; `CONFORMANCE_LEVELS.md` no longer contradicts itself; an adopter can tell a verified control from a declared one by reading their own profile; and the review packet's own two defects are fixed | The negative controls: each accepted finding seen to fail against today's text before its fix; the verified/declared label joined to `VERIFIED_CONTROLS` so it cannot drift; and the provenance allow-list must not grow, because a rendered comment is not a value |
| `ACT-039` | Register the actions only a human can take, and complete the agent-completable queue behind them | maintainer | maintainer | `done` | `ACT-038` | hard | no — it changes no control, no schema and no adopter-facing behaviour; it records what is blocked on a human and clears what is not | high — the judgement is what an agent may NOT do unattended, and the failure mode of an overnight run is not stopping but guessing: a decision made without the maintainer, landed in a merged commit, is worse than the work not being done | `org/HUMAN_ACTIONS.md` lists every action reserved to a human with why, what is blocked behind it and what is prepared; and every queue item that needs no decision is complete | The negative control: anything that would have been put to the maintainer as a question is present in the register UNMADE, not resolved on an assumption |
| `ACT-041` | Emit the seven skills to every agent's path, not only Copilot's | maintainer | maintainer | `done` | `ACT-040` | hard | yes — `AGENTS.md` tells every adopter the skills' gates are "not optional" while installing them where Claude Code cannot read them, so the framework's own stated mandatory workflow was unreachable for one of the two agents it ships for | low — `DR-30` already decided the pattern (one body, several emitters) and this applies it to the artefact class it missed; no new policy, no transformation, the SKILL.md body is unchanged and gains a second destination | `.claude/skills/*/SKILL.md` and `.github/skills/*/SKILL.md` both hold the same seven skills in a freshly installed repository, and the conformance block names both | The test is seen to fail at 0-of-7 and calibrated on a partial break withholding one skill, since a total break passes any check that only asks whether the directory exists |
| `ACT-040` | Correct two false claims on the public front door, and the same one inside the tool | maintainer | maintainer | `done` | `ACT-039` | hard | yes — one of them is the first command an adopter runs, printed by the tool itself, and it cannot work | medium — the corrections are factual rather than editorial: a package that is not published cannot be `pip install`ed, and a rule the project formally amended cannot still be advertised in its old form. Whether to publish to PyPI is a release decision and is NOT taken here | `README.md` and `INSTALL.md` name an install command that works, verified by running it into a clean virtualenv; and no live document repeats the binding rule wording `DR-46` corrected | The negative control: the replacement command is executed end to end from a fresh venv before it is written down, because the defect being fixed is precisely an instruction nobody ran |
| `ACT-042` | Record the adversarial product review of 2026-09-02, its remediation plan, decisions and findings | maintainer | maintainer | `done` | `ACT-041` | — | yes — it records nineteen findings, four decision records and the plan every later activity cites | medium — the review's verdict is the reviewer's; which findings and decisions are recorded is the maintainer's, taken in the review session | `audit/ADVERSARIAL_PRODUCT_REVIEW_2026-09-02.md`, `org/REMEDIATION_PLAN.md`, `DR-47` to `DR-50`, `F59` to `F77` and rows `ACT-042` to `ACT-046` are in the tree, `check_code_registers.py` passes, and the maintainer has merged the pull request | The maintainer's authorisation in the review session for each decision and activity, cited in each record; the fourteen CI steps green — run from `.venv/bin/python` at `dca9236` on 2026-09-02 (180, 195, 88, 6, 44, 20, 18, 21, 5, 178 files, 209, 10, 64, PASS) and the `Standard self-check` workflow green on PR #43; merged to `main` as `905b5ce` on the maintainer's instruction in the `ACT-043` session |
| `ACT-043` | Remediate `adopt`, phase 8: the eight defects that make the wizard unfinishable or destructive | maintainer | maintainer | `waiting_for_review` | `ACT-042` | hard | yes — it changes what every adopter sees on the gates screen and whether a real profile can be overwritten | low — every remedy is fixed by the finding; no rule changes | The gate status radios render at 80×24; the gates screen is seeded on the defaults route; an empty choice is refused at the field; a real profile is never mistaken for the template; `None` is blank; a validation error survives the focus move; quitting at the resume prompt keeps the draft; the resume header renders; help text is styled (`org/REMEDIATION_PLAN.md` §4 phase 0) | Each regression test seen to fail before its fix and pass after; the eight images from the review re-taken and read; `H1` re-run by the maintainer. Delivered on `claude/act-043-phase-0` (2026-09-02): eight commits, one per item, each with its test seen failing then passing and its finding closed in the same commit; `F59`, `F60`, `F63`, `F64`, `F68`, `F74` closed, `F67` closed for its help-text part, `F73` left open with the reason recorded; items 0.3 and 0.2 landed in that order because 0.2's hint assertion depends on 0.3; the fourteen CI steps run from `.venv/bin/python` are quoted in the pull request. Awaiting the fresh-session review and the maintainer's `H1` run |
| `ACT-044` | Remediate `adopt`, phase 9: proposal-first adoption with a provenance record, one gate list, validator parity, discovery that excludes the framework | maintainer | maintainer | `in_progress` | `ACT-043` | hard | yes — it changes what every adopter is asked, what the profile says about its own origin, and what discovery may propose | high — bounded by `DR-47` and `DR-48`; the level stays a human decision; no scope decision is ever supplied by the tool | Eight to twelve fields before the review on the two fixtures the prototype used; the provenance record written and read by `test_provenance.py`; the header true; a gate list with no pre-marked statuses and a recorded bulk command; a profile that passes the wizard passes its first check; no framework-owned path proposed (plan §4 phase 1) | The persona budget measured, not estimated; the prototype's profile equality reproduced on the real code; the `SP` parity test green; a repository containing only the install payload yielding no proposals |
| `ACT-045` | Remediate `adopt` and `check`, phase 10: non-interactive adoption, `doctor`, output formats and exit codes, the bounded front-door pass, generated numbers and link checks | maintainer | maintainer | `planned` | `ACT-044` | hard | yes — a public exit-code contract, a new command, and the first sentence a stranger reads | medium — bounded by `DR-49` and the release plan's item 8 | `adopt --propose` and `--answers` round-trip the prototype's answers to the same profile; `doctor` reports the five facts that stopped the stranger install; `check --format json` and `sarif` validate; exit codes as `DR-49` decides; README and `INSTALL.md` as bounded; every number and link in the documents checked by `check_code_registers.py` in both this repository and an installed checkout (plan §4 phase 2) | A clean-container run of every documented command, on a machine with a global `core.hooksPath`; a SARIF file accepted by a validator; the answers file replayed by CI |
| `ACT-046` | Remediate the evidence machinery, phase 11: the 80×24 snapshot suite and budget test, register parity, the schema change, docstring style | maintainer | maintainer | `planned` | `ACT-045` | hard | yes — a schema change and a new golden suite | medium — bounded by `DR-50`; snapshots are goldens and never regenerated to absorb an unexplained diff | Every screen snapshot-tested at 80×24 including a focused gate status; the budget test asserting the measured numbers; `check_code_registers.py` asserting body-versus-index status; the schema change with both examples updated; the suite count in `CLAUDE.md` and the workflow's "every step ran" loop updated in the same change (plan §4 phase 3) | The snapshot suite seen to fail on a one-character stylesheet change; the parity check seen to fail on one deliberately contradicted status in a scratch copy |
## Notes on the entries

`ACT-042` to `ACT-046` were authorised by the maintainer in the review session of 2026-09-02
(https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs), on the rows drafted in `org/REMEDIATION_PLAN.md` §3, together with `DR-47` to
`DR-50` and findings `F59` to `F77`. The review that produced them found the wizard unfinishable on
the route the maintainer uses, and its second pass withdrew two of its own first-pass
recommendations for breaching the binding rule; the plan carries the corrected forms only. The
four phases are sequential by design: each opens with the decision record it needs, and each is
implemented by a fresh session from the plan alone, so that the plan is tested by being read cold.

`ACT-002` and `ACT-003` are both raised by `DR-16` and are deliberately **not** resolved by
`ACT-001`. `DR-16` records the reasoning: the vendored-set question affects every future adopter and
must not be answered as a side effect of a packet whose objective is getting the publisher
conformant, and `F12` is recorded rather than fixed because its general remedy is larger than the
CI mitigation this work applies.

`ACT-004` is separated from `ACT-001` for a stronger reason than scope. It changes the behaviour of
a published control, and doing that inside the work whose objective is making that control pass is
indistinguishable — in the diff, to a reviewer later — from adjusting the control to obtain a pass.
It carries no dependency on `ACT-001` precisely so that it can be judged on its own evidence, and it
was **executed first** at the maintainer's direction: self-conformance established through an
instrument known to be wrong is not worth establishing. `DR-17` records the decision; `F15` records
the second defect that auditing the first one exposed.

`ACT-001` and `ACT-004` moved to `done` on 2026-08-31 when the maintainer merged
[PR #2](https://github.com/pipoventures/surfaceplate/pull/2). Both had stood at
`waiting_for_review` with their definitions of done met and their evidence in place; the merge is
the human review act that was outstanding, and the status records that act rather than an agent's
assessment of it. Neither was marked `done` before it happened.

`ACT-005` moved to `done` on 2026-08-31 when the maintainer merged
[PR #3](https://github.com/pipoventures/surfaceplate/pull/3). Its evidence was complete before the
merge and the merge is the review act, on the same basis as `ACT-001` and `ACT-004` above.

`ACT-006` exists because a claim that the open findings had "reached the honest floor" was wrong,
and was challenged. Re-reading each finding rather than a summary of it showed three with internal,
available work. The error was sorting findings by whether the *structural* problem was solvable, and
missing that several carry a false statement sitting in the repository now — `F10` most sharply, an
evidence document reporting `PASS` for a check `DR-6` abolished.

`ACT-007` covers the publication pass. Its judgement entry reads `high` for a specific reason: the
maintainer first chose to rewrite history to scrub the former organisation's name, and preparation
showed that choice would destroy the verifiability of four releases, invalidate the SHA citations a
second time, and still leave a visibly-redacted and suggestive history — so it would have paid the
full cost without achieving the goal. `DR-23` records the reversal and the reasoning.

`ACT-008` arose from assessing the framework against two target adopter profiles. The assessment
itself is deliberately not recorded here; what it produced that belongs in the repository is a
defect, and defects go in `org/FINDINGS.md`.

`ACT-009` implements a decision taken elsewhere. The reasoning is recorded in `hermes` and is cited
rather than restated here, per the standing constraint that commercial rationale does not live in
this repository. What belongs here is the architectural consequence: which licence covers which
paths.

`ACT-010` closes no gap by itself. It records an architecture and states plainly what is currently
checked, so that the four packets after it build to one shape rather than establishing one by
accident — and so that the honesty gap closes on the day the architecture is agreed rather than on
the day the last validator lands.

`ACT-011` is where the architecture met the repository. `DR-25` predicted that surfaceplate would
have to satisfy its own controls under the new patterns, and that failing to would be evidence
against the design rather than grounds for an exemption. It failed immediately: `dependency_lock`
was declared with nothing pinned at all. The design survived; the repository did not, and `F21`
records it.

`ACT-012` amends `DR-25` rather than working around it. That record predicted
`implementation_reference` would carry a status-check name for pattern B; implementation showed a
status check is a *job*, and one job here runs every suite, so both controls would have pointed at
the same name and the check would have been identical for both. `DR-25` states that a pattern which
does not fit means the record is wrong — so it is amended in place.

`ACT-013` restores something that was dropped. The scope review kept `H` unconditionally and
ordered it before the first record validator; patterns D, A and B were a larger substitution for
`G′` than that review anticipated, and `H` was overlooked in the process. Recorded plainly because
the sequence was agreed and then departed from without anyone deciding to.

`ACT-014` is the first pattern surfaceplate cannot demonstrate on itself. It sits at `standard`
and has no material results, no governed methods and no overrides, so there is nothing genuine for
it to record. Declaring the four controls against four empty directories would demonstrate only that
an empty register passes — the weakest thing pattern C can prove — while making the published
profile look like it holds records it does not. The proof is by fixture instead, and the absence of
a live self-demonstration is recorded in `DR-26` rather than left to be noticed.

`ACT-015` corrects a decision taken on a misread contract. The separation of `provenance` from
`run_lineage` was agreed as each obliging different optional fields; re-reading
`method-run-lineage.schema.yaml` showed the schema already requires all of them on every completed
run, so both controls would have obliged nothing. The correction was made before any code was
written, and the separation now runs on cross-reference direction instead. The original preview was
wrong on a matter of fact, and the record says so rather than presenting the second answer as the
first.

`ACT-016` is the first work in this repository raised by a repository that is not this one. Both
findings were unreachable from here: surfaceplate's own profile has never needed a placeholder-scan
exemption whose rationale quotes the token, and its own gates all point at artefacts for which the
`SP032` remedy's wording happens to read sensibly. Neither is exotic. Both appeared within an hour
of the framework meeting a repository it did not write.

`ACT-017` is the second item raised by Plyego and the first that blocked adoption outright. It is
also the plainest instance of this repository's own recurring defect appearing in itself: `SP038`
fires only when a gate claims `local_hook`, so the standard has always permitted a repository with
no surfaceplate hook — while the installer refused to produce one. Two parts of one framework
disagreeing about the same obligation is the defect it names more often than any other.

`ACT-018` is the most uncomfortable item in this register. Every packet before it was governed by
doctrine loaded from the maintainer's own machine, never by the 501 lines of agent instructions this
repository publishes and installs into others — because those sit in `.github/instructions/`, which
the agent doing the work does not read, and this repository has no `CLAUDE.md` at all. The framework
has been shipping instructions it has never itself been subject to. Raised by Plyego, like `ACT-016`
and `ACT-017`, and unreachable from inside for the same reason all three were.

`ACT-019` is the first item in this register that resumes the recorded `RELEASE_PLAN` order
(`3 → 1 → 2 → 9 → 5 → …`) rather than answering something Plyego raised. It is also the first to
edit `work_registration`'s own `gated_activity.paths` — the gate that is live over the very paths
this item moved. Eight of this repository's own gate declarations needed correcting for the move;
each was checked against the reasoning `core/PREREQUISITE_GATES.md` gives for *narrowing* a gate's
paths being safe against the history audit, where *renaming a precondition artefact* is not — `F30`
fired on exactly that second kind of edit, for the second time in one session.

`ACT-020` retires part of an existing artefact rather than only adding a new one.
`prompts/github-copilot-adoption-wizard.prompt.md` has called itself "the wizard" since before the
`0.12.0` rename; `surfaceplate adopt` takes that name from here, and the prompt is renamed and
narrowed to the phases it still uniquely does (bounded implementation, downstream of a profile the
CLI now produces). The terminal-vs-browser design question was not decided at a desk: three moments
of the flow were mocked up as a clickable comparison artifact and walked through with the
maintainer before this packet's plan was written, and the maintainer's own first reaction —
"how does someone answer in a prompt back" — is why that artifact exists rather than a written
argument alone.

`ACT-005` to `ACT-026` were registered **before** implementation begins, not alongside it. `work_registration` is
live over `scripts/**` and `schemas/**`, which is exactly what item 4 changes, and a gate satisfied
retrospectively is the failure mode `core/PREREQUISITE_GATES.md` warns is most common — satisfied on
paper, violated in spirit.

`ACT-021` is the second item resuming the recorded `RELEASE_PLAN` order (`3 → 1 → 2 → 9 → 5 → 8 → 9
→ 10`), and the first activity in this register whose product is a request sent to a party outside
this repository rather than a change inside it. That framing is why its definition of done stops
where it does: it produces something ready to hand off, not a review that has happened. Nothing here
marks Gemini as the independent validator `org/decisions/README.md` records as not existing — item
10 alone can do that, and this entry does not claim otherwise.

`ACT-022` is item 9's first actual finding — the review `ACT-021` requested came back, and it was
right. `surfaceplate/adopt/sections.py`'s `ask_controls` hardcoded rationale text for all three
baseline controls, and `ask_gates` did the same for the four UI gates it auto-marks
`not_applicable` when `builds_user_interface` is false — both bypass `Prompt` entirely, which is
exactly what the module's own docstring says never happens. Independently verified against the code
before accepting it: two of Gemini's other findings did not survive that check (`adoption.deferrals
= []` is a disclosed limitation in `DR-32`, not an invented claim; the over-engineering finding
recommending gate auto-masking is wrong about the code, which already auto-masks). `ACT-020` is not
reopened — this is a new activity against merged work, the same way a bug found after merge always
is.

`ACT-023` is the review's third finding, decided rather than left open. It touches nothing in code:
`org/decisions/DR-33.md` records why the proposed schema conditionals would not have closed the gap
described — the checker already runs schema validation as part of itself, so no bypass path exists
for a schema-only gate to close — and why the cost side (a second, hand-maintained copy of
`CONFORMANCE_LEVELS`) is the same shape `F23` and `DR-6`/`DR-9` already closed elsewhere in this
project. Recorded so the same idea, raised again by a future reviewer, finds the reasoning already
done rather than starting from nothing.

`ACT-024` substitutes one named adopter for the other, mid-plan, for a reason external to this
repository: Plyego's own Google Cloud migration, not anything found wrong with Plyego itself. It is
the second time this framework has been run against a repository it did not write, and the first
time that run needed no fix to reach a clean result — worth recording plainly rather than treated as
unremarkable, since `DR-28`'s own reading of Plyego's result leaned on exactly the contrast a second
data point now provides. The one real defect found (`--no-hooks`'s misleading next steps) was
unreachable from self-check for the same structural reason `F25`/`F26` were: surfaceplate has never
run its own declined-hook path against itself for real.

`ACT-025` is the first defect found by a human standing in front of surfaceplate's own output, not
by a probe or a review. Running the installer against Plutos for real, the maintainer's own words —
*"I run it and didn't understand what was happening... we don't give the user any alternative or
way out. It just stops"* — are the finding. `F27` gave the hook-conflict refusal a third route in
principle; this is the discovery that a route named in the message and a route the reader can
actually take are not the same thing, and that the message never said whether the conflict was
about this one repository or the whole machine, which turned out to be the fact that mattered most.

`ACT-026` is the second defect found by a human standing in front of surfaceplate's own output, and
the most severe: the maintainer's own live, unscripted `adopt` session against Plutos hit a data-loss
bug (`F36`) that destroyed roughly twenty minutes of real answers, on top of a genuine fit gap his
own words named directly — *"Extremely long and difficult... really bad experience."* He set an
explicit condition before any of it was coded: *"Until we don't have a complete remediation plan
that I approve you don't implement anything."* What shipped here is Phase 1 of the resulting,
maintainer-approved two-phase plan (`DR-35`) — the bug fix, a mode choice, dual-register content for
all 31 catalogue items, detected signals on the level screen, example answers on every reachable
rationale field, and basic resumability — re-run against the exact scenario that prompted it before
being considered complete. Phase 2, a Textual rendering rewrite, is scoped in `DR-35` but not
started.

## The 2026-09-01 status sweep

`ACT-008` to `ACT-025` moved to `done` on 2026-09-01. All eighteen had stood at
`waiting_for_review` with their definitions of done met and their evidence in place, on exactly the
basis this register already recorded for `ACT-001`, `ACT-004` and `ACT-005`: **the merge is the human
review act**, and the status records that act rather than an agent's assessment of it.

The status was stale, not the work. Every one of the eighteen was verified against `main` before
being moved — the commit citing the activity, and the merge commit that brought it in:

| Activity | Merged via | Activity | Merged via |
|---|---|---|---|
| `ACT-008` | [#4](https://github.com/pipoventures/surfaceplate/pull/4) | `ACT-017` | [#13](https://github.com/pipoventures/surfaceplate/pull/13) |
| `ACT-009` | [#5](https://github.com/pipoventures/surfaceplate/pull/5) | `ACT-018` | [#14](https://github.com/pipoventures/surfaceplate/pull/14) |
| `ACT-010` | [#6](https://github.com/pipoventures/surfaceplate/pull/6) | `ACT-019` | [#15](https://github.com/pipoventures/surfaceplate/pull/15) |
| `ACT-011` | [#7](https://github.com/pipoventures/surfaceplate/pull/7) | `ACT-020` | [#17](https://github.com/pipoventures/surfaceplate/pull/17) |
| `ACT-012` | [#8](https://github.com/pipoventures/surfaceplate/pull/8) | `ACT-021` | [#17](https://github.com/pipoventures/surfaceplate/pull/17) |
| `ACT-013` | [#9](https://github.com/pipoventures/surfaceplate/pull/9) | `ACT-022` | [#18](https://github.com/pipoventures/surfaceplate/pull/18) |
| `ACT-014` | [#10](https://github.com/pipoventures/surfaceplate/pull/10) | `ACT-023` | [#19](https://github.com/pipoventures/surfaceplate/pull/19) |
| `ACT-015` | [#11](https://github.com/pipoventures/surfaceplate/pull/11) | `ACT-024` | [#20](https://github.com/pipoventures/surfaceplate/pull/20) |
| `ACT-016` | [#12](https://github.com/pipoventures/surfaceplate/pull/12) | `ACT-025` | [#21](https://github.com/pipoventures/surfaceplate/pull/21) |

**`ACT-007` was deliberately NOT moved, and that is the finding this sweep produced.** No commit in
`main` cites it, so the evidence that closed the other eighteen does not exist for it. Its
checkable clauses do hold — `F13`, `F15` and `F16` are closed, `DR-22` and `DR-23` are recorded, and
the repository is public, so the publication decision was plainly made and executed. But its own row
reserves that decision to a human (*"publication is not reversible"*), and an agent may not conclude
a human decision by observing its apparent effect. **It stays open until the maintainer closes it.**

**The sweep itself is evidence of a control gap worth stating.** This register's own rule is that
status travels *in the same commit* as the work, and that *"a register updated afterwards is a
reconstruction, not a record"*. Eighteen entries drifting for a month is that rule not being
followed, and nothing detected it — the identifier checks verify that IDs exist and agree, not that
a status matches the repository's actual history. This paragraph records the drift rather than
quietly tidying it away.

`ACT-033` is the first time this tool writes anything into an adopting repository beyond the
profile, which is why `DR-41` split it out rather than folding it into the reduction work. The
design turns on one measured fact: **every shipped template deliberately carries placeholder
tokens** (`F15`), and `SP032` rejects a precondition artefact containing one - so the intuitive
implementation, copying a template into place, would have created a gate artefact that fails the
checker on the very next run. `seeds/` exists because a seed is finished and holds no entries, where
a template announces that it is not finished.

**The packet's headline assertion turned out to be false, and writing the test is what found it.**
A bare repository still cannot reach a clean check: the artefact is created today, `effective_from`
binds by date, and commits made earlier the same day were made when it did not exist. Binding from
tomorrow is what the artefact's history would justify and `SP033` refuses it. `F47` records the
gap; the test asserts what is actually true rather than resting on the adoption grace window, which
returns success regardless and would have made a false claim pass.

`ACT-007` moved to `done` on 2026-09-01, **on the maintainer's judgement rather than on a complete
mechanical verification**, and the difference is recorded because it is the whole basis.

Three of its four done-clauses verify directly: `F13`, `F15` and `F16` are Closed; `DR-22` and
`DR-23` are recorded; and publication was not merely decided but **executed exactly as `DR-23`
specified** - a new public repository whose first commit is the current tree (`1b0df98`, no earlier
history), with `surfaceplate-history` private and archived. The 403s that were `DR-23`'s premise are
themselves superseded: a `main-required-checks` ruleset is active.

The fourth clause - *"the working tree carries no reference to the former organisation"* - is
verified for **the forms `DR-23` says the token took**. It was embedded as
`urn:[organisation]:uk:risk-ai:...` in every schema `$id`, and `tests/check_identifiers.py` Rule 2
asserts every URN authority equals the declared one, Rule 1 does the same for the GitHub
organisation, Rule 3 rejects an undeclared token sharing the organisation's stem. All pass. The
public repository's history carries none of it by construction, because its first commit is the
clean tree.

**What is NOT verified is a bare prose mention**, and closing on judgement rather than on a check is
the maintainer's decision, taken with that stated. `F49` records the residue as a standing gap rather
than leaving it implied by an activity marked `done`.

**Two attempts to verify it mechanically both produced false alarms, which is part of why it was
closed this way.** The first used `urn:[a-z0-9-]+:` to recover the token from the archive and matched
inside the word `return:` - `check_identifiers.py` uses `\burn:` for exactly that reason, and the
ad-hoc copy did not. The second, corrected, recovered an authority segment reading
*"redacted"* - a redaction marker left in the archive, not an organisation - and reported 15
working-tree files that were all ordinary uses of that word in security and audit documents.
(Writing that segment out in its full URN form here failed Rule 2 while this note was being
drafted, which is the coverage being cited demonstrating itself.) Neither run found anything; both looked as though they
had. `DR-23`'s design is what defeats the tooling: the record describes the token rather than
reproducing it, so nothing working from the public repository holds it.

`ACT-035` set out to close recorded gaps and found a worse defect than any of them. `F47` had been
written on the assumption that `effective_from: 2026-09-01` meant midnight. It never did: `git log
--since=<bare date>` is parsed by approxidate, which fills the missing time from the **current
clock**, so the prerequisite audit's window slid forward all day and a violation visible at 09:00
was gone by 23:00. Against this repository's own adoption-day fixture the bare form saw **0 of 4**
same-day commits. That is `F48`, it is a published control failing silently permissive, and it was
found by *calibrating a fix* rather than by reasoning about the problem.

Two smaller lessons travelled with it. **A flake explained is not a flake diagnosed** - `ACT-033`'s
intermittent failure was attributed to a fragile stdout capture, and the capture was fragile, but it
sat on top of this. And **`ACT-033`'s fix for the resume defect did not work**: moving the offer
before the review was necessary and not sufficient, because the condition still asked whether the
artefact ANSWER was blank when it should have asked about the FILE. Writing the regression test that
`ACT-033` had been shipped without is what found that.

`ACT-034` came from a full-path audit the maintainer asked for after stopping a real run: every
screen rendered at **80x24**, the size the interface is designed for and the size no previous packet
had actually looked at. Five findings, and they are one defect wearing five faces - **the interface
asserting more than its evidence supports**, which is the thing this framework exists to stop other
people doing. A truncated sentence claiming to be whole (`F42`), a counter claiming completion
(`F43`), a list claiming plausibility (`F44`), a step number claiming position (`F45`).

`F46` is the serious one and it is ours: `ACT-032`'s caret change put the conformance-level screen
into an **unbounded redraw loop** - 4,484 redraws for one paint - on every repository whose answers
recommend `standard` or `full`. `ACT-032`'s own tests passed against it, because they read
`highlighted` after one pause and it is correct on half the iterations. Reading state cannot see a
loop; counting the work can.

`ACT-032` answers a challenge rather than a defect report: *"why so many parameters? can't we just
make decisions for the user according to best practice? if they had a good system in place they
wouldn't be using this package."* Walking four personas through every route measured the answer, and
the measurement moved the priority. The obvious culprit was the gate catalogue, which dominates the
count for every persona above `essential`. But the persona this package most exists for — a solo
maintainer with nothing in place — sits at `essential`, faces only 6 gate fields, and is still asked
**57** questions, because `controls` asks 30 of them: **23 concern eight controls above that level's
own floor**, which choosing `essential` had already declined. A level is a floor, and the wizard was
making adopters decline it item by item while `defaults.propose_controls` computed the same answer
silently. `F40` is the second half — the same persona's only discovered artefact is `README.md`, and
the wizard proposed it as the precondition for `work_registration`.

**Scaffolding the artefacts an adopter does not have is deliberately NOT in this packet.** It is the
real answer to a repository with nothing to name, and it would make `adopt` write files beyond the
profile — a different class of action, scoped to `ACT-033`.

`ACT-031` moved to `done` when the maintainer merged
[PR #27](https://github.com/pipoventures/surfaceplate/pull/27), and follows the first adoption this
framework has ever completed end to end - and the profile
it produced is unusable, which is the finding. Seven gates carry `asdf`, because `tui/app.py` built
the gate catalogue from `plan.gate_plan(...)` without passing the repository scan, so every artefact
field fell back to a plain text box while the controls screen - which goes through `section_plan` -
correctly offered dropdowns. **The screen-to-plan join could not have caught it**: it compares field
ids, and the ids are identical whether a field renders as a dropdown or a text box. That is `F37`'s
shape one level up - the right questions asked in the wrong form - and the join now compares kind.

`ACT-030` builds the remedy `F30` named and deliberately left unbuilt through four packets. The
restraint was right at the time — `ACT-019` and `ACT-027` both hit the defect and both recorded it
rather than fixing it in passing, which is the scope discipline this project's working method asks
for. What changed is the evidence: the same mechanism has now produced false violations twice, from
renames this repository chose for its own good reasons, and `DR-22`'s warning about an accumulating
pile of exception records applies to the two it has already filed.

`ACT-029` is the first packet in this sequence whose direction came from the maintainer rather than
from a defect report: having run the phase-3 build against Plutos and been unable to finish it, his
conclusion was that the interaction model itself is wrong — *"free text is confusing and really
prone to errors... the wizard should do a discovery of the repo first to identify what is the
potential candidate for each question."* Two of the five faults he reported turned out to be this
project's own code rather than the framework it builds on: a non-scrolling container clipped every
screen, and the multi-line blocker had a second, unguarded path that would have surfaced as a raw
traceback. `F38` records both. It also reverses half of `F37`'s remedy — help returns beside the
field it belongs to — which is recorded as a reversal on evidence rather than made quietly.

`ACT-028` exists because `ACT-027` shipped a green suite and a broken screen. Every Phase 2 test
asserted structure — field-id joins, widget counts, status transitions — and none asserted what the
screen renders, so six user-visible defects passed 87 checks; the agent then published screenshots
captioned as proof of fidelity without looking at them. `F37` records the class rather than the six
symptoms, because the transferable lesson is that structural checks cannot see a rendering fault and
adding more of them could only have confirmed the error. The remedy is a new suite that reads the
compositor's own rendered lines and asserts named properties over them.

`ACT-027` is the first activity in this register to **replace a dependency an earlier decision
record had fixed**, and it proceeded only because the maintainer was asked and answered:
`.github/skills/dependency-update/SKILL.md` makes exactly that a mandatory stop, and `questionary`
was `DR-32`'s choice. What it delivers is the interface the mockup approved before `ACT-020` was
built and which `ACT-020` then could not render. What it delivers that nobody asked for is more
interesting: the binding rule this whole package exists to honour — *it asks, the human answers, the
tool writes* — had never actually been proven, and this repository's own test file had said so since
`ACT-022` without the gap being closed. Splitting `sections.py` into pure functions made a sentinel
provenance walk possible, so the claim is now checked rather than asserted, and the list of things
the tool writes on its own behalf is 48 entries long and reviewable. `ACT-026` moved to `done` when
the maintainer merged [PR #22](https://github.com/pipoventures/surfaceplate/pull/22).

`ACT-002` and `ACT-003` are both answered by `DR-20`. They, and `ACT-006`, moved to `done` on
2026-08-31 when the maintainer merged [PR #9](https://github.com/pipoventures/surfaceplate/pull/9)
— the same basis as the entries above: the merge is the human review act, and the status records
that act rather than an agent's assessment of it.

*Worth recording about that merge.* PRs #6, #7 and #8 were stacked and merged into their base
branches rather than into `main`, so their content never reached the trunk despite GitHub marking
them merged. PR #9 recovered all of it, verified file-by-file rather than inferred. Stacking is the
practice that caused it, and it is not repeated.

`ACT-002`'s own framing had to be corrected before it could be answered. It asked whether the
vendored set should shrink "to what is mechanically read", but `check_integrity` digests every file
in the install record, so all 27 are mechanically read — only **four** have their content
interpreted. Shrinking would not have removed unused files; it would have removed 23 files from
integrity protection. The decision keeps the set, governs membership by a stated principle, and
addresses the one real cost — a 27-file upgrade diff that trains reviewers to wave installer diffs
through, including the executable inside them.
