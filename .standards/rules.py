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


# ---------------------------------------------------------------------------
# Currency: is the installed standard the published one? (`F124`, `DR-68`, `DR-72`)
#
# Integrity and currency are different properties and only one of them can be established
# offline. `DR-45` is explicit that the framework anchor "records the manifest of the tree
# installed FROM, which is a historical fact, not a live invariant", so nothing in a sealed
# checkout can answer whether a newer version exists.
#
# Held here for `DR-48`'s reason: `doctor --online` asked this question first and the installed
# conformance workflow now asks it too (`DR-72`). Two implementations of "is 0.9.0 newer than
# 0.17.0" is exactly the drift this module exists to prevent - and that comparison has a known
# wrong answer if written naively, which is the next function's whole subject.
PYPI_JSON = "https://pypi.org/pypi/surfaceplate/json"
PYPI_TIMEOUT_SECONDS = 15


def version_key(version: str) -> tuple:
    """Order two version strings without taking a dependency to do it.

    Numeric segments compare as numbers so `0.9.0` sorts below `0.17.0`, which a string
    comparison gets backwards - the case this repository would have hit first. Anything
    unparseable falls back to comparing as text, which is wrong in general and never worse than
    not answering: the only consequence is an advisory phrased as "behind" when it is "ahead".
    """
    parts = []
    for segment in str(version).replace("-", ".").split("."):
        parts.append((0, int(segment)) if segment.isdigit() else (1, segment))
    return tuple(parts)


def published_version(timeout: int = PYPI_TIMEOUT_SECONDS) -> tuple[str | None, str | None]:
    """`(version, error)` from the index. Exactly one of the two is ever set.

    THE ONLY OUTBOUND REQUEST IN THIS MODULE, and it is made nowhere unless a caller asks for
    it. Importing this module opens no socket; `check_conformance.py` imports it on every run,
    including from the pre-commit hook, and must stay offline there.

    An unreachable index returns an error rather than a version, and every caller reports that
    as its own state - never as "current". Reporting `ok` because the network was down is the
    false green this framework exists to find.
    """
    import json
    import urllib.error
    import urllib.request

    request = urllib.request.Request(
        PYPI_JSON, headers={"Accept": "application/json", "User-Agent": "surfaceplate"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed https host
            latest = json.loads(response.read().decode("utf-8")).get("info", {}).get("version")
    except urllib.error.HTTPError as exc:
        return None, f"pypi.org answered {exc.code}"
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return None, f"could not reach pypi.org: {exc}"
    if not isinstance(latest, str) or not latest:
        return None, "pypi.org named no version"
    return latest, None


def currency_state(installed: str, published: str) -> str:
    """`current`, `ahead`, or `behind`.

    `ahead` is a different fact from `behind` and must not be reported as the same one. The
    repository that publishes the standard installs from its own working tree and is therefore
    always ahead by construction; telling it to "upgrade" to an older version would be advice
    that is simply wrong. Found by running this against this repository before shipping it.
    """
    if installed == published:
        return "current"
    return "ahead" if version_key(installed) > version_key(published) else "behind"


# ---------------------------------------------------------------------------
# Does this repository have dependencies at all? (`F132`, `DR-73`, `H22`)
#
# `dependency_lock` is the only control in the `essential` floor, and `SP051` requires it to name
# a real tracked file. A repository with no dependency manifest of any kind - a documentation
# repository, a policy repository, a monorepo subtree whose dependencies resolve a level up - has
# nothing to name and could not conform at any level. `F132` was found on exactly such a
# repository, by a person, on the wizard's first screen.
#
# `H22` chose to DERIVE the answer rather than let it be declared. Nothing is written in the
# profile, so nothing can be misdeclared, and the moment a manifest appears the floor returns
# without anyone having to remember to change a file.
#
# THE LIST IS DELIBERATELY GENEROUS, because the two errors are not symmetrical. Believing a
# manifest exists where none does sends a repository back to `F132`'s dead end - bad, and visible
# to whoever hits it. Believing NONE exists where one does silently waives the one control this
# standard applies to everyone - worse, and silent. So when in doubt, this list says "has
# dependencies".
#
# Two deliberate exclusions, stated so they read as decisions rather than oversights.
# `CMakeLists.txt` and `Dockerfile` both imply a supply chain, and neither has a lock file an
# adopter could name; including them would send C and container repositories to the same dead end
# this exists to remove. A repository that pins a base image and wants the control has always been
# free to decide `dependency_lock` required and name whatever it pins with.
DEPENDENCY_MANIFESTS: frozenset[str] = frozenset({
    # Python
    "pyproject.toml", "setup.py", "setup.cfg", "pipfile", "pipfile.lock", "poetry.lock",
    "requirements.lock", "environment.yml", "environment.yaml", "uv.lock", "pdm.lock",
    # JavaScript and friends
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json",
    "bun.lockb", "deno.json", "deno.jsonc", "deno.lock",
    # Go, Rust, Ruby, PHP
    "go.mod", "go.sum", "cargo.toml", "cargo.lock", "gemfile", "gemfile.lock",
    "composer.json", "composer.lock",
    # JVM
    "pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
    "ivy.xml", "build.sbt",
    # .NET
    "packages.config", "paket.dependencies", "paket.lock", "directory.packages.props",
    # Elixir, Dart, Swift, Perl, R, Haskell, Nix, Terraform, C/C++
    "mix.exs", "mix.lock", "pubspec.yaml", "pubspec.lock", "package.swift", "package.resolved",
    "podfile", "podfile.lock", "cartfile", "cpanfile", "makefile.pl", "description", "renv.lock",
    "stack.yaml", "cabal.project", "flake.nix", "flake.lock", ".terraform.lock.hcl",
    "conanfile.txt", "conanfile.py", "conan.lock", "vcpkg.json",
})

# `F135`: the files that RECORD RESOLVED VERSIONS, as against those that merely declare
# dependencies. The distinction is the finding: `pyproject.toml` was in the lock list, so the
# wizard proposed a MANIFEST as a LOCK and showed it to the adopter with origin `discovered` -
# a fact about their repository rather than a question.
#
# It is not that naming `pyproject.toml` is wrong. THIS repository names it, legitimately: its
# dependencies are pinned exactly there (`PyYAML==6.0.3`) and it has no separate lock. A name
# cannot tell those apart - a `pyproject.toml` may pin exactly or may declare ranges - and a tool
# that cannot tell must ask rather than assert. So a manifest is still typeable, and is never
# proposed.
#
# Held here rather than in `adopt/discover.py` because `DR-73` put the manifest question here and
# two modules answering "is this file a lock" differently is the drift `DR-48` created this module
# to prevent. That split was live for one day, introduced by the change that closed `F132`.
LOCK_FILES: tuple[str, ...] = (
    "requirements.txt",     # conventionally the pinned set; genuinely ambiguous, kept as a lock
    "requirements.lock", "poetry.lock", "Pipfile.lock", "uv.lock", "pdm.lock",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json", "bun.lockb",
    "deno.lock", "Cargo.lock", "go.sum", "gemfile.lock", "composer.lock", "mix.lock",
    "pubspec.lock", "Package.resolved", "podfile.lock", "paket.lock", "conan.lock",
    "renv.lock", "flake.lock", ".terraform.lock.hcl",
)


# Suffixes that are a manifest whatever the file is called.
DEPENDENCY_MANIFEST_SUFFIXES: tuple[str, ...] = (
    ".gemspec", ".csproj", ".fsproj", ".vbproj", ".cabal",
)

# A plain text file whose NAME says it pins dependencies, wherever it sits. This exists because
# the name list above is not enough, and the combinatorial matrix proved it rather than anyone
# reasoning it out: its `mixed` shape is built as "a pinned-dependency file no lock-file rule
# names" - `deps/pins.txt`, holding `PyYAML==6.0.3` - and the first version of this derivation
# waived the control for it. That is a repository with real dependencies losing the one control
# this standard applies to everyone, which is the exact error this whole list is arranged to
# avoid. A file called `pins.txt`, `constraints.in` or `deps/versions.txt` is a dependency
# declaration under a name nobody standardised, and is treated as one.
_PINNING_WORDS = ("requirement", "constraint", "pin", "dep", "version", "lock")
_PINNING_SUFFIXES = (".txt", ".in", ".lock", ".toml", ".yaml", ".yml", ".json")
_PINNING_DIRS = ("deps/", "dependencies/", "requirements/", "constraints/")

# Paths this framework owns. A manifest inside the installed payload is the framework's, not the
# adopter's, and must never be read as evidence that the adopter has dependencies.
_FRAMEWORK_OWNED = (
    ".standards/", ".claude/", ".githooks/",
    ".github/instructions/", ".github/skills/", ".github/workflows/standards-conformance.yml",
)


# The controls whose LEVEL FLOOR a repository can fail to be held to for a reason derived from
# the repository itself. Named as a set of exactly one rather than special-cased inline: the
# wizard uses it to decide when a missing answer is legitimate, and a missing answer for anything
# NOT in this set must keep raising loudly rather than quietly dropping a control.
WAIVABLE_CONTROLS: frozenset[str] = frozenset({"dependency_lock"})


def _adopter_tracked_files(repo: Path) -> list[str] | None:
    """The repository's own tracked files, framework-owned paths removed. `None` if git cannot say.

    `None` is not an empty list and the callers must not treat it as one: "git could not answer"
    and "there are no files" are different facts, and only the second is evidence of anything.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return [
        line for line in result.stdout.splitlines()
        if line and not line.startswith(_FRAMEWORK_OWNED)
    ]


def dependency_manifest(repo: Path) -> tuple[str | None, str]:
    """`(path, state)` for the adopter's own dependency manifest.

    `state` is one of:

    - `found`    - `path` names one. `dependency_lock` applies as it always has.
    - `none`     - the repository tracks files and not one of them is a manifest. The
                   `dependency_lock` floor is lifted, and the check says so on every run.
    - `unknown`  - **git could not answer.** The floor is NOT lifted: an unanswered question is
                   not a passing one, and waiving a control because a subprocess failed would be
                   the false green this framework exists to find.

    An empty list is `none`, not `unknown`, and the distinction was got wrong first time here.
    A repository whose only tracked files are this framework's own - a fresh install, nothing
    else committed yet - owns no manifest, and git said so successfully. Conflating that with a
    failed subprocess made a brand-new repository unable to conform, which is `F132` again for a
    different shape. What matters is whether the question was ANSWERED, not whether the answer
    was interesting.
    """
    tracked = _adopter_tracked_files(repo)
    if tracked is None:
        return None, "unknown"
    for path in tracked:
        name = path.split("/")[-1].lower()
        if name in DEPENDENCY_MANIFESTS or name.endswith(DEPENDENCY_MANIFEST_SUFFIXES):
            return path, "found"
        lower = path.lower()
        if name.endswith(_PINNING_SUFFIXES) and (
            any(word in name for word in _PINNING_WORDS)
            or any(seg in lower for seg in _PINNING_DIRS)
        ):
            return path, "found"
    return None, "none"


# ---------------------------------------------------------------------------
# YAML turns a date-shaped scalar into a date object, and every schema here says `type: string`
# (`F137`, `DR-75`).
#
# The templates this framework ships say `raised_on: replace-me  # YYYY-MM-DD`. An adopter who
# does exactly that - replaces the token with `2026-09-09` - writes a valid YAML date, which
# `yaml.safe_load` returns as `datetime.date`, which the schema rejects as "not of type 'string'".
# **The natural completion of a shipped template fails the shipped schema**, on the FAQ's own
# stated remedy for a bypassed gate, and on `adoption_date` for anyone filling the profile by hand
# rather than running the wizard. The wizard's own output is unaffected: it quotes.
#
# Normalising here rather than only quoting the templates, because quoting relies on the adopter
# reading a comment and a normaliser does not. Nothing is lost: a `datetime.date` can only have
# come from a date-shaped scalar, and `.isoformat()` is the value the schema's `format: date`
# wanted. Where the intent really is "not a date", the value was never a date scalar to begin with.


def dates_as_strings(value):
    """Recursively replace `date`/`datetime`/`time` with their ISO 8601 text.

    Applied to every hand-written record this checker loads, immediately after parsing and before
    anything looks at it, so no later code has to know which YAML scalars auto-typed.
    """
    if isinstance(value, dict):
        return {k: dates_as_strings(v) for k, v in value.items()}
    if isinstance(value, list):
        return [dates_as_strings(v) for v in value]
    if isinstance(value, (_dt.datetime, _dt.date, _dt.time)):
        return value.isoformat()
    return value


# ---------------------------------------------------------------------------
# `DR-69` surface 5, `DR-77`: every finding code belongs to one of the twelve topics, so a report
# can be read, filtered and routed by subject rather than by code number.
#
# THE RULE APPLIED, stated because it decides the hard cases: **a code's topic is the subject the
# finding is ABOUT, not the mechanism that detects it.** `SP008` (the conformance block has been
# altered) is detected by a digest, which is enforcement machinery, but its subject is the block
# that declares what governs the repository - Topic 1. `SP004` and `SP005` are detected the same
# way and their subject is the installed standard itself - Topic 12.
#
# THE LIMITATION, stated rather than discovered: a **control-generic** code cannot honestly carry
# one topic. `SP051` fires for `dependency_lock` (Topic 9) and for `assurance_findings` (Topic 6)
# alike, and the code does not know which until it fires. Those map to Topic 12, whose subject
# genuinely is "a declaration and the thing that verifies it". A consumer wanting the control's own
# topic has it: the finding names the control, and `CONTROL_TOPICS` maps it.
SP_TOPICS: dict[str, int] = {
    # The install, its integrity, and the workflow that runs the check.
    "SP001": 12, "SP002": 12, "SP003": 12, "SP004": 12, "SP005": 12, "SP009": 12,
    "SP048": 12, "SP049": 12,
    # The agent instruction file and the block that declares what governs here.
    "SP006": 1, "SP007": 1, "SP008": 1,
    # The application profile: present, readable, schema-conformant, free of placeholders.
    "SP010": 12, "SP011": 12, "SP012": 12, "SP013": 12, "SP014": 12, "SP015": 12, "SP016": 12,
    "SP020": 12,
    # Levels and their floors; the gate catalogue and what a level obliges of it.
    "SP017": 12, "SP021": 12, "SP022": 12, "SP027": 12, "SP028": 12, "SP029": 12, "SP030": 12,
    "SP037": 12,
    # Adoption identity and the currency of the record that states it.
    "SP018": 1, "SP019": 1, "SP024": 1, "SP025": 1, "SP026": 1,
    # Deferrals, exceptions, and gates left unexplained: who decided, and did they say why.
    "SP023": 2, "SP031": 2, "SP043": 2,
    # Gate mechanics: preconditions, effective dates, history, the staged snapshot, pathspecs.
    "SP032": 12, "SP033": 12, "SP034": 12, "SP035": 12, "SP038": 12, "SP039": 12,
    "SP040": 12, "SP041": 12, "SP042": 12,
    # Secrets: the one control family with a topic of its own.
    "SP046": 8, "SP047": 8,
    # The documentary record: exemptions, authority, and an adopter's declared canon.
    "SP050": 1, "SP052": 1, "SP060": 1,
    # Control-generic - see the limitation above.
    "SP051": 12, "SP053": 12, "SP055": 12, "SP056": 12, "SP057": 12, "SP058": 12, "SP059": 12,
    # Records that carry their own revisit dates: overrides and the lineage family.
    "SP054": 10,
}
