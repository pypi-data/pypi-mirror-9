import os
import unittest

from mockie.test_case import TestCase as MockerTestCase


class TestCaseTests(MockerTestCase):

    def test_patch_replaces_object_with_a_magic_mock(self):
        mock_remove = self.patch("os.remove")
        self.assertIsMock(mock_remove)
        self.assertIsMock(os.remove)

    def test_patch_multiple_object_with_a_magic_mock(self):
        mock_dict = self.patch_multiple(
            "os", remove=self.MagicMock, listdir=self.MagicMock)
        self.assertIsInstance(mock_dict, dict)

    def test_patch_object_replaces_mocked_with_a_magic_mock(self):
        class Tester(object):
            def func(self):
                pass
        tester = Tester()
        mock_tester_func = self.patch_object(tester, "func")
        self.assertIsMocked(mock_tester_func)
        self.assertIsMagicMock(mock_tester_func)

    def test_patch_dict_replaces_dict_with_a_magic_mock(self):
        class Tester(object):
            def __init__(self):
                self.dictionary = {}
        tester = Tester()
        self.patch_dict(tester.dictionary, {"name": "testing"})
        self.assertIn("name", tester.dictionary)

    def test_assert_called_once_with(self):
        mock_remove = self.patch("os.remove")
        path = "/path/to/file"
        mock_remove(path)
        self.assertCalledOnceWith(mock_remove, path)
        self.assertEqual(mock_remove.call_count, 1)
        self.assertCalled(mock_remove)

    def test_assert_any_call_with(self):
        mock_remove = self.patch("os.remove")
        path = "/path/to/file"
        mock_remove(path)
        self.assertAnyCallWith(mock_remove, path)


if __name__ == "__main__":
    unittest.main()
