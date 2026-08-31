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
| `ACT-007` | Publication pass: sanitise, close `F13`/`F15`/`F16`, decide publication | maintainer | maintainer | `waiting_for_review` | — | hard | yes — it changes a published control (`SP032`), ships two new obligations to adopters, and decides where the project lives | high — publication is not reversible, and the history question had three plausible answers with very different costs | The working tree carries no reference to the former organisation; `F13`, `F15` and `F16` are closed or their obligations shipped; `DR-22` and `DR-23` recorded; the full-history sweep is runnable | Seen-to-fail probes in both directions for the exemption mechanism; the 403s read live; the former organisation's footprint counted across all commits; a full backup bundle taken before any of it |
| `ACT-008` | Remove inherited internal jargon from the public tree (`F18`) | maintainer | maintainer | `waiting_for_review` | — | hard | yes — `adapters/**` and `SETUP_GUIDE.md` are adopter-facing, and `adapters/` is in the install payload | low for the live guidance; the judgement is in what NOT to touch — the audit records are true statements about a repository that had that name | No inherited product or methodology name remains in live guidance; historical audit records keep their text under an explanatory note | A grep showing the remaining occurrences are confined to `audit/`, each under a note; suites and manifest accounted for; both checker copies PASS after reinstall |
| `ACT-009` | Implement the dual licence decided in `hermes` (`F19`) | maintainer | maintainer | `waiting_for_review` | — | hard | yes — it changes the terms under which every copied file is licensed, on a published artefact | low on mechanism, and the boundary is already locked; the judgement was made in `hermes` and is cited rather than retaken here | `LICENSE-DOCS` carries CC0-1.0, `NOTICE` exists, and `README.md` states which licence covers which paths | The CC0 text fetched from creativecommons.org and diffed byte-for-byte against the SPDX copy; suites and manifest accounted for; both checker copies PASS |
| `ACT-010` | Architecture for provable controls, and say which are checked (`F20`) | maintainer | maintainer | `waiting_for_review` | — | hard | yes — it fixes the shape every future control validator must follow, and changes what a passing check reports | high — the architecture constrains eight validators that follow it, and the boundary between what can and cannot be proven is a judgement the whole design rests on | `DR-25` records four patterns and the meaning of `implementation_reference`; `CONFORMANCE_LEVELS.md` and the checker's output distinguish a checked control from a declared one | The demonstration reproduced — a profile claiming `full` with no records still passes, and the output now says why; suites and manifest accounted for |
| `ACT-011` | Patterns D and A: three controls become checked; surfaceplate acquires a lock (`F21`) | maintainer | maintainer | `waiting_for_review` | `ACT-010` | hard | yes — it changes what a conformance result establishes, and pins the runtime for every adopting repository | medium — the patterns were fixed by `DR-25`; the judgement here was which versions to pin and whether to record the early start on item 1 | `dependency_lock`, `assurance_findings` and `documentation_authority` verified rather than declared; `pyproject.toml` pins both runtime dependencies; the level banner shrinks from 3 of 4 to 2 of 4 | Versions resolved in a clean environment with all five suites run against them before pinning; `SP051` and `SP052` seen to fail in five ways and pass in one; the drift guard seen to fail both ways |
| `ACT-012` | Pattern B: `deterministic_tests` and `contract_tests` become checked | maintainer | maintainer | `waiting_for_review` | `ACT-011` | hard | yes — it adds an obligation on every adopter at `standard` and above, and amends a published decision | medium — the mechanism is `SP046`/`SP047` reused; the judgement was step versus job granularity, which amends `DR-25` | Both controls verified rather than declared; the level banner disappears at `standard`; `DR-25` amended in place | `SP053` seen to fail four ways and pass one; the banner absent afterwards, which is the packet's own scoreboard |
| `ACT-013` | `H`: deferrals and deferred gates expire (`F22`) | maintainer | maintainer | `waiting_for_review` | — | hard | yes — a deadline that adopters declared starts being enforced | medium — the mechanism is small; the judgement is what is IN scope, and gate exceptions are deliberately out | A deferral or deferred gate whose `revisit_by` has passed raises `SP054`; one dated in the future does not | `2020-01-01` fails and surfaceplate's own `2027-02-27` passes — the second mattering more, since a check firing on every deferral would pass the first test too |
| `ACT-014` | Pattern C1: the four record-based controls acquire a register that is checked (`F20`) | maintainer | maintainer | `waiting_for_review` | `ACT-010` | hard | yes — it adds a real obligation on every adopter at `full`, and closes the half of `F20` that has been open since the architecture was written | medium — the mechanism reuses the gate-exception record loader; the judgement is that an EMPTY register must pass, and that `DR-25`'s claim about currency is wrong | Each of the four controls names a directory that exists, is tracked, and holds nothing that fails its schema; `full` becomes fully checked | The four negative controls carry the evidence — an empty register passes, a `README.md` beside a record is ignored, a valid record passes, and a valid record of the WRONG type fails |
| `ACT-015` | Pattern C2: records must reference what they describe; `provenance` and `run_lineage` separated | maintainer | maintainer | `waiting_for_review` | `ACT-014` | hard | yes — it adds cross-register obligations at `full` and edits a published schema | medium — the mechanism is an index over records already loaded; the judgements are how the two controls are separated after the first answer was disproved, and whether a redundant contract clause is removed or made real | A run naming an unregistered method, an override naming a run that never happened, a duplicated identity and a foreign `application_id` are all rejected | The three negative controls carry the evidence — the worked example set passes, an undeclared target register raises nothing, and a record that failed its schema produces no reference cascade |
| `ACT-016` | What the Plyego gate found: the exemption catch-22 and a misleading remedy (`F25`, `F26`) | maintainer | maintainer | `waiting_for_review` | `ACT-015` | medium | yes — it changes what the profile scan accepts, in every adopting repository | low — the mechanism mirrors `DR-22` exactly; the judgement is how narrow the exclusion is | An exemption may state its own rationale without failing the profile, and `SP032` names the remedy it has always had | Three negative controls — the scan still fires on `owner`, on a gate's rationale and on a deferral's — plus the Plyego probe re-run against the fixed checker |
| `ACT-017` | The installer forbids what the standard permits: a recorded hook opt-out (`F27`) | maintainer | maintainer | `waiting_for_review` | `ACT-016` | medium | yes — it changes what the installer will do in every adopting repository | medium — the mechanism is small; the judgement is that declining must leave a trace rather than being a silent flag | A repository with its own hook system can adopt without surrendering it, and the check says on every run that nothing gates staged changes | Three negative controls — the default install still refuses a foreign hooks path and writes nothing, and `SP038` still catches a gate claiming a hook that was declined |
## Notes on the entries

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

`ACT-005` to `ACT-017` were registered **before** implementation begins, not alongside it. `work_registration` is
live over `scripts/**` and `schemas/**`, which is exactly what item 4 changes, and a gate satisfied
retrospectively is the failure mode `core/PREREQUISITE_GATES.md` warns is most common — satisfied on
paper, violated in spirit.

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
