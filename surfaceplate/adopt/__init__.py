"""The `surfaceplate adopt` wizard.

One rule governs everything in this package, stated in `org/RELEASE_PLAN.md` before any of it was
built: **it asks, the human answers, the tool writes.** No module here selects a conformance level,
invents a rationale, or sets a date. Every judgement call `core/PREREQUISITE_GATES.md` and
`core/CONFORMANCE_LEVELS.md` require is elicited from the human and recorded verbatim.

The wizard produces exactly one artefact — a complete, schema-valid `governance/application-profile.yaml`
— and touches nothing else. It does not create method registry entries, wire CI, or write code. See
`org/decisions/DR-32.md`.
"""

from __future__ import annotations

__all__: list[str] = []
