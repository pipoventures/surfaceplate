# Engineering Control Kit — Technical Pre-Audit Findings

> **Historical record, with inherited names redacted.** This document records checks that were
> actually run, against a repository that had a different name. The internal product and
> methodology names it originally carried have been **replaced with generic descriptions** — they
> named someone else's product and meant nothing here. The redaction is disclosed rather than
> silent: the substance of every check and finding is unchanged, only the proper nouns are. See
> `F18`.

**Package:** `engineering-control-kit` v0.6.0
**ZIP SHA-256:** `1F895DD8F2646FABB878DA01C83BD5AAABF1D0C2881661D00B1F06D9F5DAEC76`
**Date:** 2026-08-27
**Performed by:** GitHub Copilot CLI, at the request of Mario Pipo (maintainer)
**Intended use:** Input to the adoption decision and to the formal audit.

## Status of this record

`FACT FROM PACKAGE` labels below follow `core/REVIEW_AND_EVIDENCE.md`.

**This is not the independent audit the kit requires.** `audit/AUDIT_README.md` requires the
complete ZIP and `audit/CHATGPT_ENTERPRISE_AUDIT_PROMPT.md` to be reviewed by a designated
reviewer. `core/AI_OPERATING_MODEL.md` reserves independent validation conclusions to humans.
This record therefore asserts **no** approval, independent validation, risk acceptance, or
release readiness. It is a technical pre-audit intended to reduce the cost of the formal audit.

## Package checks performed

| Check | Command / method | Result |
|---|---|---|
| Manifest integrity | SHA-256 of all 27 payload entries vs `MANIFEST.sha256` | **PASS** — 27/27 match |
| Unlisted files | payload tree vs manifest entries | **PASS** — none |
| Secret / private key scan | regex for private keys, AWS keys, GitHub PATs, Slack tokens | **PASS** — no matches |
| Schema meta-validity | `Draft202012Validator.check_schema` on all 5 schemas | **PASS** — 5/5 valid |
| Kit conformance tests | `python tests/validate_contracts.py` | **PASS** (`CONTRACT_CONFORMANCE=PASS`, exit 0) |
| Independent negative cases | 7 hand-built cases vs application-profile schema | **PASS** — 7/7 behaved correctly |
| Tool-agnosticism | grep for predecessor-application, methodology and framework leakage | **PASS** — all hits are "do not copy" guidance or audit scope |

Environment: Python 3.14.3, jsonschema 4.26.0, PyYAML, referencing. Windows 11.

### Negative cases verified independently

All correctly rejected: baseline control set to `excluded`; baseline control omitted; unknown
un-namespaced control ID; control decision without rationale; invalid data classification;
unknown top-level field. Correctly accepted: valid filled profile; correctly namespaced
`x-<app-id>-<control>` extension.

`FACT FROM PACKAGE` — the three baseline controls genuinely cannot be excluded or omitted.
This is real enforcement, not documentation.

## Findings

### F1 — HIGH — Application profile cannot record adoption identity

`SETUP_GUIDE.md` Step 1 mandates recording kit version, kit digest, adoption date, application
owner, kit maintainer, repository classification, and initial decision record ID. The Definition
of Done mandates an adoption status of `in_progress` / `blocked` / `deferred`. Step 3 mandates
deferrals with rationale.

`FACT FROM PACKAGE` — **none of these fields exist** in `schemas/application-profile.schema.yaml`.
Its properties are limited to: `application_id`, `baseline_controls`, `control_decisions`,
`data_classification`, `display_name`, `exclusions`, `human_roles`, `materiality_definition`,
`owner`, `release_route`, `risk_profile`, `schema_version`, `stack`.

Because the schema sets `additionalProperties: false`, an adopting team **cannot add them**
without forking the schema. Verified: adding `kit_version` to a valid profile is rejected with
"Additional properties are not allowed ('kit_version' was unexpected)".

**Consequence.** The mandated adoption facts survive only in a free-text decision record. Across
a business unit you cannot mechanically answer *"which applications are on which kit version, and
which adoptions are incomplete?"* — the core fleet-governance question. Tolerable for one repo;
blocking for a business-unit rollout.

### F2 — MEDIUM — Producer validation record is stale

`audit/VALIDATION_RESULTS.md` declares `Current draft: 0.5.0`, `Package files including manifest: 26`,
`Manifest payload entries: 25`.

`FACT FROM PACKAGE` — the shipped package is **0.6.0** with **28** files and **27** payload entries.
`prompts/github-copilot-adoption-wizard.prompt.md`, added in 0.6.0 and the largest single file in
the kit at 13.2 KB, is covered by **no** recorded producer check.

In a kit whose central claim is evidence-first completion, the evidence record does not describe
the artefact it ships with. The remedy is trivial, but it should not reach a business unit as-is.

### F3 — MEDIUM — Schema `$id`s use `https://example.invalid/`

`FACT FROM PACKAGE` — all five schemas declare `$id: https://example.invalid/engineering-control-kit/<name>`.

Harmless for a single vendored copy with local `$defs` resolution. At business-unit scale — multiple
repos, cross-repo `$ref`, any future schema registry or contract-diffing tooling — `example.invalid`
is not a governable identity namespace, and the identifier carries no version, so two different kit
versions produce colliding schema identities. Needs a decision on an organisation-controlled `$id` base with
the version in the path.

### F4 — LOW — Shipped templates do not validate against their own schemas

`FACT FROM PACKAGE`:
- `templates/application-profile.yaml` — fails: `control_decisions` key `replace-me` violates the
  `propertyNames` pattern. The placeholder is a **key**, not a value, so "replace every replace-me
  value" (Step 3) does not obviously cover it.
- `templates/override-record.yaml` — fails: `created_at: replace-me` is not a `date-time`.

Defensible for fill-in templates, but the kit ships **no valid example instance**, so an adopting
team cannot distinguish "I broke it" from "it ships that way". `RECOMMENDATION`: add golden valid
examples beside the templates and assert them in `tests/validate_contracts.py`.

## Assessment against `audit/AUDIT_SCOPE.md`

| Criterion | Assessment |
|---|---|
| Genuinely tool-agnostic | **Holds** — no stack imposed; adapters are advisory |
| Internally consistent | **Gap** — F1 (guide demands fields the schema forbids), F2 (stale record) |
| Proportionate for small MVPs | **Holds in principle** — proportionality is explicit; but no graded conformance level, so BU teams will read it as all-or-nothing |
| Clear on human vs agent authority | **Strong** — the clearest part of the kit |
| Sufficient for provenance/methods/runs/overrides | **Holds** at schema level; enforcement is the adopter's job and the kit says so |
| Safe to share internally | **Holds** — no secrets, no client data |
| Free of hidden predecessor-application or methodology assumptions | **Holds** |
| Explicit about policy vs schema vs enforcement | **Strong** — repeatedly warns that a schema file is not enforcement |
| Usable by many apps without a premature central platform | **Gap** — F1 and F3 are exactly the fleet-scale seams |

## Recommended remediation before business-unit rollout

Proposed as **v0.7.0**. All are changes to the kit and require the kit maintainer's authorisation;
F1 and F3 are material schema changes.

1. **F1** — add an `adoption` object to the application profile: `kit_version`, `kit_digest`,
   `adoption_date`, `kit_maintainer`, `repository_classification`, `decision_record_id`,
   `adoption_status`, and a `deferrals` array. Add positive and negative tests.
2. **F3** — replace the `example.invalid` `$id` base with an organisation-controlled, versioned namespace.
3. **F2** — regenerate `VALIDATION_RESULTS.md` against the actual shipped package.
4. **F4** — add golden valid example instances and assert them in the conformance tests.
5. Consider a graded conformance level (e.g. Essential / Standard / Full) so a small MVP can adopt
   proportionately — the kit's own Principle 12.

## Open human decisions

- Does this pre-audit plus remediation satisfy the audit gate, or is the ChatGPT Enterprise
  independent audit still required before rollout? (Kit says required; only the human may waive.)
- The `$id` namespace value.
- Whether the kit maintainer role can rest on one named individual at business-unit scale.
- Route for an adopter that already operates a competing mandatory activity-register gate.
