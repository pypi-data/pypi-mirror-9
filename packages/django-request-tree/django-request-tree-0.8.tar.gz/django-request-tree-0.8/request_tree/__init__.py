#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Provides a django view decorator for turning flat input into a tree structure
"""

import os
import re
import sys

__pkgname__ = 'django-request-tree'
__version__ = '0.8'

class generate(object):
    def __init__(self, method):
        self.method = method

    def __call__(self, request, *args, **kwargs):
        setattr(request, 'TREE', generate_tree(request.POST))
        return self.method(request, *args, **kwargs)

class UnlessList(object):
    """By default, a list of items, but transforms into a dictionary if a string is set.
       Will also operate as a padded list.
    """
    def __init__(self):
        self.l = []
        self.d = None

    @property
    def is_list(self):
        return self.d == None

    def _index(self, name):
        try:
            return int(name)
        except ValueError:
            return name

    def __setitem__(self, name, value):
        name = self._index(name)
        if self.is_list:
            if isinstance(name, int):
                # Padd the list automatically
                self.l += [None] * (name+1-len(self.l))
                self.l[name] = value
                return
            else:
                t = self.l
                self.d = dict((i, t[i]) for i in range(len(t)) if t[i] != None)
        self.d[name] = value

    def get(self, name, default=None):
        return self.__getitem__(name, default)

    def norm(self):
        """Returns a normalised list/dictionary structure"""
        def _v(v):
            return isinstance(v, UnlessList) and v.norm() or v
        if self.is_list:
            return [ _v(v) for v in self.l ]
        return dict( (k, _v(v)) for (k,v) in self.d.items() )

    def __getitem__(self, name, default='self'):
        default = default=='self' and UnlessList() or default
        name = self._index(name)
        if self.is_list:
            if isinstance(name, int):
                if name >= len(self.l) or self.l[name] == None:
                    self[name] = default
                return self.l[name]
            else: # Conversion happens here
                self[name] = default
        elif not self.d.has_key(name):
            self.d[name] = default
        return self.d[name]

    def __iter__(self):
        return self.is_list and self.l.__iter__() or self.d.__iter__()

    def __repr__(self):
        return self.is_list and self.l.__repr__() or self.d.__repr__()

def data_check(datum):
    try:
        if '.' in datum:
            return float(datum)
        return int(datum)
    except ValueError:
        return datum


def data_tree(method):
    """Decorator for post or get methods (class based)"""
    def _internal(self, *args, **kwargs):
        data = generate_tree(getattr(self.request, self.request.method))
        return method(self, data, *args, **kwargs)
    return _internal


def generate_tree(data, sep='_'):
    """Generates a tree structure from a flat list using a seperator"""
    result = UnlessList()
    for (name, value) in data.items():
        r = result
        rest = name
        while sep in rest:
            (token, rest) = rest.split(sep, 1)
            r = r[token]
        r[rest] = data_check(value)

    return result.norm()


def validate_tree(data, schema):
    """Generates a tree and then validates it against a schema"""
    result = generate_tree(data)

    # lazy import of xssd
    if 'Validator' not in locals():
        from xssd import Validator

    if isinstance(schema, dict):
        schema = Validator(schema)

    return (result, schema.validate(result))


if __name__ == '__main__':
    a = UnlessList()
    d = {
       'fruit_0_name': "banana",
       'fruit_0_colour': "yellow",
       'fruit_1_name': "apple",
       'fruit_1_colour': "red",
       'bread_name': "tigle",
       'bread_type': "05",
    }
    (s, e) = validate_tree(d, {
        'root': [
          {'name':'fruit', 'type':'fruit', 'maxOccurs': 2},
          {'name':'bread', 'type':'bread'},
        ],
        'complexTypes': {
          'fruit': [
            { 'name':'name',   'type':'string' },
            { 'name':'colour', 'type':'string' },
          ],
          'bread': [
            { 'name':'name', 'type':'string' },
            { 'name':'type', 'type':'integer' },
          ],
        },
    })
    print s
    print e

