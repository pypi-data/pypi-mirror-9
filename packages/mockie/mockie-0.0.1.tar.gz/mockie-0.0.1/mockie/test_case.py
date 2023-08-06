import unittest
try:
    from unittest.mock import Mock, patch, mock_open, MagicMock
except ImportError:
    from mock import Mock, patch, mock_open, MagicMock


class TestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.mock_open = mock_open
        self.Mock = Mock
        self.MagicMock = MagicMock

        super(TestCase, self).__init__(*args, **kwargs)

    def patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def patch_object(self, *args, **kwargs):
        patcher = patch.object(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def patch_multiple(self, *args, **kwargs):
        patcher = patch.multiple(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def patch_dict(self, *args, **kwargs):
        patcher = patch.dict(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def assertCalledOnceWith(self, mock_obj, *args, **kwargs):
        mock_obj.assert_called_once_with(*args, **kwargs)

    def assertAnyCallWith(self, mock_obj, *args, **kwargs):
        mock_obj.assert_any_call(*args, **kwargs)

    def assertCalled(self, mock_obj):
        self.assertTrue(mock_obj.called)

    def assertIsMock(self, mock_obj):
        self.assertIsInstance(mock_obj, Mock)

    def assertIsMagicMock(self, mock_obj):
        self.assertIsInstance(mock_obj, MagicMock)

    def assertIsMocked(self, mock_obj):
        self.assertIsInstance(mock_obj, (Mock, MagicMock))
