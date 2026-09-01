@AGENTS.md

# Surfaceplate

This repository publishes the standard above and installs it into itself, so the instructions
imported here are the same ones every adopter receives.

**Why this file exists**, recorded because its absence was a finding rather than an oversight:
until `F29` this repository had no `CLAUDE.md` at all, and its 501 lines of agent instructions sat
in `.github/instructions/` — a location Claude Code does not load. Every packet of governance work
here was done by an agent that had never read them. The import above is what closes that.

## Working here

- **Eleven suites**, and each reports a count on success so "everything passed" is distinguishable
  from "nothing ran". `.github/workflows/standard-self-check.yml` is the authority for the full set
  and the order — it runs every one and then asserts that every one actually ran. Five need no
  optional dependency: `validate_contracts.py`, `test_install_and_check.py`, `check_identifiers.py`,
  `check_code_registers.py`, `check_vendored_current.py`. Four more cover `adopt`: `test_adopt.py`,
  `test_provenance.py`, `test_discover.py`, `test_scaffold.py`. Two need `textual` and so must be run
  from the virtualenv (`.venv/bin/python`): `test_render.py`, `test_adopt_tui.py`.
  *(This line said "the five suites" until `ACT-033`, six suites after that stopped being true.)*
- After changing anything the standard ships: `scripts/build_release.py`, reinstall from a clean
  source copy, re-pin `adoption.framework_digest` from `.standards/INSTALL.json`, and then **build
  the manifest again, last**. The order matters and CI fails on it otherwise: the checker compares
  the profile against the install record, while `--verify-manifest` compares the manifest against the
  working tree, so pinning the digest after the final build leaves the manifest stale. The vendored
  copy under `.standards/` is what the hook and the installed workflow actually execute; source and
  vendored drifting apart is `F12`.
- `org/FINDINGS.md` is the single findings register and `org/decisions/` holds the decision records.
  A defect found here is recorded there, including when it is a defect in this framework itself.
