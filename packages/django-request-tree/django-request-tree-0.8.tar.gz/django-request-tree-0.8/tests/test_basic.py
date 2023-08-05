#!/usr/bin/python
#
# Copyright (C) 2014 Martin Owens
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os
import sys

sys.path.insert(0, './')
sys.path.insert(0, '../')

import unittest
from request_tree import generate_tree, generate
try:
    from test import test_support
except ImportError:
    from test import support as test_support

@generate
def my_view(request, thing_id=None):
    return (thing_id, request.TREE)

class FakeRequest(object):
    def __init__(self, v):
        self.POST = v

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_00_generate(self):
        """Generate Tree"""
        r = generate_tree({})

    def test_01_dectorator(self):
        v = { 'bread_name': 'foo' }
        (pid, tree) = my_view(FakeRequest(v), 'mid')
        self.assertEqual(pid, 'mid')
        self.assertEqual(tree['bread']['name'], 'foo')

if __name__ == '__main__':
    test_support.run_unittest(
       BasicTestCase,
    )
