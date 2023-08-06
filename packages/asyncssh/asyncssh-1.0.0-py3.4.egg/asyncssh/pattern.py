# Copyright (c) 2015 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

"""Pattern matching for principal and host names"""

from fnmatch import fnmatch

from .logging import *
from .misc import *


class WildcardPattern:
    """A pattern matcher for '*' and '?' wildcards"""

    def __init__(self, pattern):
        # We need to escape square brackets in host patterns if we
        # want to use Python's fnmatch.
        self._pattern = ''.join('[[]' if ch == '[' else
                                '[]]' if ch == ']' else
                                ch for ch in pattern)

    def matches(self, value):
        return fnmatch(value, self._pattern)


class WildcardHostPattern(WildcardPattern):
    """Match a host name or address against a wildcard pattern"""

    def matches(self, host, addr, ip):
        return (host and super().matches(host)) or \
               (addr and super().matches(addr))


class CIDRHostPattern:
    """Match IPv4/v6 address against CIDR-style subnet pattern"""

    def __init__(self, pattern):
        self._network = ip_network(pattern)

    def matches(self, host, addr, ip):
        return ip and ip in self._network


class _PatternList:
    """Match against a list of comma-separated positive and negative patterns

       This class is a base class for building a pattern matcher that
       takes a set of comma-separated positive and negative patterns,
       returning ``True`` if one or more positive patterns match and
       no negative ones do.

       The pattern matching is done by objects returned by the
       build_pattern method. The arguments passed in when a match
       is performed will vary depending on what class build_pattern
       returns.

    """

    def __init__(self, patterns):
        self._pos_patterns = []
        self._neg_patterns = []

        for pattern in patterns.split(','):
            if pattern.startswith('!'):
                negate = True
                pattern = pattern[1:]
            else:
                negate = False

            matcher = self.build_pattern(pattern)

            if negate:
                self._neg_patterns.append(matcher)
            else:
                self._pos_patterns.append(matcher)

    def matches(self, *args):
        pos_match = any(p.matches(*args) for p in self._pos_patterns)
        neg_match = any(p.matches(*args) for p in self._neg_patterns)

        return pos_match and not neg_match


class WildcardPatternList(_PatternList):
    """Match names against wildcard patterns"""

    def build_pattern(self, pattern):
        return WildcardPattern(pattern)


class HostPatternList(_PatternList):
    """Match host names & addresses against wildcard and CIDR patterns"""

    def build_pattern(self, pattern):
        try:
            return CIDRHostPattern(pattern)
        except ValueError:
            return WildcardHostPattern(pattern)
