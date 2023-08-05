_ = unicode

def define_worker_task_workflow(add_workflow):
    wf = add_workflow('worker_task', 'CWWorkerTask', default=True)
    # states = pending, assigned, done
    pending = wf.add_state(_('task_pending'), initial=True)
    assigned = wf.add_state(_('task_assigned'))
    failed = wf.add_state(_('task_failed'))
    done = wf.add_state(_('task_done'))
    wf.add_transition(_('task_acquire'), (pending,), assigned)
    wf.add_transition(_('task_release'), (assigned, failed), pending)
    wf.add_transition(_('task_complete'), (assigned,), done)
    wf.add_transition(_('task_fail'), (assigned,), failed)
