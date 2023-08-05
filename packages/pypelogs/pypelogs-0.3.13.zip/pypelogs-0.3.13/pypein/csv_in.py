import g11pyutils as utils
import logging
import csv
LOG = logging.getLogger("csv_in")


DELIMS = {"tab": "\t", "comma": ","}

class CSVIn(object):
    def __init__(self, spec=None):
        args = spec.split(",", 1)
        if len(args) > 1:
            self.opts = utils.to_dict(args[1])
        else:
            self.opts = {}
        if "headers" in self.opts:
            self.headers = self.opts['headers'].split(':')
        else:
            self.headers = None
        if "delim" in self.opts:
            dkey = self.opts["delim"]
            delim = DELIMS[dkey] if dkey in DELIMS else dkey
        else:
            delim = ","
        fo = utils.fopen(args[0], self.opts.get('enc', 'utf-8'))
        self.reader = csv.reader(fo, delimiter=delim)

    def __iter__(self):
        count = 0
        for vals in self.reader:
            count += 1
            if not self.headers:
                self.headers = vals
                continue
            try:
                e = {}
                i = 0
                for h in self.headers:
                    e[h] = vals[i]
                    i += 1
                yield e
            except Exception as ex:
                LOG.warn("Exception parsing input line %s: %s", count, ex)