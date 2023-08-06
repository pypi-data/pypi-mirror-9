#!/usr/bin/env python

"""Tests for the parser."""

import pytest

from sc.main import parse_size
from sc.conversions import DENSITY_DEFAULT, DENSITY_NAMES, DENSITY_VALUES


class TestScreenSizeArgumentParsing(object):
    def test_bad_input_string(self):
        try:
            parse_size('asdf')
            pytest.fail('Expected ValueError to be raised')
        except ValueError as e:
            assert 'Could not parse' in str(e)

    def test_size_not_number(self):
        try:
            parse_size('1.1.1dp')
            pytest.fail('Expected ValueError to be raised')
        except ValueError as e:
            assert '1.1.1 is not a number' in str(e)

    @pytest.mark.parametrize('value', [
        100,
        99.9,
    ])
    def test_size_number_parsing(self, value):
        size, _, _ = parse_size('%sdp' % value)
        assert size == value

    def test_use_default_density_when_none_given(self):
        _, _, density = parse_size('100sp')
        assert density == DENSITY_DEFAULT

    @pytest.mark.parametrize('name,value', zip(DENSITY_NAMES, DENSITY_VALUES))
    def test_parse_named_densities(self, name, value):
        _, _, density = parse_size('100px@%sdpi' % name)
        assert density == value

    def test_unknown_named_density_fails(self):
        try:
            parse_size('100dp@foodpi')
            pytest.fail('Expected ValueError to be raised')
        except ValueError as e:
            assert 'Invalid density: "foo"' in str(e)

    @pytest.mark.parametrize('unit', [
        'dp',
        'px',
        'sp',
        'mm',
        'in',
        'pt',
    ])
    def test_known_units(self, unit):
        _, parsed_unit, _ = parse_size('100%s@100dpi' % unit)
        assert parsed_unit == unit

    def test_unknown_unit(self):
        try:
            parse_size('100xx')
            pytest.fail('Expected ValueError to be raised')
        except ValueError as e:
            assert 'Unknown unit: "xx"' in str(e)

    def test_px_input_requires_density(self):
        try:
            parse_size('100px')
            pytest.fail('Expected ValueError to be raised')
        except ValueError as e:
            assert 'px conversions require density' in str(e)
