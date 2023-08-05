import g11pyutils as utils
from string import Template
import sys

class TextOut(object):
    def __init__(self, spec=None):
        args = spec.split(',', 1)
        if len(args) == 1:
            self.fo = sys.stdout
            self.t = Template(args[0])
        else:
            self.fo = utils.fout(args[0])
            self.t = Template(args[1])

    def process(self, events):
        for e in events:
            self.fo.write(self.t.safe_substitute(e))
            self.fo.write("\n")
            self.fo.flush()