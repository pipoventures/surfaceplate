#!/usr/bin/env python3
"""Fail if this repository's vendored copy has drifted from source.

This is the remedy for F12, and it is publisher-only by nature. An adopting repository holds
exactly one copy of the standard and has no source tree to compare against; surfaceplate,
having installed into itself, holds both. That is the whole of the asymmetry DR-11's
integrity guarantee did not consider.

WHY THE EXISTING CONTROLS DO NOT COVER THIS, since each looks as though it might:

- `check_conformance.py`'s integrity check (SP004/SP005) digests `.standards/<file>` against
  `.standards/INSTALL.json`. Both sides of that comparison were written by the same install.
  Editing `scripts/check_conformance.py` afterwards leaves the vendored digest matching its
  vendored file perfectly, and the check stays silent. It answers "has the installed copy been
  tampered with", never "is the installed copy current".
- `build_release.py --verify-manifest` is the near miss and is worth naming precisely. After
  self-install the source and vendored files are separate manifest entries, so editing source
  DOES make the manifest stale - but the remedy is to regenerate it, after which it records
  two different digests for two files and passes. It detects "manifest stale", never "the
  copies differ", and by design cannot become a drift detector. It MASKS the divergence.

WHAT DRIFT ACTUALLY COSTS, in one sentence: the hook and the installed workflow both resolve
`.standards/check_conformance.py` by path, so a finding code added to source can be violated
here and reported as PASS by the vendored checker that cannot emit it.

Observed twice on 2026-08-31 while implementing DR-18: `schemas/application-profile.schema.yaml`
was edited and the checker rejected the new profile field as unknown, because it was reading
the stale vendored schema. Nothing reported drift; the symptom was a confusing SP016.

Usage:
    python tests/check_vendored_current.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "surfaceplate"))

import install_standard  # noqa: E402  (needs the sys.path insert above)

VENDOR_DIR = install_standard.VENDOR_DIR


def main() -> int:
    installed_record = ROOT / f"{VENDOR_DIR}/INSTALL.json"
    if not installed_record.is_file():
        print(f"VENDORED_CURRENT=FAIL - {VENDOR_DIR}/INSTALL.json is absent.")
        print()
        print("This repository publishes the standard and is required to have installed it")
        print("into itself (DR-13 item 0). A missing install record is not 'nothing to")
        print("compare' - it means self-conformance is gone.")
        return 1

    # Derived from the installer rather than restated, so the set compared here cannot
    # drift from the set actually installed. Same principle as DR-6.
    payload = install_standard.build_payload(ROOT / "surfaceplate")

    missing: list[str] = []
    diverged: list[str] = []

    # `DR-45`. `.standards/MANIFEST.sha256` is compared by a DIFFERENT question, and is skipped
    # here rather than exempted from checking.
    #
    # This check asks "is the vendored copy current with source?". For every other payload file that
    # is answerable. For the manifest it is not, in THIS repository: building the manifest is what
    # happens after an install, so the installed copy necessarily lags the source by one build - the
    # same self-reference `adoption.framework_digest` has always carried, now visible on a second
    # file. In an adopting repository the two agree; only the repository that installs into itself
    # sees the lag.
    #
    # The right question for this file is "does it hash to the anchor recorded for it?", and
    # `SP049` now asks exactly that, on every run, in every adopting repository - which is stronger
    # than a text comparison, because it is the check that would catch the file being edited. This
    # is a division of labour, not a hole: the file is checked, by the control that owns it.
    OWNED_BY_SP049 = {".standards/MANIFEST.sha256"}

    for rel, src in sorted(payload.items()):
        if rel in OWNED_BY_SP049:
            continue
        installed = ROOT / rel
        if not installed.is_file():
            missing.append(rel)
            continue
        # Compared after the installer's own normalisation, because that is the transform
        # the installer applies on write. Comparing raw bytes would report every file as
        # diverged on a CRLF checkout - a check that fails for a reason unrelated to the
        # thing it is about is worse than no check.
        source_text = install_standard.payload_text(src)
        installed_text = install_standard.normalise(installed.read_text(encoding="utf-8"))
        if source_text != installed_text:
            diverged.append(rel)

    if not missing and not diverged:
        # The count is reported on success so that "everything matched" is distinguishable
        # from "nothing was compared" - the defect recorded as F3 and fixed at 0.13.0.
        compared = len(payload) - len(OWNED_BY_SP049 & set(payload))
        print(f"VENDORED_CURRENT=PASS  ({compared} files compared, "
              f"{len(OWNED_BY_SP049 & set(payload))} checked by SP049 instead)")
        return 0

    print("VENDORED_CURRENT=FAIL - the installed copy is not current.")
    print()
    for rel in missing:
        print(f"  missing from the working tree: {rel}")
    for rel in diverged:
        cls = install_standard.classify(rel)
        note = " <-- this is the checker itself" if rel.endswith("check_conformance.py") else ""
        print(f"  source and installed differ [{cls}]: {rel}{note}")
    print()
    print("Re-run the installer against this repository so the vendored copy matches source.")
    print("Until then the pre-commit hook and the installed workflow are running code that")
    print("is not the code under development, and a PASS from either answers a question")
    print("about a checker that no longer exists.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
