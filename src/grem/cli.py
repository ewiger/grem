"""Command-line interface for grem."""

from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated, Iterator

import semver
import typer
import yaml

from grem import __version__
from grem.scaffold import (
    ScaffoldError,
    load_manifest,
    scaffold as materialize,
    scaffold_template,
    stamp_grem_version,
)
from grem.upgrade import overlay_reference, require_clean_git_worktree


app = typer.Typer(
    help="Stamp a project from a deterministic template.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"grem {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show the grem CLI version and exit.",
            is_eager=True,
            callback=_version_callback,
        ),
    ] = False,
) -> None:
    """Stamp projects from declarative templates."""


@contextmanager
def _template_directory(reference: str) -> Iterator[Path]:
    candidate = Path(reference).expanduser()
    if candidate.is_dir():
        yield candidate
        return

    bundled = resources.files("grem.templates").joinpath(reference)
    if not bundled.is_dir():
        raise ScaffoldError(f"unknown template: {reference}")
    with resources.as_file(bundled) as bundled_path:
        yield bundled_path


def _layout(project: Path) -> dict:
    layout_path = project / ".grem" / "config.yaml"
    if not layout_path.is_file():
        raise ScaffoldError(f"no .grem/config.yaml in {project}")
    try:
        layout = yaml.safe_load(layout_path.read_text())
    except yaml.YAMLError as error:
        raise ScaffoldError(f"invalid .grem/config.yaml in {project}") from error
    if not isinstance(layout, dict):
        raise ScaffoldError(f".grem/config.yaml must be a mapping in {project}")
    return layout


def _project_scope(project: Path, scope: Path) -> Path:
    project_root = project.resolve()
    candidate = scope.expanduser()
    if not candidate.is_absolute():
        candidate = project_root / candidate
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(project_root)
    except ValueError as error:
        raise ScaffoldError(f"scope is outside the project: {scope}") from error
    if not resolved.exists():
        raise ScaffoldError(f"scope does not exist: {scope}")
    return relative


def _scope_prompt(
    project: Path,
    left: Path,
    right: Path,
    prompt_name: str,
) -> tuple[Path, Path, str]:
    _layout(project)
    left_scope = _project_scope(project, left)
    right_scope = _project_scope(project, right)
    prompt = project / ".grem" / "harness" / prompt_name
    if not prompt.is_file():
        raise ScaffoldError(f"no {prompt_name} prompt in {project}")
    return left_scope, right_scope, prompt.read_text()


def _safe_component(value: str, *, label: str) -> str:
    if (
        not value
        or "/" in value
        or "\\" in value
        or "\x00" in value
        or value in {".", ".."}
    ):
        raise ScaffoldError(f"invalid {label}: {value!r}")
    return value


def _style_prompt(project: Path, type_: str, style: str) -> tuple[str, str, str]:
    _layout(project)
    kind = _safe_component(type_, label="type")
    name = _safe_component(style, label="style")
    prompt = project / ".grem" / "styles" / kind / name / "prompt.md"
    if not prompt.is_file():
        raise ScaffoldError(f"no {kind}/{name} style in {project}")
    return kind, name, prompt.read_text()


CopyOption = Annotated[
    bool,
    typer.Option("--copy", "-c", help="Also copy the printed prompt to the clipboard."),
]


def _emit(text: str, *, copy: bool) -> None:
    """Print a generated prompt, optionally copying it to the clipboard too.

    The prompt always goes to stdout so it stays pipeable (``grem agent |
    pbcopy``). With ``--copy`` it is additionally placed on the system
    clipboard; the confirmation and any failure go to stderr so they never
    contaminate the piped prompt.
    """

    typer.echo(text, nl=False)
    if not copy:
        return

    import pyperclip

    try:
        pyperclip.copy(text)
    except pyperclip.PyperclipException as error:
        typer.echo(f"warning: could not copy to clipboard: {error}", err=True)
    else:
        typer.echo("Copied prompt to clipboard.", err=True)


@app.command()
def init(
    target: Annotated[
        Path,
        typer.Argument(help="Directory to initialize (defaults to the current one)."),
    ] = Path("."),
    template: Annotated[
        str,
        typer.Option("--template", "-t", help="Template name or directory."),
    ] = "python",
) -> None:
    """Scaffold a project from a template.

    Like ``git init``, this defaults to the bundled ``python`` template in the
    current directory. It refuses to run when the target already holds a
    ``.grem`` folder, i.e. it is already a grem project.
    """

    try:
        with _template_directory(template) as template_path:
            entries = scaffold_template(template_path, target)
        stamp_grem_version(target, __version__)
    except ScaffoldError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(code=1) from error

    typer.echo(f"Scaffolded {len(entries)} entries into {target}")


@app.command()
def diff(
    left: Annotated[Path, typer.Argument(help="First project scope.")],
    right: Annotated[Path, typer.Argument(help="Second project scope.")],
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Scaffolded project directory."),
    ] = Path("."),
    copy: CopyOption = False,
) -> None:
    """Print a prompt for finding semantic inconsistencies between two scopes."""

    try:
        left_scope, right_scope, prompt = _scope_prompt(
            project,
            left,
            right,
            "diff.md",
        )
    except ScaffoldError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(code=1) from error

    _emit(
        "\n".join(
            (
                "# Semantic project diff",
                "",
                f"Scope A: `{left_scope.as_posix()}`",
                f"Scope B: `{right_scope.as_posix()}`",
                "",
                prompt,
            )
        ),
        copy=copy,
    )


@app.command()
def sync(
    left: Annotated[Path, typer.Argument(help="First project scope.")],
    right: Annotated[Path, typer.Argument(help="Second project scope.")],
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Scaffolded project directory."),
    ] = Path("."),
    copy: CopyOption = False,
) -> None:
    """Print the full agent loop for reconciling two project scopes."""

    try:
        left_scope, right_scope, prompt = _scope_prompt(
            project,
            left,
            right,
            "sync.md",
        )
    except ScaffoldError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(code=1) from error

    _emit(
        "\n".join(
            (
                "# Synchronize project scopes",
                "",
                f"Scope A: `{left_scope.as_posix()}`",
                f"Scope B: `{right_scope.as_posix()}`",
                "",
                prompt,
            )
        ),
        copy=copy,
    )


def _agent_prompt(project: Path, *, copy: bool) -> None:
    prompt = project / ".grem" / "harness" / "instructions.md"
    try:
        layout = _layout(project)
        configuration = layout.get("agent_instructions")
        if not isinstance(configuration, dict):
            raise ScaffoldError(
                ".grem/config.yaml has no agent_instructions mapping"
            )
        central = configuration.get("central")
        targets = configuration.get("targets")
        if not isinstance(central, str) or not central:
            raise ScaffoldError("agent_instructions.central must be a path")
        if (
            not isinstance(targets, list)
            or not targets
            or not all(isinstance(target, str) and target for target in targets)
        ):
            raise ScaffoldError(
                "agent_instructions.targets must be a non-empty path list"
            )
        if not (project / central).is_file():
            raise ScaffoldError(f"central agent instructions do not exist: {central}")
        if not prompt.is_file():
            raise ScaffoldError(f"no agent instructions prompt in {project}")
    except ScaffoldError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(code=1) from error

    target_lines = "\n".join(f"- `{target}`" for target in targets)
    _emit(
        "\n".join(
            (
                "# Align agent instruction files",
                "",
                f"Central instructions: `{central}`",
                "Targets:",
                target_lines,
                "",
                prompt.read_text(),
            )
        ),
        copy=copy,
    )


@app.command()
def agent(
    project: Annotated[
        Path,
        typer.Argument(help="Scaffolded project directory."),
    ] = Path("."),
    copy: CopyOption = False,
) -> None:
    """Print the prompt for aligning configured agent instruction files."""

    _agent_prompt(project, copy=copy)


@app.command(name="instructions", hidden=True)
def instructions(
    project: Annotated[
        Path,
        typer.Argument(help="Scaffolded project directory."),
    ] = Path("."),
    copy: CopyOption = False,
) -> None:
    """Deprecated alias for `grem agent`."""

    _agent_prompt(project, copy=copy)


@app.command()
def new(
    path: Annotated[
        Path,
        typer.Argument(help="Source file the style is applied to."),
    ],
    type_: Annotated[
        str,
        typer.Option("--type", "-t", help="Style category, such as a doc folder."),
    ],
    style: Annotated[
        str,
        typer.Option("--style", "-s", help="Named style under the category."),
    ],
    project: Annotated[
        Path,
        typer.Option("--project", "-p", help="Scaffolded project directory."),
    ] = Path("."),
    copy: CopyOption = False,
) -> None:
    """Print a documentation-style prompt for applying STYLE to a source file."""

    try:
        kind, name, prompt = _style_prompt(project, type_, style)
        source = _project_scope(project, path)
    except ScaffoldError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(code=1) from error

    _emit(
        "\n".join(
            (
                "# Apply a documentation style",
                "",
                f"Style: `{kind}/{name}`",
                f"Source document: `{source.as_posix()}`",
                "",
                prompt,
            )
        ),
        copy=copy,
    )


@app.command()
def upgrade(
    project: Annotated[
        Path,
        typer.Argument(help="Scaffolded project directory."),
    ] = Path("."),
    template: Annotated[
        str | None,
        typer.Option("--template", help="Target template name or directory."),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option("--interactive", help="Confirm before overwriting template files."),
    ] = False,
    copy: CopyOption = False,
) -> None:
    """Overlay a newer template in a clean Git worktree and print a merge prompt."""

    try:
        layout = _layout(project)
        template_name = layout.get("template")
        current_text = layout.get("template_version")
        if not isinstance(template_name, str) or not template_name:
            raise ScaffoldError(".grem/config.yaml has no template name")
        if not isinstance(current_text, str):
            raise ScaffoldError(".grem/config.yaml has no template_version")
        try:
            current = semver.Version.parse(current_text)
        except ValueError as error:
            raise ScaffoldError(
                ".grem/config.yaml template_version is not valid SemVer 2: "
                f"{current_text!r}"
            ) from error

        target_reference = template or template_name
        with _template_directory(target_reference) as template_path:
            available = load_manifest(template_path)
            if available.name != template_name:
                raise ScaffoldError(
                    f"project template {template_name!r} does not match "
                    f"target template {available.name!r}"
                )
            prompt_path = available.content / ".grem" / "harness" / "upgrade.md"
            if not prompt_path.is_file():
                raise ScaffoldError(
                    f"target template has no upgrade prompt: {prompt_path}"
                )
            prompt_body = prompt_path.read_text()

            if available.version < current:
                raise ScaffoldError(
                    f"target {available.version} is older than project {current}"
                )
            if available.version == current:
                typer.echo(f"{template_name} is already at {current}")
                return

            if interactive and not typer.confirm(
                "Overwrite generated files with the target template?",
                default=True,
            ):
                typer.echo("Upgrade cancelled")
                return

            git_root = require_clean_git_worktree(project)
            with TemporaryDirectory(prefix="grem-upgrade-") as temporary:
                reference = Path(temporary) / "reference"
                materialize(available.root, available.content, reference)
                result = overlay_reference(reference, project)
            stamp_grem_version(project, __version__)
    except ScaffoldError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(code=1) from error

    _emit(
        "\n".join(
            (
                "# Grem template upgrade",
                "",
                f"Project template: `{template_name}`",
                f"Current version: `{current}`",
                f"Target version: `{available.version}`",
                f"Target template: `{target_reference}`",
                f"Git worktree: `{git_root}`",
                f"Files overwritten: {result.files_written}",
                f"Directories created: {result.directories_created}",
                "",
                prompt_body,
            )
        ),
        copy=copy,
    )
