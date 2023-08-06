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
"""Engine is the Narval interpreter: basically wrapped python scripts"""

from __future__ import with_statement

__docformat__ = "restructuredtext en"

import logging
import threading

from tempfile import NamedTemporaryFile

from logilab.common.proc import ResourceController, RESOURCE_LIMIT_EXCEPTION
from logilab.common import logging_ext as lext
from logilab.mtconverter import xml_escape

from . import HTTPConnectionHandler, options_dict


class HTMLFormatter(logging.Formatter):
    """A formatter for the logging standard module, using format easily
    parseable for later in the web (html) ui.
    """

    def format(self, record):
        msg = record.getMessage()
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if msg[-1:] != "\n":
                msg += "\n"
            msg =  record.exc_text
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        return '%s\t%s\t%s\t%s<br/>' % (record.levelno,
                                        record.filename or '',
                                        record.lineno or '',
                                        xml_escape(msg))


class Narval(object):
    def __init__(self, config):
        self.rc = config
        self.resource_ctrl = ResourceController(config.max_cpu_time,
                                                config.max_time,
                                                config.max_memory,
                                                config.max_reprieve)
        threshold = lext.get_threshold(True, config.log_threshold)
        lext.init_log(True, logthreshold=threshold, fmt=HTMLFormatter())
        logging.getLogger('narval').setLevel(threshold)

    def run(self, instance_id, eid):
        """run the plan identified by its eid and exit"""
        # create cnxh
        self.cnxh = HTTPConnectionHandler(instance_id)
        # not true during functional tests due to monkey patches
        if threading.currentThread().getName() == 'MainThread':
            self.resource_ctrl.setup_limit()
        try:
            plandata = self.cnxh.plan(eid)
            self._run_plan(plandata)
        finally:
            if threading.currentThread().getName() == 'MainThread':
                self.resource_ctrl.clean_limit()

    def resource_reached(self, exc, context=None):
        """method for logger to handle RessourceError"""
        if isinstance(exc, MemoryError):
            limit = 'memory'
        else:
            limit = exc.limit
        if context is not None:
            msg = '%s resource limit reached, While %s' % (limit, context)
        else:
            msg = '%s resource limit reached' % limit
        self.critical(msg, exc_info=True)

    def _run_plan(self, plandata):
        """run the given plan"""
        narvalplan = Plan(self.cnxh, plandata)
        narvalplan.fire_transition('start')
        try:
            narvalplan.run()
            narvalplan.fire_transition('end')
        except RESOURCE_LIMIT_EXCEPTION, ex:
            self.resource_reached(ex, 'processing plan %s' % narvalplan.url)
            narvalplan.fire_transition('kill')
            raise
        except Exception:
            self.error('Exception raised while running plan %s',
                       narvalplan.url, exc_info=True)
            narvalplan.fire_transition('fail')
            raise
        except:
            narvalplan.fire_transition('fail')
            raise

LOGGER = logging.getLogger('narval.engine')
lext.set_log_methods(Narval, LOGGER)


class Plan(object):
    """a plan element is a running recipe: RecipeElement + execution context"""

    def __init__(self, cnxh, plandata):
        self.cnxh = cnxh
        self.plandata = plandata
        self.options = options_dict(plandata['options'])
        self.name = plandata['recipe']['name']
        self.script = plandata['script']
        self.url = cnxh.instance_url + str(plandata['eid'])

    def fire_transition(self, trname):
        self.info('fire transition %s of %s', trname, self.url)
        self.cnxh.http_get(self.url, vid='fire_transition', trname=trname)

    def run(self):
        with NamedTemporaryFile(suffix='.py') as f:
            f.write(self.script)
            f.flush()
            execfile(f.name, {'plan': self})

LOGGER = logging.getLogger('narval.engine')
lext.set_log_methods(Plan, LOGGER)
