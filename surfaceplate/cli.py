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


def _cmd_agent_prompt(argv: list[str]) -> int:
    from surfaceplate import assist

    return assist.main(argv)


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
    # `F165`: without this, `stack.builds_user_interface` could not be answered `yes` on the
    # non-interactive route at all - the record told the reader to write it into the file and
    # re-propose, and `--propose` rebuilds from the repository and discarded it. The four interface
    # gates then never appeared, and three of them have no scaffold, so a repository with an
    # interface had no way through `--propose`/`--answers`.
    parser.add_argument(
        "--builds-ui",
        choices=("yes", "no"),
        help="With --propose: whether this repository builds a user interface. It is a decision, "
             "not a description - yes makes all four interface gates required, no makes them "
             "not_applicable. Without it the proposal assumes no.",
    )
    parser.add_argument(
        "--answers",
        metavar="FILE",
        help="Replay a human-completed answers record through the same code as the interface, and write the profile.",
    )
    parser.add_argument(
        "--edit",
        nargs=2,
        metavar=("PATH", "VALUE"),
        help="Change one line of the written profile (e.g. owner, or prerequisites[2].owner) and record the edit beside it. Needs no terminal.",
    )
    parser.add_argument("--because", metavar="REASON", default="", help="With --edit: why, recorded with the edit.")
    parser.add_argument(
        "--repin",
        action="store_true",
        help=(
            "Re-pin adoption.framework_version and framework_digest to the installed standard, "
            "after an upgrade. The values come from .standards/INSTALL.json; running this is the "
            "deliberate act, and the typing is what it removes."
        ),
    )
    args = parser.parse_args(argv)
    repo = Path(args.target).resolve()

    try:
        if args.repin:
            written, lines = wizard.repin(repo)
            for line in lines:
                print(line)
            return 0
        if args.edit:
            path, value = args.edit
            # `F140` (`PW-07`): an edit to a governance profile without a stated reason is the
            # thing `SP031` refuses in a deferral - "an omission wearing a decision's clothes".
            # It used to be accepted and recorded with boilerplate, and the CLI then said the
            # change was recorded "with the reason".
            if not args.because.strip():
                print("error: --edit requires --because: say why, in a sentence. The reason is "
                      "written into the provenance record beside the profile, and an edit "
                      "recorded without one reads later as a change nobody can account for.",
                      file=sys.stderr)
                return 3
            written = wizard.edit(repo, path, value, because=args.because)
            print(f"Edited {path} in {written}; the change is recorded beside it as typed, with the reason.")
            return 0
        if args.propose:
            written = wizard.propose(
                repo,
                level=args.level,
                builds_ui=None if args.builds_ui is None else args.builds_ui == "yes",
            )
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
    except wizard.ChoseAgentPrompt:
        # `ACT-101`: the adopter picked the AI-assisted route on the welcome screen. Printed here,
        # after the interface has released the terminal, so it can be selected and copied.
        from surfaceplate import assist

        print(assist.build_prompt(repo), end="")
        print(
            "\n" + "-" * 78 + "\n"
            "Copy everything above into your AI coding assistant, in this repository.\n"
            f"To print it again without opening this screen: surfaceplate agent-prompt --target {args.target}\n"
            "Nothing has been written here.",
            file=sys.stderr,
        )
        return 0
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
    except (wizard.AlreadyAdopted, wizard.NeedsHuman, wizard.InstallMismatch) as exc:
        print(f"\n{exc}")
        return 1
    except wizard.WriteRefused as exc:
        print(f"\nRefusing to write: {exc.detail}")
        print("This is the wizard's own safety check, not the checker. Nothing was written.")
        return 1
    except wizard.PartialWrite as exc:
        # Code item 7, and `F101`: a run that created files and then failed says so, file by
        # file - what it removed again, and anything it could not.
        print(f"\nThe profile was not written: {type(exc.cause).__name__}: {exc.cause}", file=sys.stderr)
        for path in exc.removed:
            print(f"  Created before the failure, and removed again: {path}", file=sys.stderr)
        for path in exc.created:
            if path not in exc.removed:
                print(f"  Created before the failure and NOT removed: {path}", file=sys.stderr)
        for problem in exc.problems:
            print(f"  Problem: {problem}", file=sys.stderr)
        print("Your answers are kept in the draft, so re-running `adopt` offers to resume.", file=sys.stderr)
        return 4
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

    import datetime as _dt

    from surfaceplate import check_conformance

    print("  Checking what you just wrote:\n")
    report = check_conformance.evaluate(repo, _dt.date.today(), False, False)
    print(check_conformance.render_text(report))
    # `F85`: the sentence is read from the report, not inferred from the exit code, which
    # covers a pass and a graced WARN alike (`DR-49` (2)).
    print("\n  " + verdict_sentence(report).replace("\n", "\n  "))
    if report.exit_code != 0:
        print(f"\n      surfaceplate check --repo {repo}\n")
        from surfaceplate import about

        print(f"  Looks wrong, not just unfinished? {about.ISSUES}")
        print("  `surfaceplate doctor --report` assembles a paste-ready report, offline.\n")
    print(f"  Re-running `adopt` will not overwrite it; edit {written.name} directly from here.\n")
    return report.exit_code


def verdict_sentence(report) -> str:
    """What the checker's report says, in one sentence a human can act on (`F85`, `DR-51` (6))."""
    if report.verdict == "PASS" and not report.findings:
        return "The checker passes against what you just wrote: nothing outstanding."
    if report.verdict == "WARN":
        until = str((report.record or {}).get("grace_expires", "") or "the grace window ends")
        n = len(report.graceable)
        return (
            f"The checker reports {n} finding(s) under grace until {until}; it will fail after that date.\n"
            "The output above says which artefacts it could not find. That is normal for a first adoption."
        )
    return (
        f"The profile is written, but the checker does not pass against it: {report.explanation or report.verdict}\n"
        "The output above says why. Re-run at any time:"
    )


def _cmd_uninstall(argv: list[str]) -> int:
    """`F138`: there was no way out. No command, no flag, no document - the pathway sweep found
    that by looking for one.

    The install record is the authority, not the current payload: it names every file this
    installer wrote, so removal takes out exactly what was installed rather than what a newer
    version would have installed. The adopter's profile is never removed, and neither is anything
    outside the record.
    """
    from surfaceplate import install_standard

    parser = _Parser(prog="surfaceplate uninstall", description="Remove the standard from a repository.")
    parser.add_argument("--target", default=".", help="Repository to remove it from (default: current directory).")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed, write nothing.")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"error: {target} is not a directory", file=sys.stderr)
        return 3
    code, lines = install_standard.uninstall(target, dry_run=args.dry_run)
    for line in lines:
        print(line)
    return code


_COMMANDS = {
    "install": (_cmd_install, "Install or upgrade the standard into a repository."),
    "check": (_cmd_check, "Check a repository against the standard (--format text|json|sarif)."),
    "adopt": (_cmd_adopt, "Fill in the application profile: interactively, or --propose then --answers."),
    "doctor": (_cmd_doctor, "Report what would stop the first command on this machine; --report assembles a problem report to paste, offline."),
    "agent-prompt": (_cmd_agent_prompt, "Print a prompt to paste into an AI coding assistant, so it can help you adopt without deciding anything for you."),
    "uninstall": (_cmd_uninstall, "Remove the standard, using the install record so exactly what was installed is removed."),
}


def _parser() -> _Parser:
    parser = _Parser(
        prog="surfaceplate",
        description="The Pipo Ventures software delivery standard, installed rather than copied.",
    )
    parser.add_argument("--version", action="version", version=f"surfaceplate {version()}")
    subparsers = parser.add_subparsers(dest="command", metavar="{install,check,adopt,doctor,uninstall}")
    for name, (_handler, help_text) in _COMMANDS.items():
        subparsers.add_parser(name, help=help_text, add_help=False)
    return parser


def _survive_a_narrow_terminal() -> None:
    """No command may die because the terminal cannot render a decorative glyph (`F149`).

    `doctor` and `doctor --report` both crashed with `UnicodeEncodeError` on an ASCII stdout -
    `'ascii' codec can't encode character '\\u2026'` - from the truncation ellipsis in the digest
    columns. The failing command is the one `SUPPORT.md` tells people to run **when something is
    already wrong**, so the diagnostic died exactly where it was needed.

    Fixed at the boundary rather than at the nine glyphs, because the glyph is not the defect: any
    future one would reintroduce it, and a rule that must be remembered at every print site is a
    rule that will be forgotten at one. `errors="replace"` degrades a decoration to `?` and keeps
    the output; nothing here is load-bearing enough that losing a character loses meaning, and a
    report a human can read imperfectly beats a traceback they cannot use at all.

    Narrow stdout is reached by `PYTHONCOERCECLOCALE=0` or `PYTHONUTF8=0` on an ASCII locale;
    plain `LANG=C` is coerced to UTF-8 by Python and was never affected.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:  # a redirected stream that is not a TextIOWrapper
            continue
        try:
            reconfigure(errors="replace")
        except (ValueError, OSError):  # already detached, or not reconfigurable
            pass


def main(argv: list[str] | None = None) -> int:
    _survive_a_narrow_terminal()
    argv = sys.argv[1:] if argv is None else argv
    parser = _parser()
    # The top level owns `--help` and `--version` and names the commands; each command owns its
    # own flags, so everything after the command name is handed over untouched.
    if not argv:
        parser.print_usage(sys.stderr)
        print("error: a command is required: install, check, adopt, doctor or uninstall", file=sys.stderr)
        return 3
    if argv[0] in _COMMANDS:
        handler, _ = _COMMANDS[argv[0]]
        return handler(argv[1:])
    parser.parse_args(argv[:1])  # -h, --help, --version, or a usage error (exit 3)
    parser.print_usage(sys.stderr)
    print(f"error: unknown command {argv[0]!r}; expected install, check, adopt, doctor or uninstall", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
