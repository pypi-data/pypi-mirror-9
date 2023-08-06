# copyright 2010-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-narval specific hooks and operations"""

from datetime import datetime, timedelta

from cubicweb import ValidationError
from cubicweb.predicates import is_instance
from cubicweb.server import hook


__docformat__ = "restructuredtext en"


class ServerStartupHook(hook.Hook):
    """add looping task to automatically start tests
    """
    __regid__ = 'narval.startup'
    events = ('server_startup',)
    def __call__(self):
        cleanupdelay = self.repo.config['plan-cleanup-delay']
        if not cleanupdelay:
            return # no auto cleanup
        cleanupinterval = min(60*60*24, cleanupdelay)
        def cleanup_plans(repo, delay=timedelta(seconds=cleanupdelay),
                          now=datetime.now):
            session = repo.internal_session()
            mindate = now() - delay
            try:
                for etype in [repo.schema['Plan']] + repo.schema['Plan'].specialized_by():
                    session.execute('DELETE %s TE WHERE '
                                    'TE modification_date < %%(min)s' % etype,
                                    {'min': mindate})
                    session.commit()
                    session.set_pool()
            finally:
                session.close()
        self.repo.looping_task(cleanupinterval, cleanup_plans, self.repo)


class AfterPlanCreated(hook.Hook):
    """a plan has been created:
    * check it can actually be started
    * if so, ask the bot to execute it

    XXX do this on the 'execution_of' relation creation
    """
    __regid__ = 'narval.start_plan'
    __select__ = hook.Hook.__select__ & is_instance('Plan')
    events = ('after_add_entity',)

    def __call__(self):
        plan = self.entity
        if not plan.recipe.may_be_started():
            msg = self._cw._('recipe may not be started')
            raise ValidationError(plan.eid, {None: msg})

class BeforePlanCreated(hook.Hook):
    __regid__ = 'narval.plan.set_script'
    __select__ = hook.Hook.__select__ & is_instance('Plan')
    events = ('before_add_entity',)

    def __call__(self):
        plan = self.entity
        if 'execution_of' not in plan.cw_edited:
            return
        eid = plan.cw_edited['execution_of']
        recipe = self._cw.execute('Recipe R WHERE R eid %(r)s',
                                  {'r': eid}).get_entity(0,0)
        plan.cw_edited['script'] = recipe.script
