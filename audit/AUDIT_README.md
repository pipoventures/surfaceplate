# Audit Handoff

Attach the complete release archive — `dist/surfaceplate-<version>.zip`, produced by
`scripts/build_release.py` — together with the prompt for whichever provider is reviewing:
`CHATGPT_ENTERPRISE_AUDIT_PROMPT.md` or `GEMINI_ADVERSARIAL_REVIEW_PROMPT.md` (`ACT-021`,
`org/RELEASE_PLAN.md` item 9). Both attach the same archive and ask the same first step — inspect it
and verify the manifest before reviewing the design — because that discipline is not
provider-specific; only the audit questions and the required-output shape differ between them.

*Corrected 2026-08-31: this named `engineering-control-kit.zip`, the pre-`0.12.0` product name, for
an archive that has not been produced under that name since the rename.*

The package is a revised draft until the re-audit report is received. Record the audit verdict,
findings, accepted changes, and human adoption decision in the receiving governance process. Do not
describe the kit as approved merely because the archive was generated.

**Producer evidence is the test suites, not a document.** `VALIDATION_RESULTS.md` was the producer's
check record until `0.7.0` and is now retired and marked historical ([`DR-21`](../org/decisions/DR-21.md)).
It went stale twice — once as `PRE-AUDIT-0.6.0/F2`, again as `F10` — which is the reason it is no
longer maintained. What an auditor should ask for instead:

- the five suites, each of which reports the number of checks it executed:
  `tests/validate_contracts.py`, `tests/test_install_and_check.py`, `tests/check_identifiers.py`,
  `tests/check_code_registers.py`, `tests/check_vendored_current.py`;
- `python scripts/build_release.py --verify-manifest` and `python surfaceplate/check_conformance.py --repo .`
  (the checker moved under `surfaceplate/` at `ACT-019`; this line was not updated then — found and
  fixed while writing the Gemini prompt above, the same way `ACT-020` found a stale reference in
  `scripts/build_release.py` itself);
- the CI run for the commit under audit, read **per step** — the self-check workflow confirms each
  check produced a result, because a step that never ran reports `skipped` and that is not a pass
  (`F13`).

`VALIDATION_RESULTS.md` still holds the list of checks that remain the receiving repository's
responsibility, and the statement that the audit gate is undischarged. Both are still true and are
marked as such in that file.
