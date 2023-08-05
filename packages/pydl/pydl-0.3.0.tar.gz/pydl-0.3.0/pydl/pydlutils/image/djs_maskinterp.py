# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def djs_maskinterp1(yval,mask,xval=None,const=False):
    """Interpolate over a masked, 1-d array.

    Parameters
    ----------
    yval : ndarray
        The input values
    mask : ndarray
        The mask
    xval : ndarray, optional
        If set, use these x values, otherwise use an array
    const : bool, optional
        If set to ``True``, bad values around the edges of the array will be
        set to a constant value.

    Returns
    -------
    djs_maskinterp1 : ndarray
    """
    import numpy as np
    good = mask == 0
    if good.all():
        return yval
    ngood = good.sum()
    igood = good.nonzero()[0]
    if ngood == 0:
        return yval
    if ngood == 1:
        return np.zeros(yval.shape,dtype=yval.dtype) + yval[igood[0]]
    ynew = yval.astype('d')
    ny = yval.size
    ibad = (mask != 0).nonzero()[0]
    if xval is None:
        ynew[ibad] = np.interp(ibad,igood,ynew[igood])
        if const:
            if igood[0] != 0:
                ynew[0:igood[0]] = ynew[igood[0]]
            if igood[ngood-1] != ny-1:
                ynew[igood[ngood-1]+1:ny] = ynew[igood[ngood-1]]
    else:
        ii = xval.argsort()
        ibad = (mask[ii] != 0).nonzero()[0]
        igood = (mask[ii] == 0).nonzero()[0]
        ynew[ii[ibad]] = np.interp(xval[ii[ibad]],xval[ii[igood]],ynew[ii[igood]])
        if const:
            if igood[0] != 0:
                ynew[ii[0:igood[0]]] = ynew[ii[igood[0]]]
            if igood[ngood-1] != ny-1:
                ynew[ii[igood[ngood-1]+1:ny]] = ynew[ii[igood[ngood-1]]]
    return ynew
#
#
#
def djs_maskinterp(yval,mask,xval=None,axis=None,const=False):
    """Interpolate over masked pixels in a vector, image or 3-D array.

    Parameters
    ----------
    yval : ndarray
        The input values
    mask : ndarray
        The mask
    xval : ndarray, optional
        If set, use these x values, otherwise use an array
    axis : int, optional
        Must be set if yval has more than one dimension. If set to zero,
        interpolate along the first axis of the array, if set to one,
        interpolate along the second axis of the array, and so on.
    const : bool, optional
        This value is passed to a helper function, djs_maskinterp1.

    Returns
    -------
    djs_maskinterp : ndarray

    """
    import numpy as np
    if mask.shape != yval.shape:
        raise ValueError('mask must have the same shape as yval.')
    if xval is not None:
        if xval.shape != yval.shape:
            raise ValueError('xval must have the same shape as yval.')
    ndim = yval.ndim
    if ndim == 1:
        ynew = djs_maskinterp1(yval,mask,xval,const=const)
    else:
        if axis is None:
            raise ValueError('Must set axis if yval has more than one dimension.')
        if axis < 0 or axis > ndim-1 or axis - int(axis) != 0:
            raise ValueError('Invalid axis value.')
        ynew = np.zeros(yval.shape,dtype=yval.dtype)
        if ndim == 2:
            if xval is None:
                if axis == 0:
                    for i in range(yval.shape[0]):
                        ynew[i,:] = djs_maskinterp1(yval[i,:],mask[i,:],const=const)
                else:
                    for i in range(yval.shape[1]):
                        ynew[:,i] = djs_maskinterp1(yval[:,i],mask[:,i],const=const)
            else:
                if axis == 0:
                    for i in range(yval.shape[0]):
                        ynew[i,:] = djs_maskinterp1(yval[i,:],mask[i,:],xval[i,:],const=const)
                else:
                    for i in range(yval.shape[1]):
                        ynew[:,i] = djs_maskinterp1(yval[:,i],mask[:,i],xval[:,i],const=const)
        elif ndim == 3:
            if xval is None:
                if axis == 0:
                    for i in range(yval.shape[0]):
                        for j in range(yval.shape[1]):
                            ynew[i,j,:] = djs_maskinterp1(yval[i,j,:],mask[i,j,:],const=const)
                elif axis == 1:
                    for i in range(yval.shape[0]):
                        for j in range(yval.shape[2]):
                            ynew[i,:,j] = djs_maskinterp1(yval[i,:,j],mask[i,:,j],const=const)
                else:
                    for i in range(yval.shape[1]):
                        for j in range(yval.shape[2]):
                            ynew[:,i,j] = djs_maskinterp1(yval[:,i,j],mask[:,i,j],const=const)
            else:
                if axis == 0:
                    for i in range(yval.shape[0]):
                        for j in range(yval.shape[1]):
                            ynew[i,j,:] = djs_maskinterp1(yval[i,j,:],mask[i,j,:],xval[i,j,:],const=const)
                elif axis == 1:
                    for i in range(yval.shape[0]):
                        for j in range(yval.shape[2]):
                            ynew[i,:,j] = djs_maskinterp1(yval[i,:,j],mask[i,:,j],xval[i,j,:],const=const)
                else:
                    for i in range(yval.shape[1]):
                        for j in range(yval.shape[2]):
                            ynew[:,i,j] = djs_maskinterp1(yval[:,i,j],mask[:,i,j],xval[i,j,:],const=const)
        else:
            raise NotImplementedError('Unsupported number of dimensions.')
    return ynew
