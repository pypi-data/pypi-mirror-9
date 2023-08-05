#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CIE RGB Colourspace
===================

Defines the *CIE RGB* colourspace:

-   :attr:`CIE_RGB_COLOURSPACE`.

See Also
--------
`RGB Colourspaces IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/models/rgb.ipynb>`_  # noqa

References
----------
.. [1]  Wikipedia. (n.d.). Construction of the CIE XYZ color space from the
        Wright–Guild data. Retrieved February 24, 2014, from
        http://en.wikipedia.org/wiki/CIE_1931_color_space#Construction_of_the_CIE_XYZ_color_space_from_the_Wright.E2.80.93Guild_data  # noqa
"""

from __future__ import division, unicode_literals

import numpy as np

from colour.colorimetry import ILLUMINANTS
from colour.models import RGB_Colourspace

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['CIE_RGB_PRIMARIES',
           'CIE_RGB_ILLUMINANT',
           'CIE_RGB_WHITEPOINT',
           'CIE_RGB_TO_XYZ_MATRIX',
           'XYZ_TO_CIE_RGB_MATRIX',
           'CIE_RGB_TRANSFER_FUNCTION',
           'CIE_RGB_INVERSE_TRANSFER_FUNCTION',
           'CIE_RGB_COLOURSPACE']

CIE_RGB_PRIMARIES = np.array(
    [[0.7350, 0.2650],
     [0.2740, 0.7170],
     [0.1670, 0.0090]])
"""
*CIE RGB* colourspace primaries.

CIE_RGB_PRIMARIES : ndarray, (3, 2)
"""

CIE_RGB_ILLUMINANT = 'E'
"""
*CIE RGB* colourspace whitepoint name as illuminant.

CIE_RGB_ILLUMINANT : unicode
"""

CIE_RGB_WHITEPOINT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get(CIE_RGB_ILLUMINANT)
"""
*CIE RGB* colourspace whitepoint.

CIE_RGB_WHITEPOINT : tuple
"""

CIE_RGB_TO_XYZ_MATRIX = np.array([[0.4887180, 0.3106803, 0.2006017],
                                  [0.1762044, 0.8129847, 0.0108109],
                                  [0.0000000, 0.0102048, 0.9897952]])
"""
*CIE RGB* colourspace to *CIE XYZ* colourspace matrix.

CIE_RGB_TO_XYZ_MATRIX : array_like, (3, 3)
"""

XYZ_TO_CIE_RGB_MATRIX = np.linalg.inv(CIE_RGB_TO_XYZ_MATRIX)
"""
*CIE XYZ* colourspace to *CIE RGB* colourspace matrix.

XYZ_TO_CIE_RGB_MATRIX : array_like, (3, 3)
"""


def _cie_rgb_transfer_function(value):
    """
    Defines the *CIE RGB* colourspace transfer function.

    Parameters
    ----------
    value : numeric
        Value.

    Returns
    -------
    numeric
        Companded value.
    """

    return value ** (1 / 2.2)


def _cie_rgb_inverse_transfer_function(value):
    """
    Defines the *CIE RGB* colourspace inverse transfer
    function.

    Parameters
    ----------
    value : numeric
        Value.

    Returns
    -------
    numeric
        Companded value.
    """

    return value ** 2.2


CIE_RGB_TRANSFER_FUNCTION = _cie_rgb_transfer_function
"""
Transfer function from linear to *CIE RGB* colourspace.

CIE_RGB_TRANSFER_FUNCTION : object
"""

CIE_RGB_INVERSE_TRANSFER_FUNCTION = _cie_rgb_inverse_transfer_function
"""
Inverse transfer function from *CIE RGB* colourspace to linear.

CIE_RGB_INVERSE_TRANSFER_FUNCTION : object
"""

CIE_RGB_COLOURSPACE = RGB_Colourspace(
    'CIE RGB',
    CIE_RGB_PRIMARIES,
    CIE_RGB_WHITEPOINT,
    CIE_RGB_ILLUMINANT,
    CIE_RGB_TO_XYZ_MATRIX,
    XYZ_TO_CIE_RGB_MATRIX,
    CIE_RGB_TRANSFER_FUNCTION,
    CIE_RGB_INVERSE_TRANSFER_FUNCTION)
"""
*CIE RGB* colourspace.

CIE_RGB_COLOURSPACE : RGB_Colourspace
"""
