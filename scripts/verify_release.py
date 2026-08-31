"""Verify a received release archive before adopting it.

Checks archive path safety, manifest completeness, and every payload digest. Prints the
archive SHA-256 for recording in the adoption decision record.

A digest proves integrity only once the digest itself is trusted. It does not prove
authenticity or the absence of malicious content.

Usage:
    python scripts/verify_release.py <path-to-zip>
"""
from __future__ import annotations

import hashlib
import sys
import zipfile
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2

    archive = Path(argv[1])
    if not archive.is_file():
        print(f"FAIL - not a file: {archive}")
        return 1

    problems: list[str] = []

    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()

        # Path safety
        for name in names:
            if name.startswith("/") or ".." in Path(name).parts or "\\" in name:
                problems.append(f"unsafe archive path: {name}")

        manifest_names = [n for n in names if n.endswith("MANIFEST.sha256")]
        if len(manifest_names) != 1:
            print(f"FAIL - expected exactly one manifest, found {len(manifest_names)}")
            return 1
        manifest_name = manifest_names[0]

        manifest_text = zf.read(manifest_name).decode("utf-8")
        entries: dict[str, str] = {}
        for line in manifest_text.splitlines():
            line = line.strip()
            if not line:
                continue
            digest, _, path = line.partition("  ")
            if not path:
                problems.append(f"unparsable manifest line: {line}")
                continue
            if path in entries:
                problems.append(f"duplicate manifest entry: {path}")
            entries[path] = digest.lower()

        payload = [n for n in names if n != manifest_name and not n.endswith("/")]

        for path, expected in entries.items():
            if path not in names:
                problems.append(f"manifest lists a file missing from the archive: {path}")
                continue
            actual = sha256_bytes(zf.read(path))
            if actual != expected:
                problems.append(f"digest mismatch: {path}")

        for name in payload:
            if name not in entries:
                problems.append(f"archive contains a file absent from the manifest: {name}")

    print(f"Archive:        {archive.name}")
    print(f"ZIP SHA-256:    {sha256_file(archive)}")
    print(f"Payload files:  {len(payload)}")
    print(f"Manifest lines: {len(entries)}")

    if problems:
        print(f"\nRESULT: FAIL - {len(problems)} problem(s)")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("\nRESULT: PASS - all payload digests match and no unlisted files are present.")
    print(
        "\nIntegrity only. This does NOT establish authenticity, approval, independent\n"
        "validation, or fitness for your application."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
