from itertools import chain


def get_start_to_close_timing(event):
    last_state = event['state']
    start = event['started_timestamp']
    end = event['{}_timestamp'.format(last_state)]

    return (last_state, (end - start).total_seconds())


class WorkflowStatistics(object):
    def __init__(self, history):
        self._history = history

    def total_time(self):
        history = self._history
        start = history.events[0].timestamp
        end = history.events[-1].timestamp
        return (end - start).total_seconds()

    def start_to_close_timings(self):
        history = self._history
        history.parse()

        events = chain(
            history._activities.iteritems(),
            history._child_workflows.iteritems(),
        )
        return [
            (name, get_start_to_close_timing(attributes)) for
            name, attributes in events
        ]

    def start_to_close_timings_with_percentage(self):
        total_time = self.total_time()

        return [
            (name, timing, (timing / total_time) * 100.) for
            name, (last_state, timing) in self.start_to_close_timings()
        ]
