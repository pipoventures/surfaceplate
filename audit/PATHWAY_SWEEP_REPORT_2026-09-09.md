# Adoption pathway sweep — report

Executed against `audit/PATHWAY_SWEEP.md` (written under `ACT-077`) by a separate agent session, in
its own scratch root, with the checkout treated as read-only. Nothing was fixed. No `F`/`SP` numbers
were allocated; findings are `PW-nn`. Raw logs for every scenario are under
`~/surfaceplate-sweep/log/` (one file per scenario id; `run`/`runsh` lines show the verbatim command,
the merged stdout+stderr, and `exit=<n>`).

```
Commit under test:   30bba4405fce4f49510f54bc8a824513face1d35 (branch claude/act-076-h21-and-walkthrough)
                     Tree: CLEAN at first reading (10:4xZ); DIRTY from ~10:50Z onward and still changing
                     at the end (23 modified files + org/decisions/DR-73.md untracked, none by this sweep —
                     a peer session was editing the checkout throughout; see "Deviations from §3").
                     Every result below is attributable to 30bba44 via a clone pinned to that SHA.
Tool version:        surfaceplate 0.17.0  (pip-installed from file://~/surfaceplate-sweep/source, pinned; installed
                     framework digest ceffdcf76ae5440ceae16c154893c3771455db0ad7aaa36d245bbe67db4c8d7f)
Python / git / OS:   Python 3.12.3 (only interpreter present) / git 2.43.0 / Ubuntu 24.04.4 LTS, WSL2 6.18.33.2
Environment facts:   core.hooksPath GLOBAL = /home/mps2210/.config/git/hooks (file:/home/mps2210/.gitconfig);
                     its pre-commit is delegation-only to $(git rev-parse --git-common-dir)/hooks/pre-commit.
                     strace absent. pypi.org reachable. No python3.9.
Calibration:         CAL-1 fired; CAL-2 fired; CAL-3 fired (see nuance in its entry)
Scenarios attempted: 35 of 36 (CAL-1..3, A1–A12, B1–B3, B5–B7, C1–C10, D1–D3)
Not attempted:       B4 (no Python 3.9 interpreter; packet forbids installing one) — EVIDENCE GAP
                     D1 block I4 `sudo apt install …` (privileged, machine-changing) — NOT ATTEMPTED
                     D2 Q5 (needs GitHub Actions on a remote) — EVIDENCE GAP
Sweep window:        2026-09-09 10:50:05Z → 11:05:05Z (readings in log/00-setup-readings.txt, log/99-end-readings.txt)
```

## Deviations from §3, stated up front

1. **Installed from a pinned clone, not from `file://$SP`.** `pip install` from a `file://` path
   builds the *working tree*. At setup the checkout was already dirty (`surfaceplate/check_conformance.py`,
   `surfaceplate/rules.py`, four `adopt/*.py` files, uncommitted, changing while read). Installing from it
   would have attributed results to `30bba44` while testing something else — the packet's rule 5 "wrong
   artefact". So: `git clone ~/github/surfaceplate ~/surfaceplate-sweep/source && git checkout 30bba44…`,
   verified `status --short` empty, and installed from `file://~/surfaceplate-sweep/source`. Cloning reads
   the checkout and writes nothing to it. Axis D documents were read from the pinned clone.
   `FACT`: pinned clone HEAD `30bba44…`, status `[]` at start and at end.
2. **`--no-hooks` on every install whose subject was not the hook path.** On this machine a bare
   `install` stops with exit 4 (that is B1). Each entry says which flag it used. A7 was run under both
   `--chain` and `--no-hooks`; B1, B2, C7 use the flags the packet names.
3. **D1's `pip install 'git+https://github.com/pipoventures/surfaceplate@main'`** was run verbatim in a
   separate venv. `FACT`: it resolved to `16b26fc79cb856b80cb97d04a4304a773dd71ecb` (GitHub `main`), version
   `0.17.0` — not the commit under test. Results in that venv are attributable to `16b26fc`, and are so
   marked.
4. **Instrument note.** A shell wrapper (`lib.sh`: `run`, `runsh`, `mkrepo`) recorded commands. Its first
   version masked the exit code of *piped* `runsh` commands (the exit printed was the pipe's last stage).
   All exit codes quoted in this report for piped commands were re-taken after adding `pipefail`
   (D1 entries; C3). Unpiped commands were never affected. My own error in the first C4 run is recorded
   in that entry; the scenario was rebuilt per §7.
5. **Hard boundaries.** `FACT`: `~/.gitconfig` sha256 `645f7328…` identical at start and end; global
   `core.hooksPath` unchanged; nothing under `~/github` was written by this sweep (only `git clone` /
   `git pull` reads of `~/github/surfaceplate`). `find ~/github -newer <start>` lists files under
   `surfaceplate`, `plyego*` modified during the window — by peer sessions, not this one; this sweep never
   referenced `mnemosyne` or `plyego`. No push, PR, or network call beyond: the setup `pip` (PyPI
   dependencies), D1's GitHub install, and one `--currency` request.
6. **Concurrency.** Six peer Claude sessions were live on this machine; one ("surfaceplate udpate") was
   busy on the checkout. This sweep's only writes were under `~/surfaceplate-sweep`.

---

## Calibration

### CAL-1 — `doctor` names the global `core.hooksPath` and says the installer stops
Commands:
```
$ surfaceplate doctor --repo /home/mps2210/surfaceplate-sweep/repos/cal1
```
Exit codes: 0
Output (trimmed to the line that matters; full in log/CAL-1.log):
```
warn  core.hooksPath (global) /home/mps2210/.config/git/hooks - the installer stops rather than replace it; install with --no-hooks, or unset it for this repository
DOCTOR=OK  (2 warning, 15 checks)
```
Verdict: **FIRED** — AS DOCUMENTED.

### CAL-2 — `adopt` with stdin closed exits 3 and names `--propose`
Commands:
```
$ surfaceplate install --target /home/mps2210/surfaceplate-sweep/repos/cal2 --no-hooks     # exit 0
$ surfaceplate adopt --target /home/mps2210/surfaceplate-sweep/repos/cal2 </dev/null
```
Exit codes: 0; **3**
Output:
```
`adopt` is an interactive, full-screen wizard and needs a real terminal; this one is not attached to a TTY (output is piped, redirected, or running in CI).

  Run it directly in a terminal:  surfaceplate adopt --target /home/mps2210/surfaceplate-sweep/repos/cal2
  Or without one:                 surfaceplate adopt --propose --target /home/mps2210/surfaceplate-sweep/repos/cal2

Nothing was read or written, and any saved draft in that repository is untouched.
```
Verdict: **FIRED** — AS DOCUMENTED. (Note for B3: the `textual` import preflight runs *before* this
check, so without the `adopt` extra the exit is 2, not 3.)

### CAL-3 — `adopt --propose` on a repository with no dependency manifest (fixture A1)
Commands:
```
$ git -C /home/mps2210/surfaceplate-sweep/repos/a1 ls-files
README.md
config.yaml
docs/guide.md
$ surfaceplate install --target /home/mps2210/surfaceplate-sweep/repos/a1 --no-hooks      # exit 0, then committed
$ surfaceplate adopt --propose --target /home/mps2210/surfaceplate-sweep/repos/a1 --level essential
```
Exit codes: 0; 0; 0
Output:
```
Proposed: /home/mps2210/surfaceplate-sweep/repos/a1/governance/application-profile.answers.yaml
Preview : /home/mps2210/surfaceplate-sweep/repos/a1/governance/application-profile.proposed.yaml
Nothing else was written. Complete every needs-human line in the answers record, then run:
    surfaceplate adopt --target /home/mps2210/surfaceplate-sweep/repos/a1 --answers /home/mps2210/surfaceplate-sweep/repos/a1/governance/application-profile.answers.yaml
```
The answers record (log/CAL-3.log, full text) carries:
```
  controls.dependency_lock.implementation_reference: needs-human
```
with no `choices:` hint for that line. Replay with every other line completed and this one left as is:
```
$ surfaceplate adopt --target …/a1 --answers …/a1/governance/answers-i-undecided.yaml
1 line(s) in the answers record still say 'needs-human': controls.dependency_lock.implementation_reference. Complete them - they are the decisions only a human can make - and run --answers again.
exit=1
```
Replay naming a lock file that does not exist:
```
$ surfaceplate adopt --target …/a1 --answers …/a1/governance/answers-ii-nonexistent.yaml     # poetry.lock
Refusing to write: the answers record is incomplete for this repository at level essential: ScriptedInterview: the review refuses to write: controls.dependency_lock.implementation_reference: Nothing exists at that path in this repository.. Run `surfaceplate adopt --propose --level essential` for a complete record.
This is the wizard's own safety check, not the checker. Nothing was written.
exit=1
```
Verdict: **FIRED**. `FACT`: the record cannot be replayed without a path, and a path that does not exist
is refused — the `F132` dead end. Nuance recorded under A1: it is a dead end only for an honest answer
(see A1 and PW-03), and the refused replay above wrote a file despite saying it did not (PW-02).

**All three calibration cases fired.** Clean results below are therefore established to the extent the
packet's rule 2 requires.

---

## Axis A — repository shape

### A1 — no dependency manifest at all
Commands (after CAL-3; same fixture):
```
$ surfaceplate adopt --target …/a1 --answers …/a1/governance/answers-probe.yaml     # lock = docs/guide.md
…
PASS - all conformance checks satisfied.
exit=0
$ grep -n -A4 'dependency_lock:' …/a1/governance/application-profile.yaml
57:  dependency_lock:  # checked against this repository by the conformance checker
58-    decision: required
59-    rationale: Supply-chain exposure exists regardless of output materiality.
60-    implementation_reference: docs/guide.md
$ cat …/a1/docs/guide.md
# Guide
$ surfaceplate check --repo …/a1
  - dependency_lock: verified against docs/guide.md
PASS - all conformance checks satisfied.
exit=0
```
Exit codes: 0; 0
What `--propose` wrote when it could not complete (packet asked): an answers record with the lock line
`needs-human` and no candidate, plus a preview `application-profile.proposed.yaml` containing
`implementation_reference: needs-human`. **It did not write a path that does not exist** (the outcome the
packet flagged as worse than F132 did not occur). Two things it did write, `FACT`:
```
# … Every `needs-human` below is a decision for a human, and 0 undecided gate(s) are left out entirely: .
…
data_classification: public         # public | internal | confidential | restricted
risk:
  relied_on_outside_team: false
  material_quantitative_output: false
```
while the answers record has those three as `needs-human` — the preview substitutes silent defaults.
Verdict: **DIFFERS** (from F132's "cannot produce a conformant profile at any level"): a tracked,
non-empty Markdown file is accepted as the dependency lock and the checker reports it *verified*. This is
the mechanism F132's own text describes for the matrix; here it is shown on the real pathway. See PW-03,
PW-16. Also the stale-draft defect (PW-02) was found on this fixture.

### A2 — a manifest but no lock file
Commands:
```
$ surfaceplate install --target …/a2 --no-hooks      # exit 0, committed
$ surfaceplate adopt --propose --target …/a2 --level essential
$ grep -n -A3 'dependency_lock' …/a2/governance/application-profile.answers.yaml
80:  controls.dependency_lock.implementation_reference:
81-    value: pyproject.toml
82-    origin: discovered
83-    detail: 'found: pyproject.toml'
$ grep -n -A3 'dependency_lock' …/a2/governance/application-profile.proposed.yaml
65-    implementation_reference: pyproject.toml
```
Exit codes: 0; 0; 0; 0
Verdict: **DIFFERS** — the falsifier fired. The manifest is proposed *as* the lock, origin
`discovered`, not asked. PW-03.

### A3 — no commits
Commands:
```
$ surfaceplate install --target …/a3 --no-hooks     # exit 0
$ surfaceplate check --repo …/a3
```
Exit codes: 0; 0
Output (trimmed):
```
Advisory (2) - not a failure:
  - the pre-commit hook was declined at install: …
  - Git history was not available, so none of the 1 auditable gate(s) were checked against the commits that crossed them. This is an absence of evidence, not evidence of conformance.
Adoption completeness findings (15): [SP016 ×6, SP024, SP020, SP046, SP051, SP048, SP049, SP032, SP033, SP037 — template placeholders]
WARN - adoption is incomplete, but grace expires 2026-10-09 (30 day(s) remaining).
```
Verdict: **NOT PREDICTED** — recorded. The history audit reports its own inability rather than a
negative (the `F31` shape does not recur here).

### A4 — shallow clone
Commands:
```
$ git clone -q --depth 1 file:///home/mps2210/surfaceplate-sweep/repos/a4-origin a4    # origin has 4 commits
$ git -C …/a4 rev-parse --is-shallow-repository ; git -C …/a4 log --oneline | wc -l
true
1
$ surfaceplate install --target …/a4 --no-hooks     # exit 0, committed
$ surfaceplate check --repo …/a4
```
Exit codes: 0; 0; 0
Output (line 9 of the check):
```
  - This is a SHALLOW clone, so the 1 auditable gate(s) were checked against only the commits it contains - which may be one. A history audit that found nothing here has established nothing. Fetch full history (for GitHub Actions, actions/checkout with fetch-depth: 0) if this run is meant to be evidence.
WARN - adoption is incomplete, but grace expires 2026-10-09 (30 day(s) remaining).
```
Verdict: **AS DOCUMENTED** — the local path reports the shallow window explicitly.

### A5 — not a git repository
Commands:
```
$ surfaceplate install --target /home/mps2210/surfaceplate-sweep/repos/a5
error: target /home/mps2210/surfaceplate-sweep/repos/a5 is not the root of a readable Git working tree
exit=2
$ ls -la …/a5          # only README.md; nothing written
$ surfaceplate check --repo …/a5
  [SP001] Surfaceplate is not installed
FAIL - Surfaceplate is not installed in this repository.
exit=2
```
Verdict: **AS DOCUMENTED** — usage-level refusal, no partial install. (Note: `check` on a non-repository
says "not installed" rather than "not a repository"; correct, if less specific.)

### A6 — a subdirectory of a repository
Commands:
```
$ surfaceplate install --target /home/mps2210/surfaceplate-sweep/repos/a6/sub/project --no-hooks
error: target /home/mps2210/surfaceplate-sweep/repos/a6/sub/project is not the root of a readable Git working tree
exit=2
$ git -C …/a6 status --short         # empty
$ surfaceplate check --repo …/a6/sub/project
  [SP001] Surfaceplate is not installed
exit=2
```
Verdict: **NOT PREDICTED** — recorded. The installer requires the worktree root, so the packet's three
questions (which root, `is_tracked`, where the workflow lands) do not arise: nothing is written.

### A7 — occupied standard-owned paths
Fixture: own `AGENTS.md` (3 lines), own `.github/instructions/team.instructions.md`, own executable
`.githooks/pre-commit`; sha256 recorded before.
Commands:
```
$ surfaceplate install --target …/a7 --chain
STOPPED - this repository already has its own files at paths the standard owns:
  .githooks/pre-commit
Installing would overwrite them. That is a decision for the repository owner, not
for the installer, …
Nothing has been written.
exit=3
$ git -C …/a7 status --short         # empty; all three sha256 unchanged
$ surfaceplate install --target …/a7 --no-hooks
exit=0
$ git -C …/a7 status --short
 M AGENTS.md
?? .claude/  ?? .github/copilot-instructions.md  ?? .github/instructions/01-…12-….instructions.md  ?? .github/skills/  ?? .github/workflows/  ?? .standards/  ?? governance/
$ sha256sum AGENTS.md .github/instructions/team.instructions.md .githooks/pre-commit
623f5bb4…  AGENTS.md                                   (changed: block appended)
d6a67f22…  .github/instructions/team.instructions.md   (unchanged)
816b375a…  .githooks/pre-commit                        (unchanged)
$ head -5 AGENTS.md
# Our agents file

Keep our house style. Never delete a migration. Ask before touching billing/.

<!-- BEGIN SURFACEPLATE -->
```
Exit codes: 3; 0
Verdict: **AS DOCUMENTED** for the collision the installer recognises (`--chain`: stops, writes nothing).
Under `--no-hooks` there is no collision to stop on, so it installs; the adopter's `AGENTS.md` text
survives above the managed block, `team.instructions.md` is untouched (the installer owns twelve named
files, not the `*.instructions.md` glob that `RECONCILIATION.md` claims — PW-14). Nothing of the adopter's
was lost. `FACT`.

### A8 — an existing profile
Commands:
```
$ sha256sum …/a8/governance/application-profile.yaml     # e5d7c52b…  (C8's passing profile, committed)
$ surfaceplate install --target …/a8 --no-hooks
  keep    governance/application-profile.yaml  (yours; never overwritten)
exit=0
$ sha256sum …                                              # e5d7c52b…
$ surfaceplate install --target …/a8 --no-hooks           # exit 0
$ sha256sum …                                              # e5d7c52b…
```
Verdict: **AS DOCUMENTED** — byte-identical after two installs.

### A9 — detached HEAD
Commands:
```
$ git -C …/a9 status | head -1        # HEAD detached at 71202af
$ surfaceplate install --target …/a9 --no-hooks     # exit 0, committed on the detached HEAD
$ surfaceplate check --repo …/a9                    # WARN, exit 0; no mention of the detached state
$ surfaceplate adopt --propose --target …/a9 --level essential      # exit 0
```
Verdict: **NOT PREDICTED** — every command works; none mentions the detached state.

### A10 — awkward path (space + non-ASCII)
Commands:
```
$ surfaceplate install --target '/home/mps2210/surfaceplate-sweep/repos/awkward path/répo' --no-hooks
target: /home/mps2210/surfaceplate-sweep/repos/awkward path/répo
exit=0
$ surfaceplate check --repo '…/awkward path/répo'
repository: /home/mps2210/surfaceplate-sweep/repos/awkward path/répo
WARN - … exit=0
$ surfaceplate doctor --report --repo '…/awkward path/répo'
warn  core.hooksPath (global) <home>/.config/git/hooks - …
  <repo>  this repository's absolute path
exit=0
```
Verdict: **AS DOCUMENTED** — no crash, no mangling; `--report` redacts the path to `<repo>`/`<home>` by
design.

### A11 — already installed at a newer version
Commands (fixture a11b, the second run, which inserted a `check` before reinstalling; a11 was the first):
```
$ printf '99.0.0\n' > .standards/VERSION ; sed -i 's/"standard_version": "0.17.0"/"standard_version": "99.0.0"/' .standards/INSTALL.json
$ surfaceplate check --repo …/a11b
standard  : 99.0.0 installed 2026-09-09
  [SP005] Standard-owned files have been modified locally
        what: .standards/VERSION
        fix : Revert the local edits and re-run the installer FROM VERSION 99.0.0 - the version recorded in this repository's install record. …
FAIL - the conformance check found findings that cannot be graced.
exit=1
$ surfaceplate doctor --repo …/a11b
ok    vendored digest        ceffdcf76ae5… matches the install record
ok    tool vs installed      both 0.17.0 (ceffdcf76ae5…); adopt and check agree on the schema
skip  standard is current    skipped (offline); installed 99.0.0, run with --online
exit=0
$ surfaceplate install --target …/a11 --no-hooks
Surfaceplate 0.17.0 - upgrade
currently installed: 99.0.0
NOTE: this is an UPGRADE, 99.0.0 -> 0.17.0, not a restore.
      … run the 99.0.0 installer instead, or accept this as a deliberate upgrade …
exit=0
$ cat .standards/VERSION ; grep standard_version .standards/INSTALL.json     # 0.17.0 / "0.17.0"
```
Which file the tool believed: `check` and `install` believed **`INSTALL.json`** (99.0.0) and `check`
reported the `VERSION` edit as `SP005`; `doctor` believed `INSTALL.json` on one line and printed
"both 0.17.0" on another.
Verdict: **DIFFERS** — the install is not silent, but it does not notice direction: a downgrade is
labelled "an UPGRADE" and proceeds; `doctor` contradicts itself. PW-08.

### A12 — install twice, unchanged
Commands:
```
$ surfaceplate install --target …/a12 --no-hooks ; cp .standards/MANIFEST.sha256 .standards/INSTALL.json a12-snap/ ; sleep 1
$ surfaceplate install --target …/a12 --no-hooks
$ diff a12-snap/MANIFEST.sha256 …/a12/.standards/MANIFEST.sha256 && echo MANIFEST-identical
MANIFEST-identical
$ diff a12-snap/INSTALL.json …/a12/.standards/INSTALL.json
exit=0
```
Verdict: **AS DOCUMENTED** — byte-identical, including the record (dates are day-granular).

---

## Axis B — environment

### B1 — global `core.hooksPath` set, bare install
Commands:
```
$ git config --global --get-all core.hooksPath ; sha256sum ~/.gitconfig      # /home/mps2210/.config/git/hooks ; 645f7328…
$ surfaceplate install --target /home/mps2210/surfaceplate-sweep/repos/b1
STOPPED - Git hooks for this repository already run from somewhere else.
… That setting is currently set
  at the --global level, to '/home/mps2210/.config/git/hooks' - …
Three ways forward:
  1. Keep what you have, skip the local hook: re-run with --no-hooks. …
  2. Remove the --global setting, …  git config --global --unset core.hooksPath
  3. Reconcile: keep both. … a delegation wrapper that forwards to this repository's
     own default hook path ($(git -C <repo> rev-parse --git-path hooks)/pre-commit) …
Nothing has been written.
exit=4
$ git -C …/b1 status --short ; ls -A …/b1 ; git config --global --get-all core.hooksPath ; sha256sum ~/.gitconfig
.git  README.md  /home/mps2210/.config/git/hooks  645f7328…
```
Verdict: **AS DOCUMENTED** — stops, writes nothing, global unchanged, three routes offered.

### B2 — `--chain` where the global hook delegates elsewhere
First attempt (as the packet specifies):
```
$ surfaceplate install --target …/b2 --chain            # exit 0: writes .githooks/pre-commit, leaves core.hooksPath
$ surfaceplate adopt --propose --target …/b2 --level standard ; <complete> ; surfaceplate adopt --answers …   # profile PASS-able
$ grep -n enforcement governance/application-profile.yaml | sort | uniq -c
   … every gate: enforcement: [history_audit, review]
$ <declare adoption.hook_chain: delegates_to .githooks/pre-commit + rationale> ; commit
$ ls .git/hooks/pre-commit          # No such file
$ surfaceplate check --repo …/b2    # WARN, exit 0 — NO SP038
$ <shim at .git/hooks/pre-commit exec'ing .githooks/pre-commit>
$ surfaceplate check --repo …/b2    # WARN, exit 0 — NO SP038
```
`FACT`: both halves returned the same answer. Cause (`INFERENCE` from the profile the wizard wrote):
under a `--chain` install the wizard proposes no gate with `local_hook` enforcement, so `SP038` has no
claim to test. PW-05.

Second attempt (one gate's enforcement hand-edited to `[local_hook, history_audit, review]`, stated):
```
$ rm .git/hooks/pre-commit ; surfaceplate check --repo …/b2
  [SP038] Gate 'work_registration' claims hook enforcement that is not in place
        what: enforcement lists 'local_hook', but default hooks path: /home/mps2210/.config/git/hooks/pre-commit: the declared delegation ran (exit 0) but did not reach this standard's gate.
        fix : … install with --chain, have your own hook run .githooks/pre-commit, and declare adoption.hook_chain - this check then verifies by effect that your chain reaches the gate; …
WARN … exit=0
$ <shim restored> ; surfaceplate check --repo …/b2      # no SP038; WARN exit=0
$ rm .git/hooks/pre-commit ; surfaceplate check …        # SP038 again
$ SURFACEPLATE_HOOK_PROBE=1 .githooks/pre-commit         # surfaceplate-hook-probe-ok, exit 0
$ git commit -qm 'probe commit'                          # the shipped gate ran on commit (its WARN output appeared), exit 0
```
Verdict: **DIFFERS** as specified (first attempt could not distinguish); **AS DOCUMENTED** once a gate
claims `local_hook` — `SP038` fires without the shim, clears with it, and the message reports the
delegation it actually executed (DR-66 by effect). Note `SP038` is *graceable* (verdict stayed WARN).

### B3 — `textual` absent
Commands (second venv `.venv-noadopt`, `pip install "surfaceplate @ file://…/source"`; `import textual` → `ModuleNotFoundError`):
```
$ .venv-noadopt/bin/surfaceplate adopt --target …/b3 </dev/null
`adopt` needs the optional `textual` dependency, which is not installed.
Run:  pip install 'surfaceplate[adopt] @ git+https://github.com/pipoventures/surfaceplate@main'
Or, if you have a clone:  pip install 'textual==8.2.8'
Without it, `surfaceplate adopt --propose` still works and needs no terminal.
exit=2
$ .venv-noadopt/bin/surfaceplate adopt --propose --target …/b3 --level essential     # exit 0, both files written
$ .venv-noadopt/bin/surfaceplate doctor --repo …/b3 | grep textual
warn  textual                missing - needed by adopt (the adopt extra)
```
Verdict: **AS DOCUMENTED**.

### B4 — Python 3.9
```
$ python3.9 -V ; ls /usr/bin/python3* /usr/local/bin/python3* ; ls ~/.pyenv/versions ; command -v uv ; grep requires-python pyproject.toml
bash: line 1: python3.9: command not found
/usr/bin/python3  /usr/bin/python3.12
/home/mps2210/.local/bin/uv
28:requires-python = ">=3.9"
```
Verdict: **NOT ATTEMPTED — EVIDENCE GAP.** No 3.9 interpreter; none installed, no inference from source.

### B5 — no network
Method: `strace` is absent, so instead of a dead port the proxy variables pointed at a local listener that
logs every connection (`listener.py`, port 40359). A request would therefore be *observed*, not inferred.
```
$ env | grep -i proxy      # https_proxy/http_proxy/HTTPS_PROXY/HTTP_PROXY=http://127.0.0.1:40359, no_proxy=
$ surfaceplate check --repo …/b5                    # WARN, exit 0; connections: 0
$ surfaceplate check --repo …/b5 --currency
  - currency: UNKNOWN - could not reach pypi.org: <urlopen error Remote end closed connection without response>. Installed 0.17.0. An unreachable index is not a passing check; nothing here failed because of it.
WARN - … exit=0                                      # connections: 1 —
CONNECTION from ('127.0.0.1', 34214): b'CONNECT pypi.org:443 HTTP/1.1\r\nHost: pypi.org:443\r\n\r\n'
$ surfaceplate doctor --repo …/b5                   # exit 0; connections: 0
$ surfaceplate doctor --report --repo …/b5
Nothing here was sent anywhere - this command makes no network requests. …   # exit 0; connections: 0
$ <proxies unset> surfaceplate check --repo …/b5 --currency
  - currency: installed 0.17.0 is AHEAD of the published 0.16.1 - a pre-release, or this is the repository that publishes the standard
exit=0
```
Verdict: **AS DOCUMENTED** — `currency: UNKNOWN`, exit unchanged (0 both ways); `doctor --report` made
no request, verified by effect (the listener saw the `--currency` request and nothing else).

### B6 — `LANG=C` / `LC_ALL=C`
```
$ LANG=C LC_ALL=C surfaceplate check --repo …/b6 > B6-check.out 2>&1 ; echo exit=$?        # exit=0, no Traceback
$ LANG=C LC_ALL=C surfaceplate doctor --repo …/b6 > B6-doctor.out 2>&1 ; echo exit=$?       # exit=0; output contains '…' (ceffdcf76ae5…)
$ LANG=C LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 python -c 'import sys;print(sys.stdout.encoding)'   # ascii
$ LANG=C LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 surfaceplate doctor --repo …/b6 > … ; echo exit=$?
exit=1
  File ".../surfaceplate/doctor.py", line 522, in main
    print(line.render())
UnicodeEncodeError: 'ascii' codec can't encode character '…' in position 41: ordinal not in range(128)
$ LANG=C LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 surfaceplate doctor --report --repo …/b6 …   # exit=1, UnicodeEncodeError '…' at position 1685
$ LANG=C LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 surfaceplate check --repo …/b6 …            # exit=0
$ LANG=C LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 surfaceplate adopt --propose --target …/b6 --level essential …   # exit=0
```
Verdict: **AS DOCUMENTED** under `LANG=C`/`LC_ALL=C` alone (`INFERENCE`: Python 3.12's C-locale
coercion, PEP 538/540, makes stdout UTF-8). **DIFFERS** once coercion is disabled: `doctor` and
`doctor --report` crash on the `…` glyph they print. Granularity note: `check`'s output for this
fixture contained no non-ASCII (the owner field is not echoed), so `check` was not exercised. PW-11.

### B7 — `git` not on `PATH`
```
$ env PATH=/home/mps2210/surfaceplate-sweep/.venv/bin …/.venv/bin/python -c 'import shutil;print(shutil.which("git"))'
None
$ env PATH=…/.venv/bin surfaceplate check --repo …/b7
  - Git history was not available, so none of the 1 auditable gate(s) were checked against the commits that crossed them. This is an absence of evidence, not evidence of conformance.
WARN … exit=0
$ env PATH=…/.venv/bin surfaceplate doctor --repo …/b7
ok    core.hooksPath (local) unset
ok    core.hooksPath (worktree) unset
ok    core.hooksPath (global) unset
ok    core.hooksPath (system) unset
warn  virtualenv on PATH     /usr/bin is not on PATH; …
DOCTOR=OK  (2 warning, 15 checks)
exit=0
$ git config --global --get core.hooksPath
/home/mps2210/.config/git/hooks
```
Verdict: `check` **AS DOCUMENTED** (stated inability, no traceback). `doctor` **DIFFERS**: it asserts
`core.hooksPath (global) unset` — a negative it could not have established — while the value is set. No
line says git is missing. PW-04.

---

## Axis C — command sequence and lifecycle

### C1 — `adopt` before `install`
```
$ surfaceplate adopt --propose --target …/c12 --level essential
.standards/INSTALL.json does not exist. Run `surfaceplate install` first - `adopt` fills in the profile the installer creates; it does not install the standard itself.
exit=2
$ surfaceplate adopt --target …/c12 </dev/null        # TTY message first (see CAL-2), exit=3; nothing written
```
Verdict: **AS DOCUMENTED**.

### C2 — `check` before `install`
```
$ surfaceplate check --repo …/c12
Blocking findings (1) - never graced:
  [SP001] Surfaceplate is not installed
        what: .standards/INSTALL.json is missing.
        fix : Run install_standard.py from the surfaceplate repository.
FAIL - Surfaceplate is not installed in this repository.
exit=2
```
Verdict: **AS DOCUMENTED** (exit 2, `SP001`). Wording note: the `fix` names `install_standard.py`,
not `surfaceplate install` — PW-17.

### C3 — the documented happy path, verbatim (`INSTALL.md` block I3, lines 78–86)
Copied from the pinned clone by extraction script (log/D1.log shows the block). The first two lines
(venv + `pip install 'git+…@main'`) were satisfied by the pinned venv — stated substitution; the GitHub
form is exercised in D1. `/path/to/your-repo` → `…/repos/c3`.
```
$ surfaceplate doctor                                      # DOCTOR=OK (2 warning, 15 checks), exit=0 — warns the install will stop
$ surfaceplate install --target …/c3 --dry-run             # "Nothing has been written."  exit=4
$ surfaceplate install --target …/c3                       # STOPPED - Git hooks … / Nothing has been written.  exit=4
$ surfaceplate check --repo …/c3                           # FAIL - Surfaceplate is not installed  exit=2
--- continuing with --no-hooks (stated deviation) to reach I5/I6:
$ surfaceplate install --target …/c3 --no-hooks            # exit=0
$ git add .githooks ; git update-index --chmod=+x .githooks/pre-commit        (block I5)
fatal: pathspec '.githooks' did not match any files
error: .githooks/pre-commit: does not exist and --remove not passed
exit=128
$ surfaceplate check --repo .                              (block I6)  WARN … exit=0
```
Verdict: **DIFFERS** — on a machine with a global `core.hooksPath` the block cannot complete as written
(exit 4), which its own `doctor` line predicts; and block I5 cannot run after the `--no-hooks` route the
tool itself recommends. PW-17.

### C4 — tamper
First run (fixture c4): my restore step used a wrong path, so sub-cases (c) and (d) ran on a fixture with
the topic file still deleted. Recorded in log/C4.log; **rebuilt as c4b per §7** and re-run:
```
(a) printf 'X' >> .standards/topics/01-authority.md ; surfaceplate check
  [SP005] Standard-owned files have been modified locally
        what: .standards/topics/01-authority.md                                   exit=0 (WARN; graceable)
(b) rm .standards/topics/01-authority.md ; surfaceplate check
  [SP004] Standard-owned files have been deleted
        what: .standards/topics/01-authority.md                                   exit=0
(c) sed 'Never weaken a gate.' -> '…, unless convenient.' inside the AGENTS.md block ; surfaceplate check
  [SP008] The conformance block in AGENTS.md has been altered
        what: The content between the markers in AGENTS.md does not match the installed standard.   exit=0
(d) INSTALL.json framework_digest first hex char c -> 0 ; surfaceplate check
  [SP049] The installed manifest does not hash to the digest recorded for it
  [SP049] The profile's framework digest does not match what is installed
        what: adoption.framework_digest is replace-me, but the installed standard anchors to 0effdcf7…   exit=0
    surfaceplate doctor
FAIL  vendored digest        the vendored manifest hashes to ceffdcf76ae5… but the record says 0effdcf76ae5…; re-run the installer
FAIL  tool vs installed      installed 0.17.0 (0effdcf76ae5…) but this tool is 0.17.0 (ceffdcf76ae5…); …   exit=1
    (and setting the profile's digest to the tampered record value still leaves the manifest-vs-record SP049)
restored between each: git checkout -- . ; final check WARN exit=0
```
Verdict: **AS DOCUMENTED** — each tamper is reported as its own kind. Observation: all four are
*graceable* in `check` (verdict WARN, exit 0 inside the grace window; C5 shows they fail after it).

### C5 — grace expiry, both directions
```
$ grep -E 'grace|installed_at' .standards/INSTALL.json      # first_installed_at 2026-09-09, grace_expires 2026-10-09
$ surfaceplate check --repo …/c5                             # WARN - … grace expires 2026-10-09 (30 day(s) remaining).  exit=0
$ sed grace_expires -> "2020-01-01" ; surfaceplate check
FAIL - adoption is incomplete and the grace window expired on 2020-01-01.        exit=1
$ <restore> ; surfaceplate check --repo …/c5 --no-grace
FAIL - adoption is incomplete and grace disabled by --no-grace.                  exit=1
```
Verdict: **AS DOCUMENTED** — both directions.

### C6 — `--agents` narrowing, then widening
```
$ surfaceplate install --target …/c6 --no-hooks --agents claude     # writes .claude/rules/*, .claude/skills/*; exit=0
$ ls -d .github/instructions .github/skills .claude/rules .claude/skills
ls: cannot access '.github/instructions': No such file or directory
ls: cannot access '.github/skills': No such file or directory
.claude/rules  .claude/skills
$ surfaceplate check --repo …/c6
  - agent channels declined at install: copilot. Only claude received the instructions and skills; nothing checks that an agent on a declined channel reads them, because it was not given them.
$ grep -n '"agents"' -A2 .standards/INSTALL.json           # "agents": ["claude"]
$ surfaceplate install --target …/c6 --no-hooks --agents copilot
  remove  .claude/rules/surfaceplate-01-authority.md  (no longer part of the standard)
  … (all .claude/rules/* and .claude/skills/* removed)
$ ls -d …                                                   # .github/instructions .github/skills present; .claude/rules and .claude/skills present but EMPTY directories
$ surfaceplate check --repo …/c6
  - agent channels declined at install: claude. Only copilot received the instructions and skills; …
$ ls .claude/rules/*.md                                     # none — the by-effect tamper test had nothing to tamper
```
Verdict: **NOT PREDICTED** — answer to the packet's three-way question: **removed**, and the record
updated to `["copilot"]`; not "left unchecked". Two small things: the files are removed with the reason
"no longer part of the standard" (they are; the channel was dropped), and empty `.claude/rules`,
`.claude/skills` directories remain. PW-15.

### C7 — `--no-hooks`, then hooks
```
$ surfaceplate install --target …/c7 --no-hooks             # "declined  the pre-commit hook, and core.hooksPath is left as it was"  exit=0
$ surfaceplate check --repo …/c7                            # advisory: "the pre-commit hook was declined at install: …"  WARN exit=0
$ surfaceplate install --target …/c7                        # STOPPED - Git hooks … / Nothing has been written.  exit=4
$ git status --short ; grep '"hooks"' .standards/INSTALL.json     # clean ; "hooks": "declined"
```
Verdict: **AS DOCUMENTED** (per B1).

### C8 — `--propose` then `--answers` at `standard`
Fixture: `requirements.txt` (`PyYAML==6.0.3`), `src/app.py`, a `secret-scan.yml` workflow.
```
$ surfaceplate adopt --propose --target …/c8 --level standard        # exit 0; 36 needs-human lines
```
Hand-completion, attempt 1 (statuses chosen; five gates set `not_applicable`; two test controls given
file paths):
```
5 line(s) in the answers record still say 'needs-human': gates.work_contract.artefact, gates.register_currency.artefact, gates.authority_same_change.artefact, gates.regression_before_merge.artefact, gates.equivalence_evidence.artefact. …   exit=1
```
`FACT`: a gate answered `not_applicable` still demands an artefact path.
Attempt 2 (those five set to `README.md`):
```
Refusing to write: … controls.contract_tests.implementation_reference: No workflow in this repository has a step with that name.. Run `surfaceplate adopt --propose --level standard` for a complete record.
This is the wizard's own safety check, not the checker. Nothing was written.        exit=1
$ git status --short          # ?? .standards/adopt-draft.json  ← written despite "Nothing was written"
```
`FACT`: the record's line `controls.contract_tests.implementation_reference: needs-human` has no
`choices:` entry; the expected value is a *workflow step name*, discoverable only from the validator
source (`validators.py:173`). Attempt 3 (stale draft deleted; a `tests.yml` workflow with steps named
`contract tests` / `deterministic tests` added and committed; those names used):
```
$ surfaceplate adopt --target …/c8 --answers …/c8/governance/application-profile.answers.yaml
  Checking what you just wrote:
  - dependency_lock: verified against requirements.txt
  - contract_tests: verified against step 'contract tests' in .github/workflows/tests.yml
  - deterministic_tests: verified against step 'deterministic tests' in .github/workflows/tests.yml
  … (nine seeded-artefact advisories)
PASS - all conformance checks satisfied.
  The checker passes against what you just wrote: nothing outstanding.            exit=0
$ surfaceplate check --repo …/c8                                                   # PASS exit=0
$ provenance origins: 90 computed, 14 discovered, 13 example, 13 fact of record, 11 scaffolded, 20 typed
```
Verdict: **DIFFERS** — the profile eventually passes (no `F66` shape), but the documented
propose→complete→answers path cannot be completed from the record's own contents for `standard`, and a
refused attempt writes a draft that then blocks the corrected record (PW-02, PW-10).

### C9 — `--edit`
On the installer's *template* profile (before C8 completed — recorded because it is what an adopter who
skips `adopt` has):
```
$ surfaceplate adopt --target …/c8 --edit owner "Sweep Team (renamed)" --because "team renamed after reorg"
The wizard could not finish: KeyError: 'scanner'
Nothing was written. Your answers are kept in the draft, so re-running `adopt` offers to resume from where this stopped.
exit=4
```
On the adopt-written profile:
```
$ surfaceplate adopt --target …/c8 --edit owner "Sweep Team (renamed)" --because "team renamed after reorg"
Edited owner in …/c8/governance/application-profile.yaml; the change is recorded beside it as typed, with the reason.   exit=0
$ surfaceplate adopt --target …/c8 --edit owner "Sweep Team (unexplained)"          # NO --because
Edited owner in …/c8/governance/application-profile.yaml; the change is recorded beside it as typed, with the reason.   exit=0
$ sed -n '/^edits:/,$p' governance/application-profile.provenance.yaml
edits:
- path: owner
  at: '2026-09-09T11:58:57+01:00'
  reason: team renamed after reorg
- path: owner
  at: '2026-09-09T11:58:57+01:00'
  reason: edited after the write with `surfaceplate adopt --edit`
$ surfaceplate check --repo …/c8      # PASS exit=0
```
Verdict: **DIFFERS** — an edit without `--because` is neither refused nor recorded as unexplained: it
is recorded with a canned reason and the CLI says "with the reason". PW-07. The template-profile crash is
PW-12.

### C10 — removal
```
$ surfaceplate uninstall --target …/b7
usage: surfaceplate [-h] [--version] {install,check,adopt,doctor} ...
error: argument {install,check,adopt,doctor}: invalid choice: 'uninstall' …       exit=3
$ surfaceplate install --help | grep -iE 'remov|uninstall|revert|undo'             # no match
$ grep -rn -iE 'uninstall|remove surfaceplate|removing surfaceplate|to leave the standard|opt out' README.md INSTALL.md SETUP_GUIDE.md SUPPORT.md RECONCILIATION.md   # no match
```
Verdict: **AS DOCUMENTED** (the packet predicted absence). There is no command and no document. An
adopter is left to infer the file set from the installer's output. PW-13b.

---

## Axis D — the documents, run rather than read

### D1 — every fenced command in `README.md` and `INSTALL.md`
Blocks extracted verbatim by script from the pinned clone (R1–R3, I1–I7; text in log/D1.log). I1/I2 are
YAML profile fragments, not commands. Fresh venv `.venv-doc`; **installs resolved to GitHub `main` =
`16b26fc`**, so R1/R2/I3 runs are attributable to that commit.
```
R1  pip install 'git+https://github.com/pipoventures/surfaceplate@main'         PASS  (surfaceplate @ git+…@16b26fc79cb…, 0.17.0)
    surfaceplate --version                                                     PASS  surfaceplate 0.17.0        exit=0
    surfaceplate doctor              (cwd = fresh repo)                        PASS  DOCTOR=OK (3 warning)      exit=0
    surfaceplate install --target …/d1 --dry-run                               FAIL* STOPPED … Nothing has been written.   exit=4
    surfaceplate install --target …/d1                                         FAIL* STOPPED … Nothing has been written.   exit=4
    surfaceplate check --repo …/d1                                             FAIL* SP001 not installed                 exit=2
R2  pip install 'surfaceplate[adopt] @ git+…@main'                             PASS  (textual-8.2.8 …)
    surfaceplate adopt --target …/d1        (no TTY)                           FAIL* needs a real terminal; names --propose   exit=3
R3  (in a throwaway copy of the pinned source, 30bba44)
    python3 -m venv .venv && .venv/bin/python -m pip install pyyaml jsonschema  PASS
    . .venv/bin/activate                                                       PASS
    python tests/validate_contracts.py                                         PASS  CONTRACT_CONFORMANCE=PASS (241 checks)
    python tests/test_install_and_check.py                                     FAIL  INSTALL_CONFORMANCE=FAIL (1 failed, 309 passed)
        - adopt without a terminal exits 3 and names --propose: rc=2 …`adopt` needs the optional `textual` dependency…
    python scripts/build_release.py                                            FAIL  REFUSING TO BUILD: test_install_and_check.py did not pass.
I3  python3 -m venv .venv && . .venv/bin/activate ; pip install 'git+…@main'   PASS
    surfaceplate doctor / install --dry-run / install / check                  as R1: 0 / 4 / 4 / 2
I4  sudo apt install python3-yaml python3-jsonschema                            NOT ATTEMPTED (privileged)
I5  git add .githooks ; git update-index --chmod=+x .githooks/pre-commit        PASS  (on a --chain install: mode 100755 recorded)
                                                                                — FAIL after a --no-hooks install (no .githooks; see C3)
I6  surfaceplate check --repo .                                                PASS  WARN exit=0
    python .standards/check_conformance.py                                     PASS  WARN exit=0
I7  cd surfaceplate && git pull                                                 PASS  Already up to date. (clone of ~/github/surfaceplate at 30bba44)
    python surfaceplate/install_standard.py --target …/d1 --dry-run            FAIL* Nothing has been written.   exit=4
```
`FAIL*` = the command ran as written and stopped for the machine's global `core.hooksPath` (predicted by
the preceding `doctor` line) or for its documented precondition; not a defect in the command.

Divergence between the documented set and `scripts/front_door.sh` (read, never run — it rewrites
`git config --global`): the script installs from `file://`, never the `git+https` form the documents give;
every `install` in it passes `--no-hooks`, so the documented default (with hooks), I5, and `--chain` are
never exercised; `doctor` only ever runs with `--repo`; R2's extra install, R3 entirely, I4, I5, I7, and
`--replace-existing` are outside it; it is `sh` while the fences say `bash`.
Verdict: **DIFFERS** — R3 fails as written (PW-06); the rest as documented or environment-stopped.

### D2 — `INSTALL.md` "Frequently asked"
- **Q1 "Does this replace our existing Copilot instructions?" — TRUE.** Own `.github/copilot-instructions.md`
  ("Always use tabs. Never touch billing/.") survived above `<!-- BEGIN SURFACEPLATE -->`; installer line
  `appended .github/copilot-instructions.md`; `grep -c 'Always use tabs'` → 1.
- **Q2 "Can I edit a skill?" — TRUE.** Appending to `.github/skills/change/SKILL.md` → `[SP005] … what:
  .github/skills/change/SKILL.md`, `FAIL … exit=1`; `surfaceplate install --no-hooks` rewrote it
  (`write .github/skills/change/SKILL.md`); check back to WARN exit 0; `git status` clean.
- **Q3 (implied) deleting the workflow is detected — TRUE.** `rm .github/workflows/standards-conformance.yml`
  → `[SP004] Standard-owned files have been deleted` and `[SP009] The conformance workflow is not present`,
  `FAIL exit=1`.
- **Q4 "Can I bypass the pre-commit hook?" — PARTLY FALSE.** Hook-active fixture (B2: `--chain` + shim,
  `work_registration` enforcing `local_hook`, artefact `activity/register.md`, paths `src/**`):
  ```
  $ git rm activity/register.md ; echo … >> src/app.py ; git commit -qm '…'          # hook ran: blocked, exit 1 —
    [SP035] Gate 'change_record_before_completion' was crossed without its precondition
          what: 1 commit(s) since 2026-09-09T12:02:37+01:00 changed a gated path while a required artefact was absent: b15ca92 2026-09-09 app shape (missing CHANGELOG.md)
  $ git commit -qm '… (bypassed)' --no-verify                                            # 58cdafe, succeeded
  $ surfaceplate check --repo …/b2
    [SP032] Gate 'work_registration' requires an artefact that does not exist
    [SP035] Gate 'work_registration' was crossed without its precondition
          what: 1 commit(s) since 2026-09-09T12:02:37+01:00 … : b15ca92 2026-09-09 app shape (missing activity/register.md)
  WARN - adoption is incomplete, but grace expires 2026-10-09 …                          exit=0
  $ echo … >> src/app.py ; git commit -qm 'second … (bypassed)' --no-verify              # c26c6d8; parent already lacks the register
  $ surfaceplate check --repo …/b2                                                       # identical: still "1 commit(s) … b15ca92"; WARN exit=0
  $ git log --since='2026-09-09T12:02:37+01:00' --format='%h %s' -- 'src/**'
  c26c6d8 second src change, register still gone (bypassed)
  58cdafe change src while the register is gone (bypassed)
  b15ca92 app shape
  ```
  `FACT`: neither bypassed commit is ever named; the only commit named is the fixture's pre-adoption
  "app shape" commit, whose timestamp equals `effective_from` to the second. The check did not fail
  (WARN, exit 0) — `SP035` is graceable. Exception record from the template (`raised_on: 2026-09-09`
  unquoted, as the template's `# YYYY-MM-DD` comment invites) → `[SP043] Gate exception … is invalid:
  raised_on: datetime.date(2026, 9, 9) is not of type 'string'`, FAIL exit 1; quoted → `work_registration`'s
  `SP035` cleared. Restoring the register: bypassed commits still never named.
  Mechanism, established by calling the installed module's own functions on the fixture (`FACT`):
  ```
  commits_touching(repo, ['src/**'], '2026-09-09T12:02:37+01:00') -> [c26c6d8…, 58cdafe…, b15ca92…]
  blob_exists(58cdafe, 'activity/register.md') -> False ; blob_exists(c26c6d8, …) -> False
  historical_paths(repo, 'activity/register.md') -> ['activity/register.md', '.standards/seeds/activity-register.md']
  blob_exists(58cdafe, '.standards/seeds/activity-register.md') -> True ; (c26c6d8) -> True ; (b15ca92) -> False
  $ git log --follow --name-status --format='%h %s' -- activity/register.md
  f4b97e9 restore register
  C100	.standards/seeds/activity-register.md	activity/register.md
  ```
  The audit looks for the artefact "under every name it has ever had" (`F30`); git's copy detection reports
  the scaffolded register as a 100% copy *of the seed under `.standards/seeds/`*, so the seed's path counts
  as a former name, and the seed is present in every post-install commit. PW-01.
- **Q5 "Does the AI assistant actually obey this?" — EVIDENCE GAP** (needs GitHub Actions on a remote).
Verdict: Q1–Q3 **AS DOCUMENTED**; Q4 **DIFFERS**; Q5 **NOT ATTEMPTED**.

### D3 — `RECONCILIATION.md` procedure, literally, against A7
```
step 1 as written:   $ diff .github/skills/change/SKILL.md ../surfaceplate/surfaceplate/standard/.github/skills/change/SKILL.md
                     diff: ../surfaceplate/surfaceplate/standard/.github/skills/change/SKILL.md: No such file or directory   exit=2
step 1, our file:    $ diff .githooks/pre-commit ../surfaceplate/surfaceplate/standard/.githooks/pre-commit
                     diff: …: No such file or directory   exit=2
step 1, real place:  $ diff .githooks/pre-commit ~/surfaceplate-sweep/.venv/lib/python3.12/site-packages/surfaceplate/standard/.githooks/pre-commit
                     2c2,46  < echo "our own pre-commit"  ---  > repo_root=$(git rev-parse --show-toplevel …   (works)
step 2–3:            judgement; nothing to raise.
step 4:              the document's homes ("an instruction file … or copilot-instructions.md") do not fit a hook; moved to scripts/our-pre-commit.sh (sha unchanged 816b375a…)
step 5:              $ surfaceplate install --target …/a7 --chain --replace-existing
                       write   .githooks/pre-commit, and core.hooksPath is left as it was   exit=0
                     AGENTS.md sha unchanged (623f5bb4…), own text present; team.instructions.md unchanged (d6a67f22…)
step 6:              "the application profile's decision record" = adoption.decision_record_id: replace-me — an ID, not a place; docs/decisions/ does not exist until adopt scaffolds it.
$ surfaceplate check --repo …/a7      # WARN exit=0 (template profile)
```
Verdict: **DIFFERS** — step 1 cannot be carried out as written by a pip adopter (no sibling clone;
the standard's copy lives in site-packages), step 4 has no home for hook content, step 6 names no path.
Nothing of the adopter's was lost at any step. PW-13.

---

## Findings, most severe first

### PW-01 — The history audit treats the seed copy under `.standards/seeds/` as a former name of a scaffolded artefact, so removing the artefact never registers as a gate violation
Severity:    **high** — a control (the history audit, the FAQ's stated backstop for `--no-verify`) passes
             while not holding, for every artefact `adopt` scaffolds from a seed (register, risk
             classification, decision log, authority map, test conventions, data sources, output
             validation, dependency review, release checklist, CHANGELOG).
Reproduce:   B2 fixture with a hook-active `work_registration` gate → `git rm activity/register.md`, change
             `src/app.py`, `git commit --no-verify` (twice) → `surfaceplate check`.
Observed:    `FACT` — `SP035` names only `b15ca92 app shape`; commits `58cdafe`, `c26c6d8` (gated path
             changed, artefact absent at that commit) never appear, before or after the register is
             restored. `FACT` — `historical_paths('activity/register.md')` returns
             `['activity/register.md', '.standards/seeds/activity-register.md']`; `blob_exists` of the seed path
             is `True` at both bypassed commits; `git log --follow` shows `C100 .standards/seeds/activity-register.md
             activity/register.md`.
Expected:    `INSTALL.md` FAQ: "a bypassed prerequisite violation remains in the commit graph and causes
             later conformance checks to fail until a specific, attributable exception is recorded."
Reach:       adopters — anyone whose gate artefacts were scaffolded by `adopt` (`create_missing_artefacts: yes`)
             and who has `.standards/seeds/` in the tree, i.e. every adopter of the wizard.
Cause:       `INFERENCE` (strong; each link observed): `F30`'s rename-following resolves the artefact's
             historical names with `--follow`, git's copy detection attributes the byte-identical scaffold
             to the seed, and the audit accepts presence under any historical name.

### PW-02 — A refused `--answers` replay writes `.standards/adopt-draft.json` while printing "Nothing was written", and that draft makes every later replay fail with the stale value's error; `--propose` does not clear it
Severity:    **high** — the documented propose→complete→answers path cannot be completed after one wrong
             answer, and the message that results ("Nothing exists at that path") is about a value the
             user has already corrected; the tool's own advice (`--propose` again) does not help.
Reproduce:   fresh clone of A1 (installed, committed) → `adopt --answers` with lock=`poetry.lock` (refused,
             exit 1; `.standards/adopt-draft.json` appears) → `adopt --answers` with lock=`README.md`
             (refused with the same message) → `rm .standards/adopt-draft.json` → same record → PASS.
Observed:    `FACT` — reproduced on three fresh clones (a1-repro1/2/3) in both directions; also recurred on
             C8. `FACT` — after `--propose` the draft is still present and the replay still fails.
Expected:    the refusal text: "Nothing was written."
Reach:       adopters.
Cause:       `INFERENCE` — the scripted interview persists its draft on refusal and a later replay resumes
             from the draft's answers rather than the record's.

### PW-03 — Discovery proposes `pyproject.toml` as the dependency lock (origin `discovered`), and the checker "verifies" `dependency_lock` against any tracked non-empty file, including a Markdown page
Severity:    **high** for the A2 half (a control passes while not holding — pinning a manifest is not
             pinning a lock — and it is presented as a discovered fact, not a question); the A1 half is
             `F132`'s known mechanism observed on the real pathway (the checker prints
             `dependency_lock: verified against docs/guide.md` and `PASS`).
Reproduce:   A2: `pyproject.toml` with `[project] dependencies`, no lock → `adopt --propose --level essential`.
             A1: complete the record with `controls.dependency_lock.implementation_reference: docs/guide.md`.
Observed:    `FACT` — answers record: `value: pyproject.toml / origin: discovered / detail: 'found: pyproject.toml'`;
             A1: profile written, `check` PASS.
Expected:    packet A2: "the lock-file field is asked. Falsifier: the manifest is silently proposed as the lock file".
Reach:       adopters.
Cause:       `INFERENCE` — the lock discovery's candidate list includes manifests; `SP051`/`tracked_path`
             check existence, tracking, non-emptiness and placeholders, never kind.

### PW-04 — `doctor` reports `core.hooksPath` as `unset` at every scope when `git` is not on `PATH`
Severity:    **medium** — a diagnostic asserts a negative from a command that could not run, on the exact
             setting that stops the installer; no line says git is missing.
Reproduce:   `env PATH=~/surfaceplate-sweep/.venv/bin surfaceplate doctor --repo <installed repo>` on this machine.
Observed:    `FACT` — `ok core.hooksPath (global) unset` while `git config --global --get core.hooksPath`
             → `/home/mps2210/.config/git/hooks`; `shutil.which("git")` → `None` in that PATH.
             `check` in the same PATH says "Git history was not available … absence of evidence".
Expected:    packet B7: "a stated inability, not a traceback, and no negative finding asserted from a git
             command that could not run."
Reach:       adopters (any environment where the venv is on PATH but git is not, e.g. minimal containers).
Cause:       `INFERENCE` — `_git_config` treats a failed subprocess as an empty value.

### PW-05 — Under a `--chain` install, `adopt` proposes no `local_hook` enforcement, so a declared `hook_chain` is never verified and `SP038` cannot fire
Severity:    **medium** — DR-66's verification-by-effect only engages where a gate claims `local_hook`;
             the wizard never makes that claim for a chained install, so the chain declaration is
             decorative until someone hand-edits the profile (as this sweep did).
Reproduce:   B2 first attempt.
Observed:    `FACT` — every gate `enforcement: [history_audit, review]`; `check` identical with and without
             the shim. After a hand edit to `[local_hook, …]`, `SP038` fires/clears correctly.
Expected:    packet B2: "`SP038` — the declared chain does not in fact reach the gate".
Reach:       adopters using `--chain`.
Cause:       `INFERENCE` — the wizard maps `hooks: "chained"` to the same enforcement set as `"declined"`.

### PW-06 — `README.md`'s "Working on the standard itself" block fails as written: its venv lacks `textual`, `test_install_and_check.py` fails the no-TTY case, and `build_release.py` refuses to build
Severity:    **medium** — a documented path cannot be completed as documented (the standard's own `S3`).
Reproduce:   R3 in a copy of `30bba44`: `python3 -m venv .venv && .venv/bin/python -m pip install pyyaml jsonschema`,
             then the three scripts.
Observed:    `FACT` — `INSTALL_CONFORMANCE=FAIL (1 failed, 309 passed) - adopt without a terminal exits 3 and
             names --propose: rc=2 …needs the optional textual dependency`; `REFUSING TO BUILD`.
Expected:    README R3 comments: "installer and checker, end to end" / "refuses to build unless both pass".
Reach:       this repository's own workflow (contributors), not adopters.
Cause:       `INFERENCE` — the test assumes the `adopt` extra; CI installs it, the README block does not.

### PW-07 — `adopt --edit` without `--because` is accepted and recorded with a canned reason, and the CLI says the edit was recorded "with the reason"
Severity:    **medium** — a provenance record that presents an unexplained change as explained.
Reproduce:   C9 on an adopt-written profile: `surfaceplate adopt --target … --edit owner X` (no `--because`).
Observed:    `FACT` — exit 0; provenance `edits:` gains `reason: edited after the write with \`surfaceplate adopt --edit\``.
Expected:    packet C9: "refused, or recorded as unexplained — not silently accepted."
Reach:       adopters.
Cause:       `INFERENCE` — `--because` defaults to `""` and the writer substitutes boilerplate for an empty reason.

### PW-08 — Installing over a newer recorded version is labelled "an UPGRADE, 99.0.0 -> 0.17.0" and proceeds; `doctor` prints two different installed versions in one run
Severity:    **medium** — a downgrade is reported as its opposite; the tool notices a difference but not its direction.
Reproduce:   A11.
Observed:    `FACT` — installer NOTE quoted above; `doctor`: `tool vs installed both 0.17.0` and
             `standard is current … installed 99.0.0` in the same output. `check` correctly reports the
             hand-edited `VERSION` as `SP005`.
Expected:    packet A11: "the tool notices the install is ahead of it rather than silently downgrading".
Reach:       adopters (an adopter with a newer install and an older tool on PATH).
Cause:       `INFERENCE` — version inequality is reported without ordering; `doctor`'s "tool vs installed"
             line prints the tool's version for both sides when digests match.

### PW-09 — The gate-exception template's natural completion is invalid: an unquoted `raised_on` date parses as a date and fails the schema
Severity:    **medium** — the FAQ's remedy ("record a specific, attributable exception") fails on first
             use with a blocking `SP043`; the template warns about quoting SHAs but not dates.
Reproduce:   D2-Q4: copy `templates/gate-exception.yaml`, fill `raised_on: 2026-09-09`.
Observed:    `FACT` — `[SP043] Gate exception 'governance/exceptions/GX-0001.yaml' is invalid: raised_on:
             datetime.date(2026, 9, 9) is not of type 'string'`, FAIL exit 1; quoted → accepted.
Expected:    template comment `raised_on: replace-me  # YYYY-MM-DD`.
Reach:       adopters.
Cause:       `FACT` (YAML 1.1 date scalar) + `INFERENCE` (schema `type: string`).

### PW-10 — The answers record does not say what kind of value `controls.contract_tests` / `controls.deterministic_tests` `implementation_reference` take (a workflow step name), and a gate answered `not_applicable` still demands an artefact path
Severity:    **medium** — the file an adopter must hand-edit cannot be completed from its own contents at `standard`.
Reproduce:   C8 attempts 1 and 2.
Observed:    `FACT` — refusals quoted in C8; no `choices:` entry for those lines; the expected form is
             visible only in `adopt/validators.py:173` (`candidate_ci_steps`).
Expected:    the record's header: "Every line that says needs-human is a decision only a human can make. Complete them all".
Reach:       adopters.
Cause:       `INFERENCE`.

### PW-11 — `doctor` and `doctor --report` crash with `UnicodeEncodeError` when Python's C-locale coercion is disabled
Severity:    **medium**, narrow reach — plain `LANG=C` is fine (coercion); the crash needs
             `PYTHONCOERCECLOCALE=0`/`PYTHONUTF8=0` (ASCII stdout). The command that fails is the one for
             assembling a problem report.
Reproduce:   B6 supplement.
Observed:    `FACT` — traceback at `doctor.py:522 print(line.render())`, `'…'`; `check` and
             `adopt --propose` do not fail.
Expected:    packet B6 falsifier: "a UnicodeEncodeError".
Reach:       adopters on ASCII-locale hosts with coercion off.
Cause:       `INFERENCE` — the `…` truncation glyph in the digest columns is printed without an encoding fallback.

### PW-12 — `adopt --edit` on the installer's template profile fails with an internal error (`KeyError: 'scanner'`, exit 4)
Severity:    **medium** — an adopter who completed the template by hand (the documented alternative to
             the wizard) gets a crash rather than a refusal from `--edit`.
Reproduce:   C9 first run (template profile in place).
Observed:    `FACT` — `The wizard could not finish: KeyError: 'scanner' … Your answers are kept in the draft`.
Expected:    packet C9: "confirm the edit and its reason are recorded".
Reach:       adopters.
Cause:       `INFERENCE` — `--edit` assumes the profile shape the wizard writes (a `scanner` block present).

### PW-13 — `RECONCILIATION.md` cannot be followed literally by a pip adopter, and there is no removal procedure anywhere
Severity:    **low** (reconciliation) / **medium** (removal — the packet: "the absence of an answer is the finding").
Observed:    `FACT` — step 1's `../surfaceplate/surfaceplate/standard/…` path: `No such file or directory`
             (the standard's copy is in site-packages); step 4 offers no home for hook content; step 6's
             "decision record" is an ID field. `FACT` — no `uninstall`, no flag, no document.
Reach:       adopters.
Cause:       documentation.

### PW-14 — `RECONCILIATION.md` says the standard owns `.github/instructions/*.instructions.md`; the installer owns only its twelve named files
Severity:    **low** — the behaviour is the better one (the adopter's `team.instructions.md` survived), the document overstates.
Observed:    `FACT` — A7: `team.instructions.md` untouched, not listed as a collision.
Reach:       adopters.

### PW-15 — Changing `--agents` removes the other channel's files with the reason "(no longer part of the standard)" and leaves empty `.claude/rules` and `.claude/skills` directories
Severity:    **low**.
Observed:    `FACT` — C6 output quoted.
Reach:       adopters.

### PW-16 — The `--propose` preview substitutes silent defaults for undecided answers and prints an empty-list sentence
Severity:    **low** — the preview says `data_classification: public`, `relied_on_outside_team: false`,
             `material_quantitative_output: false` where the record says `needs-human`; header reads
             "0 undecided gate(s) are left out entirely: ." Also the refusal text's double full stop
             ("repository.. Run").
Observed:    `FACT` — A1/CAL-3 files quoted.
Reach:       adopters.

### PW-17 — Documentation drift: the install block stops on a machine with a global `core.hooksPath` (predicted by its own `doctor` line) and block I5 presumes hooks were installed; `SP001`'s `fix` names `install_standard.py`; the documented `pip install` resolves to `main`, not a release
Severity:    **low**.
Observed:    `FACT` — C3, D1, C2 outputs; `pip freeze`: `surfaceplate @ git+…@16b26fc…`.
Reach:       adopters.

### PW-18 — The history audit's window includes commits made in the same second as `effective_from`
Severity:    **low** — a pre-adoption commit (`b15ca92`, 12:02:37, the fixture's own) was reported as a
             violation of nine gates because adoption happened in the same second; on a real repository
             this needs a commit and an adoption within one second.
Observed:    `FACT` — D2-Q4 output; `git log --since` is inclusive at second granularity.
Cause:       `INFERENCE`.

---

## What was not tested, and why

- **B4 (Python 3.9)** — no interpreter on the machine; the packet forbids installing one and forbids
  inferring from source. `EVIDENCE GAP`: whether `>=3.9` holds is unestablished.
- **D1 block I4** (`sudo apt install …`) — privileged and machine-changing; not run.
- **D2 Q5** — needs GitHub Actions on a remote; no network action taken.
- **B6 for `check`** — the check output on the fixture contained no non-ASCII, so `check`'s encoding path
  was not exercised (wrong granularity); `doctor` was.
- **B5 "no request" for `doctor`** rests on the listener seeing no connection while proxy variables were
  set. A request that ignored `*_proxy` would not have been seen; `strace` was absent. The `--currency`
  request *was* seen through the same path, which is the evidence the method works.
- **`front_door.sh`** was read, not run (it rewrites global git config); divergence reported from reading.
- **The interactive TUI** — out of the packet's scope by its own §3.
- **C6's by-effect tamper test** — nothing was left to tamper (the channel was removed), so "left and not
  checked" is excluded by construction rather than by a test.
- **The dirty checkout's changes** — nothing in the peer session's uncommitted edits was tested; every
  result is about `30bba44`. If those edits land as the `F132`/`H22` remedy, A1/A2/PW-03 should be re-run.

## What would have caught each finding earlier

- **PW-01** — a test that deletes a *scaffolded* artefact (not a hand-made one) and commits over a gated
  path; every existing history-audit fixture creates its artefact by hand, so it is never a copy of a
  seed. Alternatively, `historical_paths` asserting that no returned path lies under `.standards/`.
- **PW-02** — an `--answers` test that runs a refused replay and then a corrected one on the same
  repository; the suites replay once per fixture.
- **PW-03** — a discovery fixture with a manifest and no lock (`test_discover.py` fixtures all carry
  `requirements.txt`), and a `dependency_lock` validator that checks kind, or a test that a `.md` file is
  refused.
- **PW-04** — running `doctor` in a PATH without git in `test_install_and_check.py`, asserting the
  hooksPath lines say "unknown", not "unset".
- **PW-05** — DR-66's acceptance test installing with `--chain` and then running `adopt`, asserting that
  at least one gate claims `local_hook` (the matrix asks decisions, not the install mode).
- **PW-06** — `front_door.yml` running README R3, or the test skipping (and *saying* it skipped) when
  `textual` is absent.
- **PW-07/PW-12** — a `--edit` test without `--because`, and one on the template profile.
- **PW-08** — an install test with `standard_version` set above the tool's.
- **PW-09** — validating the template's own example completion against the schema in `validate_contracts.py`.
- **PW-10** — a test that completes the `standard` record using only the record's `choices` hints.
- **PW-11** — a CI job with `PYTHONCOERCECLOCALE=0 LC_ALL=C`.
- **PW-13/14/17** — `front_door.sh` executing the documents' fences verbatim rather than a hand-written subset.
- **PW-18** — a fixture whose commits and adoption fall in one second, i.e. every fast test fixture, with an
  assertion on the window boundary.

---

*End of report. Logs: `~/surfaceplate-sweep/log/`. Fixtures: `~/surfaceplate-sweep/repos/`. Everything
under `~/surfaceplate-sweep` is disposable.*
