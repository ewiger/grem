# Shared template content is duplicated per template

**2026-08-14.** grem now bundles two templates, `python` and `rust`, under
`src/grem/templates/`. They carry byte-identical copies of the harness prompts
(`.grem/harness/*.md`), doc styles (`.grem/styles/doc/*/prompt.md`), wiki cards,
proposals `TEMPLATE.md`, the Kanban seed, `CLAUDE.md`, `AGENTS.md`, and the
Claude Code skill.

This is deliberate, not drift. `_build_plan` rejects any declared file whose
source escapes its own template's `content/`, so a shared pool would require new
CLI machinery — which `CLAUDE.md` rules out.

**Editing any of those files means editing both copies and bumping both
template `VERSION`s.** Two intentional divergences exist today: the `rust`
skill file points at `uv tool install grem-ai` instead of `uv run grem`, and the
`hmd` style prompt lists ```` ```rust ```` instead of ```` ```python ````.
