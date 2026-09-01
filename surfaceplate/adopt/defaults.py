"""Proposed answers for the sections an adopter chose not to walk through one at a time.

`DR-40` records the shape and its one hard constraint. This module **proposes**; it never decides.
Every value it produces is shown on a review screen, with where it came from, and none of it
reaches disk until a human approves that screen. That is what keeps `org/RELEASE_PLAN.md`'s binding
rule intact - *it asks, the human answers, the tool writes* - and what keeps
`tests/test_provenance.py`'s allow-list from having to grow: an approved proposal is an answer,
submitted the same way a shown default in a text box has always been.

The maintainer asked for this after finishing a real adoption and finding the volume, not the
wording, was the problem: *"we should have a first set of windows asking for the absolutely minimum
information and then offer: Set defaults and Customise adoption."*

**A proposal is only made where there is something honest to propose.** Three sources, and nothing
else:

- **discovered** - a real path, directory or CI step read out of this repository (`discover.py`);
- **example** - the worked prose this framework already ships for that control or gate
  (`example_answers.py`), which is what a blank rationale box already offers today;
- **computed** - a value derived from a fact, not invented: today's date, the review horizon, a
  maintainer taken from the owner already given.

A field with no honest source is **left unanswered and still asked**. Filling it would mean the
tool authoring a judgement, which is the one thing this package exists not to do.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass

from surfaceplate.adopt import catalogue, discover, example_answers, plan


@dataclass(frozen=True)
class Proposal:
    """One proposed answer, and where it came from - the origin is shown, never just the value."""

    field: str  # "<section>.<field id>"
    value: object
    origin: str  # "discovered" | "example" | "computed"
    detail: str  # the human-readable reason, shown on the review screen

    def describe(self) -> str:
        return f"{self.field} = {self.value!r}  ({self.detail})"


def _first(candidates, fallback: str = "") -> str:
    return candidates[0] if candidates else fallback


def propose_controls(*, level: str, mode: str, found: discover.Discovered) -> list[Proposal]:
    """Rationales from the worked examples; references from what is really in the repository."""
    out: list[Proposal] = []
    section = plan.controls_plan(level=level, mode=mode, found=found)
    floor = catalogue.CONFORMANCE_LEVELS[level]

    for spec in section.fields:
        key = f"controls.{spec.id}"
        if spec.id == "above_floor":
            # Nothing above the floor. A level is a floor, and quietly opting an adopter into
            # controls they did not ask for would be the tool choosing their scope. `ACT-032` made
            # this ONE proposal where it used to be one per control - the wizard was computing this
            # same answer eight times over while also asking the adopter for it eight times.
            out.append(
                Proposal(key, [], "computed", "nothing beyond this level's floor is declared")
            )
            continue
        if spec.id.endswith(".declared"):  # pre-`ACT-032` shape, still honoured
            out.append(Proposal(key, False, "computed", "above this level's floor, so not declared"))
            continue

        if spec.id.endswith(".rationale"):
            control_id = spec.id.rsplit(".", 1)[0]
            example = example_answers.rationale_example(control_id)
            if example and (control_id in floor or control_id in plan.BASELINE_CONTROL_IDS):
                out.append(
                    Proposal(key, example, "example", "this framework's own worked example")
                )
            continue

        if spec.id.endswith(".implementation_reference"):
            if spec.choices:
                value = spec.choices[0][0]
                out.append(
                    Proposal(key, value, "discovered", "found in this repository")
                )
            continue

        if spec.id == "scanner.name":
            out.append(Proposal(key, spec.default, "example", "the scanner the examples name"))
        elif spec.id == "scanner.wired_in" and spec.choices:
            out.append(
                Proposal(key, spec.choices[0][0], "discovered", "a workflow file in this repository")
            )
    return out


def propose_gates(*, level: str, builds_ui: bool, mode: str, found: discover.Discovered) -> list[Proposal]:
    """A status for every gate, and a precondition for the ones that need one.

    Gates the level does not require are proposed `not_applicable` with the framework's own example
    rationale. That is a real decision an adopter must own, which is exactly why it is proposed on a
    review screen rather than written.
    """
    out: list[Proposal] = []
    today = _dt.date.today().isoformat()

    for spec in plan.gate_plan(level=level, builds_ui=builds_ui, mode=mode, found=found):
        prefix = f"gates.{spec.id}"
        status = "required" if spec.mandatory else (spec.auto_status or "not_applicable")

        if not spec.mandatory and not spec.auto_status:
            out.append(
                Proposal(
                    f"{prefix}.status",
                    "not_applicable",
                    "computed",
                    f"{level} does not require this gate; declare it if it applies to you",
                )
            )

        if status == "required":
            # `F40`: MATCHED, not merely ranked. `rank_for_gate` returns every candidate so the
            # dropdown offers everything; its first entry is the best *available* one, which in a
            # repository with nothing relevant is just the only file. Proposing that produced a
            # gate satisfying `SP032` while guarding nothing. No match -> no proposal, and
            # `unanswered()` asks.
            matched = discover.matched_for_gate(found.artefacts, spec.id)
            if matched:
                out.append(
                    Proposal(
                        f"{prefix}.artefact",
                        matched[0],
                        "discovered",
                        "the closest match in this repository for this gate",
                    )
                )
            out.append(
                Proposal(
                    f"{prefix}.paths",
                    _first(found.paths, "**"),
                    "discovered",
                    "this repository's main source directory",
                )
            )
            # `F51`: `effective_from` is asked again, so it is PROPOSED again - today's date, as a
            # computed fact, shown on the defaults screen and written only once a human passes it.
            # That is the distinction the amended binding rule turns on: proposing a fact a human
            # approves is not the same act as writing one nobody was shown, which is what
            # `ACT-032` did and what the review caught.
            #
            # `enforcement` and both description fields remain derived and are not proposed:
            # proposing a value for a field no adopter is shown would put rows on the review screen
            # that correspond to no question.
            out.append(
                Proposal(
                    f"{prefix}.effective_from",
                    today,
                    "computed",
                    "today - history before it is out of scope; an earlier date audits more",
                )
            )
        else:
            example = example_answers.rationale_example(spec.id)
            if example:
                out.append(
                    Proposal(f"{prefix}.rationale", example, "example", "this framework's own worked example")
                )
            else:
                # `ACT-034`: a field's OWN shipped default was never proposed, so a repository with
                # no user interface was asked to hand-write four rationales saying it has no user
                # interface - text the wizard already holds, derived from `builds_user_interface`
                # which the adopter had already answered. That was 4 of the 14 questions the
                # defaults route still asked. `computed` is the honest origin: it comes from an
                # answer already given, not from invention.
                for field in spec.fields:
                    if field.id == "rationale" and field.default:
                        out.append(
                            Proposal(
                                f"{prefix}.rationale",
                                field.default,
                                "computed",
                                "follows from an answer you already gave",
                            )
                        )
    return out


def propose_adoption(*, owner: str) -> list[Proposal]:
    """Only what can be derived from a fact. `decision_record_id` is deliberately absent: there is
    no honest way to invent an identifier for a record that may not exist."""
    return [
        Proposal(
            "adoption.review_by",
            (_dt.date.today() + _dt.timedelta(days=180)).isoformat(),
            "computed",
            "180 days from today, the interval this framework suggests",
        ),
        Proposal(
            "adoption.framework_maintainer",
            owner,
            "computed",
            "the owner you already gave",
        ),
        Proposal("adoption.needs_validator", False, "computed", "no independent review declared"),
    ]


def propose(state: dict, *, found: discover.Discovered) -> list[Proposal]:
    """Everything proposable, given what has already been answered."""
    level = state["level"]["conformance_level"]
    builds_ui = bool(state["stack"]["builds_user_interface"])
    mode = state["mode"]["mode"]
    owner = state["identity"]["owner"]
    return [
        *propose_controls(level=level, mode=mode, found=found),
        *propose_gates(level=level, builds_ui=builds_ui, mode=mode, found=found),
        *propose_adoption(owner=owner),
    ]


def unanswered(state: dict, proposals: list[Proposal], *, repo, found) -> list[str]:
    """Planned fields that no proposal covers, and so must still be asked.

    This is the honest half. A field with no discovered value, no worked example and nothing to
    compute from is a judgement, and the wizard asks for it however the adopter chose to finish.
    """
    proposed = {p.field for p in proposals}
    missing: list[str] = []
    working = dict(state)
    for name in ("controls", "gates", "adoption", "wrap"):
        section = plan.section_plan(name, repo=repo, state=working, found=found)
        local: dict = {}
        for spec in section.fields:
            key = f"{name}.{spec.id}"
            value = next((p.value for p in proposals if p.field == key), None)
            local[spec.id] = value
            if not spec.applies(local):
                local.pop(spec.id, None)
                continue
            if key not in proposed:
                missing.append(key)
        working[name] = local
    return missing
