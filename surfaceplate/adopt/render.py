"""Turn an assembled profile dict into the YAML this repository's own template teaches by example.

Not `yaml.safe_dump(profile)`. A flat dump is comment-less, and every profile in this repository -
the template, both worked examples, this repository's own - explains each field inline. `DR-32`
records why a bespoke renderer was chosen over that and over a `ruamel.yaml` dependency: the wizard
already knows exactly what it is writing, because it built every field from an answered question, so
it writes its own explanation as it goes, at roughly the template's own comment density - not the
examples' teaching-essay density, which would be excessive for a file a bespoke tool assembles.

**Correctness discipline.** `yaml.safe_dump` renders every individual VALUE (`_scalar`, `_block`) -
so escaping, quoting and block-scalar selection are PyYAML's problem, never hand-rolled string
interpolation guessing at what needs quoting. This module only places those correctly-rendered
values inside hand-written structure and comments. `render_profile` is never trusted on its own
output: `wizard.py` re-parses what this module returns and asserts it round-trips to an equivalent
structure before anything is written to disk, and validates the PARSED result against the schema -
never a string this module merely claims is correct.
"""

from __future__ import annotations

import yaml


def _strip_document_end(text: str) -> str:
    """PyYAML appends a literal `\\n...` document-end marker when a bare scalar is dumped as its
    own top-level document (a container does not get one - only a plain scalar is ambiguous
    without it per the YAML spec). `.strip()` alone does not remove it, because it is not trailing
    whitespace - it is real, embedded content that corrupts every hand-built line it lands in.
    Caught by the wizard's own round-trip verification the first time this was written without
    the fix: the assembled dict was correct, the rendered text was not, and re-parsing it failed
    outright rather than silently drifting - the fastest possible way to find this."""
    text = text.strip()
    if text.endswith("\n..."):
        text = text[: -len("\n...")]
    elif text == "...":
        text = ""
    return text


# A width wide enough that PyYAML never folds a plain scalar onto a continuation line. The
# default (80) did exactly that to a rationale sentence during this module's own first probe run:
# the continuation line landed at the indent PyYAML computed for a scalar dumped at column 0,
# which does not match where this renderer actually embeds it - the round-trip check caught it
# immediately, refusing to write rather than writing something subtly broken. It applies to values
# rendered as PLAIN scalars; prose that genuinely spans lines is emitted as a literal block scalar
# instead (`_block`), which is what the format has always allowed and this renderer once did not.
_NO_WRAP = 100_000


def _single_line(value: object) -> object:
    if isinstance(value, str) and "\n" in value:
        raise ValueError(
            f"a profile value contains a literal newline, which this renderer cannot embed safely: "
            f"{value!r}. The wizard's text prompts should never produce one - if this fires, "
            "something upstream let one through."
        )
    return value


def _scalar(value: object) -> str:
    """A single YAML value, correctly escaped and quoted by PyYAML - never guessed at by hand."""
    return _strip_document_end(
        yaml.safe_dump(_single_line(value), default_flow_style=True, width=_NO_WRAP)
    )


def _block(value: str, indent: int = 0) -> str:
    """A prose value, as a literal block scalar when it spans lines.

    `F38`: this used to refuse a newline outright, so pressing Enter in any rationale box produced
    a failure at the review screen after the whole interview had been answered. The restriction was
    never in the *format* - this repository's own shipped profiles use folded scalars seventeen
    times - only in this renderer, which interpolates values after a `key: ` prefix and so had
    nowhere to put a second line.

    PyYAML builds the scalar, including the awkward parts: `|2-` where the first line begins with a
    space, a quoted fallback where trailing whitespace means a literal block could not round-trip,
    and correct chomping so the value comes back byte-for-byte. This function's only job is to
    re-indent the continuation lines to wherever the key sits, since PyYAML indents from column 0
    and the call site may be nested. `wizard._verify`'s round-trip check is what proves the result.

    `indent` is the column of the KEY this value follows; content lands two columns further in.
    """
    multiline = isinstance(value, str) and "\n" in value
    text = _strip_document_end(
        yaml.safe_dump(value, width=_NO_WRAP, default_style="|" if multiline else None)
    )
    if "\n" not in text:
        return text
    head, *rest = text.split("\n")
    pad = " " * indent
    return "\n".join([head] + [pad + line if line else "" for line in rest])


def _flow_list(values: list[str]) -> str:
    """A one-line `[a, b, c]` YAML flow sequence, escaped by PyYAML for the structure it is
    actually part of - not built by wrapping brackets around individually-`_scalar()`-rendered
    items. `_scalar()` escapes a value correctly for a scalar that is its own document; a flow
    sequence has stricter rules for what an ITEM inside it needs quoted (for example a bare `?`
    is legal as a whole scalar document but not as one item among `[...]`). Hand-composing the
    two contexts is exactly the bug this replaces: a real adopter's `what is this?` rationale was
    lost outright because `artefacts: [{_scalar(value)}]` produced unparseable YAML. Dumping the
    whole Python list in one call lets PyYAML see the actual structure it is escaping for."""
    return _strip_document_end(yaml.safe_dump(values, default_flow_style=True, width=_NO_WRAP))


def _render_list_block(values: list[str], indent: int) -> str:
    if not values:
        return " []"
    lines = "\n".join(f"{' ' * indent}- {_scalar(v)}" for v in values)
    return "\n" + lines


def _render_gate(gate: dict) -> str:
    lines = [f"  - id: {gate['id']}", f"    status: {gate['status']}"]
    if gate["status"] == "required":
        lines.append(f"    effective_from: {_scalar(gate['effective_from'])}")
        lines.append("    precondition:")
        lines.append(f"      artefacts: {_flow_list(gate['precondition']['artefacts'])}")
        lines.append(f"      description: {_block(gate['precondition']['description'], 6)}")
        lines.append("    gated_activity:")
        lines.append(f"      paths: {_flow_list(gate['gated_activity']['paths'])}")
        lines.append(f"      description: {_block(gate['gated_activity']['description'], 6)}")
        lines.append(f"    enforcement: {_flow_list(gate['enforcement'])}")
    elif gate["status"] == "deferred":
        lines.append(f"    owner: {_scalar(gate['owner'])}")
        lines.append(f"    revisit_by: {_scalar(gate['revisit_by'])}")
        lines.append(f"    rationale: {_block(gate['rationale'], 4)}")
    else:
        lines.append(f"    rationale: {_block(gate['rationale'], 4)}")
    return "\n".join(lines)


def _assurance_note(control_id: str) -> str:
    """`# checked by ...` or `# declared - not machine-checked`, beside the control it describes.

    **`F53`.** A cross-provider reviewer read a profile and could not tell which controls the
    framework actually verifies: `actual_diff_review`, which nothing checks, and `dependency_lock`,
    which `SP051` checks, render as structurally identical objects. An adopter reading their own
    profile is the person most likely to over-read it, and this is the file they read.

    **Derived from the checker's own `VERIFIED_CONTROLS`, never restated here**, so the label cannot
    claim a control is checked after the checker stops checking it. That set was itself wrong when
    this was written - it omitted `secret_hygiene`, which `SP046`/`SP047` verify - and correcting it
    was a precondition for this label meaning anything.

    A comment, not a field: it is disclosure at the point of reading, and adding it as a value would
    put a framework-supplied string into the profile, which the binding rule forbids and
    `tests/test_provenance.py` would reject.
    """
    from surfaceplate.check_conformance import VERIFIED_CONTROLS

    if control_id in VERIFIED_CONTROLS:
        return "  # checked against this repository by the conformance checker"
    return "  # DECLARED ONLY - nothing checks this; it is a stated obligation"


def _render_control(control_id: str, entry: dict) -> str:
    lines = [
        f"  {control_id}:{_assurance_note(control_id)}",
        f"    decision: {entry['decision']}",
        f"    rationale: {_block(entry['rationale'], 4)}",
    ]
    if "implementation_reference" in entry:
        lines.append(f"    implementation_reference: {_scalar(entry['implementation_reference'])}")
    return "\n".join(lines)


def _render_deferrals(deferrals: list[dict]) -> str:
    if not deferrals:
        return " []"
    parts = []
    for d in deferrals:
        parts.append(
            f"    - control_id: {_scalar(d['control_id'])}\n"
            f"      rationale: {_block(d['rationale'], 6)}\n"
            f"      owner: {_scalar(d['owner'])}\n"
            f"      revisit_by: {_scalar(d['revisit_by'])}"
        )
    return "\n" + "\n".join(parts)


def render_profile(profile: dict, *, written_on: str = "") -> str:
    """The whole file, as text. See the module docstring for the correctness discipline this
    depends on `wizard.py` to enforce - this function only assembles what it is given.

    `F62` / `DR-47` (6): the header states what the provenance record contains and no more. The
    sentence *"Every value below was typed by a human answering a question"* is withdrawn - it
    stood above the framework's example prose, computed dates and derived text.
    """
    p = profile
    written_on = written_on or str(p["adoption"].get("adoption_date", ""))
    a = p["adoption"]
    bc = p["baseline_controls"]
    scanner = bc["secret_hygiene"]["scanner"]

    controls_text = "\n".join(_render_control(cid, e) for cid, e in p["control_decisions"].items())
    gates_text = "\n".join(_render_gate(g) for g in p["prerequisites"])
    roles_text = _render_list_block(p["human_roles"], 2)
    exclusions_text = _render_list_block(p["exclusions"], 2)
    deferrals_text = _render_deferrals(a["deferrals"])

    status_rationale_line = (
        f"\n  status_rationale: {_block(a['status_rationale'], 2)}" if a.get("status_rationale") else ""
    )
    independent_validator = _scalar(a["independent_validator"])

    return f"""\
# Application Profile — {p['display_name']}
#
# Written by `surfaceplate adopt` on {written_on}. The origin of every value below is recorded in
# application-profile.provenance.yaml beside this file: values marked typed there were entered at
# the keyboard; the rest were proposed by the tool from the sources recorded there and approved
# as one document at the review. See core/CONFORMANCE_LEVELS.md and core/PREREQUISITE_GATES.md
# for what each section means.

schema_version: "1.0"
application_id: {_scalar(p['application_id'])}
display_name: {_scalar(p['display_name'])}
owner: {_scalar(p['owner'])}

stack: {_scalar(p['stack'])}

risk_profile: {_block(p['risk_profile'], 0)}
materiality_definition: {_block(p['materiality_definition'], 0)}
data_classification: {p['data_classification']}         # public | internal | confidential | restricted

# See core/CONFORMANCE_LEVELS.md. A level is a floor, not a ceiling.
conformance_level: {p['conformance_level']}

adoption:
  framework_version: {_scalar(a['framework_version'])}
  framework_digest: {_scalar(a['framework_digest'])}
  adoption_date: {_scalar(a['adoption_date'])}
  review_by: {_scalar(a['review_by'])}
  framework_maintainer: {_scalar(a['framework_maintainer'])}
  repository_classification: {_scalar(a['repository_classification'])}
  decision_record_id: {_scalar(a['decision_record_id'])}
  adoption_status: {a['adoption_status']}{status_rationale_line}
  independent_validator: {independent_validator}
  deferrals:{deferrals_text}

# These three cannot be excluded, deferred, or omitted at any conformance level.
baseline_controls:
  agent_work_packets:{_assurance_note('agent_work_packets')}
    decision: required
    rationale: {_block(bc['agent_work_packets']['rationale'], 4)}
  actual_diff_review:{_assurance_note('actual_diff_review')}
    decision: required
    rationale: {_block(bc['actual_diff_review']['rationale'], 4)}
  secret_hygiene:{_assurance_note('secret_hygiene')}
    decision: required
    rationale: {_block(bc['secret_hygiene']['rationale'], 4)}
    scanner:
      name: {_scalar(scanner['name'])}
      wired_in: {_flow_list(scanner['wired_in'])}
      notes: {_block(scanner['notes'], 6)}

control_decisions:
{controls_text}

# Prerequisite gates: "artefact X must exist before activity Y may begin". See
# core/PREREQUISITE_GATES.md for the 19-gate catalogue and what each one guards.
builds_user_interface: {str(p['builds_user_interface']).lower()}
prerequisites:
{gates_text}

human_roles:{roles_text}
release_route: {_block(p['release_route'], 0)}
exclusions:{exclusions_text}
"""
