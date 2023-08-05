import g11pyutils as utils
import json
import logging
LOG = logging.getLogger("json_in")

class JSON(object):
    def __init__(self, f='-'):
        self.fo = utils.fopen(f)

    def __iter__(self):
        count = 0
        for line in self.fo:
            count += 1
            try:
                yield json.loads(line)
            except Exception as ex:
                LOG.warn("Exception parsing input line %s: %s", count, ex)