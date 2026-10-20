"""Tests of the command-line parameters."""
import io
import unittest
from contextlib import redirect_stderr

from shellemu.config import Config, debug_lines, parse_args


class ParseArgsTest(unittest.TestCase):
    """Parsing of --vfs, --script and --no-gui."""

    def test_defaults(self):
        self.assertEqual(parse_args([]), Config(None, None, False))

    def test_all_parameters(self):
        config = parse_args(
            ["--vfs", "a.xml", "--script", "s.emu", "--no-gui"])
        self.assertEqual(config, Config("a.xml", "s.emu", True))

    def test_unknown_parameter_exits(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args(["--unknown"])

    def test_missing_value_exits(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parse_args(["--vfs"])


class DebugLinesTest(unittest.TestCase):
    """The debug output lists every parameter."""

    def test_unset_parameters(self):
        text = "\n".join(debug_lines(Config()))
        self.assertIn("vfs    = (not set)", text)
        self.assertIn("script = (not set)", text)

    def test_given_parameters(self):
        text = "\n".join(debug_lines(Config("a.xml", "s.emu", True)))
        self.assertIn("vfs    = a.xml", text)
        self.assertIn("script = s.emu", text)
        self.assertIn("no-gui = True", text)


if __name__ == "__main__":
    unittest.main()
