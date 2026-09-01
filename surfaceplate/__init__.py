"""Surfaceplate — a governance framework that installs into a repository and checks it against
the standard it publishes.

This package IS the payload. `standard/`, `schemas/`, `core/`, `templates/`, `examples/` and
`adapters/` sitting beside this file are not resources bundled alongside the code — they are what
`install_standard.py` copies into an adopting repository, and `install_standard.py` and
`check_conformance.py` are what does the copying and the checking. Nothing here is imported for
its own sake; `install_standard.py` and `check_conformance.py` are run directly, as scripts.

No public API is exported. `import surfaceplate` exists so `repo_root()`
(`install_standard.py:repo_root`) can resolve this directory reliably under every distribution
channel this project supports — a git checkout, a normal pip install, an editable install — by
nothing more than `Path(__file__).resolve().parent`. See `org/decisions/DR-31.md`.
"""

from __future__ import annotations

__all__: list[str] = []
