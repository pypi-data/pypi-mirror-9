import g11pyutils as utils
import re
import logging
from datetime import datetime, timedelta

LOG = logging.getLogger("Nginx")

class Nginx(object):
    """
    Parses an NGINX log with the following format:
    10.208.128.193 - - [30/Apr/2014:07:32:09 +0000]  "GET / HTTP/1.1" 200 2089 "-" "Mozilla/5.0 (Lin...37.36" 0.028 "149.254.219.174, 66.249.93.213, 10.183.252.20, ::ffff:127.0.0.1,::ffff:127.0.0.1"

    And assigns to event properties as follows:
    {client_ip} - {remote_user} [{timestamp}] "GET {uri} HTTP/{http_ver}" {status} {length} "{referer}" "{user_agent}" {duration} "{forwarded_for}"

    Properties which would be set to '-' (esp. remote_user and referer) are simply omitted
    Accepts the option "deproxy=true" which will
    """

    LOG_FMT = re.compile(r'([^\s]+) - ([^\s]+) \[([^\]]+)\]\s+"(\w+) ([^\s]+) HTTP/([^"]+)" (\d+) (\d+) "([^"]*)" "([^"]*)" ([^\s]+) "([^"]+)"')
    def __init__(self, spec=None):
        if spec:
            args = spec.split(',', 1)
            f = args[0]
            self.opts = utils.to_dict(args[1]) if len(args) is 2 else {}
        else:
            f = None
            self.opts = {}
        self.fo = utils.fopen(f)

    def __iter__(self):
        for line in self.fo:
            LOG.debug("Raw line: %s" % line)
            m = Nginx.LOG_FMT.match(line)
            if not m:
                LOG.warn("Input line did not match regex: %s" % line)
            else:
                g = m.groups()
                # Always set these
                e = {"method": g[3], "uri": g[4], "http_ver": g[5], "status": int(g[6]), "length": int(g[7]), "duration":float(g[10])}
                # Set these only if not '-'
                if g[2] and g[2] != '-':
                    e['remote_user'] = g[2]
                if g[8] and g[8] != '-':
                    e['referer'] = g[8]
                if g[9] and g[9] != '-':
                    e['user_agent'] = g[9]
                # Parse timestamp
                e['timestamp'] = Nginx.to_ts(g[2])
                # For deproxy, client is actually left-most forwarded IP
                if self.opts.get('deproxy') == "true" and g[11]:
                    ips = [s.strip() for s in g[11].split(",")]
                    e['rev_proxy_ip'] = g[0]
                    e['client_ip'] = ips[0]
                    if len(ips) > 1:
                        e['forwarded_for'] = ",".join(ips[1:])
                else:
                    e['client_ip'] = g[0]
                    e['forwarded_for'] = g[11]

                yield e

    DATE_FMT = re.compile(r'([^\s]+) ([\+\-])(\d+)')
    @staticmethod
    def to_ts(s):
        """Parses an NGINX timestamp from  "30/Apr/2014:07:32:09 +0000" and returns it as ISO 8601" """

        # Strip TZ portion if present
        m = Nginx.DATE_FMT.match(s)
        if m:
            s = m.group(1)
            delta = timedelta(seconds=int(m.group(3)) * (-1 if m.group(2) == '-' else 1)) # Offset from GMT
        else:
            delta = timedelta(seconds=0)
        dt = datetime.strptime(s, "%d/%b/%Y:%H:%M:%S")
        dt += delta
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')