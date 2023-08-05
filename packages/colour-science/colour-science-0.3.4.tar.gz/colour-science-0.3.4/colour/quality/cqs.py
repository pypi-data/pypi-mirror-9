#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Colour Quality Scale
====================

Defines *colour quality scale* computation objects:

-   :class:`CQS_Specification`
-   :func:`colour_quality_scale`

See Also
--------
`Colour Quality Scale IPython Notebook
<http://nbviewer.ipython.org/github/colour-science/colour-ipython/blob/master/notebooks/quality/cqs.ipynb>`_  # noqa

References
----------
.. [1]  Davis, W., & Ohno, Y. (2010). Color quality scale. Optical
        Engineering, 49(3), 33602–33616. doi:10.1117/1.3360335

.. [2]  Ohno, Y., & Davis, W. (2008). NIST CQS simulation 7.4. Retrieved from
        http://cie2.nist.gov/TC1-69/NIST CQS simulation 7.4.xls
"""

from __future__ import division, unicode_literals

import numpy as np
from collections import namedtuple

from colour.colorimetry import STANDARD_OBSERVERS_CMFS
from colour.colorimetry import (
    ILLUMINANTS,
    D_illuminant_relative_spd,
    blackbody_spd,
    spectral_to_XYZ)
from colour.quality.dataset.vs import VS_SPDS, VS_INDEXES_TO_NAMES
from colour.models import (
    UCS_to_uv,
    XYZ_to_UCS,
    XYZ_to_xy,
    XYZ_to_Lab,
    Lab_to_LCHab,
    xy_to_XYZ)
from colour.temperature import CCT_to_xy_CIE_D, uv_to_CCT_Ohno2013
from colour.adaptation import chromatic_adaptation_VonKries

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['D65_GAMUT_AREA',
           'VS_ColorimetryData',
           'VS_ColourQualityScaleData',
           'CQS_Specification',
           'colour_quality_scale',
           'gamut_area']

D65_GAMUT_AREA = 8210


class VS_ColorimetryData(namedtuple('VS_ColorimetryData',
                                    ('name', 'XYZ', 'Lab', 'C'))):
    """
    Defines the the class holding *VS test colour samples* colorimetry data.
    """


class VS_ColourQualityScaleData(
    namedtuple('VS_ColourQualityScaleData',
               ('name', 'Q_a', 'D_C_ab', 'D_E_ab', 'D_Ep_ab'))):
    """
    Defines the the class holding *VS test colour samples* colour quality
    scale data.
    """


class CQS_Specification(
    namedtuple(
        'CQS_Specification',
        ('Q_a', 'Q_f', 'Q_p', 'Q_g', 'Q_d', 'Q_as', 'colorimetry_data'))):
    """
    Defines the *CQS* colour quality specification.

    Parameters
    ----------
    Q_a : numeric
        Colour quality scale :math:`Q_a`.
    Q_f : numeric
        Colour fidelity scale :math:`Q_f` intended to evaluate the fidelity
        of object colour appearances (compared to the reference illuminant of
        the same correlated colour temperature and illuminance).
    Q_p : numeric
        Colour preference scale :math:`Q_p` similar to colour quality scale
        :math:`Q_a` but placing additional weight on preference of object
        colour appearance. This metric is based on the notion that increases
        in chroma are generally preferred and should be rewarded.
    Q_g : numeric
         Gamut area scale :math:`Q_g` representing the relative gamut formed
         by the (:math:`a^*`, :math:`b^*`) coordinates of the 15 samples
         illuminated by the test light source in the *CIE LAB* object
         colourspace.
    Q_d : numeric
        Relative gamut area scale :math:`Q_d`.
    Q_as : dict
        Individual *CQS* data for each sample.
    colorimetry_data : tuple
        Colorimetry data for the test and reference computations.
    """


def colour_quality_scale(spd_test, additional_data=False):
    """
    Returns the *colour quality scale* of given spectral power distribution.

    Parameters
    ----------
    spd_test : SpectralPowerDistribution
        Test spectral power distribution.
    additional_data : bool, optional
        Output additional data.

    Returns
    -------
    numeric or CQS_Specification
        Color quality scale.

    Examples
    --------
    >>> from colour import ILLUMINANTS_RELATIVE_SPDS
    >>> spd = ILLUMINANTS_RELATIVE_SPDS.get('F2')
    >>> colour_quality_scale(spd)  # doctest: +ELLIPSIS
    64.6860580...
    """

    cmfs = STANDARD_OBSERVERS_CMFS.get(
        'CIE 1931 2 Degree Standard Observer')

    shape = cmfs.shape
    spd_test = spd_test.clone().align(shape)

    vs_spds = {}
    for index, vs_spd in VS_SPDS.items():
        vs_spds[index] = vs_spd.clone().align(shape)

    XYZ = spectral_to_XYZ(spd_test, cmfs)
    uv = UCS_to_uv(XYZ_to_UCS(XYZ))
    CCT, _ = uv_to_CCT_Ohno2013(uv)

    if CCT < 5000:
        spd_reference = blackbody_spd(CCT, shape)
    else:
        xy = CCT_to_xy_CIE_D(CCT)
        spd_reference = D_illuminant_relative_spd(xy)
        spd_reference.align(shape)

    test_vs_colorimetry_data = _vs_colorimetry_data(
        spd_test,
        spd_reference,
        vs_spds,
        cmfs,
        chromatic_adaptation=True)

    reference_vs_colorimetry_data = _vs_colorimetry_data(
        spd_reference,
        spd_reference,
        vs_spds,
        cmfs)

    XYZ_r = spectral_to_XYZ(spd_reference, cmfs)
    XYZ_r /= XYZ_r[1]
    CCT_factor = _CCT_factor(reference_vs_colorimetry_data, XYZ_r)

    Q_as = _colour_quality_scales(
        test_vs_colorimetry_data, reference_vs_colorimetry_data, CCT_factor)

    D_E_RMS = _delta_E_RMS(Q_as, 'D_E_ab')
    D_Ep_RMS = _delta_E_RMS(Q_as, 'D_Ep_ab')

    Q_a = _scale_conversion(D_Ep_RMS, CCT_factor)
    Q_f = _scale_conversion(D_E_RMS, CCT_factor, 2.928)

    p_delta_C = np.average(
        [sample_data.D_C_ab if sample_data.D_C_ab > 0 else 0
         for sample_data in
         Q_as.values()])
    Q_p = 100 - 3.6 * (D_Ep_RMS - p_delta_C)

    G_t = gamut_area([vs_CQS_data.Lab
                      for vs_CQS_data in test_vs_colorimetry_data])
    G_r = gamut_area([vs_CQS_data.Lab
                      for vs_CQS_data in reference_vs_colorimetry_data])

    Q_g = G_t / D65_GAMUT_AREA * 100
    Q_d = G_t / G_r * CCT_factor * 100

    if additional_data:
        return CQS_Specification(Q_a,
                                 Q_f,
                                 Q_p,
                                 Q_g,
                                 Q_d,
                                 Q_as,
                                 (test_vs_colorimetry_data,
                                  reference_vs_colorimetry_data))
    else:
        return Q_a


def gamut_area(Labs):
    """
    Returns the gamut area :math:`G` covered by given *CIE Lab* matrices.

    Parameters
    ----------
    Labs : array_like
        *CIE Lab* colourspace matrices.

    Returns
    -------
    numeric
        Gamut area :math:`G`.

    Examples
    --------
    >>> Labs = [
    ...     np.array([39.94996006, 34.59018231, -19.86046321]),
    ...     np.array([38.88395498, 21.44348519, -34.87805301]),
    ...     np.array([36.60576301, 7.06742454, -43.21461177]),
    ...     np.array([46.60142558, -15.90481586, -34.64616865]),
    ...     np.array([56.50196523, -29.5465555, -20.50177194]),
    ...     np.array([55.73912101, -43.39520959, -5.08956953]),
    ...     np.array([56.2077687, -53.68997662, 20.2113441]),
    ...     np.array([66.16683122, -38.64600327, 42.77396631]),
    ...     np.array([76.7295211, -23.9214821, 61.04740432]),
    ...     np.array([82.85370708, -3.98679065, 75.43320144]),
    ...     np.array([69.26458861, 13.11066359, 68.83858372]),
    ...     np.array([69.63154351, 28.24532497, 59.45609803]),
    ...     np.array([61.26281449, 40.87950839, 44.97606172]),
    ...     np.array([41.62567821, 57.34129516, 27.4671817]),
    ...     np.array([40.52565174, 48.87449192, 3.4512168])]
    >>> gamut_area(Labs)  # doctest: +ELLIPSIS
    8335.9482018...
    """

    Labs_s = Labs[:]
    Labs_s.append(Labs_s.pop(0))

    G = 0
    for i, _ in enumerate(Labs):
        L, a, b = Labs[i]
        L_s, a_s, b_s = Labs_s[i]

        A = np.sqrt(a ** 2 + b ** 2)
        B = np.sqrt(a_s ** 2 + b_s ** 2)
        C = np.sqrt((a_s - a) ** 2 + (b_s - b) ** 2)
        t = (A + B + C) / 2
        S = np.sqrt(t * (t - A) * (t - B) * (t - C))
        G += S

    return G


def _vs_colorimetry_data(spd_test,
                         spd_reference,
                         spds_vs,
                         cmfs,
                         chromatic_adaptation=False):
    """
    Returns the *VS test colour samples* colorimetry data.

    Parameters
    ----------
    spd_test : SpectralPowerDistribution
        Test spectral power distribution.
    spd_reference : SpectralPowerDistribution
        Reference spectral power distribution.
    spds_vs : dict
        *VS test colour samples* spectral power distributions.
    cmfs : XYZ_ColourMatchingFunctions
        Standard observer colour matching functions.
    chromatic_adaptation : bool, optional
        Perform chromatic adaptation.

    Returns
    -------
    list
        *VS test colour samples* colorimetry data.
    """

    XYZ_t = spectral_to_XYZ(spd_test, cmfs)
    XYZ_t /= XYZ_t[1]

    XYZ_r = spectral_to_XYZ(spd_reference, cmfs)
    XYZ_r /= XYZ_r[1]
    xy_r = XYZ_to_xy(XYZ_r)

    vs_data = []
    for key, value in sorted(VS_INDEXES_TO_NAMES.items()):
        spd_vs = spds_vs.get(value)
        XYZ_vs = spectral_to_XYZ(spd_vs, cmfs, spd_test)
        XYZ_vs /= 100

        if chromatic_adaptation:
            XYZ_vs = chromatic_adaptation_VonKries(XYZ_vs,
                                                   XYZ_t,
                                                   XYZ_r,
                                                   transform='CMCCAT2000')

        Lab_vs = XYZ_to_Lab(XYZ_vs, illuminant=xy_r)
        _, chroma_vs, _ = Lab_to_LCHab(Lab_vs)

        vs_data.append(
            VS_ColorimetryData(spd_vs.name,
                               XYZ_vs,
                               Lab_vs,
                               chroma_vs))
    return vs_data


def _CCT_factor(reference_data, XYZ_r):
    """
    Returns the correlated colour temperature factor penalizing lamps with
    extremely low correlated colour temperatures.

    Parameters
    ----------
    reference_data : VS_ColorimetryData
        Reference colorimetry data.
    XYZ_r : array_like
        *CIE XYZ* colourspace matrix for reference.

    Returns
    -------
    numeric
        Correlated colour temperature factor.
    """

    xy_w = ILLUMINANTS.get('CIE 1931 2 Degree Standard Observer').get('D65')
    XYZ_w = xy_to_XYZ(xy_w)

    Labs = []
    for vs_colorimetry_data in reference_data:
        _, XYZ, _, _ = vs_colorimetry_data
        XYZ_a = chromatic_adaptation_VonKries(XYZ,
                                              XYZ_r,
                                              XYZ_w,
                                              transform='CMCCAT2000')

        Lab = XYZ_to_Lab(XYZ_a, illuminant=xy_w)
        Labs.append(Lab)

    G_r = gamut_area(Labs) / D65_GAMUT_AREA
    CCT_factor = 1 if G_r > 1 else G_r

    return CCT_factor


def _scale_conversion(D_E_ab, CCT_factor, scaling_factor=3.104):
    """
    Returns the correlated colour temperature factor penalizing lamps with
    extremely low correlated colour temperatures.

    Parameters
    ----------
    reference_data : VS_ColorimetryData
        Reference colorimetry data.
    spd_reference : SpectralPowerDistribution
        Reference spectral power distribution.
    cmfs : XYZ_ColourMatchingFunctions
        Standard observer colour matching functions.

    Returns
    -------
    numeric
        Correlated colour temperature factor.
    """

    Q_a = (10 * np.log(np.exp((100 - scaling_factor * D_E_ab) / 10) + 1) *
           CCT_factor)

    return Q_a


def _delta_E_RMS(cqs_data, attribute):
    """
    Computes the root-mean-square average for given *CQS* data.

    Parameters
    ----------
    cqs_data : VS_ColourQualityScaleData
        *CQS* data.
    attribute : unicode
        Colorimetry data attribute to use to compute the root-mean-square
        average.

    Returns
    -------
    numeric
        Root-mean-square average.
    """

    return np.sqrt(1 / len(cqs_data) *
                   np.sum([getattr(sample_data, attribute) ** 2
                           for sample_data in
                           cqs_data.values()]))


def _colour_quality_scales(test_data, reference_data, CCT_factor):
    """
    Returns the *VS test colour samples* rendering scales.

    Parameters
    ----------
    test_data : list
        Test data.
    reference_data : list
        Reference data.
    CCT_factor : numeric
        Factor penalizing lamps with extremely low correlated colour
        temperatures.

    Returns
    -------
    dict
        *VS Test colour samples* colour rendering scales.
    """

    colour_quality_scales = {}
    for i, _ in enumerate(test_data):
        D_C_ab = test_data[i].C - reference_data[i].C
        D_E_ab = np.sqrt(
            np.sum((test_data[i].Lab - reference_data[i].Lab) ** 2))

        if D_C_ab > 0:
            D_Ep_ab = np.sqrt(D_E_ab ** 2 - D_C_ab ** 2)
        else:
            D_Ep_ab = D_E_ab

        Q_a = _scale_conversion(D_Ep_ab, CCT_factor)

        colour_quality_scales[i + 1] = VS_ColourQualityScaleData(
            test_data[i].name, Q_a, D_C_ab, D_E_ab, D_Ep_ab)
    return colour_quality_scales
