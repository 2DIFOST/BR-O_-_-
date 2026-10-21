"""Tests of the commands ls and cd on a VFS (stage 4)."""
from functools import cached_property
import unittest

from helpers import shell_with, texts


class LsTest(unittest.TestCase):
    """Listing of directories and files."""

    @cached_property
    def shell(self):
        """Return a fresh shell for every test."""
        return shell_with("several_files.xml")

    @cached_property
    def deep(self):
        """Return a fresh shell with the deep VFS."""
        return shell_with("deep.xml")

    def test_plain_listing_is_sorted(self):
        self.assertEqual(texts(self.shell.execute("ls")), [
            "data.bin", "empty.txt", "hello.txt", "notes.txt",
            "russian.txt",
        ])

    def test_long_listing_shows_type_and_size(self):
        lines = texts(self.shell.execute("ls -l"))
        self.assertEqual(lines[0], "- 16 data.bin")
        self.assertEqual(lines[1], "-  0 empty.txt")

    def test_long_listing_marks_directories(self):
        lines = texts(self.deep.execute("ls -l home/user"))
        self.assertEqual(lines[0], "d  0 docs")

    def test_hidden_files_need_option_a(self):
        self.assertEqual(texts(self.deep.execute("ls /home/guest")), [])
        self.assertEqual(
            texts(self.deep.execute("ls -a /home/guest")),
            [".", "..", ".hidden"])

    def test_bundled_options(self):
        lines = texts(self.deep.execute("ls -la /home/guest"))
        self.assertEqual(lines[2], "- 7 .hidden")

    def test_ls_of_a_file_prints_its_path(self):
        self.assertEqual(
            texts(self.shell.execute("ls hello.txt")), ["hello.txt"])

    def test_ls_of_a_path(self):
        self.assertEqual(
            texts(self.deep.execute("ls /home")), ["guest", "user"])

    def test_several_operands_have_headers(self):
        lines = texts(self.deep.execute("ls /home/user/docs /bin"))
        self.assertEqual(lines, [
            "/bin:", "tool.bin", "", "/home/user/docs:", "drafts",
            "report.txt",
        ])

    def test_files_are_listed_before_directories(self):
        lines = texts(self.deep.execute("ls /bin readme.txt"))
        self.assertEqual(lines[:2], ["readme.txt", ""])

    def test_missing_path_is_an_error(self):
        response = self.shell.execute("ls nosuch")
        self.assertEqual(
            texts(response),
            ["ls: cannot access 'nosuch': No such file or directory"])
        self.assertFalse(response.ok)

    def test_error_does_not_hide_other_operands(self):
        response = self.shell.execute("ls nosuch hello.txt")
        self.assertEqual(len(response.messages), 2)
        self.assertFalse(response.ok)

    def test_invalid_option(self):
        response = self.shell.execute("ls -x")
        self.assertEqual(texts(response), ["ls: invalid option -- 'x'"])
        self.assertFalse(response.ok)

    def test_unrecognized_long_option(self):
        response = self.shell.execute("ls --color")
        self.assertEqual(
            texts(response), ["ls: unrecognized option '--color'"])

    def test_file_with_trailing_slash_is_not_a_directory(self):
        response = self.shell.execute("ls hello.txt/")
        self.assertFalse(response.ok)

    def test_double_dash_ends_options(self):
        response = self.shell.execute("ls -- -l")
        self.assertIn("'-l'", texts(response)[0])


class CdTest(unittest.TestCase):
    """Changing the current directory."""

    @cached_property
    def shell(self):
        """Return a fresh shell for every test."""
        return shell_with("deep.xml")

    def test_cd_relative_and_absolute(self):
        self.assertTrue(self.shell.execute("cd home/user").ok)
        self.assertEqual(self.shell.cwd.path, "/home/user")
        self.assertTrue(self.shell.execute("cd /bin").ok)
        self.assertEqual(self.shell.cwd.path, "/bin")

    def test_cd_dot_dot(self):
        self.shell.execute("cd /home/user/docs")
        self.shell.execute("cd ../..")
        self.assertEqual(self.shell.cwd.path, "/home")

    def test_dot_dot_of_root_is_root(self):
        self.shell.execute("cd ../../..")
        self.assertEqual(self.shell.cwd.path, "/")

    def test_cd_without_arguments_goes_to_root(self):
        self.shell.execute("cd /home/user")
        self.shell.execute("cd")
        self.assertEqual(self.shell.cwd.path, "/")

    def test_prompt_shows_current_directory(self):
        self.shell.execute("cd /home/user")
        self.assertEqual(self.shell.prompt(), "u@h:/home/user$ ")

    def test_ls_uses_current_directory(self):
        self.shell.execute("cd /home/user/docs")
        self.assertEqual(
            texts(self.shell.execute("ls")), ["drafts", "report.txt"])

    def test_cd_to_missing_directory(self):
        response = self.shell.execute("cd nosuch")
        self.assertEqual(
            texts(response), ["cd: nosuch: No such file or directory"])
        self.assertEqual(self.shell.cwd.path, "/")

    def test_cd_to_a_file(self):
        response = self.shell.execute("cd readme.txt")
        self.assertEqual(texts(response), ["cd: readme.txt: Not a directory"])
        self.assertEqual(self.shell.cwd.path, "/")

    def test_path_through_a_file(self):
        response = self.shell.execute("cd readme.txt/x")
        self.assertEqual(texts(response), ["cd: readme.txt/x: Not a directory"])

    def test_too_many_arguments(self):
        response = self.shell.execute("cd a b")
        self.assertEqual(texts(response), ["cd: too many arguments"])
        self.assertFalse(response.ok)


if __name__ == "__main__":
    unittest.main()
