# Schema Namespace

## Declared base

```text
urn:pipo-ventures:surfaceplate:<schema-contract-version>:<schema-file-name>
```

Current base:

```text
urn:pipo-ventures:surfaceplate:0.7.0:
```

Every schema in `schemas/` MUST declare an `$id` of exactly the current base followed by that
schema's own file name.

**The two blocks above are the source of truth, not a description of one.**
`tests/validate_contracts.py` parses them out of this file and checks the schemas against what it
reads here. It holds no namespace literal of its own. A change to either block that the schemas do
not follow — or a schema that stops following them — fails the check. Before 0.12.0 the test held
its own copy of the base, so it agreed with the schemas by construction and could never disagree
with this document; that is the defect this arrangement removes.

## What an `$id` is, and is not

An `$id` is a **name**, not an address. Nothing is fetched from it. A JSON Schema validator uses it
only to tell schemas apart and to resolve references between them. All references inside this
package are local (`#/$defs/...`), so no network access or external resource registry is required
to validate any contract here.

A `urn:` form is used deliberately, in preference to an `https://` form, because:

- it makes no claim on any domain and therefore needs no domain-ownership, brand, or infrastructure
  decision;
- it cannot be mistaken for a live endpoint by a reader or by tooling that speculatively fetches;
- it carries a version, so two incompatible schema contracts never claim the same identity.

The previous base, `https://example.invalid/engineering-control-kit/`, was a placeholder. `.invalid`
is reserved by RFC 2606 and is guaranteed never to resolve. It also carried no version, so any two
releases produced colliding schema identities.

## Version in the identifier

**The version segment is the schema contract version.** It names the version of the contract that
the schemas in `schemas/` collectively express. It is bumped **only on a breaking schema change** —
a field removed, a type narrowed, a previously optional field made required, an enum value
withdrawn, or any other change that can invalidate an instance that was valid before.

It is **independent of the framework version** recorded in `VERSION`. A framework release that
changes no schema, or changes one additively, leaves every `$id` untouched and every adopter's
pinned identifier still valid. A schema contract version is therefore expected to lag the framework
version, often by several releases.

This replaces the rule in force up to 0.11.0, under which the segment was the framework version and
every release minted new identities for unchanged schemas. That rule was rejected: see
[DR-6](org/decisions/DR-6.md). It broke adopter pins on releases where nothing about the schemas had
moved, which is a cost paid by every adopter for no corresponding gain in identity.

The current value is **0.7.0**, carried forward unchanged. It was the framework version at the
release in which this base was introduced, and it is retained rather than renumbered precisely so
that no adopter's pinned `$id` changes at 0.12.0. Renumbering it — to `1.0.0`, say, to mark the new
meaning — was considered and rejected for the same reason the old rule was: it would change every
`$id` without a single schema having changed.

The rule is retrospective in effect as well as prospective. Between 0.7.0 and 0.11.0 the framework
version advanced four times while every schema `$id` stayed at `0.7.0`; every schema change across
those releases was additive. Under the old rule that state was a four-release drift. Under this rule
it is the correct state, correctly recorded.

Identity as recorded here is not a substitute for the pinned artefact. What reproduces a validation
result is the release digest an adopter records in `adoption.framework_digest`, which continues to
change on every release whether or not any schema does.

### The 0.12.0 rename is not a version bump

Release 0.12.0 changed the organisation and product segments of the base — the whole prefix ahead of
the version — as part of bringing every internal identifier into line with this repository's name.
That is a change of *identity*, not of *contract*, and it is deliberately not expressed through the
version segment, which stayed at `0.7.0`. It is a one-time event of the kind the next section
governs, and it was taken while the cost of taking it was still small.

## Changing the base later

This decision is deliberately reversible. It is recorded in one place, and one test fails if the
schemas stop matching what is recorded there.

To change it:

1. Update the base in every `surfaceplate/schemas/*.schema.yaml` `$id`.
2. Update the current base recorded above. There is no second copy to keep in step —
   `tests/validate_contracts.py` reads this file, and a mismatch between the two steps fails it.
3. Record the change in `CHANGELOG.md`, and, if the version segment moved, say which schema change
   was breaking.
4. Notify every application whose `application-profile.yaml` records this framework version in
   `adoption.framework_version`, and have each re-pin and re-validate.

Step 4 is the only expensive step, and its cost scales with the number of adopting applications.

**Therefore: change the base while the number of adopting applications is small.** At the time of
writing there are **no adopting applications at all**, so step 4 costs nothing and the base can
still be changed freely. That is the cheapest this decision will ever be, and it stops being cheap
with the first adopter — not the tenth.

If an organisation-wide URI or namespace convention exists or is later published, adopt it and treat
the migration above as a normal versioned change.
