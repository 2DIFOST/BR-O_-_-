"""Tests of command execution in the shell core."""
import unittest

from shellemu.response import STATUS_NOT_FOUND, STATUS_OK
from shellemu.shell import Shell


def texts(response):
    """Return the texts of all messages of a response."""
    return [message.text for message in response.messages]


class ShellTest(unittest.TestCase):
    """Behaviour of the stub commands and error reporting."""

    def setUp(self):
        self.shell = Shell("tester@box")

    def test_prompt_contains_identity(self):
        self.assertIn("tester@box", self.shell.prompt())

    def test_empty_line_does_nothing(self):
        response = self.shell.execute("   ")
        self.assertEqual(texts(response), [])
        self.assertTrue(response.ok)

    def test_unknown_command(self):
        response = self.shell.execute("foo bar")
        self.assertEqual(texts(response), ["foo: command not found"])
        self.assertEqual(response.status, STATUS_NOT_FOUND)
        self.assertTrue(response.messages[0].is_error)

    def test_ls_stub_prints_name_and_arguments(self):
        response = self.shell.execute("ls -l /tmp /var")
        self.assertEqual(texts(response), ["ls -l /tmp /var"])
        self.assertEqual(response.status, STATUS_OK)

    def test_ls_stub_without_arguments(self):
        self.assertEqual(texts(self.shell.execute("ls")), ["ls"])

    def test_cd_stub_prints_name_and_argument(self):
        self.assertEqual(texts(self.shell.execute("cd docs")), ["cd docs"])
        self.assertEqual(texts(self.shell.execute("cd")), ["cd"])

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
