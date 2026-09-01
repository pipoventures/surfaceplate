# Cross-provider adversarial review — received 2026-09-01

`RELEASE_PLAN` item 9, first pass. The packet sent was
`GEMINI_ADVERSARIAL_REVIEW_PROMPT_CURATED.md` at `ACT-037` plus an 11-file `EVIDENCE_BUNDLE.md`.

**This file is the review as delivered.** It is evidence, not authority: the verdict is the
reviewer's, and what was done about it is recorded separately in `DR-46` with each finding accepted
or rejected on its own merits. Nothing here is edited, including the parts that turned out to be
wrong.

**Read `DR-46` before acting on anything below.** Three findings were verified and acted on, one was
right about the risk and wrong about the evidence, one is a judgement, and the report's most
consequential sentence is the reviewer's disclosure that it could not perform the one computational
task the packet asked for.

---

## 1. Verdict on the 11 files reviewed

`FAIL`. The framework explicitly violates its own core binding rule by having the code silently
invent configuration data on behalf of the user, and its normative documents contain direct
structural contradictions regarding whether controls are verified by machine or declared by trust.

## 2. Manifest recomputation result

The profile declares the framework digest as
`f161a7d66ebeab0907afd84938f8946082e9832fca122b5b2e98dca6e94059c5`. The framework's
`governance/application-profile.yaml` explicitly discloses the lag property, stating that for the
publisher's self-installation, "the value below can never equal sha256 of the CURRENT
MANIFEST.sha256" and that this is "the publisher's self-installation showing through". The final
comparison between the independently computed digest and the declared digest is located at the very
end of this report.

## 3. Critical findings

- **File:** `surfaceplate/adopt/sections.py`
- **Impact:** Violates the core integrity claim of the tool.
- **Evidence:** `GEMINI_ADVERSARIAL_REVIEW_PROMPT_CURATED.md` states the rule is "It never... sets a
  date." However, `sections.py` contains
  `"effective_from": answers.get("effective_from") or _dt.date.today().isoformat()`, silently
  overriding the human by inserting the current date if an answer is missing.
- **Why it matters:** The framework advertises that the tool never invents facts or dates. The
  implementation actively sets a date without a human prompt, proving the stated security bound is
  false.
- **Remediation:** Remove the `or _dt.date.today().isoformat()` fallback. The tool must enforce a
  human answer or leave the field empty.

## 4. Material findings

- **File:** `surfaceplate/core/CONFORMANCE_LEVELS.md`
- **Impact:** Creates ambiguous authority and false confidence for adopters.
- **Evidence:** The document states `agent_work_packets` and `actual_diff_review` are "declarations
  that nothing checks". Later in the exact same document, it states "Every control this framework
  defines is now checked... Nothing is declared-only".
- **Why it matters:** A governance standard cannot simultaneously claim absolute structural
  enforcement and honor-system enforcement for its baseline controls.
- **Remediation:** Remove the contradictory absolute claim and clarify which specific controls remain
  declarations.

- **File:** `surfaceplate/adopt/scaffold.py`
- **Impact:** Bypasses prerequisite gates.
- **Evidence:** The module automatically writes empty files like `CHANGELOG.md` to disk, which
  immediately satisfies the checker.
- **Why it matters:** Creating an empty file to clear a gate (`SP032`) defeats the purpose of the
  gate, equating the creation of a blank template with the actual adoption of a practice.
- **Remediation:** Do not offer to auto-create empty governance artifacts strictly to pass structural
  checks.

## 5. Minor findings

- **File:** `surfaceplate/adopt/sections.py`, `defaults.py`, `wizard.py`
- **Impact:** Code maintainability risk.
- **Evidence:** The Python files contain extensive narrative essays detailing project management
  history, such as references to `DR-36`, `ACT-032`, and `F40`.
- **Why it matters:** Docstrings should describe what the code does, not act as a historical decision
  register. These comments will rapidly drift from the codebase.
- **Remediation:** Move historical rationales out of the source code and into the actual decision
  logs.

## 6. The binding rule, tested

`FACT FROM PACKAGE`: The code **fails** the stated rule. While `defaults.py` correctly frames origins
as proposals needing approval, `sections.py` fundamentally breaks the rule by injecting
`DERIVED_ENFORCEMENT` and `_dt.date.today().isoformat()` into the profile without an explicit answer.
Furthermore, `scaffold.py` actively creates repository artifacts on behalf of the user to force a
passing state.

## 7. The framework against its own standard

`INFERENCE`: The framework's own profile (`governance/application-profile.yaml`) accurately documents
its exclusions and defers items that do not apply to it. However, the profile does not cleanly
distinguish declared controls from verified controls. Both `actual_diff_review` (which is
declared-only) and `dependency_lock` (which is checked) appear as structurally identical YAML objects
in the `baseline_controls` and `control_decisions` blocks. An adopter reading this file cannot discern
which controls are genuinely enforced by the machine without referencing external documentation.

## 8. What you could not assess

- **Enforcement logic:** `EVIDENCE GAP` regarding how the checker actually enforces the rules,
  because `check_conformance.py` was not provided.
- **Interactive TUI:** `EVIDENCE GAP` regarding the user interface because `cli.py` and the `tui/`
  directory were omitted.
- **Audit history and security tools:** `EVIDENCE GAP` regarding the git-history audit and the
  security baseline scanning capabilities, as I lack the execution environment and required files to
  test them.

To close these gaps, the complete source code for the checker, TUI, and test suites must be provided.

## 9. Over-engineering assessment

`INFERENCE`: The framework exhibits significant over-engineering in its narrative density. The Python
files (`sections.py`, `scaffold.py`, `wizard.py`) contain exhaustive, multi-paragraph essays
defending their own design choices rather than documenting logic. Additionally, `scaffold.py`
represents process over-engineering: building a complex module to inject empty text files into a
repository simply to satisfy a rigid structural checker is disproportionate to the actual risk.

## 10. Required changes

- `RECOMMENDATION`: Remove the automatic date generation (`_dt.date.today().isoformat()`) and default
  enforcement injection in `sections.py`.
- `RECOMMENDATION`: Reconcile the contradictions in `CONFORMANCE_LEVELS.md` regarding which controls
  are structurally verified.
- `RECOMMENDATION`: Strip the historical `DR-*` and `ACT-*` essays from the Python docstrings.

To independently verify the manifest digest, the SHA-256 hash of the full `MANIFEST.sha256` text
block must be calculated step-by-step. Because I operate as an AI text model without a native
cryptographic code execution environment, I am unable to mathematically compute the raw SHA-256 byte
digest of the provided text file. Consequently, I cannot establish whether the computed digest and
the declared digest match.
