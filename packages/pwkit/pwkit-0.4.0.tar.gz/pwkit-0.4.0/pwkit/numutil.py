# -*- mode: python; coding: utf-8 -*-
# Copyright 2014 Peter Williams <peter@newton.cx> and collaborators.
# Licensed under the MIT License.

"""numutil - NumPy and generic numerical utilities.

Functions:

make_step_lcont   - Return a step function that is left-continuous.
make_step_rcont   - Return a step function that is right-continuous.
make_tophat_ee    - Return a tophat function operating on an exclusive/exclusive range.
make_tophat_ei    - Return a tophat function operating on an exclusive/inclusive range.
make_tophat_ie    - Return a tophat function operating on an inclusive/exclusive range.
make_tophat_ii    - Return a tophat function operating on an inclusive/inclusive range.
rms               - Calculate the square root of the mean of the squares of x.
unit_tophat_ee    - Tophat function on (0,1).
unit_tophat_ei    - Tophat function on (0,1].
unit_tophat_ie    - Tophat function on [0,1).
unit_tophat_ii    - Tophat function on [0,1].
weighted_variance - Estimate the variance of a weighted sampled.

Decorators:

broadcastize - Make a Python function automatically broadcast arguments.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = (b'broadcastize make_step_lcont make_step_rcont make_tophat_ee '
           b'make_tophat_ei make_tophat_ie make_tophat_ii rms unit_tophat_ee '
           b'unit_tophat_ei unit_tophat_ie unit_tophat_ii weighted_variance').split ()

import functools
import numpy as np


class _Broadcaster (object):
    def __init__ (self, n_arr, subfunc):
        self._subfunc = subfunc
        self._n_arr = int (n_arr)

        if self._n_arr < 1:
            raise ValueError ('broadcastiz\'ed function must take at least 1 '
                              'array argument')

        functools.update_wrapper (self, subfunc)


    def __call__ (self, *args, **kwargs):
        if len (args) < self._n_arr:
            raise TypeError ('expected at least %d arguments, got %d'
                             % (self._n_arr, len (args)))

        bc_raw = np.broadcast_arrays (*args[:self._n_arr])
        bc_1d = tuple (np.atleast_1d (a) for a in bc_raw)
        rest = args[self._n_arr:]
        result = self._subfunc (*(bc_1d + rest), **kwargs)

        if bc_raw[0].ndim == 0:
            return np.asscalar (result)
        return result


class _BroadcasterDecorator (object):
    """Decorator to make functions automatically work on vectorized arguments.

    @broadcastize (3) # myfunc's first 3 arguments should be arrays.
    def myfunc (arr1, arr2, arr3, non_vec_arg1, non_vec_arg2):
        ...

    This decorator makes it so that the child function's arguments are assured
    to be Numpy arrays of at least 1 dimension, and all having the same shape.
    The child can then perform vectorized computations without having to
    special-case scalar-vs.-vector possibilities or worry about manual
    broadcasting. If the inputs to the function are indeed all scalars, the output
    is converted back to scalar upon return.

    Therefore, for the caller, the function appears to have magic broadcasting
    rules equivalent to a Numpy ufunc. Meanwhile the implementer can get
    broadcasting behavior without having to special case the actual inputs.

    """
    def __init__ (self, n_arr):
        """Decorator for making a auto-broadcasting function. Arguments:

        n_arr - The number of array arguments accepted by the decorated function.
                These arguments come at the beginning of the argument list.

        """
        self._n_arr = int (n_arr)
        if self._n_arr < 1:
            raise ValueError ('broadcastiz\'ed function must take at least 1 '
                              'array argument')

    def __call__ (self, subfunc):
        return _Broadcaster (self._n_arr, subfunc)


broadcastize = _BroadcasterDecorator


# Some miscellaneous numerical tools

def rms (x):
    """Return the square root of the mean of the squares of ``x``."""
    return np.sqrt (np.square (x).mean ())


def weighted_variance (x, weights):
    """Return the variance of a weighted sample.

    The weighted sample mean is calculated and subtracted off, so the returned
    variance is upweighted by ``n / (n - 1)``. If the sample mean is known to
    be zero, you should just compute ``np.average (x**2, weights=weights)``.

    """
    n = len (x)
    if n < 3:
        raise ValueError ('cannot calculate meaningful variance of fewer '
                          'than three samples')
    wt_mean = np.average (x, weights=weights)
    return np.average (np.square (x - wt_mean), weights=weights) * n / (n - 1)


# Tophat functions -- numpy doesn't have anything built-in (that I know of)
# that does this in a convenient way that I'd like. These are useful for
# defining functions in a piecewise-ish way, although also pay attention to
# the existence of np.piecewise!
#
# We're careful with inclusivity/exclusivity of the bounds since that can be
# important.

def unit_tophat_ee (x):
    """Tophat function on the unit interval, left-exclusive and right-exclusive.
    Returns 1 if 0 < x < 1, 0 otherwise.

    """
    x = np.asarray (x)
    x1 = np.atleast_1d (x)
    r = ((0 < x1) & (x1 < 1)).astype (x.dtype)
    if x.ndim == 0:
        return np.asscalar (r)
    return r


def unit_tophat_ei (x):
    """Tophat function on the unit interval, left-exclusive and right-inclusive.
    Returns 1 if 0 < x <= 1, 0 otherwise.

    """
    x = np.asarray (x)
    x1 = np.atleast_1d (x)
    r = ((0 < x1) & (x1 <= 1)).astype (x.dtype)
    if x.ndim == 0:
        return np.asscalar (r)
    return r


def unit_tophat_ie (x):
    """Tophat function on the unit interval, left-inclusive and right-exclusive.
    Returns 1 if 0 <= x < 1, 0 otherwise.

    """
    x = np.asarray (x)
    x1 = np.atleast_1d (x)
    r = ((0 <= x1) & (x1 < 1)).astype (x.dtype)
    if x.ndim == 0:
        return np.asscalar (r)
    return r


def unit_tophat_ii (x):
    """Tophat function on the unit interval, left-inclusive and right-inclusive.
    Returns 1 if 0 <= x <= 1, 0 otherwise.

    """
    x = np.asarray (x)
    x1 = np.atleast_1d (x)
    r = ((0 <= x1) & (x1 <= 1)).astype (x.dtype)
    if x.ndim == 0:
        return np.asscalar (r)
    return r


def make_tophat_ee (lower, upper):
    """Return a ufunc-like tophat function on the defined range, left-exclusive
    and right-exclusive. Returns 1 if lower < x < upper, 0 otherwise.

    """
    if not np.isfinite (lower):
        raise ValueError ('"lower" argument must be finite number; got %r' % lower)
    if not np.isfinite (upper):
        raise ValueError ('"upper" argument must be finite number; got %r' % upper)

    def range_tophat_ee (x):
        x = np.asarray (x)
        x1 = np.atleast_1d (x)
        r = ((lower < x1) & (x1 < upper)).astype (x.dtype)
        if x.ndim == 0:
            return np.asscalar (r)
        return r

    range_tophat_ee.__doc__ = ('Ranged tophat function, left-exclusive and '
                               'right-exclusive. Returns 1 if %g < x < %g, '
                               '0 otherwise.') % (lower, upper)
    return range_tophat_ee


def make_tophat_ei (lower, upper):
    """Return a ufunc-like tophat function on the defined range, left-exclusive
    and right-inclusive. Returns 1 if lower < x <= upper, 0 otherwise.

    """
    if not np.isfinite (lower):
        raise ValueError ('"lower" argument must be finite number; got %r' % lower)
    if not np.isfinite (upper):
        raise ValueError ('"upper" argument must be finite number; got %r' % upper)

    def range_tophat_ei (x):
        x = np.asarray (x)
        x1 = np.atleast_1d (x)
        r = ((lower < x1) & (x1 <= upper)).astype (x.dtype)
        if x.ndim == 0:
            return np.asscalar (r)
        return r

    range_tophat_ei.__doc__ = ('Ranged tophat function, left-exclusive and '
                               'right-inclusive. Returns 1 if %g < x <= %g, '
                               '0 otherwise.') % (lower, upper)
    return range_tophat_ei


def make_tophat_ie (lower, upper):
    """Return a ufunc-like tophat function on the defined range, left-inclusive
    and right-exclusive. Returns 1 if lower <= x < upper, 0 otherwise.

    """
    if not np.isfinite (lower):
        raise ValueError ('"lower" argument must be finite number; got %r' % lower)
    if not np.isfinite (upper):
        raise ValueError ('"upper" argument must be finite number; got %r' % upper)

    def range_tophat_ie (x):
        x = np.asarray (x)
        x1 = np.atleast_1d (x)
        r = ((lower <= x1) & (x1 < upper)).astype (x.dtype)
        if x.ndim == 0:
            return np.asscalar (r)
        return r

    range_tophat_ie.__doc__ = ('Ranged tophat function, left-inclusive and '
                               'right-exclusive. Returns 1 if %g <= x < %g, '
                               '0 otherwise.') % (lower, upper)
    return range_tophat_ie


def make_tophat_ii (lower, upper):
    """Return a ufunc-like tophat function on the defined range, left-inclusive
    and right-inclusive. Returns 1 if lower < x < upper, 0 otherwise.

    """
    if not np.isfinite (lower):
        raise ValueError ('"lower" argument must be finite number; got %r' % lower)
    if not np.isfinite (upper):
        raise ValueError ('"upper" argument must be finite number; got %r' % upper)

    def range_tophat_ii (x):
        x = np.asarray (x)
        x1 = np.atleast_1d (x)
        r = ((lower <= x1) & (x1 <= upper)).astype (x.dtype)
        if x.ndim == 0:
            return np.asscalar (r)
        return r

    range_tophat_ii.__doc__ = ('Ranged tophat function, left-inclusive and '
                               'right-inclusive. Returns 1 if %g <= x <= %g, '
                               '0 otherwise.') % (lower, upper)
    return range_tophat_ii


# Step functions

def make_step_lcont (transition):
    """Return a ufunc-like step function that is left-continuous. Returns 1 if
    x > transition, 0 otherwise.

    """
    if not np.isfinite (transition):
        raise ValueError ('"transition" argument must be finite number; got %r' % transition)

    def step_lcont (x):
        x = np.asarray (x)
        x1 = np.atleast_1d (x)
        r = (x1 > transition).astype (x.dtype)
        if x.ndim == 0:
            return np.asscalar (r)
        return r

    step_lcont.__doc__ = ('Left-continuous step function. Returns 1 if x > %g, '
                          '0 otherwise.') % (transition,)
    return step_lcont


def make_step_rcont (transition):
    """Return a ufunc-like step function that is right-continuous. Returns 1 if
    x >= transition, 0 otherwise.

    """
    if not np.isfinite (transition):
        raise ValueError ('"transition" argument must be finite number; got %r' % transition)

    def step_rcont (x):
        x = np.asarray (x)
        x1 = np.atleast_1d (x)
        r = (x1 >= transition).astype (x.dtype)
        if x.ndim == 0:
            return np.asscalar (r)
        return r

    step_rcont.__doc__ = ('Right-continuous step function. Returns 1 if x >= '
                          '%g, 0 otherwise.') % (transition,)
    return step_rcont
