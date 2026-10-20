"""Tests of the service commands vfs-info and vfs-tree."""
import os
import unittest

from helpers import EXAMPLE_VFS
from shellemu.shell import Shell
from shellemu.vfs_loader import load_vfs


def texts(response):
    """Return the texts of all messages of a response."""
    return [message.text for message in response.messages]


class ServiceCommandsTest(unittest.TestCase):
    """Information about the loaded VFS."""

    def shell_with(self, name):
        """Return a shell with an example VFS loaded."""
        shell = Shell("u@h")
        shell.attach_vfs(load_vfs(os.path.join(EXAMPLE_VFS, name)))
        return shell

    def test_info_of_the_empty_builtin_vfs(self):
        lines = texts(Shell("u@h").execute("vfs-info"))
        self.assertEqual(lines[0], "source:      (empty, built-in)")
        self.assertEqual(lines[1], "directories: 0")

    def test_info_of_several_files(self):
        lines = texts(self.shell_with("several_files.xml")
                      .execute("vfs-info"))
        self.assertIn("files:       5", lines)
        self.assertIn("size:        80 bytes", lines)

    def test_info_of_deep_vfs(self):
        lines = texts(self.shell_with("deep.xml").execute("vfs-info"))
        self.assertIn("directories: 9", lines)
        self.assertIn("depth:       6", lines)

    def test_tree_of_several_files(self):
        lines = texts(self.shell_with("several_files.xml")
                      .execute("vfs-tree"))
        self.assertEqual(lines[0], "/")
        self.assertIn("|-- data.bin (16 bytes)", lines)

    def test_tree_of_minimal_vfs(self):
        lines = texts(self.shell_with("minimal.xml").execute("vfs-tree"))
        self.assertEqual(lines, ["/"])

    def test_arguments_are_rejected(self):
        shell = Shell("u@h")
        for line in ("vfs-info x", "vfs-tree x"):
            with self.subTest(line=line):
                response = shell.execute(line)
                self.assertFalse(response.ok)
                self.assertIn("too many arguments", texts(response)[0])


if __name__ == "__main__":
    unittest.main()
