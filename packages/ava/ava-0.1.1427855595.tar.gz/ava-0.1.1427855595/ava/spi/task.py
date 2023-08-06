# -*- coding: utf-8 -*-
"""
Task declaration
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from .context import instance as agent

_engine = agent().task_engine


def task(func):
    """
    Marks a function as a task template(code, arguments, etc).

    :param func:
    :return: the task wrapping given function object.
    """
    return _engine.register(func)


def run_once(task, seconds=0, args=[], kwargs={}):
    """
    Run a one-time task later after the specified seconds.

    :param task: the task proxy
    :param seconds: the delayed seconds before running.
    :return: the schedule.
    """
    return task.run_once(seconds, args, kwargs)


def run_periodic(task, interval, start_time=None, stop_time=None,
                 args=[], kwargs={}):
    """

    :param task: the task proxy.
    :param interval: the interval in seconds.
    :param start_time: the timestamp from which the task can be run
    :param stop_time: the timestamp before which the task should be run
    :return: the schedule.
    """
    return task.run_periodic(interval, start_time, stop_time,
                                args, kwargs)


def cancel_schedule(sched):
    _engine.cancel(sched)


def cancel_schedule_by_id(sched_id):
    sched = _engine.get_schedule(sched_id)
    if sched:
        _engine.cancel(sched)


def get_schedule_by_id(sched_id):
    """ Gets schedule by ID.

    :param sched_id:
    :return:
    """
    return _engine.get_schedule(sched_id)