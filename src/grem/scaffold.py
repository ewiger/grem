"""Declarative, deterministic template scaffolding."""

from __future__ import annotations

import importlib.util
import inspect
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Literal, TypeVar, get_type_hints

import semver
import yaml


class ScaffoldError(Exception):
    """Raised when a scaffold declaration or destination is invalid."""


class Moniker:
    """Base class for declarative folder manifests."""


DeclarationKind = Literal["file", "folder"]


@dataclass(frozen=True)
class _Declaration:
    kind: DeclarationKind
    name: str | None = None
    source: str | None = None


@dataclass(frozen=True)
class _PlannedEntry:
    path: PurePosixPath
    kind: DeclarationKind
    source: Path | None = None


@dataclass(frozen=True)
class Template:
    """A validated template loaded from its bootstrap module."""

    name: str
    version: semver.Version
    root: type[Moniker]
    content: Path
    directory: Path


F = TypeVar("F", bound=Callable[..., Any])


def _annotate(method: F, declaration: _Declaration) -> F:
    if hasattr(method, "__grem_declaration__"):
        raise TypeError(f"{method.__name__} already has a grem annotation")
    setattr(method, "__grem_declaration__", declaration)
    return method


def folder(argument: F | str | None = None) -> F | Callable[[F], F]:
    """Mark a method as a folder element.

    ``@folder`` uses the method name. ``@folder("name")`` supplies an emitted
    name explicitly. The method's return annotation names its child Moniker.
    """

    if callable(argument):
        return _annotate(argument, _Declaration("folder"))

    def decorator(method: F) -> F:
        return _annotate(method, _Declaration("folder", name=argument))

    return decorator


def file(
    argument: F | str | None = None,
    *,
    source: str | None = None,
) -> F | Callable[[F], F]:
    """Mark a method as a file element copied from the template content."""

    if callable(argument):
        return _annotate(argument, _Declaration("file", source=source))

    def decorator(method: F) -> F:
        return _annotate(
            method,
            _Declaration("file", name=argument, source=source),
        )

    return decorator


def _relative_path(
    value: str,
    *,
    label: str,
    one_component: bool = False,
) -> PurePosixPath:
    if not value or "\\" in value or "\x00" in value:
        raise ScaffoldError(f"invalid {label}: {value!r}")

    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ScaffoldError(f"invalid {label}: {value!r}")
    if one_component and len(path.parts) != 1:
        raise ScaffoldError(f"{label} must be one path component: {value!r}")
    return path


def _child_moniker(owner: type[Moniker], method: Callable[..., Any]) -> type[Moniker]:
    module = sys.modules.get(owner.__module__)
    globalns = vars(module) if module is not None else {}
    try:
        annotation = get_type_hints(
            method,
            globalns=globalns,
            localns=dict(vars(owner)),
        ).get("return")
    except (NameError, TypeError) as error:
        raise ScaffoldError(
            f"cannot resolve folder type for {owner.__name__}.{method.__name__}"
        ) from error

    if not inspect.isclass(annotation) or not issubclass(annotation, Moniker):
        raise ScaffoldError(
            f"{owner.__name__}.{method.__name__} must return a Moniker type"
        )
    return annotation


def _declarations(owner: type[Moniker]) -> list[tuple[str, Callable[..., Any], _Declaration]]:
    declarations: list[tuple[str, Callable[..., Any], _Declaration]] = []
    for method_name, member in vars(owner).items():
        declaration = getattr(member, "__grem_declaration__", None)
        if declaration is not None:
            declarations.append((method_name, member, declaration))
    return declarations


def _build_plan(
    root: type[Moniker],
    source_root: Path,
) -> tuple[_PlannedEntry, ...]:
    if not inspect.isclass(root) or not issubclass(root, Moniker):
        raise ScaffoldError("ROOT must be a Moniker type")

    entries: dict[PurePosixPath, _PlannedEntry] = {}

    def visit(owner: type[Moniker], parent: PurePosixPath) -> None:
        for method_name, method, declaration in _declarations(owner):
            emitted_name = declaration.name or method_name
            name = _relative_path(
                emitted_name,
                label=f"name on {owner.__name__}.{method_name}",
                one_component=True,
            )
            output_path = parent / name

            if output_path in entries:
                raise ScaffoldError(f"duplicate output path: {output_path}")

            if declaration.kind == "folder":
                entries[output_path] = _PlannedEntry(output_path, "folder")
                visit(_child_moniker(owner, method), output_path)
                continue

            source_name = declaration.source or output_path.as_posix()
            source_path = _relative_path(source_name, label="source path")
            candidate = (source_root / Path(*source_path.parts)).resolve()
            try:
                candidate.relative_to(source_root)
            except ValueError as error:
                raise ScaffoldError(f"source escapes template: {source_name}") from error
            if not candidate.is_file():
                raise ScaffoldError(f"missing template file: {source_name}")
            entries[output_path] = _PlannedEntry(output_path, "file", candidate)

    visit(root, PurePosixPath())

    for path, entry in entries.items():
        for parent in path.parents:
            if parent == PurePosixPath("."):
                break
            ancestor = entries.get(parent)
            if ancestor is not None and ancestor.kind == "file":
                raise ScaffoldError(f"file cannot contain an entry: {ancestor.path}")

    return tuple(entries[path] for path in sorted(entries, key=lambda item: item.as_posix()))


def scaffold(
    root: type[Moniker],
    source_root: Path,
    target: Path,
) -> tuple[Path, ...]:
    """Materialize a Moniker tree and return its relative output paths."""

    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise ScaffoldError(f"template content directory does not exist: {source_root}")

    plan = _build_plan(root, source_root)

    if target.exists():
        if not target.is_dir():
            raise ScaffoldError(f"target is not a directory: {target}")
        if next(target.iterdir(), None) is not None:
            raise ScaffoldError(f"target directory is not empty: {target}")

    target.mkdir(parents=True, exist_ok=True)
    for entry in plan:
        destination = target.joinpath(*entry.path.parts)
        if entry.kind == "folder":
            destination.mkdir(parents=True, exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            assert entry.source is not None
            shutil.copyfile(entry.source, destination)

    return tuple(Path(*entry.path.parts) for entry in plan)


def load_manifest(template: Path) -> Template:
    """Load and validate a trusted template bootstrap module."""

    template = template.resolve()
    manifest = template / "bootstrap.py"
    if not manifest.is_file():
        raise ScaffoldError(f"template has no bootstrap.py: {template}")

    module_name = f"_grem_template_{abs(hash(manifest))}"
    spec = importlib.util.spec_from_file_location(module_name, manifest)
    if spec is None or spec.loader is None:
        raise ScaffoldError(f"cannot load template manifest: {manifest}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as error:
        raise ScaffoldError(f"cannot load template manifest: {manifest}") from error

    root = getattr(module, "ROOT", None)
    if not inspect.isclass(root) or not issubclass(root, Moniker):
        raise ScaffoldError(f"template ROOT is not a Moniker type: {manifest}")

    name = getattr(module, "NAME", None)
    if not isinstance(name, str) or not name:
        raise ScaffoldError(f"template NAME must be a non-empty string: {manifest}")

    version_text = getattr(module, "VERSION", None)
    if not isinstance(version_text, str):
        raise ScaffoldError(f"template VERSION must be a SemVer 2 string: {manifest}")
    try:
        version = semver.Version.parse(version_text)
    except ValueError as error:
        raise ScaffoldError(
            f"template VERSION is not valid SemVer 2: {version_text!r}"
        ) from error

    content = template / "content"
    layout_path = content / ".grem" / "config.yaml"
    if not layout_path.is_file():
        raise ScaffoldError(f"template has no content/.grem/config.yaml: {template}")
    try:
        layout = yaml.safe_load(layout_path.read_text())
    except yaml.YAMLError as error:
        raise ScaffoldError(f"invalid template config: {layout_path}") from error
    if not isinstance(layout, dict):
        raise ScaffoldError(f"template config must be a mapping: {layout_path}")
    if layout.get("template") != name:
        raise ScaffoldError(f"template NAME does not match config: {layout_path}")
    if layout.get("template_version") != version_text:
        raise ScaffoldError(f"template VERSION does not match config: {layout_path}")

    return Template(
        name=name,
        version=version,
        root=root,
        content=content,
        directory=template,
    )


def scaffold_template(template: Path, target: Path) -> tuple[Path, ...]:
    """Load and scaffold a template directory."""

    loaded = load_manifest(template)
    return scaffold(loaded.root, loaded.content, target)


class _LayoutDumper(yaml.SafeDumper):
    """Dump config.yaml with block sequences indented under their key."""

    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        return super().increase_indent(flow, indentless=False)


def stamp_grem_version(project: Path, version: str) -> None:
    """Record in a project's config.yaml which grem CLI version produced it.

    The value is written right after ``template_version`` and replaces any
    prior stamp, so re-running upgrade keeps a single, up-to-date entry.
    """

    config_path = project / ".grem" / "config.yaml"
    try:
        layout = yaml.safe_load(config_path.read_text())
    except yaml.YAMLError as error:
        raise ScaffoldError(f"invalid .grem/config.yaml in {project}") from error
    if not isinstance(layout, dict):
        raise ScaffoldError(f".grem/config.yaml must be a mapping in {project}")

    stamped: dict = {}
    for key, value in layout.items():
        if key == "grem_version":
            continue
        stamped[key] = value
        if key == "template_version":
            stamped["grem_version"] = version
    stamped.setdefault("grem_version", version)

    config_path.write_text(
        yaml.dump(
            stamped,
            Dumper=_LayoutDumper,
            sort_keys=False,
            default_flow_style=False,
            indent=2,
        )
    )
