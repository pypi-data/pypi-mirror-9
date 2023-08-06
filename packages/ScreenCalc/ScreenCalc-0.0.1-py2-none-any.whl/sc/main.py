#!/usr/bin/env python

import sys
import re

import click
from tabulate import tabulate

from .conversions import _to_dp, _from_dp, DENSITY_DEFAULT, DENSITY_VALUE_MAP, UNITS


HDR_ROW = (('density',) + UNITS)
INPUT_RE = re.compile(r'([0-9\.]+)([a-zA-Z]{2})(?:@(.*))?')


class ScreenSizeParamType(click.ParamType):
    name = 'screensize'

    def convert(self, value, param, ctx):
        match = INPUT_RE.match(value)
        if not match:
            self.fail('Could not parse "%s" as a screen dimension' % value, param, ctx)
        else:
            size, unit, _density = match.groups()
            try:
                size = float(size)
            except ValueError:
                self.fail('%s is not a number' % size, param, ctx)

            if unit not in UNITS:
                self.fail('Unknown unit: "%s"' % unit, param, ctx)

            if _density is None:
                if unit == 'px':
                    self.fail('px conversions require density', param, ctx)
                density = DENSITY_DEFAULT
            else:
                _density = _density.rstrip('dpi')
                if _density.isdigit():
                    density = int(_density)
                else:
                    try:
                        density = DENSITY_VALUE_MAP[_density]
                    except KeyError:
                        self.fail('Invalid density: "%s"' % _density, param, ctx)

        return size, unit, density


SCREEN_SIZE_TYPE = ScreenSizeParamType()


def convert(value, unit, density=DENSITY_DEFAULT, scale=1.0):
    dp = _to_dp[unit](value, density, scale)
    results = []
    for dn, dv in DENSITY_VALUE_MAP.iteritems():
        row = [dn + 'dpi']
        for unit in UNITS:
            row.append(_from_dp[unit](dp, dv, scale))
        results.append(row)
    return results


@click.command()
@click.argument('sizes', type=SCREEN_SIZE_TYPE, nargs=-1)
@click.option('--scale', '-s', default=1.0, type=float, help='User font scale.')
def main(sizes, scale):
    for arg in sizes:
        size, unit, density = arg
        print('%s%s@%sdpi' % arg)
        print(tabulate(convert(size, unit, density, scale), HDR_ROW, tablefmt='psql'))
        print('')
