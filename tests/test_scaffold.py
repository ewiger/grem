from pathlib import Path

import pytest
import yaml

from grem.scaffold import (
    Moniker,
    ScaffoldError,
    file,
    folder,
    load_manifest,
    record_variables,
    render,
    scaffold,
    stamp_grem_version,
)
from grem.templates.python.bootstrap import ROOT
from grem.templates.rust.bootstrap import ROOT as RUST_ROOT


# The default variables `grem init` derives for a project folder named
# ``myproject`` — keeps ``src/myproject`` stable across the substitution rework.
VARIABLES = {
    "project_name": "myproject",
    "package_name": "myproject",
    "proposal_prefix": "MYPROJECT",
}


def _project_with_config(tmp_path: Path, text: str) -> Path:
    project = tmp_path / "project"
    (project / ".grem").mkdir(parents=True)
    (project / ".grem" / "config.yaml").write_text(text)
    return project


MINIMAL_CONFIG = (
    "kind: layout\n"
    "schema: 1\n"
    "template: python\n"
    "template_version: 0.6.0\n"
    "agent_instructions:\n"
    "  central: .grem/harness/README.md\n"
    "  targets:\n"
    "    - AGENTS.md\n"
)


EXPECTED_PATHS = (
    Path(".claude"),
    Path(".claude/skills"),
    Path(".claude/skills/grem"),
    Path(".claude/skills/grem/SKILL.md"),
    Path(".grem"),
    Path(".grem/config.yaml"),
    Path(".grem/harness"),
    Path(".grem/harness/README.md"),
    Path(".grem/harness/diff.md"),
    Path(".grem/harness/instructions.md"),
    Path(".grem/harness/sync.md"),
    Path(".grem/harness/upgrade.md"),
    Path(".grem/issues"),
    Path(".grem/issues/archive"),
    Path(".grem/styles"),
    Path(".grem/styles/doc"),
    Path(".grem/styles/doc/adr"),
    Path(".grem/styles/doc/adr/prompt.md"),
    Path(".grem/styles/doc/hmd"),
    Path(".grem/styles/doc/hmd/prompt.md"),
    Path(".grem/styles/doc/lenses"),
    Path(".grem/styles/doc/lenses/prompt.md"),
    Path(".grem/styles/doc/slides"),
    Path(".grem/styles/doc/slides/prompt.md"),
    Path(".gremignore"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path("README.md"),
    Path("doc"),
    Path("doc/issues"),
    Path("doc/issues/kanban.yaml"),
    Path("doc/memory"),
    Path("doc/models"),
    Path("doc/models/behavior"),
    Path("doc/models/data"),
    Path("doc/models/domain"),
    Path("doc/models/requirements"),
    Path("doc/proposals"),
    Path("doc/proposals/README.md"),
    Path("doc/proposals/TEMPLATE.md"),
    Path("doc/stack.md"),
    Path("doc/wiki"),
    Path("doc/wiki/README.md"),
    Path("doc/wiki/hyper-markdown.hmd"),
    Path("doc/wiki/kanban.hmd"),
    Path("pyproject.toml"),
    Path("src"),
    Path("src/myproject"),
    Path("tests"),
)


# The Rust tree differs from the Python one only where the language does: a
# Cargo manifest and toolchain pin instead of pyproject.toml, real source and
# test files instead of an empty package folder, and a .gitignore for target/.
RUST_EXPECTED_PATHS = (
    Path(".claude"),
    Path(".claude/skills"),
    Path(".claude/skills/grem"),
    Path(".claude/skills/grem/SKILL.md"),
    Path(".gitignore"),
    Path(".grem"),
    Path(".grem/config.yaml"),
    Path(".grem/harness"),
    Path(".grem/harness/README.md"),
    Path(".grem/harness/diff.md"),
    Path(".grem/harness/instructions.md"),
    Path(".grem/harness/sync.md"),
    Path(".grem/harness/upgrade.md"),
    Path(".grem/issues"),
    Path(".grem/issues/archive"),
    Path(".grem/styles"),
    Path(".grem/styles/doc"),
    Path(".grem/styles/doc/adr"),
    Path(".grem/styles/doc/adr/prompt.md"),
    Path(".grem/styles/doc/hmd"),
    Path(".grem/styles/doc/hmd/prompt.md"),
    Path(".grem/styles/doc/lenses"),
    Path(".grem/styles/doc/lenses/prompt.md"),
    Path(".grem/styles/doc/slides"),
    Path(".grem/styles/doc/slides/prompt.md"),
    Path(".gremignore"),
    Path("AGENTS.md"),
    Path("CLAUDE.md"),
    Path("Cargo.toml"),
    Path("README.md"),
    Path("doc"),
    Path("doc/issues"),
    Path("doc/issues/kanban.yaml"),
    Path("doc/memory"),
    Path("doc/models"),
    Path("doc/models/behavior"),
    Path("doc/models/data"),
    Path("doc/models/domain"),
    Path("doc/models/requirements"),
    Path("doc/proposals"),
    Path("doc/proposals/README.md"),
    Path("doc/proposals/TEMPLATE.md"),
    Path("doc/stack.md"),
    Path("doc/wiki"),
    Path("doc/wiki/README.md"),
    Path("doc/wiki/hyper-markdown.hmd"),
    Path("doc/wiki/kanban.hmd"),
    Path("rust-toolchain.toml"),
    Path("src"),
    Path("src/lib.rs"),
    Path("src/main.rs"),
    Path("tests"),
    Path("tests/cli.rs"),
)


def bundled_template(name: str = "python") -> Path:
    return Path(__file__).parents[1] / "src" / "grem" / "templates" / name


def bundled_content(name: str = "python") -> Path:
    return bundled_template(name) / "content"


def bundled_names() -> list[str]:
    """Every bundled template directory, discovered the way the CLI does."""

    root = Path(__file__).parents[1] / "src" / "grem" / "templates"
    return sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "bootstrap.py").is_file()
    )


def test_python_template_has_exact_tree_and_rendered_content(tmp_path: Path) -> None:
    target = tmp_path / "myproject"

    paths = scaffold(ROOT, bundled_content(), target, VARIABLES)

    assert paths == EXPECTED_PATHS
    actual_paths = tuple(
        sorted(
            (path.relative_to(target) for path in target.rglob("*")),
            key=lambda path: path.as_posix(),
        )
    )
    assert actual_paths == EXPECTED_PATHS
    # Every copied file equals its source rendered through the same variables;
    # files without tokens are therefore still reproduced byte-for-byte.
    for source in bundled_content().rglob("*"):
        if source.is_file():
            relative = source.relative_to(bundled_content())
            expected = render(source.read_text(), VARIABLES)
            assert (target / relative).read_text() == expected
    assert (target / "README.md").read_text().startswith("# myproject\n")
    assert "doc/stack.md" in (target / "README.md").read_text()
    assert 'name = "myproject"' in (target / "pyproject.toml").read_text()
    assert "MYPROJECT-0001" in (target / "doc" / "proposals" / "README.md").read_text()


def test_scaffold_substitutes_path_components(tmp_path: Path) -> None:
    target = tmp_path / "widget"
    variables = {
        "project_name": "Widget Co",
        "package_name": "widget_co",
        "proposal_prefix": "WIDGETCO",
    }

    scaffold(ROOT, bundled_content(), target, variables)

    assert (target / "src" / "widget_co").is_dir()
    assert not (target / "src" / "{{ package_name }}").exists()
    assert (target / "README.md").read_text().startswith("# Widget Co\n")
    assert "src/widget_co/" in (target / "doc" / "stack.md").read_text()


def test_rust_template_has_exact_tree_and_rendered_content(tmp_path: Path) -> None:
    target = tmp_path / "myproject"

    paths = scaffold(RUST_ROOT, bundled_content("rust"), target, VARIABLES)

    assert paths == RUST_EXPECTED_PATHS
    actual_paths = tuple(
        sorted(
            (path.relative_to(target) for path in target.rglob("*")),
            key=lambda path: path.as_posix(),
        )
    )
    assert actual_paths == RUST_EXPECTED_PATHS
    for source in bundled_content("rust").rglob("*"):
        if source.is_file():
            relative = source.relative_to(bundled_content("rust"))
            expected = render(source.read_text(), VARIABLES)
            assert (target / relative).read_text() == expected
    assert (target / "README.md").read_text().startswith("# myproject\n")
    assert 'name = "myproject"' in (target / "Cargo.toml").read_text()
    assert "MYPROJECT-0001" in (target / "doc" / "proposals" / "README.md").read_text()
    # The crate name reaches Rust source, not just the manifest.
    assert "use myproject::greeting;" in (target / "src" / "main.rs").read_text()
    # Rust has no per-package source folder; src/ holds the crate roots.
    assert not (target / "src" / "myproject").exists()


def test_python_template_declares_semver_version() -> None:
    template = load_manifest(bundled_template())

    assert template.name == "python"
    assert str(template.version) == "0.15.0"


def test_rust_template_declares_semver_version() -> None:
    template = load_manifest(bundled_template("rust"))

    assert template.name == "rust"
    assert str(template.version) == "0.1.0"


@pytest.mark.parametrize("name", bundled_names())
def test_bundled_template_config_lists_the_tree_it_generates(
    name: str,
    tmp_path: Path,
) -> None:
    """Guard the drift `doc/stack.md` warns about.

    Adding a template file means updating the ``generated:`` list in
    ``content/.grem/config.yaml``. Compare the two mechanically so a forgotten
    entry fails here instead of surfacing in a stamped project.
    """

    template = load_manifest(bundled_template(name))
    target = tmp_path / "myproject"

    paths = scaffold(template.root, template.content, target, VARIABLES)

    layout = yaml.safe_load((target / ".grem" / "config.yaml").read_text())
    declared = sorted(
        layout["generated"]["directories"] + layout["generated"]["files"]
    )
    assert declared == sorted(path.as_posix() for path in paths)


def test_render_replaces_known_tokens_and_preserves_unknown() -> None:
    variables = {"package_name": "grem"}

    assert render("src/{{ package_name }}", variables) == "src/grem"
    assert render("{{{ package_name }}}", variables) == "grem"
    assert render("{{package_name}}", variables) == "grem"
    # Unknown tokens and stray braces survive untouched (no HTML escaping).
    assert render("{{ other }} & <x>", variables) == "{{ other }} & <x>"


def test_record_variables_inserts_after_grem_version(tmp_path: Path) -> None:
    project = _project_with_config(tmp_path, MINIMAL_CONFIG)
    stamp_grem_version(project, "1.2.3")

    record_variables(project, {"project_name": "demo", "package_name": "demo"})

    layout = yaml.safe_load((project / ".grem" / "config.yaml").read_text())
    keys = list(layout)
    assert keys[keys.index("grem_version") + 1] == "variables"
    assert layout["variables"] == {"project_name": "demo", "package_name": "demo"}


def test_record_variables_replaces_prior_block(tmp_path: Path) -> None:
    project = _project_with_config(tmp_path, MINIMAL_CONFIG)

    record_variables(project, {"project_name": "one"})
    record_variables(project, {"project_name": "two"})

    text = (project / ".grem" / "config.yaml").read_text()
    assert text.count("variables:") == 1
    layout = yaml.safe_load(text)
    assert layout["variables"] == {"project_name": "two"}


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


def test_scaffold_allows_unrelated_files_in_target(tmp_path: Path) -> None:
    class Root(Moniker):
        @file("README.md")
        def readme(self):
            ...

    source = tmp_path / "content"
    source.mkdir()
    (source / "README.md").write_text("hello\n")
    target = tmp_path / "output"
    target.mkdir()
    (target / "unrelated.txt").write_text("keep me\n")

    scaffold(Root, source, target)

    assert (target / "README.md").read_text() == "hello\n"
    assert (target / "unrelated.txt").read_text() == "keep me\n"


def test_scaffold_rejects_existing_grem_project(tmp_path: Path) -> None:
    class Root(Moniker):
        pass

    source = tmp_path / "content"
    source.mkdir()
    target = tmp_path / "output"
    (target / ".grem").mkdir(parents=True)

    with pytest.raises(ScaffoldError, match="already a grem project"):
        scaffold(Root, source, target)


def test_scaffold_refuses_to_overwrite_existing_files(tmp_path: Path) -> None:
    class Root(Moniker):
        @file("README.md")
        def readme(self):
            ...

    source = tmp_path / "content"
    source.mkdir()
    (source / "README.md").write_text("new\n")
    target = tmp_path / "output"
    target.mkdir()
    (target / "README.md").write_text("existing\n")

    with pytest.raises(ScaffoldError, match="would be overwritten"):
        scaffold(Root, source, target)

    assert (target / "README.md").read_text() == "existing\n"


def test_stamp_grem_version_inserts_after_template_version(tmp_path: Path) -> None:
    project = _project_with_config(tmp_path, MINIMAL_CONFIG)

    stamp_grem_version(project, "1.2.3")

    layout = yaml.safe_load((project / ".grem" / "config.yaml").read_text())
    keys = list(layout)
    assert layout["grem_version"] == "1.2.3"
    assert keys[keys.index("template_version") + 1] == "grem_version"
    assert layout["agent_instructions"]["central"] == ".grem/harness/README.md"


def test_stamp_grem_version_replaces_prior_stamp(tmp_path: Path) -> None:
    project = _project_with_config(tmp_path, MINIMAL_CONFIG)

    stamp_grem_version(project, "1.0.0")
    stamp_grem_version(project, "2.0.0")

    text = (project / ".grem" / "config.yaml").read_text()
    assert text.count("grem_version:") == 1
    layout = yaml.safe_load(text)
    assert layout["grem_version"] == "2.0.0"
    keys = list(layout)
    assert keys[keys.index("template_version") + 1] == "grem_version"


def test_stamp_grem_version_appends_when_no_template_version(tmp_path: Path) -> None:
    project = _project_with_config(tmp_path, "kind: layout\nschema: 1\n")

    stamp_grem_version(project, "3.1.4")

    layout = yaml.safe_load((project / ".grem" / "config.yaml").read_text())
    assert layout["grem_version"] == "3.1.4"


def test_stamp_grem_version_rejects_non_mapping(tmp_path: Path) -> None:
    project = _project_with_config(tmp_path, "- just\n- a\n- list\n")

    with pytest.raises(ScaffoldError, match="must be a mapping"):
        stamp_grem_version(project, "1.0.0")


def test_folder_requires_moniker_return_annotation(tmp_path: Path) -> None:
    class Root(Moniker):
        @folder
        def invalid(self) -> str:
            ...

    source = tmp_path / "content"
    source.mkdir()

    with pytest.raises(ScaffoldError, match="must return a Moniker"):
        scaffold(Root, source, tmp_path / "output")
