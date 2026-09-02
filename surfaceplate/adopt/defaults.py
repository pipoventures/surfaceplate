"""Proposed answers, each with the origin it will be recorded under.

`DR-40` created this module to propose what the adopter chose not to type; `DR-47` makes it the
rule for every value the wizard writes. This module **proposes**; it never decides. Every value it
produces is shown on the review with where it came from, the human can change any of them, and
the origin is recorded in `governance/application-profile.provenance.yaml` exactly as proposed -
never as typed (`provenance.py`).

**A proposal is only made where there is something honest to propose.** The sources `DR-47` (2)
names, and nothing else:

- **discovered** - a real path, directory or CI step read out of this repository (`discover.py`),
  never one this framework installed (`F61`);
- **example** - the worked prose this framework already ships for that control or gate
  (`example_answers.py`);
- **computed** - a value derived from a fact or from an answer already given: today's date, the
  review horizon, a maintainer taken from the owner already given, a classification copied from
  the one already chosen;
- **fact of record** and **scaffolded** are recorded by `provenance.py` and `flow.py` rather
  than proposed here.

**What is never proposed.** A scope decision: a gate's status - `not_applicable` included - is a
key a human presses, singly or in one recorded bulk act (`DR-47` (4)). `F62` is what proposing
those cost: fifteen example rationales made true by assertion under a header claiming human
authorship. A field with no honest source is **left unanswered and still asked**.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass
from pathlib import Path

from surfaceplate.adopt import catalogue, detect, discover, example_answers, plan, provenance

# The framework's own sentence for a prose field the human left blank on the decisions form. It
# is written as computed - from the fact that nothing was stated - and is one edit on the review.
# `DR-47` accepted the prototype that wrote exactly this (report Part II §II.1).
NOT_STATED = "Not stated at adoption."


@dataclass(frozen=True)
class Proposal:
    """One proposed answer, and where it came from - the origin is shown, never just the value."""

    field: str  # "<section>.<field id>"
    value: object
    origin: str  # one of provenance.KINDS other than "typed"
    detail: str  # the human-readable reason, shown on the review

    def describe(self) -> str:
        return f"{self.field} = {self.value!r}  ({self.detail})"

    def as_origin(self) -> provenance.Origin:
        return provenance.Origin(self.origin, self.detail)


def slug(name: str) -> str:
    """A directory name as an `application_id` the schema accepts, or `""` if nothing survives."""
    text = re.sub(r"[^a-z0-9_-]+", "-", name.strip().lower()).strip("-")
    text = re.sub(r"-{2,}", "-", text)
    if len(text) < 2 or not re.match(r"^[a-z0-9]", text):
        return ""
    return text


# ---------------------------------------------------------------------------------------------
# Before the decisions form: what the form can show pre-filled
# ---------------------------------------------------------------------------------------------


def propose_identity(repo: Path) -> list[Proposal]:
    """The directory's own name, as the id and the display name. Both are one edit."""
    out: list[Proposal] = []
    name = repo.resolve().name
    ident = slug(name)
    if ident:
        out.append(
            Proposal("identity.application_id", ident, provenance.COMPUTED, "= the directory name")
        )
    if name.strip():
        out.append(
            Proposal("identity.display_name", name, provenance.COMPUTED, "= the directory name")
        )
    return out


def propose_stack(repo: Path) -> list[Proposal]:
    languages = detect.detect_languages(repo)
    if not languages:
        return []
    return [
        Proposal(
            "stack.language",
            ", ".join(languages),
            provenance.DISCOVERED,
            "language markers found in this repository",
        )
    ]


# ---------------------------------------------------------------------------------------------
# After the decisions form and the level: everything else
# ---------------------------------------------------------------------------------------------


def propose_risk(risk_answers: dict) -> list[Proposal]:
    """The two prose fields the decisions form leaves optional. `NOT_STATED` where blank."""
    out: list[Proposal] = []
    if not str(risk_answers.get("risk_profile") or "").strip():
        out.append(
            Proposal(
                "risk.risk_profile", NOT_STATED, provenance.COMPUTED, "left blank on the decisions form"
            )
        )
    if not str(risk_answers.get("materiality_definition") or "").strip():
        out.append(
            Proposal(
                "risk.materiality_definition",
                NOT_STATED,
                provenance.COMPUTED,
                "not asked before the review; one edit here",
            )
        )
    return out


def propose_controls(*, level: str, mode: str, found: discover.Discovered) -> list[Proposal]:
    """Rationales from the worked examples; references from what is really in the repository."""
    out: list[Proposal] = []
    section = plan.controls_plan(level=level, mode=mode, found=found)
    floor = catalogue.CONFORMANCE_LEVELS[level]

    for spec in section.fields:
        key = f"controls.{spec.id}"
        if spec.id == "above_floor":
            # Nothing above the floor unless a human ticks it: a level is a floor, and quietly
            # opting an adopter into controls they did not ask for would be the tool choosing
            # their scope. Presented on the remainder form, so this is the value when left unticked.
            out.append(
                Proposal(key, [], provenance.COMPUTED, "nothing beyond this level's floor is declared")
            )
            continue
        if spec.id.endswith(".rationale"):
            control_id = spec.id.rsplit(".", 1)[0]
            example = example_answers.rationale_example(control_id)
            if example and (control_id in floor or control_id in plan.BASELINE_CONTROL_IDS):
                out.append(
                    Proposal(key, example, provenance.EXAMPLE, "this framework's own worked example")
                )
            continue
        if spec.id.endswith(".implementation_reference"):
            if spec.choices:
                out.append(
                    Proposal(key, spec.choices[0][0], provenance.DISCOVERED, f"found: {spec.choices[0][0]}")
                )
            continue
        if spec.id == "scanner.name":
            out.append(Proposal(key, spec.default, provenance.EXAMPLE, "the scanner the examples name"))
        elif spec.id == "scanner.wired_in" and spec.choices:
            out.append(
                Proposal(key, spec.choices[0][0], provenance.DISCOVERED, f"found: {spec.choices[0][0]}")
            )
    return out


def propose_gates(
    *, level: str, builds_ui: bool, mode: str, found: discover.Discovered, adoption_date: str
) -> list[Proposal]:
    """A precondition for every gate that could be `required`, and nothing for any status.

    `DR-47` (4): the tool never supplies a scope decision, `not_applicable` included. `DR-47` (5):
    `effective_from` is proposed as the adoption date and recorded as computed unless changed - the
    value is shown, and a human can only widen the audit window from it (`SP033`, `SP034`).
    """
    out: list[Proposal] = []
    for spec in plan.gate_plan(level=level, builds_ui=builds_ui, mode=mode, found=found):
        prefix = f"gates.{spec.id}"
        # A gate settled `not_applicable` by an earlier answer needs no precondition.
        if spec.auto_status:
            continue
        # `F40`: MATCHED, not merely ranked - a proposal comes only from a candidate that matched
        # the gate. No match -> no proposal, and the field is asked.
        matched = discover.matched_for_gate(found.artefacts, spec.id)
        if matched:
            out.append(
                Proposal(
                    f"{prefix}.artefact",
                    matched[0],
                    provenance.DISCOVERED,
                    f"the closest match in this repository: {matched[0]}",
                )
            )
        # `F61`: only when discovery found a directory of the adopter's own.
        if found.paths:
            out.append(
                Proposal(
                    f"{prefix}.paths",
                    found.paths[0],
                    provenance.DISCOVERED,
                    "this repository's main source directory",
                )
            )
        out.append(
            Proposal(
                f"{prefix}.effective_from",
                adoption_date,
                provenance.COMPUTED,
                "= the adoption date; an earlier date audits more history",
            )
        )
    return out


def propose_adoption(*, owner: str, data_classification: str) -> list[Proposal]:
    """Only what can be derived from a fact or an answer already given."""
    return [
        Proposal(
            "adoption.review_by",
            (_dt.date.today() + _dt.timedelta(days=180)).isoformat(),
            provenance.COMPUTED,
            "180 days from today, the interval this framework suggests",
        ),
        Proposal("adoption.framework_maintainer", owner, provenance.COMPUTED, "= owner"),
        Proposal(
            "adoption.repository_classification",
            data_classification,
            provenance.COMPUTED,
            "= data_classification",
        ),
        Proposal(
            "adoption.adoption_status",
            "in_progress",
            provenance.COMPUTED,
            "adopt has just written the profile; the checker has not yet passed against it",
        ),
        Proposal(
            "adoption.needs_validator", False, provenance.COMPUTED, "no independent review declared"
        ),
    ]


def propose_wrap() -> list[Proposal]:
    return [
        Proposal("wrap.human_roles", "", provenance.COMPUTED, "none stated; one edit here"),
    ]


def propose_after_level(
    state: dict, *, found: discover.Discovered, adoption_date: str
) -> list[Proposal]:
    """Everything proposable once the level is known."""
    level = state["level"]["conformance_level"]
    builds_ui = bool(state["stack"]["builds_user_interface"])
    mode = state["mode"]["mode"]
    owner = str(state["identity"].get("owner") or "")
    classification = str(state["risk"].get("data_classification") or "")
    return [
        *propose_controls(level=level, mode=mode, found=found),
        *propose_gates(
            level=level, builds_ui=builds_ui, mode=mode, found=found, adoption_date=adoption_date
        ),
        *propose_adoption(owner=owner, data_classification=classification),
        *propose_wrap(),
    ]
