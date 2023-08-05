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
# Copyright (C) 2013-2014 Dominik Kriegner <dominik.kriegner@gmail.com>


"""
class for reading data+header information from tty08 data files

tty08 is system used at beamline P08 at Hasylab Hamburg and creates simple
ASCII files to save the data. Information is easily read from the multicolumn
data file.  the functions below enable also to parse the information of the
header
"""

import re
import numpy
import os
import matplotlib

# relative imports from xrayutilities
from .helper import xu_open
from .. import config
from ..exception import InputError

re_columns = re.compile(r"/\*H")
re_command = re.compile(r"^/\*C command")
re_comment = re.compile(r"^/\*")
re_date = re.compile(r"^/\*D date")
re_epoch = re.compile(r"^/\*T epoch")
re_initmopo = re.compile(r"^/\*M")


class tty08File(object):

    """
    Represents a tty08 data file. The file is read during the
    Constructor call. This class should work for data stored at
    beamline P08 using the tty08 acquisition system.

    Required constructor arguments:
    ------------------------------
     filename:  a string with the name of the tty08-file

    Optional keyword arguments:
    --------------------------
     mcadir .................. directory name of MCA files

    """

    def __init__(self, filename, path=None, mcadir=None):
        self.filename = filename
        if path is None:
            self.full_filename = self.filename
        else:
            self.full_filename = os.path.join(path, self.filename)

        self.Read()

        if mcadir is not None:
            self.mca_directory = mcadir
            self.mca_files = sorted(glob.glob(
                os.path.join(self.mca_directory, '*')))

            if len(self.mca_files):
                self.ReadMCA()

    def ReadMCA(self):

        mca = numpy.empty((len(raws), numpy.loadtxt(raws[0]).shape[0]),
                          dtype=numpy.float)
        for i in range(len(raws)):
            mca[i, :] = numpy.loadtxt(self.mca_files[i])[:, 1]

            fname = self.mca_file_template % i
            data = numpy.loadtxt(fname)

            if i == self.mca_start_index:
                if len(data.shape) == 2:
                    self.mca_channels = data[:, 0]
                else:
                    self.mca_channels = numpy.arange(0, data.shape[0])

            if len(data.shape) == 2:
                dlist.append(data[:, 1].tolist())
            else:
                dlist.append(data.tolist())

        self.mca = mca
        self.data = matplotlib.mlab.rec_append_fields(
            self.data, 'MCA', self.mca,
            dtypes=[(numpy.double, self.mca.shape[1])])

    def Read(self):
        """
        Read the data from the file
        """

        with xu_open(self.full_filename) as fid:
            # read header
            self.init_mopo = {}
            while True:
                line = fid.readline().decode('ascii')
                # if DEGUG: print line
                if not line:
                    break

                if re_command.match(line):
                    m = line.split(':')
                    self.scan_command = m[1].strip()
                if re_date.match(line):
                    m = line.split(':', 1)
                    self.scan_date = m[1].strip()
                if re_epoch.match(line):
                    m = line.split(':', 1)
                    self.epoch = float(m[1])
                if re_initmopo.match(line):
                    m = line[3:]
                    m = m.split(';')
                    for e in m:
                        e = e.split('=')
                        self.init_mopo[e[0].strip()] = float(e[1])

                if re_columns.match(line):
                    self.columns = tuple(line.split()[1:])
                    # here all necessary information is read and we can start
                    # reading the data
                    break
            self.data = numpy.loadtxt(fid, comments="/")

        self.data = numpy.rec.fromrecords(self.data, names=self.columns)


def gettty08_scan(scanname, scannumbers, *args):
    """
    function to obtain the angular cooridinates as well as intensity values
    saved in TTY08 datafiles. Especially usefull for reciprocal space map
    measurements, and to combine date from several scans

    further more it is possible to obtain even more positions from
    the data file if more than two string arguments with its names are given

    Parameters
    ----------
     scanname:  name of the scans, for multiple scans this needs to be a
                template string
     scannumbers:  number of the scans of the reciprocal space map (int,tuple
                   or list)

     *args:   names of the motors (optional) (strings)
     to read reciprocal space maps measured in coplanar diffraction give:
     omname:  e.g. name of the omega motor (or its equivalent)
     ttname:  e.g. name of the two theta motor (or its equivalent)

    Returns
    -------
     MAP

     or

     [ang1,ang2,...],MAP:
                angular positions of the center channel of the position
                sensitive detector (numpy.ndarray 1D) together with all the
                data values as stored in the data file (includes the
                intensities e.g. MAP['MCA']).

    Example
    -------
    >>> [om,tt],MAP = xu.io.gettty08_scan('text%05d.dat',36,'omega','gamma')
    """

    if isinstance(scannumbers, (list, tuple)):
        scanlist = scannumbers
    else:
        scanlist = list([scannumbers])

    angles = dict.fromkeys(args)
    for key in angles.keys():
        if not isinstance(key, str):
            raise InputError("*arg values need to be strings with motornames")
        angles[key] = numpy.zeros(0)
    buf = numpy.zeros(0)
    MAP = numpy.zeros(0)

    for nr in scanlist:
        scan = tty08File(scanname % nr)
        sdata = scan.data
        if MAP.dtype == numpy.float64:
            MAP.dtype = sdata.dtype
        # append scan data to MAP, where all data are stored
        MAP = numpy.append(MAP, sdata)
        # check type of scan
        for i in range(len(args)):
            motname = args[i]
            scanlength = len(sdata)
            try:
                buf = sdata[motname]
            except:
                buf = scan.init_mopo[motname] * numpy.ones(scanlength)
            angles[motname] = numpy.concatenate((angles[motname], buf))

    retval = []
    for motname in args:
        # create return values in correct order
        retval.append(angles[motname])

    if len(args) == 0:
        return MAP
    else:
        return retval, MAP
