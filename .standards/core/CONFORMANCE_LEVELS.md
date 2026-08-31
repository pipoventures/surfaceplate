# Conformance Levels

## Why levels exist

`core/CONTROL_PRINCIPLES.md` principle 12 requires proportionality: *defer controls that do not
reduce a demonstrated risk*. `core/AI_OPERATING_MODEL.md` requires the smallest control set that
protects the risk.

Without graded levels, a two-person proof of concept and a client-reported quantitative model face
the same control surface. In practice that produces one of two failures: small teams reject the
framework as disproportionate, or they claim adoption while implementing very little of it. Both
are worse than an honest tier.

A level is a **floor, not a ceiling**. Any application may require controls above its level.

## The three baseline controls

`agent_work_packets`, `actual_diff_review`, and `secret_hygiene` are required at **every** level,
including `essential`. They cannot be excluded, deferred, or omitted, and the application-profile
schema rejects any attempt to do so.

**Only one of the three is verified, and it is worth being exact about what that means.**
`secret_hygiene` must name a scanner and where it is wired; `SP046` and `SP047` check that the
wiring exists, that a step actually invokes the scanner, and that the step's exit code can fail the
job (`DR-18`). A pass says a scanner is wired somewhere that can fail. **It does not say the
repository contains no secrets** — this standard ships no scanner and inspects no file contents for
credentials.

`agent_work_packets` and `actual_diff_review` remain declarations that nothing checks. That is not
an oversight to be read past: a repository can declare both, do neither, and pass. They are stated
obligations, and the reason they are unverified is that neither leaves an artefact this framework
can inspect without inspecting the quality of human work, which `core/CONTROL_PRINCIPLES.md`
principle 9 places outside what a tool may claim.

## What a control decision is, and what it is not

**Read this before the tables below, because they will otherwise imply more than they mean.**

A **control decision** is a *declaration*. The checker verifies that a control the level requires is
listed and reads `required` (`SP021`, `SP022`). It does **not** verify that the thing exists. A
repository can declare every control its level demands, possess none of them, and pass.

A **prerequisite gate** is different in kind. The checker looks at reality: whether the named
artefact exists, whether it is blank, whether it is still an unfilled template, and — through the
history audit — whether anyone changed the gated paths while it was missing.

| | Checked against |
|---|---|
| Prerequisite gate | The repository |
| Control decision | Itself |

**Currently checked:**

| Control | How |
|---|---|
| `dependency_lock` | `SP051` — `implementation_reference` names a file; the checker confirms it exists, is not empty, is not a template, and is tracked by git |
| `assurance_findings` | `SP051`, same way |
| `documentation_authority` | The `authority_map` gate checks the artefact. `SP052` additionally requires that gate whenever the control is required, closing the seam a level being a floor rather than a ceiling would otherwise open |
| `deterministic_tests` | `SP053` — `implementation_reference` names a CI step; the checker confirms it exists, runs something, and **can fail** |
| `contract_tests` | `SP053`, same way |

**`standard` is now fully checked**: every control it requires is verified rather than declared.

**A deferral now expires.** `SP031` has always required a deferred control or gate to carry a
`revisit_by` date; `SP054` reads it. A date that has passed is a finding, a date within 30 days is
an advisory, and a malformed date fails — a deadline nobody can parse is not a deadline, and the
deferral would be permanent by accident. Gate exceptions are **not** covered: their schema carries
only an optional creation date, so there is nothing declared to expire against, and inventing a
lifetime would be this framework deciding on an adopter's behalf. See `F22`.

**Currently declared only:** `provenance`, `run_lineage`, `method_registry`, `overrides` — the four
record-based controls at `full`.

**What being checked does and does not mean.** For `dependency_lock` it means a lock file is really
there, tracked, and not a blank template. It does **not** mean the versions in it are the ones you
install, or that they are good ones.

For `deterministic_tests` and `contract_tests` it means a named CI step exists and its failure is
binding. It does **not** mean the tests are deterministic, that they are contract tests, or that
they assert anything at all — **a step running `true` would pass.** What it does catch is the
failure this framework has already seen: a suite that runs, reports success and leaves the job green
because its exit code was discarded.

The checker reads a file's presence and shape, and a step's wiring. Never truthfulness.

This is recorded as finding `F20`, and `DR-25` decides the architecture that changes it: four
patterns by which a control becomes provable, with `implementation_reference` naming where the
control lives. Until a control appears in the *checked* list above, treat its presence in a level as
an obligation the repository has accepted — not as something this framework has confirmed.

**A limit that will remain after all of it is built.** Verification establishes that a record
exists, is well-formed, is current, and is linked to what it describes. It never establishes that
the record is **true**. Nothing here will check that a run happened the way its lineage record says
it did.

## Levels

### `essential`

Intended for proofs of concept, demonstrators, internal tooling, and any application whose outputs
are not relied upon outside the delivery team.

Additionally required:

| Control | Reason |
|---|---|
| `dependency_lock` | Supply-chain exposure exists regardless of output materiality. |

### `standard`

Intended for applications with real users, or whose outputs inform work but are not the final basis
for a client-facing quantitative or regulatory conclusion.

Requires everything in `essential`, plus:

| Control | Reason |
|---|---|
| `deterministic_tests` | Behaviour must be reproducible before it can be reviewed. |
| `contract_tests` | Interfaces have consumers who will break silently otherwise. |
| `documentation_authority` | Contradictory authority is the most common governance defect observed. |

### `full`

Intended for applications producing material quantitative outputs, material AI outputs or
reasoning, or outputs relied upon by a client, a regulator, or an external party.

Requires everything in `standard`, plus:

| Control | Reason |
|---|---|
| `provenance` | A material result must be traceable to its inputs. |
| `run_lineage` | A material result must be reproducible from a recorded execution. |
| `method_registry` | Governed methods need identity, lifecycle, validation, and approval state. |
| `overrides` | Manual adjustment must never be hidden in UI or calculation code. |
| `assurance_findings` | Limitations must be recorded rather than smoothed away. |

## Enforcement

`conformance_level` is a required field in the application profile. The schema constrains it to the
three values above but **cannot** by itself check that the corresponding controls are decided
`required` — that is a cross-field semantic rule.

The semantic rule lives in `tests/validate_contracts.py`, which fails when a profile declares
a level whose required controls are absent, or decided anything other than `required`.

This is a deliberate, stated split. Consistent with the rest of this framework: **a schema file is
not enforcement**. Enforcement exists only where validation is invoked and its tests run.

## Choosing a level

The level is a human decision recorded in the adoption decision record. It is not derived
automatically from the stack, the repository size, or the data classification, because materiality
depends on intended use and reliance, which only the application owner can judge.

Raising a level is a normal versioned change. Lowering a level is a material control decision and
requires the rationale to be recorded, because it reduces assurance over outputs that may already
be relied upon.
