# Copyright 2014 Johnny Wezel
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""
Software version management

This module contains the Version class.
"""
from pkg_resources import get_distribution

__docformat__ = "restructuredtext en"
__author__ = 'Johnny Wezel'

_version = get_distribution('jw.util').version

import itertools
import re

class VersionError(RuntimeError):
    """
    Version Error
    """

class Version(object):
    """
    Software Version

    Usage:

    >>> from jw.util import version
    >>> v=version.Version('1.0a4')
    >>> v
    Version('1.0a4')
    >>> v.incr()
    Version('1.0a5')
    >>> v.decr()
    Version('1.0a4')
    >>> v.incr(-2)
    Version('1.0b')
    >>> v.incr()
    Version('1.0rc')
    >>> v.incr(1)
    Version('1.0rc0.1')
    >>> v2=version.Version('1.0rc1')
    >>> v == v2
    False
    >>> v2 > v
    True
    >>> version.Version('1.0.0')
    Version('1.0')
    >>> version.Version('1.2b0.0')
    Version('1.2b0')
    >>> version.Version('1.2b1')[:2]
    Version('1.2')
    """

    _preReleaseLevels = 'dev', 'a', 'b', 'rc'
    _levels = {v: i for i, v in enumerate(_preReleaseLevels, -len(_preReleaseLevels))}
    _levelValues = {v: k for k, v in _levels.items()}
    _matchRe = re.compile(r'((\d+(\.\d+)*(' + '|'.join(_preReleaseLevels) + r')?))+')
    _parseRe = re.compile(r'(\d+|' + '|'.join(_levels) + r')')

    def __init__(self, ver):
        """
        Create a Version object

        :param ver: Version string
        :type ver: str
        """
        if isinstance(ver, list):
            if all(isinstance(p, int) and -len(self._preReleaseLevels) < p < 1000 for p in ver):
                # Copy construction
                self.version = ver
        else:
            match = self._matchRe.match(str(ver))
            if match:
                vtuple = self._parseRe.finditer(match.group(0))
                vtuple = tuple(v.group(0) for v in vtuple)
            else:
                raise VersionError('Invalid version: "%s"' % str(ver))
            self.version = [int(p) if p.isdigit() else self._levels[p] for p in vtuple]
            if not all(-len(self._preReleaseLevels) <= p < 1000 for p in self.version):
                print self.version
                raise VersionError(
                    'Version levels must be one of %s or an int < 1000' % ', '.join(self._preReleaseLevels)
                )
            self._trim()

    def __repr__(self):
        """
        Representation

        :return: representation
        :rtype: str

        Returns a string representation of the object
        """
        return "Version('%s')" % self.__str__()

    def __str__(self):
        """
        Convert to string

        :return: string
        :rtype: str

        Returns a string of the version
        """
        return ''.join(
            self._levelValues[l] if l < 0 else '.%d' % l if p >= 0 else str(l)
            for p, l in zip([None] + self.version, self.version)
        )

    def __getslice__(self, i, j):
        """
        Return a slice

        :param i: start
        :type i: int
        :param j: end
        :type j: int
        :rtype: Version
        """
        return Version(self.version[i: j])

    def __eq__(self, other):
        """
        Compare equal

        :param other: string or Version object
        :type other: str or Version
        :rtype: bool
        """
        if not isinstance(other, Version):
            other = Version(other)
        return self.version == other.version

    def __ne__(self, other):
        """
        Compare not-equal

        :param other: string or Version object
        :type other: str or Version
        :rtype: bool
        """
        if not isinstance(other, Version):
            other = Version(other)
        return self.version != other.version

    def __gt__(self, other):
        """
        Compare greater-than

        :param other: string or Version object
        :type other: str or Version
        :rtype: bool
        """
        if not isinstance(other, Version):
            other = Version(other)
        return self.version > other.version

    def __lt__(self, other):
        """
        Compare less-than

        :param other: string or Version object
        :type other: str or Version
        :rtype: bool
        """
        if not isinstance(other, Version):
            other = Version(other)
        return self.version < other.version

    def __ge__(self, other):
        """
        Compare greater-or-equal

        :param other: string or Version object
        :type other: str or Version
        :rtype: bool
        """
        if not isinstance(other, Version):
            other = Version(other)
        return self.version >= other.version

    def __le__(self, other):
        """
        Compare less-than

        :param other: string or Version object
        :type other: str or Version
        :rtype: bool
        """
        if not isinstance(other, Version):
            other = Version(other)
        return self.version <= other.version

    def incr(self, level=-1):
        """
        Increment level

        :param level: Level to increase
        :type level: int
        :return: self
        :rtype: Version

        Increments a level (the lowest by default). Higher levels can be specified by setting level to -2 (one level
        higher) or less and lower levels by setting level to 0 or higher.
        """
        return self.add(1, level)

    def decr(self, level=-1):
        """
        Decrement level

        :param level: Level to decrease
        :type level: int
        :return: self
        :rtype: Version

        Decrements a level (the lowest by default). Higher levels can be specified by setting level to -2 (one level
        higher) or less and lower levels by setting level to 0 or higher.
        """
        return self.add(-1, level)

    def add(self, amount, level=-1):
        """
        Change a level

        :param amount: amount to increase or decrease level
        :type amount: int
        :param level: level to increase or decrease
        :type level: int
        :return: self

        Changes a level (the lowest by default). Higher levels can be specified by setting level to -2 (one level
        higher) or less and lower levels by setting level to 0 or less.
        """
        if level >= 0:
            self.version += (level + 1) * (0,)
            level = -1
        level %= len(self.version)
        v = list(self.version)
        v[level] += amount
        self.version = v[:level + 1]
        self._trim()
        return self

    def _trim(self):
        """
        Trim version down to possibly two levels or one after a pre-release level, e.g. 1.0 and 1.2b0 are not trimmed.
        """
        while len(self.version) > 2 and self.version[-2] >= 0 and self.version[-1] == 0:
            del self.version[-1]

class _Operation(object):
    """
    Operate on version
    """

    def __init__(self, version):
        """
        Create a _Operation object
        """
        self.version = version
        self.level = -1
        self.operations = self.incr, self.decr, self.up, self.down

    def operate(self, opcode):
        """
        Operate on object
        """
        self.operations[opcode]()

    def incr(self):
        """
        Increment level
        """
        self.version.incr(self.level)

    def decr(self):
        """
        Decrement level
        """
        self.version.decr(self.level)

    def up(self):
        """
        Up one level
        """
        self.level -= 1

    def down(self):
        """
        Down one level
        """
        self.level += 1

try:
    import hgapi as _hgapi
except ImportError:
    _hgapi = None

_OPERATIONS = {n: i for i, n in enumerate(('increment', 'decrement', 'up', 'down'))}
_TEMP_FILE_TEMPLATE = '~.%'
_MAX_FILE_SIZE = 1024 * 1024
_DEFAULT_WITHIN_REGEX = r'version\s*=\s*["\'][^"\']*["\']'

def _Matches(args, content):
    # Scan content
    if args.within:
        # If --within given, narrow down search to given regular expressions
        # noinspection PyProtectedMember
        matches = itertools.ifilter(
            None,
            (
                Version._matchRe.search(content, m.start(), m.end())
                for m in itertools.chain.from_iterable(
                r.finditer(content) for r in args.within
            )
            )
        )
    else:
        # noinspection PyProtectedMember
        matches = Version._matchRe.finditer(content)
    return matches

def _Tag(filename, args):
    """
    Set Mercurial tag from version found
    """
    # Initialize
    result = 0
    # Read file
    content = open(filename).read()
    # Find matches
    matches = list(_Matches(args, content))
    if len(matches) > 1:
        raise RuntimeError('More than one version found--Cannot create Mercurial tag')
    repo = _hgapi.Repo(args.hg_tag or '.')
    ver = content[matches[0].start(): matches[0].end()]
    if args.dry_run:
        print 'Would update tags from', filename, 'to', ver
    else:
        if args.verbose:
            print 'Updating tags from', filename, 'to', ver
        repo.hg_tag(str(ver))
        result = 1
    return result

def _Handle(filename, args, ops):
    """
    Handle file
    """
    # Initialize
    result = 0
    vlist = []
    # Read file
    content = open(filename).read()
    # Find matches
    matches = _Matches(args, content)
    # Apply changes in descending order
    newContent = bytearray(content)
    for m in sorted(matches, key=lambda match: match.start(), reverse=True):
        v = Version(content[m.start():m.end()])
        if not args.list:
            operation = _Operation(v)
            ops = list(ops)
            for o in ops:
                operation.operate(o)
            if args.synchronize:
                if not args.synchronizedVersion:
                    args.synchronizedVersion = v
                if args.dry_run or args.verbose:
                    print '%s: %s --> %s' % (filename, content[m.start():m.end()], str(args.synchronizedVersion))
                if not args.dry_run:
                    newContent[m.start():m.end()] = str(args.synchronizedVersion)
            else:
                if args.dry_run or args.verbose:
                    print '%s: %s --> %s' % (filename, content[m.start():m.end()], str(v))
                if not args.dry_run:
                    newContent[m.start():m.end()] = str(v)
        if args.list or args.hg_tag is not False:
            vlist.append(v)
    # Write back changes
    outFilename = _TEMP_FILE_TEMPLATE % filename if args.all_or_nothing else filename
    open(outFilename, 'w').write(newContent)
    result = 1
    # List versions if requested
    if args.list:
        for v in reversed(vlist):
            if args.verbose:
                print '%s: %s' % (filename, v)
            else:
                print '%s' % v
    return result

def _Main():
    """
    version main program
    """
    import argparse
    import glob
    import sys
    import os

    # Initialize
    result = 0
    # Set up argument parsing
    argp = argparse.ArgumentParser(description='A utility program to manage versions')
    argp.add_argument('--all-or-nothing', '-a', action='count', help='Change all files or none')
    argp.add_argument(
        '--move',
        '-m',
        action='store',
        nargs='*',
        help=(
            'Complex increment path. MOVE is either up, down, increment or decrement or any unique abbreviation '
            'thereof'
        )
    )
    argp.add_argument('--down', '-d', action='count', help='Increment one or more levels up (from 1.0.2 go to 1.1)')
    argp.add_argument('--up', '-u', action='count', help='Increment one or more levels down (from 1.0 go to 1.0.1)')
    argp.add_argument('--list', '-l', action='count', help='List version occurences. No version bumped.')
    argp.add_argument('--synchronize', '-s', action='count', help='Synchronize all versions to first occurrence')
    if _hgapi:
        argp.add_argument(
            '--hg-tag',
            '-t',
            action='store',
            default=False,
            nargs='?',
            metavar='DIRECTORY',
            help='Set Mercurial tag (default DIRECTORY: .) No version bumped.'
        )
    argp.add_argument(
        '--within',
        '-w',
        action='store',
        nargs='*',
        type=lambda r: re.compile(r, re.IGNORECASE),
        help=(
            'Case-insensitive regular expression to narrow down the search (default: %s)' % _DEFAULT_WITHIN_REGEX
        )
    )
    argp.add_argument('--verbose', '-v', action='count', help='List changes')
    argp.add_argument('--dry-run', '-n', action='count', help="Don't make any changes. Only print what would be done")
    argp.add_argument('--version', '-V', action='version', version='Version %s' % _version, help='Print version')
    argp.add_argument(
        'filename',
        action='store',
        nargs='*',
        help='Name of a file to handle (after --move/-m, --hg-tag/-t and --within/-w, prepend file list with a --)'
    )
    if not _hgapi:
        argp.epilog = (
            'Package hgapi not installed. Mercurial not available\n'
            'To install hgapi, type: pip install hgapi\n'
        )
    # Parse arguments
    args = argp.parse_args()
    # Check arguments
    if bool(args.move) + (bool(args.down) or bool(args.up)) + bool(args.hg_tag) > 1:
        argp.error("Options --move/-m, --hg-tag/-t and --down/-d/--up/-u are mutually exclusive")
    if args.within == []:
        args.within = [re.compile(_DEFAULT_WITHIN_REGEX, re.IGNORECASE)]
    if args.synchronize:
        args.synchronizedVersion = None  # abuse args as a context object
    # Get list of files to process
    fileList = list(itertools.chain.from_iterable(glob.glob(g) for g in args.filename))
    if args.hg_tag is not False:
        # Set Mercurial tag
        if len(fileList) != 1:
            argp.error('--hg-tag/-t requires one single file')
        result = _Tag(fileList[0], args)
    else:
        # Prepare operations
        if args.move:
            ops = zip(([n for n in _OPERATIONS if n.startswith(o.lower())] for o in args.move), args.move)
            invalid = [o for o in ops if not o[0]]
            ambiguous = [o for o in ops if len(o[0]) > 1]
            if invalid:
                argp.error('Invalid operation(s): %s' % ', '.join(i[1] for i in invalid))
            if ambiguous:
                argp.error('Ambiguous operation(s): %s' % ', '.join(i[1] for i in ambiguous))
            ops = (_OPERATIONS[o[0][0]] for o in ops)
        elif args.up or args.down:
            # Go up and bump if requested, then go down and bump if requested
            ops = (args.up or 0) * (2,) + bool(args.up) * (0,) + (args.down or 0) * (3,) + bool(args.down) * (0,)
        elif args.list:
            ops = ()
        else:
            # If no specific operation (--move, --up/--down/--list/--hg-tag) is given, just bump the current level
            ops = 0,
        # Process files
        try:
            if not fileList:
                argp.error('File argument required')
            for filename in fileList:
                if os.stat(filename).st_size > _MAX_FILE_SIZE:
                    sys.stderr.write('File "%s" too big---not processed\n' % filename)
                else:
                    result += _Handle(filename, args, ops)
                    if not args.list:
                        print '%s%s changed' % (filename, args.dry_run and ' would be' or '')
            if args.all_or_nothing:
                if result != len(fileList):
                    print 'No changes done because of errors (--all-or-nothing)'
                else:
                    for filename in fileList:
                        os.rename('.~' + filename, filename)
            if args.verbose and not args.list:
                print '%s file%s%s changed' % (result, (result != 1) * 's', args.dry_run and ' would be' or '')
        # Clean up
        finally:
            if args.all_or_nothing:
                for filename in fileList:
                    try:
                        os.remove(_TEMP_FILE_TEMPLATE % filename)
                    except:
                        pass
    return 0 if result == len(fileList) else 1
