#!/usr/bin/env python3
"""Check the repository's organisation identifiers against their declared source of truth.

No test framework required; run it directly:

    python tests/check_identifiers.py
    python tests/check_identifiers.py --root /path/to/another/tree

This is the derived-identifier control recorded in DR-9. It extends the principle DR-6
already established for the schema namespace: a value is DECLARED once, in ORGANISATION.md,
and DERIVED here. This module holds no literal copy of the organisation slug, the URN
authority, or the legal name -- only the grammar a declaration must satisfy. Every parse
failure below raises rather than falling back to an assumption, for the same reason
tests/validate_contracts.py's read_declared_namespace() does: a source of truth this module
cannot parse is not something to guess about.

It is deliberately standalone, not folded into tests/validate_contracts.py or wired into
scripts/build_release.py's build gate. That gate is the only sanctioned way to regenerate
MANIFEST.sha256; a failing check inside it would make the manifest un-regenerable for as
long as the underlying finding stands, recreating the exact drift this repository has
separately had to repair. This check is full strength -- it fails today, honestly, against
the current tree -- only its wiring into the release gate is deferred.

One accepted limitation: this is a text scan, not a semantic parser. It cannot tell a live
instruction (a clone command someone will actually run) from a quoted historical fact (a
decision record citing the wrong spelling as evidence of itself). A decision record's own
evidence table will therefore register as an occurrence alongside the defect it describes.
That is not a second defect; it is the same one, quoted. See DR-9.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_release  # noqa: E402  (needs the sys.path insert above)

ORG_DOC_NAME = "ORGANISATION.md"

TEXT_BLOCK = re.compile(r"^```text\n(.*?)\n```$", re.MULTILINE | re.DOTALL)
SLUG_GRAMMAR = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# Rule 1: every GitHub URL owner must equal the declared github-org.
#
# Anchored on `//github.com/` rather than a bare `github.com/`. The unanchored
# form matched any host ENDING in github.com -- `docs.github.com/en/...` scored
# as an organisation named `en`, and `raw.githubusercontent.com` would too. That
# is a false positive against this repository's own documentation links, and it
# was reported as a real identifier drift for as long as the rule existed.
GITHUB_URL = re.compile(r"//github\.com/([A-Za-z0-9._-]+)/")

# Rule 2: every URN authority segment must equal the declared urn-authority.
URN_AUTHORITY = re.compile(r"\burn:([a-z0-9][a-z0-9-]*):")

# Rule 3: every token sharing this stem must be a declared form or a declared exclusion.
# The stem itself is not spelled out in this comment -- see ORGANISATION.md's "Declared
# identifiers" section for what it is; naming it here would make this file's own source an
# occurrence of the thing it is checking for.
#
# No "." in the continuation class: a trailing sentence period is not part of an
# identifier, and an email domain (e.g. the maintainer's) still tokenises correctly without
# it -- it just yields the slug ahead of the dot, which either equals a declared identifier
# or does not, on its own merits.
STEM = "[Pp]" + "ipo"
ORG_TOKEN = re.compile(STEM + r"[A-Za-z0-9_-]*")

FAILURES: list[str] = []
PASSES = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSES
    if condition:
        PASSES += 1
    else:
        FAILURES.append(f"{name}: {detail}")


def read_declared_organisation(
    root: Path,
) -> tuple[dict[str, str], set[str], set[tuple[str, str]], set[str], set[str]]:
    """Return (declared values, declared exclusions, quoted-evidence pairs) from ORGANISATION.md.

    ORGANISATION.md states the three identifiers twice -- as a placeholder pattern and as
    concrete current values -- exactly as NAMESPACE.md states the schema namespace, plus a
    third block naming tokens that share the stem but are not the organisation, plus a
    fourth naming the specific places a record QUOTES a drift it exists to document, plus a
    fifth naming OTHER PEOPLE'S organisations that legitimately appear in GitHub URLs here.
    All five are required; a document that cannot be parsed this way cannot be derived from.
    """
    doc = root / ORG_DOC_NAME
    if not doc.is_file():
        raise AssertionError(f"{ORG_DOC_NAME} is missing; the organisation identifier is undeclared")

    text = doc.read_text(encoding="utf-8")
    blocks = [b.strip() for b in TEXT_BLOCK.findall(text)]
    if len(blocks) != 5:
        raise AssertionError(
            f"{ORG_DOC_NAME} must declare exactly five ```text blocks - the placeholder "
            f"pattern, the current values, the known non-matches, the quoted-evidence "
            f"pairs, and the third-party organisations - but declares {len(blocks)}. The "
            f"organisation identifier cannot be derived from it."
        )
    pattern, current, exclusions_block, quoted_block, third_party_block = blocks

    if "<" not in pattern:
        raise AssertionError(
            f"{ORG_DOC_NAME}: the first ```text block should be the placeholder pattern, "
            f"carrying <placeholder> segments, but is '{pattern}'"
        )

    required_keys = {"github-org", "urn-authority", "legal-name"}

    def parse_kv(block: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in block.splitlines():
            if not line.strip():
                continue
            if ":" not in line:
                raise AssertionError(
                    f"{ORG_DOC_NAME}: expected 'key: value' lines in its declaration "
                    f"blocks, found '{line}'"
                )
            key, _, value = line.partition(":")
            values[key.strip()] = value.strip()
        return values

    pattern_keys = set(parse_kv(pattern))
    if pattern_keys != required_keys:
        raise AssertionError(
            f"{ORG_DOC_NAME}: the placeholder pattern declares keys {sorted(pattern_keys)}, "
            f"expected exactly {sorted(required_keys)}"
        )

    declared = parse_kv(current)
    missing = required_keys - set(declared)
    if missing:
        raise AssertionError(
            f"{ORG_DOC_NAME}: the current-values block is missing {sorted(missing)} - see "
            f"the 'Declared identifiers' section"
        )
    for key in ("github-org", "urn-authority"):
        if "<" in declared[key] or not SLUG_GRAMMAR.match(declared[key]):
            raise AssertionError(
                f"{ORG_DOC_NAME} declares {key}='{declared[key]}', which is not a bare "
                f"lowercase slug - see the 'Declared identifiers' section"
            )
    if "<" in declared["legal-name"] or not declared["legal-name"]:
        raise AssertionError(
            f"{ORG_DOC_NAME} declares an empty or unfilled legal-name - see the 'Declared "
            f"identifiers' section"
        )

    exclusions = {line.strip() for line in exclusions_block.splitlines() if line.strip()}
    if not exclusions:
        raise AssertionError(
            f"{ORG_DOC_NAME}'s 'Known non-matches' block declares no exclusions - if there "
            f"are genuinely none, this block should not exist as an empty ```text fence"
        )

    # Fourth block: `path :: token` pairs. Scoped to BOTH a file and a token, never
    # to a file alone. A record documenting a drift must be able to quote it -- but
    # muting the whole file would also mute a DIFFERENT, real drift appearing in it
    # later, which is the mistake this pairing exists to avoid.
    quoted: set[tuple[str, str]] = set()
    for line in quoted_block.splitlines():
        line = line.strip()
        if not line:
            continue
        if "::" not in line:
            raise AssertionError(
                f"{ORG_DOC_NAME}: the quoted-evidence block takes 'path :: token' lines, "
                f"found '{line}'"
            )
        p, _, tok = line.partition("::")
        p, tok = p.strip(), tok.strip()
        if not p or not tok:
            raise AssertionError(
                f"{ORG_DOC_NAME}: '{line}' must name both a path and a token"
            )
        if not (root / p).is_file():
            raise AssertionError(
                f"{ORG_DOC_NAME}: the quoted-evidence block names '{p}', which does not "
                f"exist. A stale exemption silently widens what this check tolerates."
            )
        quoted.add((p, tok))

    # Fifth block: other people's organisations. Not paired to a path, because a third
    # party is legitimately referenced anywhere; see the reasoning in ORGANISATION.md.
    # This is a declaration that an owner IS somebody else's organisation, not a mute
    # list -- rule 1 below still asks the question of every other owner it finds.
    third_party = {line.strip() for line in third_party_block.splitlines() if line.strip()}
    if not third_party:
        raise AssertionError(
            f"{ORG_DOC_NAME}'s 'Third-party organisations' block declares none - if there "
            f"are genuinely none, this block should not exist as an empty ```text fence"
        )

    # The declaration blocks are this check's source of truth. Scanning them for drift
    # is circular: the quoted-evidence block must name the very tokens it exempts, so it
    # reports itself. Their lines are excluded -- ORGANISATION.md's PROSE is still
    # scanned, so a wrong spelling in the surrounding text is still caught.
    declaration_lines = {
        ln.strip() for b in blocks for ln in b.splitlines() if ln.strip()
    }

    return declared, exclusions, quoted, declaration_lines, third_party


def payload_files(root: Path) -> list[Path]:
    """The same payload build_release.py would package, rooted at an arbitrary tree.

    Reuses build_release.EXCLUDED_DIRS / EXCLUDED_FILES rather than restating them, so the
    two scripts cannot silently disagree about what counts as the shipped tree.
    """
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in build_release.EXCLUDED_DIRS for part in rel.parts):
            continue
        if rel.name in build_release.EXCLUDED_FILES:
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="tree to check (default: this repository)",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    declared, exclusions, quoted, declaration_lines, third_party = read_declared_organisation(root)
    declared_tokens = set(declared.values()) | exclusions

    files = payload_files(root)
    file_texts = {f: read_text(f) for f in files}
    all_text = "\n".join(t for t in file_texts.values() if t is not None)

    # Rule 1 -- GitHub URL owners.
    for path, text in file_texts.items():
        if text is None:
            continue
        rel = path.relative_to(root).as_posix()
        for lineno, line in enumerate(text.splitlines(), start=1):
            if rel == ORG_DOC_NAME and line.strip() in declaration_lines:
                continue
            for match in GITHUB_URL.finditer(line):
                owner = match.group(1)
                if (rel, owner) in quoted:
                    continue
                if owner in third_party:
                    continue
                check(
                    f"github-url:{rel}:{lineno}",
                    owner == declared["github-org"],
                    f"github.com/{owner}/ does not match declared github-org "
                    f"'{declared['github-org']}'",
                )

    # Rule 2 -- URN authority segments.
    for path, text in file_texts.items():
        if text is None:
            continue
        rel = path.relative_to(root).as_posix()
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in URN_AUTHORITY.finditer(line):
                authority = match.group(1)
                check(
                    f"urn-authority:{rel}:{lineno}",
                    authority == declared["urn-authority"],
                    f"urn:{authority}: does not match declared urn-authority "
                    f"'{declared['urn-authority']}'",
                )

    # Rule 3 -- no undeclared token sharing the organisation's stem.
    for path, text in file_texts.items():
        if text is None:
            continue
        rel = path.relative_to(root).as_posix()
        for lineno, line in enumerate(text.splitlines(), start=1):
            if rel == ORG_DOC_NAME and line.strip() in declaration_lines:
                continue
            for match in ORG_TOKEN.finditer(line):
                token = match.group(0)
                if (rel, token) in quoted:
                    continue
                check(
                    f"undeclared-token:{rel}:{lineno}:{token}",
                    token in declared_tokens,
                    f"'{token}' is not a declared identifier or a declared exclusion in "
                    f"{ORG_DOC_NAME}",
                )

    # Rule 4 -- the declaration itself must not be dead: the legal name must appear
    # somewhere in the payload, or the declaration is describing nothing.
    check(
        "legal-name-present",
        declared["legal-name"] in all_text,
        f"declared legal-name '{declared['legal-name']}' does not appear anywhere in the "
        f"checked tree",
    )

    if FAILURES:
        print(f"IDENTIFIER_CONFORMANCE=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"IDENTIFIER_CONFORMANCE=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
