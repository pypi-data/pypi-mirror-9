# This file is part of xrayutilities.
#
# xrayutilities is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2009-2010,2013
#               Eugen Wintersberger <eugen.wintersberger@desy.de>
# Copyright (C) 2009 Mario Keplinger <mario.keplinger@jku.at>
# Copyright (C) 2009-2013 Dominik Kriegner <dominik.kriegner@gmail.com>

import numpy

from . import cxrayutilities
from . import exception
from . import config

from .gridder import Gridder
from .gridder import delta
from .gridder import axis


class Gridder3D(Gridder):

    def __init__(self, nx, ny, nz):
        Gridder.__init__(self)

        # check input
        if nx <= 0 or ny <= 0 or nz <= 0:
            raise exception.InputError('None of nx,ny and nz can be smaller '
                                       'than 1!')

        self.xmin = 0
        self.xmax = 0
        self.ymin = 0
        self.ymax = 0
        self.zmin = 0
        self.zmax = 0

        self.nx = nx
        self.nz = nz
        self.ny = ny

        self._allocate_memory()

    def _allocate_memory(self):
        """
        Class method to allocate memory for the gridder based on the nx,ny
        class attributes.
        """
        self._gdata = numpy.zeros((self.nx, self.ny, self.nz),
                                  dtype=numpy.double)
        self._gnorm = numpy.zeros((self.nx, self.ny, self.nz),
                                  dtype=numpy.double)

    def SetResolution(self, nx, ny, nz):
        self.nx = nx
        self.ny = ny
        self.nz = nz

        self._allocate_memory()

    def __get_xaxis(self):
        return axis(self.xmin, self.xmax, self.nx)

    def __get_yaxis(self):
        return axis(self.ymin, self.ymax, self.ny)

    def __get_zaxis(self):
        return axis(self.zmin, self.zmax, self.nz)

    def __get_xmatrix(self):
        return ones(self.nx, self.ny, self.nz) *\
            self.xaxis[:, numpy.newaxis, numpy.newaxis]

    def __get_ymatrix(self):
        return ones(self.nx, self.ny, self.nz) *\
            self.yaxis[numpy.newaxis, :, numpy.newaxis]

    def __get_zmatrix(self):
        return ones(self.nx, self.ny, self.nz) *\
            self.zaxis[numpy.newaxis, numpy.newaxis, :]

    zaxis = property(__get_zaxis)
    zmatrix = property(__get_zmatrix)
    xaxis = property(__get_xaxis)
    xmatrix = property(__get_xmatrix)
    yaxis = property(__get_yaxis)
    ymatrix = property(__get_ymatrix)

    def dataRange(self, xmin, xmax, ymin, ymax, zmin, zmax, fixed=True):
        """
        define minimum and maximum data range, usually this is deduced
        from the given data automatically, however, for sequential
        gridding it is useful to set this before the first call of the
        gridder. data outside the range are simply ignored

        Parameters
        ----------
         xmin,ymin,zmin:   minimum value of the gridding range in x,y,z
         xmax,ymax,zmax:   maximum value of the gridding range in x,y,z
         fixed: flag to turn fixed range gridding on (True (default))
                or off (False)
        """
        self.fixed_range = fixed
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax

    def __call__(self, x, y, z, data):
        """
        Perform gridding on a set of data. After running the gridder
        the 'data' object in the class is holding the gridded data.

        Parameters
        ----------
        x ............... numpy array of arbitrary shape with x positions
        y ............... numpy array of arbitrary shape with y positions
        z ............... numpy array fo arbitrary shape with z positions
        data ............ numpy array of arbitrary shape with data values
        """

        if not self.keep_data:
            self.Clear()

        if isinstance(x, (list, tuple, numpy.float, numpy.int)):
            x = numpy.array(x)
        if isinstance(y, (list, tuple, numpy.float, numpy.int)):
            y = numpy.array(y)
        if isinstance(z, (list, tuple, numpy.float, numpy.int)):
            z = numpy.array(z)
        if isinstance(data, (list, tuple, numpy.float, numpy.int)):
            data = numpy.array(data)

        x = x.reshape(x.size)
        y = y.reshape(y.size)
        z = z.reshape(z.size)
        data = data.reshape(data.size)

        if x.size != y.size or y.size != z.size or z.size != data.size:
            raise exception.InputError("XU.Gridder3D: size of given datasets "
                                       "(x,y,z,data) is not equal!")

        if not self.fixed_range:
            # assume that with setting keep_data the user wants to call the
            # gridder more often and obtain a reasonable result
            self.dataRange(x.min(), x.max(),
                           y.min(), y.max(),
                           z.min(), z.max(),
                           self.keep_data)

        # remove normalize flag for C-code, normalization is always performed
        # in python
        flags = self.flags ^ 4
        cxrayutilities.gridder3d(x, y, z, data, self.nx, self.ny, self.nz,
                                 self.xmin, self.xmax,
                                 self.ymin, self.ymax,
                                 self.zmin, self.zmax,
                                 self._gdata, self._gnorm, flags)
