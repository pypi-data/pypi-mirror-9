# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def djs_median(array,dimension=None,width=None,boundary='none'):
    """Compute the median of an array.

    Use a filtering box or collapse the image along one dimension.

    Parameters
    ----------
    array : ndarray
        input array
    dimension : int, optional
        Compute the median over this dimension. It is an error to specify both
        `dimension` and `width`.
    width : int, optional
        Width of the median window. In general, this should be an odd
        integer.  It is an error to specify both `dimension` and `width`.
    boundary : { 'none', 'reflect', 'nearest', 'wrap' }, optional
        Boundary condition to impose.  'none' means no filtering is done within
        `width`/2 of the boundary.  'reflect' means reflect pixel values around the
        boundary. 'nearest' means use the values of the nearest boundary pixel.
        'wrap' means wrap pixel values around the boundary. 'nearest' and 'wrap'
        are not implemented.

    Returns
    -------
    djs_median : ndarray
        The output.  If neither `dimension` nor `width` are set, this is a scalar
        value, just the output of ``numpy.median()``.  If `dimension` is set,
        then the result simply ``numpy.median(array,dimension)``.
        If `width` is set, the result has the same shape as the input array.
    """
    import numpy as np
    from scipy.signal import medfilt, medfilt2d
    if dimension is None and width is None:
        return np.median(array)
    elif width is None:
        return np.median(array,axis=dimension)
    elif dimension is None:
        if width == 1:
            return array
        if boundary == 'none':
            if array.ndim == 1:
                medarray = medfilt(array,min(width,array.size))
                #
                # medfilt doesn't handle edges the same way as IDL, so we
                # have to fix them up
                #
                istart = int((width-1)/2)
                iend = array.size - int((width+1)/2)
                i = np.arange(array.size)
                w = (i < istart) | (i > iend)
                medarray[w] = array[w]
                return medarray
            elif array.ndim == 2:
                medarray = medfilt2(array,min(width,array.size))
                istart = int((width-1)/2)
                iend = (array.shape[0] - int((width+1)/2), array.shape[1] - int((width+1)/2))
                i = np.arange(array.shape[0])
                j = np.arange(array.shape[1])
                w = ((i < istart) | (i > iend[0]), (j < istart) | (j > iend[1]))
                medarray[w[0],w[1]] = array[w[0],w[1]]
                return medarray
            else:
                raise ValueError('Unsupported number of dimensions with this boundary condition.')
        elif boundary == 'reflect':
            padsize = int(np.ceil(width/2.0))
            if array.ndim == 1:
                bigarr = np.zeros(array.shape[0]+2*padsize,dtype=array.dtype)
                bigarr[padsize:padsize+array.shape[0]] = array
                bigarr[0:padsize] = array[0:padsize][::-1]
                bigarr[padsize+array.shape[0]:padsize*2+array.shape[0]] = array[array.shape[0]-padsize:array.shape[0]][::-1]
                f = medfilt(bigarr,min(width,array.size))
                istart = int((width-1)/2)
                iend = array.size - int((width+1)/2)
                i = np.arange(array.size)
                w = (i < istart) | (i > iend)
                f[w] = array[w]
                medarray = f[padsize:padsize+array.shape[0]]
                return medarray
            elif array.ndim == 2:
                bigarr = np.zeros((array.shape[0]+2*padsize,array.shape[1]+2*padsize),dtype=array.dtype)
                bigarr[padsize:padsize+array.shape[0],padsize:padsize+array.shape[1]] = array
                # Copy into top + bottom
                bigarr[0:padsize,padsize:array.shape[1]+padsize] = array[0:padsize,:][::-1,:]
                bigarr[array.shape[0]+padsize:bigarr.shape[0],padsize:array.shape[1]+padsize] = array[array.shape[0]-padsize:array.shape[0],:][::-1,:]
                # Copy into left + right
                bigarr[padsize:array.shape[0]+padsize,0:padsize] = array[:,0:padsize][:,::-1]
                bigarr[padsize:array.shape[0]+padsize] = array[:array.shape[1]-padsize:array.shape[1]][:,::-1]
                # Copy into top left
                bigarr[0:padsize,0:padsize] = foo[0:padsize,0:padsize][::-1,::-1]
                # Copy into top right
                bigarr[0:padsize,bigarr.shape[1]-padsize:bigarr.shape[1]] = array[0:padsize,array.shape[1]-padsize:array.shape[1]][::-1,::-1]
                # Copy into bottom left
                bigarr[bigarr.shape[0]-padsize:bigarr.shape[0],0:padsize] = array[array.shape[0]-padsize,0:padsize][::-1,::-1]
                # Copy into bottom right
                bigarr[bigarr.shape[0]-padsize:bigarr.shape[0],bigarr.shape[1]-padsize:bigarr.shape[1]] = array[ar]
                f = medfilt2d(bigarr,min(width,array.size))
                istart = int((width-1)/2)
                iend = (array.shape[0] - int((width+1)/2), array.shape[1] - int((width+1)/2))
                i = np.arange(array.shape[0])
                j = np.arange(array.shape[1])
                w = ((i < istart) | (i > iend[0]), (j < istart) | (j > iend[1]))
                f[w[0],w[1]] = array[w[0],w[1]]
                medarray = f[padsize:array.shape[0]+padsize,padsize:array.shape[1]+padsize]
                return medarray
            else:
                raise ValueError('Unsupported number of dimensions with this boundary condition.')
        elif boundary == 'nearest':
            raise NotImplementedError('This boundary condition not implemented')
        elif boundary == 'wrap':
            raise NotImplementedError('This boundary condition not implemented')
        else:
            raise ValueError('Unknown boundary condition.')
    else:
        raise ValueError('Invalid to specify both dimension & width.')
