#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines unit tests for :mod:`colour.difference.delta_e` module.
"""

from __future__ import division, unicode_literals

import numpy as np
import sys

if sys.version_info[:2] <= (2, 6):
    import unittest2 as unittest
else:
    import unittest

import colour.difference.delta_e

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['TestDelta_E_CIE1976',
           'TestDelta_E_CIE1994',
           'TestDelta_E_CIE2000',
           'TestDelta_E_CMC']


class TestDelta_E_CIE1976(unittest.TestCase):
    """
    Defines :func:`colour.difference.delta_e.delta_E_CIE1976`
    definition unit tests methods.
    """

    def test_delta_E_CIE1976(self):
        """
        Tests :func:`colour.difference.delta_e.delta_E_CIE1976`
        definition.
        """

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1976(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 426.67945353, 72.39590835])),
            451.713301974,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1976(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 74.05216981, 276.45318193])),
            52.6498611564,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1976(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 8.32281957, -73.58297716])),
            346.064891718,
            places=7)


class TestDelta_E_CIE1994(unittest.TestCase):
    """
    Defines :func:`colour.difference.delta_e.delta_E_CIE1994` definition
    unit tests methods.
    """

    def test_delta_E_CIE1994(self):
        """
        Tests :func:`colour.difference.delta_e.delta_E_CIE1994` definition.
        """

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1994(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 426.67945353, 72.39590835])),
            88.3355530575,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1994(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 74.05216981, 276.45318193])),
            10.61265789,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1994(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 8.32281957, -73.58297716])),
            60.3686872611,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1994(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 426.67945353, 72.39590835]),
                textiles=False),
            83.7792255009,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1994(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 74.05216981, 276.45318193]),
                textiles=False),
            10.0539319546,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE1994(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 8.32281957, -73.58297716]),
                textiles=False),
            57.5354537067,
            places=7)


class TestDelta_E_CIE2000(unittest.TestCase):
    """
    Defines :func:`colour.difference.delta_e.delta_E_CIE2000` definition
    unit tests methods.
    """

    def test_delta_E_CIE2000(self):
        """
        Tests :func:`colour.difference.delta_e.delta_E_CIE2000` definition.
        """

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE2000(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 426.67945353, 72.39590835])),
            94.0356490267,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE2000(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 74.05216981, 276.45318193])),
            14.8790641937,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CIE2000(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 8.32281957, -73.58297716])),
            68.2309487895,
            places=7)


class TestDelta_E_CMC(unittest.TestCase):
    """
    Defines :func:`colour.difference.delta_e.delta_E_CMC` definition units
    tests methods.
    """

    def test_delta_E_CMC(self):
        """
        Tests :func:`colour.difference.delta_e.delta_E_CMC` definition.
        """

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CMC(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 426.67945353, 72.39590835])),
            172.704771287,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CMC(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 74.05216981, 276.45318193])),
            20.5973271674,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CMC(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 8.32281957, -73.58297716])),
            121.718414791,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CMC(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 426.67945353, 72.39590835]),
                l=1),
            172.704771287,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CMC(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 74.05216981, 276.45318193]),
                l=1),
            20.5973271674,
            places=7)

        self.assertAlmostEqual(
            colour.difference.delta_e.delta_E_CMC(
                np.array([100, 21.57210357, 272.2281935]),
                np.array([100, 8.32281957, -73.58297716]),
                l=1),
            121.718414791,
            places=7)


if __name__ == '__main__':
    unittest.main()
