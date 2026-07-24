# The grem lifecycle — how change propagates back and forth

A behavior lens for the whole grem loop, told as one continuous story: a single
developer, **Alice**, uses grem to build a small Python **calculator** and, in
doing so, exercises every direction that change can travel.

grem's premise is that change in an AI-assisted project never flows one way. It
circulates. Structure flows **down** from a template into a project. Truth flows
**across** between a project's scopes as declarations and code are reconciled.
Knowledge flows **sideways** from one project to another as portable styles.
And hard-won lessons flow **up** from a working project back into the template
that seeded it. This document walks that circulation once, end to end.

> **Companion deck:** [grem-lifecycle/](./grem-lifecycle/) retells this story as
> a numbered set of D2 "visual story" diagrams — one idea per slide.

---

## 1. Vision — a project is more than source and tests

Alice could start her calculator with an empty folder, a `src/`, and a `tests/`.
But an AI-assisted project needs more than that. It needs distinct, durable
*homes* for the different kinds of truth that agents and humans both rely on:

- **declarations** of what the system is (requirements, data, domain, behavior),
- a **cross-linked knowledge base** — a wiki of hyper-markdown (`.hmd`) cards,
- **active work** in flight,
- **small real-time decisions** that must be reloaded on every agent turn,
- **numbered technical proposals**, and
- **operating instructions** for the agents themselves.

Without those homes, that knowledge scatters into commit messages, chat logs,
and people's heads. grem's job is to stamp those homes into existence and keep
them coherent as the project evolves — **grem stamps structure; agents do the
work.**

## 2. Two layers — deterministic mechanics vs. semantic work

grem keeps two layers strictly separated, and the whole lifecycle depends on
that separation:

- The **CLI** is deterministic. It discovers a template manifest and places
  folders and files byte-for-byte. Same template plus same inputs produce the
  same paths and bytes — no timestamps, no machine-specific values, no LLM.
- The **template** owns all generated project knowledge and agent behavior: the
  knowledge-base skeleton, the dormant `.grem/` harness of prompts, and the
  portable documentation styles.
- **Agents** (Claude, Codex, …) do the semantic work. Every grem workflow
  subcommand prints a Markdown *prompt* to stdout; it never edits files or calls
  a model itself. The agent reads that prompt and carries it out.

This is why grem can be trusted near a real codebase: the risky, judgement-heavy
work is always gated behind an agent and a user, while the CLI only does the
predictable, reversible mechanics.

## 3. Init — structure flows down (template → project)

Alice runs one command:

```console
grem init ./calc
```

Like `git init`, this defaults to the bundled `python` template and refuses to
run if a `.grem/` folder already exists. It stamps her project tree: `src/calc/`,
`tests/`, a full `doc/` knowledge base (`models/`, `wiki/`, `issues/`,
`memory/`, `proposals/`), agent instruction files (`CLAUDE.md`, `AGENTS.md`),
and the dormant `.grem/` control layer with its harness prompts and styles.

This is the first and most literal propagation: the template's structure flows
**down** into Alice's project. At this moment the project is all scaffold and no
content — the homes exist, but they are empty.

## 4. Declare and build — the project comes alive

Now Alice does the actual engineering, and she does it in both scopes at once:

- In `doc/models/behavior/` she declares how the calculator must behave:
  *division by zero raises `ZeroDivisionError`; results are exact.*
- In `doc/memory/` she records a small decision that must survive every agent
  turn: *use `Decimal`, never `float`, so `0.1 + 0.2` is exact.*
- In `src/calc/ops.py` she implements `add`, `sub`, `mul`, `div`.
- In `tests/` she pins the behavior she cares about.

Two scopes now make claims about the same system: `doc/models/` *declares* the
intended truth, and `src/` *demonstrates* the actual truth. As long as a human is
typing in both, they drift. grem's next two commands exist to make that drift
visible and then resolve it.

## 5. Diff — truth flows across, drift made visible (scope ↔ scope)

Alice asks grem to compare her declarations against her code:

```console
grem diff doc/models src
```

The CLI validates both scopes and prints the semantic-diff prompt. This is **not**
a textual diff — the agent reads both sides and reports what each *means*, then
lists the contradictions, missing counterparts, stale declarations, and behavior
that is specified but not evidenced. For Alice's calculator it finds:

1. The behavior lens says `div(x, 0)` **raises**; `src/calc/ops.py` returns
   `float('inf')`. *Contradiction.*
2. The requirements lens promises a `sqrt` operation; `src/` has none.
   *Missing counterpart.*
3. A line in the domain lens still describes an old "RPN input" idea nothing else
   references. *Stale declaration.*

grem deliberately **stops there**. The output is a numbered, evidence-backed list
and nothing more. Neither scope is automatically authoritative, so the user — not
the agent — decides what each item means.

## 6. Sync — the reconciliation loop (change propagates across)

Alice classifies the findings: (1) is a **bug** in the code, (2) is a
**follow-up feature**, (3) is an **accepted difference** to delete from the doc.
Then she runs the full loop:

```console
grem sync doc/models src
```

`sync` begins with the same semantic diff, takes her dispositions, then runs:

```text
diff → user disposition → plan → implement → test → document → diff
```

The agent fixes `div` to raise, adds `sqrt` with tests, and prunes the stale
domain line — repeating the diff until the approved inconsistencies are gone or a
concrete blocker needs Alice. Change has now propagated **across** the project:
declarations shaped the code, and the code's proven behavior flowed back into the
docs. The two scopes agree again, and every step is evidenced by tests.

## 7. Styles — knowledge flows sideways (project → project)

A teammate is about to join. Alice wants the behavior lens as an at-a-glance
deck, so she applies a stored **documentation style**:

```console
grem new doc/models/behavior/grem-lifecycle.md --type doc --style slides
```

A style is a *portable* prompt — it describes how to reproduce one documentation
style on **any** project, not tied to this repo. `grem new` validates the source
file and prints the style prompt parameterized with that path; the agent produces
the output (in this case, the very D2 deck that accompanies this document). The
same `slides`, `hmd`, `adr`, and `lenses` styles Alice used here can be lifted
into an unrelated project unchanged. Knowledge flows **sideways**, carried by the
template rather than copy-pasted.

## 8. Upgrade — structure flows down again, but guarded

Months later, a newer `python` template ships (say `0.13 → 0.14`), adding a
`.gremignore` ownership boundary and real parameterization. Alice upgrades:

```console
grem upgrade ./calc
```

Upgrade is the one controlled exception that touches files — so it is fenced in:

- It **requires a clean Git worktree** (untracked files included) before writing.
- It scaffolds the new template into a temp dir, rejects symlink and
  file/folder conflicts, and **overlays only the template-owned layer**.
- A `.gremignore` protects **project-owned** paths — `src/`, `tests/`,
  `pyproject.toml`, `README.md`, and Alice's `doc/` knowledge — so the overlay
  refreshes the dormant harness and styles without clobbering her work.
- The changes land **unstaged**. Git is the diff, rollback, and merge surface.

The upgrade prompt then asks the agent to summarize `git diff`, spot any
customization the overlay replaced, and help merge it back — never discarding a
side blindly. Structure flowed **down** again, but through a guarded gate.

## 9. Feedback — lessons flow up (project → template)

Here the loop closes. The `.gremignore` boundary in step 8 did not appear by
magic — it exists because someone *dogfooded* upgrade and got burned. Running
`grem upgrade` on an early project **clobbered** project-owned files
(`pyproject.toml`, `README.md`, `CLAUDE.md`) with template placeholders and left
the package name unresolved. That pain was written up as a numbered issue in
`doc/issues/` (see [0001 — incomplete init and upgrade](../../issues/0001-incomplete-init-and-upgrade.md)),
which named three linked gaps: no ownership list, no real parameterization, and
derived parameters that never propagated.

Those findings flowed **up** into the template as a new version: a `.gremignore`,
Mustache parameterization (`{{ project_name }}`, `src/<package_name>`), and a
derived `proposal_prefix`. The next `grem init` **anywhere** inherits the fix.
A lesson learned in one project became structure for every future one — the
upward arrow that makes grem a loop instead of a one-shot generator.

## 10. The whole loop — one circulation

Put end to end, change in a grem project travels in every direction, and that is
the entire point:

- **Down** — `init` and `upgrade` push template structure into the project.
- **Across** — `diff` and `sync` reconcile declarations with code, so the
  project's scopes keep agreeing as it grows.
- **Sideways** — `new` carries portable styles from project to project.
- **Up** — dogfooding surfaces gaps that become `doc/issues/`, then a new
  template version that seeds every future project.

The CLI never does the thinking; it stamps structure, validates scopes, and
renders prompts. Agents and Alice do the semantic work. The template holds the
accumulated knowledge. Around that triangle, change circulates — back and forth,
down and up — which is why a grem project gets *more* coherent over time instead
of less.

---

## Related documentation

- Companion visual deck: [grem-lifecycle/](./grem-lifecycle/)
- Upstream-feedback archetype: [doc/issues/0001-incomplete-init-and-upgrade.md](../../issues/0001-incomplete-init-and-upgrade.md)
- Project overview and command model: [README.md](../../../README.md)
- Agent operating manual: [.grem/harness/README.md](../../../.grem/harness/README.md)
