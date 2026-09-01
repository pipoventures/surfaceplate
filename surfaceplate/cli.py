"""`surfaceplate` — the console-script `DR-12` committed to.

Three subcommands. `install` and `check` are thin, behaviour-preserving wrappers over
`install_standard.py` and `check_conformance.py` - the mechanism does not change, only how
someone who `pip install`ed the package reaches it. `adopt` is the wizard: the substantial new
work, and the reason this module exists rather than remaining three separate scripts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _cmd_install(argv: list[str]) -> int:
    from surfaceplate import install_standard

    return install_standard.main(argv)


def _cmd_check(argv: list[str]) -> int:
    from surfaceplate import check_conformance

    return check_conformance.main(argv)


def _cmd_adopt(argv: list[str]) -> int:
    from surfaceplate.adopt import wizard
    from surfaceplate.adopt.interview import Cancelled

    try:
        import textual  # noqa: F401  (checked here so the failure is clear, not a bare traceback)
    except ImportError:
        print(
            "`adopt` needs the optional `textual` dependency, which is not installed.\n"
            "Run: pip install surfaceplate[adopt]",
            file=sys.stderr,
        )
        return 2

    parser = argparse.ArgumentParser(prog="surfaceplate adopt")
    parser.add_argument(
        "--target", default=".", help="Repository to adopt into (default: current directory)."
    )
    args = parser.parse_args(argv)
    repo = Path(args.target).resolve()

    # `adopt` is a full-screen interface and needs a real terminal. Refusing with a route the
    # reader can take is the `F35`/`ACT-025` lesson: a refusal that only describes an outcome is
    # not a refusal anyone can act on. The draft, if any, is named as preserved so a piped or
    # CI invocation cannot read as having lost work.
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print(
            "`adopt` is an interactive, full-screen wizard and needs a real terminal; this one is "
            "not attached to a TTY (output is piped, redirected, or running in CI).\n"
            "\n"
            "  Run it directly in a terminal:  surfaceplate adopt --target " + str(repo) + "\n"
            "\n"
            "Nothing was read or written, and any saved draft in that repository is untouched.",
            file=sys.stderr,
        )
        return 2

    from surfaceplate.adopt.tui.app import TextualInterview

    try:
        written = wizard.run(repo, TextualInterview())
    except Cancelled:
        print("\nCancelled. Nothing was written; your draft is kept so you can resume.")
        return 1
    except wizard.NotInstalled as exc:
        print(f"\n{exc}")
        return 2
    except wizard.AlreadyAdopted as exc:
        print(f"\n{exc}")
        return 2
    except wizard.WriteRefused as exc:
        print(f"\nRefusing to write: {exc.detail}")
        print("This is the wizard's own safety check, not the checker. Nothing was written.")
        return 3
    except Exception as exc:  # noqa: BLE001 - deliberate; see below
        # `F38`: the renderer raises `ValueError` for a value it cannot place, and `wizard.run`'s
        # second, authoritative render sits outside any handler. Before this, such a value reached
        # the adopter as a raw traceback - the failure mode this framework tells everyone else to
        # avoid. The draft is named as kept, because it is: nothing is cleared except on a
        # successful write.
        print(f"\nThe wizard could not finish: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(
            "Nothing was written. Your answers are kept in the draft, so re-running `adopt` offers "
            "to resume from where this stopped.",
            file=sys.stderr,
        )
        return 4

    # A full-screen app closes and the terminal is restored; two short lines after that are easy
    # to miss entirely. The maintainer finished a real adoption and reported "the wizard just
    # closed with no confirmation if the adoption was successful or not" - so the ending says what
    # was written AND what the checker makes of it, which is the question actually being asked.
    rule = "\u2500" * 66
    print(f"\n{rule}")
    print(f"  Written: {written}")
    # `ACT-033`: a run that created files in someone's repository and reported only the profile
    # would be understating what it did. The second paragraph is the point-of-use labelling the
    # standard's own provenance rules require: the gate's check passes on these files existing, and
    # that is not the same as the practice they stand for happening.
    for path in getattr(written, "created", []):
        print(f"  Created: {path}")
    # A file that could not be created is reported too. Silence here would leave an adopter
    # believing a gate has an artefact when it has none - the profile names it either way.
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

    # The checker prints its own report, which is the point: an adopter asking "did that work?"
    # gets the actual answer rather than a reassurance. There is no quiet mode and inventing one
    # would be a change to a published control for a cosmetic reason.
    print("  Checking what you just wrote:\n")
    findings = check_conformance.main(["--repo", str(repo)])
    if findings == 0:
        print("\n  The checker passes against what you just wrote.")
    else:
        print(
            "\n  The profile is written, but the checker does not pass against it yet.\n"
            "  That is normal for a first adoption - the output above says which artefacts it\n"
            "  could not find. Re-run at any time:\n"
            f"\n      surfaceplate check --repo {repo}\n"
        )
    print(f"  Re-running `adopt` will not overwrite it; edit {written.name} directly from here.\n")
    return 0


_COMMANDS = {"install": _cmd_install, "check": _cmd_check, "adopt": _cmd_adopt}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] not in _COMMANDS:
        print("usage: surfaceplate {install,check,adopt} ...", file=sys.stderr)
        print(
            "  install   Install or upgrade the standard into a repository.\n"
            "  check     Check a repository against the standard.\n"
            "  adopt     Interactively fill in the application profile.",
            file=sys.stderr,
        )
        return 2
    return _COMMANDS[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
