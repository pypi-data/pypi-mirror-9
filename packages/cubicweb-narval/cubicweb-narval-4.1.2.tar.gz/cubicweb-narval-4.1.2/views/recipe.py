# copyright 2010-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from logilab.common.registry import objectify_predicate

from cubicweb.predicates import is_instance, has_related_entities
from cubicweb.view import EntityView
from cubicweb.web.views import tabs, tableview, uicfg

from cubes.narval.views import no_robot_index

_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl

# Recipe #######################################################################

_pvs.tag_attribute(('Recipe', 'name'), 'hidden')
_pvs.tag_attribute(('Recipe', 'script'), 'hidden')
_pvs.tag_object_of(('*', 'execution_of', 'Recipe'), 'hidden')

class RecipePrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Recipe')

    default_tab = _('narval.recipe.tab_config')
    tabs = [default_tab, _('narval.recipe.tab_executions'),]
    html_headers = no_robot_index


class RecipeConfigTab(tabs.PrimaryTab):
    __select__ = is_instance('Recipe')
    __regid__ = 'narval.recipe.tab_config'

    def render_entity_attributes(self, entity):
        self.w(highlight(entity.script, PythonLexer(), HtmlFormatter()))
        self._cw.add_css('pygments.css')
        super(RecipeConfigTab, self).render_entity_attributes(entity)

class RecipeExecutionsTab(EntityView):
    __select__ = (is_instance('Recipe') &
                  has_related_entities('execution_of', 'object'))
    __regid__ = 'narval.recipe.tab_executions'

    html_headers = no_robot_index

    def cell_call(self, row, col):
        rset = self._cw.execute(
            'Any P ORDERBY is_null(SD) DESC, SD DESC WHERE '
            'P execution_of R, '
            'TR? wf_info_for P, '
            'TR creation_date SD, '
            'TR tr_count 0, '
            'R eid %(r)s', {'r': self.cw_rset[row][col]})
        self.wview('narval.recipe.plans_summary', rset)


@objectify_predicate
def has_errors(cls, req, rset=None, row=0, col=0, **kwargs):
    if not rset:
        return
    recipe = rset.get_entity(0, 0)
    if recipe.check_validity():
        return 1
    return 0

class RecipePlansSummaryTable(tableview.EntityTableView):
    __select__ = is_instance('Plan')
    __regid__ = 'narval.recipe.plans_summary'

    columns = ['execution', 'starttime', 'duration']
    column_renderers = {'execution': tableview.MainEntityColRenderer(),
                        'starttime': tableview.EntityTableColRenderer(lambda w, p: w(p._cw.format_date(p.starttime, time=True))),
                        'duration': tableview.EntityTableColRenderer(lambda w, p: w(unicode(p.duration)))}
    html_headers = no_robot_index

    def call(self):
        self._cw.add_css('cubes.narval.css')
        super(RecipePlansSummaryTable, self).call()

