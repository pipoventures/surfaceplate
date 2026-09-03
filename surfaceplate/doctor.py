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

`--report` assembles a problem report for a human to paste into an issue by hand: everything in
this module already reads local, non-identifying facts, so the report is the same facts, rendered
once more and redacted. **It never sends anything and is deliberately incompatible with
`--online`** - the whole point is that this path stays on the opposite side of the module's one
network call from it. See `_collect_report` for what is included, `_redact` for what never leaves
the repository verbatim, and `_never_collected` for what is not gathered in the first place.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import os
import platform
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


def check_tool_matches_install(repo: Path) -> Line:
    """`F78` / `DR-51` (1): the vendored-digest line above compares the install with its own
    record and passes on an install older than this tool. This compares the install with the
    tool, which is the state that stopped the maintainer's first run at the review."""
    try:
        from surfaceplate import about, install_standard
    except ImportError:  # imported flat, with the payload directory itself on the path (CI)
        import about  # type: ignore[no-redef]
        import install_standard  # type: ignore[no-redef]

    record_path = repo / ".standards" / "INSTALL.json"
    if not record_path.is_file():
        return Line(SKIP, "tool vs installed", f"{repo} has no .standards/INSTALL.json; not installed here")
    try:
        import json

        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return Line(FAIL, "tool vs installed", f"the install record is unreadable: {exc}")
    installed = str(record.get("framework_digest", ""))
    installed_version = str(record.get("standard_version", "") or "unknown")
    if installed == about.anchor():
        return Line(OK, "tool vs installed", f"both {about.version()} ({about.short(installed)}); adopt and check agree on the schema")
    hooks_declined = install_standard.HOOK_TARGET not in (record.get("files") or {})
    return Line(
        FAIL,
        "tool vs installed",
        f"installed {installed_version} ({about.short(installed)}) but this tool is {about.version()} "
        f"({about.short(about.anchor())}); adopt will refuse until the install is upgraded: "
        f"{about.upgrade_command(repo, no_hooks=hooks_declined)}",
    )


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
    lines.append(check_tool_matches_install(repo))
    lines.append(check_actions_enabled(repo, online))
    return lines


_OPTIONAL_MODULES = ("pip", "yaml", "jsonschema", "textual")
_DIST_NAMES = {"yaml": "PyYAML"}  # the importable name and the distribution name differ here


def _dependency_lines() -> list[str]:
    lines = []
    for module in _OPTIONAL_MODULES:
        if importlib.util.find_spec(module) is None:
            lines.append(f"  {module:<11} missing")
            continue
        try:
            version = importlib.metadata.version(_DIST_NAMES.get(module, module))
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"
        lines.append(f"  {module:<11} importable ({version})")
    return lines


def _installed_standard_lines(repo: Path) -> tuple[list[str], dict | None]:
    """The facts `.standards/INSTALL.json` already holds, none of them identifying. Returns the
    rendered lines and the parsed record (`None` when nothing is installed here)."""
    record_path = repo / ".standards" / "INSTALL.json"
    if not record_path.is_file():
        return ["  not installed in this repository"], None
    import json

    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"  the install record is unreadable: {exc}"], None
    try:
        from surfaceplate import install_standard
    except ImportError:  # imported flat, with the payload directory itself on the path (CI)
        import install_standard  # type: ignore[no-redef]

    hooks = "declined (--no-hooks)" if install_standard.HOOK_TARGET not in (record.get("files") or {}) else "installed"
    lines = [
        f"  standard_version    {record.get('standard_version', '(unknown)')}",
        f"  framework_digest    {record.get('framework_digest', '(unknown)')}",
        f"  first_installed_at  {record.get('first_installed_at', '(unknown)')}",
        f"  installed_at        {record.get('installed_at', '(unknown)')}",
        f"  grace_expires       {record.get('grace_expires', '(unknown)')}",
        f"  hooks               {hooks}",
    ]
    return lines, record


def _conformance_lines(repo: Path, installed: bool) -> list[str]:
    """The checker's own verdict, plus - verbatim, because these are standard-owned and identical
    in every adopting repository - which of its own files fail integrity (`SP004`/`SP005`). Every
    other finding is named by code and count only: its `detail` may quote the adopter's own
    artefacts, which this report does not disclose."""
    if not installed:
        return ["  skipped: not installed in this repository"]
    import datetime as _dt

    try:
        from surfaceplate import check_conformance
    except ImportError:  # imported flat, with the payload directory itself on the path (CI)
        import check_conformance  # type: ignore[no-redef]

    try:
        report = check_conformance.evaluate(repo, _dt.date.today(), False, False)
    except Exception as exc:  # noqa: BLE001 - a report must not crash on a broken repository
        return [f"  could not evaluate: {type(exc).__name__}: {exc}"]
    lines = [f"  verdict    {report.verdict}", f"  exit_code  {report.exit_code}"]
    by_code: dict[str, int] = {}
    for finding in report.findings:
        by_code[finding.code] = by_code.get(finding.code, 0) + 1
    if by_code:
        counts = ", ".join(f"{code}×{n}" for code, n in sorted(by_code.items()))
        lines.append(f"  findings   {counts}")
    else:
        lines.append("  findings   none")
    integrity_paths = [
        f.detail for f in report.findings if f.code in ("SP004", "SP005") and f.detail
    ]
    if integrity_paths:
        lines.append("  standard-owned files failing integrity (safe to share verbatim):")
        for detail in integrity_paths:
            for rel in detail.split("; "):
                lines.append(f"    {rel}")
    return lines


def _never_collected() -> list[str]:
    return [
        "  - git remotes or branch names",
        "  - governance/application-profile.yaml (it names an owner and contacts)",
        "  - this repository's directory name",
        "  - environment variables",
        "  - the full list of standard-owned files (`.standards/INSTALL.json`'s `files` map);",
        "    only the ones actually failing integrity, above, and only their paths",
    ]


def _redact(text: str, repo: Path) -> str:
    """One choke point, applied to the whole rendered report, so no collector above can bypass
    it and there is exactly one thing to test. Longest source first, so a shorter one (e.g. the
    home directory) cannot eat part of a longer one (e.g. a repo path nested inside it)."""
    substitutions = [
        (str(repo.resolve()), "<repo>"),
        (str(Path.home()), "<home>"),
        (sys.prefix, "<venv>"),
    ]
    for var in ("USER", "USERNAME", "LOGNAME"):
        value = os.environ.get(var, "")
        if value:
            substitutions.append((value, "<user>"))
    substitutions.sort(key=lambda pair: len(pair[0]), reverse=True)
    for source, placeholder in substitutions:
        if source:
            text = text.replace(source, placeholder)
    return text


def _collect_report(repo: Path) -> tuple[str, list[Line]]:
    try:
        from surfaceplate import about
    except ImportError:  # imported flat, with the payload directory itself on the path (CI)
        import about  # type: ignore[no-redef]

    lines = diagnose(repo, online=False)
    installed_lines, record = _installed_standard_lines(repo)

    sections = [
        "# surfaceplate problem report",
        "",
        "Nothing here was sent anywhere - this command makes no network requests. Read the whole",
        "report before pasting it; see \"What was redacted\" at the end for exactly what this",
        "leaves out and why.",
        "",
        "## Tool",
        f"  version  {about.version()}",
        f"  anchor   {about.anchor()}",
        "",
        "## Python",
        f"  {platform.python_implementation()} {'.'.join(str(n) for n in sys.version_info[:3])}",
        "",
        "## OS",
        f"  {platform.system()} {platform.release()} ({platform.machine()})",
        "",
        "## Optional dependencies",
        *_dependency_lines(),
        "",
        "## Installed standard (.standards/INSTALL.json)",
        *installed_lines,
        "",
        "## doctor",
        *[line.render() for line in lines],
        "",
        "## Conformance check",
        *_conformance_lines(repo, record is not None),
        "",
        "## What was redacted",
        "  <repo>  this repository's absolute path",
        "  <home>  your home directory",
        "  <venv>  the active Python environment's location",
        "  <user>  your OS username",
        "",
        "Never collected at all:",
        *_never_collected(),
        "",
        "---",
        "Read the report above. If you are happy for it to be public, paste it into:",
        f"  {about.ISSUES}",
    ]
    return _redact("\n".join(sections) + "\n", repo), lines


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        sys.stderr.write(f"error: {message}\n")
        sys.exit(3)


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(prog="surfaceplate doctor", description="Check this machine and repository for what stops the first command.")
    parser.add_argument("--repo", default=".", help="Repository to look at (default: current directory).")
    parser.add_argument("--online", action="store_true", help="Also ask api.github.com whether Actions is enabled; needs GITHUB_TOKEN.")
    parser.add_argument("--report", action="store_true", help="Assemble a paste-ready problem report and print it. Offline, always; nothing is sent.")
    parser.add_argument("--report-file", metavar="PATH", help="Also write the report to PATH (with --report). Never a default path; never overwrites silently.")
    args = parser.parse_args(argv)
    repo = Path(args.repo).resolve()

    if args.report:
        if args.online:
            parser.error("--online is not available with --report: a problem report is assembled offline and nothing is ever sent")
        text, lines = _collect_report(repo)
        if args.report_file:
            target = Path(args.report_file)
            if target.exists():
                parser.error(f"{target} already exists; choose a different path rather than overwrite it silently")
            target.write_text(text, encoding="utf-8")
        print(text, end="")
        return 1 if any(line.status == FAIL for line in lines) else 0
    if args.report_file and not args.report:
        parser.error("--report-file needs --report")

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
