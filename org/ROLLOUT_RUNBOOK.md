# Organisation rollout runbook

How Surfaceplate goes from "a repository that exists" to "a control that
actually binds" across the organisation.

**Read this first.** Every step below requires GitHub organisation-owner permissions. Whoever
prepared this repository may not hold them. Nothing in this runbook has been executed. Treat it
as a proposal until an organisation owner has performed each step and recorded that they did.

---

## Before anything else: confirm Actions runs

Every rung above 1 assumes workflows can execute. Confirm that for the target repository before
planning around it — a workflow that is installed but never runs is not a control, and a repository
whose owner has disabled Actions cannot reach rungs 2, 3 or 4 no matter what is installed in it.

GitHub Actions **does** run on this repository: confirmed 2026-08-30 by workflow run
`33327048783`, which executed `.github/workflows/standard-self-check.yml` to completion. That
establishes it for this repository only. It says nothing about any other repository or about any
organisation-level setting, and must not be cited as though it did.

Do not describe any repository as organisation-enforced until a ruleset is actually applied to it
and its status check is actually required.

---

## The enforcement ladder

There are five rungs. Each is a real increase in assurance and a real increase in friction. Do
not skip rungs — a control that arrives before the thing it controls is ready produces
circumvention, not compliance.

| Rung | What it means | Who can bypass it | Assurance |
|---|---|---|---|
| 0. Published | The standard exists and is documented. Adoption is voluntary. | Anyone, by doing nothing | None |
| 1. Installed with local hook | The pre-commit hook checks ordinary commits and the history audit detects later bypasses. | A developer, with `--no-verify`; a repository owner, by removing the hook | Preventive on the ordinary local path; detective after bypass |
| 2. Installed and checked | Adopting repositories run the conformance check in CI. | A repository admin, by editing the workflow | Detective, self-administered |
| 3. Required by ruleset | The organisation requires the check on every in-scope repository. | Only an organisation owner | Preventive |
| 4. Required and audited | Rung 3, plus periodic independent review of profiles and overrides. | Nobody silently | Preventive and assured |

**The current release delivers rung 1 after hook activation in each clone**, and has rungs 2 and 3
built and waiting. Adopters stay at their installed version until deliberately upgraded. The ruleset
in `ruleset-standards-conformance.json` is set to `"enforcement": "evaluate"` — dry-run. It reports
what *would* have been blocked and blocks nothing. It has never been applied.

There are currently **no adopting repositories**. Rung 0 is where the standard actually sits.

---

## Why rung 2 is not enough on its own

Be clear-eyed about this. At rung 2 the workflow file lives in the adopting repository. A
repository admin can delete it, and the check stops running. The integrity check detects a
tampered *workflow file* only while the workflow still runs — if the file is deleted, nothing
runs to notice.

The organisation ruleset is what closes that gap: a required workflow is injected by the
organisation, runs regardless of the repository's own files, and cannot be removed by a
repository admin. Until rung 3 is live, conformance can still be bypassed by someone controlling the local repository
or workflow.

Say this plainly to whoever is relying on the control. Do not let rung 2 be described as
enforcement.

---

## Step 1 — Define the scope, before touching anything

Create an organisation **repository custom property** named `delivery_standards`, of type
single-select, with values:

| Value | Meaning |
|---|---|
| `in_scope` | The standard applies and is enforced |
| `adopting` | In scope, currently within its adoption grace window |
| `exempt` | Out of scope, with a recorded reason |
| `unassessed` | Not yet triaged — the default, and a finding in its own right |

Set every repository to `unassessed` initially. The number of repositories still `unassessed`
after 30 days is the single most useful adoption metric you will have.

An `exempt` repository must carry a recorded reason. Exemption without a reason is not an
exemption, it is an omission.

## Step 2 — Pilot on volunteers

Pick two or three repositories whose owners have agreed. Install the standard, complete the
application profiles, let the check run for two weeks.

You are testing three things:
- does the check produce false failures on a real codebase?
- how long does completing an application profile actually take?
- do the instructions and skills change what the AI assistant does, in a way the team values?

If the answer to the third is no, stop and fix the standard. A control nobody finds useful
becomes a control everybody games.

## Step 3 — Publish the ruleset in evaluate mode

1. Create the organisation ruleset from `ruleset-standards-conformance.json`.
2. Set `repository_id` in the `workflows` rule to the numeric ID of this standards repository —
   the placeholder `0` is deliberately invalid so it cannot be applied unedited.
3. Confirm `"enforcement": "evaluate"`.
4. Leave it running for at least two weeks and read the rule insights.

Evaluate mode tells you exactly how many pull requests would have been blocked, in which
repositories, without blocking any of them. This is the step that turns "we think this is
proportionate" into evidence.

## Step 4 — Review the evaluation evidence

Before enforcing, answer these in writing:

- How many pull requests would have been blocked, and in how many repositories?
- Were any of those blocks wrong — a conformant repository failing for a checker defect?
- Which repositories are still `unassessed`, and who owns them?
- What is the break-glass route when the check is wrong and a fix must ship?

If you cannot answer the last one, do not proceed. Every preventive control needs a documented,
audited bypass, or people will invent an undocumented one.

## Step 5 — Enforce

Change `"enforcement"` to `"active"`.

Set `bypass_actors` to a **named, small** set — typically one break-glass team. Every bypass is
logged in the organisation audit log. Review those logs monthly; an unreviewed bypass list
becomes a permanent exemption.

## Step 6 — Audit

Rung 4. Periodically sample application profiles and override records and check that:

- declared conformance levels match what the repository actually does;
- overrides carry genuine approval evidence and have not silently expired;
- `exempt` repositories still merit exemption;
- adoption grace windows have not been repeatedly reset by re-installation.

---

## Prerequisites that are not yet satisfied

State these honestly to anyone approving the rollout:

1. **The standard has not been independently audited.** A pre-audit found four defects, now
   remediated, but the remediation was performed by the same party that wrote the framework. An
   independent review is required before rung 3.
2. **The organisation ruleset has never been applied.** It is untested configuration.
3. **There are no adopting repositories.** Nothing below rung 0 has been exercised against a real
   repository other than this one. A repository hosted outside GitHub cannot be reached by an
   organisation ruleset at all, and would need its own enforcement route or a recorded exemption.
4. **Organisation-level Copilot custom instructions are not version-controlled** and are capped
   at roughly 4,000 characters. They are a useful pointer to this standard, not a substitute
   for it. Do not rely on them as a control.
