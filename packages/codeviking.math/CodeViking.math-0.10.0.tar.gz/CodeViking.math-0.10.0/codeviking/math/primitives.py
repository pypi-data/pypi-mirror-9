"""
Primitive Functions
-------------------

This module contains primitive functions designed to be used in the creation
of more complex functions.
"""


import math


def clamp01(x):
    """
    Clamp input value to ［0.0, 1.0］
    """
    return max(0.0, min(x, 1.0))


def smooth101(x):
    """
    Smooth step down on the interval ［-1,0］ and up on ［0,1］.

    **WARNING**: this function is *also* defined outside the interval ［-1,1］.
    It is intended to be used as a primitive to build other functions,
    so for efficiency reasons, it is not clamped or otherwise modified.

    :type x: float
    """
    return 0.5 * math.sin(math.pi * (x - 0.5)) + 0.5


def smooth010(x):
    """
    Smooth step up on the interval ［-1,0］, and down on ［0,1］.

    **WARNING**: this function is *also* defined outside the interval ［-1,1］.
    It is intended to be used as a primitive to build other functions,
    so for efficiency reasons, it is not clamped or otherwise modified.

    :type x: float
    """
    return 0.5 * math.cos(math.pi * x) + 0.5


def smooth_step_up(x):
    """
    Step up from 0 to 1 on the interval ［0,1］, and clamp to 0.0 and 1.0
    outside the interval.

    :type x: float
    :rtype: float
    """
    if x <= 0.0:
        return 0.0
    if 1.0 <= x:
        return 1.0
    return smooth101(x)


def smooth_step_down(x):
    """
    Step up from 0 to 1 on the interval ［0,1］, and clamp to 0.0 and 1.0
    outside the interval.

    :type x: float
    :rtype: float
    """
    if x <= 0.0:
        return 1.0
    if 1.0 <= x:
        return 0.0
    return smooth010(x)


def bump(x):
    """
    Smooth step up on the interval ［-1,0］, and down on ［0,1］.  Clamp to 0.0
    outside the interval.  This is the clamped version of [smooth010].

    :type x: float
    :rtype: float
    """
    if x <= -1.0:
        return 0.0
    if 1.0 <= x:
        return 0.0
    return smooth010(x)


def rect(x):
    """
    The rect function defined as:

        * 1 for -½ ≤ x ≤ ½
        * 0 otherwise.
    """
    return 1.0 if abs(x) <= 0.5 else 0.0


def wrap_to_interval(x, x0, s):
    """
    Given an interval ［x0,x0+s), map x to this interval by assuming the
    interval repeats its values on this infinitely in both directions.
    """
    return ((x - x0) % s) + x0


def wrap_to_centered_interval(x, center, half_width):
    """
    Given an interval ［center-halfWidth, center+halfWidth),
    map x to this interval by assuming the interval repeats infinitely.
    """
    return ((x - (center - half_width)) % (2.0 * half_width)) + (
        center - half_width)


def clamp(x, x0, x1):
    """
    Clamp x to lie within the interval [x0, x1]

    :param x: the value to clamp
    :type x: float
    :param x0: left edge of the interval
    :type x0: float
    :param x1: right edge of the interval
    :type x1: float
    :return: x restricted to [x0, x1]
    :rtype: float
    """
    return max(x0, min(x, x1))
