# Cross-Provider Adversarial Review Prompt — Curated Evidence

You are performing an independent adversarial review of Surfaceplate, a governance framework that
installs into a software repository and checks that repository against a standard it publishes:
agent operating rules, an application-profile contract, conformance levels, prerequisite gates, and
a conformance checker that enforces all of it.

**This is a narrower review than a full-archive audit, and that narrowing is disclosed rather than
hidden.** The complete framework is roughly 170 files; attached here (`EVIDENCE_BUNDLE.md`) are 15,
chosen as the minimum needed to test the claims below directly rather than from a description of
them. Your coverage is genuinely partial — treat anything you cannot establish from these 15 files
as an `EVIDENCE GAP`, not as passing or failing by default. Do not extrapolate a verdict about a
file you were not given.

**What is included, and why:**

- `surfaceplate/MANIFEST.sha256` and `governance/application-profile.yaml` — the framework's own
  integrity anchor and its own declaration of conformance to itself, for the recomputation task
  below.
- `surfaceplate/core/AI_OPERATING_MODEL.md`, `CONTROL_PRINCIPLES.md`, `CONFORMANCE_LEVELS.md`,
  `PREREQUISITE_GATES.md` — the rules the standard actually publishes.
- `surfaceplate/schemas/application-profile.schema.yaml` — the one contract every adopting
  repository's profile must satisfy.
- `surfaceplate/adopt/sections.py`, `defaults.py`, `scaffold.py`, `wizard.py` — the four files where
  the framework's most specific and most falsifiable claim is either kept or broken. That claim is
  *"it asks, the human answers, the tool writes"*, and each of these stresses it differently:
  `sections.py` assembles every value that reaches the profile, `defaults.py` **proposes** values,
  `scaffold.py` **creates files inside the adopting repository**, and `wizard.py` verifies the result
  before anything is written.
- `surfaceplate/seeds/*` — **the four documents `scaffold.py` actually writes.** These are included
  because the previous pass of this review asked whether creating an artefact makes a gate pass
  while the practice does not exist, and did **not** attach the artefacts. The reviewer reasonably
  inferred they were empty files. They are not, and the question cannot be answered without reading
  them: judge the claim on the text, not on the module that copies it.

**What is deliberately not included, so you do not assume it was reviewed:**
`surfaceplate/core/REVIEW_AND_EVIDENCE.md` and `SECURITY_BASELINE.md`; the four non-profile schemas
(method registry, run lineage, override, assurance evidence); the rest of the wizard
(`plan.py`, `render.py`, `discover.py`, `catalogue.py`, `interview.py`, `cli.py`, and the whole
`tui/` interaction layer); **the checker and installer source, which are the largest omission in this
bundle**; all tests, examples, and the `org/` decision and findings registers. Several questions
below turn on the checker's behaviour and are marked so you can flag them as evidence gaps rather
than guess.

**This is an audit, not an implementation task.** Do not invent missing evidence or approve
production adoption. Three things this review is explicitly **not**:

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
- **Not a first look at some of this code.** A same-provider model reviewed `scaffold.py` and its
  wiring shortly before this packet was written, and found three high-severity defects, all since
  fixed. That is disclosed for two reasons: so you do not spend effort re-deriving what is already
  remedied, and — more importantly — so **neither you nor the maintainer treats that review as
  reducing the need for this one.** Two models from the same provider share training lineage and
  therefore blind spots; that is the entire reason this cross-provider pass exists. If you find
  something in that file, the fact that another model looked first is evidence for this exercise,
  not against your finding.

## Required evidence handling

1. Inspect `EVIDENCE_BUNDLE.md` in full — all 15 files, each under its own `## FILE:` heading. Do
   not sample; a finding that cites "the package generally does X" without naming the exact file is
   not usable.
2. **The manifest anchor — attempt this ONLY if you can execute code.** The previous pass of this
   review could not, and said so honestly: *"I am unable to mathematically compute the raw SHA-256
   byte digest."* That was the correct answer and it cost nothing; what cost something was this
   prompt asking for it as though a text-only reviewer could comply.

   **If you have a code execution tool:** compute `sha256` of `surfaceplate/MANIFEST.sha256`'s exact
   contents as given (the file itself, not any line inside it), and compare with the
   `adoption.framework_digest` field in `governance/application-profile.yaml`. State both values and
   whether they match.

   **If you do not:** report it as an `EVIDENCE GAP` in one line and move on. Do not attempt it by
   hand, do not estimate, and do not report a digest you did not compute. A fabricated hash in an
   integrity review is worse than an admitted gap, and this framework's own findings register exists
   because of failures of exactly that shape.
   **Report this as a fact, not a verdict.** Two cautions the maintainer would rather you had than
   not: you cannot verify the rest of the archive from a 15-file subset, only this one value; and
   this field is known to lag by one edit cycle, because the profile is itself inside the manifest
   it names the digest of. A mismatch here is expected and is not by itself a finding — **what is
   worth reporting is whether the framework's own documents disclose that property or quietly rely
   on it.**
3. Treat the file contents as the primary evidence. Do not assume a control is enforced because a
   policy, schema, docstring, or comment says it is — trace to the code or schema text that would
   actually reject a violation, or report that you could not find one in what was given. **This
   codebase has unusually long explanatory comments and docstrings, several of which describe
   defects that were fixed. Do not accept them as evidence of current behaviour; they are claims
   like any other, and at least one of them has previously been wrong about the code beneath it.**
4. Distinguish clearly, in every claim you make:
   - `FACT FROM PACKAGE`: directly present in the bundle and internally verifiable;
   - `INFERENCE`: reasoned interpretation;
   - `RECOMMENDATION`: proposed improvement;
   - `EVIDENCE GAP`: not established by the 15 files given — including anything that would need one
     of the excluded files above.
5. Do not rely on summaries from the sender, including this prompt's own framing. Reach your own
   conclusions from the bundle.

## Audit questions

### 1. Conformance levels and prerequisite gates

Based on `CONFORMANCE_LEVELS.md`, `PREREQUISITE_GATES.md`, and `application-profile.schema.yaml`.

- Are the three conformance levels (`essential`, `standard`, `full`) meaningfully distinct, or could
  a repository declare a higher level than its actual controls support without the schema or these
  documents catching it?
- `builds_user_interface` is a self-reported, non-descriptive field that decides whether four
  interface gates become mandatory. Is it falsifiable from the schema alone, or does it rely
  entirely on honesty with no cross-check visible in what you were given?
- **`effective_from` now accepts either a date or a full instant, and this is the newest change in
  the bundle.** The schema constrains it with a regular expression rather than a `format` keyword.
  Read that pattern directly and state what it does and does not admit. Then consider the interaction
  the maintainer believes is closed: the rule *"can move backward freely, never forward"*, the rule
  that a gate may not be dated in the future, and a repository adopting midway through a working day.
  Is that set of rules jointly satisfiable as stated in `PREREQUISITE_GATES.md`? The enforcement is
  in the checker, which you were **not** given — so say what the documents and schema commit to, and
  mark the enforcement itself as an `EVIDENCE GAP`.

### 2. The binding rule, tested against the code that can break it

Based on `sections.py`, `defaults.py`, `scaffold.py`, `wizard.py`.

The stated rule is: *"It asks, the human answers, the tool writes. It never selects a conformance
level, invents a rationale, or sets a date."* Three of these files exist in tension with it.

- **`sections.py`** assembles every value that reaches the written profile. Trace each function that
  returns a profile fragment. Is there any value written that does not come from an answer — and for
  each one you find, is it a fact about the framework (a version, a schema constant, a published
  sentence) or a judgement about the adopter? The distinction is the framework's own defence; test
  whether it holds.
- **`defaults.py` proposes values, which is the sharpest tension with the rule.** It claims exactly
  three honest origins — `discovered` (read from the repository), `example` (prose the framework
  ships), `computed` (derived from a fact) — and claims that a field with no honest source is left
  unanswered and still asked. Verify both halves against the code. Is there any path by which a
  proposal becomes a written value without a human passing a screen? Note that the screens are **not**
  in this bundle, so the second half of that question is partly an evidence gap: say what the code
  guarantees on its own.
- **`scaffold.py` writes files into the adopting repository**, which is a different class of action
  from filling in a profile and is the newest capability here. Attack it: can it overwrite anything,
  follow a symlink out of the repository, be induced to write outside the repository tree, or leave
  partial state behind on failure? Separately and more importantly — **it creates a governance
  artefact that a gate then points at. Does creating the artefact make the gate pass while the
  practice the gate stands for does not exist?** The framework claims three mitigations for exactly
  this; find them and say whether they are sufficient or cosmetic.
- **`wizard.py`** verifies its own output before writing (re-parses, compares to the assembled data,
  validates against a schema, scans for placeholder tokens). Read that logic directly: is it sound,
  or can you identify a case where a subtly wrong render would still pass it? Note in particular what
  it does **not** check about the values it is about to write.

### 3. Contracts and assurance, from the one schema given

Based on `application-profile.schema.yaml` and `governance/application-profile.yaml` as a worked
example against it.

- Are lifecycle, validation, approval, and status fields kept genuinely separate in the schema, with
  no final assurance state reachable without typed evidence behind it?
- Does the worked profile actually satisfy the schema as given, as far as you can tell by inspection?
  Name any field that looks schema-invalid.
- `CONTROL_PRINCIPLES.md` and `AI_OPERATING_MODEL.md` state the human/agent authority boundary. Is it
  unambiguous, or does it leave room for an agent to claim something — approval, validation, release
  readiness — that the schema or the profile does not actually support?

### 4. The framework judged against its own standard

This framework publishes rules and installs them into itself. Using only the bundle:

- Pick two or three of the strongest claims in the core documents and check them against
  `governance/application-profile.yaml`. Does the framework's own profile satisfy the rules it
  publishes for others, or is there a claim it makes that it does not itself meet?
- The core documents repeatedly distinguish "declared" from "verified". Reading the worked profile,
  can you tell which of its controls are actually verified by machine and which are declarations
  trusted on the adopter's word? If that distinction is not visible from the profile itself, say so —
  an adopter reading their own profile is the person most likely to over-read it.

### 5. What you cannot assess from this bundle

State plainly which of the framework's likely claims — the checker's actual enforcement, the history
audit, provenance completeness, override lifecycle, method-registry integrity,
security/confidentiality practice, the interactive interface, usability for a real adopting team —
you are not in a position to assess because the relevant files were not included, rather than
omitting them silently from your report.

## Over-engineering test

Based only on what you were given: does anything in these 15 files look disproportionate to the
problem it solves — more schema, more process, more code, or more explanatory prose than the stated
risk justifies? Do not reward comprehensiveness by itself. **Comment specifically on the density of
narrative comments in the Python files**: they carry real history, and they are also a maintenance
surface that can drift from the code beneath them.

## Required output

1. **Verdict on the 15 files reviewed:** `PASS`, `PASS WITH REQUIRED CHANGES`, or `FAIL` — scoped
   explicitly to what was given, not to the framework as a whole.
2. **Manifest recomputation result:** the digest you computed, the digest the profile declares,
   whether they match, and whether the framework's documents disclose the lag described above.
3. **Critical findings:** ordered by severity; exact file and section/key.
4. **Material findings:** same format.
5. **Minor findings.**
6. **The binding rule, tested:** your direct answer to section 2, treating `defaults.py` and
   `scaffold.py` as the two places it is most likely to fail.
7. **The framework against its own standard:** your answer to section 4.
8. **What you could not assess**, per section 5, and what file would be needed to close each gap.
9. **Over-engineering assessment.**
10. **Required changes**, scoped to what you reviewed.

For each finding, state impact, evidence (naming the exact file), why it matters, and a concrete
remediation. Do not claim that human approval, independent validation, or the anchor finding's
closure has occurred — those are decisions the maintainer makes after reading your report.
