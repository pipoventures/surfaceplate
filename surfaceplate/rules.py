"""The rules the wizard validates with and the checker checks with, held once.

`DR-48` records why this module exists. The date rules, the identifier pattern, the placeholder
pattern and "a named path is tracked by git" were written twice - once in `check_conformance.py`
and once in `adopt/validators.py` - and had drifted: the wizard accepted a future `effective_from`,
a 401-day `review_by`, a one-character `application_id` and an untracked path, each of which the
checker's first run then rejected (`F66`). Both now import from here and neither restates a rule
this module holds.

This file is install payload. It travels beside the vendored checker, which imports it as a
sibling, so an adopting repository needs nothing else - and `tests/check_vendored_current.py`
holds the vendored copy current with this one.

Each `*_state` function returns a short state name and the parsed value where there is one. The
checker maps states to finding codes; the wizard maps them to messages beside the field. Neither
side re-derives the comparison.
"""

from __future__ import annotations

import datetime as _dt
import re
import subprocess
from pathlib import Path

# `application_id`: the schema's own pattern, quoted from `schemas/application-profile.schema.yaml`.
APPLICATION_ID = re.compile(r"^[a-z0-9][a-z0-9_-]+$")

# What makes an artefact "still a template". Token-based, and deliberately NOT pattern-based on
# angle brackets - `F14` and `DR-17` record why a shape-based branch was removed and must not
# return without a seen-to-fail case that separates a slot from a metavariable.
PLACEHOLDER_PATTERN = re.compile(
    r"\breplace[-_ ]?me\b|\bTBD\b|\bTBC\b|\bTODO\b",
    re.IGNORECASE,
)

# `adoption.review_by` may not sit more than this many days ahead: without a cap an adopter could
# set it to 2099 and the control would be decorative.
MAX_REVIEW_HORIZON_DAYS = 400

# The schema's date and instant forms. `date.fromisoformat` accepts basic ISO (`20260901`) from
# Python 3.11, which the schema's `format: date` refuses - so the form is checked before parsing.
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_ISO_INSTANT = re.compile(
    r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?)?$"  # F104: as the schema
)


def iso_date(raw: object) -> _dt.date | None:
    """`raw` as a date if it is exactly the schema's `YYYY-MM-DD` form, else `None`."""
    text = str(raw).strip()
    if not _ISO_DATE.match(text):
        return None
    try:
        return _dt.date.fromisoformat(text)
    except ValueError:
        return None


def parse_effective_from(raw: object) -> tuple[_dt.date, str]:
    """`effective_from` as `(date, git --since argument)`. Raises `ValueError` when unreadable.

    `F47`: the field may carry a time, and that is the whole point of accepting one - a gate binds
    from an instant, and a date can only say "midnight". Date-only values keep their exact
    previous meaning: midnight, stated explicitly, because `F48` found that a bare date handed to
    `git log --since` means "that date, at whatever time you happen to run the check".
    """
    text = str(raw).strip()
    if not _ISO_INSTANT.match(text):
        raise ValueError(f"not a schema date or instant: {text!r}")
    day = _dt.date.fromisoformat(text[:10])
    if len(text) <= 10:
        return day, f"{day.isoformat()}T00:00:00"
    _dt.datetime.fromisoformat(text.replace("Z", "+00:00"))  # unreadable instants raise here
    return day, text


def effective_is_future(raw: object, day: _dt.date, today: _dt.date) -> bool:
    """Whether this `effective_from` is still to come, compared as an instant when one is given."""
    text = str(raw).strip()
    if len(text) <= 10:
        return day > today
    try:
        moment = _dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return day > today
    now = _dt.datetime.now(moment.tzinfo) if moment.tzinfo else _dt.datetime.now()
    return moment > now


def effective_from_state(raw: object, today: _dt.date | None = None) -> tuple[str, _dt.date | None]:
    """`absent`, `unreadable`, `future` or `ok`, with the date where one parsed."""
    today = today or _dt.date.today()
    if raw is None or not str(raw).strip():
        return "absent", None
    try:
        day, _since = parse_effective_from(raw)
    except ValueError:
        return "unreadable", None
    if effective_is_future(raw, day, today):
        return "future", day
    return "ok", day


def review_by_state(raw: object, today: _dt.date | None = None) -> tuple[str, _dt.date | None]:
    """`absent`, `unreadable`, `beyond_horizon`, `overdue` or `ok`, with the date where one parsed."""
    today = today or _dt.date.today()
    if raw is None or not str(raw).strip():
        return "absent", None
    day = iso_date(raw)
    if day is None:
        return "unreadable", None
    if day > today + _dt.timedelta(days=MAX_REVIEW_HORIZON_DAYS):
        return "beyond_horizon", day
    if day < today:
        return "overdue", day
    return "ok", day


def revisit_by_state(raw: object, today: _dt.date | None = None) -> tuple[str, _dt.date | None]:
    """`absent`, `unreadable`, `overdue` or `ok`, with the date where one parsed."""
    today = today or _dt.date.today()
    if raw is None or not str(raw).strip():
        return "absent", None
    day = iso_date(raw)
    if day is None:
        return "unreadable", None
    if day < today:
        return "overdue", day
    return "ok", day


def is_tracked(repo: Path, path: str) -> bool:
    """Whether git considers `path` part of `repo` - a file, or a directory holding tracked files.

    `SP051` requires tracked, not merely present: an untracked file exists on one machine and
    nowhere else, so it is not evidence available to anyone else. `False` when git cannot answer.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", path],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0
