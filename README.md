# Surfaceplate

A single, installable definition of how software is built, reviewed, and released — and of how AI
assistants are allowed to participate in that work.

**Status: not independently audited; no adopting repositories; fails commits locally after
activation in each clone, but not enforced server-side.** The installed pre-commit hook is bypassable with
`--no-verify`, and no organisation ruleset has ever been applied — see
[Status and limitations](#status-and-limitations) and
[How enforcement actually works](#how-enforcement-actually-works).

**Provenance.** This repository's git history begins at `0.16.0`. Development from `0.2.0` to
`0.15.0` happened in a private repository that is retained, archived and unaltered; it is not
published because its early commits carry an internal namespace belonging to a former employer,
which is not ours to publish. Nothing was rewritten to produce this repository — a scrubbed history
would have been a doctored record, and the reasoning is in
[`DR-23`](org/decisions/DR-23.md).

What survives is the documentary record, which is the substantive part: every release from `0.2.0`
in [`CHANGELOG.md`](CHANGELOG.md), all decision records in [`org/decisions/`](org/decisions/), and
all findings in [`org/FINDINGS.md`](org/FINDINGS.md) — including the ones this project failed. Commit
SHAs cited in those documents refer to the private history and will not resolve here.

---

**New to this?** Start with [`INSTALL.md`](INSTALL.md) for what an adopting repository receives and
what installing costs, and [`core/`](core/) for the control principles themselves. Written for a
non-technical reader
first and for engineers in the rest.

---

## The problem this solves

Guidance that lives in one repository stays in one repository. Copy it and it drifts. Write it in a
wiki and nobody reads it. Put it in an AI assistant's context and it is advisory at best.

This repository is the single source. You **install** it into a repository — you do not copy it —
and a checker verifies afterwards that what was installed is still what is there. That checker is
designed to run in CI; where CI is unavailable it still runs on demand, and says so.

---

## Install

```bash
python scripts/install_standard.py --target /path/to/your-repo --dry-run
python scripts/install_standard.py --target /path/to/your-repo
python /path/to/your-repo/.standards/check_conformance.py --repo /path/to/your-repo
```

Full instructions: **[INSTALL.md](INSTALL.md)**.
If the installer stops because of existing files: **[RECONCILIATION.md](RECONCILIATION.md)**.

---

## What is in the box

| Directory | Contents |
|---|---|
| `standard/.github/instructions/` | Six stack-neutral instruction files: AI workflow, authority, activity, provenance, tests, security. Copilot loads these automatically alongside a repository's own instructions. |
| `standard/.github/skills/` | Seven task workflows: `change`, `bug-fix`, `review`, `fix-ci`, `dependency-update`, `security-review`, `release`. Each states its required inputs, its gates, and its mandatory stops. |
| `standard/.github/workflows/` | The conformance workflow installed into adopting repositories. |
| `standard/.githooks/` | The pre-commit hook installed into adopting repositories. It checks the staged snapshot and runs the full conformance check before Git creates a commit. |
| `core/` | The operating model, control principles, evidence expectations, security baseline, conformance levels, and the prerequisite gate catalogue. |
| `schemas/` | JSON Schema contracts for application profiles, methods, runs, assurance evidence, overrides, and gate exceptions. |
| `templates/`, `examples/` | Blank templates, and worked examples that actually validate. |
| `adapters/` | Stack-specific guidance for Python, TypeScript, and R. |
| `scripts/` | The installer, the conformance checker, and the release builder and verifier. |
| `tests/` | Contract conformance tests and end-to-end installer tests. |
| `org/` | The organisation ruleset, the rollout runbook, and the plain-English case for adoption. |
| `audit/` | Audit scope, audit prompt, and the pre-audit findings this version remediates. |

---

## How enforcement actually works

Four layers, doing four different jobs. Do not conflate them.

1. **Instructions and skills** steer the AI assistant. They shape behaviour; they do not guarantee
   it. Treat them as guidance with teeth, not as a control. **This layer works today**, in any
   repository, on any host — Copilot reads the files from the workspace and no CI is involved.
2. **The local pre-commit hook** runs the conformance check automatically and checks the staged
   snapshot for any prerequisite gate that declares `local_hook`. It blocks the commit when a
   gated path is staged without its prerequisite. **This layer works after activation in each
   clone**, but `git commit --no-verify` can bypass it.
3. **The conformance check and history audit** are the durable detective control. They verify that
   the standard is installed, that standard-owned files still match the digests recorded in
   `.standards/INSTALL.json` **at install time**, that the conformance block is
   intact, and that the repository's application profile exists, satisfies the contract, and is
   still in date. Tampering and staged gate violations fail immediately and are never graced.

   **The history audit is scoped to prerequisite gates, and only to those.** It asks, for each
   commit that touched a gate's declared paths, whether that gate's precondition artefacts existed
   in that commit's tree. It has no relationship to the file digests in `.standards/INSTALL.json`.
   **There is no history-based integrity audit.** A modified standard-owned file is detected when
   the checker runs — in CI, in the hook, or by hand — and by nothing else afterwards.

   **What that comparison is, and is not.** It is a comparison against a record held in the
   adopting repository, not against anything published or externally held. It detects drift,
   accident, and casual modification — a file edited in place, a control deleted, a block
   rewritten. It does **not** detect deliberate coordinated modification by someone with write
   access to the repository, because the record the comparison trusts is a plain local file that
   the same person can edit in the same commit. Nothing in this repository signs, publishes, or
   independently anchors that record. See [`org/FINDINGS.md`](org/FINDINGS.md), finding F6.
4. **The organisation ruleset** is what makes the server-side check unavoidable. Without it, a
   repository admin can delete the workflow.

> **Layer 4 is not running.** No organisation ruleset has ever been applied, so no check is
> required of any repository. The conformance workflow runs where Actions is enabled — it executes
> on this repository, confirmed 2026-08-30 by run `33327048783` — but a workflow that runs is only
> layer 3; it becomes unavoidable only when a ruleset requires its status check, and none does.
>
> **In practical terms the standard has bypassable local enforcement plus a self-administered CI
> check, not organisation enforcement.** Layer 4 needs an organisation owner to apply the ruleset.
> See [`org/ROLLOUT_RUNBOOK.md`](org/ROLLOUT_RUNBOOK.md).

Say this plainly to anyone relying on it. Do not let an installed workflow be mistaken for a
running one.

### The one part that does not depend on CI

**Prerequisite gates** are rules of the shape *"X must exist before Y may begin"* — a design policy
before any UI code, a registered activity before implementation, a decision record before a material
change. See **[`core/PREREQUISITE_GATES.md`](core/PREREQUISITE_GATES.md)**.

They matter here because the hook can inspect the staged snapshot before a commit, while the
history audit can inspect the permanent order of events afterwards. Together they produce a
**gate** guarantee that survives Actions being switched off — gates only, not file integrity, for
the reason given above:

> No repository state containing a violation can pass the check, whenever that check runs.

A developer can bypass the hook with `--no-verify`. What they cannot do is bypass it *and* have the
repository pass afterwards, because repairing the file later does not repair the history. The only
clean route is a `governance/exceptions/` record, which is itself permanent and attributable.

This is weaker than prevention and stronger than most things called enforcement. Describe it in
those terms and not in stronger ones.

---

## What this does not do

It does not prescribe a language, framework, database, deployment platform, or product
architecture. It does not grant approval, independent validation, risk acceptance, or release
readiness — no automated check can, and any tool claiming otherwise should be distrusted. It does
not replace a repository's own Copilot instructions; it layers on top of them.

---

## Working on the standard itself

```bash
python3 -m venv .venv && .venv/bin/python -m pip install pyyaml jsonschema
. .venv/bin/activate                       # the hook resolves python3 from PATH
python tests/validate_contracts.py         # contracts
python tests/test_install_and_check.py     # installer and checker, end to end
python scripts/build_release.py            # refuses to build unless both pass
```

A virtual environment is used because most current Linux distributions ship a PEP 668 interpreter
that refuses `pip install` outright. `referencing` is not named: `jsonschema` pulls it in.

`scripts/build_release.py` regenerates `MANIFEST.sha256` and produces a pinned archive with a
recorded digest. `scripts/verify_release.py` lets an adopter verify an archive independently.
`--verify-manifest` checks that the committed manifest still matches the working tree.

Namespace and versioning decisions, and how to reverse them: [`NAMESPACE.md`](NAMESPACE.md).

---

## Status and limitations

- **Version 0.13.0.** See [`CHANGELOG.md`](CHANGELOG.md). The 0.6.0 pre-audit defects are
  remediated — [`audit/PRE_AUDIT_FINDINGS_0.6.0.md`](audit/PRE_AUDIT_FINDINGS_0.6.0.md).
- **There are no adopting repositories.** The standard has never been installed anywhere but here.
  Nothing below has been exercised against a real adopter, and no claim in this repository should be
  read as evidence of use.
- **This repository does not install its own standard on itself.** It runs its own test suite in
  CI, but carries no application profile, no activity register, no conformance block and no
  installed hook. It is not, at present, conformant to what it publishes. Closing this gap is
  declared the last ungoverned work in this repository — see
  [`org/decisions/DR-13.md`](org/decisions/DR-13.md) — and everything after it is ordered in
  [`org/RELEASE_PLAN.md`](org/RELEASE_PLAN.md), which cites
  [`org/decisions/DR-12.md`](org/decisions/DR-12.md) for the architecture it is ordered against.
- **The remediation was performed by the same party that wrote the framework.** An independent
  review is a prerequisite for organisation-wide rollout, not a nice-to-have.
- **No independent security review has been performed either.** See
  [`SECURITY.md`](SECURITY.md) for how to report a vulnerability, what actually happens after a
  report, and what is and is not in scope.
- **The organisation ruleset has never been applied.** It is untested configuration.
- **The local hook is bypassable** with `git commit --no-verify`, and `core.hooksPath` must be
  activated in each clone. After a bypass the history audit still detects a **prerequisite-gate**
  violation. It does **not** detect a modified standard-owned file: the audit is scoped to gates,
  and no history-based integrity check exists. In a clone where the hook was never activated — the
  default state of any clone but the installer's — someone who edits the installed workflow so it
  stops invoking the checker is caught by nothing until a human runs the checker. This is finding
  `F8`; `DR-15` records the remedy and it is not implemented, because organisation rulesets return
  HTTP 403 on this repository's plan.
- **Adoption is currently voluntary.** Nothing here binds a repository that has not installed it.

---

## Maintenance

**One maintainer, part-time, best effort: Mario Pipo.** This is one of several projects the
maintainer works on alongside other commitments; no fixed hours are guaranteed to this repository
specifically. There is no service level, no guaranteed response time, and no guaranteed fix for
anything — for a vulnerability report, see [`SECURITY.md`](SECURITY.md); for everything else, this
section.

**What a contribution needs to have a realistic chance.** Small, well-scoped changes with a clear
rationale, bug reports with reproduction steps, and documentation fixes are the kinds of
contribution most likely to get looked at. Large or architectural changes are less likely to be
reviewed promptly, if at all, given the time actually available. A pull request proposing anything
already permanently ruled out by [`DR-12`](org/decisions/DR-12.md) — hosting, a certification
service, vulnerability scanning, and the rest of that list — will not be accepted regardless of how
well it is written.

**Every pull request needs a DCO sign-off** (see [`CONTRIBUTING.md`](CONTRIBUTING.md)) before it is
looked at — that is a mechanical prerequisite, checked automatically, and is unrelated to
whether the change itself will be accepted.

**If maintenance stops entirely:** see [`org/SUNSET_PLAN.md`](org/SUNSET_PLAN.md) for what happens
to the repository, to anything published under this name, and to what you have already installed.

Change authority: the maintainer, until a governance owner is designated.
