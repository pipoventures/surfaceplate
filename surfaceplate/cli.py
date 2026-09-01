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
    from surfaceplate.adopt.prompting import Cancelled, InteractivePrompt

    try:
        import questionary  # noqa: F401  (checked here so the failure is clear, not a bare traceback)
    except ImportError:
        print(
            "`adopt` needs the optional `questionary` dependency, which is not installed.\n"
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

    print("Surfaceplate — adoption wizard")
    print("This asks; you answer; nothing is written until you confirm at the end.\n")

    try:
        written = wizard.run(repo, InteractivePrompt())
    except Cancelled:
        print("\nCancelled. Nothing was written.")
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

    print(f"\nWrote {written}.")
    print("Run `surfaceplate check` (or the installed hook, on your next commit) to verify it.")
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
