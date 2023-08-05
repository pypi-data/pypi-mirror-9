#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Showcases *RGB* *colourspaces* computations.
"""

import numpy as np
from pprint import pprint

import colour
from colour.utilities.verbose import message_box

message_box('"RGB" Colourspaces Computations')

message_box('"RGB" colourspaces dataset.')
pprint(sorted(colour.RGB_COLOURSPACES.keys()))

print('\n')

message_box('"ACES2065-1" colourspaces data.')
colourspace = colour.RGB_COLOURSPACES['ACES2065-1']
print('Name:\n"{0}"'.format(colourspace.name))
print('\nPrimaries:\n{0}'.format(colourspace.primaries))
print('\nNormalised primary matrix to "CIE XYZ":\n{0}'.format(
    colourspace.RGB_to_XYZ_matrix))
print('\nNormalised primary matrix to "ACES2065-1":\n{0}'.format(
    colourspace.XYZ_to_RGB_matrix))
print('\nTransfer function from linear to colourspace:\n{0}'.format(
    colourspace.transfer_function))
print('\nInverse transfer function from colourspace to linear:\n{0}'.format(
    colourspace.inverse_transfer_function))

print('\n')

message_box('Computing "ACES2065-1" colourspace to "sRGB" colourspace matrix.')
cat = colour.chromatic_adaptation_matrix_VonKries(
    colour.xy_to_XYZ(colour.RGB_COLOURSPACES['ACES2065-1'].whitepoint),
    colour.xy_to_XYZ(colour.RGB_COLOURSPACES['sRGB'].whitepoint))
print(np.dot(colour.RGB_COLOURSPACES['sRGB'].XYZ_to_RGB_matrix,
             np.dot(cat,
                    colour.RGB_COLOURSPACES['ACES2065-1'].RGB_to_XYZ_matrix)))

print('\n')

RGB = [0.35521588, 0.41, 0.24177934]
message_box(('Converting from "sRGB" colourspace to "ProPhoto RGB" '
             'colourspace given "RGB" values:\n'
             '\n\t{0}'.format(RGB)))
print(colour.RGB_to_RGB(RGB,
                        colour.RGB_COLOURSPACES['sRGB'],
                        colour.RGB_COLOURSPACES['ProPhoto RGB']))
