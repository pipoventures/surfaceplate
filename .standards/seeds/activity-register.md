# Activity register

The register of identified work in this repository.

**This file existing is not the practice.** It was created when Surfaceplate was adopted here, so
that the `work_registration` gate has a real place to point at. What the gate asks for is that work
is named here *before* it starts. A register that stays empty while work happens around it is a
finding about this repository, not a satisfied control — and the history audit cannot tell the
difference, because it checks that this file exists, not that anyone kept it current.

## Where this register starts

It binds from the date recorded as `effective_from` in
`governance/application-profile.yaml`, which is the day it was created. Work before that date is out
of scope: a gate binds from a date, and adopting one has never required rewriting the past.

## Status vocabulary

`planned`, `in_progress`, `blocked`, `waiting_for_review`, `external_dependency`, `deferred`,
`done`.

Status is derived from dependencies rather than asserted: an unsatisfied hard dependency is
`blocked`, an unsatisfied review dependency is `waiting_for_review`, an unsatisfied external
dependency is `external_dependency`.

`done` requires the definition of done to be met **and** the required evidence to exist. Human
approval, independent validation, risk acceptance and release readiness are never marked complete on
an agent's authority.

## Register

Each entry records at least: a stable `activity_id` cited by every commit and document change that
belongs to it; what it delivers; the accountable owner and the reviewer; its status; what it depends
on and how; whether it can change a material output; an objectively checkable definition of done;
and what evidence must exist before it can be called done.

| Activity | Title | Owner | Reviewer | Status | Depends on | Type | Material? | Definition of done | Evidence required |
|---|---|---|---|---|---|---|---|---|---|

**No activities are registered yet.** That is an accurate statement about this repository on the day
this file was created, and it stops being accurate the moment work begins without an entry above.

## Adding an entry

Add the row in the same commit as the work it describes. A register updated afterwards is a
reconstruction rather than a record, and reads identically to one that was kept properly — which is
why the timing is the rule and not the format.
