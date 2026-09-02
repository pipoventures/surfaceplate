"""What can be seen without asking - and only that.

Detection exists to save typing, never to answer for the human. Every value this module returns is
shown back to them in section 2 as something to *confirm or correct*, never written silently. In
particular `builds_user_interface` is never set from here: `core/CONFORMANCE_LEVELS.md` states
plainly that it "is NOT descriptive... a reviewer can falsify a wrong answer in seconds," and a
detector that got it wrong would be exactly that wrong answer, arrived at automatically instead of
by a human's mistake.
"""

from __future__ import annotations

from pathlib import Path

# (label, marker files) - a files-exist check, not a dependency graph walk. Enough to save someone
# typing "Python" when a pyproject.toml is sitting right there; not a claim to be exhaustive.
_LANGUAGE_MARKERS: list[tuple[str, tuple[str, ...]]] = [
    ("Python", ("pyproject.toml", "setup.py", "requirements.txt")),
    ("Node.js / TypeScript", ("package.json",)),
    ("Rust", ("Cargo.toml",)),
    ("Go", ("go.mod",)),
    ("Java", ("pom.xml", "build.gradle", "build.gradle.kts")),
    ("Ruby", ("Gemfile",)),
]

# UI-framework dependency names worth a glance inside package.json, if one exists. Presence only -
# not a claim about how the framework is used.
_UI_DEPENDENCY_HINTS = ("react", "vue", "svelte", "@angular/core", "next", "nuxt", "solid-js")


def detect_languages(repo: Path) -> list[str]:
    found = [label for label, markers in _LANGUAGE_MARKERS if any((repo / m).is_file() for m in markers)]
    return found


def detect_ui_hint(repo: Path) -> str | None:
    """A package.json dependency that suggests a UI framework, or None. A hint, not a verdict."""
    package_json = repo / "package.json"
    if not package_json.is_file():
        return None
    try:
        import json

        data = json.loads(package_json.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
    for hint in _UI_DEPENDENCY_HINTS:
        if hint in deps:
            return hint
    return None


# Marker paths for the level-choice screen's detected signals (DR-35). Files-exist checks, in the
# same spirit as _LANGUAGE_MARKERS above: enough to show the honest starting cost of a level before
# it's chosen, never a claim to detect every possible shape a repository might already have. Shown,
# never acted on - the level choice itself stays a human decision either way (DR-35: "they are
# tool/repo dependent", the maintainer's own words for why this framework does not steer it).
_CI_WORKFLOW_DIRS = (".github/workflows", ".gitlab-ci.d")
_DECISIONS_FOLDER_MARKERS = ("docs/decisions", "docs/adr", "decisions", "adr")
_CHANGELOG_MARKERS = ("CHANGELOG.md", "CHANGELOG.rst", "CHANGELOG")


def detect_ci_workflows(repo: Path) -> list[str]:
    """Existing CI workflow files, repository-relative - a candidate home for a control's CI-step
    `implementation_reference` (`deterministic_tests`, `contract_tests`) or a gate's `enforcement:
    [ci]`. Returns paths, not a verdict: this module never tells whether a step in one of them
    actually fails the build, which only `check_conformance.py`'s own pattern-B check can."""
    from surfaceplate.adopt import discover

    installed, _steps = discover.framework_paths(repo)
    found: list[str] = []
    for directory in _CI_WORKFLOW_DIRS:
        d = repo / directory
        if not d.is_dir():
            continue
        found.extend(
            p.relative_to(repo).as_posix()
            for p in sorted(d.glob("*.y*ml"))
            # `F61`: the workflow this framework installed is not one the adopter "appears to have".
            if p.is_file() and p.relative_to(repo).as_posix() not in installed
        )
    return found


def detect_decisions_folder(repo: Path) -> str | None:
    """A decisions/ADR-shaped folder that already exists, or None. A candidate precondition
    artefact for `decision_before_implementation` - never asserted to already satisfy that gate,
    since satisfying it also depends on real content and, for the gate itself, on git history."""
    for marker in _DECISIONS_FOLDER_MARKERS:
        d = repo / marker
        if d.is_dir():
            return marker
    return None


def detect_changelog(repo: Path) -> str | None:
    """An existing CHANGELOG file, or None - a candidate precondition artefact for
    `change_record_before_completion`."""
    for marker in _CHANGELOG_MARKERS:
        f = repo / marker
        if f.is_file():
            return marker
    return None


def detect_git_state(repo: Path) -> tuple[str | None, bool]:
    """(current branch, working tree is clean) - best-effort, never raises."""
    import subprocess

    def run(*args: str) -> tuple[int, str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=5
            )
            return result.returncode, result.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            return 1, ""

    code, branch = run("branch", "--show-current")
    code2, status = run("status", "--porcelain")
    return (branch if code == 0 and branch else None, code2 == 0 and status == "")
