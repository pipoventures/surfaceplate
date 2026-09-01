"""Field validation, extracted so a screen and a script apply the same rules.

Previously these lived inside `sections.py`'s asking functions - `_nonempty_text`'s `while True`
loop and `ask_identity`'s regex retry. That worked when there was exactly one asker. With a screen
and a scripted interview both driving the same `FieldSpec`, a rule that lives inside one of them is
a rule the other silently does not have, so they move here and both consume them by name
(`FieldSpec.validate`).

Each validator returns an error string, or `None` when the value is acceptable. Returning a message
rather than raising is deliberate: a screen shows it inline beside the field and lets the human fix
it, which is the whole point of validating in the interface rather than at write time.

**These are the wizard's own front door, not the checker.** `wizard._verify` still runs the schema
and the placeholder scan over the assembled profile before anything is written, and remains the
authority. Nothing here weakens that; it just stops a human getting to the end of a long session
before being told a date was malformed - which is the same class of problem `F36` was.
"""

from __future__ import annotations

import datetime as _dt
import re

_APPLICATION_ID = re.compile(r"^[a-z0-9][a-z0-9_-]+$")

# The enforcement values `application-profile.schema.yaml` allows. Stated here so a human typing a
# fourth thing is told at the field rather than by a schema error after the review screen - the
# exact confusion `F36`'s investigation found this field could produce.
ENFORCEMENT_VALUES = ("history_audit", "local_hook", "review", "ci", "unenforced")


def nonempty(value: str) -> str | None:
    """The one rule applied uniformly, everywhere: an empty string is never a decision."""
    return None if value.strip() else "This cannot be blank."


def application_id(value: str) -> str | None:
    if not value.strip():
        return "This cannot be blank."
    if not _APPLICATION_ID.match(value.strip()):
        return (
            "Must start with a letter or digit and use only lowercase letters, digits, hyphens "
            "or underscores."
        )
    return None


def date(value: str) -> str | None:
    if not value.strip():
        return "This cannot be blank."
    try:
        _dt.date.fromisoformat(value.strip())
    except ValueError:
        return "Use YYYY-MM-DD."
    return None


def enforcement(value: str) -> str | None:
    """A comma-separated list, every item of which the schema recognises.

    `F36` found this field rendered with no escaping at all, and unreachable through a
    schema-valid answer only because the schema happens to constrain it. Validating here means a
    mistyped value is caught where it was typed, rather than surviving into the renderer.
    """
    items = [item.strip() for item in value.split(",") if item.strip()]
    if not items:
        return "Name at least one: " + ", ".join(ENFORCEMENT_VALUES) + "."
    unknown = [item for item in items if item not in ENFORCEMENT_VALUES]
    if unknown:
        return f"Not recognised: {', '.join(unknown)}. Allowed: {', '.join(ENFORCEMENT_VALUES)}."
    return None


_VALIDATORS = {
    "nonempty": nonempty,
    "application_id": application_id,
    "date": date,
    "enforcement": enforcement,
}


def check(name: str, value: object) -> str | None:
    """Apply the validator `name` to `value`. An empty name means anything is acceptable,
    including blank - used for booleans and for genuinely optional fields such as `human_roles`."""
    if not name:
        return None
    validator = _VALIDATORS.get(name)
    if validator is None:
        raise KeyError(f"unknown validator: {name!r}")
    if not isinstance(value, str):
        return None  # booleans and choices are constrained by their widget, not by a text rule
    return validator(value)
