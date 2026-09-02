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

import json
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
# nobody can scan is a list nobody uses. **The cap is applied per field, after ranking, and never
# to the scan** (`F75`): `scan` used to keep 200 and a repository with 300 files under `docs/` lost
# its real `activity/register.md` before any gate had ranked it. `plan._from_candidates` and
# `rank_for_gate` cut to `SHOWN` once the field at hand has put its best candidate first.
SHOWN = 12              # what an adopter is actually offered, once ranked for the field at hand


def _tracked_files(repo: Path) -> list[str]:
    """Every path git considers part of this repository, or `[]` if git cannot answer.

    Deliberately not a filesystem walk. A walk offers `.venv/`, `node_modules/` and build output as
    candidate governance artefacts, which is worse than offering nothing.

    `-z`, so paths come back verbatim: without it git C-quotes a non-ASCII path
    (`"docs/caf\\303\\251.md"`), and the quoted string was offered while the real file was dropped
    (the review's code item 8).
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-z", "--cached", "--exclude-standard"],
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    return [
        chunk.decode("utf-8", errors="surrogateescape")
        for chunk in result.stdout.split(b"\0")
        if chunk
    ]


def _dedupe(values: list[str]) -> list[str]:
    """De-duplicated, order preserved - each caller ranks its own candidates, and sorting here
    would bury the most likely answer somewhere alphabetical. No cap: see `SHOWN`."""
    return list(dict.fromkeys(values))


# The one directory only this framework writes. Everything else it installs is read from the
# install record at scan time, so the exclusion cannot go stale when the payload changes - except
# the two files the installer CREATES when absent and then manages a block in, which the record
# does not list because they are the adopter's to keep. On a repository holding nothing else they
# are framework output all the same, and offering them proposed `**` as a discovered pathspec.
_FRAMEWORK_DIR = ".standards/"
_BLOCK_HOSTS = (".github/copilot-instructions.md", "AGENTS.md")


def framework_paths(repo: Path) -> tuple[set[str], set[str]]:
    """`(files, ci_steps)` this framework put into the repository, read from the install record.

    `F61`: discovery proposed `.github/instructions/authority.instructions.md` as the adopter's
    authority map, the installed workflow's own "Check conformance to Surfaceplate" as their
    contract test, and told a bare repository it appeared to have a CI workflow sixty seconds after
    the installer wrote one. A gate whose precondition is a file the framework installed is
    satisfied the moment the framework is installed, and the checker passes it. So every path in
    the install record's file list, the profile the wizard is about to write, and every step of the
    installed workflow are excluded from every candidate list - not ranked last, excluded.
    """
    record_path = repo / ".standards" / "INSTALL.json"
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set(), set()
    files = set((record.get("files") or {}).keys()) if isinstance(record.get("files"), dict) else set()
    profile = record.get("profile_path")
    if isinstance(profile, str):
        files.add(profile)
    steps: set[str] = set()
    for rel in files:
        if rel.startswith(".github/workflows/") and rel.endswith((".yml", ".yaml")):
            steps |= set(_steps_in(repo / rel))
    return files, steps


def _steps_in(path: Path) -> list[str]:
    from surfaceplate.check_conformance import load_yaml

    if not path.is_file():
        return []
    document, _ = load_yaml(path)
    if not isinstance(document, dict) or not isinstance(document.get("jobs"), dict):
        return []
    names: list[str] = []
    for job in document["jobs"].values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict) and isinstance(step.get("name"), str):
                names.append(step["name"])
    return names


def _adopters_own(repo: Path) -> list[str]:
    """The tracked files that are the adopter's, not this framework's."""
    excluded, _ = framework_paths(repo)
    if excluded:
        excluded |= set(_BLOCK_HOSTS)
    return [
        p for p in _tracked_files(repo)
        if p not in excluded and not p.startswith(_FRAMEWORK_DIR)
    ]


# Where a governance artefact is most likely to be, most likely first. Ranking matters more than
# it looks: people pick the first plausible line they see, so an alphabetical list that opens with
# `.github/` because a dot sorts before a letter is actively misleading.
_ARTEFACT_RANK = ("docs/", "governance/", "activity/", "decisions/", "adr/")


def _adopter_first(paths: list[str]) -> list[str]:
    """Ranked by how likely the adopter means it: their own governance directories first, then
    their root-level documents, then anything else. What this framework installed is not ranked
    last any more - it is not offered at all (`framework_paths`).

    Matches a bare directory name as well as a prefix, because the register-directory candidates are
    directories (`governance`) where the artefact candidates are files (`governance/x.yaml`).
    """

    def rank(path: str) -> tuple[int, str]:
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
    # `F84`: "inventory" matched a work inventory and proposed it as the authority map. The seed's
    # own path still matches on `source_of_truth`.
    "authority_map": ("authority", "source_of_truth"),
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
    hit = matched_for_gate(candidates, gate_id, limit=None)
    if not GATE_KEYWORDS.get(gate_id, ()):
        return list(candidates)[:limit]
    rest = [c for c in candidates if c not in hit]
    # Cut AFTER ranking, never before. `F75`: this comment was true here while `scan` capped the
    # list to 200 one level up, so the register was thrown away before this line ever ran. The
    # scan now keeps everything and this is the only cut.
    return (hit + rest)[:limit]


def matched_for_gate(
    candidates: tuple[str, ...] | list[str], gate_id: str, limit: int | None = SHOWN
) -> list[str]:
    """Only the candidates that actually matched a keyword for THIS gate, best first.

    `rank_for_gate` orders; this one **discriminates**, and the difference is `F40`. Ranking returns
    every candidate so the dropdown can offer everything - that is `DR-38`'s rule, and the adopter
    still chooses. But `defaults.py` took the top-ranked candidate as a *proposal*, and in a
    repository holding one unrelated file the top of the ranking is simply that file. The wizard
    proposed `README.md` as the precondition for `work_registration`, producing a gate that satisfies
    `SP032` - exists, non-empty, no placeholder - while guarding nothing at all.

    So a proposal now comes only from this list, and an empty list means no proposal and a question
    asked. That is `DR-40`'s own standard applied to a case it missed: *a field with no honest source
    is left unanswered and still asked.* An unmatched file is not an honest source; it is the only
    file.
    """
    words = GATE_KEYWORDS.get(gate_id, ())
    if not words:
        return []

    def score(path: str) -> tuple[int, int, str]:
        low = path.lower()
        matches = sum(1 for w in words if w in low)
        # More keywords first, then shallower paths: `activity/register.md` matches both
        # "activity" and "register" and sits above `activity/ACT-001.md`, which matches one.
        return (-matches, path.count("/"), path)

    hit = sorted((c for c in candidates if any(w in c.lower() for w in words)), key=score)
    return hit if limit is None else hit[:limit]


def candidate_artefacts(repo: Path) -> list[str]:
    """Files that could serve as a gate's precondition artefact - the adopter's own, all of them,
    ranked; the field at hand cuts the list after ranking it for its gate."""
    out = []
    for path in _adopters_own(repo):
        if not path.endswith(_ARTEFACT_SUFFIXES):
            continue
        head = path.split("/")[0]
        if head in _ARTEFACT_DIRS or "/" not in path:
            out.append(path)
    return _dedupe(_adopter_first(out))


def candidate_register_dirs(repo: Path) -> list[str]:
    """Directories holding YAML records - what a pattern-C control names (`DR-26`).

    An empty register is a legitimate answer to those controls, so a directory qualifies by holding
    records OR by sitting where records live; the checker's own rule is that the directory exists
    and contains nothing invalid, never that it contains anything at all.
    """
    dirs: set[str] = set()
    for path in _adopters_own(repo):
        if not path.endswith((".yaml", ".yml")):
            continue
        parent = "/".join(path.split("/")[:-1])
        if parent and not parent.startswith(".github"):
            dirs.add(parent)
    return _dedupe(_adopter_first(sorted(dirs)))


def candidate_lock_files(repo: Path) -> list[str]:
    """Dependency lock files, for `dependency_lock`'s implementation reference."""
    tracked = _adopters_own(repo)
    names = {name.lower() for name in _LOCK_FILES}
    return _dedupe(_adopter_first([p for p in tracked if p.split("/")[-1].lower() in names]))


def candidate_paths(repo: Path) -> list[str]:
    """Git pathspecs a gate could cover, as `src/**`-style globs.

    Offers the top-level directories that actually contain tracked code, plus `**` for a gate that
    covers the whole repository - which is a real answer, not a cop-out, for a small one.
    """
    own = _adopters_own(repo)
    if not own:
        # Nothing git could read, or nothing but this framework's own files: no pathspec is an
        # honest offer, and `Discovered.is_empty()` can then be true (the review's code item 9).
        return []
    tops: set[str] = set()
    for path in own:
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
    return _dedupe(known + others + ["**"])


def candidate_ci_steps(repo: Path) -> list[str]:
    """Every named step in every workflow, for a pattern-B control's `implementation_reference`.

    `check_conformance.find_workflow_step` looks a step up BY name and cannot enumerate, so this
    walks the same `jobs -> steps -> name` nesting it does. That duplication is deliberate and
    narrow: the checker's function answers "does this named step exist and can it fail", which is a
    different question from "what could the adopter pick", and merging them would make the checker
    depend on the wizard.
    """
    installed_files, installed_steps = framework_paths(repo)
    names: list[str] = []
    for directory in _CI_DIRS:
        d = repo / directory
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.y*ml")):
            if path.relative_to(repo).as_posix() in installed_files:
                continue  # the framework's own workflow is not the adopter's CI (`F61`)
            names.extend(step for step in _steps_in(path) if step not in installed_steps)
    return _dedupe(sorted(dict.fromkeys(names)))


# ---------------------------------------------------------------------------------------------
# The checker's own rules, applied before proposing (`DR-51` (5)), and what a choice is
# ---------------------------------------------------------------------------------------------


def content_problem(target: Path) -> str:
    """Why the checker would reject this file as an artefact, in a few words, or `""`. The same
    two rules `SP032` and `SP051` apply after the path checks: non-empty, no placeholder token.
    A directory has no content rule (a register may be empty)."""
    from surfaceplate import rules

    if not target.is_file():
        return ""
    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "cannot be read"
    if not text.strip():
        return "is empty"
    if rules.PLACEHOLDER_PATTERN.search(text):
        return "still contains a template placeholder (TBD, TODO or replace-me)"
    return ""


def scanner_step(target: Path, scanner: str) -> tuple[str, str]:
    """`("runs", step name)` where a workflow step runs the scanner; `("mentions", "")` for a
    non-workflow file that mentions it (the checker inspects those no further); `("comment", "")`
    for a workflow that mentions it outside any step; `("absent", "")` otherwise. `SP046`'s rule."""
    from surfaceplate.check_conformance import load_yaml, step_mentions

    try:
        text = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "absent", ""
    if scanner.lower() not in text.lower():
        return "absent", ""
    document, _ = load_yaml(target)
    if not isinstance(document, dict) or not isinstance(document.get("jobs"), dict):
        return "mentions", ""
    for job in document["jobs"].values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict) and step_mentions(step, scanner):
                return "runs", str(step.get("name") or step.get("uses") or step.get("id") or "the scan step")
    return "comment", ""


def scanner_workflows(repo: Path, scanner: str) -> list[str]:
    """The adopter's workflows where a step runs the named scanner - what `scanner.wired_in`
    offers and proposes. `F83`: the first workflow found was proposed, and the checker then
    reported it never mentions the scanner."""
    installed_files, _ = framework_paths(repo)
    own = set(_adopters_own(repo))
    out: list[str] = []
    for directory in _CI_DIRS:
        d = repo / directory
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.y*ml")):
            rel = path.relative_to(repo).as_posix()
            if rel in installed_files or rel not in own:
                continue
            if scanner_step(path, scanner)[0] == "runs":
                out.append(rel)
    return _dedupe(out)


def _title_of(target: Path) -> str:
    """The first heading of a Markdown file, the first comment or key of a YAML file: what a
    reader would take the file to be about, in its own words."""
    try:
        lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()[:60]
        return stripped[:60]
    return ""


def describe(
    repo: Path,
    path: str,
    *,
    gate_id: str = "",
    scanner: str = "",
    found: "Discovered | None" = None,
) -> str:
    """One line about a chosen path, for the help beside the field (`F80`, `DR-51` (4)): what
    discovery saw in it, whether it matched the gate's words, and whether the checker's rules
    would reject it. States what was read; decides nothing."""
    target = repo / path
    if not target.exists():
        return f"{path}: nothing exists at that path in this repository."
    if target.is_dir():
        records = len([p for p in target.glob("*.y*ml")])
        return f"{path}: a directory holding {records} YAML record(s); an empty register is a valid start."
    parts: list[str] = []
    title = _title_of(target)
    parts.append(f'"{title}"' if title else "no heading or first line")
    try:
        count = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
        parts[-1] += f", {count} line(s)"
    except OSError:
        pass
    if gate_id:
        words = [w for w in GATE_KEYWORDS.get(gate_id, ()) if w in path.lower()]
        parts.append(
            f"matched this gate's words: {', '.join(words)}" if words
            else f"did not match this gate's words ({', '.join(GATE_KEYWORDS.get(gate_id, ())) or 'none'}); it is simply a file found here"
        )
    if scanner:
        state, step = scanner_step(target, scanner)
        parts.append(
            {"runs": f"step '{step}' runs {scanner}",
             "mentions": f"mentions {scanner}; not a workflow, so the checker inspects it no further",
             "comment": f"mentions {scanner} but no step runs it; the checker would reject it (SP046)",
             "absent": f"never mentions {scanner}; the checker would reject it (SP046)"}[state]
        )
    problem = (found.rejected.get(path) if found is not None else None) or content_problem(target)
    if problem:
        parts.append(f"the checker would reject it: it {problem} (SP032)")
    return f"{path}: " + "; ".join(parts) + "."


@dataclass(frozen=True)
class Discovered:
    """One scan of the repository, passed to `plan.py` so every section can offer real answers."""

    artefacts: tuple[str, ...] = ()
    register_dirs: tuple[str, ...] = ()
    lock_files: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()
    ci_steps: tuple[str, ...] = ()
    # `DR-51` (5): workflows where a step runs the scanner the examples name, and artefacts the
    # checker's content rules would reject, with the reason. Rejected files stay in `artefacts`
    # (the adopter chooses from everything found) and are never proposed.
    scanner_workflows: tuple[str, ...] = ()
    rejected: dict[str, str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.rejected is None:
            object.__setattr__(self, "rejected", {})

    def is_empty(self) -> bool:
        """True when nothing of the adopter's could be read - a tree git cannot answer for, or one
        holding nothing but this framework's own files. Every `_from_candidates` field then
        degrades to the plain text box it always was; `plan.py` is the caller."""
        return not (
            self.artefacts or self.register_dirs or self.lock_files or self.paths or self.ci_steps
        )


# The scanner the examples name; `scan` looks for its workflow, and the field's validator
# re-checks against whatever name the profile ends up carrying.
DEFAULT_SCANNER = "gitleaks"


def scan(repo: Path, scanner: str = DEFAULT_SCANNER) -> Discovered:
    """Read the repository once. Cheap enough to do at startup; nothing here writes."""
    artefacts = tuple(candidate_artefacts(repo))
    rejected = {}
    for rel in artefacts:
        problem = content_problem(repo / rel)
        if problem:
            rejected[rel] = problem
    return Discovered(
        artefacts=artefacts,
        register_dirs=tuple(candidate_register_dirs(repo)),
        lock_files=tuple(candidate_lock_files(repo)),
        paths=tuple(candidate_paths(repo)),
        ci_steps=tuple(candidate_ci_steps(repo)),
        scanner_workflows=tuple(scanner_workflows(repo, scanner)),
        rejected=rejected,
    )
