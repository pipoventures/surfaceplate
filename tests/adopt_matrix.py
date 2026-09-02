"""The library behind `tests/test_adopt_matrix.py`: every reachable decision of `adopt`, enumerated
from the catalogue, run against a real installed repository, and judged by a property oracle.

`DR-58` fixes what "every combination" means and `ACT-057` is the activity. Nothing here is a second
profile builder: the expectations for a run are derived from the case (what was chosen) and from
the run's own proposals (what discovery offered), never from `sections.py`, so a builder drifting
from the plan fails a case rather than being re-implemented by the same hands. The written
profile, the provenance sidecar, the files created, and the checker's verdict are the four things
every case is judged on.

No I/O at import. `enumerate_cases()` derives the matrix from `catalogue`, `scaffold.SEEDABLE` and
`SEEDABLE_CONTROLS` at run time, so a gate or a seed added later widens the matrix on the next run
and `coverage_gaps()` fails the suite if the enumeration ever stops reaching one.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAYLOAD = ROOT / "surfaceplate"
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from surfaceplate import check_conformance  # noqa: E402
from surfaceplate.adopt import catalogue, defaults, detect, discover, plan, provenance, scaffold, wizard  # noqa: E402
from surfaceplate.adopt import flow as _flow  # noqa: E402
from surfaceplate.adopt.interview import Cancelled, ScriptedInterview  # noqa: E402

LEVELS = ("essential", "standard", "full")
SHAPES = ("bare", "rich", "mixed")
STATUSES = ("required", "deferred", "not_applicable")
STATUS_PATTERNS = ("all-required", "all-deferred", "all-not_applicable", "cycled", "bulk", "bulk-partial")
ARTEFACT_CLASSES = ("found", "seed", "typed")
ROUTES = ("interactive", "propose-replay", "propose-no-level", "propose-ui-refused", "resume", "edit", "cancel", "refusal", "screens")

# Read once, so a run that crosses midnight is reported as such rather than failing SP033 in one
# case and not the next.
TODAY = _dt.date.today()
INSTANT = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}")


# ---------------------------------------------------------------------------------------------
# The three repository shapes
# ---------------------------------------------------------------------------------------------

# A file whose name matches no gate keyword, for the "typed" artefact class on shapes that
# discover things: offered (it is a tracked Markdown file) and never proposed.
PLAIN_FILE = "docs/plain/note.md"
# Bare: one source file with an extension no language marker recognises, and a script where the
# scanner runs - tracked, mentions the scanner, and not a workflow, so nothing under a CI directory
# runs it and the decisions form asks where it does.
BARE_SOURCE = "src/app.c"
BARE_SCANNER = "ci/secret-scan.sh"
MIXED_LOCK = "deps/pins.txt"
# An artefact committed on the day of the run, after the back-dated fixture commit: with
# `effective_from` set before that commit, the gated history precedes the artefact (`SP035`).
LATE_ARTEFACT = "docs/late-artefact.md"
# The lazily committed workflow's first step, sorted first, so that discovery proposes it for every
# pattern-B control and a typed step name never coincides with a proposal (which would be recorded
# under the proposal's origin, correctly, and defeat the typed expectation).
DUMMY_STEP = "A step nothing names"

_CI = "jobs:\n  t:\n    steps:\n      - name: Run the tests\n        run: pytest\n      - name: Run the contract tests\n        run: pytest tests/contract\n"
_SCAN = "jobs:\n  scan:\n    steps:\n      - name: Run gitleaks\n        run: gitleaks detect\n"
_CI_WITH_SCAN = _CI + "      - name: Run gitleaks\n        run: gitleaks detect\n"


def _doc(title: str) -> str:
    return f"# {title}\n\nA real, non-empty document of the fixture repository. It holds no entries yet.\n"


SHAPE_FILES: dict[str, dict[str, str]] = {
    "bare": {
        BARE_SOURCE: "int main(void) { return 0; }\n",
        BARE_SCANNER: "#!/bin/sh\ngitleaks detect\n",
    },
    "rich": {
        "src/app.py": "x = 1\n",
        "requirements.txt": "PyYAML==6.0.3\n",
        ".github/workflows/ci.yml": _CI,
        ".github/workflows/secret-scan.yml": _SCAN,
        "activity/register.md": _doc("Activity register"),
        "docs/work-packet.md": _doc("Work packet"),
        "governance/RISK_CLASSIFICATION.md": _doc("Risk classification"),
        "docs/decisions/README.md": _doc("Decisions"),
        "docs/decisions/DR-1.md": _doc("DR-1"),
        "docs/decisions/OPTIONS.md": _doc("Options considered"),
        "docs/RELEASE_CHECKLIST.md": _doc("Release checklist"),
        "CHANGELOG.md": "# Changelog\n\n## Unreleased\n\nNothing yet.\n",
        "documentation/governance/inventory/source_of_truth_matrix.yaml": "questions: []\n",
        "docs/AUTHORITY.md": _doc("Authority"),
        "docs/testing/TEST_CONVENTIONS.md": _doc("Test conventions"),
        "docs/testing/REGRESSION_TESTS.md": _doc("Regression tests"),
        "docs/testing/EQUIVALENCE_PROTOCOL.md": _doc("Equivalence protocol"),
        "governance/DATA_SOURCES.md": _doc("Data sources"),
        "docs/OUTPUT_VALIDATION.md": _doc("Output validation"),
        "docs/DEPENDENCY_REVIEW.md": _doc("Dependency review"),
        "docs/design/COMPONENT_LIBRARY.md": _doc("Component library"),
        "docs/design/DESIGN_POLICY.md": _doc("Design policy"),
        "docs/design/SCREEN_STATE.md": _doc("Screen state"),
        "docs/FINDINGS.md": _doc("Findings"),
        "governance/method-registry/README.md": _doc("Method registry"),
        "governance/overrides/README.md": _doc("Overrides"),
        "governance/run-lineage/README.md": _doc("Run lineage"),
        PLAIN_FILE: _doc("A note"),
    },
    "mixed": {
        "src/app.py": "x = 1\n",
        MIXED_LOCK: "PyYAML==6.0.3\n",
        ".github/workflows/ci.yml": _CI_WITH_SCAN,
        "docs/archive/register.md": _doc("An archived register"),
        "docs/decision-log.md": "# Decision log\n\nTBD\n",
        "config/accounts/prod.yaml": "account: prod\n",
        "CHANGELOG.md": "# Changelog\n\n## Unreleased\n\nNothing yet.\n",
        PLAIN_FILE: _doc("A note"),
    },
}


def _git(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=env)


def build_shape(cache: Path, shape: str, *, name: str | None = None) -> Path:
    """One installed, committed, back-dated fixture of `shape`. Built once per suite run; cases copy it."""
    repo = cache / (name or shape)
    repo.mkdir(parents=True)
    for rel, text in SHAPE_FILES[shape].items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "matrix@example.invalid")
    _git(repo, "config", "user.name", "Matrix")
    _git(repo, "config", "commit.gpgsign", "false")
    result = subprocess.run(
        [sys.executable, str(PAYLOAD / "install_standard.py"), "--source", str(PAYLOAD), "--target", str(repo), "--no-hooks"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"fixture install failed:\n{result.stdout}\n{result.stderr}"
    # Yesterday, so a gated commit made in the same second as a seed's instant never reads as
    # crossing a gate before its artefact (the precaution `tests/test_adopt.py` records).
    yesterday = (TODAY - _dt.timedelta(days=1)).isoformat() + "T12:00:00"
    env = {**os.environ, "GIT_AUTHOR_DATE": yesterday, "GIT_COMMITTER_DATE": yesterday}
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "fixture", env=env)
    return repo


def clone_shape(built: Path, into: Path, name: str) -> Path:
    """A copy of the built shape as `into/name`. The directory name is what `application_id` and
    `display_name` are proposed from, so a twin of a case is cloned under a different parent with
    the SAME name (`twin_of`)."""
    target = into / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(built, target, symlinks=True)
    return target


def twin_of(built: Path, work: Path, case: Case, label: str) -> Path:
    return clone_shape(built, work / f"{case.id}-{label}", "___" if case.variant == "nonslug" else case.id)


def commit_all(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", message], capture_output=True)


def status_paths(repo: Path) -> set[str]:
    """Every path git reports as changed or untracked, relative."""
    out = _git(repo, "status", "--porcelain", "--untracked-files=all").stdout
    return {line[3:].strip() for line in out.splitlines() if line.strip()}


def install_record(repo: Path) -> dict:
    return json.loads((repo / wizard.INSTALL_RECORD).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------
# Cases
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Case:
    id: str
    tier: str
    level: str
    ui: bool
    shape: str
    status_pattern: str = "all-required"
    artefact_class: str = "found"
    above_floor: str = "none"  # none | all | <control id>
    variant: str = ""  # decisions variants and the stress cases, by name
    route: str = "interactive"
    stage: str = ""  # resume: the stage cancelled before; cancel: the point
    expect_codes: tuple[str, ...] = ()  # the exact sorted finding codes expected, else PASS
    expect_refusal: str = ""  # a fragment the run must refuse with, at the review or before

    @property
    def config(self) -> str:
        return f"{self.level}/{'ui' if self.ui else 'no-ui'}"


def free_gates(level: str, ui: bool) -> list[str]:
    return [s.id for s in plan.gate_plan(level=level, builds_ui=ui, mode="simple") if not s.mandatory and not s.auto_status]


def above_floor_controls(level: str) -> list[str]:
    """What the remainder form actually offers above the floor at `level` - read from the plan, so
    a control the plan withholds (`F97`: documentation_authority at essential) is not enumerated
    as though it could be ticked."""
    section = plan.controls_plan(level=level, mode="simple")
    above = next((f for f in section.fields if f.id == "above_floor"), None)
    return [value for value, _label in above.choices] if above is not None else []


def enumerate_cases() -> list[Case]:
    cases: list[Case] = []
    n = [0]

    def add(tier: str, **kw) -> Case:
        n[0] += 1
        case = Case(id=f"{tier}-{n[0]:03d}", tier=tier, **kw)
        cases.append(case)
        return case

    # T1 + T2: every configuration on every shape; every free gate in every status, cycled, in bulk,
    # and in a bulk with some statuses explicit.
    for level in LEVELS:
        for ui in (False, True):
            for shape in SHAPES:
                patterns = STATUS_PATTERNS if free_gates(level, ui) else ("all-required",)
                for pattern in patterns:
                    add("T2", level=level, ui=ui, shape=shape, status_pattern=pattern)
    # T3: every artefact field with the seed row and a typed path; the found class is T2's default.
    for level in LEVELS:
        for ui in (False, True):
            for shape in SHAPES:
                for cls in ("seed", "typed"):
                    add("T3", level=level, ui=ui, shape=shape, artefact_class=cls)
    # T4: above-floor controls: none is T2's default; all, and each singly, on rich and bare.
    for level in LEVELS:
        for shape in ("rich", "bare"):
            for choice in ["all", *above_floor_controls(level)]:
                if choice == "all" and not above_floor_controls(level):
                    continue
                add("T4", level=level, ui=False, shape=shape, above_floor=choice)
    # T5: the decisions form's variants, on bare at essential.
    for variant in ("classification:public", "classification:confidential", "classification:restricted",
                    "risk:yes-no", "risk:no-yes", "risk:yes-yes", "risk_profile:typed", "advanced", "nonslug", "display_name"):
        add("T5", level="essential", ui=False, shape="bare", variant=variant)
    # Stress cases from the design review, each an enumerated case.
    add("T5", level="standard", ui=False, shape="bare", variant="seed-declined", expect_refusal="cannot be blank")
    add("T5", level="standard", ui=False, shape="bare", variant="decision-log-and-record")
    add("T5", level="standard", ui=False, shape="mixed", variant="archived-chosen")
    add("T5", level="standard", ui=False, shape="mixed", variant="rejected-chosen", expect_refusal="placeholder")
    add("T5", level="standard", ui=False, shape="mixed", variant="unfit-register-chosen", above_floor="overrides", expect_codes=("SP056",))
    add("T5", level="standard", ui=False, shape="bare", variant="effective-from-before-history", expect_codes=("SP035",))
    add("T5", level="standard", ui=False, shape="bare", variant="revisit-by-past", status_pattern="all-deferred", expect_refusal="in the past")
    add("T5", level="standard", ui=False, shape="bare", variant="effective-from-future", expect_refusal="in the future")
    add("T5", level="essential", ui=False, shape="bare", variant="seed-parent-is-a-file", expect_codes=("SP032",))
    # T6: routes.
    for level in LEVELS:
        for shape in SHAPES:
            add("T6", level=level, ui=False, shape=shape, route="propose-replay")
    add("T6", level="standard", ui=False, shape="rich", route="propose-no-level")
    for level in LEVELS:
        # On bare nothing is proposed for the interface gates, so a record flipped to "yes" is
        # refused as incomplete; on rich their artefacts are proposed and the flipped record writes.
        add("T6", level=level, ui=True, shape="bare", route="propose-ui-refused")
        add("T6", level=level, ui=True, shape="rich", route="propose-ui-refused")
    for level in LEVELS:
        for stage in ("level", "gates", "remainder", "scaffold", "review"):
            add("T6", level=level, ui=False, shape="bare", route="resume", stage=stage, artefact_class="seed")
    add("T6", level="full", ui=True, shape="rich", route="resume", stage="gates")
    add("T6", level="standard", ui=False, shape="rich", route="edit")
    add("T6", level="standard", ui=False, shape="bare", route="edit", artefact_class="seed")
    for point in ("welcome", "resume-prompt", "review"):
        add("T6", level="essential", ui=False, shape="bare", route="cancel", stage=point)
    for refusal in ("not-installed", "already-adopted", "mismatch", "placeholder"):
        add("T6", level="essential", ui=False, shape="bare", route="refusal", variant=refusal)
    # T7: the screens, driven, at every configuration on rich.
    for level in LEVELS:
        for ui in (False, True):
            add("T7", level=level, ui=ui, shape="rich", route="screens", status_pattern="cycled")
    return cases


def coverage_gaps(cases: list[Case]) -> list[str]:
    """What the enumeration failed to reach, derived from the catalogue - so a new gate, seed, control
    or route cannot leave the matrix silently narrower."""
    gaps: list[str] = []
    full = [c for c in cases if c.route == "interactive" and not c.expect_refusal and not c.expect_codes]
    for level in LEVELS:
        for ui in (False, True):
            for shape in SHAPES:
                here = [c for c in full if (c.level, c.ui, c.shape) == (level, ui, shape)]
                if not here:
                    gaps.append(f"no full run at {level}/{ui}/{shape}")
                for gate in free_gates(level, ui):
                    for status in STATUSES:
                        if not any(_status_for(c, gate, index) == status for c in here for index in [free_gates(level, ui).index(gate)]):
                            gaps.append(f"{level}/{'ui' if ui else 'no-ui'}/{shape}: {gate} never {status}")
                for cls in ARTEFACT_CLASSES:
                    if not any(c.artefact_class == cls for c in here):
                        gaps.append(f"{level}/{'ui' if ui else 'no-ui'}/{shape}: artefact class {cls} never run")
    for level in LEVELS:
        for control in above_floor_controls(level):
            if not any(c.above_floor in (control, "all") for c in full if c.level == level):
                gaps.append(f"{level}: above-floor control {control} never ticked")
    seedable_ui = {g for g in scaffold.SEEDABLE if g in catalogue.DESIGN_GATES}
    for gate in scaffold.SEEDABLE:
        if not any(c.artefact_class == "seed" and c.shape == "bare" and (c.ui or gate not in seedable_ui) and gate in _declared_gates(c) for c in full):
            gaps.append(f"seed for {gate} never chosen")
    for control in scaffold.SEEDABLE_CONTROLS:
        if not any(c.artefact_class == "seed" and c.shape == "bare" and control in (set(catalogue.CONFORMANCE_LEVELS[c.level]) | _ticked(c)) for c in full):
            gaps.append(f"seed for control {control} never chosen")
    for route in ROUTES:
        if not any(c.route == route for c in cases):
            gaps.append(f"route {route} never run")
    for stage in ("level", "gates", "remainder", "scaffold", "review"):
        if not any(c.route == "resume" and c.stage == stage for c in cases):
            gaps.append(f"resume after {stage} never run")
    return gaps


def _declared_gates(case: Case) -> set[str]:
    return {s.id for s in plan.gate_plan(level=case.level, builds_ui=case.ui, mode="simple")}


def _ticked(case: Case) -> set[str]:
    if case.above_floor == "all":
        return set(above_floor_controls(case.level))
    if case.above_floor == "none":
        return set()
    return {case.above_floor}


def _status_for(case: Case, gate_id: str, index: int) -> str | None:
    """The status a case assigns to the `index`-th free gate; `None` means left to the bulk command."""
    pattern = case.status_pattern
    if pattern.startswith("all-"):
        return pattern[4:]
    if pattern == "cycled":
        return STATUSES[index % 3]
    if pattern == "bulk":
        return None
    if pattern == "bulk-partial":
        return "required" if index < 2 else None
    raise ValueError(pattern)


# ---------------------------------------------------------------------------------------------
# Composing a run: the answers, and what they entitle the oracle to expect
# ---------------------------------------------------------------------------------------------


@dataclass
class Script:
    answers: dict = field(default_factory=dict)
    expect: dict[str, tuple[object, str]] = field(default_factory=dict)  # profile path -> (value, origin kind)
    created: set[str] = field(default_factory=set)  # files the run must create, relative
    bulk_count: int = 0
    bulk: bool = False
    accept_scaffold: bool = True
    lazy_workflow_steps: list[str] = field(default_factory=list)  # committed when the remainder asks
    sentinels: set[str] = field(default_factory=set)
    mode: str = "simple"
    gate_status: dict[str, str] = field(default_factory=dict)
    proposals: dict = field(default_factory=dict)
    typed_artefact: str = ""
    expect_problems: bool = False  # the run must report a seed it could not create

    def sentinel(self, case_id: str, name: str) -> str:
        token = f"S-{case_id}-{name}"
        self.sentinels.add(token)
        return token


def _typed_artefact(shape: str) -> str:
    return BARE_SOURCE if shape == "bare" else PLAIN_FILE


def compose(case: Case, repo: Path) -> Script:
    """Walk the plan the wizard will walk for `case` on `repo`, choosing per the case, and record
    what each choice entitles the oracle to expect. A throwaway `Flow` supplies the proposals; the
    real run rescans the same committed tree, so its proposals are the same."""
    s = Script()
    s.mode = "advanced" if case.variant == "advanced" else "simple"
    s.typed_artefact = LATE_ARTEFACT if case.variant == "effective-from-before-history" else _typed_artefact(case.shape)
    flow = _flow.Flow(repo, {"standard_version": "0", "framework_digest": "0"}, state={"mode": {"mode": s.mode}})
    typed_prose = case.artefact_class == "typed"
    a = s.answers

    # --- decisions --------------------------------------------------------------------------
    relied, material = {"essential": (False, False), "standard": (True, False), "full": (True, True)}[case.level]
    if case.variant.startswith("risk:"):
        relied, material = (w == "yes" for w in case.variant[5:].split("-"))
    classification = case.variant[15:] if case.variant.startswith("classification:") else "internal"
    for spec in flow.decisions_plan().fields:
        key = spec.id
        if key == "identity.application_id":
            if not spec.default:  # the directory name does not slug: asked, typed
                a[key] = "app-" + re.sub(r"[^a-z0-9]", "", case.id.lower())
                s.expect["application_id"] = (a[key], provenance.TYPED)
            else:
                s.expect["application_id"] = (spec.default, provenance.COMPUTED)
        elif key == "identity.owner":
            a[key] = s.sentinel(case.id, "owner")
            s.expect["owner"] = (a[key], provenance.TYPED)
        elif key == "stack.language":
            a[key] = s.sentinel(case.id, "language")
            s.expect["stack.language"] = (a[key], provenance.TYPED)
        elif key == "stack.builds_user_interface":
            a[key] = "yes" if case.ui else "no"
            s.expect["builds_user_interface"] = (case.ui, provenance.TYPED)
        elif key == "risk.relied_on_outside_team":
            a[key] = "yes" if relied else "no"
            s.expect["risk.relied_on_outside_team"] = (relied, provenance.TYPED)
        elif key == "risk.material_quantitative_output":
            a[key] = "yes" if material else "no"
            s.expect["risk.material_quantitative_output"] = (material, provenance.TYPED)
        elif key == "risk.data_classification":
            a[key] = classification
            s.expect["data_classification"] = (classification, provenance.TYPED)
            s.expect["adoption.repository_classification"] = (classification, provenance.COMPUTED)
        elif key == "wrap.release_route":
            a[key] = s.sentinel(case.id, "release_route")
            s.expect["release_route"] = (a[key], provenance.TYPED)
        elif key == "risk.risk_profile":
            if case.variant == "risk_profile:typed":
                a[key] = s.sentinel(case.id, "risk_profile")
                s.expect["risk_profile"] = (a[key], provenance.TYPED)
            else:
                a[key] = ""
                s.expect["risk_profile"] = (defaults.NOT_STATED, provenance.COMPUTED)
        elif key == "controls.scanner.wired_in":
            a[key] = BARE_SCANNER
            s.expect["baseline_controls.secret_hygiene.scanner.wired_in[0]"] = (BARE_SCANNER, provenance.TYPED)
        elif key == "controls.dependency_lock.implementation_reference":
            a[key] = BARE_SOURCE if case.shape == "bare" else MIXED_LOCK
            s.expect["control_decisions.dependency_lock.implementation_reference"] = (a[key], provenance.TYPED)
        else:
            raise AssertionError(f"the decisions form presents a field this composer does not know: {key}")
    if "stack.language" not in a:
        proposal = flow.proposals["stack.language"]
        s.expect["stack.language"] = (proposal.value, provenance.DISCOVERED)
    if case.variant == "display_name":
        a["identity.display_name"] = s.sentinel(case.id, "display_name")
        s.expect["display_name"] = (a["identity.display_name"], provenance.TYPED)
    else:
        s.expect["display_name"] = (flow.proposals["identity.display_name"].value, provenance.COMPUTED)
    s.expect["materiality_definition"] = (defaults.NOT_STATED, provenance.COMPUTED)
    flow.answer_decisions(dict(a))

    # --- level ------------------------------------------------------------------------------
    a["level.conformance_level"] = case.level
    s.expect["conformance_level"] = (case.level, provenance.TYPED)
    flow.answer_level({"conformance_level": case.level})
    s.proposals = dict(flow.proposals)

    # --- gates ------------------------------------------------------------------------------
    free = free_gates(case.level, case.ui)
    gate_answers: dict = {}
    for spec in flow.gate_specs():
        prefix = f"gates.{spec.id}"
        if spec.mandatory:
            status = "required"
        elif spec.auto_status:
            status = spec.auto_status
        else:
            status = _status_for(case, spec.id, free.index(spec.id))
            if status is None:
                s.bulk = True
                s.bulk_count += 1
                status = "not_applicable"
            else:
                a[f"{prefix}.status"] = status
        s.gate_status[spec.id] = status
        if status == "required":
            _compose_required_gate(case, s, flow, spec, gate_answers)
        elif status == "deferred":
            a[f"{prefix}.owner"] = s.sentinel(case.id, f"{spec.id}-owner")
            revisit = (TODAY - _dt.timedelta(days=1)) if case.variant == "revisit-by-past" else (TODAY + _dt.timedelta(days=30))
            a[f"{prefix}.revisit_by"] = revisit.isoformat()
            _compose_rationale(case, s, spec, typed_prose)
        else:
            _compose_rationale(case, s, spec, typed_prose)
        for key, value in a.items():
            if key.startswith(prefix + "."):
                gate_answers[key[len("gates."):]] = value
    flow.answer_gates(gate_answers)

    # --- remainder --------------------------------------------------------------------------
    ticked = sorted(_ticked(case))
    floor = set(catalogue.CONFORMANCE_LEVELS[case.level])
    local: dict = {}
    for spec in flow.remainder_plan().fields:
        if not spec.applies(local):
            continue
        key = spec.id
        if key == "controls.above_floor":
            a[key] = ticked
            local[key] = ticked
            continue
        if key == "adoption.decision_record_id":
            a[key] = s.sentinel(case.id, "decision_record_id")
            s.expect["adoption.decision_record_id"] = (a[key], provenance.TYPED)
            local[key] = a[key]
            continue
        if key.endswith(".rationale"):
            control = key.split(".")[1]
            if typed_prose:
                a[key] = s.sentinel(case.id, f"{control}-rationale")
                s.expect[f"control_decisions.{control}.rationale"] = (a[key], provenance.TYPED)
            else:
                s.expect[f"control_decisions.{control}.rationale"] = (spec.default, provenance.EXAMPLE)
                local[key] = spec.default
            local[key] = a.get(key, spec.default)
            continue
        if key.endswith(".implementation_reference"):
            control = key.split(".")[1]
            _compose_reference(case, s, spec, control)
            local[key] = a.get(key, spec.default)
            continue
        raise AssertionError(f"the remainder form presents a field this composer does not know: {key}")
    for control in sorted(floor | set(ticked)):
        path = f"control_decisions.{control}"
        s.expect[f"{path}.decision"] = ("required", provenance.COMPUTED)
        if f"{path}.rationale" not in s.expect:
            proposal = flow.proposals.get(f"controls.{control}.rationale")
            if proposal is not None:
                s.expect[f"{path}.rationale"] = (proposal.value, proposal.origin)
        ref_key = f"controls.{control}.implementation_reference"
        if f"{path}.implementation_reference" not in s.expect and ref_key in flow.proposals:
            s.expect[f"{path}.implementation_reference"] = (flow.proposals[ref_key].value, flow.proposals[ref_key].origin)

    # --- everything proposed and never presented -----------------------------------------------
    for control in plan.BASELINE_CONTROL_IDS:
        s.expect[f"baseline_controls.{control}.rationale"] = (flow.proposals[f"controls.{control}.rationale"].value, provenance.EXAMPLE)
        s.expect[f"baseline_controls.{control}.decision"] = ("required", provenance.COMPUTED)
    s.expect["baseline_controls.secret_hygiene.scanner.name"] = (discover.DEFAULT_SCANNER, provenance.EXAMPLE)
    if "baseline_controls.secret_hygiene.scanner.wired_in[0]" not in s.expect:
        s.expect["baseline_controls.secret_hygiene.scanner.wired_in[0]"] = (flow.proposals["controls.scanner.wired_in"].value, provenance.DISCOVERED)
    s.expect["adoption.review_by"] = ((TODAY + _dt.timedelta(days=180)).isoformat(), provenance.COMPUTED)
    s.expect["adoption.framework_maintainer"] = (a["identity.owner"], provenance.COMPUTED)
    s.expect["adoption.adoption_status"] = ("in_progress", provenance.COMPUTED)
    s.expect["adoption.independent_validator"] = (None, provenance.COMPUTED)
    s.expect["adoption.adoption_date"] = (TODAY.isoformat(), provenance.FACT)
    s.expect["human_roles"] = ([], provenance.COMPUTED)
    if "adoption.decision_record_id" not in s.expect:
        if detect.detect_decisions_folder(repo) is None:
            s.expect["adoption.decision_record_id"] = (scaffold.DECISION_RECORD_ID, provenance.SCAFFOLDED)
            if s.accept_scaffold:
                s.created.add(scaffold.DECISION_RECORD[0])
    return s


def _compose_rationale(case: Case, s: Script, spec: plan.GateSpec, typed: bool) -> None:
    rationale = next(f for f in spec.fields if f.id == "rationale")
    key = f"gates.{spec.id}.rationale"
    if typed:
        s.answers[key] = s.sentinel(case.id, f"{spec.id}-rationale")
        s.expect[f"gate:{spec.id}.rationale"] = (s.answers[key], provenance.TYPED)
    else:
        from surfaceplate.adopt import example_answers

        kind = provenance.EXAMPLE if example_answers.rationale_example(spec.id) == rationale.default else provenance.COMPUTED
        s.expect[f"gate:{spec.id}.rationale"] = (rationale.default, kind)


def _compose_required_gate(case: Case, s: Script, flow: _flow.Flow, spec: plan.GateSpec, gate_answers: dict) -> None:
    prefix = f"gates.{spec.id}"
    artefact = next(f for f in spec.fields if f.id == "artefact")
    proposal = flow.proposals.get(f"{prefix}.artefact")
    seed = artefact.seed
    cls = case.artefact_class
    if case.variant == "archived-chosen" and spec.id == "work_registration":
        value, origin = "docs/archive/register.md", provenance.TYPED
    elif case.variant == "rejected-chosen" and spec.id == "decision_before_implementation":
        value, origin = "docs/decision-log.md", provenance.TYPED
    elif cls == "typed" or case.variant == "effective-from-before-history" or (proposal is None and not seed):
        value, origin = s.typed_artefact, provenance.TYPED
    elif cls == "seed" and seed:
        value, origin = seed, provenance.SCAFFOLDED
    elif proposal is not None:
        value, origin = proposal.value, provenance.DISCOVERED
    else:
        value, origin = seed, provenance.SCAFFOLDED
    if case.variant == "seed-parent-is-a-file" and spec.id == "work_registration":
        value, origin = seed, provenance.SCAFFOLDED
    if case.variant == "decision-log-and-record" and spec.id == "decision_before_implementation":
        value, origin = seed, provenance.SCAFFOLDED
    if origin == provenance.SCAFFOLDED:
        s.answers[f"{prefix}.artefact"] = value
        if s.accept_scaffold:
            s.created.add(scaffold.write_path_for(value))
        s.expect[f"gate:{spec.id}.effective_from"] = ("INSTANT", provenance.FACT)
    else:
        if not (proposal is not None and value == proposal.value):
            s.answers[f"{prefix}.artefact"] = value
        s.expect[f"gate:{spec.id}.effective_from"] = (flow.adoption_date, provenance.COMPUTED)
    if case.variant == "effective-from-before-history":
        s.answers[f"{prefix}.effective_from"] = (TODAY - _dt.timedelta(days=3)).isoformat()
        s.expect[f"gate:{spec.id}.effective_from"] = (s.answers[f"{prefix}.effective_from"], provenance.TYPED)
    if case.variant == "effective-from-future":
        s.answers[f"{prefix}.effective_from"] = (TODAY + _dt.timedelta(days=1)).isoformat()
    s.expect[f"gate:{spec.id}.precondition.artefacts[0]"] = (value, origin)
    paths_proposal = flow.proposals.get(f"{prefix}.paths")
    if cls == "typed" or paths_proposal is None or case.variant == "effective-from-before-history":
        s.answers[f"{prefix}.paths"] = "**"
        s.expect[f"gate:{spec.id}.gated_activity.paths[0]"] = ("**", provenance.TYPED)
    else:
        s.expect[f"gate:{spec.id}.gated_activity.paths[0]"] = (paths_proposal.value, provenance.DISCOVERED)
    s.expect[f"gate:{spec.id}.precondition.description"] = (catalogue.GATE_CATALOGUE[spec.id], provenance.COMPUTED)
    s.expect[f"gate:{spec.id}.enforcement"] = (["history_audit", "review"], provenance.COMPUTED)


def _compose_reference(case: Case, s: Script, spec: plan.FieldSpec, control: str) -> None:
    key = spec.id
    path = f"control_decisions.{control}.implementation_reference"
    proposal = s.proposals.get(key)
    if proposal is not None:
        s.expect[path] = (proposal.value, provenance.DISCOVERED)
        return
    if case.variant == "unfit-register-chosen" and control == "overrides":
        s.answers[key] = "config/accounts"
        s.expect[path] = ("config/accounts", provenance.TYPED)
        return
    if control in catalogue.PATTERN_B_CONTROLS:
        step = f"Step for {control}"
        s.answers[key] = step
        s.lazy_workflow_steps.append(step)
        s.expect[path] = (step, provenance.TYPED)
        return
    if spec.seed and case.artefact_class != "typed":
        s.answers[key] = spec.seed
        reference = scaffold.SEEDABLE_CONTROLS[control][0]
        s.expect[path] = (reference, provenance.SCAFFOLDED)
        if s.accept_scaffold:
            s.created.add(scaffold.write_path_for(reference))
        return
    if control in catalogue.PATTERN_C_CONTROLS:
        # A directory typed by hand: the seed's own directory, created lazily by the seed row is not
        # "typed", so the typed class for a record directory is the fitting directory rich holds,
        # and on the other shapes the seed row (stated in the report).
        s.answers[key] = spec.seed
        reference = scaffold.SEEDABLE_CONTROLS[control][0]
        s.expect[path] = (reference, provenance.SCAFFOLDED)
        if s.accept_scaffold:
            s.created.add(scaffold.write_path_for(reference))
        return
    s.answers[key] = s.typed_artefact
    s.expect[path] = (s.typed_artefact, provenance.TYPED)


# ---------------------------------------------------------------------------------------------
# Running a case, and judging it
# ---------------------------------------------------------------------------------------------


@dataclass
class Outcome:
    case: Case
    checks: list[tuple[str, bool, str]] = field(default_factory=list)
    verdict: str = ""
    codes: tuple[str, ...] = ()
    created: tuple[str, ...] = ()
    origins: dict[str, int] = field(default_factory=dict)
    seconds: float = 0.0
    note: str = ""

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        self.checks.append((name, bool(condition), "" if condition else detail))

    @property
    def failed(self) -> list[tuple[str, bool, str]]:
        return [c for c in self.checks if not c[1]]


def make_interview(s: Script, repo: Path, **kw) -> ScriptedInterview:
    interview = ScriptedInterview(answers=dict(s.answers), bulk_not_applicable=s.bulk, accept_scaffold=s.accept_scaffold, **kw)
    if s.lazy_workflow_steps:
        original = interview._answer

        def answer(section, prefix=""):
            if section.name == "remainder":
                write_lazy_workflow(repo, s.lazy_workflow_steps)
            return original(section, prefix)

        interview._answer = answer  # type: ignore[method-assign]
    return interview


def write_lazy_workflow(repo: Path, steps: list[str]) -> None:
    """A workflow with the named steps, committed - what a pattern-B control on a repository with
    no CI is answered with, written when the field is asked (after discovery scanned) so the field
    is asked rather than proposed."""
    target = repo / ".github" / "workflows" / "matrix-late.yml"
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(f"      - name: {n}\n        run: echo {n!r}\n" for n in dict.fromkeys([DUMMY_STEP, *steps]))
    target.write_text("jobs:\n  late:\n    steps:\n" + body, encoding="utf-8")
    _git(repo, "add", str(target.relative_to(repo)))
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "late workflow"], capture_output=True)


def _leaf(profile: dict, path: str):
    node = profile
    for part in re.split(r"\.(?![^\[]*\])", path):
        m = re.match(r"^(.*?)\[(\d+)\]$", part)
        if m:
            node = node[m.group(1)][int(m.group(2))]
        else:
            node = node[part]
    return node


def resolve_gate_paths(profile: dict, expect: dict) -> dict:
    """`gate:<id>.<leaf>` expectations become `prerequisites[i].<leaf>` once the profile says which index."""
    index = {g["id"]: i for i, g in enumerate(profile.get("prerequisites", []))}
    out = {}
    for path, value in expect.items():
        if path.startswith("gate:"):
            gate_id, _, leaf = path[5:].partition(".")
            if gate_id not in index:
                out[path] = value
                continue
            out[f"prerequisites[{index[gate_id]}].{leaf}"] = value
        else:
            out[path] = value
    return out


def judge_written(o: Outcome, s: Script, repo: Path, written, *, commit: bool = True) -> None:
    """The oracle, on what a completed run put on disk."""
    profile_path = repo / wizard.PROFILE_PATH
    o.check("the profile was written", profile_path.is_file())
    text = profile_path.read_text(encoding="utf-8")
    profile = yaml.safe_load(text)
    o.check("the profile validates against the installed schema", schema_ok(repo, profile))
    sidecar = yaml.safe_load((repo / provenance.PROVENANCE_PATH).read_text(encoding="utf-8"))
    fields = sidecar.get("fields") or {}
    leaves = dict(provenance.leaves(profile))
    o.check("the sidecar carries an origin for every leaf of the profile, and no other", set(fields) == set(leaves),
            f"missing {sorted(set(leaves) - set(fields))[:4]} extra {sorted(set(fields) - set(leaves))[:4]}")
    kinds = {entry.get("origin") for entry in fields.values()}
    o.check("the sidecar uses only the six origins", kinds <= set(provenance.KINDS), str(kinds - set(provenance.KINDS)))
    o.origins = {k: sum(1 for e in fields.values() if e.get("origin") == k) for k in sorted(kinds)}
    # Per-field expectations.
    expect = resolve_gate_paths(profile, s.expect)
    for path, (value, origin) in sorted(expect.items()):
        if path.startswith("gate:"):
            o.check(f"{path}: the gate is declared", False, "the profile declares no such gate")
            continue
        try:
            actual = _leaf(profile, path)
        except (KeyError, IndexError, TypeError):
            o.check(f"{path} is present", False, "absent from the profile")
            continue
        if value == "INSTANT":
            ok = isinstance(actual, str) and INSTANT.fullmatch(actual) is not None
        else:
            ok = actual == value
        o.check(f"{path} == {value!r}", ok, f"profile has {actual!r}")
        if isinstance(actual, list) and actual:
            # A list of scalars has one sidecar entry per element.
            recorded = {(fields.get(f"{path}[{i}]") or {}).get("origin") for i in range(len(actual))}
            o.check(f"{path} recorded as {origin}", recorded == {origin}, f"sidecar says {recorded!r}")
            continue
        recorded = (fields.get(path) or {}).get("origin")
        o.check(f"{path} recorded as {origin}", recorded == origin, f"sidecar says {recorded!r}")
    # Structure: every gate the plan declares, in plan order, with the status the case chose and
    # exactly the fields that status calls for.
    specs = plan.gate_plan(level=s.answers["level.conformance_level"], builds_ui=profile["builds_user_interface"], mode="simple")
    o.check("the profile declares exactly the gates the plan declares, in its order",
            [g["id"] for g in profile["prerequisites"]] == [sp.id for sp in specs], str([g["id"] for g in profile["prerequisites"]]))
    for gate in profile["prerequisites"]:
        wanted = s.gate_status.get(gate["id"])
        o.check(f"{gate['id']} status == {wanted}", gate["status"] == wanted, gate["status"])
        keys = set(gate) - {"id", "status"}
        shape = {"required": {"effective_from", "precondition", "gated_activity", "enforcement"},
                 "deferred": {"owner", "revisit_by", "rationale"}, "not_applicable": {"rationale"}}[gate["status"]]
        o.check(f"{gate['id']} carries exactly the fields {gate['status']} calls for", keys == shape, str(sorted(keys)))
    declared = set(profile["control_decisions"])
    wanted_controls = set(catalogue.CONFORMANCE_LEVELS[s.answers["level.conformance_level"]]) | set(s.answers.get("controls.above_floor") or [])
    o.check("control_decisions is exactly the floor plus what was ticked", declared == wanted_controls, f"{sorted(declared)} vs {sorted(wanted_controls)}")
    o.check("the three baseline controls are declared", set(profile["baseline_controls"]) == set(plan.BASELINE_CONTROL_IDS))
    o.check("adoption.review_by is 180 days from the adoption date",
            profile["adoption"]["review_by"] == (_dt.date.fromisoformat(profile["adoption"]["adoption_date"]) + _dt.timedelta(days=180)).isoformat())
    o.check("nothing typed carries a value nobody typed: every sentinel appears exactly where expected",
            all(any(tok in str(v) for v in leaves.values()) for tok in s.sentinels), "a sentinel never reached the profile")
    stray = [p for p, v in leaves.items() if isinstance(v, str) and "S-" in v and not any(tok in v for tok in s.sentinels)]
    o.check("no sentinel from another case leaked in", not stray, str(stray[:3]))
    # Bulk.
    bulk = sidecar.get("bulk_decisions") or []
    if s.bulk:
        o.check("the bulk decision is one act with the count of gates it decided", len(bulk) == 1 and bulk[0]["count"] == s.bulk_count and bulk[0]["status"] == "not_applicable", str(bulk))
        bulk_marked = [p for p, e in fields.items() if p.endswith(".status") and "bulk" in str(e.get("detail", ""))]
        o.check("and every gate it decided is marked as bulk in the sidecar", len(bulk_marked) == s.bulk_count, str(len(bulk_marked)))
    else:
        o.check("no bulk decision is recorded when none was made", not bulk, str(bulk))
    # Files on disk.
    changed = status_paths(repo)
    created = sorted(p.relative_to(repo).as_posix() for p in getattr(written, "created", []))
    o.created = tuple(created)
    expected_changed = {wizard.PROFILE_PATH, provenance.PROVENANCE_PATH} | s.created | set(created)
    lazy = {".github/workflows/matrix-late.yml"}
    o.check("git sees exactly the profile, the sidecar and the created files", changed - lazy == expected_changed - lazy,
            f"unexpected {sorted(changed - expected_changed)[:4]}; missing {sorted(expected_changed - changed)[:4]}")
    o.check("the run created exactly the files the chosen seeds name", set(created) == s.created, f"created {created}; expected {sorted(s.created)}")
    for rel in created:
        o.check(f"{rel} exists and is non-empty", (repo / rel).is_file() and (repo / rel).stat().st_size > 0)
    o.check("no draft remains after a completed write", not (repo / wizard.DRAFT_FILENAME).exists())
    problems = list(getattr(written, "problems", []))
    if s.expect_problems:
        o.check("the run reported the seed it could not create", any("activity/register.md" in p for p in problems), str(problems))
    else:
        o.check("the run reported no scaffold problems", not problems, str(problems))
    if commit:
        commit_all(repo, "adopted")
        report = check_conformance.evaluate(repo, TODAY, False, False)
        o.verdict = report.verdict
        o.codes = tuple(sorted({f.code for f in report.findings}))
        if o.case.expect_codes:
            # The expected-finding cases: the only non-PASS runs, each asserting exact codes.
            o.check(f"the checker reports exactly {list(o.case.expect_codes)}", o.codes == tuple(sorted(o.case.expect_codes)), f"{report.verdict}: {o.codes}")
        else:
            o.check("the checker passes with no findings against what was written", report.verdict == "PASS" and not report.findings,
                    f"{report.verdict}: " + "; ".join(f"{f.code} {f.title}" for f in report.findings[:5]))


def schema_ok(repo: Path, profile: dict) -> bool:
    import jsonschema

    schema = yaml.safe_load((repo / ".standards" / "schemas" / "application-profile.schema.yaml").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return next(validator.iter_errors(profile), None) is None


def normalised(text: str) -> str:
    return INSTANT.sub("INSTANT", text)


def profile_text(repo: Path) -> str:
    return (repo / wizard.PROFILE_PATH).read_text(encoding="utf-8")


def sidecar_origins(repo: Path) -> dict[str, str]:
    data = yaml.safe_load((repo / provenance.PROVENANCE_PATH).read_text(encoding="utf-8"))
    return {p: e["origin"] for p, e in (data.get("fields") or {}).items()}


def run_interactive(o: Outcome, s: Script, repo: Path):
    interview = make_interview(s, repo)
    try:
        written = wizard.run(repo, interview)
    except AssertionError as exc:
        if o.case.expect_refusal:
            o.check(f"the review refuses, naming {o.case.expect_refusal!r}", o.case.expect_refusal in str(exc), str(exc)[:200])
            o.check("nothing was written", not (repo / provenance.PROVENANCE_PATH).exists() and status_paths(repo) <= {wizard.DRAFT_FILENAME})
            o.note = "refused at the review, as expected"
            return None
        o.check("the run completes", False, str(exc)[:300])
        return None
    try:
        interview.assert_no_unused_keys()
        o.check("every scripted answer was asked for or overrode a proposal", True)
    except AssertionError as exc:
        o.check("every scripted answer was asked for or overrode a proposal", False, str(exc))
    if o.case.expect_refusal:
        o.check(f"the review refuses, naming {o.case.expect_refusal!r}", False, "the run completed instead")
        return written
    return written


def run_case(case: Case, built: dict[str, Path], work: Path) -> Outcome:
    import time

    o = Outcome(case=case)
    started = time.perf_counter()
    try:
        _run_case(case, o, built, work)
    except Exception as exc:  # noqa: BLE001 - the case fails, the suite goes on
        import traceback

        o.check("the case ran without an unexpected exception", False, f"{type(exc).__name__}: {exc}\n" + traceback.format_exc()[-800:])
    o.seconds = time.perf_counter() - started
    return o


def _run_case(case: Case, o: Outcome, built: dict[str, Path], work: Path) -> None:
    repo = twin_of(built[case.shape], work, case, "run")
    if case.variant == "seed-parent-is-a-file":
        (repo / "activity").write_text("a file where the seed's directory would go\n", encoding="utf-8")
        commit_all(repo, "occupied")
    if case.variant == "effective-from-before-history":
        (repo / LATE_ARTEFACT).parent.mkdir(parents=True, exist_ok=True)
        (repo / LATE_ARTEFACT).write_text("# A late artefact\n\nCommitted after the gated history.\n", encoding="utf-8")
        commit_all(repo, "late artefact")
    if case.route == "interactive":
        s = compose(case, repo)
        if case.variant == "seed-declined":
            s.accept_scaffold = False
            s.created = set()
        if case.variant == "seed-parent-is-a-file":
            s.expect_problems = True
            s.created.discard("activity/register.md")
        if case.variant == "advanced":
            _run_advanced(o, s, repo)
            return
        written = run_interactive(o, s, repo)
        if written is None:
            return
        judge_written(o, s, repo, written)
        return
    if case.route == "propose-replay":
        _run_propose_replay(case, o, repo, built, work)
    elif case.route == "propose-no-level":
        _run_propose_no_level(o, repo)
    elif case.route == "propose-ui-refused":
        _run_propose_ui_refused(case, o, repo)
    elif case.route == "resume":
        _run_resume(case, o, repo, built, work)
    elif case.route == "edit":
        _run_edit(case, o, repo)
    elif case.route == "cancel":
        _run_cancel(case, o, repo)
    elif case.route == "refusal":
        _run_refusal(case, o, repo)
    elif case.route == "screens":
        from adopt_matrix_screens import run_screens  # the Textual half, imported only here

        s = compose(case, repo)
        written = run_screens(s, repo)
        o.check("the screens completed the run", written is not None, "cancelled or stuck")
        if written is None:
            return
        judge_written(o, s, repo, written)
        twin = twin_of(built[case.shape], work, case, "scripted")
        s2 = compose(case, twin)
        run_interactive(Outcome(case=case), s2, twin)
        o.check("the screens write the profile the scripted run writes", normalised(profile_text(repo)) == normalised(profile_text(twin)),
                "\n".join(l for l in normalised(profile_text(repo)).splitlines() if l not in normalised(profile_text(twin)).splitlines())[:400])
        o.check("and the same origins", sidecar_origins(repo) == sidecar_origins(twin))
    else:
        raise ValueError(case.route)


def _run_advanced(o: Outcome, s: Script, repo: Path) -> None:
    """The `advanced` register changes explanation text only: the assembled profile is identical."""
    record = install_record(repo)
    flows = {}
    for mode in ("simple", "advanced"):
        flow = _flow.Flow(repo, record, state={"mode": {"mode": mode}})
        interview = make_interview(s, repo)
        interview.collect(flow, on_progress=lambda: None)
        flows[mode] = flow.assemble()
    o.check("advanced and simple registers assemble the same profile", flows["simple"] == flows["advanced"])
    o.note = "flow-level, nothing written"


def _run_propose_replay(case: Case, o: Outcome, repo: Path, built: dict, work: Path) -> None:
    s = compose(case, repo)
    if s.lazy_workflow_steps:
        write_lazy_workflow(repo, s.lazy_workflow_steps)
        s.expect = {k: v for k, v in s.expect.items()}  # the reference is then proposed, and overridden: typed either way
    proposed = wizard.propose(repo, level=case.level)
    o.check("--propose writes the record and the preview, never the profile",
            proposed.answers.is_file() and proposed.proposed is not None and proposed.proposed.is_file()
            and not (repo / provenance.PROVENANCE_PATH).exists() and "replace-me" in profile_text(repo))
    record = yaml.safe_load(proposed.answers.read_text(encoding="utf-8"))
    pending = [k for k, v in record["answers"].items() if v == wizard.NEEDS_HUMAN]
    o.check("every needs-human line is a decision the case answers (or a gate status)",
            all(k in s.answers or k.endswith(".status") or k == "create_missing_artefacts" for k in pending),
            str([k for k in pending if k not in s.answers and not k.endswith(".status")][:5]))
    for key in pending:
        if key == "create_missing_artefacts":
            record["answers"][key] = "yes"
        elif key.endswith(".status"):
            record["answers"][key] = s.answers.get(key, "not_applicable")
        else:
            record["answers"][key] = s.answers[key]
    # Every scripted answer joins the record: a human changing a proposed value, a deferred owner.
    for key, value in s.answers.items():
        if key != "level.conformance_level":
            record["answers"][key] = value
    completed = repo / "governance" / "answers-completed.yaml"
    completed.write_text(yaml.safe_dump(record, sort_keys=False, allow_unicode=True), encoding="utf-8")
    written = wizard.replay(repo, completed)
    completed.unlink()
    (repo / wizard.PROPOSED_PATH).unlink()
    (repo / wizard.ANSWERS_PATH).unlink()
    s.bulk = False  # the record answers each status singly
    judge_written(o, s, repo, written)
    twin = twin_of(built[case.shape], work, case, "interactive")
    s2 = compose(case, twin)
    if s2.bulk:
        for gate, status in s2.gate_status.items():
            if f"gates.{gate}.status" not in s2.answers and gate in free_gates(case.level, case.ui):
                s2.answers[f"gates.{gate}.status"] = status
        s2.bulk = False
    run_interactive(Outcome(case=case), s2, twin)
    o.check("replay writes the profile the interactive run writes from the same answers",
            normalised(profile_text(repo)) == normalised(profile_text(twin)),
            "\n".join(l for l in normalised(profile_text(repo)).splitlines() if l not in normalised(profile_text(twin)).splitlines())[:400])
    o.check("and records the same origins", sidecar_origins(repo) == sidecar_origins(twin),
            str([p for p, k in sidecar_origins(repo).items() if sidecar_origins(twin).get(p) != k][:5]))


def _run_propose_no_level(o: Outcome, repo: Path) -> None:
    proposed = wizard.propose(repo)
    o.check("without --level the record stops at the level and writes no preview", proposed.proposed is None and proposed.answers.is_file())
    try:
        wizard.replay(repo, proposed.answers)
        outcome = "wrote"
    except wizard.NeedsHuman as exc:
        outcome = str(exc)
    o.check("replaying it refuses, naming the level first", outcome != "wrote" and "level" in outcome.split(":")[1][:20], outcome[:160])
    o.note = "refused, as designed"


def _run_propose_ui_refused(case: Case, o: Outcome, repo: Path) -> None:
    """`propose` assumes no interface. A record flipped to yes at standard or full needs the four
    interface gates' answers: on bare nothing is proposed for them, so replay refuses as
    incomplete and, completed by hand, writes; on rich their artefacts are proposed and the
    flipped record writes as it stands. At essential no interface gate is declared either way."""
    s = compose(case, repo)
    if s.lazy_workflow_steps:
        write_lazy_workflow(repo, s.lazy_workflow_steps)
    proposed = wizard.propose(repo, level=case.level)
    record = yaml.safe_load(proposed.answers.read_text(encoding="utf-8"))
    for key, value in record["answers"].items():
        if value == wizard.NEEDS_HUMAN:
            record["answers"][key] = s.answers.get(key, "not_applicable" if key.endswith(".status") else "yes" if key == "create_missing_artefacts" else "x")
    record["answers"]["stack.builds_user_interface"] = "yes"
    completed = repo / "governance" / "answers-completed.yaml"
    completed.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    expect_refusal = case.level != "essential" and case.shape == "bare"
    try:
        written = wizard.replay(repo, completed)
        outcome = "wrote"
    except wizard.WriteRefused as exc:
        outcome = exc.detail
    if expect_refusal:
        o.check("a record flipped to an interface is refused as incomplete, naming --propose", outcome != "wrote" and "incomplete" in outcome and "--propose" in outcome, outcome[:200])
        o.check("and nothing was written", not (repo / provenance.PROVENANCE_PATH).exists())
        for key, value in s.answers.items():
            if any(key.startswith(f"gates.{gate}.") for gate in catalogue.DESIGN_GATES):
                record["answers"][key] = value
        completed.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
        written = wizard.replay(repo, completed)
    else:
        o.check("the flipped record writes as it stands", outcome == "wrote", outcome[:200])
    profile = yaml.safe_load(written.read_text(encoding="utf-8"))
    if case.level == "essential":
        o.check("at essential no interface gate is declared either way", [g["id"] for g in profile["prerequisites"]] == ["work_registration"] and profile["builds_user_interface"] is True)
        o.note = "essential declares no interface gate"
        return
    o.check("it writes with the four interface gates required",
            all(g["status"] == "required" for g in profile["prerequisites"] if g["id"] in catalogue.DESIGN_GATES) and profile["builds_user_interface"] is True)


def _run_resume(case: Case, o: Outcome, repo: Path, built: dict, work: Path) -> None:
    s = compose(case, repo)
    first = make_interview(s, repo, cancel_before=case.stage)
    try:
        wizard.run(repo, first)
        o.check(f"the first attempt is cancelled before {case.stage}", False, "it completed")
        return
    except Cancelled:
        pass
    draft = repo / wizard.DRAFT_FILENAME
    o.check("a draft was left", draft.is_file())
    stages = json.loads(draft.read_text(encoding="utf-8")).get("done", [])
    o.check(f"the draft records the stages before {case.stage}", case.stage not in stages and (not stages or stages[-1] != case.stage), str(stages))
    o.check("nothing else was written by the cancelled attempt", status_paths(repo) <= {wizard.DRAFT_FILENAME, ".github/workflows/matrix-late.yml"}, str(status_paths(repo)))
    # The second interview is given only the answers still outstanding, as `tests/test_adopt.py`
    # does: a resumed stage that was re-asked then fails for want of an answer rather than passing.
    done = set(stages)
    remaining = Script(**{**s.__dict__, "answers": {k: v for k, v in s.answers.items() if stage_of(k) not in done}})
    second = make_interview(remaining, repo)
    written = wizard.run(repo, second)
    o.check("the draft was offered and resumed", len(second.resume_offers) == 1 and second.resume_offers[0].matches)
    o.check("the resumed run did not re-ask the completed stages", not (set(stages) & set(second.stages)), f"re-asked {sorted(set(stages) & set(second.stages))}")
    try:
        second.assert_no_unused_keys()
        o.check("every outstanding answer was asked for", True)
    except AssertionError as exc:
        o.check("every outstanding answer was asked for", False, str(exc))
    judge_written(o, s, repo, written)
    twin = twin_of(built[case.shape], work, case, "uninterrupted")
    s2 = compose(case, twin)
    run_interactive(Outcome(case=case), s2, twin)
    o.check("the resumed run writes the profile the uninterrupted run writes", normalised(profile_text(repo)) == normalised(profile_text(twin)),
            "\n".join(l for l in normalised(profile_text(repo)).splitlines() if l not in normalised(profile_text(twin)).splitlines())[:400])


def stage_of(key: str) -> str:
    """The stage at which an answer key is presented, for a resume that must not re-supply it."""
    section = key.split(".")[0]
    if section == "gates":
        return "gates"
    if section == "level":
        return "level"
    if section in ("identity", "stack", "risk") or key in ("wrap.release_route", "controls.scanner.wired_in", "controls.dependency_lock.implementation_reference"):
        return "decisions"
    return "remainder"


def _run_edit(case: Case, o: Outcome, repo: Path) -> None:
    s = compose(case, repo)
    written = run_interactive(o, s, repo)
    if written is None:
        return
    commit_all(repo, "adopted")
    before = yaml.safe_load(profile_text(repo))

    def passes(label: str) -> None:
        commit_all(repo, label)
        report = check_conformance.evaluate(repo, TODAY, False, False)
        o.check(f"after {label} the checker still passes", report.verdict == "PASS" and not report.findings, f"{report.verdict} {[f.code for f in report.findings]}")

    wizard.edit(repo, "owner", "Edited Owner", because="a string edit")
    after = yaml.safe_load(profile_text(repo))
    o.check("a string edit changes that line", after["owner"] == "Edited Owner")
    after["owner"] = before["owner"]
    o.check("and nothing else", after == before)
    record = yaml.safe_load((repo / provenance.PROVENANCE_PATH).read_text(encoding="utf-8"))
    o.check("the sidecar records the edit as typed with the reason", record["fields"]["owner"]["origin"] == "typed" and "string edit" in record["fields"]["owner"]["detail"] and record["edits"][-1]["path"] == "owner")
    passes("the string edit")
    wizard.edit(repo, "risk.relied_on_outside_team", "yes", because="a bool edit")
    o.check("a bool edit parses yes as true", yaml.safe_load(profile_text(repo))["risk"]["relied_on_outside_team"] is True)
    wizard.edit(repo, "risk.relied_on_outside_team", "false", because="a bool edit back")
    o.check("and false as false", yaml.safe_load(profile_text(repo))["risk"]["relied_on_outside_team"] is False)
    passes("the bool edits")
    wired = before["baseline_controls"]["secret_hygiene"]["scanner"]["wired_in"][0]
    wizard.edit(repo, "baseline_controls.secret_hygiene.scanner.wired_in[0]", wired, because="a list element, same value")
    o.check("a list element is addressed by index", yaml.safe_load(profile_text(repo))["baseline_controls"]["secret_hygiene"]["scanner"]["wired_in"] == [wired])
    passes("the list-element edit")
    for path, value, why in (("prerequisites[0].precondition.artefacts", "x", "a list"), ("adoption", "x", "a block"),
                             ("prerequisites[0].status", "deferred", "a gate status"), ("conformance_level", "full", "a not-editable line"),
                             ("ownr", "x", "a path the profile lacks")):
        try:
            wizard.edit(repo, path, value)
            outcome = "edited"
        except wizard.WriteRefused as exc:
            outcome = exc.detail
        o.check(f"refused: {why}", outcome != "edited", outcome[:120])
    # The predicted defect: an edit that names an untracked artefact must be refused at the field,
    # as the wizard refuses it, rather than written to fail SP032 on the next run.
    index = next(i for i, g in enumerate(before["prerequisites"]) if g["status"] == "required")
    path = f"prerequisites[{index}].precondition.artefacts[0]"
    try:
        wizard.edit(repo, path, "does-not-exist.md", because="an untracked path")
        outcome = "edited"
    except wizard.WriteRefused as exc:
        outcome = exc.detail
    o.check("an edit to an untracked artefact path is refused with the field's own rule", outcome != "edited" and "Nothing exists" in outcome, outcome[:160])
    o.check("and the profile is unchanged by the refusal", yaml.safe_load(profile_text(repo))["prerequisites"][index]["precondition"]["artefacts"] == before["prerequisites"][index]["precondition"]["artefacts"])
    passes("the refused edits")


def _run_cancel(case: Case, o: Outcome, repo: Path) -> None:
    s = compose(case, repo)
    before = {p.relative_to(repo).as_posix(): p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}

    def snapshot() -> dict:
        return {p.relative_to(repo).as_posix(): p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}

    class QuitsAtTheOpening:
        def open(self, welcome):
            return None

        def collect(self, **kw):
            raise AssertionError("collect must not run after a quit at the opening")

    if case.stage == "welcome":
        try:
            wizard.run(repo, QuitsAtTheOpening())
            outcome = "ran"
        except Cancelled:
            outcome = "cancelled"
        o.check("quitting at the opening cancels", outcome == "cancelled", outcome)
        o.check("and leaves the tree byte-identical", snapshot() == before)
    elif case.stage == "resume-prompt":
        try:
            wizard.run(repo, make_interview(s, repo, cancel_before="gates"))
        except Cancelled:
            pass
        with_draft = snapshot()
        o.check("a draft exists", wizard.DRAFT_FILENAME in with_draft and set(with_draft) - set(before) == {wizard.DRAFT_FILENAME})
        try:
            wizard.run(repo, QuitsAtTheOpening())
            outcome = "ran"
        except Cancelled:
            outcome = "cancelled"
        o.check("quitting at the resume prompt cancels", outcome == "cancelled", outcome)
        o.check("and keeps the draft, changing nothing", snapshot() == with_draft)
    else:
        try:
            wizard.run(repo, make_interview(s, repo, confirm_write=False))
            outcome = "ran"
        except Cancelled:
            outcome = "cancelled"
        o.check("declining the write at the review cancels", outcome == "cancelled", outcome)
        after = snapshot()
        o.check("the only new file is the draft", set(after) - set(before) == {wizard.DRAFT_FILENAME}, str(sorted(set(after) - set(before))))
        o.check("every other file is byte-identical", all(after[p] == before[p] for p in before))
    o.note = "cancelled, as designed"


def _run_refusal(case: Case, o: Outcome, repo: Path) -> None:
    from surfaceplate import about

    s = compose(case, repo)
    if case.variant == "not-installed":
        shutil.rmtree(repo / ".standards")
        try:
            wizard.run(repo, make_interview(s, repo))
            outcome = "ran"
        except wizard.NotInstalled:
            outcome = "refused"
        o.check("a repository without the install record is refused", outcome == "refused", outcome)
    elif case.variant == "already-adopted":
        (repo / wizard.PROFILE_PATH).write_text("application_id: already-here\nowner: Someone\n", encoding="utf-8")
        try:
            wizard.run(repo, make_interview(s, repo))
            outcome = "ran"
        except wizard.AlreadyAdopted:
            outcome = "refused"
        o.check("a real profile is never overwritten", outcome == "refused" and profile_text(repo).startswith("application_id: already-here"), outcome)
    elif case.variant == "mismatch":
        record_path = repo / wizard.INSTALL_RECORD
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["framework_digest"] = "0" * 64
        record_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        interview = make_interview(s, repo)
        try:
            wizard.run(repo, interview)
            outcome = "ran"
        except wizard.InstallMismatch as exc:
            outcome = str(exc)
        o.check("an install older than the tool is refused before the first question", outcome != "ran" and not interview.stages and about.anchor()[:12] in outcome, outcome[:160])
    else:
        s.answers["identity.owner"] = "TBD"
        try:
            wizard.run(repo, make_interview(s, repo))
            outcome = "ran"
        except AssertionError as exc:
            outcome = str(exc)
        o.check("a placeholder typed into a field is refused at the review", outcome != "ran" and "placeholder" in outcome, outcome[:160])
    o.check("nothing was written", not (repo / provenance.PROVENANCE_PATH).exists())
    o.note = "refused, as designed"
