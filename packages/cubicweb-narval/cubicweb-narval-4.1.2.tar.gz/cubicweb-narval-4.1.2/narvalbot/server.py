# Copyright (c) 2003-2013 LOGILAB S.A. (Paris, FRANCE).
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
"""Narval bot polling plans to be executed"""

__docformat__ = "restructuredtext en"

import os
import sys
import signal
import stat
import logging
import errno
import time
import requests
from subprocess import Popen
from tempfile import TemporaryFile
from threading import Thread, Condition, Timer, currentThread
from urlparse import urljoin, urlparse
from datetime import timedelta

from logilab.common import tasksqueue
from logilab.common.logging_ext import set_log_methods, init_log
from logilab.common.daemon import daemonize, setugid
from logilab.common.configuration import format_option_value

from . import NarvalConfiguration, options_dict, main

class NarvalTask(tasksqueue.Task):

    def __init__(self, instance_id, eid, priority=0, options=None):
        self.instance_id = instance_id
        self.planeid = int(eid)
        self.options = options_dict(options or {})
        super(NarvalTask, self).__init__("%s:%s" % (instance_id, self.planeid),
                                         -int(priority))

    def __hash__(self):
        return hash(self.id)

    def run_command(self, config):
        cmd = [sys.argv[0], 'run-plan', self.instance_id, str(self.planeid)]
        for optname, optdef in main.RunPlanCommand.options:
            value = self.options.get(optname, config[optname])
            fvalue = format_option_value(optdef, value)
            if fvalue:
                cmd.append('--'+optname)
                cmd.append(str(fvalue))
        return cmd


class NarvalProcessManager(object):
    def __init__(self, config=None):
        """ """
        self.config = config or NarvalConfiguration()
        #args = self.config.load_command_line_configuration()
        self._quiting = None
        self._running_tasks = set()
        self._cvar = Condition() # protect _running_tasks and signal free slot
        # interval of time where plan queued while there is an identical plan
        # running will be ignored
        self._skip_duplicate_time_delta = timedelta(seconds=15) # XXX

    def start(self, instance_ids=None, debug=False, pidfile=None):
        config = self.config
        self.instance_ids = instance_ids or config.cnx_infos.keys()
        if debug:
            logthreshold = config['log-threshold'] = 'DEBUG'
        else:
            logthreshold = config['log-threshold']
        init_log(debug, logthreshold=logthreshold, logfile=config['log-file'])
        self._install_sig_handlers()
        # go ! (don't daemonize in debug mode)
        if not debug and daemonize(pidfile):
            return
        # change process uid
        if config['uid']:
            setugid(config['uid'])
        self._loop()

    def _loop(self):
        """enter the service loop"""
        # service loop
        if not self.instance_ids:
            self.warning('There are no CubicWeb sources. Ensure your narval sources configuration file is correct')
            return
        while self._quiting is None:
            queue = set()
            # init the process queue
            for instance_id in self.instance_ids:
                try:
                    self.info('get pending plan from %s', instance_id)
                    for plandata in self.config.cnxh(instance_id).pending_plans():
                        self._queue_plan(queue, instance_id, plandata)
                except Exception, ex:
                    self.exception(str(ex))
            try:
                queue = sorted(queue)
                self._start_processes(queue)
            except SystemExit:
                raise
            except Exception, ex:
                self.exception('error while starting process: %s', ex)
            if not queue:
                # nothing to do, sleep a bit
                delay =  min(float(self.config.cnx_infos[instid].get('poll-delay', 0))
                             for instid in self.instance_ids) or 60
                time.sleep(delay)
            self._wait_for_free_slot()

    def _quit(self):
        """stop the server"""
        self._quiting = True
        with self._cvar:
            for _, t in self._running_tasks:
                try:
                    os.killpg(t.pid, signal.SIGTERM)
                except OSError:
                    pass
            self._cvar.notify()
        for i in xrange(5):
            time.sleep(1)
            with self._cvar:
                if not self._running_tasks:
                    return
        with self._cvar:
            for _, t in self._running_tasks:
                try:
                    os.killpg(t.pid, signal.SIGKILL)
                except OSError:
                    pass
            self._cvar.notify()

    def _install_sig_handlers(self):
        """install signal handlers"""
        self.info('installing signal handlers')
        signal.signal(signal.SIGINT, lambda x, y, s=self: s._quit())
        signal.signal(signal.SIGTERM, lambda x, y, s=self: s._quit())

    # internal process managements #############################################

    def _queue_plan(self, queue, instance_id, plan):
        self.info('queuing plan %s:%s', instance_id, plan['eid'])
        task = NarvalTask(instance_id, plan['eid'], plan['priority'],
                          plan['options'])
        with self._cvar:
            if any(task == t for _, t in self._running_tasks):
                return
        queue.add(task)

    def _wait_for_free_slot(self):
        with self._cvar:
            while not self._can_run_task() and not self._quiting:
                self._cvar.wait()

    def _can_run_task(self):
        with self._cvar:
            return len(self._running_tasks) < self.config['threads']

    def _start_processes(self, queue):
        """start pending plans according to available resources"""
        while self._can_run_task():
            try:
                self._start_process(queue.pop(0))
            except IndexError:
                break

    def _start_process(self, task):
        """start given task in a separated thread"""
        self.info('start test %s', task.id)
        # start a thread to wait for the end of the child process
        thread = Thread(target=self._run_task, args=(task,))
        with self._cvar:
            self._running_tasks.add( (thread, task) )
        thread.start()

    def _run_task(self, task):
        """run the task and remove it from running tasks set once finished"""
        try:
            self._spawn_task_process(task)
        finally:
            with self._cvar:
                self._running_tasks.remove( (currentThread(), task) )
                self._cvar.notify()
            self.info('task %s finished', task.id)

    def _spawn_task_process(self, task):
        """actually run the task by spawning a subprocess"""
        command = task.run_command(self.config)
        outfile = TemporaryFile(mode='w+', bufsize=0)
        errfile = TemporaryFile(mode='w+', bufsize=0)
        self.info(' '.join(command))
        try:
            cmd = Popen(command, bufsize=0, stdout=outfile, stderr=errfile)
        except OSError as e:
            self.error('Cannot create subprocess %r' % command)
            self.debug('Exception: %s' % e)
            return
        task.pid = cmd.pid
        maxtime = task.options.get('max-time', self.config['max-time'])
        if maxtime:
            maxreprieve = task.options.get('max-reprieve',
                                           self.config['max-reprieve'])
            maxtime = maxtime + (maxreprieve or 60) * 1.25
            timer = Timer(maxtime, os.killpg, [cmd.pid, signal.SIGKILL])
            timer.start()
        else:
            timer = None
        cmd.communicate()
        if timer is not None:
            timer.cancel()
        try:
            # kill possibly remaining children
            os.killpg(cmd.pid, signal.SIGKILL)
        except OSError, ex:
            if ex.errno != errno.ESRCH:
                raise
        for stream in (outfile, errfile):
            stream.seek(0)
        if cmd.returncode:
            self.error('error while running %s', command)
            self.error('`%s` returned with status : %s',
                       ' '.join(command), cmd.returncode)
        # add output to Plan entity and change it's state if necessary
        log = u''
        if os.fstat(errfile.fileno())[stat.ST_SIZE]:
            log += unicode(errfile.read(), 'utf-8', 'replace')
            self.info('***** %s error output', ' '.join(command))
            self.info(log)
        if os.fstat(outfile.fileno())[stat.ST_SIZE]:
            out = unicode(outfile.read(), 'utf-8', 'replace')
            self.info('***** %s standard output', ' '.join(command))
            self.info(out)
            log += out

        cnxh = self.config.cnxh(task.instance_id)
        url = cnxh.instance_url + str(task.planeid)
        if cmd.returncode:
            try:
                ret = cnxh.http_get(url, vid='fire_transition', trname='kill')
            except requests.HTTPError, ex:
                # CW returns a 409 (CONFLICT) on ValidationError,
                # expected if plan already is done or failed
                if ex.response.status_code != 409:
                    raise
        files = {'data': ('dummy', log)}
        #an empty binary object is added automatically as "data" by create_subentity
        data = cnxh.http_post(url, vid='create_subentity',
                              __cwetype__='File',
                              __cwrel__='reverse_execution_log',
                              data_name=u'execution_log.txt',
                              data_encoding='utf-8')
        if not data:
            self.warning('Could not create execution_log File for %s' % url)
        else:
            if not cnxh.http_post(url=cnxh.instance_url + 'narval-file-append',
                                  files=files, eid=data[0]['eid']):
                self.warning('Could not upload execution_log for %s' % url)


LOGGER = logging.getLogger('narval.bot')
set_log_methods(NarvalProcessManager, LOGGER)
