# Decision Record

- Decision ID: DR-1
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision
  about the framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted (decision only — not implemented; see Limitations and follow-up)
- Risk level: 2 — governs the installer/hook enforcement mechanism (workflow), per the risk table
  in `core/REVIEW_AND_EVIDENCE.md`. Not yet level 3, because nothing is implemented; a live
  security-boundary change would be.
- Related work item: `v0.11.0` (commit `22728e770dbd018305744b9ae5785fe04dbe2a36`)

## Decision

Refuse by default when `core.hooksPath` is already set to something other than this standard's own
`.githooks` directory. Allow an adopter to opt into chaining — declared explicitly in the
application profile — rather than the installer silently composing with, or silently overriding, an
existing hook configuration.

## Context and alternatives

Two alternatives considered and rejected:

- **Silent chaining.** Have the installer automatically detect and delegate to whatever is already
  configured at the existing `core.hooksPath`, composing its own check into that chain without
  asking. Rejected because it adds an undeclared dependency on another tool's directory contract —
  the installer would need to understand and preserve semantics it does not own, and a future
  change to that other tool's hook layout could silently break enforcement with nothing in this
  repository showing why.
- **Refuse-only, permanently, with no route to ever compose.** Keep the current 0.11.0 behaviour
  (`STOPPED`, nothing written) as the only behaviour, forever. Rejected because it is unusable for
  a large share of realistic adopters: any repository that already has its own local hook tooling
  (common) can never gain this standard's enforcement without first disabling its existing tooling
  outright, which the standard should not require blindly.

## Impact

- Numerical/model output: none.
- Contracts/schemas: `application-profile.schema.yaml` would need a new opt-in field to declare
  chaining. Not yet added.
- Security/data: directly affects the credibility of the standard's local enforcement layer. A
  wrongly composed chain is worse than an honest refusal, because it can silently stop running
  without anything on disk showing that it has.
- Reproducibility/lineage: none beyond the enforcement mechanism itself.
- Operations/release: no adopter-facing change yet. This decision only fixes the direction future
  0.12.0+ work must take.

## Evidence

- Code/configuration: FACT FROM PACKAGE. The existing hook-collision check in
  `scripts/install_standard.py` (`git config --get core.hooksPath`) already implements
  refuse-only. Reproduced directly against this repository at HEAD, against a disposable scratch
  repository, with `core.hooksPath` set globally on the machine used: `STOPPED - this repository
  already has a different Git hook configuration ... Nothing has been written.` (installer exit
  code 4).
- Tests/checks: `tests/test_install_and_check.py`'s "hook configuration collision safety" scenario
  (5 checks) already covers refuse-only behaviour and passed on this platform — 97/97 total, run
  under `GIT_CONFIG_GLOBAL=/dev/null` neutralisation (see DR-5, finding F1). Opt-in chaining is
  untested because it does not exist yet.
- Runtime evidence: on the machine this was verified against, the global hooks delegation shim at
  `~/.config/git/hooks/pre-commit` exists, but its own delegation target
  (`$(git rev-parse --git-common-dir)/hooks/pre-commit` inside this clone) is absent, so the shim
  exits 0 with no enforcement — confirmed directly (`test -x .git/hooks/pre-commit` returns false)
  and by the `v0.11.0` commit itself completing with no hook output. An adopter's own pre-existing
  hook chain can be similarly inert without anything in the clone revealing it, which is direct
  evidence that composing with an unverified existing chain would produce enforcement that looks
  present but is not — the same failure mode this standard exists to catch elsewhere.
- Independent review: none. Not yet reviewed by anyone beyond the session that recorded this
  decision.

## Limitations and follow-up

Decided, not implemented. No code, schema, or documentation change has been made toward opt-in
chaining. Implementation is scoped to 0.12.0 or later. Until then, the only available behaviour
remains refuse-only, exactly as at `v0.11.0`.

## Approval

- Technical reviewer: not yet assigned.
- Method owner: not yet assigned.
- Independent validator: not yet assigned.
- Release authority: not yet assigned.

This record does not itself constitute approval, validation, or release authorisation.
