"""Tests of command execution in the shell core."""
import unittest

from shellemu.response import STATUS_NOT_FOUND, STATUS_OK
from shellemu.shell import Shell


def texts(response):
    """Return the texts of all messages of a response."""
    return [message.text for message in response.messages]


class ShellTest(unittest.TestCase):
    """Behaviour of the shell core and error reporting."""

    def setUp(self):
        self.shell = Shell("tester@box")

    def test_prompt_contains_identity_and_directory(self):
        self.assertEqual(self.shell.prompt(), "tester@box:/$ ")

    def test_empty_line_does_nothing(self):
        response = self.shell.execute("   ")
        self.assertEqual(texts(response), [])
        self.assertTrue(response.ok)

    def test_unknown_command(self):
        response = self.shell.execute("foo bar")
        self.assertEqual(texts(response), ["foo: command not found"])
        self.assertEqual(response.status, STATUS_NOT_FOUND)
        self.assertTrue(response.messages[0].is_error)

    def test_ls_of_empty_vfs_prints_nothing(self):
        response = self.shell.execute("ls")
        self.assertEqual(texts(response), [])
        self.assertEqual(response.status, STATUS_OK)

    def test_cd_without_arguments_goes_to_root(self):
        self.assertTrue(self.shell.execute("cd").ok)
        self.assertEqual(self.shell.prompt(), "tester@box:/$ ")

    def test_cd_with_too_many_arguments(self):
        response = self.shell.execute("cd a b")
        self.assertEqual(texts(response), ["cd: too many arguments"])
        self.assertFalse(response.ok)

    def test_exit_stops_the_shell(self):
        self.assertTrue(self.shell.execute("exit").should_exit)

    def test_exit_with_arguments_is_an_error(self):
        response = self.shell.execute("exit now")
        self.assertFalse(response.should_exit)
        self.assertEqual(texts(response), ["exit: too many arguments"])


if __name__ == "__main__":
    unittest.main()
