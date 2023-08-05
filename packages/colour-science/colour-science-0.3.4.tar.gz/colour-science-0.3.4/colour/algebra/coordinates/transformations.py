#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Coordinates System Transformations
==================================

Defines objects to apply transformations on coordinates systems.

The following transformations are available:

-   :func:`cartesian_to_spherical`: Cartesian to Spherical transformation.
-   :func:`spherical_to_cartesian`: Spherical to Cartesian transformation.
-   :func:`cartesian_to_cylindrical`: Cartesian to Cylindrical transformation.
-   :func:`cylindrical_to_cartesian`: Cylindrical to Cartesian transformation.

References
----------
.. [1]  Wikipedia. (n.d.). List of common coordinate transformations.
        Retrieved from
        http://en.wikipedia.org/wiki/List_of_common_coordinate_transformations
"""

from __future__ import division, unicode_literals

import numpy as np

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['cartesian_to_spherical',
           'spherical_to_cartesian',
           'cartesian_to_cylindrical',
           'cylindrical_to_cartesian']


def cartesian_to_spherical(vector):
    """
    Transforms given Cartesian coordinates vector to Spherical coordinates.

    Parameters
    ----------
    vector : array_like
        Cartesian coordinates vector (x, y, z) to transform.

    Returns
    -------
    ndarray
        Spherical coordinates vector (r, theta, phi).

    See Also
    --------
    spherical_to_cartesian, cartesian_to_cylindrical, cylindrical_to_cartesian

    Examples
    --------
    >>> vector = np.array([3, 1, 6])
    >>> cartesian_to_spherical(vector)  # doctest: +ELLIPSIS
    array([ 6.7823299...,  1.0857465...,  0.3217505...])
    """

    r = np.linalg.norm(vector)
    x, y, z = np.ravel(vector)

    theta = np.arctan2(z, np.linalg.norm((x, y)))
    phi = np.arctan2(y, x)

    return np.array((r, theta, phi))


def spherical_to_cartesian(vector):
    """
    Transforms given Spherical coordinates vector to Cartesian coordinates.

    Parameters
    ----------
    vector : array_like
        Spherical coordinates vector (r, theta, phi) to transform.

    Returns
    -------
    ndarray
        Cartesian coordinates vector (x, y, z).

    See Also
    --------
    cartesian_to_spherical, cartesian_to_cylindrical, cylindrical_to_cartesian

    Examples
    --------
    >>> vector = np.array([6.78232998, 1.08574654, 0.32175055])
    >>> spherical_to_cartesian(vector)  # doctest: +ELLIPSIS
    array([ 3.        ,  0.9999999...,  6.        ])
    """

    r, theta, phi = np.ravel(vector)

    x = r * np.cos(theta) * np.cos(phi)
    y = r * np.cos(theta) * np.sin(phi)
    z = r * np.sin(theta)

    return np.array((x, y, z))


def cartesian_to_cylindrical(vector):
    """
    Transforms given Cartesian coordinates vector to Cylindrical coordinates.

    Parameters
    ----------
    vector : array_like
        Cartesian coordinates vector (x, y, z) to transform.

    Returns
    -------
    ndarray
        Cylindrical coordinates vector (z, theta, rho).

    See Also
    --------
    cartesian_to_spherical, spherical_to_cartesian, cylindrical_to_cartesian

    Examples
    --------
    >>> vector = np.array([3, 1, 6])
    >>> cartesian_to_cylindrical(vector)  # doctest: +ELLIPSIS
    array([ 6.        ,  0.3217505...,  3.1622776...])
    """

    x, y, z = np.ravel(vector)

    theta = np.arctan2(y, x)
    rho = np.linalg.norm((x, y))

    return np.array((z, theta, rho))


def cylindrical_to_cartesian(vector):
    """
    Transforms given Cylindrical coordinates vector to Cartesian coordinates.

    Parameters
    ----------
    vector : array_like
        Cylindrical coordinates vector (z, theta, rho) to transform.

    Returns
    -------
    ndarray
        Cartesian coordinates vector (x, y, z).

    See Also
    --------
    cartesian_to_spherical, spherical_to_cartesian, cartesian_to_cylindrical

    Examples
    --------
    >>> vector = np.array([6, 0.32175055, 3.16227766])
    >>> cylindrical_to_cartesian(vector)  # doctest: +ELLIPSIS
    array([ 3.        ,  0.9999999...,  6.        ])
    """

    z, theta, rho = np.ravel(vector)

    x = rho * np.cos(theta)
    y = rho * np.sin(theta)

    return np.array((x, y, z))
