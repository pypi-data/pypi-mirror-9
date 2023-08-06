from itertools import chain


def get_start_to_close_timing(event):
    last_state = event['state']
    scheduled = event.get('scheduled_timestamp')
    if scheduled is None:
        start = None
        end = None
        duration = None
    else:
        start = event['started_timestamp']
        end = event['{}_timestamp'.format(last_state)]
        duration = (end - start).total_seconds()

    return (last_state, scheduled, start, end, duration)


class WorkflowStatistics(object):
    def __init__(self, history):
        self._history = history

    def total_time(self):
        """
        Returns the total time of the workflow execution in seconds.

        :returns:
            :rtype: ``float``.

        """
        history = self._history
        start = history.events[0].timestamp
        end = history.events[-1].timestamp
        return (end - start).total_seconds()

    def get_timings(self):
        """
        Returns the time in seconds spent in the execution of a task, i.e.
        between the start and the close events, by task ID.

        :returns:
            :rtype: ``[(str, datetime.datetime, datetime.datetime, float)]``.

        Example: ::

            [(activity-module.func-1', start, end, 37.22),
             ('activity-module.otherfunc-1', start, end, 13.37)]

        """
        history = self._history
        history.parse()

        events = chain(
            history._activities.iteritems(),
            history._child_workflows.iteritems(),
        )
        return [
            (name,) + get_start_to_close_timing(attributes) for
            name, attributes in events
        ]

    def get_timings_with_percentage(self):
        """
        Returns the time in seconds and its percentage against the total time
        spent in the execution of a task, i.e. between the start and the close
        events, by task ID.

        :returns:
            :rtype: ``[(str, float, float)]``

        Example: ::

            [(activity-module.func-1', 36.22, 24.4),
             ('activity-module.otherfunc-1', 18.11, 12.2)]

        """
        total_time = self.total_time()

        return [
            (name, last_state, scheduled, start, end, timing, (timing / total_time) * 100. if timing else None) for
            name, last_state, scheduled, start, end, timing in self.get_timings()
        ]
