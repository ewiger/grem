# 0001 — Incomplete init and upgrade

- **Status:** Done
- **Discovered:** 2026-07-24, while dogfooding `grem upgrade .` on the grem repo.
- **Resolved:** 2026-07-24. All three gaps closed in the `python` template
  (bumped to `0.14.0`) and the CLI:
  - **Gap 1** — a per-template root `.gremignore` marks project-owned paths;
    `grem upgrade` overlays only the template-owned layer and skips them
    (`.gremignore` itself is always protected). `CLAUDE.md`/`AGENTS.md` are
    template-owned and refreshed — custom rules live under `doc/memory/`.
  - **Gap 2** — Mustache interpolation (`{{ project_name }}`) substitutes real
    parameters into paths and file contents. `grem init` resolves the project
    name (`--name` or the target folder, prompting when interactive) and records
    `variables:` in `.grem/config.yaml`; `src/myproject` → `src/<package_name>`.
  - **Gap 3** — the proposal ID prefix is the derived `proposal_prefix` variable
    (uppercased short form of the name), propagated to the proposals index and
    template.

## Summary

`grem upgrade` overlays *every* template file, and `grem init` copies vanilla
placeholders verbatim. Running upgrade on this repo clobbered project-owned
files (`pyproject.toml`, `README.md`, `CLAUDE.md`, `AGENTS.md`,
`doc/proposals/README.md`) with template placeholders and left the `myproject`
name unresolved. Three linked gaps make init/upgrade unsafe to run as-is.

## Gap 1 — No project-owned protection list (`.gremignore`)

The overlay rewrites files that belong to the project after init and must never
be re-stamped.

- Add an ignore/keep list — like `.gitignore`, e.g. a `.gremignore` file or a
  field in `.grem/config.yaml` — naming paths the overlay must not touch.
- Formalize the missing distinction:
  - **Template-owned** (harness prompts, styles) → refreshed on upgrade.
  - **Project-owned** (seeded once at init) → never overwritten.
- Result: `grem upgrade` refreshes only the dormant control layer; no clobber,
  no manual merge-back.

## Gap 2 — No real parameterization; `myproject` is never substituted

Templates ship literal placeholders (`name = "myproject"`, `src/myproject/`)
that scaffolding copies verbatim instead of resolving.

- `.grem/config.yaml` should carry **variables** (project name first, more
  later) that act as real parameters during generation *and* regeneration.
  Template content references the variable; the scaffolder substitutes it.
- `grem init` must prompt for the project name, defaulting to the **target
  folder name** (like `git init` uses the directory).
- The config is itself a "vanilla" output, so init must write a **parameterized**
  config (name filled in), not a literal `myproject` config.
- Once variables are real: `src/myproject` → `src/<name>`,
  `pyproject.name` → `<name>`, and upgrade can re-render deterministically.

## Gap 3 — Derived parameters not propagated (proposal ID prefix)

The proposals template ships `XYZ-0001`; this repo hand-evolved it to
`GREM-0001`. That drift is the missing-propagation problem.

- Make the proposal ID prefix a **derived parameter**, not a hardcoded
  placeholder.
- Preferred: an explicit variable in `.grem/config.yaml` (e.g.
  `proposal_prefix: GREM`), defaulting to an uppercased short form of the
  project name (`grem` ⇒ `GREM`).

## Through-line

Gaps 2 and 3 are one theme — parameter definition and propagation driven by
`.grem/config.yaml`. Gap 1 is the complementary ownership boundary that makes
upgrade safe. Together they define what real `grem init` and `grem upgrade` need.
