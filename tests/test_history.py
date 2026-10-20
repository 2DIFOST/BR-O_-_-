"""Tests of the command history."""
import unittest

from shellemu.history import History


class HistoryTest(unittest.TestCase):
    """Navigation through the entered lines."""

    def setUp(self):
        self.history = History()
        for line in ("ls", "cd a", "ls -l"):
            self.history.add(line)

    def test_previous_walks_back_and_stops_at_start(self):
        self.assertEqual(self.history.previous(), "ls -l")
        self.assertEqual(self.history.previous(), "cd a")
        self.assertEqual(self.history.previous(), "ls")
        self.assertEqual(self.history.previous(), "ls")

    def test_following_returns_empty_line_at_the_end(self):
        self.history.previous()
        self.assertEqual(self.history.following(), "")
        self.assertEqual(self.history.following(), "")

    def test_empty_lines_are_not_stored(self):
        self.history.add("")
        self.assertEqual(self.history.items, ["ls", "cd a", "ls -l"])

    def test_empty_history(self):
        history = History()
        self.assertEqual(history.previous(), "")
        self.assertEqual(history.following(), "")


if __name__ == "__main__":
    unittest.main()
