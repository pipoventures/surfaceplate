#!/usr/bin/env python3
"""Proves the binding rule: nothing reaches a written profile that no human answered.

    python tests/test_provenance.py

`org/RELEASE_PLAN.md` states the rule as "it asks, the human answers, the tool writes". Until now
that was checked by `ScriptedPrompt`, and this repository's own test file recorded exactly how far
that fell short: it "only objects to a call it wasn't given an answer for, never to a value written
without any call." `F32`/`ACT-022` walked straight through that gap - seven controls and gates were
given rationale text no prompt ever asked for, and every scripted test passed.

This closes it from the other side. `sections.py`'s `build_*` functions are pure, so the whole
profile can be assembled from answers in which **every free-text field carries a unique sentinel**.
Any string in the result that carries no sentinel was not typed by anyone: it was contributed by the
tool. Some of that is legitimate and unavoidable - the schema version, a gate's own id, the statuses
the schema allows - so those are enumerated in an allow-list below.

**The allow-list is the point.** It is the honest, reviewable statement of everything this wizard
writes on its own behalf. Adding an entry to it is a code-review event, and a change that starts
inventing prose again cannot be made without either failing this test or visibly widening the list.
"""

from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from surfaceplate.adopt import catalogue, plan, sections, wizard  # noqa: E402

FAILURES: list[str] = []
PASSES = 0

FRAMEWORK_VERSION = "0.0.0-sentinel-version"
FRAMEWORK_DIGEST = "0000-sentinel-digest"


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASSES
    if condition:
        PASSES += 1
        print(f"  PASS  {name}")
    else:
        FAILURES.append(f"{name}: {detail}")
        print(f"  FAIL  {name}  {detail}")


def _all_choice_values() -> set[str]:
    """Every value any choice field in any plan can legally take.

    Derived from the plans themselves rather than typed out, so a new option added to a dropdown
    does not silently need a hand-edit here - the same discipline `catalogue.py` applies to gate and
    control data (`DR-6`).
    """
    values: set[str] = set()
    for level in ("essential", "standard", "full"):
        for builds_ui in (True, False):
            state = {
                "mode": {"mode": "simple"},
                "stack": {"builds_user_interface": builds_ui},
                "level": {"conformance_level": level},
                "identity": {"owner": "x"},
                "risk": {},
            }
            for name in plan.SECTION_ORDER:
                section = plan.section_plan(name, repo=ROOT, state=state)
                for spec in section.fields:
                    # ONLY closed enums. A `select` field's options are discovered from the
                    # repository (`DR-38`), so admitting them here would let the allow-list absorb
                    # arbitrary file paths and CI step names - and an allow-list that grows with
                    # the adopter's repository is not an allow-list. Select fields are answered
                    # with sentinels below, exactly like the free-text ones, so they never need to
                    # appear here. If that stops being true this test has stopped proving anything.
                    if spec.kind not in ("choice", "multiselect"):
                        continue
                    for value, _label in spec.choices:
                        values.add(value)
    return values


def sentinel_answers(repo: Path, *, level: str, builds_ui: bool, mode: str = "simple") -> tuple[dict, set[str]]:
    """A full set of answers in which every free-text field is a unique, traceable sentinel."""
    state: dict = {}
    sentinels: set[str] = set()
    counter = 0

    seeded = {
        "mode.mode": mode,
        "stack.builds_user_interface": builds_ui,
        "level.conformance_level": level,
    }

    for name in plan.SECTION_ORDER:
        section = plan.section_plan(name, repo=repo, state=state)
        local: dict = {}
        for spec in section.fields:
            if not spec.applies(local):
                continue
            key = f"{name}.{spec.id}"
            if key in seeded:
                local[spec.id] = seeded[key]
            elif spec.kind == "bool":
                local[spec.id] = bool(spec.default)
            elif spec.kind == "choice":
                local[spec.id] = spec.choices[0][0]
            elif spec.kind == "multiselect":
                local[spec.id] = [spec.choices[0][0]]
            else:
                # `select` lands here deliberately, alongside text and textarea: its value is
                # chosen by a human from real candidates, so it must be traceable like any other
                # answer rather than waved through as a known constant.
                counter += 1
                token = f"SENTINEL-{counter:04d}"
                sentinels.add(token)
                local[spec.id] = token
        state[name] = local
    return state, sentinels


def unexplained(profile: dict, sentinels: set[str], allowed: set[str]) -> list[tuple[str, str]]:
    """Every string in `profile` that neither carries a sentinel nor is an allowed constant."""
    offenders = []
    for path, value in wizard._walk_strings(profile):
        if any(token in value for token in sentinels):
            continue
        if value in allowed:
            continue
        offenders.append((path, value))
    return offenders


def allow_list() -> set[str]:
    """Everything this wizard legitimately contributes without anyone typing it.

    Read this list as the answer to "what does the tool write on its own?" - it should stay short,
    and every entry should be a fact about the framework rather than a judgement about the adopter.
    """
    allowed = {
        sections.SCHEMA_VERSION,  # "1.0"
        sections.SCANNER_NOTES,  # "Blocking."
        sections.DECISION_REQUIRED,  # "required"
        FRAMEWORK_VERSION,  # both read from .standards/INSTALL.json, never from an answer
        FRAMEWORK_DIGEST,
        _dt.date.today().isoformat(),  # adoption_date
    }
    allowed |= set(catalogue.GATE_CATALOGUE)  # a gate's own id
    allowed |= set(catalogue.CONFORMANCE_LEVELS["full"])  # a control's own id
    allowed |= {"required", "deferred", "not_applicable"}  # gate statuses
    allowed |= _all_choice_values()  # every value a dropdown can take
    # `ACT-032`. The ONLY prose this list has ever admitted beyond `SCANNER_NOTES`, and the entries
    # are taken from the catalogue rather than restated, so nothing can be added here by editing
    # this file. Each is the framework's own one-line definition of a gate, published in
    # `core/PREREQUISITE_GATES.md` and read out of the checker by `catalogue.py` - a fact about the
    # framework, not a judgement about the adopter, which is the line this list exists to hold.
    # The wizard now writes it as the gate's `precondition.description` instead of asking an
    # adopter to paraphrase the sentence printed above the box.
    allowed |= set(catalogue.GATE_CATALOGUE.values())
    allowed |= set(sections.DERIVED_ENFORCEMENT)  # "history_audit", "review" - a fixed schema enum
    return allowed


def test_no_value_is_invented(level: str, builds_ui: bool) -> None:
    state, sentinels = sentinel_answers(ROOT, level=level, builds_ui=builds_ui)
    profile = sections.build_profile(
        state, framework_version=FRAMEWORK_VERSION, framework_digest=FRAMEWORK_DIGEST
    )
    offenders = unexplained(profile, sentinels, allow_list())
    check(
        f"{level}{'/UI' if builds_ui else ''}: every string traces to an answer or the allow-list",
        not offenders,
        "; ".join(f"{p} = {v!r}" for p, v in offenders[:6]),
    )


def test_the_walk_can_fail() -> None:
    """The negative control. A test that only ever passes proves nothing, so a value nobody
    supplied is injected and the walk must object to it - the exact shape of the `F32` defect."""
    state, sentinels = sentinel_answers(ROOT, level="essential", builds_ui=False)
    profile = sections.build_profile(
        state, framework_version=FRAMEWORK_VERSION, framework_digest=FRAMEWORK_DIGEST
    )
    profile["baseline_controls"]["agent_work_packets"]["rationale"] = (
        "All agent work is bounded, scoped, and reviewable."  # plausible, and nobody typed it
    )
    offenders = unexplained(profile, sentinels, allow_list())
    check(
        "a fabricated rationale is caught by the walk",
        any("agent_work_packets" in path for path, _ in offenders),
        f"offenders: {offenders}",
    )


def test_allow_list_is_small_and_declared() -> None:
    """The allow-list should be facts about the framework, not prose about an adopter. Nothing
    enforces brevity, but a sudden jump in size is worth a reviewer's attention, so the count is
    reported rather than left implicit."""
    # The two admitted sources of prose, named exactly. `GATE_CATALOGUE.values()` is compared
    # against the catalogue itself, so this exemption cannot be widened by adding a string here -
    # a new sentence must first be a gate definition in `core/PREREQUISITE_GATES.md`.
    admitted = {sections.SCANNER_NOTES} | set(catalogue.GATE_CATALOGUE.values())
    prose = [value for value in allow_list() if " " in value and value not in admitted]
    check(
        "no free prose entered the allow-list unnoticed",
        not prose,
        f"prose-like entries: {prose}",
    )
    check(
        "the admitted prose is exactly the framework's own gate definitions, one per gate",
        len(set(catalogue.GATE_CATALOGUE.values())) == len(catalogue.GATE_CATALOGUE),
        "two gates share a definition, so one gate's profile entry would describe another",
    )


# ---------------------------------------------------------------------------------------------
# DR-47: the provenance record
# ---------------------------------------------------------------------------------------------


def _installed_fixture(tmp: Path, *, discoverable: bool) -> Path:
    """A git repository the flow can run against. With `discoverable`, it holds a register, a
    source directory, a workflow and a lock file; without, one file and nothing to find."""
    import subprocess

    repo = tmp / ("discoverable" if discoverable else "bare")
    repo.mkdir(parents=True)
    (repo / "main.py").write_text("x = 1\n", encoding="utf-8")
    if discoverable:
        (repo / "activity").mkdir()
        (repo / "activity" / "register.md").write_text("# register\n", encoding="utf-8")
        (repo / "src").mkdir()
        (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        (repo / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
        (repo / ".github" / "workflows").mkdir(parents=True)
        (repo / ".github" / "workflows" / "ci.yml").write_text(
            "jobs:\n  t:\n    steps:\n      - name: Run the tests\n        run: pytest\n",
            encoding="utf-8",
        )
    for args in (
        ["init", "-q"], ["config", "user.email", "h@example.invalid"],
        ["config", "user.name", "H"], ["config", "commit.gpgsign", "false"],
        ["add", "-A"], ["commit", "-qm", "fixture"],
    ):
        subprocess.run(["git", "-C", str(repo), *args], check=True)
    return repo


def _typed_with_sentinels(repo: Path, level: str) -> tuple:
    """Drive a `Flow` with a sentinel in every typed field and every proposal left standing.
    Returns `(flow, sentinels)`."""
    from surfaceplate.adopt import flow as _flow
    from surfaceplate.adopt.interview import ScriptedInterview

    sentinels: set[str] = set()
    counter = [0]

    def token() -> str:
        counter[0] += 1
        value = f"SENTINEL-{counter[0]:04d}"
        sentinels.add(value)
        return value

    flow = _flow.Flow(repo, {"standard_version": FRAMEWORK_VERSION, "framework_digest": FRAMEWORK_DIGEST})
    answers: dict = {
        "identity.owner": token(),
        "stack.builds_user_interface": "no",
        "risk.relied_on_outside_team": "yes" if level != "essential" else "no",
        "risk.material_quantitative_output": "yes" if level == "full" else "no",
        "risk.data_classification": "internal",
        "wrap.release_route": token(),
        "level.conformance_level": level,
    }
    # Anything the decisions form asks because discovery found nothing: a real tracked path.
    for spec in flow.decisions_plan().fields:
        if spec.id in answers or spec.default:
            continue  # a pre-filled proposal is submitted unchanged, and recorded as proposed
        if spec.validate == "tracked_path":
            answers[spec.id] = "main.py"
        elif spec.kind in ("text", "textarea") and spec.validate:
            answers[spec.id] = token()
    # A mandatory gate with nothing matched and nothing seedable needs a real tracked path.
    mandatory = plan.gate_plan(level=level, builds_ui=False, mode="simple", found=flow.found)
    for spec in mandatory:
        if spec.mandatory and not plan.discover.matched_for_gate(flow.found.artefacts, spec.id):
            answers[f"gates.{spec.id}.artefact"] = "main.py"
    interview = ScriptedInterview(answers=answers, bulk_not_applicable=True, accept_scaffold=True)
    # The remainder form: answer what it presents with sentinels or real paths.
    original_answer = interview._answer

    def answer(section, prefix=""):
        for spec in section.fields:
            key = f"{prefix}{spec.id}"
            if key in interview.answers or spec.default or not spec.validate or spec.kind not in ("text", "textarea"):
                continue
            interview.answers[key] = "main.py" if spec.validate in ("tracked_path",) else token()
        return original_answer(section, prefix)

    interview._answer = answer  # type: ignore[method-assign]
    interview.collect(flow, on_progress=lambda: None)
    return flow, sentinels


def test_the_record_carries_an_origin_for_every_value(level: str, discoverable: bool) -> None:
    """`DR-47` (7): every non-typed value carries an origin; no origin says typed for a value
    the human did not type; the approval is document-level with a timestamp."""
    import tempfile

    from surfaceplate.adopt import provenance

    with tempfile.TemporaryDirectory() as tmp:
        repo = _installed_fixture(Path(tmp), discoverable=discoverable)
        flow, sentinels = _typed_with_sentinels(repo, level)
        profile = flow.assemble()
        traced = provenance.trace(profile, flow.state, flow.origins)  # raises on an unreached leaf
        leaves = dict(provenance.leaves(profile))
        label = f"{level}{'' if discoverable else '/bare'}"
        check(
            f"{label}: every leaf of the profile has an origin in the record",
            set(leaves) == set(traced),
            f"unreached: {sorted(set(leaves) - set(traced))[:5]}",
        )
        typed_without_sentinel = [
            path for path, origin in traced.items()
            if origin.kind == "typed" and isinstance(leaves[path], str) and not any(s in leaves[path] for s in sentinels)
            # a key pressed on the decisions form or the gate list is typed without being prose,
            # and a real tracked path the driver typed is typed without being a sentinel
            and leaves[path] != "main.py"
            and not (path in ("builds_user_interface", "data_classification", "conformance_level")
                     or path.endswith(".status") or path.startswith("adoption.decision_record_id"))
        ]
        check(
            f"{label}: nothing is recorded as typed that the human did not type",
            not typed_without_sentinel,
            str(typed_without_sentinel[:5]),
        )
        copied = [
            path for path, origin in traced.items()
            if origin.kind != "typed" and isinstance(leaves[path], str)
            and any(s in leaves[path] for s in sentinels) and not origin.detail.startswith("= ")
        ]
        check(
            f"{label}: a typed value only reappears under a non-typed origin as a recorded copy (computed: = ...)",
            not copied,
            str(copied[:5]),
        )
        kinds = {o.kind for o in traced.values()}
        check(
            f"{label}: the record uses only the six origins DR-47 names",
            kinds <= set(provenance.KINDS),
            str(kinds - set(provenance.KINDS)),
        )
        record = provenance.record(traced, framework_version=FRAMEWORK_VERSION, approved_at=provenance.now_iso(), bulk=flow.bulk)
        check(
            f"{label}: the approval is recorded once, for the document, with a timestamp",
            "T" in record["approved_at"] and "approved" not in str(record["fields"]),
            record["approved_at"],
        )
        if level != "essential":
            check(
                f"{label}: the bulk decision is one human act with its count",
                record.get("bulk_decisions") and record["bulk_decisions"][0]["count"] == len([
                    1 for path, o in traced.items() if path.endswith(".status") and "bulk" in o.detail
                ]),
                str(record.get("bulk_decisions")),
            )
        print(f"      ({label}: {provenance.summarise(traced)})")


def test_a_proposed_value_marked_typed_is_caught() -> None:
    """The negative control for the record: the walk above must object when a proposal's origin
    says typed - the exact promotion `DR-47` (3) forbids."""
    import tempfile

    from surfaceplate.adopt import provenance
    from surfaceplate.adopt.provenance import TYPED, Origin

    with tempfile.TemporaryDirectory() as tmp:
        repo = _installed_fixture(Path(tmp), discoverable=True)
        flow, sentinels = _typed_with_sentinels(repo, "standard")
        # Promote the example rationale to "typed" without anyone typing it.
        flow.origins["controls.agent_work_packets.rationale"] = Origin(TYPED)
        traced = provenance.trace(flow.assemble(), flow.state, flow.origins)
        leaves = dict(provenance.leaves(flow.assemble()))
        offenders = [
            path for path, origin in traced.items()
            if origin.kind == "typed" and isinstance(leaves[path], str) and leaves[path]
            and not any(s in leaves[path] for s in sentinels)
            and path == "baseline_controls.agent_work_packets.rationale"
        ]
        check("a proposed value recorded as typed is caught by the walk", bool(offenders), str(offenders))


def test_an_unreached_profile_field_fails_loudly() -> None:
    """The other negative control: a leaf the rule table does not reach raises rather than
    passing without an origin - so a builder that starts writing a new field cannot ship it
    unrecorded (`F55`'s class, on this table)."""
    from surfaceplate.adopt import provenance

    try:
        provenance.answer_key_for("adoption.brand_new_field", {"prerequisites": []})
        check("a profile path the table does not reach raises", False, "returned instead")
    except KeyError:
        check("a profile path the table does not reach raises", True)


def main() -> int:
    print("provenance: nothing is written that nobody answered")
    for level, builds_ui in (("essential", False), ("standard", False), ("full", True)):
        test_no_value_is_invented(level, builds_ui)

    print("\nnegative controls")
    test_the_walk_can_fail()
    test_allow_list_is_small_and_declared()

    print("\nDR-47: the provenance record beside the profile")
    for level, discoverable in (("standard", True), ("essential", False), ("full", True)):
        test_the_record_carries_an_origin_for_every_value(level, discoverable)
    test_a_proposed_value_marked_typed_is_caught()
    test_an_unreached_profile_field_fails_loudly()

    print(f"\n  (allow-list carries {len(allow_list())} entries)")
    print()
    if FAILURES:
        print(f"PROVENANCE=FAIL  ({len(FAILURES)} failed, {PASSES} passed)")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    print(f"PROVENANCE=PASS  ({PASSES} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
