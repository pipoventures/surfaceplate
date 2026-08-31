# Contract Schema Standard

The files in this directory use **JSON Schema Draft 2020-12**, expressed as YAML. `$schema` identifies the standard and `$id` identifies the contract. The method registry embeds its assurance-evidence definition under a local `$defs` URI, so a compliant validator does not need an application-specific external resource registry to resolve that contract. `assurance-evidence.schema.yaml` is the standalone reusable form of the same definition.

Receiving repositories must validate these schemas with an approved JSON Schema Draft 2020-12 validator in their native toolchain. This kit supplies the canonical contract definitions, not a universal runtime validator. A receiving application must add positive and negative conformance tests and wire validation into its own CI or application boundary before claiming automatic enforcement.

Status values are intentionally separate:

- lifecycle status describes where a method is in its product life;
- validation status describes validation evidence;
- approval status describes human authorization;
- run status describes execution state.

Unqualified `passed` and `approved` require unconditional successful evidence. Conditional evidence must use `validation_status: passed_with_conditions` or `approval_status: approved_with_conditions`, and the evidence record must contain non-empty limitations/conditions.

`lifecycle_status: active` is catalogue state only and is never execution authority. A receiving application must define execution eligibility using validation status, approval status, materiality, findings/limitations, expiry, and any required human decision. In particular, an active method with failed validation or rejected approval must not execute merely because it is catalogued.

The application profile has three mandatory baseline controls: `agent_work_packets`, `actual_diff_review`, and `secret_hygiene`. Selectable controls use stable kit IDs; application-specific controls must use an `x-<application-id>-<control>` name. Baseline controls cannot be excluded through `control_decisions`.

Override expiry and review triggers are normative control requirements but remain application-enforced. The receiving application must evaluate them before an override becomes effective and on each relevant run.

The schemas require supporting evidence when a registry record claims `validation_status: passed` or `approval_status: approved`. They require identity, role, date, scope, outcome, and reference through `assurance-evidence.schema.yaml`.

The universal run-lineage schema contains no product-specific scenario/package fields. Applications should add an application-owned extension schema for package, scenario, batch, notebook, or other domain-specific lineage fields. Extensions must be capability-neutral and must not weaken the base completion/provenance requirements.
