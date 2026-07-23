import shutil
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from grem.cli import app


runner = CliRunner()


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
    target_template = tmp_path / "python-0.7.0"
    shutil.copytree(bundled, target_template)
    bootstrap = target_template / "bootstrap.py"
    bootstrap.write_text(
        bootstrap.read_text().replace('VERSION = "0.6.0"', 'VERSION = "0.7.0"')
    )
    layout = target_template / "content" / ".grem" / "config.yaml"
    layout.write_text(
        layout.read_text().replace(
            "template_version: 0.6.0",
            "template_version: 0.7.0",
        )
    )
    readme = target_template / "content" / "README.md"
    readme.write_text("# myproject\n\nUpgraded template.\n")
    return target_template


def test_scaffold_command_uses_bundled_template(tmp_path: Path) -> None:
    target = tmp_path / "myproject"

    result = runner.invoke(app, ["scaffold", "python", str(target)])

    assert result.exit_code == 0
    assert "Scaffolded 25 entries" in result.stdout
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
    scaffold_result = runner.invoke(app, ["scaffold", "python", str(target)])
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
    scaffold_result = runner.invoke(app, ["scaffold", "python", str(target)])
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
    scaffold_result = runner.invoke(app, ["scaffold", "python", str(target)])
    assert scaffold_result.exit_code == 0

    result = runner.invoke(app, ["instructions", str(target)])

    assert result.exit_code == 0
    assert "Central instructions: `.grem/harness/README.md`" in result.stdout
    assert "- `AGENTS.md`" in result.stdout
    assert "- `CLAUDE.md`" in result.stdout
    assert "every file under `doc/memory/`" in result.stdout
    assert "ignore `.grem/**`" in result.stdout


def test_upgrade_overlays_template_and_prints_merge_prompt(tmp_path: Path) -> None:
    project = tmp_path / "myproject"
    scaffold_result = runner.invoke(app, ["scaffold", "python", str(project)])
    assert scaffold_result.exit_code == 0
    commit_project(project)

    target_template = newer_template(tmp_path)

    result = runner.invoke(
        app,
        ["upgrade", str(project), "--template", str(target_template)],
    )

    assert result.exit_code == 0
    assert "Current version: `0.6.0`" in result.stdout
    assert "Target version: `0.7.0`" in result.stdout
    assert "Files overwritten:" in result.stdout
    assert "resulting unstaged Git diff" in result.stdout
    assert project.joinpath("README.md").read_text() == (
        "# myproject\n\nUpgraded template.\n"
    )
    assert "template_version: 0.7.0" in (
        project / ".grem" / "config.yaml"
    ).read_text()
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
    runner.invoke(app, ["scaffold", "python", str(project)])
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
    assert "template_version: 0.6.0" in (
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
    runner.invoke(app, ["scaffold", "python", str(project)])
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
    assert "template_version: 0.6.0" in (
        project / ".grem" / "config.yaml"
    ).read_text()
