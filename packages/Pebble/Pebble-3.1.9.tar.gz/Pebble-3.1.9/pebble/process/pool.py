# This file is part of Pebble.

# Pebble is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# Pebble is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with Pebble.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys

from itertools import count
from time import sleep, time
from signal import SIG_IGN, SIGINT, signal
from traceback import format_exc
from contextlib import contextmanager
from multiprocessing import Pipe, RLock
try:  # Python 2
    from Queue import Empty
    from cPickle import PicklingError
except:  # Python 3
    from queue import Empty
    from pickle import PicklingError

from pebble import thread
from pebble.task import Task
from pebble.process.utils import stop
from pebble.process.decorators import spawn
from pebble.utils import BasePool, PoolContext
from pebble.utils import STOPPED, RUNNING, ERROR
from pebble.exceptions import TimeoutError, TaskCancelled


ACK = 0  # task aknowledged by worker
RES = 1  # task results from worker


def get_task(channel, pid):
    """Gets new task for Pool Worker.

    Waits for next task to be ready, atomically unpacks its contents
    and sends back acknowledgment to the Pool.

    """
    function = None

    while function is None:
        try:
            channel.poll()
            with lock(channel):
                number, function, args, kwargs = channel.recv(0)
                channel.send((ACK, number, pid))
        except TimeoutError:  # race condition between workers
            continue
        except (OSError, IOError):
            sys.exit(0)

    return number, function, args, kwargs


def task_state(task, pool, timestamp):
    """Inspects the task state.

    Checks for tasks timing out, cancelled or fetched
    by an accidentally stopped worker.

    """
    error = False
    results = None

    if (task.timeout > 0 and timestamp - task._timestamp > task.timeout):
        error = True
        results = TimeoutError('Task timeout')
    elif task.cancelled:
        error = True
        results = TaskCancelled('Task cancelled')
    else:
        try:
            if not pool[task._pid].is_alive():
                error = True
        except KeyError:
            error = True

    return error, results


@spawn(name='pool_worker', daemon=True)
def pool_worker(channel, initializer, initargs, limit):
    """Runs the actual function in separate process."""
    error = None
    value = None
    counter = count()
    pid = os.getpid()
    signal(SIGINT, SIG_IGN)

    if initializer is not None:
        try:
            initializer(*initargs)
        except Exception as err:
            error = err
            error.traceback = format_exc()

    while limit == 0 or next(counter) < limit:
        number, function, args, kwargs = get_task(channel, pid)

        try:
            value = function(*args, **kwargs)
        except Exception as err:
            if error is None:
                error = err
                error.traceback = format_exc()

        try:
            channel.send((RES, number, error is not None and error or value))
        except PicklingError as error:
            channel.send((RES, number, error))

        error = None
        value = None

    sys.exit(0)


@thread.spawn(name='task_scheduler', daemon=True)
def task_scheduler(context):
    """Schedules enqueued tasks to the workers."""
    queue = context.queue
    tasks = context.tasks
    put = lambda o: context.pool_channel.send(o)

    while context.state not in (ERROR, STOPPED):
        try:
            task = queue.get(0.6)
        except Empty:
            continue

        if task is not None:
            function = task._metadata['function']
            args = task._metadata['args']
            kwargs = task._metadata['kwargs']
            tasks[task.number] = task

            put((task.number, function, args, kwargs))
        else:  # stop sentinel
            return


@thread.spawn(name='task_manager', daemon=True)
def task_manager(context):
    """Manages running tasks.

    If a task's timeout expired it stops its worker and set it.
    If a task is cancelled it stops its worker and set it.
    If an expired worker has accidentally fetched a task it re-enqueues
    it in the Pool's queue.

    """
    pool = context.pool
    queue = context.queue
    tasks = context.tasks

    while context.state not in (ERROR, STOPPED):
        timestamp = time()
        running = [t for t in list(tasks.values())
                   if t.started and not t.ready]

        for task in running:
            error, results = task_state(task, pool, timestamp)

            if error:
                try:
                    del tasks[task.number]

                    if results is not None:  # timeout or cancelled
                        context.task_done(task, results)

                        with lock(context.worker_channel):
                            stop(pool[task._pid])
                    else:  # race condition between pool and worker
                        task._timestamp = task._pid = 0
                        queue.put(task)
                        queue.task_done()
                except KeyError:  # task completed or worker already expired
                    continue

        sleep(0.2)


@thread.spawn(name='message_manager', daemon=True)
def message_manager(context):
    """Gather messages from workers,
    sets tasks status and runs callbacks.

    """
    tasks = context.tasks
    get = lambda t: context.pool_channel.recv(timeout=t)

    while context.state not in (ERROR, STOPPED):
        try:
            message, number, data = get(0.6)

            if message is ACK:
                task = tasks[number]
                task._pid = data
                task._timestamp = time()
            elif message is RES:
                task = tasks.pop(number)
                context.task_done(task, data)
        except (TimeoutError, KeyError):
            continue  # nothing on channel or task cancelled
        except TypeError:  # stop sentinel
            return


@thread.spawn(name='worker_manager', daemon=True)
def worker_manager(context):
    """Collects expired workers and spawns new ones."""
    pool = context.pool
    limit = context.worker_limit
    initializer = context.initializer
    initargs = context.initargs
    workers = context.worker_number
    channel = context.worker_channel

    while context.state not in (ERROR, STOPPED):
        expired = [w for w in pool.values() if not w.is_alive()]

        for worker in expired:
            worker.join()
            del pool[worker.pid]

        for _ in range(workers - len(pool)):
            worker = pool_worker(channel, initializer, initargs, limit)
            pool[worker.pid] = worker

        sleep(0.2)


class PoolTask(Task):
    """Extends the *Task* object to support *process* decorator."""
    def cancel(self):
        """Overrides the *Task* cancel method."""
        self._cancelled = True


class Context(PoolContext):
    """Pool's Context."""
    def __init__(self, queue, queueargs, initializer, initargs,
                 workers, limit):
        super(Context, self).__init__(queue, queueargs,
                                      initializer, initargs,
                                      workers, limit)
        self.pool_channel, self.worker_channel = channels()

    def stop(self):
        """Stop the workers."""
        for worker in self.pool.values():
            stop(worker)


class Pool(BasePool):
    """A ProcessPool allows to schedule jobs into a Pool of Processes
    which will perform them concurrently.

    workers is an integer representing the amount of desired process workers
    managed by the pool.
    If worker_task_limit is a number greater than zero,
    each worker will be restarted after performing an equal amount of tasks.
    initializer must be callable, if passed, it will be called
    every time a worker is started, receiving initargs as arguments.
    queue represents a Class which, if passed, will be constructed
    with queueargs as parameters and used internally as a task queue.
    The queue object resulting from its construction must expose
    same functionalities of Python standard Queue object,
    especially for what concerns the put(), get() and join() methods.

    """
    def __init__(self, workers=1, task_limit=0, queue=None, queueargs=None,
                 initializer=None, initargs=()):
        super(Pool, self).__init__()
        self._context = Context(queue, queueargs, initializer, initargs,
                                workers, task_limit)

    def _start(self):
        """Start the Pool managers."""
        self._managers = (task_scheduler(self._context),
                          task_manager(self._context),
                          message_manager(self._context),
                          worker_manager(self._context))
        self._context.state = RUNNING

    def stop(self):
        """Stops the pool without performing any pending task."""
        self._context.state = STOPPED

        self._context.queue.put(None)  # task_scheduler stop sentinel
        self._context.worker_channel.send(None)  # task_manager stop sentinel

        for manager in self._managers:
            manager.join()

        self._context.stop()

    def kill(self):
        """Kills the pool forcing all workers to terminate immediately."""
        self._context.state = STOPPED

        self._context.stop()

    def schedule(self, function, args=(), kwargs={}, identifier=None,
                 callback=None, timeout=0):
        """Schedules *function* into the Pool, passing *args* and *kwargs*
        respectively as arguments and keyword arguments.

        If *callback* is a callable it will be executed once the function
        execution has completed with the returned *Task* as a parameter.

        *timeout* is an integer, if expires the task will be terminated
        and *Task.get()* will raise *TimeoutError*.

        The *identifier* value will be forwarded to the *Task.id* attribute.

        A *Task* object is returned.

        """
        metadata = {'function': function, 'args': args, 'kwargs':  kwargs}
        task = PoolTask(next(self._counter),
                        callback=callback, timeout=timeout,
                        identifier=identifier, metadata=metadata)

        self._schedule(task)

        return task


# --------------------------------------------------------------------------- #
#                              Pool's Related                                 #
# --------------------------------------------------------------------------- #
def channels():
    """Process Pool channel factory."""
    read0, write0 = Pipe()
    read1, write1 = Pipe()

    return PoolChannel(read1, write0), WorkerChannel(read0, write1)


@contextmanager
def lock(channel):
    channel.rlock.acquire()
    if channel.wlock is not None:
        channel.wlock.acquire()
    try:
        yield channel
    finally:
        channel.rlock.release()
        if channel.wlock is not None:
            channel.wlock.release()


class PoolChannel(object):
    """Pool's side of the channel."""
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    def poll(self, timeout=None):
        return self.reader.poll(timeout)

    def recv(self, timeout=None):
        if self.reader.poll(timeout):
            return self.reader.recv()
        else:
            raise TimeoutError("Channel timeout")

    def send(self, obj):
        return self.writer.send(obj)


class WorkerChannel(PoolChannel):
    """Worker's side of the channel."""
    def __init__(self, reader, writer):
        super(WorkerChannel, self).__init__(reader, writer)
        self.rlock = RLock()
        self.wlock = os.name != 'nt' and RLock() or None
        self.recv = self._make_recv_method()
        self.send = self._make_send_method()

    def __getstate__(self):
        return (self.reader, self.writer,
                self.rlock, self.wlock)

    def __setstate__(self, state):
        (self.reader, self.writer,
         self.rlock, self.wlock) = state

        self.recv = self._make_recv_method()
        self.send = self._make_send_method()

    def _make_recv_method(self):
        def recv(timeout=None):
            with self.rlock:
                if self.reader.poll(timeout):
                    return self.reader.recv()
                else:
                    raise TimeoutError("Channel timeout")

        return recv

    def _make_send_method(self):
        def send(obj):
            if self.wlock is not None:
                with self.wlock:
                    return self.writer.send(obj)
            else:
                return self.writer.send(obj)

        return send
