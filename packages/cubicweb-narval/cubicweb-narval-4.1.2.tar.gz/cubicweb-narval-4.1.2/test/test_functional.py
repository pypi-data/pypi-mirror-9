# -*- coding: utf-8 -*-
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

import os.path

from cubicweb import ValidationError, devtools

from cubes.narval.testutils import NarvalBaseTC

import narvalbot

##override default ini file
test_dir = os.path.dirname(__file__)
narvalbot._CW_SOURCES_FILE = os.path.join(test_dir, 'data', 'narval-cw-sources.ini')

class NarvalFunctionalTC(NarvalBaseTC):
    """Test for no operation recipe"""
    def test_noop(self):
        with self.admin_access.web_request() as req:
            recipe = req.create_entity('Recipe', name=u'functest.noop',
                                            script=u'pass')
            self.run_recipe(recipe)

    def test_hello_world(self):
        "test a simple recipe is properly executed"
        with self.admin_access.web_request() as req:
            recipe = req.create_entity('Recipe', name=u'functest.helloworld',
                                            script=u'print("hello world")')
            cwplan = self.run_recipe(recipe)
            self.assertEqual(1, len(cwplan.execution_log))
            self.assertEqual(cwplan.execution_log[0].data.read().rsplit('<br/>', 1)[-1].strip(), 'hello world')

    def test_crlf(self):
        "test a simple recipe with CRLF endlines"
        with self.admin_access.web_request() as req:
            recipe = req.create_entity('Recipe', name=u'functest.crlf',
                                            script=u'print("hello world")\r\nprint "OK?"\r\n')
            cwplan = self.run_recipe(recipe)
            self.assertEqual(1, len(cwplan.execution_log))
            self.assertEqual(cwplan.execution_log[0].data.read().rsplit('<br/>', 1)[-1].strip(), 'hello world\nOK?')

    def test_plan_options(self):
        '''test that options defined on the `Plan` are available in
        the executed recipe, via `plan.options`'''
        with self.admin_access.web_request() as req:
            recipe = req.create_entity('Recipe', name=u'functest.mirror',
                                            script=u'''
assert len(plan.options) == 2
assert plan.options['attr'] == '1'
assert plan.options['autre'] == '2'
''')
            self.run_recipe(recipe, options=u'attr=1\n autre=2')
            self.run_recipe(recipe, options=u'attr=1\n autre=3', expected_status='error')


    def test_traceback_in_recipe(self):
        '''check a traceback in the executed script is properly
        handled by the bot'''
        with self.admin_access.web_request() as req:
            recipe = req.create_entity('Recipe', name=u'functest.werror',
                                            script=u'''
def toto():
    b = c

toto()
''')
            cwplan = self.run_recipe(recipe, expected_status='error')
            self.assertEqual(1, len(cwplan.execution_log))
            self.assertIn('NameError: global name',
                          cwplan.execution_log[0].data.read())


    def test_sigkill(self):
        '''check the situation where the script dies via a sigkill
        (segfault or similar) is properly handled'''
        with self.admin_access.web_request() as req:
            recipe = req.create_entity('Recipe', name=u'functest.werror',
                                            script=u'''
import os
import signal
print "banzai!"
os.kill(os.getpid(), signal.SIGKILL)
''')
            cwplan = self.run_recipe(recipe, expected_status='killed')
            self.assertEqual(1, len(cwplan.execution_log))
            self.assertIn('banzai!', cwplan.execution_log[0].data.read())

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
