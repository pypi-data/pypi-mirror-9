import logging
import itertools
LOG = logging.getLogger("keep")


class Filter(object):
    """Base filter class; can be used for subclasses that want to treat events and buckets uniformly"""

    def filter(self, events):
        #first = events.next()  # Remove first event
        first = next(events)
        events = itertools.chain([first], events)  # Paste it back on
        if isinstance(first, dict):
            for e in self.filter_events(events):
                yield e
        else:
            for e in events:
                yield [e for e in self.filter_events(e)]

    def filter_events(self, events):
        raise Exception("Subclasses must override")