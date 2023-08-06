# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 fileencoding=utf-8
#
# MDAnalysis --- http://mdanalysis.googlecode.com
# Copyright (c) 2006-2015 Naveen Michaud-Agrawal, Elizabeth J. Denning, Oliver Beckstein
# and contributors (see AUTHORS for the full list)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#

"""
GRO file format --- :mod:`MDAnalysis.coordinates.GRO`
======================================================

Classes to read and write Gromacs_ GRO_ coordinate files; see the notes on the
`GRO format`_ which includes a conversion routine for the box.

.. _Gromacs: http://www.gromacs.org
.. _GRO: http://manual.gromacs.org/current/online/gro.html
.. _GRO format: http://chembytes.wikidot.com/g-grofile
"""

import os
import errno
import warnings

import numpy

import MDAnalysis
import base
import MDAnalysis.core.util as util
from MDAnalysis.coordinates.core import triclinic_box, triclinic_vectors

from copy import deepcopy


class Timestep(base.Timestep):
    _ts_order_x = [0, 3, 4]
    _ts_order_y = [5, 1, 6]
    _ts_order_z = [7, 8, 2]

    def _init_unitcell(self):
        return numpy.zeros(9, dtype=numpy.float32)

    @property
    def dimensions(self):
        """unitcell dimensions (A, B, C, alpha, beta, gamma)

        GRO::

          8.00170   8.00170   5.65806   0.00000   0.00000   0.00000   0.00000   4.00085   4.00085

        PDB::

          CRYST1   80.017   80.017   80.017  60.00  60.00  90.00 P 1           1

        XTC: c.trajectory.ts._unitcell::

          array([[ 80.00515747,   0.        ,   0.        ],
                 [  0.        ,  80.00515747,   0.        ],
                 [ 40.00257874,  40.00257874,  56.57218552]], dtype=float32)
        """
        # unit cell line (from http://manual.gromacs.org/current/online/gro.html)
        # v1(x) v2(y) v3(z) v1(y) v1(z) v2(x) v2(z) v3(x) v3(y)
        # 0     1     2      3     4     5     6    7     8
        # This information now stored as _ts_order_x/y/z to keep DRY
        x = self._unitcell[self._ts_order_x]
        y = self._unitcell[self._ts_order_y]
        z = self._unitcell[self._ts_order_z]  # this ordering is correct! (checked it, OB)
        return triclinic_box(x, y, z)

    @dimensions.setter
    def dimensions(self, box):
        x, y, z = triclinic_vectors(box)
        numpy.put(self._unitcell, self._ts_order_x, x)
        numpy.put(self._unitcell, self._ts_order_y, y)
        numpy.put(self._unitcell, self._ts_order_z, z)


class GROReader(base.Reader):
    '''Now reads in velocities as well, if available.'''
    format = 'GRO'
    units = {'time': None, 'length': 'nm', 'velocity': 'nm/ps'}
    _Timestep = Timestep

    def __init__(self, grofilename, convert_units=None, **kwargs):
        self.grofilename = grofilename
        self.filename = self.grofilename
        if convert_units is None:
            convert_units = MDAnalysis.core.flags['convert_lengths']
        self.convert_units = convert_units  # convert length and time to base units

        coords_list = []
        velocities_list = []

        with util.openany(grofilename, 'r') as grofile:
            # Read first two lines to get number of atoms
            grofile.readline()
            total_atnums = int(grofile.readline())
            # and the third line to get the spacing between coords (cs) (dependent upon the GRO file precision)
            cs = grofile.readline()[25:].find('.') + 1
            grofile.seek(0)
            for linenum, line in enumerate(grofile):
                # Should work with any precision
                if linenum not in (0, 1, total_atnums + 2):
                    coords_list.append(
                        numpy.array((
                            float(line[20:20 + cs]),
                            float(line[20 + cs:20 + (cs * 2)]),
                            float(line[20 + (cs * 2):20 + (cs * 3)]))))
                    if line[20:].count('.') > 3:  # if there are enough decimals to indicate the presence of velocities
                        velocities_list.append(
                            numpy.array((
                                float(line[20 + (cs * 3):20 + (cs * 4)]),
                                float(line[20 + (cs * 4):20 + (cs * 5)]),
                                float(line[20 + (cs * 5):20 + (cs * 6)]))))
                # Unit cell footer
                elif linenum == total_atnums + 2:
                    unitcell = numpy.array(map(float, line.split()))

        self.numatoms = len(coords_list)
        coords_list = numpy.array(coords_list)
        self.ts = self._Timestep(coords_list)
        self.ts.frame = 1  # 1-based frame number
        if velocities_list:  # perform this operation only if velocities are present in coord file
            # TODO: use a Timestep that knows about velocities such as TRR.Timestep or better, TRJ.Timestep
            self.ts._velocities = numpy.array(velocities_list, dtype=numpy.float32)
            self.convert_velocities_from_native(self.ts._velocities)  # converts nm/ps to A/ps units
        # ts._unitcell layout is format dependent; Timestep.dimensions does the conversion
        # behind the scene
        self.ts._unitcell = numpy.zeros(9, dtype=numpy.float32)  # GRO has 9 entries
        if len(unitcell) == 3:
            # special case: a b c --> (a 0 0) (b 0 0) (c 0 0)
            # see Timestep.dimensions() above for format (!)
            self.ts._unitcell[:3] = unitcell
        elif len(unitcell) == 9:
            self.ts._unitcell[:] = unitcell  # fill all
        else:  # or maybe raise an error for wrong format??
            import warnings

            warnings.warn("GRO unitcell has neither 3 nor 9 entries --- might be wrong.")
            self.ts._unitcell[:len(unitcell)] = unitcell  # fill linearly ... not sure about this
        if self.convert_units:
            self.convert_pos_from_native(self.ts._pos)  # in-place !
            self.convert_pos_from_native(self.ts._unitcell)  # in-place ! (all are lengths)
        self.numframes = 1
        self.fixed = 0
        self.skip = 1
        self.periodic = False
        self.delta = 0
        self.skip_timestep = 1

    def Writer(self, filename, **kwargs):
        """Returns a CRDWriter for *filename*.

        :Arguments:
          *filename*
            filename of the output GRO file

        :Returns: :class:`GROWriter`

        """
        return GROWriter(filename, **kwargs)

    def __iter__(self):
        yield self.ts  # Just a single frame
        raise StopIteration

    def _read_frame(self, frame):
        if frame != 0:
            raise IndexError("GROReader only handles a single frame at frame index 0")
        return self.ts

    def _read_next_timestep(self):
        # CRD files only contain a single frame
        raise IOError


class GROWriter(base.Writer):
    """GRO Writer that conforms to the Trajectory API.

    .. Note::

       The precision is hard coded to three decimal places and
       velocities are not written (yet).
    """

    format = 'GRO'
    units = {'time': None, 'length': 'nm'}
    gro_coor_limits = {'min': -999.9995, 'max': 9999.9995}

    #: format strings for the GRO file (all include newline); precision
    #: of 3 decimal places is hard-coded here.
    fmt = {
        'numatoms': "%5d\n",  # number of atoms
        # coordinates output format, see http://chembytes.wikidot.com/g-grofile
        'xyz_v': "%5s%-5s%5s%5s%8.3f%8.3f%8.3f%8.4f%8.4f%8.4f\n",  # coordinates and velocities
        'xyz': "%5s%-5s%5s%5s%8.3f%8.3f%8.3f\n",  # coordinates only
        # unitcell
        'box_orthorhombic': "%10.5f%10.5f%10.5f\n",
        'box_triclinic': "%10.5f%10.5f%10.5f%10.5f%10.5f%10.5f%10.5f%10.5f%10.5f\n",
    }

    def __init__(self, filename, convert_units=None, **kwargs):
        """Set up a GROWriter with a precision of 3 decimal places.

        :Arguments:
           *filename*
              output filename
        """
        self.filename = util.filename(filename, ext='gro')

        if convert_units is None:
            convert_units = MDAnalysis.core.flags['convert_lengths']
        self.convert_units = convert_units  # convert length and time to base units

    def convert_dimensions_to_unitcell(self, ts):
        """Read dimensions from timestep *ts* and return appropriate unitcell"""
        return self.convert_pos_to_native(triclinic_vectors(ts.dimensions))

    def write(self, selection, frame=None):
        """Write selection at current trajectory frame to file.

        :Arguments:
          selection
              MDAnalysis AtomGroup (selection or Universe.atoms)
              or also Universe
        :Keywords:
          frame
              optionally move to frame number *frame*

        The GRO format only allows 5 digits for resid and atom
        number. If these number become larger than 99,999 then this
        routine will chop off the leading digits.

        .. versionchanged:: 0.7.6
           resName and atomName are truncated to a maximum of 5 characters
        """
        # write() method that complies with the Trajectory API
        u = selection.universe
        if frame is not None:
            u.trajectory[frame]  # advance to frame
        else:
            try:
                frame = u.trajectory.ts.frame
            except AttributeError:
                frame = 1  # should catch cases when we are analyzing a single GRO (?)

        atoms = selection.atoms  # make sure to use atoms (Issue 46)
        coordinates = atoms.coordinates()  # can write from selection == Universe (Issue 49)
        if self.convert_units:
            # Convert back to nm from Angstroms, inplace because coordinates is already a copy
            self.convert_pos_to_native(coordinates)
        # check if any coordinates are illegal (checks the coordinates in native nm!)
        if not self.has_valid_coordinates(self.gro_coor_limits, coordinates):
            raise ValueError("GRO files must have coordinate values between %.3f and %.3f nm:"
                             "No file was written." %
                             (self.gro_coor_limits["min"], self.gro_coor_limits["max"]))

        with util.openany(self.filename, 'w') as output_gro:
            # Header
            output_gro.write('Written by MDAnalysis\n')
            output_gro.write(self.fmt['numatoms'] % len(atoms))
            # Atom descriptions and coords
            for atom_index, atom in enumerate(atoms):
                c = coordinates[atom_index]
                output_line = self.fmt['xyz'] % (
                    str(atom.resid)[-5:],  # truncate highest digits on overflow
                    atom.resname.strip()[:5],
                    atom.name.strip()[:5],
                    str(atom.number + 1)[-5:],  # number (1-based), truncate highest digits on overflow
                    c[0], c[1], c[2],  # coords - outputted with 3 d.p.
                )
                output_gro.write(output_line)

            # Footer: box dimensions
            box = self.convert_dimensions_to_unitcell(u.trajectory.ts)
            if numpy.all(u.trajectory.ts.dimensions[3:] == [90., 90., 90.]):
                # orthorhombic cell, only lengths along axes needed in gro
                output_gro.write(self.fmt['box_orthorhombic'] % (box[0, 0], box[1, 1], box[2, 2]))
            else:
                # full output
                output_gro.write(self.fmt['box_triclinic'] %
                                 (box[0, 0], box[1, 1], box[2, 2],
                                 box[0, 1], box[0, 2],
                                 box[1, 0], box[1, 2],
                                 box[2, 0], box[2, 1]))
