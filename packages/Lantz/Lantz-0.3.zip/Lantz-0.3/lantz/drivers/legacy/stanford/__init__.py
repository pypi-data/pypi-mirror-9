# -*- coding: utf-8 -*-
"""
    lantz.drivers.legacy.stanford
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :company: Standford Research Systems.
    :description: Manufactures test instruments for research and industrial applications
    :website: http://www.thinksrs.com/

    ----

    :copyright: 2015 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from .sr830 import SR830Serial, SR830GPIB

__all__ = ['SR830Serial', 'SR830GPIB']
