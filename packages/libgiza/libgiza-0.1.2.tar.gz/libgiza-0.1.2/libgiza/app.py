# Copyright 2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
:mod:`app` holds the :class:`~giza.app.BuildApp()` class that provides an
organizing framework for running larger sequences of operations.
"""

import contextlib
import logging
import random
import numbers

logger = logging.getLogger('libgiza.app')

from libgiza.pool import ThreadPool, ProcessPool, SerialPool, WorkerPool, EventPool
from libgiza.task import Task, MapTask
from libgiza.config import ConfigurationBase

class BuildApp(object):
    """
    A unit of work. :class:`~giza.app.BuildApp()` instances possess queues of
    :class:`~giza.task.Task()` objects and sub-\ :class:`~giza.app.BuildApp()`
    objects that describe a build process. Groups of :class:`~giza.task.Task()`
    objects may execute in parallel, while any :class:`~giza.app.BuildApp()`
    objects in the queue execute in isolation after proceeding group of
    :class:`~giza.task.Task()` operations complete. Mix
    :class:`~giza.app.BuildApp()` and :class:`~giza.task.Task()` operations to
    control task ordering.

    The results of all operations are accessible in the
    :attr:`~giza.app.BuildApp.results`, which largely preserves the ordering of the
    insertion of operations into the queue. Unlike the queue,
    :attr:`~giza.app.BuildApp.results` contains the result of each operation in
    an embedded :class:`~giza.app.BuildApp()` in the order that each task was
    added to the embedded :class:`~giza.app.BuildApp()` instance.

    :class:`~giza.app.BuildApp()` are reusable: after running all operations in
    the queue, the queue resets. However, results do not reset.
    """

    def __init__(self, conf=None, force=False):
        """
        :param ConfigurationBase conf: A top level
           ``Configuration`` object.
        """

        self._conf = conf
        self._force = force
        self._default_pool = None
        self._pool_size = None

        self.queue = []
        self.results = []
        self.worker_pool = None
        self.randomize = False

        self.pool_mapping = {
            'thread': ThreadPool,
            'process': ProcessPool,
            'event': EventPool,
            'serial': SerialPool
        }
        self.pool_types = tuple([ self.pool_mapping[p] for p in self.pool_mapping])

        self.needs_rebuild = True
        self.root_app = True

        self.target = None
        self.dependency = None

    @classmethod
    def new(cls, pool_type='process', pool_size=None, force=False):
        app = cls()
        app.force = force
        app.default_pool = pool_type
        app.pool_size = pool_size

        return app

    @property
    def dependency(self):
        return self._dependency

    @dependency.setter
    def dependency(self, value):
        self._dependency = value

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def force(self):
        if self._force is None:
            if self.conf is None:
                logger.warning('force flag for app is not set, setting to "false"')
                self._force = False
            else:
                logger.warning('deprecated use of conf object in app setup for force value')
                self._force = self.conf.runstate.force

        return self._force

    @force.setter
    def force(self, value):
        self._force = bool(value)

    @property
    def pool_size(self):
        if self._pool_size is None:
            if self.conf is None:
                # the pool objects themselves know what to do, and so we don't
                # need to over-define defaults here.
                return None
            else:
                logger.warning('deprecated use of conf object for setting pool size')
                self.pool_size = self.conf.runstate.pool_size

        return self._pool_size

    @pool_size.setter
    def pool_size(self, value):
        if isinstance(value, numbers.Number):
            self._pool_size = value
        else:
            logger.warning('{0} is an invalid pool size'.format(str(value)))

    @property
    def conf(self):
        return self._conf

    @conf.setter
    def conf(self, value):
        if isinstance(value, ConfigurationBase):
            self._conf = value

    @property
    def default_pool(self):
        if self._default_pool is None:
            if self.conf is None:
                logger.warning('pool type not specified, choosing at random')
                return random.choice(self.pool_mapping.keys())
            else:
                logger.warning('deprecated use of conf object in app setup for pool type')
                self._default_pool = self.conf.runstate.runner
                return self._default_pool
        else:
            return self._default_pool

    @default_pool.setter
    def default_pool(self, value):
        if value in self.pool_mapping:
            self._default_pool = value
        else:
            logger.error('{0} is not a valid pool type'.format(value))

    def define_dependency_node(self, target, dependency):
        self.target = target
        self.dependency = dependency

    def reset(self):
        self.randomize = False
        self.queue = []
        self.results = []

    @property
    def pool(self):
        if self.worker_pool is None:
            self.create_pool()

        return self.worker_pool

    @pool.setter
    def pool(self, value=None):
        self.create_pool(value)

    def create_pool(self, pool=None):
        if pool is None:
            if self.worker_pool is None:
                pool = self.default_pool
            else:
                pool = self.worker_pool

        if self.worker_pool is not None:
            logger.debug('not creating a pool because one already exists. ({0}, {1})'.format(pool, type(pool)))
            return

        if self.worker_pool is None:
            if self.is_pool(pool) and self.worker_pool is None:
                self.worker_pool = pool
            elif pool in self.pool_types:
                self.worker_pool = pool(self.pool_size)
            elif self.is_pool_type(pool) and self.worker_pool is None:
                self.worker_pool = self.pool_mapping[pool](self.pool_size)
            elif self.default_pool in self.pool_types:
                self.worker_pool = self.pool_mapping[self.default_pool](self.pool_size)
        elif self.is_pool(self.worker_pool):
            return
        elif self.conf is not None and pool in self.pool_types and isinstance(self.worker_pool, self.pool_mapping[pool]):
            self.close_pool()
            self.worker_pool = self.pool_mapping[pool](self.pool_size)
        else:
            raise TypeError("pool {0} of type {1} is invalid".format(pool, type(pool)))

    def is_pool(self, pool):
        if isinstance(pool, self.pool_types):
            return True
        else:
            return False

    def is_pool_type(self, value):
        if value in self.pool_mapping:
            return True
        else:
           return False

    @property
    def queue_has_apps(self):
        num_apps = len([ True for t in self.queue if isinstance(t, BuildApp)])

        if num_apps >= 1:
            return True
        else:
            return False

    def close_pool(self):
        if self.is_pool(self.worker_pool) and not isinstance(self.worker_pool, SerialPool):
            self.worker_pool.close()
            self.worker_pool = None

    def extend_queue(self, tasks):
        for task in tasks:
            self.add(task)

    def sub_app(self):
        app = BuildApp()
        app.force = self.force
        app.root_app = False
        app.default_pool = self.default_pool
        app.pool = self.pool

        if self.conf is not None:
            app.conf = self.conf

        return app

    def add(self, task=None, conf=None):
        """
        Adds a new :class:`~giza.app.BuildApp()` or :class:`~giza.task.Task()`
        to the :class:`~giza.app.BuildApp()` object.

        :param string,Task,BuildApp task: Optional. If not specified,
           :meth:`~giza.app.BuildApp.add()` creates and returns a new
           :class:`~giza.task.Task()` object. You can pass the string ``task``
           or the class :class:`~giza.task.Task` to explicitly create a new
           Task, or pass an existing :class:`~giza.task.Task()` instance to add
           that task to the :class:`~giza.app.BuildApp()` instance. You can also
           pass the string ``app`` or the :class:`~giza.app.BuildApp` class, to
           create and add new :class:`~giza.app.BuildApp()`: pass an existing
           :class:`~giza.app.BuildApp()`  instance to add that that operation
           grouping to the queue.

        :returns: A reference to a :class:`~giza.app.BuildApp()` or
           :class:`~giza.task.Task()` object in the :class:`~giza.app.BuildApp()`

        :raises: :exc:`TypeError` if the ``task`` argument is invalid.

        """
        if conf is not None:
            self.conf = conf

        if task is None or task in (Task, 'task'):
            t = Task()
            t.conf = self.conf
            t.force = self.force
            self.queue.append(t)
            return t
        elif task in (MapTask, 'map'):
            t = MapTask()
            t.conf = self.conf
            t.force = self.force
            self.queue.append(t)
            return t
        elif task in (BuildApp, 'app'):
            self.create_pool()
            t = self.sub_app()

            self.queue.append(t)
            return t
        else:
            if isinstance(task, Task):
                task.force = self.force
                if task.conf is None:
                    task.conf = self.conf

                self.queue.append(task)
                return task
            elif isinstance(task, BuildApp):
                self.create_pool()
                task.root_app = False
                task.defualt_pool = self.default_pool
                task.force = self.force
                task.pool = self.pool
                self.queue.append(task)
                return task
            else:
                raise TypeError('invalid task type')

    def _run_single(self, j):
        if isinstance(j, BuildApp):
            if j.pool is None:
                j.pool = self.pool

            self.results.extend(j.run())
        elif isinstance(j, Task):
            if j.needs_rebuild is True:
                if isinstance(j, MapTask):
                    self.results.extend(self.pool.runner([j]))
                else:
                    self.results.append(j.run())
        else:
            raise TypeError

    def _run_mixed_queue(self):
        group = [ ]

        for task in self.queue:
            if not isinstance(task, BuildApp):
                group.append(task)
            else:
                if len(group) == 1:
                    j = group[0]
                    if isinstance(j, MapTask):
                        self.results.extend(self.pool.runner([j]))
                    else:
                        self.results.append(j.run())
                        group = []
                elif len(group) > 1:
                    if self.randomize is True:
                        random.shuffle(group)

                    self.results.extend(self.pool.runner(group))
                    group = []

                if task.pool is None:
                    task.pool = self.pool

                if isinstance(task, MapTask):
                    self.results.extend(self.pool.runner([task]))
                elif isinstance(task, Task):
                    self.results.append(task.run())
                else:
                    self.results.extend(task.run())

        if len(group) != 0:
            self.results.extend(self.pool.runner(group))

    def run(self):
        "Executes all tasks in the :attr:`~giza.app.BuildApp.queue`."

        if len(self.queue) == 1:
            self._run_single(self.queue[0])
        elif self.queue_has_apps is True:
            self._run_mixed_queue()
        else:
            if self.randomize is True:
                random.shuffle(self.queue)
            self.results.extend(self.pool.runner(self.queue))

        self.queue = []
        return self.results

    @contextlib.contextmanager
    def context(self, conf=None):
        if len(self.queue) == 0:
            yield self
            self.run()
        else:
            app = self.add('app')
            yield app
            app.run()
