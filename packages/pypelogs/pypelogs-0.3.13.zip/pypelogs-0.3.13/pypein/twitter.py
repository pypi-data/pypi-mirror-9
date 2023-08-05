import g11pyutils as utils
import logging
from datetime import datetime, timedelta

LOG = logging.getLogger("Twitter")


class Twitter(object):
    """
    Input from the Twitter API
    """
    def __init__(self, spec):
        # Defer import until we need it
        import tweepy

        args = spec.split(',', 2)
        creds_file = args[0]
        with open(creds_file, "r") as fo:
            creds = eval(fo.read())
        LOG.info("Creds: (%s) %s" % (type(creds), creds))
        auth = tweepy.OAuthHandler(creds['api_key'], creds['api_secret'])

        self.cmd = args[1]
        self.params = {
            'result_type': 'mixed',
            'lang': 'en',
            'include_entities': 'true',
            'count': 100
        }
        self.params.update(utils.to_dict(args[2]))
        if 'count' in self.params:
            self.params['count'] = int(self.params['count'])
        if 'as' in self.params:
            user = creds['users'][self.params.pop('as')]
            auth.set_access_token(user['access_token'], user['access_token_secret'])
        if 'geocode' in self.params:
            self.params['geocode'] = self.params['geocode'].replace(':', ',')
        self.api = tweepy.API(auth)

    def __iter__(self):
        f = getattr(self.api, self.cmd)
        i = 0
        while True:
            i += 1
            LOG.info("%s call(s) to %s with params %s" % (i, self.cmd, self.params))
            last_id = None
            for t in f(**self.params):
                tweet = t._json
                tweet['created_at'] = normalize_timestamp(tweet['created_at'])
                last_id = tweet['id_str']
                yield tweet
            self.params['max_id'] = last_id


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
