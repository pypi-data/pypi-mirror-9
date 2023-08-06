#!/usr/bin/env python

"""Tests for the conversion functions."""

import pytest

from sc.conversions import UNITS, _to_dp, _from_dp


@pytest.mark.parametrize('unit', UNITS)
def test_conversion_bidirectional(unit):
    to_ = _from_dp[unit]
    from_ = _to_dp[unit]
    assert to_(from_(100)) == 100
