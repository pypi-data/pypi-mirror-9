#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Academy Color Encoding System
=============================

Defines the *Academy Color Encoding System* (ACES) related encodings:

-   :attr:`ACES_2065_1_COLOURSPACE`
-   :attr:`ACES_CC_COLOURSPACE`
-   :attr:`ACES_PROXY_COLOURSPACE`
-   :attr:`ACES_CG_COLOURSPACE`

See Also
--------
`RGB Colourspaces IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/models/rgb.ipynb>`_  # noqa

References
----------
.. [1]  The Academy of Motion Picture Arts and Sciences, Science and
        Technology Council, & Academy Color Encoding System (ACES) Project
        Subcommittee. (n.d.). Academy Color Encoding System. Retrieved
        February 24, 2014, from
        http://www.oscars.org/science-technology/council/projects/aces.html
.. [2]  The Academy of Motion Picture Arts and Sciences, Science and
        Technology Council, & Academy Color Encoding System (ACES) Project
        Subcommittee. (2014). Technical Bulletin TB-2014-004 - Informative
        Notes on SMPTE ST 2065-1 – Academy Color Encoding Specification
        (ACES). Retrieved from
        https://github.com/ampas/aces-dev/tree/master/documents
.. [3]  The Academy of Motion Picture Arts and Sciences, Science and
        Technology Council, & Academy Color Encoding System (ACES) Project
        Subcommittee. (2014). Specification S-2014-003 - ACEScc , A
        Logarithmic Encoding of ACES Data for use within Color Grading
        Systems. Retrieved from
        https://github.com/ampas/aces-dev/tree/master/documents
.. [4]  The Academy of Motion Picture Arts and Sciences, Science and
        Technology Council, & Academy Color Encoding System (ACES) Project
        Subcommittee. (2014). Specification S-2013-001 - ACESproxy , an
        Integer Log Encoding of ACES Image Data. Retrieved from
        https://github.com/ampas/aces-dev/tree/master/documents
.. [5]  The Academy of Motion Picture Arts and Sciences, Science and
        Technology Council, & Academy Color Encoding System (ACES) Project
        Subcommittee. (2014). Technical Bulletin TB-2014-012 - Academy Color
        Encoding System Version 1.0 Component Names. Retrieved from
        https://github.com/ampas/aces-dev/tree/master/documents
"""

from __future__ import division, unicode_literals

import numpy as np

from colour.colorimetry import ILLUMINANTS
from colour.utilities import Structure
from colour.models import RGB_Colourspace, normalised_primary_matrix
from colour.utilities import CaseInsensitiveMapping

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['AP0',
           'AP1',
           'ACES_ILLUMINANT',
           'ACES_WHITEPOINT',
           'AP0_TO_XYZ_MATRIX',
           'XYZ_TO_AP0_MATRIX',
           'AP1_TO_XYZ_MATRIX',
           'XYZ_TO_AP1_MATRIX',
           'ACES_2065_1_TRANSFER_FUNCTION',
           'ACES_2065_1_INVERSE_TRANSFER_FUNCTION',
           'ACES_2065_1_COLOURSPACE',
           'ACES_CC_TRANSFER_FUNCTION',
           'ACES_CC_INVERSE_TRANSFER_FUNCTION',
           'ACES_CC_COLOURSPACE',
           'ACES_PROXY_10_CONSTANTS',
           'ACES_PROXY_12_CONSTANTS',
           'ACES_PROXY_CONSTANTS',
           'ACES_PROXY_TRANSFER_FUNCTION',
           'ACES_PROXY_INVERSE_TRANSFER_FUNCTION',
           'ACES_PROXY_COLOURSPACE',
           'ACES_CG_COLOURSPACE']

AP0 = np.array(
    [[0.73470, 0.26530],
     [0.00000, 1.00000],
     [0.00010, -0.07700]])
"""
*ACES Primaries 0* or *AP0* primaries.

AP0 : ndarray, (3, 2)
"""

AP1 = np.array(
    [[0.713, 0.293],
     [0.165, 0.830],
     [0.128, 0.044]])
"""
*ACES Primaries 1* or *AP1* primaries (known as *Rec. 2020+* primaries prior
to *ACES* 1.0 release).

AP1 : ndarray, (3, 2)
"""

ACES_ILLUMINANT = 'D60'
"""
*ACES2065-1* colourspace whitepoint name as illuminant.

ACES_ILLUMINANT : unicode
"""

ACES_WHITEPOINT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get(ACES_ILLUMINANT)
"""
*ACES2065-1* colourspace whitepoint.

ACES_WHITEPOINT : tuple
"""

AP0_TO_XYZ_MATRIX = np.array(
    [[9.52552396e-01, 0.00000000e+00, 9.36786317e-05],
     [3.43966450e-01, 7.28166097e-01, -7.21325464e-02],
     [0.00000000e+00, 0.00000000e+00, 1.00882518e+00]])
"""
*ACES Primaries 0* to *CIE XYZ* colourspace matrix.

AP0_TO_XYZ_MATRIX : array_like, (3, 3)
"""

XYZ_TO_AP0_MATRIX = np.linalg.inv(AP0_TO_XYZ_MATRIX)
"""
*CIE XYZ* colourspace to *ACES Primaries 0* matrix.

XYZ_TO_AP0_MATRIX : array_like, (3, 3)
"""

AP1_TO_XYZ_MATRIX = normalised_primary_matrix(AP1, ACES_WHITEPOINT)
"""
*ACES Primaries 1* to *CIE XYZ* colourspace matrix.

AP1_TO_XYZ_MATRIX : array_like, (3, 3)
"""

XYZ_TO_AP1_MATRIX = np.linalg.inv(AP1_TO_XYZ_MATRIX)
"""
*CIE XYZ* colourspace to *ACES Primaries 1* matrix.

XYZ_TO_AP1_MATRIX : array_like, (3, 3)
"""


def _aces_2065_1_transfer_function(value):
    """
    Defines the *ACES2065-1* colourspace transfer function.

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


def _aces_2065_1_inverse_transfer_function(value):
    """
    Defines the *ACES2065-1* colourspace inverse transfer function.

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


ACES_2065_1_TRANSFER_FUNCTION = _aces_2065_1_transfer_function
"""
Transfer function from linear to *ACES2065-1* colourspace.

ACES_2065_1_TRANSFER_FUNCTION : object
"""

ACES_2065_1_INVERSE_TRANSFER_FUNCTION = _aces_2065_1_inverse_transfer_function
"""
Inverse transfer function from *ACES2065-1* colourspace to linear.

ACES_2065_1_INVERSE_TRANSFER_FUNCTION : object
"""

ACES_2065_1_COLOURSPACE = RGB_Colourspace(
    'ACES2065-1',
    AP0,
    ACES_WHITEPOINT,
    ACES_ILLUMINANT,
    AP0_TO_XYZ_MATRIX,
    XYZ_TO_AP0_MATRIX,
    ACES_2065_1_TRANSFER_FUNCTION,
    ACES_2065_1_INVERSE_TRANSFER_FUNCTION)
"""
*ACES2065-1* colourspace, base encoding, used for exchange of full fidelity
images and archiving.

ACES_2065_1_COLOURSPACE : RGB_Colourspace
"""


def _aces_cc_transfer_function(value):
    """
    Defines the *ACEScc* colourspace transfer function.

    Parameters
    ----------
    value : numeric
        Value.

    Returns
    -------
    numeric
        Companded value.
    """

    if value < 0:
        return (np.log2(2 ** -15 * 0.5) + 9.72) / 17.52
    elif value < 2 ** -15:
        return (np.log2(2 ** -16 + value * 0.5) + 9.72) / 17.52
    else:
        return (np.log2(value) + 9.72) / 17.52


def _aces_cc_inverse_transfer_function(value):
    """
    Defines the *ACEScc* colourspace inverse transfer function.

    Parameters
    ----------
    value : numeric
        Value.

    Returns
    -------
    numeric
        Companded value.
    """

    if value < (9.72 - 15) / 17.52:
        return (2 ** (value * 17.52 - 9.72) - 2 ** -16) * 2
    elif (9.72 - 15) / 17.52 < value < (np.log2(65504) + 9.72) / 17.52:
        return 2 ** (value * 17.52 - 9.72)
    else:
        return 65504


ACES_CC_TRANSFER_FUNCTION = _aces_cc_transfer_function
"""
Transfer function from linear to *ACEScc* colourspace.

ACES_CC_TRANSFER_FUNCTION : object
"""

ACES_CC_INVERSE_TRANSFER_FUNCTION = (
    _aces_cc_inverse_transfer_function)
"""
Inverse transfer function from *ACEScc* colourspace to linear.

ACES_CC_INVERSE_TRANSFER_FUNCTION : object
"""

ACES_CC_COLOURSPACE = RGB_Colourspace(
    'ACEScc',
    AP1,
    ACES_WHITEPOINT,
    ACES_ILLUMINANT,
    AP1_TO_XYZ_MATRIX,
    XYZ_TO_AP1_MATRIX,
    ACES_CC_TRANSFER_FUNCTION,
    ACES_CC_INVERSE_TRANSFER_FUNCTION)
"""
*ACEScc* colourspace, a working space for color correctors, target for ASC-CDL
values created on-set.

ACES_CC_COLOURSPACE : RGB_Colourspace
"""

ACES_PROXY_10_CONSTANTS = Structure(
    CV_min=64,
    CV_max=940,
    steps_per_stop=50,
    mid_CV_offset=425,
    mid_log_offset=2.5)
"""
*ACESproxy* 10 bit colourspace constants.

ACES_PROXY_10_CONSTANTS : Structure
"""

ACES_PROXY_12_CONSTANTS = Structure(
    CV_min=256,
    CV_max=3760,
    steps_per_stop=200,
    mid_CV_offset=1700,
    mid_log_offset=2.5)
"""
*ACESproxy* 12 bit colourspace constants.

ACES_PROXY_12_CONSTANTS : Structure
"""

ACES_PROXY_CONSTANTS = CaseInsensitiveMapping(
    {'10 Bit': ACES_PROXY_10_CONSTANTS,
     '12 Bit': ACES_PROXY_12_CONSTANTS})
"""
Aggregated *ACESproxy* colourspace constants.

ACES_PROXY_CONSTANTS : CaseInsensitiveMapping
    {'10 Bit', '12 Bit'}
"""


def _aces_proxy_transfer_function(value, bit_depth='10 Bit'):
    """
    Defines the *ACESproxy* colourspace transfer function.

    Parameters
    ----------
    value : numeric
        Value.
    bit_depth : unicode, optional
        {'10 Bit', '12 Bit'}
        *ACESproxy* bit depth.

    Returns
    -------
    numeric
        Companded value.
    """

    constants = ACES_PROXY_CONSTANTS.get(bit_depth)

    float_2_cv = lambda x: max(constants.CV_min,
                               min(constants.CV_max, round(x)))
    if value > 2 ** -9.72:
        return float_2_cv((np.log2(value) + constants.mid_log_offset) *
                          constants.steps_per_stop + constants.mid_CV_offset)
    else:
        return constants.CV_min


def _aces_proxy_inverse_transfer_function(value, bit_depth='10 Bit'):
    """
    Defines the *ACESproxy* colourspace inverse transfer function.

    Parameters
    ----------
    value : numeric
        Value.
    bit_depth : unicode, optional
        {'10 Bit', '12 Bit'}
        *ACESproxy* bit depth.

    Returns
    -------
    numeric
        Companded value.
    """

    constants = ACES_PROXY_CONSTANTS.get(bit_depth)

    return (2 ** (((value - constants.mid_CV_offset) /
                   constants.steps_per_stop - constants.mid_log_offset)))


ACES_PROXY_TRANSFER_FUNCTION = _aces_proxy_transfer_function
"""
Transfer function from linear to *ACESproxy* colourspace.

ACES_PROXY_TRANSFER_FUNCTION : object
"""

ACES_PROXY_INVERSE_TRANSFER_FUNCTION = (
    _aces_proxy_inverse_transfer_function)
"""
Inverse transfer function from *ACESproxy* colourspace to linear.

ACES_PROXY_INVERSE_TRANSFER_FUNCTION : object
"""

ACES_PROXY_COLOURSPACE = RGB_Colourspace(
    'ACESproxy',
    AP0,
    ACES_WHITEPOINT,
    ACES_ILLUMINANT,
    AP0_TO_XYZ_MATRIX,
    XYZ_TO_AP0_MATRIX,
    ACES_PROXY_TRANSFER_FUNCTION,
    ACES_PROXY_INVERSE_TRANSFER_FUNCTION)
"""
*ACESproxy* colourspace, a lightweight encoding for transmission over HD-SDI
(or other production transmission schemes), onset look management. Not
intended to be stored or used in production imagery or for final color
grading/mastering.

ACES_PROXY_COLOURSPACE : RGB_Colourspace
"""

ACES_CG_COLOURSPACE = RGB_Colourspace(
    'ACEScg',
    AP1,
    ACES_WHITEPOINT,
    ACES_ILLUMINANT,
    AP1_TO_XYZ_MATRIX,
    XYZ_TO_AP1_MATRIX,
    ACES_PROXY_TRANSFER_FUNCTION,
    ACES_PROXY_INVERSE_TRANSFER_FUNCTION)
"""
*ACEScg* colourspace, a working space for paint/compositor applications that
don’t support ACES2065-1 or ACEScc.

ACES_CG_COLOURSPACE : RGB_Colourspace
"""
