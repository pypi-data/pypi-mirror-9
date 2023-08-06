from . import task


__all__ = ['with_attributes', 'Activity']


def with_attributes(name=None, version=None, task_list=None,
                    retry=0,
                    raises_on_failure=False,
                    start_to_close_timeout=None,
                    schedule_to_close_timeout=None,
                    schedule_to_start_timeout=None,
                    heartbeat_timeout=None):
    """
    :param name: of the activity type.
    :type  name: str.

    """
    def wrap(func):
        return Activity(
            func, name, version, task_list,
            retry,
            raises_on_failure,
            start_to_close_timeout,
            schedule_to_close_timeout,
            schedule_to_start_timeout,
            heartbeat_timeout
        )

    return wrap


class Activity(object):
    def __init__(self, callable,
                 name=None,
                 version=None,
                 task_list=None,
                 retry=0,
                 raises_on_failure=False,
                 start_to_close_timeout=None,
                 schedule_to_close_timeout=None,
                 schedule_to_start_timeout=None,
                 heartbeat_timeout=None):
        self._callable = callable

        self._name = name
        self.version = version
        self.task_list = task_list
        self.retry = retry
        self.raises_on_failure = raises_on_failure
        self.task_start_to_close_timeout = start_to_close_timeout
        self.task_schedule_to_close_timeout = schedule_to_close_timeout
        self.task_schedule_to_start_timeout = schedule_to_start_timeout
        self.task_heartbeat_timeout = heartbeat_timeout

        self.register()

    def register(self):
        task.registry.register(self, self.task_list)

    @property
    def name(self):
        import types

        if self._name is not None:
            return self._name

        callable = self._callable
        prefix = self._callable.__module__

        if hasattr(callable, 'name'):
            name = callable.name
        elif isinstance(callable, types.FunctionType):
            name = callable.func_name
        else:
            name = callable.__class__.__name__

        return '.'.join([prefix, name])

    def __repr__(self):
        return 'Activity(name={}, version={}, task_list={})'.format(
            self.name,
            self.version,
            self.task_list)
