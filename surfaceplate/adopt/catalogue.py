"""Catalogue data the wizard presents, derived from the checker rather than restated (`DR-6`).

`check_conformance.py` is the checker's own source of truth for what a gate is, which controls a
level requires, and which gates a UI repository cannot avoid. Every constant this module exposes is
read from it directly. A copy would agree with the checker on the day it was written and silently
stop agreeing the next time a gate is added — the exact shape `F23` found inside a drift guard, one
packet before this one.

The one thing genuinely new here is `SECTIONS`: which of the six groups in
`core/PREREQUISITE_GATES.md` each gate belongs to. That grouping exists only as prose section
headings in the document — there is no machine-readable form of it to derive from — so it is encoded
here as boundary counts over `GATE_CATALOGUE`'s own insertion order, which the checker already
declares grouped exactly this way. `tests/adopt/test_catalogue.py` asserts the counts still sum to
`len(GATE_CATALOGUE)` and the names still match the document's own headings, so this is the one place
in the wizard where a real, if narrow, drift risk is checked rather than merely hoped not to occur.
"""

from __future__ import annotations

from surfaceplate import check_conformance as _cc

GATE_CATALOGUE: dict[str, str] = _cc.GATE_CATALOGUE
LEVEL_REQUIRED_GATES: dict[str, set[str]] = _cc.LEVEL_REQUIRED_GATES
DESIGN_GATES: set[str] = _cc.DESIGN_GATES
CONFORMANCE_LEVELS: dict[str, set[str]] = _cc.CONFORMANCE_LEVELS
LEVELS_REQUIRING_FULL_DECLARATION: set[str] = _cc.LEVELS_REQUIRING_FULL_DECLARATION
PATTERN_A_CONTROLS: set[str] = _cc.PATTERN_A_CONTROLS
PATTERN_B_CONTROLS: set[str] = _cc.PATTERN_B_CONTROLS
PATTERN_C_CONTROLS: dict[str, str] = _cc.PATTERN_C_CONTROLS

# (section heading, gate count) in the order core/PREREQUISITE_GATES.md declares them, which is
# also GATE_CATALOGUE's own insertion order. 4 + 5 + 2 + 3 + 2 + 3 = 19.
SECTIONS: list[tuple[str, int]] = [
    ("Design and user interface", 4),
    ("Work and decisions", 5),
    ("Documentation authority", 2),
    ("Tests and evidence", 3),
    ("Data", 2),
    ("Dependencies and release", 3),
]


def sectioned_gates() -> list[tuple[str, list[str]]]:
    """Gate IDs grouped by section, in catalogue order. Derived, not stored."""
    ids = list(GATE_CATALOGUE)
    out: list[tuple[str, list[str]]] = []
    cursor = 0
    for name, count in SECTIONS:
        out.append((name, ids[cursor : cursor + count]))
        cursor += count
    return out


# What each level actually costs, for the recap the conformance-level screen shows (DR-31's
# artifact, Frame 2). Gate and control counts are computed, not typed in; only the one-line
# character of each level - who it is for - is prose, because the catalogue has no field for that
# and inventing one to avoid four lines of hand-written text would be its own small overclaim.
LEVEL_BLURBS: dict[str, str] = {
    "essential": "Proofs of concept, internal tooling, anything whose output nobody outside the "
    "team relies on.",
    "standard": "Anything a colleague or a customer depends on.",
    "full": "Applications producing material quantitative or AI output that other systems consume "
    "as fact.",
}


def level_summary(level: str, builds_ui: bool) -> dict[str, object]:
    """Gate and control counts for `level`, honest about the UI floor's effect on the count."""
    required_gates = set(LEVEL_REQUIRED_GATES[level])
    if builds_ui and level in LEVELS_REQUIRING_FULL_DECLARATION:
        required_gates |= DESIGN_GATES
    return {
        "level": level,
        "blurb": LEVEL_BLURBS[level],
        "gate_count": len(required_gates),
        "control_count": len(CONFORMANCE_LEVELS[level]),
        "controls": sorted(CONFORMANCE_LEVELS[level]),
    }
