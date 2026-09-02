# Installing Surfaceplate

Two commands. Then one file to fill in.

---

## What you are installing

| Path | Owner | What it is |
|---|---|---|
| `.github/instructions/*.instructions.md` | The standard | Rules the AI assistant must follow. Copilot reads these automatically, **in addition to** your own `copilot-instructions.md`. |
| `.github/skills/*/SKILL.md` | The standard | The workflow for each kind of task: change, bug fix, review, CI fix, dependency update, security review, release. |
| `.github/workflows/standards-conformance.yml` | The standard | The CI check. |
| `.githooks/pre-commit` | The standard | The local commit-time check. The installer activates it with `core.hooksPath=.githooks`. |
| `.claude/rules/surfaceplate-*.md` | The standard | The agent instructions, in the form Claude Code loads. |
| `.github/instructions/*.instructions.md` | The standard | The same instructions, in the form GitHub Copilot loads. |
| `.standards/agent-instructions/*.md` | The standard | The canonical copies. If your agent reads neither form above, point it here. |
| `AGENTS.md` | **You**, apart from the marked block | The installer inserts a conformance block and preserves everything outside it. Your own content is never touched. |
| `.standards/` | The standard | A pinned copy of the standard, the schemas, and the checker. Machine-managed. Do not edit. |
| `.github/copilot-instructions.md` | **You** | Your own guidance. The installer appends a marked block; everything outside the markers is untouched. |
| `governance/application-profile.yaml` | **You** | Your repository's control decisions. Created from a template, never overwritten. |

No product file is touched. The installer also sets the repository-local Git configuration
`core.hooksPath=.githooks`. If another hook path or a default pre-commit hook already exists, the
installer stops before writing anything so the existing automation is not silently disabled.

**If you have your own hook system and intend to keep it, install with `--no-hooks`.** The hook is
one enforcement route of three: a profile whose gates declare `enforcement: [history_audit, review]`
is fully conformant without it. `--no-hooks` writes no `.githooks/`, leaves `core.hooksPath` exactly
as it was, and records the declination in `.standards/INSTALL.json` so every conformance check
reports it. What you give up is stated rather than implied: nothing will check staged changes before
they are committed, and a gate violation is caught by the history audit after the commit rather than
before it. Declaring `local_hook` enforcement anyway is a finding (`SP038`), and that check compares
the hook Git will actually run against the one this standard installed — an unrelated pre-commit
hook does not satisfy the claim.

---

## Install

```bash
# once, into a virtual environment on your machine
python3 -m venv .venv && . .venv/bin/activate
pip install 'git+https://github.com/pipoventures/surfaceplate@main'

# then, for each repository
surfaceplate doctor
surfaceplate install --target /path/to/your-repo --dry-run
surfaceplate install --target /path/to/your-repo
surfaceplate check --repo /path/to/your-repo
```

Always run `--dry-run` first. It writes nothing and shows you exactly what would change.
`surfaceplate doctor` says, one line each, what on this machine would stop the next commands: a
global `core.hooksPath`, a Python without pip, a virtual environment the hook cannot find, an
installed copy of the standard that is not the release this tool ships (`adopt` refuses until it
is upgraded, and names the command).

Working from a clone instead? From inside the clone, `python surfaceplate/install_standard.py
--target ...` does the same thing without installing anything: the installable package is the
`surfaceplate/` directory inside the clone.

Requirements: Python 3.9 or later, plus `PyYAML` and `jsonschema` in an interpreter available to
the hook. The virtual environment above provides them; `pip install` into the system interpreter
does not work on most current Linux distributions, whose Python is a PEP 668 interpreter that
refuses it ("externally-managed-environment") or ships without pip ("No module named pip"). The
distribution's own packages are the other route:

```bash
sudo apt install python3-yaml python3-jsonschema
```

The hook resolves an interpreter from `PATH` and requires one that can import **both** packages.
If you install into a virtual environment, that environment must be on `PATH` when you commit, or
the hook will refuse to run and the commit will fail closed. It fails closed deliberately: a hook
that skipped its check on a missing dependency would be worse than no hook.

The standard remains application-stack neutral: these packages run the governance contracts, not
the adopting repository's product code.

`core.hooksPath` is local Git configuration, not a tracked repository setting. The person running
the installer gets the hook immediately. In every later clone, run the installer once to activate
the tracked hook. Do not set `core.hooksPath` directly: the installer first checks effective local,
worktree, global and system configuration and every existing hook type, so activation cannot
silently disable another hook system.

Before the first adoption commit, preserve the hook's executable mode in Git:

```bash
git add .githooks
git update-index --chmod=+x .githooks/pre-commit
```

The staged check refuses mode `100644`, even on Windows where the hook can still run locally,
because a Linux clone would ignore that committed hook.

### If the installer stops

If your repository already has files where the standard puts its own — for example a hand-written
`.github/skills/change/SKILL.md` — the installer **stops and writes nothing**, and lists the
conflicts.

It also stops if the effective `core.hooksPath` comes from repository, worktree, global or system
configuration, or if the default hooks directory contains any active hook type. Setting a new
hooks path changes where Git looks for every hook, not only `pre-commit`; silently disabling an
existing `commit-msg` or `pre-push` hook would be a regression.

That is deliberate. Those files may contain stack-specific guidance the stack-neutral standard
does not reproduce, and losing it silently would be a regression. See
[`RECONCILIATION.md`](RECONCILIATION.md) for how to resolve it. Only use `--replace-existing` once
you have decided the standard supersedes what is there.

---

## Complete your application profile

`governance/application-profile.yaml` is the only file you have to write. It records what controls
apply to this repository and why.

**Recommended: run `surfaceplate adopt`.** It asks what only you can tell it, proposes the rest
from your repository and this framework's own worked examples, shows every value with where it
came from, and writes a complete, schema-valid profile only once you approve the review — with the
origin of every value recorded beside it in `governance/application-profile.provenance.yaml`. It
never selects a level or makes a scope decision on your behalf: every gate is decided by you, one
key each. Needs the `adopt` extra (`pip install 'surfaceplate[adopt] @ git+https://github.com/pipoventures/surfaceplate@main'`,
or `python -m pip install textual==8.2.8` alongside a git-clone install) and a real terminal.
Without one, `surfaceplate adopt --propose --target <repo>` writes the proposal and an answers
record in which every decision only a human can make says `needs-human`; complete those lines and
`surfaceplate adopt --answers <file>` replays the record through the same code. `surfaceplate
install`/`check` need nothing beyond `PyYAML` and `jsonschema`. Once it has written the profile,
the checker runs against it and says what is still missing.

The steps below are what `surfaceplate adopt` does on your behalf — read them if you are filling
the profile in by hand instead, or want to understand what a generated profile actually contains.

1. Choose a conformance level — `essential`, `standard`, or `full`. See
   `.standards/core/CONFORMANCE_LEVELS.md`. Choosing a lower level is a legitimate, recorded
   decision; pretending to a higher one is not.
2. Copy the shape of the nearest worked example in `.standards/examples/`.
3. Replace **every** placeholder. The check fails on any that remain.
4. Fill in the `adoption` block: which version of the standard, its digest, the date, the
   maintainer, the decision record, and `review_by`.

`review_by` is the date by which a human must re-read the profile and confirm it still describes
the repository. Nothing automated can tell that a repository has outgrown the level it declared —
the files are intact, the schema is satisfied, and the claim is simply no longer true. 180 days is
the suggested interval; 400 is the furthest ahead the checker will accept. Once the date passes,
the check fails.

---

## Declare your prerequisite gates

The `prerequisites` block is the second thing you have to write — or, again, what `surfaceplate
adopt` writes for you, one gate at a time. A gate is a rule of the shape *"X must exist before Y
may begin"*. Read `.standards/core/PREREQUISITE_GATES.md` first.

1. Every level requires at least `work_registration`. `standard` and `full` require more, and also
   require that **every** catalogue gate is declared — `required`, `deferred`, or
   `not_applicable`, each with a reason. `not_applicable` is a good answer; an omitted gate is not.
2. For each gate you decide `required`, name the `precondition.artefacts` that must exist and the
   `gated_activity.paths` they gate. These are your paths, not ours.
3. Set `effective_from` to your adoption date. History before that date is out of scope, which is
   what lets you adopt a gate without rewriting the past.

**`effective_from` can never move forward.** The checker reads your profile's own git history,
recovers the earliest date each gate has ever declared, and fails if the current value is later —
because moving it forward silently discards every violation in between. That finding is never
graced. It can move backward freely.

If a gate was genuinely crossed — an emergency fix, a commit made before adoption was understood —
record it in `governance/exceptions/` using `.standards/templates/gate-exception.yaml`. It clears
exactly the commits it names. A growing pile of exception records is a signal that the gate is
scoped wrongly, and should be treated as one.

---

## Verify

```bash
surfaceplate check --repo .          # or: python .standards/check_conformance.py
```

Run it locally before you push. `--format json` and `--format sarif` give the same report as data;
exit codes are `0` pass or graced, `1` findings that fail, `2` not installed, `3` usage error, `4`
internal error. Every code the checker can report is listed in
`.standards/core/CONFORMANCE_LEVELS.md`. **If GitHub Actions is not enabled for your repository, this is
also what the installed pre-commit hook runs automatically** — see "Where this check actually
runs" below.

Three possible outcomes:

- **PASS** — conformant. An `Advisory` section may still appear; it is informational, not a
  failure.
- **WARN** — your profile is incomplete, but you are inside the adoption grace window. Exit code 0,
  so CI stays green. The message tells you when that stops being true.
- **FAIL** — either the window has closed, or standard-owned files have been altered or deleted.

Integrity failures are **never** graced. If a skill, instruction or the conformance block has been
edited locally, the check fails immediately and says which file. Re-run the installer to repair it.

For prerequisite gates declaring `local_hook`, the hook reads the **staged snapshot**, not merely
the working tree. A gated file cannot be committed while its prerequisite is unstaged, deleted,
empty or still a template. These findings are never graced.

---

## Where this check actually runs

The installer places a workflow at `.github/workflows/standards-conformance.yml`. It runs on pull
requests and on pushes to the default branch — **if GitHub Actions is enabled**.

Where a repository or its organisation has Actions **disabled**, the workflow is installed but
**dormant**: it will never run, and no status check appears on a pull request. In that case:

- the activated pre-commit hook still runs the conformance check and staged prerequisite checks
  before ordinary commits in that clone;
- `git commit --no-verify` can bypass the hook, so the repository has local enforcement but no
  unavoidable server-side enforcement;
- a later conformance run audits history and exposes a bypassed prerequisite gate.

The workflow is installed either way, so that enablement is a switch rather than a migration.

**A workflow that runs is still not enforcement.** Even where Actions is enabled, the check is
self-administered until an organisation ruleset requires its status check — a repository admin can
edit or delete the workflow. Do not read the presence of the workflow file, or a green run, as
evidence that anything is being enforced.

---

## The grace window

You get **30 days from first install** to complete your profile. The clock starts at first install
and does not reset when you re-run the installer or hand-edit the recorded expiry date — the
checker caps the window independently. This is intentional: a grace window that can be extended is
an opt-out with a friendlier name.

---

## Upgrading

```bash
cd surfaceplate && git pull
# the outer "surfaceplate" above is whatever you named your clone; the inner one below is the
# fixed package directory inside it - the two are coincidentally the same word, not the same thing
python surfaceplate/install_standard.py --target /path/to/your-repo --dry-run
```

The installer reports exactly what changes, removes controls the new version has dropped, never
touches your profile, and refreshes the marked block in your Copilot instructions while leaving
your own content alone. It also installs and activates the tracked pre-commit hook. Running it
twice in a row changes nothing the second time.

---

## Frequently asked

**Does this replace our existing Copilot instructions?**
No. Copilot reads `.github/instructions/*.instructions.md` *in addition to*
`.github/copilot-instructions.md`. Your file stays yours; the standard adds a marked block to it
stating the precedence rules.

**Can I edit a skill to suit our repository?**
Not in place — the integrity check will fail, by design. If a change is genuinely needed, raise it
against the standard so every repository benefits. If it is truly repository-specific, put it in
your own `copilot-instructions.md` or in an instruction file the standard does not own.

**What if the check is wrong?**
Then the checker has a defect and it should be fixed here, not worked around there. Raise it. Do
not delete the workflow.

**Can I bypass the pre-commit hook?**
Git permits `git commit --no-verify`; a client-side hook cannot prevent that. The history audit is
the backstop: a bypassed prerequisite violation remains in the commit graph and causes later
conformance checks to fail until a specific, attributable exception is recorded.

**Does the AI assistant actually obey this?**
It follows the instructions and skills far more consistently than free-text guidance, but it is
not a control system. The conformance check is the control; the instructions are the steer. Do not
confuse the two — and note that where Actions is disabled, the control only runs when the hook fires
or someone runs it by hand.
