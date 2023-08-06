# -*- coding: utf-8 -*-

from functools import wraps


def task_on_callbacks(*task_args, **task_kwargs):
    """
    A proxy for ``invoke.tasks.task`` parameterized decorator.
    """

    def decorator(function):
        """
        A decorator which wraps original Deferred-using function and converts
        it into Invoke task.
        """

        @wraps(function)
        def wrapper(*args, **kwargs):
            """
            Wrap original function and run in inside reactor loop.
            """

            from twisted.internet import defer, reactor

            def errback(failure):
                print(failure)

            deferred = defer.inlineCallbacks(function)(*args, **kwargs)
            deferred.addErrback(errback)
            deferred.addBoth(lambda unused: reactor.stop())

            reactor.run()

        from invoke.tasks import Task, task as task_decoracor

        class TaskProxy(Task):
            """
            A class which behaves like ``invoke.tasks.Task``.

            Inherit ``invoke.tasks.Task`` just to make Invoke's parser be able
            to recognize objects of this class as tasks. It would be better if
            Invoke had a defined task interface, but now we can use inheritance
            from ``Task`` only.
            """

            def __init__(self, task):
                # Store the task we want to proxy and mimic its attributes
                self.task = task
                self.__name__ = self.task.__name__
                self.__module__ = self.task.__module__
                self.__doc__ = self.task.__doc__

            def __call__(self, *args, **kwargs):
                # Substitute original function with wrapper for the time the
                # task is invoked
                self.task.body = wrapper
                result = self.task(*args, **kwargs)
                self.task.body = function
                return result

            def __getattr__(self, key):
                # Proxy logic: look up for attributes inside original task if
                # they were not found in this proxy
                return getattr(self.task, key)

        # Get usual Invoke task from original function. We cannot simply use
        # our wrapper here, because task's parameters are inspected dynamicaly
        # at runtime an they will be lost for Invoke's parser.
        task = task_decoracor(*task_args, **task_kwargs)(function)

        # Wrap task with a proxy, which will substitute original function
        # with our wrapper during task call.
        return TaskProxy(task)

    return decorator
