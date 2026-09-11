# Review invitation

The covering message sent when the independent review packet (`ACT-060`, `DR-64`) is actually
handed to someone, tracked here so what was sent is on the record — the same discipline this
directory already applies to `CHATGPT_ENTERPRISE_AUDIT_PROMPT.md` and
`GEMINI_ADVERSARIAL_REVIEW_PROMPT.md`. Two variants, because Part A and Part B are different asks
with different audiences and different honest time costs; do not send Part B's ask to a Part-A
channel or the response rate collapses.

**What is attached** — the three files at the
[`pypi/0.18.0` release](https://github.com/pipoventures/surfaceplate/releases/tag/pypi/0.18.0):
`INDEPENDENT_REVIEW_PACKET-0.18.0.html` (sha256 `2cbdd97b5105…`), `surfaceplate-0.18.0.zip`
(sha256 `bda9442b4808…`), and `SHA256SUMS`. The expected anchor for this release is
`20e7c982c28b…`, and the published sdist hashes to `6bdcacc9b8f8…`.

**The release is the authority for these files, not `dist/`.** Every `scripts/build_release.py` run
rewrites `dist/` from the current tree, so the local archive goes stale the moment anything else is
built — it did, between the upload and the send, and `sha256sum -c SHA256SUMS` on the local copy
failed while the release was correct throughout. Re-fetch with `gh release download pypi/0.18.0`
and check the sums file before attaching anything.

---

## Variant A — the thirty-minute ask (recompute one digest)

> Subject: Does this published package match its source? (30-minute check, no context needed)
>
> I maintain Surfaceplate, a software-delivery governance framework. It publishes an integrity
> anchor — a SHA-256 over its own framework manifest — and I would like someone who is not me to
> check that the published PyPI package actually produces it. That is the whole ask.
>
> No familiarity with the project is needed. The attached page
> (`INDEPENDENT_REVIEW_PACKET-0.18.0.html`, sha256 `2cbdd97b5105…` — check that first, against
> what you actually received) walks through three commands: download the sdist, hash one file
> inside it, compare against a value the page states before you compute anything. It also offers a
> second, independent way to get the same number, so you are not trusting my instructions alone.
>
> If the numbers agree, that is a fact you established, not one I told you — and I would like your
> name recorded as having established it (`governance/assurance/AE-0002-framework-anchor.yaml`, a
> form on the page composes it for you). If they disagree, that is a defect I need to know about
> more than I need anything else this project has ever produced.
>
> Repository: https://github.com/pipoventures/surfaceplate

## Variant B — the scoped audit (a few hours, wants some judgement)

> Subject: Independent review of a governance framework's design (scoped, a few hours)
>
> Surfaceplate installs a software-delivery control standard into a repository and checks
> afterwards that what was installed is still there, unmodified. No independent reviewer has ever
> looked at it — every finding on record so far was found by the same party who maintains it, which
> is stated as a limitation rather than hidden (`org/FINDINGS.md`'s closing section says so
> explicitly).
>
> The attached packet's Part B is scoped, not open-ended: a stated time-boxed minimum
> (`audit/AUDIT_SCOPE.md`'s ten criteria, sections 2, 8, 9, 13 and 14 of the packet if you have
> limited time), a form that composes the record for you
> (`governance/assurance/AE-0003-independent-audit.yaml`), and an explicit claim-labelling
> convention — `FACT FROM PACKAGE`, `INFERENCE`, `RECOMMENDATION`, `EVIDENCE GAP` — so "I could not
> establish this" is a legitimate, expected answer, not a failure on your part.
>
> I am not asking for approval. I am asking what a reviewer who owes me nothing actually finds.
>
> Repository: https://github.com/pipoventures/surfaceplate

---

## Channel-specific postings (Part A, recruited in bulk)

### Reproducible Builds (`rb-general@lists.reproducible-builds.org`, `#reproducible-builds`)

> Subject: [RFH] Verify a published Python package matches its source (30 min, one SHA-256)
>
> I maintain a small Python governance tool (Surfaceplate) that publishes an integrity anchor over
> its own payload, and I'd value a reproducibility-minded pair of eyes from people who do exactly
> this kind of check for a living.
>
> The ask: download `surfaceplate` 0.18.0's sdist from PyPI, hash one file inside it
> (`surfaceplate/MANIFEST.sha256`), and compare against a value stated on a self-contained page
> before you compute anything (attached, or linked from the GitHub Release for the `pypi/0.18.0`
> tag: https://github.com/pipoventures/surfaceplate). A second, independent path to the same number
> is offered on the same page, so you aren't trusting my instructions alone. No familiarity with
> the project needed, no code review, no judgement call — either the numbers agree or they don't.
>
> If you're willing to be named as having checked it, there's a short form on the page that writes
> the record. Genuinely grateful for anyone who has ten minutes to spare on this.

### `discuss.python.org` (Packaging category)

> Subject: Reproducibility check requested: does the sdist match the published anchor? (30 min)
>
> `surfaceplate` (https://pypi.org/project/surfaceplate/) publishes a SHA-256 anchor over its
> framework payload as part of how it verifies its own installed copies stay unmodified. I'd like
> someone outside the project to independently recompute that anchor from the published sdist and
> confirm it matches. Self-contained instructions, two independent ways to reach the same number,
> no project familiarity required: [link to the release / packet]. About thirty minutes. Happy to
> answer questions about the packaging side here.

### Show HN

> Title: Show HN: A software standard that publishes its own integrity anchor — please try to
> break it
>
> Surfaceplate installs a delivery-governance standard into a repository and checks afterward that
> nothing installed has drifted. It publishes a SHA-256 anchor over its own payload so that claim is
> checkable rather than asserted. Nobody outside the project has verified it yet — that's stated
> plainly in the README's status line, not buried.
>
> I'm not asking you to trust it. I'm asking you to try to find where the chain breaks: recompute
> the anchor from the PyPI sdist against the published commit, or read the scoped review packet and
> see whether its scope criteria actually hold. Either result is useful to me; a defect found this
> way is worth more than a quiet install. Repo: https://github.com/pipoventures/surfaceplate

---

## What has actually been sent

The point of this file. A drafted invitation that was never sent looks, from the register, exactly
like one that was — so the sending is recorded here with its date, and `H4` and `H16` are corrected
in place when it changes.

| Date | Ask | Recipient | Attached |
|---|---|---|---|
| 2026-09-11 | Part A **and** Part B, bundled but separately costed — twenty minutes and a few hours, with explicit permission to take only the first | A software engineer known to the maintainer, approached directly | all three |
| 2026-09-11 | Product-fit evaluation against real repositories, **and** an independent review of the framework itself | A partner at a professional-services firm, approached directly | the packet page |

**Why no names here, yet.** Approaching someone is not the same as their agreeing to participate,
and this register is public. Being asked to review something is the recipient's business to disclose,
not the sender's. Names belong in `governance/assurance/` when a reviewer returns evidence and
consents to being recorded — which is what `F6` requires of them anyway: *the reviewer is named, and
is not the maintainer*. The form on the packet page asks for that consent explicitly.

**These are direct approaches and they do not close `H16`.** That item asks for the Part A
invitation to be posted to a public Part-A channel — Reproducible Builds, `discuss.python.org`, or
Show HN — which recruits from people who owe the maintainer nothing at all, and is a different and
stronger kind of independence than asking someone you know. Both are worth having. Only one has
happened.

### Departure from this file's own advice, recorded rather than made silently

The header above warns: *"do not send Part B's ask to a Part-A channel or the response rate
collapses."* The 2026-09-11 engineer email bundles both asks, which reads as a breach of that and is
not one: the warning is about **cold bulk channels**, where a heavy ask suppresses a light one across
a population. For a single named person who has already agreed to help, two emails a week apart is
more friction rather than less. The asks were bundled but kept separable, separately time-costed,
and the smaller one stated as sufficient. If the response is silence, this paragraph is the first
thing to reconsider.
