# ChatGPT Enterprise Audit Prompt

You are performing an independent design and reuse re-audit of the complete ZIP attached to this message: `engineering-control-kit.zip`.

## Objective

Assess whether this package is a sound, tool-agnostic foundation for AI-assisted engineering across multiple new applications, including AI Scenario Factory, without importing disproportionate PEM-specific architecture or claiming controls that are only documented.

This is an audit, not an implementation task. Do not modify the ZIP, invent missing evidence, or approve production adoption.

## Required evidence handling

1. Inspect the complete ZIP, every file, directory structure, schemas, templates, adapters, README, changelog, and audit materials.
2. Verify the SHA-256 manifest against the exact ZIP central-directory entry names. Entry names must use POSIX `/` separators and must reconstruct the documented directory tree on POSIX and Windows. Report any missing file, extra file, checksum mismatch, path ambiguity, or packaging defect.
3. Treat the package contents as the primary evidence. Do not assume a control is enforced because a policy, schema, or template mentions it.
4. Distinguish clearly between:
   - `FACT FROM PACKAGE`: directly present and internally verifiable;
   - `INFERENCE`: reasoned interpretation;
   - `RECOMMENDATION`: proposed improvement;
   - `EVIDENCE GAP`: not established by the package.
5. Do not rely on summaries from the sender. Inspect the actual files.

## Audit questions

### 1. Operating model

- Does the AI operating model define bounded work, acceptance criteria, ownership, escalation, and completion evidence?
- Are agent capabilities and human-only decisions clear and non-contradictory?
- Does it prevent fabricated approval, risk acceptance, independent validation, release readiness, or external-control claims?
- Are actual diffs, tests, runtime behavior, failures, warnings, and limitations required?
- Are the audit triggers useful and proportionate across different applications?

### 2. Tool neutrality and reuse

- Can the core rules be used for Python, TypeScript, R, or another stack without changing their meaning?
- Are stack-specific recommendations isolated in adapters?
- Are PEM/R/Shiny/PCAF/client-branch assumptions excluded from the core?
- Does the package avoid prescribing microservices, plugins, workflow engines, graph databases, or unnecessary infrastructure?
- Can several application teams use it without creating a central platform team prematurely?

### 3. Contracts and control framework

- Are application profiles, method registry entries, run lineage, assurance evidence, and overrides sufficiently specified for a B1 MVP?
- Are the schemas a defined standard such as JSON Schema Draft 2020-12, with clear `$ref` resolution and validator responsibility?
- Are lifecycle, validation, approval, execution, and retirement statuses separated, with no final assurance state possible without typed evidence?
- Are model/tool kinds complete enough for deterministic methods, quantitative models, AI reasoning, external services, rules, transformations, and human judgement?
- Are assumptions, limitations, dependencies, input/output contracts, implementation revisions, and revalidation triggers represented?
- Are provenance fields conditionally sufficient for completed/material/AI runs, including input/config/code/output identity and AI provider/model/prompt versions where relevant?

### 4. Enforcement and assurance

- Does the package distinguish documented controls from schema-represented controls, automatically enforceable controls, and human/process controls? Does it avoid claiming enforcement before a receiving application wires a validator and tests?
- Are override approval, expiry, rollback, before/after values, materiality, and evidence requirements enforceable or clearly identified as requiring application implementation?
- Are findings, limitations, independent validation, and approval records represented without false assurance?
- Does the risk-level model provide proportionate validation without silently lowering controls for material numerical or AI outputs?

### 5. Usability and maintainability

- Could a small team understand and use the package without a governance specialist?
- Are the templates concise enough for routine work?
- Are naming, status vocabularies, and schema conventions consistent?
- Are there duplicated or contradictory authorities?
- Is versioning and change control for this kit itself adequate?
- Are there missing examples or validation scripts that materially reduce usability?

### 6. Security and confidentiality

- Does the package avoid secrets, customer data, proprietary datasets, and unsafe examples?
- Are prompt, input, output, log, and fixture confidentiality risks addressed?
- Are dependency and supply-chain controls sufficiently specified for a shared kit?

## Over-engineering test

Explicitly identify anything that should be removed, deferred, or simplified for a small MVP. Do not reward comprehensiveness by itself. Evaluate whether each element reduces real implementation or control risk.

## Required output

Return an audit report with these sections:

1. **Verdict:** `PASS`, `PASS WITH REQUIRED CHANGES`, or `FAIL`.
2. **Critical findings:** ordered by severity; include exact package path and section or key where possible.
3. **Material findings:** same format.
4. **Minor findings and usability issues.**
5. **Contradictions or ambiguous authority.**
6. **Controls that are only documented versus structurally represented versus automatically enforceable versus human-process dependent.**
7. **Tool-neutrality assessment.**
8. **AI operating-model assessment.**
9. **Method/run/provenance/override/assurance assessment.**
10. **Over-engineering assessment.**
11. **Required changes before sharing broadly.**
12. **Recommended changes that may wait.**
13. **Evidence gaps and tests the receiving team should add.**
14. **File-by-file audit coverage statement.**
15. **Re-audit disposition:** identify which findings from the prior audit are closed, partially closed, or still open: C1, C2, C3, C4, M1, M2, M3, M4, M5, M6, M7, O1, O2, O3, O4.
16. **Second-audit disposition:** explicitly test the prior second-audit blockers: evidence type/outcome coupling, null AI/completion provenance, override approval lifecycle/materiality, application control-authority consistency, no-output failure states, product-neutral run lineage, format checking, and expanded negative conformance tests.

For each finding, state impact, evidence, why it matters, and a concrete remediation. Do not rewrite the package or claim that a human approval or independent validation has occurred.
