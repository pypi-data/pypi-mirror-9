import logging
from .filter import Filter
LOG = logging.getLogger("keep")


class Keep(Filter):
    """Keeps only the indicated, comma-delimited list of fields"""
    def __init__(self, spec):
        super(Filter, self).__init__()
        self.keeps = spec.split(',')

    def filter_events(self, events):
        for e in events:
            keep = {k: e[k] for k in self.keeps if k in e}
            yield keep