import logging
from .filter import Filter
import re
LOG = logging.getLogger("set")
from string import Template

SIMPLE = re.compile(r'^\$\{([^\{]+)\}$')
class Set(Filter):
    """Sets specified fields, treating each as a template with the original event subbed in"""
    def __init__(self, spec):
        super(Filter, self).__init__()
        self.templates = {}
        for s in spec.split(','):
            k, v = s.split('=')
            m = SIMPLE.match(v)
            if m:
                self.templates[k] = m.group(1)
            else:
                self.templates[k] = Template(v)

    def filter_events(self, events):
        for e in events:
            copy = e.copy()
            for k, t in self.templates.items():
                if isinstance(t, str):
                    copy[k] = e[t]  # Simple
                else:
                    copy[k] = t.safe_substitute(e)
            yield copy