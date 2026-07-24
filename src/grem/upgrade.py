"""Safe filesystem operations for template upgrades."""

from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from grem.scaffold import ScaffoldError


#: Name of the project-owned protection list, always protected implicitly.
GREMIGNORE = ".gremignore"


@dataclass(frozen=True)
class OverlayResult:
    """Counts from overlaying a generated reference tree."""

    directories_created: int
    files_written: int
    files_skipped: int = 0


def load_gremignore(project: Path) -> list[str]:
    """Read the project's ``.gremignore`` patterns, dropping comments/blanks."""

    ignore_file = project / GREMIGNORE
    if not ignore_file.is_file():
        return []
    patterns: list[str] = []
    for line in ignore_file.read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            patterns.append(stripped)
    return patterns


def _pattern_to_regex(pattern: str) -> str:
    """Translate a gitignore-ish pattern into an anchored regex body."""

    subtree = pattern.endswith("/")
    body = pattern.rstrip("/")
    out: list[str] = []
    index = 0
    while index < len(body):
        char = body[index]
        if char == "*":
            if body[index : index + 2] == "**":
                out.append(".*")
                index += 2
                continue
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(char))
        index += 1
    regex = "".join(out)
    # A trailing-slash pattern protects the directory and everything under it;
    # a plain path matches itself (a leading-directory match is spelled `dir/**`).
    return regex + "(?:/.*)?$" if subtree else regex + "$"


def gremignore_matcher(patterns: list[str]) -> Callable[[str], bool]:
    """Build a predicate matching project-relative posix paths against patterns.

    ``.gremignore`` itself always matches: the protection list is project-owned
    so upgrades never overwrite a user's edits to it.
    """

    compiled = [re.compile("^" + _pattern_to_regex(pattern)) for pattern in patterns]

    def matches(relative: str) -> bool:
        if relative == GREMIGNORE:
            return True
        return any(rule.match(relative) for rule in compiled)

    return matches


def require_clean_git_worktree(project: Path) -> Path:
    """Return the Git root after verifying the entire worktree is clean."""

    project = project.resolve()
    if not project.is_dir():
        raise ScaffoldError(f"project is not a directory: {project}")

    try:
        root_result = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as error:
        raise ScaffoldError("git is required for template upgrades") from error
    if root_result.returncode != 0:
        raise ScaffoldError(f"project is not in a Git worktree: {project}")

    git_root = Path(root_result.stdout.strip()).resolve()
    status_result = subprocess.run(
        [
            "git",
            "-C",
            str(git_root),
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if status_result.returncode != 0:
        raise ScaffoldError(f"cannot read Git status: {git_root}")
    if status_result.stdout:
        raise ScaffoldError(
            "Git worktree must be clean before upgrade; commit or stash all "
            "tracked and untracked changes"
        )
    return git_root


def _has_symlink_parent(path: Path, root: Path) -> bool:
    current = path
    while current != root:
        if current.is_symlink():
            return True
        current = current.parent
    return root.is_symlink()


def overlay_reference(
    reference: Path,
    project: Path,
    ignore: Callable[[str], bool] | None = None,
) -> OverlayResult:
    """Overlay a generated reference tree after validating every destination.

    ``ignore`` receives each entry's project-relative posix path; when it
    returns ``True`` the entry is left untouched, so project-owned files
    (see :func:`gremignore_matcher`) survive the upgrade.
    """

    reference = reference.resolve()
    project = project.resolve()
    if not reference.is_dir():
        raise ScaffoldError(f"upgrade reference is not a directory: {reference}")
    if not project.is_dir():
        raise ScaffoldError(f"project is not a directory: {project}")

    skip = ignore or (lambda _relative: False)

    entries = sorted(
        reference.rglob("*"),
        key=lambda path: (len(path.relative_to(reference).parts), path.as_posix()),
    )

    for source in entries:
        relative = source.relative_to(reference)
        if skip(relative.as_posix()):
            continue
        destination = project / relative
        if source.is_symlink():
            raise ScaffoldError(f"upgrade reference contains a symlink: {relative}")
        if _has_symlink_parent(destination, project):
            raise ScaffoldError(f"upgrade destination uses a symlink: {relative}")
        if source.is_dir() and destination.exists() and not destination.is_dir():
            raise ScaffoldError(f"upgrade folder conflicts with a file: {relative}")
        if source.is_file() and destination.exists() and not destination.is_file():
            raise ScaffoldError(f"upgrade file conflicts with a folder: {relative}")

    directories_created = 0
    files_written = 0
    files_skipped = 0
    for source in entries:
        relative = source.relative_to(reference)
        if skip(relative.as_posix()):
            if source.is_file():
                files_skipped += 1
            continue
        destination = project / relative
        if source.is_dir():
            if not destination.exists():
                destination.mkdir(parents=True)
                directories_created += 1
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        files_written += 1

    return OverlayResult(
        directories_created=directories_created,
        files_written=files_written,
        files_skipped=files_skipped,
    )
