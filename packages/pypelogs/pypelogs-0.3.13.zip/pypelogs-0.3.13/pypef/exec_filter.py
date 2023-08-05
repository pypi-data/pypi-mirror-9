import logging
from .filter import Filter
LOG = logging.getLogger("exec")

class Exec(Filter):
    """Executes arbitrary code on each even, where local 'e' is the event being passed in."""
    def __init__(self, spec):
        super(Filter, self).__init__()
        self.expr = compile(spec, '<string>', 'exec')

    def filter_events(self, events):
        for e in events:
            exec(self.expr, {}, {"e": e})
            yield e