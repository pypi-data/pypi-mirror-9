# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-bootstrap automatic tests


uncomment code below if you want to activate automatic test for your cube:

.. sourcecode:: python

    from cubicweb.devtools.testlib import AutomaticWebTest

    class AutomaticWebTest(AutomaticWebTest):
        '''provides `to_test_etypes` and/or `list_startup_views` implementation
        to limit test scope
        '''

        def to_test_etypes(self):
            '''only test views for entities of the returned types'''
            return set(('My', 'Cube', 'Entity', 'Types'))

        def list_startup_views(self):
            '''only test startup views of the returned identifiers'''
            return ('some', 'startup', 'views')
"""

from logilab.common.testlib import TestCase

# this will make sure cubes are in our sys.path
import cubicweb.devtools

from cubes.bootstrap import monkeypatch_default_value


class MonkeypatchDefaultValueTC(TestCase):
    def test_function(self):
        def func(a, b, c=0, d=None, e=False, f=()):
            return c
        self.assertEqual(func(1, 2), 0)
        monkeypatch_default_value(func, 'c', 42)
        self.assertEqual(func(1, 2), 42)

    def test_method(self):
        class Class(object):
            def meth(self, a, b, c=0, d=None, e=False, f=()):
                return c
        obj = Class()
        self.assertEqual(obj.meth(1, 2), 0)
        monkeypatch_default_value(Class.meth, 'c', 42)
        self.assertEqual(obj.meth(1, 2), 42)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
