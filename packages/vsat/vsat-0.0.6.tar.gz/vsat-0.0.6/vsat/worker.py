"""
Contains the task worker that executes queued tasks.
"""
import logging
import json

from multiprocessing import Process, Queue

LOG = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


class PoolNotInitialised(Exception):
    """
    Raised when the worker pool has not been created yet.
    """


class WorkerPool(object):
    """
    Looks after the pool of workers.
    """
    WORKER_POOL = None
    RESULT_CLASS = None

    @classmethod
    def _process(cls, queue):
        """
        Executes the tasks for a worker.
        """
        finished = False

        while not finished:

            item = queue.get()

            if item == "stop":
                finished = True

            else:
                result = cls.RESULT_CLASS.get(json.loads(item)['task_uuid'])

                result.set_state("RUNNING")

                ret_value = result.get_task()(*result.args, **result.kwargs)

                result.set_result(ret_value)

    def __init__(self, num_workers=1):
        """
        Creates a WorkerPool.
        """
        self.queue = Queue()
        self.workers = []

        for _ in xrange(num_workers):
            self.workers.append(Process(target=WorkerPool._process,
                                        args=(self.queue, )))

    @classmethod
    def init(cls, num_workers=1):
        """
        Starts THE worker pool.
        """
        cls.WORKER_POOL = cls(num_workers=num_workers)
        return cls.WORKER_POOL

    @classmethod
    def set_result_class(cls, result_class):
        """
        Links AsyncResult
        """
        cls.RESULT_CLASS = result_class

    @classmethod
    def get(cls):
        """
        Returns a handle to THE worker pool.
        """
        if cls.WORKER_POOL is None:
            raise PoolNotInitialised()

        return cls.WORKER_POOL

    def start(self):
        """
        Starts this worker pool.
        """
        for worker in self.workers:
            worker.start()

    def stop(self, timeout=DEFAULT_TIMEOUT):
        """
        Shuts down all workers.
        """
        LOG.info("Shutting down %d workers.", len(self.workers))
        for worker in self.workers:
            # Inform each worker to stop and then wait for them
            self.queue.put("stop")

        for worker in self.workers:
            worker.join(timeout=timeout)

        WorkerPool.WORKER_POOL = None

    def schedule_task(self, result):
        """
        Queues a Task to be executed by a Worker.
        """
        self.queue.put(result.to_json())
