# 0003 — Bundled Rust template

- **Status:** Done
- **Opened:** 2026-08-14. grem shipped exactly one bundled template, `python`,
  so `--template` had nothing to select but a local directory.
- **Resolved:** 2026-08-14. `src/grem/templates/rust/` ships at `0.1.0`.

## Summary

The CLI already resolved templates by directory name — `_template_directory`
falls back to `resources.files("grem.templates").joinpath(reference)` — so a
second bundled template needed no CLI change, only content. About 90% of the
`python` template is language-agnostic (harness prompts, doc styles, wiki
cards, proposals, Kanban, `CLAUDE.md`, `AGENTS.md`); the Rust template is that
content plus a Rust-shaped `doc/stack.md` and source layout.

## What the template stamps

- `Cargo.toml` (edition 2024, `rust-version = "1.85"`, a `[lib]` and a `[[bin]]`
  both named after the crate) and `rust-toolchain.toml` pinning the stable
  channel with `rustfmt` and `clippy`.
- `src/lib.rs` + `src/main.rs` + `tests/cli.rs` stubs that compile. Unlike the
  Python template's empty package folder, a fresh `grem init -t rust` passes
  `cargo build`, `cargo test`, `cargo clippy -- -D warnings`, and
  `cargo fmt --check`.
- `.gitignore` for `/target`. This is load-bearing: `require_clean_git_worktree`
  rejects untracked files, so an unignored `target/` would block every
  `grem upgrade`.

## Decisions

- **clap with `derive` is the Typer analogue.** The Python stack declares Typer
  — a CLI derived from typed function signatures. The Rust stack declares
  clap's `derive` API, deriving one from a typed struct. The rest of the
  default-choices table follows the same mirroring: cargo/rustup for uv,
  `cargo test` for pytest, serde + toml for PyYAML, thiserror/anyhow for the
  project exception type.
- **clap is the one shipped dependency.** The Python template's
  `pyproject.toml` has none, but a `main.rs` that demonstrates the derive idiom
  needs the crate. The cost is that a first `cargo build` requires network.
- **Shared content is duplicated, not shared.** A declared file's bytes must
  come from its own template's `content/` — the planner rejects any source that
  escapes it. Sharing would need new CLI machinery, which `CLAUDE.md` rules
  out. Editing a harness prompt or doc style now means editing both copies.

## Follow-on

A parametrized test scaffolds every bundled template and compares the produced
tree against that template's own `generated:` list, so the drift `doc/stack.md`
warns about now fails as a test rather than surfacing in a stamped project.
