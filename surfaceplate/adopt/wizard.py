"""Orchestration: collect answers, assemble, verify, and only then write.

`run()` is the one function anything outside this package should call. It is deliberately thin -
an `Interview` collects the answers, `sections.py` turns them into a profile, and this module's own
job is narrow: hold the pieces together, verify what they produced before it reaches disk, and
guarantee that a cancelled run leaves the repository untouched.

**Verification is never delegated to the interface (`DR-36`).** `_verify` runs twice: once through
the `preview` closure, so the review screen can show a `WriteRefused` as a message instead of a
traceback, and again here after the interview returns, before anything is written. Both passes are
pure and deterministic, so the second costs nothing - and it means a defect in the interface cannot
put an unverified profile on disk, however convincing the screen looked.
"""

from __future__ import annotations

import json
from pathlib import Path

from surfaceplate.adopt import render, scaffold, sections
from surfaceplate.adopt.interview import DRAFT_FORMAT, Cancelled, DraftInfo, Interview

PROFILE_PATH = "governance/application-profile.yaml"
INSTALL_RECORD = ".standards/INSTALL.json"

# DR-35: basic resumability. A name distinct from anything the standard itself ships (never
# `.standards/...`, never `governance/...`) so it can never be mistaken for payload, and a leading
# dot so it reads as scratch state rather than a file this framework is asking anyone to commit.
# This lives only in an ADOPTING repository's working tree - never in surfaceplate's own source
# tree - so it has no interaction with this project's own release manifest.
DRAFT_FILENAME = ".surfaceplate-adopt-draft.json"

# `ACT-033`. Where the interface parks the scaffold files a human approved, on its way back here.
# Deliberately not a section name: everything else in the collected state is a section of the
# profile, and `sections.build_profile` walks it. A list of paths is an instruction to this module,
# not an answer, and it is popped before the profile is assembled so it can never be mistaken for
# one.
SCAFFOLD_KEY = "__scaffold__"


class Written:
    """What a completed run put on disk: the profile, and any artefacts it was asked to create.

    `run` used to return a single `Path`, and the caller printed it. It now returns both, because a
    run that creates files in someone's repository and reports only one of them is the kind of
    understatement this project spends its time removing from other people's tools.
    """

    def __init__(self, profile: Path, created: list[Path]) -> None:
        self.profile = profile
        self.created = created

    # `cli.py` and four packets of tests used this return value as a `Path`. Enumerating the few
    # methods they happened to call was the first attempt and it was wrong twice over - `.is_file`
    # was missing, and the next caller would have found the next gap. Delegating everything the
    # wrapper does not define keeps every existing use working and confines this change to the one
    # thing it adds.
    def __getattr__(self, name: str):
        return getattr(self.profile, name)

    def __fspath__(self) -> str:
        return str(self.profile)

    def __eq__(self, other) -> bool:
        return self.profile == getattr(other, "profile", other)

    def __str__(self) -> str:
        return str(self.profile)


class NotInstalled(Exception):
    """The standard has not been installed here yet - `adopt` has nothing to attach a profile to."""


class AlreadyAdopted(Exception):
    """A real (non-template) profile already exists - `adopt` will not overwrite it silently."""


class WriteRefused(Exception):
    """The assembled profile failed its own verification. Nothing was written. Carries `detail`."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


def _read_install_record(repo: Path) -> dict:
    path = repo / INSTALL_RECORD
    if not path.is_file():
        raise NotInstalled(
            f"{INSTALL_RECORD} does not exist. Run `surfaceplate install` first - `adopt` fills in "
            "the profile the installer creates; it does not install the standard itself."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _refuse_if_already_adopted(repo: Path) -> None:
    """Refuses only on a REAL profile, not the untouched template.

    The installer already never overwrites an existing profile (`install_standard.py`'s own rule);
    this is the same protection applied one step later, to the wizard that is much more likely to
    be run against a repository someone has already been working in.
    """
    path = repo / PROFILE_PATH
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "replace-me" in text:
        return  # the untouched template - fair game
    raise AlreadyAdopted(
        f"{PROFILE_PATH} already exists and does not look like the untouched template. "
        "Edit it directly, or move it aside before running `adopt` again."
    )


def _verify(profile: dict, rendered: str, repo: Path) -> None:
    """Round-trips the rendered text and validates it against the schema. Raises `WriteRefused`
    with the exact problem rather than letting a malformed profile reach disk."""
    import yaml

    try:
        reparsed = yaml.safe_load(rendered)
    except yaml.YAMLError as exc:
        raise WriteRefused(f"the rendered YAML does not parse: {exc}") from None

    if reparsed != profile:
        # A structural diff a human could act on, not just "they differ".
        import difflib

        left = json.dumps(profile, indent=2, sort_keys=True, default=str).splitlines()
        right = json.dumps(reparsed, indent=2, sort_keys=True, default=str).splitlines()
        diff = "\n".join(difflib.unified_diff(left, right, "assembled", "rendered", lineterm=""))
        raise WriteRefused(
            "the rendered YAML does not round-trip to what was assembled - the renderer has a "
            f"bug, and nothing is written while that is true:\n{diff}"
        )

    schema_path = repo / ".standards" / "schemas" / "application-profile.schema.yaml"
    if not schema_path.is_file():
        raise WriteRefused(f"{schema_path} is missing - cannot validate before writing.")
    import jsonschema

    schema = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(reparsed), key=lambda e: list(e.path))
    if errors:
        detail = "; ".join(
            f"{'/'.join(str(p) for p in e.path) or '(root)'}: {e.message}" for e in errors[:8]
        )
        raise WriteRefused(f"the assembled profile does not satisfy its own schema: {detail}")

    from surfaceplate import check_conformance

    hits = [
        path_str
        for path_str, value in _walk_strings(reparsed)
        if check_conformance.PLACEHOLDER_PATTERN.search(value)
    ]
    if hits:
        raise WriteRefused(
            "an answer still contains a template placeholder token (TBD/TODO/replace-me/…) at: "
            + ", ".join(hits)
        )


def _draft_path(repo: Path) -> Path:
    return repo / DRAFT_FILENAME


def _save_draft(repo: Path, record: dict, state: dict) -> None:
    """Called after every section completes - a late failure loses at most the section in
    progress, not the whole run. `framework_version`/`framework_digest` travel with the draft so a
    later resume can tell whether the install underneath it has changed since, flagged rather than
    silently trusted; `format` states the shape of `sections` so a draft written by a different
    shape of this wizard is recognised rather than misread (`DRAFT_FORMAT`)."""
    payload = {
        "format": DRAFT_FORMAT,
        "framework_version": record.get("standard_version", ""),
        "framework_digest": record.get("framework_digest", ""),
        "sections": state,
    }
    _draft_path(repo).write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _load_draft(repo: Path) -> dict | None:
    path = _draft_path(repo)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # A corrupt or unreadable draft is treated as no draft, never as a reason to fail the run
        # it would otherwise only have helped.
        return None


def _clear_draft(repo: Path) -> None:
    _draft_path(repo).unlink(missing_ok=True)


def _resume_or_start(repo: Path, record: dict, interview: Interview) -> dict:
    """Never resumes silently. A version/digest mismatch is flagged - shown to the human, who
    still decides - rather than either trusted or refused outright.

    A draft in an older `format` is a different case and is not offered at all: Phase 1 drafts hold
    built profile fragments where these hold raw answers, so resuming one as the other would produce
    a confidently wrong profile rather than an error. It is left in place rather than deleted -
    this run's first completed section overwrites it - so nothing is destroyed to tidy up.
    """
    draft = _load_draft(repo)
    if draft is None:
        return {}

    if draft.get("format") != DRAFT_FORMAT:
        return {}

    matches = draft.get("framework_version") == record.get(
        "standard_version", ""
    ) and draft.get("framework_digest") == record.get("framework_digest", "")

    info = DraftInfo(
        sections=tuple(draft.get("sections", {})),
        framework_version=str(draft.get("framework_version", "")),
        framework_digest=str(draft.get("framework_digest", "")),
        matches=matches,
    )
    if not interview.confirm_resume(info):
        _clear_draft(repo)
        return {}
    return dict(draft.get("sections", {}))


def _walk_strings(node: object, path: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if isinstance(node, dict):
        for k, v in node.items():
            out.extend(_walk_strings(v, f"{path}.{k}" if path else str(k)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(_walk_strings(v, f"{path}[{i}]"))
    elif isinstance(node, str):
        out.append((path, node))
    return out


def assemble(state: dict, record: dict) -> dict:
    """The profile a set of answers produces. Pure, and shared by the preview and the real write so
    the thing reviewed on screen is assembled by the same code as the thing written to disk."""
    return sections.build_profile(
        state,
        framework_version=record.get("standard_version", ""),
        framework_digest=record.get("framework_digest", ""),
    )


def run(repo: Path, interview: Interview) -> Path:
    """Runs the whole wizard. Returns the path written. Raises `Cancelled`, `NotInstalled`,
    `AlreadyAdopted`, or `WriteRefused` - every one of them leaves the repository untouched, except
    that `Cancelled` (and any other failure) may leave a resumable draft behind - see
    `_save_draft`. A completed write clears it (below)."""
    _refuse_if_already_adopted(repo)
    record = _read_install_record(repo)

    state: dict = _resume_or_start(repo, record, interview)

    def on_section_complete(name: str, answers: dict) -> None:
        state[name] = answers
        _save_draft(repo, record, state)

    def preview(current: dict) -> str:
        """Assemble, render and verify without writing - what the review screen shows.

        A `WriteRefused` raised here surfaces in the interface as a message the human can act on.
        It is deliberately NOT the last word: `run` verifies again below before writing, so the
        interface cannot put an unverified profile on disk however this closure behaved.
        """
        profile = assemble(current, record)
        rendered = render.render_profile(profile)
        _verify(profile, rendered, repo)
        return rendered

    state = interview.collect(
        repo=repo,
        resumed=state,
        on_section_complete=on_section_complete,
        preview=preview,
    )

    # `ACT-033`. Files the adopter approved on the scaffold screen, carried out of band under a key
    # `assemble` never sees: everything else in `state` is a section of the profile, and putting a
    # list of paths in there would put it in front of the provenance walk as though it were an
    # answer. Popped before `assemble`, so a profile is built from answers only.
    accepted = state.pop(SCAFFOLD_KEY, [])

    profile = assemble(state, record)
    rendered = render.render_profile(profile)
    _verify(profile, rendered, repo)

    # Written BEFORE the profile, and only once the profile is known to render and verify. A
    # profile naming an artefact that does not exist fails `SP032` on the next run, so if anything
    # here is going to fail it should fail before the profile claims the artefact is there.
    created = scaffold.write(repo, accepted)

    target = repo / PROFILE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered, encoding="utf-8", newline="\n")
    _clear_draft(repo)  # a completed run leaves no draft behind - it exists only to protect one
    return Written(profile=target, created=created)
