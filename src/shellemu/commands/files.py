"""Commands that change the VFS in memory: ``rm`` and ``cp``."""
from dataclasses import dataclass

from ..errors import PathError, UsageError
from ..response import Response
from ..vfs import (
    CURRENT, ERR_IS_DIR, ERR_NO_ENTRY, PARENT, SEPARATOR,
    Directory, Node, is_inside,
)
from .options import split_options

RM_OPTIONS = "rRf"
CP_OPTIONS = "rR"
RECURSIVE_FLAGS = ("r", "R")
ERR_BUSY = "Device or resource busy"
SPECIAL_NAMES = (CURRENT, PARENT)
SINGLE = 1


@dataclass
class Destination:
    """Where ``cp`` puts its copies.

    With ``name`` unset the copy goes into ``directory`` under the
    name of the source; otherwise ``name`` is the name of the copy.
    """

    directory: Directory
    name: str | None


def last_component(path: str) -> str:
    """Return the last name of a path, ignoring trailing slashes."""
    return path.rstrip(SEPARATOR).rpartition(SEPARATOR)[2]


def join_path(directory: str, name: str) -> str:
    """Append ``name`` to a path typed by the user."""
    return directory.rstrip(SEPARATOR) + SEPARATOR + name


def removal_problem(shell, path: str, node: Node, recursive: bool):
    """Return why ``node`` must not be removed, or None if it can be."""
    if last_component(path) in SPECIAL_NAMES:
        return ("rm: refusing to remove '.' or '..' directory: "
                f"skipping '{path}'")
    if not recursive and isinstance(node, Directory):
        return f"rm: cannot remove '{path}': {ERR_IS_DIR}"
    if node.parent is None:
        return f"rm: it is dangerous to operate recursively on '{path}'"
    if is_inside(shell.cwd, node):
        return f"rm: cannot remove '{path}': {ERR_BUSY}"
    return None


def remove_one(
    shell, path: str, flags: set[str], response: Response
) -> None:
    """Remove the file or directory ``path`` or report the problem."""
    try:
        node = shell.resolve(path)
    except PathError as error:
        if "f" not in flags or str(error) != ERR_NO_ENTRY:
            response.err(f"rm: cannot remove '{path}': {error}")
        return
    recursive = any(flag in flags for flag in RECURSIVE_FLAGS)
    problem = removal_problem(shell, path, node, recursive)
    if problem is not None:
        response.err(problem)
        return
    node.parent.remove(node.name)


def cmd_rm(shell, args: list[str]) -> Response:
    """Remove files; ``-r`` removes directories, ``-f`` ignores missing."""
    response = Response()
    try:
        flags, operands = split_options("rm", args, RM_OPTIONS)
    except UsageError as error:
        response.err(str(error))
        return response
    if not operands and "f" not in flags:
        response.err("rm: missing operand")
    for path in operands:
        remove_one(shell, path, flags, response)
    return response


def find_destination(shell, path: str, sources: int) -> Destination:
    """Decide where the copies go (raises UsageError with the message)."""
    try:
        node = shell.resolve(path)
    except PathError as error:
        if str(error) != ERR_NO_ENTRY:
            raise UsageError(f"cp: cannot stat '{path}': {error}") from error
        node = None
    if isinstance(node, Directory):
        return Destination(node, None)
    if sources > SINGLE:
        raise UsageError(f"cp: target '{path}' is not a directory")
    if node is not None:
        return Destination(node.parent, node.name)
    try:
        parent, name = shell.resolve_parent(path)
    except PathError as error:
        raise UsageError(
            f"cp: cannot create regular file '{path}': {error}") from error
    return Destination(parent, name)


def copy_problem(
    source: str, node: Node, target: str, existing: Node | None,
    destination: Destination,
) -> str | None:
    """Return why ``node`` cannot be copied to ``target``, or None."""
    if existing is node:
        return f"cp: '{source}' and '{target}' are the same file"
    is_dir = isinstance(node, Directory)
    if is_dir and is_inside(destination.directory, node):
        return (f"cp: cannot copy a directory, '{source}', "
                f"into itself, '{target}'")
    if isinstance(existing, Directory) and not is_dir:
        return f"cp: cannot overwrite directory '{target}' with non-directory"
    if existing is not None and is_dir and not isinstance(
            existing, Directory):
        return (f"cp: cannot overwrite non-directory '{target}' "
                f"with directory '{source}'")
    return None


def copy_one(
    shell, source: str, destination: Destination, dest_path: str,
    recursive: bool,
) -> str | None:
    """Copy one source; return an error message if it fails."""
    try:
        node = shell.resolve(source)
    except PathError as error:
        return f"cp: cannot stat '{source}': {error}"
    if isinstance(node, Directory) and not recursive:
        return f"cp: -r not specified; omitting directory '{source}'"
    name = destination.name or node.name
    target = dest_path
    if destination.name is None:
        target = join_path(dest_path, name)
    existing = destination.directory.children.get(name)
    problem = copy_problem(source, node, target, existing, destination)
    if problem is None:
        destination.directory.add(node.clone(name))
    return problem


def cmd_cp(shell, args: list[str]) -> Response:
    """Copy files; ``-r`` copies directories with their content."""
    response = Response()
    try:
        flags, operands = split_options("cp", args, CP_OPTIONS)
        if not operands:
            raise UsageError("cp: missing file operand")
        if len(operands) == SINGLE:
            raise UsageError(
                f"cp: missing destination file operand after '{operands[0]}'")
        *sources, dest_path = operands
        destination = find_destination(shell, dest_path, len(sources))
    except UsageError as error:
        response.err(str(error))
        return response
    for source in sources:
        problem = copy_one(shell, source, destination, dest_path, bool(flags))
        if problem is not None:
            response.err(problem)
    return response
