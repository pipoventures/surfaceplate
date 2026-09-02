# Release checklist

The records a release of this repository needs before its preparation begins, drawn from the standard's own rules.

**This file existing is not the practice.** It was created when Surfaceplate was adopted here, so that the `records_before_release` gate has a real place to point at. What the gate asks is that the change and decision records a change's risk class requires *exist before release preparation begins*, rather than being backfilled to make a checklist look complete. A file that stays empty while the thing it records happens around it is a finding about this repository, not a satisfied control; the checker cannot tell the difference, because it checks that this file exists and holds no placeholder.

## Before preparing a release

For every change in the release:

- the activity is registered and marked done, with the evidence its definition of done named (`work_registration`);
- the change record exists (`change_record_before_completion`);
- for a material change, the decision record exists and predates the implementation (`decision_before_implementation`);
- the risk class was written on the work packet before implementation (`risk_classification`);
- any records that class requires beyond these exist; which records each class requires is declared in this repository's risk classification, and until it is declared this line cannot be ticked.

Then, for the release itself: the checksum manifest is produced and verified, the archive is scanned for secrets and inspected for unintended files, and the release decision is taken by the release authority named in `governance/application-profile.yaml`. Checks passing means checks passed; a release is a human decision.

**This checklist quotes the standard and declares nothing of this repository's own yet.** Which records each risk class requires is the one item only this repository can supply.
