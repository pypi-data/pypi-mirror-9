import logging
from .filter import Filter
LOG = logging.getLogger("trim")


class Trim(Filter):
    """Trims the indicated, comma-delimited list of fields"""
    def __init__(self, spec):
        super(Filter, self).__init__()
        self.fields = spec.split(',')

    def filter_events(self, events):
        for e in events:
            #LOG.warn("Keeping %s", e)
            yield dict((k,v) for k, v in e.iteritems() if not k in self.fields)
