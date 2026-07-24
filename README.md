# grem 👹

**Grem stamps structure. Agents do the work.**

grem (short for "gremlin") is a deterministic project bootstrap and control CLI for AI-assisted development. It stamps a versioned project layout, keeps agent workflows under `.grem/`, and turns those workflows into prompts for agents such as Claude and Codex.

The tool handles predictable mechanics. Templates define the knowledge model
and agent behavior. The generated project's agents perform the semantic work.

## Vision

AI-assisted projects need more than source and tests. They need distinct homes
for system declarations, active work, real-time decisions, technical proposals,
and operating instructions.

grem establishes and evolves that environment without becoming the project's
build system or autonomous agent:

- Scaffolding is deterministic: the same template and inputs produce the same
  paths and bytes.
- `.grem/` is a dormant control layer, activated only by an explicit user
  request.
- `doc/` is the project's modular knowledge base.
- Semantic comparison and synchronization are expressed as prompts, not hidden
  logic inside the CLI.
- Template upgrades use a clean Git worktree so Git provides the diff, rollback,
  and merge surface.

## Quick start

From this checkout:

```console
uv sync
uv run grem scaffold python ./myproject
```

The bundled Python template produces:

```text
myproject/
  .grem/
    config.yaml
    harness/
      README.md
      diff.md
      instructions.md
      sync.md
      upgrade.md
  src/myproject/
  tests/
  doc/
    models/
      data/
      domain/
      behavior/
    wiki/
    issues/
    memory/
    proposals/
      README.md
  AGENTS.md
  CLAUDE.md
  pyproject.toml
  README.md
```

The target must be absent or empty. grem rejects unsafe paths, duplicate output
paths, missing template sources, and non-empty targets.

## Command model

| Command | CLI action | Agent action |
| --- | --- | --- |
| `grem scaffold TEMPLATE TARGET` | Writes the declared project tree | None |
| `grem diff A B` | Validates two scopes and prints a semantic-diff prompt | Returns numbered inconsistencies |
| `grem sync A B` | Validates two scopes and prints the full reconciliation prompt | Plans, implements, tests, documents, and diffs |
| `grem instructions [PROJECT]` | Reads configured instruction targets and prints a prompt | Aligns `AGENTS.md`, `CLAUDE.md`, and other configured files |
| `grem upgrade [PROJECT]` | Overlays a newer template in a clean Git worktree | Reviews the Git diff and helps merge customizations |

`diff`, `sync`, and `instructions` do not modify project files or invoke an
LLM. Their output is copied into an agent by the user. `upgrade` is the
controlled exception: it overlays template files first, then prints the merge
prompt.

Use `--project` when diffing or syncing another project:

```console
uv run grem diff doc/models src --project ./myproject
uv run grem sync doc/models tests --project ./myproject
```

Both scopes must exist inside the selected project. A scope may be a file,
directory, or nested path under `doc/`, `src/`, `tests/`, or another project
area.

## Prompt lifecycle

Prompts under `.grem/harness/` follow an explicit lifecycle.

1. **Stamped** — the template places a versioned config and prompt set.
2. **Dormant** — generated agent instructions tell agents to ignore `.grem/**`
   during ordinary work.
3. **Activated** — the user runs a grem command or explicitly supplies a grem
   prompt for execution.
4. **Contextualized** — grem validates paths or versions and adds the concrete
   scopes, targets, or upgrade metadata to the prompt.
5. **Executed by an agent** — the user gives the prompt to Claude, Codex, or
   another LLM agent. Every workflow first loads `doc/memory/`.
6. **Gated by the user** — semantic-diff findings remain a numbered list until
   the user classifies them as a feature, bug, follow-up, accepted difference,
   or no action.
7. **Reconciled** — sync runs the approved plan → implement → test → document →
   diff loop until the selected inconsistencies are resolved or blocked.
8. **Evolved** — a newer template can update the config and harness through
   `grem upgrade`, with Git exposing every change.

This keeps activation intentional: agents always read `doc/memory/`, but they
do not inspect or execute `.grem/**` without a user request.

## Semantic diff and sync

`grem diff A B` compares what can be learned from two parts of a project. It is
not a textual diff. The generated prompt asks the agent to find contradictions,
missing counterparts, stale declarations, and behavior that is specified but
not evidenced.

The result is a numbered, evidence-backed list. grem deliberately stops there
so the user decides what each inconsistency means.

```console
uv run grem diff doc/models src
```

`grem sync A B` starts with the same semantic comparison, then provides the
complete agent loop:

```text
diff → user disposition → plan → implement → test → document → diff
```

Neither side is automatically authoritative. The agent uses project evidence,
`doc/memory/`, and user decisions to reconcile the scopes.

## Knowledge model

`doc/` contains categories of truth with different lifetimes:

- `doc/models/` declares the system through data, domain, and behavior lenses.
  [len](https://github.com/ewiger/len) files such as L0, L1, and L2 live
  directly here.
- `doc/wiki/` contains cross-linked hyper-markdown (`.hmd`) cards.
- `doc/issues/` tracks active work.
- `doc/memory/` contains small real-time decisions and is loaded for every agent
  invocation.
- `doc/proposals/` contains numbered ADR/RFC-style technical specifications.
  Reserve an ID such as `XYZ-0001` in `doc/proposals/README.md`, then create
  `doc/proposals/XYZ-0001/README.md`.

`.grem/` is not part of that knowledge base. It is versioned control data and a
dormant prompt harness.

## Agent instructions

Agent instruction files are configured in `.grem/config.yaml`:

```yaml
agent_instructions:
  central: .grem/harness/README.md
  targets:
    - AGENTS.md
    - CLAUDE.md
```

The Python template's `AGENTS.md` tells Codex to read `CLAUDE.md`. Both files
also preserve the two context rules:

- always load `doc/memory/**`;
- ignore `.grem/**` unless the user explicitly activates a grem workflow.

Generate the alignment prompt with:

```console
uv run grem instructions ./myproject
```

## Template upgrades

Templates use SemVer 2. `grem upgrade` compares the version recorded in
`.grem/config.yaml` with the selected template:

```console
uv run grem upgrade ./myproject
uv run grem upgrade ./myproject --template ./path/to/template
```

Before writing, upgrade requires the entire containing Git worktree to be
clean, including untracked files. It scaffolds the target into a temporary
directory, rejects symlinks and file/folder conflicts, then overlays generated
files without deleting old paths.

The changes remain unstaged. The resulting prompt asks the agent to summarize
`git diff`, identify overwritten customizations, and help merge them. Add
`--interactive` to confirm before the overlay.

## Templates

A template contains:

```text
template/
  bootstrap.py
  content/
    .grem/
      config.yaml
      harness/
```

`bootstrap.py` is a trusted Python module evaluated by grem. It declares a
template name, SemVer 2 version, and root `Moniker`:

```python
from grem.scaffold import Moniker, file, folder


NAME = "python"
VERSION = "0.6.0"


class Empty(Moniker):
    pass


class Project(Moniker):
    @folder
    def tests(self) -> Empty:
        ...

    @file("README.md")
    def readme(self):
        ...


ROOT = Project
```

Each folder element is an annotated method. Folder return annotations describe
nested `Moniker` trees; file declarations copy bytes from matching paths under
`content/`. Declaration method bodies are never executed.

The version in `bootstrap.py` must match `content/.grem/config.yaml`. Output
ordering is canonical, and scaffolding generates no timestamps or
machine-specific values.

Use a local template directory while developing one:

```console
uv run grem scaffold ./path/to/template ./myproject
```

## Boundaries

grem owns deterministic placement, validation, prompt rendering, template
version checks, and the safe upgrade overlay.

The template and generated project own linting, documentation publishing,
worktrees, semantic reconciliation, and the specification-to-code loop through
their harness and normal project tooling.
