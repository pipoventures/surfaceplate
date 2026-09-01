# Organisation Identifier

This document is the declared source of truth for the organisation identifier, in the same sense
that `NAMESPACE.md` is the declared source of truth for the schema namespace (see
[DR-6](org/decisions/DR-6.md)). `tests/check_identifiers.py` parses this file at run time and holds
no copy of any of these values. A change to the block below that the repository does not follow —
or content that introduces a spelling not declared here — fails the check.

## Declared identifiers

```text
github-org:    <github-organisation-slug>
urn-authority: <urn-authority-segment>
legal-name:    <registered-legal-name>
```

Current values:

```text
github-org:    pipoventures
urn-authority: pipo-ventures
legal-name:    Pipo Ventures Ltd
```

- **`github-org`** — the slug this repository is actually hosted under. Authoritative for every
  `github.com/<org>/...` URL in this repository. Confirmed live: `git ls-remote` against
  `https://github.com/pipoventures/surfaceplate.git` resolves `refs/heads/main`.
- **`urn-authority`** — the authority segment of the schema namespace URN declared in
  `NAMESPACE.md` and carried in every `surfaceplate/schemas/*.schema.yaml` `$id`. Governed by
  [DR-6](org/decisions/DR-6.md); changing it is a rename of identity, not covered by this document.
- **`legal-name`** — the registered entity named in prose (for example
  `surfaceplate/standard/conformance-block.md`).

**These three values currently disagree in spelling**, which is exactly the state
[DR-9](org/decisions/DR-9.md) records as finding F5. This document does not assert they are
reconciled; it asserts what each *should* read as, given what is currently true of each context, so
that a check can compare the repository against a declaration rather than against an assumption.
Reconciling them — including whether the URN authority ever changes — is out of scope here and
governed separately by `NAMESPACE.md`'s "Changing the base later" section.

## Known non-matches

The organisation-check strips a trailing `.` before comparing a token, so a sentence ending in the
maintainer's surname does not need a separate exclusion, and the maintainer's personal email domain
(`mario@pipoventures.com`) tokenises to `pipoventures` — the declared `github-org` value — and
passes on its own merits rather than needing to be named here. Only the bare surname needs
declaring, because on its own it is not the organisation:

```text
Pipo
```

**`Pipo`** — the maintainer's surname (Mario Pipo / Mario Pipo Sanchez), used throughout
`org/decisions/*.md` and elsewhere as a personal name, not an organisation reference.

## Quoted evidence

A record that documents an identifier drift has to be able to quote the drift. The check
cannot tell a live instruction from a quoted historical fact — that limitation is recorded
in [DR-9](org/decisions/DR-9.md) — so the places where a record legitimately reproduces a
wrong spelling are declared here.

Each entry is a **`path :: token`** pair, never a bare path. Muting a whole file would also
mute a *different*, real drift appearing in it later; pairing the exemption to one token in
one file means a new wrong spelling in the same record is still caught. The check refuses to
start if an entry names a file that does not exist, so an exemption cannot outlive the thing
it was written for.

```text
org/decisions/DR-9.md :: Pipo-Ventures-Ltd
org/FINDINGS.md :: Pipo-Ventures-Ltd
```

Both record finding F5 — the organisation-identifier drift — and quote the non-resolving
clone URL as the evidence for it. `INSTALL.md` is deliberately **not** on this list: it
carried the drift as a live instruction rather than as a quotation, and was corrected.

## Third-party organisations

The GitHub-URL rule asks whether every `github.com/<owner>/` matches the declared `github-org`.
That question is right for a URL that is *meant* to point at this organisation and wrong for one
that is not: a repository that links to a tool, an action, or a document hosted by somebody else is
not misspelling its own identity. The rule cannot tell the two apart, and treating a third party as
a drift is the same defect class as `F14` — a check whose rule is broader than the thing it means
to detect. It is recorded as `F17`.

The escape hatch is a declaration rather than a widening of the rule. Owners named here are
recognised as **other people's organisations** and are exempt wherever they appear:

```text
gitleaks
```

**`gitleaks`** — the secret scanner declared in `governance/application-profile.yaml` and fetched
by `.github/workflows/secret-scan.yml` from `github.com/gitleaks/gitleaks`. It is a third party,
not a spelling of this organisation.

Unlike the quoted-evidence block above, these entries are **not** paired to a path, and the
difference is deliberate rather than an inconsistency. A quoted drift is a wrong spelling of *this*
organisation that one specific record has a reason to reproduce, so scoping it to that record keeps
the same wrong spelling caught everywhere else. A third-party organisation is legitimately
referenced anywhere, and pairing it to paths would mean editing this document every time a link
moves — a maintenance cost with no detection benefit, since the token is not a drift in any file.

This block is **not** a general mute list. Adding an owner here asserts it is a real organisation
belonging to somebody else; it does not mean "ignore this spelling."

## Why this cannot live in `NAMESPACE.md`

`tests/validate_contracts.py` asserts that `NAMESPACE.md` contains **exactly two** ` ```text `
blocks — the base pattern and the current base. A third block anywhere in that file fails that
check. The organisation identifier is declared here instead, in its own document with its own
reader, following the same shape rather than sharing the file.
