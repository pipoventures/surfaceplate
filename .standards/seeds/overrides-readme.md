# Overrides

The directory of override records: each a YAML file validating against `override-record.schema.yaml`, recording one deliberate manual adjustment to a governed result, with its classification, before and after values, rationale, evidence, owner, approval and rollback.

**This directory existing is not the practice.** It was created when Surfaceplate was adopted here, so that the `overrides` control has a real place to point at. The checker validates every YAML record here and requires each one's run reference to resolve; an empty directory passes, because it establishes that no invalid override exists, never that adjustments are being recorded.

**No overrides are recorded yet.** That is an accurate statement on the day this directory was created, and it stops being accurate the moment a number is adjusted by hand anywhere in this repository without a record beside this file. This note is not a record and the checker does not read it.
