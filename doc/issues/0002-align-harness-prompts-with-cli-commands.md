# 0002 — Align harness prompts with CLI commands

- **Status:** Backlog
- **Discovered:** 2026-07-25, while reviewing the quick-start demo.

## Summary

Harness prompt filenames should map one-to-one to the `grem` commands that
print them. The current agent-alignment prompt is named
`.grem/harness/instructions.md`, even though its public command is
`grem agent`.

Rename that prompt to `.grem/harness/agent.md` and update the corresponding
template declaration, CLI lookup, tests, and documentation so the command and
prompt mappings are:

- `grem agent` → `.grem/harness/agent.md`
- `grem diff` → `.grem/harness/diff.md`
- `grem sync` → `.grem/harness/sync.md`
- `grem upgrade` → `.grem/harness/upgrade.md`

## Acceptance criteria

- New projects contain `agent.md`, not `instructions.md`, in the harness.
- `grem agent` reads `agent.md`.
- Template upgrades migrate the template-owned prompt to the new filename
  without leaving a stale `instructions.md`.
- Tests and user-facing documentation consistently describe the one-to-one
  command-to-prompt naming.
