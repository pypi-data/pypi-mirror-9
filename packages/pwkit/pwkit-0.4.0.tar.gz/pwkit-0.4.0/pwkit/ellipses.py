# -*- mode: python; coding: utf-8 -*-
# Copyright 2012-2014 Peter Williams <peter@newton.cx> and collaborators.
# Licensed under the MIT License.

"""pwkit.ellipses - utilities for manipulating 2D Gaussians and ellipses

Useful for sources and bivariate error distributions. We can express the shape
of the function in several ways, which have different strengths and
weaknesses:

* "biv", as in Gaussian bivariate: sigma x, sigma y, cov(x,y)
* "ell", as in ellipse: major, minor, PA [*]
* "abc": coefficients such that z = exp (ax² + bxy + cy²)

[*] Any slice through a 2D Gaussian is an ellipse. Ours is defined such it is
the same as a Gaussian bivariate when major = minor.

Note that when considering astronomical position angles, conventionally
defined as East from North, the Dec/lat axis should be considered the X axis
and the RA/long axis should be considered the Y axis.

Possible TODO: make more array-friendly. All of the bounds-checking becomes a
pain (e.g. need to wrap in np.any()) to make array-friendly while still
providing useful debug output. np.vectorize() might save the day here, or my
@numutil.broadcastize.

NOTE: Pineau et al 2011A&A...527A.126P has some relevant equations, including
ones for computing the overlap of two error ellipses, which is something I've
had trouble figuring out in the past.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = (b'F2S S2F sigmascale clscale '
           b'bivell bivnorm bivabc databiv bivrandom bivplot '
           b'ellnorm ellpoint elld2 ellbiv ellabc ellplot '
           b'abcell abcd2 abcplot').split ()

import numpy as np


# Some utilities for scaling ellipse axis lengths

F2S = 1 / np.sqrt (8 * np.log (2)) # FWHM to sigma; redundant w/ astutil
S2F = np.sqrt (8 * np.log (2))


def sigmascale (nsigma):
    """Say we take a Gaussian bivariate and convert the parameters of the
    distribution to an ellipse (major, minor, PA). By what factor should we
    scale those axes to make the area of the ellipse correspond to the n-sigma
    confidence interval?

    """
    from scipy.special import erfc
    if nsigma <= 0:
        raise ValueError ('nsigma must be positive (%.10e)' % nsigma)
    return np.sqrt (-2 * np.log (erfc (nsigma / np.sqrt (2))))


def clscale (cl):
    """Say we take a Gaussian bivariate and convert the parameters of the
    distribution to an ellipse (major, minor, PA). By what factor should we
    scale those axes to make the area of the ellipse correspond to the
    confidence interval CL? (I.e. 0 < CL < 1)

    """
    if cl <= 0 or cl >= 1:
        raise ValueError ('must have 0 < cl < 1 (%.10e)' % cl)
    return np.sqrt (-2 * np.log (1 - cl))


# Bivariate form: sigma x, sigma y, cov(x,y)

def _bivcheck (sx, sy, cxy):
    if sx <= 0:
        raise ValueError ('negative sx (%.10e)' % sx)
    if sy <= 0:
        raise ValueError ('negative sy (%.10e)' % sy)
    if abs (cxy) >= sx * sy:
        raise ValueError ('illegal covariance (sx=%.10e, sy=%.10e, cxy=%.10e, '
                          'cxy/sxsy=%.16f)' % (sx, sy, cxy, cxy / (sx * sy)))
    return sx, sy, cxy # convenience


def bivell (sx, sy, cxy):
    """Given the parameters of a Gaussian bivariate distribution, compute the
    parameters for the equivalent 2D Gaussian in ellipse form (major, minor,
    pa).

    Inputs:

    * sx: standard deviation (not variance) of x var
    * sy: standard deviation (not variance) of y var
    * cxy: covariance (not correlation coefficient) of x and y

    Outputs:

    * mjr: major axis of equivalent 2D Gaussian (sigma, not FWHM)
    * mnr: minor axis
    * pa: position angle, rotating from +x to +y

    Lots of sanity-checking because it's obnoxiously easy to have numerics
    that just barely blow up on you.

    """
    # See CfA notebook #1 pp. 129-133.
    _bivcheck (sx, sy, cxy)
    from numpy import arctan2, sqrt

    sx2, sy2, cxy2 = sx**2, sy**2, cxy**2

    pa = 0.5 * arctan2 (2 * cxy, sx2 - sy2)
    h = sqrt ((sx2 - sy2)**2 + 4*cxy2)

    t = 2 * (sx2 * sy2 - cxy2) / (sx2 + sy2 - h)
    if t < 0:
        raise ValueError ('covariance just barely out of bounds [1] '
                          '(sx=%.10e, sy=%.10e, cxy=%.10e, cxy/sxsy=%.16f)' %
                          (sx, sy, cxy, cxy / (sx * sy)))
    mjr = sqrt (t)

    t = 2 * (sx2 * sy2 - cxy2) / (sx2 + sy2 + h)
    if t < 0: # if we got this far, shouldn't happen, but ...
        raise ValueError ('covariance just barely out of bounds [2] '
                          '(sx=%.10e, sy=%.10e, cxy=%.10e, cxy/sxsy=%.16f)' %
                          (sx, sy, cxy, cxy / (sx * sy)))
    mnr = sqrt (t)

    return ellnorm (mjr, mnr, pa)


def bivnorm (sx, sy, cxy):
    """Given the parameters of a Gaussian bivariate distribution, compute the
    correct normalization for the equivalent 2D Gaussian. It's 1 / (2 pi sqrt
    (sx**2 sy**2 - cxy**2). This function adds a lot of sanity checking.

    Inputs:

    * sx: standard deviation (not variance) of x var
    * sy: standard deviation (not variance) of y var
    * cxy: covariance (not correlation coefficient) of x and y

    Returns: the scalar normalization

    """
    _bivcheck (sx, sy, cxy)
    from numpy import pi, sqrt

    t = (sx * sy)**2 - cxy**2
    if t <= 0:
        raise ValueError ('covariance just barely out of bounds '
                          '(sx=%.10e, sy=%.10e, cxy=%.10e, cxy/sxsy=%.16f)' %
                          (sx, sy, cxy, cxy / (sx * sy)))
    return (2 * pi * sqrt (t))**-1


def bivabc (sx, sy, cxy):
    """Compute nontrivial parameters for evaluating a bivariate distribution
    as a 2D Gaussian. Inputs:

    * sx: standard deviation (not variance) of x var
    * sy: standard deviation (not variance) of y var
    * cxy: covariance (not correlation coefficient) of x and y

    Returns: (a, b, c), where z = k exp (ax² + bxy + cy²)

    The proper value for k can be obtained from bivnorm().

    """
    _bivcheck (sx, sy, cxy)

    sx2, sy2, cxy2 = sx**2, sy**2, cxy**2
    t = 1. / (sx2 * sy2 - cxy2)
    if t <= 0:
        raise ValueError ('covariance just barely out of bounds '
                          '(sx=%.10e, sy=%.10e, cxy=%.10e, cxy/sxsy=%.16f)' %
                          (sx, sy, cxy, cxy / (sx * sy)))

    a = -0.5 * sy2 * t
    c = -0.5 * sx2 * t
    b = cxy * t
    return _abccheck (a, b, c)


def databiv (xy, coordouter=False, **kwargs):
    """Compute the main parameters of a bivariate distribution from data. The
    parameters are returned in the same format as used in the rest of this
    module.

    * xy: a 2D data array of shape (2, nsamp) or (nsamp, 2)
    * coordouter: if True, the coordinate axis is the outer axis; i.e.
      the shape is (2, nsamp). Otherwise, the coordinate axis is the
      inner axis; i.e. shape is (nsamp, 2).

    Returns: (sx, sy, cxy)

    In both cases, the first slice along the coordinate axis gives the X data
    (i.e., xy[0] or xy[:,0]) and the second slice gives the Y data (xy[1] or
    xy[:,1]).

    """
    xy = np.asarray (xy)
    if xy.ndim != 2:
        raise ValueError ('"xy" must be a 2D array')

    if coordouter:
        if xy.shape[0] != 2:
            raise ValueError ('if "coordouter" is True, first axis of "xy" '
                              'must have size 2')
    else:
        if xy.shape[1] != 2:
            raise ValueError ('if "coordouter" is False, second axis of "xy" '
                              'must have size 2')

    cov = np.cov (xy, rowvar=coordouter, **kwargs)
    sx, sy = np.sqrt (np.diag (cov))
    cxy = cov[0,1]
    return _bivcheck (sx, sy, cxy)


def bivrandom (x0, y0, sx, sy, cxy, size=None):
    """Compute random values distributed according to the specified bivariate
    distribution.

    Inputs:

    * x0: the center of the x distribution (i.e. its intended mean)
    * y0: the center of the y distribution
    * sx: standard deviation (not variance) of x var
    * sy: standard deviation (not variance) of y var
    * cxy: covariance (not correlation coefficient) of x and y
    * size (optional): the number of values to compute

    Returns: array of shape (size, 2); or just (2, ), if size was not
      specified.

    The bivariate parameters of the generated data are approximately
    recoverable by calling 'databiv(retval)'.

    """
    from numpy.random import multivariate_normal as mvn
    p0 = np.asarray ([x0, y0])
    cov = np.asarray ([[sx**2, cxy],
                       [cxy, sy**2]])
    return mvn (p0, cov, size)


def bivplot (sx, sy, cxy, **kwargs):
    _bivcheck (sx, sy, cxy)
    return ellplot (*bivell (sx, sy, cxy), **kwargs)


# Ellipse form: major, minor, pa

def _ellcheck (mjr, mnr, pa):
    if mjr <= 0:
        raise ValueError ('mjr must be positive (%.10e)' % mjr)
    if mnr <= 0:
        raise ValueError ('mnr must be positive (%.10e)' % mnr)
    if mnr > mjr:
        raise ValueError ('mnr must be less than mjr (mnr=%.10e, '
                          'mjr=%.10e)' % (mnr, mjr))
    return mjr, mnr, pa


def ellnorm (mjr, mnr, pa):
    if mjr <= 0:
        raise ValueError ('mjr must be positive (%.10e)' % mjr)
    if mnr <= 0:
        raise ValueError ('mnr must be positive (%.10e)' % mnr)

    from numpy import pi
    hp = 0.5 * pi

    if mnr > mjr:
        mjr, mnr = mnr, mjr
        pa += hp

    while pa < -hp:
        pa += pi
    while pa >= hp:
        pa -= pi

    return mjr, mnr, pa


def ellpoint (mjr, mnr, pa, th):
    """Compute a point on an ellipse parametrically. Inputs:

    * mjr: major axis (sigma not FWHM) of the ellipse
    * mnr: minor axis (sigma not FWHM) of the ellipse
    * pa: position angle (from +x to +y) of the ellipse, radians
    * th: the parameter, 0 <= th < 2pi: the eccentric anomaly

    Returns: (x, y)

    th may be a vector, in which case x and y will be as well.
    """
    _ellcheck (mjr, mnr, pa)
    from numpy import cos, sin

    ct, st = cos (th), sin (th)
    cp, sp = cos (pa), sin (pa)
    x = mjr * cp * ct - mnr * sp * st
    y = mjr * sp * ct + mnr * cp * st
    return x, y


def elld2 (x0, y0, mjr, mnr, pa, x, y):
    """Given an 2D Gaussian expressed as an ellipse (major, minor, pa), compute a
    "squared distance parameter" such that

       z = exp (-0.5 * d2)

    Inputs:

    * x0: position of Gaussian center on x axis
    * y0: position of Gaussian center on y axis
    * mjr: major axis (sigma not FWHM) of the Gaussian
    * mnr: minor axis (sigma not FWHM) of the Gaussian
    * pa: position angle (from +x to +y) of the Gaussian, radians
    * x: x coordinates of the locations for which to evaluate d2
    * y: y coordinates of the locations for which to evaluate d2

    Returns: d2, distance parameter defined as above.

    x0, y0, mjr, and mnr may be in any units so long as they're consistent. x
    and y may be arrays (of the same shape), in which case d2 will be an array
    as well.

    """
    _ellcheck (mjr, mnr, pa)

    dx, dy = x - x0, y - y0
    c, s = np.cos (pa), np.sin (pa)
    a = c * dx + s * dy
    b = -s * dx + c * dy
    return (a / mjr)**2 + (b / mnr)**2


def ellbiv (mjr, mnr, pa):
    """Given a 2D Gaussian expressed as an ellipse (major, minor, pa), compute the
    equivalent parameters for a Gaussian bivariate distribution. We assume
    that the ellipse is normalized so that the functions evaluate identicall
    for major = minor.

    Inputs:

    * mjr: major axis (sigma not FWHM) of the Gaussian
    * mnr: minor axis (sigma not FWHM) of the Gaussian
    * pa: position angle (from +x to +y) of the Gaussian, radians

    Returns:

    * sx: standard deviation (not variance) of x var
    * sy: standard deviation (not variance) of y var
    * cxy: covariance (not correlation coefficient) of x and y

    """
    _ellcheck (mjr, mnr, pa)

    cpa, spa = np.cos (pa), np.sin (pa)
    q = np.asarray ([[cpa, -spa],
                     [spa, cpa]])
    cov = np.dot (q, np.dot (np.diag ([mjr**2, mnr**2]), q.T))
    sx = np.sqrt (cov[0,0])
    sy = np.sqrt (cov[1,1])
    cxy = cov[0,1]

    return _bivcheck (sx, sy, cxy)


def ellabc (mjr, mnr, pa):
    """Given a 2D Gaussian expressed as an ellipse (major, minor, pa), compute the
    nontrivial parameters for its evaluation.

    * mjr: major axis (sigma not FWHM) of the Gaussian
    * mnr: minor axis (sigma not FWHM) of the Gaussian
    * pa: position angle (from +x to +y) of the Gaussian, radians

    Returns: (a, b, c), where z = exp (ax² + bxy + cy²)

    """
    _ellcheck (mjr, mnr, pa)

    cpa, spa = np.cos (pa), np.sin (pa)
    mjrm2, mnrm2 = mjr**-2, mnr**-2

    a = -0.5 * (cpa**2 * mjrm2 + spa**2 * mnrm2)
    c = -0.5 * (spa**2 * mjrm2 + cpa**2 * mnrm2)
    b = cpa * spa * (mnrm2 - mjrm2)

    return _abccheck (a, b, c)


def ellplot (mjr, mnr, pa):
    """Utility for debugging."""
    _ellcheck (mjr, mnr, pa)
    import omega as om

    th = np.linspace (0, 2 * np.pi, 200)
    x, y = ellpoint (mjr, mnr, pa, th)
    return om.quickXY (x, y, 'mjr=%f mnr=%f pa=%f' %
                       (mjr, mnr, pa * 180 / np.pi))


# "ABC" form (maybe better called polynomial form): exp (Ax² + Bxy + Cy²)

def _abccheck (a, b, c):
    if a >= 0:
        raise ValueError ('a must be negative (%.10e)' % a)
    if c >= 0:
        raise ValueError ('c must be negative (%.10e)' % c)
    if b**2 >= 4 * a * c:
        raise ValueError ('must have b² < 4ac (a=%.10e, c=%.10e, '
                          'b=%.10e, b²/4ac=%.10e)' % (a, c, b, b**2/(4*a*c)))
    return a, b, c



def abcell (a, b, c):
    """Given the nontrivial parameters for evaluation a 2D Gaussian as a
    polynomial, compute the equivalent ellipse parameters (major, minor, pa)

    Inputs: (a, b, c), where z = exp (ax² + bxy + cy²)

    Returns:

    * mjr: major axis (sigma not FWHM) of the Gaussian
    * mnr: minor axis (sigma not FWHM) of the Gaussian
    * pa: position angle (from +x to +y) of the Gaussian, radians

    """
    _abccheck (a, b, c)

    from numpy import arctan2, sqrt

    pa = 0.5 * arctan2 (b, a - c)

    t1 = np.sqrt ((a - c)**2 + b**2)
    t2 = -t1 - a - c
    if t2 <= 0:
        raise ValueError ('abc parameters just barely illegal [1] '
                          '(a=%.10e, c=%.10e, b=%.10e, b²/4ac=%.10e)'
                          % (a, c, b, b**2 / (4 * a * c)))
    mjr = t2**-0.5

    t2 = t1 - a - c
    if t2 <= 0: # should never be a problem but ...
        raise ValueError ('abc parameters just barely illegal [2] '
                          '(a=%.10e, c=%.10e, b=%.10e, b²/4ac=%.10e)'
                          % (a, c, b, b**2 / (4 * a * c)))
    mnr = t2**-0.5

    return ellnorm (mjr, mnr, pa)


def abcd2 (x0, y0, a, b, c, x, y):
    """Given an 2D Gaussian expressed as the ABC polynomial coefficients, compute
    a "squared distance parameter" such that

       z = exp (-0.5 * d2)

    Inputs:

    * x0: position of Gaussian center on x axis
    * y0: position of Gaussian center on y axis
    * a: such that z = exp (ax² + bxy + cy²)
    * b: see above
    * c: see above
    * x: x coordinates of the locations for which to evaluate d2
    * y: y coordinates of the locations for which to evaluate d2

    Returns: d2, distance parameter defined as above.

    This is pretty trivial.

    """
    _abccheck (a, b, c)
    dx, dy = x - x0, y - y0
    return -2 * (a * dx**2 + b * dx * dy + c * dy**2)


def abcplot (a, b, c, **kwargs):
    _abccheck (a, b, c)
    return ellplot (*abcell (a, b, c), **kwargs)
