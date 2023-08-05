# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def is_cap_used(use_caps,i):
    """Returns True if a cap is used.

    Parameters
    ----------
    use_caps :
    i : int

    Returns
    -------
    is_cap_used : bool
    """
    return (use_caps & 1 << i) != 0
