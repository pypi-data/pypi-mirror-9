#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rec. 709 Colourspace
====================

Defines the *Rec. 709* colourspace:

-   :attr:`REC_709_COLOURSPACE`.

See Also
--------
`RGB Colourspaces IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/models/rgb.ipynb>`_  # noqa

References
----------
.. [1]  International Telecommunication Union. (2002). Parameter values for
        the HDTV standards for production and international programme exchange
        BT Series Broadcasting service. In Recommendation ITU-R BT.709-5
        (Vol. 5, pp. 1–32). Retrieved from
        http://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.709-5-200204-I!!PDF-E.pdf  # noqa
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

__all__ = ['REC_709_PRIMARIES',
           'REC_709_WHITEPOINT',
           'REC_709_ILLUMINANT',
           'REC_709_TO_XYZ_MATRIX',
           'XYZ_TO_REC_709_MATRIX',
           'REC_709_TRANSFER_FUNCTION',
           'REC_709_INVERSE_TRANSFER_FUNCTION',
           'REC_709_COLOURSPACE']

REC_709_PRIMARIES = np.array(
    [[0.6400, 0.3300],
     [0.3000, 0.6000],
     [0.1500, 0.0600]])
"""
*Rec. 709* colourspace primaries.

REC_709_PRIMARIES : ndarray, (3, 2)
"""

REC_709_ILLUMINANT = 'D65'
"""
*Rec. 709* colourspace whitepoint name as illuminant.

REC_709_ILLUMINANT : unicode
"""

REC_709_WHITEPOINT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get(REC_709_ILLUMINANT)
"""
*Rec. 709* colourspace whitepoint.

REC_709_WHITEPOINT : tuple
"""

REC_709_TO_XYZ_MATRIX = np.array(
    [[0.41238656, 0.35759149, 0.18045049],
     [0.21263682, 0.71518298, 0.0721802],
     [0.01933062, 0.11919716, 0.95037259]])
"""
*Rec. 709* colourspace to *CIE XYZ* colourspace matrix.

REC_709_TO_XYZ_MATRIX : array_like, (3, 3)
"""

XYZ_TO_REC_709_MATRIX = np.linalg.inv(REC_709_TO_XYZ_MATRIX)
"""
*CIE XYZ* colourspace to *Rec. 709* colourspace matrix.

XYZ_TO_REC_709_MATRIX : array_like, (3, 3)
"""


def _rec_709_transfer_function(value):
    """
    Defines the *Rec. 709* colourspace transfer function.

    Parameters
    ----------
    value : numeric
        Value.

    Returns
    -------
    numeric
        Companded value.
    """

    return value * 4.5 if value < 0.018 else 1.099 * (value ** 0.45) - 0.099


def _rec_709_inverse_transfer_function(value):
    """
    Defines the *Rec. 709* colourspace inverse transfer
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

    return (value / 4.5
            if value < _rec_709_transfer_function(0.018) else
            ((value + 0.099) / 1.099) ** (1 / 0.45))


REC_709_TRANSFER_FUNCTION = _rec_709_transfer_function
"""
Transfer function from linear to *Rec. 709* colourspace.

REC_709_TRANSFER_FUNCTION : object
"""

REC_709_INVERSE_TRANSFER_FUNCTION = _rec_709_inverse_transfer_function
"""
Inverse transfer function from *Rec. 709* colourspace to linear.

REC_709_INVERSE_TRANSFER_FUNCTION : object
"""

REC_709_COLOURSPACE = RGB_Colourspace(
    'Rec. 709',
    REC_709_PRIMARIES,
    REC_709_WHITEPOINT,
    REC_709_ILLUMINANT,
    REC_709_TO_XYZ_MATRIX,
    XYZ_TO_REC_709_MATRIX,
    REC_709_TRANSFER_FUNCTION,
    REC_709_INVERSE_TRANSFER_FUNCTION)
"""
*Rec. 709* colourspace.

REC_709_COLOURSPACE : RGB_Colourspace
"""
