# Human actions — what no agent in this repository can do

The register of work reserved to a person. Everything here is blocked on a human **by nature**, not
by scheduling: an agent may inspect, plan, edit, test, verify and report, and may not approve, accept
risk, conclude a validation, or authorise a release — nor stand in for a party this framework's own
findings define as external.

**Why this file exists.** `activity/register.md` records work; `org/FINDINGS.md` records defects.
Neither answers the question *"what is waiting on me?"*, and the answer had been scattered across
decision records, findings entries and commit messages. Created at `ACT-039`, before an unattended
overnight run, so that what needs a human survives independently of what an agent got through.

**How to read the last column.** *Prepared* means the work an agent could legitimately do first has
been done, so the human action can start cold rather than beginning with an hour of reconstruction.

## Open

| # | Action | Why no agent can do it | Blocked behind it | Prepared |
|---|---|---|---|---|
| H2 | **Exercise or adopt Plyego** (`RELEASE_PLAN` item 5) | Same, plus a judgement that is explicitly yours: Plyego is mid-migration to Google Cloud and `DR-28` records the pause as deliberate | The second half of item 5 | `DR-28` records the first exercise and the two defects it found. Nothing has been written to Plyego |
| H3 | **Second cross-provider adversarial review** (item 9, pass 2) | It means putting a packet to a party outside this repository. An agent here cannot be that party, and a same-provider model shares blind spots — the reason the item says *cross*-provider | Item 10, which needs a reviewed framework to audit | `audit/GEMINI_ADVERSARIAL_REVIEW_PROMPT_CURATED.md` rebuilt at `ACT-037`/`ACT-038`; the bundle command in `audit/AUDIT_README.md` runs and produces 15 files. `RELEASE_PLAN` schedules this **after** adopters, so H1/H2 come first |
| H4 | **`F6`: external recomputation of the framework digest** | Two independent reasons. `F6` names the closing party as *"someone who is not the maintainer"* — so not you either, acting alone. And the first review established the second: it must be a party who can **compute**, not only read. A text-only model cannot produce a SHA-256 | `F6`, the oldest open finding, and item 10 | `MANIFEST.sha256` now ships in the payload (`DR-45`), so the anchor is recomputable from an installed repository for the first time. The packet asks for the computation only from a reviewer with code execution |
| H5 | **`F49`: search the tree for the former organisation's token** | `DR-23` deliberately does not write the token down, so nothing working from the public repository holds it. That is the policy working, not a gap | `F49`; `ACT-007` was closed on judgement over this residue | One command: `cd ~/github/surfaceplate && git grep -Iil -- '<token>'`. Zero hits closes it. Two attempts to automate this produced **false alarms** — do not build a third instrument |
| H6 | **Item 10: independent audit** | The final gate. `org/decisions/README.md` records that no independent validator exists for this repository; an audit is what would create one. Self-approval is not independence | 1.0. It is the last item | Everything below it in the order. The audit prompt at `audit/GEMINI_ADVERSARIAL_REVIEW_PROMPT.md` is the full-archive form |
| H7 | **Decide forge neutrality** (item 3's remainder) | A scope decision about what the framework ships. `RELEASE_PLAN` calls it *"a larger question"* | Item 3 moving from *largely done* to done | **Narrowed from 8 files to 1.** Researching this found `F58`: seven of those eight files were not a forge question at all — the skills were installed only where Copilot reads them, while `AGENTS.md` called their gates mandatory. Fixed at `ACT-041` on `DR-30`'s pattern, so they now install for both agents. **What is left for you is the conformance workflow alone** — one file, genuinely GitHub Actions-specific, and the only installed file that assumes a forge |
| H8 | **Publish to PyPI, or decide not to** | A release decision with credentials attached. An agent may not take one, and `org/decisions/README.md` reserves release authority | Nothing hard, but it is the difference between `pip install surfaceplate` and the git URL every instruction now carries. `F57` found the README, `INSTALL.md` and the tool itself all naming a command that 404s | The package builds and installs cleanly — verified 2026-09-02 from a wheel into a clean venv, and from `git+https` into another. Every live instruction names the git form, which was **run before it was written down**. When you publish, the interim wording is what to replace |
| H9 | **Take decisions `DR-47` to `DR-50` and authorise `ACT-042` to `ACT-046`** | Decision records and activity authorisations are the maintainer's, never an agent's | Every phase of `org/REMEDIATION_PLAN.md` | **Taken 2026-09-02** in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs): all four records accepted as drafted, all five activities authorised, findings `F59` to `F77` recorded. Kept here as the evidence reference the records cite |
| H10 | **Verify the organisation-level GitHub Actions claim** in `PREREQUISITE_GATES.md:30-32` and say which document wins | It is a fact about the organisation's settings that only an account holder can read; the README's opening paragraph demonstrates the opposite for this repository | `ACT-045` item 2.6 (`F71`) | One line: which of the two statements is true today, dated; the implementing session edits the losing document |
| H11 | **Decide the remedy for `F78` to `F82`**: a decision record on what the wizard shows a reader meeting the framework for the first time — an opening screen with the version comparison, a sentence per artefact choice on meaning, cost and benefit, and a stated minimum for every screen — and the activity that builds it | It changes what the interview asks and shows, which `DR-47` reserves for a decision record; and `F82` is a judgement about who the framework is for, which only its owner can make | Plutos adopting without the workaround in `H1`; every adopter after it | **Taken 2026-09-02** in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z): the maintainer instructed *"Fix findings 78 to 82. Then fix findings SP046 and SP032"* after his own run; `DR-51` records the decision and `ACT-048` implements it. Kept here as the evidence reference the record cites |

## Standing practices, not one-off actions

| # | Practice | Why it is here |
|---|---|---|
| S1 | **`F55`: verify a docstring's claim when touching the code beneath it** | Open with no mechanical remedy. Two docstrings were found wrong about their own code on 2026-09-01, both corrected. A comment describing a guarantee is a claim to be checked, not a fact |
| S3 | **Run an instruction before publishing it** | `F50` and `F57` are the same defect one layer apart: a hand-off command naming a file deleted three packets earlier, and a README, an `INSTALL.md` and the tool itself naming a package that 404s. Both survived because **a document is read for sense rather than run**. `F50`'s half is now checked by `tests/check_audit_packet.py`; **`F57`'s is not, and deliberately so** — whether `pip install X` resolves cannot be answered offline, and a check that would not have caught the defect it is named for is the false green this project exists to find |
| S2 | **Approve, or decline, each merge** | An agent merges on your authorisation and never on its own judgement. Where a packet was planned and approved, the merge is mechanical; where it was not, it waits |

## Closed

| # | Action | Closed |
|---|---|---|
| — | Decide publication (`ACT-007`) | 2026-09-01, on judgement, with the unverifiable residue recorded as `F49` |
| — | Choose the `F47` remedy | 2026-09-01 — `effective_from` accepts an instant (`DR-44`) |
| — | Choose the `F51` remedy | 2026-09-02 — asked again, and the binding rule made precise (`DR-46`) |
| — | Merge or reject the README front-door PR | 2026-09-02 — merged as PR #39 on your authorisation |
| H1 | Run `adopt` against Plutos (`RELEASE_PLAN` item 5) | 2026-09-02 — run by the maintainer on the rebuilt wizard; stopped once at the review on a version mismatch (`F78`), resumed after the upgrade, and completed; the two checker findings it left (`F83`, `F84`) fixed by hand and merged as plutos#6, after which `surfaceplate check` passes there in full. Eight findings (`F78` to `F85`) recorded from the run and closed by `ACT-048` |
| — | First cross-provider review (item 9, pass 1) | 2026-09-01, returned `FAIL`; acted on at `ACT-038`. **It did not narrow `F6`** — see H4 |

## What an agent may not do here, restated

Recorded so this file is not read as a to-do list an agent could simply work through given more
time. None of the above is blocked on effort:

- **approve, accept risk, conclude a validation, or authorise a release** — never an agent's,
  however clear the intent and authority appear;
- **stand in for an external party** — `F6`'s closing condition and item 10 both define the closer as
  someone other than this repository, and an agent inside it is the least independent party of all;
- **decide methodology, a control's semantics, or what the framework ships** — H7 is the live
  example;
- **supply a value the maintainer holds and the records deliberately do not** — H5.
