# -*- mode: python; coding: utf-8 -*-
# Copyright 2012-2014 Peter Williams <peter@newton.cx> and collaborators.
# Licensed under the MIT License.

"""A simple parser for ini-style files that's better than Python's
ConfigParser/configparser.

Functions:

read            - Generate a stream of `pwkit.Holder`s from an ini-format file.
mutate          - Rewrite an ini file chunk by chunk.
write           - Write a stream of `pwkit.Holder`s to an ini-format file.
mutate_stream   - Lower-level version; only operates on streams, not path names.
read_stream     - Lower-level version; only operates on streams, not path names.
write_stream    - Lower-level version; only operates on streams, not path names.
mutate_in_place - Rewrite an ini file specififed by its path name, in place.

"""

from __future__ import absolute_import, division, print_function, unicode_literals

__all__ = (b'FileChunk InifileError mutate_in_place mutate_stream '
           b'mutate read_stream read write_stream write').split ()

import io, os, re
from . import Holder, PKError

sectionre = re.compile (r'^\[(.*)]\s*$')
keyre = re.compile (r'^(\S+)\s*=(.*)$') # leading space chomped later
escre = re.compile (r'^(\S+)\s*=\s*"(.*)"\s*$')


class InifileError (PKError):
    pass


def read_stream (stream):
    """Python 3 compat note: we're assuming `stream` gives bytes not unicode."""

    section = None
    key = None
    data = None

    for fullline in stream:
        line = fullline.split ('#', 1)[0]

        m = sectionre.match (line)
        if m is not None:
            # New section
            if section is not None:
                if key is not None:
                    section.setone (key, data.strip ().decode ('utf8'))
                    key = data = None
                yield section

            section = Holder ()
            section.section = m.group (1)
            continue

        if len (line.strip ()) == 0:
            if key is not None:
                section.setone (key, data.strip ().decode ('utf8'))
                key = data = None
            continue

        m = escre.match (fullline)
        if m is not None:
            if section is None:
                raise InifileError ('key seen without section!')
            if key is not None:
                section.setone (key, data.strip ().decode ('utf8'))
            key = m.group (1)
            data = m.group (2).replace (r'\"', '"').replace (r'\n', '\n').replace (r'\\', '\\')
            section.setone (key, data.decode ('utf8'))
            key = data = None
            continue

        m = keyre.match (line)
        if m is not None:
            if section is None:
                raise InifileError ('key seen without section!')
            if key is not None:
                section.setone (key, data.strip ().decode ('utf8'))
            key = m.group (1)
            data = m.group (2)
            if not len (data):
                data = ' '
            elif not data[-1].isspace ():
                data += ' '
            continue

        if line[0].isspace () and key is not None:
            data += line.strip () + ' '
            continue

        raise InifileError ('unparsable line: ' + line[:-1])

    if section is not None:
        if key is not None:
            section.setone (key, data.strip ().decode ('utf8'))
        yield section


def read (stream_or_path):
    if isinstance (stream_or_path, basestring):
        return read_stream (io.open (stream_or_path, 'rb'))
    return read_stream (stream_or_path)


# Writing

def write_stream (stream, holders, defaultsection=None):
    """Very simple writing in ini format. The simple stringification of each value
    in each Holder is printed, and no escaping is performed. (This is most
    relevant for multiline values or ones containing pound signs.) `None`s are
    skipped.

    Arguments:

    stream              - A text stream to write to.
    holders             - An iterable of objects to write. Their fields will be
                          written as sections.
    defaultsection=None - Section name to use if a holder doesn't contain a
                          `section` field.

    """
    anybefore = False

    for h in holders:
        if anybefore:
            print ('', file=stream)

        s = h.get ('section', defaultsection)
        if s is None:
            raise ValueError ('cannot determine section name for item <%s>' % h)
        print ('[%s]' % s, file=stream)

        for k in sorted (x for x in h.__dict__.iterkeys () if x != 'section'):
            v = h.get (k)
            if v is None:
                continue

            print ('%s = %s' % (k, v), file=stream)

        anybefore = True


def write (stream_or_path, holders, **kwargs):
    """Very simple writing in ini format. The simple stringification of each value
    in each Holder is printed, and no escaping is performed. (This is most
    relevant for multiline values or ones containing pound signs.) `None`s are
    skipped.

    Arguments:

    stream              - A text stream to write to.
    holders             - An iterable of objects to write. Their fields will be
                          written as sections.
    defaultsection=None - Section name to use if a holder doesn't contain a
                          `section` field.

    """
    if isinstance (stream_or_path, basestring):
        return write_stream (io.open (stream_or_path, 'wt'), holders, **kwargs)
    else:
        return write_stream (stream_or_path, holders, **kwargs)


# Parsing plus inline modification, preserving the file as much as possible.
#
# I'm pretty sure that this code gets the corner cases right, but it hasn't
# been thoroughly tested, and it's a little hairy ...

class FileChunk (object):
    def __init__ (self):
        self.data = Holder ()
        self._lines = []


    def _addLine (self, line, assoc):
        self._lines.append ((assoc, line))


    def set (self, name, value):
        newline = ((u'%s = %s' % (name, value)) + os.linesep).encode ('utf8')
        first = True

        for i in xrange (len (self._lines)):
            assoc, line = self._lines[i]

            if assoc != name:
                continue

            if first:
                self._lines[i] = (assoc, newline)
                first = False
            else:
                # delete the line
                self._lines[i] = (None, None)

        if first:
            # Need to append the line to the last block
            for i in xrange (len (self._lines) - 1, -1, -1):
                if self._lines[i][0] is not None:
                    break

            self._lines.insert (i + 1, (name, newline))


    def emit (self, stream):
        for assoc, line in self._lines:
            if line is None:
                continue
            stream.write (line)


def mutate_stream (instream, outstream):
    """Python 3 compat note: we're assuming `stream` gives bytes not unicode."""

    chunk = None
    key = None
    data = None
    misclines = []

    for fullline in instream:
        line = fullline.split ('#', 1)[0]

        m = sectionre.match (line)
        if m is not None:
            # New chunk
            if chunk is not None:
                if key is not None:
                    chunk.data.setone (key, data.strip ().decode ('utf8'))
                    key = data = None
                yield chunk
                chunk.emit (outstream)

            chunk = FileChunk ()
            for miscline in misclines:
                chunk._addLine (miscline, None)
            misclines = []
            chunk.data.section = m.group (1)
            chunk._addLine (fullline, None)
            continue

        if len (line.strip ()) == 0:
            if key is not None:
                chunk.data.setone (key, data.strip ().decode ('utf8'))
                key = data = None
            if chunk is not None:
                chunk._addLine (fullline, None)
            else:
                misclines.append (fullline)
            continue

        m = escre.match (fullline)
        if m is not None:
            if chunk is None:
                raise InifileError ('key seen without section!')
            if key is not None:
                chunk.data.setone (key, data.strip ().decode ('utf8'))
            key = m.group (1)
            data = m.group (2).replace (r'\"', '"').replace (r'\n', '\n').replace (r'\\', '\\')
            chunk.data.setone (key, data.decode ('utf8'))
            chunk._addLine (fullline, key)
            key = data = None
            continue

        m = keyre.match (line)
        if m is not None:
            if chunk is None:
                raise InifileError ('key seen without section!')
            if key is not None:
                chunk.data.setone (key, data.strip ().decode ('utf8'))
            key = m.group (1)
            data = m.group (2)
            if not data[-1].isspace ():
                data += ' '
            chunk._addLine (fullline, key)
            continue

        if line[0].isspace () and key is not None:
            data += line.strip () + ' '
            chunk._addLine (fullline, key)
            continue

        raise InifileError ('unparsable line: ' + line[:-1])

    if chunk is not None:
        if key is not None:
            chunk.data.setone (key, data.strip ().decode ('utf8'))
        yield chunk
        chunk.emit (outstream)


def mutate (instream_or_path, outstream_or_path, outmode='wb'):
    if isinstance (instream_or_path, basestring):
        instream_or_path = io.open (instream_or_path, 'rb')

    if isinstance (outstream_or_path, basestring):
        outstream_or_path = io.open (outstream_or_path, outmode)

    return mutate_stream (instream_or_path, outstream_or_path)


def mutate_in_place (inpath):
    from sys import exc_info
    from os import rename, unlink

    tmppath = inpath + '.new'

    with io.open (inpath, 'rb') as instream:
        try:
            with io.open (tmppath, 'wb') as outstream:
                for item in mutate_stream (instream, outstream):
                    yield item
                rename (tmppath, inpath)
        except:
            et, ev, etb = exc_info ()
            try:
                os.unlink (tmppath)
            except Exception:
                pass
            raise et, ev, etb
