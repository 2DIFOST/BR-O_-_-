"""Tests of the commands wc and echo (stage 4)."""
from functools import cached_property
import unittest

from helpers import shell_with, texts


class WcTest(unittest.TestCase):
    """Counting of lines, words and bytes."""

    @cached_property
    def shell(self):
        """Return a fresh shell for every test."""
        return shell_with("several_files.xml")

    def test_all_counters_by_default(self):
        self.assertEqual(
            texts(self.shell.execute("wc notes.txt")), [" 3  6 28 notes.txt"])

    def test_single_counter_is_not_padded(self):
        self.assertEqual(
            texts(self.shell.execute("wc -l hello.txt")), ["1 hello.txt"])
        self.assertEqual(
            texts(self.shell.execute("wc -w notes.txt")), ["6 notes.txt"])
        self.assertEqual(
            texts(self.shell.execute("wc -c notes.txt")), ["28 notes.txt"])

    def test_selected_counters_keep_fixed_order(self):
        lines = texts(self.shell.execute("wc -cl notes.txt"))
        self.assertEqual(lines, [" 3 28 notes.txt"])

    def test_bundled_options(self):
        lines = texts(self.shell.execute("wc -lw notes.txt"))
        self.assertEqual(lines, [" 3  6 notes.txt"])

    def test_bytes_not_characters(self):
        lines = texts(self.shell.execute("wc -c russian.txt"))
        self.assertEqual(lines, ["22 russian.txt"])

    def test_empty_file(self):
        lines = texts(self.shell.execute("wc empty.txt"))
        self.assertEqual(lines, ["0 0 0 empty.txt"])

    def test_binary_file(self):
        lines = texts(self.shell.execute("wc -c data.bin"))
        self.assertEqual(lines, ["16 data.bin"])

    def test_several_files_have_total(self):
        lines = texts(self.shell.execute("wc -lw notes.txt hello.txt"))
        self.assertEqual(
            lines, [" 3  6 notes.txt", " 1  2 hello.txt", " 4  8 total"])

    def test_missing_file(self):
        response = self.shell.execute("wc nosuch")
        self.assertEqual(
            texts(response), ["wc: nosuch: No such file or directory"])
        self.assertFalse(response.ok)

    def test_directory(self):
        response = self.shell.execute("wc /")
        self.assertEqual(texts(response), ["wc: /: Is a directory"])
        self.assertFalse(response.ok)

    def test_missing_operand(self):
        response = self.shell.execute("wc -l")
        self.assertEqual(texts(response), ["wc: missing file operand"])
        self.assertFalse(response.ok)

    def test_invalid_option(self):
        response = self.shell.execute("wc -z notes.txt")
        self.assertEqual(texts(response), ["wc: invalid option -- 'z'"])

    def test_good_files_are_counted_despite_an_error(self):
        response = self.shell.execute("wc -l nosuch hello.txt")
        self.assertEqual(len(response.messages), 3)
        self.assertFalse(response.ok)


class EchoTest(unittest.TestCase):
    """Printing of the arguments."""

    @cached_property
    def shell(self):
        """Return a fresh shell for every test."""
        return shell_with("minimal.xml")

    def test_echo_joins_arguments_with_one_space(self):
        self.assertEqual(
            texts(self.shell.execute("echo a   b  c")), ["a b c"])

    def test_echo_without_arguments_prints_empty_line(self):
        self.assertEqual(texts(self.shell.execute("echo")), [""])

    def test_echo_does_not_interpret_options(self):
        self.assertEqual(texts(self.shell.execute("echo -n x")), ["-n x"])


if __name__ == "__main__":
    unittest.main()
