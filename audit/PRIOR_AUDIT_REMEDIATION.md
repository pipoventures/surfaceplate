# Prior Audit Remediation

> **Historical record, with inherited names redacted.** This document records checks that were
> actually run, against a repository that had a different name. The internal product and
> methodology names it originally carried have been **replaced with generic descriptions** — they
> named someone else's product and meant nothing here. The redaction is disclosed rather than
> silent: the substance of every check and finding is unchanged, only the proper nouns are. See
> `F18`.

Source: independent ChatGPT Enterprise audit supplied to the predecessor repository on 2026-08-21.

| Finding | Disposition in 0.2.0 |
|---|---|
| C1 ZIP path portability | Remediated in packaging: archive entries are created with POSIX `/` separators; exact central-directory names are checked before handoff. |
| C2 custom schema dialect | Remediated: contracts use JSON Schema Draft 2020-12 expressed as YAML; `tests/validate_contracts.py` provides positive/negative reference conformance tests. |
| C3 unsupported approval/validation claims | Remediated in schema: lifecycle no longer contains `approved`; final validation/approval states require typed `assurance_evidence`. Human approval remains external to the package. |
| C4 incomplete completed/AI provenance | Remediated in schema: completed/material runs require input, configuration, implementation, completion, and output identity; AI methods require provider/model/prompt fields. |
| M1 override contract | Remediated: added `schemas/override-record.schema.yaml` with controlled values and conditional approval rules; receiving applications must enforce expiry semantics and add tests. |
| M2 tool neutrality leakage | Remediated: stack topology is optional; Scenario Package fields are optional extension fields; product-specific examples are not universal defaults. |
| M3 all-controls default | Remediated: application template starts with no required controls and requires explicit control decisions and rationale. |
| M4 actual diff ambiguity | Remediated: material/audit-triggered work requires actual diff or patch content; file lists remain low-risk routing evidence only. |
| M5 material output routing | Remediated: material numerical/model and material AI outputs are explicitly Level 3 examples. |
| M6 confidentiality/supply chain | Partially remediated: audit prompt and handoff specify receiving-repository AI confidentiality, secret, and dependency controls; native enforcement remains application-owned. |
| M7 kit change control | Partially remediated: added version `0.2.0`, owner assignment requirement, changelog, and re-audit status. Formal release ownership remains a human adoption decision. |
| O1 evidence vocabulary | Remediated: package uses `FACT FROM PACKAGE` and `FACT FROM RECEIVING REPOSITORY`. |
| O2 repeated override vocabulary | Remediated: allowed classifications are only in the schema, not in each record template. |
| O3 work-packet owner | Remediated: added accountable task owner. |
| O4 approval template weakness | Clarified: assurance evidence is a typed schema; the decision template remains a prompt and not proof of approval by itself. |

This document records package changes only. It does not claim that any receiving application has implemented or approved the controls.

## Latest audit remediation

- Conditional assurance outcomes now require non-empty limitation/condition details.
- Approved overrides now require an approval-specific evidence reference and approval timestamp.
- Application profiles now separate three mandatory baseline controls from stable selectable control IDs and namespaced extensions.
- Lifecycle `active` is explicitly catalogue state and never execution authority; receiving applications must enforce eligibility.
- The historical changelog was corrected and a canonical kit maintainer/change authority is required before broad sharing.
- Conditional assurance now uses explicit `passed_with_conditions` and `approved_with_conditions` statuses; unqualified final states require unconditional evidence.

## Second audit remediation

The supplied second audit identified three blocking schema defects and five material issues. This revision addresses them as follows:

- Final validation and approval states now require qualifying evidence type and acceptable outcome; independent validation requires an independence basis.
- Completed timestamps and AI provider/model/prompt fields are non-null when required; terminal failed/blocked/cancelled records may omit outputs.
- Override approval requirement, approval status, and approval evidence are separate; high/material-impacting overrides require approval, pending/rejected states remain representable, and asserted approval requires an approver.
- Application control decisions are a single keyed object rather than duplicated required/optional arrays.
- The universal run schema has no predecessor-application-specific fields; application-owned extensions are required for domain-specific lineage.
- The reference tests now enable date-time format checking and cover the adversarial cases identified by the second audit.
- A normative AI confidentiality and dependency baseline and a producer validation-results record were added.

The package remains pending re-audit. No broad adoption or human approval is claimed.
