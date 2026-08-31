# Decision Record

- Decision ID: DR-5
- Date: 2026-08-30
- Application: Surfaceplate (the framework itself) — a self-referential decision
  about the framework, not an adopting application.
- Decision owner: Mario Pipo (maintainer), per the decision-maker convention recorded in
  `org/decisions/README.md`.
- Status: accepted (recorded; no fixes applied — by design; see Limitations and follow-up)
- Risk level: 0 — a documentation/findings record; no code, test, or workflow change is made here,
  per the risk table in `core/REVIEW_AND_EVIDENCE.md`.
- Related work item: `v0.11.0` (commit `22728e770dbd018305744b9ae5785fe04dbe2a36`)

## Decision

Record findings F1, F2 and F3 below as open findings with assigned severity, in this repository's
durable decision-record form, and defer any fix to separately scoped work. No code, test, or
workflow change is made as part of this record.

## Context and alternatives

Rejected: fixing F1, F2 or F3 as part of recording them. Rejected because a fix bundled into a
findings record would make the record read as remediation evidence for something it has not
actually verified end-to-end, and this recording step was explicitly scoped to findings only, with
fixes scoped elsewhere. Recording first and fixing later keeps a finding and its remedy separately
reviewable.

## Impact

- Numerical/model output: none.
- Contracts/schemas: none directly from this record. F1 concerns test-harness robustness, F2
  concerns documented install instructions, F3 concerns test-runner output consistency.
- Security/data: none directly.
- Reproducibility/lineage: F1 is a reproducibility defect in its own right — a suite whose pass
  depends on an unstated environmental precondition is not reproducible across machines that differ
  only in that precondition.
- Operations/release: none from recording; each finding, once fixed, would touch `tests/` and
  possibly `.github/workflows/`.

## Evidence

- Code/configuration: not applicable — this record changes no code, test, or workflow file. The
  three findings below concern `tests/test_install_and_check.py`, the documented installation
  instructions, and `tests/validate_contracts.py` respectively, all read as they stand at `v0.11.0`.
- Tests/checks: the raw run output establishing F1 (both the crashing and the neutralised run) is
  reproduced in full below; it is command output from this repository, not summarised.
- Runtime evidence: F2's virtual-environment requirement and the corrected transitive-dependency
  check underlying the unassigned CI note were both reproduced directly on the machine used for this
  repository's restoration, not inferred.
- Independent review: none. Not yet reviewed by anyone beyond the session that recorded this
  finding.

### F1 — severity: high

`tests/test_install_and_check.py` depends on an undeclared precondition: it only reaches its full
check count where `core.hooksPath` is unset for the invocation. FACT FROM PACKAGE, directly
reproduced in this repository. Run without neutralisation: the suite fails at 2 checks passed before
an unhandled `FileNotFoundError` in `main()` (`.github/skills`, `iterdir` on a directory the
installer never created because it correctly refused) crashes the runner entirely, well short of the
113 static `check(` call sites in the file. Run with `GIT_CONFIG_GLOBAL=/dev/null` neutralising the
condition per-invocation (not `git config --unset`), it completes with
`INSTALL_CONFORMANCE=PASS (97 checks)`, independently recounted from raw output
(`grep -c "^  PASS"` → 97, `grep -c "^  FAIL"` → 0).

The unguarded crash is the *symptom*, not the finding. The finding is that the suite's pass is
conditional on an environment fact — the effective value of `core.hooksPath` at invocation time —
that the suite itself never checks, states, or guards against. This is the second instance of that
shape of defect in this repository. The `local_hook` profile claim that 0.11.0 exists to strengthen
was itself an instrument whose positive result did not establish what it claimed to establish, until
0.11.0's `SP038` change required a hook actually present in Git's active hooks directory and,
on POSIX, executable — a hook-shaped file elsewhere was not, before that change, evidence of
activation. F1 is the same category of defect recurring in the standard's own test harness rather
than in an adopting application's profile claim.

### F2 — severity: medium

The documented `python -m pip install pyyaml jsonschema ...` instruction fails on a PEP 668
externally-managed interpreter. FACT FROM PACKAGE, directly reproduced in this repository's own
restoration, on Ubuntu under WSL2: `python3 -m pip install ...` reported "No module named pip";
`python3 -m ensurepip --user` refused with "Python modules for the system python are usually
handled by dpkg and apt-get ... Install the python3-pip package to use pip itself ... use it on your
own risk, or make sure to only use it in virtual environments." A disposable virtual environment was
required to install the named dependencies at all. This is exactly the class of environment this
standard is meant to be stack-neutral and installable on — Debian and Ubuntu 24.04 are also the
family of the `ubuntu-latest` runners `.github/workflows/standard-self-check.yml` already targets.

### F3 — severity: low

`tests/validate_contracts.py` prints no executed-check count on success — only
`CONTRACT_CONFORMANCE=PASS`. `tests/test_install_and_check.py` does print one
(`INSTALL_CONFORMANCE=PASS  (97 checks)`), because it maintains an explicit `PASSES` counter. FACT
FROM PACKAGE, verified directly against both files' source and their actual output in this
repository. The inconsistency is the finding: one of the two conformance scripts this standard
relies on as its own build gate provides no way to distinguish "everything was checked and passed"
from "nothing was checked," while the other does. Independent reading confirmed
`validate_contracts.py` is not a zero-check pass — it globs `schemas/*.schema.yaml` (6 real files)
and asserts against real example files — but establishing that required reading the script; its own
output does not provide it.

### Unassigned — not yet a numbered finding

`.github/workflows/standard-self-check.yml` installs `pyyaml jsonschema` via `python -m pip
install`, without naming `referencing` explicitly. This was initially flagged as a likely dependency
gap; checked directly before being recorded here, and the framing needs correcting. FACT FROM
PACKAGE: `pip show jsonschema` against a freshly `pip`-installed `jsonschema` 4.26.0, in this
repository's own build virtual environment, reports `Requires: attrs, jsonschema-specifications,
referencing, rpds-py`. A clean `pip install jsonschema` on an `ubuntu-latest` runner with no
pre-existing system `jsonschema` would therefore resolve and install `referencing` transitively,
without it being named in the workflow. The `ModuleNotFoundError: No module named 'referencing'`
observed during this repository's own restoration arose from a different cause, covered by F2: that
machine's system Python already had an old, `apt`-installed `jsonschema` satisfying `import
jsonschema` before `pip` was ever invoked, and that old package predates the `referencing` split. On
a clean runner with no pre-existing system `jsonschema`, that specific failure mode would not occur,
so the workflow's dependency line is very likely fine as written.

What remains genuinely unestablished, and is not investigated further here: whether
`.github/workflows/standard-self-check.yml` has ever executed at all. FACT FROM PACKAGE, already
recorded in this repository at `org/SCOPE_DECISIONS.md`: "GitHub Actions is disabled at the
organisation level ... the conformance workflow is installed but dormant. It never executes and no
status check exists." Given that, "has CI ever run green" is not merely unanswered but currently
unanswerable from outside the organisation's Actions settings, and it would have been the wrong
finding to record this workflow's dependency list as the open question — the dependency list is very
likely fine; its inability to run at all is the fact already established and recorded elsewhere in
this repository.

> **ANSWERED at 0.13.0 — this paragraph is left as written, and corrected here rather than
> rewritten.**
>
> The workflow has executed. It ran on pull request #2 on 30 August 2026 — GitHub Actions run
> `33327048783`, check run `Contract and installer tests`, conclusion `success`, 26 seconds — and
> installed its dependencies with the very `python -m pip install pyyaml jsonschema` line this
> section reasoned about, on a clean `ubuntu-latest` runner. The reasoning above about `referencing`
> resolving transitively was correct, and is now confirmed by execution rather than inference.
>
> The premise was wrong. Actions was not disabled for this repository, or ceased to be, and the
> quoted claim in `org/SCOPE_DECISIONS.md` was false. That document was deleted at 0.13.0 — it
> recorded three adopting repositories that do not exist — so the quotation above now cites a file
> that is no longer in the tree. It is retained verbatim because it is what this record actually
> relied on at `v0.11.0`, and removing it would hide the reason a wrong conclusion was reached.
>
> The lesson is the one this record already draws twice elsewhere: an instrument whose result was
> never observed is not evidence. "Unanswerable from outside the organisation's Actions settings"
> was itself an inference from a document, not a check — and one push settled it.

## Limitations and follow-up

None of F1, F2 or F3 is fixed by this record. Fixing each is separately scoped:

- F1 requires either declaring the precondition explicitly (skip or fail loudly when
  `core.hooksPath` is set, rather than crashing) or making the test harness itself neutralise the
  condition the way this record's evidence did.
- F2 requires either vendoring or documenting the virtual-environment step as part of the
  installation instructions, or a system-package-based alternative.
- F3 requires `validate_contracts.py` to report an executed-check count symmetrically with
  `test_install_and_check.py`.

## Approval

- Technical reviewer: not yet assigned.
- Method owner: not yet assigned.
- Independent validator: not yet assigned.
- Release authority: not yet assigned.

This record does not itself constitute approval, validation, or release authorisation.
