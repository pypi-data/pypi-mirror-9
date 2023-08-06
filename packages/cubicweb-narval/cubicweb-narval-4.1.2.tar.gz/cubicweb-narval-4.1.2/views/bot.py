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

__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.view import StartupView


class BotStatusView(StartupView):
    """This view displays pending and running plans"""
    __regid__ = 'botstatus'
    title = _('Plan status')

    def call(self):
        req = self._cw
        _ = req._
        self._cw.add_css('cubes.narval.css')
        if not 'vtitle' in req.form:
            self.w(u'<h1>%s</h1>' % _(self.title))
        self._running_plans()
        self._pending_plans()
        self._latest_done_plans()

    def _running_plans(self):
        rset = self._cw.execute('Any P, P, PO WHERE P is_instance_of Plan, '
                                'P in_state S, S name "running", P options PO')
        if rset:
            self.w(u'<h2>%s</h2>'
                   % self._cw._('Running plans (%i)') % len(rset))
            self.wview('table', rset,
                       headers=[self._cw._('Plan_plural'),
                                self._cw._('options')],
                       cellvids={0: 'outofcontext', 1: 'narval.plan.optionscell'})

    def _pending_plans(self):
        rset = self._cw.execute('Any P, PR, P, PO WHERE P is_instance_of Plan, '
                                'P execution_status "ready", P priority PR, P options PO')
        if rset:
            _ = self._cw._
            self.w(u'<h2>%s</h2>' % _('Pending plans (%i)') % len(rset))
            self.wview('table', rset,
                       headers=[_('Plan_plural'), _('priority'), _('options')],
                       cellvids={0: 'outofcontext',
                                 2: 'narval.plan.optionscell'})

    def _latest_done_plans(self):
        rset = self._cw.execute('Any P,P, PO ORDERBY PMD DESC LIMIT 3 WHERE '
                                'P is_instance_of Plan, '
                                'NOT P execution_status IN ("ready", "running"), '
                                'P options PO, P modification_date PMD')
        if rset:
            self.w(u'<h2>%s</h2>' % self._cw._('Latest plans executed'))
            self.wview('table', rset,
                       headers=[self._cw._('Plan_plural'),
                                self._cw._('options')],
                       cellvids={0: 'outofcontext', 1: 'narval.plan.optionscell'})

