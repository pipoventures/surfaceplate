---
name: dependency-update
description: "Add, upgrade, or remove a dependency under Surfaceplate, with provenance, licence, and output-impact evidence."
---

# Dependency Update

Use when adding, upgrading, downgrading, replacing, or removing a third-party dependency, or when
changing a lockfile, runtime version, or base image.

## Required inputs

- the dependency, the current version, and the target version;
- the reason — new capability, security advisory, transitive requirement, or maintenance;
- whether the change is security-driven, and if so the advisory identifier;
- the registered activity ID.

## Workflow

1. **Justify the dependency.** For a new one: what does it do that existing dependencies or a small
   amount of local code cannot? Every dependency is a permanent supply-chain liability.
2. **Check provenance and health** — source repository, maintenance activity, release cadence,
   maintainer count, and whether the package name is plausibly typosquatted.
3. **Check the licence** against what this repository and its distribution model permit. An
   incompatible licence is a mandatory stop, not a judgement call.
4. **Read the changelog** between current and target. Identify breaking changes, deprecations, and
   behavioural changes. "Minor version, should be fine" is not evidence.
5. **Update the manifest and the lockfile together.** Never leave them inconsistent. Pin to an
   exact version where the ecosystem supports it.
6. **Run the security scanner** and record the before/after finding counts.
7. **Run the full suite** — dependency changes have unbounded blast radius, so focused tests are
   not sufficient.
8. **Check for output impact.** If the dependency participates in computation, rendering,
   serialisation, randomness, or number formatting, run the golden, reference, or reconciliation
   tests and report any delta.

## Gates

- manifest and lockfile updated consistently and committed together;
- licence checked and compatible;
- changelog reviewed and breaking changes addressed;
- security scan run; no new high or critical findings introduced;
- full test suite green;
- output-impact evidence produced where the dependency could affect results;
- register updated.

## Mandatory stops

- an incompatible, ambiguous, or changed licence;
- a major-version upgrade with breaking changes affecting our usage;
- any change in a material output value;
- a new high or critical vulnerability introduced;
- a dependency with no clear provenance, an unmaintained upstream, or a suspicious name;
- removing or replacing a dependency that is part of a documented methodology or control.

## Completion report

Report: the activity ID; each dependency with old and new version; the licence position; the
breaking changes identified and how they were handled; the scanner results before and after; the
full-suite result; the output delta or an explicit statement that outputs are unchanged and how
that was verified; and any human decision required.
