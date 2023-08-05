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
# Copyright (C) 2013 Dominik Kriegner <dominik.kriegner@gmail.com>

# module for handling files stored in the CBF data format

import numpy
import os
import os.path
import gzip
import re

from .. import cxrayutilities
from .. import config

cbf_name_start_num = re.compile(r"^\d")


class CBFFile(object):

    def __init__(self, fname, nxkey="X-Binary-Size-Fastest-Dimension",
                 nykey="X-Binary-Size-Second-Dimension",
                 dtkey="DataType", path=None):
        """
        CBF detector image parser

        required arguments:
        fname ........ name of the CBF file of type .cbf or .cbf.gz

        keyword arguments:
        nxkey ........ name of the header key that holds the number of points
                       in x-direction
        nykey ........ name of the header key that holds the number of points
                       in y-direction
        dtkey ........ name of the header key that holds the datatype for the
                       binary data
        path ......... path to the CBF file
        """

        self.filename = fname
        if path:
            self.full_filename = os.path.join(path, fname)
        else:
            self.full_filename = self.filename

        # evaluate keyword arguments
        self.nxkey = nxkey
        self.nykey = nykey
        self.dtkey = dtkey

        # create attributes for holding data
        self.data = None
        self._open()
        self.ReadData()
        self.fid.close()

    def _open(self):
        """
        open data file for reading
        """
        try:
            if os.path.splitext(self.full_filename)[-1] == '.gz':
                self.fid = gzip.open(self.full_filename, "rb")
            else:
                self.fid = open(self.full_filename, "rb")
        except:
            raise IOError("cannot open file %s" % (self.full_filename))

    def ReadData(self):
        """
        Read the CCD data into the .data object
        this function is called by the initialization
        """
        wasclosed = False
        if self.fid.closed:
            wasclosed = True
            self._open()

        tmp = numpy.fromfile(file=self.fid, dtype="u1").tostring()
        tmp2 = tmp.decode('ascii', 'ignore')
        # read header information
        pos = tmp2.index(self.nxkey + ':') + len(self.nxkey + ':')
        self.xdim = int(tmp2[pos:pos + 6].strip())
        pos = tmp2.index(self.nykey + ':') + len(self.nykey + ':')
        self.ydim = int(tmp2[pos:pos + 6].strip())

        self.data = cxrayutilities.cbfread(tmp, self.xdim, self.ydim)
        self.data.shape = (self.ydim, self.xdim)
        if wasclosed:
            self.fid.close()

    def Save2HDF5(self, h5, group="/", comp=True):
        """
        Saves the data stored in the EDF file in a HDF5 file as a HDF5 array.
        By default the data is stored in the root group of the HDF5 file - this
        can be changed by passing the name of a target group or a path to the
        target group via the "group" keyword argument.

        Parameters
        ----------
         h5 ........ a HDF5 file object

        optional keyword arguments:
         group ..... group where to store the data (default to the root of the
                     file)
         comp ...... activate compression - true by default
        """

        if isinstance(group, str):
            g = h5.getNode(group)
        else:
            g = group

        # create the array name
        ca_name = os.path.split(self.filename)[-1]
        ca_name = os.path.splitext(ca_name)[0]
        # perform a second time for case of .cbf.gz files
        ca_name = os.path.splitext(ca_name)[0]
        ca_name = ca_name.replace("-", "_")
        if cbf_name_start_num.match(ca_name):
            ca_name = "ccd_" + ca_name
        if config.VERBOSITY >= config.INFO_ALL:
            print(ca_name)
        ca_name = ca_name.replace(" ", "_")

        # create the array description
        ca_desc = "CBF CCD data from file %s " % (self.filename)

        # create the Atom for the array
        a = tables.Atom.from_dtype(self.data.dtype)
        f = tables.Filters(complevel=7, complib="zlib", fletcher32=True)
        if comp:
            try:
                ca = h5.createCArray(g, ca_name, a, self.data.shape,
                                     ca_desc, filters=f)
            except:
                h5.removeNode(g, ca_name, recursive=True)
                ca = h5.createCArray(g, ca_name, a, self.data.shape,
                                     ca_desc, filters=f)
        else:
            try:
                ca = h5.createCArray(g, ca_name, a, self.data.shape, ca_desc)
            except:
                h5.removeNode(g, ca_name, recursive=True)
                ca = h5.createCArray(g, ca_name, a, self.data.shape, ca_desc)

        # write the data
        ca[...] = self.data[...]


class CBFDirectory(object):

    """
    Parses a directory for CBF files, which can be stored to a HDF5 file for
    further usage
    """

    def __init__(self, datapath, ext="cbf", **keyargs):
        """
        required arguments:
        datapath ... directory of the CBF file

        optional keyword arguments:
        ext......... extension of the ccd files in the datapath
                     (default: "cbf")

        further keyword arguments are passed to CBFFile
        """

        self.datapath = os.path.normpath(datapath)
        self.extension = ext

        # create list of files to read
        self.files = glob.glob(
            os.path.join(self.datapath, '*.%s' % (self.extension)))

        if len(self.files) == 0:
            print("XU.io.CBFDirectory: no files found in %s" % (self.datapath))
            return

        if config.VERBOSITY >= config.INFO_ALL:
            print("XU.io.CBFDirectory: %d files found in %s"
                  % (len(self.files), self.datapath))

        self.init_keyargs = keyargs

    def Save2HDF5(self, h5, group="", comp=True):
        """
        Saves the data stored in the CBF files in the specified directory in a
        HDF5 file as a HDF5 arrays in a subgroup.  By default the data is
        stored in a group given by the foldername - this can be changed by
        passing the name of a target group or a path to the target group via
        the "group" keyword argument.

        Parameters
        ----------
         h5 ........ a HDF5 file object

        optional keyword arguments:
         group ..... group where to store the data (defaults to
                     pathname if group is empty string)
         comp ...... activate compression - true by default
        """

        if isinstance(group, str):
            if group == "":
                group = os.path.split(self.datapath)[1]
            try:
                g = h5.getNode(h5.root, group)
            except:
                g = h5.createGroup(h5.root, group)
        else:
            g = group

        if "comp" in keyargs:
            compflag = keyargs["comp"]
        else:
            compflag = True

        for infile in self.files:
            # read EDFFile and save to hdf5
            filename = os.path.split(infile)[1]
            e = CBFFile(filename, path=self.datapath, **self.init_keyargs)
            # e.ReadData()
            e.Save2HDF5(h5, group=g)
