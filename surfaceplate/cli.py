"""`surfaceplate` — the console-script `DR-12` committed to.

Four subcommands. `install` and `check` are thin wrappers over `install_standard.py` and
`check_conformance.py`; `adopt` is the wizard, interactive or - since `DR-49` - as `--propose` and
`--answers`, which need no terminal; `doctor` reports the facts that stop a first command.

**Exit codes are a public contract** (`DR-49` (2)), read by the installed hook and workflow and by
any wrapper: `0` pass, or graced findings with a printed summary; `1` findings that fail, or a run
that stopped for a reason the human must act on; `2` not installed; `3` usage error or no terminal;
`4` internal error. `adopt` returns the checker's code after a successful write, so a first adoption
of an existing repository, which produces graced findings by design, does not fail.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

VERSION_FILE = Path(__file__).with_name("VERSION")


def version() -> str:
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"


class _Parser(argparse.ArgumentParser):
    """A usage error exits 3, not argparse's 2, which `DR-49` gives to "not installed"."""

    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        sys.stderr.write(f"error: {message}\n")
        sys.exit(3)


def _cmd_install(argv: list[str]) -> int:
    from surfaceplate import install_standard

    return install_standard.main(argv)


def _cmd_check(argv: list[str]) -> int:
    from surfaceplate import check_conformance

    return check_conformance.main(argv)


def _cmd_doctor(argv: list[str]) -> int:
    from surfaceplate import doctor

    return doctor.main(argv)


def _cmd_adopt(argv: list[str]) -> int:
    from surfaceplate.adopt import wizard
    from surfaceplate.adopt.interview import Cancelled

    parser = _Parser(prog="surfaceplate adopt", description="Fill in the application profile.")
    parser.add_argument("--target", default=".", help="Repository to adopt into (default: current directory).")
    parser.add_argument(
        "--propose",
        action="store_true",
        help="Run discovery and write the proposed profile and the answers record; never the profile. Needs no terminal.",
    )
    parser.add_argument(
        "--level",
        choices=("essential", "standard", "full"),
        help="With --propose: the level to build the proposal at. Without it, the record stops at the level.",
    )
    parser.add_argument(
        "--answers",
        metavar="FILE",
        help="Replay a human-completed answers record through the same code as the interface, and write the profile.",
    )
    args = parser.parse_args(argv)
    repo = Path(args.target).resolve()

    try:
        if args.propose:
            written = wizard.propose(repo, level=args.level)
            print(f"Proposed: {written.answers}")
            if written.proposed is not None:
                print(f"Preview : {written.proposed}")
            print("Nothing else was written. Complete every needs-human line in the answers record, then run:")
            print(f"    surfaceplate adopt --target {repo} --answers {written.answers}")
            return 0
        if args.answers:
            written = wizard.replay(repo, Path(args.answers))
            return _report_written(repo, written)

        try:
            import textual  # noqa: F401  (checked here so the failure is clear, not a bare traceback)
        except ImportError:
            print(
                "`adopt` needs the optional `textual` dependency, which is not installed.\n"
                "Run:  pip install 'surfaceplate[adopt] @ git+https://github.com/pipoventures/surfaceplate@main'\n"
                "Or, if you have a clone:  pip install 'textual==8.2.8'\n"
                "Without it, `surfaceplate adopt --propose` still works and needs no terminal.",
                file=sys.stderr,
            )
            return 2

        # `adopt` is a full-screen interface and needs a real terminal. Refusing with a route the
        # reader can take is the `F35`/`ACT-025` lesson; since `DR-49` the route needs no terminal.
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            print(
                "`adopt` is an interactive, full-screen wizard and needs a real terminal; this one is "
                "not attached to a TTY (output is piped, redirected, or running in CI).\n"
                "\n"
                f"  Run it directly in a terminal:  surfaceplate adopt --target {repo}\n"
                f"  Or without one:                 surfaceplate adopt --propose --target {repo}\n"
                "\n"
                "Nothing was read or written, and any saved draft in that repository is untouched.",
                file=sys.stderr,
            )
            return 3

        from surfaceplate.adopt.tui.app import TextualInterview

        written = wizard.run(repo, TextualInterview())
        return _report_written(repo, written)
    except Cancelled:
        print("\nCancelled. Nothing was written; your draft is kept so you can resume.")
        return 1
    except KeyboardInterrupt:
        # Code item 14: one line, the draft kept, and nothing else runs.
        print("\nInterrupted. Nothing was written; your draft is kept so you can resume.", file=sys.stderr)
        return 130
    except wizard.NotInstalled as exc:
        print(f"\n{exc}")
        return 2
    except (wizard.AlreadyAdopted, wizard.NeedsHuman) as exc:
        print(f"\n{exc}")
        return 1
    except wizard.WriteRefused as exc:
        print(f"\nRefusing to write: {exc.detail}")
        print("This is the wizard's own safety check, not the checker. Nothing was written.")
        return 1
    except Exception as exc:  # noqa: BLE001 - deliberate; an internal error is its own exit code
        print(f"\nThe wizard could not finish: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(
            "Nothing was written. Your answers are kept in the draft, so re-running `adopt` offers "
            "to resume from where this stopped.",
            file=sys.stderr,
        )
        return 4


def _report_written(repo: Path, written) -> int:
    """What was written, what was created, and what the checker makes of it - which is the
    question actually being asked. Returns the checker's exit code (`DR-49` (2))."""
    rule = "─" * 66
    print(f"\n{rule}")
    print(f"  Written: {written}")
    for path in getattr(written, "created", []):
        print(f"  Created: {path}")
    for problem in getattr(written, "problems", []):
        print(f"  NOT created: {problem}")
    if getattr(written, "created", []):
        print(
            "\n  Those are real, complete files, and creating them is not the work they are for.\n"
            "  A register that exists and stays empty while work happens around it is a finding\n"
            "  about this repository - the checker cannot tell the difference, because what it\n"
            "  checks is that the file is there."
        )
    print(rule)

    from surfaceplate import check_conformance

    print("  Checking what you just wrote:\n")
    code = check_conformance.main(["--repo", str(repo)])
    if code == 0:
        print("\n  The checker passes against what you just wrote.")
    else:
        print(
            "\n  The profile is written, but the checker does not pass against it yet.\n"
            "  That is normal for a first adoption - the output above says which artefacts it\n"
            "  could not find. Re-run at any time:\n"
            f"\n      surfaceplate check --repo {repo}\n"
        )
    print(f"  Re-running `adopt` will not overwrite it; edit {written.name} directly from here.\n")
    return code


_COMMANDS = {
    "install": (_cmd_install, "Install or upgrade the standard into a repository."),
    "check": (_cmd_check, "Check a repository against the standard (--format text|json|sarif)."),
    "adopt": (_cmd_adopt, "Fill in the application profile: interactively, or --propose then --answers."),
    "doctor": (_cmd_doctor, "Report what would stop the first command on this machine."),
}


def _parser() -> _Parser:
    parser = _Parser(
        prog="surfaceplate",
        description="The Pipo Ventures software delivery standard, installed rather than copied.",
    )
    parser.add_argument("--version", action="version", version=f"surfaceplate {version()}")
    subparsers = parser.add_subparsers(dest="command", metavar="{install,check,adopt,doctor}")
    for name, (_handler, help_text) in _COMMANDS.items():
        subparsers.add_parser(name, help=help_text, add_help=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    parser = _parser()
    # The top level owns `--help` and `--version` and names the commands; each command owns its
    # own flags, so everything after the command name is handed over untouched.
    if not argv:
        parser.print_usage(sys.stderr)
        print("error: a command is required: install, check, adopt or doctor", file=sys.stderr)
        return 3
    if argv[0] in _COMMANDS:
        handler, _ = _COMMANDS[argv[0]]
        return handler(argv[1:])
    parser.parse_args(argv[:1])  # -h, --help, --version, or a usage error (exit 3)
    parser.print_usage(sys.stderr)
    print(f"error: unknown command {argv[0]!r}; expected install, check, adopt or doctor", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
