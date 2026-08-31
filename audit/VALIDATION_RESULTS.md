# Package Validation Results — HISTORICAL, frozen at 0.7.0

> **This file is a historical record. It is not evidence for any release after `0.7.0`, and it is
> not maintained.** It was retired by [`DR-21`](../org/decisions/DR-21.md), which records why
> producer evidence stopped being a hand-written document.
>
> **Where producer evidence lives now:** the five suites that run on every push and pull request,
> each reporting the number of checks it actually executed —
> `tests/validate_contracts.py`, `tests/test_install_and_check.py`, `tests/check_identifiers.py`,
> `tests/check_code_registers.py`, `tests/check_vendored_current.py` — plus
> `scripts/build_release.py --verify-manifest` and `scripts/check_conformance.py --repo .`. The
> self-check workflow additionally confirms that each of those steps produced a result, so a check
> that never ran cannot be mistaken for one that passed.

The table below is kept as the record of what was claimed at `0.7.0`. **Rows are annotated inline
where they are no longer true or describe a check that no longer exists** — deliberately in the row
rather than only in a note above it, because a correction that depends on reading order is not a
correction. A grep that lands on one of these rows must not return it as a live claim.

Original preamble, as written at `0.7.0`: *"This file records checks run by the package producer for
the current release. It is evidence of package checks. It is not approval, and it is not independent
validation."*

Release recorded: `0.7.0`. Previous release: `0.6.0`. **Current `VERSION` is `0.14.0`.**

## Checks performed — as recorded at 0.7.0

| Check | Method | Result recorded at 0.7.0 |
|---|---|---|
| JSON Schema meta-validity | `Draft202012Validator.check_schema` on every file in `schemas/` | PASS - 5/5 — *count is historical; there are 6 schemas at 0.14.0* |
| Reference conformance tests | `python tests/validate_contracts.py` | PASS - `CONTRACT_CONFORMANCE=PASS`, exit 0 — *still run, in CI, on every push* |
| Namespace identity | every `$id` asserted against `NAMESPACE_BASE` | PASS - 5/5 — *count is historical; still asserted, derived from `NAMESPACE.md` per `DR-6`* |
| Version consistency | `VERSION` matches the namespace base version segment | **NOT A CHECK. `DR-6` abolished this rule deliberately** — `VERSION` and the namespace segment are decoupled by design. At 0.14.0 they read `0.14.0` and `0.7.0` and that is correct. Recorded here only as what was claimed at 0.7.0 |
| Golden example conformance | `examples/` instances asserted against their schemas | PASS - 3/3 — *still 3, still asserted* |
| Conformance-level semantics | level-vs-control-decision rules, positive and negative | PASS — *still asserted* |
| Adoption identity enforcement | required fields, digest/version/date formats, unknown fields | PASS — *shape only at 0.7.0. The declared pin was compared against nothing until `SP048`/`SP049` (`DR-14`, closing `F7`)* |
| YAML parse | all YAML files | PASS — *still asserted* |
| Secret-pattern scan | private keys, cloud access keys, tokens | PASS - no matches — **this repository had no automated secret scanner until `DR-18`.** Whatever produced this row was not a repeatable control, and a "no matches" result from an unnamed method is not evidence |
| Manifest check | every payload path appears once and every digest matches | PASS — *still run, as `build_release.py --verify-manifest`, in CI* |
| Archive path check | relative POSIX paths, no traversal, no absolute paths | PASS — *historical; `scripts/verify_release.py` checks the manifest against the payload, integrity only* |

Environment for the recorded run: Python 3.14.3, `jsonschema` 4.26.0, `PyYAML`, `referencing`,
Windows 11. *One run, on one machine, at one version — which is the shape of the problem `DR-21`
describes.*

## Checks NOT performed by this package

These remain the responsibility of the receiving repository. **This section is still true** and is
not historical:

- dependency and vulnerability scanning against the receiving repository's lockfiles;
- cross-platform extraction testing on the receiving team's supported platforms;
- runtime enforcement of any contract — a schema file is not enforcement;
- independent validation, approval, risk acceptance, or release readiness.

## Building and verifying a release

*Commands corrected to be runnable; the 0.7.0 archive named in the original no longer exists.*

`MANIFEST.sha256` and the release archive are produced by `scripts/build_release.py`, which runs the
conformance tests first and **refuses to build** if they do not pass:

```bash
python scripts/build_release.py
```

A receiving team verifies an archive before adopting it — integrity only, which is all it claims:

```bash
python scripts/verify_release.py dist/surfaceplate-<version>.zip
```

## Outstanding

**This section is still true** and is cited by `F6` and `F8` in `org/FINDINGS.md`:

The ChatGPT Enterprise audit in `audit/CHATGPT_ENTERPRISE_AUDIT_PROMPT.md` has **not** been
performed for this release.

Findings F1-F4 recorded in `audit/PRE_AUDIT_FINDINGS_0.6.0.md` are remediated here, but that
pre-audit was performed by a coding agent at the maintainer's request. It was not independent, and
it does not discharge the audit gate.
