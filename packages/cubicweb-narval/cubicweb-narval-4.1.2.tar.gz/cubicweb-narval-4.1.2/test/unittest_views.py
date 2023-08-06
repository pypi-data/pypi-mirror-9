# Copyright (c) 2013 LOGILAB S.A. (Paris, FRANCE).
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

import os.path

from cubicweb import devtools

from cubes.narval.testutils import NarvalBaseTC

import narvalbot

##override default ini file
test_dir = os.path.dirname(__file__)
narvalbot._CW_SOURCES_FILE = os.path.join(test_dir, 'data', 'narval-cw-sources.ini')

class NarvalViewsTC(NarvalBaseTC):
    """Test for no operation recipe"""
    def test_plan_json(self):
        with self.admin_access.web_request() as req:
            recipe = req.create_entity('Recipe', name=u'test.pass', script=u'pass')
            plan = self.run_recipe(recipe, options=u'a=2')
            plan.cw_clear_all_caches()
            json = self.view('ejsonexport', plan.as_rset())
            self.assertEqual(len(json), 1)
            json = json[0]
            self.assertEqual(json['eid'], plan.eid)
            self.assertEqual(json['options'], 'a=2')
            self.assertEqual(json['state'], 'done')
            self.assertEqual(json['recipe']['name'], 'test.pass')
            self.assertEqual(json['recipe']['script'], 'pass')

    def test_plan_ordering(self):
        with self.admin_access.web_request() as req:
            recipe = req.create_entity('Recipe', name=u'test.pass', script=u'pass')
            plan_first = self.run_recipe(recipe, options=u'a=2')
            plan_ready = req.create_entity('Plan', execution_of=recipe)
            plan_last = self.run_recipe(recipe)
            data = self.view('narval.recipe.tab_executions', recipe.as_rset())
            plans = [b['href'] for a, b in data.a_tags if a == 'execution of test.pass']
            self.assertEqual(len(plans), 3)
            self.assertIn(str(plan_ready.eid), plans[0])
            self.assertIn(str(plan_last.eid), plans[1])
            self.assertIn(str(plan_first.eid), plans[2])

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
