# The matrix's first run against the code before the fixes — historical record (`ACT-057`)

**Historical. Hand-written, dated 2026-09-02, never regenerated.** This is the preserved output of the
matrix suite run against the wizard *as it stood before the four fixes* of `ACT-057`, so that the
claim "seen to fail first" in `F97` to `F100` is a quotable output rather than a sentence. The live
report of what the suite measures now is `audit/validation/ADOPT_MATRIX.md`, generated on every run;
this file is not compared by anything and describes a state of the code that no longer exists.

## What was run

- **Code under test:** the tree at commit `4377470` ("ACT-057: DR-58 taken"), which is `main` at
  `5461713` plus the decision record and the register row — the wizard before `F97` to `F100` were fixed.
- **Suite:** `tests/adopt_matrix.py`, `tests/adopt_matrix_screens.py` and `tests/test_adopt_matrix.py`
  copied from the branch head (`a11c8a7`) into a scratch worktree of that commit. The suite is the
  same code that produces the live report; only the code it drives differs.
- **Command:** `python tests/test_adopt_matrix.py --only T` from the worktree, with the branch's
  virtualenv (Python 3.12, Textual 8.2.8), on 2026-09-02.
- **Why 210 cases, not 208:** the enumeration reads the above-floor list from the plan, and the
  pre-fix plan offered `documentation_authority` at `essential`, so two more single-control cases
  existed. Case ids below are the pre-fix ids; the live report's ids differ by that offset from `T4`
  onward.

## Result

```
the matrix: 210 cases enumerated from the catalogue
ran 210 case(s), 44283 checks, in 146s
ADOPT_MATRIX=FAIL  (28 failed, 44255 passed; 210 runs)
```

Every one of the 28 failed checks belongs to one of the fifteen cases below, and every case maps to
one of the four findings. Nothing else failed: the 44,255 passing checks are the same oracle applied
to the same code, which is what makes the fifteen a finding about the wizard and not about the suite.

## The failing cases, verbatim, by finding

### `F97` — `documentation_authority` offered above the floor at `essential`; the profile fails `SP052`

```
  FAIL  T4-115   essential/no-ui  rich  artefacts found; above floor: all                            137 checks  0.29s  WARN ['SP052']
        - the checker passes with no findings against what was written: WARN: SP052 documentation_authority is required without the gate that verifies it
  FAIL  T4-119   essential/no-ui  rich  artefacts found; above floor: documentation_authority         95 checks  0.24s  WARN ['SP052']
        - the checker passes with no findings against what was written: WARN: SP052 documentation_authority is required without the gate that verifies it
  FAIL  T4-124   essential/no-ui  bare  artefacts found; above floor: all                            143 checks  0.27s  WARN ['SP052']
        - the checker passes with no findings against what was written: WARN: SP052 documentation_authority is required without the gate that verifies it
  FAIL  T4-128   essential/no-ui  bare  artefacts found; above floor: documentation_authority         97 checks  0.22s  WARN ['SP052']
        - the checker passes with no findings against what was written: WARN: SP052 documentation_authority is required without the gate that verifies it
```

### `F98` — a run cancelled after the scaffold stage and resumed never creates the decision record it names

```
  FAIL  T6-184   essential/no-ui  bare  resume (review)                                               98 checks  0.41s
        - git sees exactly the profile, the sidecar and the created files: unexpected []; missing ['docs/decisions/DR-0001-adopt-surfaceplate.md']
        - the run created exactly the files the chosen seeds name: created ['activity/register.md']; expected ['activity/register.md', 'docs/decisions/DR-0001-adopt-surfaceplate.md']
  FAIL  T6-189   standard/no-ui   bare  resume (review)                                              307 checks  0.89s
        - git sees exactly the profile, the sidecar and the created files: unexpected []; missing ['docs/decisions/DR-0001-adopt-surfaceplate.md']
        - the run created exactly the files the chosen seeds name: created ['CHANGELOG.md', 'activity/register.md', 'docs/DEPENDENCY_REVIEW.md', 'docs/OUTPUT_VALIDATION.md', 'docs/RELEASE_CHECKLIST.md', 'docs/decisions/decision-log.md', 'docs/testing/TEST_CONVENTIONS.md', 'documentation/governance/inventory/source_of_truth_matrix.yaml', 'governance/DATA_SOURCES.md', 'governance/RISK_CLASSIFICATION.md']; expected ['CHANGELOG.md', 'activity/register.md', 'docs/DEPENDENCY_REVIEW.md', 'docs/OUTPUT_VALIDATION.md', 'docs/RELEASE_CHECKLIST.md', 'docs/decisions/DR-0001-adopt-surfaceplate.md', 'docs/decisions/decision-log.md', 'docs/testing/TEST_CONVENTIONS.md', 'documentation/governance/inventory/source_of_truth_matrix.yaml', 'governance/DATA_SOURCES.md', 'governance/RISK_CLASSIFICATION.md']
  FAIL  T6-194   full/no-ui       bare  resume (review)                                              341 checks  0.94s
        - git sees exactly the profile, the sidecar and the created files: unexpected []; missing ['docs/decisions/DR-0001-adopt-surfaceplate.md']
        - the run created exactly the files the chosen seeds name: created ['CHANGELOG.md', 'activity/register.md', 'docs/DEPENDENCY_REVIEW.md', 'docs/FINDINGS.md', 'docs/OUTPUT_VALIDATION.md', 'docs/RELEASE_CHECKLIST.md', 'docs/decisions/decision-log.md', 'docs/testing/TEST_CONVENTIONS.md', 'documentation/governance/inventory/source_of_truth_matrix.yaml', 'governance/DATA_SOURCES.md', 'governance/RISK_CLASSIFICATION.md', 'governance/method-registry/README.md', 'governance/overrides/README.md', 'governance/run-lineage/README.md']; expected ['CHANGELOG.md', 'activity/register.md', 'docs/DEPENDENCY_REVIEW.md', 'docs/FINDINGS.md', 'docs/OUTPUT_VALIDATION.md', 'docs/RELEASE_CHECKLIST.md', 'docs/decisions/DR-0001-adopt-surfaceplate.md', 'docs/decisions/decision-log.md', 'docs/testing/TEST_CONVENTIONS.md', 'documentation/governance/inventory/source_of_truth_matrix.yaml', 'governance/DATA_SOURCES.md', 'governance/RISK_CLASSIFICATION.md', 'governance/method-registry/README.md', 'governance/overrides/README.md', 'governance/run-lineage/README.md']
```

### `F99` — `--propose` marks every above-floor control's lines `needs-human`, and `--answers` refuses until they are filled

```
  FAIL  T6-164   essential/no-ui  bare  propose-replay                                                 3 checks  0.11s
        - every needs-human line is a decision the case answers (or a gate status): ['controls.assurance_findings.rationale', 'controls.assurance_findings.implementation_reference', 'controls.contract_tests.rationale', 'controls.contract_tests.implementation_reference', 'controls.deterministic_tests.rationale']
        - the case ran without an unexpected exception: KeyError: 'controls.assurance_findings.rationale'
  FAIL  T6-165   essential/no-ui  rich  propose-replay                                                 3 checks  0.13s
        - every needs-human line is a decision the case answers (or a gate status): ['controls.assurance_findings.rationale', 'controls.contract_tests.rationale', 'controls.deterministic_tests.rationale', 'controls.documentation_authority.rationale', 'controls.method_registry.rationale']
        - the case ran without an unexpected exception: KeyError: 'controls.assurance_findings.rationale'
  FAIL  T6-166   essential/no-ui  mixed propose-replay                                                 3 checks  0.12s
        - every needs-human line is a decision the case answers (or a gate status): ['controls.assurance_findings.rationale', 'controls.assurance_findings.implementation_reference', 'controls.contract_tests.rationale', 'controls.deterministic_tests.rationale', 'controls.documentation_authority.rationale']
        - the case ran without an unexpected exception: KeyError: 'controls.assurance_findings.rationale'
  FAIL  T6-167   standard/no-ui   bare  propose-replay                                                 3 checks  0.14s
        - every needs-human line is a decision the case answers (or a gate status): ['controls.assurance_findings.rationale', 'controls.assurance_findings.implementation_reference', 'controls.method_registry.rationale', 'controls.method_registry.implementation_reference', 'controls.overrides.rationale']
        - the case ran without an unexpected exception: KeyError: 'controls.assurance_findings.rationale'
  FAIL  T6-168   standard/no-ui   rich  propose-replay                                                 3 checks  0.15s
        - every needs-human line is a decision the case answers (or a gate status): ['controls.assurance_findings.rationale', 'controls.method_registry.rationale', 'controls.overrides.rationale', 'controls.provenance.rationale', 'controls.run_lineage.rationale']
        - the case ran without an unexpected exception: KeyError: 'controls.assurance_findings.rationale'
  FAIL  T6-169   standard/no-ui   mixed propose-replay                                                 3 checks  0.13s
        - every needs-human line is a decision the case answers (or a gate status): ['controls.assurance_findings.rationale', 'controls.assurance_findings.implementation_reference', 'controls.method_registry.rationale', 'controls.method_registry.implementation_reference', 'controls.overrides.rationale']
        - the case ran without an unexpected exception: KeyError: 'controls.assurance_findings.rationale'
```

### `F100` — `--edit` applies no field validator; an untracked artefact is written and fails `SP032`

```
  FAIL  T6-196   standard/no-ui   rich  edit                                                          18 checks  3.08s
        - an edit to an untracked artefact path is refused with the field's own rule: edited
        - and the profile is unchanged by the refusal:
        - after the refused edits the checker still passes: WARN ['SP032']
  FAIL  T6-197   standard/no-ui   bare  edit                                                          18 checks  3.16s
        - an edit to an untracked artefact path is refused with the field's own rule: edited
        - and the profile is unchanged by the refusal:
        - after the refused edits the checker still passes: WARN ['SP032']
```

## How each was closed

Recorded in `org/FINDINGS.md` under each code, with the regression in `tests/test_adopt.py` that was
seen to fail before the fix and the decision record where one was taken (`DR-59` for `F97`). After
the fixes the same suite reports `ADOPT_MATRIX=PASS  (45257 checks; 208 runs)` locally and on the
runner (`audit/validation/ADOPT_MATRIX.md`; PR #60, run 33682871213).

## What this file does not show

- The earlier development runs of the suite, in which the harness itself was wrong in several places
  (twin repositories cloned under a different directory name, resume re-supplying answers already in
  the draft, the edit case addressing a gate with no artefact). Those were the suite's defects, fixed
  before this run; this is the first run of the corrected suite against the uncorrected wizard.
- Independent confirmation. The same party wrote the suite, ran it, read the failures and fixed the
  code. `org/decisions/README.md` applies: no independent validator exists for this repository.
