import logging
import g11pyutils as utils
LOG = logging.getLogger("head")


class Head(object):
    """Implements the equivalent of Unix 'head' command"""
    def __init__(self, spec = None):
        self.count = 0
        opts = utils.to_dict(spec)
        self.n = int(opts["n"]) if opts and "n" in opts else 10

    def done(self):
        if self.n > 0 and self.n <= self.count:
            return True

    def filter(self, events):
        self.count = 0
        for e in events:
            self.count += 1
            yield e
            if self.done():
                raise StopIteration

