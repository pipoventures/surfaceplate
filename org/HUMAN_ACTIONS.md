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
| H4 | **`F6`: external recomputation of the framework digest** | Two independent reasons. `F6` names the closing party as *"someone who is not the maintainer"* — so not you either, acting alone. And the first review established the second: it must be a party who can **compute**, not only read. A text-only model cannot produce a SHA-256 | `F6`, the oldest open finding, and item 10 | **Prepared (`ACT-060`, `DR-64`): the independent review packet.** Build it with `.venv/bin/python scripts/build_review_packet.py --ref b60cb5bbbe5e0f7ada15ea1eb657383e8ff3f72b --sdist-url <PyPI sdist URL> --sdist-sha256 5313a14f… --wheel-sha256 dfd95147… --publish-run 33697386488 --ci-run 33682871213 --zip dist/surfaceplate-0.16.0.zip` (the archive in `dist/` must be the one built from the published commit - every `build_release.py` run replaces it with the current tree's, so rebuild it from a worktree at that commit last, then generate; the generator refuses any other), send the page, its printed SHA-256 and the archive to a person with a shell who is not you. Part A takes about thirty minutes. On return: save the YAML as `governance/assurance/AE-0002-framework-anchor.yaml`, run `tests/validate_contracts.py`, check the three values equal `7d5b7a44…` and the reviewer is named and not you; then `F6` closes citing the record and this row moves below |
| H6 | **Item 10: independent audit** | The final gate. `org/decisions/README.md` records that no independent validator exists for this repository; an audit is what would create one. Self-approval is not independence | 1.0. It is the last item | **Prepared (`ACT-060`): Part B of the same packet as `H4`** — the full-archive prompt verbatim, one row per scope criterion, the time-boxed minimum, and a form that composes `governance/assurance/AE-0003-independent-audit.yaml` and the report as Markdown. On return: save the report verbatim as `audit/INDEPENDENT_REVIEW_<date>.md`, the record under `governance/assurance/`, record each finding as `F<n>`, and decide whether the profile's `independent_validator` names the reviewer |
| H9 | **Take decisions `DR-47` to `DR-50` and authorise `ACT-042` to `ACT-046`** | Decision records and activity authorisations are the maintainer's, never an agent's | Every phase of `org/REMEDIATION_PLAN.md` | **Taken 2026-09-02** in the review session (https://claude.ai/code/session_01X1MZfNScrJjgD5e2AGBjvs): all four records accepted as drafted, all five activities authorised, findings `F59` to `F77` recorded. Kept here as the evidence reference the records cite |
| H11 | **Decide the remedy for `F78` to `F82`**: a decision record on what the wizard shows a reader meeting the framework for the first time — an opening screen with the version comparison, a sentence per artefact choice on meaning, cost and benefit, and a stated minimum for every screen — and the activity that builds it | It changes what the interview asks and shows, which `DR-47` reserves for a decision record; and `F82` is a judgement about who the framework is for, which only its owner can make | Plutos adopting without the workaround in `H1`; every adopter after it | **Taken 2026-09-02** in this session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z): the maintainer instructed *"Fix findings 78 to 82. Then fix findings SP046 and SP032"* after his own run; `DR-51` records the decision and `ACT-048` implements it. Kept here as the evidence reference the record cites |
| H12 | **Taken 2026-09-02.** Set the outcome of the `adopt` validation record (`governance/assurance/AE-0001-adopt-matrix.yaml`) after reading `audit/validation/ADOPT_MATRIX.md` | A validation is concluded by a human; the agent runs it and drafts the record with the measured result and the evidence gaps as limitations, and may not set `outcome` or sign as reviewer | Pointing a complainant at the testing done; release-plan item 10 reads this record | Taken: PR #60 merged at `bc2fd94` with the record as drafted, `passed_with_conditions`, the maintainer named as reviewer; the nine limitations stand as the conditions |

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
| H5 | `F49`: search the tree for the former organisation's token | 2026-09-02 — the maintainer ran the one command with the name in place: zero hits on the tracked tree at `main`. A first attempt searched the placeholder itself and returned the file quoting the command; the second closed it. `F49` closed |
| H10 | Verify the organisation-level GitHub Actions claim and say which document wins | 2026-09-02 — the maintainer showed the organisation policy: Actions enabled for all repositories, all actions allowed. The README wins; `PREREQUISITE_GATES.md`'s paragraph rewritten; `F71` closed |
| H7 | Decide forge neutrality (item 3's remainder) | 2026-09-02 — `DR-62`: 1.0 supports GitHub as the forge and says so in `README.md` and `INSTALL.md`; a per-forge emitter is 1.x (`1.4`). Item 3 done with its scope stated |
| H3 | Second cross-provider adversarial review (item 9, pass 2) | 2026-09-02 — run by the maintainer with the curated prompt and the 27-file bundle from `main` at `56d2163`; the review reproduced verbatim as `audit/CROSS_PROVIDER_REVIEW_2026-09-02_PASS2.md` and its eleven points recorded as `F101` to `F111`, each assessed. The digest recomputation was an evidence gap (no code execution), so `H4` stays open |
| H13 | Decide the remedies for the second cross-provider review (`F101` to `F111`) | 2026-09-02/03 — every item put one at a time and decided: `F107` fixed as proposed; `F106`, `F109`, `F110` profile edits approved; `F108` note omitted; `F101` rollback; `F103` acceptance line; `F102` seed advisory over the reviewer's placeholder; `F104`/`F105` schema tightened (`DR-63`); `F111` the practice kept. `ACT-059` done |
| H14 | **Tag the published commit** (`F115`): `git tag pypi/0.16.0 b60cb5bbbe5e0f7ada15ea1eb657383e8ff3f72b && git push origin pypi/0.16.0`; never move `v0.16.0` | A tag on the public repository is the maintainer's act, and the choice of name is a convention only the owner sets | Reviewers and adopters who check out "the release" by tag; a future publish-workflow refusal when the tag and the published commit differ | The commit is known (run 33697386488's head); the packet names it until the tag exists |
| H8 | Reserve the name on PyPI (`DR-61`) | 2026-09-03 — the maintainer created the account and the pending trusted publisher, the `pypi` environment was created, and he dispatched *Publish to PyPI* (run 33697386488, both jobs green). `surfaceplate 0.16.0` is on the index with the alpha classifier, a wheel and an sdist; installed from PyPI into a clean environment and `surfaceplate --version` answered. Every instruction keeps the git form until 1.0 |
| — | Choose the `F47` remedy | 2026-09-01 — `effective_from` accepts an instant (`DR-44`) |
| — | Choose the `F51` remedy | 2026-09-02 — asked again, and the binding rule made precise (`DR-46`) |
| — | Merge or reject the README front-door PR | 2026-09-02 — merged as PR #39 on your authorisation |
| H1 | Run `adopt` against Plutos (`RELEASE_PLAN` item 5) | 2026-09-02 — run by the maintainer on the rebuilt wizard; stopped once at the review on a version mismatch (`F78`), resumed after the upgrade, and completed; the two checker findings it left (`F83`, `F84`) fixed by hand and merged as plutos#6, after which `surfaceplate check` passes there in full. Eight findings (`F78` to `F85`) recorded from the run and closed by `ACT-048` |
| H2 | Exercise or adopt Plyego (`RELEASE_PLAN` item 5) | 2026-09-02 — closed by `DR-52`: item 5 is met with one real adopter, Plutos; Plyego is mid-migration with important work ahead and is not to be touched. `DR-28` stands as the record of its exercise |
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
