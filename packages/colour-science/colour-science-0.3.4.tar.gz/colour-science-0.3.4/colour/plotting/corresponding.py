#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Corresponding Chromaticities Prediction Plotting
================================================

Defines corresponding chromaticities prediction plotting objects:

-   :func:`corresponding_chromaticities_prediction_plot`
"""

from __future__ import division
import pylab

from colour.corresponding import CORRESPONDING_CHROMATICITIES_PREDICTION_MODELS
from colour.plotting import (
    CIE_1976_UCS_chromaticity_diagram_plot,
    DEFAULT_FIGURE_WIDTH,
    canvas,
    display)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['get_corresponding_chromaticities_prediction_model',
           'corresponding_chromaticities_prediction_plot']


def get_corresponding_chromaticities_prediction_model(model):
    """
    Returns the corresponding chromaticities prediction model with given name.

    Parameters
    ----------
    model : unicode
        Corresponding chromaticities prediction models name.

    Returns
    -------
    object
        Corresponding chromaticities prediction models.

    Raises
    ------
    KeyError
        If the given corresponding chromaticities prediction model is not found
        in the factory corresponding chromaticities prediction models.
    """

    model, name = (
        CORRESPONDING_CHROMATICITIES_PREDICTION_MODELS.get(model), model)
    if model is None:
        models = ', '.join(
            sorted(CORRESPONDING_CHROMATICITIES_PREDICTION_MODELS.keys()))
        raise KeyError(
            ('"{0}" not found in factory corresponding chromaticities '
             'prediction models: "{1}".').format(name, models))
    return model


def corresponding_chromaticities_prediction_plot(
        experiment=1,
        model='Von Kries',
        transform='CAT02',
        **kwargs):
    """
    Plots given chromatic adaptation model corresponding chromaticities
    prediction.

    Parameters
    ----------
    model : unicode, optional
        Corresponding chromaticities prediction models name.
    model : unicode, optional
        Corresponding chromaticities prediction models name.
    transform : unicode, optional
        Transformation to use with Von Kries chromatic adaptation model.

    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> corresponding_chromaticities_prediction_plot()  # doctest: +SKIP
    True
    """

    settings = {'figure_size': (DEFAULT_FIGURE_WIDTH, DEFAULT_FIGURE_WIDTH)}
    settings.update(kwargs)

    canvas(**settings)

    model, name = (
        get_corresponding_chromaticities_prediction_model(model), model)

    settings.update({
        'title': (('Corresponding Chromaticities Prediction\n{0} ({1}) - '
                   'Experiment {2}\nCIE 1960 UCS Chromaticity Diagram').format(
            name, transform, experiment)
                  if name.lower() in ('von kries', 'vonkries') else
                  ('Corresponding Chromaticities Prediction\n{0} - '
                   'Experiment {1}\nCIE 1960 UCS Chromaticity Diagram').format(
                      name, experiment)),
        'standalone': False})
    settings.update(kwargs)

    if not CIE_1976_UCS_chromaticity_diagram_plot(**settings):
        return

    results = model(experiment, transform=transform)

    for result in results:
        name, uvp_t, uvp_m, uvp_p = result
        pylab.arrow(uvp_t[0],
                    uvp_t[1],
                    uvp_p[0] - uvp_t[0] - 0.1 * (uvp_p[0] - uvp_t[0]),
                    uvp_p[1] - uvp_t[1] - 0.1 * (uvp_p[1] - uvp_t[1]),
                    head_width=0.005,
                    head_length=0.005,
                    linewidth=0.5,
                    color='black')
        pylab.plot(uvp_t[0], uvp_t[1], 'o', color='white')
        pylab.plot(uvp_m[0], uvp_m[1], '^', color='white')
        pylab.plot(uvp_p[0], uvp_p[1], '^', color='black')
    settings.update({'standalone': True})

    return display(**settings)
