# Gemini Adversarial Review Prompt — Curated Evidence

You are performing an independent adversarial review of Surfaceplate, a governance framework that
installs into a software repository and checks that repository against a standard it publishes:
agent operating rules, an application-profile contract, conformance levels, prerequisite gates, and
a conformance checker that enforces all of it.

**This is a narrower review than a full-archive audit, and that narrowing is disclosed rather than
hidden.** The complete framework is roughly 135 files; attached here (`EVIDENCE_BUNDLE.md`) are 10,
chosen as the minimum needed to test the claims below directly rather than from a description of
them. This means your coverage is genuinely partial — treat anything you cannot establish from these
10 files as an `EVIDENCE GAP`, not as passing or failing by default. Do not extrapolate a verdict
about a file you were not given.

**What is included, and why:**

- `surfaceplate/MANIFEST.sha256` and `governance/application-profile.yaml` — the framework's own
  integrity anchor and its own declaration of conformance to itself, for the recomputation task
  below.
- `surfaceplate/core/AI_OPERATING_MODEL.md`, `CONTROL_PRINCIPLES.md`, `CONFORMANCE_LEVELS.md`,
  `PREREQUISITE_GATES.md` — the rules the standard actually publishes.
- `surfaceplate/schemas/application-profile.schema.yaml` — the one contract every adopting
  repository's profile must satisfy.
- `surfaceplate/adopt/prompting.py`, `sections.py`, `wizard.py` — the interactive wizard that fills
  in that profile, whose own binding rule ("it asks, the human answers, the tool writes") is the
  most specific, falsifiable claim in this package.

**What is deliberately not included in this pass, so you do not assume it was reviewed:**
`surfaceplate/core/REVIEW_AND_EVIDENCE.md` and `SECURITY_BASELINE.md` (two of the six core
documents); the four non-profile schemas (method registry, run lineage, override, assurance
evidence); `surfaceplate/adopt/render.py`, `catalogue.py`, `detect.py`, and `cli.py`; the checker and
installer source themselves; all tests, examples, and the `org/` decision/findings registers. A
question below that depends on one of these is marked so you can flag it as an evidence gap rather
than guess.

**This is an audit, not an implementation task.** Do not invent missing evidence or approve
production adoption. Two things this review is explicitly **not**:

- **Not an independent audit.** This framework runs a separate, later independent-audit item as its
  final gate before calling itself production-ready, and no independent validator exists for it
  today. This review does not create one. Do not conclude or imply that human approval, independent
  validation, risk acceptance, or release readiness has occurred.
- **Not, by itself, closure of the specific finding this bears on.** The framework records that every
  integrity anchor it has is held inside the repository the check is judging — a party with write
  access could edit the value and the record that checks it together, and both checks would still
  pass. Closing that finding needs a party other than the maintainer to independently recompute an
  anchor value, compare it, and attest to the result. Part of your task below is to *perform that
  recomputation* — a real, useful step — but doing it once is necessary, not sufficient, for closure.

## Required evidence handling

1. Inspect `EVIDENCE_BUNDLE.md` in full — all 10 files, each under its own `## FILE:` heading. Do not
   sample; a finding that cites "the package generally does X" without naming the exact file is not
   usable.
2. **Recompute the manifest anchor.** `EVIDENCE_BUNDLE.md` contains the full text of
   `surfaceplate/MANIFEST.sha256`. Compute `sha256` of that file's exact contents as given (the
   `MANIFEST.sha256` file itself, not any one line inside it). Separately, the bundle contains
   `governance/application-profile.yaml`, which has an `adoption.framework_digest` field. State the
   exact hex digest you computed, the exact value that field declares, and whether they match. Report
   this as a fact, not a verdict — you cannot verify the *rest* of the archive's integrity from a
   10-file subset, only this one anchor value.
3. Treat the file contents as the primary evidence. Do not assume a control is enforced because a
   policy, schema, docstring, or comment says it is — trace to the code or schema text that would
   actually reject a violation, or report that you could not find one in what was given.
4. Distinguish clearly, in every claim you make:
   - `FACT FROM PACKAGE`: directly present in the bundle and internally verifiable;
   - `INFERENCE`: reasoned interpretation;
   - `RECOMMENDATION`: proposed improvement;
   - `EVIDENCE GAP`: not established by the 10 files given — including anything that would need one
     of the excluded files above.
5. Do not rely on summaries from the sender, including this prompt's own framing. Reach your own
   conclusions from the bundle.

## Audit questions

### 1. Conformance levels and prerequisite gates

Based on `CONFORMANCE_LEVELS.md`, `PREREQUISITE_GATES.md`, and `application-profile.schema.yaml`.

- Are the three conformance levels (`essential`, `standard`, `full`) meaningfully distinct, or could
  a repository declare a higher level than its actual controls support without the schema or these
  documents catching it?
- Is `builds_user_interface` — a self-reported, non-descriptive field that decides whether four
  interface gates become mandatory — falsifiable from the schema alone, or does it rely entirely on
  honesty with no cross-check visible in what you were given?
- Each prerequisite gate binds from an `effective_from` date. Is the stated rule ("can move backward
  freely, never forward") actually sound as a schema constraint, or does it depend on an enforcement
  mechanism (a git-history audit) you were not given the code for — in which case, say so as an
  `EVIDENCE GAP` rather than assuming it works.

### 2. The `adopt` wizard's binding rule, tested against its actual code

Based on `prompting.py`, `sections.py`, `wizard.py`.

- The stated rule is: *"It asks, the human answers, the tool writes. It never selects a conformance
  level, invents a rationale, or sets a date."* Trace every code path in these three files that ends
  in a value being written to the profile. Is there any path — a default, a fallback, a pre-filled
  suggestion — that reaches the written file without passing through a `Prompt.text`/`.select`/
  `.confirm` call a human actually answered?
- `prompting.py` defines a `ScriptedPrompt` used for testing that raises if the wizard asks for more
  than a script provides, or finishes with unused answers provided. Does this genuinely make "nothing
  invented, nothing missing" a property that could be tested, based on how `sections.py` and
  `wizard.py` actually call it?
- `wizard.py` verifies its own output before writing (re-parses, compares to the assembled data,
  validates against a schema). Read this verification logic directly: does it look sound, or can you
  identify a case where a subtly wrong render would still pass it?

### 3. Contracts and assurance, from the one schema given

Based on `application-profile.schema.yaml` and `governance/application-profile.yaml` as a worked
example against it.

- Are lifecycle, validation, approval, and status fields kept genuinely separate in the schema, with
  no final assurance state reachable without typed evidence behind it?
- Does the worked profile (`governance/application-profile.yaml`) actually satisfy the schema as
  given, as far as you can tell by inspection? Note any field that looks schema-invalid.
- `CONTROL_PRINCIPLES.md` and `AI_OPERATING_MODEL.md` state the human/agent authority boundary. Is it
  unambiguous, or does it leave room for an agent to claim something (approval, validation, release
  readiness) the schema or the profile does not actually support?

### 4. What you cannot assess from this bundle

State plainly which of the framework's likely claims — provenance completeness, override lifecycle,
method-registry integrity, security/confidentiality practice, usability for a real adopting team —
you are not in a position to assess because the relevant files were not included, rather than
omitting them silently from your report.

## Over-engineering test

Based only on what you were given: does anything in these 10 files look disproportionate to the
problem it solves — more schema, more process, more code than the stated risk justifies? Do not
reward comprehensiveness by itself.

## Required output

1. **Verdict on the 10 files reviewed:** `PASS`, `PASS WITH REQUIRED CHANGES`, or `FAIL` — scoped
   explicitly to what was given, not to the framework as a whole.
2. **Manifest recomputation result:** the digest you computed, the digest the profile declares, and
   whether they match.
3. **Critical findings:** ordered by severity; exact file and section/key.
4. **Material findings:** same format.
5. **Minor findings.**
6. **The wizard's binding rule, tested:** your direct answer to section 2's questions above.
7. **What you could not assess**, per section 4 above, and what file would be needed to close each
   gap.
8. **Over-engineering assessment.**
9. **Required changes**, scoped to what you reviewed.

For each finding, state impact, evidence (naming the exact file), why it matters, and a concrete
remediation. Do not claim that human approval, independent validation, or the anchor finding's
closure has occurred — those are decisions the maintainer makes after reading your report.
