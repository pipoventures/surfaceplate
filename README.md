# Surfaceplate

A single, installable definition of how software is built, reviewed, and released — and of how AI
assistants are allowed to participate in that work.

**Status: not independently audited; one adopting repository, the owner's own; enforced server-side on this
repository only.** A branch ruleset on `main` requires all four status checks and a pull request,
with no bypass actors — demonstrated to block a merge, not merely configured. That protects *this*
repository. It says nothing about any adopting repository, which must apply its own. The installed
pre-commit hook remains bypassable with `--no-verify`. See
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
what installing costs, and [`surfaceplate/core/`](surfaceplate/core/) for the control principles themselves. Written for a
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
pip install 'git+https://github.com/pipoventures/surfaceplate@main'

surfaceplate --version
surfaceplate doctor                       # what on this machine would stop the next commands
surfaceplate install --target /path/to/your-repo --dry-run
surfaceplate install --target /path/to/your-repo
surfaceplate check --repo /path/to/your-repo
```

If `surfaceplate install` stops with *"Git hooks for this repository already run from somewhere
else"*, your machine sets `core.hooksPath` globally or at system level: `surfaceplate doctor` shows
where, and `surfaceplate install --no-hooks` keeps your own hook system and records the choice in
the install record, so every conformance check reports it.

**Not the instruction to follow yet: `pip install surfaceplate`.** The name is reserved on PyPI —
`0.16.0` and `0.16.1` are both on the index, each carrying the `Development Status :: 3 - Alpha`
classifier — but every instruction here keeps naming the git form until 1.0
([`DR-61`](org/decisions/DR-61.md)). The PyPI upload is a reservation, not the install route: "not
independently audited" should not be contradicted by anything an adopter is told to run. The git
form was run into a clean virtualenv before being written here, which is more than could be said for
the instruction it replaced (`F57`). Publishing it as the install route is a release decision and is
listed in [`org/HUMAN_ACTIONS.md`](org/HUMAN_ACTIONS.md).

Working from a clone instead? `python surfaceplate/install_standard.py --target ...` does the same
thing without installing anything.

Then, to fill in `governance/application-profile.yaml` — the one file the installer leaves for you
to write — run the interactive wizard rather than editing the template by hand:

```bash
pip install 'surfaceplate[adopt] @ git+https://github.com/pipoventures/surfaceplate@main'
surfaceplate adopt --target /path/to/your-repo
```

It asks what only you can tell it — who owns this, whether it builds an interface, who relies on
its output, how its data is classified, the conformance level — proposes the rest from your
repository and its own worked examples, shows every value with where it came from, and writes
nothing until you approve the review. Every gate the level asks about is decided by you, one key
each; nothing is pre-marked. Without a terminal, `surfaceplate adopt --propose` writes the
proposal and an answers record for a human to complete, and `surfaceplate adopt --answers <file>`
replays it.

**What it will and will not fill in for you**, stated precisely because the looser version of this
sentence turned out to be false (`F51`): it never chooses your conformance level, writes a
rationale, or makes a scope decision such as which paths a gate covers or the date it binds from. It
does supply facts of record — the date you adopted, the version you installed — and its own
published prose, such as a gate's definition. Where it can propose an answer it shows you the
proposal and where it came from, writes nothing you have not approved at the review, and records
the origin of every value in `governance/application-profile.provenance.yaml` beside the profile.

Full instructions: **[INSTALL.md](INSTALL.md)**.
If the installer stops because of existing files: **[RECONCILIATION.md](RECONCILIATION.md)**.

---

## Reviewing this

**No independent reviewer has looked at this yet — that is what the status line above is stating,
not a formality.** Every finding on record was found by the party who maintains it
([`org/FINDINGS.md`](org/FINDINGS.md) says so in its own closing section). If you have thirty
minutes or a few hours and owe this project nothing, that is exactly the review it needs.

The [release for `pypi/0.16.1`](https://github.com/pipoventures/surfaceplate/releases/tag/pypi%2F0.16.1)
carries a self-contained review packet
(`INDEPENDENT_REVIEW_PACKET-0.16.1.html`, sha256 `59bd0a33352d…`) with two independent asks:

- **Part A (~30 minutes, no context needed):** recompute one SHA-256 from the published PyPI
  package and check it against the anchor this framework publishes. Two independent ways to reach
  the same number are given, so nothing here needs to be taken on trust.
- **Part B (a few hours, wants judgement):** a scoped audit against
  [`audit/AUDIT_SCOPE.md`](audit/AUDIT_SCOPE.md)'s ten criteria, with a stated time-boxed minimum
  and an explicit claim-labelling convention (`FACT FROM PACKAGE` / `INFERENCE` / `RECOMMENDATION`
  / `EVIDENCE GAP`) — "I could not establish this" is a legitimate answer.

Either return is recorded as a named, dated assurance record under `governance/assurance/`, never
folded silently into "validated." See `org/decisions/DR-64.md` for exactly what closes `F6`, this
framework's oldest open finding.

---

## What is in the box

| Directory | Contents |
|---|---|
| `surfaceplate/` | The installable package. Everything below is inside it — `install_standard.py` and `check_conformance.py` sit at its root, beside the payload they copy. Since `ACT-019` (`DR-31`), this is what `pip install`s, and what `git clone` gives you is this directory's parent. |
| `surfaceplate/standard/agent-instructions/` | Six stack-neutral instruction files: AI workflow, authority, activity, provenance, tests, security. Emitted per agent at install — Claude Code's `.claude/rules/`, Copilot's `.github/instructions/` — from this one canonical source. |
| `surfaceplate/standard/.github/skills/` | Seven task workflows: `change`, `bug-fix`, `review`, `fix-ci`, `dependency-update`, `security-review`, `release`. Each states its required inputs, its gates, and its mandatory stops. |
| `surfaceplate/standard/.github/workflows/` | The conformance workflow installed into adopting repositories. |
| `surfaceplate/standard/.githooks/` | The pre-commit hook installed into adopting repositories. It checks the staged snapshot and runs the full conformance check before Git creates a commit. |
| `surfaceplate/core/` | The operating model, control principles, evidence expectations, security baseline, conformance levels, and the prerequisite gate catalogue. |
| `surfaceplate/schemas/` | JSON Schema contracts for application profiles, methods, runs, assurance evidence, overrides, and gate exceptions. |
| `surfaceplate/templates/`, `surfaceplate/examples/` | Blank templates, and worked examples that actually validate. |
| `surfaceplate/adapters/` | Stack-specific guidance for Python, TypeScript, and R. |
| `scripts/` | Maintainer-only release tooling: the release builder and verifier. Never installed into an adopter, never part of the pip package. |
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

> **Layer 4 runs on this repository, and nowhere else.** A ruleset named `main-required-checks`
> targets the default branch, requires a pull request and all four status checks, and lists **no
> bypass actors** — so it binds the maintainer too. It was verified rather than assumed: a direct
> push to `main` was refused with *"Changes must be made through a pull request"*, and a pull
> request whose `Contract and installer tests` check failed was refused with *"the base branch
> policy prohibits the merge"*. Both on 2026-08-31; the probe branch was deleted afterwards.
>
> **What that does not mean.** It protects this repository. It requires nothing of any adopting
> repository, which must apply its own ruleset — `org/ROLLOUT_RUNBOOK.md` describes it. An adopter
> who installs the standard and applies no ruleset has bypassable local enforcement plus a
> self-administered CI check, which is layer 3, and this document should not be read as saying
> otherwise.
>
> One limit is untested and stated rather than glossed: whether an explicit administrator override
> (`gh pr merge --admin`) is refused. GitHub documents rulesets as binding admins when the bypass
> list is empty, and the ordinary merge path was refused for the repository owner — but the
> override flag itself was not exercised, because doing so would have required merging a knowingly
> broken tree to a public branch to find out.

Say this plainly to anyone relying on it. Do not let an installed workflow be mistaken for a
running one.

### The one part that does not depend on CI

**Prerequisite gates** are rules of the shape *"X must exist before Y may begin"* — a design policy
before any UI code, a registered activity before implementation, a decision record before a material
change. See **[`surfaceplate/core/PREREQUISITE_GATES.md`](surfaceplate/core/PREREQUISITE_GATES.md)**.

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

It does not run its CI check on a forge other than GitHub by itself. The installed workflow is a
GitHub Actions file; on another forge it is inert, and you add a job that runs
`python .standards/check_conformance.py --repo .` yourself. 1.0 supports GitHub (`DR-62`); a
per-forge emitter is 1.x work, taken up when an adopter on another forge appears.

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

- **Version 0.16.1.** See [`CHANGELOG.md`](CHANGELOG.md). The 0.6.0 pre-audit defects are
  remediated — [`audit/PRE_AUDIT_FINDINGS_0.6.0.md`](audit/PRE_AUDIT_FINDINGS_0.6.0.md).
- **One adopting repository, and it is the owner's own.** Plutos, a private repository of the same
  maintainer, adopted on 2 September 2026 through `surfaceplate adopt` and was upgraded to the
  published 0.16.0 the next day; its check passes. That is real use by one party, not evidence of
  use by anyone else, and no claim in this repository should be read as more.
- **This repository installs its own standard on itself and passes its own check.** It carries an
  application profile, an activity register, the conformance block and the installed hook, and the
  conformance check runs on every pull request. That was not always so:
  [`org/decisions/DR-13.md`](org/decisions/DR-13.md) declared closing the gap the last ungoverned
  work here, and everything after it is ordered in [`org/RELEASE_PLAN.md`](org/RELEASE_PLAN.md),
  which cites [`org/decisions/DR-12.md`](org/decisions/DR-12.md) for the architecture it is
  ordered against. Passing its own check is what the check can establish, and no more.
- **The remediation was performed by the same party that wrote the framework.** An independent
  review is a prerequisite for organisation-wide rollout, not a nice-to-have.
- **No independent security review has been performed either.** See
  [`SECURITY.md`](SECURITY.md) for how to report a vulnerability, what actually happens after a
  report, and what is and is not in scope.
- **A ruleset is applied to this repository only, and was demonstrated rather than assumed.** No
  organisation-level ruleset exists, so nothing is required of any other repository.
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

## Licensing

**Two licences, split by artefact type: software is Apache-2.0, documents are CC0-1.0.**

The split exists so that copying a governance document into your repository carries no obligation.
CC0 is a public-domain dedication — no attribution, no licence link, no indication of changes. A
file you copy is a file you stop having to reason about.

| Licence | What it covers |
|---|---|
| **Apache-2.0** — [`LICENSE`](LICENSE) | `scripts/`, `tests/`, `surfaceplate/schemas/`, `surfaceplate/adapters/`, `surfaceplate/install_standard.py`, `surfaceplate/check_conformance.py`, `surfaceplate/standard/.githooks/`, `surfaceplate/standard/.github/workflows/`, and everything not listed opposite |
| **CC0-1.0** — [`LICENSE-DOCS`](LICENSE-DOCS) | `surfaceplate/core/` (the standard text), `surfaceplate/templates/`, `surfaceplate/standard/agent-instructions/`, `surfaceplate/standard/.github/skills/`, `surfaceplate/standard/conformance-block.md` |

Apache-2.0 rather than MIT for the software, because of its express patent grant, and because it
grants no trademark rights. The code is open; the name is not.

**Schemas and adapters are software, not documents**, despite installing alongside the documents and
being written in YAML and Markdown. They are contracts a program parses and stack-specific technical
guidance, so they carry the patent grant with them.

[`NOTICE`](NOTICE) is present as Apache-2.0 requires.

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

**Something wrong, or something you expected and did not get?** See [`SUPPORT.md`](SUPPORT.md).
`surfaceplate doctor --report` assembles a paste-ready report on your own machine — nothing is sent
anywhere until you post it — and names what it collected and what it never gathers at all.

**Every pull request needs a DCO sign-off** (see [`CONTRIBUTING.md`](CONTRIBUTING.md)) before it is
looked at — that is a mechanical prerequisite, checked automatically, and is unrelated to
whether the change itself will be accepted.

**If maintenance stops entirely:** see [`org/SUNSET_PLAN.md`](org/SUNSET_PLAN.md) for what happens
to the repository, to anything published under this name, and to what you have already installed.

Change authority: the maintainer, until a governance owner is designated.
