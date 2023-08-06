# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- http://mdanalysis.googlecode.com
# Copyright (c) 2006-2014 Naveen Michaud-Agrawal,
#               Elizabeth J. Denning, Oliver Beckstein,
#               and contributors (see AUTHORS for the full list)
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
#     N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and
#     O. Beckstein. MDAnalysis: A Toolkit for the Analysis of
#     Molecular Dynamics Simulations. J. Comput. Chem. 32 (2011), 2319--2327,
#     doi:10.1002/jcc.21787
#

cimport c_numpy
c_numpy.import_array()

ctypedef int size_t

cdef extern from "Python.h":
    int PyErr_CheckSignals()
    void* PyCObject_AsVoidPtr(object o)
    char* PyString_AsString(object o)

cdef extern from *:
    ctypedef int fio_fd
    ctypedef int fio_size_t
    fio_size_t fio_fseek(fio_fd fd, fio_size_t offset, int whence)

cdef extern from "readdcd.h":
    int read_dcdsubset(fio_fd fd, int natoms, int lowerb, int upperb, float *x, float *y, float *z,
                       float *unitcell, int nfixed, int first, int *freeind,
                       float *fixedcoords, int reverse, int charmm)
    int skip_dcdstep(fio_fd fd, int natoms, int nfixed, int charmm, int numstep)
    int jump_to_dcdstep(fio_fd fd, int natoms, int nsets, int nfixed, int charmm, int header_size, int step)

ctypedef struct dcdhandle:
    fio_fd fd
    fio_size_t header_size
    int natoms
    int nsets
    int setsread
    int istart
    int nsavc
    double delta
    int nfixed
    int *freeind
    float *fixedcoords
    int reverse
    int charmm
    int first
    int with_unitcell

cdef extern from "correl.h":
    void copyseries(int frame, char *data, int *strides, float *tempX, float *tempY, float *tempZ, char* datacode, int numdata, int* atomlist, int* atomcounts, int lowerb, double *aux)

import numpy

def __read_timecorrel(object self, object atoms, object atomcounts, object format, object auxdata, int sizedata, int lowerb, int upperb, int start, int stop, int skip):
    cdef dcdhandle* dcd
    cdef c_numpy.ndarray atomlist, atomcountslist, auxlist
    cdef c_numpy.ndarray data, temp
    cdef float *tempX, *tempY, *tempZ
    cdef int rc
    cdef char* fmtstr

    dcd = <dcdhandle*>PyCObject_AsVoidPtr(self._dcd_C_ptr)
    cdef int numframes
    if (stop == -1): stop = dcd.nsets
    numframes = (stop-start+1) / skip
    cdef int numdata
    numdata = len(format)
    if numdata==0:
        raise Exception("No data requested, timeseries is empty")
    fmtstr = PyString_AsString(format)
    atomlist = numpy.array(atoms, numpy.int32)
    atomcountslist = numpy.array(atomcounts, numpy.int32)
    auxlist = numpy.array(auxdata, numpy.float64)
    #print "atomlist", atomlist
    #print "atomcountslist", atomcountslist
    #print "formatcode", fmtstr
    cdef int range
    range = upperb - lowerb + 1
    # Create data list
    #data = numpy.zeros((numframes, sizedata), numpy.float64)
    data = numpy.zeros((sizedata, numframes), numpy.float64)
    temp = numpy.zeros((3, range), numpy.float32)
    tempX = <float*>(temp.data+0*temp.strides[0])
    tempY = <float*>(temp.data+1*temp.strides[0])
    tempZ = <float*>(temp.data+2*temp.strides[0])

    # Reset trajectory
    rc = fio_fseek(dcd.fd, dcd.header_size, 0) #FIO_SEEK_SET
    dcd.setsread = 0
    dcd.first = 1

    # Jump to frame
    if (start > 0):
        rc = jump_to_dcdstep(dcd.fd, dcd.natoms, dcd.nsets, dcd.nfixed, dcd.charmm, dcd.header_size, start)
        if (rc < 0):
            raise IOError("Error jumping to starting frame")
        dcd.first = 0
        dcd.setsread = start

    cdef int index, numskip
    cdef int i, j
    cdef float unitcell[6]
    for i from 0 <= i < numframes:
        if (skip > 1):
            # Check if we have fixed atoms
            # XXX not done
            numskip = skip - (dcd.setsread % skip) - 1
            rc = skip_dcdstep(dcd.fd, dcd.natoms, dcd.nfixed, dcd.charmm, numskip)
            if (rc < 0):
                raise IOError("Error skipping frame from DCD file")
            dcd.setsread = dcd.setsread + numskip
        rc = read_dcdsubset(dcd.fd, dcd.natoms, lowerb, upperb, tempX, tempY, tempZ, unitcell, dcd.nfixed, dcd.first, dcd.freeind, dcd.fixedcoords, dcd.reverse, dcd.charmm)
        dcd.first=0
        dcd.setsread = dcd.setsread + 1
        if (rc < 0):
            raise IOError("Error reading frame from DCD file")
        # Copy into data array based on format
        copyseries(i, <char*>data.data, data.strides, tempX, tempY, tempZ, fmtstr, numdata, <int*>atomlist.data, <int*>atomcountslist.data, lowerb, <double*>auxlist.data);
        PyErr_CheckSignals()

    # Reset trajectory
    rc = fio_fseek(dcd.fd, dcd.header_size, 0) #FIO_SEEK_SET
    dcd.setsread = 0
    dcd.first = 1
    return data

def __read_timeseries(object self, object atoms, int skip):
    cdef dcdhandle* dcd
    cdef c_numpy.ndarray atomlist
    cdef c_numpy.ndarray coord, temp
    cdef float *tempX, *tempY, *tempZ
    cdef int rc

    dcd = <dcdhandle*>PyCObject_AsVoidPtr(self._dcd_C_ptr)
    cdef int numframes
    numframes = dcd.nsets / skip
    cdef int numatoms
    numatoms = len(atoms)
    if numatoms==0:
        raise Exception("No atoms passed into __read_timeseries function")
    atomlist = numpy.array(atoms)
    cdef int lowerb, upperb, range
    lowerb = atoms[0]
    upperb = atoms[-1]
    range = upperb - lowerb + 1
    # Create atom list
    coord = numpy.zeros((numatoms, numframes, 3), numpy.float64)
    temp = numpy.zeros((3, range), numpy.float32)
    tempX = <float*>(temp.data+0*temp.strides[0])
    tempY = <float*>(temp.data+1*temp.strides[0])
    tempZ = <float*>(temp.data+2*temp.strides[0])
    # Jump to the beginning of the trajectory file
    rc = fio_fseek(dcd.fd, dcd.header_size, 0) #FIO_SEEK_SET
    dcd.setsread = 0
    dcd.first = 1

    cdef int index, numskip
    cdef int i, j
    cdef float unitcell[6]
    for i from 0 <= i < numframes:
        if (skip > 1):
            # Check if we have fixed atoms
            # XXX not done
            numskip = skip - (dcd.setsread % skip) - 1
            rc = skip_dcdstep(dcd.fd, dcd.natoms, dcd.nfixed, dcd.charmm, numskip)
            if (rc < 0):
                raise IOError("Error skipping frame from DCD file")
            dcd.setsread = dcd.setsread + numskip
        rc = read_dcdsubset(dcd.fd, dcd.natoms, lowerb, upperb, tempX, tempY, tempZ, unitcell, dcd.nfixed, dcd.first, dcd.freeind, dcd.fixedcoords, dcd.reverse, dcd.charmm)
        dcd.first=0
        dcd.setsread = dcd.setsread + 1
        if (rc < 0):
            raise IOError("Error reading frame from DCD file")
        # Copy into numeric array
        for j from 0 <= j < numatoms:
            index = (<int*>atomlist.data)[j]-lowerb
            (<double*> (coord.data+j*coord.strides[0]+i*coord.strides[1]+0*coord.strides[2]))[0] = tempX[index]
            (<double*> (coord.data+j*coord.strides[0]+i*coord.strides[1]+1*coord.strides[2]))[0] = tempY[index]
            (<double*> (coord.data+j*coord.strides[0]+i*coord.strides[1]+2*coord.strides[2]))[0] = tempZ[index]
    return coord
