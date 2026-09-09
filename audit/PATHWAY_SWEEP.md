# Adoption pathway sweep — a hand-off packet for another session

**What this is.** An executable brief for a separate agent session to walk Surfaceplate's adoption
pathways against deliberately awkward repositories and environments, and report where it breaks or
behaves other than as documented. It exists because the suites that already run — fourteen of them,
including a 208-case combinatorial matrix — walk **decisions** exhaustively and had never varied the
**repository** the decisions were made about. `F132` was found by a human on the first screen of the
first walkthrough, on a real repository, after 45,266 matrix checks passed.

**What it is not.** Not exhaustive, and the difference is the point. The state space is
`repository shape × environment × command sequence × decision path`. The matrix covers the last
dimension and this packet covers the first three, at the shapes most likely to be real. A clean
report from this packet means *"these pathways were tried and behaved as documented"* — never
*"Surfaceplate works"*.

**Who runs it.** Any capable agent session, in its own checkout, not sharing a working tree with
another session (Topic 11 — one writer per tree). The report comes back to the maintainer's session
for adjudication and for allocation of finding numbers.

---

## 1. The rules that make the report worth reading

These are not style preferences. A sweep that ignores them produces a document that is more
dangerous than no document, because it reads as assurance.

1. **Never adjust an expectation to match what you got.** If output differs from what this packet
   says to expect, that is the finding. Report the difference and its cause. Do not decide the
   packet meant something else.
2. **A negative finding must establish that the observation could have succeeded.** *"No error
   appeared"* and *"I did not look where the error would be"* return the same thing. Say how you
   would have seen it.
3. **Label every claim.** `FACT` — you ran it and this is the output. `INFERENCE` — you reasoned
   it. `EVIDENCE GAP` — you could not establish it. A cause you did not reproduce is `INFERENCE`,
   however obvious.
4. **Paste raw output, not a summary of it.** Exit codes as numbers. Commands verbatim, including
   the flags. The adjudicating session re-reads your evidence and will disagree with your verdicts
   where the evidence does not carry them; it cannot do that from a paraphrase.
5. **Check what the observation actually examined.** The four ways it fails: wrong object, wrong
   interval, wrong granularity, and — the one that never looks like an error — **wrong artefact**,
   a right answer about a near-identical sibling. You are testing an *installed copy* under
   `.standards/`; the source tree is a different object.
6. **Do not fix anything.** Not the tool, not the docs, not a scenario that looks mis-specified.
   Report it. A fix applied mid-sweep changes the thing being measured and destroys every later
   result's baseline.
7. **Do not allocate `F<n>` or `SP<n>` numbers.** Those are assigned in
   `org/FINDINGS.md` by the maintainer's session. Number your findings `PW-01`, `PW-02`, … in the
   order you found them. Inventing an identifier that does not exist is prohibited by the standard
   you are testing.

## 2. Hard boundaries

- **Never write to `~/github/`.** Every scenario works on a *clone* under the scratch root. If a
  scenario seems to require editing a real repository, that is a defect in the scenario — report it
  and skip.
- **`~/github/mnemosyne` is read-only and `~/github/plyego` is out of scope entirely.** Do not
  clone, read, or reference either.
- **Do not push, open pull requests, publish, or send anything anywhere.** Nothing in this packet
  requires a network call except installing the package and one `pypi.org` currency check.
- **Do not modify the surfaceplate checkout you install from.** Install the built package; treat the
  source tree as read-only.

## 3. Setup

Record the exact commit under test in the report header. Every result is attributable to it or it is
attributable to nothing.

```bash
SWEEP=~/surfaceplate-sweep          # scratch root; anything under it is disposable
SP=~/github/surfaceplate            # the checkout under test — READ ONLY
rm -rf "$SWEEP" && mkdir -p "$SWEEP/repos" && cd "$SWEEP"
git -C "$SP" rev-parse HEAD         # <- put this SHA in the report header
git -C "$SP" status --short         # <- and note whether the tree was dirty

python3 -m venv .venv && . .venv/bin/activate
pip install --disable-pip-version-check -q "surfaceplate[adopt] @ file://$SP"
surfaceplate --version
```

Two environment facts to record before any scenario, because both change what you will see:

```bash
git config --show-origin --get-all core.hooksPath   # this machine has a GLOBAL one set
git --version
python3 -V
```

**A note on the wizard.** `surfaceplate adopt` needs a terminal you do not have. Two supported
routes go through the same code and need none: `adopt --propose` writes the proposal and the answers
record; `adopt --answers FILE` replays a completed answers record and writes the profile. Use those.
The interactive interface itself is covered by `tests/test_adopt_tui.py`,
`tests/test_adopt_snapshots.py` and `tests/test_adopt_matrix.py` and is **not** this packet's
subject. Where a scenario says "run the wizard", it means `--propose` and then `--answers`.

## 4. Calibration — run these first, and stop if they do not fire

Three defects are known to exist. If the sweep does not reproduce all three, it is not sensitive
enough for its clean results to mean anything, and the run should stop and say so rather than
continue. **This is rule 2 applied to the sweep as a whole.**

| | Scenario | Must observe |
|---|---|---|
| **CAL-1** | `surfaceplate doctor --repo <any fresh clone>` on this machine | A `warn` line naming the **global** `core.hooksPath`, saying the installer stops rather than replace it |
| **CAL-2** | `surfaceplate adopt --target <installed repo>` with stdin closed (`</dev/null`) | Exit **3**, and the message names `--propose` |
| **CAL-3** | `adopt --propose` on a repository with **no dependency manifest of any kind** (see `A1`) | The proposal cannot be completed without naming a lock file that does not exist — `F132` |

Report each as fired / did not fire, with output. **If any did not fire, say so at the top of the
report and treat every subsequent "no defect found" as unestablished.**

## 5. The scenarios

Each is: **set up**, **do**, **expect**, **what would falsify the expectation**. Where "expect" is
uncertain, it says so — an uncertain expectation is not a licence to accept whatever happens; it is
an instruction to report what happened and say the packet did not predict it.

Build the fixture repositories once, under `$SWEEP/repos`. Every one is a fresh `git init` with
`user.email`/`user.name` configured locally and `commit.gpgsign false`, unless it says otherwise.

### Axis A — repository shape

The axis `F132` exposed. Every existing fixture in every suite has had something to name.

- **A1 — no dependency manifest at all.** A repository of Markdown and YAML only: no
  `package.json`, `pyproject.toml`, `requirements*.txt`, `go.mod`, `Gemfile`, `pom.xml`,
  `Cargo.toml`, `composer.json`. Install, commit, `adopt --propose --level essential`.
  *Expect:* the known `F132` dead end (CAL-3). *Also record:* what `--propose` writes when it cannot
  complete — a partial proposal, an error, or a file naming a path that does not exist. **That last
  outcome would be a new and worse finding than `F132` itself.**
- **A2 — a manifest but no lock file.** `pyproject.toml` with dependencies, no `poetry.lock` or
  equivalent. *Expect:* the lock-file field is asked. *Falsifier:* the manifest is silently proposed
  *as* the lock file — pinning a manifest is not pinning a lock.
- **A3 — no commits.** `git init` and nothing else. Install, check.
  *Expect:* not predicted by this packet. Record exactly what happens, including whether the history
  audit reports a negative result it could not have established (`F31`'s shape).
- **A4 — shallow clone.** `git clone --depth 1` of a repository with history. Install, check.
  *Expect:* the history audit must not report "nothing wrong" from a one-commit window. `F31` is the
  finding that installed `fetch-depth: 0` in the workflow; the local path is the question here.
- **A5 — not a git repository.** A plain directory. `install`, then `check`.
  *Expect:* a usage-level refusal that says so. *Falsifier:* a traceback, or a partial install left
  on disk.
- **A6 — a subdirectory of a repository.** `git init` at the root; install into `sub/project`.
  *Expect:* not predicted. The interesting questions: which root does the checker use for `git`
  operations, does `is_tracked` resolve against the right root, and does the installed workflow land
  where CI would find it.
- **A7 — occupied standard-owned paths.** The repository already has its own `AGENTS.md` with
  content, its own `.github/instructions/team.instructions.md`, and its own
  `.githooks/pre-commit`. Install without `--replace-existing`, then read `RECONCILIATION.md` and
  follow it. *Expect:* the installer stops before writing anything, and `AGENTS.md`'s own content
  survives outside the managed block. *Falsifier:* anything of the adopter's is overwritten or
  lost — the most serious class of defect this packet can find.
- **A8 — an existing profile.** `governance/application-profile.yaml` already present and complete.
  Install, then install again. *Expect:* never overwritten. *Falsifier:* any change to its bytes.
- **A9 — detached HEAD.** *Expect:* not predicted; record.
- **A10 — awkward path.** A repository whose path contains a space and a non-ASCII character.
  Install, check, `doctor --report`. *Falsifier:* a crash, or a path mangled in output.
- **A11 — already installed at a newer version.** Hand-edit `.standards/VERSION` and
  `INSTALL.json`'s `standard_version` to `99.0.0`, then install. *Expect:* the tool notices the
  install is ahead of it rather than silently downgrading. Note that hand-editing `VERSION` is
  exactly what `_installed_version`'s docstring says the record exists to defeat — record which of
  the two the tool believed.
- **A12 — install twice, unchanged.** Install, record `MANIFEST.sha256` and `INSTALL.json`, install
  again, compare. *Expect:* byte-identical except any field that legitimately records the run.
  *Falsifier:* an unexplained digest change, which would mean the install is not reproducible.

### Axis B — environment

- **B1 — global `core.hooksPath` set.** This machine already has one (CAL-1). Install **without**
  `--no-hooks` or `--chain`. *Expect:* the installer stops, writes nothing, and offers the three
  routes. *Falsifier:* anything written, or the global setting changed.
- **B2 — `--chain` where the global hook delegates elsewhere.** This machine's global `pre-commit`
  delegates to `$(git rev-parse --git-common-dir)/hooks/pre-commit`, **not** to `.githooks/`.
  Install `--chain`, declare `adoption.hook_chain` in the profile, commit, check.
  *Expect:* `SP038` — the declared chain does not in fact reach the gate, and `DR-66` verifies by
  execution rather than by reading. *Then* add a delegating shim at
  `$(git rev-parse --git-common-dir)/hooks/pre-commit` that execs `.githooks/pre-commit`, and check
  again. *Expect:* `SP038` clears. **Both halves are required**: a check that only ever returns one
  answer has not been shown to distinguish anything.
- **B3 — `textual` absent.** A second virtualenv with `surfaceplate` but **not** the `adopt` extra.
  Run `adopt`. *Expect:* a message naming the exact install command, not an `ImportError`.
- **B4 — Python 3.9.** `pyproject.toml` declares `requires-python = ">=3.9"` and CI tests **only
  3.12**. If a 3.9 interpreter is available, install into it and run `--version`, `install`, `check`.
  *Expect:* the packet does not predict this and considers it a live suspicion. A `SyntaxError` or
  `TypeError` from a runtime `X | Y` annotation, or from any 3.10+ syntax, is a finding against the
  declared floor. If no 3.9 interpreter is available, record `EVIDENCE GAP` — **do not install one
  and do not infer the answer from reading the source.**
- **B5 — no network.** With `https_proxy=http://127.0.0.1:1 http_proxy=http://127.0.0.1:1`, run
  `check --currency`, `doctor`, `doctor --report`. *Expect:* `check --currency` reports
  `currency: UNKNOWN` and **does not change the exit code**; `doctor --report` is documented as
  offline and must make no request at all. *Falsifier for the last one:* any wording indicating a
  request was attempted.
- **B6 — `LANG=C` / `LC_ALL=C`.** Run `check` and `doctor` on a repository whose output contains the
  non-ASCII characters this project uses (`—`, `…`, `·`). *Falsifier:* a `UnicodeEncodeError`.
- **B7 — `git` not on `PATH`.** Run `check` and `doctor`. *Expect:* a stated inability, not a
  traceback, and no negative finding asserted from a git command that could not run.

### Axis C — command sequence and lifecycle

- **C1 — `adopt` before `install`.** *Expect:* refused with a message saying to install first.
- **C2 — `check` before `install`.** *Expect:* exit **2** and `SP001`.
- **C3 — the documented happy path, verbatim.** Every command in `INSTALL.md` in the order it gives
  them, on a fresh repository, **copied from the document rather than from memory**. Any command
  that does not run as written is a finding against the document, which is the standard's own `S3`.
- **C4 — tamper.** After a clean install: (a) change one byte in a vendored `.standards/topics/*.md`;
  (b) delete a vendored file; (c) edit the managed block inside `AGENTS.md`; (d) hand-edit
  `INSTALL.json`'s `framework_digest`. Run `check` after each and restore between.
  *Expect:* each is reported, and reported as the right kind — modification, deletion, block
  alteration, record mismatch. *Falsifier:* any one that passes, or that is reported as a different
  kind than it is.
- **C5 — grace expiry.** Set `grace_expires` in `INSTALL.json` to a past date on a repository with
  an incomplete profile; run `check`. *Expect:* `FAIL`, exit 1, where the same repository inside its
  window gave `WARN`, exit 0. Then run with `--no-grace` inside the window and expect the same
  failure. **Both directions.**
- **C6 — `--agents` narrowing, then widening.** Install `--agents claude`; confirm no
  `.github/instructions/` and no `.github/skills/`; check, and confirm the check *says* the channel
  was declined. Then install `--agents copilot` over it. *Expect:* not predicted — record whether
  the Claude channel is removed, left, or left and no longer integrity-checked. **A file left behind
  that nothing checks is the worst of the three.**
- **C7 — `--no-hooks`, then hooks.** Install `--no-hooks`, commit, check (expect the declination
  reported). Then install again without `--no-hooks` on a machine where the global hooks path is
  set. *Expect:* per `B1`.
- **C8 — `--propose` then `--answers`.** `adopt --propose --level standard`, complete the answers
  record by hand, `adopt --answers <file>`, then `check`. *Expect:* a profile that passes, and an
  answers record that records where each value came from. *Falsifier:* a written profile the
  checker rejects — the wizard writing something its own checker refuses is `F66`'s defect.
- **C9 — `--edit`.** Change one field of a written profile with `--edit ... --because ...`; confirm
  the edit and its reason are recorded beside the profile. Then try `--edit` **without**
  `--because`. *Expect:* refused, or recorded as unexplained — not silently accepted.
- **C10 — removal.** Try to uninstall. There is no documented command. Record what an adopter who
  wants Surfaceplate out of their repository is expected to do, and whether any document says.
  **The absence of an answer is the finding, if there is no answer.**

### Axis D — the documents, run rather than read

- **D1.** Every fenced command in `README.md` and `INSTALL.md`, executed verbatim on a clean
  repository. Report each `PASS` / `FAIL` with its output. `scripts/front_door.sh` already does a
  subset in CI; this is the whole set, and any divergence between the two is itself worth reporting.
- **D2.** `INSTALL.md`'s "Frequently asked" section: for each answer that states a fact about
  behaviour, do the thing and say whether the answer is true.
- **D3.** `RECONCILIATION.md`'s procedure, followed literally against `A7`. *Falsifier:* a step that
  cannot be carried out as written.

## 6. What to report

One Markdown document. Header first:

```
Commit under test:   <sha>, tree clean/dirty
Tool version:        <surfaceplate --version>
Python / git / OS:   <versions>
Calibration:         CAL-1 fired / did not fire; CAL-2 …; CAL-3 …
Scenarios attempted: <n>; not attempted: <list, with the reason for each>
```

Then, for **every** scenario, in order — including the ones where nothing went wrong, because a
scenario that is silently dropped is indistinguishable from one that passed:

```
### <id> — <one line>
Commands:   <verbatim, with flags>
Exit codes: <numbers>
Output:     <raw, trimmed only where it repeats>
Verdict:    AS DOCUMENTED / DIFFERS / NOT PREDICTED / NOT ATTEMPTED
```

Then the findings, most severe first:

```
### PW-nn — <title naming the defect, not the symptom>
Severity:    high / medium / low, and why
Reproduce:   the minimal commands, from the setup in §3
Observed:    FACT — what happened
Expected:    what this packet said, or what the document under test says, quoted
Reach:       does this affect adopters, or only this repository's own workflow?
Cause:       INFERENCE unless you reproduced it; say which
```

**Severity guidance.** `high` = an adopter loses their own content, or a control passes while not
holding, or a documented path cannot be completed at all. `medium` = a documented path completes but
not as documented. `low` = wording, ordering, or an ugly but correct outcome.

**Finish with the two lists that make the report honest:**

- **What was not tested**, and why — every scenario skipped, every `EVIDENCE GAP`.
- **What would have caught each finding earlier**, where you can say. A finding whose remedy is
  "someone should have noticed" is worth less than one that names the check that was missing.

## 7. When something breaks

Report it and continue with the next scenario. Do not fix, do not work around, do not re-run with
different flags until it passes and report only that run. If a scenario cannot proceed because an
earlier one left the fixture broken, rebuild the fixture from §3 and say that you did.

If the **same** scenario fails twice for what looks like the same reason, stop and question the
scenario rather than attempting it a third time. State what you tried, what it was supposed to
establish, and what actually happened. The gap between those three is the finding.

---

*Written under `ACT-077` for the 1.0 validation pack. The packet is a work packet in the standard's
own sense (Topic 3): objective, non-goals, bounded scope, acceptance criteria, verification
commands, and the escalation rule that an agent reports rather than decides.*
