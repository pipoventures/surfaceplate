"""The Textual interface for `surfaceplate adopt` (`DR-36`).

Imported only by `cli.py`'s `adopt` subcommand and by the TUI tests, never at package import time,
so `install` and `check` - the two commands an adopting repository's CI actually runs - continue to
need none of this and none of `textual`. That is the same discipline `DR-32` established when
`questionary` was the optional dependency, kept intact when it was replaced.
"""
