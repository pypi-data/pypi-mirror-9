# copyright 2001-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of Narval.
#
# Narval is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# Narval is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with Narval.  If not, see <http://www.gnu.org/licenses/>.
"""Command line input functions"""

__docformat__ = "restructuredtext en"

from logilab.common import clcommands as cl

from __pkginfo__ import version

NARVAL = cl.CommandLine('narval', doc='Control Narval agents.', version=version)
ENGINE = None # global making engine accessible **for testing purpose**

from . import NarvalConfiguration

class StartCommand(cl.Command):
    """start the narval process master. Takes optional cubicweb instance
    identifiers from which it should load its task queue.
    """
    name = 'start'
    arguments = '[<cw instance id>...]'
    options = (
        ('debug',
         {'action' : 'store_true', 'short': 'D',
          'help': 'start in debug mode',
          }),
        ('pid-file',
         {'type' : 'string',
          'help': 'daemon\'s pid file',
          }),

        )

    def run(self, args):
        from .server import NarvalProcessManager
        if self.config.debug:
            import logging
            NARVAL.logger.setLevel(logging.DEBUG)
        npm = NarvalProcessManager()
        npm.start(args, self.config.debug, self.config.pid_file)


class GenerateRCFileCommand(cl.Command):
    """generate a configuration file and exist"""
    name = 'rcfile'
    min_args = max_args = 0
    arguments = ''

    def run(self, args):
        from . import NarvalConfiguration
        nc = NarvalConfiguration()
        nc.generate_config()


class RunPlanCommand(cl.Command):
    """start a narval plan."""
    name = 'run-plan'
    arguments = '<instance id> <plan eid 1> ...'
    min_args = 2
    options = [(optname, optdef)
               for optname, optdef in NarvalConfiguration.options
               if optdef['group'] != 'daemon'
               or optname in ('log-threshold',)]

    def run(self, args):
        from . import engine
        # create Narval instance
        narval = engine.Narval(self.config)
        global ENGINE
        ENGINE = narval
        instance_id = args.pop(0)
        for eid in args:
            narval.run(instance_id, eid)


for cmdcls in (StartCommand,
               RunPlanCommand,
               #StopInstanceCommand,
               GenerateRCFileCommand,
               ):
    NARVAL.register(cmdcls)

run = NARVAL.run
