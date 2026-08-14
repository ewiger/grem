# Run tests with `uv run python -m pytest`

**2026-08-14.** `uv run pytest` fails at collection in this checkout with
`ModuleNotFoundError: No module named 'grem'` — the console-script entry point
does not pick up the editable install's `.pth`. It fails the same way on a clean
`main`, so it is an environment quirk, not a code defect.

`uv run python -m pytest` works and runs the full suite. Use it until the
environment issue is diagnosed. `doc/stack.md` still documents `uv run pytest`
as the command, which is correct as the intended interface — CI runs exactly
that on Python 3.11-3.13 and passes. The local `.venv` is Python 3.14, which is
the likely difference.
