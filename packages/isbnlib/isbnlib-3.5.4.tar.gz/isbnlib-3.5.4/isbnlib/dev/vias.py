# -*- coding: utf-8 -*-

from .. import config


def serial(named_tasks, arg):
    """Serial calls."""
    RESULTS = {}
    for name, task in named_tasks:
        try:
            RESULTS[name] = task(arg)
        except:    # pragma: no cover
            RESULTS[name] = None
            continue
    return RESULTS


def parallel(named_tasks, arg):
    """Threaded calls."""
    from threading import Thread
    RESULTS = {}

    def _worker(name, task, arg):
        try:
            RESULTS[name] = task(arg)
        except:    # pragma: no cover
            pass

    for name, task in named_tasks:
        t = Thread(target=_worker, args=(name, task, arg))
        t.start()
        t.join(config.THREADS_TIMEOUT)
    return RESULTS


def multi(named_tasks, arg):
    """Multiprocessing: using several cores (if available)."""
    from multiprocessing import Process, Queue
    RESULTS = {}
    q = Queue()

    def _worker(name, task, arg, q):
        q.put((name, task(arg)))    # pragma: no cover

    for name, task in named_tasks:
        p = Process(target=_worker, args=(name, task, arg, q))
        p.start()
        p.join(config.THREADS_TIMEOUT)
    q.put('STOP')

    while True:
        el = q.get()
        if el == 'STOP':
            break
        RESULTS[el[0]] = el[1]
    return RESULTS
