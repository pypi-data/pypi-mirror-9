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
"""cubicweb-narval entity's classes"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import IFTIndexableAdapter
from cubicweb.predicates import has_related_entities, is_instance

# work around https://www.cubicweb.org/ticket/2559931
@monkeypatch(AnyEntity)
def __json_encode__(self):
    try:
        self.complete()
    except Exception:
        pass
    return super(AnyEntity, self).__json_encode__()


class Recipe(AnyEntity):
    __regid__ = 'Recipe'
    __permissions__ = ('execute',)
    rest_attr = 'name'
    fetch_attrs, cw_fetch_order = fetch_config(['name'])

    def may_be_started(self):
        return self._permissions_are_fulfiled() and not self.check_validity()

    def _permissions_are_fulfiled(self):
        if self._cw.user.matching_groups(('managers', 'narval')):
            return True
        rset = self._cw.execute('CWPermission P WHERE R require_permission P, P name "execute", '
                                'P require_group G, U in_group G, U eid %(u)s, R eid %(r)s',
                                {'u': self._cw.user.eid, 'r': self.eid})
        return bool(rset)

    def check_validity(self):
        """XXX check python script is syntaxically correct
        """
        return ()


class Plan(AnyEntity):
    __regid__ = 'Plan'
    fetch_attrs, cw_fetch_order = fetch_config(['execution_of', 'priority',
                                                'options'])

    def dc_title(self):
        return self._cw._('execution of %s') % self.recipe.dc_title()

    @property
    def recipe(self):
        return self.execution_of[0]

    @property
    def starttime(self):
        wf = self.cw_adapt_to('IWorkflowable')
        hist = wf.workflow_history
        for trinfo in hist:
            if trinfo.transition.name == 'start':
                return trinfo.creation_date

    @property
    def endtime(self):
        wf = self.cw_adapt_to('IWorkflowable')
        hist = wf.workflow_history
        for trinfo in hist:
            if trinfo.transition.name in ('end', 'kill', 'fail'):
                return trinfo.creation_date

    @property
    def duration(self):
        if self.endtime and self.starttime:
            return self.endtime - self.starttime

    @property
    def execution_status(self):
        return self.cw_adapt_to('IWorkflowable').state

    def __json_encode__(self):
        data = super(Plan, self).__json_encode__()
        data['recipe'] = self.recipe
        data['state'] = self.execution_status
        return data

class NoIndexLogFileIndexableAdapter(IFTIndexableAdapter):
    __select__ = is_instance('File') & has_related_entities('execution_log', 'object')

    def get_words(self):
        return {}
