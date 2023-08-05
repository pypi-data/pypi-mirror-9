import logging
import re
LOG = logging.getLogger("bucket")


class Bucket(object):
    """Converts individual events to lists of events of a specified length. If events are already coming in as buckets,
    then re-buckets them.  Use with negative arguments to distribute into N buckets (requires
    getting whole list into memory).  Use 0 to unbucket.  Use with a field name to create a new bucket
    whenever that property changes"""

    INT_FMT = re.compile(r'\d+')
    def __init__(self, spec=0):
        if Bucket.INT_FMT.match(spec):
            self.size = int(spec)
            self.prop = None
            self.filter_func = self.filter_by_size
        else:
            self.size = 0
            self.prop = spec
            self.filter_func = self.filter_by_prop

    def filter(self, events):
        return self.filter_func(events)

    def filter_by_size(self, events):
        bucket = []
        for e in events:
            if isinstance(e, dict):  # Single event, append
                bucket.append(e)
            else:
                bucket += list(e)  # List, add all to bucket
            if self.size == 0:  # Unbucket
                for b in bucket:
                    yield b
                bucket = []
            while 1 <= self.size <= len(bucket):  # Re-bucket (positive)
                b = bucket[0:self.size]
                bucket = bucket[self.size:]
                yield b
        if self.size >= 1 and len(bucket):  # Re-bucket (positive)
            yield bucket   # Leftover
        elif self.size < 0: # Must be re-bucketing into N
            n_buckets = -self.size
            b_size = len(bucket) / n_buckets  # Num events/bucket (if no extra)
            extra = len(bucket) % n_buckets  # Num of buckets with an extra item
            LOG.info("Splitting %s items into %s buckets (%s items per bucket)", len(bucket), n_buckets, b_size)
            n = 0
            while n < len(bucket):
                sz = b_size
                if extra > 0:
                    sz += 1
                    extra -= 1
                yield bucket[n:n+sz] if n+sz < len(bucket) else bucket[n:]
                n += sz

    def filter_by_prop(self, events):
        b = []
        for e in events:
            if not b or b[0].get(self.prop) == e.get(self.prop):
                b.append(e)
            else:
                yield b
                b = []
        if b:
            yield b




