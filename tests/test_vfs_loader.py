"""Tests of loading a VFS from XML."""
import os
import unittest

from helpers import EXAMPLE_VFS, TEST_DATA, write_temp
from shellemu.errors import VfsError
from shellemu.vfs import Directory, File
from shellemu.vfs_loader import load_vfs


def load_text(test, xml):
    """Load a VFS described by the ``xml`` string."""
    return load_vfs(write_temp(test, "vfs.xml", xml))


def error_text(test, xml):
    """Return the message of the error raised for ``xml``."""
    path = write_temp(test, "vfs.xml", xml)
    with test.assertRaises(VfsError) as context:
        load_vfs(path)
    return str(context.exception)


class LoadValidTest(unittest.TestCase):
    """Valid files produce the expected structure."""

    def test_empty_root(self):
        vfs = load_text(self, "<vfs/>")
        self.assertEqual(vfs.root.children, {})

    def test_source_is_remembered(self):
        path = write_temp(self, "vfs.xml", "<vfs/>")
        self.assertEqual(load_vfs(path).source, path)

    def test_text_file(self):
        vfs = load_text(self, '<vfs><file name="a">Привет</file></vfs>')
        self.assertEqual(vfs.root.children["a"].data,
                         "Привет".encode("utf-8"))

    def test_empty_file(self):
        vfs = load_text(self, '<vfs><file name="a"/></vfs>')
        self.assertEqual(vfs.root.children["a"].data, b"")

    def test_base64_file(self):
        xml = '<vfs><file name="b" encoding="base64">AAEC/w==</file></vfs>'
        vfs = load_text(self, xml)
        self.assertEqual(vfs.root.children["b"].data, b"\x00\x01\x02\xff")

    def test_base64_with_whitespace(self):
        xml = '<vfs><file name="b" encoding="base64">\n AAEC\n /w==\n' \
              '</file></vfs>'
        vfs = load_text(self, xml)
        self.assertEqual(vfs.root.children["b"].data, b"\x00\x01\x02\xff")

    def test_nested_directories(self):
        xml = ('<vfs><dir name="a"><dir name="b"><file name="c">x</file>'
               '</dir></dir></vfs>')
        vfs = load_text(self, xml)
        folder_b = vfs.root.children["a"].children["b"]
        self.assertIsInstance(folder_b, Directory)
        self.assertIsInstance(folder_b.children["c"], File)
        self.assertEqual(folder_b.children["c"].path, "/a/b/c")

    def test_xml_comments_are_ignored(self):
        vfs = load_text(self, "<vfs><!-- note --><dir name='d'/></vfs>")
        self.assertEqual(list(vfs.root.children), ["d"])

    def test_loading_does_not_change_the_file(self):
        path = write_temp(self, "vfs.xml", '<vfs><file name="a">1</file></vfs>')
        before = os.stat(path).st_mtime_ns, os.listdir(os.path.dirname(path))
        load_vfs(path)
        after = os.stat(path).st_mtime_ns, os.listdir(os.path.dirname(path))
        self.assertEqual(before, after)

    def test_all_examples_are_valid(self):
        for name in os.listdir(EXAMPLE_VFS):
            with self.subTest(name=name):
                load_vfs(os.path.join(EXAMPLE_VFS, name))


class LoadInvalidTest(unittest.TestCase):
    """Errors are reported with the path and the reason."""

    def test_file_not_found(self):
        with self.assertRaises(VfsError) as context:
            load_vfs("/no/such/vfs.xml")
        self.assertIn("cannot load VFS '/no/such/vfs.xml'",
                      str(context.exception))
        self.assertIn("No such file or directory", str(context.exception))

    def test_directory_instead_of_file(self):
        with self.assertRaises(VfsError) as context:
            load_vfs(os.path.dirname(__file__))
        self.assertIn("Is a directory", str(context.exception))

    def test_not_xml(self):
        message = error_text(self, "this is not xml")
        self.assertIn("invalid XML", message)

    def test_unclosed_tag(self):
        self.assertIn("invalid XML", error_text(self, "<vfs><dir name='a'>"))

    def test_wrong_root(self):
        message = error_text(self, "<root/>")
        self.assertIn("root element must be <vfs>, found <root>", message)

    def test_unknown_element(self):
        message = error_text(self, "<vfs><link name='a'/></vfs>")
        self.assertIn("unknown element <link>", message)

    def test_missing_name(self):
        self.assertIn("without a name", error_text(self, "<vfs><dir/></vfs>"))

    def test_invalid_names(self):
        for name in ("a/b", ".", "..", "a b"):
            with self.subTest(name=name):
                xml = f'<vfs><file name="{name}"/></vfs>'
                self.assertIn("invalid name", error_text(self, xml))

    def test_duplicate_names(self):
        xml = '<vfs><dir name="a"/><file name="a"/></vfs>'
        self.assertIn("duplicate name 'a' in '/'", error_text(self, xml))

    def test_bad_base64(self):
        xml = '<vfs><file name="a" encoding="base64">!!!</file></vfs>'
        self.assertIn("invalid base64 data", error_text(self, xml))

    def test_unknown_encoding(self):
        xml = '<vfs><file name="a" encoding="hex">00</file></vfs>'
        self.assertIn("unknown encoding 'hex'", error_text(self, xml))

    def test_file_with_children(self):
        xml = '<vfs><file name="a"><file name="b"/></file></vfs>'
        self.assertIn("must not contain elements", error_text(self, xml))

    def test_text_inside_directory(self):
        xml = '<vfs><dir name="a">oops</dir></vfs>'
        self.assertIn("must not contain text", error_text(self, xml))

    def test_all_bad_data_files_are_rejected(self):
        for name in os.listdir(TEST_DATA):
            with self.subTest(name=name):
                with self.assertRaises(VfsError):
                    load_vfs(os.path.join(TEST_DATA, name))


if __name__ == "__main__":
    unittest.main()
