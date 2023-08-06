# -*- mode: python; coding: utf-8 -*-
# Copyright 2012-2014 Peter Williams <peter@newton.cx> and collaborators.
# Licensed under the MIT License.

"""pwkit.casautil - utilities for using the CASA Python libraries

Variables:

INVERSE_C_SM  - Inverse of C in s/m (useful for wavelength to time conversion)
INVERSE_C_NSM - Inverse of C in ns/m (ditto).
pol_names     - Dict mapping CASA polarization codes to their string names.
pol_to_miriad - Dict mapping CASA polarization codes to their MIRIAD equivalents.
msselect_keys - A set of the keys supported by the CASA ms-select subsystem.
tools         - An object for constructing CASA tools: ``ia = tools.image ()``.

Functions:

datadir       - Return the CASA data directory.
logger        - Create a CASA logger that prints to stderr without leaving a
                casapy.log file around.
forkandlog    - Run a function in a subprocess, returning the text it outputs
                via the CASA logging subsystem.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = (b'INVERSE_C_SM INVERSE_C_NSM pol_names pol_to_miriad msselect_keys '
           b'datadir logger forkandlog tools').split ()


# Some constants that can be useful.

INVERSE_C_SM  = 3.3356409519815204e-09 # inverse speed of light in s/m
INVERSE_C_NSM = 3.3356409519815204 # inverse speed of light in ns/m

pol_names = {
    0: '?',
    1: 'I', 2: 'Q', 3: 'U', 4: 'V',
    5: 'RR', 6: 'RL', 7: 'LR', 8: 'LL',
    9: 'XX', 10: 'XY', 11: 'YX', 12: 'YY',
    13: 'RX', 14: 'RY', 15: 'LX', 16: 'LY',
    17: 'XR', 18: 'XL', 19: 'YR', 20: 'YL',
    21: 'PP', 22: 'PQ', 23: 'QP', 24: 'QQ',
    25: 'RCirc', 26: 'Lcirc', 27: 'Lin', 28: 'Ptot', 29: 'Plin',
    30: 'PFtot', 31: 'PFlin', 32: 'Pang',
}

pol_to_miriad = {
    # see mirtask.util for the MIRIAD magic numbers.
    1: 1, 2: 2, 3: 3, 4: 4, # IQUV
    5: -1, 6: -3, 7: -4, 8: -2, # R/L
    9: -5, 10: -7, 11: -8, 12: -6, # X/Y
    # rest are inexpressible
}

# "polarization" is technically valid, but it pretty much doesn't do
# what you'd want since records generally contain multiple
# pols. ms.selectpolarization() should be used instead. Maybe ditto
# for spw?
msselect_keys = frozenset ('array baseline field observation '
                           'scan scaninent spw taql time uvdist'.split ())


# Finding the data directory

def datadir (*subdirs):
    import os.path

    if 'CASAPATH' in os.environ:
        data = os.path.join (os.environ['CASAPATH'].split ()[0], 'data')
    else:
        import casac

        prevp = None
        p = os.path.dirname (casac.__file__)
        while len (p) and p != prevp:
            data = os.path.join (p, 'data')
            if os.path.isdir (data):
                break
            prevp = p
            p = os.path.dirname (p)

    if not os.path.isdir (data):
        raise RuntimeError ('cannot identify CASA data directory')

    return os.path.join (data, *subdirs)


# Trying to use the logging facility in a sane way.
#
# As soon as you create a logsink, it creates a file called casapy.log. So we
# do some junk to not leave turds all around the filesystem.

def _rmtree_error (func, path, excinfo):
    import sys
    print >>sys.stderr, 'warning: couldn\'t delete temporary file %s: %s (%s)' \
        % (path, excinfo[0], func)


def logger (filter='WARN'):
    import os, shutil, tempfile

    cwd = os.getcwd ()
    tempdir = None

    try:
        tempdir = tempfile.mkdtemp (prefix='casautil')

        try:
            os.chdir (tempdir)
            sink = tools.logsink ()
            sink.setlogfile (os.devnull)
            os.unlink ('casapy.log')
        finally:
            os.chdir (cwd)
    finally:
        if tempdir is not None:
            shutil.rmtree (tempdir, onerror=_rmtree_error)

    sink.showconsole (True)
    sink.setglobal (True)
    sink.filter (filter.upper ())
    return sink


def forkandlog (function, filter='INFO5', debug=False):
    import sys, os

    readfd, writefd = os.pipe ()
    pid = os.fork ()

    if pid == 0:
        # Child process. We never leave this branch.
        #
        # Log messages of priority >WARN are sent to stderr regardless of the
        # status of log.showconsole(). The idea is for this subprocess to be
        # something super lightweight and constrained, so it seems best to
        # nullify stderr, and stdout, to not pollute the output of the calling
        # process.
        #
        # I thought of using the default logger() setup and dup2'ing stderr to
        # the pipe fd, but then if anything else gets printed to stderr (e.g.
        # Python exception info), it'll get sent along the pipe too. The
        # caller would have to be much more complex to be able to detect and
        # handle such output.

        os.close (readfd)

        if not debug:
            f = open (os.devnull, 'w')
            os.dup2 (f.fileno (), 1)
            os.dup2 (f.fileno (), 2)

        sink = logger (filter=filter)
        sink.setlogfile ('/dev/fd/%d' % writefd)
        function (sink)
        sys.exit (0)

    # Original process.

    os.close (writefd)

    with os.fdopen (readfd) as readhandle:
        for line in readhandle:
            yield line

    info = os.waitpid (pid, 0)

    if info[1]:
        # Because we're a generator, this is the only way for us to signal if
        # the process died. We could be rewritten as a context manager.
        e = RuntimeError ('logging child process PID %d exited '
                          'with error code %d' % tuple (info))
        e.pid, e.exitcode = info
        raise e


# Tool factories.

class _Tools (object):
    """This class is structured so that it supports useful tab-completion
    interactively, but also so that new tools can be constructed if the
    underlying library provides them.

    """
    _builtinNames = ('agentflagger atmosphere calanalysis calibrater calplot componentlist '
                     'coordsys deconvolver fitter flagger functional image imagepol '
                     'imager logsink measures msmetadata ms msplot plotms regionmanager '
                     'simulator spectralline quanta table tableplot utils vlafiller '
                     'vpmanager').split ()

    def __getattribute__ (self, n):
        """Returns factories, not instances."""
        # We need to make this __getattribute__, not __getattr__, only because
        # we set the builtin names in the class __dict__ to enable tab-completion.
        import casac

        if hasattr (casac, 'casac'): # casapy >= 4.0?
            t = getattr (casac.casac, n, None)
            if t is None:
                raise AttributeError ('tool "%s" not present' % n)
            return t
        else:
            try:
                return casac.homefinder.find_home_by_name (n + 'Home').create
            except Exception:
                # raised exception is class 'homefinder.error'; it appears unavailable
                # on the Python layer
                raise AttributeError ('tool "%s" not present' % n)

for n in _Tools._builtinNames:
    setattr (_Tools, n, None) # ease autocompletion

tools = _Tools ()
