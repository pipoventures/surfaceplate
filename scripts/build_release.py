"""Build a pinned release archive.

Refuses to build unless the conformance tests pass, so a release archive cannot be
produced from a payload that fails its own contracts.

Usage:
    python scripts/build_release.py
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# install_standard.py moved into surfaceplate/ at ACT-019, along with the payload it locates.
sys.path.insert(0, str(ROOT / "surfaceplate"))
import install_standard  # noqa: E402  (needs the sys.path insert above)

DIST = ROOT / "dist"
MANIFEST = ROOT / "surfaceplate" / "MANIFEST.sha256"

# `.standards` holds this repository's OWN vendored copy of the standard, created when
# surfaceplate installs into itself for self-conformance (DR-13 item 0). Listed here as a
# directory because it also contains INSTALL.json, which the installer GENERATES and which
# is therefore not a payload entry — so `installed_paths()` below cannot know about it.
EXCLUDED_DIRS = {".git", "dist", "__pycache__", ".venv", ".ruff_cache", ".scratch", ".pytest_cache", ".standards"}
EXCLUDED_FILES = {"MANIFEST.sha256", ".gitignore"}


def version() -> str:
    return (ROOT / "surfaceplate" / "VERSION").read_text(encoding="utf-8").strip()


def installed_paths() -> set[str]:
    """Target-relative paths the installer writes into an adopting repository.

    DERIVED from install_standard.build_payload rather than restated here, so the two
    cannot drift apart — the same principle DR-6 established for the schema namespace and
    DR-9 for the organisation identifier. A hardcoded list would agree with the installer
    on the day it was written and silently stop agreeing afterwards.

    Why this exists: when surfaceplate installs into itself (DR-13 item 0), every file the
    installer writes is a byte-copy of content this repository already ships from source.
    43 files: 27 under `.standards/`, and 16 outside it — `.github/instructions/`,
    `.github/skills/`, `.github/workflows/standards-conformance.yml` and `.githooks/`, each
    copied from `standard/`. Packaging them would digest the same bytes twice under two
    names in one manifest.

    Excluding by PATH, not by name: `EXCLUDED_FILES` matches `rel.name` at any depth, so
    excluding "standards-conformance.yml" by name would also drop
    `standard/.github/workflows/standards-conformance.yml` — the source template adopters
    install FROM. That would break every adopter to tidy the publisher's manifest.

    This is a publisher-side build setting, not a conformance exemption (DR-16): no adopter
    runs build_release.py, and an adopter's own installed files are produced by their own
    install, never unpacked from our archive.
    """
    return set(install_standard.build_payload(ROOT / "surfaceplate"))


def _git_tracked_or_addable() -> set[str]:
    """Every path git considers part of this repository: tracked, or untracked-but-not-ignored
    (so a file created and not yet `git add`ed still enters a release built before commit, which
    is this project's own normal packet order - build the manifest, then stage, then commit).

    Found necessary rather than assumed: `payload_files()` used a pure filesystem walk, which
    swept up `.claude/scheduled_tasks.lock` - a Claude Code harness runtime artefact, excluded
    from this repository only via the machine-local `.git/info/exclude`, invisible to a walk that
    never asks git anything. The manifest then named a file that existed on the machine that built
    it and nowhere else - caught when CI, checking out the exact same commit, could not find it.
    `--exclude-standard` honours `.gitignore` *and* `.git/info/exclude` *and* the global excludes
    file, which is the same set a plain `git status` would call clean.
    """
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        check=True,
    )
    return {line for line in result.stdout.splitlines() if line}


def payload_files() -> list[Path]:
    installed = installed_paths()
    tracked_or_addable = _git_tracked_or_addable()
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if rel.name in EXCLUDED_FILES:
            continue
        if rel.as_posix() in installed:
            continue
        if rel.as_posix() not in tracked_or_addable:
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_conformance_tests() -> None:
    print("Running conformance tests before building...")
    for script, marker in (
        ("validate_contracts.py", "CONTRACT_CONFORMANCE=PASS"),
        ("test_install_and_check.py", "INSTALL_CONFORMANCE=PASS"),
    ):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tests" / script)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=ROOT,
        )
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        if result.returncode != 0 or marker not in result.stdout:
            raise SystemExit(
                f"REFUSING TO BUILD: {script} did not pass. "
                "A release archive must not be produced from a failing payload."
            )
    print("Conformance tests PASS.\n")


def write_manifest(files: list[Path], top: str) -> None:
    lines = [f"{sha256(f)}  {top}/{f.relative_to(ROOT).as_posix()}" for f in files]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {MANIFEST.name} with {len(lines)} payload entries.")


def build_zip(files: list[Path], top: str) -> Path:
    DIST.mkdir(exist_ok=True)
    archive = DIST / f"{top}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, f"{top}/{f.relative_to(ROOT).as_posix()}")
        # MANIFEST lives at surfaceplate/MANIFEST.sha256 on disk since ACT-019 moved the payload
        # under the package directory (DR-31) - the arcname below must match, via the same
        # relative_to(ROOT) every other payload file uses. Before that move this file sat at the
        # repository root, and the arcname was never updated when it moved: it kept writing
        # `{top}/MANIFEST.sha256` (the pre-move location) instead of `{top}/surfaceplate/
        # MANIFEST.sha256` (where install_standard.py's framework_anchor() has looked for it since
        # ACT-019). Found reinstalling from a real release archive during ACT-020's verification
        # cycle: framework_digest came back unverifiable (SP049) because the installer's --source
        # genuinely had no manifest at the path it checked. Not created by ACT-020 - see DR-32.
        zf.write(MANIFEST, f"{top}/{MANIFEST.relative_to(ROOT).as_posix()}")
    return archive


def verify_manifest() -> int:
    """Fail if MANIFEST.sha256 does not describe the current working tree.

    A manifest that has drifted from the payload is worse than none: it produces a
    verification pass that means nothing.
    """
    ver = version()
    top = f"surfaceplate-{ver}"
    if not MANIFEST.is_file():
        print("FAIL: MANIFEST.sha256 does not exist.")
        return 1

    recorded: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, _, name = line.partition("  ")
        recorded[name] = digest

    actual = {
        f"{top}/{f.relative_to(ROOT).as_posix()}": sha256(f) for f in payload_files()
    }

    missing = sorted(set(recorded) - set(actual))
    added = sorted(set(actual) - set(recorded))
    changed = sorted(k for k in set(recorded) & set(actual) if recorded[k] != actual[k])

    if not (missing or added or changed):
        print(f"MANIFEST_CURRENT=PASS ({len(actual)} files)")
        return 0

    print("MANIFEST_CURRENT=FAIL - the manifest does not match the working tree.")
    for label, items in (("in manifest but not on disk", missing),
                         ("on disk but not in manifest", added),
                         ("digest changed", changed)):
        for item in items:
            print(f"  {label}: {item}")
    print("\nRun: python scripts/build_release.py")
    return 1


def main() -> None:
    if "--verify-manifest" in sys.argv:
        raise SystemExit(verify_manifest())

    run_conformance_tests()
    ver = version()
    top = f"surfaceplate-{ver}"
    files = payload_files()
    write_manifest(files, top)
    archive = build_zip(files, top)
    digest = sha256(archive)

    print(f"\nRelease:        {top}")
    print(f"Payload files:  {len(files)} (+1 manifest = {len(files) + 1})")
    print(f"Archive:        {archive.relative_to(ROOT).as_posix()}")
    print(f"ZIP SHA-256:    {digest}")
    print(
        "\nRecord this digest in the adoption decision record and in each adopting "
        "application's\napplication-profile.yaml under adoption.framework_digest.\n"
        "\nThis archive is NOT approved, independently validated, or released by being built."
    )


if __name__ == "__main__":
    main()
