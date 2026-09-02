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

from surfaceplate import about, install_standard
from surfaceplate.adopt import flow as _flow
from surfaceplate.adopt import provenance, render, scaffold, sections
from surfaceplate.adopt.interview import DRAFT_FORMAT, Cancelled, DraftInfo, Interview

PROFILE_PATH = "governance/application-profile.yaml"
INSTALL_RECORD = ".standards/INSTALL.json"

# `DR-49` (3): adoption without a terminal. `--propose` writes these two and never the profile;
# `--answers` replays the second once a human has completed every `needs-human` line.
PROPOSED_PATH = "governance/application-profile.proposed.yaml"
ANSWERS_PATH = "governance/application-profile.answers.yaml"
NEEDS_HUMAN = "needs-human"
ANSWERS_FORMAT = 1

# DR-35: basic resumability. A name distinct from anything the standard itself ships (never
# `.standards/...`, never `governance/...`) so it can never be mistaken for payload, and a leading
# dot so it reads as scratch state rather than a file this framework is asking anyone to commit.
# This lives only in an ADOPTING repository's working tree - never in surfaceplate's own source
# tree - so it has no interaction with this project's own release manifest.
DRAFT_FILENAME = ".standards/adopt-draft.json"
# Where drafts lived before `DR-50` (3): untracked at the root, with nothing ignoring it, and
# gitignoring it would have meant the installer editing an adopter-owned file. A draft found here
# is offered once and moved.
LEGACY_DRAFT_FILENAME = ".surfaceplate-adopt-draft.json"

# `ACT-033`. Where the interface parks the scaffold files a human approved, on its way back here.
# Deliberately not a section name: everything else in the collected state is a section of the
# profile, and `sections.build_profile` walks it. A list of paths is an instruction to this module,
# not an answer, and it is popped before the profile is assembled so it can never be mistaken for
# one.
SCAFFOLD_KEY = "__scaffold__"  # historical: `Flow.accepted_scaffold` carries offers now


class Written:
    """What a completed run put on disk: the profile, and any artefacts it was asked to create.

    `run` used to return a single `Path`, and the caller printed it. It now returns both, because a
    run that creates files in someone's repository and reports only one of them is the kind of
    understatement this project spends its time removing from other people's tools.
    """

    def __init__(self, profile: Path, created: list[Path], problems: list[str] | None = None) -> None:
        self.profile = profile
        self.created = created
        self.problems = problems or []

    # `cli.py` and four packets of tests used this return value as a `Path`. Enumerating the few
    # methods they happened to call was the first attempt and it was wrong twice over - `.is_file`
    # was missing, and the next caller would have found the next gap.
    #
    # **This is not a `Path` and does not claim to be.** Attribute access delegates; operators do
    # not, so `written / "sub"` is a `TypeError` where `written.parent` works. That asymmetry is
    # stated rather than papered over: the wrapper exists so existing ATTRIBUTE use keeps working,
    # and anything needing a real path should take `.profile`.
    def __getattr__(self, name: str):
        # Guarded against its own delegation target. Without this, anything that probes an
        # attribute BEFORE `__init__` has run - `pickle` looking for `__setstate__` is the usual
        # one - recurses until the stack ends, because looking up `self.profile` re-enters here.
        if name.startswith("__") or name == "profile":
            raise AttributeError(name)
        return getattr(self.profile, name)

    def __fspath__(self) -> str:
        return str(self.profile)

    def __eq__(self, other) -> bool:
        return self.profile == getattr(other, "profile", other)

    # Defining `__eq__` alone sets `__hash__ = None`, so this became unhashable where it used to be
    # a `Path`. Any caller putting the result in a set or a dict key would have met a `TypeError`
    # for a change that was supposed to be additive.
    def __hash__(self) -> int:
        return hash(self.profile)

    def __str__(self) -> str:
        return str(self.profile)


class NotInstalled(Exception):
    """The standard has not been installed here yet - `adopt` has nothing to attach a profile to."""


class AlreadyAdopted(Exception):
    """A real (non-template) profile already exists - `adopt` will not overwrite it silently."""


class InstallMismatch(Exception):
    """The installed copy of the standard is not the one this tool ships (`F78`, `DR-51` (1)).

    The wizard validates against the schema installed in the repository, because that is the copy
    the repository's own checker reads; a profile written by a newer tool against an older install
    fails at the review in the validator's words. So the comparison is made before the first
    question, and the message carries the command that resolves it.
    """

    def __init__(self, repo: Path, record: dict) -> None:
        installed_version = str(record.get("standard_version", "") or "unknown")
        installed_anchor = str(record.get("framework_digest", "") or "")
        hooks_declined = install_standard.HOOK_TARGET not in (record.get("files") or {})
        self.command = about.upgrade_command(repo, no_hooks=hooks_declined)
        super().__init__(
            f"{repo.name} has {about.NAME} {installed_version} ({about.short(installed_anchor)}) "
            f"installed; this tool is {about.version()} ({about.short(about.anchor())}). "
            "Upgrade the installation first, so the profile this tool writes matches the checker "
            f"that will read it:\n\n    {self.command}\n\n"
            "Nothing was asked and nothing was written."
        )


def _refuse_if_mismatched(repo: Path, record: dict) -> None:
    if str(record.get("framework_digest", "")) != about.anchor():
        raise InstallMismatch(repo, record)


class NeedsHuman(Exception):
    """An answers record still carries `needs-human` lines - nothing is written until a human
    has completed them. Carries the keys, so the message says which."""

    def __init__(self, keys: list[str]) -> None:
        shown = ", ".join(keys[:6]) + (f" (and {len(keys) - 6} more)" if len(keys) > 6 else "")
        super().__init__(
            f"{len(keys)} line(s) in the answers record still say {NEEDS_HUMAN!r}: {shown}. "
            "Complete them - they are the decisions only a human can make - and run --answers again."
        )
        self.keys = keys


class Proposed:
    """What `propose` wrote: the answers record, and the preview profile where a level was given."""

    def __init__(self, answers: Path, proposed: Path | None) -> None:
        self.answers = answers
        self.proposed = proposed

    def __str__(self) -> str:
        return f"{self.answers}" + (f" and {self.proposed}" if self.proposed else "")


class PartialWrite(Exception):
    """The profile could not be written after the scaffold had already created files. Carries
    `created` and `problems`, so the failure names what is on disk rather than denying it
    (the review's code item 7)."""

    def __init__(self, cause: BaseException, created: list[Path], problems: list[str]) -> None:
        names = ", ".join(str(p) for p in created) or "none"
        super().__init__(
            f"the profile could not be written ({type(cause).__name__}: {cause}); "
            f"files already created by this run: {names}"
        )
        self.cause = cause
        self.created = created
        self.problems = problems


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


# The scalars the shipped template (`templates/application-profile.yaml`) leaves as `replace-me`
# and that no completed profile could carry that value in: its identity and its adoption record.
# Prose fields are deliberately absent - they are where a real profile may mention the token.
_TEMPLATE_SCALARS = (
    ("application_id",),
    ("owner",),
    ("adoption", "framework_version"),
    ("adoption", "framework_digest"),
    ("adoption", "adoption_date"),
)


def _refuse_if_already_adopted(repo: Path) -> None:
    """Refuses on a REAL profile; the template, still carrying its placeholders, is fair game.

    A profile is the template when one of its identifying scalars is still literally
    `replace-me`. `F63`: this tested `"replace-me" in text` over the whole file, so a completed
    profile whose prose mentioned the token was mistaken for the template and overwritten with no
    prompt. A file that does not parse as a mapping is refused too: whatever it is, it is not
    the template, and the only safe thing to do with it is leave it alone.

    The installer already never overwrites an existing profile (`install_standard.py`'s own rule);
    this is the same protection applied one step later, to the wizard that is much more likely to
    be run against a repository someone has already been working in.
    """
    path = repo / PROFILE_PATH
    if not path.is_file():
        return
    import yaml

    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        document = None
    if isinstance(document, dict):
        for keys in _TEMPLATE_SCALARS:
            node: object = document
            for key in keys:
                node = node.get(key) if isinstance(node, dict) else None
            if isinstance(node, str) and node.strip() == "replace-me":
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


def _save_draft(repo: Path, record: dict, draft: dict) -> None:
    """Called after every stage completes - a late failure loses at most the stage in progress,
    not the whole run. `framework_version`/`framework_digest` travel with the draft so a later
    resume can tell whether the install underneath it has changed since, flagged rather than
    silently trusted; `format` states the shape so a draft written by a different shape of this
    wizard is recognised rather than misread (`DRAFT_FORMAT`). `draft` is `Flow.draft()`: the
    answers, the origin of each, and which stages are done."""
    payload = {
        "format": DRAFT_FORMAT,
        "framework_version": record.get("standard_version", ""),
        "framework_digest": record.get("framework_digest", ""),
        **draft,
    }
    target = _draft_path(repo)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _legacy_draft_path(repo: Path) -> Path:
    return repo / LEGACY_DRAFT_FILENAME


def _load_draft(repo: Path) -> dict | None:
    path = _draft_path(repo)
    if not path.is_file():
        path = _legacy_draft_path(repo)
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
    _legacy_draft_path(repo).unlink(missing_ok=True)


def _resume_or_start(repo: Path, record: dict, interview: Interview) -> dict:
    """Never resumes silently. A version/digest mismatch is flagged - shown to the human, who
    still decides - rather than either trusted or refused outright. Three answers: yes resumes,
    an explicit no deletes the draft, and quitting at the prompt (`None`) cancels the run with
    the draft kept.

    A draft in an older `format` is a different case and is not offered at all: Phase 1 drafts hold
    built profile fragments where these hold raw answers, so resuming one as the other would produce
    a confidently wrong profile rather than an error. It is left in place rather than deleted -
    this run's first completed section overwrites it - so nothing is destroyed to tidy up.
    """
    draft = _load_draft(repo)
    if draft is None:
        return {}

    if draft.get("format") != DRAFT_FORMAT or not isinstance(draft.get("sections"), dict):
        # An older shape, or a JSON-valid file that is not a draft: not offered. Left in place
        # rather than deleted; this run's first completed stage overwrites it.
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
    answer = interview.confirm_resume(info)
    if answer is None:
        # `F68`: the human quit at the prompt - `Ctrl+Q`, or the terminal closed. That is neither
        # "resume" nor "start fresh", and reading it as the latter deleted the draft the prompt
        # existed to protect. The run is cancelled and the draft stays where it was.
        raise Cancelled()
    if not answer:
        _clear_draft(repo)  # an explicit "n": the human chose to discard it
        return {}
    legacy = _legacy_draft_path(repo)
    if legacy.is_file():
        # Resumed from the old location: moved to the one the install record governs.
        _save_draft(repo, record, {k: v for k, v in draft.items() if k not in ("format", "framework_version", "framework_digest")})
        legacy.unlink()
    return draft


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
    `AlreadyAdopted`, `InstallMismatch` or `WriteRefused` - every one of them leaves the repository untouched, except
    that `Cancelled` (and any other failure) may leave a resumable draft behind - see
    `_save_draft`. A completed write clears it (below)."""
    _refuse_if_already_adopted(repo)
    record = _read_install_record(repo)
    _refuse_if_mismatched(repo, record)

    draft = _resume_or_start(repo, record, interview)
    flow = _flow.Flow(
        repo,
        record,
        verify=lambda profile, rendered: _verify(profile, rendered, repo),
        state=draft.get("sections") or {},
        origins=_flow.Flow.origins_from(draft),
        done=tuple(draft.get("done") or ()),
    )

    def on_progress() -> None:
        _save_draft(repo, record, flow.draft())

    approved_at = interview.collect(flow, on_progress=on_progress)

    profile = flow.assemble()
    rendered = render.render_profile(profile, written_on=flow.adoption_date)
    _verify(profile, rendered, repo)
    traced = provenance.trace(profile, flow.state, flow.origins)
    sidecar = provenance.render_record(
        provenance.record(
            traced,
            framework_version=record.get("standard_version", ""),
            approved_at=approved_at,
            bulk=flow.bulk,
        )
    )

    # Written BEFORE the profile, and only once the profile is known to render and verify. A
    # profile naming an artefact that does not exist fails `SP032` on the next run, so if anything
    # here is going to fail it should fail before the profile claims the artefact is there.
    created, scaffold_problems = scaffold.write(repo, flow.accepted_scaffold)

    target = repo / PROFILE_PATH
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8", newline="\n")
        # `DR-47` (2): the machine-owned record beside the profile, every field's origin and the
        # one document-level approval.
        (repo / provenance.PROVENANCE_PATH).write_text(sidecar, encoding="utf-8", newline="\n")
    except Exception as exc:  # noqa: BLE001 - whatever failed, say what is already on disk
        raise PartialWrite(exc, created, scaffold_problems) from exc
    _clear_draft(repo)  # a completed run leaves no draft behind - it exists only to protect one
    return Written(profile=target, created=created, problems=scaffold_problems)


# ---------------------------------------------------------------------------------------------
# Without a terminal: propose, then replay
# ---------------------------------------------------------------------------------------------

# The yes/no decisions the form asks as radios; a record answers them with the same two words.
_YES_NO = {"stack.builds_user_interface", "risk.relied_on_outside_team", "risk.material_quantitative_output"}


def _proposal_entry(proposal) -> dict:
    """A proposal as the answers record carries it. A value copied from an answer the human has
    not given yet (`= owner`, `= data_classification`) is written as `null`: it is filled from
    the human's answer when the record is replayed, and must not carry a placeholder into the
    profile."""
    if proposal.detail.startswith("= "):
        return {"value": None, "origin": proposal.origin, "detail": f"{proposal.detail} (filled from your answer at replay)"}
    return {"value": proposal.value, "origin": proposal.origin, "detail": proposal.detail}


def propose(repo: Path, *, level: str | None = None) -> Proposed:
    """Run discovery and write the answers record - every proposal with its origin, every decision
    only a human can make as a `needs-human` line - and, where `level` is given, a preview of the
    profile the proposals would produce. Never the profile (`DR-49` (3)).

    Without a level the record stops at the level, because nothing after it can be proposed
    until the level is known; the human sets the level and runs `--propose --level` again, or
    completes the record by hand. With a level, the interface gates are proposed as though the
    repository builds no user interface, and the record says so beside that line.
    """
    import yaml

    from surfaceplate.adopt import detect
    from surfaceplate.adopt import flow as _flow
    from surfaceplate.adopt import provenance, scaffold

    record = _read_install_record(repo)
    _refuse_if_mismatched(repo, record)
    flow = _flow.Flow(repo, record)
    answers: dict[str, object] = {}
    notes: dict[str, str] = {}

    decisions = flow.decisions_plan()
    placeholder: dict[str, object] = {}
    for spec in decisions.fields:
        proposal = flow.proposals.get(spec.id)
        if proposal is not None:
            answers[spec.id] = _proposal_entry(proposal)
            placeholder[spec.id] = proposal.value
        else:
            answers[spec.id] = NEEDS_HUMAN
            if spec.id in _YES_NO:
                placeholder[spec.id] = "no"
                notes[spec.id] = "yes | no"
            elif spec.kind == "choice":
                placeholder[spec.id] = spec.choices[0][0]
                notes[spec.id] = " | ".join(value for value, _ in spec.choices)
            else:
                placeholder[spec.id] = NEEDS_HUMAN
    flow.answer_decisions(placeholder)
    # The two prose fields the form leaves blank are proposed as "Not stated"; recorded as such.
    for key in ("risk.risk_profile", "risk.materiality_definition"):
        proposal = flow.proposals.get(key)
        if proposal is not None and answers.get(key) in (None, NEEDS_HUMAN):
            answers[key] = _proposal_entry(proposal)

    header = [
        "# Written by `surfaceplate adopt --propose`. Nothing else was written.",
        "#",
        "# Every line that says needs-human is a decision only a human can make. Complete them all,",
        "# then run:  surfaceplate adopt --answers <this file>",
        "# A proposed value is shown with where it came from; change it if it is wrong. The origin",
        "# of every value is recorded beside the profile when it is written.",
    ]
    proposed_path: Path | None = None
    if level is None:
        answers["level.conformance_level"] = NEEDS_HUMAN
        notes["level.conformance_level"] = "essential | standard | full - then run --propose --level <level> for the rest"
        header.append("# No level was given, so the record stops at the level: set it and run --propose --level.")
    else:
        flow.answer_level({"conformance_level": level})
        answers["level.conformance_level"] = level
        header.append(
            f"# Proposed at level {level}, and as though this repository builds no user interface;"
        )
        header.append("# answer stack.builds_user_interface and run --propose --level again to see the interface gates.")
        seeds = flow.gate_seeds()
        gate_placeholder: dict = {}
        for spec in flow.gate_specs():
            if not spec.mandatory and not spec.auto_status:
                answers[f"gates.{spec.id}.status"] = NEEDS_HUMAN
                notes[f"gates.{spec.id}.status"] = "required | deferred | not_applicable"
            for field in spec.fields:
                key = f"{spec.id}.{field.id}"
                proposal = flow.proposals.get(f"gates.{key}")
                if proposal is not None:
                    answers[f"gates.{key}"] = _proposal_entry(proposal)
                    gate_placeholder[key] = proposal.value
                elif field.id == "artefact" and (spec.mandatory or spec.auto_status == ""):
                    if spec.id in scaffold.SEEDABLE and not (repo / scaffold.SEEDABLE[spec.id][0]).exists():
                        answers[f"gates.{key}"] = {"value": scaffold.SEEDABLE[spec.id][0], "origin": provenance.SCAFFOLDED,
                                                 "detail": "created when the profile is written, if create_missing_artefacts is yes"}
                        gate_placeholder[key] = scaffold.SEEDABLE[spec.id][0]
                    else:
                        answers[f"gates.{key}"] = NEEDS_HUMAN
                        notes[f"gates.{key}"] = "a file git tracks in this repository"
                        gate_placeholder[key] = NEEDS_HUMAN
                elif field.id == "paths" and (spec.mandatory or spec.auto_status == ""):
                    answers[f"gates.{key}"] = NEEDS_HUMAN
                    notes[f"gates.{key}"] = "a git pathspec, e.g. src/**"
                    gate_placeholder[key] = NEEDS_HUMAN
        # Everything after the level that was proposed, and what the remainder form would ask.
        for key, proposal in flow.proposals.items():
            if key.startswith("gates.") or key in answers:
                continue
            answers[key] = _proposal_entry(proposal)
        for spec in flow.remainder_plan().fields:
            if spec.id not in answers:
                answers[spec.id] = NEEDS_HUMAN
                if spec.kind == "multiselect":
                    notes[spec.id] = "a list of control ids, or []"
        if detect.detect_decisions_folder(repo) is None:
            answers.setdefault("adoption.decision_record_id", {
                "value": scaffold.DECISION_RECORD_ID, "origin": provenance.SCAFFOLDED,
                "detail": f"created as {scaffold.DECISION_RECORD[0]} when the profile is written, if create_missing_artefacts is yes",
            })
        # The preview: the proposals rendered, human lines as needs-human, undecided gates left out.
        preview_state = {name: dict(values) for name, values in flow.state.items()}
        for key, value in answers.items():
            section, _, field_id = key.partition(".")
            if section == "gates" or section == "level":
                continue
            if value == NEEDS_HUMAN and field_id not in preview_state.get(section, {}):
                preview_state.setdefault(section, {})[field_id] = NEEDS_HUMAN
        preview_state["gates"] = dict(gate_placeholder)
        undecided = [spec.id for spec in flow.gate_specs() if not spec.mandatory and not spec.auto_status]
        for spec in flow.gate_specs():
            if spec.id in undecided:
                preview_state["gates"][f"{spec.id}.status"] = "not_applicable"
                preview_state["gates"][f"{spec.id}.rationale"] = NEEDS_HUMAN
            if spec.auto_status:
                preview_state["gates"].setdefault(f"{spec.id}.rationale", "This repository has no user interface.")
        preview_state.setdefault("adoption", {}).setdefault("decision_record_id", scaffold.DECISION_RECORD_ID)
        for key in ("adoption.repository_classification",):
            preview_state["adoption"].setdefault(key.split(".")[1], NEEDS_HUMAN)
        profile = sections.build_profile(
            preview_state, framework_version=record.get("standard_version", ""), framework_digest=record.get("framework_digest", "")
        )
        profile["prerequisites"] = [g for g in profile["prerequisites"] if g["id"] not in undecided]
        rendered = render.render_profile(profile, written_on=flow.adoption_date)
        preview_header = (
            "# PROPOSED - not the profile. Written by `surfaceplate adopt --propose` as a preview of what the\n"
            "# answers record would produce; the checker never reads this file. Every `needs-human` below is a\n"
            f"# decision for a human, and {len(undecided)} undecided gate(s) are left out entirely: "
            + ", ".join(undecided) + ".\n"
            "# Complete the answers record and run `surfaceplate adopt --answers` to write the real profile.\n\n"
        )
        proposed_path = repo / PROPOSED_PATH
        proposed_path.parent.mkdir(parents=True, exist_ok=True)
        proposed_path.write_text(preview_header + rendered, encoding="utf-8", newline="\n")
        answers.setdefault("create_missing_artefacts", NEEDS_HUMAN)
        notes.setdefault("create_missing_artefacts", "yes | no - whether to create the scaffolded files named above")

    record_out = {
        "format": ANSWERS_FORMAT,
        "framework_version": record.get("standard_version", ""),
        "framework_digest": record.get("framework_digest", ""),
        "level": answers.pop("level.conformance_level"),
        "answers": answers,
    }
    if notes:
        record_out["choices"] = notes
    body = yaml.safe_dump(record_out, sort_keys=False, allow_unicode=True, width=1000)
    answers_path = repo / ANSWERS_PATH
    answers_path.parent.mkdir(parents=True, exist_ok=True)
    answers_path.write_text("\n".join(header) + "\n\n" + body, encoding="utf-8", newline="\n")
    return Proposed(answers=answers_path, proposed=proposed_path)


def replay(repo: Path, answers_path: Path) -> Path:
    """Replay a human-completed answers record through the same code as the interface, and
    write the profile. A record with any `needs-human` line left refuses to write anything."""
    import yaml

    from surfaceplate.adopt.interview import ScriptedInterview

    try:
        record = yaml.safe_load(answers_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WriteRefused(f"the answers record could not be read: {exc}") from None
    if not isinstance(record, dict) or record.get("format") != ANSWERS_FORMAT or not isinstance(record.get("answers"), dict):
        raise WriteRefused(f"{answers_path} is not an answers record this version writes (format {ANSWERS_FORMAT}).")
    pending = [key for key, value in record["answers"].items() if value == NEEDS_HUMAN]
    if record.get("level") == NEEDS_HUMAN or not record.get("level"):
        pending.insert(0, "level")
    if pending:
        raise NeedsHuman(pending)
    scripted: dict[str, object] = {}
    for key, value in record["answers"].items():
        if key == "create_missing_artefacts":
            continue
        if isinstance(value, dict):
            if value.get("value") is None:
                continue  # filled from the human's answers by the flow itself
            scripted[key] = value["value"]
        else:
            scripted[key] = value
    scripted["level.conformance_level"] = record["level"]
    create = str(record["answers"].get("create_missing_artefacts", "yes")).strip().lower() in ("yes", "true", "y")
    interview = ScriptedInterview(answers=scripted, accept_scaffold=create)
    try:
        return run(repo, interview)
    except AssertionError as exc:
        # The scripted interview objects to a presented field the record lacks: say which, and
        # how to get a complete record.
        raise WriteRefused(
            f"the answers record is incomplete for this repository at level {record['level']}: {exc}. "
            f"Run `surfaceplate adopt --propose --level {record['level']}` for a complete record."
        ) from None
