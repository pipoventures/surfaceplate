# Decision log

The append-only record of material decisions taken in this repository, and the artefact the
`decision_before_implementation` gate points at.

**This file existing is not the practice.** It was created when Surfaceplate was adopted here so the
gate has a real place to point at. What the gate asks is that a material decision is written down
*before* the change implementing it is built, rather than reconstructed afterwards once the shape is
already settled.

## How this log works

**Append only.** Add a new entry; never rewrite or delete an existing one. Where a decision is
superseded, the new entry says so and the old one is marked historical rather than removed — a
correction whose validity depends on reading order is not a correction.

A decision worth recording here is one that would be expensive to reverse, that changes a public
contract or a material output, that accepts a risk, or that a future reader would otherwise have to
reverse-engineer from the code.

Each entry identifies: the decision, the alternatives considered, the rationale, the accountable
human, the date, and the authorities it affects. Anything richer belongs in its own decision record,
for which `.standards/templates/decision-record.md` is the form.

## Entries

**No decisions are recorded yet.** That is accurate on the day this file was created, and stops
being accurate the moment a material change is made without an entry.
