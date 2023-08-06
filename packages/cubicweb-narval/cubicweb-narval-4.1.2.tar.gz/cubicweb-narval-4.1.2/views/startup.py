# copyright 2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from cubicweb.predicates import is_instance, none_rset
from cubicweb.web.views import tableview

from cubes.narval.views import no_robot_index

class PlanSummaryTable(tableview.EntityTableView):
    __regid__ = 'narval.plan.summarytable'
    __select__ = is_instance('Plan') | none_rset()

    title = _('Narval plans')
    category = 'startupview'

    layout_args = {'display_filter': 'top'}

    columns = ['execution', 'recipe', 'starttime', 'duration']
    column_renderers = {'execution': tableview.MainEntityColRenderer(vid='narval.plan.statuscell'),
                        'starttime': tableview.EntityTableColRenderer(lambda w, p: w(p._cw.format_date(p.starttime))),
                        'duration': tableview.EntityTableColRenderer(lambda w, p: w(unicode(p.duration))),
                        'recipe': tableview.RelatedEntityColRenderer(lambda p: p.recipe),
                        }
    html_headers = no_robot_index

    def call(self):
        self._cw.add_css('cubes.narval.css')
        if self.cw_rset is None:
            self.cw_rset = self._cw.execute(
                'Any P ORDERBY is_null(PST) DESC, PST DESC '
                'WHERE P is_instance_of Plan,'
                '      TR? wf_info_for P,'
                '      TR tr_count 0,'
                '      TR creation_date PST')
            if not self.cw_rset:
                self.w('<h1>%s</h1>' % _(self.title))
                self.w(_('no plans'))
                return
        super(PlanSummaryTable, self).call()

