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
# immediately, refusing to write rather than writing something subtly broken. Every value this
# renderer emits must be single-line for the same reason a value with an embedded newline (below)
# is refused outright: the whole design is string interpolation after a `key: ` prefix, which is
# only safe for single-line content.
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


def _block(value: str) -> str:
    """A string value, letting PyYAML choose plain/quoted/block style based on its content."""
    return _strip_document_end(yaml.safe_dump(_single_line(value), width=_NO_WRAP))


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
        lines.append(f"      artefacts: [{_scalar(gate['precondition']['artefacts'][0])}]")
        lines.append(f"      description: {_block(gate['precondition']['description'])}")
        lines.append("    gated_activity:")
        lines.append(f"      paths: [{_scalar(gate['gated_activity']['paths'][0])}]")
        lines.append(f"      description: {_block(gate['gated_activity']['description'])}")
        enforcement = ", ".join(gate["enforcement"])
        lines.append(f"    enforcement: [{enforcement}]")
    elif gate["status"] == "deferred":
        lines.append(f"    owner: {_scalar(gate['owner'])}")
        lines.append(f"    revisit_by: {_scalar(gate['revisit_by'])}")
        lines.append(f"    rationale: {_block(gate['rationale'])}")
    else:
        lines.append(f"    rationale: {_block(gate['rationale'])}")
    return "\n".join(lines)


def _render_control(control_id: str, entry: dict) -> str:
    lines = [f"  {control_id}:", f"    decision: {entry['decision']}", f"    rationale: {_block(entry['rationale'])}"]
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
            f"      rationale: {_block(d['rationale'])}\n"
            f"      owner: {_scalar(d['owner'])}\n"
            f"      revisit_by: {_scalar(d['revisit_by'])}"
        )
    return "\n" + "\n".join(parts)


def render_profile(profile: dict) -> str:
    """The whole file, as text. See the module docstring for the correctness discipline this
    depends on `wizard.py` to enforce - this function only assembles what it is given."""
    p = profile
    a = p["adoption"]
    bc = p["baseline_controls"]
    scanner = bc["secret_hygiene"]["scanner"]

    controls_text = "\n".join(_render_control(cid, e) for cid, e in p["control_decisions"].items())
    gates_text = "\n".join(_render_gate(g) for g in p["prerequisites"])
    roles_text = _render_list_block(p["human_roles"], 2)
    exclusions_text = _render_list_block(p["exclusions"], 2)
    deferrals_text = _render_deferrals(a["deferrals"])

    status_rationale_line = (
        f"\n  status_rationale: {_block(a['status_rationale'])}" if a.get("status_rationale") else ""
    )
    independent_validator = _scalar(a["independent_validator"])

    return f"""\
# Application Profile — {p['display_name']}
#
# Written by `surfaceplate adopt`. Every value below was typed by a human answering a question;
# nothing here was inferred, defaulted silently, or chosen by the wizard. See
# core/CONFORMANCE_LEVELS.md and core/PREREQUISITE_GATES.md for what each section means.

schema_version: "1.0"
application_id: {_scalar(p['application_id'])}
display_name: {_scalar(p['display_name'])}
owner: {_scalar(p['owner'])}

stack: {_scalar(p['stack'])}

risk_profile: {_block(p['risk_profile'])}
materiality_definition: {_block(p['materiality_definition'])}
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
  agent_work_packets:
    decision: required
    rationale: {_block(bc['agent_work_packets']['rationale'])}
  actual_diff_review:
    decision: required
    rationale: {_block(bc['actual_diff_review']['rationale'])}
  secret_hygiene:
    decision: required
    rationale: {_block(bc['secret_hygiene']['rationale'])}
    scanner:
      name: {_scalar(scanner['name'])}
      wired_in: [{_scalar(scanner['wired_in'][0])}]
      notes: {_block(scanner['notes'])}

control_decisions:
{controls_text}

# Prerequisite gates: "artefact X must exist before activity Y may begin". See
# core/PREREQUISITE_GATES.md for the 19-gate catalogue and what each one guards.
builds_user_interface: {str(p['builds_user_interface']).lower()}
prerequisites:
{gates_text}

human_roles:{roles_text}
release_route: {_block(p['release_route'])}
exclusions:{exclusions_text}
"""
