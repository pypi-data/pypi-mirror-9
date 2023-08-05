# copyright 2011-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-worker specific hooks and operations"""

from warnings import warn

from logilab.common.registry import ObjectNotFound

from cubicweb import ValidationError
from cubicweb.predicates import is_instance
from cubicweb.server.hook import Hook

from cubes.worker.workutils import (make_worker, worker_ping,
                                    worker_remove_stale_workers,
                                    worker_remove_old_tasks,
                                    worker_pending_tasks)


MYWORKERS = set()

class StartupInitWorker(Hook):
    __regid__ = 'worker.worker_registration_hook'
    events = ('server_startup',)
    ping_period = 60

    def __call__(self):
        repo = self.repo
        worker_remove_stale_workers(repo, self.ping_period + 1)
        polling_period = max(1, repo.config.get('worker-polling-period', 0))
        worker = None
        if repo.config['long-transaction-worker']:
            with repo.internal_session(safe=True) as session:
                worker = make_worker(session, repo)
                session.commit()
                MYWORKERS.add(worker.eid)
                # the eid_dict is shared by the worker_ping and
                # worker_pending_tasks looping tasks only worker_ping
                # may modify it in case the ping detects the worker
                # has been deleted and creates a new one
                eid_dict = {'eid': worker.eid}
                repo.looping_task(self.ping_period, worker_ping, repo, eid_dict)
                self.warning('starting worker looping tasks')
                repo.looping_task(polling_period, worker_pending_tasks, repo, eid_dict)
                repo.looping_task(45 * self.ping_period, worker_remove_old_tasks, repo)
                repo.looping_task(1 + self.ping_period // 2, worker_remove_stale_workers,
                                  repo, 2 * self.ping_period)
        return worker


class ShutdownWorker(Hook):
    __regid__ = 'worker.worker_unregister_hook'
    events = ('before_server_shutdown',)

    def __call__(self):
        repo = self.repo
        if repo.config['long-transaction-worker']:
            with repo.internal_session(safe=True) as session:
                for eid in MYWORKERS:
                    session.execute('DELETE CWWorker W WHERE W eid %(eid)s',
                                    {'eid': eid})
                    self.warning('removed worker %s', eid)
                    session.commit()


def operation(klass, uopname):
    try:
        opname = 'do_%s' % uopname.encode('ascii')
    except:
        warn('Bad operation name %r' % uopname)
        return
    return getattr(klass, opname, None)


class TaskPerformerOpcheck(Hook):
    __regid__ = 'worker.check_operation'
    events = ('after_add_entity',)
    __select__ = Hook.__select__ & is_instance('CWWorkerTask')

    def __call__(self):
        task = self.entity
        try:
            performer = self._cw.vreg['worker.performer'].select(task.operation,
                                                                 self._cw, task)
        except ObjectNotFound:
            # try bw compat. 1
            adapter = task.cw_adapt_to(task.operation)
            if adapter:
                return
            # bw compat. 2
            workerclass = self._cw.vreg['etypes'].etype_class('CWWorker')
            if operation(workerclass, task.operation):
                return
            msg = self._cw._('The operation name must match a Task '
                             'adapter of the same regid')
            raise ValidationError(task, {'operation': msg})
