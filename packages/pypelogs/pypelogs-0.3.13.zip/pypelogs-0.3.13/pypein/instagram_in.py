import g11pyutils as utils
import logging
from datetime import datetime, timedelta

LOG = logging.getLogger("Instagram")


class Instagram(object):
    """
    Input from the Instagram API
    """
    def __init__(self, spec):
        # Defer import until we need it
        from instagram import client



        args = spec.split(',', 2)
        creds_file = args[0]
        with open(creds_file, "r") as fo:
            creds = eval(fo.read())
        LOG.info("Creds: (%s) %s" % (type(creds), creds))
        self.api = client.InstagramAPI(**creds)
        self.cmd = args[1]
        self.params = utils.to_dict(args[2])
        for k in self.params.keys():
            if Instagram.is_numeric(k):
                self.params[k] = float(self.params[k])

    @staticmethod
    def is_numeric(key):
        return key in set(['lat', 'lng', 'distance'])

    def __iter__(self):
        f = getattr(self.api, self.cmd)
        i = 0
        while True:
            i += 1
            LOG.info("%s call(s) to %s with params %s" % (i, self.cmd, self.params))
            data = f(**self.params)
            yielded = 0
            min_date = datetime.now()
            for e in data:
                e = e.__dict__
                if e.get('created_time'):
                    if e['created_time'] < min_date:
                        min_date = e['created_time']
                yield e
                yielded += 1
                LOG.info("Method '%s' yielded %s rows, min TS: %s" % (self.cmd, yielded, min_date))
                ts = utils.to_epoch_seconds(min_date)
                # If we've gone back in time in posts, then keep going
            if not 'max_timestamp' in self.params or self.params['max_timestamp'] > ts:
                LOG.info("Timestamp decreased from %s to %s" % (self.params.get('max_timestamp'), ts))
                self.params['max_timestamp'] = ts
            else:  # End of the line
                break





def normalize_timestamp(s):
    # Twitter format
    #"created_at":"Wed Aug 27 13:08:45 +0000 2008"
    # Pull off year
    dow, mo, dom, time, tz, yr = s.split(' ')
    # Put it back as RFC822 with no TZ
    rfc822 = '%s, %s %s %s %s' % (dow, dom, mo, yr, time)
    dt = datetime.strptime(rfc822, "%a, %d %b %Y %H:%M:%S")
    delta = timedelta(seconds=60*(60*int(tz[1:3]) + int(tz[4:5]))*(1 if tz[0] == '-' else -1))
    return dt + delta
