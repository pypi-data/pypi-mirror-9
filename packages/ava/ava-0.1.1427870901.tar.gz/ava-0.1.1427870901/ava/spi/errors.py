# -*- coding: utf-8 -*-
"""
Exceptions raised in eavtar.kits package.
"""
from __future__ import absolute_import, division, print_function, unicode_literals


class AvaError(Exception):
    """
    Raised when error is framework-related but no specific error subclass exists.
    """
    def __init__(self, *args, **kwargs):
        super(AvaError, self).__init__(args, kwargs)


class DataError(AvaError):
    """
    Generic error related to database operations.
    """
    def __init__(self, *args, **kwargs):
        super(DataError, self).__init__(*args, **kwargs)


class DataNotFoundError(DataError):
    def __init__(self, *args, **kwargs):
        super(DataNotFoundError, self).__init__(*args, **kwargs)


class DataExistError(DataError):
    def __init__(self, *args, **kwargs):
        super(DataExistError, self).__init__(*args, **kwargs)


class TaskAlreadyRegistered(AvaError):
    """ Raised to indicate a task is being registered with the same key as a
    existing one.
    """
    def __init__(self, task_key):
        super(TaskAlreadyRegistered, self).__init__()
        self.task_key = task_key

    def __str__(self):
        return "Task %s already registered." % self.task_key


class TaskNotRegistered(AvaError):
    """
    Raised when a task is not registered but is requested to schedule.
    """
    def __init__(self, task_key):
        super(TaskNotRegistered, self).__init__()
        self.task_key = task_key

    def __str__(self):
        return "Task %s not registered." % self.task_key

