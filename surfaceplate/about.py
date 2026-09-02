"""What this tool is: the identity the opening screen shows and the anchor `adopt` compares.

`DR-51` (2). Held in one module so the opening screen, the version-parity refusal and `doctor`
say the same thing, and `tests/test_adopt.py` holds it to `pyproject.toml` so it cannot drift.
"""

from __future__ import annotations

from pathlib import Path

NAME = "Surfaceplate"
PUBLISHER = "Pipo Ventures Ltd"
LICENCE = "Apache-2.0"
HOMEPAGE = "https://github.com/pipoventures/surfaceplate"
TAGLINE = (
    "a software delivery standard that installs into a repository and checks it against what it "
    "publishes"
)

PACKAGE_DIR = Path(__file__).resolve().parent


def version() -> str:
    try:
        return (PACKAGE_DIR / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


def anchor() -> str:
    """The framework anchor of this tool's own payload: what `install` records as
    `framework_digest`, computed the same way (`install_standard.framework_anchor`)."""
    try:
        from surfaceplate import install_standard
    except ImportError:  # imported flat, with the payload directory itself on the path (CI)
        import install_standard  # type: ignore[no-redef]

    return install_standard.framework_anchor(PACKAGE_DIR) or ""


def short(digest: str) -> str:
    return f"{digest[:12]}…" if digest else "(no anchor)"


def upgrade_command(repo: Path, *, no_hooks: bool) -> str:
    """The `install` invocation that brings a repository's installed copy up to this tool."""
    command = f"surfaceplate install --source {PACKAGE_DIR} --target {repo}"
    return command + (" --no-hooks" if no_hooks else "")
