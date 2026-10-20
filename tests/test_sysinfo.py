"""Tests of the window title built from real OS data."""
import unittest
from unittest import mock

from shellemu import sysinfo


class SysinfoTest(unittest.TestCase):
    """The title must be built from the real user and host names."""

    def test_title_format(self):
        with mock.patch.object(sysinfo, "get_username", return_value="bob"):
            with mock.patch.object(sysinfo, "get_hostname",
                                   return_value="pc"):
                self.assertEqual(sysinfo.make_title(),
                                 "Эмулятор - [bob@pc]")

    def test_username_fallback(self):
        with mock.patch.object(sysinfo.getpass, "getuser",
                               side_effect=KeyError):
            with mock.patch.dict(sysinfo.os.environ, {"USER": "alice"}):
                self.assertEqual(sysinfo.get_username(), "alice")

    def test_hostname_fallback(self):
        with mock.patch.object(sysinfo.socket, "gethostname",
                               return_value=""):
            self.assertEqual(sysinfo.get_hostname(), sysinfo.DEFAULT_HOST)


if __name__ == "__main__":
    unittest.main()
