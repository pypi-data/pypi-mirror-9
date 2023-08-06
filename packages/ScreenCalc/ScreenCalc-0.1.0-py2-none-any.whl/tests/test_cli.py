#!/usr/bin/env python

"""Tests for the CLI interface."""

from textwrap import dedent

import pytest
from click.testing import CliRunner

from sc.main import main

runner = CliRunner()


class TestScreenSizeArgumentValidation(object):
    def test_unparseable_string(self):
        r = runner.invoke(main, ['asdf'])
        assert r.exit_code == 2
        assert 'Could not parse "asdf" as a screen dimension' in r.output

    def test_size_must_be_number(self):
        r = runner.invoke(main, ['1.1.1px@123'])
        assert r.exit_code == 2
        assert '1.1.1 is not a number' in r.output

    def test_fail_on_unknown_unit(self):
        r = runner.invoke(main, ['180xx'])
        assert r.exit_code == 2
        assert 'Unknown unit: "xx"' in r.output

    @pytest.mark.parametrize('unit', [
        'dp',
        'px',
        'sp',
        'mm',
        'in',
        'pt',
    ])
    def test_known_units(self, unit):
        r = runner.invoke(main, ['180%s@hdpi' % unit])
        assert r.exit_code == 0

    def test_px_input_requires_density(self):
        r = runner.invoke(main, ['180px'])
        assert r.exit_code == 2
        assert 'px conversions require density' in r.output

    def test_decimal_density_parsing(self):
        r = runner.invoke(main, ['180px@480dpi'])
        assert r.exit_code == 0

    @pytest.mark.parametrize('density', [
        'ldpi',
        'mdpi',
        'tvdpi',
        'hdpi',
        'xhdpi',
        'xxhdpi',
        'xxxhdpi',
    ])
    def test_named_density_parsing(self, density):
        r = runner.invoke(main, ['180px@%s' % density])
        assert r.exit_code == 0

    def test_unknown_named_density_fails(self):
        r = runner.invoke(main, ['180px@foodpi'])
        assert r.exit_code == 2
        assert 'Invalid density: "foo"' in r.output

    def test_accepts_multiple_sizes(self):
        r = runner.invoke(main, ['180px@hdpi', '100dp'])
        assert r.exit_code == 0


class TestCLI(object):
    def test_conversion_format(self):
        exp = dedent("""\
        100.0px@480dpi
        +-----------+---------+----------+---------+---------+----------+------+
        | density   |      dp |       px |      sp |      mm |       in |   pt |
        |-----------+---------+----------+---------+---------+----------+------|
        | ldpi      | 33.3333 |  25      | 33.3333 | 5.29167 | 0.208333 |   15 |
        | mdpi      | 33.3333 |  33.3333 | 33.3333 | 5.29167 | 0.208333 |   15 |
        | tvdpi     | 33.3333 |  44.375  | 33.3333 | 5.29167 | 0.208333 |   15 |
        | hdpi      | 33.3333 |  50      | 33.3333 | 5.29167 | 0.208333 |   15 |
        | xhdpi     | 33.3333 |  66.6667 | 33.3333 | 5.29167 | 0.208333 |   15 |
        | xxhdpi    | 33.3333 | 100      | 33.3333 | 5.29167 | 0.208333 |   15 |
        | xxxhdpi   | 33.3333 | 133.333  | 33.3333 | 5.29167 | 0.208333 |   15 |
        +-----------+---------+----------+---------+---------+----------+------+

        """)  # NOQA
        r = runner.invoke(main, ['100px@xxhdpi'])
        assert r.output == exp
