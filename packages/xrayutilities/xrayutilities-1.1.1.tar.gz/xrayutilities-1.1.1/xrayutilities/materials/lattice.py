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
# Copyright (C) 2009 Eugen Wintersberger <eugen.wintersberger@desy.de>
# Copyright (C) 2009-2010 Dominik Kriegner <dominik.kriegner@gmail.com>

"""
module handling crystal lattice structures
"""

import numpy
from numpy.linalg import norm
import numbers
import atexit
import os.path

from . import __path__
from . import database
from .. import math
from .. import config
from .. import utilities
from ..exception import InputError

_db = database.DataBase(os.path.join(__path__[0], "data", config.DBNAME))
_db.Open()


def _db_cleanup():
    _db.Close()

atexit.register(_db_cleanup)


class Atom(object):

    def __init__(self, name, num):
        self.name = name
        self.num = num
        _db.SetMaterial(self.name)
        self.weight = _db.weight

    def __key__(self):
        """ key function to return the elements number """
        return self.num

    def __lt__(self, other_el):
        """ make elements sortable by their key """
        return self.__key__() < other_el.__key__()

    def f0(self, q):
        _db.SetMaterial(self.name)

        if isinstance(q, numpy.ndarray) or isinstance(q, list):
            d = numpy.zeros((len(q)), dtype=numpy.double)
            for i in range(len(q)):
                d[i] = _db.GetF0(q[i])

            return d
        else:
            return _db.GetF0(q)

    def f1(self, en="config"):
        if en == "config":
            en = utilities.energy(config.ENERGY)

        _db.SetMaterial(self.name)

        if isinstance(en, numpy.ndarray) or isinstance(en, list):
            d = numpy.zeros((len(en)), dtype=numpy.double)
            for i in range(len(en)):
                d[i] = _db.GetF1(utilities.energy(en[i]))

            return d
        else:
            return _db.GetF1(utilities.energy(en))

    def f2(self, en="config"):
        if en == "config":
            en = utilities.energy(config.ENERGY)

        _db.SetMaterial(self.name)

        if isinstance(en, numpy.ndarray) or isinstance(en, list):
            d = numpy.zeros((len(en)), dtype=numpy.double)
            for i in range(len(en)):
                d[i] = _db.GetF2(utilities.energy(en[i]))

            return d
        else:
            return _db.GetF2(utilities.energy(en))

    def f(self, q, en="config"):
        """
        function to calculate the atomic structure factor F

        Parameter
        ---------
         q:     momentum transfer
         en:    energy for which F should be calculated, if omitted the value
                from the xrayutilities configuration is used

        Returns
        -------
         f (float)
        """
        f = self.f0(norm(q)) + self.f1(en) + 1.j * self.f2(en)
        return f

    def __str__(self):
        ostr = self.name
        ostr += " (%2d)" % self.num
        return ostr

    def __repr__(self):
        return self.__str__()


class LatticeBase(list):

    """
    The LatticeBase class implements a container for a set of points that form
    the base of a crystal lattice. An instance of this class can be treated as
    a simple container object.
    """

    def __init__(self, *args, **keyargs):
        list.__init__(self, *args, **keyargs)

    def append(self, atom, pos, occ=1.0, b=0.):
        """
        add new Atom to the lattice base

        Parameter
        ---------
         atom:   atom object to be added
         pos:    position of the atom
         occ:    occupancy (default=1.0)
         b:      b-factor of the atom used as exp(-b*q**2/(4*pi)**2) to reduce
                 the intensity of this atom (only used in case of temp=0 in
                 StructureFactor and chi calculation)
        """
        if not isinstance(atom, Atom):
            raise TypeError("atom must be an instance of class "
                            "xrayutilities.materials.Atom")

        if isinstance(pos, list):
            pos = numpy.array(pos, dtype=numpy.double)
        elif isinstance(pos, numpy.ndarray):
            pos = pos
        else:
            raise TypeError("Atom position must be array or list!")

        list.append(self, (atom, pos, occ, b))

    def __setitem__(self, key, data):
        (atom, pos, occ, b) = data
        if not isinstance(atom, Atom):
            raise TypeError("atom must be an instance of class "
                            "xrayutilities.materials.Atom!")

        if isinstance(pos, list):
            p = numpy.array(pos, dtype=numpy.double)
        elif isinstance(pos, numpy.ndarray):
            p = pos
        else:
            raise TypeError("point must be a list or numpy array of shape (3)")

        if not isinstance(occ, numbers.Number):
            raise TypeError("occupation (occ) must be a numerical value")
        if not isinstance(b, numbers.Number):
            raise TypeError("occupation (occ) must be a numerical value")

        list.__setitem__(self, key, (atom, p, float(occ), float(b)))

    def __str__(self):
        ostr = ""
        for i in range(list.__len__(self)):
            (atom, p, occ, b) = list.__getitem__(self, i)

            ostr += "Base point %i: %s (%f %f %f) occ=%4.2f b=%4.2f\n" % (
                i, atom.__str__(), p[0], p[1], p[2], occ, b)

        return ostr


class Lattice(object):

    """
    class Lattice:
    This object represents a Bravais lattice. A lattice consists of a base and
    unit cell defined by three vectors.
    """

    def __init__(self, a1, a2, a3, base=None):
        if isinstance(a1, list):
            self.a1 = numpy.array(a1, dtype=numpy.double)
        elif isinstance(a1, numpy.ndarray):
            self.a1 = a1
        else:
            raise TypeError("a1 must be a list or a numpy array")

        if isinstance(a2, list):
            self.a2 = numpy.array(a2, dtype=numpy.double)
        elif isinstance(a1, numpy.ndarray):
            self.a2 = a2
        else:
            raise TypeError("a2 must be a list or a numpy array")

        if isinstance(a3, list):
            self.a3 = numpy.array(a3, dtype=numpy.double)
        elif isinstance(a3, numpy.ndarray):
            self.a3 = a3
        else:
            raise TypeError("a3 must be a list or a numpy array")

        if base is not None:
            if not isinstance(base, LatticeBase):
                raise TypeError("lattice base must be an instance of class "
                                "xrayutilities.materials.LatticeBase")
            else:
                self.base = base
        else:
            self.base = None

        m = numpy.transpose(numpy.array([self.a1, self.a2, self.a3]))
        self.transform = math.Transform(m)

    def ApplyStrain(self, eps):
        """
        Applies a certain strain on a lattice. The result is a change
        in the base vectors. The full strain matrix (3x3) needs to be given.
        Note: NO elastic response of the material will be considered!

        requiered input arguments:
         eps .............. a 3x3 matrix independent strain components
        """

        if isinstance(eps, (list, tuple)):
            eps = numpy.array(eps, dtype=numpy.double)
        if eps.shape != (3, 3):
            raise InputError("ApplyStrain needs a 3x3 matrix "
                             "with strain values")

        u1 = (eps * self.a1[numpy.newaxis, :]).sum(axis=1)
        self.a1 = self.a1 + u1
        u2 = (eps * self.a2[numpy.newaxis, :]).sum(axis=1)
        self.a2 = self.a2 + u2
        u3 = (eps * self.a3[numpy.newaxis, :]).sum(axis=1)
        self.a3 = self.a3 + u3

    def ReciprocalLattice(self):
        V = self.UnitCellVolume()
        p = 2. * numpy.pi / V
        b1 = p * numpy.cross(self.a2, self.a3)
        b2 = p * numpy.cross(self.a3, self.a1)
        b3 = p * numpy.cross(self.a1, self.a2)

        return Lattice(b1, b2, b3)

    def UnitCellVolume(self):
        """
        function to calculate the unit cell volume of a lattice (angstrom^3)
        """
        V = numpy.abs(numpy.dot(self.a3, numpy.cross(self.a1, self.a2)))
        return V

    def GetPoint(self, *args):
        """
        determine lattice points with indices given in the argument

        Examples
        --------
        >>> xu.materials.Si.lattice.GetPoint(0,0,4)
        array([  0.     ,   0.     ,  21.72416])

        or

        >>> xu.materials.Si.lattice.GetPoint((1,1,1))
        array([ 5.43104,  5.43104,  5.43104])
        """
        if len(args) < 3:
            args = args[0]
            if len(args) < 3:
                raise InputError("need 3 indices for the lattice point")

        return self.transform(args)

    def __str__(self):
        ostr = ""
        ostr += "a1 = (%f %f %f), %f\n" % (self.a1[0], self.a1[1], self.a1[2],
                                           math.VecNorm(self.a1))
        ostr += "a2 = (%f %f %f), %f\n" % (self.a2[0], self.a2[1], self.a2[2],
                                           math.VecNorm(self.a2))
        ostr += "a3 = (%f %f %f), %f\n" % (self.a3[0], self.a3[1], self.a3[2],
                                           math.VecNorm(self.a3))
        ostr += "alpha = %f, beta = %f, gamma = %f\n" % (
            math.VecAngle(self.a2, self.a3, deg=True),
            math.VecAngle(self.a1, self.a3, deg=True),
            math.VecAngle(self.a1, self.a2, deg=True))

        if self.base:
            ostr += "Lattice base:\n"
            ostr += self.base.__str__()

        return ostr

# some idiom functions to simplify lattice creation


def CubicLattice(a):
    """
    Returns a Lattice object representing a simple cubic lattice.

    required input arguments:
     a ................ lattice parameter

    return value:
     an instance of Lattice class
    """

    return Lattice([a, 0, 0], [0, a, 0], [0, 0, a])


def GeneralPrimitiveLattice(a, b, c, alpha, beta, gamma):

    # create lattice vectors
    ca = numpy.cos(numpy.radians(alpha))
    cb = numpy.cos(numpy.radians(beta))
    cg = numpy.cos(numpy.radians(gamma))
    sa = numpy.sin(numpy.radians(alpha))
    sb = numpy.sin(numpy.radians(beta))
    sg = numpy.sin(numpy.radians(gamma))

    a1 = a * numpy.array([1, 0, 0], dtype=numpy.double)
    a2 = b * numpy.array([cg, sg, 0], dtype=numpy.double)
    a3 = c * numpy.array([
        cb,
        (ca - cb * cg) / sg,
        numpy.sqrt(1 - ca ** 2 - cb ** 2 - cg ** 2 + 2 * ca * cb * cg) / sg],
        dtype=numpy.double)
    l = Lattice(a1, a2, a3)

    return l

# some lattice related functions


def ZincBlendeLattice(aa, ab, a):
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0])
    lb.append(aa, [0.5, 0, 0.5])
    lb.append(aa, [0, 0.5, 0.5])
    lb.append(ab, [0.25, 0.25, 0.25])
    lb.append(ab, [0.75, 0.75, 0.25])
    lb.append(ab, [0.75, 0.25, 0.75])
    lb.append(ab, [0.25, 0.75, 0.75])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, a]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def DiamondLattice(aa, a):
    # Diamond is ZincBlende with two times the same atom
    return ZincBlendeLattice(aa, aa, a)


def FCCLattice(aa, a):
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0])
    lb.append(aa, [0.5, 0, 0.5])
    lb.append(aa, [0, 0.5, 0.5])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, a]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def FCCSharedLattice(aa, ab, occa, occb, a):
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0], occ=occa)
    lb.append(aa, [0.5, 0.5, 0], occ=occa)
    lb.append(aa, [0.5, 0, 0.5], occ=occa)
    lb.append(aa, [0, 0.5, 0.5], occ=occa)
    lb.append(ab, [0, 0, 0], occ=occb)
    lb.append(ab, [0.5, 0.5, 0], occ=occb)
    lb.append(ab, [0.5, 0, 0.5], occ=occb)
    lb.append(ab, [0, 0.5, 0.5], occ=occb)

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, a]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def BCCLattice(aa, a):
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0.5])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, a]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def HCPLattice(aa, a, c):
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [1 / 3., 2 / 3., 0.5])

    # create lattice vectors
    a1 = numpy.array([a, 0., 0.], dtype=numpy.double)
    a2 = numpy.array([-a / 2., numpy.sqrt(3) * a / 2., 0.], dtype=numpy.double)
    a3 = numpy.array([0., 0., c], dtype=numpy.double)

    l = Lattice(a1, a2, a3, base=lb)

    return l


def BCTLattice(aa, a, c):
    # body centered tetragonal lattice
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0.5])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, c]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def RockSaltLattice(aa, ab, a):
    """
    creates the primitive unit cell of a RockSalt structure.
    For the more commonly used cubic reprentation see RockSalt_Cubic_Lattice
    """
    # create lattice base; data from
    # http://cst-www.nrl.navy.mil/lattice/index.html
    if config.VERBOSITY >= config.INFO_LOW:
        print("XU.materials.RockSaltLattice: Warning; "
              "NaCl lattice is not using a cubic lattice structure")
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(ab, [0.5, 0.5, 0.5])

    # create lattice vectors
    a1 = [0, 0.5 * a, 0.5 * a]
    a2 = [0.5 * a, 0, 0.5 * a]
    a3 = [0.5 * a, 0.5 * a, 0]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def RockSalt_Cubic_Lattice(aa, ab, a):
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0])
    lb.append(aa, [0, 0.5, 0.5])
    lb.append(aa, [0.5, 0, 0.5])

    lb.append(ab, [0.5, 0, 0])
    lb.append(ab, [0, 0.5, 0])
    lb.append(ab, [0, 0, 0.5])
    lb.append(ab, [0.5, 0.5, 0.5])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, a]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def CsClLattice(aa, ab, a):
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(ab, [0.5, 0.5, 0.5])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, a]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def RutileLattice(aa, ab, a, c, u):
    # create lattice base; data from
    # http://cst-www.nrl.navy.mil/lattice/index.html
    # P4_2/mmm(136) aa=2a,ab=4f; x \approx 0.305 (VO_2)
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0.5])
    lb.append(ab, [u, u, 0.])
    lb.append(ab, [-u, -u, 0.])
    lb.append(ab, [0.5 + u, 0.5 - u, 0.5])
    lb.append(ab, [0.5 - u, 0.5 + u, 0.5])

    # create lattice vectors
    a1 = [a, 0., 0.]
    a2 = [0., a, 0.]
    a3 = [0., 0., c]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def BaddeleyiteLattice(aa, ab, a, b, c, beta, deg=True):
    # create lattice base; data from
    # http://cst-www.nrl.navy.mil/lattice/index.html
    # P2_1/c(14), aa=4e,ab=2*4e
    lb = LatticeBase()
    lb.append(aa, [0.242, 0.975, 0.025])
    lb.append(aa, [-0.242, 0.975 + 0.5, -0.025 + 0.5])
    lb.append(aa, [-0.242, -0.975, -0.025])
    lb.append(aa, [0.242, -0.975 + 0.5, 0.025 + 0.5])

    lb.append(ab, [0.1, 0.21, 0.20])
    lb.append(ab, [-0.1, 0.21 + 0.5, -0.20 + 0.5])
    lb.append(ab, [-0.1, -0.21, -0.20])
    lb.append(ab, [0.1, -0.21 + 0.5, 0.20 + 0.5])

    lb.append(ab, [0.39, 0.69, 0.29])
    lb.append(ab, [-0.39, 0.69 + 0.5, -0.29 + 0.5])
    lb.append(ab, [-0.39, -0.69, -0.29])
    lb.append(ab, [0.39, -0.69 + 0.5, 0.29 + 0.5])

    # create lattice vectors
    d2r = numpy.pi / 180.
    if deg:
        beta = beta * d2r
    a1 = numpy.array([a, 0., 0.], dtype=numpy.double)
    a2 = numpy.array([0., b, 0.], dtype=numpy.double)
    a3 = numpy.array([c * numpy.cos(beta), 0., c * numpy.sin(beta)],
                     dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def WurtziteLattice(aa, ab, a, c, u=3 / 8., biso=0.):
    # create lattice base: data from laue atlas (hexagonal ZnS)
    # P63mc; aa=4e,ab=4e
    lb = LatticeBase()
    lb.append(aa, [0., 0., 0.], b=biso)
    lb.append(aa, [1 / 3., 2 / 3., 0.5], b=biso)

    lb.append(ab, [0., 0, u], b=biso)
    lb.append(ab, [1 / 3., 2 / 3., u + 0.5], b=biso)

    # create lattice vectors
    a1 = numpy.array([a, 0., 0.], dtype=numpy.double)
    a2 = numpy.array([-a / 2., numpy.sqrt(3) * a / 2., 0.], dtype=numpy.double)
    a3 = numpy.array([0., 0., c], dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def NiAsLattice(aa, ab, a, c, biso=0.):
    # create lattice base: hexagonal NiAs
    # P63mc; aa=2a,ab=2c
    lb = LatticeBase()
    lb.append(aa, [0., 0., 0.], b=biso)
    lb.append(aa, [0., 0., 0.5], b=biso)

    lb.append(ab, [1 / 3., 2 / 3., 0.25], b=biso)
    lb.append(ab, [2 / 3., 1 / 3., 0.75], b=biso)

    # create lattice vectors
    a1 = numpy.array([a, 0., 0.], dtype=numpy.double)
    a2 = numpy.array([-a / 2., numpy.sqrt(3) * a / 2., 0.], dtype=numpy.double)
    a3 = numpy.array([0., 0., c], dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def Hexagonal4HLattice(aa, ab, a, c, u=3 / 16., v1=1 / 4., v2=7 / 16.):
    # create lattice base: data from laue atlas (hexagonal ZnS) + brainwork by
    # B. Mandl and D. Kriegner
    # ABAC
    lb = LatticeBase()
    lb.append(aa, [0., 0., 0.])  # A
    lb.append(aa, [1 / 3., 2 / 3., v1])  # B
    lb.append(aa, [2 / 3., 1 / 3., 0.5])  # C
    lb.append(aa, [1 / 3., 2 / 3., 0.5 + v1])  # B

    lb.append(ab, [0., 0., u])  # A
    lb.append(ab, [1 / 3., 2 / 3., v2])  # B
    lb.append(ab, [2 / 3., 1 / 3., 0.5 + u])  # C
    lb.append(ab, [1 / 3., 2 / 3., 0.5 + v2])  # B

    # create lattice vectors
    a1 = numpy.array([a, 0., 0.], dtype=numpy.double)
    a2 = numpy.array([-a / 2., numpy.sqrt(3) * a / 2., 0.], dtype=numpy.double)
    a3 = numpy.array([0., 0., c], dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def Hexagonal6HLattice(aa, ab, a, c):
    # create lattice base:
    # https://www.ifm.liu.se/semicond/new_page/research/sic/Chapter2.html +
    # brainwork by B. Mandl and D. Kriegner
    # ABCACB
    lb = LatticeBase()
    lb.append(aa, [0., 0., 0.])  # A
    lb.append(aa, [1 / 3., 2 / 3., 1 / 6.])  # B
    lb.append(aa, [2 / 3., 1 / 3., 2 / 6.])  # C
    lb.append(aa, [0., 0., 3 / 6.])  # A
    lb.append(aa, [2 / 3., 1 / 3., 4 / 6.])  # C
    lb.append(aa, [1 / 3., 2 / 3., 5 / 6.])  # B

    lb.append(ab, [0., 0., 0. + 3 / 24.])  # A
    lb.append(ab, [1 / 3., 2 / 3., 1 / 6. + 3 / 24.])  # B
    lb.append(ab, [2 / 3., 1 / 3., 2 / 6. + 3 / 24.])  # C
    lb.append(ab, [0., 0., 3 / 6. + 3 / 24.])  # A
    lb.append(ab, [2 / 3., 1 / 3., 4 / 6. + 3 / 24.])  # C
    lb.append(ab, [1 / 3., 2 / 3., 5 / 6. + 3 / 24.])  # B

    # create lattice vectors
    a1 = numpy.array([a, 0., 0.], dtype=numpy.double)
    a2 = numpy.array([-a / 2., numpy.sqrt(3) * a / 2., 0.], dtype=numpy.double)
    a3 = numpy.array([0., 0., c], dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def TrigonalR3mh(aa, a, c):
    # create Lattice base from american mineralogist: R3mh (166)
    # http://rruff.geo.arizona.edu/AMS/download.php?id=12092.amc&down=amc
    lb = LatticeBase()
    lb.append(aa, [0., 0., 0.23349])
    lb.append(aa, [2 / 3., 1 / 3., 1 / 3. + 0.23349])
    lb.append(aa, [1 / 3., 2 / 3., 2 / 3. + 0.23349])

    # create lattice vectors
    a1 = numpy.array([a, 0., 0.], dtype=numpy.double)
    a2 = numpy.array([a / 2., numpy.sqrt(3) * a / 2., 0.], dtype=numpy.double)
    a3 = numpy.array([0., 0., c], dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def Hexagonal3CLattice(aa, ab, a, c):
    # create lattice base: data from laue atlas (hexagonal ZnS) + brainwork by
    # B. Mandl and D. Kriegner
    lb = LatticeBase()
    lb.append(aa, [0., 0., 0.])
    lb.append(aa, [1 / 3., 2 / 3., 1 / 3.])
    lb.append(aa, [2 / 3., 1 / 3., 2 / 3.])

    lb.append(ab, [0., 0., 0. + 1 / 4.])
    lb.append(ab, [1 / 3., 2 / 3., 1 / 3. + 1 / 4.])
    lb.append(ab, [2 / 3., 1 / 3., 2 / 3. + 1 / 4.])

    # create lattice vectors
    a1 = numpy.array([a, 0., 0.], dtype=numpy.double)
    a2 = numpy.array([-a / 2., numpy.sqrt(3) * a / 2., 0.], dtype=numpy.double)
    a3 = numpy.array([0., 0., c], dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def QuartzLattice(aa, ab, a, b, c):
    # create lattice base: data from american mineralogist 65 (1980) 920-930
    lb = LatticeBase()
    lb.append(aa, [0.4697, 0., 0.])
    lb.append(aa, [0., 0.4697, 2 / 3.])
    lb.append(aa, [-0.4697, -0.4697, 1 / 3.])

    lb.append(ab, [0.4135, 0.2669, 0.1191])
    lb.append(ab, [0.2669, 0.4135, 2 / 3. - 0.1191])
    lb.append(ab, [-0.2669, 0.4135 - 0.2669, 2 / 3. + 0.1191])
    lb.append(ab, [-0.4135, -0.4135 + 0.2669, 1 / 3. - 0.1191])
    lb.append(ab, [-0.4135 + 0.2669, -0.4135, 1 / 3. + 0.1191])
    lb.append(ab, [0.4135 - 0.2669, -0.2669, -0.1191])

    # create lattice vectors alpha=beta=90 gamma=120
    ca = numpy.cos(numpy.radians(90))
    cb = numpy.cos(numpy.radians(90))
    cg = numpy.cos(numpy.radians(120))
    sa = numpy.sin(numpy.radians(90))
    sb = numpy.sin(numpy.radians(90))
    sg = numpy.sin(numpy.radians(120))

    a1 = a * numpy.array([1, 0, 0], dtype=numpy.double)
    a2 = b * numpy.array([cg, sg, 0], dtype=numpy.double)
    a3 = c * numpy.array([
        cb,
        (ca - cb * cg) / sg,
        numpy.sqrt(1 - ca ** 2 - cb ** 2 - cg ** 2 + 2 * ca * cb * cg) / sg],
        dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def TetragonalIndiumLattice(aa, a, c):
    # create lattice base: I4/mmm (139) site symmetry (2a)
    # data from: Journal of less common-metals 7 (1964) 17-22 (see american
    # mineralogist database)
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0.5])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, c]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def TetragonalTinLattice(aa, a, c):
    # create lattice base: I4_1/amd (141) site symmetry (4a)
    # data from: Wykhoff (see american mineralogist database)
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0.5])
    lb.append(aa, [0.0, 0.5, 0.25])
    lb.append(aa, [0.5, 0.0, 0.75])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, c]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def NaumanniteLattice(aa, ab, a, b, c):
    # create lattice base: P 21 21 21
    # data from: american mineralogist
    # http://rruff.geo.arizona.edu/AMS/download.php?id=00261.amc&down=amc
    lb = LatticeBase()
    lb.append(aa, [0.107, 0.369, 0.456])
    lb.append(aa, [0.5 - 0.107, 0.5 + 0.369, 0.5 - 0.456])
    lb.append(aa, [0.5 + 0.107, -0.369, -0.456])
    lb.append(aa, [-0.107, 0.5 - 0.369, 0.5 + 0.456])

    lb.append(aa, [0.728, 0.029, 0.361])
    lb.append(aa, [0.5 - 0.728, 0.5 + 0.029, 0.5 - 0.361])
    lb.append(aa, [0.5 + 0.728, -0.029, -0.361])
    lb.append(aa, [-0.728, 0.5 - 0.029, 0.5 + 0.361])

    lb.append(ab, [0.358, 0.235, 0.149])
    lb.append(ab, [0.5 - 0.358, 0.5 + 0.235, 0.5 - 0.149])
    lb.append(ab, [0.5 + 0.358, -0.235, -0.149])
    lb.append(ab, [-0.358, 0.5 - 0.235, 0.5 + 0.149])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, b, 0]
    a3 = [0, 0, c]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def CubicFm3mBaF2(aa, ab, a):
    # create lattice base: F m 3 m
    # American Mineralogist Database: Frankdicksonite
    lb = LatticeBase()
    lb.append(aa, [0., 0., 0.])
    lb.append(aa, [0., 0.5, 0.5])
    lb.append(aa, [0.5, 0., 0.5])
    lb.append(aa, [0.5, 0.5, 0.])

    lb.append(ab, [0.25, 0.25, 0.25])
    lb.append(ab, [0.25, 0.75, 0.75])
    lb.append(ab, [0.75, 0.25, 0.75])
    lb.append(ab, [0.75, 0.75, 0.25])
    lb.append(ab, [0.25, 0.75, 0.25])
    lb.append(ab, [0.25, 0.25, 0.75])
    lb.append(ab, [0.75, 0.75, 0.75])
    lb.append(ab, [0.75, 0.25, 0.25])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, a]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def CuMnAsLattice(aa, ab, ac, a, b, c):
    # data from:
    # http://www.sciencedirect.com/science/article/pii/S0304885311008900 and
    # private communication X. Marti
    # unique positions of Cu (2a) (0, 0, 0)
    #                     Mn (2c) (0,0.5,0.2840)
    #                     As (2c) (0,0.5,0.6895)
    lb = LatticeBase()
    lb.append(aa, [0, 0, 0])
    lb.append(aa, [0.5, 0.5, 0])
    lb.append(ab, [0, 0.5, 0.2840])
    lb.append(ab, [0.5, 0, 1 - 0.2840])
    lb.append(ac, [0, 0.5, 0.6895])
    lb.append(ac, [0.5, 0, 1 - 0.6895])

    # create lattice vectors
    a1 = [a, 0, 0]
    a2 = [0, b, 0]
    a3 = [0, 0, c]

    l = Lattice(a1, a2, a3, base=lb)

    return l


def PerovskiteTypeRhombohedral(aa, ab, ac, a, ang):
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0., 0., 0.])
    lb.append(ab, [0.5, 0.5, 0.5])
    lb.append(ac, [0.5, 0.5, 0.])
    lb.append(ac, [0., 0.5, 0.5])
    lb.append(ac, [0.5, 0., 0.5])

    ca = numpy.cos(numpy.radians(ang))
    cb = numpy.cos(numpy.radians(ang))
    cg = numpy.cos(numpy.radians(ang))
    sa = numpy.sin(numpy.radians(ang))
    sb = numpy.sin(numpy.radians(ang))
    sg = numpy.sin(numpy.radians(ang))

    a1 = a * numpy.array([1, 0, 0], dtype=numpy.double)
    a2 = a * numpy.array([cg, sg, 0], dtype=numpy.double)
    a3 = a * numpy.array([
        cb,
        (ca - cb * cg) / sg,
        numpy.sqrt(1 - ca ** 2 - cb ** 2 - cg ** 2 + 2 * ca * cb * cg) / sg],
        dtype=numpy.double)
    l = Lattice(a1, a2, a3, base=lb)

    return l


def GeTeRhombohedral(aa, ab, a, ang, x=0.237):
    # create lattice base
    lb = LatticeBase()
    lb.append(aa, [0. - x, 0. - x, 0. - x])
    lb.append(aa, [0.5 - x, 0.5 - x, 0.0 - x])
    lb.append(aa, [0.5 - x, 0. - x, 0.5 - x])
    lb.append(aa, [0.0 - x, 0.5 - x, 0.5 - x])
    lb.append(ab, [0. + x, 0. + x, 0. + x])
    lb.append(ab, [0.5 + x, 0.5 + x, 0.0 + x])
    lb.append(ab, [0.5 + x, 0. + x, 0.5 + x])
    lb.append(ab, [0.0 + x, 0.5 + x, 0.5 + x])

    # create lattice vectors
    ca = numpy.cos(numpy.radians(ang))
    cb = numpy.cos(numpy.radians(ang))
    cg = numpy.cos(numpy.radians(ang))
    sa = numpy.sin(numpy.radians(ang))
    sb = numpy.sin(numpy.radians(ang))
    sg = numpy.sin(numpy.radians(ang))

    a1 = a * numpy.array([1, 0, 0], dtype=numpy.double)
    a2 = a * numpy.array([cg, sg, 0], dtype=numpy.double)
    a3 = a * numpy.array([
        cb,
        (ca - cb * cg) / sg,
        numpy.sqrt(1 - ca ** 2 - cb ** 2 - cg ** 2 + 2 * ca * cb * cg) / sg],
        dtype=numpy.double)

    l = Lattice(a1, a2, a3, base=lb)

    return l


def MagnetiteLattice(aa, ab, ac, a, x=0.255):
    lb = LatticeBase()
    # Fe1
    lb.append(aa, [0.125, 0.125, 0.125])
    lb.append(aa, [0.875, 0.375, 0.375])
    lb.append(aa, [0.375, .875, .375])
    lb.append(aa, [0.375, 0.375, .875])
    lb.append(aa, [.875, .875, .875])
    lb.append(aa, [.125, .625, .625])
    lb.append(aa, [.625, .125, .625])
    lb.append(aa, [.625, .625, .125])
    # Fe2
    lb.append(ab, [0.5, 0.5, 0.5])
    lb.append(ab, [.5, 0.75, 0.75])
    lb.append(ab, [0.75, 0.75, 0.5])
    lb.append(ab, [0.75, 0.5, 0.75])
    lb.append(ab, [0.5, 0.25, .25])
    lb.append(ab, [.25, .25, .5])
    lb.append(ab, [.25, .5, .25])
    lb.append(ab, [.5, 0, 0])
    lb.append(ab, [.75, .25, 0])
    lb.append(ab, [.75, 0, .25])
    lb.append(ab, [.25, .75, 0])
    lb.append(ab, [.25, 0, .75])
    lb.append(ab, [0, .5, 0])
    lb.append(ab, [0, .75, .25])
    lb.append(ab, [0, .25, .75])
    lb.append(ab, [0, 0, .5])
    # O
    lb.append(ac, [x, x, x])
    lb.append(ac, [1 - x, x + 0.25, x + 0.25])
    lb.append(ac, [1 - x + 0.25, 1 - x + 0.25, x])
    lb.append(ac, [x + 0.25, 1 - x, x + 0.25])
    lb.append(ac, [x, 1 - x + 0.25, 1 - x + 0.25])
    lb.append(ac, [x + 0.25, x + 0.25, 1 - x])
    lb.append(ac, [1 - x + 0.25, x, 1 - x + 0.25])
    lb.append(ac, [1 - x, 1 - x, 1 - x])
    lb.append(ac, [x, .75 - x, .75 - x])
    lb.append(ac, [x - .25, x - .25, 1 - x])
    lb.append(ac, [.75 - x, x, .75 - x])
    lb.append(ac, [1 - x, x - .25, x - .25])
    lb.append(ac, [.75 - x, .75 - x, x])
    lb.append(ac, [x - .25, 1 - x, x - .25])
    lb.append(ac, [x, .5 + x, .5 + x])
    lb.append(ac, [1 - x + .25, .25 + x, .5 + x])
    lb.append(ac, [.25 + x, .5 - x, x - .25])
    lb.append(ac, [x + .25, x - .25, .5 - x])
    lb.append(ac, [1 - x + .25, .5 + x, 1 - .25 - x])
    lb.append(ac, [1 - x, .5 - x, .5 - x])
    lb.append(ac, [x - .25, .25 + x, .5 - x])
    lb.append(ac, [.75 - x, .5 + x, 1 - x + .25])
    lb.append(ac, [.75 - x, 1 - x + .25, .5 + x])
    lb.append(ac, [x - .25, .5 - x, .25 + x])
    lb.append(ac, [.5 + x, x, .5 + x])
    lb.append(ac, [.5 - x, .25 + x, x - .25])
    lb.append(ac, [.5 + x, 1 - x + .25, .75 - x])
    lb.append(ac, [.5 - x, 1 - x, .5 - x])
    lb.append(ac, [.5 + x, .75 - x, 1 - x + .25])
    lb.append(ac, [.5 - x, x - .25, x + .25])
    lb.append(ac, [.5 + x, .5 + x, x])
    lb.append(ac, [.5 - x, .5 - x, 1 - x])

    a1 = [a, 0, 0]
    a2 = [0, a, 0]
    a3 = [0, 0, a]
    l = Lattice(a1, a2, a3, base=lb)
    return l
