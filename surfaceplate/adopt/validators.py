"""Field validation, extracted so a screen and a script apply the same rules.

Previously these lived inside `sections.py`'s asking functions. With a screen and a scripted
interview both driving the same `FieldSpec`, a rule that lives inside one of them is a rule the
other silently does not have, so they live here and both consume them by name (`FieldSpec.validate`).

**The rules themselves live in `surfaceplate/rules.py`, shared with the checker (`DR-48`).** `F66`
found this module accepting a future `effective_from`, a 401-day and a past `review_by`, a
one-character `application_id`, basic-ISO dates and untracked paths - each rejected by the
checker's first run - because the rules had been written twice. Nothing here restates a rule that
module holds; this module turns its states into messages beside the field.

Each validator returns an error string, or `None` when the value is acceptable. Returning a message
rather than raising is deliberate: a screen shows it inline and lets the human fix it, which is the
whole point of validating in the interface rather than at write time.

**These are the wizard's own front door, not the checker.** `wizard._verify` still runs the schema
and the placeholder scan over the assembled profile before anything is written, and remains the
authority.
"""

from __future__ import annotations

from pathlib import Path

from surfaceplate import rules

# The enforcement values `application-profile.schema.yaml` allows. Stated here so a human typing a
# fourth thing is told at the field rather than by a schema error after the review screen.
ENFORCEMENT_VALUES = ("history_audit", "local_hook", "review", "ci", "unenforced")

BLANK = "This cannot be blank."
PLACEHOLDER = (
    "That is a template placeholder (TBD, TODO, replace-me), which the checker rejects. "
    "Type the real value."
)
DATE_FORM = "Use YYYY-MM-DD."


def nonempty(value: str) -> str | None:
    """The one rule applied uniformly, everywhere: an empty string is never a decision, and
    `check` turns an absent value into one before it reaches here."""
    return None if value.strip() else BLANK


def application_id(value: str) -> str | None:
    if not value.strip():
        return BLANK
    if not rules.APPLICATION_ID.match(value.strip()):
        return (
            "Must be at least two characters, start with a letter or digit, and use only "
            "lowercase letters, digits, hyphens or underscores."
        )
    return None


def date(value: str) -> str | None:
    if not value.strip():
        return BLANK
    return None if rules.iso_date(value) else DATE_FORM


def effective_from(value: str) -> str | None:
    """A date, or a full instant (`DR-44`), and never in the future: `SP033` refuses a gate dated
    later, so accepting one here would write a profile that fails its first check."""
    state, _day = rules.effective_from_state(value)
    if state == "absent":
        return BLANK
    if state == "unreadable":
        return "Use YYYY-MM-DD, or YYYY-MM-DDThh:mm:ss+hh:mm to bind from an instant."
    if state == "future":
        return "This is in the future. A gate that binds later is a deferral - date it today or earlier."
    return None


def review_by(value: str) -> str | None:
    """Between today and today plus 400 days - `SP025` and `SP026`'s window, held in `rules`."""
    state, _day = rules.review_by_state(value)
    if state == "absent":
        return BLANK
    if state == "unreadable":
        return DATE_FORM
    if state == "beyond_horizon":
        return f"More than {rules.MAX_REVIEW_HORIZON_DAYS} days away. A review deferred indefinitely is not a review."
    if state == "overdue":
        return "This is in the past. A review date that has already passed fails the first check."
    return None


def revisit_by(value: str) -> str | None:
    """Not yet past - `SP054`'s rule, held in `rules`."""
    state, _day = rules.revisit_by_state(value)
    if state == "absent":
        return BLANK
    if state == "unreadable":
        return DATE_FORM
    if state == "overdue":
        return "This is in the past. A deferral whose revisit date has passed fails the first check."
    return None


def enforcement(value: str) -> str | None:
    """A comma-separated list, every item of which the schema recognises."""
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        return "Name at least one: " + ", ".join(ENFORCEMENT_VALUES) + "."
    unknown = [item for item in items if item not in ENFORCEMENT_VALUES]
    if unknown:
        return f"Not recognised: {', '.join(unknown)}. Allowed: {', '.join(ENFORCEMENT_VALUES)}."
    return None


def tracked_path(value: str, repo: Path | None) -> str | None:
    """A path git tracks in this repository - `SP032` and `SP051` require tracked, not merely
    present. Without a repository to ask, only blankness is checked and the reason is stated in
    the parity table beside the codes that read this."""
    if not value.strip():
        return BLANK
    if repo is None:
        return None
    if not (repo / value.strip()).exists():
        return "Nothing exists at that path in this repository."
    if not rules.is_tracked(repo, value.strip()):
        return "That path exists but is not tracked by git. Commit it first - the checker only counts what git holds."
    return None


def ci_step(value: str, repo: Path | None) -> str | None:
    """A step name found in a workflow file - `SP053` looks it up by name."""
    if not value.strip():
        return BLANK
    if repo is None:
        return None
    from surfaceplate.adopt import discover

    if value.strip() not in discover.candidate_ci_steps(repo):
        return "No workflow in this repository has a step with that name."
    return None


_VALIDATORS = {
    "nonempty": nonempty,
    "application_id": application_id,
    "date": date,
    "effective_from": effective_from,
    "review_by": review_by,
    "revisit_by": revisit_by,
    "enforcement": enforcement,
}
_REPO_VALIDATORS = {
    "tracked_path": tracked_path,
    "ci_step": ci_step,
}


def check(name: str, value: object, *, repo: Path | None = None) -> str | None:
    """Apply the validator `name` to `value`. An empty name means anything is acceptable,
    including blank - used for booleans and for genuinely optional fields such as `human_roles`.

    `None` is blank (`F64`). Booleans and lists still pass: a tick box always shows a state, and
    the only list-valued fields carry no validator. Every string validator also refuses a template
    placeholder (`F65`): `SP020` rejects one at check time, so accepting it at the field let a
    human reach the review before being told.
    """
    if not name:
        return None
    if name not in _VALIDATORS and name not in _REPO_VALIDATORS:
        raise KeyError(f"unknown validator: {name!r}")
    if value is None:
        value = ""
    if not isinstance(value, str):
        return None  # booleans and lists are constrained by their widget, not by a text rule
    if rules.PLACEHOLDER_PATTERN.search(value):
        return PLACEHOLDER
    if name in _REPO_VALIDATORS:
        return _REPO_VALIDATORS[name](value, repo)
    return _VALIDATORS[name](value)
