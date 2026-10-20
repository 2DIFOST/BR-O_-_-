"""Helpers shared by the tests."""
import os
import tempfile

from shellemu.session import KIND_ERROR


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
