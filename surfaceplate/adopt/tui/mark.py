"""The mark on the opening screen: a surface plate, in isometric, with the monogram on its top
face (`F89`). Generated from two numbers rather than drawn, so the proportions cannot be wrong by
a row the way a hand drawing was: the right face is exactly `thickness` rows deep and its bottom
slant runs parallel to the top face's edge for the full length.

Only three kinds of character: box-drawing slants and edges for the slab, and the full block for
the letters, which is the one glyph every monospace font renders identically. The maintainer
chose the mark from alternatives on 2026-09-02 (`DR-53`).
"""

from __future__ import annotations

# The monogram, five rows high, full blocks only.
S = ("█████", "█    ", "█████", "    █", "█████")
P = ("█████", "█   █", "█████", "█    ", "█    ")

WIDTH = 25      # inner width of the top face, in cells
THICKNESS = 2   # depth of the slab: rows of the front face
LEFT = 6        # column of the front face's left edge
GAP = 3         # cells between the two letters

EDGE = "╱▔▁▏"   # the characters the slab is drawn with, for the tests


def slab(width: int = WIDTH, thickness: int = THICKNESS, left: int = LEFT) -> list[str]:
    """The rows of the slab with the monogram on its top face, left-facing, right-stripped.

    Row 0 is the top edge; the letters occupy the next five rows; then the bottom edge of the top
    face, and `thickness` rows of the front face. The right face's back edge is vertical for
    `thickness` rows below the top-right corner, and its bottom edge slants down-left from there
    to the front face's bottom-right corner, parallel to the top face's right edge.
    """
    top_rows = 2 + len(S)
    x0 = left + top_rows - 1            # column of the top edge's left corner
    back = x0 + 1 + width + 1           # column of the back-right vertical edge
    letters_x = x0 + 4                  # inside the top face at every row: its left edge ends at x0 - 6
    rows: list[str] = []
    for i in range(top_rows):
        line = [" "] * (back + 1)
        lft = x0 - i
        line[lft] = "╱"
        fill = "▔" if i == 0 else ("▁" if i == top_rows - 1 else " ")
        for x in range(lft + 1, lft + 1 + width):
            line[x] = fill
        line[lft + 1 + width] = "╱"
        if 1 <= i <= len(S):
            for k, c in enumerate(S[i - 1]):
                line[letters_x + k] = c
            for k, c in enumerate(P[i - 1]):
                line[letters_x + len(S[0]) + GAP + k] = c
        if i <= thickness:
            line[back] = "▏"
        else:
            line[back - (i - thickness)] = "╱"
        rows.append("".join(line).rstrip())
    front_left = x0 - (top_rows - 1)
    for j in range(thickness):
        i = top_rows + j
        line = [" "] * (back + 1)
        line[front_left] = "▏"
        line[front_left + 1 + width] = "▏"
        if j == thickness - 1:
            for x in range(front_left + 1, front_left + 1 + width):
                line[x] = "▁"
        line[back - (i - thickness)] = "╱"
        rows.append("".join(line).rstrip())
    return rows


def height() -> int:
    return 2 + len(S) + THICKNESS


def beside_column() -> int:
    """The column where text beside the slab starts: two cells clear of the back edge."""
    x0 = LEFT + (2 + len(S)) - 1
    return x0 + 1 + WIDTH + 1 + 3
