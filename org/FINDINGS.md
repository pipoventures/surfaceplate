# Findings — register and convention

The single register of findings against this repository and the framework it publishes. Before this
file existed, findings were scattered across three documents using two colliding `F1`–`F4`
sequences, plus an `F4` named only in prose and an `F5` with no heading of its own. This file is the
one place to look.

`assurance_findings` — *"Limitations must be recorded rather than smoothed away"*
(`core/CONFORMANCE_LEVELS.md:61`) — is one of the controls this framework requires of others at the
`full` level. Until this file existed the publisher did not implement it. Creating the register did
not by itself discharge that control: per `core/CONFORMANCE_LEVELS.md:73-76`, a declaration without
an invoked check is not enforcement. That gap closed with `DR-13` item 0 — this repository now
carries an application profile declaring `assurance_findings` as met, above the floor its level
obliges, and `check_conformance.py` runs against it in CI.

---

## Numbering convention

> `F<n>`, sequential, never reused. The register assigns a new number **only** to a finding first
> raised here. A finding that originated elsewhere keeps its original code, is cited
> document-qualified, and is never renumbered.

**Why not renumber.** Two constraints make renumbering the wrong answer, not merely the harder one.
`org/decisions/README.md:74-77` explicitly freezes `DR-5`: *"It is left as written — its severity
assessments and its raw evidence are the historical record of what was found at `v0.11.0`, and
rewriting them would destroy the record rather than update it."* And the live `F1`–`F5` codes are
cited in `DR-5`, `DR-6`, `DR-9`, `CHANGELOG.md`, `tests/validate_contracts.py:26` and
`tests/test_install_and_check.py:152`. Renumbering breaks every one of those citations and gains
nothing; namespacing the live series breaks the same citations for a cosmetic tidy.

So the collision is resolved by **qualification, not renumbering**: a bare `F<n>` always means the
live series indexed below. The historical series are always cited with their document prefix.

**Codes that are not findings, listed so nobody merges them later:**

| Namespace | What it is |
|---|---|
| `SP<n>` | Checker *output* codes emitted at runtime against an adopting repository — not durable records with severity or lifecycle. `DR-8.md:64`. The exact space is declared below, and checked. |
| `DR-<n>` | Decision records. `org/decisions/README.md`. |
| `ACT-<n>` | Activities. `activity/register.md`, which begins 2026-08-31 and records why earlier work being unregistered is not a gap. |

### The `SP` code space, declared

`tests/check_code_registers.py` parses the block below and compares it against the codes
`scripts/check_conformance.py` actually emits. Prose alone is what allowed this very section to
state, until 2026-08-31, that the space ended at `SP043` — after `SP046` and `SP047` had been
added and while the person adding them was editing this file.

```text
emitted:  SP001-SP035, SP037-SP043, SP046-SP058
gap:      SP036
reserved: SP044-SP045
```

`SP036` is a deliberate gap (`DR-8`). `SP044` and `SP045` are reserved by `DR-11.md:49` and are
emitted by nothing until a generator exists; the check asserts they stay unemitted, so a
reservation cannot quietly become a code in use. It also asserts the space has no **undeclared**
hole — the defect `DR-8` originally found, where `SDS036` sat documented-but-unimplemented across
an unknown number of releases with nothing noticing.

---

## Live register

| ID | Title | Severity | Status |
|---|---|---|---|
| F1 | Test suite pass conditional on an unstated environment fact | high | Closed — v0.13.0 |
| F2 | Documented install line fails on a PEP 668 interpreter | medium | Closed — v0.13.0 |
| F3 | `validate_contracts.py` reported no executed-check count | low | Closed — v0.13.0 |
| F4 | Namespace rule and schemas drifted; the test could not detect it | not assessed | Closed — v0.12.0 |
| F5 | Three spellings of the organisation identifier; one does not resolve | medium | Closed — corrected, verified live |
| F6 | Every integrity anchor sits inside the boundary being checked | high | **Open** |
| F7 | `adoption.framework_digest` is never checked against anything | medium | Closed — `SP048`/`SP049`, `DR-14` |
| F8 | The CI detector is inside the artefact it protects | medium | Closed — ruleset applied and demonstrated |
| F9 | Remediation text names no pinned version | low | Closed — text scoped, installer reports upgrades |
| F10 | The producer evidence record describes an artefact that no longer exists | medium | Closed — `DR-21` |
| F11 | Nothing checks finding-code uniqueness or contiguity | low | Closed — `tests/check_code_registers.py` |
| F12 | Source and vendored checker copies can diverge, and nothing detects it | medium | Closed — `DR-20` |
| F13 | A wired CI check can never have run, inside a green pipeline | medium | Closed — requirement shipped to adopters |
| F14 | The placeholder heuristic cannot distinguish notation from an unfilled template | medium | Closed — `DR-17` |
| F15 | Two shipped templates were undetectable as templates | medium | Closed — obligation shipped; detection still not possible |
| F16 | Placeholder detection cannot separate mentioning a token from containing one | low | Closed — `DR-22`, by declaration |
| F17 | The identifier check reads every GitHub URL as a claim about this organisation | low | Closed — declared third parties |
| F18 | Inherited product and methodology names throughout the public tree | medium | Closed — redacted, disclosed |
| F19 | A licence decision recorded in another repository, never implemented in this one | medium | Closed — `DR-24` |
| F20 | A control is checked against itself, never against reality | high | Closed — all 9 controls checked; `DR-26` completes pattern C |
| F21 | `dependency_lock` declared with nothing pinned, and CI not recording what it used | medium | Closed — `pyproject.toml`, `SP051` |
| F22 | A deferral's revisit date was required to exist and never read again | medium | Closed for deferrals — `SP054`; **open** for gate exceptions |
| F23 | A drift guard matched on line shape rather than on the thing it guards | medium | Closed — anchored to the block; the false green constructed and run |
| F24 | A schema clause that could never add an obligation, grading the wrong axis | low | Closed — removed; `materiality` grades approval, not completeness |
| F25 | Declaring a placeholder-scan exemption made the profile fail the placeholder scan | medium | Closed — the exemption's own rationale is excluded; found in Plyego |
| F26 | `SP032`'s placeholder remedy was wrong for 17 of 19 gates and named no remedy | low | Closed — generic wording that names the exemption route |
| F27 | The installer forbade what the standard permits: no way to adopt without the hook | high | Closed — `--no-hooks`, recorded and announced |
| F28 | `SP038` accepted any pre-commit hook as satisfying a `local_hook` claim | high | Closed — the active hook is compared against the one installed |
| F29 | The agent instructions the framework ships are not read by the agent that uses it | high | Closed — emitted per agent; surfaceplate finally subject to its own |
| F30 | The history audit resolves a precondition by its current path, so a rename falsifies the whole history | medium | **Open** — cleared by exception `GX-0001`; following renames is unbuilt |
| F31 | The history audit ran against a depth-1 clone in CI and reported nothing wrong | high | Closed — `fetch-depth: 0`, and a shallow clone is now reported |
| F32 | The wizard invented rationale text for baseline controls and auto-masked UI gates | high | Closed — `ACT-022`, routed through `Prompt`; found by the review `ACT-021` requested |

Closed entries are indexed here and left in their original records; they are not restated.
`F1`–`F3` — `org/decisions/DR-5.md:53,75,87`, fixed per `CHANGELOG.md:490-508`.
`F4` — stated in prose at `org/decisions/DR-6.md:34-39`, never given a heading or a severity;
implemented by the release that named it. This register gives it an index entry without editing
`DR-6`.
`F5` — `org/decisions/DR-9.md:17-19,56-61`. **Closed.** The live instruction was corrected:
`INSTALL.md:29` now reads the declared `github-org`, and `git ls-remote` against it resolves while
the old spelling still returns a hard 404. Every remaining occurrence of the broken spelling is a
*quotation inside a record* — `DR-9` documenting the finding, and the exemption pairs in
`ORGANISATION.md` that permit those quotations. `tests/check_identifiers.py` verifies this on every
run rather than it being asserted here.

**What was never a defect, stated so it is not re-raised.** The three declared identifiers still
differ from one another — a GitHub slug, a URN authority segment, and a registered legal name. That
is three namespaces with different grammars naming one organisation, not drift. Each is declared in
`ORGANISATION.md`, each is checked against its own contexts, and `NAMESPACE.md` governs whether the
URN authority ever changes. `F5` was about a spelling that *resolved to nothing*, and that is fixed.

*This entry was itself stale until 2026-08-31,* asserting that `INSTALL.md:29` "still reads" the
broken URL long after it had been corrected. It is one of the three false statements this register
was carrying, and part of the evidence behind `F11` below.

---

## F6 — Every integrity anchor sits inside the boundary being checked

**Severity: high. Open.**

**The finding is not that `INSTALL.json` is unprotected.** That is the symptom. The finding is
structural: every value the integrity check trusts is held inside the repository the check is
supposed to be judging, so the check can only ever establish internal self-consistency. A party with
write access edits the artefact and the record together, and both checks pass.

`FACT FROM PACKAGE`, read directly:

- `.standards/INSTALL.json` is not an entry in its own `files` map and structurally cannot be:
  `build_payload` (`scripts/install_standard.py:62-103`) admits only files that already exist in the
  source tree, and the record is generated at install time. Nothing else hashes it.
- `check_integrity` (`scripts/check_conformance.py:277-292`) iterates `record["files"]` — a map read
  out of the very file whose integrity is in question.
- `check_staged_integrity` (`:833-963`) compares the staged record against the **working-tree**
  record (`:862-865`), then staged blobs against digests held **inside that same staged record**
  (`:883-894`). One untrusted local copy against another.

**Consequence.** The check is sound against drift, accident, and casual modification, and that is
worth having. It is not, and cannot be, evidence against a party with write access. `README.md` now
says so; this finding is why.

**Not closed by DR-14, now that DR-14 is implemented.** `DR-14` gives distribution identity an
externally recomputable anchor, and `SP049` now checks the profile's declaration against the install
record. That narrows this finding twice over — a third party can establish which release a claim
refers to, and a profile can no longer name a version it was not installed from. It does not close
it, and the reason is unchanged by the implementation: **both values compared live inside the
repository being checked.** A party with write access edits the profile and the install record
together, and both checks pass.

One further limit found while implementing it: `MANIFEST.sha256` is not part of the install payload,
so an adopter cannot recompute the anchor from their own repository — only compare against what the
installer wrote for them. Recomputing it independently requires the published tree. `DR-14`'s
implementation note records this and leaves installing the manifest as an open question for whoever
revisits `DR-20`'s payload principle.

## What would actually close `F6`

Recorded because "structural, stays open" is not a plan, and because two things that look like
remedies are not.

**Closure requires a party other than this repository to hold the value.** Everything compared today
— the files, their digests, the install record, the profile — is writable by whoever holds commit
access. No arrangement of those four closes it, because the problem is not which values are
compared but that one party controls all of them.

**Signing does not close it, and was considered.** A signed tag proves the tag came from a
particular key. The holder of that key is the same person with commit access, so it establishes
provenance, not honesty. It is worth doing once there is a public repository where a stranger
verifying that release *n* came from the same key as release *n−1* has some value — but it would be
a mistake to record it as closing this, and a green *Verified* badge invites exactly that reading.
Decided 2026-08-31: not now, and recorded rather than left as an unexamined omission.

**A ruleset does not close it either.** That is `F8` — it stops the *check* being deleted; it does
not give the check an external anchor.

So what closes `F6` is release plan **items 9 and 10**: a cross-provider adversarial review, and an
independent audit. Concretely, someone who is not the maintainer recomputes `sha256(MANIFEST.sha256)`
from a published tree, compares it against what an adopting repository records, and attests to the
result. Until then this finding is open, and any claim that the integrity check establishes anything
against a party with write access is false.

---

## F7 — `adoption.framework_digest` is never checked against anything

**Severity: medium. Open.**

**The finding is not that a check is missing.** It is that the field's presence, its name, its
`^[A-Fa-f0-9]{64}$` constraint and its description — *"SHA-256 of the pinned release archive"*
(`schemas/application-profile.schema.yaml:59-62`) — together create the appearance of a verified pin
for a value that is only ever shape-checked. A reader of a conformant profile has no way to tell the
difference from the artefact alone.

`FACT FROM PACKAGE`: exhaustive grep of `scripts/check_conformance.py` (1882 lines) returns **zero**
occurrences of `framework_digest` or `framework_version`. The only code anywhere that touches the
field is a negative shape test, `tests/validate_contracts.py:458-459`. `MANIFEST.sha256` and `zip`
likewise appear nowhere in the checker.

`DR-7.md:117-120` already records that the digest shipped in `examples/*.yaml` *"is unverifiable now
and is very likely fabricated too"* — an instance of exactly this finding, recorded before the
finding itself was.

`DR-10.md:239-241` records the gap as known and out of its own scope. This entry is where it was
tracked.

**Closed by implementing `DR-14`.** The installer now records
`sha256(MANIFEST.sha256)` in `.standards/INSTALL.json`, and the checker compares the profile's
declaration against it: `SP048` when the declared version is not the one installed, `SP049` when the
digest disagrees or when the record carries no anchor to compare against. Both graceable, because
`DR-14` *changes what the field means* — every profile written under the previous definition carries
an archive digest and would fail the day this shipped.

**Why the manifest and not the archive**, since the field's old description said archive: the zip
embeds file mtimes, so nobody — including the maintainer — can recompute the digest of an archive
they did not keep. `MANIFEST.sha256` is a pure function of tree content, so a third party holding
the published tree can recompute the anchor on a machine that is not the adopter's. That is the
question `DR-10` set and could not answer.

**A case worth stating because it is the one that silently passed before.** An install record with
no anchor now raises `SP049` rather than being skipped. "Nothing to compare" and "the values match"
must not summarise the same way — the defect shape this register keeps recording.

**What is NOT closed.** Both values compared live inside the repository being checked, so this
establishes that the profile agrees with the install record, not that either is true. A party with
write access edits both. That is `F6`, which stays open, and `DR-14` says so itself rather than
claiming the anchoring gap is closed. What narrowed is real but bounded: a profile claiming a
version it was not installed from now fails, where before it passed in silence.

*One consequence peculiar to this repository:* its own profile sits inside the tree its manifest
covers, so the recorded anchor can never equal `sha256` of the **current** `MANIFEST.sha256` —
writing the value changes the manifest. The anchor records the tree installed *from*, which is a
historical fact rather than a live invariant, and an adopter's anchor behaves the same way with
respect to the framework's later changes.

---

## F8 — The CI detector is inside the artefact it protects

**Severity: medium. Open.**

**The finding is not "the workflow can be edited".** Everything in an adopter's repository can be
edited. The finding is that the workflow file is *itself* one of the digest-protected `files`
entries, while being the thing that invokes the check that would report its own modification — and
that the fallback this repository documents for exactly this case does not cover this class of
tampering.

`FACT FROM PACKAGE`:

- The workflow is vendored and digest-protected: `scripts/install_standard.py:41,74`, digests at
  `:312-314`, recorded as `files` at `:366`.
- It is what runs the checker in CI: `standard/.github/workflows/standards-conformance.yml:32-33`,
  `run: python .standards/check_conformance.py --repo .`
- **Independent detection exists, and is real, when the hook is active.**
  `standard/.githooks/pre-commit:9-26` invokes `.standards/check_conformance.py --repo … --staged`
  directly. It reads nothing from `.github/workflows/`. A staged edit to the workflow is reported by
  name as a modified `files` entry (`SP040`, `scripts/check_conformance.py:883-894`) and separately
  as `SP005` on the working tree (`:303-315`) — both `graceable=False`, both blocking.
- **But hook activation is the exception, not the default.** It is repository-*local* Git config,
  written only by the installer (`scripts/install_standard.py:210`,
  `git config --local core.hooksPath .githooks`). Local config is neither cloned nor pushed;
  `INSTALL.md:66-68` states that every later clone must run the installer again to activate it.
- **The documented fallback does not apply.** `README.md` states that "the history audit remains the
  durable detector after a bypass". That is true for prerequisite gates and false for `files`
  integrity: `audit_gate_history` (`scripts/check_conformance.py:1264-1280`) is scoped exclusively to
  a gate's own declared `gated_activity.paths` with a precondition-artefact test, and has no
  relationship to `record["files"]`. There is no history-based integrity audit anywhere in the
  checker. That imprecision in `README.md` is recorded here rather than edited, per this packet's
  "record, do not fix".

**Consequence.** Where the hook is active there are two genuinely independent detectors and a CI
bypass alone does not neuter the control. Where it is not — the default state of any clone but the
installer's — a party who edits the workflow to stop invoking the checker is caught by nothing until
someone runs the checker by hand. `DR-15` addresses the remedy and does not implement it.

**The documentation half is discharged (2026-08-31); the finding stays open.**

This entry recorded `README.md`'s imprecision *"rather than edited, per this packet's 'record, do not
fix'"*. That packet closed weeks ago, and the sentence was still on the adopter-facing surface
overstating a control — the exact failure this repository has spent the surrounding work removing.
An expired instruction is not a reason.

Three passages corrected, all carrying the same over-broad reading:

- the claim that the history audit *"exposes a bypass after the commit exists"*, which is true of
  prerequisite gates and false of `files` integrity;
- *"a guarantee that survives Actions being switched off"*, now scoped to gates;
- *"the history audit remains the durable detector after a bypass"* — the sentence this finding
  named — now stating plainly that no history-based integrity check exists, that a modified
  standard-owned file is detected only when the checker runs, and that in a clone where the hook was
  never activated nobody is watching until a human looks.

**Why the finding is still open.** The structural remedy is `DR-15`'s ruleset posture, and it cannot
be demonstrated: `/branches/main/protection` and `/rulesets` both return HTTP 403 on this
repository's plan. Correcting the description of a control is not the same as fixing the control,
and closing this on a documentation fix would be the overclaim the finding is about.

**A route to closure is now decided.** `DR-23` decides to publish surfaceplate as a new public
repository, where rulesets are available at no cost, and to move development there — which matters,
because a ruleset must guard the repository where work happens rather than an archive. The intended
end state is all four status checks and a pull request required before merge on `main`.

That is a decision, not a control. This finding closes when the ruleset **exists and is shown to
block a merge that fails a check** — not when it is configured. The gap between enabling something
and demonstrating it is one this register has recorded repeatedly, most directly in `F13`.

**Closed 2026-08-31, on demonstration.**

`DR-23` was executed: surfaceplate is published at `github.com/pipoventures/surfaceplate`, and a
ruleset `main-required-checks` targets the default branch. Read back from the API rather than
trusted from the request that created it:

- `enforcement: active`
- **`bypass_actors: 0`** — nobody is exempt, including the maintainer
- rules: `deletion`, `non_fast_forward`, `pull_request` (0 approvals), `required_status_checks`
- contexts: `check`, `gitleaks`, `Contract and installer tests`, `Conformance check`
- `strict_required_status_checks_policy: true`

**Zero required approvals is deliberate, not an oversight.** A single maintainer cannot approve
their own pull request, so requiring one would lock the repository rather than protect it. The
control here is the checks; the pull request is what makes them run.

**Demonstrated, twice, because a configured control is not a control:**

| Probe | Result |
|---|---|
| Direct push to `main` | Refused — *"Changes must be made through a pull request"*, *"4 of 4 required status checks are expected"* |
| Pull request with a deliberately corrupted manifest digest | `Contract and installer tests` **FAILURE**; merge refused — *"the base branch policy prohibits the merge"*; `main` unchanged |

The probe branch was deleted immediately afterwards.

**What this does and does not fix.** The finding was that the detector lives inside the artefact it
protects — delete the workflow file and the check disappears. It now cannot: the requirement is held
in the forge's settings, so deleting the workflow makes the merge impossible rather than making the
check vanish. That is the structural change.

**One limit, untested and stated rather than glossed.** Whether an explicit administrator override
(`gh pr merge --admin`) is refused was **not** exercised. GitHub documents rulesets as binding
administrators when the bypass list is empty, and the ordinary merge path *was* refused for the
repository owner — but the override flag itself was not tried, because testing it would have meant
merging a knowingly broken tree to a public branch to find out. Recorded as unverified rather than
assumed either way. If it matters later, the safe test is a trivially revertible failure, not a
corrupted manifest.

**And what stays open regardless.** This protects *this* repository. It requires nothing of any
adopting repository, which must apply its own ruleset. It also does nothing for `F6`: a ruleset
stops the check being deleted; it does not give the check an anchor outside the repository.

---

## F9 — Remediation text names no pinned version

**Severity: low today, rising under any ambient-installer distribution. Open.**

**The finding is not that today's behaviour is wrong.** Today it is correct. The finding is that the
correctness rests on a property of the *operator's environment* that no code establishes, and the
remediation text is written as though the code establishes it.

`scripts/check_conformance.py:308-311` tells an adopter to *"Revert the local edits and re-run the
installer"*. Nothing scopes "the installer" to a version:

- `repo_root()` (`scripts/install_standard.py:58-59`) resolves the source to wherever the running
  copy of the script physically sits.
- `build_payload` re-reads and re-hashes every file fresh from that source on every run
  (`:313-316`); the run **rewrites** the record rather than restoring toward the previous one.
- Nothing compares the source's `VERSION` against the previously recorded `standard_version`, or
  refuses on mismatch. `:271-272` prints the previous value as a courtesy and acts on nothing.

So "re-run the installer" restores the original bytes only because the operator's checkout is a
fixed artefact they have not moved. That is operator discipline, not a property of the code. Under a
distribution where the installer is an ambient upgradeable package, the same sentence would restore
*different* bytes and call it a repair. `DR-10.md:42-48` already commits to keeping the checker
vendored per-adopter for exactly this reason.

**Closed, in both halves.**

*The text.* `SP004` and `SP005` now name the version from the install record and say why it matters:
the installer rewrites the record from whatever source it runs from, so a different version restores
different bytes. The advice is no longer correct-by-coincidence.

*The behaviour.* `install_standard.py` now reports when its source `VERSION` differs from the
recorded `standard_version`, in the words that matter — **this is an upgrade, not a restore** — and
tells an operator who arrived from an integrity failure to stop and run the recorded version
instead. Reported, deliberately **not** refused: upgrading is the ordinary path and blocking it
would trade one defect for a worse one. What was missing was never that upgrading is wrong, only
that it was indistinguishable from repairing.

Seen to fail: silent on a fresh install, silent on a re-run at the same version, and firing with the
old and new versions named when the source `VERSION` differs.

**What remains true and is not this finding.** `repo_root()` still resolves the source to wherever
the script sits, and item 1 of `org/RELEASE_PLAN.md` will change that under a wheel install. The
notice makes the change visible; it does not make an ambient installer safe.

---

## F10 — The producer evidence record describes an artefact that no longer exists

**Severity: medium. Open.**

**The finding is not that a file is out of date.** It is that a document whose stated purpose is to
be *evidence of package checks* (`audit/VALIDATION_RESULTS.md:3-4`) describes a different artefact
than the one shipped, and asserts as PASS a rule this repository deliberately abolished. An evidence
record that does not describe the thing it ships with is not weak evidence; it is a false claim.

`FACT FROM PACKAGE`, against `VERSION` = `0.14.0`:

- `:6` — `Current release: 0.7.0`. Seven releases stale.
- `:13`, `:15` — `PASS - 5/5` schemas. There are **6** (`schemas/*.schema.yaml`).
- `:54` — instructs verifying `dist/surfaceplate-0.7.0.zip`, which does not exist.
- `:16` — `| Version consistency | VERSION matches the namespace base version segment | PASS |`.
  **`DR-6` explicitly decoupled these.** The claim is now false on its face — `VERSION` is `0.14.0`
  and the namespace segment is `0.7.0` (`NAMESPACE.md:12`) — and, more importantly, it reports a
  passing check for a rule that was removed on purpose. `DR-6.md:26-30` records the replacement.

This is the pre-audit's own `PRE-AUDIT-0.6.0/F2` — *"Producer validation record is stale"* — recurring
in the same file that F2 was raised against, which is why it is recorded rather than quietly fixed.

**Closed by `DR-21`: the file is retired, not regenerated.**

The recurrence is the whole argument. `CHANGELOG.md:75` records fixing `PRE-AUDIT-0.6.0/F2` by
regenerating this exact file; seven releases later it was stale again. Applying the same remedy
twice and expecting a different result would be the register failing to learn from itself. The
structural reason is that a hand-written evidence document depends on a human updating it every
release and nothing fails when they do not — an artefact whose accuracy rests entirely on
discipline, in a repository whose thesis is that discipline is not a control.

Its function is now genuinely served: five suites run on every push and pull request, each reporting
the count of checks it executed, and the workflow confirms each step produced a result. That is
better evidence than a table — re-runnable, dated by the commit, and unable to go stale without
going red.

The file is **kept, marked historical, with every stale or abolished row annotated inline** rather
than only under a banner, because a correction that depends on reading order is not one: a grep for
`Version consistency` lands on the row, not the header. It is kept rather than deleted because its
"Checks NOT performed" and "Outstanding" sections are still true, and `F6` and `F8` cite the latter
by line.

One further thing the audit turned up, fixed in the same change: `audit/AUDIT_README.md` pointed an
auditor at this file as *"the producer's current check record"* and told them to attach
`engineering-control-kit.zip` — the pre-`0.12.0` product name, for an archive not produced under
that name since the rename.

---

## F11 — Nothing checks finding-code uniqueness or contiguity

**Severity: low. Open.**

Migrated from `org/decisions/DR-8.md:99-103`, which recorded it as open and never gave it a code:

> *"Nothing enforces that a newly added finding code is unique, contiguous, or documented in
> `core/PREREQUISITE_GATES.md`. The existing catalogue check in `tests/validate_contracts.py` covers
> prerequisite-gate identifiers only, not the finding codes. `SDS036` existed as a
> documented-but-unimplemented code for an unknown number of releases without anything noticing,
> which is precisely what such a check would catch. Not added here; recorded as open."*

The register is the first thing this applies to, and the colliding `F1`–`F4` series this file exists
to resolve is a second instance of the same defect shape.

**Closed by `tests/check_code_registers.py`**, which runs as its own CI step.

The case for a check rather than more care is that care demonstrably did not work. On 2026-08-31
this register carried **four** false statements at once, each written by someone reading the file:

| Claim | Reality |
|---|---|
| `F5`'s entry: `INSTALL.md:29` "still reads" a non-resolving clone URL | Corrected some releases earlier |
| The code table: the checker emits `SP001`–`SP043` | `SP046` and `SP047` existed, added by the session editing this file |
| The `ACT-<n>` row: "no register behind it" | `activity/register.md` existed |
| The header: "this repository still carries no application profile" | It had one, and CI was checking it |

None is a typo. Each was true when written and became false when something else changed — the class
of error a careful reader cannot catch, because nothing about a stale sentence looks different from
a current one.

The check compares **declarations against reality**: the `SP` space declared above against the codes
`check_conformance.py` actually constructs, and the `F` table against its own body sections. Seen to
fail on all five assertions, including a reproduction of the real error — a code added to the
checker and not declared here.

**What it does not do, since three of the four claims above would have survived it.** It cannot
judge whether a finding's prose is still accurate; that is not mechanically decidable. It makes one
narrower thing impossible: a code that exists in one register and not the other.

---

## F12 — Source and vendored checker copies can diverge, and nothing detects it

**Severity: medium. Open.** Raised by `org/decisions/DR-16.md` during self-conformance work.

The finding is **not** that two copies exist. That is deliberate design, recorded at
`org/decisions/DR-10.md:42-48`. The finding is that `org/decisions/DR-11.md:143-152`'s load-bearing
guarantee — *"the code that recorded a digest is guaranteed … to be the code now checking it"* — is
**scoped to the adopter boundary**, where exactly one copy exists and there is no source tree. A
publisher that has installed into itself holds both, and neither `DR-10` nor `DR-11` considers that
case. The guarantee still holds pointwise; that is precisely what makes the self-check answer
questions about a checker that is no longer the one under development.

Mechanically:

- **Every automated route runs the vendored copy.** The hook resolves
  `"$repo_root/.standards/check_conformance.py"` and `exec`s it
  (`standard/.githooks/pre-commit:9,17`); the installed workflow does the same
  (`standard/.github/workflows/standards-conformance.yml:33`). Both hard-fail if it is absent.
  Neither falls back to `scripts/`.
- **The staleness is real, not theoretical.** `check_integrity` digests `repo / rel` where `rel` is
  `.standards/check_conformance.py` (`scripts/check_conformance.py:281-291`).
  `scripts/check_conformance.py` is not a key in `files` and is never opened — the checker contains
  zero references to `scripts/` in its entire length. Editing the source therefore leaves the
  vendored digest matching, and `SP004`/`SP005` stay silent.
- **Consequence.** Add a finding code to source that this repository violates, do not reinstall, and
  the hook and the installed workflow run the *old* vendored checker, which cannot emit it, and
  report **PASS** — while `python scripts/check_conformance.py --repo .` would **FAIL**.
- **`--verify-manifest` is the near miss and must not be mistaken for a remedy.** After
  self-install the two files are separate manifest entries, so editing source does make the manifest
  stale — but the remedy is to regenerate it, after which it records two different digests for two
  files and passes. It detects *"manifest stale"*, never *"the copies differ"*, and by design cannot
  become a drift detector. It **masks** the divergence rather than revealing it.

Adjacent but distinct: `F9` is the installer being ambient-upgradeable — the reverse asymmetry,
adopter-framed. `F8` is the CI detector sitting inside the artefact it protects — the same
self-reference shape, a different mechanism.

**Closed by `DR-20` (`ACT-003`).** The original mitigation — CI running the **source** copy, while
the hook and installed workflow run the vendored one — is kept, because the two routes serve
different purposes and both are wanted. But a mitigation that ensures one route is current is not a
detector, and this finding is about the *absence of detection*.

`tests/check_vendored_current.py` now compares every payload path's source against its installed
copy, deriving the set from `install_standard.build_payload` rather than restating it, and runs as
its own CI step. It reports the review class of anything that differs, so
`[enforcing] .standards/check_conformance.py` reads differently from `[reference] core/…`.

**It was not written speculatively.** The condition occurred twice on 2026-08-31 while implementing
`DR-18`: `schemas/application-profile.schema.yaml` was edited and the checker rejected the new
profile field as unknown, because it was parsing the stale vendored schema. Nothing reported drift.
The symptom was a confusing `SP016` that took a reinstall to explain.

Seen to fail three ways: an edited checker, an edited normative document, and a deleted install
record — the last reporting that self-conformance is gone rather than that there is nothing to
compare, since "no baseline" and "matches baseline" must not summarise the same way.

**What stays open, and it is not this finding.** The check is publisher-only, because an adopter
holds one copy and has no source tree to compare against. An adopter whose vendored copy is stale
relative to a newer *published release* is a different problem, governed by `adoption.review_by`
and `framework_version` — and `F7` records that the digest anchor meant to detect it is checked
against nothing.

---

## F13 — A wired CI check can never have run, inside a green pipeline

**Severity: medium. Open.** Found while diagnosing this repository's own red CI.

`tests/check_identifiers.py` was added, committed, wired into
`.github/workflows/standard-self-check.yml`, and had **never executed in CI** since being added. An
earlier step failed, GitHub Actions short-circuits the remaining steps by default, and the step's
conclusion was recorded as `skipped`. Nothing in the run summary distinguishes *"this check passed"*
from *"this check never produced a result"* unless the per-step conclusion is read individually.

This is distinct from `F1`. `F1` was a result **conditional on an unstated environment fact** — the
check ran and its answer depended on something nobody had declared. This is a result that was
**never produced at all**, while every artefact that would suggest otherwise — the workflow file,
the commit, the step name — was present and correct.

It belongs to the defect shape this register keeps meeting: *an instrument whose negative result
does not establish what it appears to*. It was not caught by reading output more carefully; the
output was internally consistent and wrong. It was caught by comparing one instrument against
another.

**Mitigated in this repository, not fixed in the standard.** The self-check workflow now carries
`if: ${{ !cancelled() }}` on each *check* step, so every check runs regardless of a prior failure
while each step keeps its own pass/fail and the job stays red if any failed. Deliberately **not**
`continue-on-error`, which would mark a failed step as tolerated — that would be weakening a control
to obtain a pass. A final step then confirms each check produced a result, because a mitigation that
reports on itself is what this finding was about.

**Demonstrated, not asserted.** Two runs, both read per-step from the API rather than from the job's
green tick — the artefact that concealed this finding in the first place:

| Run | What it shows |
|---|---|
| `33386896054` (`pull_request`) | All six check steps `success`, none `skipped`. |
| `33387146079` (`workflow_dispatch`) | The **first** check step deliberately failed, and every later check step still executed. |

The second run is the one that matters. Its per-step conclusions read `failure`, `success`,
`failure`, `success`, `success` across the five checks, and the confirm step printed
`ran, FAILED : contracts` / `ran, passed : installer` / `ran, FAILED : manifest` / `ran, passed :
identifiers` / `ran, passed : conformance` before failing the job. **Two independent failures
surfaced in one run.** Under the previous behaviour the first would have appeared and the other four
steps would have reported `skipped` — which is exactly how this finding stayed invisible.

*A limitation found while demonstrating it:* the workflow triggers on `pull_request` and pushes to
`main` only, so a pushed branch with no pull request runs nothing at all. The demonstration used
`workflow_dispatch`. This is not a defect — it is the intended trigger set — but it means a branch
can carry a failing check indefinitely without any run existing to reveal it, and "no failing run"
is therefore not evidence of a passing branch.

**Closed: the requirement now ships.** `core/REVIEW_AND_EVIDENCE.md`'s failure-discipline section
states it for every adopting repository — a pipeline must not silently skip its checks, something
must confirm each check produced a result, and a green run is evidence only for the steps that
actually executed, so cite the step rather than the job.

**It is an obligation, not an enforced control, and the standard says so where it states it.** This
framework inspects a declared profile and a git history, not the semantics of an adopter's
pipelines. Recording the difference is the point: the failure this finding describes is invisible
precisely because everything around it looks correct, and a reader who assumed the framework
checked it would be in the same position the finding describes.

---

## F14 — The placeholder heuristic cannot distinguish notation from an unfilled template

**Severity: medium. Open.** Found by running the check against this repository (DR-13 item 0).

`SP032` fails a prerequisite gate whose precondition artefact *"still contains template
placeholders"*. The test is `PLACEHOLDER_PATTERN.search(text)` over the whole file
(`scripts/check_conformance.py:1547`), and the pattern's fourth branch is
`<[a-z0-9_\- ]{1,30}>` (`:63-66`). That branch matches **any** angle-bracketed lowercase token, so it
cannot tell an unfilled template slot from a metavariable in prose.

Measured against this repository's own content, the branch has a **100% false-positive rate**. Seven
occurrences across six files; not one is an unfilled placeholder:

| File | Line | Text | What it is |
|---|---|---|---|
| `org/decisions/README.md` | 33 | ``DR-<n>``, sequential, never reused | numbering convention |
| `org/FINDINGS.md` | 19, 31, 40, 41, 286 | ``F<n>``, ``DR-<n>``, ``ACT-<n>`` | numbering conventions |
| `core/PREREQUISITE_GATES.md` | 67 | `git log --since=<effective_from>` | command template |
| `CHANGELOG.md` | 418 | `urn:…:0.7.0:<schema-file-name>` | historical URN form |
| `scripts/verify_release.py` | 10 | `python scripts/verify_release.py <path-to-zip>` | CLI usage line |

Three of those are normative documents this framework publishes. The defect is therefore **not**
publisher-specific: any adopter whose governed artefact contains a usage line or a naming convention
gets a spurious `SP032` on a gate that is a **floor at `standard`**.

**No principled narrowing is available.** A real unfilled slot (`<your-org>`) and a metavariable
(`<schema-file-name>`) are lexically identical — both lowercase, hyphenated, angle-bracketed.
Excluding matches inside Markdown code spans would clear five of the seven but not the `.py` usage
line, and would be a Markdown-specific rule inside a general check. The other three branches
(`replace-me`, `TBD`/`TBC`, `TODO`) fire on nothing here and are not implicated.

**Live effect on this repository while it stood.** It was what stood between this repository and a
clean `check_conformance.py --repo .` — five `SP032` findings, all graceable, giving `WARN` with
grace expiring 2026-09-30.

**Closed by `DR-17`.** The branch was removed rather than narrowed, and the removal was measured
rather than asserted: no test depended on it, and the only shipped template carrying an
angle-bracket slot also carries `replace-me`, so file-level detection is unchanged.
`tests/validate_contracts.py` now pins the negative direction — the three notation strings above
must **not** match — and that guard was seen to fail by reinstating the branch in a scratch copy.

**On the sequencing, since it is the part worth preserving.** This finding was raised inside the
work whose objective was making this same check pass, and was deliberately *not* fixed there:
changing a published control's behaviour inside that work is indistinguishable, in the diff, to a
reviewer later, from adjusting the control to obtain a pass. It was registered as `ACT-004` with no
dependency on `ACT-001` and given its own decision record, and the maintainer directed that the
instrument be fixed **before** self-conformance landed, on the grounds that conformance established
through a known-wrong instrument is not worth establishing. `DR-17` records the reasoning; the
seen-to-fail guards are what make the claim checkable rather than merely stated.

---

## F15 — Two shipped templates were undetectable as templates

**Severity: medium. Closed for the templates this framework ships (`DR-17`); open in general.**

Found while auditing `F14` — specifically, while establishing what the branch being removed was
actually worth. This is the reason that audit had to enumerate rather than reason: the defect is a
**false negative**, and a false negative leaves no output to read.

`SP032` exists to catch a gate whose precondition artefact is still a blank form. Of the five
templates under `templates/`, two — `decision-record.md` and `work-packet.md` — marked their blanks
with a key and an empty value (`- Decision ID:`), which matches no branch of `PLACEHOLDER_PATTERN`,
before or after `DR-17`. An adopter copying either to satisfy a gate and leaving it blank would have
passed `SP032` while pointing at an empty form.

Note the direction of the error relative to `F14`. `F14` made the check fire on correct work;
`F15` made it stay silent on exactly the condition it exists to catch. They were present
simultaneously, in the same four lines of code, and the loud one concealed the quiet one — the
branch's noise made the check feel more sensitive than it was.

**Fixed in the templates, not in the checker.** Both now carry a visible `replace-me` marker.
Teaching the checker to detect empty-value-after-colon was rejected in `DR-17`: it is a second
shape-based heuristic of the kind being removed, and it would misfire on ordinary prose. The
convention belongs where it is chosen.

**Closed, by shipping the obligation rather than by gaining the detection.** The distinction is the
whole content of this closure. `tests/validate_contracts.py` asserts that every file under
`templates/` is detectable, seen to fail by stripping the marker from `templates/work-packet.md` —
but that protects only what this framework ships.

For an adopter's own templates, detection is **not available**: the only general way to recognise a
blank form by its shape was removed under `DR-17` after producing seven false positives and no true
ones, and reinstating it would undo a decision made on measurement. So
`core/PREREQUISITE_GATES.md` now states it as a requirement on the adopting repository — mark your
own templates with one of the tokens, because the framework will not guess — and explains why the
guessing was removed.

An adopter who ignores that requirement still gets a blank form passing `SP032`. That residue is
real and is not closed by this entry; what is closed is the framework's silence about it.

---

## F16 — Placeholder detection cannot separate mentioning a token from containing one

**Severity: low. Open, and not closable by choosing a better token vocabulary.**

Found the way findings of this shape are always found — by tripping it. The `CHANGELOG.md` entry
documenting `DR-17` spelled out the four placeholder tokens it had just made canonical, and
`CHANGELOG.md` is a precondition artefact for two gates. The entry describing the fix failed the
check it was describing.

`PLACEHOLDER_PATTERN` is matched against whole file text, so a document that **mentions** a token
is indistinguishable from one that **contains** an unfilled slot. `DR-17` removed the
shape-based branch precisely because it could not draw a distinction its input did not carry; this
is the same defect, narrowed. Four fixed tokens is a far smaller surface than any angle-bracketed
string — which is why this is `low` where `F14` was `medium` — but the surface is not zero, and no
choice of token removes it. A living record that discusses its own controls will always risk
quoting them.

**This is the third instance of one shape in this project**, and the pattern is worth naming
because it keeps arriving disguised as three unrelated bugs:

| Where | What quoted itself |
|---|---|
| `.gitleaksignore` | a comment naming the finding it suppressed became a finding |
| `ORGANISATION.md` | the source of truth for the identifiers failed its own identifier check |
| `CHANGELOG.md` | the entry documenting placeholder detection tripped placeholder detection |

The remedy adopted for the first two was *describe, do not reproduce*, and the same remedy applies
here: `core/PREREQUISITE_GATES.md` is the single document that spells the tokens out, and every
other document refers to it. The first two also needed a second remedy — excluding a source-of-truth
document's own declaration blocks from its own scan — which has no equivalent here, because the
scan belongs to a published control rather than to a local test.

**Closed by `DR-22`, by declaration rather than by detection.** An artefact may now be declared
exempt from the placeholder scan in the profile, with a mandatory rationale. Three properties make
that an exemption and not a hole, and each is tested: it suppresses the *token branch only*, so an
exempt artefact must still exist and still be non-empty; it is declared in the **profile**, never
inside the artefact, because a template able to exempt itself would be exactly the condition
`SP032` exists to catch; and every exemption is reported as an advisory on every run, so a narrowed
control says it was narrowed. `SP050` fires on an exemption naming an artefact that does not exist,
since a stale exemption outlives the thing it was written for.

**The underlying defect is not solved, and the closure does not claim it is.** Whole-file matching
still cannot separate mention from use. What changed is who decides: a human can now say which
artefacts legitimately mention the tokens, in a place a reviewer reads and a diff shows. An adopter
can exempt an artefact that really is unfinished, and nothing prevents that —
`core/CONTROL_PRINCIPLES.md` principle 9 already places the quality of a human declaration outside
what this framework may verify.

This repository uses the mechanism on itself: `CHANGELOG.md` is a precondition artefact for two
gates and documents this very control, so it necessarily contains the tokens. The previous
workaround was to avoid naming them, and that was worse — a changelog that cannot describe a
control is a poorer artefact than one that needs an exemption.

*Note on this entry:* `org/FINDINGS.md` is not a precondition artefact for any gate, which is the
only reason it may discuss this at all. If it ever becomes one, this section is why it will fail.

---

## F17 — The identifier check reads every GitHub URL as a claim about this organisation

**Severity: low. Closed by a declaration mechanism; the underlying rule is unchanged.**

Found by adding the first third-party GitHub URL to a payload file. `tests/check_identifiers.py`
rule 1 asserts that every `github.com/<owner>/` in the shipped tree equals the declared
`github-org`. The secret-scan workflow fetches its scanner from `github.com/gitleaks/gitleaks`, and
the check reported that as organisation drift.

The rule is right for a URL that is *meant* to point at this organisation and wrong for one that is
not. A repository linking to a tool, an action, or somebody's documentation is not misspelling its
own identity. This is the same defect class as `F14` — a rule broader than the thing it means to
detect — and it is the **second** time this check has produced a false positive of that shape: the
first was a regex that matched any host ending in `github.com`, so `docs.github.com/en/...` scored
as an organisation named `en`.

**Closed by declaration, not by weakening the rule.** `ORGANISATION.md` gains a fifth block naming
other people's organisations, and `check_identifiers.py` derives the exemption from it rather than
holding a list — the `DR-6` principle. Rule 1 still asks its question of every owner not declared.

Unlike the quoted-evidence block, third-party entries are **not** paired to a path. The asymmetry
is deliberate: a quoted drift is a wrong spelling of *this* organisation that one record has reason
to reproduce, so scoping it keeps that spelling caught elsewhere. A third party is legitimately
referenced anywhere, and pairing would cost maintenance for no detection.

**Seen to fail both ways.** Removing `gitleaks` from the block restores the failure; deleting the
block makes the parser refuse to start rather than silently exempting nothing.

**What remains open.** The rule cannot distinguish the two cases by itself and still cannot; it now
asks a human to declare which owners are third parties. A third party added to a payload file
without being declared still fails, which is the intended direction — the check fails loudly rather
than tolerating silently — but it is friction, not detection.

---

## F18 — Inherited product and methodology names throughout the public tree

**Severity: medium. Closed 2026-08-31.**

Found while assessing the framework against two target adopter profiles, which is worth noting: it
was invisible for as long as the only readers were people who knew what the names meant.

The tree carried internal product and methodology names from the private repository this framework
grew out of — in `adapters/r.md`, `adapters/typescript.md`, `SETUP_GUIDE.md`, four documents under
`audit/`, `CHANGELOG.md`, `RECONCILIATION.md` and `org/decisions/DR-7.md`. `SETUP_GUIDE.md` was
**titled** with the pre-`0.12.0` product name, and the adoption wizard prompt still called the
product by it in live text.

**Not a brand-policy breach** — these are product and methodology names, not the organisation. It
is a comprehensibility defect, and it landed hardest exactly where an evaluating reader looks
first: `adapters/r.md` is three lines long and spent a third of its length warning against copying
a product the reader has never heard of.

**What was done.** Every inherited name is replaced with a generic description. Live guidance was
rewritten outright; historical records under `audit/` were redacted **with the redaction
disclosed** in a note at the top of each, because the substance of what was checked and found is
unchanged and only the proper nouns are.

An earlier draft of this fix left the historical records untouched under a note explaining the
names, on the reasoning that `DR-23` gives for not rewriting history. The maintainer overruled it:
remove the references everywhere. Recorded because the reasoning matters and was not
wrong — it was outweighed. The compromise that survives is disclosure: nothing was altered
silently, and each redacted document says so.

**What deliberately remains, and why:**

| Retained | Reason |
|---|---|
| `Shiny` in `adapters/r.md` | A public R framework, named the way `pytest` or `React` would be. *"Keep calculation logic outside Shiny server orchestration"* is genuine R guidance, not inherited jargon |
| The pre-rename product name in `CHANGELOG.md` | It records **this** product's own rename. Removing it would erase the record of the rename itself |
| The same name in a historical `audit/` document title | This project's own history, in a record marked historical |
| *"tool-agnostic"* lowercase | Ordinary English used as an adjective, not a product name |

The line drawn: **someone else's names go; this product's own former name stays where it records
history and goes from live guidance.** `SETUP_GUIDE.md`'s title and the wizard prompt were live
guidance and were corrected.

**Two things this does not fix.** The adapters remain 3 and 5 lines — thin for the audience they
serve, and a quantitative team writing R would rely on `adapters/r.md`. And nothing prevents the
same residue recurring; `tests/check_identifiers.py` guards the *organisation* identifier, not
inherited product names, and no check was added here.

---

## F19 — A licence decision recorded in another repository, never implemented in this one

**Severity: medium. Closed by `DR-24`.**

Found by a pre-check demanded during a scope review, not by anything in this repository. That is the
finding's whole shape: nothing here could have caught it, because the decision was never here.

On 2026-08-30 a Class C decision was recorded in `hermes` licensing surfaceplate **by artefact
type** — Apache-2.0 for software, and a separate licence for the documents, amended the same day
from CC BY 4.0 to CC0-1.0 on the reasoning that attribution and change-indication duties are real
friction on files copied into a corporate repository. It required a `LICENSE-DOCS`, a `NOTICE`, and
a README statement of which licence covers what.

**None of it existed.** The root `LICENSE` carried Apache-2.0 correctly; `LICENSE-DOCS` and `NOTICE`
were absent, and `README.md` contained no occurrence of the word "licence" at all. **The repository
was made public in that state**, so every template and agent skill shipped under a code licence the
decision says should not govern prose.

**This is the fourth instance of one shape**, and the register should say so plainly: a decision
recorded in one place and not implemented where it applies. `DR-14` stood decided-not-implemented
until `F7` forced it; `DR-15`'s remedy is still unimplemented; `DR-11` reserved codes for a
generator that does not exist. Those three were at least visible *inside* this repository. This one
was not, and no check here could have found it — the decision lives in a repository this one does
not read.

**A near miss recorded alongside it, because it was luck rather than method.** The same pre-check
asked whether publication had violated a locked sequencing control. It had not — a same-day entry
discharged the cross-provider review requirement. But `DR-23` was written and publication carried
out **without ever consulting `hermes`**, where a Class C decision with an explicit publication
precondition was sitting. The answer came out clean by accident. Had it not, a locked control would
have been breached by an agent that never looked for it.

**What is not fixed.** Nothing checks that decisions recorded elsewhere are implemented here.
`governance/authority-map.yaml` maps paths to governing documents *within* this repository; it has
no concept of an external authority. Whether that is worth building is not decided — but the
absence is now recorded rather than assumed away.

---

## F20 — A control is checked against itself, never against reality

**Severity: high. Closed 2026-08-31**, when the last of `DR-25`'s four patterns was built (`DR-26`).

**Demonstrated, not argued.** This repository was made to claim `full` and declare `provenance`,
`run_lineage`, `method_registry` and `overrides`, in a tree containing no such records. **The
checker raised zero objections about any of them.** Every finding it produced concerned gates.

`SP021` and `SP022` verify exactly two things about a control: that it appears in
`control_decisions`, and that it reads `required`. Nothing asks whether the thing exists.

**The asymmetry, stated in the terms that matter:**

| | What the checker does |
|---|---|
| **A gate** | Looks at reality — does the artefact exist, is it blank, is it still a template, and did anyone touch the gated paths while it was missing |
| **A control** | Looks at the declaration — is it listed, does it say `required` |

**This is uniform across levels, which is why it is severity high rather than a `full`-only
problem.** `dependency_lock` at `essential` is as unverified as `provenance` at `full`. An adopter
at any level can declare every control it requires, possess none of them, and pass.

**Why it is not simply a false claim.** `core/CONFORMANCE_LEVELS.md` already states that *"a schema
file is not enforcement"*, and some controls genuinely cannot be tool-checked — *"we review actual
diffs"* is a promise about human behaviour, and `core/CONTROL_PRINCIPLES.md` principle 9 places that
beyond what this framework may assert. The defect is narrower and real: a reader who sees that
`full` requires `run_lineage` may reasonably infer that something checks run lineage, and the levels
documentation did nothing to prevent that inference.

**Four of them ship a schema and are never read.** `override-record`, `method-registry-entry`,
`method-run-lineage` and `assurance-evidence` describe precisely the records these controls demand.
The checker references **none** of them. The framework wrote down what the evidence should look like
and then never looked.

**How it was closed, in four packets rather than one.** `DR-25` fixed four patterns and made
`implementation_reference` — a field already in the schema and used by nothing — the place an
adopter says where a control lives.

| Packet | Pattern | Controls | Codes |
|---|---|---|---|
| `ACT-011` | D — already a gate; A — declared artefact | `documentation_authority`, `dependency_lock`, `assurance_findings` | `SP051`, `SP052` |
| `ACT-012` | B — declared CI step | `deterministic_tests`, `contract_tests` | `SP053` |
| `ACT-014` | C — declared records | `overrides`, `method_registry`, `run_lineage`, `provenance` | `SP055`, `SP056` |

The four schemas noted above as written and never read are now read: `override-record`,
`method-registry-entry` and `method-run-lineage` validate the registers, and `assurance-evidence` is
consumed within the method-registry schema that embeds it.

**Two claims in this entry did not survive being built**, and are corrected here rather than left
standing:

- *"is current"* — appears twice above. It is **not** provable for these record types, because no
  record schema carries an expiry or review date. `DR-25` is amended in place; `DR-26` records why.
- *"Only the records validator is new"* was right about the code and wrong about the difficulty.
  The judgement in pattern C is not the validation — it is that an **empty register must pass**,
  because a check demanding records is a check rewarding invented ones.

**What is still not provable, now stated at its real width.** That a record is **true**: a lineage
record can carry an input hash computed over nothing. And that a register is **complete**: nothing
detects a run that happened and went unrecorded, so an adopter who files nothing passes forever.
`DR-25` records the first as a permanent boundary; `DR-26` adds the second.

---

## F21 — `dependency_lock` declared with nothing pinned, and CI not recording what it used

**Severity: medium. Closed.**

The first thing `F20`'s architecture was pointed at, and it landed on the framework itself before a
single validator existed.

**Surfaceplate declared `dependency_lock: required` and had no lock of any kind.** No
`requirements.txt`, no `pyproject.toml`, nothing pinned anywhere. All three workflows ran
`pip install pyyaml jsonschema`, unpinned, resolving whatever was newest that morning.

**Worse than unpinned: unrecorded.** `pip --quiet` suppressed the resolution output, so a green CI
run could not tell you which `jsonschema` had validated the schemas. Local carried `pyyaml 6.0.1`
and `jsonschema 4.10.3`; CI had been resolving something newer for months. The two had never
matched, and nothing noticed because nothing looked.

**The rationale described the absence as though it were the control.** It read: *"the runtime set is
two packages, named in every documented install line and in CI."* Naming is not locking. That
sentence is what a declared-but-unverified control looks like from the inside — it sounds like
diligence and commits to nothing.

**Not merely paperwork.** A breaking `jsonschema` release would have broken the checker in every
adopting repository simultaneously, with no record of which version had ever worked.

**Closed by:** `pyproject.toml` pinning both runtime dependencies to exact versions, resolved in a
clean virtual environment with all five suites run against them **before** pinning — not copied from
whatever happened to be installed on a developer machine, which was older and had never matched CI.
The workflows install those exact versions and no longer pass `--quiet`, so the resolution is
recorded in the run. `SP051` verifies the profile's `implementation_reference` points at a file that
exists, is non-empty, is not a template, and is tracked by git.

`tests/validate_contracts.py` asserts the workflows install what `pyproject.toml` declares, and that
every dependency is pinned with `==` rather than a range. Both seen to fail: a drifted workflow
version, and a pin loosened to `>=`. One source of truth, checked rather than trusted — the remedy
this register has now applied to the namespace (`F4`), the organisation identifier (`F5`), the
vendored checker (`F12`) and now the dependency set.

**What is still not proven.** That the pinned versions are *good*, only that they are fixed and
recorded. And pinning a version is not pinning an artefact: there are no hashes here, so this
protects against an unexpected new release rather than a compromised re-upload of the same version.
PyPI does not permit re-uploading a version, which makes that largely theoretical — but it is a
weaker guarantee than a hash-bearing lock, and `pyproject.toml` says so rather than implying
otherwise.

---

## F32 — The wizard invented rationale text for baseline controls and auto-masked UI gates

**Severity: high. Closed.**

Found by the review `ACT-021` requested — item 9 of `org/RELEASE_PLAN.md`, the first time this
framework has been read by a party other than the maintainer and the agent that built it, and the
first thing it found was real.

`surfaceplate/adopt/`'s own binding rule, stated in its `__init__.py` docstring before any of the
package was written: *"No module here selects a conformance level, invents a rationale, or sets a
date."* `sections.py`'s `ask_controls` hardcoded the rationale for all three baseline controls
(`agent_work_packets`, `actual_diff_review`, `secret_hygiene`) as Python string constants, never
routed through a `Prompt` call. `ask_gates` did the same for the four `DESIGN_GATES` it
auto-marks `not_applicable` when `builds_user_interface` is false. Both wrote a rationale to the
profile the human never saw asked — a direct violation of the rule stated to govern the whole
package, undetected by `ACT-020`'s own 23-check test suite, which proved every *asked* question
was answered and nothing more, but never proved every *written* value traced to a question.

`FACT FROM PACKAGE`, read directly, before accepting the report: `sections.py:149-176` (as it stood
before this finding) constructed `baseline_controls` from a module-level `_BASELINE_RATIONALES`
dict and a second inline string for `secret_hygiene`, none reachable from any `prompt.text` call;
`sections.py:255-260` wrote `"rationale": "This repository has no user interface."` inside a loop
with no `Prompt` argument at all.

**Not every finding in the same report survived the same check.** Two others were verified against
the code and found not to hold: `adoption.deferrals = []` is a disclosed limitation
(`org/decisions/DR-32.md`'s "Limitations and follow-up"), not an invented claim — it asserts
nothing false, unlike a fabricated rationale. And the report's over-engineering finding — that a
non-UI repository must manually justify all four UI gates — is wrong about the code: `ask_gates`
already auto-masks them; the reviewer had not traced that branch. Accepting a review's findings
without independently checking each one against the artefact would have been exactly the "wrong
artefact" failure this project's own working-method doctrine names — validating the *report about*
the code rather than the code itself.

**A third finding in the same report was neither confirmed nor dismissed here — it was a genuine
design question, decided separately.** The report's material finding — that the schema alone
cannot detect a profile declaring `full` while omitting required controls — is accurate as far as
it goes. Whether adding conditional schema logic to close it was worth the cost is `org/decisions/DR-33.md`'s
question, not this entry's: decided against, on the finding that the scenario described does not
occur in this project's actual pipeline (the checker already runs schema validation as part of
itself), and that the proposed remedy would duplicate `CONFORMANCE_LEVELS` a second time by hand.

**Closed at `ACT-022`, in the same session the finding arrived.** `ask_controls` now asks for each
baseline control's rationale exactly as it already asked for every level-required control's; the
`DESIGN_GATES` auto-mask now asks per gate, with the old fixed string offered as an editable
default rather than a silent write, so the "no UI" fact already given earlier is not re-litigated
four times over — an answer with a default is still a `Prompt` call a human confirmed, the same
pattern `review_by` and `enforcement` already use elsewhere in the same file. A new test
(`tests/test_adopt.py::test_design_gates_rationale_is_asked`) scripts rationale text that matches
none of the old hardcoded strings and asserts the written profile contains exactly that text — a
regression here would misalign the scripted answer sequence and fail loudly, not silently pass.

---

## F31 — The history audit ran against a depth-1 clone and reported nothing wrong

**Severity: high. Closed.**

`actions/checkout@v4` fetches **one commit** unless told otherwise, and neither this repository's
self-check workflow nor the one it installs into adopters said otherwise.

`git_history_available()` verifies `HEAD` and returns true, because a shallow clone has a perfectly
good `HEAD`. So the audit ran, examined the single commit it had been given, found no gate
violations, and said nothing — while `SP035` and `SP036` were, in CI, incapable of firing at all.

**Every green CI run this project has ever had reported a clean history audit from a look that
could not have found anything.** The advisory written for exactly this situation — *"This is an
absence of evidence, not evidence of conformance"* — never fired, because history *was* available.
Just almost none of it.

**How it surfaced**, and it is worth recording because nothing was going to surface it otherwise:
`GX-0001` names nine historical commits, and CI could not resolve one of them —
`'1b0df98': fatal: Needed a single revision`. The exception mechanism failed loudly on a shallow
clone, and that failure is the only reason the audit's silence was examined. A control that fails
closed exposed one that had been failing open.

**Closed** two ways, because either alone leaves the defect somewhere:

- `fetch-depth: 0` in both this repository's self-check workflow **and** the one installed into
  every adopter. Without the second, every adopter inherits the same false green.
- The checker now detects a shallow clone with `git rev-parse --is-shallow-repository` and says so,
  in the same terms as the unavailable-history note. A workflow is configuration an adopter can
  change; the checker saying what it could and could not see is not.

**The shape, and its worst form.** An instrument whose negative result does not establish what it
appears to — `F12`, `F14`, `F21`, `F23`, `F25`, `F28`. This instance is the most complete: the
control was present, configured, running, and green, in the repository that publishes the control,
for its entire history. Nothing failed. The audit's silence was indistinguishable from success, and
only an unrelated check refusing to pass on the same missing data made anyone look.

## F30 — A renamed precondition artefact makes a gate's entire history read as non-compliant

**Severity: medium. Open.** Cleared for this instance by `governance/exceptions/GX-0001.yaml`.

The history audit resolves a gate's precondition artefact by its **current** path, then asks
whether that path existed at each commit that touched a gated path. So renaming the artefact —
without changing a word of it — retroactively reports every earlier commit as having crossed the
gate without its precondition.

Observed here, immediately and unavoidably. `test_convention` names a testing-convention document
that has existed continuously since `0.9.0`. At `0.17.0` it moved from
`standard/.github/instructions/tests.instructions.md` to `standard/agent-instructions/tests.md`
so the instructions could be emitted per agent (`DR-30`, `F29`). The audit then reported **nine
commits** as violations, back to the repository's first:

```
[SP035] Gate 'test_convention' was crossed without its precondition
  9 commit(s) since 2026-08-31 changed a gated path while a required artefact was absent
```

Not one of them crossed anything. The convention was in force throughout, under a different name.

**Why the obvious remedies do not apply**, which is what makes this a finding rather than a
nuisance:

- **Moving `effective_from` forward** is refused by `SP034`, deliberately and correctly — it would
  erase every violation between the old date and the new one.
- **Listing both the old and new path** fails `SP032`, which requires every named artefact to
  exist; the old path is gone.
- **Not renaming** is not available: the rename was the fix for `F29`.

So the only route is a gate exception, which is the designed escape hatch and leaves a permanent
mark. That is the right outcome for *this* instance and the wrong shape as a general answer: an
adopter who reorganises their documentation will be asked to file exceptions for work that never
violated anything, and `DR-22`'s warning applies — *"a growing pile of these records is evidence
that the gate is wrongly scoped or the process is wrong."*

**The candidate remedy is to follow renames**, which git can do (`--follow`), resolving the
precondition's path *as at each commit* rather than as at HEAD. It is not built, and it is not a
small change: `--follow` is heuristic, single-path, and its results would have to be trusted by a
control. Left open rather than half-built.

**A trap found on the way, worth its own line.** The exception record listed abbreviated SHAs
unquoted, and `7547482` — seven digits, no letters — parsed as an **integer**. `SP043` rejected the
record. The check did its job; the trap will catch any adopter whose abbreviated SHA happens to be
all digits, roughly one in every few dozen.

**It fired again, immediately, on the next rename.** `ACT-019` moved
`standard/agent-instructions/tests.md` to `surfaceplate/standard/agent-instructions/tests.md` when
the payload was packaged for pip (`DR-31`). The same mechanism reported the `DR-30` commit as a
violation, for the same reason, and was cleared by a second exception,
`governance/exceptions/GX-0002.yaml`. Two occurrences of the same defect in one session, both from
renames this project chose for its own good reasons, is stronger evidence than this finding had when
first written that the deferred remedy deserves higher priority. Not built in either packet:
building it as a side effect of an unrelated change would be the scope creep this project's own
working method exists to catch. Severity and status unchanged; this is evidence added to an open
finding, not a reopening of a closed one.

## F29 — The agent instructions the framework ships are not read by the agent that uses it

**Severity: high. Closed.**

Surfaceplate shipped 501 lines of agent instruction as six
`.github/instructions/*.instructions.md` files, each declaring `applyTo: "**"` and opening
*"Installed by Surfaceplate. Do not edit this file in an adopting repository."*

**That is GitHub Copilot's format.** Claude Code loads managed policy, `~/.claude/CLAUDE.md`,
`./CLAUDE.md` or `./.claude/CLAUDE.md`, `./CLAUDE.local.md`, and `.claude/rules/*.md`.
`.github/instructions/` is not on that list. `.github/copilot-instructions.md` is read **only by
`/init`**, as a one-time generation step rather than session loading.

So the instructions reached one agent and no other — and surfaceplate has no `CLAUDE.md`, so they
reached **nothing at all in the repository that publishes them**. Every packet of governance work
done here has been done by an agent that never read a line of them.

**Established on two independent lines of evidence**, because assuming behaviour from a filename is
the error that produced this finding:

- **Direct observation.** Across a long working session in this repository, none of that content
  entered context, while `~/.claude/CLAUDE.md` and its four imports did. The positive control
  matters: instruction loading demonstrably works here and simply never reaches `.github/`.
- **The published documentation**, which lists the loaded locations exhaustively and states
  plainly: *"Claude Code reads `CLAUDE.md`, not `AGENTS.md`."*

That last sentence also disposes of the remedy `DR-12` had planned. It committed to *"`AGENTS.md`
as the canonical emitted instruction file"* — which would have been **equally inert** for Claude
Code without a `CLAUDE.md` importing it. The commitment was right about neutrality and wrong about
mechanism, and it was never built, so the error was never discovered.

**Fourteen of forty-five installed files — 31% of the payload — were GitHub-specific**, in a
framework whose `DR-12` promises forge and agent neutrality.

**Closed** by one canonical body in `standard/agent-instructions/` and per-agent emitters: the
Copilot form byte-for-byte as before, plus `.claude/rules/surfaceplate-*.md` carrying `paths:`
where Copilot carries `applyTo:`. `.claude/rules/` is additive, so it cannot collide with an
adopter's own `CLAUDE.md` the way writing that file would. `AGENTS.md` receives the conformance
block through the existing marker mechanism, so an adopter's own 293 lines survive untouched.

**And surfaceplate now has a `CLAUDE.md` importing `@AGENTS.md`.** That is what makes this closable
rather than merely recorded: the framework is finally subject to the instructions it publishes.

**What is not claimed.** That the instructions were subsequently *read*. Files existing in
documented locations is not the same as content entering a context window, and the difference is
this finding. It is observable in a later session via `/context` under **Memory files**, and it has
not been observed yet. Whether Copilot reads its own form is likewise untested here.

**The shape.** An instrument whose negative result does not establish what it appears to — the
register's most-repeated defect — with one aggravation the others lack: **nothing failed.** No check
went red, no adopter complained, no test broke. The files were present, correctly formatted, and
comprehensively ignored. It surfaced only when an adopter's own conventions forced the question of
which instructions govern.

## F28 — `SP038` accepted any pre-commit hook as satisfying a `local_hook` claim

**Severity: high. Closed.**

`active_pre_commit_hook` asked one question: **is there an executable `pre-commit` in the active
hooks directory?** Any hook, from anyone, doing anything.

So a gate could declare `enforcement: [local_hook, ...]` and be satisfied by a hook that formats
code, prints a message, or does nothing at all. `SP038`'s own text was *"Gate claims hook
enforcement, but there is no hook"* — and what its silence established was **"a hook exists"**, not
**"staged changes are checked before they are committed"**, which is the whole content of the
enforcement claim.

Demonstrated: a repository with the standard installed, `core.hooksPath` pointed at an unrelated
hook, and every gate claiming `local_hook`. **Zero findings.**

**This predates the hook opt-out and was exposed by it.** Declining hooks leaves `core.hooksPath`
pointing at the adopter's own system, which satisfied the old test perfectly — so the first probe
written to prove that a false `local_hook` claim is still caught found that it is not.

**Closed** by comparing the active hook against the one this standard installed. The remedy needed
no new data: `.standards/INSTALL.json` has always carried the digest of `.githooks/pre-commit`, and
a record with no such entry — because hooks were declined — cannot support the claim, which is the
correct answer rather than a special case. Three failure modes are now distinguished and each is
asserted: no hook at all, a hook that is not this standard's, and hooks declined at install. The
finding's title changed with them, because *"there is no hook"* is plainly wrong against a
repository that has one.

**The shape, again.** An instrument whose negative result does not establish what it appears to —
`F12`, `F14`, `F21`, `F23`, `F25`. What is different here is *where it was found*: not by reading
the code, but by writing a probe to demonstrate a property the plan had asserted, and watching the
probe fail. The assertion in the approved plan — *"`SP038` is untouched and still catches a gate
claiming a hook that was declined"* — was **false when written**.

## F27 — The installer forbade what the standard permits

**Severity: high. Closed.**

Surfaceplate would not install into Plyego at all:

```
STOPPED - this repository already has a different Git hook configuration:
  the effective core.hooksPath is already '<the adopter's own hooks directory>'.
Nothing has been written.                                        (exit 4)
```

The refusal is *correct*: setting `core.hooksPath=.githooks` would silently stop the adopter's
existing hook running. The installer detects this thoroughly — effective local, worktree, global and
system configuration, every hook type — and fails closed and atomically.

**The defect is that there was no third route.** `SP038` fires only when a gate's `enforcement` list
claims `local_hook`, so a profile declaring `enforcement: [history_audit, review]` has always been
fully conformant with no surfaceplate hook anywhere. **The standard said the hook was optional and
the installer said it was mandatory** — two parts of one framework disagreeing about the same
obligation, which is the defect this register names more often than any other, found in itself.

Three things made it more than a nuisance:

- Both offered remedies — *reconcile the existing hooks* or *remove the old hook configuration* —
  assume the adopter wants surfaceplate's hook. Neither contemplates keeping their own.
- The blocked case is **any repository with existing commit-time automation**, which is the target
  rather than an edge case. The first real adopter hit it immediately.
- The refusal is at the wrong layer: forty-five files of standard, schemas and checker withheld over
  one optional **25-line shim** whose entire body is
  `exec python3 "$checker" --repo "$repo_root" --staged`.

**Closed** by `--no-hooks`, which is **recorded and announced** rather than silent. The declination
is stored in `.standards/INSTALL.json` and reported by every conformance check, because the
alternative is the shape this framework exists to catch: nothing would distinguish *"staged changes
are gated"* from *"nothing gates them"*, in the profile or in a passing check alike. Every other
narrowing here announces itself — `DR-22`'s exemptions, deferral dates, `DR-27`'s unchecked-reference
notes — and a silent opt-out would have been conspicuous by inconsistency.

Chaining the adopter's hook from surfaceplate's was considered and rejected: `.githooks/pre-commit`
is standard-owned and integrity-checked, so delegation logic would ship to every adopter and have to
work for arbitrary hooks; and once `core.hooksPath=.githooks`, the displaced hook is reachable only
if surfaceplate calls it, making the framework the permanent owner of another system's hook.

## F26 — `SP032`'s placeholder remedy was wrong for most gates, and named no remedy

**Severity: low. Closed.**

`SP032`'s placeholder branch hard-coded *"Complete the artefact. A template is not a design
policy."* — for **every one of the nineteen gates**. The wording was written for `design_authority`
and copied into the generic path, where it says nothing sensible about a work register, a changelog,
or a dependency review. Seventeen of the nineteen gates are not about design policy.

The larger half is that it **named no remedy**. `placeholder_scan_exemptions` has existed since
`DR-22`, and the finding that most often needs it never mentioned it. Plyego is the evidence: the
remedy had to be recalled from a decision record, because the finding gave nothing to act on.

**Closed** with generic wording — following `SP051`'s existing *"A template is not an implemented
control"* — plus a sentence naming the exemption route and stating what it does not suppress.

## F25 — Declaring a placeholder-scan exemption made the profile fail the placeholder scan

**Severity: medium. Closed.**

`SP020` walked **every string in the application profile** and raised a finding on any placeholder
token. `SP032` does the same for a gate's precondition artefacts, and `DR-22` gave that one a
remedy: declare `placeholder_scan_exemptions` with a rationale saying why the artefact legitimately
contains the token.

**The remedy could not be used.** A rationale explaining why an artefact contains a token has to
quote it — and the rationale is a string in the profile, so `SP020` fired on the exemption itself.

Observed end to end, and not here. Plyego's `activity/register.md` line 401:

```
| ACT-395 | debt | F080 appendix-card chapter_archetype always "tbd" in S2 — RESOLVED | Closed | |
```

A **closed** work item whose title quotes the literal string because that string *was* the defect,
inside a 590-line live register. `SP032` flags the file. Declaring the exemption then failed
`SP020`. A `PASS` was only obtained by wording around the token — precisely the workaround `DR-22`
names as bad: *"a changelog that cannot describe a control is a worse artefact than one needing an
exemption."*

**This is the fifth instance of the self-quotation shape in this register, and the first that is
structurally unavoidable.** The earlier four — `.gitleaksignore`, `ORGANISATION.md`, `CHANGELOG.md`,
`DR-23` — were documents that happened to describe a defect and so reproduced it; each could be
reworded or exempted. Here the **mechanism built to fix the defect cannot be used without causing
it**. That is a different class of problem, and it is why this one is a finding rather than another
instance of `F16`.

**Why it was invisible from inside.** Surfaceplate declares two exemptions of its own, for
`org/FINDINGS.md` and `CHANGELOG.md`, and both rationales *describe* the tokens without reproducing
them — a habit formed by `F14` and `F15`. The trap needed an adopter who wrote the natural sentence.

**Closed** by excluding `placeholder_scan_exemptions[*].rationale` from the profile walk, and
nothing else. One field, not one record: the `artefact` path beside it is still scanned, as is every
other rationale in the profile. Three negative controls hold that line.

**What it costs.** A rationale reading only `TODO` now passes. That is `DR-22`'s already-recorded
limitation — *"nothing checks that a rationale is a real one"* — and is cited rather than restated
as new.

## F24 — A schema clause that could never add an obligation, grading the wrong axis

**Severity: low. Closed.**

`schemas/method-run-lineage.schema.yaml` carried three `allOf` branches. The third required
`input_hash`, `implementation_revision`, `configuration_hash` and `output_hash` of completed runs at
medium or high materiality. **Both its condition and its consequent are subsets of the first
branch's**, which requires those fields — and three more — of *every* completed run. It could never
add an obligation to any instance.

Inert, and not harmless. A schema is a **contract people read to learn what is required of them**,
and this one told a reader that a low-materiality completed run escapes fields it does not escape.
That is a contradictory-authority defect — the one this framework names most often — living inside a
published schema rather than between two documents.

**Which branch was the leftover could not be settled from history.** The public repository is one
squashed commit (`DR-23`), and `CHANGELOG.md` had never mentioned materiality at all. The design
evidence settled it:

> `schemas/override-record.schema.yaml:45-48` is the **only** live use of `materiality` in any
> schema, and it grades **approval** — a material override requires approval. It does not relax
> record completeness: `evidence_reference`, `rollback_approach` and `calculation_impact` are
> required of every override at every materiality.

So where the framework actually expresses this principle, **materiality decides who must sign off,
not how complete a record must be.** The run-lineage branch graded the wrong axis.

**Closed by removing it**, not by making it real. Narrowing the first branch so low-materiality runs
genuinely need less would loosen a published contract against the only place the principle is
stated, and would grade completeness by a **self-declared** field — an incentive to classify
everything `low`. No instance's validity moves, so the change is not breaking and the `$id` version
segment stays at `0.7.0`.

**What this says about the schemas generally**, and it is the reusable part: `materiality` is
required on both record types and, after this change, is consequential in exactly one of them.
Together with `F22` — where the only date on a gate exception records its creation and not its
expiry — the pattern is that **these schemas collect a field far more readily than they give it
force.** Worth checking before adding another.

## F23 — A drift guard matched on line shape rather than on the thing it guards

**Severity: medium. Closed.**

`tests/validate_contracts.py` asserts that the gate catalogue in the checker and the one in
`core/PREREQUISITE_GATES.md` do not drift apart. It found the catalogue with:

```python
re.findall(r'^    "([a-z0-9_]+)": "', CHECKER, re.MULTILINE)
```

That matches any four-space-indented `"key": "value"` line **anywhere in the file**. It was not
reading the gate catalogue; it was reading a line shape that the gate catalogue happened to have
exclusively. Adding `PATTERN_C_CONTROLS` — an unrelated module-level dictionary of the same shape —
put four non-gates into "the gate catalogue".

**It failed, and that is the only reason it was noticed**: the count went 19 → 23 and the assertion
tripped. The failure was luck, not design. Constructed and run rather than reasoned about:

| Mutation | Old guard | New guard |
|---|---|---|
| Drop one gate, add a **one-entry** dict of the same shape | **19 — passes** | 18 — fails |

The set the old guard then iterates has silently lost `component_library` and gained `not_a_gate`,
and every assertion downstream — including *"every catalogue gate is documented"* — runs against it
and passes. A false green on the guard whose whole purpose is to prevent silent divergence.

**Closed** by anchoring the search to the `GATE_CATALOGUE` block itself, so a dictionary elsewhere
in the file cannot be absorbed and a renamed or moved block fails loudly rather than matching
nothing. Verified in both directions: the real tree still reads 19 with `PATTERN_C_CONTROLS`
present, a removed gate reads 18, and a decoy dictionary changes nothing.

**Why it is recorded rather than quietly fixed.** This is the register's most-repeated shape — an
instrument whose negative result does not establish what it appears to — and this instance was
*inside an instrument*, in a guard written specifically to stop something drifting. `F14` was the
same shape in the placeholder check, `F21` in a control that named its own absence, `F12` in the
vendored-copy comparison. The lesson that generalises: **a check anchored on incidental syntax is
measuring a coincidence**, and it keeps passing after the coincidence ends.

## F22 — A deferral's revisit date was required to exist and never read again

**Severity: medium. Closed for deferrals; open for gate exceptions.**

`SP031` refuses a deferred control or gate that carries no `revisit_by`, on the stated grounds that
*"a deferral with no owner and no date is an omission wearing a decision's clothes."* Nothing then
ever read the date. Demonstrated before the fix:

```
revisit_by: "2020-01-01"   ->   PASS - all conformance checks satisfied.
```

Six years expired. The control that exists to prevent a permanent exclusion was creating one.

**Closed by `SP054`** for `adoption.deferrals[].revisit_by` and for deferred prerequisite gates. A
date that has passed raises a finding; a date within 30 days produces an advisory, mirroring how
`adoption.review_by` has always been treated; a malformed date fails, because a date that cannot be
parsed is not a deadline and the deferral would be permanent by accident.

**Why this is recording rather than judging.** The date was declared by the adopter. Comparing it
against today establishes whether a stated commitment has come due — it decides nothing on their
behalf. That distinction is what kept `I` (per-change risk classification) deferred and what keeps
gate exceptions out of scope below.

**Open: gate exceptions have no expiry mechanism at all.** `schemas/gate-exception.schema.yaml`
carries `raised_on`, and it is **optional** — a creation date, not a deadline. So an exception is
permanent by construction, and no amount of checking fixes that, because there is nothing declared
to check against. Giving exceptions an expiry means adding a field to a published contract, which is
a decision rather than an implementation detail, and it is not taken here.

That is the sharper version of this finding: deferrals were unenforced, exceptions are
**unenforceable**. The first was a gap in the checker; the second is a gap in the schema.

**Recorded about the sequence, not the code.** The scope review kept this item unconditionally and
ordered it *before* the first record validator. Patterns D, A and B were a larger substitution for
`G′` than that review anticipated, and this was overlooked in the process — an agreed sequence
departed from without anyone deciding to.

---

## Historical series — closed, cross-referenced, not renumbered

### `PRE-AUDIT-0.6.0/F1`–`F4` — `audit/PRE_AUDIT_FINDINGS_0.6.0.md`

Technical pre-audit of `0.6.0`, severity carried in each heading (`:45,66,78,88`): F1 HIGH
(application profile could not record adoption identity), F2 MEDIUM (producer validation record
stale), F3 MEDIUM (schema `$id`s used `https://example.invalid/`), F4 LOW (shipped templates did not
validate against their own schemas).

**All four remediated at `0.7.0`** — `CHANGELOG.md:60-82`. Carry the caveat the closure itself
records, `audit/VALIDATION_RESULTS.md:62-64`: the pre-audit *"was performed by a coding agent at the
maintainer's request. It was not independent, and it does not discharge the audit gate."*

### `PRIOR-AUDIT/C1`–`C4`, `M1`–`M7`, `O1`–`O4` — `audit/PRIOR_AUDIT_REMEDIATION.md`

Fifteen findings from the audit supplied 2026-08-21, severity carried in the prefix
(Critical / Material / Other). **Twelve are remediated. Three are not, and nothing was tracking
them until this register:**

| Code | Disposition as recorded | Status here |
|---|---|---|
| `PRIOR-AUDIT/M6` | *"Partially remediated: … native enforcement remains application-owned."* (`:16`) | **Open — partial** |
| `PRIOR-AUDIT/M7` | *"Partially remediated: … Formal release ownership remains a human adoption decision."* (`:17`) | **Open — partial** |
| `PRIOR-AUDIT/O4` | *"Clarified: …"* — clarified, not remediated (`:21`) | **Open — clarified only** |

They keep their original codes and are not renumbered. The re-audit that would close them remains
outstanding (`audit/VALIDATION_RESULTS.md:59-60`), and
`audit/CHATGPT_ENTERPRISE_AUDIT_PROMPT.md:94` still asks a future auditor to disposition all fifteen.

### Uncoded historical items

Recorded so they are not lost, without retrospective codes — assigning numbers to items nobody has
ever cited would manufacture citations for no benefit:

- `org/decisions/DR-8.md:87-95` — the `SDS036` incidental: a finding code cited in a deleted document
  and emitted by nothing. No action followed; the citation went with the file.
- `org/decisions/DR-5.md:100-143` — *"Unassigned — not yet a numbered finding"*: raised, investigated,
  and **withdrawn** (`:113-114`), with the residual question answered at `0.13.0` in an annotation
  left in place rather than rewritten. Not a finding; recorded as raised-and-withdrawn.
- `audit/PRIOR_AUDIT_REMEDIATION.md:27-32` and `:38-44` — fourteen remediation bullets across two
  batches, never individually coded by the audits that produced them.

---

## Observations — not findings

- **A bare `python3` can carry package versions older than this project's own pins, with no error
  until something is actually run against them.** Discovered while building `ACT-020`
  (`org/decisions/DR-32.md`): the machine used had no `pip` at all, and apt-installed
  `jsonschema==4.10.3`/`PyYAML==6.0.1` — both older than `4.26.0`/`6.0.3`. This is not `F21` again —
  the pin is correctly declared, and every workflow correctly installs it — it is the same class of
  divergence one layer closer to the developer, on a machine nothing in CI ever touches. Not a
  finding, because nothing in the framework failed: a repository-local `.venv`, built once with the
  pinned versions, is the ordinary remedy and is what every verification command in `DR-32` used
  once this was noticed. Recorded so the next session on a fresh machine checks rather than assumes.
- **`ACT-<n>` identifiers have no register.** `ACT-200` and `ACT-201` appear in commit subjects and
  in **no tracked file**. The activity register that would give them meaning is unlanded work
  (`org/RELEASE_PLAN.md`, item 0; `DR-13`). This is the `SDS036` shape — an identifier cited before
  the thing it names exists — and is recorded here as an observation rather than a finding, because
  the register it points at is already scheduled.

## Limitations of this register

- **The external review's own output was not available to the session that built this register.**
  `F6`–`F9` are recorded from the claims named in the work packet and verified independently against
  the code. The review raised seven items; four are represented here. **Anything it raised beyond
  those is not in this register**, and this file does not claim otherwise.
- **The review did not report what it tried and failed to break.** A review that reports only its
  hits gives no basis for judging coverage: a reader cannot distinguish "these are the weaknesses"
  from "these are the weaknesses that happened to be found". Recorded as a limitation of the review,
  not as a finding about the code.
- **No finding here has been independently confirmed.** Every entry was verified against the source
  by the same party that maintains it. `org/decisions/README.md:16-18` applies: no independent
  validator exists for this repository.
- **Severity is a judgement, not a measurement.** Each entry states its reasoning so the judgement
  can be disagreed with.
