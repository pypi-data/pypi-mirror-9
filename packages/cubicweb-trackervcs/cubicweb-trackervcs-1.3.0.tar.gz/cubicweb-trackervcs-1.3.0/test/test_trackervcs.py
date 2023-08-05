# copyright 2011-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""trackervcs automatic tests"""

from cubicweb.devtools.fill import ValueGenerator
from cubicweb.devtools.testlib import AutomaticWebTest

class MyValueGenerator(ValueGenerator):
    def generate_Repository_source_url(self, entity, index):
        return u'file:///path/to/repo/%s/' % index

    def generate_Repository_local_cache(self, entity, index):
        return u'/tmp/repo/%s/' % index

    def generate_Repository_encoding(self, entity, index):
        return u'utf-8'

    def generate_Project_icon(self, entity, index, **kwargs):
        return None

class AutomaticWebTest(AutomaticWebTest):
    '''provides `to_test_etypes` and/or `list_startup_views` implementation
    to limit test scope
    '''
    no_auto_populate = ('Revision', 'InsertionPoint', 'Patch')
    ignored_relations = set(('nosy_list', 'subproject_of'))

    def to_test_etypes(self):
        '''only test views for entities of the returned types'''
        return set()

    def list_startup_views(self):
        '''only test startup views of the returned identifiers'''
        return ()

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
