# Independent review packet — Surfaceplate {{version}}

**Source document.** `scripts/build_review_packet.py` turns this file into one self-contained HTML page
for the reviewer, filling every placeholder from the published release. The page is a build output and
is not committed; this source is (`DR-64`, `ACT-060`). Read the page, not this file, when reviewing.

Generated {{generated_at}} from commit `{{commit}}` ({{commit_url}}).

## What this is, and what it is not

Surfaceplate is a software delivery standard that installs into a repository and checks the
repository against what it publishes. Its own records state that **no independent validator exists**
for it: one maintainer, and self-approval is not independence. This packet asks you to be that
outside party for one or two things, and it is written so that each can be done from a clean
machine with nothing but Python, a shell and the public artefacts.

- **Part A, about thirty minutes.** Recompute one number, the framework's integrity anchor, from the
  published package with plain tools, and say whether it agrees with what the package itself
  declares and with what this packet states. This is finding `F6`'s closing condition.
- **Part B, a few hours, optional.** The independent audit of the release: read the archive and the
  repository against the framework's own audit prompt and scope, and report in its required shape.

**What your review does not do.** It does not approve anything, does not declare the framework
production-ready, and does not accept any risk on the maintainer's behalf. Those are the
maintainer's acts, taken afterwards on the record you return. If you cannot establish something,
write `EVIDENCE GAP`; a gap is a result, a guess is not.

**Who you need to be.** Not the maintainer (Mario Pipo, Pipo Ventures Ltd), not a holder of write
access to the repository, and not an author of any of it. You state your relationship in the
`independence_basis` field of the return form; "none" is a fine answer. You compute on your own
machine, from PyPI and GitHub, never from bytes the maintainer sent you - the archive attached to
this packet is for Part B's reading, and Part A tells you how to tie it to the public release
without trusting it.

## Part A — the framework anchor (`F6`, human action `H4`)

**Why this matters.** Every adopting repository pins a *framework digest*: the SHA-256 of the
release's `MANIFEST.sha256`, a path-sorted, LF-terminated list of every payload file and its digest.
Until now every value of that digest was computed by the maintainer, on the maintainer's machine,
with the maintainer's script, and compared with a value the maintainer also computed. `F6` says
that is a closed loop, and names as its closing condition exactly this: *someone who is not the
maintainer recomputes it from a published tree and attests to the result.*

**The three values that must agree.**

| value | what it is | who computes it |
|---|---|---|
| **A** | `sha256` of `surfaceplate/MANIFEST.sha256` inside the source distribution fetched from PyPI, computed with `sha256sum` or the Python one-liner below | you, with no code from the package |
| **B** | the anchor the released tool declares about itself, `about.anchor()` after `pip install surfaceplate=={{version}}` | you, running the package's code in a throwaway environment (skippable: see below) |
| **C** | `{{anchor}}` | the maintainer, from the published commit's manifest; it is what a repository installing this release pins in `.standards/INSTALL.json` |

A = C is the recomputation `F6` names. B confirms the package agrees with the two of you; if you
prefer not to run the package's code, skip B and say so under limitations.

**Do not compare with `governance/application-profile.yaml` in the repository.** That file's
`adoption.framework_digest` is, by construction, the anchor of an *earlier* tree: Surfaceplate
installs into itself and the profile sits inside the tree its own manifest covers, so writing it
changes the manifest. The profile's comment says so. A difference there is expected and is not a
finding; what is worth reporting is whether the framework's documents disclose that property.

**The commands.** Linux or macOS; the Python line is the cross-platform form and applies the same
line-ending normalisation the framework's own installer applies (`\r\n` and `\r` to `\n`), which
is a no-op on the LF file the release ships.

```bash
python3 -m venv sp-review && . sp-review/bin/activate      # nothing outside this directory is touched
mkdir sdist && cd sdist
curl -sSLo surfaceplate-{{version}}.tar.gz "{{sdist_url}}"
sha256sum surfaceplate-{{version}}.tar.gz                    # PyPI's own digest of the file: {{sdist_sha256}}
tar -xzf surfaceplate-{{version}}.tar.gz
sha256sum surfaceplate-{{version}}/surfaceplate/MANIFEST.sha256           # VALUE A
python -c "import hashlib,sys;b=open(sys.argv[1],'rb').read().replace(b'\r\n',b'\n').replace(b'\r',b'\n');print(hashlib.sha256(b).hexdigest())" surfaceplate-{{version}}/surfaceplate/MANIFEST.sha256   # VALUE A, cross-platform
cd ..
pip install --disable-pip-version-check surfaceplate=={{version}}
python -c "from surfaceplate import about; print(about.anchor())"   # VALUE B (runs the package's code)
# VALUE C is stated in this packet: {{anchor}}
curl -sSL https://raw.githubusercontent.com/pipoventures/surfaceplate/{{commit}}/surfaceplate/MANIFEST.sha256 | sha256sum   # optional D: the same file at the published commit
```

**Notes.**

- The manifest is in `sha256sum` text format: a digest, two spaces, then `surfaceplate-{{version}}/<path>`.
  Do not reformat it; hash the file as it is.
- `tar` preserves bytes, so no line-ending conversion happens on extraction. If you clone with git
  on Windows instead, use `git -c core.autocrlf=false clone …`, or read the file with
  `git show {{commit}}:surfaceplate/MANIFEST.sha256`; the repository's `.gitattributes` forces LF anyway.
- The published release is commit `{{commit}}`. **Do not use the `v{{version}}` tag**: it points at an
  older tree and gives a different anchor (recorded as `F115`).
- {{adopter_pin}}

**What to write down.** The three values as you computed or read them, whether they agree, your
operating system and the tool you used for A. The form in Part C composes the record from them.

## Part B — the independent audit (release-plan item 10, human action `H6`)

**What you are given.** The release archive `{{zip_name}}` (its SHA-256 as sent: `{{zip_sha256}}`; verify
it first), the public repository at commit `{{commit}}`, and this packet. The archive's contents are
the framework's payload, one directory `surfaceplate-{{version}}/`, with `surfaceplate/MANIFEST.sha256`
inside it listing every file and its digest ({{manifest_entries}} entries).

**Tie the archive to the public release before reading it.** From the directory you extracted into:

```bash
sha256sum {{zip_name}}                                                 # must be {{zip_sha256}}
unzip -q {{zip_name}}
sha256sum -c surfaceplate-{{version}}/surfaceplate/MANIFEST.sha256      # every payload file: OK
sha256sum surfaceplate-{{version}}/surfaceplate/MANIFEST.sha256         # must equal VALUE A
```

If the last line does not equal A, the archive you were sent is not the published release: stop
and say so. If it does, everything you read in the archive is what PyPI and GitHub hold.

**What else to look at.** The repository's self-check run for the published commit
({{ci_run_url}}), read **per step**: a step that never ran reports `skipped`, and the last step of
the workflow confirms each check produced a result. The six suites that need no optional
dependency can be run from the archive in the same environment
(`pip install PyYAML==6.0.3 jsonschema==4.26.0`, then `python tests/validate_contracts.py`,
`tests/test_install_and_check.py`, `tests/check_identifiers.py`, `tests/check_code_registers.py`,
`tests/check_vendored_current.py`, `tests/check_audit_packet.py`); each prints a count on success.

**The time-boxed minimum.** If you cannot do all of the prompt below, do sections 2 (the
recomputation, which is Part A), 8 (the binding rule), 9 (the scope criteria), 13 (evidence gaps)
and 14 (coverage). Anything else you did not do is written as `EVIDENCE GAP` under section 13,
never left out silently.

**The scope criteria, one row each.** Score each `Holds`, `Gap` or `Strong`, with a justification
that cites a file.

{{scope_rows}}

**The audit prompt, verbatim.** What follows is the framework's own full-archive review prompt from
its "Required evidence handling" section onward, unchanged but for one substitution: where item 2
asks you to compare the recomputed anchor with the profile's field, compare it with **VALUE C**
from Part A instead, for the reason Part A gives. Its claim labels are the ones to use
throughout: `FACT FROM PACKAGE`, `INFERENCE`, `RECOMMENDATION`, `EVIDENCE GAP`.

{{audit_prompt}}

## Part C — the return form

The form below composes one or two records. Each is an *assurance-evidence record* in the
framework's own schema, and the maintainer files it under `governance/assurance/` unchanged: the
values you type are the values that stand. Fill Part A's fields, tick "Part B performed" only if you
did the audit, press **Compose**, then copy or download the YAML and send it back with the audit
text (Part B composes that too, as Markdown).

Two records rather than one, so that an outcome is never ambiguous: `AE-0002` says whether the
anchor agreed, `AE-0003` says what the audit found. If you did only Part A, the first record says
so in its limitations and does not bear on the audit.

**The `outcome` vocabulary.** `passed`: A, B and C agree (or, for the audit, `PASS`).
`passed_with_conditions`: they agree with a stated condition, for example B not computed (or `PASS
WITH REQUIRED CHANGES`). `failed`: any disagreement (or `FAIL`). The fourth value the schema allows,
`accepted_with_limitation`, is the owner's acceptance of a limitation and is not yours to give.

{{form}}

**The skeletons, for a printed or script-free copy.** Fill by hand and return as text.

```yaml
# governance/assurance/AE-0002-framework-anchor.yaml
schema_version: "1.0"
evidence_id: AE-0002
evidence_type: independent_validation
outcome: passed | passed_with_conditions | failed
reviewer_role: external reviewer
reviewer_identity: <your name, and affiliation or handle if you wish>
reviewed_at: "<YYYY-MM-DDThh:mm:ss+hh:mm>"
independence_basis: >-
  <who you are, your relationship to the maintainer or none, that you hold no write access and
  wrote none of it, and that you computed on your own machine from PyPI and GitHub>
scope: >-
  Surfaceplate {{version}}, published commit {{commit}}. A (sdist manifest, own hash): <hex>.
  B (the tool's declared anchor): <hex or "not computed">. C (stated in the packet): {{anchor}}.
  D (GitHub at the commit): <hex or "not computed">. Agreement: <all agree | which differ>.
  Computed on <OS> with <sha256sum | the Python one-liner>.
reference: >-
  {{sdist_url}} (sha256 {{sdist_sha256}}); wheel sha256 {{wheel_sha256}}; {{commit_url}};
  {{publish_run_url}}; packet generated {{generated_at}}.
limitations:
  - >-
    The independent audit (release-plan item 10) was not performed; this record does not bear on H6.
```

```yaml
# governance/assurance/AE-0003-independent-audit.yaml  (only if Part B was done)
schema_version: "1.0"
evidence_id: AE-0003
evidence_type: independent_validation
outcome: passed | passed_with_conditions | failed
reviewer_role: independent reviewer
reviewer_identity: <your name, and affiliation or handle if you wish>
reviewed_at: "<YYYY-MM-DDThh:mm:ss+hh:mm>"
independence_basis: >-
  <as above, adding that the archive's lineage was verified through its inner manifest (Part B)>
scope: >-
  Independent audit of Surfaceplate {{version}} at commit {{commit}}: the archive {{zip_name}}
  (sha256 {{zip_sha256}}, inner manifest anchor <hex, must equal A>), the repository, the self-check
  run read per step, and the suites run from the archive. Verdict: <PASS | PASS WITH REQUIRED
  CHANGES | FAIL>. Sections done: <list>.
reference: >-
  audit/INDEPENDENT_REVIEW_<date>.md (the report, verbatim); {{ci_run_url}}; {{commit_url}};
  {{sdist_url}}; packet generated {{generated_at}}.
limitations:
  - >-
    <each evidence gap from section 13, one per item>
```

## Provenance of this packet

Generated {{generated_at}} by `scripts/build_review_packet.py` from commit `{{commit}}` of
`pipoventures/surfaceplate`. The page's own SHA-256 cannot be inside the page; the maintainer quotes
it in the message that carries the page, so you can check that what you opened is what was sent.
The source of this page is `audit/INDEPENDENT_REVIEW_PACKET.md` at that commit, and the decision
that shaped it is `org/decisions/DR-64.md`.
