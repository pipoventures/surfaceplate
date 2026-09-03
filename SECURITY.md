# Security

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository)
via this repository's Security tab: **Security → Report a vulnerability**. This keeps the report
private between you and the maintainer until a fix, if one is needed, is ready.

**This repository is now public** (it was private when this paragraph was first written; that
statement went stale the moment the repository's visibility changed, and is corrected here rather
than left standing beside a later note). Private vulnerability reporting is therefore available to
enable, but **is not enabled today** — verified directly against GitHub's API
(`GET /repos/pipoventures/surfaceplate/private-vulnerability-reporting` currently answers
`enabled: false`), not assumed. Enabling it is listed in
[`org/HUMAN_ACTIONS.md`](org/HUMAN_ACTIONS.md). Until it is, there is no confidential channel here:
a genuinely sensitive report should hold back specifics and ask, via
[GitHub Issues](https://github.com/pipoventures/surfaceplate/issues), for a private way to send them
rather than posting them in the open.

## What happens after a report

There is no dedicated security team and no formal triage or advisory-publication process. A report
is read by the one maintainer. It is acknowledged, and — where a genuine fix is needed — addressed
within the time realistically available, described under [Maintenance](README.md#maintenance) in
the main README. That is the whole process. Nothing more elaborate exists, and this document does
not describe one that doesn't.

## Response expectation

Best effort, from one part-time maintainer. There is no guaranteed response time. A soft
expectation — roughly 30 days to an initial response — is stated so you know what to expect, but it
is an expectation, not a commitment, and may not be met.

## Scope

**In scope:** the code this repository ships — the conformance checker, the installer, the
schemas, and the stack adapters (`scripts/`, `schemas/`, `adapters/`).

**Out of scope:** the security of any repository that installs this standard. This tool checks that
declared controls and artefacts are present and unmodified; it says nothing about whether an
adopting repository's own code, infrastructure, or data are secure, and cannot.

## Independent review

No independent security review of this code has been performed. If one is ever carried out, its
findings will be recorded honestly rather than implied to already exist.
