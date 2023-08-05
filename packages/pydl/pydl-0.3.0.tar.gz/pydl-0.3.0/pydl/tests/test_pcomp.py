# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def test_pcomp():
    from ..pcomp import pcomp
    from numpy import array, tile
    try:
        from astropy.tests.compat import assert_allclose
    except ImportError:
        from numpy.testing.utils import assert_allclose
    pcomp_data = array([
        [19.5, 43.1, 29.1, 11.9],
        [24.7, 49.8, 28.2, 22.8],
        [30.7, 51.9, 37.0, 18.7],
        [29.8, 54.3, 31.1, 20.1],
        [19.1, 42.2, 30.9, 12.9],
        [25.6, 53.9, 23.7, 21.7],
        [31.4, 58.5, 27.6, 27.1],
        [27.9, 52.1, 30.6, 25.4],
        [22.1, 49.9, 23.2, 21.3],
        [25.5, 53.5, 24.8, 19.3],
        [31.1, 56.6, 30.0, 25.4],
        [30.4, 56.7, 28.3, 27.2],
        [18.7, 46.5, 23.0, 11.7],
        [19.7, 44.2, 28.6, 17.8],
        [14.6, 42.7, 21.3, 12.8],
        [29.5, 54.4, 30.1, 23.9],
        [27.7, 55.3, 25.7, 22.6],
        [30.2, 58.6, 24.6, 25.4],
        [22.7, 48.2, 27.1, 14.8],
        [25.2, 51.0, 27.5, 21.1]])
    m=4
    n=20
    means = tile(pcomp_data.mean(0),20).reshape(pcomp_data.shape)
    newarray = pcomp_data - means
    foo = pcomp(newarray,covariance=True)
    #
    # This array is obtained from the IDL version of PCOMP.
    # It is only accurate up to an overall sign on each column.
    #
    derived = array([
        [ -107.377  ,  13.3986  , -1.40521  , -0.0324538 ],
        [    3.20342,   0.699964,  5.95396  , -0.0154266 ],
        [   32.4969 ,  38.6573  , -3.87102  ,  0.00906474],
        [   40.8858 ,  13.7870  , -4.98349  , -0.00512299],
        [ -107.236  ,  19.3568  ,  1.76589  ,  0.0231152 ],
        [   18.4284 , -17.1468  , -1.46805  , -0.00318355],
        [   99.8885 ,  -6.22849 ,  0.130080 ,  0.0166338 ],
        [   45.3808 ,   8.11078 ,  6.53065  , -0.0114850 ],
        [  -21.3101 , -18.3147  ,  3.75132  , -0.0133497 ],
        [    5.54411, -11.1707  , -4.51918  ,  0.0224445 ],
        [   83.1352 ,   4.96944 ,  0.0912485,  0.0104372 ],
        [   87.1055 ,  -3.16057 ,  2.81444  ,  0.00460935],
        [ -101.319  , -11.7835  , -6.11614  ,  0.00658332],
        [  -73.0708 ,   6.23879 ,  6.60536  ,  0.0215680 ],
        [ -137.017  , -19.0988  ,  1.32969  ,  0.0120680 ],
        [   57.1149 ,   6.95618 ,  0.839940 , -0.00950313],
        [   42.1264 , -10.0721  , -2.14432  ,  0.00948831],
        [   83.3046 , -16.6907  , -2.71600  , -0.0132752 ],
        [  -54.1269 ,   2.55509 , -4.21364  , -0.0251960 ],
        [    2.84273,  -1.06368 ,  1.62462  , -0.00701279]])
    for k in range(m):
        assert_allclose(abs(foo.derived[:,k]),abs(derived[:,k]),1e-4)
    coefficients = array([
        [  4.87988  ,  5.05684  , 1.02824  ,  4.79357   ],
        [  1.01466  , -0.954475 , 3.48852  , -0.774333  ],
        [ -0.618291 , -0.955430 , 0.269045 ,  1.57962   ],
        [ -0.0900205,  0.0751850, 0.0472409,  0.00219369]])
    coefficientsT = coefficients.T
    for k in range(m):
        assert_allclose(abs(foo.coefficients[:,k]),abs(coefficientsT[:,k]),1e-4)
    eigenvalues = array([73.4205, 14.7100, 3.86270, 0.0159930])
    assert_allclose(foo.eigenvalues,eigenvalues,1e-4)
    variance = array([0.797969, 0.159875, 0.0419817, 0.000173819])
    assert_allclose(foo.variance,variance,1e-4)
