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
principle 11 places outside what a tool may claim.

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
| `overrides` | `SP055`/`SP056` — `implementation_reference` names a register directory; every record in it must validate against `override-record.schema.yaml`. `SP057` — each override's `method_run_id` resolves to a run |
| `method_registry` | `SP055`/`SP056`, against `method-registry-entry.schema.yaml` |
| `run_lineage` | `SP055`/`SP056`, against `method-run-lineage.schema.yaml`. `SP057` — each run's `method_id` **and `method_version`** resolve to a registry entry |
| `provenance` | `SP055`/`SP056`, against the same record type as `run_lineage`. `SP057` — every id in a run's `overrides` resolves to an override record |
| all four | `SP058` — no two records in one register claim one identity, and no record carries another application's `application_id` |

**Ten of the twelve controls this framework defines are checked**, at every level. The two that are
not are `agent_work_packets` and `actual_diff_review`, named above and unchanged: neither leaves an
artefact this framework can inspect without inspecting the quality of human work, which
`core/CONTROL_PRINCIPLES.md` principle 11 places outside what a tool may claim.

*This paragraph read "Every control this framework defines is now checked, at every level. Nothing is
declared-only" until `F52`. That directly contradicted the statement thirty-eight lines above it, in
this same document, and a cross-provider reviewer found it. A governance standard cannot claim both
absolute enforcement and honour-system enforcement for its own baseline controls; the one above is
the true one.*

**The pre-commit hook is one enforcement route of three, not a requirement.** A gate declares
`enforcement`, and `history_audit`, `review` and `local_hook` are all valid answers. A repository
with its own hook system may install with `--no-hooks`, keep it, and rely on the history audit —
which catches a violation after the commit rather than before it. The declination is recorded at
install and reported on every run, so a passing check never reads as "staged changes are gated" when
they are not. Claiming `local_hook` without the standard's hook actually being what Git runs is a
finding (`SP038`). See `F27` and `F28`.

**An exemption may quote what it describes.** A `placeholder_scan_exemptions` entry must say why an
artefact legitimately contains a placeholder token, and saying so usually means quoting it. That one
field — the exemption's `rationale` — is excluded from the profile's own placeholder scan for that
reason. Nothing else is: the artefact path beside it, and every other rationale in the profile, are
still scanned. Before this, declaring the exemption failed the profile, so the remedy could not be
used without causing the defect it fixes. See `F25`.

**How `provenance` and `run_lineage` differ.** They share a record type — provenance is its
traceability, run lineage its reproducibility — so they are separated by **which reference each
obliges**, not by which fields. `run_lineage` requires a run to resolve to the method that ran it;
`provenance` requires it to resolve to every override that adjusted the result. Separating them by
field content was tried and abandoned: `method-run-lineage.schema.yaml` already requires every hash
and revision on a completed run, so both controls would have obliged nothing.

**A cross-reference is only checked when the register it points into is declared here.** Obliging
otherwise would make declaring one control silently require another, which is this framework
deciding your scope. At `full` all four are required, so every reference is checked. Below that, a
control whose target register is undeclared adds nothing beyond `SP055`/`SP056` — and the check
**says so on the run** rather than letting a green line imply the references were examined. The same
applies when a register holds a record that failed its schema: its index is incomplete, so
references into it are reported as unchecked rather than as unresolved.

**A deferral now expires.** `SP031` has always required a deferred control or gate to carry a
`revisit_by` date; `SP054` reads it. A date that has passed is a finding, a date within 30 days is
an advisory, and a malformed date fails — a deadline nobody can parse is not a deadline, and the
deferral would be permanent by accident. Gate exceptions are **not** covered: their schema carries
only an optional creation date, so there is nothing declared to expire against, and inventing a
lifetime would be this framework deciding on an adopter's behalf. See `F22`.

**`full` is now fully checked too.** `provenance`, `run_lineage`, `method_registry` and `overrides`
each name a **directory** in `implementation_reference`. `SP055` requires that directory to exist,
to be a directory rather than a file, and to hold no untracked records; `SP056` requires every
`.yaml` file in it to validate against the schema this framework ships for that record type —
`override-record`, `method-registry-entry`, or `method-run-lineage` for both `run_lineage` and
`provenance`, which are two properties of one record. Non-YAML files are ignored, so a register may
carry a `README.md`.

**An empty register passes, and that is a decision rather than a gap.** A check that demanded
records would be a check that rewarded inventing them. So what a pass establishes here is that **no
unvalidated record exists in that register** — never that records exist. If you have made no
overrides, an empty overrides register is the correct and honest state, and it will stay correct
until you make one.

There is no live self-demonstration for this pattern. Surfaceplate sits at `standard`, has no
material results, no governed methods and no overrides, so it declares none of these four. It is
the first control in this framework proven only by fixture, and `DR-26` records that.

**What being checked does and does not mean.** For `dependency_lock` it means a lock file is really
there, tracked, and not a blank template. It does **not** mean the versions in it are the ones you
install, or that they are good ones.

For `deterministic_tests` and `contract_tests` it means a named CI step exists and its failure is
binding. It does **not** mean the tests are deterministic, that they are contract tests, or that
they assert anything at all — **a step running `true` would pass.** What it does catch is the
failure this framework has already seen: a suite that runs, reports success and leaves the job green
because its exit code was discarded.

For the four record-based controls it means every record filed is well-formed and complete against
its schema, and that the records it names exist. It does **not** mean the record it names is the
**right** one — a run may resolve to a registered method and still be a record of something else
entirely. Nor does it mean any record is **true**: a run-lineage record can carry an input
hash computed over nothing at all, and it will validate. Nor does it mean the register is complete —
nothing can tell you that a run happened and went unrecorded.

The checker reads a file's presence and shape, a step's wiring, and a record's structure. Never
truthfulness, and never completeness.

This was recorded as finding `F20` and is now closed. `DR-25` set out four patterns by which a
control becomes provable, with `implementation_reference` naming where the control lives; `DR-26`
completes the last of them. Every control that leaves an inspectable artefact is checked — ten of
the twelve, as stated above — so the list above is no longer partial.

**A limit that remains now they are all built, stated more narrowly than it once was.**
Verification establishes that a record exists, is well-formed, and is linked to what it describes.
It never establishes that the record is **true**. Nothing here checks that a run happened the way
its lineage record says it did.

It does **not** establish that a record is *current* either, and that sentence used to appear here
saying otherwise. None of the three record schemas carries an expiry or a review date —
`method-registry-entry` has `revalidation_trigger`, but that is a free-text condition, not a
deadline. There is nothing declared to check currency against, which is the same shape as the gate
exceptions `F22` left open. `DR-25` is amended accordingly rather than corrected by a note.

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

## Every finding code the checker can report

<!-- BEGIN GENERATED: finding codes (tests/check_code_registers.py --write) -->

56 codes. Generated from the checker's own source by `tests/check_code_registers.py --write`;
the same script fails in CI when this table and the checker disagree. A code's title is what
the report prints; `<gate>`, `<control>`, `<file>` stand for the name the report fills in.

| Code | What it reports |
|---|---|
| `SP001` | Surfaceplate is not installed |
| `SP002` | The install record is unreadable |
| `SP003` | The install record is incomplete |
| `SP004` | Standard-owned files have been deleted |
| `SP005` | Standard-owned files have been modified locally; Standard-owned hook files are not executable |
| `SP006` | No agent instruction file at <file> |
| `SP007` | The conformance block is absent from <file> |
| `SP008` | The conformance block in <file> has been altered |
| `SP009` | The conformance workflow is not present |
| `SP010` | No application profile |
| `SP011` | The application profile could not be read |
| `SP012` | The application profile is not a mapping |
| `SP013` | The application profile schema is not vendored |
| `SP014` | The schema could not be read |
| `SP015` | Schema validation could not be performed |
| `SP016` | The application profile does not satisfy the control contract; Further schema errors were suppressed |
| `SP017` | The declared conformance level is not recognised |
| `SP018` | The profile records no adoption metadata |
| `SP019` | An incomplete adoption carries no rationale |
| `SP020` | The application profile still contains template placeholders |
| `SP021` | Conformance level '<level>' is overclaimed |
| `SP022` | Conformance level '<level>' is overclaimed |
| `SP023` | Controls were deferred without an owner or a revisit date |
| `SP024` | The profile records no review date; The profile review date is unreadable |
| `SP025` | The application profile is overdue for review |
| `SP026` | The profile review date is beyond the permitted horizon |
| `SP027` | The profile declares no prerequisite gates |
| `SP028` | The prerequisites block is malformed; A prerequisite gate is malformed; A prerequisite gate has no identifier; Prerequisite gate '<gate>' is declared more than once; Prerequisite gate '<gate>' is not in the catalogue; Prerequisite gate '<gate>' has no usable status |
| `SP029` | Conformance level '<level>' requires gate '<gate>'; Conformance level '<level>' leaves catalogue gates undecided |
| `SP030` | Conformance level '<level>' requires gate '<gate>' to be required |
| `SP031` | Gate '<gate>' is <status> without a reason; Gate '<gate>' is deferred without an owner or a revisit date |
| `SP032` | Gate '<gate>' requires an artefact that does not exist; Gate '<gate>' names an empty precondition artefact; Gate '<gate>' names an unfinished precondition artefact |
| `SP033` | Gate '<gate>' records no effective date; Gate '<gate>' has an unreadable effective date; Gate '<gate>' is dated in the future |
| `SP034` | Gate '<gate>' has had its effective date moved forward |
| `SP035` | Gate '<gate>' was crossed without its precondition |
| `SP037` | The profile does not say whether this repository builds a user interface; 'builds_user_interface' is not a yes or no; Gate '<gate>' is not_applicable in a repository that builds a UI; Gate '<gate>' is {gate.get('status')} in a repository with no UI |
| `SP038` | Gate '<gate>' claims hook enforcement that is not in place |
| `SP039` | Staged change crosses gate '<gate>' without its precondition |
| `SP040` | The staged snapshot has no install record; The staged install record is unreadable; The staged install record differs from the checked-out installer output; Standard-owned files are invalid in the staged snapshot; Standard-owned hooks are not executable in the staged snapshot; The staged snapshot has no Copilot instructions; The conformance block is absent from the staged snapshot; The conformance block is altered in the staged snapshot |
| `SP041` | The staged application profile cannot be evaluated |
| `SP042` | Gate '<gate>' has an invalid Git pathspec |
| `SP043` | Gate exception '<file>' is invalid; Gate exception '<file>' names an unresolved commit; Gate exceptions could not be validated; Gate exception '{path.relative_to(repo).as_posix()}' is unreadable; Staged gate exceptions could not be validated; Staged gate exception '<file>' is unreadable |
| `SP046` | secret_hygiene is declared but no scanner is named; Scanner '<scanner>' is named but not wired anywhere; Scanner '<scanner>' is wired to a file that does not exist; <file> does not mention '<scanner>'; <file> names '<scanner>' but no step runs it |
| `SP047` | The scan step in <file> cannot fail the job; The scan command in <file> discards its exit code |
| `SP048` | The profile declares a different version from the one installed |
| `SP049` | The profile declares a framework digest that cannot be verified; The installed manifest does not hash to the digest recorded for it; The profile's framework digest does not match what is installed |
| `SP050` | A placeholder-scan exemption names an artefact that does not exist |
| `SP051` | Control '<control>' is required but names nothing to check; Control '<control>' names a file that does not exist; Control '<control>' names an empty file; Control '<control>' names an unfinished file; Control '<control>' names an untracked file |
| `SP052` | documentation_authority is required without the gate that verifies it |
| `SP053` | Control '<control>' is required but names no CI step; Control '<control>' names a CI step that does not exist; Control '<control>' names a CI step that runs nothing; Control '<control>' names a step that cannot fail the build; Control '<control>' names a step that discards its exit code |
| `SP054` | <record> has an unreadable revisit date; <record> passed its revisit date |
| `SP055` | Control '<control>' is required but names no register; Control '<control>' names a file where a register belongs; Control '<control>' names a register that does not exist; Control '<control>' names a register holding untracked records |
| `SP056` | Control '<control>' could not be checked; Record '<file>' is unreadable; Record '<file>' is invalid for control '<control>' |
| `SP057` | Record '<file>' references something that does not exist |
| `SP058` | Two records in the '<control>' register claim one identity; Record '<file>' belongs to a different application |
| `SP059` | Control '<control>' names a step of the workflow this framework installed; Gate '<gate>' names a file this framework installed as its precondition |

<!-- END GENERATED: finding codes -->
