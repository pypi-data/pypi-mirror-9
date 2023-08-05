#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines unit tests for :mod:`colour.algebra.interpolation` module.
"""

from __future__ import division, unicode_literals

import numpy as np
import sys

if sys.version_info[:2] <= (2, 6):
    import unittest2 as unittest
else:
    import unittest

from colour.algebra import LinearInterpolator1d
from colour.algebra import SpragueInterpolator

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['POINTS_DATA_A',
           'LINEAR_INTERPOLATED_POINTS_DATA_A_10_SAMPLES',
           'SPRAGUE_INTERPOLATED_POINTS_DATA_A_10_SAMPLES',
           'TestLinearInterpolator1d',
           'TestSpragueInterpolator']

POINTS_DATA_A = np.array([
    9.3700,
    12.3200,
    12.4600,
    9.5100,
    5.9200,
    4.3300,
    4.2900,
    3.8800,
    4.5100,
    10.9200,
    27.5000,
    49.6700,
    69.5900,
    81.7300,
    88.1900,
    86.0500])

LINEAR_INTERPOLATED_POINTS_DATA_A_10_SAMPLES = [
    9.37,
    9.665,
    9.96,
    10.255,
    10.55,
    10.845,
    11.14,
    11.435,
    11.73,
    12.025,
    12.32,
    12.334,
    12.348,
    12.362,
    12.376,
    12.39,
    12.404,
    12.418,
    12.432,
    12.446,
    12.46,
    12.165,
    11.87,
    11.575,
    11.28,
    10.985,
    10.69,
    10.395,
    10.1,
    9.805,
    9.51,
    9.151,
    8.792,
    8.433,
    8.074,
    7.715,
    7.356,
    6.997,
    6.638,
    6.279,
    5.92,
    5.761,
    5.602,
    5.443,
    5.284,
    5.125,
    4.966,
    4.807,
    4.648,
    4.489,
    4.33,
    4.326,
    4.322,
    4.318,
    4.314,
    4.31,
    4.306,
    4.302,
    4.298,
    4.294,
    4.29,
    4.249,
    4.208,
    4.167,
    4.126,
    4.085,
    4.044,
    4.003,
    3.962,
    3.921,
    3.88,
    3.943,
    4.006,
    4.069,
    4.132,
    4.195,
    4.258,
    4.321,
    4.384,
    4.447,
    4.51,
    5.151,
    5.792,
    6.433,
    7.074,
    7.715,
    8.356,
    8.997,
    9.638,
    10.279,
    10.92,
    12.578,
    14.236,
    15.894,
    17.552,
    19.21,
    20.868,
    22.526,
    24.184,
    25.842,
    27.5,
    29.717,
    31.934,
    34.151,
    36.368,
    38.585,
    40.802,
    43.019,
    45.236,
    47.453,
    49.67,
    51.662,
    53.654,
    55.646,
    57.638,
    59.63,
    61.622,
    63.614,
    65.606,
    67.598,
    69.59,
    70.804,
    72.018,
    73.232,
    74.446,
    75.66,
    76.874,
    78.088,
    79.302,
    80.516,
    81.73,
    82.376,
    83.022,
    83.668,
    84.314,
    84.96,
    85.606,
    86.252,
    86.898,
    87.544,
    88.19,
    87.976,
    87.762,
    87.548,
    87.334,
    87.12,
    86.906,
    86.692,
    86.478,
    86.264,
    86.05]

SPRAGUE_INTERPOLATED_POINTS_DATA_A_10_SAMPLES = [
    9.37,
    9.72075073,
    10.06936191,
    10.4114757,
    10.7430227,
    11.06022653,
    11.35960827,
    11.637991,
    11.89250427,
    12.1205886,
    12.32,
    12.48873542,
    12.62489669,
    12.7270653,
    12.79433478,
    12.82623598,
    12.82266243,
    12.78379557,
    12.71003009,
    12.60189921,
    12.46,
    12.28440225,
    12.074048,
    11.829765,
    11.554432,
    11.25234375,
    10.928576,
    10.5883505,
    10.2364,
    9.87633325,
    9.51,
    9.13692962,
    8.756208,
    8.36954763,
    7.980976,
    7.59601562,
    7.220864,
    6.86157362,
    6.523232,
    6.20914162,
    5.92,
    5.654602,
    5.414496,
    5.20073875,
    5.012944,
    4.8496875,
    4.708912,
    4.58833225,
    4.48584,
    4.399909,
    4.33,
    4.27757887,
    4.245952,
    4.23497388,
    4.240992,
    4.25804688,
    4.279072,
    4.29709387,
    4.306432,
    4.30389887,
    4.29,
    4.26848387,
    4.240432,
    4.20608887,
    4.166032,
    4.12117188,
    4.072752,
    4.02234887,
    3.971872,
    3.92356387,
    3.88,
    3.84319188,
    3.813184,
    3.79258487,
    3.786912,
    3.80367187,
    3.85144,
    3.93894087,
    4.074128,
    4.26326387,
    4.51,
    4.81362075,
    5.170288,
    5.5822515,
    6.05776,
    6.60890625,
    7.249472,
    7.992773,
    8.849504,
    9.82558375,
    10.92,
    12.12700944,
    13.448928,
    14.88581406,
    16.432832,
    18.08167969,
    19.822016,
    21.64288831,
    23.53416,
    25.48793794,
    27.5,
    29.57061744,
    31.699648,
    33.88185481,
    36.107776,
    38.36511719,
    40.640144,
    42.91907456,
    45.189472,
    47.44163694,
    49.67,
    51.87389638,
    54.052736,
    56.20157688,
    58.311984,
    60.37335938,
    62.374272,
    64.30378787,
    66.1528,
    67.91535838,
    69.59,
    71.17616669,
    72.662832,
    74.04610481,
    75.331712,
    76.53183594,
    77.661952,
    78.73766606,
    79.771552,
    80.76998919,
    81.73,
    82.64375688,
    83.51935227,
    84.35919976,
    85.15567334,
    85.89451368,
    86.55823441,
    87.12952842,
    87.59467414,
    87.94694187,
    88.19,
    88.33345751,
    88.37111372,
    88.30221714,
    88.13600972,
    87.88846516,
    87.57902706,
    87.2273472,
    86.85002373,
    86.45733945,
    86.05]


class TestLinearInterpolator1d(unittest.TestCase):
    """
    Defines
    :func:`colour.algebra.interpolation.LinearInterpolator1d` class units
    tests methods.
    """

    def test_required_attributes(self):
        """
        Tests presence of required attributes.
        """

        required_attributes = ('x',
                               'y')

        for attribute in required_attributes:
            self.assertIn(attribute, dir(LinearInterpolator1d))

    def test_required_methods(self):
        """
        Tests presence of required methods.
        """

        required_methods = ()

        for method in required_methods:
            self.assertIn(method, dir(LinearInterpolator1d))

    def test___call__(self):
        """
        Tests
        :func:`colour.algebra.interpolation.LinearInterpolator1d.__call__`
        method.
        """

        steps = 0.1
        x = np.arange(len(POINTS_DATA_A))
        linear_interpolator = LinearInterpolator1d(x, POINTS_DATA_A)

        for i, value in enumerate(
                np.arange(0, len(POINTS_DATA_A) - 1 + steps, steps)):
            self.assertAlmostEqual(
                LINEAR_INTERPOLATED_POINTS_DATA_A_10_SAMPLES[i],
                linear_interpolator(value),
                places=7)

        np.testing.assert_almost_equal(
            linear_interpolator(
                np.arange(0, len(POINTS_DATA_A) - 1 + steps, steps)),
            LINEAR_INTERPOLATED_POINTS_DATA_A_10_SAMPLES)


class TestSpragueInterpolator(unittest.TestCase):
    """
    Defines :func:`colour.algebra.interpolation.SpragueInterpolator` class
    unit tests methods.
    """

    def test_required_attributes(self):
        """
        Tests presence of required attributes.
        """

        required_attributes = ('x',
                               'y')

        for attribute in required_attributes:
            self.assertIn(attribute, dir(SpragueInterpolator))

    def test_required_methods(self):
        """
        Tests presence of required methods.
        """

        required_methods = ()

        for method in required_methods:
            self.assertIn(method, dir(SpragueInterpolator))

    def test___call__(self):
        """
        Tests :func:`colour.algebra.interpolation.SpragueInterpolator.__call__`
        method.
        """

        steps = 0.1
        x = np.arange(len(POINTS_DATA_A))
        sprague_interpolator = SpragueInterpolator(x, POINTS_DATA_A)

        for i, value in enumerate(
                np.arange(0, len(POINTS_DATA_A) - 1 + steps, steps)):
            self.assertAlmostEqual(
                SPRAGUE_INTERPOLATED_POINTS_DATA_A_10_SAMPLES[i],
                sprague_interpolator(value),
                places=7)

        np.testing.assert_almost_equal(
            sprague_interpolator(
                np.arange(0, len(POINTS_DATA_A) - 1 + steps, steps)),
            SPRAGUE_INTERPOLATED_POINTS_DATA_A_10_SAMPLES)


if __name__ == '__main__':
    unittest.main()
