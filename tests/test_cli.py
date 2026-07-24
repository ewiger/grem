import shutil
import subprocess
from pathlib import Path

import semver
from typer.testing import CliRunner

from grem import __version__
from grem.cli import app
from grem.templates.python.bootstrap import VERSION as TEMPLATE_VERSION


runner = CliRunner()

CURRENT_VERSION = TEMPLATE_VERSION
NEXT_VERSION = str(semver.Version.parse(TEMPLATE_VERSION).bump_minor())


def commit_project(project: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=project, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@grem.invalid"],
        cwd=project,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "grem tests"],
        cwd=project,
        check=True,
    )
    subprocess.run(["git", "add", "."], cwd=project, check=True)
    subprocess.run(
        ["git", "commit", "-qm", "initial scaffold"],
        cwd=project,
        check=True,
    )


def newer_template(tmp_path: Path) -> Path:
    bundled = (
        Path(__file__).parents[1] / "src" / "grem" / "templates" / "python"
    )
    target_template = tmp_path / f"python-{NEXT_VERSION}"
    shutil.copytree(bundled, target_template)
    bootstrap = target_template / "bootstrap.py"
    bootstrap.write_text(
        bootstrap.read_text().replace(
            f'VERSION = "{CURRENT_VERSION}"',
            f'VERSION = "{NEXT_VERSION}"',
        )
    )
    layout = target_template / "content" / ".grem" / "config.yaml"
    layout.write_text(
        layout.read_text().replace(
            f"template_version: {CURRENT_VERSION}",
            f"template_version: {NEXT_VERSION}",
        )
    )
    readme = target_template / "content" / "README.md"
    readme.write_text("# myproject\n\nUpgraded template.\n")
    return target_template


def test_version_flag_reports_cli_version() -> None:
    for flag in ("--version", "-v"):
        result = runner.invoke(app, [flag])
        assert result.exit_code == 0
        assert result.stdout.strip() == f"grem {__version__}"


def test_cli_version_matches_pyproject() -> None:
    import tomllib

    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text())
    assert __version__ == data["project"]["version"]


def test_scaffold_stamps_grem_cli_version(tmp_path: Path) -> None:
    target = tmp_path / "myproject"

    result = runner.invoke(app, ["init", str(target)])

    assert result.exit_code == 0
    config = (target / ".grem" / "config.yaml").read_text()
    assert f"grem_version: {__version__}" in config
    assert (
        f"template_version: {CURRENT_VERSION}\ngrem_version: {__version__}\n"
        in config
    )


def test_scaffold_command_uses_bundled_template(tmp_path: Path) -> None:
    target = tmp_path / "myproject"

    result = runner.invoke(app, ["init", str(target)])

    assert result.exit_code == 0
    assert "Scaffolded 37 entries" in result.stdout
    assert (target / "src" / "myproject").is_dir()
    assert (target / "doc" / "models" / "behavior").is_dir()
    assert (target / "doc" / "proposals" / "README.md").is_file()
    assert (target / "AGENTS.md").is_file()
    assert "Ignore `.grem/**` during ordinary work" in (
        target / "AGENTS.md"
    ).read_text()
    assert "Read and follow `CLAUDE.md`" in (target / "AGENTS.md").read_text()
    assert (target / ".grem" / "config.yaml").is_file()
    assert (target / "pyproject.toml").is_file()


def test_sync_command_prints_project_prompt(tmp_path: Path) -> None:
    target = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(target)])
    assert scaffold_result.exit_code == 0

    result = runner.invoke(
        app,
        ["sync", "doc", "src", "--project", str(target)],
    )

    assert result.exit_code == 0
    assert "Scope A: `doc`" in result.stdout
    assert "Scope B: `src`" in result.stdout
    assert "plan → implement → test → document → diff" in result.stdout


def test_diff_command_prints_numbered_inconsistency_prompt(tmp_path: Path) -> None:
    target = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(target)])
    assert scaffold_result.exit_code == 0

    result = runner.invoke(
        app,
        ["diff", "doc/models", "tests", "--project", str(target)],
    )

    assert result.exit_code == 0
    assert "Scope A: `doc/models`" in result.stdout
    assert "Scope B: `tests`" in result.stdout
    assert "Return a numbered list" in result.stdout
    assert "Do not plan or change files" in result.stdout


def test_instructions_command_uses_configured_paths(tmp_path: Path) -> None:
    target = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(target)])
    assert scaffold_result.exit_code == 0

    result = runner.invoke(app, ["instructions", str(target)])

    assert result.exit_code == 0
    assert "Central instructions: `.grem/harness/README.md`" in result.stdout
    assert "- `AGENTS.md`" in result.stdout
    assert "- `CLAUDE.md`" in result.stdout
    assert "every file under `doc/memory/`" in result.stdout
    assert "ignore `.grem/**`" in result.stdout


def test_new_command_prints_style_prompt(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(project)])
    assert scaffold_result.exit_code == 0

    style = project / ".grem" / "styles" / "doc" / "slides"
    style.mkdir(parents=True, exist_ok=True)
    (style / "prompt.md").write_text("MARKER-STYLE-BODY\n")
    source = project / "doc" / "wiki" / "example.md"
    source.write_text("# Example\n")

    result = runner.invoke(
        app,
        [
            "new",
            "doc/wiki/example.md",
            "--type",
            "doc",
            "--style",
            "slides",
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 0
    assert "Style: `doc/slides`" in result.stdout
    assert "Source document: `doc/wiki/example.md`" in result.stdout
    assert "MARKER-STYLE-BODY" in result.stdout


def test_new_command_reports_missing_style(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(project)])
    assert scaffold_result.exit_code == 0
    (project / "doc" / "wiki" / "example.md").write_text("# Example\n")

    result = runner.invoke(
        app,
        [
            "new",
            "doc/wiki/example.md",
            "--type",
            "doc",
            "--style",
            "nonexistent",
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 1
    assert "no doc/nonexistent style" in result.stderr


def test_new_command_rejects_source_outside_project(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(project)])
    assert scaffold_result.exit_code == 0

    result = runner.invoke(
        app,
        [
            "new",
            "../outside.md",
            "--type",
            "doc",
            "--style",
            "slides",
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 1
    assert "outside the project" in result.stderr


def test_scaffolded_project_ships_slides_style(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(project)])
    assert scaffold_result.exit_code == 0
    assert (
        project / ".grem" / "styles" / "doc" / "slides" / "prompt.md"
    ).is_file()
    (project / "doc" / "wiki" / "example.md").write_text("# Example\n")

    result = runner.invoke(
        app,
        [
            "new",
            "doc/wiki/example.md",
            "--type",
            "doc",
            "--style",
            "slides",
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 0
    assert "Style: `doc/slides`" in result.stdout
    assert "numbered D2" in result.stdout


def test_scaffolded_project_ships_adr_style(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(project)])
    assert scaffold_result.exit_code == 0
    assert (
        project / ".grem" / "styles" / "doc" / "adr" / "prompt.md"
    ).is_file()
    assert (project / "doc" / "proposals" / "TEMPLATE.md").is_file()
    (project / "doc" / "wiki" / "example.md").write_text("# Example\n")

    result = runner.invoke(
        app,
        [
            "new",
            "doc/wiki/example.md",
            "--type",
            "doc",
            "--style",
            "adr",
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 0
    assert "Style: `doc/adr`" in result.stdout
    assert "ADR-style technical decision record" in result.stdout


def test_scaffolded_project_ships_lenses_style(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(project)])
    assert scaffold_result.exit_code == 0
    assert (
        project / ".grem" / "styles" / "doc" / "lenses" / "prompt.md"
    ).is_file()
    (project / "doc" / "wiki" / "example.md").write_text("# Example\n")

    result = runner.invoke(
        app,
        [
            "new",
            "doc/wiki/example.md",
            "--type",
            "doc",
            "--style",
            "lenses",
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 0
    assert "Style: `doc/lenses`" in result.stdout
    assert "L0/L1 model lens" in result.stdout


def test_scaffolded_project_ships_hmd_style(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(project)])
    assert scaffold_result.exit_code == 0
    assert (
        project / ".grem" / "styles" / "doc" / "hmd" / "prompt.md"
    ).is_file()
    (project / "doc" / "wiki" / "example.md").write_text("# Example\n")

    result = runner.invoke(
        app,
        [
            "new",
            "doc/wiki/example.md",
            "--type",
            "doc",
            "--style",
            "hmd",
            "--project",
            str(project),
        ],
    )

    assert result.exit_code == 0
    assert "Style: `doc/hmd`" in result.stdout
    assert "hyper-markdown" in result.stdout


def test_new_command_prints_shipped_slides_style() -> None:
    repo_root = Path(__file__).parents[1]

    result = runner.invoke(
        app,
        [
            "new",
            "doc/wiki/grem-cli.hmd",
            "--type",
            "doc",
            "--style",
            "slides",
            "--project",
            str(repo_root),
        ],
    )

    assert result.exit_code == 0
    assert "Style: `doc/slides`" in result.stdout
    assert "Source document: `doc/wiki/grem-cli.hmd`" in result.stdout
    assert "numbered D2" in result.stdout
    assert "One idea per diagram" in result.stdout


def test_upgrade_overlays_template_and_prints_merge_prompt(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["init", str(project)])
    assert scaffold_result.exit_code == 0
    commit_project(project)

    target_template = newer_template(tmp_path)

    result = runner.invoke(
        app,
        ["upgrade", str(project), "--template", str(target_template)],
    )

    assert result.exit_code == 0
    assert f"Current version: `{CURRENT_VERSION}`" in result.stdout
    assert f"Target version: `{NEXT_VERSION}`" in result.stdout
    assert "Files overwritten:" in result.stdout
    assert "resulting unstaged Git diff" in result.stdout
    assert project.joinpath("README.md").read_text() == (
        "# myproject\n\nUpgraded template.\n"
    )
    upgraded_config = (project / ".grem" / "config.yaml").read_text()
    assert f"template_version: {NEXT_VERSION}" in upgraded_config
    assert f"grem_version: {__version__}" in upgraded_config
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert "README.md" in status
    assert ".grem/config.yaml" in status


def test_interactive_upgrade_can_cancel_before_overlay(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    runner.invoke(app, ["init", str(project)])
    commit_project(project)

    target_template = newer_template(tmp_path)

    result = runner.invoke(
        app,
        [
            "upgrade",
            str(project),
            "--template",
            str(target_template),
            "--interactive",
        ],
        input="n\n",
    )

    assert result.exit_code == 0
    assert "Upgrade cancelled" in result.stdout
    assert f"template_version: {CURRENT_VERSION}" in (
        project / ".grem" / "config.yaml"
    ).read_text()
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert status == ""


def test_upgrade_rejects_dirty_git_worktree(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    runner.invoke(app, ["init", str(project)])
    commit_project(project)
    (project / "README.md").write_text("uncommitted work\n")
    target_template = newer_template(tmp_path)

    result = runner.invoke(
        app,
        ["upgrade", str(project), "--template", str(target_template)],
    )

    assert result.exit_code == 1
    assert "Git worktree must be clean" in result.stderr
    assert (project / "README.md").read_text() == "uncommitted work\n"
    assert f"template_version: {CURRENT_VERSION}" in (
        project / ".grem" / "config.yaml"
    ).read_text()
