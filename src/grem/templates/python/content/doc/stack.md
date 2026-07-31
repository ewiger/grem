# Stack

{{ project_name }} is built on this stack. Read it before adding a dependency,
picking a tool, or writing code — it is the contract contributors and agents
follow, so keep it current when the stack changes.

## Language

- Python 3.11 or newer. `requires-python` in `pyproject.toml` is the floor.
- Modern syntax only: `X | None` unions, built-in generics (`list[str]`),
  `from __future__ import annotations` at the top of every module, structural
  pattern matching where it reads better than a chain of `if`s.
- `pathlib.Path` for paths, `dataclasses` for records, `enum` for closed sets of
  values, `collections.abc` for container annotations.
- Prefer the standard library. Add a dependency only when it removes
  significant, well-understood work.

## Types

- Annotate every function signature, including `-> None`, and every
  module-level constant and dataclass field.
- Types are part of the interface. Prefer precise ones — `Literal`, `Protocol`,
  `TypeVar`, and `Mapping`/`Sequence` for parameters — and avoid `Any` unless
  the boundary is genuinely dynamic.
- Run a type checker over `src/` and `tests/` and configure it in
  `pyproject.toml`. A type error is a defect, not a warning.

## Environment and packaging

- [uv](https://docs.astral.sh/uv/) is the only supported workflow: `uv sync` to
  install, `uv run <command>` to execute, `uv add <package>` to add a
  dependency. Do not call `pip` or a bare `python`, and do not activate the
  virtualenv by hand.
- `pyproject.toml` is the single manifest. Development-only dependencies belong
  in `[dependency-groups] dev`.
- `uv.lock` is committed and is the reproducible resolution. Regenerate it with
  `uv add` or `uv lock`; never edit it by hand.
- `src/` layout: importable code lives in `src/{{ package_name }}/`, tests in
  `tests/`. Nothing importable sits at the repository root.

## Tests

- pytest, run as `uv run pytest`. Test modules mirror the source module they
  cover.
- Tests are deterministic and offline: no network, no wall-clock or
  machine-specific values, `tmp_path` for anything touching the filesystem.
- A behavior change lands with the test that pins it.

## Code conventions

- Every module opens with a docstring saying what it is for. Public functions
  and classes carry a one-sentence docstring; comments explain why, not what.
- Keep functions small and pure, and push I/O to the edges so the core stays
  testable.
- Raise a project-specific exception type for expected failures. No bare
  `except`.
- Match the surrounding code: naming, import order, and comment density are
  local conventions, not global ones.

## Default choices

Reach for these before introducing an alternative:

| Need | Choice |
| --- | --- |
| Environment and packaging | uv |
| Build backend | setuptools |
| Tests | pytest |
| CLI | Typer |
| YAML and config files | PyYAML |
| Version numbers | SemVer 2 (`semver`) |

Changing the stack is a decision, not a detail. Record a small one in
`doc/memory/` and a substantial one as a numbered proposal under
`doc/proposals/`, then update this file.
