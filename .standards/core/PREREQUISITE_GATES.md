# Prerequisite Gates

## What a gate is, and why it is a different shape of control

Every other control in this framework describes what a repository **does**: it locks its
dependencies, it reviews actual diffs, it records provenance. A prerequisite gate describes
what a repository **may not do yet**.

A gate always takes the same form:

> **X must exist before Y may begin.**

That difference matters more than it first appears. A control that says "decisions must be
recorded" is satisfied by a decision record written after the fact, on the afternoon of the
audit, describing a choice that was actually made three months earlier by accident. A gate that
says "a decision record must exist *before* implementation begins" cannot be satisfied that way,
because the evidence for it is not the artefact — it is the **order of events**, and the order
of events is permanent in git history.

The catalogue below articulates roughly twenty rules of this kind and gives each one a check. It is
stated tool-neutrally so that it does not depend on any particular stack or repository layout.

## The enforcement claim, stated honestly

**A gate can be blocked locally and made impossible to hide afterwards.**

The installed pre-commit hook reads the staged snapshot and blocks a gated change when its
precondition is absent, empty or unfinished. It must be activated in each clone because
`core.hooksPath` is local Git configuration. `git commit --no-verify` defeats any client-side
hook, and github.com does not offer pre-receive hooks. A server-side check exists only where the
repository's owner configures one: the installed workflow runs the conformance check on every pull
request where GitHub Actions is enabled, and it blocks a merge only where a branch ruleset requires
that check to pass. This framework's own repository has both; an adopting repository has neither
until its owner sets them, and nothing installed here can set them on the owner's behalf. Any
document claiming the hook is unavoidable would be false.

What *is* guaranteed is narrower in one respect and stronger in another:

> **No repository state containing a violation can pass the conformance check, whenever that
> check runs.**

A developer can bypass the hook. They cannot bypass it *and* have the repository pass afterwards,
because the bypass is written permanently into the commit graph and the history audit reads that
graph rather than the working tree. Repairing the file later does not repair the history. The only
ways to clear a violation are to record an exception, which is itself permanent and attributable,
or to rewrite history, which is detectable and is a far louder act than the original bypass.

Four layers, in increasing order of reliability:

| Layer | Catches | Defeated by |
|---|---|---|
| **Local hook** | **Accidental staged violations** | **`--no-verify`, or not installing the hook** |
| **History audit** | **Deliberate bypass** | **Rewriting published history** |
| Manifest digests | Tampering with the checker itself | Nothing available to an adopter |
| CI | Everything, at push time | Being switched off — which it currently is |

The local hook and history audit both work without GitHub Actions. The hook prevents the ordinary
path; the audit detects the bypass.

## How the check works

For each gate decided `required`, the normal checker:

1. Confirms every artefact in `precondition.artefacts` exists in the working tree, is non-empty,
   and carries no unreplaced placeholder token — `replace-me`, `TODO`, `TBD` or `TBC`. An empty
   file satisfies a path check and no one else.

   **Detection is by token, not by shape, and the limit matters.** The check does *not* flag
   angle-bracket notation such as `<schema-file-name>`. An unfilled slot and a metavariable are
   lexically identical, and the earlier shape-based rule failed on this framework's own
   normative documents and on any adopter artefact containing a usage line (`F14`, `DR-17`).
   The consequence for an adopter is worth stating plainly: an artefact whose blanks are marked
   some other way — a bare `Owner:` with nothing after it — is **not** detected. Every template
   shipped under `templates/` carries a `replace-me` marker so that copying one and leaving it
   blank *is* caught; a template of your own must do the same to get the same protection.

   **This is a requirement on the adopting repository, not a suggestion.** If you write your own
   template and a gate names a copy of it as a precondition artefact, put one of the four tokens in
   it. Otherwise a blank form satisfies `SP032` — it exists, it is non-empty, and it carries no
   token — and the gate points at nothing while reporting that it points at something. That is
   `F15`, and it is open in general precisely because the alternative was rejected on evidence: a
   rule that guessed at blank forms by their shape was removed under `DR-17` after producing seven
   false positives and no true ones. The framework will not guess; you must mark.
2. Reads `effective_from`, rejects a date in the future, and compares it against every value
   that gate has *ever* carried in the profile's own git history. If the date has moved forward,
   the check fails and **is never graced** — see below.
3. Runs `git log --since=<effective_from> -- <gated_activity.paths>` and, for each commit
   returned, asks whether the precondition artefacts existed **in that commit's tree**. Any
   commit that changed a gated path while a precondition was absent is a violation.
4. Excludes any commit covered by an exception record in `governance/exceptions/`.

Where git history cannot be read, the check reports that the audit did not run. That is an
absence of evidence and is reported as such, rather than allowed to look like a pass.

For each required gate whose `enforcement` includes `local_hook`, the pre-commit invocation also:

1. Asks Git which staged paths match `gated_activity.paths`, preserving Git pathspec semantics.
3. Reads each precondition artefact from the index, so an untracked or unstaged working-tree file
   cannot create a false pass.
4. Verifies the standard-owned files, install record and managed Copilot block from the index, so
   a valid working tree cannot hide a staged control change.
5. Reads gate exception records from the index, so an untracked or unstaged exception cannot
   suppress a historical violation in the commit being created.
6. Blocks the commit with `SP039` if a required artefact is absent, empty or unfinished, with
   `SP040` if the staged control is invalid, with `SP041` if the staged profile cannot be read,
   with `SP042` if Git rejects a pathspec, or with `SP043` if an exception is invalid or names an
   unresolved commit.

## `effective_from`, and why it can never move forward

A gate binds from a date. History before that date is out of scope. Without this, adopting a
gate would require rewriting the past, and no real repository would ever adopt one.

The obvious way to game this is to move the date forward, which silently discards every
violation between the old date and the new one. So the checker reads the profile's own git
history, recovers the earliest `effective_from` this gate has ever declared, and fails if the
current value is later. This finding (`SP034`) is **never graced**, for the same reason the
review-horizon cap is never graced: a control whose anti-gaming rule can itself be deferred is
not a control.

The date may move *backward* freely. Claiming a gate bound earlier than it did only ever
increases the scrutiny a repository invites.

## Exceptions

A control with no legitimate escape route gets bypassed illegitimately instead. So there is one,
and it leaves a permanent mark.

An exception record lives in `governance/exceptions/`, validates against
`schemas/gate-exception.schema.yaml`, and names the gate, the specific commit SHAs it covers, an
accountable owner, and a rationale. It clears exactly those commits and nothing else. It cannot
be written retrospectively without appearing in history as a retrospective act.

An accumulation of exception records is a finding in its own right, and should be read as
evidence that the gate is wrongly scoped or the process is wrong — not as a clean bill of health.

## Declaration, and what each level demands

Gates are declared in the `prerequisites` block of `governance/application-profile.yaml`. Each
carries a status:

| Status | Meaning | Also requires |
|---|---|---|
| `required` | The gate binds and is audited | `effective_from`, `precondition`, `gated_activity` |
| `deferred` | It will bind, but not yet | `rationale`, `owner`, `revisit_by` |
| `not_applicable` | It does not apply here | `rationale` |

A deferral with no owner and no date is an omission wearing a decision's clothes, so the checker
rejects it.

**The level sets a floor on which gates must be `required`:**

| Level | Gates that must be `required` |
|---|---|
| `essential` | `work_registration` |
| `standard` | the above, plus `authority_map`, `decision_before_implementation`, `change_record_before_completion` |
| `full` | the above, plus `authority_same_change`, `regression_before_merge`, `equivalence_evidence`, `data_source_lifecycle`, `output_validation_before_external_use`, `dependency_output_delta`, `records_before_release` |

At `standard` and `full`, a repository that declares `builds_user_interface: true` also has
the four interface gates in its floor. See below.

As with control decisions, a level is a floor and never a ceiling.

**At `standard` and `full`, every gate in the catalogue must additionally be *declared*** —
`required`, `deferred` or `not_applicable`, each with a reason. `not_applicable` is a perfectly
good answer: an application with no user interface should record that the four interface gates do
not apply to it. What it may not do is leave the question unasked. Silence is not a decision.

The questionnaire chooses *how* a required gate is satisfied and *which paths* it covers. It
never chooses *whether* a required gate applies.

## `builds_user_interface`

One boolean in the profile, and it is not descriptive. It decides whether the four interface
gates are a floor.

| Value | Effect at `standard` and `full` |
|---|---|
| `true` | `component_library`, `design_authority`, `options_before_build` and `prerequisite_state_ui` must all be `required`. `not_applicable` is rejected as self-contradictory. |
| `false` | All four must be `not_applicable`. Declaring one `required` or `deferred` is rejected as self-contradictory. |
| absent | A finding at `standard` and `full`. The answer is the difference between a floor and no floor. |

The floor is conditional rather than absolute for a specific reason: the checker cannot tell
whether a repository has a user interface, and an unconditional requirement would leave a
headless service able to conform only by declaring paths it does not have — a fake pass, which is
worse than an honest exemption.

Note what this removes. Under a `deferred`-with-a-rationale scheme, a team building screens could
write "we will define the design policy next sprint" indefinitely and pass. That option no longer
exists. A repository that builds interfaces either has decided its component library, its design
policy and its page templates before starting, or it has not; there is no third state worth
recording. `false` is a claim about the world that a reviewer can falsify in seconds, which is a
better control than a rationale nobody reads.

## The catalogue

Nineteen gates in six groups. Each is stated in general form; each repository binds it to its own
artefacts and paths.

### Design and user interface

| Gate | Rule |
|---|---|
| `component_library` | A component library must contain a component before a screen uses it. |
| `design_authority` | A design policy and screen templates must exist before UI code is written. |
| `options_before_build` | Alternatives must be documented and one selected before a designed surface is built. |
| `prerequisite_state_ui` | A screen must not present its main workflow until its data prerequisite is satisfied. |

These four are the reason this section exists. The rule being carried across is not *"use these
components"* — that would be someone else's design language imposed on an unrelated product. It
is *"decide your component library, your design policy and your page templates before you build
any interface at all."* The specific answers are local. The requirement to have answered before
starting is not.

At `standard` and `full` these four are a **floor** for any repository declaring
`builds_user_interface: true`, which means `deferred` is not available to them. See
"`builds_user_interface`" above. At `essential` they remain declare-or-justify, on the same
proportionality grounds as every other tier difference.

### Work and decisions

| Gate | Rule |
|---|---|
| `work_registration` | No work begins until it is registered as an identified activity. |
| `work_contract` | A written work contract must exist before AI-assisted implementation starts. |
| `risk_classification` | A change must be classified for risk before implementation, not after. |
| `decision_before_implementation` | A decision record must exist before implementation of a material change begins. |
| `register_currency` | The work register and its generated views must be current before handover. |

`risk_classification` is the one most often violated in spirit while satisfied on paper.
Classifying a change after building it rationalises the work that was already done.

### Documentation authority

| Gate | Rule |
|---|---|
| `authority_map` | A machine-readable map of which document governs which path must exist. |
| `authority_same_change` | A change to a governed path must update its controlling document in the same change. |

Without the map, "the documentation" is a claim rather than an addressable object, and
`authority_same_change` has nothing to check against. The two are almost always adopted together.

### Tests and evidence

| Gate | Rule |
|---|---|
| `test_convention` | New tests must follow the repository's declared naming and location standard. |
| `regression_before_merge` | Named regression suites must pass before a change to critical logic merges. |
| `equivalence_evidence` | A performance or refactoring change on a critical path must ship evidence results are unchanged. |

`equivalence_evidence` exists because "it looked the same" is the most common form of evidence
offered for a refactor, and it is not evidence.

### Data

| Gate | Rule |
|---|---|
| `data_source_lifecycle` | A data source must pass its validation and approval lifecycle before it is selectable. |
| `output_validation_before_external_use` | Generated outputs must be validated and reviewed before use outside the delivery team. |

An unapproved data source that is merely *present* will eventually be used.

### Dependencies and release

| Gate | Rule |
|---|---|
| `dependency_output_delta` | A dependency change able to move outputs requires delta evidence and review before merge. |
| `records_before_release` | The change and decision records required by the risk class must exist before release preparation. |
| `change_record_before_completion` | A change record must exist before a change is treated as complete. |

A lock file records what changed. It does not record what the change *did*, which is what
`dependency_output_delta` is for.

## Repository-specific gates

A repository may declare a gate that is not in the catalogue by giving it any `id` together with
`catalogue_id: custom`. Custom gates are checked against history identically. They are not counted towards the
level floor, and they do not satisfy the full-declaration requirement in place of a catalogue
gate.

If several repositories independently declare the same custom gate, that is a candidate for the
catalogue and should be raised as a change to this standard.

## Findings

| Code | Meaning | Graceable |
|---|---|---|
| `SP027` | No `prerequisites` block | Yes |
| `SP028` | Malformed, duplicated, or uncatalogued gate | Yes |
| `SP029` | A gate the level requires is absent, or the catalogue is incompletely declared | Yes |
| `SP030` | A gate the level requires is decided otherwise | Yes |
| `SP031` | `deferred` or `not_applicable` without a rationale, owner or revisit date | Yes |
| `SP032` | A precondition artefact is missing, empty, or still a template | Yes |
| `SP033` | `effective_from` absent, unreadable, or in the future | Yes |
| `SP034` | **`effective_from` moved forward** | **Never** |
| `SP035` | A gated path was changed while its precondition was absent | Yes |
| `SP037` | `builds_user_interface` absent at `standard`/`full`, or contradicted by an interface gate's status | Yes |
| `SP046` | `secret_hygiene` names no scanner, or names wiring that is absent or never invokes it | Yes |
| `SP047` | The declared scanner's step cannot fail the job | Yes |
| `SP051` | A control's implementation reference is missing, unresolvable, empty, or a template | Yes |
| `SP052` | `documentation_authority` is required without the `authority_map` gate | Yes |
| `SP053` | A control's named CI step is missing, runs nothing, or cannot fail | Yes |
| `SP054` | A deferral or deferred gate has passed its `revisit_by`, or carries an unreadable one | Yes |
| `SP055` | A record-based control names no register, or one that is missing, is a file, or holds untracked records | Yes |
| `SP056` | A record in a declared register is unreadable or invalid against its schema | Yes |
| `SP057` | A record references a method, run or override that is absent from the register it names | Yes |
| `SP058` | Two records in one register claim the same identity, or a record carries another application's `application_id` | Yes |

## Worked examples

`examples/application-profile.essential.example.yaml` shows the minimum: two required gates and
one honest deferral, for a fixture-driven frontend demonstrator.

`examples/application-profile.full.example.yaml` shows a complete declaration: fifteen required
gates, and the four interface gates decided `not_applicable` because the application is a
headless API — which is a decision the profile records, not a question it omits.
