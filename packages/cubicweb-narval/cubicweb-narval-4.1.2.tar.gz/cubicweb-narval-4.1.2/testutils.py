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

import os
import sys
import subprocess
import urllib2
from cStringIO import StringIO
from json import load

from logilab.common.tasksqueue import LOW

from cubicweb.devtools.testlib import CubicWebTC

try:
    import narvalbot
except:
    from cubes.narval import narvalbot
sys.modules['narvalbot'] = narvalbot

import narvalbot as bot
from narvalbot import server, main


os.killpg = lambda x,y: None


class Popen:
    pid = -1
    returncode = 0

    def __init__(self, command, bufsize, stdout, stderr):
        self.command = command
        self.stdout = stdout
        self.stderr = stderr

    def communicate(self):
        pid = os.fork()
        if not pid:
            # forked child
            try:
                sys.stdout = self.stdout
                sys.stderr = self.stderr
                main.run(self.command[1:])
            except SystemExit, ex:
                self.returncode = ex.code
            except:
                self.returncode = -1
                import traceback
                traceback.print_exc(file=sys.stderr)
        else: # parent
            pid, status = os.wait()
            self.returncode = status

class NarvalBaseTC(CubicWebTC):
    """Narval Base class for Narval Recipe test."""
    @classmethod
    def setUpClass(cls):
        super(NarvalBaseTC, cls).setUpClass()
        # monkey patch npm
        server.Popen = Popen

    @classmethod
    def tearDownClass(cls):
        super(NarvalBaseTC, cls).tearDownClass()
        server.Popen = subprocess.Popen

    def setUp(self):
        super(NarvalBaseTC, self).setUp()
        config = bot.NarvalConfiguration()

        def mp_http_post(ch, url, **form):
            if 'files' in form:
                for fname, fval in form.pop('files').items():
                    if not isinstance(fval, tuple):
                        fval = (fname, fval)
                    if isinstance(fval[1], unicode):
                        fval = (fval[0], fval[1].encode('utf-8'))
                    if isinstance(fval[1], basestring):
                        fval = (fval[0], StringIO(fval[1]))
                    form[fname] = fval
            if '_cw_fields' not in form:
                form['_cw_fields'] = ','.join([x for x in form.keys() if not x.startswith('__')])
            data, req = self.http_publish(url, form)
            fp = StringIO(data)
            if req.status_out not in (200,303):
                raise urllib2.HTTPError(url, req.status_out,
                                        "Failed", req.headers_out, fp)
            try:
                return load(fp)
            except:
                return fp

        self.orig_http_get = bot.HTTPConnectionHandler.http_get
        self.orig_http_post = bot.HTTPConnectionHandler.http_post
        bot.HTTPConnectionHandler.http_get = mp_http_post
        bot.HTTPConnectionHandler.http_post = mp_http_post
        # /end connection handler monkey patching, instantiate the process
        # manager
        self.npm = server.NarvalProcessManager(config)
        # go
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute('SET U in_group G WHERE U login "admin", G name "narval", NOT U in_group G')
            cnx.commit()

    def tearDown(self):
        self.npm._quit()
        super(NarvalBaseTC, self).tearDown()
        bot.HTTPConnectionHandler.http_get = self.orig_http_get
        bot.HTTPConnectionHandler.http_post = self.orig_http_post

    def run_recipe(self, recipe, expected_status="done", options=None):
        req = recipe._cw
        cwplan = req.create_entity('Plan', priority=LOW, options=options,
                                   execution_of=recipe)
        req.cnx.commit()
        self.assertEqual(cwplan.execution_status, 'ready')
        self.run_plan(cwplan, expected_status, options)
        return cwplan

    def run_plan(self, cwplan, expected_status="done", options=None):
        queue = [server.NarvalTask('narval', cwplan.eid, cwplan.priority,
                                   cwplan.options)]
        self.npm._start_processes(queue)
        self.assertFalse(queue)
        for thread, plan in self.npm._running_tasks.copy():
            thread.join()
        cwplan = cwplan._cw.execute('Any X, L WHERE X eid %(x)s, X execution_log L',
                                    {'x': cwplan.eid}).get_entity(0, 0)
        self.assertEqual(cwplan.execution_status, expected_status,
                         '%r (got) != %r (expected), execution log:\n%s'
                         % (cwplan.execution_status, expected_status,
                            cwplan.execution_log[0].data.getvalue()))
