#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Lightness :math:`L*`
====================

Defines *Lightness* :math:`L*` computation objects.

The following methods are available:

-   :func:`lightness_Glasser1958`: *Lightness* :math:`L^*` computation of given
    *luminance* :math:`Y` using
    Glasser, Mckinney, Reilly and Schnelle (1958)⁠⁠⁠ method.
-   :func:`lightness_Wyszecki1963`: *Lightness* :math:`W` computation of
    given *luminance* :math:`Y` using Wyszecki (1963)⁠⁠⁠⁠ method.
-   :func:`lightness_1976`: *Lightness* :math:`L^*` computation of given
    *luminance* :math:`Y` as per *CIE Lab* implementation.

See Also
--------
`Lightness IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/colorimetry/lightness.ipynb>`_  # noqa

References
----------
.. [1]  Wikipedia. (n.d.). Lightness. Retrieved April 13, 2014, from
        http://en.wikipedia.org/wiki/Lightness
"""

from __future__ import division, unicode_literals

from colour.constants import CIE_E, CIE_K
from colour.utilities import CaseInsensitiveMapping, warning

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['lightness_Glasser1958',
           'lightness_Wyszecki1963',
           'lightness_1976',
           'LIGHTNESS_METHODS',
           'lightness']


def lightness_Glasser1958(Y, **kwargs):
    """
    Returns the *Lightness* :math:`L` of given *luminance* :math:`Y` using
    *Glasser, Mckinney, Reilly and Schnelle (1958)* method.

    Parameters
    ----------
    Y : numeric
        *luminance* :math:`Y`.
    \*\*kwargs : \*\*, optional
        Unused parameter provided for signature compatibility with other
        *Lightness* computation objects.

    Returns
    -------
    numeric
        *Lightness* :math:`L`.

    Notes
    -----
    -   Input *luminance* :math:`Y` is in domain [0, 100].
    -   Output *Lightness* :math:`L` is in domain [0, 100].

    References
    ----------
    .. [2]  Glasser, L. G., McKinney, A. H., Reilly, C. D., & Schnelle, P. D.
            (1958). Cube-Root Color Coordinate System. J. Opt. Soc. Am.,
            48(10), 736–740. doi:10.1364/JOSA.48.000736

    Examples
    --------
    >>> lightness_Glasser1958(10.08)  # doctest: +ELLIPSIS
    36.2505626...
    """

    L = 25.29 * (Y ** (1 / 3)) - 18.38

    return L


def lightness_Wyszecki1963(Y, **kwargs):
    """
    Returns the *Lightness* :math:`W` of given *luminance* :math:`Y` using
    *Wyszecki (1963)* method.


    Parameters
    ----------
    Y : numeric
        *luminance* :math:`Y`.
    \*\*kwargs : \*\*, optional
        Unused parameter provided for signature compatibility with other
        *Lightness* computation objects.

    Returns
    -------
    numeric
        *Lightness* :math:`W`.

    Notes
    -----
    -   Input *luminance* :math:`Y` is in domain [0, 100].
    -   Output *Lightness* :math:`W` is in domain [0, 100].

    References
    ----------
    .. [3]  Wyszecki, G. (1963). Proposal for a New Color-Difference Formula.
            J. Opt. Soc. Am., 53(11), 1318–1319. doi:10.1364/JOSA.53.001318

    Examples
    --------
    >>> lightness_Wyszecki1963(10.08)  # doctest: +ELLIPSIS
    37.0041149...
    """

    if not 1 < Y < 98:
        warning(('"W*" Lightness computation is only applicable for '
                 '1% < "Y" < 98%, unpredictable results may occur!'))

    W = 25 * (Y ** (1 / 3)) - 17

    return W


def lightness_1976(Y, Y_n=100):
    """
    Returns the *Lightness* :math:`L^*` of given *luminance* :math:`Y` using
    given reference white *luminance* :math:`Y_n` as per *CIE Lab*
    implementation.

    Parameters
    ----------
    Y : numeric
        *luminance* :math:`Y`.
    Y_n : numeric, optional
        White reference *luminance* :math:`Y_n`.

    Returns
    -------
    numeric
        *Lightness* :math:`L^*`.

    Notes
    -----
    -   Input *luminance* :math:`Y` and :math:`Y_n` are in domain [0, 100].
    -   Output *Lightness* :math:`L^*` is in domain [0, 100].

    References
    ----------
    .. [4]  Wyszecki, G., & Stiles, W. S. (2000). CIE 1976 (L*u*v*)-Space and
            Color-Difference Formula. In Color Science: Concepts and Methods,
            Quantitative Data and Formulae (p. 167). Wiley. ISBN:978-0471399186
    .. [5]  Lindbloom, B. (2003). A Continuity Study of the CIE L* Function.
            Retrieved February 24, 2014, from
            http://brucelindbloom.com/LContinuity.html

    Examples
    --------
    >>> lightness_1976(10.08)  # doctest: +ELLIPSIS
    37.9856290...
    """

    ratio = Y / Y_n
    Lstar = CIE_K * ratio if ratio <= CIE_E else 116 * ratio ** (1 / 3) - 16

    return Lstar


LIGHTNESS_METHODS = CaseInsensitiveMapping(
    {'Glasser 1958': lightness_Glasser1958,
     'Wyszecki 1963': lightness_Wyszecki1963,
     'CIE 1976': lightness_1976})
"""
Supported *Lightness* computations methods.

LIGHTNESS_METHODS : CaseInsensitiveMapping
    {'Glasser 1958', 'Wyszecki 1963', 'CIE 1976'}

Aliases:

-   'Lstar1976': 'CIE 1976'
"""
LIGHTNESS_METHODS['Lstar1976'] = LIGHTNESS_METHODS['CIE 1976']


def lightness(Y, method='CIE 1976', **kwargs):
    """
    Returns the *Lightness* :math:`L^*` using given method.

    Parameters
    ----------
    Y : numeric
        *luminance* :math:`Y`.
    method : unicode, optional
        {'CIE 1976', 'Glasser 1958', 'Wyszecki 1963'},
        Computation method.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    numeric
        *Lightness* :math:`L^*`.

    Notes
    -----
    -   Input *luminance* :math:`Y` and optional :math:`Y_n` are in domain
        [0, 100].
    -   Output *Lightness* :math:`L^*` is in domain [0, 100].

    Examples
    --------
    >>> lightness(10.08)  # doctest: +ELLIPSIS
    37.9856290...
    >>> lightness(10.08, Y_n=100)  # doctest: +ELLIPSIS
    37.9856290...
    >>> lightness(10.08, Y_n=95)  # doctest: +ELLIPSIS
    38.9165987...
    >>> lightness(10.08, method='Glasser 1958')  # doctest: +ELLIPSIS
    36.2505626...
    >>> lightness(10.08, method='Wyszecki 1963')  # doctest: +ELLIPSIS
    37.0041149...
    """

    return LIGHTNESS_METHODS.get(method)(Y, **kwargs)
