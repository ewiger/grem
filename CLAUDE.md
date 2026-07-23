# grem

grem stamps a project from a template. Diff, sync, and instruction commands
only print template-provided prompts. Upgrade requires a clean Git worktree,
overlays the new template, then prints a prompt for reviewing and merging the
Git diff.

Keep two layers separate:

- The CLI discovers a template manifest and deterministically places folders and
  files.
- Templates own all generated project knowledge and agent behavior.

Do not add linting, documentation publishing, git worktree management, or a
spec-to-code loop to the CLI.

The project knowledge base lives under `doc/`. Model lenses belong directly
under `doc/models/`; hyper-markdown wiki cards belong under `doc/wiki/`;
numbered ADR/RFC-style specifications belong under `doc/proposals/`.
Template control data and copyable agent prompts belong under `.grem/`.

At the start of every agent invocation, read every file under `doc/memory/` and
include those small real-time decisions in the work.

Ignore `.grem/**` during ordinary work. Do not inspect, summarize, follow, or
modify its contents unless the user explicitly asks to execute a grem workflow
or supplies a grem prompt for execution.
