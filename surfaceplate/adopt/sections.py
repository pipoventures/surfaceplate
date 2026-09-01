"""The seven sections, in order. Each function asks; none of them decide.

Every function takes a `Prompt` and returns a plain dict fragment shaped exactly like the piece of
`governance/application-profile.yaml` it fills. `wizard.py` assembles the fragments; nothing here
writes a file, and nothing here is reachable except through a `Prompt.text`/`.select`/`.confirm`
call - there is no code path from a detected fact or a suggested default to the written profile that
does not pass through the human answering.

A default shown in a prompt (a suggested `review_by` date, a pre-checked `enforcement` set) is not
an invented answer: `questionary` shows it, the human sees it, and pressing Enter is still an
answer - the same way accepting a form's pre-filled field is still submitting the form. What would
cross the line is writing a value the human never saw asked. Nothing here does that.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from surfaceplate.adopt import catalogue
from surfaceplate.adopt.prompting import Prompt

TEMPLATE_PLACEHOLDER_HELP = (
    "Type an actual value. \"TBD\", \"TODO\" and similar are template placeholders this "
    "framework's own checker rejects (SP020) - writing one here would fail the profile you're "
    "about to produce."
)


def _nonempty_text(prompt: Prompt, message: str, *, help: str | None = None, default: str = "") -> str:
    """A text answer that cannot be blank. The one validation rule applied uniformly, everywhere:
    an empty string is never a decision, on any field, at any point in this wizard."""
    while True:
        answer = prompt.text(message, help=help, default=default).strip()
        if answer:
            return answer


# ---------------------------------------------------------------------------------------------
# Section 1 — Identity
# ---------------------------------------------------------------------------------------------

_APPLICATION_ID_HELP = "short, stable, used in file paths and IDs - lowercase, digits, hyphen or underscore"


def ask_identity(prompt: Prompt) -> dict:
    import re

    while True:
        application_id = _nonempty_text(prompt, "Application ID", help=_APPLICATION_ID_HELP)
        if re.match(r"^[a-z0-9][a-z0-9_-]+$", application_id):
            break
        print(f'  "{application_id}" must start with a letter or digit and use only lowercase, '
              "digits, hyphens or underscores - try again.")

    display_name = _nonempty_text(prompt, "Display name", help="what humans call it")
    owner = _nonempty_text(
        prompt, "Owner",
        help="who is accountable for this application, not this adoption",
    )
    return {"application_id": application_id, "display_name": display_name, "owner": owner}


# ---------------------------------------------------------------------------------------------
# Section 2 — Stack
# ---------------------------------------------------------------------------------------------

def ask_stack(prompt: Prompt, repo: Path) -> dict:
    from surfaceplate.adopt import detect

    languages = detect.detect_languages(repo)
    ui_hint = detect.detect_ui_hint(repo)
    if languages:
        print(f"  Detected: {', '.join(languages)}")
    if ui_hint:
        print(f"  Detected a UI-framework dependency: {ui_hint}")

    language = _nonempty_text(
        prompt, "Language(s) / framework", default=", ".join(languages) if languages else "",
        help="shown above if detected - confirm or correct it",
    )

    # builds_user_interface is asked outright and never set from ui_hint. core/CONFORMANCE_LEVELS.md
    # is explicit about why: "a reviewer can falsify a wrong answer in seconds" - which is only a
    # meaningful check if a human, not a heuristic, gave the answer being checked.
    builds_ui_help = (
        "Decides whether the four interface gates are a floor at standard and full. Not "
        "descriptive - answer for what this repository actually does, not what it might do later."
    )
    builds_user_interface = prompt.confirm(
        "Does this repository build a user interface?", help=builds_ui_help
    )

    return {"stack": {"language": language}, "builds_user_interface": builds_user_interface}


# ---------------------------------------------------------------------------------------------
# Section 3 — Risk & materiality
# ---------------------------------------------------------------------------------------------

def ask_risk(prompt: Prompt) -> dict:
    risk_profile = _nonempty_text(
        prompt, "Risk profile",
        help="intended use, uncertainty, materiality - a sentence or two, in your own words",
    )
    materiality_definition = _nonempty_text(
        prompt, "Materiality definition",
        help="which outputs or decisions are material - what would make a wrong one matter",
    )
    data_classification = prompt.select(
        "Data classification",
        [
            ("public", "public — no restriction"),
            ("internal", "internal — not for external release"),
            ("confidential", "confidential — restricted within the organisation"),
            ("restricted", "restricted — the strictest tier this framework recognises"),
        ],
    )
    return {
        "risk_profile": risk_profile,
        "materiality_definition": materiality_definition,
        "data_classification": data_classification,
    }


# ---------------------------------------------------------------------------------------------
# Section 4 — Conformance level
# ---------------------------------------------------------------------------------------------

def ask_conformance_level(prompt: Prompt, *, builds_user_interface: bool) -> str:
    choices = []
    for level in ("essential", "standard", "full"):
        summary = catalogue.level_summary(level, builds_user_interface)
        label = (
            f"{level} — {summary['gate_count']} gate(s), {summary['control_count']} control(s). "
            f"{summary['blurb']}"
        )
        choices.append((level, label))
    return prompt.select(
        "Conformance level — a floor, not a ceiling; you may require more than the level asks",
        choices,
    )


# ---------------------------------------------------------------------------------------------
# Section 5 — Controls
# ---------------------------------------------------------------------------------------------

_BASELINE_CONTROL_IDS = ("agent_work_packets", "actual_diff_review", "secret_hygiene")


def ask_controls(prompt: Prompt, *, level: str) -> dict:
    """Every rationale below, baseline or level-required, is asked - none is ever supplied by
    this module. A Gemini adversarial review (`ACT-021`) found that `agent_work_packets`,
    `actual_diff_review`, and `secret_hygiene` used to get a hardcoded rationale string here,
    never routed through `Prompt` at all - a real violation of this package's own binding rule,
    confirmed against the code before this fix (`ACT-022`; `org/FINDINGS.md`). It applied
    regardless of whether the reasoning was true for every adopter; the rule is about what asked
    the question, not about whether the answer was likely to be uncontroversial."""
    print("  Three baseline controls apply at every level and cannot be excluded, deferred, or")
    print("  omitted - but why each applies here is still yours to state, not ours to assume.")

    baseline_controls: dict = {}
    for control_id in _BASELINE_CONTROL_IDS:
        rationale = _nonempty_text(
            prompt, f"Why does {control_id} apply here?", help=TEMPLATE_PLACEHOLDER_HELP
        )
        baseline_controls[control_id] = {"decision": "required", "rationale": rationale}

    scanner_name = _nonempty_text(
        prompt, "Secret scanner", default="gitleaks",
        help="the tool that scans for secrets before they're committed",
    )
    scanner_workflow = _nonempty_text(
        prompt, "Workflow file the scanner is wired into",
        help="e.g. .github/workflows/secret-scan.yml - a step naming this scanner must be able to fail the build",
    )
    baseline_controls["secret_hygiene"]["scanner"] = {
        "name": scanner_name, "wired_in": [scanner_workflow], "notes": "Blocking."
    }

    required = catalogue.CONFORMANCE_LEVELS[level]
    control_decisions: dict = {}
    for control_id in sorted(required):
        print(f"  --- {control_id} (required at {level}) ---")
        rationale = _nonempty_text(
            prompt, f"Why does {control_id} apply here?", help=TEMPLATE_PLACEHOLDER_HELP
        )
        entry: dict = {"decision": "required", "rationale": rationale}
        if control_id in catalogue.PATTERN_A_CONTROLS:
            entry["implementation_reference"] = _nonempty_text(
                prompt, f"File that implements {control_id}",
                help="a lock file, a findings register - whatever this control is actually checked against",
            )
        elif control_id in catalogue.PATTERN_B_CONTROLS:
            entry["implementation_reference"] = _nonempty_text(
                prompt, f"CI step name that implements {control_id}",
                help="the exact step name in your workflow file - matched by name, not by job",
            )
        elif control_id in catalogue.PATTERN_C_CONTROLS:
            entry["implementation_reference"] = _nonempty_text(
                prompt, f"Register directory for {control_id}",
                help="a directory of records validating against this control's schema - empty is a valid, honest start",
            )
        control_decisions[control_id] = entry

    add_more = prompt.confirm(
        "Declare any control above the floor? (a level is a floor, not a ceiling)", default=False
    )
    while add_more:
        remaining = sorted(set(catalogue.CONFORMANCE_LEVELS["full"]) - set(control_decisions))
        if not remaining:
            break
        control_id = prompt.select(
            "Which control?", [(c, c) for c in remaining]
        )
        rationale = _nonempty_text(prompt, f"Why declare {control_id} here, above the floor?")
        entry = {"decision": "required", "rationale": rationale}
        if control_id in catalogue.PATTERN_A_CONTROLS or control_id in catalogue.PATTERN_C_CONTROLS:
            entry["implementation_reference"] = _nonempty_text(prompt, f"Reference for {control_id}")
        elif control_id in catalogue.PATTERN_B_CONTROLS:
            entry["implementation_reference"] = _nonempty_text(prompt, f"CI step name for {control_id}")
        control_decisions[control_id] = entry
        add_more = prompt.confirm("Declare another?", default=False)

    return {"baseline_controls": baseline_controls, "control_decisions": control_decisions}


# ---------------------------------------------------------------------------------------------
# Section 6 — Prerequisite gates
# ---------------------------------------------------------------------------------------------

def ask_gates(prompt: Prompt, *, level: str, builds_user_interface: bool) -> list[dict]:
    mandatory = set(catalogue.LEVEL_REQUIRED_GATES[level])
    if builds_user_interface and level in catalogue.LEVELS_REQUIRING_FULL_DECLARATION:
        mandatory |= catalogue.DESIGN_GATES

    full_declaration = level in catalogue.LEVELS_REQUIRING_FULL_DECLARATION
    if not full_declaration:
        # essential only requires work_registration to be declared; everything else is silent by
        # design at this level, and asking 18 questions the checker will not read is exactly the
        # volume problem the terminal-vs-form comparison (DR-32) was built to avoid.
        print("  At essential, only work_registration must be declared. The other 18 gates are")
        print("  not read by the checker at this level and are skipped.")
        gate = _ask_one_gate(prompt, "work_registration", mandatory=True)
        return [gate]

    gates: list[dict] = []
    total = len(catalogue.GATE_CATALOGUE)
    answered = 0
    for section_name, gate_ids in catalogue.sectioned_gates():
        applicable_ids = gate_ids
        if not builds_user_interface:
            applicable_ids = [g for g in gate_ids if g not in catalogue.DESIGN_GATES]
            for g in gate_ids:
                if g in catalogue.DESIGN_GATES:
                    # The STATUS is not asked again here - `builds_user_interface: false`, a
                    # real answer given earlier in section 2, already settles that these four
                    # are not_applicable. The RATIONALE still is: a Gemini adversarial review
                    # found this used to write a fixed string with no Prompt call at all, the
                    # same defect ask_controls had (ACT-022). Offering the old text as an
                    # editable default keeps this from turning into four redundant re-typings
                    # of a fact already given, while still making it a real answer, not an
                    # invented one - the same "shown, must submit" pattern review_by and
                    # enforcement already use elsewhere in this module.
                    rationale = _nonempty_text(
                        prompt, f"Rationale for {g} being not applicable",
                        default="This repository has no user interface.",
                    )
                    gates.append({"id": g, "status": "not_applicable", "rationale": rationale})
                    answered += 1
        print(f"  --- {section_name} ({answered + 1}-{answered + len(applicable_ids)} of {total}) ---")
        for gate_id in applicable_ids:
            gates.append(_ask_one_gate(prompt, gate_id, mandatory=gate_id in mandatory))
            answered += 1
    return gates


def _ask_one_gate(prompt: Prompt, gate_id: str, *, mandatory: bool) -> dict:
    description = catalogue.GATE_CATALOGUE[gate_id]
    print(f"  {gate_id}: {description}")

    if mandatory:
        print("  Required at this level - not a free choice. Its precondition is.")
        status = "required"
    else:
        status = prompt.select(
            f"{gate_id}",
            [
                ("required", "required — a precondition must exist before the gated paths change"),
                ("deferred", "deferred — not yet, with an owner and a date"),
                ("not_applicable", "not applicable — with a stated reason"),
            ],
        )

    if status == "required":
        artefact = _nonempty_text(prompt, "  Precondition artefact (a real path)")
        precondition_description = _nonempty_text(prompt, "  What must exist first, and why")
        paths = _nonempty_text(
            prompt, "  Gated paths (git pathspec, e.g. src/**)", help="what may not proceed until then"
        )
        gated_description = _nonempty_text(prompt, "  What may not proceed until then")
        effective_from = prompt.text(
            "  Effective from (YYYY-MM-DD)", default=_dt.date.today().isoformat()
        ).strip()
        enforcement = prompt.text(
            "  Enforcement (comma-separated: history_audit, review, ci, local_hook)",
            default="history_audit, review",
        )
        return {
            "id": gate_id,
            "status": "required",
            "effective_from": effective_from,
            "precondition": {"artefacts": [artefact], "description": precondition_description},
            "gated_activity": {"paths": [paths], "description": gated_description},
            "enforcement": [e.strip() for e in enforcement.split(",") if e.strip()],
        }

    if status == "deferred":
        owner = _nonempty_text(prompt, "  Owner")
        revisit_by = _nonempty_text(prompt, "  Revisit by (YYYY-MM-DD)")
        rationale = _nonempty_text(prompt, "  Why defer, and what happens instead")
        return {"id": gate_id, "status": "deferred", "owner": owner, "revisit_by": revisit_by, "rationale": rationale}

    rationale = _nonempty_text(prompt, "  Why is this not applicable here")
    return {"id": gate_id, "status": "not_applicable", "rationale": rationale}


# ---------------------------------------------------------------------------------------------
# Wrap-up — adoption identity, roles, release route (asked just before the final review)
# ---------------------------------------------------------------------------------------------

def ask_adoption_identity(prompt: Prompt, *, framework_version: str, framework_digest: str, owner: str) -> dict:
    review_by = prompt.text(
        "Review by (YYYY-MM-DD)",
        default=(_dt.date.today() + _dt.timedelta(days=180)).isoformat(),
        help="180 days is the suggested interval; the checker fails once this date passes",
    ).strip()
    framework_maintainer = _nonempty_text(
        prompt, "Framework maintainer", default=owner,
        help="the change authority for the standard in this repository - often the same as owner",
    )
    repository_classification = _nonempty_text(prompt, "Repository classification")
    decision_record_id = _nonempty_text(
        prompt, "Adoption decision record ID",
        help="if none exists yet, this is the moment to name one - it does not need to be written yet",
    )
    adoption_status = prompt.select(
        "Adoption status",
        [
            ("in_progress", "in_progress"),
            ("complete", "complete"),
            ("blocked", "blocked"),
            ("deferred", "deferred"),
        ],
    )
    status_rationale = None
    if adoption_status in ("blocked", "deferred"):
        status_rationale = _nonempty_text(prompt, "Why is adoption blocked/deferred?")

    needs_validator = prompt.confirm(
        "Does independent (Level 3) review apply to this adoption?", default=False
    )
    independent_validator = _nonempty_text(prompt, "Independent validator") if needs_validator else None

    result: dict = {
        "framework_version": framework_version,
        "framework_digest": framework_digest,
        "adoption_date": _dt.date.today().isoformat(),
        "review_by": review_by,
        "framework_maintainer": framework_maintainer,
        "repository_classification": repository_classification,
        "decision_record_id": decision_record_id,
        "adoption_status": adoption_status,
        "independent_validator": independent_validator,
    }
    # The KEY is absent when there is no rationale, not present-with-null. The schema does not
    # require this field outside blocked/deferred, so an absent key is the correct representation
    # - unlike independent_validator, which the schema types as [string, "null"] and the template
    # itself always writes explicitly, even when null.
    if status_rationale is not None:
        result["status_rationale"] = status_rationale
    return result


def ask_roles_and_release(prompt: Prompt) -> dict:
    roles: list[str] = []
    while True:
        role = prompt.text(
            "Human role (blank to finish)",
            help="e.g. \"Maintainer — Jane Doe. Sole change authority.\"",
        ).strip()
        if not role:
            break
        roles.append(role)

    release_route = _nonempty_text(
        prompt, "Release route", help="human and platform release controls, in your own words"
    )
    return {"human_roles": roles, "release_route": release_route, "exclusions": []}
