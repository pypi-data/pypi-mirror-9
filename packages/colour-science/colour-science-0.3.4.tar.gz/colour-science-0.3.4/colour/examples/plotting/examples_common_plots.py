#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Showcases common plotting examples.
"""

from colour.plotting import *  # noqa
from colour.utilities.verbose import message_box

message_box('Common Plots')

message_box('Plotting a single colour.')
single_colour_plot(colour_parameter('Neutral 5 (.70 D)',
                                    RGB=(0.32315746, 0.32983556, 0.33640183)),
                   text_size=32)

print('\n')

message_box('Plotting multiple colours.')
multi_colour_plot(
    [colour_parameter('Dark Skin', RGB=(0.45293517, 0.31732158, 0.26414773)),
     colour_parameter('Light Skin', RGB=(0.77875824, 0.5772645, 0.50453169))],
    spacing=0,
    text_size=32)
