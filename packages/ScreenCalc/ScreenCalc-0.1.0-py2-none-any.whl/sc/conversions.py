#!/usr/bin/env python

from __future__ import division

from collections import OrderedDict as odict

LDPI = 120
MDPI = 160
TVDPI = 213
HDPI = 240
XHDPI = 320
XXHDPI = 480
XXXHDPI = 640
DENSITY_DEFAULT = MDPI

UNITS = ('dp', 'px', 'sp', 'mm', 'in', 'pt')
RATIO_MM = 0.15875
RATIO_IN = 0.00625
PT_PER_IN = 72

DENSITY_NAMES = ('l', 'm', 'tv', 'h', 'xh', 'xxh', 'xxxh',)
DENSITY_VALUES = (LDPI, MDPI, TVDPI, HDPI, XHDPI, XXHDPI, XXXHDPI,)
DENSITY_VALUE_MAP = odict(zip(DENSITY_NAMES, DENSITY_VALUES))
DENSITY_NAMES_MAP = odict(zip(DENSITY_VALUES, DENSITY_NAMES))


_ignored = object()


def dp_to_dp(dp, density=_ignored, scale=_ignored):
    return dp


def px_to_dp(px, density=DENSITY_DEFAULT, scale=_ignored):
    return px / (density / DENSITY_DEFAULT)


def dp_to_px(dp, density=DENSITY_DEFAULT, scale=_ignored):
    return dp * (density / DENSITY_DEFAULT)


def dp_to_mm(dp, density=_ignored, scale=_ignored):
    return dp * RATIO_MM


def mm_to_dp(mm, density=_ignored, scale=_ignored):
    return mm / RATIO_MM


def dp_to_in(dp, density=_ignored, scale=_ignored):
    return dp * RATIO_IN


def in_to_dp(in_, density=_ignored, scale=_ignored):
    return in_ / RATIO_IN


def dp_to_sp(dp, density=_ignored, scale=1.0):
    return dp / scale


def sp_to_dp(sp, density=_ignored, scale=1.0):
    return sp * scale


def dp_to_pt(dp, density=DENSITY_DEFAULT, scale=_ignored):
    px = dp_to_px(dp, density)
    return px * (PT_PER_IN / density)


def pt_to_dp(pt, density=DENSITY_DEFAULT, scale=_ignored):
    return pt / (PT_PER_IN / density)


_to_dp = {
    'dp': dp_to_dp,
    'px': px_to_dp,
    'sp': sp_to_dp,
    'mm': mm_to_dp,
    'in': in_to_dp,
    'pt': pt_to_dp,
}

_from_dp = {
    'dp': dp_to_dp,
    'px': dp_to_px,
    'sp': dp_to_sp,
    'mm': dp_to_mm,
    'in': dp_to_in,
    'pt': dp_to_pt,
}
