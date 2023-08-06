#emacs, this is -*-Python-*- mode

# tracking_funcs.pyx
# JAB 7/27/13

from libc.stdlib cimport malloc, free

import numpy as num
cimport numpy as num
num.import_array()

cimport cython

## On the SBFMF videos used for benchmarking, the average processing
## time for all background-subtraction operations was 0.36 s using NumPy.
## After implementing these particular operations in Cython, the processing
## time dropped to 0.05 s.
##
## Ellipse-fitting took 0.26 s before using Cython, and now takes 0.19 s.
##
## Total processing per frame dropped from 0.66 s to 0.28 s, a 58% improvement.


#######################################################################
# binarize()
#######################################################################
@cython.boundscheck( False )
def binarize( num.ndarray[num.float64_t, ndim=2] fg_img,
              num.ndarray arena_mask,
              float thresh ):
    """calculate fg_img[arena_mask] > thresh"""
    # this takes 0.03 s instead of 0.15 s on my benchmark images
    
    # cast boolean mask as uint8 (which it is already) as a workaround
    # to the lack of a bool_t type in Numpy (which causes Cython to complain)
    cdef num.ndarray[num.uint8_t, ndim=2] byte_mask = num.array( arena_mask, dtype=num.uint8 )

    cdef Py_ssize_t i, j
    cdef Py_ssize_t imax = fg_img.shape[0]
    cdef Py_ssize_t jmax = fg_img.shape[1]

    cdef num.ndarray[num.uint8_t, ndim=2] bin_img = num.zeros( (fg_img.shape[0], fg_img.shape[1]), dtype=num.uint8 )

    for i in xrange( imax ):
        for j in xrange( jmax ):
            if byte_mask[i,j] and fg_img[i,j] > thresh:
                bin_img[i,j] = 1

    return num.array( bin_img, dtype=bool )


#######################################################################
# normalize()
#######################################################################
@cython.boundscheck( False )
def normalize( num.ndarray[num.float64_t, ndim=2] fg_img,
               num.ndarray[num.float64_t, ndim=2] dev_img,
               num.ndarray arena_mask ):
    """fg_img[arena_mask] /= dev_img[arena_mask]"""
    # this takes 0.003 s instead of 0.1 s on my benchmark images

    # cast boolean mask as uint8 (which it is already) as a workaround
    # to the lack of a bool_t type in Numpy (which causes Cython to complain)
    cdef num.ndarray[num.uint8_t, ndim=2] byte_mask = num.array( arena_mask, dtype=num.uint8 )

    cdef Py_ssize_t i, j
    cdef Py_ssize_t imax = fg_img.shape[0]
    cdef Py_ssize_t jmax = fg_img.shape[1]

    for i in xrange( imax ):
        for j in xrange( jmax ):
            if byte_mask[i,j]:
                fg_img[i,j] /= dev_img[i,j]


#######################################################################
# thresh_img()
#######################################################################
@cython.boundscheck( False )
def thresh_img( num.ndarray[num.float64_t, ndim=2] raw_img,
                num.ndarray[num.float64_t, ndim=2] center_img,
                num.ndarray arena_mask,
                bg_type ):
    """calculate raw_img[arena_mask] - center_img[arena_mask], or variant"""
    # this takes 0.005 s instead of 0.1 s on my benchmark images

    # cast boolean mask as uint8 (which it is already) as a workaround
    # to the lack of a bool_t type in Numpy (which causes Cython to complain)
    cdef num.ndarray[num.uint8_t, ndim=2] byte_mask = num.array( arena_mask, dtype=num.uint8 )

    cdef Py_ssize_t i, j
    cdef Py_ssize_t imax = raw_img.shape[0]
    cdef Py_ssize_t jmax = raw_img.shape[1]

    cdef num.ndarray[num.float64_t, ndim=2] thresh_img = num.zeros( (raw_img.shape[0], raw_img.shape[1]), dtype=num.float64 )

    if bg_type == 'light_on_dark':
        for i in xrange( imax ):
            for j in xrange( jmax ):
                if byte_mask[i,j]:
                    thresh_img[i,j] = raw_img[i,j] - center_img[i,j]
                    if thresh_img[i,j] < 0.:
                        thresh_img[i,j] = 0.
    elif bg_type == 'dark_on_light':
        for i in xrange( imax ):
            for j in xrange( jmax ):
                if byte_mask[i,j]:
                    thresh_img[i,j] = center_img[i,j] - raw_img[i,j]
                    if thresh_img[i,j] < 0.:
                        thresh_img[i,j] = 0.
    else:
        for i in xrange( imax ):
            for j in xrange( jmax ):
                if byte_mask[i,j]:
                    thresh_img[i,j] = raw_img[i,j] - center_img[i,j]
                    if thresh_img[i,j] < 0.:
                        thresh_img[i,j] = -thresh_img[i,j]

    return thresh_img


#######################################################################
# indexed_sum()
#######################################################################
@cython.boundscheck( False )
def indexed_sum( num.ndarray[num.float64_t, ndim=2] input,
                 num.ndarray[num.int64_t, ndim=2] scale,
                 num.ndarray[num.int32_t, ndim=2] labels,
                 int n_labels ):
    """scipy.ndimage.measurements.sum( input*scale, labels, range(1,n_labels+1) )"""
    cdef num.ndarray[num.float64_t, ndim=1] sum = num.zeros( (n_labels,), dtype=num.float64 )

    cdef Py_ssize_t i, j
    cdef Py_ssize_t imax = input.shape[0]
    cdef Py_ssize_t jmax = input.shape[1]
    
    for i in xrange( imax ):
        for j in xrange( jmax ):
            if labels[i,j] > 0 and labels[i,j] <= n_labels:
                sum[labels[i,j] - 1] += input[i,j]*scale[i,j]

    return sum
