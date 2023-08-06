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
"""cubicweb-narval schema"""

_ = unicode

from logilab.common.tasksqueue import MEDIUM, PRIORITY
from yams.buildobjs import (DEFAULT_ATTRPERMS, EntityType, RelationDefinition,
                            String, Datetime, Int)
from cubicweb.schema import PUB_SYSTEM_ENTITY_PERMS, make_workflowable
from cubes.file.schema import File

IMMUTABLE_ATTR_PERMS = DEFAULT_ATTRPERMS.copy()
IMMUTABLE_ATTR_PERMS['update'] = ()

class Recipe(EntityType):
    __permissions__ = PUB_SYSTEM_ENTITY_PERMS
    name = String(maxsize=256, unique=True, required=True,
                  description=_("the recipe's name"))
    script = String(description=_("the recipe's script to execute"),
                    required=True)

class granted_permission(RelationDefinition):
    subject = 'Recipe'
    object = 'CWPermission'

class require_permission(RelationDefinition):
    subject = 'Recipe'
    object = 'CWPermission'


class Plan(EntityType):
     # add permissions actually checked according to recipe
    __permissions__ = {'read': ('managers', 'users', 'guests', 'narval'),
        'add': ('managers', 'users', 'narval'),
        'update': ('narval',),
        'delete': ('managers',),
        }

    priority = Int(default=MEDIUM,
                   vocabulary=PRIORITY.values(),
                   __permissions__=IMMUTABLE_ATTR_PERMS)
    options = String(description=_('plan option: key=value, one per line'),
                     __permissions__=IMMUTABLE_ATTR_PERMS)
    script = String(description=_('executed script'), required=True)

make_workflowable(Plan, in_state_descr=_('execution status'))

class execution_log(RelationDefinition):
    __permissions__ = {
        'read':   ('managers', 'users', 'guests', 'narval'),
        'add':    ('managers', 'narval',),
        'delete': ('managers',),
        }
    subject = 'Plan'
    object = 'File'
    cardinality = '??'
    composite = 'subject'
    inlined = True


class execution_of(RelationDefinition):
    # add permissions actually checked according to recipe
    __permissions__ = {'read': ('managers', 'users', 'guests', 'narval'),
                       'add': ('managers', 'users', 'narval'),
                       'delete': ('managers',),
                       }
    subject = 'Plan'
    object = 'Recipe'
    inlined = True
    cardinality = '1*'
    composite = 'object'

# add permissions to File objects
File.__permissions__ = File.__permissions__.copy()
for perm_type in ['read', 'add', 'update']:
    File.__permissions__[perm_type] += ('narval',)
