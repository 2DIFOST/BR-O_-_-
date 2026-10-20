"""In-memory virtual file system (VFS)."""
from collections.abc import Iterator
from dataclasses import dataclass

from .errors import PathError

ROOT_NAME = ""
SEPARATOR = "/"
CURRENT = "."
PARENT = ".."
ERR_NO_ENTRY = "No such file or directory"
ERR_NOT_DIR = "Not a directory"
ERR_IS_DIR = "Is a directory"


class Node:
    """Common part of files and directories."""

    is_dir = False

    def __init__(self, name: str, parent: "Directory | None" = None) -> None:
        """Create a node with the given name inside ``parent``."""
        self.name = name
        self.parent = parent

    @property
    def path(self) -> str:
        """Return the absolute path of the node."""
        names = []
        node = self
        while node.parent is not None:
            names.append(node.name)
            node = node.parent
        return SEPARATOR + SEPARATOR.join(reversed(names))

    def clone(self, name: str) -> "Node":
        """Return a detached deep copy of the node named ``name``."""
        raise NotImplementedError


class File(Node):
    """A file; its content is a sequence of bytes."""

    def __init__(
        self, name: str, data: bytes = b"", parent: "Directory | None" = None
    ) -> None:
        """Create a file with the given content."""
        super().__init__(name, parent)
        self.data = data

    @property
    def size(self) -> int:
        """Return the size of the file in bytes."""
        return len(self.data)

    def clone(self, name: str) -> "File":
        """Return a copy of the file with the same content."""
        return File(name, self.data)


class Directory(Node):
    """A directory; it maps names to child nodes."""

    is_dir = True

    def __init__(
        self, name: str = ROOT_NAME, parent: "Directory | None" = None
    ) -> None:
        """Create an empty directory (the root by default)."""
        super().__init__(name, parent)
        self.children: dict[str, Node] = {}

    def add(self, node: Node) -> Node:
        """Put ``node`` into this directory and return it."""
        node.parent = self
        self.children[node.name] = node
        return node

    def remove(self, name: str) -> None:
        """Detach the child ``name`` together with all its content."""
        node = self.children.pop(name)
        node.parent = None

    def clone(self, name: str) -> "Directory":
        """Return a deep copy of the directory and everything in it."""
        copy = Directory(name)
        for child_name, child in self.children.items():
            copy.add(child.clone(child_name))
        return copy


@dataclass(frozen=True)
class VfsStats:
    """Summary of the content of a VFS."""

    directories: int
    files: int
    size: int
    depth: int


def walk(directory: Directory, level: int = 1) -> Iterator[tuple[int, Node]]:
    """Yield (level, node) for all descendants in name order."""
    for name in sorted(directory.children):
        node = directory.children[name]
        yield level, node
        if isinstance(node, Directory):
            yield from walk(node, level + 1)


def describe(node: Node) -> str:
    """Return the name of a node with a short description."""
    if isinstance(node, File):
        return f"{node.name} ({node.size} bytes)"
    return node.name + SEPARATOR


def tree_lines(directory: Directory, prefix: str = "") -> Iterator[str]:
    """Yield the lines of an ASCII tree of the directory content."""
    names = sorted(directory.children)
    for index, name in enumerate(names):
        node = directory.children[name]
        last = index == len(names) - 1
        yield prefix + ("`-- " if last else "|-- ") + describe(node)
        if isinstance(node, Directory):
            yield from tree_lines(node, prefix + ("    " if last else "|   "))


def step(node: Node, part: str) -> Node:
    """Return the node reached from ``node`` by one path component."""
    if not isinstance(node, Directory):
        raise PathError(ERR_NOT_DIR)
    match part:
        case "" | ".":
            return node
        case "..":
            return node.parent if node.parent is not None else node
        case _:
            child = node.children.get(part)
            if child is None:
                raise PathError(ERR_NO_ENTRY)
            return child


def resolve(root: Directory, cwd: Directory, path: str) -> Node:
    """Find the node for an absolute or relative path.

    Raises PathError if some component does not exist or a file is
    used as a directory (also when the path ends with ``/``).
    """
    node: Node = root if path.startswith(SEPARATOR) else cwd
    for part in path.split(SEPARATOR):
        node = step(node, part)
    if path.endswith(SEPARATOR) and not isinstance(node, Directory):
        raise PathError(ERR_NOT_DIR)
    return node


def is_inside(node: Node, directory: Directory) -> bool:
    """Return True if ``node`` is ``directory`` or lies somewhere in it."""
    current: Node | None = node
    while current is not None:
        if current is directory:
            return True
        current = current.parent
    return False


def resolve_parent(
    root: Directory, cwd: Directory, path: str
) -> tuple[Directory, str]:
    """Return the directory that holds ``path`` and its last name.

    The last component itself does not have to exist, which makes the
    function suitable for creating new entries. Raises PathError if
    the parent is missing or is not a directory.
    """
    head, _separator, name = path.rstrip(SEPARATOR).rpartition(SEPARATOR)
    if name in ("", CURRENT, PARENT):
        raise PathError(ERR_NO_ENTRY)
    base = head or (SEPARATOR if path.startswith(SEPARATOR) else CURRENT)
    parent = resolve(root, cwd, base)
    if not isinstance(parent, Directory):
        raise PathError(ERR_NOT_DIR)
    return parent, name


class Vfs:
    """A loaded virtual file system and the place it came from."""

    def __init__(
        self, root: Directory | None = None, source: str | None = None
    ) -> None:
        """Create a VFS; without a root it is empty."""
        self.root = root if root is not None else Directory()
        self.source = source

    def stats(self) -> VfsStats:
        """Count directories, files, bytes and the depth of the tree."""
        directories = files = size = depth = 0
        for level, node in walk(self.root):
            depth = max(depth, level)
            if isinstance(node, File):
                files += 1
                size += node.size
            else:
                directories += 1
        return VfsStats(directories, files, size, depth)
