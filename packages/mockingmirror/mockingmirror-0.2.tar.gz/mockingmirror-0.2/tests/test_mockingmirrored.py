import unittest
import mockingmirror


class TestMirror(unittest.TestCase):

    @mockingmirror.mirrored
    def test_setup(self, mirror, mock):
        self.assertIs(mirror, self.mirror)
        self.assertIs(mock, self.mock)
        self.assertIs(mirror._mock, mock)
