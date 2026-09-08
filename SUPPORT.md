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

## A vulnerability

Do not open a public issue. See [`SECURITY.md`](SECURITY.md) for the current reporting route and
its limitations.

## A question about your own repository's conformance

Start with [`INSTALL.md`](INSTALL.md)'s "Frequently asked" section and
[`RECONCILIATION.md`](RECONCILIATION.md) if the installer stopped on existing files. If neither
answers it, that gap is itself worth an issue.
