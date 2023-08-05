# copyright 2011-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-worker schema"""
from yams.buildobjs import EntityType, String, Int, SubjectRelation, Boolean, Datetime
from cubicweb.schema import  WorkflowableEntityType

_ = unicode

class CWWorker(EntityType):
    """A worker CW instance. Each worker registers by creating such an
    entity at startup and deleting it at exit
    """
    __permissions__ = {'read': ('users', 'managers'),
                       'add': ('managers',),
                       'update': ('managers',),
                       'delete': ('managers',),
                       }
    last_ping = Datetime(required=True,
                         description='date of the last ping sent by the Worker')


class CWWorkerTask(WorkflowableEntityType):
    __permissions__ = {'read': ('users', 'managers'),
                       'add': ('managers', 'users'),
                       'update': ('managers', 'users'),
                       'delete': ('managers', 'users'),
                       }
    operation = String(
        description="""'name' of the operation to be performed:

        The "do_<operation>" method will be called to perform the task""",
        required=True)
    done_by = SubjectRelation('CWWorker',
        description="""Worker instance which acquired the task""",
        cardinality='?*',
        inlined=True,
        __permissions__={'read': ('users', 'managers'),
                         'add': ('managers', 'users'),
                         'delete': ('managers', 'users')})

