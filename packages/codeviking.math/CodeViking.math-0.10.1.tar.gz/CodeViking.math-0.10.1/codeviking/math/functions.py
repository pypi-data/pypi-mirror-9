"""
Functions
---------

This module contains functions that are used to create other functions.
Clamping and mixing functions are provided, as are transition functions and
piecewise function assembly.
"""


import math

from codeviking.math.primitives import smooth010


def make_clamp(x0, x1):
    """
    Create a clamping function that clhtamps input values to the range [x0,x1］.
    """
    return lambda x: max(x0, min(x, x1))


# ［］（）∈∉
def make_mix(y0, y1):
    """
    Create a mix function that mixes between y0 and y1 as x varies between 0
    and 1.

      * y0  for x0 ≤ 0
      * y1 for 1 ≤ x
      * y0 + x*(y1-y0) for x ∈［0,1］
    """

    def _(x):
        if x <= 0.0:
            return y0
        elif x >= 1.0:
            return y1
        return y0 * (1.0 - x) + y1 * x

    return _


def piecewise_func1(x0, f0, f1):
    """
    Create a piecewise function with one knot:

      * f0(x)  for x < x0
      * f1(x)  for x0 ≤ x

    :param x0: knot between f0 and f1
    :type x0: float
    :param f0: function to use for x < x0
    :type f0: (float) -> object
    :param f1: function to use for x0 ≤ x
    :type f1: (float) -> object
    :return: piecewise function
    :rtype: (float) -> float
    """
    return lambda x: f0(x) if x < x0 else f1(x)


def piecewise_func2(x0, x1, f0, f1, f2):
    """
    Create a piecewise function with two knots:
        * f0(x)  for x < x0
        * f1(x)  for x0 ≤ x < x1
        * f2(x)  for x1 ≤ x

    :param x0: knot between f0 and f1
    :type x0: float
    :param x1: knot between f1 and f2
    :type x1: float
    :param f0: function to use for x < x0
    :type f0: (float) -> object
    :param f1: function to use for x0 ≤ x < x1
    :type f1: (float) -> object
    :param f2: function to use for x1 ≤ x
    :type f2: (float) -> object
    :return: piecewise function
    :rtype: (float) -> float
    """

    def _(x):
        if x < x0:
            return f0(x)
        if x < x1:
            return f1(x)
        return f2(x)

    return _


def make_interval_func(x0, x1, y0, f, y1):
    """
    Create function on the interval [x0,x1] with constant value outside that
    interval:

        * y0  for x < x0
        * f(x)  for x0 ≤ x < x1
        * y1  for x1 ≤ x

    :type x0 x1 y0 y1: float
    :type f: (float) -> float
    """

    def _(x):
        if x < x0:
            return y0
        if x < x1:
            return f(x)
        return y1

    return _


def make_triangle_func(x0, x1, x2, y0, y1, y2):
    """
    Create triangle function ( ╱╲ ) on the interval ［x0,x2］:

        * y0  for x < x0
        * linear slope from (x0,y0) to (x1,y1)  for x0 ≤ x < x1
        * linear slope from (x1,y1) to (x2,y2)  for x1 ≤ x < x2
        * y2  for x2 ≤ x

    :type x0 x1 x2 y0 y1 y2: float
    """
    m0 = (y1 - y0) / (x1 - x0)
    b0 = -(x1 * y0 - x0 * y1) / (x0 - x1)
    m1 = (y2 - y1) / (x2 - x1)
    b1 = -(x2 * y1 - x1 * y2) / (x1 - x2)

    def _(x):
        if x < x0:
            return y0
        if x < x1:
            return m0 * x + b0
        if x < x2:
            return m1 * x + b1
        return y2

    return _


def make_step(x0, y0=0.0, y1=1.0):
    """
    create a step function:

        * f(x) = y0 for x<x0
        * f(x) = y1 for x0≤x
    """

    def _(x):
        return y0 if (x < x0) else y1

    return _


def make_rect_func(x0, x1, y0, y1, y2):
    """
    Create rect function ( ┌─┐ )on the interval ［x0,x1］:

        * y0  for x < x0
        * y1  for x0 ≤ x ≤ x1
        * y2  for x1 < x
    """

    def _(x):
        if x < x0:
            return y0
        if x <= x1:
            return y1
        return y2

    return _


def make_smooth_step(x0,
                     x1,
                     y0=0.0,
                     y1=1.0):
    """
    Creates a smooth step function f with the following properties:

      * f(x)=y0 for x ≤ x0
      * f(x)=y1 for x1 ≤ x
      * f'(x) = 0 for x=x0 and x=x1.
      * in the interval [x0,x1], the function smoothly transitions between
        y0 and  y1.  We use a monotonically increasing sin function on this
        interval.
    """
    height = y1 - y0
    s = math.pi / (x1 - x0)
    shift = math.pi / 2.0

    def _(x):
        if x <= x0:
            return y0
        if x >= x1:
            return y1
        return height * 0.5 * (math.sin(s * (x - x0) - shift) + 1.0) + y0

    return _


def make_bump_func(x0, x1, x2,
                   y0, y1, y2):
    """
    Create a bump function with the following properties:

        * f(x)=y0 for x≤x0
        * f(x1)=y1
        * f(x)=y2 for x2≤x
        * f'(x) = 0 for x=x0, x=x1, x=x2.
        * in the interval ［x0,x1］, smoothly and monotonically transition
          between y0 and y1.
        * in the interval ［x1,x2］, smoothly and monotonically transition
          between y1 and y2.
    """
    ah = y1 - y0
    bh = y2 - y1
    aw = x1 - x0
    bw = x2 - x1

    def _(x):
        if x <= x0:
            return y0
        if x <= x1:
            return y0 + ah * smooth010((x - x1) / aw)
        if x <= x2:
            return y2 - bh * smooth010((x - x1) / bw)
        return y2

    return _

