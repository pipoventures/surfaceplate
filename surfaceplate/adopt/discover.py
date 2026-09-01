"""What this repository already contains, offered as answers instead of a blank box.

`DR-38` records why this exists. A maintainer ran the wizard against a real repository and could
not finish it, and his verdict was about the interaction model rather than any single defect:
*"free text is confusing and really prone to errors... the wizard should do a discovery of the repo
first to identify what is the potential candidate for each question."*

So every structural question - which file is the precondition, which paths does the gate cover,
which CI step implements this control - is answered from a list built by reading the repository,
and free text remains only where the answer is genuinely prose.

**This reconciles `example_answers.py`'s scoping rather than reversing it.** That module refused to
offer example artefact paths, because "a plausible-looking example risks being copied unedited" -
and it was right: an invented path that looks real is worse than a blank field. A file that
actually exists in the adopter's own repository is a different kind of thing entirely. The rule
this module keeps is the one underneath that decision: **never offer something that isn't there.**

**Git-aware throughout.** Candidates come from `git ls-files`, so an ignored build artefact, a
`.venv`, or an untracked scratch file is never offered as though it were part of the repository.
That is also what stops the lists being unusably long. Where git is unavailable the functions return
nothing rather than falling back to a filesystem walk: an empty list makes the field behave as it
did before, while a walk would quietly start offering junk.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

# Directories whose contents are plausible governance artefacts. Not exhaustive, and not a
# judgement about the adopter's layout - just the places this framework's own documents, and both
# worked examples, actually put things.
_ARTEFACT_DIRS = ("docs", "governance", "activity", "adr", "decisions", ".github")
_ARTEFACT_SUFFIXES = (".md", ".yaml", ".yml")

# Files that are a lock file by name. `dependency_lock` names one of these.
_LOCK_FILES = (
    "requirements.txt",
    "requirements.lock",
    "poetry.lock",
    "Pipfile.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "go.sum",
    "gemfile.lock",
    "pyproject.toml",
)

# Top-level directories that usually hold the code a gate would guard.
_SOURCE_DIRS = ("src", "lib", "app", "pkg", "internal", "cmd", "services", "packages")

_CI_DIRS = (".github/workflows", ".gitlab-ci.d")

# Short enough to read. Forty was "too many options to know which one is the right one", and a list
# nobody can scan is a list nobody uses. Ranking (below) is what makes a short list the RIGHT short
# list rather than an arbitrary truncation.
_MAX_CANDIDATES = 200   # what `scan` keeps; the per-field list is cut to `SHOWN` after ranking
SHOWN = 12              # what an adopter is actually offered, once ranked for the field at hand


def _tracked_files(repo: Path) -> list[str]:
    """Every path git considers part of this repository, or `[]` if git cannot answer.

    Deliberately not a filesystem walk. A walk offers `.venv/`, `node_modules/` and build output as
    candidate governance artefacts, which is worse than offering nothing.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "--cached", "--exclude-standard"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line]


def _capped(values: list[str]) -> list[str]:
    """De-duplicated, order preserved, and short enough to pick from.

    A list nobody can scan is a list nobody uses, and a repository with three thousand markdown
    files would produce one. The cap is on the OFFER, never on what may be typed: every field that
    takes a candidate list also accepts a value that is not in it.

    Insertion order is kept deliberately - each caller ranks its own candidates, and sorting here
    would throw that away and bury the most likely answer somewhere alphabetical.
    """
    return list(dict.fromkeys(values))[:_MAX_CANDIDATES]


# Paths this framework installs into an adopting repository. They are real files and a gate may
# legitimately point at one, so they are still offered - but never ahead of the adopter's own
# documents, which are almost always the intended answer.
_FRAMEWORK_OWNED = (".standards/", ".github/instructions/", ".github/skills/", ".claude/")


# Where a governance artefact is most likely to be, most likely first. Ranking matters more than
# it looks: people pick the first plausible line they see, so an alphabetical list that opens with
# `.github/` because a dot sorts before a letter is actively misleading.
_ARTEFACT_RANK = ("docs/", "governance/", "activity/", "decisions/", "adr/")


def _adopter_first(paths: list[str]) -> list[str]:
    """Ranked by how likely the adopter means it: their own governance directories first, then
    their root-level documents, then anything else of theirs, then what this framework installed.

    Matches a bare directory name as well as a prefix, because the register-directory candidates are
    directories (`governance`) where the artefact candidates are files (`governance/x.yaml`).
    """

    def rank(path: str) -> tuple[int, str]:
        if path.startswith(_FRAMEWORK_OWNED):
            return (len(_ARTEFACT_RANK) + 2, path)
        for index, prefix in enumerate(_ARTEFACT_RANK):
            if path == prefix.rstrip("/") or path.startswith(prefix):
                return (index, path)
        if "/" not in path:
            return (len(_ARTEFACT_RANK), path)
        return (len(_ARTEFACT_RANK) + 1, path)

    return sorted(paths, key=rank)


# Words that suggest a file is the artefact a particular gate is about. Ranking only; nothing here
# decides anything, and every candidate stays in the list either way.
GATE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "work_registration": ("register", "activity", "backlog"),
    "register_currency": ("register", "activity"),
    "work_contract": ("packet", "contract", "brief"),
    "risk_classification": ("risk", "classification"),
    "decision_before_implementation": ("decision", "adr"),
    "records_before_release": ("release", "checklist"),
    "change_record_before_completion": ("changelog", "change"),
    "authority_map": ("authority", "source_of_truth", "inventory"),
    "authority_same_change": ("authority",),
    "test_convention": ("test", "convention"),
    "regression_before_merge": ("regression", "test"),
    "equivalence_evidence": ("equivalence", "protocol", "test"),
    "data_source_lifecycle": ("data", "source"),
    "output_validation_before_external_use": ("output", "validation"),
    "dependency_output_delta": ("dependency", "review"),
    "component_library": ("component", "design"),
    "design_authority": ("design", "policy"),
    "options_before_build": ("option", "design", "decision"),
    "prerequisite_state_ui": ("design", "state", "screen"),
}


def rank_for_gate(
    candidates: tuple[str, ...] | list[str], gate_id: str, limit: int = SHOWN
) -> list[str]:
    """The same candidates, most plausible for THIS gate first.

    A precondition list is only useful if the right answer is near the top; forty alphabetical
    paths is a haystack. Keyword matching is a hint, not a decision - nothing is removed, and the
    adopter still chooses.
    """
    words = GATE_KEYWORDS.get(gate_id, ())
    if not words:
        return list(candidates)[:limit]
    def score(path: str) -> tuple[int, int, str]:
        low = path.lower()
        matches = sum(1 for w in words if w in low)
        # More keywords first, then shallower paths: `activity/register.md` matches both
        # "activity" and "register" and sits above `activity/ACT-001.md`, which matches one.
        return (-matches, path.count("/"), path)

    hit = sorted((c for c in candidates if any(w in c.lower() for w in words)), key=score)
    rest = [c for c in candidates if c not in hit]
    # Cut AFTER ranking, never before: capping first threw away the register and the CHANGELOG
    # because they sorted below a dozen files in `docs/archive/`, and then ranking had nothing
    # left to promote.
    return (hit + rest)[:limit]


def candidate_artefacts(repo: Path) -> list[str]:
    """Files that could serve as a gate's precondition artefact."""
    out = []
    for path in _tracked_files(repo):
        if not path.endswith(_ARTEFACT_SUFFIXES):
            continue
        head = path.split("/")[0]
        if head in _ARTEFACT_DIRS or "/" not in path:
            out.append(path)
    return _capped(_adopter_first(out))


def candidate_register_dirs(repo: Path) -> list[str]:
    """Directories holding YAML records - what a pattern-C control names (`DR-26`).

    An empty register is a legitimate answer to those controls, so a directory qualifies by holding
    records OR by sitting where records live; the checker's own rule is that the directory exists
    and contains nothing invalid, never that it contains anything at all.
    """
    dirs: set[str] = set()
    for path in _tracked_files(repo):
        if not path.endswith((".yaml", ".yml")):
            continue
        parent = "/".join(path.split("/")[:-1])
        if parent and not parent.startswith(".github"):
            dirs.add(parent)
    return _capped(_adopter_first(sorted(dirs)))


def candidate_lock_files(repo: Path) -> list[str]:
    """Dependency lock files, for `dependency_lock`'s implementation reference."""
    tracked = _tracked_files(repo)
    names = {name.lower() for name in _LOCK_FILES}
    return _capped(_adopter_first([p for p in tracked if p.split("/")[-1].lower() in names]))


def candidate_paths(repo: Path) -> list[str]:
    """Git pathspecs a gate could cover, as `src/**`-style globs.

    Offers the top-level directories that actually contain tracked code, plus `**` for a gate that
    covers the whole repository - which is a real answer, not a cop-out, for a small one.
    """
    tops: set[str] = set()
    for path in _tracked_files(repo):
        if "/" not in path:
            continue
        head = path.split("/")[0]
        if head.startswith("."):
            continue
        tops.add(head)
    # Recognised source directories first, then everything else, then the whole repository - which
    # is a real answer for a small one, but rarely the one someone means, so it goes last.
    known = [f"{d}/**" for d in sorted(tops) if d in _SOURCE_DIRS]
    others = [f"{d}/**" for d in sorted(tops) if d not in _SOURCE_DIRS]
    return _capped(known + others + ["**"])


def candidate_ci_steps(repo: Path) -> list[str]:
    """Every named step in every workflow, for a pattern-B control's `implementation_reference`.

    `check_conformance.find_workflow_step` looks a step up BY name and cannot enumerate, so this
    walks the same `jobs -> steps -> name` nesting it does. That duplication is deliberate and
    narrow: the checker's function answers "does this named step exist and can it fail", which is a
    different question from "what could the adopter pick", and merging them would make the checker
    depend on the wizard.
    """
    from surfaceplate.check_conformance import load_yaml

    names: list[str] = []
    for directory in _CI_DIRS:
        d = repo / directory
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.y*ml")):
            document, _ = load_yaml(path)
            if not isinstance(document, dict):
                continue
            jobs = document.get("jobs")
            if not isinstance(jobs, dict):
                continue
            for job in jobs.values():
                if not isinstance(job, dict):
                    continue
                for step in job.get("steps") or []:
                    if isinstance(step, dict) and isinstance(step.get("name"), str):
                        names.append(step["name"])
    return _capped(sorted(dict.fromkeys(names)))


@dataclass(frozen=True)
class Discovered:
    """One scan of the repository, passed to `plan.py` so every section can offer real answers."""

    artefacts: tuple[str, ...] = ()
    register_dirs: tuple[str, ...] = ()
    lock_files: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()
    ci_steps: tuple[str, ...] = ()

    def is_empty(self) -> bool:
        """True when nothing could be read - an unusual repository, or no git. Callers fall back to
        plain text fields, which is exactly how the wizard behaved before this module existed."""
        return not (
            self.artefacts or self.register_dirs or self.lock_files or self.paths or self.ci_steps
        )


def scan(repo: Path) -> Discovered:
    """Read the repository once. Cheap enough to do at startup; nothing here writes."""
    return Discovered(
        artefacts=tuple(candidate_artefacts(repo)),
        register_dirs=tuple(candidate_register_dirs(repo)),
        lock_files=tuple(candidate_lock_files(repo)),
        paths=tuple(candidate_paths(repo)),
        ci_steps=tuple(candidate_ci_steps(repo)),
    )
