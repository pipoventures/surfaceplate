# Dependency reviews

The log of dependency changes that could move this repository's outputs, with the evidence of what each change did.

**This file existing is not the practice.** It was created when Surfaceplate was adopted here, so that the `dependency_output_delta` gate has a real place to point at. What the gate asks is that a dependency change capable of moving outputs carries delta evidence and a review *before* it merges; a lock file records what changed, not what the change did. A file that stays empty while the thing it records happens around it is a finding about this repository, not a satisfied control; the checker cannot tell the difference, because it checks that this file exists and holds no placeholder.

## Log

Each entry records: the dependency and the versions before and after; whether outputs could move and why; the delta evidence, or the reasoned statement that there is none; who reviewed it; and the date.

| Dependency | From | To | Could outputs move? | Evidence | Reviewed by, on |
|---|---|---|---|---|---|

**No dependency reviews are logged yet.** That is an accurate statement on the day this file was created, and it stops being accurate the moment a dependency that could move outputs changes without an entry above.

## Adding an entry

Log the review in the change that updates the dependency, before it merges.
