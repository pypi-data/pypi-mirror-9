import logging
import g11pyutils as utils
LOG = logging.getLogger("each")


class Each(object):
    """Yields multiple events for each input event by replicating the
    event per instance of the input event field, which must be a list"""
    def __init__(self, spec):
        if spec.find('=') > 0:
            self.key, self.new_key = spec.split('=', 1)
        else:
            self.key = spec
            self.new_key = self.key


    def filter(self, events):
        for e in events:
            prop = e.get(self.key)
            if prop:
                if isinstance(prop, (list, tuple)):
                    for p in prop:
                        new_e = e.copy()
                        del new_e[self.key]
                        new_e[self.new_key] = p
                        yield new_e
                elif self.key != self.new_key:
                    e[self.new_key] = prop
                    del e[self.key]
                    yield e

