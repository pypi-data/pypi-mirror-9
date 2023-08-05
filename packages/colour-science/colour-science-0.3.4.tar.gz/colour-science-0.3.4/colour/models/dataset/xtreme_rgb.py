#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Xtreme RGB Colourspace
======================

Defines the *Xtreme RGB* colourspace:

-   :attr:`XTREME_RGB_COLOURSPACE`.

See Also
--------
`RGB Colourspaces IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/models/rgb.ipynb>`_  # noqa

References
----------
.. [1]  HutchColor. (n.d.). XtremeRGB (4 K). Retrieved from
        http://www.hutchcolor.com/profiles/XtremeRGB.zip
"""

from __future__ import division, unicode_literals

import numpy as np

from colour.colorimetry import ILLUMINANTS
from colour.models import RGB_Colourspace, normalised_primary_matrix

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['XTREME_RGB_PRIMARIES',
           'XTREME_RGB_ILLUMINANT',
           'XTREME_RGB_WHITEPOINT',
           'XTREME_RGB_TO_XYZ_MATRIX',
           'XYZ_TO_XTREME_RGB_MATRIX',
           'XTREME_RGB_TRANSFER_FUNCTION',
           'XTREME_RGB_INVERSE_TRANSFER_FUNCTION',
           'XTREME_RGB_COLOURSPACE']

XTREME_RGB_PRIMARIES = np.array(
    [[1, 0],
     [0, 1],
     [0, 0]])
"""
*Xtreme RGB* colourspace primaries.

XTREME_RGB_PRIMARIES : ndarray, (3, 2)
"""

XTREME_RGB_ILLUMINANT = 'D50'
"""
*Xtreme RGB* colourspace whitepoint name as illuminant.

XTREME_RGB_WHITEPOINT : unicode
"""

XTREME_RGB_WHITEPOINT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get(XTREME_RGB_ILLUMINANT)
"""
*Xtreme RGB* colourspace whitepoint.

XTREME_RGB_WHITEPOINT : tuple
"""

XTREME_RGB_TO_XYZ_MATRIX = normalised_primary_matrix(XTREME_RGB_PRIMARIES,
                                                     XTREME_RGB_WHITEPOINT)
"""
*Xtreme RGB* colourspace to *CIE XYZ* colourspace matrix.

XTREME_RGB_TO_XYZ_MATRIX : array_like, (3, 3)
"""

XYZ_TO_XTREME_RGB_MATRIX = np.linalg.inv(XTREME_RGB_TO_XYZ_MATRIX)
"""
*CIE XYZ* colourspace to *Xtreme RGB* colourspace matrix.

XYZ_TO_XTREME_RGB_MATRIX : array_like, (3, 3)
"""


def _xtreme_rgb_transfer_function(value):
    """
    Defines the *Xtreme RGB* colourspace transfer function.

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


def _xtreme_rgb_inverse_transfer_function(value):
    """
    Defines the *Xtreme RGB* colourspace inverse transfer
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


XTREME_RGB_TRANSFER_FUNCTION = _xtreme_rgb_transfer_function
"""
Transfer function from linear to *Xtreme RGB* colourspace.

XTREME_RGB_TRANSFER_FUNCTION : object
"""

XTREME_RGB_INVERSE_TRANSFER_FUNCTION = _xtreme_rgb_inverse_transfer_function
"""
Inverse transfer function from *Xtreme RGB* colourspace to linear.

XTREME_RGB_INVERSE_TRANSFER_FUNCTION : object
"""

XTREME_RGB_COLOURSPACE = RGB_Colourspace(
    'Xtreme RGB',
    XTREME_RGB_PRIMARIES,
    XTREME_RGB_WHITEPOINT,
    XTREME_RGB_ILLUMINANT,
    XTREME_RGB_TO_XYZ_MATRIX,
    XYZ_TO_XTREME_RGB_MATRIX,
    XTREME_RGB_TRANSFER_FUNCTION,
    XTREME_RGB_INVERSE_TRANSFER_FUNCTION)
"""
*Xtreme RGB* colourspace.

XTREME_RGB_COLOURSPACE : RGB_Colourspace
"""
