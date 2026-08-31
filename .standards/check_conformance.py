#!/usr/bin/env python3
"""Surfaceplate - conformance checker.

Stack-neutral. Runs on any repository that has installed the standard, in CI or
locally, with nothing but Python. Schema validation additionally requires
``PyYAML`` and ``jsonschema``; the shipped workflow installs both.

This file is vendored into an adopting repository at ``.standards/check_conformance.py``
by ``install_standard.py`` and is itself covered by the integrity check, so a
repository cannot quietly weaken its own gate without that being visible.

Exit codes:
    0  conformance satisfied, or only graced findings within an unexpired window
    1  conformance failed
    2  the checker could not run (misuse, unreadable repository)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# --- Fixed contract with adopting repositories -------------------------------
# These paths are part of the published standard. Changing one is a breaking
# change for every adopting repository, not a refactor.

VENDOR_DIR = ".standards"
INSTALL_RECORD = f"{VENDOR_DIR}/INSTALL.json"
PROFILE_PATH = "governance/application-profile.yaml"
COPILOT_INSTRUCTIONS = ".github/copilot-instructions.md"
WORKFLOW_PATH = ".github/workflows/standards-conformance.yml"
SCHEMA_PATH = f"{VENDOR_DIR}/schemas/application-profile.schema.yaml"
EXCEPTION_SCHEMA_PATH = f"{VENDOR_DIR}/schemas/gate-exception.schema.yaml"

BLOCK_BEGIN = "<!-- BEGIN SURFACEPLATE -->"
BLOCK_END = "<!-- END SURFACEPLATE -->"

# The grace window may never exceed this many days from the recorded install
# date, regardless of what the install record claims. Editing `grace_expires`
# by hand therefore does not buy an indefinite exemption.
MAX_GRACE_DAYS = 30

# A profile describes a repository at a point in time. Repositories move; profiles
# do not move themselves. `adoption.review_by` is the date by which a human must
# re-read the profile and confirm it still describes reality.
#
# The horizon is capped for the same reason the grace window is: without a cap, an
# adopter could set `review_by` to 2099 and the control would be decorative.
MAX_REVIEW_HORIZON_DAYS = 400
REVIEW_WARN_DAYS = 30
DEFAULT_REVIEW_INTERVAL_DAYS = 180

# What makes an artefact "still a template". Token-based, and deliberately NOT
# pattern-based on angle brackets.
#
# An earlier version also matched `<[a-z0-9_\- ]{1,30}>`, on the theory that an unfilled
# slot looks like `<your-org>`. Measured against this repository it produced seven matches
# across six files and not one of them was a placeholder: two numbering conventions, a
# command template inside `core/PREREQUISITE_GATES.md` itself, a CLI usage line, and a
# historical URN form. Three of the six files were normative documents this framework
# publishes, so the same spurious failure reached any adopter whose governed artefact
# happened to contain a usage line — on a gate that is a floor at `standard`.
#
# It was removed rather than narrowed because the distinction it needed to draw is not
# available at this level: an unfilled slot `<your-org>` and a metavariable
# `<schema-file-name>` are lexically identical. Recorded as F14, decided in DR-17.
#
# Nothing detectable was lost. Every template this framework ships that carried an
# angle-bracket slot also carries `replace-me`, so file-level detection is unchanged. The
# audit that produced this change also found two templates carrying neither — a false
# negative — and they now carry `replace-me` for the same reason.
#
# tests/test_install_and_check.py pins both directions: a genuinely unfilled artefact is
# still caught, and notation is not. Do not re-add a shape-based branch here without a
# seen-to-fail case showing it separates the two.
PLACEHOLDER_PATTERN = re.compile(
    r"\breplace[-_ ]?me\b|\bTBD\b|\bTBC\b|\bTODO\b",
    re.IGNORECASE,
)

# Controls this checker actually verifies against the repository, as opposed to verifying
# that they were declared. DR-25 records the architecture by which the rest join them; each
# later packet moves one control into this set and the reporting shrinks accordingly.
#
# `documentation_authority` qualifies indirectly: the `authority_map` gate checks the artefact
# it depends on, so a repository cannot declare it and produce nothing.
VERIFIED_CONTROLS: set[str] = {
    "documentation_authority",  # pattern D - the authority_map gate, plus SP052
    "dependency_lock",          # pattern A - SP051
    "assurance_findings",       # pattern A - SP051
    "deterministic_tests",      # pattern B - SP053
    "contract_tests",           # pattern B - SP053
    "overrides",                # pattern C - SP055/SP056
    "method_registry",          # pattern C - SP055/SP056
    "run_lineage",              # pattern C - SP055/SP056
    "provenance",               # pattern C - SP055/SP056
}

# The controls each level requires, mirroring core/CONFORMANCE_LEVELS.md. A level is a
# floor, not a ceiling: an application may require more, never fewer.
CONFORMANCE_LEVELS: dict[str, set[str]] = {
    "essential": {"dependency_lock"},
    "standard": {
        "dependency_lock",
        "deterministic_tests",
        "contract_tests",
        "documentation_authority",
    },
    "full": {
        "dependency_lock",
        "deterministic_tests",
        "contract_tests",
        "documentation_authority",
        "provenance",
        "run_lineage",
        "method_registry",
        "overrides",
        "assurance_findings",
    },
}


# --- Prerequisite gates ------------------------------------------------------
#
# A gate is a rule of the shape "artefact X must exist before activity Y may begin".
# See core/PREREQUISITE_GATES.md for the catalogue in full.
#
# Enforcement has two local layers. The installed pre-commit hook checks the index before
# a commit is created. `git commit --no-verify` can bypass it, so the history audit remains
# the durable backstop: no repository state containing a violation can pass this check
# afterwards, whenever it runs.

GATE_CATALOGUE: dict[str, str] = {
    # design and user interface
    "component_library": "A component library must contain a component before a screen uses it.",
    "design_authority": "A design policy and screen templates must exist before UI code is written.",
    "options_before_build": "Alternatives must be documented and one selected before a designed surface is built.",
    "prerequisite_state_ui": "A screen must not present its main workflow until its data prerequisite is satisfied.",
    # work and decisions
    "work_registration": "No work begins until it is registered as an identified activity.",
    "work_contract": "A written work contract must exist before AI-assisted implementation starts.",
    "risk_classification": "A change must be classified for risk before implementation, not after.",
    "decision_before_implementation": "A decision record must exist before implementation of a material change begins.",
    "register_currency": "The work register and its generated views must be current before handover.",
    # documentation authority
    "authority_map": "A machine-readable map of which document governs which path must exist.",
    "authority_same_change": "A change to a governed path must update its controlling document in the same change.",
    # tests and evidence
    "test_convention": "New tests must follow the repository's declared naming and location standard.",
    "regression_before_merge": "Named regression suites must pass before a change to critical logic merges.",
    "equivalence_evidence": "A performance or refactoring change on a critical path must ship evidence results are unchanged.",
    # data
    "data_source_lifecycle": "A data source must pass its validation and approval lifecycle before it is selectable.",
    "output_validation_before_external_use": "Generated outputs must be validated and reviewed before use outside the delivery team.",
    # dependencies and release
    "dependency_output_delta": "A dependency change able to move outputs requires delta evidence and review before merge.",
    "records_before_release": "The change and decision records required by the risk class must exist before release preparation.",
    "change_record_before_completion": "A change record must exist before a change is treated as complete.",
}

# Gates each level requires to be decided 'required'. As with control_decisions, a level
# is a floor: an application may require more, never fewer.
LEVEL_REQUIRED_GATES: dict[str, set[str]] = {
    "essential": {"work_registration"},
    "standard": {
        "work_registration",
        "authority_map",
        "decision_before_implementation",
        "change_record_before_completion",
    },
    "full": {
        "work_registration",
        "authority_map",
        "decision_before_implementation",
        "change_record_before_completion",
        "authority_same_change",
        "regression_before_merge",
        "equivalence_evidence",
        "data_source_lifecycle",
        "output_validation_before_external_use",
        "dependency_output_delta",
        "records_before_release",
    },
}

# Levels at which every catalogue gate must at least be DECLARED - required, deferred or
# not_applicable, each with a reason. Silence is not a decision: a repository with no user
# interface should say so, not omit the question.
LEVELS_REQUIRING_FULL_DECLARATION = {"standard", "full"}

GATE_STATUSES = {"required", "deferred", "not_applicable"}

# The interface gates. These are a floor at `standard` and `full` for any repository that
# declares it builds a user interface. They cannot be `deferred`: a repository that builds
# screens either has decided its component library, design policy and page templates, or is
# building screens without having decided them. There is no third state worth recording.
#
# The floor is conditional rather than absolute because the checker cannot tell whether a
# repository has a user interface, and an unconditional requirement would leave a headless
# service able to conform only by declaring paths it does not have. So the repository
# declares the fact, in one field, and the declaration is a claim a human can falsify in
# seconds - which is a better control than a rationale nobody reads.
DESIGN_GATES = {
    "component_library",
    "design_authority",
    "options_before_build",
    "prerequisite_state_ui",
}

EXCEPTIONS_DIR = "governance/exceptions"
MAX_HISTORY_COMMITS = 2000

STANDARD_HOOKS_PATH = ".githooks"


class Finding:
    """A single conformance finding."""

    def __init__(self, code: str, title: str, detail: str, remedy: str, graceable: bool) -> None:
        self.code = code
        self.title = title
        self.detail = detail
        self.remedy = remedy
        self.graceable = graceable

    def render(self) -> str:
        return (
            f"  [{self.code}] {self.title}\n"
            f"        what: {self.detail}\n"
            f"        fix : {self.remedy}"
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalise(text: str) -> str:
    """Line-ending agnostic. A Windows checkout must not fail an integrity check."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def load_yaml(path: Path) -> tuple[Any, str | None]:
    try:
        import yaml
    except ImportError:
        return None, "PyYAML is not installed"
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle), None
    except Exception as exc:  # noqa: BLE001 - report any parse failure verbatim
        return None, f"{type(exc).__name__}: {exc}"


# --- Individual checks -------------------------------------------------------


def check_install_record(repo: Path, findings: list[Finding]) -> dict | None:
    record_path = repo / INSTALL_RECORD
    if not record_path.is_file():
        findings.append(
            Finding(
                "SP001",
                "Surfaceplate is not installed",
                f"{INSTALL_RECORD} is missing.",
                "Run install_standard.py from the surfaceplate repository.",
                graceable=False,
            )
        )
        return None
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        findings.append(
            Finding(
                "SP002",
                "The install record is unreadable",
                f"{INSTALL_RECORD}: {type(exc).__name__}: {exc}",
                "Re-run the installer to regenerate the install record.",
                graceable=False,
            )
        )
        return None

    for field in ("standard_version", "installed_at", "files"):
        if field not in record:
            findings.append(
                Finding(
                    "SP003",
                    "The install record is incomplete",
                    f"{INSTALL_RECORD} has no '{field}' field.",
                    "Re-run the installer to regenerate the install record.",
                    graceable=False,
                )
            )
            return None
    return record


def check_integrity(repo: Path, record: dict, findings: list[Finding]) -> None:
    """Every standard-owned file must be present and byte-identical to what was installed.

    F9: the remediation text below names a VERSION. It used to say "re-run the installer" with
    nothing scoping which installer. That advice is correct only if the operator's checkout is a
    fixed artefact they have not moved - `install_standard.repo_root()` resolves the source to
    wherever the running script sits, `build_payload` re-hashes from that source every run, and
    the run REWRITES the record rather than restoring toward the previous one. Under any ambient
    or upgradeable installer the same sentence restores different bytes and calls it a repair.
    """
    version_hint = record.get("standard_version") or "the version in .standards/INSTALL.json"
    missing: list[str] = []
    modified: list[str] = []
    for rel, expected in sorted(record.get("files", {}).items()):
        path = repo / rel
        if not path.is_file():
            missing.append(rel)
            continue
        try:
            actual = sha256_text(normalise(path.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            actual = sha256_file(path)
        if actual != expected:
            modified.append(rel)

    if missing:
        findings.append(
            Finding(
                "SP004",
                "Standard-owned files have been deleted",
                "; ".join(missing),
                f"Re-run the installer FROM VERSION {version_hint} to restore them, or record "
                "an approved override. The version matters: the installer rewrites this record "
                "from whatever source it is run from, so a different version restores different "
                "bytes and calls it a repair.",
                graceable=False,
            )
        )
    if modified:
        findings.append(
            Finding(
                "SP005",
                "Standard-owned files have been modified locally",
                "; ".join(modified),
                (
                    f"Revert the local edits and re-run the installer FROM VERSION "
                    f"{version_hint} - the version recorded in this repository's install "
                    "record. Running a different version does not restore these files; it "
                    "installs that version's files and rewrites the record to match, which "
                    "reads as a repair and is an upgrade. If the change is genuinely needed, "
                    "raise it against the standard so every repository gets it."
                ),
                graceable=False,
            )
        )
    if os.name != "nt":
        non_executable = [
            rel
            for rel in record.get("executable_files", [])
            if (repo / rel).is_file() and not os.access(repo / rel, os.X_OK)
        ]
        if non_executable:
            findings.append(
                Finding(
                    "SP005",
                    "Standard-owned hook files are not executable",
                    "; ".join(non_executable),
                    "Re-run the installer, then preserve the executable bit in Git with "
                    "'git update-index --chmod=+x <path>'.",
                    graceable=False,
                )
            )


def check_conformance_block(repo: Path, record: dict, findings: list[Finding]) -> None:
    path = repo / COPILOT_INSTRUCTIONS
    if not path.is_file():
        findings.append(
            Finding(
                "SP006",
                "No Copilot instructions file",
                f"{COPILOT_INSTRUCTIONS} is missing.",
                "Re-run the installer; it creates the file and inserts the conformance block.",
                graceable=False,
            )
        )
        return

    text = normalise(path.read_text(encoding="utf-8"))
    if BLOCK_BEGIN not in text or BLOCK_END not in text:
        findings.append(
            Finding(
                "SP007",
                "The conformance block is absent from the Copilot instructions",
                f"{COPILOT_INSTRUCTIONS} has no {BLOCK_BEGIN} / {BLOCK_END} markers.",
                "Re-run the installer. It inserts the block without touching your own content.",
                graceable=False,
            )
        )
        return

    body = text.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0]
    expected = record.get("conformance_block_digest")
    if expected and sha256_text(body.strip()) != expected:
        findings.append(
            Finding(
                "SP008",
                "The conformance block has been altered",
                f"The content between the markers in {COPILOT_INSTRUCTIONS} does not match the "
                "installed standard.",
                "Restore it by re-running the installer. Your own content outside the markers is "
                "left untouched.",
                graceable=False,
            )
        )


def check_workflow(repo: Path, findings: list[Finding]) -> None:
    if not (repo / WORKFLOW_PATH).is_file():
        findings.append(
            Finding(
                "SP009",
                "The conformance workflow is not present",
                f"{WORKFLOW_PATH} is missing.",
                "Re-run the installer.",
                graceable=False,
            )
        )


def check_profile(repo: Path, findings: list[Finding]) -> dict | None:
    path = repo / PROFILE_PATH
    if not path.is_file():
        findings.append(
            Finding(
                "SP010",
                "No application profile",
                f"{PROFILE_PATH} is missing.",
                f"Copy {VENDOR_DIR}/templates/application-profile.yaml to {PROFILE_PATH} and "
                "complete it.",
                graceable=True,
            )
        )
        return None

    data, error = load_yaml(path)
    if error:
        findings.append(
            Finding(
                "SP011",
                "The application profile could not be read",
                f"{PROFILE_PATH}: {error}",
                "Fix the YAML, or install PyYAML if that is what is missing.",
                graceable=False,
            )
        )
        return None
    if not isinstance(data, dict):
        findings.append(
            Finding(
                "SP012",
                "The application profile is not a mapping",
                f"{PROFILE_PATH} parsed as {type(data).__name__}.",
                "The profile must be a YAML mapping. See the template.",
                graceable=False,
            )
        )
        return None
    return data


def check_profile_schema(repo: Path, profile: dict, findings: list[Finding]) -> None:
    schema_file = repo / SCHEMA_PATH
    if not schema_file.is_file():
        findings.append(
            Finding(
                "SP013",
                "The application profile schema is not vendored",
                f"{SCHEMA_PATH} is missing.",
                "Re-run the installer.",
                graceable=False,
            )
        )
        return

    schema, error = load_yaml(schema_file)
    if error:
        findings.append(
            Finding(
                "SP014",
                "The schema could not be read",
                f"{SCHEMA_PATH}: {error}",
                "Install PyYAML, or re-run the installer if the file is corrupt.",
                graceable=False,
            )
        )
        return

    try:
        import jsonschema
    except ImportError:
        findings.append(
            Finding(
                "SP015",
                "Schema validation could not be performed",
                "The 'jsonschema' package is not installed, so the application profile was not "
                "validated. This is an absence of evidence, not evidence of conformance.",
                "pip install jsonschema pyyaml",
                graceable=False,
            )
        )
        return

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(profile), key=lambda e: list(e.path))
    for err in errors[:20]:
        location = "/".join(str(p) for p in err.path) or "(root)"
        findings.append(
            Finding(
                "SP016",
                "The application profile does not satisfy the control contract",
                f"at {location}: {err.message}",
                "Correct the profile. See the worked examples in examples/.",
                graceable=True,
            )
        )
    if len(errors) > 20:
        findings.append(
            Finding(
                "SP016",
                "Further schema errors were suppressed",
                f"{len(errors) - 20} additional errors not shown.",
                "Fix the reported errors and re-run.",
                graceable=True,
            )
        )


def check_profile_semantics(
    profile: dict,
    findings: list[Finding],
    today: _dt.date,
    notes: list[str],
) -> None:
    """Cross-field rules that JSON Schema cannot express."""
    level = profile.get("conformance_level")
    if level not in CONFORMANCE_LEVELS:
        findings.append(
            Finding(
                "SP017",
                "The declared conformance level is not recognised",
                f"conformance_level = {level!r}.",
                f"Set it to one of: {', '.join(CONFORMANCE_LEVELS)}. "
                "See core/CONFORMANCE_LEVELS.md.",
                graceable=True,
            )
        )
    else:
        # The declared level's controls must all be present and decided `required`.
        # Without this, a repository could claim `full` while deciding nothing - the
        # level would be a label rather than a commitment.
        decisions = profile.get("control_decisions")
        decisions = decisions if isinstance(decisions, dict) else {}
        for control_id in sorted(CONFORMANCE_LEVELS[level]):
            entry = decisions.get(control_id)
            if entry is None:
                findings.append(
                    Finding(
                        "SP021",
                        f"Conformance level '{level}' is overclaimed",
                        f"it requires control '{control_id}', which is absent from "
                        "control_decisions.",
                        f"Either decide '{control_id}' as required, or declare a lower level. "
                        "See core/CONFORMANCE_LEVELS.md.",
                        graceable=True,
                    )
                )
            elif not isinstance(entry, dict) or entry.get("decision") != "required":
                found = entry.get("decision") if isinstance(entry, dict) else entry
                findings.append(
                    Finding(
                        "SP022",
                        f"Conformance level '{level}' is overclaimed",
                        f"it requires control '{control_id}' to be 'required', found {found!r}.",
                        f"Either decide '{control_id}' as required, or declare a lower level.",
                        graceable=True,
                    )
                )

        # Every control decided `deferred` must be owned and dated, not merely dropped.
        deferred = {
            cid
            for cid, entry in decisions.items()
            if isinstance(entry, dict) and entry.get("decision") == "deferred"
        }
        adoption_block = profile.get("adoption")
        recorded = {
            d.get("control_id")
            for d in (adoption_block.get("deferrals") or [])
            if isinstance(d, dict)
        } if isinstance(adoption_block, dict) else set()
        unowned = sorted(deferred - recorded)
        if unowned:
            findings.append(
                Finding(
                    "SP023",
                    "Controls were deferred without an owner or a revisit date",
                    f"deferred but absent from adoption.deferrals: {', '.join(unowned)}.",
                    "Add each to adoption.deferrals with a rationale, an owner, and a revisit_by "
                    "date. A deferral nobody owns is an exclusion.",
                    graceable=True,
                )
            )

    adoption = profile.get("adoption")
    if not isinstance(adoption, dict):
        findings.append(
            Finding(
                "SP018",
                "The profile records no adoption metadata",
                "The 'adoption' block is missing.",
                "Complete the adoption block: version, digest, date, maintainer, classification.",
                graceable=True,
            )
        )
    else:
        status = adoption.get("adoption_status")
        if status in ("blocked", "deferred") and not adoption.get("status_rationale"):
            findings.append(
                Finding(
                    "SP019",
                    "An incomplete adoption carries no rationale",
                    f"adoption_status is '{status}' with no status_rationale.",
                    "State why adoption is blocked or deferred, and what would unblock it.",
                    graceable=False,
                )
            )
        check_profile_review(adoption, findings, today, notes)

    # Unfilled template placeholders mean the profile was installed, not adopted.
    placeholders: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, f"{path}.{key}" if path else str(key))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f"{path}[{index}]")
        elif isinstance(node, str) and PLACEHOLDER_PATTERN.search(node):
            placeholders.append(f"{path} = {node!r}")

    walk(profile, "")
    if placeholders:
        findings.append(
            Finding(
                "SP020",
                "The application profile still contains template placeholders",
                "; ".join(placeholders[:10])
                + (f" (and {len(placeholders) - 10} more)" if len(placeholders) > 10 else ""),
                "Replace every placeholder with a real value. A profile of placeholders records "
                "nothing.",
                graceable=True,
            )
        )


# --- Grace window ------------------------------------------------------------


def check_profile_review(
    adoption: dict,
    findings: list[Finding],
    today: _dt.date,
    notes: list[str],
) -> None:
    """The profile must carry a live review date.

    A profile is a snapshot of a judgement. Nothing in an integrity check can tell
    that a repository has outgrown the level it declared: the files are intact, the
    schema is satisfied, and the claim is simply no longer true. A dated review is
    the only thing that forces a human back to the question.
    """
    raw = adoption.get("review_by")
    if raw is None:
        findings.append(
            Finding(
                "SP024",
                "The profile records no review date",
                "adoption.review_by is absent.",
                "Add 'review_by: YYYY-MM-DD' to the adoption block - the date by which someone "
                f"must confirm this profile still describes the repository. "
                f"{DEFAULT_REVIEW_INTERVAL_DAYS} days is the suggested interval.",
                graceable=True,
            )
        )
        return

    try:
        review_by = _dt.date.fromisoformat(str(raw)[:10])
    except ValueError:
        findings.append(
            Finding(
                "SP024",
                "The profile review date is unreadable",
                f"adoption.review_by is {raw!r}, which is not an ISO date.",
                "Use the YYYY-MM-DD form, for example '2027-02-15'.",
                graceable=True,
            )
        )
        return

    horizon = today + _dt.timedelta(days=MAX_REVIEW_HORIZON_DAYS)
    if review_by > horizon:
        findings.append(
            Finding(
                "SP026",
                "The profile review date is beyond the permitted horizon",
                f"adoption.review_by is {review_by.isoformat()}, more than "
                f"{MAX_REVIEW_HORIZON_DAYS} days away.",
                f"Set a review date within {MAX_REVIEW_HORIZON_DAYS} days. A review deferred "
                "indefinitely is not a review.",
                graceable=False,
            )
        )
        return

    if review_by < today:
        overdue = (today - review_by).days
        findings.append(
            Finding(
                "SP025",
                "The application profile is overdue for review",
                f"adoption.review_by was {review_by.isoformat()}, {overdue} day(s) ago.",
                "Re-read the profile. Confirm the conformance level, the materiality definition "
                "and the control decisions still describe this repository, record the outcome in "
                "the decision record, then set the next review_by date.",
                graceable=True,
            )
        )
        return

    remaining = (review_by - today).days
    if remaining <= REVIEW_WARN_DAYS:
        notes.append(
            f"The application profile is due for review on {review_by.isoformat()} "
            f"({remaining} day(s) away). This check will fail once that date passes."
        )


# Ways a step's exit code stops reaching the job. Narrow on purpose: each of these
# discards a non-zero status outright. `|| echo` is here because it is not hypothetical -
# see the run cited in DR-18.
NEUTRALISING_SUFFIXES = ("|| true", "|| :", "|| exit 0", "|| echo")


def step_mentions(step: dict, scanner: str) -> bool:
    """Whether a workflow step invokes the named scanner."""
    haystack = " ".join(
        str(step.get(key, "")) for key in ("uses", "run", "name", "id")
    ).lower()
    return scanner.lower() in haystack


def check_pinned_identity(profile: dict, record: dict | None, findings: list[Finding]) -> None:
    """Check the profile's declared pin against the standard actually installed.

    F7's remedy. Until this existed, `adoption.framework_digest` was shape-checked against
    `^[A-Fa-f0-9]{64}$` and nothing else, while its name, its description and its 64-hex
    constraint together made it read as a verified pin. A reader of a conformant profile could
    not tell the difference from the artefact alone, which is the actual finding - not that a
    check was missing, but that its absence was invisible.

    The anchor is `sha256(MANIFEST.sha256)`, per DR-14, recorded by the installer. NOT the
    release archive's digest: `build_release.py` writes zip entries with their mtimes, so the
    archive is not reproducible and an adopter could never recompute what they had recorded.
    The manifest is a pure function of tree content, so a third party holding the published tree
    can recompute the anchor on a machine that is not the adopter's.

    WHAT THIS DOES NOT DO. It compares two values that both live inside the repository being
    checked, so it establishes that the profile agrees with the install record - not that either
    is true. A party with write access edits both. That is F6, which is structural and stays
    open; DR-14 says as much and this function does not claim more. What it does close is
    narrower and real: a profile that claims a version it was not installed from now fails,
    where before it passed in silence.

    Both codes are graceable. DR-14 CHANGES what framework_digest means, so every profile
    written under the previous definition carries an archive digest and would fail the day this
    ships. An obligation that arrives without grace is one nobody can adopt.
    """
    adoption = profile.get("adoption")
    if not isinstance(adoption, dict) or not isinstance(record, dict):
        return

    declared_version = adoption.get("framework_version")
    installed_version = record.get("standard_version")
    if declared_version and installed_version and declared_version != installed_version:
        findings.append(
            Finding(
                "SP048",
                "The profile declares a different version from the one installed",
                f"adoption.framework_version is {declared_version}, but "
                f"{INSTALL_RECORD} records {installed_version} as installed.",
                "Correct the profile, or re-run the installer. A conformance claim names the "
                "version it was assessed against; naming one that is not present makes the "
                "claim unverifiable rather than merely wrong.",
                graceable=True,
            )
        )

    declared_digest = adoption.get("framework_digest")
    if not declared_digest:
        return

    installed_digest = record.get("framework_digest")
    if not installed_digest:
        findings.append(
            Finding(
                "SP049",
                "The profile declares a framework digest that cannot be verified",
                f"{INSTALL_RECORD} carries no framework_digest, so the declared value is "
                f"compared against nothing. The standard was installed either from a tree with "
                f"no MANIFEST.sha256, or by an installer predating DR-14.",
                "Re-run the installer from a complete source tree. An unverifiable pin is "
                "reported rather than passed over: 'nothing to compare' and 'the values match' "
                "must not summarise the same way.",
                graceable=True,
            )
        )
        return

    if declared_digest.lower() != installed_digest.lower():
        findings.append(
            Finding(
                "SP049",
                "The profile's framework digest does not match what is installed",
                f"adoption.framework_digest is {declared_digest}, but the installed standard "
                f"anchors to {installed_digest}.",
                "Set adoption.framework_digest to the value in "
                f"{INSTALL_RECORD}, or re-run the installer. Note that DR-14 changed this "
                "field's meaning: it is now sha256(MANIFEST.sha256), not the release archive's "
                "digest, because the archive is not reproducible and so could never be "
                "recomputed by anyone checking the claim.",
                graceable=True,
            )
        )


# Controls verified by pattern A: the profile names an artefact, and the checker confirms it is
# really there. DR-25's cheapest pattern, reusing SP032's artefact logic rather than restating it.
PATTERN_A_CONTROLS: set[str] = {"dependency_lock", "assurance_findings"}

# Controls verified by pattern B: the profile names a CI step, and the checker confirms it exists
# and can fail. DR-25's second pattern, reusing check_secret_hygiene's mechanism.
PATTERN_B_CONTROLS: set[str] = {"deterministic_tests", "contract_tests"}

# Controls verified by pattern C: the profile names a DIRECTORY of records, and the checker confirms
# every record in it validates against the schema this framework ships for that type (DR-26).
#
# `provenance` and `run_lineage` share a record type deliberately. method-run-lineage already
# requires input_references and input_hash, so traceability to inputs is a property of the same
# record that carries reproducibility - DR-25 established that no separate provenance schema is
# needed. They are two properties of one record, not two records. What separates the two CONTROLS
# is which optional fields each obliges, and that is C2's work rather than this one's.
PATTERN_C_CONTROLS: dict[str, str] = {
    "overrides": "override-record.schema.yaml",
    "method_registry": "method-registry-entry.schema.yaml",
    "run_lineage": "method-run-lineage.schema.yaml",
    "provenance": "method-run-lineage.schema.yaml",
}


def find_workflow_step(repo: Path, step_name: str) -> tuple[str | None, dict | None]:
    """Locate a named step across the repository's workflow files.

    Returns (workflow path, step) or (None, None). Searches rather than requiring the adopter to
    name a file too: a step name is what a human recognises, and which file holds it is an
    implementation detail that moves.
    """
    for directory in (repo / ".github" / "workflows", repo / ".gitlab-ci.d"):
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.y*ml")):
            document, _ = load_yaml(path)
            if not isinstance(document, dict):
                continue
            jobs = document.get("jobs")
            if not isinstance(jobs, dict):
                continue
            for job in jobs.values():
                if not isinstance(job, dict):
                    continue
                for step in job.get("steps") or []:
                    if isinstance(step, dict) and step.get("name") == step_name:
                        return path.relative_to(repo).as_posix(), step
    return None, None


def check_pattern_b_controls(
    repo: Path, profile: dict, findings: list[Finding], notes: list[str]
) -> None:
    """Verify that controls claiming pattern B name a CI step that exists and can fail (DR-25).

    WHAT THIS PROVES, and the limit is the whole of it: a named step exists, runs something, and
    its failure is binding. NOT that the tests are deterministic, NOT that they are contract
    tests, NOT that they assert anything. A step running `true` would pass this check.

    That is the same boundary as SP046/SP047, which verify a scanner is wired and never that
    secrets are absent - and it is why the bypass half matters. A workflow can run a suite,
    report success and stay green while the suite failed, if the exit code is discarded. That is
    an observed failure in this project's own history, not a hypothesis.

    DR-25 predicted this reference would be a status-check name. It is a STEP name, amended in
    that record: a status check is a job, one job here runs every suite, and both controls would
    have pointed at the same name with an identical check - losing the distinction between them.
    """
    decisions = profile.get("control_decisions")
    decisions = decisions if isinstance(decisions, dict) else {}

    for control_id in sorted(PATTERN_B_CONTROLS):
        entry = decisions.get(control_id)
        if not isinstance(entry, dict) or entry.get("decision") != "required":
            continue

        reference = entry.get("implementation_reference")
        if not isinstance(reference, str) or not reference.strip():
            findings.append(
                Finding(
                    "SP053",
                    f"Control '{control_id}' is required but names no CI step",
                    f"control_decisions.{control_id} has no implementation_reference, so nothing "
                    f"connects the declaration to anything that runs.",
                    "Add implementation_reference naming the CI step that runs these tests. A "
                    "control nobody can locate is a statement of intent.",
                    graceable=True,
                )
            )
            continue

        reference = reference.strip()
        workflow, step = find_workflow_step(repo, reference)
        if step is None:
            findings.append(
                Finding(
                    "SP053",
                    f"Control '{control_id}' names a CI step that does not exist",
                    f"No workflow contains a step named {reference!r}.",
                    "Correct the name or add the step. A reference resolving to nothing reads as "
                    "evidence and is not.",
                    graceable=True,
                )
            )
            continue

        if not (step.get("run") or step.get("uses")):
            findings.append(
                Finding(
                    "SP053",
                    f"Control '{control_id}' names a CI step that runs nothing",
                    f"{reference!r} in {workflow} has neither `run` nor `uses`.",
                    "A named step that executes nothing satisfies a search and no one else.",
                    graceable=True,
                )
            )
            continue

        if step.get("continue-on-error") is True:
            findings.append(
                Finding(
                    "SP053",
                    f"Control '{control_id}' names a step that cannot fail the build",
                    f"{reference!r} in {workflow} sets continue-on-error: true, so a failing "
                    f"test run is recorded as tolerated and the job stays green.",
                    "Remove continue-on-error. A test whose failure is not binding reports, it "
                    "does not control.",
                    graceable=True,
                )
            )
            continue

        run = str(step.get("run") or "")
        swallowed = [
            line.strip() for line in run.splitlines()
            if any(token in line for token in NEUTRALISING_SUFFIXES)
        ]
        if swallowed:
            findings.append(
                Finding(
                    "SP053",
                    f"Control '{control_id}' names a step that discards its exit code",
                    f"{reference!r} in {workflow} swallows a non-zero status, so a failed run is "
                    f"indistinguishable from a passing one.",
                    "Let the exit code reach the job. If a non-blocking report is wanted, run it "
                    "as a separate reporting step rather than disarming this one.",
                    graceable=True,
                )
            )
            continue

        notes.append(f"{control_id}: verified against step {reference!r} in {workflow}")



def check_control_implementations(
    repo: Path, profile: dict, findings: list[Finding], notes: list[str],
    exempt_from_placeholder: set[str] | None = None,
) -> None:
    """Verify that controls claiming pattern A point at an artefact that exists (DR-25).

    F20 recorded that a control was checked against itself: SP021/SP022 confirmed it was listed
    and read `required`, and nothing asked whether the thing existed. This closes that for the
    two controls whose evidence is simply a file.

    `implementation_reference` is where the adopter says which file. The field has been in the
    schema since the beginning and was read by nothing.

    WHAT THIS PROVES, and the limit is the point: that a named file exists, is not empty, is not
    still a template, and is tracked by git. NOT that its contents are honest. A lockfile listing
    versions nobody installs would pass. DR-25 records that boundary as permanent rather than as
    a gap to close later.
    """
    # The same declared exemptions the gates honour (F16, DR-22). Applying the placeholder scan
    # here but ignoring the exemption would mean one mechanism behaving two ways depending on
    # which check reached the file - and org/FINDINGS.md is the case that proves it, since it
    # documents the very tokens the scan looks for.
    exempt_from_placeholder = exempt_from_placeholder or set()

    decisions = profile.get("control_decisions")
    decisions = decisions if isinstance(decisions, dict) else {}

    for control_id in sorted(PATTERN_A_CONTROLS):
        entry = decisions.get(control_id)
        if not isinstance(entry, dict) or entry.get("decision") != "required":
            continue  # not required here; SP021/SP022 own whether it should have been

        reference = entry.get("implementation_reference")
        if not isinstance(reference, str) or not reference.strip():
            findings.append(
                Finding(
                    "SP051",
                    f"Control '{control_id}' is required but names nothing to check",
                    f"control_decisions.{control_id} has no implementation_reference, so the "
                    f"declaration is compared against nothing.",
                    "Add implementation_reference naming the file that implements this control "
                    "- a lock file, a findings register. A control checked only against its own "
                    "declaration is a statement of intent, not a control.",
                    graceable=True,
                )
            )
            continue

        reference = reference.strip()
        target = repo / reference
        if not target.is_file():
            findings.append(
                Finding(
                    "SP051",
                    f"Control '{control_id}' names a file that does not exist",
                    f"implementation_reference is {reference}, which is not present.",
                    "Correct the path or create the file. A reference that resolves to nothing "
                    "is worse than none: it reads as evidence.",
                    graceable=True,
                )
            )
            continue

        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""

        if not text.strip():
            findings.append(
                Finding(
                    "SP051",
                    f"Control '{control_id}' names an empty file",
                    f"{reference} exists but is empty.",
                    "An empty file satisfies a path check and no one else.",
                    graceable=True,
                )
            )
            continue

        if reference not in exempt_from_placeholder and PLACEHOLDER_PATTERN.search(text):
            findings.append(
                Finding(
                    "SP051",
                    f"Control '{control_id}' names an unfinished file",
                    f"{reference} still contains template placeholders.",
                    "Complete it. A template is not an implemented control.",
                    graceable=True,
                )
            )
            continue

        # Tracked by git, because an untracked file is not part of the repository an auditor
        # would receive - it exists on one machine and nowhere else.
        if git_available(repo):
            code, _ = git(repo, "ls-files", "--error-unmatch", reference)
            if code != 0:
                findings.append(
                    Finding(
                        "SP051",
                        f"Control '{control_id}' names an untracked file",
                        f"{reference} exists locally but is not tracked by git.",
                        "Commit it. A file present on one machine is not evidence available to "
                        "anyone else.",
                        graceable=True,
                    )
                )
                continue

        notes.append(f"{control_id}: verified against {reference}")

    # Pattern D. `documentation_authority` is verified by the `authority_map` gate checking the
    # artefact it names - but only when that gate is required. A level is a floor, not a ceiling,
    # so an adopter may require the control at `essential`, where the gate is not part of the
    # floor, and be back to a control checked against itself. This closes that seam.
    entry = decisions.get("documentation_authority")
    if isinstance(entry, dict) and entry.get("decision") == "required":
        gates = profile.get("prerequisites")
        gates = gates if isinstance(gates, list) else []
        declared = {
            g.get("id"): g for g in gates if isinstance(g, dict) and g.get("id")
        }
        gate = declared.get("authority_map")
        if not isinstance(gate, dict) or gate.get("status") != "required":
            findings.append(
                Finding(
                    "SP052",
                    "documentation_authority is required without the gate that verifies it",
                    "The control is decided 'required', but the 'authority_map' gate is not - "
                    f"found {(gate or {}).get('status', 'no declaration')!r}.",
                    "Declare the 'authority_map' gate as required. Without it nothing checks "
                    "that an authority map exists, and the control is verified by nothing - "
                    "which is what it looks like from the profile either way.",
                    graceable=True,
                )
            )
        else:
            notes.append(
                "documentation_authority: verified via the authority_map gate"
            )


def check_pattern_c_controls(
    repo: Path, profile: dict, findings: list[Finding], notes: list[str]
) -> None:
    """Verify that controls claiming pattern C name a register whose records validate (DR-26).

    This closes the half of F20 that has been open since the architecture was written. A
    repository could claim `full`, declare `provenance`, `run_lineage`, `method_registry` and
    `overrides`, contain no records whatsoever, and draw no finding about any of them.

    AN EMPTY REGISTER PASSES, AND THAT IS THE DESIGN RATHER THAN A HOLE IN IT. A validator that
    demanded records would be a validator that rewarded inventing them, which is the one failure
    this whole sequence is arranged to avoid: records are cheap and git-native, judgements are
    where fabrication lives. So what a pass establishes here is "NO UNVALIDATED RECORD EXISTS IN
    THIS REGISTER", never "records exist". core/CONFORMANCE_LEVELS.md says so in those words,
    because a reader will otherwise infer the stronger claim from the same green line.

    Nor does validity mean truth. A run-lineage record can name an input hash that was never
    computed over anything, and it will validate. DR-25 records that boundary as permanent.
    """
    decisions = profile.get("control_decisions")
    decisions = decisions if isinstance(decisions, dict) else {}

    # One validator per SCHEMA rather than per control, because provenance and run_lineage share
    # a record type and would otherwise parse and compile the same schema twice.
    validators: dict[str, tuple[Any | None, str | None]] = {}

    for control_id, schema_name in sorted(PATTERN_C_CONTROLS.items()):
        entry = decisions.get(control_id)
        if not isinstance(entry, dict) or entry.get("decision") != "required":
            continue  # not required here; SP021/SP022 own whether it should have been

        reference = entry.get("implementation_reference")
        if not isinstance(reference, str) or not reference.strip():
            findings.append(
                Finding(
                    "SP055",
                    f"Control '{control_id}' is required but names no register",
                    f"control_decisions.{control_id} has no implementation_reference, so there "
                    f"is nowhere to look for the records it obliges.",
                    "Add implementation_reference naming the directory that holds these records. "
                    "An empty directory is acceptable and is the honest starting point; a "
                    "directory that is not named at all is a control checked against nothing.",
                    graceable=True,
                )
            )
            continue

        reference = reference.strip()
        target = repo / reference

        if target.is_file():
            findings.append(
                Finding(
                    "SP055",
                    f"Control '{control_id}' names a file where a register belongs",
                    f"implementation_reference is {reference}, which is a file.",
                    "Name the directory that holds the records. This control is satisfied by a "
                    "register that grows, not by a single document.",
                    graceable=True,
                )
            )
            continue

        if not target.is_dir():
            findings.append(
                Finding(
                    "SP055",
                    f"Control '{control_id}' names a register that does not exist",
                    f"implementation_reference is {reference}, which is not present.",
                    "Create the directory or correct the path. A reference that resolves to "
                    "nothing is worse than none: it reads as evidence.",
                    graceable=True,
                )
            )
            continue

        # Non-YAML files are ignored on purpose, so a register can carry a README explaining what
        # it holds without the README being read as a malformed record.
        records = sorted(target.glob("*.y*ml"))

        # Tracked by git, asked PER RECORD rather than of the directory, and both halves of that
        # matter. Git does not track empty directories, so demanding the directory be tracked
        # would make an empty register impossible - forcing exactly the fabrication this control
        # refuses to incentivise. And `ls-files --others --exclude-standard` was the first
        # implementation here: it reports nothing for a register that is gitignored outright,
        # which is the one case where every record is guaranteed to reach nobody. Asking
        # --error-unmatch of each record answers the question actually being put.
        if git_available(repo):
            untracked = [
                path.relative_to(repo).as_posix()
                for path in records
                if git(repo, "ls-files", "--error-unmatch", path.relative_to(repo).as_posix())[0]
                != 0
            ]
            if untracked:
                shown = ", ".join(untracked[:3])
                more = f" (+{len(untracked) - 3} more)" if len(untracked) > 3 else ""
                findings.append(
                    Finding(
                        "SP055",
                        f"Control '{control_id}' names a register holding untracked records",
                        f"{reference} contains untracked records: {shown}{more}.",
                        "Commit them. A record present on one machine is not available to the "
                        "reviewer, the auditor, or the next person.",
                        graceable=True,
                    )
                )
                continue

        if validators.get(schema_name) is None:
            validators[schema_name] = record_validator(
                repo, f"{VENDOR_DIR}/schemas/{schema_name}"
            )
        validator, validator_error = validators[schema_name]

        if validator is None:
            # A negative result must establish that the observation succeeded. Falling silent here
            # would report "no invalid records" from a look that could not have found one - and
            # this is the exact handling SP043 already applies to gate exceptions.
            findings.append(
                Finding(
                    "SP056",
                    f"Control '{control_id}' could not be checked",
                    validator_error or f"the validator for {schema_name} is unavailable",
                    f"Restore {VENDOR_DIR}/schemas/{schema_name} and install jsonschema. Until "
                    "then this control is unverified, which is not the same as satisfied.",
                    graceable=True,
                )
            )
            continue

        invalid = False
        for path in records:
            rel = path.relative_to(repo).as_posix()
            data, error = load_yaml(path)
            if error:
                findings.append(
                    Finding(
                        "SP056",
                        f"Record '{rel}' is unreadable",
                        error,
                        "Correct or remove it. A record nobody can parse records nothing.",
                        graceable=True,
                    )
                )
                invalid = True
                continue
            errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
            if errors:
                detail = "; ".join(
                    f"{'/'.join(str(part) for part in e.path) or '(root)'}: {e.message}"
                    for e in errors[:5]
                )
                findings.append(
                    Finding(
                        "SP056",
                        f"Record '{rel}' is invalid for control '{control_id}'",
                        detail,
                        f"Correct it against {VENDOR_DIR}/schemas/{schema_name}, or move it to "
                        "the register for the type it actually is.",
                        graceable=True,
                    )
                )
                invalid = True

        if invalid:
            continue

        # The count is reported, and zero is reported as zero rather than as silence, so that
        # "the register is clean" is distinguishable from "the register is empty" - the F3 defect
        # in its natural habitat.
        if records:
            notes.append(
                f"{control_id}: verified against {reference} "
                f"({len(records)} record(s), all valid)"
            )
        else:
            notes.append(
                f"{control_id}: verified against {reference} (register is empty - this control "
                f"establishes that nothing invalid is filed, not that anything is)"
            )


def check_deferral_expiry(
    profile: dict, findings: list[Finding], today: _dt.date, notes: list[str]
) -> None:
    """A deferral expires on the date its author gave it (F22, DR-25's `H`).

    SP031 requires a deferred control or gate to carry `revisit_by`, and until now nothing ever
    read it again. A deferral dated 2020 passed in 2026. This framework's own phrase for that
    state is "an omission wearing a decision's clothes" - which SP031 uses while failing to
    prevent the thing it describes.

    WHY THIS IS RECORDING AND NOT JUDGING. The date was declared by the adopter. Comparing a
    declared date against today establishes whether a stated commitment has come due; it does
    not decide anything on the adopter's behalf.

    GATE EXCEPTIONS ARE DELIBERATELY OUT OF SCOPE. `schemas/gate-exception.schema.yaml` carries
    only `raised_on`, and it is optional - there is no declared expiry, so a lifetime would have
    to be invented. That would be the tool deciding rather than recording. The absence is a real
    gap and is recorded in F22 rather than papered over here; giving exceptions an expiry is a
    contract change and deserves its own decision.
    """
    def assess(label: str, raw: object, remedy: str) -> None:
        try:
            due = _dt.date.fromisoformat(str(raw)[:10])
        except ValueError:
            findings.append(
                Finding(
                    "SP054",
                    f"{label} has an unreadable revisit date",
                    f"revisit_by is {raw!r}, which is not an ISO date.",
                    "Use the YYYY-MM-DD form. A malformed date is not a deadline - nothing can "
                    "come due, so the deferral is permanent by accident.",
                    graceable=True,
                )
            )
            return

        overdue = (today - due).days
        if overdue > 0:
            findings.append(
                Finding(
                    "SP054",
                    f"{label} passed its revisit date",
                    f"revisit_by was {due.isoformat()}, {overdue} day(s) ago.",
                    remedy,
                    graceable=True,
                )
            )
        elif -overdue <= REVIEW_WARN_DAYS:
            notes.append(
                f"{label} is due for revisit on {due.isoformat()} "
                f"({-overdue} day(s) away)."
            )

    adoption = profile.get("adoption")
    if isinstance(adoption, dict):
        for deferral in adoption.get("deferrals") or []:
            if not isinstance(deferral, dict):
                continue
            control = deferral.get("control_id") or "a deferral"
            if deferral.get("revisit_by") is not None:
                assess(
                    f"Deferral '{control}'",
                    deferral["revisit_by"],
                    "Revisit it: adopt the control, or set a new date with a reason that "
                    "survives someone who did not write the first one. A deferral nobody "
                    "revisits is an exclusion.",
                )

    for gate in profile.get("prerequisites") or []:
        if not isinstance(gate, dict) or gate.get("status") != "deferred":
            continue
        if gate.get("revisit_by") is not None:
            assess(
                f"Deferred gate '{gate.get('id', 'unnamed')}'",
                gate["revisit_by"],
                "Require the gate, or set a new date and say why. SP031 made you give this a "
                "date; this is the date arriving.",
            )


def check_secret_hygiene(repo: Path, profile: dict, findings: list[Finding]) -> None:
    """Verify that a secret scanner is declared and non-bypassably wired.

    WHAT THIS DOES NOT DO, stated first because the temptation to read it the other way is
    the whole risk: it does not scan for secrets, and a pass here says NOTHING about whether
    secrets are present. It checks that the repository has named a scanner and wired it
    somewhere that can fail. `core/SECURITY_BASELINE.md` puts the scanner itself on the
    adopting repository - "run the receiving repository's approved secret scanner" - and this
    framework has no business reimplementing one behind two YAML dependencies.

    Why the bypass check exists at all, and why it is not paranoia: a workflow can run a
    scanner, report `no findings`, and be green while the scanner found several, if the
    step's exit code is discarded. That is an observed failure, not a hypothesis. Confirming
    a scan step *exists* would pass such a workflow, so it would be a control that measures
    the presence of a control rather than its effect - the exact defect
    `core/CONTROL_PRINCIPLES.md` principle 9 warns about.

    Both codes are graceable. A new control that hard-failed every existing adopter on the
    day it shipped would be a control nobody could adopt; grace is the mechanism this
    framework already provides for arriving obligations.
    """
    baseline = profile.get("baseline_controls") or {}
    hygiene = baseline.get("secret_hygiene") or {}
    scanner_decl = hygiene.get("scanner")

    if not isinstance(scanner_decl, dict) or not scanner_decl.get("name"):
        findings.append(
            Finding(
                "SP046",
                "secret_hygiene is declared but no scanner is named",
                "baseline_controls.secret_hygiene has no scanner block naming a tool and "
                "where it is wired.",
                "Name the scanner and the file(s) that run it under "
                "baseline_controls.secret_hygiene.scanner. This standard requires "
                "secret_hygiene at every level; until the scanner is named, the requirement "
                "is a declaration with nothing behind it.",
                graceable=True,
            )
        )
        return

    scanner = str(scanner_decl["name"])
    wired_in = [w for w in (scanner_decl.get("wired_in") or []) if isinstance(w, str) and w]

    if not wired_in:
        findings.append(
            Finding(
                "SP046",
                f"Scanner '{scanner}' is named but not wired anywhere",
                "scanner.wired_in is empty, so nothing states where the scanner runs.",
                "List the workflow, hook, or script that runs the scanner. A named tool "
                "that no file invokes is not a control.",
                graceable=True,
            )
        )
        return

    for rel in wired_in:
        target = repo / rel
        if not target.is_file():
            findings.append(
                Finding(
                    "SP046",
                    f"Scanner '{scanner}' is wired to a file that does not exist",
                    f"{rel} is named in scanner.wired_in but is not present.",
                    "Correct the path or add the file. A gate whose wiring is absent is "
                    "not a control.",
                    graceable=True,
                )
            )
            continue

        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""

        if scanner.lower() not in text.lower():
            findings.append(
                Finding(
                    "SP046",
                    f"{rel} does not mention '{scanner}'",
                    f"{rel} is named as where the scanner runs, but the file never "
                    f"references it.",
                    "Point wired_in at the file that actually invokes the scanner.",
                    graceable=True,
                )
            )
            continue

        # Structured inspection, only where the file really is a workflow. Anything else
        # gets existence-and-mention only, and this function does not pretend otherwise -
        # a shell hook is not parsed, and no bypass finding is raised for one.
        document, _ = load_yaml(target)
        if not isinstance(document, dict) or "jobs" not in document:
            continue

        jobs = document.get("jobs")
        if not isinstance(jobs, dict):
            continue

        invoking = []
        for job in jobs.values():
            if not isinstance(job, dict):
                continue
            for step in job.get("steps") or []:
                if isinstance(step, dict) and step_mentions(step, scanner):
                    invoking.append(step)

        if not invoking:
            findings.append(
                Finding(
                    "SP046",
                    f"{rel} names '{scanner}' but no step runs it",
                    f"{rel} is a workflow and mentions the scanner, but no step uses or "
                    f"runs it. A mention in a comment is not an invocation.",
                    "Wire the scanner into a step, or point wired_in at the file that does.",
                    graceable=True,
                )
            )
            continue

        for step in invoking:
            label = step.get("name") or step.get("uses") or step.get("id") or "the scan step"
            if step.get("continue-on-error") is True:
                findings.append(
                    Finding(
                        "SP047",
                        f"The scan step in {rel} cannot fail the job",
                        f"'{label}' sets continue-on-error: true, so a finding is recorded "
                        f"as tolerated and the job stays green.",
                        "Remove continue-on-error from the scan step. A scanner that cannot "
                        "fail the build reports, it does not gate.",
                        graceable=True,
                    )
                )
            run = str(step.get("run") or "")
            for line in run.splitlines():
                stripped = line.strip()
                if scanner.lower() not in stripped.lower():
                    continue
                if any(token in stripped for token in NEUTRALISING_SUFFIXES):
                    findings.append(
                        Finding(
                            "SP047",
                            f"The scan command in {rel} discards its exit code",
                            f"'{label}' runs the scanner on a line that swallows a non-zero "
                            f"status, so a failed scan is indistinguishable from a clean one.",
                            "Let the scanner's exit code reach the job. If a non-blocking "
                            "report is genuinely wanted, run it as a separate reporting "
                            "workflow rather than disarming the gate.",
                            graceable=True,
                        )
                    )
                    break


def git(repo: Path, *args: str) -> tuple[int, str]:
    """Run git in the repository. Returns (exit code, stdout)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return 127, ""
    return result.returncode, result.stdout.strip()


def git_bytes(repo: Path, *args: str) -> tuple[int, bytes]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return 127, b""
    return result.returncode, result.stdout


def git_diagnostic(repo: Path, *args: str) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, "", f"{type(exc).__name__}: {exc}"
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def git_available(repo: Path) -> bool:
    code, _ = git(repo, "rev-parse", "--git-dir")
    return code == 0


def git_history_available(repo: Path) -> bool:
    code, _ = git(repo, "rev-parse", "--verify", "HEAD")
    return code == 0


def active_pre_commit_hook(repo: Path) -> tuple[bool, str]:
    """Return whether Git's active hooks directory contains a pre-commit hook."""
    code, configured = git(repo, "config", "--local", "--get", "core.hooksPath")
    if code == 0 and configured:
        hooks_dir = Path(configured)
        if not hooks_dir.is_absolute():
            hooks_dir = repo / hooks_dir
        hook = hooks_dir / "pre-commit"
        active = hook.is_file() and (os.name == "nt" or os.access(hook, os.X_OK))
        return active, f"core.hooksPath={configured!r}, expected executable hook {hook}"

    code, default_hook = git(repo, "rev-parse", "--git-path", "hooks/pre-commit")
    if code != 0 or not default_hook:
        return False, "Git could not resolve its active hooks directory"
    hook = Path(default_hook)
    if not hook.is_absolute():
        hook = repo / hook
    active = hook.is_file() and (os.name == "nt" or os.access(hook, os.X_OK))
    return active, f"default hooks path, expected executable hook {hook}"


def staged_paths(
    repo: Path, pathspecs: list[str] | None = None
) -> tuple[list[str], str | None]:
    args = ["diff", "--cached", "--name-only", "--diff-filter=ACMRTD"]
    if pathspecs:
        args.extend(["--", *pathspecs])
    code, out, error = git_diagnostic(repo, *args)
    if code != 0:
        return [], error or f"git exited with status {code}"
    return [line.replace("\\", "/") for line in out.splitlines() if line], None


def staged_artefact(repo: Path, path: str) -> tuple[bool, str | None]:
    """Return existence and file content from the index, not the working tree."""
    code, out = git(repo, "show", f":{path}")
    if code == 0:
        return True, out

    code, out = git(repo, "ls-files", "--cached", "--", path)
    if code == 0 and out:
        return True, None
    return False, None


def load_staged_profile(repo: Path) -> tuple[dict | None, str | None]:
    code, raw = git_bytes(repo, "show", f":{PROFILE_PATH}")
    if code != 0:
        return None, f"{PROFILE_PATH} is absent from the staged snapshot"
    try:
        import yaml
        data = yaml.safe_load(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - report the staged parse failure
        return None, f"{PROFILE_PATH} is unreadable in the staged snapshot: {type(exc).__name__}: {exc}"
    if not isinstance(data, dict):
        return None, (
            f"{PROFILE_PATH} parsed as {type(data).__name__} in the staged snapshot, "
            "expected a mapping"
        )
    return data, None


def staged_file_mode(repo: Path, path: str) -> str | None:
    code, out = git(repo, "ls-files", "--stage", "--", path)
    if code != 0 or not out:
        return None
    return out.split(None, 1)[0]


def check_staged_integrity(repo: Path, findings: list[Finding]) -> None:
    """Validate the commit being created, not only the checked-out working tree."""
    code, staged_record_raw = git_bytes(repo, "show", f":{INSTALL_RECORD}")
    if code != 0:
        findings.append(
            Finding(
                "SP040",
                "The staged snapshot has no install record",
                f"{INSTALL_RECORD} is absent from Git's index.",
                "Stage the installer output before committing.",
                graceable=False,
            )
        )
        return

    try:
        staged_record = json.loads(staged_record_raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        findings.append(
            Finding(
                "SP040",
                "The staged install record is unreadable",
                f"{INSTALL_RECORD}: {type(exc).__name__}: {exc}",
                "Re-run the installer and stage the resulting install record.",
                graceable=False,
            )
        )
        return

    working_record = (repo / INSTALL_RECORD).read_bytes()
    if normalise(staged_record_raw.decode("utf-8")) != normalise(
        working_record.decode("utf-8")
    ):
        findings.append(
            Finding(
                "SP040",
                "The staged install record differs from the checked-out installer output",
                f"{INSTALL_RECORD} is partially staged or was altered directly.",
                "Re-run the installer, then stage its complete output. The install record is "
                "the digest authority and must not be edited independently.",
                graceable=False,
            )
        )
        return

    missing: list[str] = []
    modified: list[str] = []
    for rel, expected in sorted(staged_record.get("files", {}).items()):
        code, raw = git_bytes(repo, "show", f":{rel}")
        if code != 0:
            missing.append(rel)
            continue
        try:
            actual = sha256_text(normalise(raw.decode("utf-8")))
        except UnicodeDecodeError:
            actual = hashlib.sha256(raw).hexdigest()
        if actual != expected:
            modified.append(rel)

    if missing or modified:
        detail = []
        if missing:
            detail.append("missing: " + ", ".join(missing))
        if modified:
            detail.append("modified: " + ", ".join(modified))
        findings.append(
            Finding(
                "SP040",
                "Standard-owned files are invalid in the staged snapshot",
                "; ".join(detail),
                "Stage the complete installer output. A valid working tree cannot make an "
                "invalid staged control safe to commit.",
                graceable=False,
            )
        )

    wrong_modes = [
        rel
        for rel in staged_record.get("executable_files", [])
        if staged_file_mode(repo, rel) != "100755"
    ]
    if wrong_modes:
        findings.append(
            Finding(
                "SP040",
                "Standard-owned hooks are not executable in the staged snapshot",
                "; ".join(wrong_modes),
                "Run 'git update-index --chmod=+x "
                + " ".join(wrong_modes)
                + "' before committing so Linux clones can execute the hook.",
                graceable=False,
            )
        )

    code, instructions_raw = git_bytes(repo, "show", f":{COPILOT_INSTRUCTIONS}")
    if code != 0:
        findings.append(
            Finding(
                "SP040",
                "The staged snapshot has no Copilot instructions",
                f"{COPILOT_INSTRUCTIONS} is absent from Git's index.",
                "Stage the complete installer output.",
                graceable=False,
            )
        )
        return
    instructions = normalise(instructions_raw.decode("utf-8", errors="replace"))
    if BLOCK_BEGIN not in instructions or BLOCK_END not in instructions:
        findings.append(
            Finding(
                "SP040",
                "The conformance block is absent from the staged snapshot",
                f"{COPILOT_INSTRUCTIONS} has no managed block in Git's index.",
                "Stage the complete installer output.",
                graceable=False,
            )
        )
        return
    body = instructions.split(BLOCK_BEGIN, 1)[1].split(BLOCK_END, 1)[0]
    expected_block = staged_record.get("conformance_block_digest")
    if expected_block and sha256_text(body.strip()) != expected_block:
        findings.append(
            Finding(
                "SP040",
                "The conformance block is altered in the staged snapshot",
                f"{COPILOT_INSTRUCTIONS} does not match the staged install record.",
                "Re-run the installer and stage the complete managed block.",
                graceable=False,
            )
        )


def check_staged_prerequisites(repo: Path, profile: dict, findings: list[Finding]) -> None:
    """Block staged gate crossings whose preconditions are absent from the index."""
    for gate in profile.get("prerequisites") or []:
        if not isinstance(gate, dict) or gate.get("status") != "required":
            continue
        if "local_hook" not in (gate.get("enforcement") or []):
            continue

        gate_id = str(gate.get("id", "<unnamed>"))
        paths = [
            path
            for path in ((gate.get("gated_activity") or {}).get("paths") or [])
            if isinstance(path, str) and path
        ]
        touched, pathspec_error = staged_paths(repo, paths)
        if pathspec_error:
            findings.append(
                Finding(
                    "SP042",
                    f"Gate '{gate_id}' has an invalid Git pathspec",
                    f"gated_activity.paths={paths!r}: {pathspec_error}",
                    "Correct the gate paths. A pathspec error must not become a silent "
                    "'no staged changes' result.",
                    graceable=False,
                )
            )
            continue
        if not touched:
            continue

        artefacts = [
            path
            for path in ((gate.get("precondition") or {}).get("artefacts") or [])
            if isinstance(path, str) and path
        ]
        unusable: list[str] = []
        for artefact in artefacts:
            exists, content = staged_artefact(repo, artefact)
            if not exists:
                unusable.append(f"{artefact} (absent from the staged snapshot)")
            elif content is not None and not content.strip():
                unusable.append(f"{artefact} (empty in the staged snapshot)")
            elif content is not None and PLACEHOLDER_PATTERN.search(content):
                unusable.append(f"{artefact} (unfinished in the staged snapshot)")

        if unusable:
            findings.append(
                Finding(
                    "SP039",
                    f"Staged change crosses gate '{gate_id}' without its precondition",
                    f"staged path(s) {', '.join(touched[:5])} are gated, while "
                    f"{'; '.join(unusable)}.",
                    "Stage a complete precondition artefact, unstage the gated change, or remove "
                    "'local_hook' from the enforcement claim if this gate cannot be checked "
                    "before commit. Bypassing with --no-verify remains visible to the history "
                    "audit.",
                    graceable=False,
                )
            )


def commits_touching(
    repo: Path, paths: list[str], since: _dt.date
) -> tuple[list[str], str | None]:
    code, out, error = git_diagnostic(
        repo,
        "log",
        f"-{MAX_HISTORY_COMMITS}",
        f"--since={since.isoformat()}",
        "--format=%H",
        "--",
        *paths,
    )
    if code != 0:
        return [], error or f"git exited with status {code}"
    return [line for line in out.splitlines() if line], None


def blob_exists(repo: Path, sha: str, path: str) -> bool:
    code, _ = git(repo, "cat-file", "-e", f"{sha}:{path}")
    return code == 0


def commit_subject(repo: Path, sha: str) -> str:
    code, out = git(repo, "log", "-1", "--format=%h %ad %s", "--date=short", sha)
    return out if code == 0 else sha[:8]


def record_validator(repo: Path, schema_rel: str) -> tuple[Any | None, str | None]:
    """A schema validator for one installed record type.

    Generalised from `exception_validator` when pattern C arrived (DR-26). Gate exceptions and
    the four record-based controls are the same problem - a directory of YAML records validated
    against a schema this framework ships - and a second loader would have been a second place
    for the jsonschema-absent path to be got wrong.

    The schema is read from the INSTALLED copy, whose integrity SP004/SP005 anchor, rather than
    from wherever the checker happens to be running.
    """
    schema, error = load_yaml(repo / schema_rel)
    if error:
        return None, error
    try:
        import jsonschema
    except ImportError:
        return None, "jsonschema is not installed"
    return (
        jsonschema.Draft202012Validator(
            schema,
            format_checker=jsonschema.FormatChecker(),
        ),
        None,
    )


def exception_validator(repo: Path) -> tuple[Any | None, str | None]:
    return record_validator(repo, EXCEPTION_SCHEMA_PATH)


def validated_exception(
    repo: Path,
    rel: str,
    data: Any,
    validator: Any,
    findings: list[Finding],
) -> tuple[str, set[str]] | None:
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        detail = "; ".join(
            f"{'/'.join(str(part) for part in error.path) or '(root)'}: {error.message}"
            for error in errors[:5]
        )
        findings.append(
            Finding(
                "SP043",
                f"Gate exception '{rel}' is invalid",
                detail,
                f"Correct the record against {EXCEPTION_SCHEMA_PATH}. An invalid exception "
                "provides no coverage.",
                graceable=False,
            )
        )
        return None

    gate_id = data["gate_id"]
    resolved: set[str] = set()
    for abbreviated in data["commits"]:
        code, full, error = git_diagnostic(
            repo,
            "rev-parse",
            "--verify",
            f"{abbreviated}^{{commit}}",
        )
        if code != 0 or not full:
            findings.append(
                Finding(
                    "SP043",
                    f"Gate exception '{rel}' names an unresolved commit",
                    f"{abbreviated!r}: {error or 'not a unique commit in this repository'}",
                    "Use a unique full or abbreviated commit SHA from this repository. An "
                    "unresolved exception provides no coverage.",
                    graceable=False,
                )
            )
            return None
        resolved.add(full.lower())
    return gate_id, resolved


def load_exceptions(repo: Path, findings: list[Finding]) -> dict[str, set[str]]:
    """Map gate_id -> set of commit SHAs an exception record covers.

    An exception is a legitimate escape hatch that leaves a permanent mark. A control
    with no legitimate exception route gets bypassed illegitimately instead.
    """
    covered: dict[str, set[str]] = {}
    directory = repo / EXCEPTIONS_DIR
    if not directory.is_dir():
        return covered
    validator, validator_error = exception_validator(repo)
    if validator is None:
        findings.append(
            Finding(
                "SP043",
                "Gate exceptions could not be validated",
                validator_error or "the exception schema validator is unavailable",
                f"Restore {EXCEPTION_SCHEMA_PATH} and install jsonschema.",
                graceable=False,
            )
        )
        return covered
    for path in sorted(directory.glob("*.y*ml")):
        data, error = load_yaml(path)
        if error:
            findings.append(
                Finding(
                    "SP043",
                    f"Gate exception '{path.relative_to(repo).as_posix()}' is unreadable",
                    error,
                    "Correct or remove the invalid exception. It provides no coverage.",
                    graceable=False,
                )
            )
            continue
        validated = validated_exception(
            repo,
            path.relative_to(repo).as_posix(),
            data,
            validator,
            findings,
        )
        if validated is None:
            continue
        gate_id, commits = validated
        bucket = covered.setdefault(gate_id, set())
        bucket.update(commits)
    return covered


def load_staged_exceptions(repo: Path, findings: list[Finding]) -> dict[str, set[str]]:
    """Map gate exceptions from Git's index, ignoring untracked and unstaged records."""
    code, out = git(repo, "ls-files", "--cached", "--", EXCEPTIONS_DIR)
    if code != 0:
        return {}
    try:
        import yaml
    except ImportError:
        return {}

    validator, validator_error = exception_validator(repo)
    if validator is None:
        findings.append(
            Finding(
                "SP043",
                "Staged gate exceptions could not be validated",
                validator_error or "the exception schema validator is unavailable",
                f"Restore {EXCEPTION_SCHEMA_PATH} and install jsonschema.",
                graceable=False,
            )
        )
        return {}

    covered: dict[str, set[str]] = {}
    for rel in sorted(
        line for line in out.splitlines() if line.lower().endswith((".yaml", ".yml"))
    ):
        code, raw = git_bytes(repo, "show", f":{rel}")
        if code != 0:
            continue
        try:
            data = yaml.safe_load(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - report malformed staged records
            findings.append(
                Finding(
                    "SP043",
                    f"Staged gate exception '{rel}' is unreadable",
                    f"{type(exc).__name__}: {exc}",
                    "Correct or unstage the invalid exception. It provides no coverage.",
                    graceable=False,
                )
            )
            continue
        validated = validated_exception(repo, rel, data, validator, findings)
        if validated is None:
            continue
        gate_id, commits = validated
        bucket = covered.setdefault(gate_id, set())
        bucket.update(commits)
    return covered


def earliest_declared_effective_from(repo: Path, gate_id: str) -> _dt.date | None:
    """The earliest effective_from this gate has ever carried, read from git history.

    This is what makes effective_from immutable in the only direction that matters.
    Moving the date forward would silently erase every violation between the old date
    and the new one, which is the one way this control could be gamed from inside.
    """
    if not git_available(repo):
        return None
    code, out = git(repo, "log", "-200", "--format=%H", "--", PROFILE_PATH)
    if code != 0:
        return None
    earliest: _dt.date | None = None
    try:
        import yaml
    except ImportError:
        return None
    for sha in [line for line in out.splitlines() if line]:
        code, blob = git(repo, "show", f"{sha}:{PROFILE_PATH}")
        if code != 0 or not blob:
            continue
        try:
            data = yaml.safe_load(blob)
        except Exception:  # noqa: BLE001 - a historical profile may be malformed
            continue
        if not isinstance(data, dict):
            continue
        for gate in data.get("prerequisites") or []:
            if not isinstance(gate, dict) or gate.get("id") != gate_id:
                continue
            raw = gate.get("effective_from")
            if raw is None:
                continue
            try:
                seen = _dt.date.fromisoformat(str(raw)[:10])
            except ValueError:
                continue
            if earliest is None or seen < earliest:
                earliest = seen
    return earliest


def audit_gate_history(
    repo: Path,
    gate: dict,
    effective_from: _dt.date,
    exceptions: dict[str, set[str]],
    findings: list[Finding],
) -> None:
    """Every commit touching a gated path must have had the preconditions in place."""
    gate_id = str(gate.get("id"))
    gated = gate.get("gated_activity") or {}
    precondition = gate.get("precondition") or {}
    paths = [p for p in (gated.get("paths") or []) if isinstance(p, str) and p]
    artefacts = [a for a in (precondition.get("artefacts") or []) if isinstance(a, str) and a]
    if not paths or not artefacts:
        return

    covered = exceptions.get(gate_id, set())
    violations: list[tuple[str, list[str]]] = []
    commits, pathspec_error = commits_touching(repo, paths, effective_from)
    if pathspec_error:
        findings.append(
            Finding(
                "SP042",
                f"Gate '{gate_id}' has an invalid Git pathspec",
                f"gated_activity.paths={paths!r}: {pathspec_error}",
                "Correct the gate paths. A failed history query must not be treated as an "
                "empty compliant history.",
                graceable=False,
            )
        )
        return

    for sha in commits:
        if sha.lower() in covered:
            continue
        missing = [a for a in artefacts if not blob_exists(repo, sha, a)]
        if missing:
            violations.append((sha, missing))

    if not violations:
        return

    shown = "; ".join(
        f"{commit_subject(repo, sha)} (missing {', '.join(missing)})"
        for sha, missing in violations[:3]
    )
    if len(violations) > 3:
        shown += f"; and {len(violations) - 3} more"
    findings.append(
        Finding(
            "SP035",
            f"Gate '{gate_id}' was crossed without its precondition",
            f"{len(violations)} commit(s) since {effective_from.isoformat()} changed a gated "
            f"path while a required artefact was absent: {shown}",
            "Either the gate was not honoured, or it is declared over paths it should not "
            f"cover. Correct the gate, or record the exception in {EXCEPTIONS_DIR}/ with a "
            "gate_id, the commit SHAs, an owner and a rationale.",
            graceable=True,
        )
    )


def placeholder_exemptions(
    repo: Path, profile: dict, findings: list[Finding], notes: list[str]
) -> set[str]:
    """Artefacts the profile declares exempt from the placeholder scan (F16, DR-22).

    The exemption is narrow on purpose. It suppresses the placeholder branch of SP032 and
    nothing else: an exempt artefact must still exist and must still be non-empty, and both
    remain checked.

    It is DECLARED IN THE PROFILE rather than marked inside the artefact. A template able to
    exempt itself would be precisely the hole SP032 exists to close, so the declaration lives
    where a reviewer reads it and a diff shows it.

    Every exemption is reported as an advisory on every run. A control that has been narrowed
    must say it was narrowed - a silently narrowed control is the shape this register has
    recorded more than any other.
    """
    declared = profile.get("placeholder_scan_exemptions") or []
    exempt: set[str] = set()
    for entry in declared:
        if not isinstance(entry, dict):
            continue
        artefact = entry.get("artefact")
        if not isinstance(artefact, str) or not artefact:
            continue
        if not (repo / artefact).is_file():
            findings.append(
                Finding(
                    "SP050",
                    "A placeholder-scan exemption names an artefact that does not exist",
                    f"{artefact} is declared exempt but is not present.",
                    "Remove the exemption or correct the path. A stale exemption silently "
                    "widens what this check tolerates, and outlives the thing it was written "
                    "for.",
                    graceable=True,
                )
            )
            continue
        exempt.add(artefact)
        notes.append(
            f"{artefact} is exempt from the placeholder scan by declaration: "
            f"{str(entry.get('rationale', '')).strip()}"
        )
    return exempt


def check_prerequisites(
    repo: Path,
    profile: dict,
    findings: list[Finding],
    today: _dt.date,
    notes: list[str],
    staged_snapshot: bool = False,
    exempt_from_placeholder: set[str] | None = None,
) -> None:
    """Prerequisite gates: artefact X must exist before activity Y may begin.

    The standard's other controls describe what a repository does. A gate describes
    what a repository may not do yet. That is a different and largely absent shape of
    control, and it is the shape both findings of the first profile review took.
    """
    # Defaulted here too: the parameter is optional, and `in None` would be a crash rather
    # than a missing exemption.
    exempt_from_placeholder = exempt_from_placeholder or set()
    level = str(profile.get("conformance_level", "")).strip()
    gates_raw = profile.get("prerequisites")

    if gates_raw is None:
        findings.append(
            Finding(
                "SP027",
                "The profile declares no prerequisite gates",
                "The 'prerequisites' block is absent.",
                "Add a 'prerequisites' block. It may be a short list, but it must exist: "
                "a repository that has decided it needs no gates should record that decision "
                "rather than leave the question unasked. See core/PREREQUISITE_GATES.md.",
                graceable=True,
            )
        )
        return

    if not isinstance(gates_raw, list):
        findings.append(
            Finding(
                "SP028",
                "The prerequisites block is malformed",
                f"'prerequisites' parsed as {type(gates_raw).__name__}, expected a list.",
                "See templates/application-profile.yaml for the shape.",
                graceable=True,
            )
        )
        return

    declared: dict[str, dict] = {}
    needs_hook_check = any(
        isinstance(gate, dict) and "local_hook" in (gate.get("enforcement") or [])
        for gate in gates_raw
    )
    hook_active, hook_detail = (
        active_pre_commit_hook(repo)
        if needs_hook_check
        else (True, "no gate claims local hook enforcement")
    )
    history_available = git_history_available(repo)
    exceptions = (
        load_staged_exceptions(repo, findings)
        if staged_snapshot
        else load_exceptions(repo, findings)
    ) if history_available else {}
    for index, gate in enumerate(gates_raw):
        if not isinstance(gate, dict):
            findings.append(
                Finding(
                    "SP028",
                    "A prerequisite gate is malformed",
                    f"prerequisites[{index}] parsed as {type(gate).__name__}, expected a mapping.",
                    "Each gate is a mapping with id, status, precondition and gated_activity.",
                    graceable=True,
                )
            )
            continue
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or not gate_id:
            findings.append(
                Finding(
                    "SP028",
                    "A prerequisite gate has no identifier",
                    f"prerequisites[{index}] has no 'id'.",
                    "Give the gate a catalogue id from core/PREREQUISITE_GATES.md, or a "
                    "repository-specific id with catalogue_id: custom.",
                    graceable=True,
                )
            )
            continue
        if gate_id in declared:
            findings.append(
                Finding(
                    "SP028",
                    f"Prerequisite gate '{gate_id}' is declared more than once",
                    "Duplicate gate identifiers make the effective decision ambiguous.",
                    "Declare each gate exactly once.",
                    graceable=True,
                )
            )
            continue
        declared[gate_id] = gate

        catalogue_id = gate.get("catalogue_id", gate_id)
        if catalogue_id != "custom" and gate_id not in GATE_CATALOGUE:
            findings.append(
                Finding(
                    "SP028",
                    f"Prerequisite gate '{gate_id}' is not in the catalogue",
                    f"'{gate_id}' is not a catalogue gate and catalogue_id is not 'custom'.",
                    "Use a catalogue id from core/PREREQUISITE_GATES.md, or set "
                    "catalogue_id: custom to declare a repository-specific gate.",
                    graceable=True,
                )
            )

        status = gate.get("status")
        if status not in GATE_STATUSES:
            findings.append(
                Finding(
                    "SP028",
                    f"Prerequisite gate '{gate_id}' has no usable status",
                    f"status is {status!r}.",
                    f"Set status to one of: {', '.join(sorted(GATE_STATUSES))}.",
                    graceable=True,
                )
            )
            continue

        rationale = gate.get("rationale")
        if status in {"deferred", "not_applicable"} and not (
            isinstance(rationale, str) and rationale.strip()
        ):
            findings.append(
                Finding(
                    "SP031",
                    f"Gate '{gate_id}' is {status} without a reason",
                    "A gate that does not apply, or does not apply yet, carries no rationale.",
                    "State why. 'not_applicable' is a legitimate answer and an unjustified one "
                    "is not.",
                    graceable=True,
                )
            )
        if status == "deferred":
            owner = gate.get("owner")
            revisit = gate.get("revisit_by")
            if not (isinstance(owner, str) and owner.strip()) or revisit is None:
                findings.append(
                    Finding(
                        "SP031",
                        f"Gate '{gate_id}' is deferred without an owner or a revisit date",
                        f"owner={owner!r}, revisit_by={revisit!r}.",
                        "A deferral with no owner and no date is an omission wearing a "
                        "decision's clothes. Give it both.",
                        graceable=True,
                    )
                )

        if status != "required":
            continue

        # An enforcement list that cannot be contradicted is decoration. The hook must be in
        # Git's active hooks directory, not merely present somewhere in the working tree.
        if "local_hook" in (gate.get("enforcement") or []) and not hook_active:
            findings.append(
                Finding(
                    "SP038",
                    f"Gate '{gate_id}' claims hook enforcement, but there is no hook",
                    f"enforcement lists 'local_hook', but {hook_detail}.",
                    f"Re-run the installer so {STANDARD_HOOKS_PATH}/pre-commit is installed and "
                    f"core.hooksPath is set to {STANDARD_HOOKS_PATH}, or remove the claim and "
                    "rely on the history audit. Claiming an inactive control is worse than not "
                    "having it.",
                    graceable=True,
                )
            )

        # From here on the gate is live, so its content must actually hold up.
        precondition = gate.get("precondition") or {}
        artefacts = [
            a for a in (precondition.get("artefacts") or []) if isinstance(a, str) and a
        ]
        for artefact in artefacts:
            target = repo / artefact
            staged_exists, staged_content = (
                staged_artefact(repo, artefact) if staged_snapshot else (False, None)
            )
            exists = staged_exists if staged_snapshot else target.exists()
            if not exists:
                findings.append(
                    Finding(
                        "SP032",
                        f"Gate '{gate_id}' requires an artefact that does not exist",
                        f"{artefact} is named as a precondition but is not present"
                        + (" in the staged snapshot." if staged_snapshot else "."),
                        "Create the artefact, correct the path, or change the gate's status. "
                        "A gate whose precondition cannot be satisfied is not a control.",
                        graceable=not (
                            staged_snapshot
                            and "local_hook" in (gate.get("enforcement") or [])
                        ),
                    )
                )
                continue
            if staged_snapshot and staged_content is not None:
                text = staged_content
            elif not staged_snapshot and target.is_file():
                try:
                    text = target.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    text = ""
            else:
                text = None
            if text is not None:
                if not text.strip():
                    findings.append(
                        Finding(
                            "SP032",
                            f"Gate '{gate_id}' names an empty precondition artefact",
                            f"{artefact} exists but is empty.",
                            "An empty file satisfies a path check and no one else.",
                            graceable=not (
                                staged_snapshot
                                and "local_hook" in (gate.get("enforcement") or [])
                            ),
                        )
                    )
                elif artefact in exempt_from_placeholder:
                    pass  # declared exempt; existence and non-emptiness were still checked
                elif PLACEHOLDER_PATTERN.search(text):
                    findings.append(
                        Finding(
                            "SP032",
                            f"Gate '{gate_id}' names an unfinished precondition artefact",
                            f"{artefact} still contains template placeholders.",
                            "Complete the artefact. A template is not a design policy.",
                            graceable=not (
                                staged_snapshot
                                and "local_hook" in (gate.get("enforcement") or [])
                            ),
                        )
                    )

        raw_effective = gate.get("effective_from")
        if raw_effective is None:
            findings.append(
                Finding(
                    "SP033",
                    f"Gate '{gate_id}' records no effective date",
                    "effective_from is absent.",
                    "Add 'effective_from: YYYY-MM-DD' - the date from which this gate binds. "
                    "History before that date is out of scope, which is what makes adoption "
                    "possible without rewriting the past.",
                    graceable=True,
                )
            )
            continue
        try:
            effective_from = _dt.date.fromisoformat(str(raw_effective)[:10])
        except ValueError:
            findings.append(
                Finding(
                    "SP033",
                    f"Gate '{gate_id}' has an unreadable effective date",
                    f"effective_from is {raw_effective!r}, which is not an ISO date.",
                    "Use the YYYY-MM-DD form.",
                    graceable=True,
                )
            )
            continue
        if effective_from > today:
            findings.append(
                Finding(
                    "SP033",
                    f"Gate '{gate_id}' is dated in the future",
                    f"effective_from is {effective_from.isoformat()}, which is after today.",
                    "A gate that binds later is a deferral. Set status: deferred with an owner "
                    "and a revisit_by date, and say so.",
                    graceable=True,
                )
            )
            continue

        earliest = earliest_declared_effective_from(repo, gate_id)
        if earliest is not None and effective_from > earliest:
            findings.append(
                Finding(
                    "SP034",
                    f"Gate '{gate_id}' has had its effective date moved forward",
                    f"effective_from is {effective_from.isoformat()}, but this gate previously "
                    f"declared {earliest.isoformat()} in the profile's own history.",
                    "Restore the earlier date. Moving it forward silently discards every "
                    "violation in between, which is the one way this control can be gamed from "
                    "inside the repository.",
                    graceable=False,
                )
            )
            continue

        if history_available:
            audit_gate_history(repo, gate, effective_from, exceptions, findings)

    required = LEVEL_REQUIRED_GATES.get(level, set())
    builds_ui = profile.get("builds_user_interface")

    if builds_ui is None:
        if level in LEVELS_REQUIRING_FULL_DECLARATION:
            findings.append(
                Finding(
                    "SP037",
                    "The profile does not say whether this repository builds a user interface",
                    "'builds_user_interface' is absent.",
                    "Add 'builds_user_interface: true' or 'false'. It decides whether the four "
                    "interface gates bind. The question is not optional at this level, because "
                    "the answer is the difference between a floor and no floor.",
                    graceable=True,
                )
            )
    elif not isinstance(builds_ui, bool):
        findings.append(
            Finding(
                "SP037",
                "'builds_user_interface' is not a yes or no",
                f"found {builds_ui!r}.",
                "Use true or false.",
                graceable=True,
            )
        )
    elif builds_ui:
        if level in LEVELS_REQUIRING_FULL_DECLARATION:
            required = required | DESIGN_GATES
        for gate_id in sorted(DESIGN_GATES):
            gate = declared.get(gate_id)
            if gate is not None and gate.get("status") == "not_applicable":
                findings.append(
                    Finding(
                        "SP037",
                        f"Gate '{gate_id}' is not_applicable in a repository that builds a UI",
                        "the profile declares builds_user_interface: true.",
                        "An interface gate cannot be inapplicable to a repository that builds "
                        "interfaces. Decide it required, or correct builds_user_interface.",
                        graceable=True,
                    )
                )
    else:
        for gate_id in sorted(DESIGN_GATES):
            gate = declared.get(gate_id)
            if gate is not None and gate.get("status") != "not_applicable":
                findings.append(
                    Finding(
                        "SP037",
                        f"Gate '{gate_id}' is {gate.get('status')} in a repository with no UI",
                        "the profile declares builds_user_interface: false.",
                        "If there is no interface these gates are not_applicable, and saying so "
                        "is a claim that can be checked. If there is one, correct "
                        "builds_user_interface rather than the gate.",
                        graceable=True,
                    )
                )

    for gate_id in sorted(required):
        gate = declared.get(gate_id)
        if gate is None:
            findings.append(
                Finding(
                    "SP029",
                    f"Conformance level '{level}' requires gate '{gate_id}'",
                    f"'{gate_id}' is absent from prerequisites. "
                    f"{GATE_CATALOGUE.get(gate_id, '')}",
                    f"Declare '{gate_id}' as required, or declare a lower conformance level.",
                    graceable=True,
                )
            )
            continue
        if gate.get("status") != "required":
            findings.append(
                Finding(
                    "SP030",
                    f"Conformance level '{level}' requires gate '{gate_id}' to be required",
                    f"found status {gate.get('status')!r}.",
                    f"Either decide '{gate_id}' as required, or declare a lower level.",
                    graceable=True,
                )
            )

    if level in LEVELS_REQUIRING_FULL_DECLARATION:
        undeclared = sorted(set(GATE_CATALOGUE) - set(declared))
        if undeclared:
            findings.append(
                Finding(
                    "SP029",
                    f"Conformance level '{level}' leaves catalogue gates undecided",
                    "not declared: " + ", ".join(undeclared[:8])
                    + (f" (and {len(undeclared) - 8} more)" if len(undeclared) > 8 else ""),
                    "Declare each one required, deferred or not_applicable with a reason. "
                    "A repository with no user interface should say so, not omit the question.",
                    graceable=True,
                )
            )

    auditable = [
        gate
        for gate in declared.values()
        if gate.get("status") == "required"
        and (gate.get("gated_activity") or {}).get("paths")
        and (gate.get("precondition") or {}).get("artefacts")
    ]
    if auditable and not history_available:
        notes.append(
            f"Git history was not available, so none of the {len(auditable)} auditable gate(s) "
            "were checked against the commits that crossed them. This is an absence of "
            "evidence, not evidence of conformance."
        )


def grace_state(record: dict, today: _dt.date) -> tuple[bool, str]:
    """Return (in_grace, human-readable explanation)."""
    installed_raw = str(record.get("first_installed_at") or record.get("installed_at", ""))[:10]
    try:
        installed = _dt.date.fromisoformat(installed_raw)
    except ValueError:
        return False, "the first-install date is unreadable, so no grace window applies"

    hard_cap = installed + _dt.timedelta(days=MAX_GRACE_DAYS)
    declared_raw = str(record.get("grace_expires", ""))[:10]
    try:
        declared = _dt.date.fromisoformat(declared_raw)
    except ValueError:
        return False, "no grace window is recorded"

    effective = min(declared, hard_cap)
    if today <= effective:
        remaining = (effective - today).days
        note = f"grace expires {effective.isoformat()} ({remaining} day(s) remaining)"
        if effective < declared:
            note += f"; capped at {MAX_GRACE_DAYS} days from install, ignoring the recorded "
            note += f"{declared.isoformat()}"
        return True, note
    return False, f"the grace window expired on {effective.isoformat()}"


# --- Entry point -------------------------------------------------------------


def run(repo: Path, today: _dt.date, no_grace: bool, staged: bool) -> int:
    findings: list[Finding] = []
    notes: list[str] = []

    # Bound before the branch below, because the level-reporting block after it runs whether
    # or not the standard is installed. Leaving it bound only inside the installed path made an
    # UNINSTALLED repository crash with UnboundLocalError before it could print SP001 - caught
    # by the two existing tests that check exactly that path.
    profile: dict | None = None

    record = check_install_record(repo, findings)
    if record is not None:
        check_integrity(repo, record, findings)
        check_conformance_block(repo, record, findings)
        check_workflow(repo, findings)
        if staged:
            check_staged_integrity(repo, findings)
            staged_profile, staged_error = load_staged_profile(repo)
            if staged_error:
                profile = None
                findings.append(
                    Finding(
                        "SP041",
                        "The staged application profile cannot be evaluated",
                        staged_error,
                        "Stage a readable application profile. The hook cannot enforce gates "
                        "against a fallback working-tree version.",
                        graceable=False,
                    )
                )
            else:
                profile = staged_profile
        else:
            profile = check_profile(repo, findings)
        if profile is not None:
            check_profile_schema(repo, profile, findings)
            check_profile_semantics(profile, findings, today, notes)
            check_secret_hygiene(repo, profile, findings)
            # Computed ONCE and shared. Calling it per consumer duplicated the advisory - two
            # exemptions produced four lines - which is noise that trains a reader to skim
            # exactly the output that says a control was narrowed.
            exempt = placeholder_exemptions(repo, profile, findings, notes)
            check_control_implementations(repo, profile, findings, notes, exempt)
            check_pattern_b_controls(repo, profile, findings, notes)
            check_pattern_c_controls(repo, profile, findings, notes)
            check_deferral_expiry(profile, findings, today, notes)
            check_pinned_identity(profile, record, findings)
            check_prerequisites(
                repo,
                profile,
                findings,
                today,
                notes,
                staged_snapshot=staged,
                exempt_from_placeholder=exempt,
            )
            if staged:
                check_staged_prerequisites(repo, profile, findings)

    print("Surfaceplate - conformance check")
    print(f"repository: {repo}")
    if record:
        print(f"standard  : {record.get('standard_version')} "
              f"installed {str(record.get('installed_at'))[:10]}")

    # F20 / DR-25. A reader who sees a level pass may reasonably infer that the controls that
    # level requires were checked. They were not: SP021/SP022 verify only that each is listed
    # and reads `required`. Saying so here, in the result itself, is what stops a pass being
    # read as more than it is - the verification arrives across four later packets, and this
    # line is removed control by control as each becomes genuinely checked.
    if profile is not None:
        level = profile.get("conformance_level")
        if isinstance(level, str) and level in CONFORMANCE_LEVELS:
            declared = sorted(CONFORMANCE_LEVELS[level] - VERIFIED_CONTROLS)
            if declared:
                print(f"level     : {level} - {len(declared)} of "
                      f"{len(CONFORMANCE_LEVELS[level])} required controls are DECLARED, "
                      f"not checked")
                print(f"            {', '.join(declared)}")
                print("            A pass does not establish these exist. See F20.")
    print()

    if notes:
        print(f"Advisory ({len(notes)}) - not a failure:")
        for note in notes:
            print(f"  - {note}")
        print()

    if not findings:
        print("PASS - all conformance checks satisfied.")
        return 0

    blocking = [f for f in findings if not f.graceable]
    graceable = [f for f in findings if f.graceable]

    if blocking:
        print(f"Blocking findings ({len(blocking)}) - never graced:")
        for finding in blocking:
            print(finding.render())
        print()
    if graceable:
        print(f"Adoption completeness findings ({len(graceable)}):")
        for finding in graceable:
            print(finding.render())
        print()

    if blocking:
        print("FAIL - the conformance check found findings that cannot be graced.")
        print("These findings indicate either an invalid staged change or an untrustworthy control.")
        return 1

    in_grace, note = (False, "grace disabled by --no-grace") if no_grace else grace_state(
        record or {}, today
    )
    if in_grace:
        print(f"WARN - adoption is incomplete, but {note}.")
        print("This check will fail once the grace window ends. Complete the profile before then.")
        return 0

    print(f"FAIL - adoption is incomplete and {note}.")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check conformance to Surfaceplate.")
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the repository to check (default: current directory).",
    )
    parser.add_argument(
        "--no-grace",
        action="store_true",
        help="Ignore any grace window and fail on any finding.",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Also check the staged snapshot for prerequisite gates the local hook blocks on.",
    )
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"error: {repo} is not a directory", file=sys.stderr)
        return 2
    if args.staged and not git_available(repo):
        print("error: --staged requires a readable Git repository", file=sys.stderr)
        return 2
    return run(repo, _dt.date.today(), args.no_grace, args.staged)


if __name__ == "__main__":
    raise SystemExit(main())
