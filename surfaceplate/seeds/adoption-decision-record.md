# Decision record: adopt the Surfaceplate software delivery standard

The record the `adoption.decision_record_id` field of `governance/application-profile.yaml` points
at. It was created by `surfaceplate adopt` when this repository was adopted, because no decisions
directory existed yet to hold one.

**This file existing is not the decision.** The decision was taken by the person who ran the wizard
and approved the profile at its review; this record is where that decision is written down so a
later reader does not have to reconstruct it from the profile alone.

## Decision

Adopt the Surfaceplate standard in this repository, at the conformance level recorded in
`governance/application-profile.yaml`, with the control decisions and prerequisite gates recorded
there. The origin of every value in that profile - typed, discovered, example, computed, fact of
record, scaffolded - is in `governance/application-profile.provenance.yaml`, written beside it.

## Alternatives considered

Not adopting; adopting at a different level. The level is a human decision recorded in the
profile, and the profile's own `review_by` date is when it is next reconsidered.

## Accountable human

The profile's `owner`. Date: the profile's `adoption.adoption_date`.

## Affected authorities

`governance/application-profile.yaml` is the authority for what applies here. This record does
not restate it.
