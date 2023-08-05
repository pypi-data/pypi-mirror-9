# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-worker automatic tests"""
from cubicweb import ValidationError

from cubicweb.devtools import testlib
from cubes.worker.workutils import worker_pending_tasks
from cubes.worker.testutils import run_all_tasks

import threading

class DefaultTC(testlib.CubicWebTC):


    def setUp(self):
        super(DefaultTC, self).setUp()
        self.repo.cv = threading.Condition()
        self.repo._type_source_cache.clear()
        self.repo._extid_cache.clear()


    def tearDown(self):
        # We have to copy the list. because when a thread ens it remove itself
        # from the list altering the iteration
        for thread in list(self.repo._running_threads):
            thread.join()
        super(DefaultTC, self).tearDown()

    def test_bogus_operation(self):
        with self.assertRaises(ValidationError):
            self.session.create_entity('CWWorkerTask', operation=u'bogop')

    def test_work_is_done(self):
        cv = self.repo.cv
        with cv:
            task_orig = self.session.create_entity('CWWorkerTask',
                                                   operation=u'test_operation',
                                                   test_val=0)
            self.session.commit()
            worker = self.session.execute('Any CWW WHERE CWW is CWWorker'
                                          ).get_entity(0,0)
            worker_pending_tasks(self.repo, {'eid': worker.eid})
            cv.wait(5)
            task = self.session.execute('Any CWWT WHERE CWWT eid %d' % task_orig.eid).get_entity(0,0)

        state = task.cw_adapt_to('IWorkflowable').state
        self.assertNotEqual('task_pending', state)
        self.assertEqual(task.test_val, task_orig.test_val + 1)

    def test_task_are_acquired(self):
        task1 = self.session.create_entity('CWWorkerTask',
                                           operation=u'no_op',
                                           test_val=0)
        task2 = self.session.create_entity('CWWorkerTask',
                                           operation=u'no_op',
                                           test_val=0)
        self.session.commit(free_cnxset=False)
        worker = self.session.execute('Any CWW WHERE CWW is CWWorker'
                                      ).get_entity(0,0)
        self.session.commit(free_cnxset=False)
        worker_pending_tasks(self.repo, {'eid': worker.eid})
        self.assertEqual(2, len(worker.reverse_done_by))

    def test_testutils(self):
        task1 = self.session.create_entity('CWWorkerTask',
                                           operation=u'test_operation',
                                           test_val=0)
        task2 = self.session.create_entity('CWWorkerTask',
                                           operation=u'test_operation',
                                           test_val=0)
        self.commit()
        tasks = run_all_tasks(self.session)
        self.commit()
        self.assertEqual(2, len(tasks))
        self.assertEqual([[1], [1]],
                         self.session.execute('Any V WHERE T is CWWorkerTask, T test_val V').rows)

    def test_load(self):
        task1 = self.session.create_entity('CWWorkerTask',
                                           operation=u'no_op',
                                           test_val=0)
        task2 = self.session.create_entity('CWWorkerTask',
                                           operation=u'no_op',
                                           test_val=0)
        self.session.commit(free_cnxset=False)
        worker = self.session.execute('Any CWW WHERE CWW is CWWorker'
                                      ).get_entity(0,0)

        self.assertEqual(0, worker.get_load())

        worker.acquire_task(task1)
        self.session.commit(free_cnxset=False)
        self.assertEqual(1, worker.get_load())

        worker.acquire_task(task2)
        self.session.commit(free_cnxset=False)
        self.assertEqual(2, worker.get_load())

        worker.commit_transition(task2, 'task_complete', 'success')
        self.session.commit(free_cnxset=False)
        self.assertEqual(1, worker.get_load())

        worker.commit_transition(task1, 'task_complete', 'success')
        self.session.commit(free_cnxset=False)
        self.assertEqual(0, worker.get_load())

    def test_failure(self):
        cv = self.repo.cv
        with cv:
            task_orig = self.session.create_entity('CWWorkerTask',
                                                   operation=u'fail_validation',
                                                   test_val=0)
            self.session.commit()
            worker = self.session.execute('Any CWW WHERE CWW is CWWorker'
                                          ).get_entity(0,0)
            worker_pending_tasks(self.repo, {'eid': worker.eid})
            cv.wait(5)
            self.session.commit()
        task = self.session.execute('Any CWWT WHERE CWWT eid %d' % task_orig.eid).get_entity(0,0)
        task.cw_clear_all_caches()
        wfable = task.cw_adapt_to('IWorkflowable')
        self.assertEqual('task_failed', wfable.state)
        comment = wfable.latest_trinfo().comment
        self.assertEqual('error during validation', comment)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
