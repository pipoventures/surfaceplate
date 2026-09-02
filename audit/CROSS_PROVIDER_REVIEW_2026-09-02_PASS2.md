# Cross-provider adversarial review, pass 2 — 2026-09-02

**What this is.** The second cross-provider adversarial review (`org/RELEASE_PLAN.md` item 9,
pass 2; `H3`), run by the maintainer on 2026-09-02 with the curated prompt
`audit/GEMINI_ADVERSARIAL_REVIEW_PROMPT_CURATED.md` and the 27-file `EVIDENCE_BUNDLE.md` built from
`main` at `56d2163`. The reviewer's text is reproduced below **verbatim**, as the maintainer pasted
it into the implementing session (https://claude.ai/code/session_01Bz6QZWcsg9tRFuH9gS331Z); nothing
has been corrected, reordered or trimmed. The provider and model are the maintainer's to state and
are recorded in `org/FINDINGS.md` beside each finding this review raised (`F101` to `F111`), where
each claim is assessed against the code and given a status. The reviewer had no code execution,
so the manifest recomputation (`H4`, `F6`) remains an evidence gap.

**How to read it.** The reviewer's own labels apply: `FACT FROM PACKAGE` is what it read in the
bundle, `INFERENCE` its reasoning, `EVIDENCE GAP` what the 27 files could not establish. Where the
implementing session found a claim to rest on a decision already recorded, or on a fact the bundle
did not contain, the finding entry says so; the text below is the record of what was said.

---

### 1. Verdict on Files Reviewed

**PASS WITH REQUIRED CHANGES**

* **Scope**: This verdict is strictly confined to the 27 files provided in `EVIDENCE_BUNDLE.md`. It does not constitute an audit, approval, or validation of the complete Surfaceplate framework, its unprovided checker source (`check_conformance.py`), its installer, or repository release readiness.

* **Basis**: The core schemas, definitions, and seed concepts are structurally coherent and demonstrate rigorous adversarial awareness. However, material flaws exist in failure-state atomicity (`scaffold.py`/`wizard.py`), the automated bypass of human authorship during replay (`defaults.py`/`wizard.py`), and the structural inability of the checker to distinguish empty scaffold seeds from functioning engineering practices (`scaffold.py`/seeds).

---

### 2. Manifest Recomputation Result

* **Recomputation Digest**: `EVIDENCE GAP` — A code execution tool is not available in this environment; per instruction, no digest was computed by hand or estimated.

* **Declared Profile Digest**: `46ad705f47e93e10981c20fa9704daa33da44bdf6a04dde842278318824cbde0` (`governance/application-profile.yaml`, `adoption.framework_digest`).

* **Match Status**: `EVIDENCE GAP` (unverified mathematically).

* **Disclosure of Lag**: `FACT FROM PACKAGE` — The framework explicitly documents this lag in `governance/application-profile.yaml` under `adoption.framework_digest` notes. It discloses that because Surfaceplate installs into itself, writing the profile alters the working tree manifest; thus, `framework_digest` records the installation source tree rather than matching the current live `MANIFEST.sha256`.

---

### 3. Critical Findings

**CRIT-01: Non-Atomic Scaffold Writes and Orphaned Artifacts on Partial Failure**

* **Location**: `surfaceplate/adopt/scaffold.py` (`write()`), `surfaceplate/adopt/wizard.py` (`run()`)

* **Evidence**:
* `scaffold.write()` iterates through accepted offers and creates files sequentially on disk using `open(target, "x")`. If an exception occurs midway through the loop (e.g., I/O failure, disk exhaustion, permission revocation), earlier files remain on disk. `scaffold.write()` catches only `FileExistsError` and `OSError`, appending to `problems` and continuing.
* In `wizard.py`, `created, scaffold_problems = scaffold.write(repo, flow.accepted_scaffold)` runs *before* `_write_atomically(target, rendered)` (the profile). If `_write_atomically` fails, `wizard.py` catches `Exception` and raises `PartialWrite(exc, created, scaffold_problems)` without rolling back `created`.

* **Impact**:
* `FACT FROM PACKAGE`: `wizard.py`'s module docstring claims: `run()` "guarantee[s] that a cancelled run leaves the repository untouched".
* `INFERENCE`: This claim is false. A failed run can leave multiple scaffolded seed files committed to the working tree while failing to write `application-profile.yaml` or its provenance record. On subsequent runs, `_occupied()` in `scaffold.py` detects these files, preventing re-scaffolding, while `_refuse_if_already_adopted` may be confused if state is partial.

* **Why It Matters**: Violates invariant I2 (misrepresenting system behavior). An aborted or crashed wizard execution leaves untracked, unreferenced governance files strewn across an adopter's repository.

* **Remediation**:
* `RECOMMENDATION`: Implement a transactional rollback mechanism in `scaffold.write()` and `wizard.run()`. If profile rendering, schema validation, or file writes fail, delete any files created during that session before raising.

**CRIT-02: Scaffolded Seeds Satisfy Gates Mechanically Without Practice Existing**

* **Location**: `surfaceplate/adopt/scaffold.py`, `surfaceplate/core/PREREQUISITE_GATES.md`, and all files under `surfaceplate/seeds/*`

* **Evidence**:
* `PREREQUISITE_GATES.md` defines gate enforcement: `SP032` checks that precondition artifacts exist, are non-empty, and contain no placeholder tokens (`replace-me`, `TODO`, `TBD`, `TBC`).
* Every seed under `surfaceplate/seeds/` (e.g., `risk-classification.md`, `release-checklist.md`, `activity-register.md`, `decision-log.md`) is non-empty (>0 bytes) and contains none of the forbidden tokens.
* Specifically, `surfaceplate/seeds/risk-classification.md` leaves the table columns blank for levels 0–3 and states *"The meanings are not declared yet"*, but contains no flagged tokens. `surfaceplate/seeds/release-checklist.md` states *"This checklist quotes the standard and declares nothing of this repository's own yet"*, but contains no flagged tokens.

* **Impact**:
* `FACT FROM PACKAGE`: When `scaffold.py` writes these seeds and `defaults.py` sets `effective_from` to today's date, `check_conformance.py` evaluates every associated prerequisite gate as completely satisfied.
* `INFERENCE`: The three mitigations claimed in `scaffold.py` ("the seed says so in its own text, the offer says so at the point of choosing, and the run's closing report says so") are purely informative prose; they exert zero programmatic constraint.

* **Why It Matters**: The wizard allows an adopting repository to scaffold empty registers and pass every prerequisite gate in CI on day 1 with zero actual engineering governance in place. This directly undermines the framework's core premise that prerequisite gates test reality rather than self-declaration.

* **Remediation**:
* `RECOMMENDATION`: Seeds that require adopter-supplied definitions (such as `risk-classification.md` and `test-conventions.md`) must include a placeholder token (e.g., `replace-me`) in their required declaration sections so that `SP032` legitimately fails until the adopter defines their repository-specific rules. Alternatively, keep gates deferred until entries exist.

---

### 4. Material Findings

**MAT-01: Silent Adoption of Default Proposals via `--propose` and `--answers` Replay**

* **Location**: `surfaceplate/adopt/wizard.py` (`propose()`, `replay()`), `surfaceplate/adopt/defaults.py`

* **Evidence**:
* `wizard.propose()` populates `answers` with `_proposal_entry(proposal)` for every field that has a proposal. Only fields with no proposal are assigned `NEEDS_HUMAN`.
* In `wizard.replay()`, verification only checks: `pending = [key for key, value in record["answers"].items() if value == NEEDS_HUMAN]`.
* If a human fills in only the few `needs-human` lines (such as `gates.<id>.status`) and leaves all proposed fields untouched, `replay()` feeds all proposals—including worked example rationales (`provenance.EXAMPLE`), computed review dates, and discovered paths—directly into the profile via `ScriptedInterview`.

* **Impact**:
* `INFERENCE`: The rule *"It asks, the human answers, the tool writes"* is bypassed in headless/replay mode. An adopter can accept standard-shipped rationales and synthetic assertions across 15+ gates and controls without writing a single sentence of rationale, while the generated profile claims compliance.

* **Why It Matters**: Contradicts the framework's anti-gaming doctrine. An adopter can generate an entire `application-profile.yaml` populated with pre-baked boilerplate justifications simply by replacing 3 or 4 strings.

* **Remediation**:
* `RECOMMENDATION`: Require `adopt --answers` to explicitly distinguish between accepted proposals and human-authored answers, or require an explicit confirmation flag/entry acknowledging each adopted example rationale.

**MAT-02: `effective_from` Temporal Boundary and Schema Validation Flaws**

* **Location**: `surfaceplate/schemas/application-profile.schema.yaml` (`$defs/prerequisite_gate/properties/effective_from`), `surfaceplate/adopt/defaults.py` (`propose_gates()`)

* **Evidence**:
* The schema enforces `effective_from` via pattern:
`'^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$'`.
* `FACT FROM PACKAGE`: The pattern admits invalid calendar dates (e.g., `2026-02-31`, `2026-13-45`), admits minute-fraction strings without seconds (e.g., `14:30.500`), and admits offset-naive datetimes alongside offset-aware datetimes.
* In `defaults.py`, `propose_gates()` assigns:
`Proposal(f"{prefix}.effective_from", adoption_date, provenance.COMPUTED, ...)` where `adoption_date` is a plain `YYYY-MM-DD` date.

* **Impact**:
* `INFERENCE`: If an adopter runs `adopt` midway through a working day, `defaults.py` proposes a date interpreted as midnight that morning (`YYYY-MM-DDT00:00:00`). Any commit pushed earlier that day touching gated paths immediately triggers `SP035`. If the adopter subsequently attempts to advance `effective_from` to an exact instant (e.g., `14:30:00`) to clear the violation, `SP034` permanently fails the profile because moving the timestamp forward is strictly forbidden and never graced.

* **Why It Matters**: The feature introduced to solve `F47` (accepting an instant) is not utilized by the wizard's defaults, leading unsuspecting adopters into an unrecoverable `SP034` failure loop on day 1.

* **Remediation**:
* `RECOMMENDATION`: Update `defaults.py` to propose a full ISO-8601 instant with timezone offset (or UTC `Z`) matching the execution time of the wizard. Refine the regex to reject invalid minute/second combinations.

**MAT-03: Unbacked Assurance State in Application Profile Schema**

* **Location**: `surfaceplate/schemas/application-profile.schema.yaml` (`adoption.adoption_status`, `adoption.independent_validator`)

* **Evidence**:
* `adoption_status` is an enum: `[in_progress, complete, blocked, deferred]`.
* The schema requires `status_rationale` only when `adoption_status` is `blocked` or `deferred`.
* When `adoption_status` is `complete`, `status_rationale` is optional, `independent_validator` is nullable, and no verification digest, test run ID, or evidence reference is required.

* **Impact**:
* `FACT FROM PACKAGE`: A profile can declare `adoption_status: complete` with `independent_validator: null` and zero attached evidence, and validate cleanly against the schema.

* **Why It Matters**: Principle 7 of `CONTROL_PRINCIPLES.md` mandates that lifecycle, validation status, approval status, and execution status be kept distinct and backed by evidence. In the schema, the final assurance state (`complete`) is an unverified self-assertion.

* **Remediation**:
* `RECOMMENDATION`: Require `status_rationale` and an explicit evidence or audit reference when `adoption_status: complete` is declared.

**MAT-04: Contradiction Between Baseline Control Declaration and Deferred Gate**

* **Location**: `governance/application-profile.yaml` (`baseline_controls.agent_work_packets`, `prerequisites[id=work_contract]`)

* **Evidence**:
* Under `baseline_controls`, `agent_work_packets` is marked `required` with rationale: *"All work in this repository arrives as a bounded packet with stated done-criteria. This is how the repository has actually operated; the register now records it."*
* Under `prerequisites`, gate `work_contract` is marked `deferred` with rationale: *"Work packets arrive through an operator conversation and are not committed here, so there is no artefact for the gate to check."*

* **Impact**:
* `INFERENCE`: The profile claims that the baseline control is fully operational while admitting in the prerequisite gate that the necessary artifacts do not exist in the repository and are merely ephemeral chat conversations.

* **Why It Matters**: Surfaceplate judges itself by a standard where it claims a practice exists in an unverified baseline declaration while deferring the prerequisite gate that actually verifies it.

* **Remediation**:
* `RECOMMENDATION`: Harmonize the rationale: either commit operator work packets to git (under `activity/` or `org/work-packets/`) and require the gate, or explicitly document in `agent_work_packets` that the control operates outside git and is unverified.

---

### 5. Minor Findings

**MIN-01: Overly Permissive Template Detection in `_refuse_if_already_adopted`**

* **Location**: `surfaceplate/adopt/wizard.py` (`_refuse_if_already_adopted()`)

* **Evidence**:
* The loop checks `_TEMPLATE_SCALARS`:
```python
for keys in _TEMPLATE_SCALARS:
    node: object = document
    for key in keys:
        node = node.get(key) if isinstance(node, dict) else None
    if isinstance(node, str) and node.strip() == "replace-me":
        return  # the untouched template - fair game
```

* **Impact**:
* `INFERENCE`: If *any single one* of the five scalar fields is `"replace-me"` (for instance, if an adopter filled out everything but left `application_id: replace-me`), the function returns early without raising `AlreadyAdopted`, permitting the wizard to overwrite the existing custom profile.

* **Remediation**:
* `RECOMMENDATION`: Require *all* template identifying scalars (or at least both `application_id` and `owner`) to equal `"replace-me"` before treating the file as an unedited template.

**MIN-02: Hardcoded Scanner Notes Injected Unconditionally**

* **Location**: `surfaceplate/adopt/sections.py` (`build_controls()`)

* **Evidence**:
* `sections.py` defines `SCANNER_NOTES = "Blocking."` and injects it directly into `baseline_controls["secret_hygiene"]["scanner"]["notes"]`.

* **Impact**:
* `FACT FROM PACKAGE`: The tool injects a factual assertion about the adopter's scanner ("Blocking.") without prompting the adopter or verifying scanner configuration.

* **Remediation**:
* `RECOMMENDATION`: Allow adopter input for scanner notes or leave the field omitted unless supplied.

**MIN-03: Improper Gate Deferral Representation in `adoption.deferrals`**

* **Location**: `governance/application-profile.yaml` (`adoption.deferrals`)

* **Evidence**:
* `governance/application-profile.yaml` lists `x-surfaceplate-work-contract-gate` and `x-surfaceplate-risk-classification-gate` under `adoption.deferrals`.

* **Impact**:
* `FACT FROM PACKAGE`: `$defs/deferral` in `application-profile.schema.yaml` specifies `control_id` matching selectable control IDs or custom extensions (`x-*`). Gate deferrals belong in `prerequisites` (where they are already declared). Inventing synthetic `x-*` control IDs to mirror gate deferrals creates duplicate, misleading governance records.

* **Remediation**:
* `RECOMMENDATION`: Remove gate deferrals from `adoption.deferrals` in `application-profile.yaml` and rely solely on `prerequisites`.

---

### 6. The Binding Rule, Tested

The rule states: *"It asks, the human answers, the tool writes. It never selects a conformance level, invents a rationale, or sets a date."*

* **`sections.py`**:
* Does it invent values?
* `FACT FROM PACKAGE`: It sets `"adoption_date": _dt.date.today().isoformat()`. It directly sets a date.
* `FACT FROM PACKAGE`: It sets `precondition.description` to `catalogue.GATE_CATALOGUE[spec.id]` and `gated_activity.description` to `f"Changes under {paths}."` if no answer is provided.
* `FACT FROM PACKAGE`: It sets `enforcement` to `["history_audit", "review"]` (`DERIVED_ENFORCEMENT`) by default without asking.
* `FACT FROM PACKAGE`: It sets `SCANNER_NOTES = "Blocking."` unconditionally.

* *Evaluation*: The framework defends these as facts about the standard or mechanical consequences. However, asserting that an external CI scanner is "Blocking." and setting the gate's enforcement methods are judgements about the adopter's repository, not facts about the framework.

* **`defaults.py`**:
* Does it propose honest origins?
* `FACT FROM PACKAGE`: It proposes worked example prose (`example_answers.py`) as `provenance.EXAMPLE` for every control rationale.
* `FACT FROM PACKAGE`: For blank risk fields, it proposes `"Not stated at adoption."` as `provenance.COMPUTED`.
* `FACT FROM PACKAGE`: It proposes `effective_from` as `adoption_date`.

* Does a proposal reach disk without human input?
* `INFERENCE`: In interactive TUI mode, screens present the proposals for human review (`EVIDENCE GAP` for exact UI behavior).
* `FACT FROM PACKAGE`: In non-interactive mode (`adopt --propose` followed by `adopt --answers`), any proposal not marked `NEEDS_HUMAN` is written directly to disk upon replay. The tool writes example rationales and dates without human authorship.

* **`scaffold.py`**:
* Can it overwrite files? No. `_occupied()` checks `os.path.lexists()`, and `open(..., "x")` enforces atomic creation.
* Can it traverse symlinks or escape root? No. `_inside()` resolves paths against repository root, and all seedable paths are hardcoded relative constants.
* Does it leave partial state on failure? Yes (see CRIT-01).
* Does it make gates pass while practice is absent? Yes (see CRIT-02).

* **`wizard.py`**:
* Soundness of verification:
* `_verify()` round-trips YAML, checks JSON Schema, and scans for placeholder tokens.
* `FACT FROM PACKAGE`: It does *not* verify that precondition files actually exist on disk, that CI step references exist in workflow files, that `effective_from` represents a valid calendar date, or that `conformance_level` control dependencies are satisfied.

---

### 7. The Framework Judged Against Its Own Standard

* **Claim vs. Reality in Core Documents**:
* *Claim*: Principle 11 ("Automation can produce evidence, not approval or risk acceptance") and `AI_OPERATING_MODEL.md` ("Agents must not fabricate approval, independent validation, risk acceptance, production readiness").
* *Reality in Bundle*: In `governance/application-profile.yaml`, `adoption_status: complete` is declared while `independent_validator: null`. The status rationale notes that multiple findings (`F5, F9, F11, F12, F13, F16`) remain open in `org/FINDINGS.md` and actions remain live. The profile is self-approved by the sole maintainer.
* *Claim*: `CONFORMANCE_LEVELS.md` emphasizes that `agent_work_packets` and `actual_diff_review` are declarations that nothing checks. In `governance/application-profile.yaml`, Surfaceplate declares `agent_work_packets: required` while deferring the prerequisite gate `work_contract` because work packets are not committed.

* **Declared vs. Verified Controls in the Worked Profile**:
* `FACT FROM PACKAGE`: Looking at `governance/application-profile.yaml`, there is no syntactic distinction between machine-verified controls and unverified declarations.
* `agent_work_packets` and `actual_diff_review` are marked `decision: required` with prose rationales.
* `dependency_lock` is marked `decision: required` with `implementation_reference: pyproject.toml`.
* `deterministic_tests` is marked `decision: required` with `implementation_reference: Test the installer and the conformance checker end to end`.
* `INFERENCE`: A reader inspecting the profile cannot tell that the first two are unverified honor-system statements, the third checks file existence and git-tracking, and the fourth checks that a workflow step exists and does not discard its exit code. An adopter reading their own profile will naturally overestimate the extent of mechanical verification.

---

### 8. What Could Not Be Assessed (Evidence Gaps)

The following components could not be evaluated due to exclusion from `EVIDENCE_BUNDLE.md`:

1. **Conformance Checker Enforcement Engine (`surfaceplate/check_conformance.py`)**:
* *Gap*: Cannot verify how finding codes `SP001`–`SP059` are implemented, how `PLACEHOLDER_PATTERN` is defined, how `effective_from` is parsed and compared against git log, or how CI workflow ASTs are inspected for exit-code suppression.
* *Needed File*: `surfaceplate/check_conformance.py`.

2. **Standard Installer (`surfaceplate/install_standard.py`)**:
* *Gap*: Cannot assess how `.standards/INSTALL.json` is constructed, how standard-owned files are tracked, or how hook permissions are set.
* *Needed File*: `surfaceplate/install_standard.py`.

3. **Cross-Field Contract Validation (`tests/validate_contracts.py`)**:
* *Gap*: Cannot verify semantic enforcement linking `conformance_level` to mandatory `control_decisions`.
* *Needed File*: `tests/validate_contracts.py`.

4. **Interactive TUI and Screen Execution (`surfaceplate/adopt/tui/*`, `interview.py`, `flow.py`)**:
* *Gap*: Cannot verify whether interactive screens force explicit human keystrokes for proposals or allow silent click-throughs.
* *Needed Files*: `surfaceplate/adopt/interview.py`, `surfaceplate/adopt/flow.py`, `surfaceplate/adopt/tui/screens.py`.

5. **Non-Profile Schemas**:
* *Gap*: Cannot assess validation rules for method registry, run lineage, overrides, or gate exceptions.
* *Needed Files*: `surfaceplate/schemas/*.schema.yaml` (remaining 5 schemas).

6. **Git History and Repository Audit Trail**:
* *Gap*: Cannot evaluate git-history auditing behavior or commit graph traversal.
* *Needed Data*: Repository `.git` commit graph.

---

### 9. Over-Engineering Assessment

* **Narrative Comments in Python Files**:
* `FACT FROM PACKAGE`: The Python files (`sections.py`, `defaults.py`, `scaffold.py`, `wizard.py`) contain extensive narrative docstrings detailing past defects (`F14`, `F15`, `F22`, `F25`, `F32`, `F40`, `F61`, `F62`, `F77`, `F78`, `F79`, `F84`, `F93`, `F99`, `F100`), decision records, and arguments with prior reviewers.
* `INFERENCE`: This constitutes a significant maintenance risk. Comment-to-code drift is inevitable (as admitted in `CONFORMANCE_LEVELS.md` regarding `F52`). Baking project historical lore and debate transcripts into module docstrings obscures the functional logic and turns maintenance into an exercise in archaeological reconciliation. Git history and decision records exist for this purpose.

* **Proportionality of Architecture**:
* For what is described as a local CLI tool without databases or background services, the governance apparatus is extraordinarily dense: 19 gates, 12 controls, 56 checker error codes, custom regex datetime validators, dual preview/replay configuration flows, and a 16-seed scaffolding subsystem.
* The framework approaches self-referential hyper-specification: extensive effort is spent managing the bureaucracy of empty registers, provenance sidecars, and decision-log seeds to satisfy check codes, rather than verifying functional software quality.

---

### 10. Required Changes

1. **Atomic Rollback in Scaffold and Wizard (`scaffold.py`, `wizard.py`)**:
* Implement rollback logic so that any failure during `scaffold.write()`, profile rendering, or sidecar write removes all newly created scaffold files, preserving working tree cleanliness.

2. **Insert Required Placeholders in Structural Seeds (`seeds/*`)**:
* Update seeds that require repository-specific customization (especially `risk-classification.md`, `test-conventions.md`, and `release-checklist.md`) to include a flagged placeholder (e.g., `replace-me`). Ensure `SP032` blocks adoption until the adopter replaces the placeholder with actual local rules.

3. **Strict Mode for Headless Replay (`wizard.py`, `defaults.py`)**:
* Modify `wizard.replay()` so that example rationales and computed defaults cannot be silently adopted into the profile without explicit acknowledgement.

4. **Instant-Aware Gate Defaults (`defaults.py`)**:
* Update `propose_gates()` in `defaults.py` to propose an exact ISO instant with timezone for `effective_from` rather than a naive date, preventing mid-day adoptions from failing against morning commits.

5. **Tighten Schema Requirements for Completed Adoption (`application-profile.schema.yaml`)**:
* Add validation rules requiring `status_rationale` when `adoption_status: complete`.

6. **Refactor Template Scalar Check (`wizard.py`)**:
* Update `_refuse_if_already_adopted()` to require that *all* identifying template scalars equal `"replace-me"` before permitting a profile overwrite.

7. **Prune Narrative Historical Docstrings (`sections.py`, `defaults.py`, `scaffold.py`, `wizard.py`)**:
* Extract historical debugging narratives and PR-by-PR debate logs out of Python docstrings and into the appropriate `org/decisions/` records or `CHANGELOG.md`. Keep code documentation focused strictly on current behavior and invariants.
