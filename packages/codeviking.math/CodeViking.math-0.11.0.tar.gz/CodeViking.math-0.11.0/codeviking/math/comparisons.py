r"""
Numerical Comparison Functions
------------------------------

Comparing floating-point numbers for equality can be problematic.  Testing
for exact equality is usually not a good idea.  Instead, we usually want to
consider two values equal if they are very close.  The functions in this
module can be used to create comparison functions that tolerate a
user-specified amount of error.

Definitions:
````````````

  Relative Difference
    :math:`\textrm{rel_diff}(a, b) = \frac{\left| a - b \right|}{\max\left(|a|,
    |b|\right)}`


  Absolute Difference
    :math:`\textrm{abs_diff}(a, b) = |a - b|`

"""


def make_relative_equals(tol):
    r"""
    Create a comparison function `is_equal(a,b)` that returns True if
    :math:`\textrm{rel_diff}(a, b) \leq tol`

    :param tol: relative tolerance
    :type tol: float
    :return: function that returns True if relative difference between a and b
             is less than tol.
    :rtype: (float, float) -> bool
    """

    def is_equal(a, b):
        mx = max(abs(a), abs(b))
        delta = abs(a - b)
        return delta <= tol * mx

    return is_equal


def make_absolute_equals(tol):
    r"""
    Create a comparison function `is_equal(a,b)` that returns True if
    :math:`\textrm{abs_diff}(a, b) \leq tol`

    :param tol: absolute tolerance
    :type tol: float
    :return: function that returns True if absolute difference between a and b
             is less than tol.
    :rtype: (float, float) -> bool
    """

    def is_equal(a, b):
        delta = abs(a - b)
        return delta <= tol

    return is_equal


def make_equals(abs_tol, rel_tol):
    r"""
    Create a comparison that returns True if either
        :math:`\textrm{rel_diff}(a, b) \leq \textit{rel_tol}` or :math:`\textrm{
        rel_diff}(a, b) \leq \textit{abs_tol}`


    :param abs_tol: absolute tolerance
    :type abs_tol: float
    :param rel_tol: relative tolerance
    :type rel_tol: float
    :return: function that returns True if either the relative difference is
    less than rel_tol or absolute difference is less than abs_tol
    :rtype: (float, float) -> bool
    """

    def is_equal(a, b):
        mx = max(abs(a), abs(b))
        delta = abs(a - b)
        return delta <= max(abs_tol, rel_tol * mx)

    return is_equal


def make_seq_equals(eq_func):
    r"""
    Create a comparison function that compares corresponding elements of two
    sequences.  Two sequences are considered equal if they have the same
    length, and :math:`\textrm{eq_func}(a_i, b_i) \forall i=0, ..., n`

    :param equals_func: The function used to compare elements
    :type equals_func: (float, float) -> bool
    :return: comparison function
    :rtype: (list[float], list[float]) -> bool
    """
    def _(a, b):
        if len(a) != len(b):
            return False
        for i in range(len(a)):
            if not eq_func(a[i], b[i]):
                return False
        return True
    return _
