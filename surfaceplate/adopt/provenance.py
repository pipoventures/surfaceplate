"""Where every value in a written profile came from, and the machine-owned record that says so.

`DR-47` decides the shape. A value is *asked* when it is presented to the human with its origin
and the human can change it before the profile is written; the annotated review is one way to
present it. The tool may propose from six sources - `typed`, `discovered`, `example`, `computed`,
`fact of record`, `scaffolded` - and must record, for every field it wrote, which one. It never
records a proposed value as typed. The record lives beside the profile as
`governance/application-profile.provenance.yaml`: a sidecar rather than comments in the profile,
because `yaml.safe_load` drops comments, any round-trip drops them, and a comment is one keystroke
from gone (the review's second reviewer, Part II §II.6).

Two things live here:

- `trace` maps every leaf of an assembled profile to an `Origin`, by a rule table from profile
  path to the answer that produced it. The table is checked by `tests/test_provenance.py`, which
  fails on any leaf the table does not reach - so the mapping cannot drift silently from the
  builders in `sections.py` (`F55`'s class).
- `record` and `render_record` write the sidecar: one entry per profile path, the framework
  version, one document-level approval line with its timestamp, and any bulk gate decision as one
  human act with its count.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field

import yaml

PROVENANCE_PATH = "governance/application-profile.provenance.yaml"
RECORD_SCHEMA_VERSION = "1.0"

TYPED = "typed"
DISCOVERED = "discovered"
EXAMPLE = "example"
COMPUTED = "computed"
FACT = "fact of record"
SCAFFOLDED = "scaffolded"
KINDS = (TYPED, DISCOVERED, EXAMPLE, COMPUTED, FACT, SCAFFOLDED)


@dataclass(frozen=True)
class Origin:
    """One value's origin. `detail` says from what (a path, a rule); `at` is set only for a
    value typed on the review, which `DR-47` (3) asks to be timestamped."""

    kind: str
    detail: str = ""
    at: str = ""

    def label(self) -> str:
        """The short tag the review shows beside a line."""
        if self.kind == COMPUTED and self.detail.startswith("= "):
            return f"{COMPUTED}: {self.detail}"
        return self.kind


def now_iso() -> str:
    return _dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


# ---------------------------------------------------------------------------------------------
# The rule table: profile path -> where the value came from
# ---------------------------------------------------------------------------------------------

# A rule is either an answer key ("<section>.<field>") whose recorded origin applies, or a fixed
# `Origin` for a value the builders supply themselves. Gate rules take the gate id; control rules
# the control id. Order matters only in that the first matching pattern wins.
_CONSTANT = {
    "schema_version": Origin(COMPUTED, "the schema version this wizard writes"),
    "adoption.framework_version": Origin(FACT, "read from .standards/INSTALL.json"),
    "adoption.framework_digest": Origin(FACT, "read from .standards/INSTALL.json"),
    "adoption.adoption_date": Origin(FACT, "the date adopt wrote this profile"),
    "adoption.deferrals": Origin(COMPUTED, "nothing can be deferred through the wizard"),
    "baseline_controls.secret_hygiene.scanner.notes": Origin(COMPUTED, "the framework's own note"),
    "exclusions": Origin(COMPUTED, "nothing is excluded through the wizard"),
}

_DIRECT = {
    "application_id": "identity.application_id",
    "display_name": "identity.display_name",
    "owner": "identity.owner",
    "stack.language": "stack.language",
    "builds_user_interface": "stack.builds_user_interface",
    "risk_profile": "risk.risk_profile",
    "materiality_definition": "risk.materiality_definition",
    "data_classification": "risk.data_classification",
    "conformance_level": "level.conformance_level",
    "adoption.review_by": "adoption.review_by",
    "adoption.framework_maintainer": "adoption.framework_maintainer",
    "adoption.repository_classification": "adoption.repository_classification",
    "adoption.decision_record_id": "adoption.decision_record_id",
    "adoption.adoption_status": "adoption.adoption_status",
    "adoption.status_rationale": "adoption.status_rationale",
    "adoption.independent_validator": "adoption.independent_validator",
    "baseline_controls.secret_hygiene.scanner.name": "controls.scanner.name",
    "baseline_controls.secret_hygiene.scanner.wired_in": "controls.scanner.wired_in",
    "release_route": "wrap.release_route",
    "human_roles": "wrap.human_roles",
}

_BASELINE = re.compile(r"^baseline_controls\.([a-z_]+)\.(decision|rationale)$")
_CONTROL = re.compile(r"^control_decisions\.([a-z0-9_-]+)\.(decision|rationale|implementation_reference)$")
_GATE = re.compile(r"^prerequisites\[(\d+)\]\.(.+)$")

# Which values are decided on their own screen and cannot be edited on the review: changing one
# would change which other fields exist. The review says so beside them.
NOT_EDITABLE_ON_REVIEW = {
    "conformance_level": "chosen on the level screen",
    "builds_user_interface": "decided on the decisions screen; it settles the design gates",
}


def _index_free(path: str) -> str:
    """`human_roles[2]` -> `human_roles`; `...artefacts[0]` -> `...artefacts`."""
    return re.sub(r"\[\d+\]$", "", path)


def answer_key_for(path: str, profile: dict) -> tuple[str | None, Origin | None]:
    """`(answer key, fixed origin)` for one profile leaf path. Exactly one of the two is set.

    Raises `KeyError` for a path the table does not reach, which is the whole point: a builder
    that starts writing a field this table does not know fails `tests/test_provenance.py` rather
    than shipping an unrecorded value.
    """
    bare = _index_free(path)
    if bare in _CONSTANT:
        return None, _CONSTANT[bare]
    if bare in _DIRECT:
        return _DIRECT[bare], None

    m = _BASELINE.match(bare)
    if m:
        control_id, leaf = m.groups()
        if leaf == "decision":
            return None, Origin(COMPUTED, "required at every level")
        return f"controls.{control_id}.rationale", None

    m = _CONTROL.match(bare)
    if m:
        control_id, leaf = m.groups()
        if leaf == "decision":
            return None, Origin(COMPUTED, "the level's floor, or declared above it by you")
        return f"controls.{control_id}.{leaf}", None

    m = _GATE.match(bare)
    if m:
        index, leaf = int(m.group(1)), m.group(2)
        gate_id = profile["prerequisites"][index]["id"]
        if leaf == "id":
            return None, Origin(COMPUTED, "the gate catalogue")
        if leaf == "status":
            return f"gates.{gate_id}.status", None
        if leaf == "precondition.artefacts":
            return f"gates.{gate_id}.artefact", None
        if leaf == "precondition.description":
            return f"gates.{gate_id}.precondition_description", None
        if leaf == "gated_activity.paths":
            return f"gates.{gate_id}.paths", None
        if leaf == "gated_activity.description":
            return f"gates.{gate_id}.gated_description", None
        if leaf in ("effective_from", "enforcement", "owner", "revisit_by", "rationale"):
            return f"gates.{gate_id}.{leaf}", None
    raise KeyError(f"no provenance rule reaches profile path {path!r}")


# Values `sections.py` derives when the answer is absent; these are the origins recorded then.
_DERIVED_WHEN_ABSENT = {
    "precondition_description": Origin(COMPUTED, "the framework's own definition of the gate"),
    "gated_description": Origin(COMPUTED, "= the gated paths"),
    "enforcement": Origin(COMPUTED, "history audit and review, the two needing no tooling"),
    "status": Origin(COMPUTED, "settled by the level, or by having no user interface"),
    "independent_validator": Origin(COMPUTED, "no independent review declared"),
}


def leaves(node: object, path: str = "") -> list[tuple[str, object]]:
    """Every scalar leaf of a profile with its dotted path. A list of scalars yields one leaf per
    element (`human_roles[0]`); an empty list yields the list itself, so it still has an origin."""
    out: list[tuple[str, object]] = []
    if isinstance(node, dict):
        for key, value in node.items():
            out.extend(leaves(value, f"{path}.{key}" if path else str(key)))
    elif isinstance(node, list):
        if not node:
            out.append((path, node))
        for index, value in enumerate(node):
            out.extend(leaves(value, f"{path}[{index}]"))
    else:
        out.append((path, node))
    return out


def trace(profile: dict, state: dict, origins: dict[str, Origin]) -> dict[str, Origin]:
    """An `Origin` for every leaf of `profile`.

    `origins` is keyed by answer key. A leaf whose answer key has a recorded origin takes it; a
    leaf whose answer is absent and derived by the builders takes the derived origin; a leaf the
    table reaches as a constant takes that. A leaf with an answer in `state` but no recorded
    origin is an error, never silently `typed`: that is `DR-47` (3) enforced at the seam.
    """
    result: dict[str, Origin] = {}
    for path, _value in leaves(profile):
        key, fixed = answer_key_for(path, profile)
        if fixed is not None:
            result[path] = fixed
            continue
        assert key is not None
        if key in origins:
            result[path] = origins[key]
            continue
        section, _, field_id = key.partition(".")
        answered = field_id in (state.get(section) or {})
        leaf = field_id.rsplit(".", 1)[-1]
        if not answered and leaf in _DERIVED_WHEN_ABSENT:
            result[path] = _DERIVED_WHEN_ABSENT[leaf]
            continue
        raise KeyError(f"{path}: answer {key!r} has no recorded origin")
    return result


# ---------------------------------------------------------------------------------------------
# The record
# ---------------------------------------------------------------------------------------------


@dataclass
class BulkDecision:
    """One explicit bulk command - a human making N scope decisions in one recorded act."""

    status: str
    count: int
    at: str = field(default_factory=now_iso)


def record(
    traced: dict[str, Origin],
    *,
    framework_version: str,
    approved_at: str,
    bulk: list[BulkDecision] | None = None,
) -> dict:
    """The sidecar's content, as data: origin per profile path, the version, one approval line."""
    fields: dict[str, dict] = {}
    for path, origin in traced.items():
        entry: dict = {"origin": origin.kind}
        if origin.detail:
            entry["detail"] = origin.detail
        if origin.at:
            entry["typed_at"] = origin.at
        fields[path] = entry
    out: dict = {
        "schema_version": RECORD_SCHEMA_VERSION,
        "profile": "application-profile.yaml",
        "framework_version": framework_version,
        "approved_at": approved_at,
        "fields": fields,
    }
    if bulk:
        out["bulk_decisions"] = [
            {"status": b.status, "count": b.count, "at": b.at} for b in bulk
        ]
    return out


def render_record(data: dict) -> str:
    header = (
        "# Machine-owned. Written by `surfaceplate adopt`; do not edit by hand.\n"
        "#\n"
        "# For every field of application-profile.yaml, where its value came from:\n"
        "#   typed            entered at the keyboard (typed_at is set for an edit made on the review)\n"
        "#   discovered       read out of this repository\n"
        "#   example          this framework's own worked example, shown and reviewed\n"
        "#   computed         derived from an answer already given, or from a fixed rule\n"
        "#   fact of record   a date, a version, a digest\n"
        "#   scaffolded       a file this tool created and therefore knows\n"
        "# Approval is recorded once, for the whole document, at the review.\n"
        "\n"
    )
    return header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)


def summarise(traced: dict[str, Origin]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for origin in traced.values():
        counts[origin.kind] = counts.get(origin.kind, 0) + 1
    return counts
