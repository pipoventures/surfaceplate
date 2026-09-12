# Sunset and archival plan

What happens to this project if maintenance stops, stated now, before there is any pressure to
decide it under worse conditions.

---

## If maintenance stops

The repository is **archived, not deleted.** GitHub's archive state makes it read-only — no new
commits, issues, or pull requests — while leaving it visible and clonable exactly as it stood.
Nothing already public disappears.

## The PyPI namespace

**`surfaceplate` IS claimed on PyPI, and this section now describes something real.**
Corrected 2026-09-12: it previously read *"not currently claimed on PyPI — publication has
deliberately not happened yet… not a description of something already published."* That was true
when written on 2026-08-31 and false from the first publish. **Three releases have shipped since
— `0.16.0`, `0.16.1` and `0.18.0`** — and the file was not revisited, so a reader consulting the
sunset policy was told the thing it governs did not exist.

Recorded rather than silently overwritten because this is the **same defect class this project has
already raised against its own `SECURITY.md` three times** (`F117`, `F118`, `F127`): a
dated claim that was accurate on the day it was written and decays without anything announcing it.
It had not been raised against this file. Found by an external reconciliation
(hermes, 2026-09-12) rather than by any check here — **there is no instrument that would have
caught it**, which is the more useful finding than the wrong sentence.

**The policy below is unchanged by this correction — it now applies rather than anticipates.**
If the project is abandoned, the last published release keeps installing indefinitely: `pip` does
not depend on ongoing maintenance to keep serving an already-published file. There is no mechanism today that automatically transfers PyPI project
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
