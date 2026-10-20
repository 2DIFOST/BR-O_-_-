"""Service commands for inspecting the loaded VFS."""
from ..response import Response
from ..vfs import tree_lines

NO_SOURCE = "(empty, built-in)"


def cmd_vfs_info(shell, args: list[str]) -> Response:
    """Print the source and the statistics of the loaded VFS."""
    response = Response()
    match args:
        case []:
            stats = shell.vfs.stats()
            response.out(f"source:      {shell.vfs.source or NO_SOURCE}")
            response.out(f"directories: {stats.directories}")
            response.out(f"files:       {stats.files}")
            response.out(f"size:        {stats.size} bytes")
            response.out(f"depth:       {stats.depth}")
        case _:
            response.err("vfs-info: too many arguments")
    return response


def cmd_vfs_tree(shell, args: list[str]) -> Response:
    """Print the whole VFS as a tree."""
    response = Response()
    match args:
        case []:
            response.out("/")
            for line in tree_lines(shell.vfs.root):
                response.out(line)
        case _:
            response.err("vfs-tree: too many arguments")
    return response
