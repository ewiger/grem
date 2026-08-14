# Stack

The language, tooling, and conventions grem is built on. Read this before adding
a dependency, picking a tool, or writing code, and update it when the stack
changes.

## Language

- Python 3.11 or newer. CI runs the test suite on 3.11, 3.12, and 3.13, so no
  syntax or standard-library feature newer than 3.11 may be used.
- Modern syntax only: `X | None` unions, built-in generics (`list[str]`),
  `from __future__ import annotations` at the top of every module, structural
  pattern matching where it beats a chain of `if`s.
- `pathlib.Path` and `PurePosixPath` for paths, `dataclasses` for records,
  `collections.abc` for container annotations.
- Prefer the standard library. Every dependency has to earn its place; the CLI
  stays small enough to install as a tool.

## Types

- Annotate every function signature, including `-> None`, plus module-level
  constants and dataclass fields.
- Types are part of the interface: prefer `Literal`, `TypeVar`, and
  `Mapping`/`Sequence` for parameters over `Any` and concrete containers.

## Environment and packaging

- [uv](https://docs.astral.sh/uv/) is the supported workflow: `uv sync`,
  `uv run pytest`, `uv run grem ...`, `uv add <package>`. Do not call `pip` or a
  bare `python`, and do not activate `.venv` by hand.
- `pyproject.toml` is the single manifest; `uv.lock` is committed and
  regenerated only through `uv`.
- setuptools build backend, `src/` layout. The distribution is published as
  `grem-ai`; the import package and console script are both `grem`.
- Template content ships as package data — new template files must be reachable
  by the `[tool.setuptools.package-data]` globs. Dotfiles at a template's
  `content/` root need their own glob line; the recursive globs do not match
  them.

## Dependencies

| Need | Choice |
| --- | --- |
| CLI framework | Typer |
| YAML and control data | PyYAML |
| Template version numbers | SemVer 2 (`semver`) |
| Clipboard for prompts | pyperclip |
| Tests | pytest |

## Tests

- pytest with Typer's `CliRunner`; `uv run pytest`. Test modules mirror the
  source module they cover: `tests/test_scaffold.py` for `src/grem/scaffold.py`.
- Tests are deterministic and offline, and use `tmp_path` for anything touching
  the filesystem.
- Each bundled template has an exact expected tree in `tests/test_scaffold.py`.
  Adding or removing a template file means updating that tree, the `generated:`
  list in `content/.grem/config.yaml`, and the template `VERSION`. A
  parametrized test scaffolds every bundled template and checks its tree
  against its own `generated:` list, so a forgotten entry fails there.

## Determinism

Scaffolding is the product's core promise: the same template and inputs produce
the same paths and the same bytes. No timestamps, no machine-specific values, no
network, canonical output ordering, and template declaration method bodies are
never executed.

## Releases

Publishing runs from GitHub, never from a laptop. Bump `version` in
`pyproject.toml`, run `uv sync` so `uv.lock` follows, commit, then tag
`vX.Y.Z` and publish a GitHub release for that tag. The `Release` workflow
(`.github/workflows/release.yml`) checks the tag against the packaged version,
runs the tests, builds with `uv build`, uploads to PyPI through trusted
publishing (OIDC — no stored token), and attaches the distributions to the
release. Retry a failed publish with the workflow's manual trigger.

## Diagrams

Slide decks under `doc/models/**/` are D2 sources rendered by
`scripts/render-d2.sh` (a thin `build.sh` in each deck folder delegates to it).
It commits `.svg` next to the `.d2` so diagrams render without the D2 toolchain;
`WITH_PNG=1` also emits PNG. `d2` and `rsvg-convert` come from Homebrew and are
not on a non-login `PATH` — the renderer exports it.

## Boundaries

Linting, documentation publishing, worktree management, and any
specification-to-code loop belong to the template and the generated project, not
to this CLI. Changing the stack is a decision: record a small one in
`doc/memory/`, a substantial one as a numbered proposal under `doc/proposals/`,
then update this file.
