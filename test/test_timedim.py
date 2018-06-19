import unittest

import numpy as np
# noinspection PyUnresolvedReferences
from matplotlib import pyplot as plt

from test.sampledata import create_highroc_dataset
from xcube.timedim import add_time_coords, get_time_in_days_since_1970

nan = np.nan


class TimeDimTest(unittest.TestCase):

    def test_add_time_coords_point(self):
        dataset = create_highroc_dataset()
        dataset_with_time = add_time_coords(dataset, (365 * 47 + 20, 365 * 47 + 20))
        self.assertIsNot(dataset_with_time, dataset)
        self.assertIn('time', dataset_with_time)
        self.assertEqual(dataset_with_time.time.shape, (1,))
        self.assertNotIn('time_bnds', dataset_with_time)

    def test_add_time_coords_range(self):
        dataset = create_highroc_dataset()
        dataset_with_time = add_time_coords(dataset, (365 * 47 + 20, 365 * 47 + 21))
        self.assertIsNot(dataset_with_time, dataset)
        self.assertIn('time', dataset_with_time)
        self.assertEqual(dataset_with_time.time.shape, (1,))
        self.assertIn('time_bnds', dataset_with_time)
        self.assertEqual(dataset_with_time.time_bnds.shape, (1, 2))

    def test_get_time_in_days_since_1970(self):
        self.assertEqual(17324.5, get_time_in_days_since_1970('201706071200'))
        self.assertEqual(17325.5, get_time_in_days_since_1970('201706081200'))
        self.assertEqual(17690.5, get_time_in_days_since_1970('2018-06-08 12:00'))
        self.assertEqual(17690.5, get_time_in_days_since_1970('2018-06-08T12:00'))