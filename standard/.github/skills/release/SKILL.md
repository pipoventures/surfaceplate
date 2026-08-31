---
name: release
description: "Prepare a release candidate under Surfaceplate: evidence, versioning, changelog, and traceability. Never authorises the release."
---

# Release

Use when preparing a version for release, tagging, or promotion to a controlled environment.

**Read this first:** this skill *prepares* a release. It does not *authorise* one. Release
authorisation is a human decision by the accountable owner, and cannot be inferred from green
checks.

## Required inputs

- the target version and the versioning scheme in use;
- the commit range since the previous release;
- the release type — patch, minor, major, or methodology-affecting;
- the environment being promoted to;
- who the accountable release approver is.

## Workflow

1. **Establish the change set.** List every commit and pull request since the last release. Map each
   to a register entry. Unregistered changes in a release are a finding.
2. **Classify the release.** If any included change is output-affecting, methodology-affecting, or
   contract-breaking, the release inherits that classification and the corresponding approval
   requirement.
3. **Check every included change is complete** — reviewed, tested, documented, and with its
   required human decisions actually obtained. A change carrying an outstanding approval blocks the
   release.
4. **Determine the version number** from the change set, not from habit. Breaking contract change
   means a major increment.
5. **Update the changelog** — user-visible changes, breaking changes, deprecations, security fixes,
   and known issues. Check the file's existing ordering convention before editing it.
6. **Run the full verification suite** — tests, contract conformance, lint, type, build, security
   scan, and any reproducibility or golden checks. Record every command and its result.
7. **Verify reproducibility** where the repository claims it: a clean build from the tagged source
   must produce the same outputs.
8. **Assemble the evidence pack**: version, commit SHA, change set with register IDs, all
   verification results, security scan results, known issues and their risk position, output deltas,
   and the outstanding approvals.

## Gates

- every included change is registered, reviewed, and has its required approvals;
- version number justified by the change set;
- changelog complete and accurate;
- full verification suite green, with output captured;
- security scan clean of new high or critical findings;
- reproducibility verified where claimed;
- artefact digests recorded where artefacts are published.

## Mandatory stops

Always stop for human decision before:

- creating a tag, publishing an artefact, or promoting to a controlled environment;
- releasing with any known defect, open finding, or unresolved approval;
- any release classified as output- or methodology-affecting;
- a breaking contract change;
- rolling back or superseding a previously released version.

## Completion report

Report: the proposed version and why; the full change set with register IDs; every verification
command and its result; the security position; known issues; the output delta or an explicit
statement that outputs are unchanged; and — stated plainly — the named approvals that are still
required before this can be released.

Never state that a release is approved, signed off, or production-ready.
