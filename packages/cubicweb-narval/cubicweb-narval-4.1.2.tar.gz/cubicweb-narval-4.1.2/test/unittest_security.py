# Copyright (c) 2000-2013 LOGILAB S.A. (Paris, FRANCE).
#
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""cubicweb-narval validity tests classes"""

from __future__ import with_statement

__docformat__ = "restructuredtext en"

from logilab.common.tasksqueue import LOW
from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC

class NarvalSecurityTC(CubicWebTC):

    def setUp(self):
        super(NarvalSecurityTC, self).setUp()
        with self.admin_access.repo_cnx() as cnx:
            self.narvaux = cnx.create_entity('CWGroup', name=u'narvaux').eid
            self.toto = self.create_user(cnx, u'toto', groups=('narvaux', 'users')).eid
            self.titi = self.create_user(cnx, u'titi', groups=('users',)).eid

    def test_noop(self):
        with self.admin_access.repo_cnx() as cnx:
            recipe = cnx.create_entity('Recipe', name=u'functest.noop', script=u'pass')

            eperm = cnx.create_entity('CWPermission', name=u'execute', label=u'execute (narvaux)')
            cnx.execute('SET R granted_permission P WHERE R eid %(r)s, P eid %(p)s',
                        {'r': recipe.eid, 'p': eperm.eid})
            cnx.execute('SET P require_group G WHERE G eid %(g)s, P eid %(p)s',
                        {'g': self.narvaux, 'p': eperm.eid})
            cnx.commit()

        with self.new_access('titi').client_cnx() as cnx:
            self.assertRaises(ValidationError, cnx.create_entity, 'Plan',
                              priority=LOW,
                              execution_of=recipe)
        with self.new_access('toto').client_cnx() as cnx:
            plan = cnx.create_entity('Plan', priority=LOW,
                                     execution_of=recipe)
            cnx.commit()

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
