---
name: review
description: "Risk-based review of an actual diff under Surfaceplate. Identifies required approvals; never supplies them."
---

# Review

Risk-based review of a change, using the **actual diff** and the surrounding code. A changed-file
list is not a review.

## Required inputs

- the branch, commit range, pull request, or file set to review;
- the registered activity ID, if one applies;
- the author's stated intent and acceptance criteria.

## Workflow

1. **Read the actual diff.** Every hunk. Then read enough surrounding code to judge whether each
   hunk is correct *in context*, not merely syntactically plausible.
2. **Classify the risk.** Route the review depth by what the change touches:

   | Level | Change | Minimum review |
   |---|---|---|
   | 0 | Documentation or formatting only | Ordinary review |
   | 1 | Low-risk implementation, no expected output impact | Focused checks and diff review |
   | 2 | Output-affecting code, data, schema, or workflow | Regression and contract tests, output self-review, change record, reviewer |
   | 3 | Methodology, material model or numerical output, material AI output, security boundary, or externally relied-on output | Level 2 plus independent challenge, sensitivity or benchmark evidence, explicit approval |

3. **Check the controlling implementation**, not just the diff. Does the change respect the
   canonical authority, the domain boundary, and the existing contract?
4. **Check the tests.** Were tests added for new behaviour? Were any tests weakened, skipped, or
   had assertions loosened? Were golden files regenerated, and if so, is the delta explained?
5. **Check the records.** Register updated? Documentation impact addressed? Decision record where
   required?
6. **Verify the evidence.** Were the claimed commands actually run, and do the reported results
   match the output?

## What to report

For each finding: the file and line, what is wrong, why it matters, and the severity. Separate:

- **blocking defects** — must be fixed before merge;
- **required human decisions** — approval, validation, or risk acceptance that must be obtained;
- **recommendations** — improvements that do not block.

Report explicitly when tests were weakened or golden outputs regenerated. That is a finding, even
if the author had a reason.

## Boundary

This skill can **identify** that technical review, method-owner approval, independent validation,
risk acceptance, or release authorisation is required.

It can **never provide** any of them. Do not conclude that a change is approved, validated, safe to
release, or production-ready. State what is outstanding and who must decide.
