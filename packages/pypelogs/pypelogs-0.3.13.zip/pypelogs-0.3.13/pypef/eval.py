import logging
from .filter import Filter
LOG = logging.getLogger("eval")

class Eval(Filter):
    """Sets specified fields, treating each as a template with the original event subbed in"""
    def __init__(self, spec):
        super(Filter, self).__init__()
        self.expr = compile(spec, '<string>', 'eval')

    def filter_events(self, events):
        for e in events:
            if eval(self.expr):
                yield e