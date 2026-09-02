# Test conventions

How tests in this repository are named and where they live, so that a change can be routed to its tests mechanically and a new test lands where the next reader expects it.

**This file existing is not the practice.** It was created when Surfaceplate was adopted here, so that the `test_convention` gate has a real place to point at. What the gate asks is that a declared convention exists and that new tests follow it; the convention itself is this repository's own. A file that stays empty while the thing it records happens around it is a finding about this repository, not a satisfied control; the checker cannot tell the difference, because it checks that this file exists and holds no placeholder.

## Naming

Tests are named `test_{area}_{description}`, the convention the standard recommends (`.standards/agent-instructions/tests.md`). The area names the part of the repository under test; the description says what behaviour is asserted.

## Areas

| Area | What it covers | Where its tests live |
|---|---|---|

**No test areas are declared yet.** That is an accurate statement on the day this file was created. Until an area is declared, a test's name follows the convention but nothing routes a change to the subset that covers it, which is what the areas exist for.

## Adding an area

Declare the area when its first test is written, in the same change.
