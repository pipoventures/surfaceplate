# Contributing

## Sign off your commits

Every commit in a pull request must carry a `Signed-off-by` line. This is a
[Developer Certificate of Origin (DCO)](https://developercertificate.org/) sign-off, not a
contributor licence agreement — no separate document to sign, no legal review workflow. Signing off
is you certifying, under the terms at the link above, that you wrote the contribution or otherwise
have the right to submit it under this project's licence.

Add it automatically:

```bash
git commit -s -m "your commit message"
```

This appends a line to the commit message in the form:

```
Signed-off-by: Your Name <your.email@example.com>
```

The name and email must match your Git author identity (`git config user.name` /
`git config user.email`).

**Forgot to sign off?** Fix the most recent commit:

```bash
git commit --amend -s --no-edit
```

For several commits, rebase and sign off each one:

```bash
git rebase --signoff main
```

Then force-push your branch (`git push --force-with-lease`).

## What is checked, and what is not

A CI check runs on every pull request and fails if any commit is missing a valid sign-off. It
checks authorship certification only — it does not review code quality, run tests, or grant
approval of any kind; those remain separate, human steps.

## Before you open a pull request

Read `README.md` and `core/` for what this project is and how it is controlled. There is one
maintainer; see `org/decisions/README.md` for what that does and does not mean for review and
approval.

## Reporting a problem, not proposing a fix

Found a bug, a defect in the standard itself, or something the checker gets wrong?
[Open an issue](https://github.com/pipoventures/surfaceplate/issues) — see `SUPPORT.md` for which
form to use. You do not need a fix in hand; a clear reproduction is enough, and is more useful to a
part-time maintainer than a large unreviewed patch. A vulnerability report follows `SECURITY.md`
instead, not this route.
