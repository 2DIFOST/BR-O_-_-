"""Tests of the entry point in terminal mode."""
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from helpers import write_temp
from shellemu import cli, console


def run_main(args, stdin_text=""):
    """Run cli.main with fake stdin; return (status, stdout, stderr)."""
    stdout, stderr = io.StringIO(), io.StringIO()
    with mock.patch.object(console.sys, "stdin", io.StringIO(stdin_text)):
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = cli.main(args)
    return status, stdout.getvalue(), stderr.getvalue()


class ConsoleModeTest(unittest.TestCase):
    """The --no-gui mode behaves like the window."""

    def test_stdin_dialog_is_echoed(self):
        status, out, _err = run_main(["--no-gui"], "ls x\nexit\n")
        self.assertEqual(status, cli.EXIT_OK)
        self.assertRegex(out, r"\$ ls x\nls x\n")
        self.assertIn("[debug]   no-gui = True", out)

    def test_end_of_input_finishes(self):
        status, _out, _err = run_main(["--no-gui"], "ls\n")
        self.assertEqual(status, cli.EXIT_OK)

    def test_errors_go_to_stderr(self):
        _status, _out, err = run_main(["--no-gui"], "foo\n")
        self.assertIn("foo: command not found", err)

    def test_failed_script_gives_error_status(self):
        path = write_temp(self, "s.emu", "foo\n")
        status, _out, err = run_main(
            ["--no-gui", "--script", path], "exit\n")
        self.assertEqual(status, cli.EXIT_ERROR)
        self.assertIn("script error", err)

    def test_successful_script(self):
        path = write_temp(self, "s.emu", "ls a\nexit\n")
        status, out, _err = run_main(["--no-gui", "--script", path])
        self.assertEqual(status, cli.EXIT_OK)
        self.assertIn("ls a", out)


if __name__ == "__main__":
    unittest.main()
