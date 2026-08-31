# Engineering Control Kit Setup Guide

This guide is the exact adoption sequence for a new repository. It is written to be independent of programming language, framework, database, CI provider, and AI vendor.

The kit supplies control principles, contracts, templates, and reference tests. It does **not** install a platform, create runtime enforcement automatically, approve a method, or replace human governance.

For an interactive guided installation, use `prompts/github-copilot-adoption-wizard.prompt.md` after copying the kit into the receiving repository. The prompt makes Copilot act as the discovery wizard and bounded implementer; it does not remove the human decision gates in this guide.

## What you need before starting

- A new or existing application repository.
- A named application owner.
- A named canonical kit maintainer and change authority.
- A technical reviewer.
- A method/model owner where the application produces material quantitative or AI outputs.
- An independent validator when the application's risk profile requires Level 3 review.
- An approved repository location for the kit or a pinned kit release archive.
- An approved secret store and dependency-management process for the receiving repository.

Do not begin adoption if the repository cannot identify who owns the application and who controls future kit updates.

## Step 1: Create the repository boundary

Choose one of these patterns:

- **Pinned copy:** copy the kit into a controlled directory such as `engineering-control-kit/` and record the kit version and ZIP SHA-256 in the repository's decision record.
- **Referenced release:** retain the kit ZIP in an approved internal artefact store and record its version and trusted digest. Do not depend on a mutable URL or an unpinned branch.

Do not copy PEM application code, PCAF methodology, R/Shiny modules, client-branch rules, or PEM-specific UI patterns. Copy the control concepts and use the receiving repository's native implementation.

Record:

- kit version;
- kit digest;
- adoption date;
- application owner;
- kit maintainer;
- repository classification;
- initial decision record ID.

## Step 2: Copy and inspect the package

Copy the package files into the repository or unpack the pinned ZIP. Verify:

1. the archive contains only intended files;
2. paths are relative and use `/` separators;
3. `MANIFEST.sha256` has exactly one entry for every payload;
4. every payload digest matches;
5. no secrets, customer data, private certificates, or uncontrolled fixtures are present.

Use the receiving repository's approved archive and secret-scanning commands. Store the command results in the adoption decision record. The kit's own manifest proves integrity only after the digest is trusted; it does not prove authenticity.

## Step 3: Create the application profile

Copy `templates/application-profile.yaml` to the receiving repository's canonical configuration location, for example:

```text
config/governance/application-profile.yaml
```

Replace every `replace-me` value. Do not leave placeholders in the active profile.

Complete:

- `schema_version: "1.0"`;
- `application_id` and display name;
- application owner;
- technology description in `stack` if useful, without making it a kit requirement;
- intended use, uncertainty, and materiality definition;
- data classification;
- all three mandatory `baseline_controls`;
- `control_decisions` for each applicable stable kit control;
- namespaced application controls as `x-<application-id>-<control>`;
- human roles and release route;
- explicit exclusions and deferrals with rationale.

The baseline controls cannot be excluded:

- `agent_work_packets`;
- `actual_diff_review`;
- `secret_hygiene`.

Use `required`, `optional`, `excluded`, or `deferred` only after recording a rationale. Keep this profile as the single authority for the application's control selection.

Validate the profile with a JSON Schema Draft 2020-12 validator using `schemas/application-profile.schema.yaml`. Add a negative test proving that an unknown unnamespaced control ID and an excluded baseline control are rejected.

## Step 4: Add the schema validator

Select a standards-compliant JSON Schema Draft 2020-12 validator supported by the repository's stack. Declare and lock its dependencies in the receiving repository.

The validator must:

- validate YAML or JSON instances against the schemas;
- enable date-time format checking;
- resolve local `$defs` and `$ref` consistently;
- reject unknown fields where the schema uses `additionalProperties: false`;
- run both positive and negative conformance tests;
- execute in the repository's normal test/CI command.

Do not claim that a schema is enforced merely because the file exists. Enforcement exists only after validation is invoked at an application boundary or CI gate and its tests pass.

At minimum, add tests for:

- valid and invalid application profiles;
- method assurance with failed or irrelevant evidence;
- conditional evidence without limitations;
- independent validation without an independence basis;
- completed runs missing hashes or timestamps;
- completed AI runs with missing provider/model/prompt identity;
- failed/blocked/cancelled runs with no outputs;
- high/material overrides without approval requirement;
- approved overrides without approval evidence, approver, or timestamp;
- pending and rejected approval-required overrides;
- invalid dates and unknown fields.

## Step 5: Create the method registry

Copy `schemas/method-registry-entry.schema.yaml` into the repository's contract location and create one registry entry for every governed method, model, rule, transformation, AI reasoning component, or external analytical service.

For each entry record:

- stable method ID and version;
- method kind;
- name and intended use;
- owner;
- lifecycle status;
- validation status;
- approval status;
- input and output contract references;
- implementation revision;
- data/configuration dependencies;
- assumptions and limitations;
- revalidation trigger;
- typed assurance evidence and findings.

Keep these meanings separate:

- `lifecycle_status: active` means catalogued/current, not executable;
- `validation_status` describes validation evidence;
- `approval_status` describes human authorization;
- run status describes one execution.

Unqualified `passed` and `approved` require unconditional evidence. Use `passed_with_conditions` or `approved_with_conditions` when limitations or conditions remain. The receiving dispatcher must refuse execution when validation has failed/expired, approval is rejected/withdrawn, required evidence is absent, or a condition/limitation is not satisfied.

## Step 6: Define contracts and lineage

Use explicit input/output contracts for each method. For every material or completed run, record a Method Run lineage instance using `schemas/method-run-lineage.schema.yaml`.

At minimum, connect:

- application ID;
- run ID;
- method ID and version;
- method kind;
- input references and input hash;
- implementation revision;
- configuration version and hash;
- start and completion timestamps;
- run status;
- materiality;
- output references and output hash when output exists.

For completed AI runs also record non-empty:

- AI provider;
- model identifier;
- prompt/template version.

Failed, blocked, cancelled, queued, and running records may have no output references when no output was produced. Do not invent placeholder outputs or hashes.

If the application has scenario packages, batches, notebooks, portfolios, or another domain-specific input concept, add an application-owned extension schema. Do not modify the universal contract to privilege one product concept, and do not allow an extension to weaken base provenance requirements.

Define hash semantics in the receiving repository. For multiple inputs or outputs, hash a canonical manifest or canonical serialized collection and record that convention.

## Step 7: Implement execution eligibility

Create one application-owned eligibility function or policy decision at the method dispatch boundary. It must evaluate, at minimum:

- method lifecycle;
- validation status and evidence;
- approval status and evidence;
- materiality;
- findings and limitations;
- revalidation/expiry triggers;
- required human decisions;
- application-specific conditions.

The rule must make clear that `active` alone never authorizes execution. Test the negative cases first: failed validation, rejected approval, expired evidence, unmet conditions, and missing provenance must not execute.

## Step 8: Implement overrides and human judgement

Use `schemas/override-record.schema.yaml` for every deliberate deviation from the default automated path.

Record:

- classification;
- affected method/run/scope;
- before and after values;
- rationale and generic evidence reference;
- calculation/output impact;
- materiality;
- approval requirement and status;
- owner;
- approver where approval is asserted;
- approval evidence reference and timestamp for approved overrides;
- review/expiry trigger;
- closure condition;
- rollback approach.

High/material or calculation/output-impacting overrides must route through approval. Pending and rejected states may be recorded but must not become effective. Approved records must point to an approval-specific evidence record. The application must evaluate expiry and review triggers before applying an override and on each relevant run.

## Step 9: Install the AI operating model

Copy or adapt `core/AI_OPERATING_MODEL.md`, `core/CONTROL_PRINCIPLES.md`, and `core/REVIEW_AND_EVIDENCE.md` into the repository's developer/governance documentation.

Make the work-packet template mandatory for coding-agent tasks. Every task must identify:

- objective and non-goals;
- bounded ownership;
- constraints and data/security handling;
- acceptance criteria;
- expected tests/checks;
- accountable task owner;
- reviewer and escalation triggers.

For material or audit-triggered work, require the actual diff or patch content. A changed-file list is not sufficient. The agent completion record must include commands, results, failures/warnings, runtime evidence where relevant, assumptions, evidence gaps, and unresolved human decisions.

Agents may implement and report evidence. They may not approve methodology, accept risk, conclude independent validation, authorize release, or claim external platform controls.

## Step 10: Add security and confidentiality controls

Adopt `core/SECURITY_BASELINE.md` and bind each requirement to the receiving repository's approved tools.

At minimum implement:

- secret scanning before commit and archive sharing;
- no customer/client data or credentials in fixtures/examples/logs;
- AI input/output classification and provider handling rules;
- prompt/output/log redaction and retention rules;
- declared and locked dependencies;
- approved dependency/vulnerability checks;
- archive path, content, and digest verification.

Record security exceptions as human decisions. Do not introduce a central security platform merely to consume this kit.

## Step 11: Wire repository quality gates

Add the receiving repository's native commands to its normal local and CI checks. The minimum gate should cover:

1. schema validation and semantic conformance tests;
2. unit and integration tests for the method/run/override seams;
3. deterministic replay or golden/reference tests for material outputs;
4. lint, format, type, and build checks appropriate to the stack;
5. secret scanning;
6. dependency lock and vulnerability checks;
7. documentation/decision-record checks for material changes.

Record exact commands and results. A passing wrapper with hidden test failures is not a pass.

## Step 12: Review, audit, and release

Before the first governed release:

1. review the actual diff and all new control wiring;
2. inspect the method registry and application profile;
3. run the complete quality/security gate;
4. perform output, replay, sensitivity, or benchmark checks appropriate to materiality;
5. obtain required technical, method-owner, independent-validator, and release decisions;
6. attach the evidence bundle to the decision/change record;
7. have ChatGPT Enterprise audit the complete kit plus the receiving repository's actual diff where the audit trigger applies;
8. record findings, limitations, accepted conditions, and unresolved questions;
9. obtain human release authorization through the receiving repository's process.

Do not call the application approved, independently validated, risk-accepted, or production-ready because the kit's own tests pass.

## Definition of done for adoption

Adoption is complete only when all of these are true:

- a pinned kit version and trusted digest are recorded;
- the application profile is complete and validated;
- mandatory baseline controls are active;
- selectable controls have decisions and rationales;
- schemas are validated by a declared receiving-repository validator;
- positive and negative conformance tests pass in the receiving repository;
- method registry entries exist for governed analytical components;
- execution eligibility is implemented and tested;
- run lineage is persisted for material/completed runs;
- override approval and expiry behavior is implemented and tested;
- AI confidentiality and dependency controls are wired to native tooling;
- agent work packets and actual-diff review are in the developer workflow;
- CI/local quality gates run and their results are recorded;
- human review, approval, independent validation, risk acceptance, and release decisions are recorded where required.

If any item is not complete, mark the adoption as `in_progress`, `blocked`, or `deferred` with an owner and rationale. Do not represent partial adoption as full control implementation.
