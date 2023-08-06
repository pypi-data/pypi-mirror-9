# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


import logging
import gevent
from uuid import uuid1
from gevent import Greenlet
from datetime import datetime
from ava.spi.errors import TaskNotRegistered, TaskAlreadyRegistered

logger = logging.getLogger(__name__)


class TaskProxy(object):
    def __init__(self, task_engine, func):
        self.task_engine = task_engine
        self.func = func
        self.key = func.__module__ + '.' + func.func_name

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def run_once(self, delayed_secs=0, args=[], kwargs={}):
        return self.task_engine.run_once(self.key, delayed_secs, args, kwargs)

    def run_periodic(self, interval,
                     start_time=None, stop_time=None,
                     args=[], kwargs={}):
        return self.task_engine.run_periodic(self.key, interval,
                                             start_time=None, stop_time=None,
                                             args=[], kwargs={})


class Schedule(Greenlet):
    def __init__(self, sched_id, task, args=[], kwargs={}):
        super(Schedule, self).__init__()
        self.id = sched_id
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.error = None

    def call(self):
        try:
            logger.debug("Before running task:")
            self.result = self.task(*self.args, **self.kwargs)
            logger.debug("Task result: %r", self.result)
            return self.result
        except Exception as ex:
            logger.error("Error in calling task: %s", self.task.key)
            self.error = ex

    def _run(self):
        raise NotImplementedError()


class OnceSchedule(Schedule):
    def __init__(self, sched_id, task, seconds=0, args=[], kwargs={}):
        super(OnceSchedule, self).__init__(sched_id, task, args, kwargs)
        self.seconds = seconds

    def _run(self):
        if self.seconds > 0:
            gevent.sleep(self.seconds)
        self.call()


class PeriodicSchedule(Schedule):
    def __init__(self, sched_id, task, interval, start_time=None,
                 stop_time=None, args=[], kwargs={}):
        super(PeriodicSchedule, self).__init__(sched_id, task, args, kwargs)
        self.interval = interval
        self.start_time = start_time
        self.stop_time = stop_time
        self.next_run = 0

    def _run(self):
        now = datetime.now()
        if self.start_time is None:
            self.start_time = now

        if now < self.start_time:
            self.next_run = self.start_time - now
            gevent.sleep(self.next_run)

        while True:
            self.call()
            now = datetime.now()
            if self.stop_time and now >= self.stop_time:
                break
            self.next_run = self.interval
            gevent.sleep(self.next_run)


class TaskEngine(object):

    def __init__(self):
        self.context = None
        self._schedules = {}
        self._tasks = {}

    def start(self, ctx):
        logger.debug("Starting task engine...")
        self.context = ctx
        self.context['taskengine'] = self

    def stop(self, ctx):
        logger.debug("Stopping task engine...")
        for sched in self._schedules.values():
            sched.kill()
        gevent.joinall(self._schedules.values())

    def register(self, func):
        task_key = func.__module__ + '.' + func.func_name
        if self._tasks.get(task_key) is not None:
            raise TaskAlreadyRegistered(task_key)

        proxy = TaskProxy(self, func)
        self._tasks[task_key] = proxy
        return proxy

    def unregister(self, task_key):
        proxy = self._tasks.get(task_key)
        if proxy is not None:
            del self._tasks[task_key]

    def get_task(self, task_key):
        return self._tasks.get(task_key)

    def run_once(self, task_key, delayed_secs, args, kwargs):
        """
        Schedules a one-time task.

        :param task_key:
        :param delayed_secs:
        :return: the schedule
        """

        task = self._tasks.get(task_key)
        if task is None:
            raise TaskNotRegistered(task_key)
        schedule_id = uuid1().hex
        schedule = OnceSchedule(schedule_id, task, delayed_secs, args, kwargs)
        self._schedules[schedule_id] = schedule
        schedule.start()
        return schedule

    def run_periodic(self, task_key, interval,
                     start_time=None, stop_time=None,
                     args=[], kwargs={}):
        """
        Schedules a periodic task.

        :param task_key:
        :param interval:
        :param start_time: If None, start immediately.
        :param stop_time: If None, the task run indefinitely.
        :return: the schedule
        """
        task = self._tasks.get(task_key)
        if task is None:
            raise TaskNotRegistered()

        schedule_id = uuid1().hex
        schedule = PeriodicSchedule(schedule_id, task, interval,
                                    start_time, stop_time,
                                    args, kwargs)
        self._schedules[schedule_id] = schedule
        schedule.start()
        return schedule

    def cancel(self, schedule):
        """
        Cancels the scheduled task.

        :param schedule_id:
        :return:
        """
        if schedule is None:
            return False
        del self._schedules[schedule.id]
        schedule.kill()
        return True

    def get_schedule(self, sched_id):
        """ Gets the schedule via the given id.

        :param sched_id: the schedule id.
        :return:
        """
        return self._schedules.get(sched_id)