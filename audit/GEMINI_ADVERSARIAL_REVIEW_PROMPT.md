# Gemini Adversarial Review Prompt

You are performing an independent adversarial review of the complete ZIP attached to this message:
`surfaceplate-0.16.0.zip`. This is the first review this framework has ever asked of your provider.

## Objective

Surfaceplate is a governance framework that installs into a software repository and checks that
repository against a standard it publishes: agent operating rules, an application-profile contract,
conformance levels, prerequisite gates, and a conformance checker that enforces all of it. Assess
whether the framework is internally sound, honestly represented, and safe to install into a real
repository — and find what its own authors, having built it, are the wrong party to find.

**This is an audit, not an implementation task.** Do not modify the ZIP, invent missing evidence, or
approve production adoption. Two things this review explicitly is **not**, stated here so your report
does not overclaim either by accident:

- **Not an independent audit.** `org/RELEASE_PLAN.md` runs two separate items: a cross-provider
  adversarial review (this one), and a later, separate independent audit that is the framework's
  *final* gate before calling itself production-ready. `org/decisions/README.md` states plainly that
  no independent validator, technical reviewer, or release authority exists for this repository
  today. This review does not create one. Do not conclude or imply that human approval, independent
  validation, risk acceptance, or release readiness has occurred.
- **Not, by itself, closure of the finding this review most directly bears on.** `org/FINDINGS.md`'s
  `F6` records that every integrity anchor in this framework is held inside the repository the check
  is judging — a party with write access could edit the value and the record that checks it together,
  and both checks would still pass. Closing `F6` needs a party other than the maintainer to
  independently recompute an anchor value, compare it, and attest to the result. Part of your task
  below is to *perform that recomputation* — a real, useful step — but recomputing one value is
  necessary, not sufficient, for closure: the attestation and what it establishes is a human decision
  the maintainer makes afterward, not a status your report can confer on its own.

## Required evidence handling

1. Inspect the complete ZIP: every file, the directory structure, schemas, templates, examples,
   adapters, source code, tests, and audit materials. Do not sample — a finding that cites "the
   package generally does X" without a path is not usable.
2. **Recompute the manifest anchor.** The archive contains `surfaceplate/MANIFEST.sha256`, a file
   listing the SHA-256 of every payload file. Compute `sha256(MANIFEST.sha256)` yourself, from the
   bytes as they exist inside the ZIP. Separately, the archive's repository root contains
   `governance/application-profile.yaml` — this framework's own profile for itself — with an
   `adoption.framework_digest` field. State the exact hex digest you computed, the exact value that
   field declares, and whether they match. This is the `F6` recomputation described above; report it
   as a fact, not a verdict on the finding.
3. Verify the SHA-256 manifest itself against the ZIP's own central-directory entry names. Entry
   names must use POSIX `/` separators and must reconstruct the documented directory tree on both
   POSIX and Windows. Report any missing file, extra file, checksum mismatch, path ambiguity, or
   packaging defect.
4. Treat the package contents as the primary evidence. Do not assume a control is enforced because a
   policy, schema, docstring, or comment says it is — trace to the code or the schema that would
   actually reject a violation, or report that you could not find one.
5. Distinguish clearly, in every claim you make:
   - `FACT FROM PACKAGE`: directly present and internally verifiable;
   - `INFERENCE`: reasoned interpretation;
   - `RECOMMENDATION`: proposed improvement;
   - `EVIDENCE GAP`: not established by the package.
6. **The ZIP contains no `.git` history and no CI run** — `scripts/build_release.py` excludes both
   deliberately. It cannot itself prove that a test suite ran, that a check passed on a real commit,
   or what the git history behind a claim looks like. `audit/AUDIT_README.md` (inside the archive)
   names what to ask the sender for beyond the ZIP if you need it: the five test suites' own reported
   check counts, `python scripts/build_release.py --verify-manifest`,
   `python surfaceplate/check_conformance.py --repo .`, and the CI run for the commit under review,
   read **per step** rather than by rollup status (a step that never ran reports `skipped`, which is
   not the same as a pass — `org/FINDINGS.md`'s `F13`). If something in your review depends on this
   and you were not given it, say so as an `EVIDENCE GAP` rather than assuming either outcome.
7. Do not rely on summaries from the sender, including this prompt's own framing above. Inspect the
   actual files and reach your own conclusions.

## Audit questions

### 1. Operating model and human/agent authority boundary

Read `surfaceplate/core/AI_OPERATING_MODEL.md`, `surfaceplate/core/CONTROL_PRINCIPLES.md`, and
`surfaceplate/core/REVIEW_AND_EVIDENCE.md`.

- Does the operating model define bounded work, acceptance criteria, ownership, escalation, and
  completion evidence clearly enough to follow without a governance specialist?
- Are agent capabilities and human-only decisions unambiguous and non-contradictory?
- Does it actually prevent an agent from fabricating approval, risk acceptance, independent
  validation, release readiness, or an external control's status — or only ask the agent not to?
- Are actual diffs, tests, runtime behaviour, failures, warnings, and limitations required as
  evidence, or is a narrative summary treated as sufficient anywhere?

### 2. Tool neutrality and reuse

- Can the core rules (`surfaceplate/core/`) be used for a stack other than Python without changing
  their meaning? Is anything stack-specific leaking out of `surfaceplate/adapters/`?
- Are there hidden assumptions specific to *this repository being the framework's own publisher* —
  places where the standard's own self-adoption shaped a rule in a way that would not generalise to
  an adopting application?
- Does the package avoid prescribing microservices, plugins, workflow engines, graph databases, or
  infrastructure disproportionate to what it governs?

### 3. Conformance levels and prerequisite gates

Read `surfaceplate/core/CONFORMANCE_LEVELS.md` and `surfaceplate/core/PREREQUISITE_GATES.md`, and
`surfaceplate/schemas/application-profile.schema.yaml`.

- Are the three conformance levels (`essential`, `standard`, `full`) meaningfully distinct, or could
  a repository declare a higher level than its actual controls support without the checker noticing?
- Is `builds_user_interface` — a self-reported, non-descriptive field that decides whether four
  interface gates are mandatory — falsifiable in practice, or does it rely entirely on honesty with
  no cross-check?
- The 19 prerequisite gates each bind from an `effective_from` date that can move backward freely but
  never forward (`SP034`, stated as never graced). Is that asymmetry actually sound, or does it create
  a gaming path — e.g. adopting a gate with an `effective_from` set unrealistically far in the past,
  or far in the future, to change what history counts?
- `surfaceplate/check_conformance.py` checks each control by one of a small number of patterns —
  presence of a named file, presence of a named CI step by name, or an empty-or-valid register
  directory. Could a repository satisfy any of these patterns' letter while violating what the
  control is actually meant to guarantee — for instance, naming a CI step that exists but does not
  run the check it is supposed to represent, or naming a scanner workflow file that never actually
  executes on a real trigger?

### 4. The `adopt` wizard's binding rule, adversarially tested against the code

Read `surfaceplate/adopt/` in full — `sections.py`, `defaults.py`, `scaffold.py`, `wizard.py`,
`plan.py`, `render.py`, `discover.py`, `catalogue.py`, `interview.py`, the `tui/` package — and
`surfaceplate/cli.py`.

- `org/RELEASE_PLAN.md` states the wizard's rule as: *"It asks, the human answers, the tool writes.
  It never selects a conformance level, invents a rationale, or sets a date."* Trace every code path
  that ends in a value being written to the profile. Is there any path — a default, a discovered
  value, a proposed one, a fallback — that reaches the written file without a human having answered
  for it?
- **`defaults.py` proposes values and `scaffold.py` creates files inside the adopting repository.**
  These are the two places the rule is most likely to fail, and both are recent. `defaults.py`
  claims three honest origins and claims that a field with no honest source is left unanswered and
  still asked; `scaffold.py` claims it may create and may never replace. Test both claims against
  the code rather than the docstrings.
- `interview.py` defines `ScriptedInterview`, used by the test suite, which raises if the wizard
  asks for a field the script has no answer for **or** finishes with answers nothing asked for.
  Does that actually make "nothing invented, nothing missing" a property the tests can fail on? Note
  that its predecessor did **not**: the framework records that the earlier `ScriptedPrompt` "only
  objects to a call it wasn't given an answer for, never to a value written without any call", which
  is how a real defect passed a full suite. Is the current mechanism actually free of that flaw, or
  does it inherit a version of it?
- `wizard.py` verifies its own rendered output before writing: re-parses the YAML, compares it to the
  assembled dict, validates against the schema, scans for placeholder tokens. Could a renderer bug
  produce output that is semantically wrong but still round-trips identically through this check —
  for example, a YAML representation that reparses to an equal Python value while meaning something
  different to a strict reader, or a value silently coerced to the wrong type?
- `pyproject.toml` declares `questionary` as an optional extra (`[project.optional-dependencies]
  adopt`) rather than a hard dependency, on the stated reasoning that the CI workflow this project
  installs into adopting repositories never runs `adopt`. Is that reasoning sound, and does the code
  in `cli.py` actually degrade cleanly (a clear message, not a traceback) if the extra is missing?

### 5. Contracts, provenance, and assurance

Read `surfaceplate/schemas/` in full and `surfaceplate/examples/`.

- Are lifecycle, validation, approval, execution, and retirement statuses kept genuinely separate,
  with no final assurance state reachable without typed evidence behind it?
- Are provenance fields conditionally sufficient for completed, material, and AI-assisted runs —
  input/config/code/output identity, and AI provider/model/prompt version where relevant?
- Are override approval, expiry, rollback, before/after values, materiality, and evidence
  requirements enforceable by the schema, or dependent on a human process the schema cannot check?
- `org/decisions/DR-25.md` and `DR-26.md` (inside `org/decisions/`) describe a deliberate choice that
  an *empty* record register (for `overrides`, `method_registry`, `run_lineage`, `provenance`) passes
  conformance, on the reasoning that requiring at least one record would incentivise fabricating one.
  Test this directly: does that design actually prevent fabrication, or does it just move the
  fabrication risk to "declare the control, never file a record, pass forever"? Is that cost stated
  honestly in the documents that make the choice?

### 6. Usability and maintainability

- Could a small team adopt and understand this without a governance specialist?
- Are the templates in `surfaceplate/templates/` concise enough for routine work, or do they demand
  more ceremony than the risk they govern justifies?
- Are naming, status vocabularies, and schema conventions consistent across `surfaceplate/schemas/`,
  `surfaceplate/core/`, and the checker's own finding codes?
- Is there any duplicated or contradictory authority — two documents that could each be read as
  governing the same question, with no stated precedence?

### 7. Security and confidentiality

- Does the package avoid secrets, credentials, tokens, real customer data, or private URLs anywhere,
  including in tests, fixtures, and worked examples?
- Are dependency and supply-chain controls (`pyproject.toml`'s exact pins, the dependency-lock
  control) sufficiently specified for a package other repositories install?
- Is anything in `surfaceplate/adopt/` or `surfaceplate/cli.py` a plausible injection or path-handling
  risk — for instance, how gate paths, precondition artefacts, or CI step names typed by a human
  during `adopt` are later used by the checker?

## Over-engineering test

Explicitly identify anything that should be removed, deferred, or simplified. Do not reward
comprehensiveness by itself — evaluate whether each element reduces a real risk this framework
actually faces, or exists because it was possible to build.

## Required output

Return a report with these sections:

1. **Verdict:** `PASS`, `PASS WITH REQUIRED CHANGES`, or `FAIL`.
2. **Manifest recomputation result:** the digest you computed, the digest the profile declares, and
   whether they match — stated as fact, per "Required evidence handling" item 2 above.
3. **Critical findings:** ordered by severity; exact package path and section/key where possible.
4. **Material findings:** same format.
5. **Minor findings and usability issues.**
6. **Contradictions or ambiguous authority.**
7. **Controls that are only documented versus structurally represented versus automatically
   enforceable versus human-process dependent** — for every control this framework defines, not a
   sample.
8. **The wizard's binding rule, tested:** your direct answer to section 4's questions above — does
   the code enforce "it asks, the human answers, the tool writes," or only assert it?
9. **Assessment against `audit/AUDIT_SCOPE.md`'s declared scope** (inside the archive) — one row per
   criterion it lists, scored and justified, in the same spirit as this repository's own
   `audit/PRE_AUDIT_FINDINGS_0.6.0.md` did for an earlier version of the package.
10. **Over-engineering assessment.**
11. **Required changes before this can be considered for real adoption.**
12. **Recommended changes that may wait.**
13. **Evidence gaps** — anything you could not establish from the package alone, and what you would
    need to establish it.
14. **File-by-file audit coverage statement** — what you read, and what (if anything) you did not.

For each finding, state impact, evidence, why it matters, and a concrete remediation. Do not rewrite
the package. Do not claim that human approval, independent validation, or `F6`'s closure has
occurred — those are decisions the maintainer makes after reading your report, not conclusions this
review can reach on its own.
