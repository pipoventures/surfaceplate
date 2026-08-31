# Reconciling a repository that already has its own instructions and skills

The installer stops rather than overwrite files you wrote. This is how to resolve that.

## Why it stops

The standard owns fixed paths: `.github/instructions/*.instructions.md` and
`.github/skills/<name>/SKILL.md`. If your repository already has a file at one of those paths, the
installer cannot tell whether it is a rough draft or the most carefully considered document in the
repository. So it refuses, lists the conflicts, and writes nothing.

The case this exists for is a repository that already carries some or all of the seven skill names
and the six instruction file names, with its own stack and methodology detail in them that the
stack-neutral standard deliberately does not reproduce. Overwriting those would be a regression
presented as an installation.

## The distinction that resolves it

Separate two things that tend to sit in the same file:

- **How work is controlled** — what must be true before a change merges; when to stop and ask; what
  evidence to produce. This is common across every repository, and it belongs to the standard.
- **How work is done here** — the language, the package layout, the test runner, the methodology,
  the client-branch model, the deployment target. This is specific, and it belongs to you.

Almost every existing skill file is a blend. Split it.

## Procedure

1. **Diff, don't assume.** For each conflicting file, compare it with the standard's version:

   ```bash
   diff .github/skills/change/SKILL.md ../surfaceplate/standard/.github/skills/change/SKILL.md
   ```

2. **Classify every paragraph** as control or stack-specific.

3. **Anything genuinely missing from the standard** — a gate, a stop condition, a required input
   that applies to any repository — should be raised against the standard, not kept locally. If it
   was worth having in one repository it is probably worth having in all of them.

4. **Move the stack-specific content out of the standard-owned paths.** Put it in an instruction
   file the standard does not own — for example `r-package.instructions.md`,
   `data.instructions.md`, `docs.instructions.md` — or in your own `copilot-instructions.md`.
   Copilot loads all of them, so nothing is lost. Adding an `applyTo:` frontmatter pattern lets you
   scope it to the relevant files.

5. **Re-run the installer** with `--replace-existing` once the conflicting files contain nothing
   you still need.

6. **Record what you did.** The reconciliation is a change to how the repository is controlled.
   Note it in the application profile's decision record.

## What must not happen

- Do not keep two skills with near-identical names. If both a `change` and a `local-change` skill
  exist, the assistant will pick one unpredictably, and you will have two authorities for one
  control — the exact failure the standard exists to prevent.
- Do not resolve a conflict by weakening the standard's version to match the local one.
- Do not mark the repository as conformant while the reconciliation is outstanding. Record the
  adoption status as `deferred`, with a rationale, and complete it.

## The shape that needs a decision, not a merge

The hardest case is not a naming collision but two mandates that overlap without being identical —
an adopter that mandates an activity-register gate, say, where the standard mandates a work-packet
gate. Two canonical authorities for one control is a defect under the standard's own principles, so
**one of them must give way**, explicitly and on the record.

Do not resolve this by merging the two into a single document that satisfies neither. Decide which
is authoritative, record the decision, and demote the other to guidance. A repository with this
conflict outstanding should not be marked in scope until it is settled.
