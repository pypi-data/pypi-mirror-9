#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Colour Fitting
==============

Defines various objects for colour fitting, like colour matching two images.

See Also
--------
`Colour Fitting IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/characterisation/fitting.ipynb>`_  # noqa
"""

from __future__ import division, unicode_literals

import numpy as np

from colour.algebra import linear_regression

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['first_order_colour_fit']


def first_order_colour_fit(m1, m2):
    """
    Performs a first order colour fit from given :math:`m2` colour matrix to
    :math:`m1` colour matrix. The resulting colour matrix is calculated using
    multiple linear regression.

    The purpose of that object is for example matching of two *ColorChecker*
    colour rendition charts together.

    Parameters
    ----------
    m1 : array_like, (3, n)
        Reference matrix the matrix :math:`m2` will be colour fitted against.
    m2 : array_like, (3, n)
        Matrix to fit.

    Returns
    -------
    ndarray, (3, 3)
        Fitting colour matrix.

    Examples
    --------
    >>> m1 = np.array([
    ...     [0.1722481, 0.0917066, 0.06416938],
    ...     [0.49189645, 0.2780205, 0.21923399],
    ...     [0.10999751, 0.18658946, 0.29938611],
    ...     [0.1166612, 0.14327905, 0.05713804],
    ...     [0.18988879, 0.18227649, 0.36056247],
    ...     [0.12501329, 0.42223442, 0.37027445],
    ...     [0.64785606, 0.22396782, 0.03365194],
    ...     [0.06761093, 0.11076896, 0.39779139],
    ...     [0.49101797, 0.09448929, 0.11623839],
    ...     [0.11622386, 0.04425753, 0.14469986],
    ...     [0.36867946, 0.4454523, 0.06028681],
    ...     [0.61632937, 0.32323906, 0.02437089],
    ...     [0.03016472, 0.06153243, 0.29014596],
    ...     [0.11103655, 0.30553067, 0.08149137],
    ...     [0.4116219, 0.05816656, 0.04845934],
    ...     [0.73339206, 0.53075188, 0.02475212],
    ...     [0.47347718, 0.08834792, 0.30310315],
    ...     [0., 0.25187016, 0.3506245],
    ...     [0.76809639, 0.7848624, 0.77808297],
    ...     [0.53822392, 0.54307997, 0.54710883],
    ...     [0.35458526, 0.35318419, 0.35524431],
    ...     [0.17976704, 0.18000531, 0.17991488],
    ...     [0.09351417, 0.09510603, 0.09675027],
    ...     [0.03405071, 0.03295077, 0.03702047]])
    >>> m2 = np.array([
    ...     [0.15579559, 0.09715755, 0.07514556],
    ...     [0.3911314, 0.25943419, 0.21266708],
    ...     [0.12824821, 0.1846357, 0.31508023],
    ...     [0.12028974, 0.13455659, 0.074084],
    ...     [0.19368988, 0.21158946, 0.37955964],
    ...     [0.19957425, 0.36085439, 0.40678123],
    ...     [0.48896605, 0.20691688, 0.05816533],
    ...     [0.09775522, 0.16710693, 0.47147724],
    ...     [0.39358649, 0.122334, 0.10526425],
    ...     [0.10780332, 0.07258529, 0.16151473],
    ...     [0.27502671, 0.34705454, 0.09728099],
    ...     [0.43980441, 0.26880559, 0.05430533],
    ...     [0.05887212, 0.11126272, 0.38552469],
    ...     [0.12705825, 0.2578786, 0.13566464],
    ...     [0.35612929, 0.07933258, 0.05118732],
    ...     [0.48131976, 0.42082843, 0.07120612],
    ...     [0.34665585, 0.15170714, 0.24969804],
    ...     [0.08261116, 0.24588716, 0.48707733],
    ...     [0.66054904, 0.65941137, 0.66376412],
    ...     [0.48051509, 0.47870296, 0.48230082],
    ...     [0.33045354, 0.32904184, 0.33228886],
    ...     [0.18001305, 0.17978567, 0.18004416],
    ...     [0.10283975, 0.1042468, 0.10384975],
    ...     [0.04742204, 0.04772203, 0.04914226]])
    >>> first_order_colour_fit(m1, m2)  # doctest: +ELLIPSIS
    array([[ 1.4043128...,  0.0112806..., -0.2029710...],
           [-0.0998911...,  1.5012214..., -0.1856479...],
           [ 0.2248369..., -0.0767236...,  1.0496013...]])
    """

    x_coefficients = linear_regression(m1[:, 0], m2)
    y_coefficients = linear_regression(m1[:, 1], m2)
    z_coefficients = linear_regression(m1[:, 2], m2)

    return np.array([x_coefficients[:3],
                     y_coefficients[:3],
                     z_coefficients[:3]]).reshape((3, 3))
