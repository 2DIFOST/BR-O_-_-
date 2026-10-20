"""Commands for navigating the file system: ``ls`` and ``cd``."""
from dataclasses import dataclass

from ..errors import PathError, UsageError
from ..response import Response
from ..vfs import CURRENT, ERR_NOT_DIR, Directory, File, Node
from .options import split_options

Entries = list[tuple[str, Node]]

LS_OPTIONS = "al"
DIRECTORY_SIZE = 0
MIN_OPERANDS_FOR_HEADERS = 2


@dataclass
class Target:
    """An operand of ``ls``: the path as typed and the node it names."""

    path: str
    node: Node


def node_size(node: Node) -> int:
    """Return the size shown by ``ls -l``."""
    return node.size if isinstance(node, File) else DIRECTORY_SIZE


def type_char(node: Node) -> str:
    """Return ``d`` for directories and ``-`` for files."""
    return "d" if isinstance(node, Directory) else "-"


def list_entries(directory: Directory, show_all: bool) -> Entries:
    """Return the sorted (name, node) pairs of a directory."""
    entries = [
        (name, node) for name, node in directory.children.items()
        if show_all or not name.startswith(".")
    ]
    if show_all:
        parent = directory.parent or directory
        entries += [(".", directory), ("..", parent)]
    return sorted(entries, key=lambda entry: entry[0])


def format_entries(entries: Entries, long: bool) -> list[str]:
    """Format entries as names or as the long listing (``-l``)."""
    if not long:
        return [name for name, _node in entries]
    sizes = [node_size(node) for _name, node in entries]
    width = len(str(max(sizes, default=DIRECTORY_SIZE)))
    return [
        f"{type_char(node)} {node_size(node):>{width}} {name}"
        for name, node in entries
    ]


def collect_targets(
    shell, operands: list[str], response: Response
) -> tuple[list[Target], list[Target]]:
    """Resolve the operands; return (files, directories).

    Operands that cannot be found are reported as errors.
    """
    files: list[Target] = []
    directories: list[Target] = []
    for path in operands:
        try:
            node = shell.resolve(path)
        except PathError as error:
            response.err(f"ls: cannot access '{path}': {error}")
            continue
        group = directories if isinstance(node, Directory) else files
        group.append(Target(path, node))
    return files, directories


def build_blocks(
    files: list[Target], directories: list[Target],
    flags: set[str], with_headers: bool,
) -> list[list[str]]:
    """Return the blocks of lines separated by empty lines."""
    long = "l" in flags
    blocks = []
    if files:
        entries = [(target.path, target.node) for target in files]
        entries.sort(key=lambda entry: entry[0])
        blocks.append(format_entries(entries, long))
    for target in sorted(directories, key=lambda t: t.path):
        entries = list_entries(target.node, "a" in flags)
        header = [target.path + ":"] if with_headers else []
        blocks.append(header + format_entries(entries, long))
    return blocks


def cmd_ls(shell, args: list[str]) -> Response:
    """List a directory (or files); supports ``-a`` and ``-l``."""
    response = Response()
    try:
        flags, operands = split_options("ls", args, LS_OPTIONS)
    except UsageError as error:
        response.err(str(error))
        return response
    operands = operands or [CURRENT]
    files, directories = collect_targets(shell, operands, response)
    with_headers = len(operands) >= MIN_OPERANDS_FOR_HEADERS
    blocks = build_blocks(files, directories, flags, with_headers)
    for number, block in enumerate(blocks):
        if number:
            response.out("")
        for line in block:
            response.out(line)
    return response


def change_directory(shell, path: str, response: Response) -> None:
    """Make ``path`` the current directory or report why it is not."""
    try:
        node = shell.resolve(path)
    except PathError as error:
        response.err(f"cd: {path}: {error}")
        return
    if isinstance(node, Directory):
        shell.cwd = node
    else:
        response.err(f"cd: {path}: {ERR_NOT_DIR}")


def cmd_cd(shell, args: list[str]) -> Response:
    """Change the current directory; without arguments go to ``/``."""
    response = Response()
    match args:
        case []:
            shell.cwd = shell.vfs.root
        case [path]:
            change_directory(shell, path, response)
        case _:
            response.err("cd: too many arguments")
    return response
