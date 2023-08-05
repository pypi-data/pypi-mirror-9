#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Showcases Von Kries chromatic adaptation model computations.
"""

from __future__ import division, unicode_literals

import colour
from colour.utilities.verbose import message_box

message_box('Von Kries Chromatic Adaptation Model Computations')

XYZ_w = (1.09846607, 1., 0.3558228)
XYZ_wr = (1.09846607, 1., 0.3558228)
message_box(('Computing the chromatic adaptation matrix from two source '
             '"CIE XYZ" matrices, default CAT is "CAT02".\n'
             '\n\t"XYZ_w":\n\t\t{0}\n\t"XYZ_wr":\n\t\t{1}'.format(
    XYZ_w, XYZ_wr)))
print(colour.chromatic_adaptation_matrix_VonKries(XYZ_w, XYZ_wr))

print('\n')

message_box('Using "Bradford" CAT.')
print(colour.chromatic_adaptation_matrix_VonKries(
    XYZ_w, XYZ_wr, transform='Bradford'))

print('\n')

message_box(('Computing the chromatic adaptation matrix from '
             '"CIE Standard Illuminant A" to '
             '"CIE Standard Illuminant D Series D65" using Von Kries CAT.'))
A = colour.ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['A']
D65 = colour.ILLUMINANTS['CIE 1931 2 Degree Standard Observer']['D65']
print(colour.chromatic_adaptation_matrix_VonKries(
    colour.xy_to_XYZ(A),
    colour.xy_to_XYZ(D65),
    transform='Von Kries'))

print('\n')

XYZ = [1.14176346, 1., 0.49815206]
message_box(('Adapting given "CIE XYZ" matrix from '
             '"CIE Standard Illuminant A" to '
             '"CIE Standard Illuminant D Series D65" using "Sharp" CAT.\n'
             '\n\t"XYZ":\n\t\t{0}'.format(XYZ)))
print(colour.chromatic_adaptation_VonKries(
    XYZ,
    colour.xy_to_XYZ(A),
    colour.xy_to_XYZ(D65),
    transform='Von Kries'))
