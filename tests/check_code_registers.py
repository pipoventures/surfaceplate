#!/usr/bin/env python3
"""Fail if the identifier registers disagree with reality.

This is the remedy for F11, which `DR-8` raised and left open: *"Nothing enforces that a newly
added finding code is unique, contiguous, or documented."*

The case for a check rather than more care is that care demonstrably did not work. On
2026-08-31, `org/FINDINGS.md` carried **three** false statements at once, all written by people
reading the file at the time:

- `F5`'s entry said `INSTALL.md:29` still held a non-resolving clone URL. It had been corrected.
- The code-space table said the checker emitted `SP001`-`SP043`. `SP046` and `SP047` existed,
  added by the same session that was editing the file.
- The `ACT-<n>` row said there was "no register behind it". `activity/register.md` existed.

None of these is a typo. Each was true when written and became false when something else
changed, which is precisely the class of error a reader cannot catch by being careful: nothing
about a stale sentence looks different from a current one.

WHAT THIS CHECKS, and equally what it does not: it compares *declarations against reality*. It
cannot tell whether a finding's prose is still accurate - that is not mechanically decidable,
and `F5`'s stale entry would have survived this check. What it makes impossible is a code that
exists in one register and not the other.

Usage:
    python tests/check_code_registers.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "org" / "FINDINGS.md"
CHECKER = ROOT / "surfaceplate" / "check_conformance.py"

# A code is emitted where a Finding is constructed. Deliberately not "any SPnnn literal in the
# file": the checker names other codes in remedy prose ("see SP034"), and counting those would
# report codes that are documented rather than emitted - the opposite of what this checks.
EMITTED = re.compile(r"Finding\(\s*\"(SP\d+)\"")

DECLARATION = re.compile(r"```text\n(emitted:.*?)```", re.DOTALL)
RANGE = re.compile(r"SP(\d+)(?:-SP(\d+))?")

# `F70` / `F71` (`ACT-045`): the front door is checked, not trusted. Every relative link and every
# path-like code span in README.md and INSTALL.md must resolve - in this repository, or, for a
# `.standards/` path, in an installed checkout (which is the installer's payload, by
# construction); the README's version line equals `surfaceplate/VERSION`; the gate and control
# counts the documents state equal the catalogue; and every code the checker emits is in the
# generated catalogue below, which this script writes with `--write` and checks otherwise.
README = ROOT / "README.md"
INSTALL = ROOT / "INSTALL.md"
VERSION_FILE = ROOT / "surfaceplate" / "VERSION"
LEVELS_DOC = ROOT / "surfaceplate" / "core" / "CONFORMANCE_LEVELS.md"
CATALOGUE_BEGIN = "<!-- BEGIN GENERATED: finding codes (tests/check_code_registers.py --write) -->"
CATALOGUE_END = "<!-- END GENERATED: finding codes -->"
# `DR-76`, surface 4 of `DR-69`. What each level requires, arranged by the twelve topics rather
# than as a flat list of controls - GENERATED from the checker's own levels and `rules.CONTROL_TOPICS`,
# so the reader gets the topic view and neither structure restates the other.
TOPICS_BEGIN = "<!-- BEGIN GENERATED: levels by topic (tests/check_code_registers.py --write) -->"
TOPICS_END = "<!-- END GENERATED: levels by topic -->"
# `DR-69`: "twelve" names three different things in the shipped corpus - twelve controls, twelve
# topics, twelve cross-application control principles. Every current use is qualified; this keeps
# it that way. Bare uses only: "the twelve", "twelve." and "twelve," - a qualified "twelve topic
# documents" is exactly what is wanted and must not be flagged.
BARE_TWELVE = re.compile(r"\btwelve(?=[\s]*[.,;)]|\s+(?:are|is|were|of\b))", re.IGNORECASE)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
# `F162`: this repository's own blob URLs, so an absolute link in README.md is still checked
# for existence rather than waved through because it has a scheme.
OWN_BLOB = re.compile(r"^https://github\.com/pipoventures/surfaceplate/blob/main/(.+)$")
PATHISH = re.compile(r"`((?:\.standards|\.github|surfaceplate|org|audit|core|prompts|tests|scripts|docs)/[A-Za-z0-9_./*-]+)`")
# `F130`: a `name==version` pin, wherever it is written. Anchored on a digit so that a comparison
# written in prose or code ("x == y") cannot be read as a pin.
PINNED = re.compile(r"([A-Za-z][A-Za-z0-9_.-]*)==([0-9][A-Za-z0-9_.]*)")
# `F128`: the same treatment, applied to what the payload says about itself - see
# `payload_pointer_checks`. Only pointers that name an installed destination are resolved.
PAYLOAD_POINTER = re.compile(
    r"`((?:\.standards/[A-Za-z0-9_./*-]+)"
    r"|(?:\.claude/(?:rules|skills)/[A-Za-z0-9_./*-]+)"
    r"|(?:\.github/(?:instructions|skills)/[A-Za-z0-9_./*-]+)"
    r"|(?:[A-Za-z0-9_.*-]+\.instructions\.md))`"
)
# A comment may sit between the code and the title (SP038's does), so it is skipped.
TITLE = re.compile(r"Finding\(\s*\"(SP\d{3})\",\s*(?:#[^\n]*\n\s*)*((?:f?\"[^\"]*\"\s*)+)")
PLACEHOLDERS = {
    "{gate_id}": "<gate>", "{control_id}": "<control>", "{level}": "<level>", "{rel}": "<file>",
    "{label}": "<record>", "{reference}": "<reference>", "{scanner}": "<scanner>", "{status}": "<status>",
    "{path}": "<path>", "{name}": "<name>",
}
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "nineteen": 19}

CHECKS = 0
FAILURES: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(f"{label}{': ' + detail if detail else ''}")


def parse_codes(spec: str) -> set[int]:
    """Expand 'SP001-SP035, SP037' into the integers it names."""
    codes: set[int] = set()
    for lo, hi in RANGE.findall(spec):
        start = int(lo)
        end = int(hi) if hi else start
        if end < start:
            raise SystemExit(f"declared range SP{lo}-SP{hi} runs backwards")
        codes.update(range(start, end + 1))
    return codes


def declared_space(text: str) -> dict[str, set[int]]:
    match = DECLARATION.search(text)
    if not match:
        raise SystemExit(
            "org/FINDINGS.md has no ```text block declaring the SP code space. The check "
            "derives the expected codes from that block rather than restating them; without "
            "it there is nothing to compare the checker against."
        )
    space: dict[str, set[int]] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, _, spec = line.partition(":")
        space[key.strip()] = parse_codes(spec)
    for required in ("emitted", "gap", "reserved"):
        if required not in space:
            raise SystemExit(f"the SP declaration block has no '{required}:' line")
    return space


def _catalogue_rows(checker_text: str) -> list[tuple[str, str]]:
    """`(code, titles)` for every code the checker constructs a `Finding` for, titles read from
    the source with their f-string placeholders shown as `<gate>`, `<control>` and so on."""
    titles: dict[str, list[str]] = {}
    for code, raw in TITLE.findall(checker_text):
        text = "".join(re.findall(r"\"([^\"]*)\"", raw))
        for placeholder, shown in PLACEHOLDERS.items():
            text = text.replace(placeholder, shown)
        text = re.sub(r"\{[a-z_]+\}", "<value>", text)
        if text not in titles.setdefault(code, []):
            titles[code].append(text)
    return [(code, "; ".join(titles[code])) for code in sorted(titles)]


def render_catalogue(checker_text: str) -> str:
    rows = _catalogue_rows(checker_text)
    lines = [
        CATALOGUE_BEGIN,
        "",
        f"{len(rows)} codes. Generated from the checker's own source by `tests/check_code_registers.py --write`;",
        "the same script fails in CI when this table and the checker disagree. A code's title is what",
        "the report prints; `<gate>`, `<control>`, `<file>` stand for the name the report fills in.",
        "",
        "| Code | What it reports |",
        "|---|---|",
    ]
    for code, title in rows:
        lines.append(f"| `{code}` | {title} |")
    lines += ["", CATALOGUE_END]
    return "\n".join(lines)


def render_levels_by_topic(checker) -> str:
    """What each level requires, by topic. Generated, never hand-maintained.

    `DR-76` decided that surface 4 of `DR-69` is a VIEW and not a restructuring, for the reason
    `DR-71` gave about the profile: the goal was never nesting, it was that a reader sees twelve
    named subjects. `CONFORMANCE_LEVELS` stays a flat map of level -> controls, read by 58 places
    that all ask "is this control required here" and none of which ask about topics. Keying it by
    topic would hold `rules.CONTROL_TOPICS` twice inside the framework, which is `F130`'s shape.
    """
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import rules  # noqa: E402

    levels = ("essential", "standard", "full")
    lines = [
        TOPICS_BEGIN,
        "",
        "Generated by `tests/check_code_registers.py --write` from the checker's own",
        "`CONFORMANCE_LEVELS` and the topic map in `rules.py`; the same script fails in CI when this",
        "table and the code disagree. A topic with no row requires no *selectable control* at any",
        "level by this axis - which is not the same as requiring nothing, since the nineteen",
        "prerequisite gates are a separate obligation with their own catalogue grouping.",
        "",
        "| Topic | Every level | `essential` | `standard` | `full` |",
        "|---|---|---|---|---|",
    ]
    # The three baseline controls are required at EVERY level and are therefore absent from
    # `CONFORMANCE_LEVELS`. Omitting them made topics 3 and 8 read as four em-dashes - a topic
    # that in fact obliges every adopter, shown as obliging none. They get their own column.
    baseline = sorted(checker.BASELINE_CONTROLS) if hasattr(checker, "BASELINE_CONTROLS") else [
        "actual_diff_review", "agent_work_packets", "secret_hygiene"
    ]
    for number in sorted(rules.TOPIC_NAMES):
        controls = sorted(c for c, topic in rules.CONTROL_TOPICS.items() if topic == number)
        if not controls:
            continue
        always = [c for c in controls if c in baseline]
        cells = [", ".join(f"`{c}`" for c in always) if always else "—"]
        for level in levels:
            here = [c for c in controls if c in checker.CONFORMANCE_LEVELS[level]]
            cells.append(", ".join(f"`{c}`" for c in here) if here else "—")
        if set(cells) == {"—"}:
            continue  # a topic this axis says nothing about; the gates still may
        lines.append(f"| {number}. {rules.TOPIC_NAMES[number]} | " + " | ".join(cells) + " |")
    lines += ["", TOPICS_END]
    return "\n".join(lines)


def _installed_targets() -> set[str]:
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import install_standard  # noqa: E402

    payload = install_standard.build_payload(ROOT / "surfaceplate")
    targets = set(payload)
    # Written by the installer without being payload: the record, the profile it creates from
    # the template, and the two files it creates when absent and manages a block in.
    targets |= {install_standard.PROFILE_PATH, ".standards/INSTALL.json", ".github/copilot-instructions.md", "AGENTS.md"}
    return targets


def _resolves_installed(path: str, targets: set[str]) -> bool:
    import fnmatch

    bare = path.rstrip("/")
    if "*" in bare:
        return any(fnmatch.fnmatch(t, bare) for t in targets)
    return any(t == bare or t.startswith(bare + "/") for t in targets)


def front_door_checks(checker_text: str, write: bool) -> None:
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import check_conformance  # noqa: E402

    targets = _installed_targets()
    for doc in (README, INSTALL):
        text = doc.read_text(encoding="utf-8")
        for target in sorted(set(LINK.findall(text))):
            # `F162`: README.md is rendered by PyPI as well as by GitHub, and PyPI resolves a
            # relative link against `pypi.org` - so `](INSTALL.md)` became a 404 on the project
            # page. The README's file links are therefore absolute.
            #
            # Absolute links used to be SKIPPED here, which would have traded a 404 on PyPI for a
            # link to a deleted file nobody checks. This repository's own blob URLs are resolved
            # by their path instead, so both properties hold: the reader gets a link that works
            # from either renderer, and a target that stops existing still fails this suite.
            own = OWN_BLOB.match(target)
            if own:
                check(f"{doc.name}: link `{target}` resolves in this repository",
                      (ROOT / own.group(1)).exists(), f"no such path: {own.group(1)}")
                continue
            if "://" in target or target.startswith("mailto:"):
                continue
            check(f"{doc.name}: link `{target}` resolves in this repository", (doc.parent / target).exists())
        for path in sorted(set(PATHISH.findall(text))):
            if path.startswith((".standards/", ".github/")):
                check(f"{doc.name}: `{path}` exists in an installed checkout", _resolves_installed(path, targets))
            else:
                check(f"{doc.name}: `{path}` exists in this repository", (ROOT / path.replace("*", "")).exists() or (ROOT / path.split("*")[0]).exists())
    readme = README.read_text(encoding="utf-8")
    version = VERSION_FILE.read_text(encoding="utf-8").strip()
    stated = re.search(r"\*\*Version ([0-9][0-9.]*)\.\*\*", readme)
    check("README.md states the version surfaceplate/VERSION holds", bool(stated) and stated.group(1) == version,
          f"README says {stated.group(1) if stated else 'nothing'}, VERSION is {version}")
    gates = len(check_conformance.GATE_CATALOGUE)
    for doc in (README, INSTALL, LEVELS_DOC, ROOT / "surfaceplate" / "core" / "PREREQUISITE_GATES.md"):
        text = doc.read_text(encoding="utf-8")
        for number in re.findall(r"\b(\d+)(?:-gate catalogue| prerequisite gates)\b", text):
            check(f"{doc.name}: '{number} gates' is the catalogue's count", int(number) == gates, f"the catalogue holds {gates}")
    levels = LEVELS_DOC.read_text(encoding="utf-8")
    controls = len(check_conformance.CONFORMANCE_LEVELS["full"]) + 3
    checked = len(check_conformance.VERIFIED_CONTROLS | {"secret_hygiene"})
    for ten, twelve in re.findall(r"\*\*(\w+) of the (\w+) controls this framework defines are checked\*\*", levels):
        check("CONFORMANCE_LEVELS.md: the checked-controls sentence matches the checker", WORDS.get(ten.lower()) == checked and WORDS.get(twelve.lower()) == controls,
              f"document says {ten} of {twelve}; checker has {checked} of {controls}")
    check("CONFORMANCE_LEVELS.md does not also claim every control is checked",
          "Every control is checked" not in levels and "Nothing is declared-only" not in levels.split("*This paragraph read")[0])
    # `DR-76`: the levels-by-topic view, same generate-and-check pattern as the catalogue below.
    topic_view = render_levels_by_topic(check_conformance)
    tbegin, tend = levels.find(TOPICS_BEGIN), levels.find(TOPICS_END)
    present_topics = levels[tbegin:tend + len(TOPICS_END)] if tbegin >= 0 and tend >= 0 else ""
    if write and present_topics != topic_view:
        if tbegin >= 0:
            levels = levels[:tbegin] + topic_view + levels[tend + len(TOPICS_END):]
        else:
            levels = levels.rstrip("\n") + "\n\n## What each level requires, by topic\n\n" + topic_view + "\n"
        LEVELS_DOC.write_text(levels, encoding="utf-8")
        present_topics = topic_view
        print(f"wrote the levels-by-topic view into {LEVELS_DOC.relative_to(ROOT)}")
    check("CONFORMANCE_LEVELS.md's levels-by-topic view matches the checker and the topic map",
          present_topics == topic_view, "run: python tests/check_code_registers.py --write")

    # `DR-69`: "twelve" names three different things in the shipped corpus - controls, topics, and
    # cross-application control principles. A bare "the twelve" is therefore unreadable, and the
    # collision is the kind that only becomes visible once someone writes the ambiguous sentence.
    for path in sorted((ROOT / "surfaceplate" / "standard" / "topics").glob("*.md")) + [
        LEVELS_DOC,
        ROOT / "surfaceplate" / "core" / "PREREQUISITE_GATES.md",
        ROOT / "surfaceplate" / "core" / "CONTROL_PRINCIPLES.md",
        ROOT / "surfaceplate" / "standard" / "conformance-block.md",
    ]:
        if not path.exists():
            continue
        bare = BARE_TWELVE.findall(path.read_text(encoding="utf-8"))
        check(f"{path.name}: 'twelve' is never used bare - it names three different sets here",
              not bare, f"{len(bare)} bare use(s)")

    expected = render_catalogue(checker_text)
    begin, end = levels.find(CATALOGUE_BEGIN), levels.find(CATALOGUE_END)
    present = levels[begin:end + len(CATALOGUE_END)] if begin >= 0 and end >= 0 else ""
    if write and present != expected:
        if begin >= 0:
            levels = levels[:begin] + expected + levels[end + len(CATALOGUE_END):]
        else:
            levels = levels.rstrip("\n") + "\n\n## Every finding code the checker can report\n\n" + expected + "\n"
        LEVELS_DOC.write_text(levels, encoding="utf-8")
        present = expected
        print(f"wrote the finding-code catalogue into {LEVELS_DOC.relative_to(ROOT)}")
    check("every code the checker emits is in the generated catalogue in CONFORMANCE_LEVELS.md, and nothing else is",
          present == expected, "run: python tests/check_code_registers.py --write")


def dependency_pin_checks() -> None:
    """`F130`: the same version is pinned in five places and nothing compared them.

    `pyproject.toml` is the authority for what this package depends on. The self-check workflow
    installs its own hard-coded copy of that list; `standards-conformance.yml` installs the two
    runtime pins; the **payload's** copy of that workflow installs them into every adopting
    repository; and `INSTALL.md` tells a reader to install `textual` by version. Five declarations
    of one fact.

    Found when Dependabot's pytest bump edited `pyproject.toml` alone and every suite passed:
    CI had installed 8.4.2 from its own line and never saw the change under review. A dependency
    change was about to be judged by a run that did not install it - and the payload copy makes the
    same drift reach adopters, whose CI would install a set the package does not declare.

    LIMIT, stated rather than implied: this compares versions for packages `pyproject.toml`
    declares. A pin elsewhere for something it does not declare (`build` in `publish.yml`, a
    publish-time tool) is not checked, because there is no authority here to compare it against.
    """
    import tomllib

    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    declared: dict[str, str] = {}
    groups = [project.get("dependencies", [])] + list(project.get("optional-dependencies", {}).values())
    for group in groups:
        for spec in group:
            m = PINNED.fullmatch(spec.strip())
            if m:
                declared[m.group(1).lower().replace("_", "-")] = m.group(2)
    check("pyproject.toml declares exactly-pinned dependencies to compare against", bool(declared))

    files = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    files += sorted((ROOT / "surfaceplate" / "standard" / ".github" / "workflows").glob("*.yml"))
    files += [ROOT / "INSTALL.md", ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "scripts" / "front_door.sh"]
    for path in files:
        if not path.exists():
            continue
        for name, version in PINNED.findall(path.read_text(encoding="utf-8")):
            key = name.lower().replace("_", "-")
            if key not in declared:
                continue
            check(
                f"{path.relative_to(ROOT).as_posix()}: {name}=={version} matches pyproject.toml",
                version == declared[key],
                f"pyproject.toml pins {declared[key]}",
            )


def payload_pointer_checks(targets: set[str]) -> None:
    """`F128`: the front door is checked and the payload's own documents were not.

    The `change` skill, shipped to every adopter, said *"the registered activity ID (see
    `activity.instructions.md`)"* - a file the twelve-topic restructure stopped writing three
    surfaces earlier, and a Copilot-only emitted filename before that. Nothing failed, because no
    check reads what the payload says about itself. `F50` is the same defect one layer out: a
    hand-off command naming a file deleted three packets earlier, caught only when someone ran it.

    Narrow on purpose. It resolves exactly the pointers that name an installed destination - an
    agent-instruction filename, a rules file, a skill, or a `.standards/` path. A payload document
    naming `README.md` or a stack's own file is naming the adopter's tree, which this cannot and
    must not try to resolve.
    """
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import install_standard  # noqa: E402

    payload = install_standard.build_payload(ROOT / "surfaceplate")
    for dest in sorted(payload):
        if not dest.endswith(".md"):
            continue
        source = payload[dest]
        text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
        for pointer in sorted(set(PAYLOAD_POINTER.findall(text))):
            # A bare `x.instructions.md` can only mean the Copilot destination; that it reads as a
            # bare filename is part of what made this defect survive.
            qualified = pointer if "/" in pointer else f".github/instructions/{pointer}"
            check(
                f"payload {dest}: `{pointer}` names a file the installer writes",
                _resolves_installed(qualified, targets),
                "no installed destination matches it",
            )


def agent_prompt_names_commands_that_exist() -> None:
    """`ACT-100`: every `surfaceplate …` invocation in the generated prompt parses.

    This is `S3` - *run an instruction before publishing it* - applied to the one output whose
    entire purpose is to be followed. `F57` is what happens otherwise: a README, an `INSTALL.md`
    and the tool itself all naming a package that 404s, because a document is read for sense
    rather than run.

    The prompt is prose that names commands and flags, so it will drift from the CLI unless
    something compares them. A renamed flag now breaks this suite rather than an adopter who
    pasted the prompt into an agent and watched it fail.
    """
    import sys

    sys.path.insert(0, str(ROOT))
    from surfaceplate import assist, cli

    prompt = assist.build_prompt(ROOT, register="simple")
    invocations = re.findall(r"`surfaceplate ([a-z-]+)((?: [^`]*)?)`", prompt)
    check("the prompt names some commands - an empty sweep proves nothing", bool(invocations),
          f"{len(invocations)} found")

    for command, tail in invocations:
        check(
            f"the prompt's `surfaceplate {command}` is a real command",
            command in cli._COMMANDS,
            f"known: {', '.join(sorted(cli._COMMANDS))}",
        )
        # Long flags only. A value like `.` or a path placeholder is the adopter's to supply and
        # cannot be validated here; a FLAG that does not exist is the drift this guards against.
        for flag in re.findall(r"(--[a-z-]+)", tail):
            check(
                f"the prompt's `{flag}` is a real flag of `surfaceplate {command}`",
                _flag_exists(command, flag),
                f"{command} does not accept {flag}",
            )


def _flag_exists(command: str, flag: str) -> bool:
    """Whether `surfaceplate <command> <flag>` is accepted, asked of the real parser.

    Runs the command's own `--help` in a subprocess: each builds its parser inside its handler,
    so there is no parser object to interrogate without invoking it, and `--help` is the one
    invocation that is guaranteed to write nothing.
    """
    import subprocess
    import sys

    out = subprocess.run(
        [sys.executable, "-m", "surfaceplate.cli", command, "--help"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    return flag in (out.stdout + out.stderr)


def nothing_is_defined_below_the_entry_point() -> None:
    """`F152`: a module's `if __name__ == "__main__"` block must be the last thing in it.

    `ACT-081` appended `uninstall` and `_prune_empty` - some 125 lines - BELOW that block in
    `install_standard.py`. Imported, the whole module executes and everything binds; run as a
    script, `main()` is called before the interpreter ever reaches those definitions, so they do
    not exist. `uninstall` is only ever imported, so it never showed a symptom.

    It surfaced when `install()` - which IS run as a script - first called `_prune_empty`:
    `NameError`, **after one file had already been deleted**. A half-completed removal.

    Cheap to check and impossible to notice by reading, because the file looks completely normal:
    the defect is a relationship between two line numbers, not anything at either one.
    """
    for path in sorted((ROOT / "surfaceplate").rglob("*.py")) + sorted((ROOT / "scripts").glob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        guard = next((i for i, line in enumerate(lines) if line.startswith('if __name__ == "__main__"')), None)
        if guard is None:
            continue
        below = [
            f"{path.name}:{i + 1}"
            for i, line in enumerate(lines[guard + 1:], start=guard + 1)
            if line.startswith(("def ", "class ")) or (line and not line[0].isspace() and "=" in line.split("#")[0] and not line.startswith(("if ", "raise ")))
        ]
        check(
            f"{path.relative_to(ROOT)}: nothing is defined below the __main__ block",
            not below,
            ", ".join(below[:4]),
        )


def hook_target_agrees() -> None:
    """`F156`: `adopt` names the hook path it declares; the checker names the one it looks for.

    Two copies of one fact, and a profile that declared a path the checker did not check would
    pass while guarding nothing - `DR-48`'s discipline, applied to the one constant `adopt` could
    not simply import (it must work where the checker is not importable).
    """
    import sys

    sys.path.insert(0, str(ROOT))
    from surfaceplate.adopt import sections

    checker = re.search(r'^HOOK_TARGET = "([^"]+)"', CHECKER.read_text(encoding="utf-8"), re.M)
    check("check_conformance.py declares HOOK_TARGET", checker is not None)
    if checker is not None:
        check(
            "adopt declares the same hook path the checker looks for",
            sections.HOOK_TARGET == checker.group(1),
            f"adopt={sections.HOOK_TARGET!r} checker={checker.group(1)!r}",
        )


def agent_tables_name_the_same_channels() -> None:
    """`F171`: a third agent must be impossible to add to one table and forget in the other.

    `rules.AGENT_CHANNELS` says which paths a channel owns; `rules.AGENT_BLOCK_PROSE` says how the
    conformance block describes it. A channel in the first and not the second renders an adopter a
    block with a missing sentence — or a `KeyError` mid-install. A channel in the second and not
    the first describes files nobody installs.

    This is `F58`'s shape, which is why it is checked rather than trusted: `DR-30`'s per-agent
    pattern was applied to six instruction documents and not to seven skills, and nothing noticed
    for five releases.
    """
    import sys

    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import rules as _rules  # noqa: E402

    channels, prose = set(_rules.AGENT_CHANNELS), set(_rules.AGENT_BLOCK_PROSE)
    check(
        "every agent channel has block prose",
        not (channels - prose),
        ", ".join(sorted(channels - prose)),
    )
    check(
        "and the block prose names no channel that is not installed",
        not (prose - channels),
        ", ".join(sorted(prose - channels)),
    )
    bad = sorted(n for n, row in _rules.AGENT_BLOCK_PROSE.items() if len(row) != 3 or not all(row))
    check("and each row carries a label, a topic path and a skill path", not bad, ", ".join(bad))

    # These four paths used to sit in `conformance-block.md` as prose, where `payload_pointer_checks`
    # resolved them against the installer's own destinations. Rendering the block from this table
    # moved them out of the document and out of that check's reach - a silent LOSS of coverage
    # bought by a gain elsewhere, which is the trade this project is meant to notice rather than
    # bank. Resolved here instead, against the same destinations, so the table is checked rather
    # than the sentence it happens to produce.
    targets = _installed_targets()
    unresolved = sorted(
        p
        for row in _rules.AGENT_BLOCK_PROSE.values()
        for p in row[1:]
        if not _resolves_installed(p, targets)
    )
    check(
        "and every path it names is one the installer actually writes",
        not unresolved,
        ", ".join(unresolved),
    )


def no_script_writes_the_machine_s_git_config() -> None:
    """`F164`: a script under `scripts/` may set global git config, but only in a sandbox.

    `front_door.sh` must set a GLOBAL `core.hooksPath` - that is `F70`'s condition and the whole
    point of the script. Until this check it wrote that, and a git identity, into the invoking
    user's real `~/.gitconfig`, then deleted the directory it had pointed the hooks at. Run in a
    container that is harmless; run by hand it silently disabled every git hook on the machine and
    misattributed every later commit in any repository without a local identity.

    The property is therefore not "do not set global config" but **"redirect the global scope
    first"**: `GIT_CONFIG_GLOBAL` must be exported above the first `git config --global` write in
    the same file. Checked by position, because an export below the write protects nothing.
    """
    scripts = sorted((ROOT / "scripts").glob("*.sh"))
    check("there are shell scripts to check", bool(scripts), str(len(scripts)))
    for script in scripts:
        lines = script.read_text(encoding="utf-8").splitlines()
        writes = [n for n, line in enumerate(lines)
                  if "git config --global" in line and not line.lstrip().startswith("#")]
        if not writes:
            continue
        redirects = [n for n, line in enumerate(lines) if "export GIT_CONFIG_GLOBAL=" in line]
        check(
            f"{script.name} redirects the global git scope before writing to it",
            bool(redirects) and min(redirects) < min(writes),
            f"first write at line {min(writes) + 1}, "
            + (f"export at line {min(redirects) + 1}" if redirects else "no export"),
        )


def main() -> int:
    import sys

    write = "--write" in sys.argv[1:]
    findings_text = FINDINGS.read_text(encoding="utf-8")
    checker_text = CHECKER.read_text(encoding="utf-8")
    front_door_checks(checker_text, write)
    payload_pointer_checks(_installed_targets())
    dependency_pin_checks()
    nothing_is_defined_below_the_entry_point()
    agent_prompt_names_commands_that_exist()
    hook_target_agrees()
    no_script_writes_the_machine_s_git_config()
    agent_tables_name_the_same_channels()

    # ---- SP codes: declaration against the code that emits them ----
    space = declared_space(findings_text)
    emitted = {int(code[2:]) for code in EMITTED.findall(checker_text)}

    check(
        "every emitted SP code is declared",
        emitted <= space["emitted"],
        ", ".join(f"SP{n:03d}" for n in sorted(emitted - space["emitted"])),
    )
    check(
        "every declared SP code is emitted",
        space["emitted"] <= emitted,
        ", ".join(f"SP{n:03d}" for n in sorted(space["emitted"] - emitted)),
    )
    # The SDS036 defect: a code documented but implemented by nothing, for releases, unnoticed.
    check(
        "no reserved SP code is quietly in use",
        not (space["reserved"] & emitted),
        ", ".join(f"SP{n:03d}" for n in sorted(space["reserved"] & emitted)),
    )
    check(
        "no declared gap is in use",
        not (space["gap"] & emitted),
        ", ".join(f"SP{n:03d}" for n in sorted(space["gap"] & emitted)),
    )
    # An undeclared hole is the thing that hides a code nobody remembers removing.
    whole = space["emitted"] | space["gap"] | space["reserved"]
    holes = set(range(1, max(whole) + 1)) - whole
    check(
        "the SP space has no undeclared hole",
        not holes,
        ", ".join(f"SP{n:03d}" for n in sorted(holes)),
    )

    # ---- SP codes carry a topic (`DR-69` surface 5, `DR-77`) ----
    sys.path.insert(0, str(ROOT / "surfaceplate"))
    import rules as _rules  # noqa: E402

    missing = sorted(f"SP{n:03d}" for n in emitted if f"SP{n:03d}" not in _rules.SP_TOPICS)
    check("every emitted SP code has a topic", not missing, ", ".join(missing))
    stray = sorted(c for c in _rules.SP_TOPICS if int(c[2:]) not in emitted)
    check("and SP_TOPICS names no code the checker does not emit", not stray, ", ".join(stray))
    bad = sorted(f"{c}={t}" for c, t in _rules.SP_TOPICS.items() if t not in _rules.TOPIC_NAMES)
    check("every topic named is one of the twelve topics", not bad, ", ".join(bad))

    # ---- F codes: the register against itself ----
    rows = [int(m) for m in re.findall(r"^\| F(\d+) \|", findings_text, re.MULTILINE)]
    bodies = [int(m) for m in re.findall(r"^## F(\d+) ", findings_text, re.MULTILINE)]

    check("the live register is not empty", bool(rows))
    check(
        "no F code is indexed twice",
        len(rows) == len(set(rows)),
        ", ".join(f"F{n}" for n in sorted({n for n in rows if rows.count(n) > 1})),
    )
    check(
        "no F code has two body sections",
        len(bodies) == len(set(bodies)),
        ", ".join(f"F{n}" for n in sorted({n for n in bodies if bodies.count(n) > 1})),
    )
    check(
        "F codes are contiguous from F1",
        set(rows) == set(range(1, max(rows) + 1)) if rows else False,
        ", ".join(f"F{n}" for n in sorted(set(range(1, max(rows) + 1)) - set(rows))) if rows else "",
    )
    # A body with no index entry is a finding that exists but cannot be found from the table -
    # the register's own summary would understate what it holds.
    check(
        "every body section is indexed in the table",
        set(bodies) <= set(rows),
        ", ".join(f"F{n}" for n in sorted(set(bodies) - set(rows))),
    )
    # `F72`: ten findings said Open in the body and Closed in the index, and nothing compared
    # them. The index row's status column and the body's `**Severity: ... <status>.**` line
    # must agree on Open versus Closed; a partial closure ("Closed for deferrals; open for
    # gate exceptions") counts as whichever word it leads with.
    index_status = {
        int(m.group(1)): m.group(2).strip().strip("*").strip()
        for m in re.finditer(r"^\| F(\d+) \|[^|]*\|[^|]*\| ([^|]*)\|", findings_text, re.MULTILINE)
    }
    body_status = {
        int(m.group(1)): m.group(2).strip()
        for m in re.finditer(r"^## F(\d+) [^\n]*\n\n\*\*Severity: [^.]*\. ([^*]*)\*\*", findings_text, re.MULTILINE)
    }

    # `DR-86`: three states, not two. `Accepted` is decided, no action pending, and the condition
    # PERSISTS - which `Open` overstates (it implies work outstanding) and `Closed` understates
    # (it reads identically to a defect that was fixed). The register's whole job is answering
    # *what is still wrong here*, and it could not distinguish an accepted risk from a repaired
    # one without this.
    def word(status: str) -> str:
        head = status.lower()
        for known in ("closed", "accepted", "open"):
            if head.startswith(known):
                return known
        return "?"

    disagree = sorted(
        n for n in body_status if n in index_status and word(index_status[n]) != word(body_status[n])
    )
    check(
        "every finding's body status agrees with its index status (F72)",
        not disagree,
        ", ".join(f"F{n} (index {word(index_status[n])}, body {word(body_status[n])})" for n in disagree),
    )
    unparsed = sorted(n for n in body_status if word(body_status[n]) == "?")
    check(
        "every body status line leads with Open, Accepted or Closed",
        not unparsed,
        ", ".join(f"F{n}: {body_status[n][:40]!r}" for n in unparsed),
    )
    # `DR-86`: an accepted finding says what would reopen it, or it is an abandonment wearing a
    # decision's clothes. `F131`'s trigger is an upstream release; `F55`'s is the habit failing.
    accepted = [n for n in body_status if word(body_status[n]) == "accepted"]
    bodies = {
        int(m.group(1)): m.group(2)
        for m in re.finditer(r"^## F(\d+) [^\n]*\n(.*?)(?=^## F\d+ |\Z)", findings_text,
                             re.MULTILINE | re.DOTALL)
    }
    silent = [n for n in accepted if "what would reopen" not in bodies.get(n, "").lower()]
    check(
        "every Accepted finding states what would reopen it (DR-86)",
        not silent,
        ", ".join(f"F{n}" for n in silent),
    )

    if FAILURES:
        print("CODE_REGISTERS=FAIL")
        print()
        for failure in FAILURES:
            print(f"  {failure}")
        print()
        print("Something states a fact about this repository that this repository does not have.")
        print("Correct the statement, or the code it describes, so the two agree - a register or a")
        print("document that describes what is not there is worse than none: it reads as")
        print("authoritative and is not. For a payload pointer, the document ships to every")
        print("adopter, so the wrong name is theirs to trip over as well as yours.")
        return 1

    # Reported so that "the registers agree" is distinguishable from "nothing was compared",
    # the defect recorded as F3.
    print(
        f"CODE_REGISTERS=PASS  ({CHECKS} checks; "
        f"{len(space['emitted'])} SP codes, {len(rows)} F codes)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
