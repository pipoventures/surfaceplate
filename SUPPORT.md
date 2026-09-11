# Support

Three different things land here, and they go three different ways.

## Something is broken, or a check gets something wrong

[Open an issue](https://github.com/pipoventures/surfaceplate/issues). Run
`surfaceplate doctor --report` first and paste its output into the form — it assembles your tool
version, the installed standard's version and digest, your Python and OS, which optional
dependencies are available, and the current conformance verdict, entirely on your own machine.
**It makes no network requests; nothing is sent until you paste it.** Read what it collected before
you do — it tells you exactly what it redacted and what it never gathers at all, so you can decide
whether the rest is fine to post.

You do not need a fix in hand. A clear reproduction — what you ran, what you expected, what
happened instead — is more useful to a part-time maintainer than a large unreviewed patch; see
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## The terminal is the problem, not the standard

`surfaceplate agent-prompt --target <repo>` prints a prompt to paste into whatever AI coding
assistant you already use. It describes your repository in counts rather than contents — redacted
exactly as `doctor --report` is — and holds the agent to a contract: it may run the commands and
explain every decision, and it may **not** answer any line marked `needs-human`, choose your
conformance level, or decide a gate's status.

That boundary is the point. The decisions this standard asks for are yours, and a profile filled
with an agent's plausible answers is worse than no profile, because it reads as a decision someone
made. What the prompt gets you is someone to ask, not someone to decide.

Read it before you paste it: the last section lists what it left out, and pasting it sends that
content to your assistant's provider.

## A vulnerability

Do not open a public issue. See [`SECURITY.md`](SECURITY.md) for the current reporting route and
its limitations.

## You want it out

`surfaceplate uninstall --target <repo>`, or `--dry-run` first to see the list. It removes what the
install record says it wrote and nothing else; your profile and everything outside the managed
blocks stay. If something of yours went with it, that is a defect — [open an
issue](https://github.com/pipoventures/surfaceplate/issues) and say what.

## A question about your own repository's conformance

Start with [`INSTALL.md`](INSTALL.md)'s "Frequently asked" section and
[`RECONCILIATION.md`](RECONCILIATION.md) if the installer stopped on existing files.

If neither answers it, ask in
[Discussions](https://github.com/pipoventures/surfaceplate/discussions). A question is not a
defect, and the two want different treatment: an issue is a thing to be fixed and closed, while a
question is worth leaving where the next person can find it. **A question that the documentation
should have answered is also a defect in the documentation** — say so in the same post if you think
it is one, and it becomes an issue as well.
