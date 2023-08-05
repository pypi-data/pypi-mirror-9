#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Defines unit tests for :mod:`colour.phenomenons.rayleigh` module.
"""

from __future__ import division, unicode_literals

import numpy as np

import sys

if sys.version_info[:2] <= (2, 6):
    import unittest2 as unittest
else:
    import unittest

from colour.phenomenons.rayleigh import (
    air_refraction_index_Penndorf1957,
    air_refraction_index_Edlen1966,
    air_refraction_index_Peck1972,
    air_refraction_index_Bodhaine1999,
    N2_depolarisation,
    O2_depolarisation,
    F_air_Penndorf1957,
    F_air_Young1981,
    F_air_Bates1984,
    F_air_Bodhaine1999,
    molecular_density,
    mean_molecular_weights,
    gravity_List1968)
from colour.phenomenons import (
    scattering_cross_section,
    rayleigh_optical_depth,
    rayleigh_scattering_spd)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['RAYLEIGH_SCATTERING_SPD_DATA',
           'TestAirRefractionIndexPenndorf1957',
           'TestAirRefractionIndexEdlen1966',
           'TestAirRefractionIndexPeck1972',
           'TestAirRefractionIndexBodhaine1999',
           'TestN2Depolarisation',
           'TestO2Depolarisation',
           'TestF_airPenndorf1957',
           'TestF_airYoung1981',
           'TestF_airBates1984',
           'TestF_airBodhaine1999',
           'TestMolecularDensity',
           'TestMeanMolecularWeights',
           'TestGravityList1968',
           'TestScatteringCrossSection',
           'TestRayleighOpticalDepth',
           'TestRayleighScatteringSpd']

RAYLEIGH_SCATTERING_SPD_DATA = np.array([
    0.59910134,
    0.59217069,
    0.58534101,
    0.57861051,
    0.57197745,
    0.56544013,
    0.55899687,
    0.55264605,
    0.54638605,
    0.54021531,
    0.53413228,
    0.52813547,
    0.5222234,
    0.51639461,
    0.51064769,
    0.50498125,
    0.49939393,
    0.4938844,
    0.48845134,
    0.48309347,
    0.47780954,
    0.47259832,
    0.46745859,
    0.46238917,
    0.4573889,
    0.45245664,
    0.44759127,
    0.4427917,
    0.43805685,
    0.43338567,
    0.42877712,
    0.4242302,
    0.4197439,
    0.41531726,
    0.4109493,
    0.4066391,
    0.40238573,
    0.39818829,
    0.39404589,
    0.38995765,
    0.38592273,
    0.38194029,
    0.37800949,
    0.37412954,
    0.37029964,
    0.366519,
    0.36278687,
    0.3591025,
    0.35546514,
    0.35187408,
    0.3483286,
    0.344828,
    0.34137161,
    0.33795874,
    0.33458873,
    0.33126094,
    0.32797472,
    0.32472946,
    0.32152453,
    0.31835934,
    0.31523328,
    0.31214577,
    0.30909624,
    0.30608413,
    0.30310889,
    0.30016996,
    0.29726682,
    0.29439893,
    0.29156579,
    0.28876688,
    0.28600171,
    0.28326979,
    0.28057063,
    0.27790377,
    0.27526872,
    0.27266505,
    0.27009229,
    0.26755001,
    0.26503777,
    0.26255513,
    0.26010169,
    0.25767703,
    0.25528074,
    0.25291242,
    0.25057168,
    0.24825813,
    0.24597138,
    0.24371107,
    0.24147683,
    0.2392683,
    0.23708511,
    0.23492692,
    0.23279339,
    0.23068417,
    0.22859893,
    0.22653734,
    0.22449907,
    0.22248382,
    0.22049127,
    0.21852111,
    0.21657303,
    0.21464674,
    0.21274195,
    0.21085836,
    0.2089957,
    0.20715367,
    0.20533201,
    0.20353045,
    0.20174871,
    0.19998654,
    0.19824368,
    0.19651987,
    0.19481486,
    0.1931284,
    0.19146025,
    0.18981018,
    0.18817794,
    0.18656331,
    0.18496605,
    0.18338593,
    0.18182275,
    0.18027628,
    0.1787463,
    0.17723261,
    0.17573499,
    0.17425324,
    0.17278715,
    0.17133653,
    0.16990119,
    0.16848091,
    0.16707553,
    0.16568484,
    0.16430867,
    0.16294683,
    0.16159914,
    0.16026543,
    0.15894551,
    0.15763923,
    0.1563464,
    0.15506686,
    0.15380046,
    0.15254701,
    0.15130638,
    0.15007839,
    0.14886289,
    0.14765974,
    0.14646877,
    0.14528984,
    0.14412281,
    0.14296753,
    0.14182386,
    0.14069165,
    0.13957077,
    0.13846109,
    0.13736246,
    0.13627476,
    0.13519785,
    0.13413161,
    0.1330759,
    0.13203061,
    0.13099561,
    0.12997078,
    0.12895599,
    0.12795114,
    0.12695609,
    0.12597074,
    0.12499498,
    0.12402869,
    0.12307176,
    0.12212407,
    0.12118554,
    0.12025604,
    0.11933547,
    0.11842374,
    0.11752073,
    0.11662635,
    0.11574049,
    0.11486307,
    0.11399398,
    0.11313313,
    0.11228043,
    0.11143577,
    0.11059908,
    0.10977026,
    0.10894922,
    0.10813587,
    0.10733013,
    0.10653191,
    0.10574113,
    0.1049577,
    0.10418154,
    0.10341257,
    0.10265072,
    0.10189589,
    0.10114802,
    0.10040702,
    0.09967282,
    0.09894535,
    0.09822452,
    0.09751028,
    0.09680254,
    0.09610123,
    0.09540629,
    0.09471764,
    0.09403522,
    0.09335896,
    0.09268878,
    0.09202464,
    0.09136645,
    0.09071416,
    0.0900677,
    0.08942701,
    0.08879203,
    0.0881627,
    0.08753895,
    0.08692073,
    0.08630797,
    0.08570063,
    0.08509864,
    0.08450194,
    0.08391049,
    0.08332421,
    0.08274307,
    0.082167,
    0.08159596,
    0.08102988,
    0.08046872,
    0.07991243,
    0.07936096,
    0.07881425,
    0.07827225,
    0.07773493,
    0.07720222,
    0.07667408,
    0.07615047,
    0.07563133,
    0.07511663,
    0.07460631,
    0.07410033,
    0.07359865,
    0.07310122,
    0.072608,
    0.07211894,
    0.07163402,
    0.07115317,
    0.07067636,
    0.07020356,
    0.06973471,
    0.06926979,
    0.06880874,
    0.06835154,
    0.06789814,
    0.06744851,
    0.0670026,
    0.06656038,
    0.06612182,
    0.06568688,
    0.06525551,
    0.0648277,
    0.06440339,
    0.06398256,
    0.06356518,
    0.0631512,
    0.0627406,
    0.06233333,
    0.06192938,
    0.06152871,
    0.06113128,
    0.06073706,
    0.06034603,
    0.05995814,
    0.05957338,
    0.05919171,
    0.0588131,
    0.05843752,
    0.05806494,
    0.05769534,
    0.05732868,
    0.05696494,
    0.05660408,
    0.05624609,
    0.05589093,
    0.05553858,
    0.05518901,
    0.05484219,
    0.0544981,
    0.05415671,
    0.053818,
    0.05348194,
    0.05314851,
    0.05281768,
    0.05248942,
    0.05216372,
    0.05184055,
    0.05151988,
    0.0512017,
    0.05088598,
    0.05057269,
    0.05026182,
    0.04995333,
    0.04964722,
    0.04934346,
    0.04904202,
    0.04874288,
    0.04844603,
    0.04815144,
    0.0478591,
    0.04756897,
    0.04728105,
    0.0469953,
    0.04671172,
    0.04643028,
    0.04615096,
    0.04587374,
    0.04559861,
    0.04532554,
    0.04505452,
    0.04478553,
    0.04451855,
    0.04425355,
    0.04399054,
    0.04372947,
    0.04347035,
    0.04321315,
    0.04295785,
    0.04270444,
    0.0424529,
    0.04220321,
    0.04195537,
    0.04170934,
    0.04146512,
    0.04122268,
    0.04098202,
    0.04074312,
    0.04050596,
    0.04027053,
    0.04003681,
    0.03980479,
    0.03957445,
    0.03934578,
    0.03911876,
    0.03889338,
    0.03866963,
    0.03844748,
    0.03822694,
    0.03800797,
    0.03779058,
    0.03757474,
    0.03736044,
    0.03714767,
    0.03693642,
    0.03672667,
    0.03651841,
    0.03631163,
    0.03610632,
    0.03590245,
    0.03570003,
    0.03549903,
    0.03529945,
    0.03510128,
    0.03490449,
    0.03470909,
    0.03451505,
    0.03432237,
    0.03413104,
    0.03394104,
    0.03375237,
    0.033565,
    0.03337894,
    0.03319417,
    0.03301068,
    0.03282846,
    0.03264749,
    0.03246778,
    0.0322893,
    0.03211204,
    0.03193601,
    0.03176118,
    0.03158755,
    0.03141511,
    0.03124385,
    0.03107375,
    0.03090481,
    0.03073702,
    0.03057037,
    0.03040485,
    0.03024045,
    0.03007717,
    0.02991498,
    0.02975389,
    0.02959389,
    0.02943496,
    0.0292771,
    0.0291203,
    0.02896455,
    0.02880984,
    0.02865616,
    0.02850351,
    0.02835188,
    0.02820126,
    0.02805164,
    0.02790301,
    0.02775536,
    0.02760869,
    0.027463,
    0.02731826,
    0.02717448,
    0.02703164,
    0.02688975,
    0.02674878,
    0.02660874,
    0.02646962,
    0.02633141,
    0.0261941,
    0.02605768,
    0.02592215,
    0.02578751,
    0.02565374,
    0.02552084,
    0.0253888,
    0.02525761,
    0.02512727,
    0.02499778,
    0.02486911,
    0.02474128,
    0.02461427,
    0.02448807,
    0.02436268,
    0.0242381,
    0.02411431,
    0.02399131,
    0.0238691,
    0.02374767,
    0.02362701,
    0.02350711,
    0.02338798,
    0.0232696,
    0.02315197,
    0.02303509,
    0.02291894,
    0.02280353,
    0.02268884,
    0.02257487,
    0.02246162,
    0.02234908,
    0.02223725,
    0.02212612,
    0.02201568,
    0.02190593,
    0.02179686,
    0.02168847,
    0.02158076,
    0.02147372,
    0.02136734,
    0.02126162,
    0.02115655,
    0.02105213,
    0.02094836,
    0.02084523,
    0.02074273,
    0.02064086,
    0.02053962,
    0.020439,
    0.02033899,
    0.0202396,
    0.02014082,
    0.02004263,
    0.01994505,
    0.01984806,
    0.01975166,
    0.01965585])


class TestAirRefractionIndexPenndorf1957(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.air_refraction_index_Penndorf1957`
    definition unit tests methods.
    """

    def test_air_refraction_index_Penndorf1957(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.air_refraction_index_Penndorf1957`
        definition.
        """

        self.assertAlmostEqual(
            air_refraction_index_Penndorf1957(0.360),
            1.0002853167951464,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Penndorf1957(0.555),
            1.000277729533864,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Penndorf1957(0.830),
            1.000274856640486,
            places=10)


class TestAirRefractionIndexEdlen1966(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.air_refraction_index_Edlen1966`
    definition unit tests methods.
    """

    def test_air_refraction_index_Edlen1966(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.air_refraction_index_Edlen1966`
        definition.
        """

        self.assertAlmostEqual(
            air_refraction_index_Edlen1966(0.360),
            1.000285308809879,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Edlen1966(0.555),
            1.000277727690364,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Edlen1966(0.830),
            1.0002748622188347,
            places=10)


class TestAirRefractionIndexPeck1972(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.air_refraction_index_Peck1972`
    definition unit tests methods.
    """

    def test_air_refraction_index_Peck1972(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.air_refraction_index_Peck1972`
        definition.
        """

        self.assertAlmostEqual(
            air_refraction_index_Peck1972(0.360),
            1.0002853102850557,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Peck1972(0.555),
            1.0002777265414837,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Peck1972(0.830),
            1.0002748591448039,
            places=10)


class TestAirRefractionIndexBodhaine1999(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.air_refraction_index_Bodhaine1999`
    definition unit tests methods.
    """

    def test_air_refraction_index_Bodhaine1999(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.air_refraction_index_Bodhaine1999`
        definition.
        """

        self.assertAlmostEqual(
            air_refraction_index_Bodhaine1999(0.360),
            1.0002853102850557,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Bodhaine1999(0.555),
            1.0002777265414837,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Bodhaine1999(0.830),
            1.0002748591448039,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Bodhaine1999(0.360, 0),
            1.0002852640647895,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Bodhaine1999(0.555, 360),
            1.0002777355398236,
            places=10)

        self.assertAlmostEqual(
            air_refraction_index_Bodhaine1999(0.830, 620),
            1.0002749066404641,
            places=10)


class TestN2Depolarisation(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.N2_depolarisation`
    definition unit tests methods.
    """

    def test_N2_depolarisation(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.N2_depolarisation`
        definition.
        """

        self.assertAlmostEqual(
            N2_depolarisation(0.360),
            1.036445987654321,
            places=7)

        self.assertAlmostEqual(
            N2_depolarisation(0.555),
            1.0350291372453535,
            places=7)

        self.assertAlmostEqual(
            N2_depolarisation(0.830),
            1.034460153868486,
            places=7)


class TestO2Depolarisation(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.O2_depolarisation`
    definition unit tests methods.
    """

    def test_O2_depolarisation(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.O2_depolarisation`
        definition.
        """

        self.assertAlmostEqual(
            O2_depolarisation(0.360),
            1.115307746532541,
            places=7)

        self.assertAlmostEqual(
            O2_depolarisation(0.555),
            1.1020225362010714,
            places=7)

        self.assertAlmostEqual(
            O2_depolarisation(0.830),
            1.0983155612690134,
            places=7)


class TestF_airPenndorf1957(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.F_air_Penndorf1957`
    definition unit tests methods.
    """

    def test_F_air_Penndorf1957(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.F_air_Penndorf1957`
        definition.
        """

        self.assertEqual(F_air_Penndorf1957(), 1.0608)


class TestF_airYoung1981(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.F_air_Young1981`
    definition unit tests methods.
    """

    def test_F_air_Young1981(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.F_air_Young1981`
        definition.
        """

        self.assertEqual(F_air_Young1981(), 1.0480)


class TestF_airBates1984(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.F_air_Bates1984`
    definition unit tests methods.
    """

    def test_F_air_Bates1984(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.F_air_Bates1984`
        definition.
        """

        self.assertAlmostEqual(
            F_air_Bates1984(0.360),
            1.051997277711708,
            places=7)

        self.assertAlmostEqual(
            F_air_Bates1984(0.555),
            1.048153579718658,
            places=7)

        self.assertAlmostEqual(
            F_air_Bates1984(0.830),
            1.0469470686005893,
            places=7)


class TestF_airBodhaine1999(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.F_air_Bodhaine1999`
    definition unit tests methods.
    """

    def test_F_air_Bodhaine1999(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.F_air_Bodhaine1999`
        definition.
        """

        self.assertAlmostEqual(
            F_air_Bodhaine1999(0.360),
            1.125664021159081,
            places=7)

        self.assertAlmostEqual(
            F_air_Bodhaine1999(0.555),
            1.1246916702401561,
            places=7)

        self.assertAlmostEqual(
            F_air_Bodhaine1999(0.830),
            1.1243864557835395,
            places=7)

        self.assertAlmostEqual(
            F_air_Bodhaine1999(0.360, 0),
            1.0526297923139392,
            places=7)

        self.assertAlmostEqual(
            F_air_Bodhaine1999(0.555, 360),
            1.1279930150966895,
            places=7)

        self.assertAlmostEqual(
            F_air_Bodhaine1999(0.830, 620),
            1.13577082243141,
            places=7)


class TestMolecularDensity(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.molecular_density`
    definition unit tests methods.
    """

    def test_molecular_density(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.molecular_density`
        definition.
        """

        self.assertAlmostEqual(
            molecular_density(200),
            3.669449208173649e+19,
            places=24)

        self.assertAlmostEqual(
            molecular_density(300),
            2.4462994721157665e+19,
            places=24)

        self.assertAlmostEqual(
            molecular_density(400),
            1.8347246040868246e+19,
            places=24)


class TestMeanMolecularWeights(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.mean_molecular_weights`
    definition unit tests methods.
    """

    def test_mean_molecular_weights(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.mean_molecular_weights`
        definition.
        """

        self.assertAlmostEqual(
            mean_molecular_weights(0),
            28.9595,
            places=7)

        self.assertAlmostEqual(
            mean_molecular_weights(360),
            28.964920015999997,
            places=7)

        self.assertAlmostEqual(
            mean_molecular_weights(620),
            28.968834471999998,
            places=7)


class TestGravityList1968(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.gravity_List1968`
    definition unit tests methods.
    """

    def test_gravity_List1968(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.gravity_List1968`
        definition.
        """

        self.assertAlmostEqual(
            gravity_List1968(0, 0),
            978.0356070576,
            places=7)

        self.assertAlmostEqual(
            gravity_List1968(45, 1500),
            980.1533438638013,
            places=7)

        self.assertAlmostEqual(
            gravity_List1968(48.8567, 35),
            980.9524178426182,
            places=7)


class TestScatteringCrossSection(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.scattering_cross_section`
    definition unit tests methods.
    """

    def test_scattering_cross_section(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.scattering_cross_section`
        definition.
        """

        self.assertAlmostEqual(
            scattering_cross_section(360 * 10e-8),
            2.7812892348020306e-26,
            places=32)

        self.assertAlmostEqual(
            scattering_cross_section(555 * 10e-8),
            4.661330902337604e-27,
            places=32)

        self.assertAlmostEqual(
            scattering_cross_section(830 * 10e-8),
            9.12510035221888e-28,
            places=32)

        self.assertAlmostEqual(
            scattering_cross_section(555 * 10e-8, 0),
            4.3465433368391025e-27,
            places=32)

        self.assertAlmostEqual(
            scattering_cross_section(555 * 10e-8, 360),
            4.675013461928133e-27,
            places=32)

        self.assertAlmostEqual(
            scattering_cross_section(555 * 10e-8, 620),
            4.707951639592975e-27,
            places=32)

        self.assertAlmostEqual(
            scattering_cross_section(555 * 10e-8, temperature=200),
            2.245601437154005e-27,
            places=32)

        self.assertAlmostEqual(
            scattering_cross_section(555 * 10e-8, temperature=300),
            5.05260323359651e-27,
            places=32)

        self.assertAlmostEqual(
            scattering_cross_section(555 * 10e-8, temperature=400),
            8.98240574861602e-27,
            places=32)


class TestRayleighOpticalDepth(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.rayleigh_optical_depth`
    definition unit tests methods.
    """

    def test_rayleigh_optical_depth(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.rayleigh_optical_depth`
        definition.
        """

        self.assertAlmostEqual(
            rayleigh_optical_depth(360 * 10e-8),
            0.5991013368480278,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8),
            0.10040701772896546,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(830 * 10e-8),
            0.019655847912113555,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, 0),
            0.09364096434804903,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, 360),
            0.10069860517689733,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, 620),
            0.10139438226086347,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, temperature=200),
            0.0483711944156206,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, temperature=300),
            0.10883518743514632,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, temperature=400),
            0.1934847776624824,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, pressure=101325),
            0.10040701772896546,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, pressure=100325),
            0.0994160775095826,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, pressure=99325),
            0.09842513729019979,
            places=7)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, latitude=0, altitude=0),
            0.10040701772896546,
            places=10)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, latitude=45, altitude=1500),
            0.10019007653463426,
            places=10)

        self.assertAlmostEqual(
            rayleigh_optical_depth(555 * 10e-8, latitude=48.8567, altitude=35),
            0.10010846270542267,
            places=10)


class TestRayleighScatteringSpd(unittest.TestCase):
    """
    Defines
    :func:`colour.phenomenons.rayleigh.rayleigh_scattering_spd`
    definition unit tests methods.
    """

    def test_rayleigh_scattering_spd(self):
        """
        Tests
        :func:`colour.phenomenons.rayleigh.rayleigh_scattering_spd`
        definition.
        """

        np.testing.assert_almost_equal(
            rayleigh_scattering_spd().values,
            RAYLEIGH_SCATTERING_SPD_DATA,
            decimal=7)


if __name__ == '__main__':
    unittest.main()
