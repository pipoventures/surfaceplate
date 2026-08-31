# Copilot instructions

Repository-specific guidance goes outside the markers below. The block between the markers is managed by the Surfaceplate installer and will be overwritten on upgrade.

<!-- BEGIN SURFACEPLATE -->
## Surfaceplate

This repository operates under **Surfaceplate**, the Pipo Ventures Ltd software delivery
standard. The standard is installed, not copied: it lives in `.standards/`, and its files are
integrity-checked in CI. Do not edit anything under `.standards/`, `.claude/rules/`,
`.github/instructions/`, or `.github/skills/` — raise changes against the `surfaceplate`
repository so every repository gets them.

**Binding rules, in force for every task in this repository:**

- **The standard's agent instructions are mandatory. Read them before acting.** Where anything in
  this file contradicts them, they win. The same six documents are installed once per agent, each
  in the location that agent actually loads: `.claude/rules/surfaceplate-*.md` for Claude Code,
  `.github/instructions/*.instructions.md` for Copilot. If your agent reads neither, the canonical
  copies are in `.standards/agent-instructions/` and you are responsible for loading them.
- `.github/skills/` defines the workflow for each kind of task. Use the matching skill. Its required
  inputs, gates and mandatory stops are not optional.
- **Stop and ask** before anything touching methodology, a material output, a public contract or
  schema, provenance, a security boundary, an irreversible migration, or a release.
- **Never weaken a gate.** Do not skip, disable, suppress or loosen a test, hook, threshold or
  check, and do not regenerate golden files to match new output, without recorded human approval.
- **Report evidence, not intent.** State the commands you actually ran and their actual output.
  Never claim a change is approved, validated, signed off, or production-ready — you cannot grant
  those.
- The repository's control decisions are recorded in `governance/application-profile.yaml`. It is
  the authority for what applies here.

Everything outside these markers is this repository's own guidance and takes effect alongside the
standard, except where it would weaken it.
<!-- END SURFACEPLATE -->
