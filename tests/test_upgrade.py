from pathlib import Path

from grem.upgrade import (
    gremignore_matcher,
    load_gremignore,
    overlay_reference,
)


def test_load_gremignore_drops_comments_and_blanks(tmp_path: Path) -> None:
    (tmp_path / ".gremignore").write_text(
        "# a comment\n\npyproject.toml\n  src/**  \n# trailing\n"
    )

    assert load_gremignore(tmp_path) == ["pyproject.toml", "src/**"]


def test_load_gremignore_absent_is_empty(tmp_path: Path) -> None:
    assert load_gremignore(tmp_path) == []


def test_gremignore_matcher_globs_and_subtrees() -> None:
    matches = gremignore_matcher(["pyproject.toml", "src/**", "doc/memory/"])

    assert matches("pyproject.toml")
    assert matches("src/pkg/__init__.py")
    assert matches("doc/memory")
    assert matches("doc/memory/note.md")
    # `.gremignore` is always protected, even when unlisted.
    assert matches(".gremignore")
    # Non-matches stay writable.
    assert not matches("CLAUDE.md")
    assert not matches("srcfile.py")
    assert not matches("doc/proposals/TEMPLATE.md")


def _reference(tmp_path: Path) -> Path:
    reference = tmp_path / "reference"
    (reference / "src").mkdir(parents=True)
    (reference / "src" / "app.py").write_text("new\n")
    (reference / "CLAUDE.md").write_text("new claude\n")
    (reference / ".gremignore").write_text("new ignore\n")
    return reference


def test_overlay_skips_ignored_and_gremignore(tmp_path: Path) -> None:
    reference = _reference(tmp_path)
    project = tmp_path / "project"
    (project / "src").mkdir(parents=True)
    (project / "src" / "app.py").write_text("mine\n")
    (project / "CLAUDE.md").write_text("old claude\n")
    (project / ".gremignore").write_text("mine ignore\n")

    result = overlay_reference(
        reference, project, gremignore_matcher(["src/**"])
    )

    # Project-owned tree and the protection list survive.
    assert (project / "src" / "app.py").read_text() == "mine\n"
    assert (project / ".gremignore").read_text() == "mine ignore\n"
    # Template-owned file is refreshed.
    assert (project / "CLAUDE.md").read_text() == "new claude\n"
    assert result.files_written == 1
    assert result.files_skipped == 2
