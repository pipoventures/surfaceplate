# Review and Evidence Standard

## Minimum review packet

For every bounded change, retain:

- work packet and application profile reference;
- actual diff or changed-file list for low-risk routing;
- actual diff or patch content for material or audit-triggered changes;
- tests/checks and exact commands;
- runtime or integration evidence where relevant;
- known failures, warnings, and environmental limitations;
- dependency/security impact;
- documentation/contract impact;
- reviewer disposition and unresolved questions.

## Risk levels

| Level | Typical change | Minimum evidence |
|---|---|---|
| 0 | Documentation or formatting only | Self-check and ordinary review |
| 1 | Low-risk implementation with no expected output impact | Focused automated checks and diff review |
| 2 | Output-affecting code, data, schema, or workflow | Regression/contract tests, output self-review, change record, reviewer |
| 3 | Methodology, material model or numerical output, material AI output/reasoning, security boundary, or externally relied-on output | Level 2 plus independent challenge, sensitivity/benchmark evidence where relevant, explicit approval |

The receiving application must define its own materiality thresholds. These levels are a routing aid, not approval authority.

## Evidence labels

Use these labels in reports:

The four labels are the ones the installed agent instructions (`ai-workflow`) use; one vocabulary,
so a report reads the same whoever wrote it:

- `FACT`: directly verified — and say where: in this kit's files, schemas, templates or package
  checks, or in the adopting application's code, configuration, tests or current runtime output.
- `INFERENCE`: reasoned conclusion that is not directly enforced or fully observed.
- `RECOMMENDATION`: proposed treatment for the receiving application.
- `EVIDENCE GAP`: requested fact not established by available evidence.

## Failure discipline

Report failed checks and warnings honestly. Distinguish code failures from environment/dependency failures, and do not call a process successful solely because a wrapper returned exit code zero when the test output shows failures.

**A check that did not run is not a check that passed.** This is a distinct failure from the one above, and it is harder to see: the first produces a wrong result, this one produces *no* result while every artefact around it — the workflow file, the commit, the step name — looks correct.

The requirement, for any repository adopting this standard:

1. **A pipeline must not silently skip its checks.** Most CI systems stop at the first failing step by default, and record the rest as *skipped*. A summary that reports only an overall status cannot distinguish `skipped` from `passed`. On GitHub Actions the guard is `if: ${{ !cancelled() }}` on each check step. It is **not** `continue-on-error`, which marks a real failure as tolerated and turns the job green — trading a hidden non-result for a hidden failure.
2. **Something must confirm each check produced a result.** A guard that is never verified is an assumption. Read the per-step conclusions, not the overall tick.
3. **A green run is evidence only for the checks that actually executed.** When citing CI as evidence, cite the step, not the job.

Why this is stated rather than assumed: a check was once added to this framework's own repository, wired into CI, committed, and had **never executed** — an earlier step failed, the step's conclusion read `skipped`, and nothing distinguished that from passing. It was found by comparing two instruments against each other, not by reading output more carefully; the output was internally consistent and wrong. It is recorded as `F13`.

**This standard cannot check any of the above for you.** It inspects an adopting repository's declared profile and its git history, not the semantics of its pipelines. This is an obligation, not an enforced control, and it is listed here so the difference is visible rather than assumed.
