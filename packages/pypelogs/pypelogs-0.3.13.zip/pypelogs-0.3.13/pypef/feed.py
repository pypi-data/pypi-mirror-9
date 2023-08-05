import logging
import g11pyutils as utils
import xml.etree.ElementTree as ET
LOG = logging.getLogger("feed")
import re
from datetime import datetime, timedelta

STRIP = set(['category', 'box', 'featurename', 'guid', 'pubDate'])

class Feed(object):

    """
    Pulls URLs off of incoming events (field name given as the spec).
    For each URL, fetches the URL and attempts to parse it as an RSS/Atom feed.
    Emits a new event for each item in the RSS feed, containing all of the
    attributes of the original event (except the URL), along with:
    title
    description
    url (of the individual item)
    coords (any GeoRSS coordinates found)
    timestamp
    image_url
    """
    def __init__(self, spec='url'):
        self.key = spec

    def filter(self, events):
        for e in events:
            url = e.get(self.key)
            if not url:
                continue
            e.pop(self.key)
            for i in self.feed_items(url):
                d = e.copy()
                d.update(i)
                yield d

    def feed_items(self, url):
        fo = utils.fopen(url, 'b')
        context = ET.iterparse(fo, events=("start", "end"))
        ET.register_namespace('', 'rss')
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = context.next()
        LOG.info("Root attrib: %s", root.attrib)
        items = 0
        yielded = 0
        for event, el in context:
            tag = bare(el.tag)
            LOG.debug("Event: %s, El: %s, Tag: '%s'", event, el, tag)
            if event == "end" and tag == "item":
                items += 1
                d = utils.etree_to_dict(el, ignore=['domain'])
                item = d["item"]

                # Ignore items without points, else covert to GeoJSON loc
                if not "point" in item:
                    continue
                lat, lon = [float(s) for s in item.pop("point").split(' ')]
                item['loc'] = {"type": "Point", "coordinates": (lon, lat)}
                # Fixup date
                if "updated" in item:
                    item['updated'] = normalize_timestamp(item['updated'])
                elif "pubDate" in item:
                    item['updated'] = normalize_timestamp(item['pubDate'])
                if "origLink" in item:
                    item['link'] = item.pop('origLink')
                if "link" in item:
                    item['url'] = item.pop('link')
                [item.pop(s) for s in STRIP if s in item]
                yielded += 1
                yield item
            root.clear()  # clear each time to prevent memory growth
        LOG.info("Found coords in %s of %s items" % (yielded, items))

    def to_event(self, d):
        pass


def bare(tag):
    """Returns a tag stripped of preceding namespace info"""
    n = tag.rfind('}')
    return tag[n+1:] if n >= 0 else tag


TRAILING_TZ = re.compile(r'.*([+\-])(\d{2}):?(\d{2})')


def normalize_timestamp(s):
    LOG.info("Parsing '%s'" % s)
    if not s:
        return None
    # Convert trailing TZ to timedelta
    m = TRAILING_TZ.match(s)
    if m:
        s = s[0:m.start(1)]
        delta = timedelta(seconds=60*( 60*int(m.group(2)) + int(m.group(3)) ) * (1 if m.group(1) == '-' else -1)) # Offset from GMT
    else:
        delta = timedelta(seconds=0)
    # Ignore MS
    dot = s.find('.')
    if dot:
        s = s[0:dot]
    LOG.info("Found timedelta %s, parsing '%s'" % (delta, s))
    try:
        dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")  # ISO 8061
    except ValueError:
        dt = datetime.strptime(s, "%a, %d %b %Y %H:%M:%S")  # RFC822: Fri, 11 Jul 2014 12:21:04 +000
    dt += delta
    return dt  # dt.strftime('%Y-%m-%dT%H:%M:%SZ')