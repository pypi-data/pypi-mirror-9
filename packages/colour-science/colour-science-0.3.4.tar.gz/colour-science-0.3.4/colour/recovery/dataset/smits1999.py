#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Smits (1999) - Reflectance Recovery Dataset
===========================================

Defines the dataset for reflectance recovery using Smits (1999) method.

References
----------
.. [1]  Smits, B. (1999). An RGB-to-Spectrum Conversion for Reflectances.
        Journal of Graphics Tools, 4(4), 11–22.
        doi:10.1080/10867651.1999.10487511
"""

from __future__ import division, unicode_literals

from colour.colorimetry.spectrum import SpectralPowerDistribution
from colour.utilities import CaseInsensitiveMapping

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['SMITS_1999_SPDS_DATA',
           'SMITS_1999_SPDS']

SMITS_1999_SPDS_DATA = {
    'white': {
        380.0: 1.0,
        417.7778: 1.0,
        455.5556: 0.9999,
        493.3333: 0.9993,
        531.1111: 0.9992,
        568.8889: 0.9998,
        606.6667: 1.0,
        644.4444: 1.0,
        682.2222: 1.0,
        720.0: 1.0},
    'cyan': {
        380.0: 0.971,
        417.7778: 0.9426,
        455.5556: 1.0007,
        493.3333: 1.0007,
        531.1111: 1.0007,
        568.8889: 1.0007,
        606.6667: 0.1564,
        644.4444: 0.0,
        682.2222: 0.0,
        720.0: 0.0},
    'magenta': {
        380.0: 1.0,
        417.7778: 1.0,
        455.5556: 0.9685,
        493.3333: 0.2229,
        531.1111: 0.0,
        568.8889: 0.0458,
        606.6667: 0.8369,
        644.4444: 1.0,
        682.2222: 1.0,
        720.0: 0.9959},
    'yellow': {
        380.0: 0.0001,
        417.7778: 0.0,
        455.5556: 0.1088,
        493.3333: 0.6651,
        531.1111: 1.0,
        568.8889: 1.0,
        606.6667: 0.9996,
        644.4444: 0.9586,
        682.2222: 0.9685,
        720.0: 0.984},
    'red': {
        380.0: 0.1012,
        417.7778: 0.0515,
        455.5556: 0.0,
        493.3333: 0.0,
        531.1111: 0.0,
        568.8889: 0.0,
        606.6667: 0.8325,
        644.4444: 1.0149,
        682.2222: 1.0149,
        720.0: 1.0149},
    'green': {
        380.0: 0.0,
        417.7778: 0.0,
        455.5556: 0.0273,
        493.3333: 0.7937,
        531.1111: 1.0,
        568.8889: 0.9418,
        606.6667: 0.1719,
        644.4444: 0.0,
        682.2222: 0.0,
        720.0: 0.0025},
    'blue': {
        380.0: 1.0,
        417.7778: 1.0,
        455.5556: 0.8916,
        493.3333: 0.3323,
        531.1111: 0.0,
        568.8889: 0.0,
        606.6667: 0.0003,
        644.4444: 0.0369,
        682.2222: 0.0483,
        720.0: 0.0496}}

SMITS_1999_SPDS = CaseInsensitiveMapping({
    'white': SpectralPowerDistribution(
        'white', SMITS_1999_SPDS_DATA.get('white')),
    'cyan': SpectralPowerDistribution(
        'cyan', SMITS_1999_SPDS_DATA.get('cyan')),
    'magenta': SpectralPowerDistribution(
        'magenta', SMITS_1999_SPDS_DATA.get('magenta')),
    'yellow': SpectralPowerDistribution(
        'yellow', SMITS_1999_SPDS_DATA.get('yellow')),
    'red': SpectralPowerDistribution(
        'red', SMITS_1999_SPDS_DATA.get('red')),
    'green': SpectralPowerDistribution(
        'green', SMITS_1999_SPDS_DATA.get('green')),
    'blue': SpectralPowerDistribution(
        'blue', SMITS_1999_SPDS_DATA.get('blue'))})
"""
Smits (1999) spectral power distributions.

SMITS_1999_SPDS : CaseInsensitiveMapping
"""
