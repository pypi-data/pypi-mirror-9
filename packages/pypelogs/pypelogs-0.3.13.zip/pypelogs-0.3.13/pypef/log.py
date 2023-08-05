import g11pyutils as utils

class Log(object):
    """Logs events as they pass through"""
    def __init__(self, spec=None):
        self.m = None
        if spec:
            args = spec.split(",", 1)
            fname = args[0]
            if len(args) > 1:
                opts = utils.to_dict(args[1])
                self.m = int(opts["m"]) if "m" in opts else None
        else:
            fname = spec
        self.fo = utils.fout(fname)

    def filter(self, events):
        ctr = 0
        for e in events:
            if not self.m or ctr % self.m == 0:
                self.fo.write("LOG event %s: " % ctr)
                self.fo.write(repr(e))
                self.fo.write('\n')
                self.fo.flush()
            yield e
            ctr += 1