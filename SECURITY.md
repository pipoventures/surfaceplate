# Security

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/configuring-private-vulnerability-reporting-for-a-repository)
via this repository's Security tab: **Security → Report a vulnerability**. This keeps the report
private between you and the maintainer until a fix, if one is needed, is ready.

The repository is public and the feature is on: `GET
/repos/pipoventures/surfaceplate/private-vulnerability-reporting` answered `enabled: true` on
**2026-09-08**. That is a dated observation of a setting a person can change, not a standing
property of this document — if the Security tab offers you no such button, the setting has moved
and this line is stale.

*Historical, kept because the pattern is the point:* this paragraph has now been wrong twice. It
said the repository was private weeks after it was made public (`F118`), and then said private
reporting was *"not enabled today"* after it had been enabled (`F127`). Both were
true when written and both went false without the file changing, because what they describe lives
in GitHub's settings and not in this repository. Nothing here can check it; only a person looking
can. Hence the date above.

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
