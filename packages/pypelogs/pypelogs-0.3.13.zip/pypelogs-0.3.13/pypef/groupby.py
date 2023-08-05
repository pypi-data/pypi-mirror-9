import logging
import g11pyutils as utils
import itertools
LOG = logging.getLogger("groupby")


class GroupBy(object):
    """Yields an event per input bucket, grouping on a given field and outputting fields via aggregate functions"""
    def __init__(self, spec):
        args = spec.split(",", 1)
        self.group_keys = args[0].split(":")
        opts = utils.to_dict(args[1]) if len(args) > 1 else {}

    def filter(self, events):
        for e in events:
            if isinstance(e, dict):
                yield self.group_events(itertools.chain([e], events))
                break
            else:
                yield self.group_events(e)

    def group_events(self, events):
        groups = {}
        for e in events:
            key = ':'.join([str(e.get(k, 'None')) for k in self.group_keys])
            if not groups.has_key(key):
                LOG.info("New group key: %s", key)
                groups[key] = [e]
            else:
                groups[key].append(e)
        bucket = []
        for k, v in groups.iteritems():
            e = {}
            for gk in self.group_keys:
                if gk != '*':
                    e[gk] = v[0][gk]  # Use first event to populate keys
            e['count'] = len(v)
            bucket.append(e)
        return bucket









