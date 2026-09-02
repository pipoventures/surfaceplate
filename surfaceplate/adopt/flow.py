"""The run as stages, driven by the screens and by the scripted interview alike.

`DR-47` fixes the flow: decisions, level, the gate list, whatever the proposal could not fill,
the scaffold offer, and an annotated review that shows every line of the profile with its origin
and lets the human change any of them before anything is written. This module holds that
sequence as data and transitions, so the Textual app and `ScriptedInterview` drive the same
object and neither can invent a step the other lacks - the seam `tests/test_adopt_tui.py`'s join
closes for the screens, closed once more for the sequence.

What it owns: the state (raw answers by section, as `sections.build_profile` reads them), the
origin of every answer (`provenance.Origin` by answer key), the proposals, which stages are done,
and the bulk decisions. What it does not own: rendering, verification and writing, which stay in
`render.py` and `wizard.py`; the review is built by asking the wizard to verify, never by
verifying here.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import yaml

from surfaceplate.adopt import defaults, detect, discover, plan, provenance, render, scaffold, sections, validators
from surfaceplate.adopt.provenance import Origin

# The screens, in order. `remainder` and `scaffold` appear only when they have something to show.
STAGES = ("decisions", "level", "gates", "remainder", "scaffold", "review")

# Decisions-form fields whose state target is a boolean; the form asks yes/no so that nothing is
# pre-selected (`F64`), and the answer becomes the boolean the builders read.
_YES_NO = ("stack.builds_user_interface", "risk.relied_on_outside_team", "risk.material_quantitative_output")


@dataclass(frozen=True)
class ReviewLine:
    """One annotated line of the rendered profile."""

    line: int  # 0-based line in `Review.rendered`
    path: str  # profile path, e.g. `adoption.review_by`
    origin: str  # the label shown
    editable: bool
    note: str = ""  # why not editable, where it is not


@dataclass
class Review:
    rendered: str
    lines: list[ReviewLine]
    error: str = ""
    error_path: str | None = None

    @property
    def error_line(self) -> int | None:
        for entry in self.lines:
            if entry.path == self.error_path:
                return entry.line
        return None

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for entry in self.lines:
            kind = entry.origin.split(":")[0]
            out[kind] = out.get(kind, 0) + 1
        return out


class Flow:
    """One run, as stages. Construct once per run; resume by passing the draft's state back in."""

    def __init__(
        self,
        repo: Path,
        record: dict,
        *,
        verify: Callable[[dict, str], None] | None = None,
        state: dict | None = None,
        origins: dict[str, Origin] | None = None,
        done: tuple[str, ...] = (),
        found: discover.Discovered | None = None,
        today: _dt.date | None = None,
    ) -> None:
        self.repo = repo
        self.record = record
        self.verify = verify or (lambda _profile, _rendered: None)
        self.found = found if found is not None else discover.scan(repo)
        self.state: dict[str, dict] = {name: dict(values) for name, values in (state or {}).items()}
        self.origins: dict[str, Origin] = dict(origins or {})
        self.done: list[str] = list(done)
        self.bulk: list[provenance.BulkDecision] = []
        self.adoption_date = (today or _dt.date.today()).isoformat()
        self.accepted_scaffold: list[scaffold.Offer] = []
        self.proposals: dict[str, defaults.Proposal] = {}
        # The register of explanation. `DR-47`'s flow has no screen for it; plain English is the
        # register that assumes nothing, so it is the one used.
        self.state.setdefault("mode", {"mode": "simple"})
        for proposal in defaults.propose_identity(repo) + defaults.propose_stack(repo):
            self.proposals[proposal.field] = proposal
        if "level" in self.state:
            self._propose_after_level()

    # ----------------------------------------------------------------------------------------
    # where we are
    # ----------------------------------------------------------------------------------------

    def next_stage(self) -> str:
        for stage in STAGES:
            if stage in self.done:
                continue
            if stage == "remainder" and not self.remainder_plan().fields:
                self.done.append(stage)
                continue
            if stage == "scaffold" and not self.scaffold_offers():
                self.done.append(stage)
                continue
            return stage
        return "review"

    def _set(self, key: str, value: object, origin: Origin) -> None:
        section, _, field_id = key.partition(".")
        self.state.setdefault(section, {})[field_id] = value
        self.origins[key] = origin

    def _answered(self, key: str) -> bool:
        section, _, field_id = key.partition(".")
        return field_id in (self.state.get(section) or {})

    def _record_answer(self, key: str, value: object, spec: plan.FieldSpec | None = None) -> None:
        """A submitted form value: the proposal's origin if it is the proposal, the field's own
        default's origin if it is that, typed otherwise. `DR-47` (3): a proposed value submitted
        unchanged is never recorded as typed - and a field's shown default (a worked example, a
        sentence that follows from an earlier answer) is a proposal too."""
        proposal = self.proposals.get(key)
        if proposal is not None and value == proposal.value:
            self._set(key, value, proposal.as_origin())
            return
        if spec is None:
            spec = self.field_spec(key)
        if spec is not None and spec.default and value == spec.default and spec.kind in ("text", "textarea"):
            self._set(key, value, _default_origin(key, spec))
            return
        self._set(key, value, Origin(provenance.TYPED))

    # ----------------------------------------------------------------------------------------
    # stage 1: decisions
    # ----------------------------------------------------------------------------------------

    def decisions_plan(self) -> plan.SectionPlan:
        return plan.decisions_plan(self.repo, found=self.found, proposals=self.proposals)

    def answer_decisions(self, answers: dict) -> None:
        for key, value in answers.items():
            if key in _YES_NO and isinstance(value, str):
                value = value == "yes"
            self._record_answer(key, value)
        # What the form could show pre-filled but did not ask: the display name, a detected
        # language. Recorded as proposed, shown on the review.
        for key, proposal in self.proposals.items():
            if key.split(".")[0] in ("identity", "stack") and not self._answered(key):
                self._set(key, proposal.value, proposal.as_origin())
        for proposal in defaults.propose_risk(self.state.get("risk") or {}):
            self.proposals[proposal.field] = proposal
            self._set(proposal.field, proposal.value, proposal.as_origin())
        self.done.append("decisions")

    # ----------------------------------------------------------------------------------------
    # stage 2: level
    # ----------------------------------------------------------------------------------------

    def level_plan(self) -> plan.SectionPlan:
        return plan.section_plan("level", repo=self.repo, state=self.state, found=self.found)

    def recommended_level(self) -> str:
        return plan.recommended_level(self.state.get("risk") or {})[0]

    def answer_level(self, answers: dict) -> None:
        self._set("level.conformance_level", answers["conformance_level"], Origin(provenance.TYPED))
        self._propose_after_level()
        self.done.append("level")

    def _propose_after_level(self) -> None:
        for proposal in defaults.propose_after_level(
            self.state, found=self.found, adoption_date=self.adoption_date
        ):
            self.proposals[proposal.field] = proposal
            section = proposal.field.split(".")[0]
            # Gate proposals seed the gate list and are recorded when it is answered; the rest
            # are recorded now and shown on the remainder form or the review.
            if section != "gates" and not self._answered(proposal.field):
                self._set(proposal.field, proposal.value, proposal.as_origin())

    # ----------------------------------------------------------------------------------------
    # stage 3: the gate list
    # ----------------------------------------------------------------------------------------

    def _level(self) -> str:
        return self.state["level"]["conformance_level"]

    def _builds_ui(self) -> bool:
        return bool(self.state["stack"]["builds_user_interface"])

    def gate_specs(self) -> tuple[plan.GateSpec, ...]:
        return plan.gate_plan(
            level=self._level(), builds_ui=self._builds_ui(), mode=self.state["mode"]["mode"], found=self.found
        )

    def gates_plan(self) -> plan.SectionPlan:
        return plan.gates_plan(
            level=self._level(), builds_ui=self._builds_ui(), mode=self.state["mode"]["mode"], found=self.found
        )

    def gate_seeds(self) -> dict[str, object]:
        """What the gate list shows pre-filled: every gate proposal, keyed `<gate>.<field>`."""
        seeds = {
            key[len("gates."):]: proposal.value
            for key, proposal in self.proposals.items()
            if key.startswith("gates.")
        }
        # A resumed run carries its own answers, which win over the proposals.
        seeds.update(self.state.get("gates") or {})
        return seeds

    def answer_gates(self, answers: dict, *, bulk: tuple[str, set[str]] | None = None) -> None:
        """`answers` keyed `<gate>.<field>`; `bulk` is `(status, gate ids)` for one explicit bulk
        command, recorded as a single human act with its count (`DR-47` (4))."""
        bulk_status, bulk_gates = bulk if bulk else ("", set())
        self.state["gates"] = {}
        gate_proposals = {
            key[len("gates."):]: proposal for key, proposal in self.proposals.items() if key.startswith("gates.")
        }
        specs = {
            f"{spec.id}.{f.id}": f for spec in self.gate_specs() for f in spec.fields
        }
        for key, value in answers.items():
            gate_id, _, field_id = key.partition(".")
            if field_id == "status":
                detail = f"bulk: every undecided gate declared {bulk_status}" if gate_id in bulk_gates else ""
                self._set(f"gates.{key}", value, Origin(provenance.TYPED, detail))
                continue
            proposal = gate_proposals.get(key)
            spec = specs.get(key)
            if proposal is not None and value == proposal.value:
                self._set(f"gates.{key}", value, proposal.as_origin())
            elif spec is not None and spec.default and value == spec.default and spec.kind in ("text", "textarea"):
                self._set(f"gates.{key}", value, _default_origin(f"gates.{key}", spec))
            else:
                self._set(f"gates.{key}", value, Origin(provenance.TYPED))
        if bulk_gates:
            self.bulk.append(provenance.BulkDecision(status=bulk_status, count=len(bulk_gates)))
        self.done.append("gates")

    # ----------------------------------------------------------------------------------------
    # stage 4: what the proposal could not fill
    # ----------------------------------------------------------------------------------------

    def remainder_plan(self) -> plan.SectionPlan:
        """Every planned field in controls, adoption and wrap that has no answer yet, plus the
        above-the-floor list. Presented as one form; empty when there is nothing to ask."""
        fields: list[plan.FieldSpec] = []
        for name in ("controls", "adoption", "wrap"):
            section = plan.section_plan(name, repo=self.repo, state=self.state, found=self.found)
            answered = self.state.get(name) or {}
            for spec in section.fields:
                key = f"{name}.{spec.id}"
                present = spec.id in answered
                if spec.id == "above_floor":
                    # Presented pre-filled with the proposal, because a level is a floor and not
                    # a ceiling: declaring more is a real choice the human must be able to make.
                    fields.append(_dotted(name, spec, default=list(answered.get("above_floor") or [])))
                    continue
                if key == "adoption.decision_record_id" and not present:
                    # Asked where a decisions directory exists to name a record in; scaffolded
                    # otherwise (`scaffold.DECISION_RECORD`).
                    if detect.detect_decisions_folder(self.repo) is None:
                        continue
                    fields.append(_dotted(name, spec))
                    continue
                if key == "adoption.needs_validator":
                    continue  # proposed False; the review shows independent_validator as computed
                if present:
                    continue
                if spec.depends_on is not None:
                    other, wanted = spec.depends_on
                    if other != "above_floor" and answered.get(other) not in wanted:
                        continue
                fields.append(_dotted(name, spec))
        return plan.SectionPlan(
            name="remainder",
            title="A few things this repository did not answer",
            intro=(
                "Nothing in this repository answered these, so they are yours. Everything else "
                "has been proposed and is shown, with where it came from, on the review next."
            ),
            fields=tuple(fields),
        )

    def answer_remainder(self, answers: dict) -> None:
        for key, value in answers.items():
            self._record_answer(key, value)
        self.done.append("remainder")

    # ----------------------------------------------------------------------------------------
    # stage 5: scaffold
    # ----------------------------------------------------------------------------------------

    def scaffold_offers(self) -> list[scaffold.Offer]:
        """Where a gate the profile will declare as required has no artefact, offer one; and the
        adoption decision record where no decisions directory exists (`ACT-033`, `DR-47` (2))."""
        gates = self.state.get("gates") or {}
        needs: list[str] = []
        for spec in self.gate_specs():
            if spec.id not in scaffold.SEEDABLE:
                continue
            status = "required" if spec.mandatory else (spec.auto_status or gates.get(f"{spec.id}.status"))
            if status != "required":
                continue
            answer = str(gates.get(f"{spec.id}.artefact") or "").strip()
            seed_path = scaffold.SEEDABLE[spec.id][0]
            if answer and answer != seed_path:
                continue
            if (self.repo / seed_path).exists():
                continue
            needs.append(spec.id)
        offers = scaffold.offers(self.repo, needs)
        if "decisions" in self.done and not self._answered("adoption.decision_record_id"):
            if detect.detect_decisions_folder(self.repo) is None:
                offer = scaffold.decision_record_offer(self.repo)
                if offer is not None:
                    offers.append(offer)
        return [o for o in offers if o.gate_id not in {a.gate_id for a in self.accepted_scaffold}]

    def accept_scaffold(self, accepted: list[scaffold.Offer]) -> None:
        moment = provenance.now_iso()
        for offer in accepted:
            if offer.gate_id == scaffold.DECISION_RECORD_GATE:
                self._set(
                    "adoption.decision_record_id",
                    scaffold.DECISION_RECORD_ID,
                    Origin(provenance.SCAFFOLDED, f"created: {offer.path}"),
                )
                continue
            self._set(f"gates.{offer.gate_id}.artefact", offer.path, Origin(provenance.SCAFFOLDED, f"created: {offer.path}"))
            # `F47`: the gate binds from the instant the artefact was created, not from midnight.
            self._set(f"gates.{offer.gate_id}.effective_from", moment, Origin(provenance.FACT, "the moment the artefact was created"))
        self.accepted_scaffold.extend(accepted)
        self.done.append("scaffold")

    # ----------------------------------------------------------------------------------------
    # stage 6: the review
    # ----------------------------------------------------------------------------------------

    def assemble(self) -> dict:
        return sections.build_profile(
            self.state,
            framework_version=self.record.get("standard_version", ""),
            framework_digest=self.record.get("framework_digest", ""),
        )

    def field_spec(self, key: str) -> plan.FieldSpec | None:
        """The `FieldSpec` behind an answer key, so an edit knows its kind and choices."""
        section, _, field_id = key.partition(".")
        try:
            section_plan = plan.section_plan(section, repo=self.repo, state=self.state, found=self.found)
        except KeyError:
            return None
        return next((s for s in section_plan.fields if s.id == field_id), None)

    def _first_problem(self) -> tuple[str, str] | None:
        """`(answer key, message)` for the first answered field its validator refuses, or one the
        profile needs and nothing answered. `F65`: the review names the line, and the line is
        reachable."""
        for name in plan.SECTION_ORDER:
            answered = self.state.get(name) or {}
            section = plan.section_plan(name, repo=self.repo, state=self.state, found=self.found)
            for spec in section.fields:
                if not spec.applies(answered):
                    continue
                if spec.id not in answered:
                    if spec.validate:
                        return f"{name}.{spec.id}", validators.BLANK
                    continue
                origin = self.origins.get(f"{name}.{spec.id}")
                if origin is not None and origin.kind == provenance.SCAFFOLDED:
                    continue  # the file is created when the profile is written, not before
                problem = validators.check(spec.validate, answered.get(spec.id), repo=self.repo)
                if problem:
                    return f"{name}.{spec.id}", problem
        return None

    def review(self) -> Review:
        """The rendered profile, every line annotated, and the first thing stopping a write."""
        problem = self._first_problem()
        state_for_render = {n: dict(v) for n, v in self.state.items()}
        placeholders: dict[str, Origin] = {}
        # Render with every blank in place, so the builders never meet a missing answer and the
        # error has a line to go to. The first problem is the one named.
        for name in plan.SECTION_ORDER:
            answered = state_for_render.get(name) or {}
            section = plan.section_plan(name, repo=self.repo, state=self.state, found=self.found)
            for spec in section.fields:
                if spec.applies(answered) and spec.id not in answered:
                    state_for_render.setdefault(name, {})[spec.id] = ""
                    placeholders[f"{name}.{spec.id}"] = Origin(provenance.TYPED, "not yet answered")
        profile = sections.build_profile(
            state_for_render,
            framework_version=self.record.get("standard_version", ""),
            framework_digest=self.record.get("framework_digest", ""),
        )
        rendered = render.render_profile(profile, written_on=self.adoption_date)
        traced = provenance.trace(profile, state_for_render, {**self.origins, **placeholders})
        line_of = _line_map(rendered)
        lines: list[ReviewLine] = []
        for path, origin in traced.items():
            line = line_of.get(path)
            if line is None:
                continue
            key, _fixed = provenance.answer_key_for(path, profile)
            bare = provenance._index_free(path)
            note = provenance.NOT_EDITABLE_ON_REVIEW.get(bare, "")
            if key is not None and key.endswith(".status") and key.startswith("gates."):
                note = "decided on the gates screen"
            lines.append(ReviewLine(line=line, path=path, origin=origin.label(), editable=key is not None and not note, note=note))
        lines.sort(key=lambda entry: entry.line)
        error = ""
        error_path = None
        if problem is not None:
            key, message = problem
            error = f"{key}: {message}"
            error_path = next((p for p in traced if provenance.answer_key_for(p, profile)[0] == key), None)
        else:
            try:
                self.verify(profile, rendered)
            except Exception as exc:  # WriteRefused, or anything the renderer did not expect
                error = f"This cannot be written yet: {getattr(exc, 'detail', exc)}"
        return Review(rendered=rendered, lines=lines, error=error, error_path=error_path)

    def edit(self, path: str, value: object) -> None:
        """A change made on the review: recorded as typed, with a timestamp (`DR-47` (3))."""
        profile = self.assemble()
        key, _fixed = provenance.answer_key_for(path, profile)
        if key is None:
            raise ValueError(f"{path} is not editable")
        if key in _YES_NO and isinstance(value, str):
            value = value == "yes"
        self._set(key, value, Origin(provenance.TYPED, at=provenance.now_iso()))

    def approve(self) -> str:
        at = provenance.now_iso()
        self.done.append("review")
        return at

    # ----------------------------------------------------------------------------------------
    # the draft
    # ----------------------------------------------------------------------------------------

    def draft(self) -> dict:
        return {
            "sections": self.state,
            "origins": {key: {"kind": o.kind, "detail": o.detail, "at": o.at} for key, o in self.origins.items()},
            "done": [s for s in self.done if s not in ("scaffold", "review")],
            "bulk": [{"status": b.status, "count": b.count, "at": b.at} for b in self.bulk],
        }

    @staticmethod
    def origins_from(draft: dict) -> dict[str, Origin]:
        raw = draft.get("origins") or {}
        return {
            key: Origin(str(o.get("kind", "")), str(o.get("detail", "")), str(o.get("at", "")))
            for key, o in raw.items()
            if isinstance(o, dict)
        }


def _default_origin(key: str, spec: plan.FieldSpec) -> Origin:
    """The origin of a field's shown default, submitted unchanged: a worked example where the
    framework ships one for that item, otherwise a value that follows from an earlier answer."""
    from surfaceplate.adopt import example_answers

    item = key.split(".")[1] if key.count(".") >= 2 else ""
    if item and example_answers.rationale_example(item) == spec.default:
        return Origin(provenance.EXAMPLE, "this framework's own worked example")
    return Origin(provenance.COMPUTED, "the field's own default; follows from an answer already given")


def _dotted(section_name: str, spec: plan.FieldSpec, default: object | None = None) -> plan.FieldSpec:
    """A section's field, re-keyed to its state address so one form can carry several sections."""
    depends_on = None
    if spec.depends_on is not None:
        other, wanted = spec.depends_on
        depends_on = (f"{section_name}.{other}", wanted)
    return plan.FieldSpec(
        id=f"{section_name}.{spec.id}",
        label=spec.label,
        kind=spec.kind,
        help=spec.help,
        default=spec.default if default is None else (",".join(default) if isinstance(default, list) else default),
        choices=spec.choices,
        validate=spec.validate,
        depends_on=depends_on,
        suggestions=spec.suggestions,
        decides=spec.decides,
        wrong=spec.wrong,
        context=spec.context,
    )


def _line_map(rendered: str) -> dict[str, int]:
    """Profile path -> 0-based line, read from the YAML's own node marks rather than from the
    renderer's layout, so the review cannot drift from what `render.py` actually wrote."""
    node = yaml.compose(rendered)
    out: dict[str, int] = {}

    def walk(current, path: str) -> None:
        if isinstance(current, yaml.MappingNode):
            for key_node, value_node in current.value:
                walk(value_node, f"{path}.{key_node.value}" if path else str(key_node.value))
        elif isinstance(current, yaml.SequenceNode):
            if not current.value:
                out[path] = current.start_mark.line
            for index, item in enumerate(current.value):
                walk(item, f"{path}[{index}]")
        else:
            out[path] = current.start_mark.line

    if node is not None:
        walk(node, "")
    return out
