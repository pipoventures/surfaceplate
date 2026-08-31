@AGENTS.md

# Surfaceplate

This repository publishes the standard above and installs it into itself, so the instructions
imported here are the same ones every adopter receives.

**Why this file exists**, recorded because its absence was a finding rather than an oversight:
until `F29` this repository had no `CLAUDE.md` at all, and its 501 lines of agent instructions sat
in `.github/instructions/` — a location Claude Code does not load. Every packet of governance work
here was done by an agent that had never read them. The import above is what closes that.

## Working here

- `python3 tests/validate_contracts.py`, `tests/test_install_and_check.py`,
  `tests/check_identifiers.py`, `tests/check_code_registers.py` and `tests/check_vendored_current.py`
  are the five suites. Each reports a count on success, so "everything passed" is distinguishable
  from "nothing ran".
- After changing anything the standard ships, run `scripts/build_release.py`, reinstall from a clean
  source copy, then `scripts/build_release.py --verify-manifest`. The vendored copy under
  `.standards/` is what the hook and the installed workflow actually execute; source and vendored
  drifting apart is `F12`.
- `org/FINDINGS.md` is the single findings register and `org/decisions/` holds the decision records.
  A defect found here is recorded there, including when it is a defect in this framework itself.
