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
# Copyright (C) 2012 Dominik Kriegner <dominik.kriegner@gmail.com>

import xrayutilities as xu
import numpy

# define elements
In = xu.materials.elements.In
P = xu.materials.elements.P

# define materials
# Si = xu.materials.Si
InP = xu.materials.InP
# InAs = xu.materials.InAs

# hexagonal polytypes
ainp = 5.8687
InP_WZ = xu.materials.Material(
    "InP(wz)", xu.materials.WurtziteLattice(In, P, ainp / numpy.sqrt(2),
                                            numpy.sqrt(4 / 3.) * ainp))
InP_4H = xu.materials.Material(
    "InP(4H)", xu.materials.Hexagonal4HLattice(In, P, ainp / numpy.sqrt(2),
                                               2 * numpy.sqrt(4 / 3.) * ainp))

for energy in [8041]:  # eV

    lam = xu.en2lam(energy)  # e in eV -> lam in Angstroem
    print('         %d eV = %8.4f A' % (energy, lam))
    print('------------------------------------------------------------------'
          '-----------------')
    print('material |         peak    |   omega  |  2theta  |    phi   |   '
          'tt-om  |     |F|   ')
    print('------------------------------------------------------------------'
          '-----------------')

    exp111 = xu.HXRD(InP.Q(1, 1, -2), InP.Q(1, 1, 1), en=energy)
    exphex = xu.HXRD(InP_WZ.Q(1, -1, 0), InP_WZ.Q(0, 0, 1), en=energy)

    # InP ZB reflections
    reflections = [[1, 1, 1], [2, 2, 2], [3, 3, 3],
                   [3, 3, 1], [2, 2, 4], [1, 1, 5]]
    mat = InP
    for hkl in reflections:
        qvec = mat.Q(hkl)
        [om, chi, phi, tt] = exp111.Q2Ang(qvec, trans=True)
        F = mat.StructureFactor(qvec, exp111._en)
        F /= mat.lattice.UnitCellVolume()
        print('%8s | %15s | %8.4f | %8.4f | %8.4f | %8.4f | %8.2f '
              % (mat.name, ' '.join(map(str, numpy.round(hkl, 2))), om, tt,
                 phi, tt - om, numpy.abs(F)))

    print('------------------------------------------------------------------'
          '-----------------')
    # InP WZ reflections
    reflections = [[0, 0, 2], [0, 0, 4], [1, -1, 4], [1, -1, 5], [1, -1, 6]]
    mat = InP_WZ
    for hkl in reflections:
        qvec = mat.Q(hkl)
        [om, chi, phi, tt] = exphex.Q2Ang(qvec, trans=True)
        F = mat.StructureFactor(qvec, exphex._en)
        F /= mat.lattice.UnitCellVolume()
        print('%8s | %15s | %8.4f | %8.4f | %8.4f | %8.4f | %8.2f '
              % (mat.name, ' '.join(map(str, numpy.round(hkl, 2))), om, tt,
                 phi, tt - om, numpy.abs(F)))

    print('------------------------------------------------------------------'
          '-----------------')
    # InP 4H
    reflections = [[0, 0, 4], [0, 0, 8], [1, -1, 9], [1, -1, 10], [1, -1, 11]]
    mat = InP_4H
    for hkl in reflections:
        qvec = mat.Q(hkl)
        [om, chi, phi, tt] = exphex.Q2Ang(qvec, trans=True)
        F = mat.StructureFactor(qvec, exphex._en)
        F /= mat.lattice.UnitCellVolume()
        print('%8s | %15s | %8.4f | %8.4f | %8.4f | %8.4f | %8.2f '
              % (mat.name, ' '.join(map(str, numpy.round(hkl, 2))), om, tt,
                 phi, tt - om, numpy.abs(F)))

    print('------------------------------------------------------------------'
          '-----------------')
