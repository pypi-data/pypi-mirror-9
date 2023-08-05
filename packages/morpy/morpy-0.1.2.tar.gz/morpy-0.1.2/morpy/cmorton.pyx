from copy import copy
import numpy as np
cimport numpy as np

ctypedef fused anyuint:
    int
    long
    unsigned int
    unsigned long
    np.int32_t
    np.int64_t
    np.uint32_t
    np.uint64_t

class MortonLib(object):
    """docstring for MortonLib"""
    def __init__(self, ndim=3):
        self.ndim = ndim

    def get_cell(self, anyuint key):
        cdef np.ndarray[np.uint64_t, ndim=1] iarr =\
            np.zeros(self.ndim, dtype='uint64')
        cdef np.int64_t tkey = key
        cdef int level = 0
        cdef int ndim = self.ndim
        cdef int d
        while (tkey > 0):
            for d in range(ndim):
                iarr[ndim-d-1] += (tkey & 1) << level
                tkey = tkey >> 1
            level += 1
        return iarr

    def get_cells(self, np.ndarray[anyuint, ndim=1] key_arr):
        cdef np.ndarray[np.uint64_t, ndim=2] iarr =\
            np.zeros([key_arr.size, self.ndim], dtype='uint64')
        cdef int level = 0
        cdef int ndim = self.ndim
        cdef int d
        cdef int k
        cdef np.int64_t tkey
        cdef int nkeys = key_arr.shape[0]
        for k in range(nkeys):
            key = key_arr[k]
            level = 0
            while (key > 0):
                for d in range(ndim):
                    iarr[k, ndim-d-1] += (key & 1) << level
                    key = key >> 1
                level += 1
        return iarr

    def get_key(self, np.ndarray[anyuint, ndim=1] inarr):
        cdef np.ndarray[np.uint64_t, ndim=1] iarr = np.zeros(inarr.shape[0], dtype='uint64')
        cdef int d
        cdef np.int64_t m = 0
        cdef int level = 0
        cdef int ndim = self.ndim
        cdef int keep_going = 1
        for d in range(ndim):
            iarr[d] = inarr[d]
        while keep_going:
            for d in range(ndim):
                m |= (iarr[d] & 1) << (ndim*level + (ndim-d-1))
                iarr[d] = iarr[d] >> 1

            keep_going = 0
            for d in range(ndim):
                if iarr[d] > 0:
                    keep_going = 1
            level += 1
        return m

    def get_keys(self, np.ndarray[anyuint, ndim=2] inarr):
        cdef np.ndarray[np.uint64_t, ndim=1] marr = np.zeros(inarr.shape[0], dtype='uint64')
        cdef np.ndarray[np.uint64_t, ndim=1] iarr = np.zeros(inarr.shape[1], dtype='uint64')
        cdef np.int64_t m
        cdef int level
        cdef int c, d, i
        cdef int ncells = inarr.shape[0]
        cdef int ndim = self.ndim
        cdef int keep_going
        for c in range(ncells):
            m = 0
            level = 0
            for d in range(ndim):
                iarr[d] = inarr[c, d]

            keep_going = 1
            while keep_going:
                keep_going = 0
                for d in range(ndim):
                    m |= (iarr[d] & 1) << (ndim*level + (ndim-d-1))
                    iarr[d] = iarr[d] >> 1
                for d in range(ndim):
                    if iarr[d] > 0:
                        keep_going = 1
                level += 1
            marr[c] = m
        return marr
