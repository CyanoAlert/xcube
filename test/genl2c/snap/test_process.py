import os
import unittest

from test.genl2c.snap.helpers import get_inputdata_file, get_inputdata_files
from xcube.genl2c.process import process_inputs
from xcube.io import rimraf


class SnapProcessTest(unittest.TestCase):
    # noinspection PyMethodMayBeStatic
    def test_process_inputs_single(self):
        path, status = process_inputs_wrapper(input=[get_inputdata_file('O_L2_0001_SNS_2017105100139_v1.0.nc')],
                                              name='l2c-single',
                                              format='netcdf4',
                                              append=False)
        self.assertEqual(True, status)
        self.assertEqual(os.path.join('.', 'l2c-single.nc'), path)
        rimraf(os.path.join('.', 'l2c-single.nc'))

    def test_process_inputs_append_multiple_nc(self):
        path, status = process_inputs_wrapper(input=[get_inputdata_file('O_L2_0001_SNS_*_v1.0.nc')],
                                              name='l2c',
                                              format='netcdf4',
                                              append=True)
        self.assertEqual(True, status)
        self.assertEqual(os.path.join('.', 'l2c.nc'), path)
        rimraf(os.path.join('.', 'l2c.nc'))

    def test_process_inputs_append_multiple_zarr(self):
        path, status = process_inputs_wrapper(input=[get_inputdata_file('O_L2_0001_SNS_*_v1.0.nc')],
                                              name='l2c',
                                              format='zarr',
                                              append=True)
        self.assertEqual(True, status)
        self.assertEqual(os.path.join('.', 'l2c.zarr'), path)
        rimraf(os.path.join('.', 'l2c.zarr'))



# noinspection PyShadowingBuiltins
def process_inputs_wrapper(input=None, name=None, format='netcdf4', append=False):
    return process_inputs(input,
                          'snap-olci-highroc-l2',
                          (2000, 1000),
                          (0., 50., 5., 52.5),
                          {'conc_chl', 'conc_tsm', 'kd489', 'c2rcc_flags', 'quality_flags'},
                          None,
                          '.',
                          name,
                          output_format=format,
                          append=append, dry_run=False, monitor=None)