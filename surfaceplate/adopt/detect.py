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
