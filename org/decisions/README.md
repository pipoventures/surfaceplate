# Decision records

> **Commit SHAs cited in these records refer to a private development history.** This repository
> begins at `0.16.0`; work from `0.2.0` to `0.15.0` was done in a repository that is retained,
> archived and unaltered but not published (`DR-23`). The citations are kept rather than stripped:
> they are accurate about what happened, and removing them would make these records less true, not
> more verifiable. What they cost a reader is corroboration, and this note is here so that cost is
> visible rather than discovered. — index and convention

This directory did not exist before 30 August 2026. It is the location for decision records
instantiated from `templates/decision-record.md` that concern the Surfaceplate framework's own
architecture and governance, as distinct from a decision made by an adopting application (which
records its own decisions in its own repository, using the same template).

## Decision maker

**Mario Pipo (maintainer).**

This is the convention every record in this directory cites in its `Decision owner` field. It was
previously recorded in `org/SCOPE_DECISIONS.md`, which `v0.13.0` deleted; the line was rescued here
rather than lost, because six records depend on it.

There is one maintainer. No independent validator, technical reviewer or release authority exists,
and self-approval would not be independence — so those roles stay unassigned in every record, and
that is a stated constraint rather than an oversight. See [DR-6](DR-6.md)'s approval block.

## Why here

`org/` holds this repository's self-referential governance documents. `org/decisions/` follows that
placement precedent but not the shape of the prose registers that used to sit beside it.
`templates/decision-record.md` is structured per instance (a Decision ID, an Approval block),
matching an architecture-decision-record idiom rather than a running prose register. Each decision
here is therefore its own file, addressable by its Decision ID, with this file as the index.

No prior convention for where `decision-record.md` instances live existed anywhere in this
repository at the time the first five were written. Nothing here supersedes an existing rule.

## Numbering

`DR-<n>`, sequential, never reused.

## Records

| ID | Title | Status |
|---|---|---|
| [DR-1](DR-1.md) | Hook composition when `core.hooksPath` is already set | accepted — not implemented |
| [DR-2](DR-2.md) | Doctrine authority: demotion, not merge | accepted — not implemented |
| [DR-3](DR-3.md) | Crosswalk scope | accepted — not started |
| [DR-4](DR-4.md) | Doctrine vendoring | accepted — not implemented |
| [DR-5](DR-5.md) | Open findings F1, F2, F3 | accepted — F1, F2, F3 fixed in v0.13.0 |
| [DR-6](DR-6.md) | Namespace version segment tracks the schema contract | accepted — implemented in v0.12.0 |
| [DR-7](DR-7.md) | Removal of the fabricated adoption record | accepted — implemented in v0.13.0 |
| [DR-8](DR-8.md) | Finding codes renamed `SDS` → `SP` | accepted — implemented in v0.13.0 |
| [DR-9](DR-9.md) | Finding F5: organisation identifier drift, and a derived-identifier control | accepted — implemented in v0.14.0 |
| [DR-10](DR-10.md) | Pip distribution and the pinning model | accepted — not implemented |
| [DR-11](DR-11.md) | Integrity for generated artefacts | accepted — not implemented |
| [DR-12](DR-12.md) | Architecture and permanent scope | accepted — not implemented |
| [DR-13](DR-13.md) | Governance before implementation | accepted — not implemented |
| [DR-14](DR-14.md) | Anchor distribution identity on the manifest digest | accepted — implemented, closing `F7` |
| [DR-15](DR-15.md) | Enforcement placement: organisation-level reusable workflow | accepted — not implemented |
| [DR-16](DR-16.md) | Publisher vendoring: install normally, exclude `.standards/` from the release build | accepted — implemented with DR-13 item 0 |
| [DR-17](DR-17.md) | `SP032` detects placeholders by token, not by shape: remove the angle-bracket branch | accepted — implemented |
| [DR-18](DR-18.md) | `secret_hygiene` gains verification: declare a scanner, and wire it so it can fail | accepted — implemented |
| [DR-19](DR-19.md) | Contributor framework: DCO sign-off, no contributor licence agreement | accepted |
| [DR-20](DR-20.md) | Vendored set kept whole and governed; review surface separated; drift detected | accepted — implemented |
| [DR-21](DR-21.md) | Retire the hand-written producer evidence record; the suites are the evidence | accepted — implemented |
| [DR-22](DR-22.md) | Placeholder-scan exemptions: declared in the profile, narrow, and announced | accepted — implemented |
| [DR-23](DR-23.md) | Publish as a new public repository with no prior history; archive this one | accepted — maintainer actions outstanding |

`DR-1` through `DR-5` were recorded together, on 30 August 2026, against `v0.11.0`
(`22728e770dbd018305744b9ae5785fe04dbe2a36`), as the first deliberate application of this
framework's own decision-record template to a decision about the framework itself.

`DR-6` was recorded the same day against `v0.12.0`, `DR-7` and `DR-8` against `v0.13.0`, and `DR-9`
against `v0.14.0`. These four differ from the first five in one respect worth noting: those five
record decisions taken and then deferred, and each is marked "not implemented". `DR-6` through
`DR-9` are implemented by the releases that record them, so their evidence sections cite the change
and its tests rather than describing work still to be done.

`DR-10` and `DR-11` were recorded together against `v0.14.0`, deliberately reasoned about as a
pair because each constrains the other — see the "cross-record interaction" section each carries.
They return to the first five's shape: decided, and explicitly marked not implemented, pending
whichever future release first ships pip distribution or a per-agent generated file.

`DR-12` and `DR-13` were recorded together, also against `v0.14.0`. `DR-12` settles this framework's
permanent architecture and scope; `DR-13` gates all further implementation on surfaceplate first
being conformant to what it publishes, and depends on `DR-12` being settled to know what "conformant
to" means. Both are decided, not implemented, and both are ordered by `org/RELEASE_PLAN.md`, which
is not itself a decision record and will change.

`DR-14` and `DR-15` follow an external adversarial review whose claims were verified against the
source before anything was recorded; what survived that verification is in
[`org/FINDINGS.md`](../FINDINGS.md). `DR-14` takes up an option `DR-10` explicitly deferred rather
than rejected, and supersedes one reasoning premise in `DR-10` while leaving its rejections intact —
the record says precisely which. `DR-15` responds to finding `F8` and is the first record here to
recommend a posture the maintainer cannot currently demonstrate, because rulesets are unavailable on
this repository's plan; it says so rather than omitting it. Both are decided, not implemented.

`DR-5` is a special case. It is left as written — its severity assessments and its raw evidence are
the historical record of what was found at `v0.11.0`, and rewriting them would destroy the record
rather than update it. Only its one open question about whether the self-check workflow had ever
executed is updated in place, because that question has since been answered.
