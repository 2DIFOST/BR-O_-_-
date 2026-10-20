"""Tests of the in-memory VFS model."""
import unittest

from shellemu.vfs import Directory, File, Vfs, tree_lines


def make_tree():
    """Build /a/b/f.txt, /a/g.bin and /h.txt."""
    root = Directory()
    folder_a = root.add(Directory("a"))
    folder_b = folder_a.add(Directory("b"))
    folder_b.add(File("f.txt", b"12345"))
    folder_a.add(File("g.bin", b"\x00\x01"))
    root.add(File("h.txt"))
    return root


class NodeTest(unittest.TestCase):
    """Paths and sizes of nodes."""

    def test_root_path(self):
        self.assertEqual(Directory().path, "/")

    def test_nested_path(self):
        root = make_tree()
        node = root.children["a"].children["b"].children["f.txt"]
        self.assertEqual(node.path, "/a/b/f.txt")

    def test_file_size_is_number_of_bytes(self):
        self.assertEqual(File("x", "Привет".encode("utf-8")).size, 12)

    def test_add_sets_parent(self):
        root = Directory()
        child = root.add(Directory("d"))
        self.assertIs(child.parent, root)


class VfsTest(unittest.TestCase):
    """Statistics and the tree."""

    def test_empty_vfs(self):
        stats = Vfs().stats()
        self.assertEqual((stats.directories, stats.files), (0, 0))
        self.assertEqual((stats.size, stats.depth), (0, 0))

    def test_stats(self):
        stats = Vfs(make_tree()).stats()
        self.assertEqual(stats.directories, 2)
        self.assertEqual(stats.files, 3)
        self.assertEqual(stats.size, 7)
        self.assertEqual(stats.depth, 3)

    def test_tree_lines(self):
        self.assertEqual(list(tree_lines(make_tree())), [
            "|-- a/",
            "|   |-- b/",
            "|   |   `-- f.txt (5 bytes)",
            "|   `-- g.bin (2 bytes)",
            "`-- h.txt (0 bytes)",
        ])


if __name__ == "__main__":
    unittest.main()
