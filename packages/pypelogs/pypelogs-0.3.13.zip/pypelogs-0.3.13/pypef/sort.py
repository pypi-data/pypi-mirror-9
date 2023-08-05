import logging
from .filter import Filter
import operator
LOG = logging.getLogger("sorts")


class Sort(Filter):
    """Sorts on the indicated, comma-delimited list of fields"""
    def __init__(self, spec):
        super(Filter, self).__init__()
        self.sort_keys = []
        self.desc = set()
        for field in spec.split(','):
            if '=' in field:
                field, desc = field.split('=', 1)
                if desc.lower() == 'desc':
                    self.desc.add(field)
            self.sort_keys.append(field)

    def filter_events(self, events):
        l = list(events)
        for field in reversed(self.sort_keys):
            l = sorted(l, key=operator.itemgetter(field), reverse=(field in self.desc))
        for e in l:
            yield e