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

# `DR-69`'s twelve topics, and `DR-71`'s mapping of each control to the one it belongs to.
#
# Held here, once, for the reason `DR-48` created this module: the checker and the wizard both
# need it and neither may restate it. `DR-71` rejected putting a control's topic in the ADOPTER's
# profile - a control's topic is decided by this framework, so nesting it into every adopter's
# file would restate a fact this framework already owns, where it could only be redundant or
# wrong. That is `F121`'s defect ("a constant column carries no information") one level up.
#
# What the topic axis reaches in the profile is therefore its LAYOUT, not its keys: `render.py`
# groups `control_decisions` under generated headings from this map, and the written keys stay
# flat and canonical. An adopter reads twelve subjects; the contract carries no duplicate.
TOPIC_NAMES: dict[int, str] = {
    1: "Authority and the documentary record",
    2: "Decision authority and escalation",
    3: "Work definition",
    4: "Work tracking",
    5: "Risk and proportionality",
    6: "Evidence and completion",
    7: "Testing",
    8: "Confidentiality and data boundaries",
    9: "Dependencies and supply chain",
    10: "Provenance and lineage",
    11: "Concurrency and shared-repository discipline",
    12: "Enforcement and change control",
}

# Every control this framework defines, and the one topic it belongs to. Topics 2, 4, 5, 11 and 12
# carry no control, which is informative rather than a gap: those topics are governed by rules and
# by prerequisite gates rather than by declared controls.
#
# Prerequisite gates deliberately keep their own six-group catalogue order and are NOT re-cut
# across these twelve (`DR-71`): nineteen gates do not divide cleanly across twelve subjects, and
# `DR-69` kept `core/PREREQUISITE_GATES.md` whole as a specification whose internal grouping is
# its own.
CONTROL_TOPICS: dict[str, int] = {
    "documentation_authority": 1,
    "agent_work_packets": 3,
    "actual_diff_review": 6,
    "assurance_findings": 6,
    "contract_tests": 7,
    "deterministic_tests": 7,
    "secret_hygiene": 8,
    "dependency_lock": 9,
    "provenance": 10,
    "run_lineage": 10,
    "method_registry": 10,
    "overrides": 10,
}

# `DR-67`. The agents this standard emits for, and the destination prefixes each one owns.
# Held here rather than in the installer because the checker needs the same set and cannot import
# the installer - it is vendored standalone beside this file. Restating it in two places is the
# drift `DR-48` created this module to stop.
#
# `.github/copilot-instructions.md` is listed under `copilot` although it is not a payload path:
# the block upsert creates it, so declining the channel has to skip it there too (`F122`).
AGENT_CHANNELS: dict[str, tuple[str, ...]] = {
    "claude": (".claude/rules/", ".claude/skills/"),
    "copilot": (".github/instructions/", ".github/skills/", ".github/copilot-instructions.md"),
}

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


# `F126`. An instant is RECORDED at one moment and CHECKED against a live clock read later, and
# those two readings are not guaranteed to agree. NTP steps, VM suspend/resume, and WSL2's periodic
# resync against its host can all move the wall clock backward by around a second - which makes a
# timestamp minted before the adjustment look like the future after it.
#
# Measured, not assumed: an instrumented matrix run caught six verdicts where the recorded
# `effective_from` sat ~1.2s AHEAD of the clock the checker read moments later, with the write path
# truncating microseconds DOWNWARD and so incapable of producing that gap on a monotonic clock. The
# mechanism was never forced to reproduce and is recorded as INFERENCE; the effect is FACT.
#
# The tolerance is what makes the comparison robust to it. Sixty seconds is chosen because nobody
# defers a gate by a minute: a gate genuinely "dated in the future" is hours or days out, and
# `F47`/`DR-44`'s intent - that "an instant later today is genuinely in the future and must still
# be refused" - survives untouched, because an instant later today is hours ahead, not seconds.
#
# Instants only. A date-valued `effective_from` is compared date-to-date, where a one-day error
# needs a midnight crossing rather than a clock nudge, and where a tolerance would weaken the
# deliberate "dated tomorrow" refusal for no gain.
FUTURE_INSTANT_TOLERANCE = _dt.timedelta(seconds=60)


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
    return moment > now + FUTURE_INSTANT_TOLERANCE


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
