"""Tests of the commands rm and cp that change the VFS (stage 5)."""
from functools import cached_property
import unittest

from helpers import shell_with, texts


class RmTest(unittest.TestCase):
    """Removing files and directories in memory."""

    @cached_property
    def shell(self):
        """Return a fresh shell for every test."""
        return shell_with("deep.xml")

    def names(self, path="/"):
        """Return the names listed by ``ls`` for ``path``."""
        return texts(self.shell.execute(f"ls -a {path}"))

    def test_remove_a_file(self):
        self.assertTrue(self.shell.execute("rm readme.txt").ok)
        self.assertNotIn("readme.txt", self.names())

    def test_remove_several_files(self):
        self.shell.execute("rm home/user/notes.txt readme.txt")
        self.assertNotIn("readme.txt", self.names())
        self.assertNotIn("notes.txt", self.names("home/user"))

    def test_directory_needs_option_r(self):
        response = self.shell.execute("rm bin")
        self.assertEqual(
            texts(response), ["rm: cannot remove 'bin': Is a directory"])
        self.assertFalse(response.ok)
        self.assertIn("bin", self.names())

    def test_remove_directory_recursively(self):
        self.assertTrue(self.shell.execute("rm -r home/user").ok)
        self.assertEqual(self.names("home"), [".", "..", "guest"])

    def test_capital_r_is_the_same_as_r(self):
        self.assertTrue(self.shell.execute("rm -R bin").ok)
        self.assertNotIn("bin", self.names())

    def test_missing_file(self):
        response = self.shell.execute("rm nosuch")
        self.assertEqual(
            texts(response),
            ["rm: cannot remove 'nosuch': No such file or directory"])
        self.assertFalse(response.ok)

    def test_force_ignores_missing_files(self):
        response = self.shell.execute("rm -f nosuch")
        self.assertEqual(texts(response), [])
        self.assertTrue(response.ok)

    def test_force_does_not_hide_other_errors(self):
        response = self.shell.execute("rm -f bin")
        self.assertFalse(response.ok)

    def test_missing_operand(self):
        response = self.shell.execute("rm")
        self.assertEqual(texts(response), ["rm: missing operand"])
        self.assertFalse(response.ok)

    def test_missing_operand_with_force_is_silent(self):
        self.assertTrue(self.shell.execute("rm -f").ok)

    def test_other_operands_are_removed_despite_an_error(self):
        response = self.shell.execute("rm nosuch readme.txt")
        self.assertFalse(response.ok)
        self.assertNotIn("readme.txt", self.names())

    def test_dot_and_dot_dot_are_refused(self):
        for path in (".", "..", "bin/..", "bin/."):
            response = self.shell.execute(f"rm -r {path}")
            self.assertFalse(response.ok, path)

    def test_root_is_protected(self):
        response = self.shell.execute("rm -r /")
        self.assertEqual(
            texts(response),
            ["rm: it is dangerous to operate recursively on '/'"])
        self.assertIn("bin", self.names())

    def test_current_directory_and_its_parents_are_protected(self):
        self.shell.execute("cd /home/user/docs")
        for path in ("/home", "../../user", "/home/user/docs"):
            response = self.shell.execute(f"rm -r {path}")
            self.assertEqual(
                texts(response),
                [f"rm: cannot remove '{path}': Device or resource busy"])
        self.assertEqual(self.shell.cwd.path, "/home/user/docs")

    def test_removal_does_not_touch_the_xml_file(self):
        with open(self.shell.vfs.source, "rb") as file:
            before = file.read()
        self.shell.execute("rm -r home bin readme.txt")
        with open(self.shell.vfs.source, "rb") as file:
            self.assertEqual(file.read(), before)

    def test_invalid_option(self):
        response = self.shell.execute("rm -x a")
        self.assertEqual(texts(response), ["rm: invalid option -- 'x'"])

    def test_stats_follow_the_changes(self):
        self.shell.execute("rm -r home")
        lines = texts(self.shell.execute("vfs-info"))
        self.assertIn("directories: 1", lines)
        self.assertIn("files:       2", lines)


class CpTest(unittest.TestCase):
    """Copying files and directories in memory."""

    @cached_property
    def shell(self):
        """Return a fresh shell for every test."""
        return shell_with("deep.xml")

    def run_ok(self, line):
        """Execute ``line`` and check that it succeeds."""
        response = self.shell.execute(line)
        self.assertEqual(texts(response), [])
        self.assertTrue(response.ok)

    def run_error(self, line, message):
        """Execute ``line`` and check the error message."""
        response = self.shell.execute(line)
        self.assertEqual(texts(response), [message])
        self.assertFalse(response.ok)

    def test_copy_file_to_new_name(self):
        self.run_ok("cp readme.txt copy.txt")
        self.assertEqual(
            texts(self.shell.execute("wc copy.txt")), [" 1  3 18 copy.txt"])
        self.assertIn("readme.txt", texts(self.shell.execute("ls")))

    def test_copy_file_into_directory(self):
        self.run_ok("cp readme.txt home/guest")
        self.assertIn("readme.txt", texts(self.shell.execute("ls home/guest")))

    def test_copy_file_into_directory_with_slash(self):
        self.run_ok("cp readme.txt home/guest/")
        self.assertIn("readme.txt", texts(self.shell.execute("ls home/guest")))

    def test_copy_overwrites_existing_file(self):
        self.run_ok("cp readme.txt bin/tool.bin")
        self.assertEqual(
            texts(self.shell.execute("wc -c bin/tool.bin")),
            ["18 bin/tool.bin"])

    def test_copy_several_files_into_directory(self):
        self.run_ok("cp readme.txt home/user/notes.txt bin")
        self.assertEqual(
            texts(self.shell.execute("ls bin")),
            ["notes.txt", "readme.txt", "tool.bin"])

    def test_copy_is_independent_of_the_original(self):
        self.run_ok("cp readme.txt copy.txt")
        self.run_ok("rm readme.txt")
        self.assertEqual(
            texts(self.shell.execute("wc -c copy.txt")), ["18 copy.txt"])

    def test_copy_of_binary_data(self):
        self.run_ok("cp bin/tool.bin tool2.bin")
        self.assertEqual(
            self.shell.resolve("tool2.bin").data,
            self.shell.resolve("bin/tool.bin").data)

    def test_directory_needs_option_r(self):
        self.run_error(
            "cp home/user/docs x",
            "cp: -r not specified; omitting directory 'home/user/docs'")

    def test_copy_directory_recursively(self):
        self.run_ok("cp -r home/user/docs /docs2")
        self.assertEqual(
            texts(self.shell.execute("ls /docs2")), ["drafts", "report.txt"])
        self.assertEqual(
            texts(self.shell.execute("ls /docs2/drafts")), ["idea.txt"])

    def test_copy_directory_into_existing_directory(self):
        self.run_ok("cp -R home/user/docs bin")
        self.assertEqual(
            texts(self.shell.execute("ls bin")), ["docs", "tool.bin"])

    def test_copied_directory_is_independent(self):
        self.run_ok("cp -r home/user/docs /docs2")
        self.run_ok("rm -r home/user/docs")
        self.assertEqual(
            texts(self.shell.execute("ls /docs2/drafts")), ["idea.txt"])

    def test_copied_directory_knows_its_path(self):
        self.run_ok("cp -r home/user/docs /docs2")
        self.shell.execute("cd /docs2/drafts")
        self.assertEqual(self.shell.cwd.path, "/docs2/drafts")

    def test_directory_into_itself(self):
        self.run_error(
            "cp -r home/user home/user/docs",
            "cp: cannot copy a directory, 'home/user', into itself, "
            "'home/user/docs/user'")

    def test_directory_into_new_name_inside_itself(self):
        response = self.shell.execute("cp -r home home/new")
        self.assertFalse(response.ok)

    def test_root_into_itself(self):
        response = self.shell.execute("cp -r / copy")
        self.assertFalse(response.ok)

    def test_same_file(self):
        self.run_error(
            "cp readme.txt readme.txt",
            "cp: 'readme.txt' and 'readme.txt' are the same file")

    def test_directory_over_file(self):
        self.run_error(
            "cp -r home readme.txt",
            "cp: cannot overwrite non-directory 'readme.txt' "
            "with directory 'home'")

    def test_file_into_directory_keeps_its_name(self):
        self.run_ok("cp readme.txt home")
        self.assertIn("readme.txt", texts(self.shell.execute("ls home")))

    def test_file_over_directory(self):
        self.run_ok("cp -r bin home/readme.txt")
        self.run_error(
            "cp readme.txt home",
            "cp: cannot overwrite directory 'home/readme.txt' "
            "with non-directory")

    def test_missing_source(self):
        self.run_error(
            "cp nosuch x",
            "cp: cannot stat 'nosuch': No such file or directory")

    def test_missing_destination_directory(self):
        self.run_error(
            "cp readme.txt nosuch/x",
            "cp: cannot create regular file 'nosuch/x': "
            "No such file or directory")

    def test_destination_through_a_file(self):
        self.run_error(
            "cp readme.txt readme.txt/x",
            "cp: cannot stat 'readme.txt/x': Not a directory")

    def test_several_sources_need_a_directory(self):
        self.run_error(
            "cp readme.txt bin/tool.bin copy.txt",
            "cp: target 'copy.txt' is not a directory")

    def test_missing_operands(self):
        self.run_error("cp", "cp: missing file operand")
        self.run_error(
            "cp a", "cp: missing destination file operand after 'a'")

    def test_invalid_option(self):
        self.run_error("cp -x a b", "cp: invalid option -- 'x'")

    def test_other_sources_are_copied_despite_an_error(self):
        response = self.shell.execute("cp nosuch readme.txt bin")
        self.assertFalse(response.ok)
        self.assertIn("readme.txt", texts(self.shell.execute("ls bin")))


if __name__ == "__main__":
    unittest.main()
