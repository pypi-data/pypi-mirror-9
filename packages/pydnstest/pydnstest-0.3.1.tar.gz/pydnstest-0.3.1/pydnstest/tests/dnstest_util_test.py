"""
pydnstest
tests for util.py

The latest version of this package is available at:
<https://github.com/jantman/pydnstest>

##################################################################################
Copyright 2013 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of pydnstest.

    pydnstest is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pydnstest is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/pydnstest> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

"""

import pytest

from pydnstest.util import dns_dict_to_string


class TestDNSUtil:
    """
    Tests util.py
    """

    def test_dns_dict_to_string(self):
        """
        Test with a simple dict
        """
        d = {'a': 'vala', 'c': 'valc', 'b': 'valb'}
        s = "{'a': 'vala', 'b': 'valb', 'c': 'valc'}"
        foo = dns_dict_to_string(d)
        assert foo == s

    def test_dns_dict_to_string_deep(self):
        """
        Test with a deep dict
        """
        d = {'a': 'vala', 'c': {'cc': 'valcc', 'ca': 'valca', 'cb': 'valcb'}, 'b': 'valb'}
        s = "{'a': 'vala', 'b': 'valb', 'c': {'ca': 'valca', 'cb': 'valcb', 'cc': 'valcc'}}"
        foo = dns_dict_to_string(d)
        assert foo == s
