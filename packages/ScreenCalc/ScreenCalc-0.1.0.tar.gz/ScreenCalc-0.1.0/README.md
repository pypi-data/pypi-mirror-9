# ScreenCalc
A simple screen size calculator to convert screen measurement units at various
densities

[![Build Status](http://img.shields.io/travis/joshfriend/screencalc/master.svg)](https://travis-ci.org/joshfriend/screencalc)
[![Coverage Status](http://img.shields.io/coveralls/joshfriend/screencalc/master.svg)](https://coveralls.io/r/joshfriend/screencalc)
[![PyPI Version](http://img.shields.io/pypi/v/ScreenCalc.svg)](https://pypi.python.org/pypi/ScreenCalc)
[![PyPI Downloads](http://img.shields.io/pypi/dm/ScreenCalc.svg)](https://pypi.python.org/pypi/ScreenCalc)

# Getting Started

Install:
```
$ pip install ScreenCalc
```

Use it:
```
$ sc 100px@hdpi 100dp ...
100.0px@240dpi
+-----------+---------+----------+---------+---------+----------+------+
| density   |      dp |       px |      sp |      mm |       in |   pt |
|-----------+---------+----------+---------+---------+----------+------|
| ldpi      | 66.6667 |  50      | 66.6667 | 10.5833 | 0.416667 |   30 |
| mdpi      | 66.6667 |  66.6667 | 66.6667 | 10.5833 | 0.416667 |   30 |
| tvdpi     | 66.6667 |  88.75   | 66.6667 | 10.5833 | 0.416667 |   30 |
| hdpi      | 66.6667 | 100      | 66.6667 | 10.5833 | 0.416667 |   30 |
| xhdpi     | 66.6667 | 133.333  | 66.6667 | 10.5833 | 0.416667 |   30 |
| xxhdpi    | 66.6667 | 200      | 66.6667 | 10.5833 | 0.416667 |   30 |
| xxxhdpi   | 66.6667 | 266.667  | 66.6667 | 10.5833 | 0.416667 |   30 |
+-----------+---------+----------+---------+---------+----------+------+

...
```

Known measurement units are: `dp`, `px`, `sp`, `mm`, `in`, and `pt`. Screen
density can be one of the named values (`ldpi`, `mdpi`, `tvdpi`, `hdpi`,
`xhdpi`, `xxhdpi`, or `xxxhdpi`), or a decimal value (e.g. `100`).
