"""Tests of the command-line parser."""
import unittest

from shellemu.parser import parse_line


class ParseLineTest(unittest.TestCase):
    """Splitting of a line into the command and its arguments."""

    def test_command_without_arguments(self):
        self.assertEqual(parse_line("ls"), ["ls"])

    def test_command_with_arguments(self):
        self.assertEqual(parse_line("cd a b"), ["cd", "a", "b"])

    def test_extra_whitespace_is_ignored(self):
        self.assertEqual(parse_line("  ls \t -l   dir  "),
                         ["ls", "-l", "dir"])

    def test_empty_line(self):
        self.assertEqual(parse_line(""), [])
        self.assertEqual(parse_line("   "), [])


if __name__ == "__main__":
    unittest.main()
