# Output validation

The log of validation and review for every output that leaves the delivery team.

**This file existing is not the practice.** It was created when Surfaceplate was adopted here, so that the `output_validation_before_external_use` gate has a real place to point at. What the gate asks is that an output is validated and reviewed *before* any use outside the team; the boundary is external use, not generation. A file that stays empty while the thing it records happens around it is a finding about this repository, not a satisfied control; the checker cannot tell the difference, because it checks that this file exists and holds no placeholder.

## Log

Each entry records: the output and the run that produced it; who validated it and how; who reviewed it; the date; and where it went.

| Output | Run | Validated by, how | Reviewed by | Date | Sent to |
|---|---|---|---|---|---|

**No outputs are logged yet.** That is an accurate statement on the day this file was created, and it stops being accurate the moment an output crosses the team's boundary without an entry above.

## Adding an entry

Log the validation before the output is sent, in the same change or record that sends it.
