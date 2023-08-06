from cubicweb.view import EntityView, NOINDEX, NOFOLLOW
from cubicweb.predicates import is_instance, has_related_entities
from cubicweb.web.views import uicfg
from cubes.narval.logformat import log_to_html

def no_robot_index(self):
    return [NOINDEX, NOFOLLOW]

class FormatedLogView(EntityView):
    __select__ = EntityView.__select__ & is_instance('File')
    __regid__ = 'narval.formated_log'

    def cell_call(self, row, col, loglevel='Info', **kwargs):
        if 'dispctrl' in self.cw_extra_kwargs:
            loglevel = self.cw_extra_kwargs['dispctrl'].get('loglevel', loglevel)
        entity = self.cw_rset.get_entity(row, col)

        if entity.data:
            log_to_html(self._cw, unicode(entity.eid),
                        entity.data.read().decode(entity.data_encoding),
                        self.w, defaultlevel=loglevel)
        else:
            self.w(self._cw._('no log to display'))

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('*', 'execution_of', 'Recipe'), False)
