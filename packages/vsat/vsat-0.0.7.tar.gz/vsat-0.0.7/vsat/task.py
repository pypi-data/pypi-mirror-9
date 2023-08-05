
# Disable a couple of Lint warnings here because we need to do a bit of
# magic
# pylint: disable=C0111
# pylint: disable=W0142


import time
import uuid
import json

from os import remove
from os.path import join, exists

from vsat.worker import WorkerPool


# Will be used to store tasks as they are registered.
TASK_REGISTRY = {}

RESULT_LOCATION = "/tmp/"


class NotReady(Exception):
    """
    Raised if a result it not ready yet.
    """


class InvalidTask(Exception):
    """
    Raised if a there us no current task for a particular uuid.
    """


class AsyncResult(object):
    """
    Contains the promise of a result from Task once it is executed.
    """
    task_name = ""
    task_uuid = ""
    state = ""
    result = ""
    task_uuid = ""
    args = []
    kwargs = {}

    @classmethod
    def create(cls, task_name, args, kwargs):
        """
        Creates a new result
        """
        result = cls()
        result.task_uuid = str(uuid.uuid4())
        result.state = "CREATED"
        result.task_name = task_name
        result.args = args
        result.kwargs = kwargs

        result.save_state("task_name", result.task_name)
        result.save_state("args", result.args)
        result.save_state("kwargs", result.kwargs)
        result.save_state("task_uuid", result.task_uuid)
        result.save_state("state", result.state)
        result.save_state("result", None)

        return result

    @classmethod
    def get(cls, task_uuid):
        """
        Gets an existing result
        """
        result = cls()
        result.task_uuid = task_uuid

        if not exists(result.path):
            raise InvalidTask()

        result.task_name = result.load_state()["task_name"]
        result.args = result.load_state()["args"]
        result.kwargs = result.load_state()["kwargs"]
        result.state = result.load_state()["state"]
        result.result = result.load_state()["result"]

        return result

    @property
    def path(self):
        """
        Returns the path for this results state.
        """
        return join(RESULT_LOCATION, str(self.task_uuid))

    def load_state(self):
        """
        Returns a dictionary containing this results state.
        """
        state = {}

        if exists(self.path):
            with open(self.path, "r") as state_file:
                state_file_contents = state_file.read()
                state = json.loads(state_file_contents)
    
        return state

    def save_state(self, key, value):
        """
        Persists an attributes value
        """
        state = self.load_state()
        state[key] = value

        with open(self.path, "w+") as state_file:
            state_file.write(json.dumps(state))

    def set_state(self, state):
        """
        Sets the state of the remote task.
        """
        self.save_state("state", state)

    def set_result(self, result):
        """
        Sets the result of the remote task.
        """
        self.save_state("result", result)
        self.save_state("state", "FINISHED")

    def set_error(self, error):
        """
        Sets the error that the remote task raised.
        """
        self.save_state("result", error)
        self.save_state("state", "ERROR")

    def get_result(self, block=False):
        """
        Attempts to get the result, an exception is raises if it is not
        ready.
        """
        if block:
            while self.get_state() != "FINISHED":
                time.sleep(0.25)

        if self.load_state()['state'] != "FINISHED":
            raise NotReady()

        state = self.load_state()
        remove(self.path)

        return state['result']

    def get_state(self):
        """
        Returns the state of the task.
        """
        return self.load_state()['state']

    def to_json(self):
        """
        Returns this result as JSON
        """
        return json.dumps(self.load_state())

    def get_task(self):
        """
        Returns the Task object associated with this result.
        """
        return TASK_REGISTRY[self.task_name]

WorkerPool.set_result_class(AsyncResult)


class Task(object):
    """
    A task that can be called asynchronously.
    """
    run = {"func": lambda: None}
    name = "base_task"

    @classmethod
    def get(cls, task_name):
        """
        Returns a Task object that maybe called by a worker.
        """
        return TASK_REGISTRY[task_name]

    def apply(self, *args, **kwargs):
        """
        Applies the task locally.
        """
        return self.run['func'](*args, **kwargs)

    def apply_async(self, *args, **kwargs):
        """
        Applies the task remotely and returns an AsyncResult object.
        """
        worker_pool = WorkerPool.get()
        result = AsyncResult.create(self.name, args, kwargs)
        worker_pool.schedule_task(result)
        return result

    def __call__(self, *args, **kwargs):
        """
        Leaves the task callable as a normal function.
        """
        return self.apply(*args, **kwargs)

    @classmethod
    def func_to_name(cls, func):
        """
        Returns a standard name for a task function.
        """
        return ".".join([func.__module__, func.__name__])


def task(*args, **options):
    """Creates new task class from any callable."""

    def inner_create_task_cls(**options):

        def _create_task_cls(func):

            return task_from_func(func, **options)

        return _create_task_cls

    if len(args) == 1:
        if callable(args[0]):
            return inner_create_task_cls(**options)(*args)
        raise TypeError('argument 1 to @task() must be a callable')
    if args:
        raise TypeError(
            '@task() takes exactly 1 argument ({0} given)'.format(
                sum([len(args), len(options)])))

    return inner_create_task_cls(**options)


def task_from_func(func, **options):
    """
    Creates a Callable class from any Callable.
    """
    name = Task.func_to_name(func)

    if name not in TASK_REGISTRY:
        _task = type(func.__name__, (Task, ), dict({
            'name': name,
            'run': {'func': func},
            '__doc__': func.__doc__,
            '__module__': func.__module__}, **options))()
        TASK_REGISTRY[name] = _task

    else:
        _task = TASK_REGISTRY[name]

    return _task
