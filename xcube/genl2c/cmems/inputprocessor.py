# The MIT License (MIT)
# Copyright (c) 2018 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from abc import ABCMeta

import xarray as xr

from ..inputprocessor import InputProcessor, InputInfo
from ...constants import CRS_WKT_EPSG_4326
from ...io import get_default_dataset_io_registry


class CmemsNetcdfInputProcessor(InputProcessor, metaclass=ABCMeta):
    """
    Input processor for SNAP L2 NetCDF inputs.
    """

    @property
    def name(self) -> str:
        # TODO
        return 'cmems'

    @property
    def description(self) -> str:
        # TODO
        return 'CMEMS NetCDF inputs'

    @property
    def ext(self) -> str:
        return 'nc'

    @property
    def input_info(self) -> InputInfo:
        # TODO
        return InputInfo(xy_var_names=('lon', 'lat'),
                         xy_tp_var_names=('TP_longitude', 'TP_latitude'),
                         xy_crs=CRS_WKT_EPSG_4326,
                         time_range_attr_names=('start_date', 'stop_date'))

    def read(self, input_file: str, **kwargs) -> xr.Dataset:
        """ Read CMEMS NetCDF inputs. """
        # TODO
        return xr.open_dataset(input_file, decode_cf=True, decode_coords=True, decode_times=True)

    def pre_reproject(self, dataset: xr.Dataset) -> xr.Dataset:
        """ Do any pre-processing before reprojection. """
        # TODO
        return dataset

    def post_reproject(self, dataset: xr.Dataset) -> xr.Dataset:
        # TODO
        return dataset


def init_plugin():
    """ Register a DatasetIO object: SnapOlciHighrocL2NetcdfInputProcessor() """
    ds_io_registry = get_default_dataset_io_registry()
    ds_io_registry.register(CmemsNetcdfInputProcessor())
