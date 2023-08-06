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
Coordinate/Trajectory Readers and Writers  --- :mod:`MDAnalysis.coordinates`
============================================================================

The coordinates submodule contains code to read coordinates, either
single frames (e.g. the PDB module) or trajectories (such as the DCD
reader). All readers are supposed to expose a :class:`Reader` object
that presents a common `Trajectory API`_ to other code.

The :class:`~MDAnalysis.core.AtomGroup.Universe` contains the API
entry point attribute

  :attr:`Universe.trajectory`

that points to the actual :class:`~MDAnalysis.coordinates.base.Reader`
object; all Readers are supposed to be accessible through this entry
point in the same manner ("`duck typing`_").

In order to **write coordinates**, a factory function is provided
(:func:`MDAnalysis.coordinates.core.writer`) which is made available
as :func:`MDAnalysis.Writer`) that returns a *Writer* appropriate for
the desired file format (as indicated by the filename
suffix). Furthermore, a trajectory
:class:`~MDAnalysis.coordinates.base.Reader` can also have a method
:meth:`~MDAnalysis.coordinates.base.Reader.Writer` that returns an
appropriate :class:`~MDAnalysis.coordinates.base.Writer` for the file
format of the trajectory.

In analogy to :func:`MDAnalysis.coordinates.core.writer`, there is
also a :func:`MDAnalysis.coordinates.core.reader` function available
to return a trajectory :class:`~MDAnalysis.coordinates.base.Reader`
instance although this is often not needed because the
:class:`~MDAnalysis.core.AtomGroup.Universe` class can choose an
appropriate reader automatically.

.. _duck typing: http://c2.com/cgi/wiki?DuckTyping


Using Readers
-------------

Normally, one does not explicitly need to select a reader. This is handled
automatically when creating a :class:`~MDAnalysis.core.AtomGroup.Universe` and
the appropriate reader for the file type is selected (typically by the file
extension but this choice can be overriden with the ``format`` argument to
:class:`~MDAnalysis.core.AtomGroup.Universe`).

Using Writers
-------------

A typical approach is to generate a new trajectory from an old one, e.g. to
only keep the protein::

  u = MDAnalysis.Universe(PDB, XTC)
  protein = u.selectAtoms("protein")
  with MDAnalysis.Writer("protein.xtc", protein.numberOfAtoms()) as W:
      for ts in u.trajectory:
          W.write(protein)

Using the :func:`with` statement will automatically close the trajectory when
the last frame has been written.


Supported coordinate formats
----------------------------

The table below lists the coordinate file formats understood by MDAnalysis. The
emphasis is on formats that are used in popular molecular dynamics codes. By
default, MDAnalysis figures out formats by looking at the extension. Thus, a
DCD file always has to end with ".dcd" to be recognized as such unless the
format is explicitly specified with the *format* keyword to
:class:`~MDAnalysis.core.AtomGroup.Universe` or
:meth:`~MDAnalysis.core.AtomGroup.Universe.load_new`.  A number of files are
also recognized when they are compressed with :program:`gzip` or
:program:`bzip2` such as ".xyz.bz2".

.. _Supported coordinate formats:

.. table:: Table of Supported coordinate formats

   +---------------+-----------+-------+------------------------------------------------------+
   |Name           | extension |  IO   | remarks                                              |
   +===============+===========+=======+======================================================+
   | CHARMM,       | dcd       |  r/w  | standard CHARMM binary trajectory; endianness is     |
   | NAMD          |           |       | autodetected. Fixed atoms may not be handled         |
   |               |           |       | correctly (requires testing). Module                 |
   |               |           |       | :mod:`MDAnalysis.coordinates.DCD`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | LAMMPS        | dcd       |  r/w  | CHARMM-style binary trajectory; endianness is        |
   |               |           |       | autodetected. Units are appropriate for LAMMPS.      |
   |               |           |       | Module :mod:`MDAnalysis.coordinates.LAMMPS`          |
   +---------------+-----------+-------+------------------------------------------------------+
   | LAMMPS [#a]_  | data      |  r    | Single frame of coordinates read from .data files    |
   +---------------+-----------+-------+------------------------------------------------------+
   | Gromacs       | xtc       |  r/w  | Compressed (lossy) xtc trajectory format. Module     |
   |               |           |       | :mod:`MDAnalysis.coordinates.XTC`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | Gromacs       | trr       |  r/w  | Full precision trr trajectory. Coordinates and       |
   |               |           |       | velocities are processed. Module                     |
   |               |           |       | :mod:`MDAnalysis.coordinates.TRR`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | XYZ [#a]_     |  xyz      |  r/w  | Generic white-space separate XYZ format; can be      |
   |               |           |       | compressed (gzip or bzip2). Module                   |
   |               |           |       | :mod:`MDAnalysis.coordinates.XYZ`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | GAMESS        |  gms,     |  r    | Generic semi-formatted GAMESS output log; can be     |
   |               |  log,     |       | compressed (gzip or bzip2). Module                   |
   |               |  out      |       | :mod:`MDAnalysis.coordinates.GMS`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | AMBER         | trj,      |  r    | formatted (ASCII) trajectories; the presence of a    |
   |               | mdcrd     |       | periodic box is autodetected (*experimental*).       |
   |               |           |       | Module :mod:`MDAnalysis.coordinates.TRJ`             |
   +---------------+-----------+-------+------------------------------------------------------+
   | AMBER         | ncdf      |  r/w  | binary (NetCDF) trajectories are fully supported with|
   |               |           |       | optional `netcdf4-python`_ module (coordinates and   |
   |               |           |       | velocities). Module :mod:`MDAnalysis.coordinates.TRJ`|
   +---------------+-----------+-------+------------------------------------------------------+
   | Brookhaven    | pdb       |  r/w  | a simplified PDB format (as used in MD simulations)  |
   | [#a]_         |           |       | is read by default; the full format can be read by   |
   |               |           |       | supplying the `permissive=False` flag to             |
   |               |           |       | :class:`MDAnalysis.Universe`. Multiple frames (MODEL)|
   |               |           |       | are supported but require the *multiframe* keyword.  |
   |               |           |       | Module :mod:`MDAnalysis.coordinates.PDB`             |
   +---------------+-----------+-------+------------------------------------------------------+
   | XPDB          | pdb       |   r   | Extended PDB format (can use 5-digit residue         |
   |               |           |       | numbers). To use, specify the format "XPBD"          |
   |               |           |       | explicitly: ``Universe(..., format="XPDB")``.        |
   |               |           |       | Module :MDAnalysis.coordinates.PDB`                  |
   +---------------+-----------+-------+------------------------------------------------------+
   | PDBQT [#a]_   | pdbqt     | r/w   | file format used by AutoDock with atom types *t*     |
   |               |           |       | and partial charges *q*. Module:                     |
   |               |           |       | :mod:`MDAnalysis.coordinates.PDBQT`                  |
   +---------------+-----------+-------+------------------------------------------------------+
   | PQR [#a]_     | pqr       | r/w   | PDB-like but whitespace-separated files with charge  |
   |               |           |       | and radius information. Module                       |
   |               |           |       | :mod:`MDAnalysis.coordinates.PQR`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | GROMOS96      | gro       |  r/w  | basic GROMOS96 format (velocities as well). Module   |
   | [#a]_         |           |       | :mod:`MDAnalysis.coordinates.GRO`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | CHARMM [#a]_  | crd       |  r/w  | "CARD" coordinate output from CHARMM; deals with     |
   |               |           |       | either standard or EXTended format. Module           |
   |               |           |       | :mod:`MDAnalysis.coordinates.CRD`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | DESRES [#a]_  | dms       |  r    | DESRES Molecular Structure file format reader.       |
   |               |           |       | Module :mod:`MDAnalysis.coordinates.DMS`             |
   +---------------+-----------+-------+------------------------------------------------------+
   | IBIsCO/YASP   | trz       |  r/w  | Binary IBIsCO or YASP trajectories Module            |
   |               |           |       | :mod:`MDAnalysis.coordinates.TRZ`                    |
   +---------------+-----------+-------+------------------------------------------------------+
   | MOL2          | mol2      |  r/w  | Text-based Tripos molecular structure format         |
   |               |           |       | :mod:`MDAnalysis.coordinates.MOL2`                   |
   +---------------+-----------+-------+------------------------------------------------------+

.. [#a] This format can also be used to provide basic *topology*
   information (i.e. the list of atoms); it is possible to create a
   full :mod:`~MDAnalysis.core.AtomGroup.Universe` by simply
   providing a file of this format: ``u = Universe(filename)``

.. _`netcdf4-python`: http://code.google.com/p/netcdf4-python/

.. _Trajectory API:

Trajectory API
--------------

The **Trajectory API** defines how classes have to be structured that allow
reading and writing of coordinate files. By following the API it is possible to
seamlessly enhance the I/O capabilities of MDAnalysis. The actual underlying
I/O code can be written in C or python or a mixture thereof.

Typically, each format resides in its own module, named by the format specifier
(and using upper case by convention).

Reader and Writer classes are derived from base classes in
:mod:`MDAnalysis.coordinates.base`.


History
~~~~~~~

- 2010-04-30 Draft [orbeckst]
- 2010-08-20 added single frame writers to API [orbeckst]
- 2010-10-09 added write() method to Writers [orbeckst]
- 2010-10-19 use close() instead of close_trajectory() [orbeckst]
- 2010-10-30 clarified Writer write() methods (see also `Issue 49`_)
- 2011-02-01 extended call signatur of Reader class
- 2011-03-30 optional Writer() method for Readers
- 2011-04-18 added time and frame managed attributes to Reader
- 2011-04-20 added volume to Timestep
- 2012-02-11 added _velocities to Timestep
- 2012-05-24 multiframe keyword to distinguish trajectory from single frame writers
- 2012-06-04 missing implementations of Reader.__getitem__ should raise :exc:`TypeError`
- 2013-08-02 Readers/Writers must conform to the Python `Context Manager`_ API
- 2015-01-15 Timestep._init_unitcell() method added

.. _Issue 49: http://code.google.com/p/mdanalysis/issues/detail?id=49
.. _Context Manager: http://docs.python.org/2/reference/datamodel.html#context-managers

Registry
~~~~~~~~

In various places, MDAnalysis tries to automatically select appropriate formats
(e.g. by looking at file extensions). In order to allow it to choose the
correct format, all I/O classes must be registered in one of three dictionaries
with the format (typically the file extension in upper case):

- Trajectory reader classes must be added to
  :data:`MDAnalysis.coordinates._trajectory_readers`.

- Trajectory writer classes must be added to
  :data:`MDAnalysis.coordinates._trajectory_writers`.

- Single-frame writer classes must be added to to
  :data:`MDAnalysis.coordinates._frame_writers`.


Timestep class
~~~~~~~~~~~~~~

A Timestep instance holds data for the current frame. It is updated whenever a
new frame of the trajectory is read.

Timestep classes are derived from
:class:`MDAnalysis.coordinates.base.Timestep`, which is the primary
implementation example (and used directly for the DCDReader).

Methods
.......

  ``__init__(arg)``
      depending on the type of *arg*, Timestep instances are created in
      different ways:

        ``int``
            empty Timestep for *arg* atoms (allocate arrays etc)
        :class:`Timestep`
            makes a deep copy of the *arg*
        :class:`numpy.ndarray`
            update the Timesteps positions array with the contents of *arg*

      Anything else raises an exception; in particular it is not possible to
      create a "empty" :class:`~MDAnalysis.coordinates.base.Timestep` instance.
  ``__getitem__(atoms)``
      position(s) of atoms; can be a slice or numpy array and then returns
      coordinate array
  ``__len__()``
      number of coordinates (atoms) in the frame
  ``__iter__()``
      iterator over all coordinates
  ``copy()``
      deep copy of the instance
  ``_init_unitcell``
      hook that returns empty data structure for the unitcell representation
      of this particular file format; called from within ``__init__()`` to
      initialize :attr:`Timestep._unitcell`.

Attributes
..........

  ``numatoms``
      number of atoms in the frame
  ``frame``
      current frame number (1-based)
  ``dimensions``
      system box dimensions (`x, y, z, alpha, beta, gamma`)
      (typically implemented as a property because it needs to translate whatever is in the
      underlying :class:`~MDAnalysis.coordinates.base.Timestep._unitcell` attribute. Also
      comes with a setter that takes a MDAnalysis box so that one can do ::

          Timestep.dimensions = [A, B, C, alpha, beta, gamma]

      which then converts automatically to the underlying representation and stores it
      in :attr:`Timestep._unitcell`.
  ``volume``
      system box volume (derived as the determinant of the box vectors of ``dimensions``)

Private attributes
..................

These attributes are set directly by the underlying trajectory
readers. Normally the user should not have to directly access those (although in
some cases it is convenient to directly use :class:`~MDAnalysis.coordinates.base.Timestep._pos`).

  ``_pos``
      raw coordinates, a :class:`numpy.float32` array; ``X = _pos[:,0], Y =
      _pos[:,1], Z = _pos[:,2]``

  ``_unitcell``
      native unit cell description; the format depends on the
      underlying trajectory format. A user should use the
      :class:`~MDAnalysis.coordinates.base.Timestep.dimensions`
      attribute to access the data in a canonical format instead of
      accessing :class:`Timestep._unitcell` directly.

      The method :meth:`Timestep._init_unitcell` is a hook to initialize
      this attribute.

Optional attributes (only implemented by some readers); if an optional
attribute does not exist, a :exc:`AttributeError` is raised and the calling
code should handle this gracefully.

  ``_velocities``
      raw velocities, a :class:`numpy.float32` array containing velocities
      (similar to ``_pos``)


Trajectory Reader class
~~~~~~~~~~~~~~~~~~~~~~~

Trajectory readers are derived from :class:`MDAnalysis.coordinates.base.Reader`.
Typically, many methods and attributes are overriden.

Methods
.......

The :class:`MDAnalysis.coordinates.DCD.DCDReader` class is the primary
implementation example.

**Mandatory methods**

The following methods must be implemented in a Reader class.

 ``__init__(filename, **kwargs)``
     open *filename*; other *kwargs* are processed as needed and the
     Reader is free to ignore them. Typically, MDAnalysis supplies as
     much information as possible to the Reader in `kwargs`; at the moment the
     following data are supplied in keywords when a trajectory is loaded from
     within :class:`MDAnalysis.Universe`:

      - *numatoms*: the number of atoms (known from the topology)

 ``__iter__()``
     allow iteration from beginning to end::

        for ts in trajectory:
            print ts.frame

 ``close()``
     close the file and cease I/O
 ``__del__()``
     ensure that the trajectory is closed
 ``next()``
     advance to next time step or raise :exc:`IOError` when moving
     past the last frame
 ``rewind()``
     reposition to first frame
 ``__entry__()``
     entry method of a `Context Manager`_ (returns self)
 ``__exit__()``
     exit method of a `Context Manager`_, should call ``close()``.


**Optional methods**

Not all trajectory formats support the following methods, either because the
data are not available or the methods have not been implemented. Code should
deal with missing methods gracefully.

 ``__len__()``
     number of frames in trajectory

 ``__getitem__(arg)``
     advance to time step `arg` = `frame` and return :class:`Timestep`; or if `arg` is a
     slice, then return an iterator over that part of the trajectory.

     The first functionality allows one to randomly access frames in the
     trajectory::

       universe.trajectory[314]

     would load frame 314 into the current :class:`Timestep`.

     Using slices allows iteration over parts of a trajectory ::

       for ts in universe.trajectory[1000:2000]:
           process_frame(ts)   # do something

     or skipping frames ::

       for ts in universe.trajectory[1000::100]:
           process_frame(ts)   # do something

     The last example starts reading the trajectory at frame 1000 and
     reads every 100th frame until the end.

     The performance of the ``__getitem__()`` method depends on the underlying
     trajectory reader and if it can implement random access to frames. In many
     cases this is not easily (or reliably) implementable and thus one is
     restricted to sequential iteration.

     If the Reader is not able to provide random access to frames then it
     should raise :exc:`TypeError` on indexing. It is possible to partially
     implement ``__getitem__`` (as done on
     :class:`MDAnalysis.coordinates.base.Reader.__getitem__` where slicing the
     full trajectory is equivalent to
     :class:`MDAnalysis.coordinates.base.Reader.__iter__` (which is always
     implemented) and other slices raise :exc:`TypeError`.

     .. Note::

        ``__getitem__`` uses 0-based indices for frames so that indexing and
        slicing works exactly as in Python. However, the ``Timestep.frame``
        attribute (the "frame number") is 1-based. Thus, the first frame in a
        trajectory can be accessed as ``trajectory[0]`` (frame index 0) and the
        corresponding frame number is 1 (``trajectory.ts.frame == 1``).


 ``Writer(filename, **kwargs)``
     returns a :class:`~MDAnalysis.coordinates.base.Writer` which is set up with
     the same parameters as the trajectory that is being read (e.g. time step,
     length etc), which facilitates copying and simple on-the-fly manipulation.

     If no Writer is defined then a :exc:`NotImplementedError` is raised.

     The *kwargs* can be used to customize the Writer as they are typically
     passed through to the init method of the Writer, with sensible defaults
     filled in; the actual keyword arguments depend on the Writer.

 ``timeseries(atomGroup, [start[,stop[,skip[,format]]]])``
     returns a subset of coordinate data

 ``correl(timeseriesCollection[,start[,stop[,skip]]])``
     populate a :class:`MDAnalysis.core.Timeseries.TimeseriesCollection` object
     with observable timeseries computed from the trajectory


Attributes
..........

 ``filename``
     filename of the trajectory
 ``numatoms``
     number of atoms (coordinate sets) in a frame (constant)
 ``numframes``
     total number of frames (if known) -- ``None`` if not known
 ``fixed``
     bool, saying if there are fixed atoms (e.g. dcds)
 ``skip``
     step size for iterating through the trajectory [1]
 ``skip_timestep``
     number of integrator steps between frames + 1 (i.e.
     the stride at which the MD simulation was sampled)
 ``delta``
     integrator time step (in native units); hence the "length"
     of a trajctory frame is  ``skip_timestep*delta`` time units
 ``periodic``
     contains box information for periodic boundary conditions
 ``ts``
     the :class:`~base.Timestep` object; typically customized for each
     trajectory format and derived from :class:`base.Timestep`.
 ``units``
     dictionary with keys *time*, *length*, *speed*, *force* and the
     appropriate unit (e.g. 'AKMA' and 'Angstrom' for Charmm dcds, 'ps' and
     'nm' for Gromacs trajectories, ``None`` and 'Angstrom' for PDB).
     Any field not used should be set to ``None``.
 ``format``
     string that identifies the file format, e.g. "DCD", "PDB", "CRD", "XTC",
     "TRR"; this is typically the file extension in upper case.
 ``dt``
     time between frames in ps; a managed attribute (read only) that computes
     on the fly ``skip_timestep * delta`` and converts to the MDAnalysis base
     unit for time (pico seconds by default)
 ``totaltime``
     total length of the trajectory = ``numframes * dt``
 ``time``
     time of the current time step, in MDAnalysis time units (ps)
 ``frame``
     frame number of the current time step (1-based)

**Optional attributes**

 ``compressed``
     string that identifies the compression (e.g. "gz" or "bz2") or ``None``.


Trajectory Writer class
~~~~~~~~~~~~~~~~~~~~~~~

Trajectory writers are derived from
:class:`MDAnalysis.coordinates.base.Writer`. They are used to write
multiple frames to a trajectory file. Every time the
:meth:`~MDAnalysis.coordinates.base.Writer.write` method is called,
another frame is appended to the trajectory.

Typically, many methods and attributes are overriden.

Signature::

   W = TrajectoryWriter(filename,numatoms,**kwargs)
   W.write_next_timestep(Timestep)

or::

   W.write(AtomGroup)   # write a selection
   W.write(Universe)    # write a whole universe
   W.write(Timestep)    # same as write_next_timestep()


Methods
.......

 ``__init__(filename,numatoms[,start[,step[,delta[,remarks]]]])``
     opens *filename* and writes header if required by format
 ``write(obj)``
     write Timestep data in *obj*
 ``write_next_timestep([timestep])``
     write data in *timestep* to trajectory file
 ``convert_dimensions_to_unitcell(timestep)``
     take the dimensions from the timestep and convert to the native
     unitcell representation of the format
 ``close()``
     close file and finish I/O
 ``__del__()``
     ensures that close() is called

Attributes
..........

 ``filename``
     name of the trajectory file
 ``start, stop, step``
     first and last frame number (1-based) and step
 ``units``
     dictionary with keys *time*, *length*, *speed*, *force* and the
     appropriate unit (e.g. 'AKMA' and 'Angstrom' for Charmm dcds, 'ps' and
     'nm' for Gromacs trajectories, ``None`` and 'Angstrom' for PDB).
     Any field not used should be set to ``None``.
 ``format``
     string that identifies the file format, e.g. "DCD", "PDB", "CRD", "XTC",
     "TRR"


**Optional**

 ``ts``
     :class:`Timestep` instance


Single Frame Writer class
~~~~~~~~~~~~~~~~~~~~~~~~~

A single frame writer is a special case of a trajectory writer in that it
writes only a single coordinate frame to a file, for instance, a pdb or gro
file. Unlike trajectory formats, which only contains coordinates, *single
frame* formats contain much more information (e.g. atom and residue names and
numbers) and hence it is possible to write selections of atoms in a meaningful
way.

Signature::

   W = FrameWriter(filename, **kwargs)
   W.write(AtomGroup)
   W.write(Universe)

The blanket *kwargs* is required so that one can pass the same kind of
arguments (filename and numatoms) as for the Trajectory writers. In
this way, the simple :func:`~MDAnalysis.coordinates.core.writer`
factory function can be used for all writers.

Methods
.......

 ``__init__(filename, **kwargs)``
   opens *filename* for writing; `kwargs` are typically ignored
 ``write(obj)``
   writes the object *obj*, containing a
   :class:`~MDAnalysis.core.AtomGroup.AtomGroup` group of atoms (typically
   obtained from a selection) or :class:`~MDAnalysis.core.AtomGroup.Universe`
   to the file and closes the file

.. Note::

   Trajectory and Frame writers can be used in almost exactly the same
   manner with the one difference that Frame writers cannot deal with
   raw :class:`~MDAnalysis.coordinates.base.Timestep` objects.


Reader/Writer registry
----------------------

The following data structures connect reader/writer classes to their
format identifiers. They are documented for programmers who want to
enhance MDAnalysis; the casual user is unlikely to access them
directly.

Some formats can either write single frames or trajectories (such as
PDB). In theses cases, the kind of writer is selected with the
*multiframe* keyword to :func:`MDAnalysis.coordinates.core.get_writer`
(or the writer itself).

.. autodata:: _trajectory_readers
.. autodata:: _topology_coordinates_readers
.. autodata:: _trajectory_readers_permissive
.. autodata:: _compressed_formats
.. autodata:: _frame_writers
.. autodata:: _trajectory_writers

"""

__all__ = ['reader', 'writer']

import PDB
import PQR
import DCD
import CRD
import XTC
import TRR
import GRO
import XYZ
import TRJ
import PDBQT
import LAMMPS
import DMS
import TRZ
import MOL2
import GMS
import base
from core import reader, writer


#: standard trajectory readers (dict with identifier as key and reader class as value)
_trajectory_readers = {
    'DCD': DCD.DCDReader,
    # 'TRJ': DCD.DCDReader, #commented out because overridden by TRJ.TRJReader
    'XTC': XTC.XTCReader,
    'XYZ': XYZ.XYZReader,
    'TRR': TRR.TRRReader,
    'PDB': PDB.PDBReader,
    'XPDB': PDB.ExtendedPDBReader,
    'PDBQT': PDBQT.PDBQTReader,
    'CRD': CRD.CRDReader,
    'GRO': GRO.GROReader,
    'MOL2': MOL2.MOL2Reader,
    'TRJ': TRJ.TRJReader,  # AMBER text
    'MDCRD': TRJ.TRJReader,  # AMBER text
    'NCDF': TRJ.NCDFReader,  # AMBER netcdf
    'PQR': PQR.PQRReader,
    'LAMMPS': LAMMPS.DCDReader,
    'CHAIN': base.ChainReader,
    'DMS': DMS.DMSReader,
    'TRZ': TRZ.TRZReader,
    'DATA': LAMMPS.DATAReader,
    'GMS': GMS.GMSReader,
}

#: formats of readers that can also handle gzip or bzip2 compressed files
_compressed_formats = ['XYZ', 'TRJ', 'MDCRD', 'PQR', 'PDBQT']

#: readers of files that contain both topology/atom data and coordinates
#: (currently only the keys are used)
_topology_coordinates_readers = {
    'PDB': PDB.PrimitivePDBReader,  # FIXME: should be able to use BioPython PDBReader for topolgy if permissive=False!
    'XPDB': PDB.ExtendedPDBReader,
    'PDBQT': PDBQT.PDBQTReader,
    'GRO': GRO.GROReader,
    'CRD': CRD.CRDReader,
    'PQR': PQR.PQRReader,
    'DMS': DMS.DMSReader,
    'MOL2': MOL2.MOL2Reader,
    'DATA': LAMMPS.DATAReader,
    'GMS': GMS.GMSReader,
}

#: hack: readers that ignore most errors (permissive=True); at the moment
#: the same as :data:`_trajectory_readers` with the exception of the
#: the PDB reader (:class:`~MDAnalysis.coordinates.PDB.PDBReader` is replaced by
# :class:`~MDAnalysis.coordinates.PDB.PrimitivePDBReader`).
_trajectory_readers_permissive = _trajectory_readers.copy()
_trajectory_readers_permissive['PDB'] = PDB.PrimitivePDBReader

#: frame writers: export to single frame formats such as PDB, gro, crd
#: Signature::
#:
#:   W = FrameWriter(filename)
#:   W.write(AtomGroup)
_frame_writers = {
    'PDBQT': PDBQT.PDBQTWriter,
    'CRD': CRD.CRDWriter,
    'GRO': GRO.GROWriter,
    'PDB': PDB.PrimitivePDBWriter,
    'PQR': PQR.PQRWriter,
    'XYZ': XYZ.XYZWriter,
    'MOL2': MOL2.MOL2Writer,
}

#: trajectory writers: export frames, typically only saving coordinates
#: Signature::
#:
#:   W = TrajectoryWriter(filename,numatoms,**kwargs)
#:   W.write_next_timestep(TimeStep)
#:   W.write(Timestep)
#:   W.write(AtomGroup)
#:   W.write(Universe)
_trajectory_writers = {
    'DCD': DCD.DCDWriter,
    'XTC': XTC.XTCWriter,
    'TRR': TRR.TRRWriter,
    'LAMMPS': LAMMPS.DCDWriter,
    'PDB': PDB.MultiPDBWriter,
    'NCDF': TRJ.NCDFWriter,
    'TRZ': TRZ.TRZWriter,
    'XYZ': XYZ.XYZWriter,
    'MOL2': MOL2.MOL2Writer,
}
