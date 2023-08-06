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

from tempfile import NamedTemporaryFile
from logilab.mtconverter import xml_escape
from logilab.common.tasksqueue import REVERSE_PRIORITY
from logilab.common.textutils import splitstrip

from cubicweb import tags, view, Binary
from cubicweb.predicates import (none_rset, is_instance,
                                 match_kwargs, match_form_params)
from cubicweb.web import RequestError
from cubicweb.web.views import tabs, navigation, ibreadcrumbs, json, uicfg

from cubes.narval.views import no_robot_index

from cubicweb.web.views import forms
from cubicweb.web import controller, formwidgets, formfields, Redirect

_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl

_pvs.tag_attribute(('Plan', 'execution_log'), 'relations')
_pvdc.tag_attribute(('Plan', 'execution_log'), {'vid': 'narval.formated_log'})
_pvdc.tag_attribute(('Plan', 'priority',), {'vid': 'tasksqueue.priority'})
_pvs.tag_subject_of(('Plan', 'execution_of', '*'), 'hidden')


class PlanPrimaryView(tabs.TabbedPrimaryView):
    __select__ = is_instance('Plan')

    default_tab = _('narval.plan.tab_setup')
    tabs = [default_tab]
    html_headers = no_robot_index

    def render_entity_title(self, entity):
        #self._cw.add_css('cubes.apycot.css')
        title = self._cw._('Execution of %(recipe)s') % {
            'recipe': entity.recipe.view('outofcontext')}
        self.w('<h1>%s</h1>' % title)

class PlanConfigTab(tabs.PrimaryTab):
    __regid__ = _('narval.plan.tab_setup')
    __select__ = is_instance('Plan')

    html_headers = no_robot_index


class PlanBreadCrumbTextView(ibreadcrumbs.BreadCrumbTextView):
    __select__ = is_instance('Plan')
    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        starttime = self._cw.format_date(entity.starttime, time=True)
        if starttime:
            self.w(starttime)
        else:
            self.w(self._cw._(entity.execution_status))

class PlanIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Plan')

    def parent_entity(self):
        """hierarchy, used for breadcrumbs"""
        return self.entity.recipe


class PlanIPrevNextAdapter(navigation.IPrevNextAdapter):
    __select__ = is_instance('Plan')

    def previous_entity(self):
        rset = self._cw.execute(
            'Any X,R ORDERBY X DESC LIMIT 1 '
            'WHERE X is Plan, X execution_of R, R eid %(c)s, '
            'X eid < %(x)s',
            {'x': self.entity.eid, 'c': self.entity.recipe.eid})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        rset = self._cw.execute(
            'Any X,R ORDERBY X ASC LIMIT 1 '
            'WHERE X is Plan, X execution_of R, R eid %(c)s, '
            'X eid > %(x)s',
            {'x': self.entity.eid, 'c': self.entity.recipe.eid})
        if rset:
            return rset.get_entity(0, 0)


class PriorityView(view.EntityView):
    __regid__ = 'tasksqueue.priority'
    __select__ = is_instance('Plan') & match_kwargs('rtype')

    def cell_call(self, row, col, rtype, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        value = getattr(entity, rtype)
        if value:
            priority = REVERSE_PRIORITY[value]
            self.w(u'<span class="priority_%s">' % priority)
            self.w(xml_escape(self._cw._(priority)))
            self.w(u'</span>')


class PlanStatusCell(view.EntityView):
    __regid__ = 'narval.plan.statuscell'
    __select__ = is_instance('Plan')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(self._cw._(entity.execution_status),
                      href=entity.absolute_url(),
                      klass="global status_%s" % entity.execution_status,
                      title=self._cw._('see detailed execution report')))


class PlanOptionsCell(view.EntityView):
    __regid__ = 'narval.plan.optionscell'
    __select__ = is_instance('Plan')

    def cell_call(self, row, col, **kwargs):
        entity = self.cw_rset.get_entity(row, col)
        if entity.options:
            self.w(xml_escape('; '.join(entity.options.splitlines())))


class FireTransitionView(json.JsonEntityView):
    __regid__ = 'fire_transition'
    __select__ = match_form_params('trname')

    def call(self):
        self._cw.ajax_request = True
        for entity in self.cw_rset.entities():
            entity.cw_adapt_to('IWorkflowable').fire_transition(self._cw.form['trname'])
        self.wdata([])


class SetAttributes(json.JsonEntityView):
    __regid__ = 'set_attributes'

    def call(self):
        self._cw.ajax_request = True
	for entity in self.cw_rset.entities():
            kwargs = {}
            for attribute in entity.e_schema.subject_relations():
                if attribute.final and attribute.type in self._cw.form:
                    kwargs[attribute.type] = self._cw.form[attribute.type]
            if kwargs:
                entity.cw_set(**kwargs)
        self.wdata([])


class CreateSubEntity(json.JsonEntityView):
    '''
    Create a new entity from posted form:
    - `__cwetype__`: type of created entity,
    - `__cwrel__`: relation between the target entity and the created one,
    - `_cw_fields`: initialisation values for entity content

    Produces a JSON representation of the created entities.
    '''
    __regid__ = 'create_subentity'
    __select__ = (json.JsonEntityView.__select__ &
                  match_form_params('__cwetype__', '__cwrel__'))

    def call(self):
        self._cw.ajax_request = True
        etype = self._cw.form.pop('__cwetype__')
        rel = self._cw.form.pop('__cwrel__')
        subentities = []
        try:
            fields = self._cw.form['_cw_fields']
        except KeyError:
            raise RequestError(self._cw._('no edited fields specified'))
        fields = splitstrip(fields)
        kwargs = dict((k, self._cw.form[k]) for k in fields if k in
                      self._cw.form)
        kwargs.pop('vid', None)
        if etype == 'File':
            kwargs.setdefault('data', Binary())
        for entity in self.cw_rset.entities():
            kwargs[rel] = entity
            subentities.append(self._cw.create_entity(etype, **kwargs))
        self.wdata(subentities)


class PendingPlansView(json.JsonMixIn, view.StartupView):
    __regid__ = 'narval.pending-plans'
    __select__ = none_rset()

    def call(self):
        self._cw.ajax_request = True
        self.wdata([dict(eid=x, cwuri=xu, options=xo, priority=xp)
                   for x, xu, xo, xp in self._cw.execute(
            'Any X,XU,XO,XP WHERE X is_instance_of Plan, X cwuri XU, X options XO, X priority XP, '
            'X in_state S, S name "ready"')])

class FileAppendForm(forms.FieldsForm):
    __regid__ = 'narval-file-append'

    data = formfields.FileField(help=_(u'data to append'))
    eid = formfields.IntField(help=_('eid of the file entity to append to'))
    form_buttons = [formwidgets.SubmitButton()]

    def get_action(self):
        return self._cw.build_url('narval-file-append')

class FileAppendFormView(view.StartupView):
    '''
    useful for debugging, call with ?vid=narval-file-append
    '''
    __regid__ = 'narval-file-append'

    def call(self, **kwargs):
        form = self._cw.vreg['forms'].select('narval-file-append', self._cw)
        form.render(w=self.w)

class FileAppendController(controller.Controller):
    __regid__ = 'narval-file-append'

    def publish(self, rset=None):
        '''
        append to the file corresponding to the eid
        '''
        self._cw.ajax_request = True
        form = self._cw.vreg['forms'].select('narval-file-append', self._cw)
        posted = form.process_posted()
        if rset is None:
            rset = self.process_rql()
        assert len(rset) == 1
        entity = rset.get_entity(0, 0)
        log_file = self._cw.entity_from_eid(int(posted['eid']))
        with NamedTemporaryFile() as tmpfile:
            if log_file.data:
                log_file.data.to_file(tmpfile)
            while 1:
                if not posted['data']: # empty file
                    break
                buf = posted['data'].read(4096)
                if not buf:
                    break
                tmpfile.write(buf)
            tmpfile.flush()
            log_file.cw_set(data=Binary.from_file(tmpfile.name))
        raise Redirect(entity.absolute_url(vid='ejsonexport'))

