#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RGB Colourspace & Transformations
=================================

Defines the :class:`RGB_Colourspace` class for the *RGB* colourspaces dataset
from :mod:`colour.models.dataset.aces_rgb`, etc... and the following *RGB*
colourspace transformations:

-   :func:`XYZ_to_RGB`
-   :func:`RGB_to_XYZ`
-   :func:`RGB_to_RGB`

See Also
--------
`RGB Colourspaces IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/models/rgb.ipynb>`_  # noqa
"""

from __future__ import division, unicode_literals

import numpy as np

from colour.algebra import as_array
from colour.models import xy_to_XYZ
from colour.adaptation import chromatic_adaptation_matrix_VonKries

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['RGB_Colourspace',
           'XYZ_to_RGB',
           'RGB_to_XYZ',
           'RGB_to_RGB']


class RGB_Colourspace(object):
    """
    Implements support for the *RGB* colourspaces dataset from
    :mod:`colour.models.dataset.aces_rgb`, etc....

    Parameters
    ----------
    name : unicode
        *RGB* colourspace name.
    primaries : array_like
        *RGB* colourspace primaries.
    whitepoint : array_like
        *RGB* colourspace whitepoint.
    illuminant : unicode, optional
        *RGB* colourspace whitepoint name as illuminant.
    RGB_to_XYZ_matrix : array_like, optional
        Transformation matrix from colourspace to *CIE XYZ* colourspace.
    XYZ_to_RGB_matrix : array_like, optional
        Transformation matrix from *CIE XYZ* colourspace to colourspace.
    transfer_function : object, optional
        *RGB* colourspace opto-electronic conversion function from linear to
        colourspace.
    inverse_transfer_function : object, optional
        *RGB* colourspace inverse opto-electronic conversion function from
        colourspace to linear.
    """

    def __init__(self,
                 name,
                 primaries,
                 whitepoint,
                 illuminant=None,
                 RGB_to_XYZ_matrix=None,
                 XYZ_to_RGB_matrix=None,
                 transfer_function=None,
                 inverse_transfer_function=None):
        self.__name = None
        self.name = name
        self.__primaries = None
        self.primaries = primaries
        self.__whitepoint = None
        self.whitepoint = whitepoint
        self.__illuminant = None
        self.illuminant = illuminant
        self.__RGB_to_XYZ_matrix = None
        self.RGB_to_XYZ_matrix = RGB_to_XYZ_matrix
        self.__XYZ_to_RGB_matrix = None
        self.XYZ_to_RGB_matrix = XYZ_to_RGB_matrix
        self.__transfer_function = None
        self.transfer_function = transfer_function
        self.__inverse_transfer_function = None
        self.inverse_transfer_function = inverse_transfer_function

    @property
    def name(self):
        """
        Property for **self.__name** private attribute.

        Returns
        -------
        unicode
            self.__name.
        """

        return self.__name

    @name.setter
    def name(self, value):
        """
        Setter for **self.__name** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('name', value))
        self.__name = value

    @property
    def primaries(self):
        """
        Property for **self.__primaries** private attribute.

        Returns
        -------
        array_like, (3, 2)
            self.__primaries.
        """

        return self.__primaries

    @primaries.setter
    def primaries(self, value):
        """
        Setter for **self.__primaries** private attribute.

        Parameters
        ----------
        value : array_like, (3, 2)
            Attribute value.
        """

        if value is not None:
            value = as_array(value)
        self.__primaries = value

    @property
    def whitepoint(self):
        """
        Property for **self.__whitepoint** private attribute.

        Returns
        -------
        array_like
            self.__whitepoint.
        """

        return self.__whitepoint

    @whitepoint.setter
    def whitepoint(self, value):
        """
        Setter for **self.__whitepoint** private attribute.

        Parameters
        ----------
        value : array_like
            Attribute value.
        """

        if value is not None:
            assert type(value) in (tuple, list, np.ndarray, np.matrix), (
                ('"{0}" attribute: "{1}" type is not "tuple", "list", '
                 '"ndarray" or "matrix"!').format('whitepoint', value))
        self.__whitepoint = value

    @property
    def illuminant(self):
        """
        Property for **self.__illuminant** private attribute.

        Returns
        -------
        unicode
            self.__illuminant.
        """

        return self.__illuminant

    @illuminant.setter
    def illuminant(self, value):
        """
        Setter for **self.__illuminant** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('illuminant', value))
        self.__illuminant = value

    @property
    def RGB_to_XYZ_matrix(self):
        """
        Property for **self.__to_XYZ** private attribute.

        Returns
        -------
        array_like, (3, 3)
            self.__to_XYZ.
        """

        return self.__RGB_to_XYZ_matrix

    @RGB_to_XYZ_matrix.setter
    def RGB_to_XYZ_matrix(self, value):
        """
        Setter for **self.__to_XYZ** private attribute.

        Parameters
        ----------
        value : array_like
            Attribute value.
        """

        if value is not None:
            value = as_array(value)
        self.__RGB_to_XYZ_matrix = value

    @property
    def XYZ_to_RGB_matrix(self):
        """
        Property for **self.__to_RGB** private attribute.

        Returns
        -------
        array_like, (3, 3)
            self.__to_RGB.
        """

        return self.__XYZ_to_RGB_matrix

    @XYZ_to_RGB_matrix.setter
    def XYZ_to_RGB_matrix(self, value):
        """
        Setter for **self.__to_RGB** private attribute.

        Parameters
        ----------
        value : array_like
            Attribute value.
        """

        if value is not None:
            value = as_array(value)
        self.__XYZ_to_RGB_matrix = value

    @property
    def transfer_function(self):
        """
        Property for **self.__transfer_function** private attribute.

        Returns
        -------
        object
            self.__transfer_function.
        """

        return self.__transfer_function

    @transfer_function.setter
    def transfer_function(self, value):
        """
        Setter for **self.__transfer_function** private attribute.

        Parameters
        ----------
        value : object
            Attribute value.
        """

        if value is not None:
            assert hasattr(value, '__call__'), (
                '"{0}" attribute: "{1}" is not callable!'.format(
                    'transfer_function', value))
        self.__transfer_function = value

    @property
    def inverse_transfer_function(self):
        """
        Property for **self.__inverse_transfer_function** private attribute.

        Returns
        -------
        object
            self.__inverse_transfer_function.
        """

        return self.__inverse_transfer_function

    @inverse_transfer_function.setter
    def inverse_transfer_function(self, value):
        """
        Setter for **self.__inverse_transfer_function** private attribute.

        Parameters
        ----------
        value : object
            Attribute value.
        """

        if value is not None:
            assert hasattr(value, '__call__'), (
                '"{0}" attribute: "{1}" is not callable!'.format(
                    'inverse_transfer_function', value))
        self.__inverse_transfer_function = value


def XYZ_to_RGB(XYZ,
               illuminant_XYZ,
               illuminant_RGB,
               XYZ_to_RGB_matrix,
               chromatic_adaptation_transform='CAT02',
               transfer_function=None):
    """
    Converts from *CIE XYZ* colourspace to *RGB* colourspace using given
    *CIE XYZ* colourspace matrix, *illuminants*, *chromatic adaptation* method,
    *normalised primary matrix* and *transfer function*.

    Parameters
    ----------
    XYZ : array_like, (3,)
        *CIE XYZ* colourspace matrix.
    illuminant_XYZ : array_like
        *CIE XYZ* colourspace *illuminant* *xy* chromaticity coordinates.
    illuminant_RGB : array_like
        *RGB* colourspace *illuminant* *xy* chromaticity coordinates.
    XYZ_to_RGB_matrix : array_like, (3, 3)
        *Normalised primary matrix*.
    chromatic_adaptation_transform : unicode, optional
        {'CAT02', 'XYZ Scaling', 'Von Kries', 'Bradford', 'Sharp', 'Fairchild,
        'CMCCAT97', 'CMCCAT2000', 'CAT02_BRILL_CAT', 'Bianco', 'Bianco PC'},
        *Chromatic adaptation* transform.
    transfer_function : object, optional
        *Transfer function*.

    Returns
    -------
    ndarray, (3,)
        *RGB* colourspace matrix.

    Notes
    -----
    -   Input *CIE XYZ* colourspace matrix is in domain [0, 1].
    -   Input *illuminant_XYZ* *xy* chromaticity coordinates are in domain
        [0, 1].
    -   Input *illuminant_RGB* *xy* chromaticity coordinates are in domain
        [0, 1].
    -   Output *RGB* colourspace matrix is in domain [0, 1].

    Examples
    --------
    >>> XYZ = np.array([0.07049534, 0.1008, 0.09558313])
    >>> illuminant_XYZ = (0.34567, 0.35850)
    >>> illuminant_RGB = (0.31271, 0.32902)
    >>> chromatic_adaptation_transform = 'Bradford'
    >>> XYZ_to_RGB_matrix = np.array([
    ...     [3.24100326, -1.53739899, -0.49861587],
    ...     [-0.96922426, 1.87592999, 0.04155422],
    ...     [0.05563942, -0.2040112, 1.05714897]])
    >>> XYZ_to_RGB(
    ...     XYZ,
    ...     illuminant_XYZ,
    ...     illuminant_RGB,
    ...     XYZ_to_RGB_matrix,
    ...     chromatic_adaptation_transform)  # doctest: +ELLIPSIS
    array([ 0.0110360...,  0.1273446...,  0.1163103...])
    """

    XYZ = np.ravel(XYZ)

    cat = chromatic_adaptation_matrix_VonKries(
        xy_to_XYZ(illuminant_XYZ),
        xy_to_XYZ(illuminant_RGB),
        transform=chromatic_adaptation_transform)

    XYZ_a = np.dot(cat, XYZ)

    RGB = np.dot(XYZ_to_RGB_matrix.reshape((3, 3)),
                 XYZ_a.reshape((3, 1)))

    RGB = np.ravel(RGB)

    if transfer_function is not None:
        RGB = np.array([transfer_function(x) for x in RGB])

    return RGB


def RGB_to_XYZ(RGB,
               illuminant_RGB,
               illuminant_XYZ,
               RGB_to_XYZ_matrix,
               chromatic_adaptation_transform='CAT02',
               inverse_transfer_function=None):
    """
    Converts from *RGB* colourspace to *CIE XYZ* colourspace using given
    *RGB* colourspace matrix, *illuminants*, *chromatic adaptation* method,
    *normalised primary matrix* and *transfer function*.

    Parameters
    ----------
    RGB : array_like, (3,)
        *RGB* colourspace matrix.
    illuminant_RGB : array_like
        *RGB* colourspace *illuminant* chromaticity coordinates.
    illuminant_XYZ : array_like
        *CIE XYZ* colourspace *illuminant* chromaticity coordinates.
    RGB_to_XYZ_matrix : array_like, (3, 3)
        *Normalised primary matrix*.
    chromatic_adaptation_transform : unicode, optional
        {'CAT02', 'XYZ Scaling', 'Von Kries', 'Bradford', 'Sharp', 'Fairchild,
        'CMCCAT97', 'CMCCAT2000', 'CAT02_BRILL_CAT', 'Bianco', 'Bianco PC'},
        *Chromatic adaptation* transform.
    inverse_transfer_function : object, optional
        *Inverse transfer function*.

    Returns
    -------
    ndarray, (3,)
        *CIE XYZ* colourspace matrix.

    Notes
    -----
    -   Input *RGB* colourspace matrix is in domain [0, 1].
    -   Input *illuminant_RGB* *xy* chromaticity coordinates are in domain
        [0, 1].
    -   Input *illuminant_XYZ* *xy* chromaticity coordinates are in domain
        [0, 1].
    -   Output *CIE XYZ* colourspace matrix is in domain [0, 1].

    Examples
    --------
    >>> RGB = np.array([0.01103604, 0.12734466, 0.11631037])
    >>> illuminant_RGB = (0.31271, 0.32902)
    >>> illuminant_XYZ = (0.34567, 0.35850)
    >>> chromatic_adaptation_transform = 'Bradford'
    >>> RGB_to_XYZ_matrix = np.array([
    ...     [0.41238656, 0.35759149, 0.18045049],
    ...     [0.21263682, 0.71518298, 0.0721802],
    ...     [0.01933062, 0.11919716, 0.95037259]])
    >>> RGB_to_XYZ(
    ...     RGB,
    ...     illuminant_RGB,
    ...     illuminant_XYZ,
    ...     RGB_to_XYZ_matrix,
    ...     chromatic_adaptation_transform)  # doctest: +ELLIPSIS
    array([ 0.0704953...,  0.1008    ,  0.0955831...])
    """

    RGB = np.ravel(RGB)

    if inverse_transfer_function is not None:
        RGB = np.array([inverse_transfer_function(x) for x in RGB])

    XYZ = np.dot(RGB_to_XYZ_matrix.reshape((3, 3)), RGB.reshape((3, 1)))

    cat = chromatic_adaptation_matrix_VonKries(
        xy_to_XYZ(illuminant_RGB),
        xy_to_XYZ(illuminant_XYZ),
        transform=chromatic_adaptation_transform)

    XYZ_a = np.dot(cat, XYZ.reshape((3, 1)))

    return np.ravel(XYZ_a)


def RGB_to_RGB(RGB,
               input_colourspace,
               output_colourspace,
               chromatic_adaptation_transform='CAT02'):
    """
    Converts from given input *RGB* colourspace to output *RGB* colourspace
    using given *chromatic adaptation* method.

    Parameters
    ----------
    RGB : array_like, (3,)
        *RGB* colourspace matrix.
    input_colourspace : RGB_Colourspace
        *RGB* input colourspace.
    output_colourspace : RGB_Colourspace
        *RGB* output colourspace.
    chromatic_adaptation_transform : unicode, optional
        {'CAT02', 'XYZ Scaling', 'Von Kries', 'Bradford', 'Sharp', 'Fairchild,
        'CMCCAT97', 'CMCCAT2000', 'CAT02_BRILL_CAT', 'Bianco', 'Bianco PC'},
        *Chromatic adaptation* transform.

    ndarray, (3,)
        *RGB* colourspace matrix.

    Notes
    -----
    -   *RGB* colourspace matrices are in domain [0, 1].

    Examples
    --------
    >>> from colour import sRGB_COLOURSPACE, PROPHOTO_RGB_COLOURSPACE
    >>> RGB = np.array([0.01103604, 0.12734466, 0.11631037])
    >>> RGB_to_RGB(
    ...     RGB,
    ...     sRGB_COLOURSPACE,
    ...     PROPHOTO_RGB_COLOURSPACE)  # doctest: +ELLIPSIS
    array([ 0.0643338...,  0.1157362...,  0.1157614...])
    """

    RGB = np.ravel(RGB)

    cat = chromatic_adaptation_matrix_VonKries(
        xy_to_XYZ(input_colourspace.whitepoint),
        xy_to_XYZ(output_colourspace.whitepoint),
        chromatic_adaptation_transform)

    M = np.dot(output_colourspace.XYZ_to_RGB_matrix,
               np.dot(cat, input_colourspace.RGB_to_XYZ_matrix))

    return np.dot(M, RGB)
