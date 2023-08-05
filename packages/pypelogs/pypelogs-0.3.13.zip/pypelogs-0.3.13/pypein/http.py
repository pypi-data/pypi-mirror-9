import g11pyutils as utils
import logging
import requests
import os
LOG = logging.getLogger(os.path.basename(__file__))


class HTTP(object):
    """
    Fetches a JSON URL and emits the results as an object.

    If the result is a raw array, then
    an event for each array element is produced.  Otherwise, yields the whole thing.
    """
    def __init__(self, spec):
        args = spec.split(',', 1)
        self.url, host = self.parse_url(args[0])
        self.headers = {}
        self.cookies = {}
        if len(args) > 1:
            params = utils.to_dict(args[1])
            self.login(host, params.pop('login_uri'), params)

    def __iter__(self):
        rsp = self.fetch()
        if isinstance(rsp, dict):
            yield rsp
        else:
            for r in rsp:
                e = r if isinstance(r, dict) else {'scalar': r}
                yield e

    def login(self, host, login_uri, params):
        proto = 'https:' if self.is_secure() else 'http:'
        login_url = proto + '//' + host + login_uri
        LOG.info("Posting to %s with data %s and headers %s" % (login_url, params, self.headers))
        r = requests.post(login_url, data=params, cookies=self.cookies, headers=self.headers)
        LOG.info("Received response %s" % r.status_code)
        self.cookies = r.cookies

    def parse_url(self, uri):
        proto = 'https:' if self.is_secure() else 'http:'
        if uri[0:2] == '//':
            n = uri.find('/', 2)
            host = uri[2:n]
            url = proto + uri
        elif uri[0] == '/':
            host = '127.0.0.1'
            url = proto + '/' + host + uri
        else:
            raise ValueError('URI "%s" must begin with / or // ' % uri)
        return url, host

    def fetch(self):
        r = requests.get(self.url, cookies=self.cookies)
        if r.status_code != 200:
            raise Exception("Bad status fetching URL: %s" % r.status_code)
        try:
            json = r.json()
            return json
        except Exception:
            raise Exception("Exception parsing JSON (content type is '%s')" % r.headers.get('content-type'))


    def is_secure(self):
        return False


class HTTPS(HTTP):
    def is_secure(self):
        return True