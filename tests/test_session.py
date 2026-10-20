"""Tests of the dialog session and startup scripts."""
import os
import unittest

from helpers import EXAMPLE_VFS, TEST_DATA, ListOutput, write_temp
from shellemu.config import Config
from shellemu.session import KIND_DEBUG, KIND_INPUT, Session
from shellemu.shell import Shell


class SessionTest(unittest.TestCase):
    """Running of lines and scripts."""

    def setUp(self):
        self.output = ListOutput()
        self.session = Session(Shell("u@h"), self.output)

    def test_run_line_echoes_input(self):
        self.session.run_line("ls a")
        self.assertEqual(self.output.records[0][1], KIND_INPUT)
        self.assertEqual(self.output.texts()[0], "u@h:/$ ls a")
        self.assertEqual(self.output.texts()[1], "ls a")

    def test_execute_line_does_not_echo(self):
        self.session.execute_line("ls a")
        self.assertEqual(self.output.texts(), ["ls a"])

    def test_exit_finishes_session(self):
        self.session.run_line("exit")
        self.assertTrue(self.session.finished)

    def test_script_runs_as_dialog(self):
        path = write_temp(self, "s.emu", "ls a\n\ncd b\n")
        self.assertTrue(self.session.run_script(path))
        self.assertEqual(self.output.texts(), [
            "u@h:/$ ls a", "ls a", "u@h:/$ cd b", "cd b",
        ])

    def test_script_stops_at_first_error(self):
        path = write_temp(self, "s.emu", "ls a\nfoo\nls never\n")
        self.assertFalse(self.session.run_script(path))
        self.assertNotIn("ls never", self.output.texts())
        self.assertIn("foo: command not found", self.output.errors())
        self.assertIn("line 2 failed", self.output.errors()[-1])

    def test_script_comments_are_echoed_but_not_executed(self):
        path = write_temp(self, "s.emu", "# note\nls\n")
        self.assertTrue(self.session.run_script(path))
        self.assertEqual(self.output.texts()[0], "u@h:/$ # note")

    def test_script_exit_stops_the_rest(self):
        path = write_temp(self, "s.emu", "exit\nls never\n")
        self.assertTrue(self.session.run_script(path))
        self.assertTrue(self.session.finished)
        self.assertNotIn("ls never", self.output.texts())

    def test_missing_script_is_reported(self):
        self.assertFalse(self.session.run_script("/no/such/file"))
        self.assertIn("cannot read script", self.output.errors()[0])

    def test_binary_script_is_reported(self):
        path = write_temp(self, "s.emu", "")
        with open(path, "wb") as file:
            file.write(b"\xff\xfe\x00bad")
        self.assertFalse(self.session.run_script(path))
        self.assertIn("not a UTF-8 text file", self.output.errors()[0])


class StartupTest(unittest.TestCase):
    """Debug output and the startup script."""

    def test_debug_output_comes_first(self):
        output = ListOutput()
        session = Session(Shell("u@h"), output)
        session.startup(Config(None, None, True))
        self.assertTrue(all(kind == KIND_DEBUG
                            for _text, kind in output.records))
        self.assertIn("[debug]   no-gui = True", output.texts())

    def test_startup_failure_is_remembered(self):
        session = Session(Shell("u@h"), ListOutput())
        session.startup(Config(None, "/no/such/file", True))
        self.assertFalse(session.startup_ok)

    def test_startup_without_script_is_ok(self):
        session = Session(Shell("u@h"), ListOutput())
        session.startup(Config())
        self.assertTrue(session.startup_ok)


class VfsStartupTest(unittest.TestCase):
    """Loading of the VFS at startup."""

    def setUp(self):
        self.output = ListOutput()
        self.session = Session(Shell("u@h"), self.output)

    def test_vfs_is_loaded(self):
        path = os.path.join(EXAMPLE_VFS, "deep.xml")
        self.session.startup(Config(path, None, True))
        self.assertTrue(self.session.startup_ok)
        self.assertEqual(self.session.shell.vfs.source, path)
        self.assertIn(f"[debug]   vfs    = {path}", self.output.texts())

    def test_missing_vfs_is_reported(self):
        self.session.startup(Config("/no/such/vfs.xml", None, True))
        self.assertFalse(self.session.startup_ok)
        self.assertIn("vfs error: cannot load VFS", self.output.errors()[0])
        self.assertIsNone(self.session.shell.vfs.source)

    def test_invalid_vfs_is_reported(self):
        path = os.path.join(TEST_DATA, "wrong_root.xml")
        self.session.startup(Config(path, None, True))
        self.assertFalse(self.session.startup_ok)
        self.assertIn("invalid format", self.output.errors()[0])

    def test_script_is_skipped_after_vfs_error(self):
        script = write_temp(self, "s.emu", "vfs-info\n")
        self.session.startup(Config("/no/such/vfs.xml", script, True))
        self.assertIn("startup script skipped", self.output.errors()[-1])
        self.assertNotIn("vfs-info", " ".join(self.output.texts()))

    def test_script_works_with_loaded_vfs(self):
        path = os.path.join(EXAMPLE_VFS, "several_files.xml")
        script = write_temp(self, "s.emu", "vfs-info\n")
        self.session.startup(Config(path, script, True))
        self.assertTrue(self.session.startup_ok)
        self.assertIn("files:       5", self.output.texts())


if __name__ == "__main__":
    unittest.main()
