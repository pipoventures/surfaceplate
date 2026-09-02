# Data sources

The register of data sources this repository uses, with each one's validation and approval state.

**This file existing is not the practice.** It was created when Surfaceplate was adopted here, so that the `data_source_lifecycle` gate has a real place to point at. What the gate asks is that a data source completes its validation and approval *before* it becomes selectable in the system; a source that is merely present and unapproved is eventually used by someone who assumed it was vetted. A file that stays empty while the thing it records happens around it is a finding about this repository, not a satisfied control; the checker cannot tell the difference, because it checks that this file exists and holds no placeholder.

## Register

Each entry records: the source and where it comes from; what it is used for; its classification; its validation state and evidence; its approval state, by whom and when; and the date it is next reviewed.

| Source | Used for | Classification | Validation | Approval | Review by |
|---|---|---|---|---|---|

**No data sources are registered yet.** That is an accurate statement on the day this file was created, and it stops being accurate the moment a source is used here without an entry above.

## Adding an entry

Register the source when it is proposed, with its validation and approval columns empty and saying so; fill them as each step completes. A source becomes selectable only when both are filled.
