# Sunset and archival plan

What happens to this project if maintenance stops, stated now, before there is any pressure to
decide it under worse conditions.

---

## If maintenance stops

The repository is **archived, not deleted.** GitHub's archive state makes it read-only — no new
commits, issues, or pull requests — while leaving it visible and clonable exactly as it stood.
Nothing already public disappears.

## The PyPI namespace

`surfaceplate` is not currently claimed on PyPI — publication has deliberately not happened yet
(see `org/RELEASE_PLAN.md`). This section is forward-looking policy for a namespace that does not
exist yet, not a description of something already published.

If the name is later claimed and the project is subsequently abandoned, the last published release
keeps installing indefinitely — `pip` does not depend on ongoing maintenance to keep serving an
already-published file. There is no mechanism today that automatically transfers PyPI project
ownership to anyone else. A future maintainer taking the project over (see below) would need PyPI
access granted to them separately, as its own explicit step.

## If you have already installed this

**Nothing changes for you, and nothing has to.** The files this standard installs
(`.standards/`, the pre-commit hook, your application profile) run entirely from your own
repository. Nothing is fetched over the network at check time — the checker reads only local files.
If this project is abandoned tomorrow, everything you have already installed keeps working exactly
as it does today, indefinitely. You do not need to do anything, and you are not depending on this
repository staying alive for what you already have to keep functioning.

Whether to keep using a version whose upstream has stopped moving is your own call to make, on your
own timeline — not something this document tells you.

## Could someone else take it over?

This project is Apache 2.0 (see [`org/decisions/DR-12.md`](decisions/DR-12.md)), so **anyone may
fork it and continue it independently at any time, for any reason, with or without the current
maintainer's involvement — that requires no one's permission.**

Taking over *this specific repository*, and any PyPI project published under this name, is a
narrower question with a thinner answer: it would require the current maintainer to explicitly
transfer them while still reachable. There is no named successor, and no automatic succession
process if the maintainer becomes permanently unreachable with no transfer having happened. In that
case, forking under the licence is the available route — not a formal handover, but a real one.
