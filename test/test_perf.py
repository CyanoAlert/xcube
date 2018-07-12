import unittest

from xcube.perf import time_it


class TimeItTest(unittest.TestCase):
    def test_silent(self):
        with time_it(label='test', silent=True) as cm:
            pass
        self.assertEqual('test', cm.label)
        self.assertTrue(cm.delta >= 0.)

    def test_non_silent(self):
        with time_it(label='test', silent=False) as cm:
            pass
        self.assertEqual('test', cm.label)
        self.assertTrue(cm.delta >= 0.)
