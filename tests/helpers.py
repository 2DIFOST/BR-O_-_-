"""Helpers shared by the tests."""
import os
import tempfile

from shellemu.session import KIND_ERROR
from shellemu.shell import Shell
from shellemu.vfs_loader import load_vfs


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLE_VFS = os.path.join(ROOT, "examples", "vfs")
EXAMPLE_STARTUP = os.path.join(ROOT, "examples", "startup")
TEST_DATA = os.path.join(ROOT, "tests", "data")


class ListOutput:
    """Output that remembers everything written to it."""

    def __init__(self):
        """Start with no records."""
        self.records = []

    def write(self, text, kind):
        """Remember a line together with its kind."""
        self.records.append((text, kind))

    def texts(self):
        """Return only the texts."""
        return [text for text, _kind in self.records]

    def errors(self):
        """Return only the error texts."""
        return [text for text, kind in self.records if kind == KIND_ERROR]


def write_temp(test, name, content):
    """Create a file with ``content`` in a temp dir removed after test."""
    folder = tempfile.TemporaryDirectory()
    test.addCleanup(folder.cleanup)
    path = os.path.join(folder.name, name)
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)
    return path


def texts(response):
    """Return the texts of all messages of a response."""
    return [message.text for message in response.messages]


def shell_with(name):
    """Return a shell with the example VFS ``name`` loaded."""
    shell = Shell("u@h")
    shell.attach_vfs(load_vfs(os.path.join(EXAMPLE_VFS, name)))
    return shell
