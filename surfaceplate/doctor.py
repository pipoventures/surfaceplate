"""`surfaceplate doctor`: the facts that stopped a stranger's first command, one line each.

`DR-49` (4). The review's stranger install failed at its first command on a machine with a global
`core.hooksPath` the README never mentioned; the wizard had no path without a terminal; a system
Python without pip made the documented install line fail. None of that is a defect in the adopting
repository, and all of it is checkable in a second. So: Python and pip, the two packages the
checker needs and the one the wizard needs, `core.hooksPath` at every scope, whether a terminal is
attached, whether the interpreter's virtualenv is on `PATH`, and the vendored copy's digest against
the install record.

Offline by default. Whether GitHub Actions is enabled for a repository is a fact only the GitHub
API can answer and it needs a token, so it sits behind `--online` and `GITHUB_TOKEN`: the token is
read from the environment, sent only to `api.github.com` over HTTPS in an `Authorization` header,
and never printed. That request is the one trust boundary in this module.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

OK, WARN, FAIL, SKIP = "ok", "warn", "FAIL", "skip"


class Line:
    def __init__(self, status: str, name: str, detail: str) -> None:
        self.status = status
        self.name = name
        self.detail = detail

    def render(self) -> str:
        return f"{self.status:<5} {self.name:<22} {self.detail}"


def _git_config(repo: Path, scope: str) -> str | None:
    """`core.hooksPath` at one scope, or `None` when unset or git cannot answer."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "config", f"--{scope}", "--get-all", "core.hooksPath"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value or None


def check_python() -> list[Line]:
    version = ".".join(str(n) for n in sys.version_info[:3])
    lines = [
        Line(OK if sys.version_info >= (3, 9) else FAIL, "python", f"{version} at {sys.executable}"),
    ]
    if importlib.util.find_spec("pip") is None:
        lines.append(
            Line(WARN, "pip", "not importable: `python -m pip` fails here; use a virtual environment "
                             "or the distribution's python3-yaml and python3-jsonschema packages")
        )
    else:
        lines.append(Line(OK, "pip", "importable"))
    for module, needed_by, status in (("yaml", "install and check", FAIL), ("jsonschema", "install and check", FAIL), ("textual", "adopt (the adopt extra)", WARN)):
        present = importlib.util.find_spec(module) is not None
        lines.append(Line(OK if present else status, module, f"{'importable' if present else 'missing'} - needed by {needed_by}"))
    return lines


def check_hooks_path(repo: Path) -> list[Line]:
    lines: list[Line] = []
    local = _git_config(repo, "local")
    for scope in ("local", "worktree", "global", "system"):
        value = _git_config(repo, scope)
        if value is None:
            lines.append(Line(OK, f"core.hooksPath ({scope})", "unset"))
        elif scope == "worktree" and value == local:
            # Without `extensions.worktreeConfig`, git answers the worktree scope with the
            # local value; that is not a second setting.
            lines.append(Line(OK, f"core.hooksPath ({scope})", "unset (git reports the local value here)"))
        elif scope == "local" and value.rstrip("/") == ".githooks":
            lines.append(Line(OK, f"core.hooksPath ({scope})", f"{value} - this standard's hook"))
        else:
            lines.append(
                Line(WARN, f"core.hooksPath ({scope})",
                     f"{value} - the installer stops rather than replace it; install with "
                     "--no-hooks, or unset it for this repository")
            )
    return lines


def check_terminal() -> Line:
    attached = sys.stdin.isatty() and sys.stdout.isatty()
    if attached:
        return Line(OK, "terminal", "attached; `adopt` can run here")
    return Line(WARN, "terminal", "not attached; `adopt` needs one, `adopt --propose` does not")


def check_venv_on_path() -> Line:
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if not in_venv:
        return Line(OK, "virtualenv on PATH", "not running in a virtual environment")
    bindir = str(Path(sys.executable).resolve().parent)
    entries = [str(Path(p).resolve()) for p in os.environ.get("PATH", "").split(os.pathsep) if p]
    if bindir in entries:
        return Line(OK, "virtualenv on PATH", f"{bindir} is on PATH; the hook will find this interpreter")
    return Line(WARN, "virtualenv on PATH", f"{bindir} is not on PATH; the hook resolves python3 from PATH and will not find this interpreter")


def check_vendored_digest(repo: Path) -> Line:
    record_path = repo / ".standards" / "INSTALL.json"
    manifest = repo / ".standards" / "MANIFEST.sha256"
    if not record_path.is_file():
        return Line(SKIP, "vendored digest", f"{repo} has no .standards/INSTALL.json; not installed here")
    try:
        import json

        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return Line(FAIL, "vendored digest", f"the install record is unreadable: {exc}")
    if not manifest.is_file():
        return Line(FAIL, "vendored digest", "the vendored manifest is missing; re-run the installer")
    actual = hashlib.sha256(manifest.read_bytes()).hexdigest()
    expected = str(record.get("framework_digest", ""))
    if actual == expected:
        return Line(OK, "vendored digest", f"{actual[:12]}… matches the install record")
    return Line(FAIL, "vendored digest", f"the vendored manifest hashes to {actual[:12]}… but the record says {expected[:12]}…; re-run the installer")


def check_actions_enabled(repo: Path, online: bool) -> Line:
    if not online:
        return Line(SKIP, "GitHub Actions enabled", "skipped (offline); run with --online and GITHUB_TOKEN set")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return Line(SKIP, "GitHub Actions enabled", "skipped: --online needs GITHUB_TOKEN in the environment (a token is never printed)")
    try:
        origin = subprocess.run(
            ["git", "-C", str(repo), "remote", "get-url", "origin"], capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        origin = ""
    slug = _github_slug(origin)
    if not slug:
        return Line(WARN, "GitHub Actions enabled", f"origin is not a github.com remote: {origin or 'none'}")
    import json
    import urllib.error
    import urllib.request

    request = urllib.request.Request(
        f"https://api.github.com/repos/{slug}/actions/permissions",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "surfaceplate-doctor"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310 - fixed https host
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return Line(WARN, "GitHub Actions enabled", f"api.github.com answered {exc.code} for {slug}")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return Line(WARN, "GitHub Actions enabled", f"could not reach api.github.com: {exc}")
    enabled = data.get("enabled")
    return Line(OK if enabled else FAIL, "GitHub Actions enabled", f"{enabled} for {slug} (allowed_actions: {data.get('allowed_actions')})")


def _github_slug(origin: str) -> str:
    for prefix in ("git@github.com:", "https://github.com/", "ssh://git@github.com/"):
        if origin.startswith(prefix):
            slug = origin[len(prefix):]
            return slug[:-4] if slug.endswith(".git") else slug
    return ""


def diagnose(repo: Path, *, online: bool) -> list[Line]:
    lines = check_python()
    lines += check_hooks_path(repo)
    lines.append(check_terminal())
    lines.append(check_venv_on_path())
    lines.append(check_vendored_digest(repo))
    lines.append(check_actions_enabled(repo, online))
    return lines


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        sys.stderr.write(f"error: {message}\n")
        sys.exit(3)


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(prog="surfaceplate doctor", description="Check this machine and repository for what stops the first command.")
    parser.add_argument("--repo", default=".", help="Repository to look at (default: current directory).")
    parser.add_argument("--online", action="store_true", help="Also ask api.github.com whether Actions is enabled; needs GITHUB_TOKEN.")
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()
    lines = diagnose(repo, online=args.online)
    print("Surfaceplate - doctor")
    print(f"repository: {repo}")
    print()
    for line in lines:
        print(line.render())
    print()
    failed = [line for line in lines if line.status == FAIL]
    warned = [line for line in lines if line.status == WARN]
    if failed:
        print(f"DOCTOR=FAIL  ({len(failed)} failing, {len(warned)} warning, {len(lines)} checks)")
        return 1
    print(f"DOCTOR=OK  ({len(warned)} warning, {len(lines)} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
