"""What each item the wizard asks about actually means, in two registers.

`DR-35` records why this module exists: a real, live adoption session hit both a data-loss bug
(`F36`) and a genuine fit gap — three consecutive "I don't know what this is" answers at the start
of the gate catalogue, and a wizard whose only register was terse and unexplained. The maintainer's
own correction, preserved because it is the whole design constraint this module exists to satisfy:
*"keep in mind that we need much more detail and guidance compared to the one we have for advanced
as well. don't ever think what we have now would be suitable to advance."* Both registers explain;
they differ in the vocabulary they assume, not in whether an explanation is given at all.

- **`simple`** — plain English, zero jargon, practical framing. Assumes no software-development or
  governance background. Says what a check actually verifies and, just as importantly, what it does
  *not* verify, wherever that distinction exists — an unqualified "this is checked" would overclaim
  exactly the way `core/CONFORMANCE_LEVELS.md` itself warns against.
- **`advanced`** — precise technical/software terminology. Assumes real engineering literacy, but
  not familiarity with *this framework's own* vocabulary — "prerequisite gate" is still explained,
  just in language a competent engineer reads instantly rather than needing translated.

Grounded, not invented: every `advanced` entry traces to `core/PREREQUISITE_GATES.md`,
`core/CONFORMANCE_LEVELS.md`, or `core/CONTROL_PRINCIPLES.md`. Every `simple` entry is new authoring
— none of these three documents has a plain-English register today, which the maintainer's approval
of the first worked example (`agent_work_packets`) surfaced as a real documentation gap in its own
right, not merely a wizard gap.

`tests/test_adopt.py` asserts every gate ID in `catalogue.GATE_CATALOGUE` and every control ID in
`catalogue.CONFORMANCE_LEVELS["full"]` (the union across all levels) has a non-empty entry in both
registers here — a coverage test that fails loudly on a gap, rather than a wizard that silently
falls back to no explanation for whatever was missed.
"""

from __future__ import annotations

MODES = ("simple", "advanced")

# ---------------------------------------------------------------------------------------------
# The three baseline controls — required at every level, and named `agent_work_packets`,
# `actual_diff_review`, `secret_hygiene` in that fixed order throughout this package.
# ---------------------------------------------------------------------------------------------

_BASELINE_CONTROLS: dict[str, dict[str, str]] = {
    "agent_work_packets": {
        "simple": (
            "When an AI coding assistant does work in this repository, it should be given a clear, "
            "written brief first - what to do, what not to touch, and how you'll know it's done - "
            "rather than a vague, open-ended instruction. This control is your repository saying "
            "\"yes, we do that here.\" Nothing checks this automatically; it's a promise you're "
            "making, not something the tool can verify for you."
        ),
        "advanced": (
            "Every AI-assisted task is scoped by a written work packet before implementation begins "
            "- objective, explicit non-goals, bounded ownership area, acceptance criteria, required "
            "verification. Declaring this control asserts that discipline is followed; it's one of "
            "two baseline controls this framework does not verify, because doing so would mean "
            "judging the quality of human work."
        ),
    },
    "actual_diff_review": {
        "simple": (
            "When someone reviews a change before it ships, they should look at what actually "
            "changed - the real lines of code - not just a description of what the change was "
            "supposed to do. This control is your repository saying reviewers read the real diff. "
            "Like agent_work_packets, nothing checks this automatically; it's a discipline you're "
            "committing to, not something the tool can verify."
        ),
        "advanced": (
            "Every material change is reviewed against its actual diff content, not a summary, a "
            "changelog entry, or a description of intent. The other of the two baseline controls "
            "this framework does not verify - verifying it would mean the tool judging the quality "
            "of a human review, which `core/CONTROL_PRINCIPLES.md` principle 9 places outside what "
            "a tool may claim."
        ),
    },
    "secret_hygiene": {
        "simple": (
            "Secrets - passwords, API keys, tokens - should never end up committed into your "
            "repository's history, because once they are, they're effectively public even after "
            "you delete them. This control means you have an automated scanner checking every "
            "change for exactly that, wired in so it can actually stop a change, not just warn "
            "about it afterwards. This is the one baseline control the tool actually checks: it "
            "confirms a scanner is really wired in and can fail the build. It does not scan your "
            "files itself, and a pass here doesn't mean your repository has no secrets in it "
            "already - only that new ones won't slip through unnoticed."
        ),
        "advanced": (
            "A named scanner is wired into a build step capable of failing the job. The one "
            "baseline control this framework verifies rather than merely declares: `SP046` checks "
            "the scanner and its wiring are named; `SP047` confirms the step's exit code can "
            "actually fail the job, not merely report. A pass says a scanner is wired somewhere "
            "that can fail; it says nothing about whether secrets are currently present - this "
            "standard ships no scanner and inspects no file contents itself."
        ),
    },
}

# ---------------------------------------------------------------------------------------------
# The nine conformance-level controls (the union across essential/standard/full). Source:
# core/CONFORMANCE_LEVELS.md, read directly for the "reason" column and the "currently checked"
# table, never restated from memory.
# ---------------------------------------------------------------------------------------------

_LEVEL_CONTROLS: dict[str, dict[str, str]] = {
    "dependency_lock": {
        "simple": (
            "Every project depends on other people's code - libraries, packages. A dependency lock "
            "file pins the exact versions you're actually using, so \"it worked yesterday\" can't "
            "quietly become \"a dependency changed underneath us and now something's different.\" "
            "This one is actually checked: the tool confirms the lock file you name is real, has "
            "content, and is tracked in git - not just that you said you have one."
        ),
        "advanced": (
            "Every dependency's exact version is pinned in a lock file, named as this control's "
            "`implementation_reference`. Verified - `SP051` confirms the file exists, is non-empty, "
            "carries no template placeholder, and is tracked by git. It does not confirm the "
            "versions pinned are the ones actually installed, or that they are good ones."
        ),
    },
    "deterministic_tests": {
        "simple": (
            "A test suite that gives a different answer each time it runs isn't really testing "
            "anything - you can't tell if a red result means a real bug or just bad luck. This "
            "control names a real CI step that runs your tests and can actually fail the build if "
            "they fail. It's checked: the tool confirms that step exists, runs something, and its "
            "failure is binding - but it can't tell whether your tests are good ones, or even "
            "whether they assert anything at all."
        ),
        "advanced": (
            "A named CI step runs the test suite, and its failure is binding on the build. Verified "
            "via `SP053` - the checker confirms the step exists, runs something, and can fail the "
            "job. It does not confirm the tests are deterministic, that they assert anything, or "
            "that they test the right thing - a step running `true` would technically pass."
        ),
    },
    "contract_tests": {
        "simple": (
            "If another team, another service, or a separate frontend relies on the shape of what "
            "your code returns, a contract test catches you breaking that shape before it ships - "
            "instead of the other side finding out at runtime. Checked the same way as "
            "deterministic_tests: a real, failure-binding CI step, confirmed to exist and actually "
            "able to fail."
        ),
        "advanced": (
            "A named CI step runs contract tests against the interface's declared shape, with "
            "binding failure. Verified via `SP053`, identically to `deterministic_tests` - same "
            "mechanism, different step name, matched by name rather than by job."
        ),
    },
    "documentation_authority": {
        "simple": (
            "When two documents disagree about how something works, and nobody's said which one "
            "wins, people end up trusting whichever one they happened to open. This control means "
            "you have a single, real map of which document is the final word for which part of "
            "your project. It's checked indirectly: declaring this control requires the "
            "authority_map gate to also be required, and that gate's own artefact is what gets "
            "verified."
        ),
        "advanced": (
            "A machine-readable map states which document governs which path, closing the "
            "ambiguity contradictory authority creates. Checked through the `authority_map` gate "
            "rather than directly: `SP052` requires that gate whenever this control is declared "
            "required, closing the seam a level being a floor rather than a ceiling would otherwise "
            "leave open."
        ),
    },
    "provenance": {
        "simple": (
            "If a number your system produces really matters, you should be able to trace it back "
            "to exactly what data and settings went into it - not just trust that it's probably "
            "right. provenance and run_lineage share the same kind of record; provenance is the "
            "half that's about tracing back to inputs. The tool checks that every record you file "
            "is well-formed and points at something real - it can't tell you the record is true, "
            "only that it's complete and structurally sound."
        ),
        "advanced": (
            "A material result traces to its inputs - recorded in the same record type "
            "`run_lineage` uses, distinguished by which cross-reference each control obliges: "
            "`provenance` requires the run to resolve to every override that adjusted the result. "
            "Verified via `SP055`/`SP056` (schema-valid records in a declared directory) and "
            "`SP057` (the reference itself resolves) - never that the record is true."
        ),
    },
    "run_lineage": {
        "simple": (
            "Being able to trace inputs isn't the same as being able to re-run the exact thing "
            "that produced a result. run_lineage is the half of the record that's about "
            "reproducibility - this run, with this method, at this version, produced this output. "
            "Checked the same structural way as provenance: the record must exist, be well-formed, "
            "and its reference to the method that ran it must resolve to something real in your "
            "registry."
        ),
        "advanced": (
            "A material result is reproducible from a recorded execution - the run resolves to the "
            "method (and method version) that produced it. Same record type as `provenance`; "
            "distinguished by requiring the method reference specifically, not the override "
            "reference. Verified via `SP055`/`SP056`/`SP057`."
        ),
    },
    "method_registry": {
        "simple": (
            "If a calculation method changes over time, someone needs a real place recording which "
            "version is current, whether it's been validated, and who approved it - otherwise "
            "\"which version did we actually use\" becomes a guess. This is a register: a directory "
            "of records, checked to be well-formed. An empty register is a genuinely honest answer "
            "if you haven't governed any methods yet - it's not treated as a failure."
        ),
        "advanced": (
            "Governed methods carry identity, lifecycle, validation, and approval state, in a "
            "directory of records validating against `method-registry-entry.schema.yaml`. Verified "
            "via `SP055`/`SP056`. An empty register passes deliberately - the check establishes no "
            "unvalidated record exists, never that any records exist."
        ),
    },
    "overrides": {
        "simple": (
            "Sometimes a human has to manually adjust a number a system produced - that's fine, but "
            "it should never happen invisibly, buried in a spreadsheet formula or a line of code "
            "nobody notices. This control means every manual adjustment gets its own real, visible "
            "record: what changed, why, who approved it. Checked structurally the same way as the "
            "other record-based controls."
        ),
        "advanced": (
            "A manual adjustment is never hidden in UI or calculation code - recorded instead, "
            "carrying classification, before/after values, rationale, evidence, owner, impact, "
            "approval, and rollback approach (`core/CONTROL_PRINCIPLES.md` principle 6). Verified "
            "via `SP055`/`SP056`/`SP057` - each override's `method_run_id` must resolve to a real "
            "run in the register it names."
        ),
    },
    "assurance_findings": {
        "simple": (
            "Every real system has limitations - edge cases it doesn't handle well, assumptions "
            "that might not hold. This control is a commitment to writing those down honestly "
            "instead of quietly hoping nobody asks. Checked the same way as dependency_lock: the "
            "file you name must really exist, have real content, and not be a template you forgot "
            "to fill in."
        ),
        "advanced": (
            "Limitations and findings are recorded rather than smoothed away, in a named artefact. "
            "Verified via `SP051`, the same pattern as `dependency_lock` - existence, "
            "non-emptiness, absence of a template placeholder, and that it's tracked by git."
        ),
    },
}

# ---------------------------------------------------------------------------------------------
# The nineteen prerequisite gates, in core/PREREQUISITE_GATES.md's own catalogue order.
# ---------------------------------------------------------------------------------------------

_GATES: dict[str, dict[str, str]] = {
    # --- Design and user interface ---
    "component_library": {
        "simple": (
            "If your app has a screen with a button, a form, a table - build that piece once, as a "
            "reusable thing, before any screen uses it. This gate checks the order: the reusable "
            "piece has to exist first, then a screen can use it."
        ),
        "advanced": (
            "No screen may consume a UI component that does not already exist in the shared "
            "component library at the time it is introduced - checked against git history, not "
            "just current file state."
        ),
    },
    "design_authority": {
        "simple": (
            "Before you build any screen, decide up front how screens should look and be put "
            "together - a written design policy, plus a set of page templates to build from. This "
            "gate checks that those exist before UI code gets written, not that they get invented "
            "screen-by-screen as you go."
        ),
        "advanced": (
            "A design policy and a set of page templates must exist in the working tree before any "
            "UI code is written - checked against git history, so a policy written after the first "
            "screen still fails the audit even if it exists today."
        ),
    },
    "options_before_build": {
        "simple": (
            "Before building a screen or feature that has real design choices behind it, write "
            "down the alternatives you considered and which one you picked, and why. This gate "
            "isn't about the specific decision - it's about making sure a real choice happened, on "
            "the record, instead of just building the first idea."
        ),
        "advanced": (
            "Design alternatives for a surface are documented, and one is selected, before that "
            "surface is built - checked against history, the same \"decide before, not during\" "
            "shape every gate in this catalogue shares."
        ),
    },
    "prerequisite_state_ui": {
        "simple": (
            "If a screen depends on some data being ready first - an account being set up, a file "
            "being uploaded - it shouldn't show its main workflow as if that data already exists. "
            "This gate is about the screen honestly reflecting the state things are actually in, "
            "rather than presenting a workflow that will fail once someone tries to use it."
        ),
        "advanced": (
            "A screen does not present its main workflow before its stated data prerequisite is "
            "actually satisfied - a UI-specific instance of the general \"X must exist before Y may "
            "begin\" shape, applied to what a screen shows a user rather than to what code may "
            "change."
        ),
    },
    # --- Work and decisions ---
    "work_registration": {
        "simple": (
            "Before any real work starts - writing code, making a change - it should be written "
            "down somewhere as a named, identified piece of work: what it is, who owns it, what "
            "\"done\" looks like. This is the one gate that applies no matter how light your "
            "conformance level is; every repository using this framework registers its work before "
            "starting it."
        ),
        "advanced": (
            "No implementation work begins until it is registered as an identified activity, with "
            "an owner, a scope, and a definition of done - the only gate required at every "
            "conformance level, including `essential`."
        ),
    },
    "work_contract": {
        "simple": (
            "When an AI assistant is going to do implementation work, it should get a real written "
            "brief first - not just a registered activity in general, but the specific scope, "
            "constraints, and what \"done\" means for this particular piece of AI-assisted work. "
            "This gate checks that the brief exists before the AI starts, not that one gets written "
            "afterwards to match what happened."
        ),
        "advanced": (
            "A written work contract - scope, constraints, acceptance criteria - exists before "
            "AI-assisted implementation begins. The gate form of what `agent_work_packets` declares "
            "as a baseline control: this one is checked against the artefact and against history; "
            "that one is not checked at all."
        ),
    },
    "risk_classification": {
        "simple": (
            "Before you start building a change, decide how risky it is - not after you've already "
            "built it and are looking for a reason it was fine. The framework calls this out "
            "directly as the gate most often satisfied on paper while being violated in spirit, "
            "because classifying afterwards just rationalises work that already happened."
        ),
        "advanced": (
            "A change's risk class is decided before implementation begins, not derived afterwards "
            "to match what was built. Named in the framework's own text as the gate most often "
            "violated in spirit while satisfied on paper - classifying after the fact rationalises "
            "work already done rather than genuinely assessing it."
        ),
    },
    "decision_before_implementation": {
        "simple": (
            "For a material change - one that actually matters - write down the decision (what "
            "you're doing and why) before you start building it, not as an afterthought once it's "
            "already shipped. This is one of the gates that becomes mandatory once you're above the "
            "lightest conformance level, because \"we discussed it, trust us\" isn't something "
            "anyone can check later."
        ),
        "advanced": (
            "A decision record exists before implementation of a material change begins - required "
            "at `standard` and above. The evidence for this gate is the order of events in git "
            "history, not merely the record's existence, since a record can always be backdated but "
            "the commit graph cannot."
        ),
    },
    "register_currency": {
        "simple": (
            "If your project keeps a register of work (what work_registration points at), it needs "
            "to actually be up to date at the point you hand work off - not a stale list from three "
            "weeks ago. Any dashboards or views generated from that register have to be regenerated "
            "too, not left showing old data."
        ),
        "advanced": (
            "The work register, and any views generated from it, are current at the point of "
            "handover - checked against history, so a register updated after the handover it was "
            "meant to inform still fails."
        ),
    },
    # --- Documentation authority ---
    "authority_map": {
        "simple": (
            "Have one real, structured file that says which document is the final word for which "
            "part of your project - not scattered opinions in READMEs that might contradict each "
            "other. Without this map, \"the documentation\" is just a phrase, not something anyone "
            "can actually point at and check."
        ),
        "advanced": (
            "A machine-readable map of which document governs which path exists before it can be "
            "relied on elsewhere - the artefact the `documentation_authority` control's own check "
            "reads (`SP052` requires this gate whenever that control is declared)."
        ),
    },
    "authority_same_change": {
        "simple": (
            "When you change something the authority map covers, update the document that governs "
            "it in that same change - not in a follow-up commit that, in practice, often never "
            "arrives. This gate checks that the update actually happened together with the code "
            "change, using git history."
        ),
        "advanced": (
            "A change to a governed path updates its controlling document in the same change - "
            "checked against history, so a documentation update landing in a later, separate commit "
            "still fails the commit that didn't include it."
        ),
    },
    # --- Tests and evidence ---
    "test_convention": {
        "simple": (
            "Write down your own convention for how tests are named and where they live, and then "
            "actually follow it - so a new contributor (human or AI) can find and add tests "
            "predictably instead of guessing. This gate doesn't dictate what your convention is; it "
            "just requires that you have one and stick to it."
        ),
        "advanced": (
            "New tests follow the repository's own declared naming and location standard - the "
            "standard itself is repository-defined; this gate only requires that a declared "
            "convention exists and that new tests are checked against it."
        ),
    },
    "regression_before_merge": {
        "simple": (
            "If a piece of logic really matters, name the test suite that proves it still works, "
            "and don't let a change to that logic merge unless that suite actually passes. This is "
            "about making sure the safety net that exists actually gets used at the moment it "
            "matters, not just sitting there unused."
        ),
        "advanced": (
            "Named regression suites must pass before a change to critical logic is allowed to "
            "merge - the gate ties a specific, named suite to specific critical paths, rather than "
            "relying on \"the tests\" as an undifferentiated whole."
        ),
    },
    "equivalence_evidence": {
        "simple": (
            "If you're refactoring or optimising code without meaning to change what it produces, "
            "don't just eyeball the output and say \"looks the same\" - actually ship evidence (a "
            "real comparison, a diff of results) that proves it. The framework is blunt about this: "
            "\"it looked the same\" is the most common thing offered as proof of a safe refactor, "
            "and it isn't evidence."
        ),
        "advanced": (
            "A performance or refactoring change on a critical path ships evidence that results are "
            "unchanged - a genuine comparison output, not an assertion. The framework's own stated "
            "reason: \"it looked the same\" is the most commonly offered non-evidence for exactly "
            "this claim."
        ),
    },
    # --- Data ---
    "data_source_lifecycle": {
        "simple": (
            "Before a data source can actually be used in your system, it should go through a real "
            "validation and approval step - not just get added to a config file and quietly become "
            "available. The framework's own reasoning: a data source that's merely present, "
            "unapproved, will eventually get used by someone who assumed it was already vetted."
        ),
        "advanced": (
            "A data source completes its validation and approval lifecycle before it becomes "
            "selectable in the system - closing the gap where an unapproved but present source "
            "eventually gets used regardless."
        ),
    },
    "output_validation_before_external_use": {
        "simple": (
            "Before an output your system generates leaves your own team - goes to a client, a "
            "colleague in another team, a downstream system - someone should validate and review it "
            "first. This gate is about the boundary: what happens before it crosses that line, not "
            "after."
        ),
        "advanced": (
            "Generated outputs are validated and reviewed before any use outside the delivery team "
            "- the boundary the gate is scoped to is external use, not generation itself."
        ),
    },
    # --- Dependencies and release ---
    "dependency_output_delta": {
        "simple": (
            "If updating a dependency could actually change what your system produces - not just "
            "how it's built, but its real output - that update needs evidence showing what changed "
            "and a review, before it merges. A lock file alone only tells you a version number "
            "changed, not what effect that had."
        ),
        "advanced": (
            "A dependency change capable of moving outputs requires delta evidence and review "
            "before merge - the framework's own distinction: a lock file records what changed; "
            "this gate is for what the change actually did."
        ),
    },
    "records_before_release": {
        "simple": (
            "Whatever records your project's risk level says you need - change records, decision "
            "records - they need to actually exist before you start preparing a release, not get "
            "backfilled afterwards to make the release checklist look complete."
        ),
        "advanced": (
            "The change and decision records a change's risk classification requires exist before "
            "release preparation begins - ties back to `risk_classification`, since what's required "
            "here depends on that earlier decision."
        ),
    },
    "change_record_before_completion": {
        "simple": (
            "A change isn't \"done\" just because the code works - it's done once there's a real "
            "record of the change too. This gate checks that the record exists before the change is "
            "treated as finished."
        ),
        "advanced": (
            "A change record exists before the change is treated as complete - closing the gap "
            "where \"done\" quietly comes to mean only \"the code merged\", with the record arriving "
            "later or not at all."
        ),
    },
}

# What "conformance level" itself means, shown once before the level-choice list - the third
# worked example the maintainer approved, verbatim. The per-level gate/control counts are shown
# separately, computed from the catalogue (`catalogue.level_summary`), not restated here as static
# prose that could drift from it.
LEVEL_CHOICE: dict[str, str] = {
    "simple": (
        "Think of this as choosing how strict your own rules are. essential is lightest - for "
        "something only your own team sees. standard is for anything a colleague or customer "
        "relies on. full is strictest - for things where a wrong number could genuinely hurt "
        "someone."
    ),
    "advanced": (
        "essential: one required gate, one required control. standard: floor grows to "
        "authority_map, decision_before_implementation, change_record_before_completion, plus "
        "four interface gates if UI, plus four controls. full: floor grows further to "
        "regression_before_merge, equivalence_evidence, and four record-based controls."
    ),
}

# `F67`: one short cue per level control, for a list row that has to fit beside a tick box at 80
# columns. The full explanation is shown for the highlighted row; the cue only has to say which
# control this is in words a first-time reader recognises. `tests/test_adopt.py` asserts every
# level control has one and that none exceeds forty characters.
CUES: dict[str, str] = {
    "dependency_lock": "exact dependency versions, checked",
    "deterministic_tests": "a CI test step that can fail, checked",
    "contract_tests": "tests of what others rely on, checked",
    "documentation_authority": "one map of which document wins",
    "provenance": "trace a result back to its inputs",
    "run_lineage": "reproduce a result from its run",
    "method_registry": "a register of governed methods",
    "overrides": "every manual adjustment on record",
    "assurance_findings": "known limitations written down",
}

EXPLANATIONS: dict[str, dict[str, str]] = {**_BASELINE_CONTROLS, **_LEVEL_CONTROLS, **_GATES}


def explain(item_id: str, mode: str) -> str:
    """The explanation for `item_id` in `mode` ("simple" or "advanced"). Raises `KeyError` on an
    unknown item ID rather than returning a silent empty string - a missing item is a coverage gap
    this module's own test catches, not something to paper over at the call site."""
    return EXPLANATIONS[item_id][mode]
