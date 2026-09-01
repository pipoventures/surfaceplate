---
name: bug-fix
description: "Diagnose and fix a defect with a regression test, under Surfaceplate."
---

# Bug Fix

Use when something behaves incorrectly. If the failure is in CI or a validation hook rather than in
product behaviour, use `fix-ci` instead.

## Required inputs

- observed behaviour and expected behaviour;
- how to reproduce it, and how reliably;
- affected branch, environment, and inputs;
- any error output, stack trace, or log excerpt;
- the registered activity ID.

If the defect cannot be reproduced, say so and stop. Do not "fix" a defect you cannot observe.

## Workflow

1. **Reproduce.** Establish the failure locally with the narrowest possible harness. Record the
   exact command and output.
2. **Root-cause.** Explain *why* it fails, not just where. A fix without a cause is a guess.
3. **Write the failing test first** where practical. It must fail for the stated reason before the
   fix, and pass after. This is the evidence that the fix works.
4. **Fix minimally.** Address the cause. Do not opportunistically refactor surrounding code inside
   a defect fix — raise that separately.
5. **Re-run** the regression test, then the affected area's tests, then widen.
6. **Assess blast radius.** Did this defect produce incorrect outputs that were already relied
   upon? If so, that is an escalation, not a footnote.

## Gates

- new regression test present, and demonstrably failing before the fix;
- focused area tests green;
- golden, reference, or reconciliation tests green where output could be affected;
- lint, type, and build checks green;
- methodology, validation, or data authority updated where the defect changed a documented
  behaviour.

## Mandatory stops

Stop and escalate when the defect or its fix involves:

- a change to methodology or to a material output value;
- a schema or contract change;
- incorrect outputs that have already been released, reported, or relied upon;
- a security or authorisation boundary;
- client-specific or branch-specific divergence.

## Completion report

Report: the activity ID; the root cause in one clear sentence; the reproduction command and its
output before the fix; the regression test added; the actual diff; every command run and its
result; the output delta if any; the blast-radius assessment; and any human decision required.
