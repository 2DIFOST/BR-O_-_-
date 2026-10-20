"""Tests of the graphical interface (skipped without a display)."""
import unittest

from shellemu.shell import Shell

try:
    from shellemu.gui import EmulatorWindow
    import tkinter
except ImportError:
    tkinter = None


def make_window():
    """Create a window or return None if there is no display."""
    try:
        return EmulatorWindow(Shell("tester@box"), "Test")
    except tkinter.TclError:
        return None


@unittest.skipIf(tkinter is None, "tkinter is not installed")
class GuiTest(unittest.TestCase):
    """The window must show the dialog like a terminal."""

    def setUp(self):
        self.window = make_window()
        if self.window is None:
            self.skipTest("no display available")

    def tearDown(self):
        if self.window is not None:
            self.window.root.destroy()

    def output_text(self):
        """Return everything shown in the output area."""
        return self.window.output.get("1.0", tkinter.END)

    def type_line(self, line):
        """Emulate typing a line and pressing Enter."""
        self.window.entry.insert(0, line)
        self.window.on_enter(None)

    def test_title(self):
        self.assertEqual(self.window.root.title(), "Test")

    def test_dialog_is_shown(self):
        self.type_line("ls -l")
        self.assertIn("tester@box:~$ ls -l", self.output_text())
        self.assertIn("ls -l\n", self.output_text())

    def test_error_is_shown(self):
        self.type_line("foo")
        self.assertIn("foo: command not found", self.output_text())

    def test_entry_is_cleared_after_enter(self):
        self.type_line("ls")
        self.assertEqual(self.window.entry.get(), "")

    def test_history_with_up_key(self):
        self.type_line("ls")
        self.window.on_up(None)
        self.assertEqual(self.window.entry.get(), "ls")


if __name__ == "__main__":
    unittest.main()
