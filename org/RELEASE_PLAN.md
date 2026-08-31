# Release plan

The ordered scope between where surfaceplate stands today and its first real release, and what
happens if the schedule doesn't hold.

**This is not a decision record.** It will change. Where it commits to something permanent, it
cites the decision record that actually commits to it (`DR-10`, `DR-11`, `DR-12`, `DR-13`) rather
than asserting permanence itself.

---

## Before anything else: item 0

`DR-13` gates everything below it. **No item in this plan begins before self-conformance lands** —
an application profile, an activity register, the conformance block, declared prerequisite gates,
and the checker running in this repository's own CI, all against surfaceplate itself. This is not
the first feature; it is the precondition for every feature after it having been built under the
process this framework itself requires. See `DR-13` for why and for the bootstrap problem it
accepts.

**Item 0 has landed.** `governance/application-profile.yaml` declares level `standard` with all
nineteen catalogue gates reasoned, `governance/authority-map.yaml` and `activity/register.md` exist,
`.standards/` is installer-produced, and `check_conformance.py --repo .` passes on both the source
and the vendored copy. `DR-16` records how the publisher installs into itself without packaging its
own installed set. `DR-13`'s open question — *does this repository's CI fail on its own
non-conformance?* — **is now answered yes**: the self-check workflow runs the source checker against
this repository, and every check step carries `if: ${{ !cancelled() }}` plus a step that confirms
each one produced a result, so a failure cannot be hidden by an earlier failure short-circuiting the
rest.

Doing it surfaced five findings, which is the point of the exercise rather than a cost of it:
`F12` (the source and vendored checkers can diverge undetected), `F13` (a wired CI check that had
never run), `F14` (`SP032`'s placeholder detection could not tell notation from an unfilled
template — the instrument was fixed first, `DR-17`), `F15` (two shipped templates were undetectable
as templates) and `F16` (a record that discusses placeholder tokens trips its own gate).

**Landed, reviewed and closed.** `ACT-001` and `ACT-004` moved to `done` when the maintainer
merged them, and `adoption.adoption_status` reads `complete`. What `complete` does **not** mean is
stated in the profile itself: five findings remain open, and nothing here is independently
validated. The audit gate (item 10) is undischarged.

---

## Execution order

**The numbers below are identities, not a sequence.** They are cited as "item 4", "item 7" and so
on from decision records, findings and commit messages, so they are never renumbered. The order in
which the remaining items are actually worked is stated here instead, decided 2026-08-31:

**3 → 1 → 2 → 9 → 5 → 8 → 9 → 10**

| Position | Item | Why here |
|---|---|---|
| 1st | **3** Agent neutrality | Changes *what* ships. Settle the payload's shape before deciding how it is distributed, or item 1 packages a moving target. Not urgent on honesty grounds — checked 2026-08-31, nothing on any public surface claims agent neutrality — so this is a feature, not a correction. |
| 2nd | **1** Pip packaging | Where `repo_root()`-under-a-wheel finally gets solved, which `DR-10` flagged and left unfixed. It decides the install story everything after it depends on. |
| 3rd | **2** CLI and wizard | A CLI is *delivered by* packaging — pip's entry point. Built before item 1 it would either assume a git clone and be rebuilt, or make the packaging decision implicitly instead of deliberately. |
| 4th | **9** Adversarial review | **Before** real adopters, not after. Items 1–3 are the substance a reviewer examines, so reviewing earlier means reviewing a thing about to change shape — and installing an unreviewed framework into someone else's working repository is the failure this project would raise as a finding against anybody else. |
| 5th | **5** Two real adopters | Only after review. This is the first time the framework meets a repository that is not its own. |
| 6th | **8** Documentation for a stranger | Deliberately after adopters. Writing it earlier means guessing what a stranger needs; after item 5 there is evidence. Publication (`DR-23`) weakened that argument by putting strangers in front of the docs today, but the current documents are accurate — author-shaped, which is a quality gap rather than a correctness one. A bounded README front-door pass is available at any point without spending item 8. |
| 7th | **9 again** Second adversarial review | Not repetition. The first review examines the design; the second has usage evidence from real adopters that the first could not have. Two instruments asking different questions, which is how nearly every finding in `org/FINDINGS.md` was actually found. |
| 8th | **10** Independent audit | The final gate, and the only item that can close `F6`. |

**On `F6` specifically, because it is easy to overstate.** An adversarial review *finds flaws*; it
does not by itself close `F6`. Closure needs a party other than this repository to recompute
`sha256(MANIFEST.sha256)` from a published tree and **attest** to it. That is item 10's shape, or a
review explicitly scoped to include attestation. `F6`'s own entry says "items 9 and 10" and means
both.

---

## 1.0 scope

The numbers are **identities**, not a sequence — see [Execution order](#execution-order) above for
the order the remaining items are worked in. They are cited from decision records and findings, so
they are never renumbered.

| # | Item | Why 1.0, not later |
|---|---|---|
| 0 | Self-conformance (`DR-13`) — **done** | Everything below is implementation work; `DR-13` forbade implementation work until this landed. See "Before anything else" above for what landed, and `DR-16`/`DR-17` for the two decisions it required. |
| 1 | Pip packaging; the payload becomes package data — **declaration half begun early** | `DR-12` commits to pip distribution and `DR-10` already decided the pinning semantics it depends on. `DR-10` also flagged, unsolved, that `install_standard.py`'s `repo_root()` and `build_payload` resolve repository-root directories that do not exist under a wheel install — this item is where that precondition finally gets addressed, not merely cited again. **Partly begun ahead of the gate:** `pyproject.toml` was added in `ACT-011` to give `dependency_lock` something real to check (`F21`). That is the dependency-declaration half only — no build backend, no entry point, no package data, and `repo_root()` under a wheel is untouched. Recorded here so the sequence does not drift silently. |
| 2 | The CLI and the wizard | `DR-12` commits to a `surfaceplate` command-line tool. See "The wizard's binding rule" below — this is a *different* artefact from the existing `prompts/github-copilot-adoption-wizard.prompt.md`, which must be explicitly reconciled, not silently duplicated (see "A naming collision" below). |
| 3 | Agent neutrality: `AGENTS.md` and per-agent emitters — **largely done** | `DR-12` commits to this; `DR-11` decided the integrity mechanics it depends on. **Built at `ACT-018` (`DR-30`), and the delay was expensive**: because it was decided and not implemented, nobody discovered that `DR-12`'s planned remedy was itself wrong — *"Claude Code reads `CLAUDE.md`, not `AGENTS.md`"* — so `AGENTS.md` alone would have been as inert as the Copilot files it replaced. Meanwhile this repository's own 501 lines of agent instruction were read by nothing at all (`F29`). One canonical body now emits per agent: Copilot's form unchanged, `.claude/rules/` added, `AGENTS.md` carrying the block, and a canonical copy for agents not emitted for. **Not finished:** only two agents have emitters, and forge neutrality — `.github/skills/` and the conformance workflow, 8 of 57 installed files — is untouched and is a larger question. |
| 4 | `secret_hygiene` gains an actual check — **done** (`DR-18`, `SP046`/`SP047`) | Not cuttable — see "The cut order" below for why. Selected as the first item after 0: it is the only baseline control required at every level with no verification of any kind, and this repository has no scanner of its own either (no scanner configuration, no scan workflow), so its own profile declares the control while recording the gap. |
| 5 | Two real adopters: Plyego, Plutos — **half begun** | `DR-7` established that every previously-recorded adopter was fabricated, and until 2026-08-31 neither name appeared anywhere in this repository. **Plyego has now been exercised**: the framework was installed into a throwaway clone of it and returned `PASS` at `essential`, exposing two defects in surfaceplate that were unreachable from here (`F25`, `F26`) and running the four interface gates for the first time. `DR-28` records the result. **Plyego is not adopted** — nothing was written to it, and the level decision waits on the per-gate cost. Plutos is untouched. So this row is no longer 'no adopter has ever been exercised'; it is 'one has been exercised, none has adopted'. |
| 6 | Licence and contributor framework — **done** | `LICENSE:189` names the copyright holder, `CONTRIBUTING.md` states the sign-off requirement, and `.github/workflows/dco-check.yml` enforces it. [DR-19](decisions/DR-19.md) decides DCO sign-off and **no** contributor licence agreement, resolving the contradiction between this row's original wording and the constraint the sign-off work was commissioned under. The trade is recorded rather than glossed: relicensing away from Apache-2.0 would need every contributor's agreement, and that cost grows with each one accepted. Untested against a real external contributor — it is preparation, not something proven in use. |
| 7 | F5 remediation — **done** | Both halves closed. The series collision is resolved by [`org/FINDINGS.md`](FINDINGS.md), which is now the single register. `F5` itself is closed: the live clone instruction was corrected, `git ls-remote` against the declared owner resolves, and every remaining occurrence of the broken spelling is a quotation inside a record that `tests/check_identifiers.py` verifies. `F11` closed alongside it — `tests/check_code_registers.py` compares the declared code space against the codes the checker emits, after the register was found carrying four false statements at once. |
| 8 | Documentation written for a stranger | Every document in this repository today is written by, and largely for, the one person who wrote the framework. A reader with no prior context is 1.0's actual audience once real adopters exist (item 5); writing for them earlier would be guessing at what they need before anyone real has needed it. |
| 9 | Cross-provider adversarial review | Not cuttable — see "The cut order" below. |
| 10 | Independent audit, as the final gate | The last item, deliberately: `org/decisions/README.md:16-18` already establishes no independent validator exists for this repository today. An audit is what would establish one, and everything above it is what an audit needs to already exist to have something real to examine. |

---

## The wizard's binding rule

The CLI wizard (item 2) is bound by one rule, stated here because it is a design constraint on that
item, not a scheduling fact:

**It asks, the human answers, the tool writes.** It never selects a conformance level, invents a
rationale, or sets a date. Every judgement call in `core/PREREQUISITE_GATES.md` and
`core/CONFORMANCE_LEVELS.md` — which level applies, why a control is `deferred` rather than
`required`, what `effective_from` should read — is a human decision the wizard elicits and records
verbatim, never one it makes on the human's behalf.

**A naming collision this item must resolve, not duplicate.**
`prompts/github-copilot-adoption-wizard.prompt.md` already exists, is already called "the wizard,"
and is already referenced from `SETUP_GUIDE.md:7`. It is an LLM prompt for Copilot Chat, not a CLI,
and it named the pre-`0.12.0`-rename product until `F18` corrected it, confirming it predates the
rename and had not been touched since. It also omits `core/PREREQUISITE_GATES.md` and
`core/CONFORMANCE_LEVELS.md` from its "read these first" list, which is why it carries a staleness
banner rather than merely a corrected name. Item 2 is a different artefact —
a deterministic questionnaire bound by the rule above, not an LLM-driven conversation. Building it
without explicitly stating what happens to the existing prompt-wizard (retire it, fold its
discovery flow into the new tool, or keep both with a stated division of labour) would leave two
things called "wizard" in the same repository with no record of which is authoritative.

---

## `secret_hygiene`, stated precisely

`core/CONFORMANCE_LEVELS.md:18-20` already requires `secret_hygiene` at every conformance level,
unconditionally. It has, today, **zero automated verification** — confirmed independently
(`grep -i secret scripts/check_conformance.py` returns no hits) and already admitted in this
repository's own history: `CHANGELOG.md:272-276` — *"`secret_hygiene` is required by this standard
at every level and has no check of any kind."* Shipping a 1.0 with one of its three unconditional
baseline controls carrying no enforcement at all is not incompleteness — it is a false claim of a
floor that is not there. This is why item 4 is building an actual check, not merely keeping the
control declared.

---

## 1.x outline

- **1.1** — the organisation ruleset and required status checks, evidenced. `org/ROLLOUT_RUNBOOK.md`
  already describes the enforcement ladder this exercises (rungs 3 and 4); 1.1 is where a real
  organisation owner actually applies it and the evaluation evidence gets recorded, not merely
  described as available.
- **1.2** — the crosswalk (`DR-3`) and doctrine vendoring (`DR-4`). **Blocked on an external
  dependency that does not yet exist.** `DR-4`'s own text is explicit: the doctrine bundle this
  product would vendor must be *"a reference kernel — a generic, unopinionated starting point — not
  any individual maintainer's personal, machine-specific doctrine."* No such generic, versioned,
  publishable bundle exists yet outside this repository. 1.2 cannot start before one does.
- **1.3** — further stack adapters and monorepo support. Extends `adapters/` beyond Python,
  TypeScript, and R, and addresses the single-application-per-repository assumption the current
  installer carries.
- **2.0** — a check for instruments whose result is conditional on an undeclared precondition. The
  shape this repository has already found twice: `DR-6`'s F4 (a namespace test that agreed with the
  schemas by construction and could never disagree with the document governing them) and `DR-5`'s F1
  (a test suite whose pass depended on an unstated environment fact). A general-purpose check for
  this defect shape — an instrument whose positive result does not establish what it claims to
  establish — is 2.0-scale work, not a 1.x addition.

---

## The cut order, if 1.0 stalls

In this order, cut what's needed and nothing more:

1. Additional agent emitters beyond the first, item 3's scope narrowed to one working agent
   integration rather than several.
2. The second adopter (item 5) — ship with one real adopter rather than two.
3. Documentation polish (item 8) — the minimum a stranger needs, not the ideal.

**Not cuttable, under any schedule pressure: `secret_hygiene` (item 4), the licence and
contributor licence agreement (item 6), and the cross-provider adversarial review (item 9).** Their
absence does not make the product incomplete — it makes it dishonest. A 1.0 that claims a security
baseline control it does not check, accepts external contributions with no licence framework in
place, or was never adversarially reviewed by anything other than the tools that built it, is
claiming assurance it has not earned. Every other item on this list can ship smaller. These three
cannot ship absent.

---

## What is not yet true

State these honestly, the same way `org/ROLLOUT_RUNBOOK.md:142-155` states its own list:

1. **Items 0, 4, 6 and 7 are done. Items 1, 2, 3, 5, 8, 9 and 10 do not exist in any form.**
   Done here means built, reviewed and merged — not independently validated. No item on this list
   has been examined by anyone other than the maintainer and the agent that wrote it, which is
   exactly what items 9 and 10 exist to change.
2. **No external contributor exists.** The licence and CLA item (6) is preparation for a state that
   has not arrived, not a response to a pull request already pending.
3. **Neither named adopter (Plyego, Plutos) has agreed to anything.** Their presence in this
   plan is scope, not a commitment made on their behalf. Plyego was *exercised* on
   2026-08-31 — installed into a throwaway clone, never into the repository — which is a
   test the maintainer ran on his own project, not an adoption anyone agreed to. `DR-28`.
4. **The 1.2 blocker is outside this repository's control.** 1.2 cannot be pulled forward by working
   harder on it; it requires a dependency that does not yet exist, published elsewhere.
