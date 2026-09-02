---
name: fix-ci
description: "Diagnose and fix a failing CI job, pre-commit hook, or validation gate under Surfaceplate, without weakening the gate."
---

# Fix CI

Use when a pipeline job, pre-commit hook, linter, or validation gate is failing. Use `bug-fix` when
the defect is in product behaviour rather than in the checks.

## Required inputs

- the failing job, hook, or check name;
- the branch and commit;
- the failure log — the actual output, not a paraphrase;
- whether the check passed previously, and on which commit.

## The governing rule

**A failing gate is evidence, not an obstacle.** The default assumption is that the gate is right
and the code is wrong.

You may not, without explicit human approval recorded in the change:

- disable, skip, or delete a check, hook, test, or job;
- add a suppression, ignore rule, `nolint`, `noqa`, `eslint-disable`, `# type: ignore`, or
  equivalent;
- loosen a threshold, tolerance, coverage floor, or severity level;
- weaken an assertion or mark a test as expected-to-fail;
- regenerate a golden or snapshot file to match new output;
- pin around a check rather than fixing it.

If one of these genuinely is the right answer, stop and ask. Present the evidence and let a human
decide.

## Workflow

1. **Reproduce locally.** Run the same check with the same configuration. If it passes locally but
   fails in CI, the difference itself is the finding — environment, versions, cache, ordering, or
   permissions.
2. **Read the whole log**, not the first error. Cascading failures usually have one cause.
3. **Classify the failure**: genuine code defect; genuine configuration defect; environment or
   dependency drift; flaky or order-dependent test; or a genuinely incorrect check.
4. **Fix the cause** in the code or configuration.
5. **Re-run the same check** and confirm it passes for the right reason.
6. **Re-run the wider suite** — CI fixes frequently move a failure rather than remove it.

## Gates

- the originally failing check passes locally;
- no check, hook, test, or threshold was weakened, skipped, or suppressed;
- no golden or snapshot file was regenerated without an explained, approved delta;
- the broader suite is no worse than before;
- if the fix was environmental, the cause is recorded so it does not recur silently.

## Mandatory stops

- any request to disable, skip, suppress, or loosen a check;
- flakiness that would be "fixed" by retrying or by raising a tolerance;
- a failure that reveals a real defect in released or relied-upon output;
- a security scanner finding — hand to `security-review`;
- a failure caused by a dependency change — hand to `dependency-update`.

## Completion report

Report: the failing check and its original error; the root cause; the actual diff; the command and
output proving the check now passes; the wider suite result; an explicit statement that no gate was
weakened (or, if one was, the approval that authorised it); and any human decision required.
