import g11pyutils as utils
import codecs
import sys
import logging
LOG = logging.getLogger("csv_out")

class CSVOut(object):
    def __init__(self, spec=""):
        args = spec.split(",", 1)
        if len(args) > 1:
            opts = utils.to_dict(args[1])
        else:
            opts = {}
        self.fo = utils.fout(args[0], opts.get('enc', 'utf-8'))

        #self.fo = codecs.getwriter('utf8')(sys.stdout)

    def process(self, events):
        keys = None
        for e in events:
            if not keys:
                keys = e.keys()
                self.fo.write(','.join(keys))
                self.fo.write('\n')
            try:
                self.fo.write(','.join([str(e.get(k, '')) for k in keys]))
                self.fo.write('\n')
            except:
                LOG.warn("Exception outputting: %s", e)
        self.fo.flush()