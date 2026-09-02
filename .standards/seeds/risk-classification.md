# Risk classification

How a change in this repository is classified for risk, and the rule that it happens before implementation.

**This file existing is not the practice.** It was created when Surfaceplate was adopted here, so that the `risk_classification` gate has a real place to point at. What the gate asks is that a change's risk class is decided *before* implementation begins, never derived afterwards to match what was built; the standard names this the gate most often satisfied on paper while violated in spirit. A file that stays empty while the thing it records happens around it is a finding about this repository, not a satisfied control; the checker cannot tell the difference, because it checks that this file exists and holds no placeholder.

## The scale

The standard's templates carry a four-point scale, `0` to `3`, on every work packet and decision record (`.standards/templates/work-packet.md`, `.standards/templates/decision-record.md`). A change's class is written on its work packet before implementation and on its decision record where one exists.

## What raises a class

The standard's audit triggers (`.standards/agent-instructions/ai-workflow.md`) are the inputs: a change that affects material numerical or model outputs, material AI outputs or reasoning, public schemas or contracts, provenance or run lineage, security boundaries, dependencies, approval state, model or tool classification, AI provider or prompt behaviour, or is a broad refactor, is never the lowest class. Review depth increases for a change that is novel, hard to test, irreversible, externally reported or difficult to reproduce.

## What each level means here

| Level | Meaning in this repository | Records required |
|---|---|---|
| 0 | | |
| 1 | | |
| 2 | | |
| 3 | | |

**The meanings are not declared yet.** That is an accurate statement on the day this file was created: the scale and the rule are the standard's, and what each level means for this repository, and which records each level requires before release, is a decision its owner has not yet written down. Until it is, every classification made here is made against an undeclared scheme, which is itself something to record.
