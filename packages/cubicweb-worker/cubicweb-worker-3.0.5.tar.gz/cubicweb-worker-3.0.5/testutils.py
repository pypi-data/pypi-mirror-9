# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-worker test utilities"""


def _process_task(session, task, trname):
    session.set_cnxset()
    print 'do', task.operation, trname
    task._cw = session
    task.cw_adapt_to('IWorkflowable').fire_transition(trname)
    session.commit()
    session.set_cnxset()

def run_all_tasks(session):
    """Emulate a worker, processing synchronously all pending tasks
    (by creation order)

    """
    tasks = []
    perfreg = session.vreg['worker.performer']
    tasksrset = session.execute('Any T,D ORDERBY D WHERE T is CWWorkerTask, T creation_date D')
    for task in tasksrset.entities():
        tasks.append(task)
        _process_task(session, task, 'task_acquire')
        performer = perfreg.select(task.operation, session, entity=task)
        try:
            performer.perform_task(session, task)
        except Exception, exc:
            import traceback as tb; tb.print_exc()
            _process_task(session, task, 'task_fail')
        else:
            _process_task(session, task, 'task_complete')
    return tasks
