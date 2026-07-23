from pathlib import Path

import pytest

from grem.scaffold import Moniker, ScaffoldError, file, folder, load_manifest, scaffold
from grem.templates.python.bootstrap import ROOT


EXPECTED_PATHS = (
    Path(".grem"),
    Path(".grem/config.yaml"),
    Path(".grem/harness"),
    Path(".grem/harness/README.md"),
    Path(".grem/harness/diff.md"),
    Path(".grem/harness/instructions.md"),
    Path(".grem/harness/sync.md"),
    Path(".grem/harness/upgrade.md"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path("README.md"),
    Path("doc"),
    Path("doc/issues"),
    Path("doc/memory"),
    Path("doc/models"),
    Path("doc/models/behavior"),
    Path("doc/models/data"),
    Path("doc/models/domain"),
    Path("doc/proposals"),
    Path("doc/proposals/README.md"),
    Path("doc/wiki"),
    Path("pyproject.toml"),
    Path("src"),
    Path("src/myproject"),
    Path("tests"),
)


def bundled_content() -> Path:
    return (
        Path(__file__).parents[1]
        / "src"
        / "grem"
        / "templates"
        / "python"
        / "content"
    )


def bundled_template() -> Path:
    return bundled_content().parent


def test_python_template_has_exact_tree_and_bytes(tmp_path: Path) -> None:
    target = tmp_path / "myproject"

    paths = scaffold(ROOT, bundled_content(), target)

    assert paths == EXPECTED_PATHS
    actual_paths = tuple(
        sorted(
            (path.relative_to(target) for path in target.rglob("*")),
            key=lambda path: path.as_posix(),
        )
    )
    assert actual_paths == EXPECTED_PATHS
    for source in bundled_content().rglob("*"):
        if source.is_file():
            relative = source.relative_to(bundled_content())
            assert (target / relative).read_bytes() == source.read_bytes()


def test_python_template_declares_semver_version() -> None:
    template = load_manifest(bundled_template())

    assert template.name == "python"
    assert str(template.version) == "0.6.0"


def test_scaffold_does_not_execute_declaration_methods(tmp_path: Path) -> None:
    class Root(Moniker):
        @file("README.md")
        def should_not_run(self):
            raise AssertionError("declaration method was executed")

    source = tmp_path / "content"
    source.mkdir()
    (source / "README.md").write_text("hello\n")

    scaffold(Root, source, tmp_path / "output")

    assert (tmp_path / "output" / "README.md").read_text() == "hello\n"


def test_scaffold_rejects_duplicate_output_paths(tmp_path: Path) -> None:
    class Root(Moniker):
        @file("same")
        def first(self):
            ...

        @file("same")
        def second(self):
            ...

    source = tmp_path / "content"
    source.mkdir()
    (source / "same").write_text("")

    with pytest.raises(ScaffoldError, match="duplicate output path"):
        scaffold(Root, source, tmp_path / "output")


def test_scaffold_rejects_nonempty_target(tmp_path: Path) -> None:
    class Root(Moniker):
        pass

    source = tmp_path / "content"
    source.mkdir()
    target = tmp_path / "output"
    target.mkdir()
    (target / "existing").write_text("")

    with pytest.raises(ScaffoldError, match="not empty"):
        scaffold(Root, source, target)


def test_folder_requires_moniker_return_annotation(tmp_path: Path) -> None:
    class Root(Moniker):
        @folder
        def invalid(self) -> str:
            ...

    source = tmp_path / "content"
    source.mkdir()

    with pytest.raises(ScaffoldError, match="must return a Moniker"):
        scaffold(Root, source, tmp_path / "output")
