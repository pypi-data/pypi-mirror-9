#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cinema Gamut Colourspace
========================

Defines the *Canon* *Cinema Gamut* colourspace:

-   :attr:`CINEMA_GAMUT_COLOURSPACE`.

See Also
--------
`RGB Colourspaces IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/models/rgb.ipynb>`_  # noqa

References
----------
.. [1]  Canon. (2014). EOS C500 Firmware Update. Retrieved January 14, 2015,
        from http://www.usa.canon.com/cusa/professional/standard_display/cinema-firmware-c500  # noqa
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

__all__ = ['CINEMA_GAMUT_PRIMARIES',
           'CINEMA_GAMUT_ILLUMINANT',
           'CINEMA_GAMUT_WHITEPOINT',
           'CINEMA_GAMUT_TO_XYZ_MATRIX',
           'XYZ_TO_CINEMA_GAMUT_MATRIX',
           'CINEMA_GAMUT_TRANSFER_FUNCTION',
           'CINEMA_GAMUT_INVERSE_TRANSFER_FUNCTION',
           'CINEMA_GAMUT_COLOURSPACE']

CINEMA_GAMUT_PRIMARIES = np.array(
    [[0.7400, 0.2700],
     [0.1700, 1.1400],
     [0.0800, -0.1000]])
"""
*Cinema Gamut* colourspace primaries.

CINEMA_GAMUT_PRIMARIES : ndarray, (3, 2)
"""

CINEMA_GAMUT_ILLUMINANT = 'D65'
"""
*Cinema Gamut* colourspace whitepoint name as illuminant.

CINEMA_GAMUT_ILLUMINANT : unicode
"""

CINEMA_GAMUT_WHITEPOINT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get(CINEMA_GAMUT_ILLUMINANT)
"""
*Cinema Gamut* colourspace whitepoint.

CINEMA_GAMUT_WHITEPOINT : tuple
"""

CINEMA_GAMUT_TO_XYZ_MATRIX = normalised_primary_matrix(CINEMA_GAMUT_PRIMARIES,
                                                       CINEMA_GAMUT_WHITEPOINT)
"""
*Cinema Gamut* colourspace to *CIE XYZ* colourspace matrix.

CINEMA_GAMUT_TO_XYZ_MATRIX : array_like, (3, 3)
"""

XYZ_TO_CINEMA_GAMUT_MATRIX = np.linalg.inv(CINEMA_GAMUT_TO_XYZ_MATRIX)
"""
*CIE XYZ* colourspace to *Cinema Gamut* colourspace matrix.

XYZ_TO_CINEMA_GAMUT_MATRIX : array_like, (3, 3)
"""


def _cinema_gamut_transfer_function(value):
    """
    Defines the *Cinema Gamut* colourspace transfer function.

    Parameters
    ----------
    value : numeric
        Value.

    Returns
    -------
    numeric
        Companded value.
    """

    return value


def _cinema_gamut_inverse_transfer_function(value):
    """
    Defines the *Cinema Gamut* colourspace inverse transfer
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

    return value


CINEMA_GAMUT_TRANSFER_FUNCTION = _cinema_gamut_transfer_function
"""
Transfer function from linear to *Cinema Gamut* colourspace.

CINEMA_GAMUT_TRANSFER_FUNCTION : object
"""

CINEMA_GAMUT_INVERSE_TRANSFER_FUNCTION = (
    _cinema_gamut_inverse_transfer_function)
"""
Inverse transfer function from *Cinema Gamut* colourspace to linear.

CINEMA_GAMUT_INVERSE_TRANSFER_FUNCTION : object
"""

CINEMA_GAMUT_COLOURSPACE = RGB_Colourspace(
    'Cinema Gamut',
    CINEMA_GAMUT_PRIMARIES,
    CINEMA_GAMUT_WHITEPOINT,
    CINEMA_GAMUT_ILLUMINANT,
    CINEMA_GAMUT_TO_XYZ_MATRIX,
    XYZ_TO_CINEMA_GAMUT_MATRIX,
    CINEMA_GAMUT_TRANSFER_FUNCTION,
    CINEMA_GAMUT_INVERSE_TRANSFER_FUNCTION)
"""
*Cinema Gamut* colourspace.

CINEMA_GAMUT_COLOURSPACE : RGB_Colourspace
"""
