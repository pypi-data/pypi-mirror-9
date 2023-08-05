import g11pyutils as utils
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
import logging
import re
import base64
import hashlib
import codecs

LOG = logging.getLogger("wikip")

class WikipXMLParser(XMLParser):
    def init(self, html=0, target=None, encoding=None):
        super(WikipXMLParser, self).__init__(html, target, encoding)

    def feed(self, data):
        #LOG.warn("Feeding %s %s" % (type(%s), data))
        # Yes this is awful, I've got to encode it...
        #data = codecs.
        r = super(WikipXMLParser, self).feed(data)
        LOG.warn("Returned %s" % r)
        return r

    def Parse(self, data, num):
        LOG.warn("Hello!!!!")
        super(WikipXMLParser, self).Parse(data, num)

class WikipArticles(object):
    """Iterates over a Wikipedia XML article dump, producing one event per article.

    The event is a deeply-nested dict matching the article XML and capturing the full article contents.
    """
    def __init__(self, article_file=None, filter = None):
        self.fo = utils.fopen(article_file, 'b') # 'utf-8')
        self.filter = filter
        LOG.info("Using ElementTree version %s", ET.VERSION)

    def __iter__(self):
        # get an iterable
        context = ET.iterparse(self.fo, events=("start", "end"))#, parser=XMLParser(encoding="UTF-8"))
        ET.register_namespace('', 'http://www.mediawiki.org/xml/export-0.8/')
        # turn it into an iterator
        context = iter(context)
        # get the root element
        event, root = next(context)
        LOG.info("Root attrib: %s", root.attrib)
        for event, el in context:
            tag = bare(el.tag)
            LOG.debug("Event: %s, El: %s, Tag: '%s'", event, el, tag)
            if event == "end" and tag == "page":
                d = utils.etree_to_dict(el)
                if self.filter:
                    try:
                        d = self.filter(d)
                        if d:
                            yield d
                    except Exception as e:
                        LOG.warn("Exception filtering article: %s", e)
                else:
                    yield d
            root.clear()  # clear each time to prevent memory growth

class WikipGeo(WikipArticles):
    def __init__(self, article_file=None):
        super(WikipGeo, self).__init__(article_file, geo_filter)

def wikip_url(s):
    return 'http://wikipedia.org/wiki/'+s.replace(' ', '_')

def skip_article(title):
    """Skips articles that have no value"""
    if title.find("Wikipedia:WikiProject National Register of Historic Places/") == 0:
        return True
    return False

def geo_filter(d):
    """Inspects the given Wikipedia article dict for geo-coordinates.

    If no coordinates are found, returns None.  Otherwise, returns a new dict
    with the title and URL of the original article, along with coordinates."""
    page = d["page"]
    if not "revision" in page:
        return None
    title = page["title"]
    if skip_article(title):
        LOG.info("Skipping low-value article %s", title)
        return None
    text = page["revision"]["text"]
    if not utils.is_str_type(text):
        if "#text" in text:
            text = text["#text"]
        else:
            return None
    LOG.debug("--------------------------------------------------------------")
    LOG.debug(title)
    LOG.debug("--------------------------------------------------------------")
    LOG.debug(text)
    c = find_geo_coords(text)
    u = wikip_url(title)
    """
    m = hashlib.md5()
    m.update(u.encode("UTF-8") if hasattr(u, 'encode') else u)
    i = base64.urlsafe_b64encode(m.digest()).replace('=', '')
    """
    return {
        #"id": i,
        "title": title,
        "url": u,
        "coords": c,
        "updated": page["revision"].get("timestamp")
    } if c else None


def bare(tag):
    """Returns a tag stripped of preceding namespace info"""
    n = tag.rfind('}')
    return tag[n+1:] if n >= 0 else tag

'''
| latitude = 48.8738
| longitude = 2.2950
'''
INFO_BOX_LAT_LON = re.compile(r"(\|\s*latitude\s*=\s*(-?[\d\.]+)\s*\|\s*longitude\s*=\s*(-?[\d\.]+))", re.MULTILINE )
'''
{{coord|35.0797|-80.7742|region:US-NC_type:edu|display=title}}
{{coord|77|51|S|166|40|E|}}
'''
COORDS_GEN = re.compile(r"(\{\{coord\|[^\}]+\}\})")
#COORDS_GROUPS = re.compile(r"\{\{coord\|(?:display[^\|]+\|)?((?:\s*-?[\d\.]+\s*\|?){1,3})([NS]\|)?((?:\s*-?[\d\.]+\s*\|){0,3})([EW])?")
COORDS_GROUPS = re.compile(r"\{\{coord\|(?:[^\d\|]+\|)*((?:\s*-?[\d\.]+\s*\|?){1,3})([NS]\|)?((?:\s*-?[\d\.]+\s*\|){0,3})([EW])?")

def find_geo_coords(s):
    """Returns a list of lat/lons found by scanning the given text"""
    coords = []
    LOG.debug("Matching in text size %s", len(s))
    for c in INFO_BOX_LAT_LON.findall(s):
        try:
            coord = (float(c[1]), float(c[2]))  #, c[0])
            coords.append(coord)
            LOG.debug("Found info box lat/lon: %s", coord)
        except Exception as ex:
            LOG.warn("Bad parse of info box %s: %s", c, ex)
    for c in COORDS_GEN.findall(s):
        # Special cases
        if skip_coords(c):
            LOG.debug("Ignorning coords %s", c)
            continue
        m = COORDS_GROUPS.search(c)
        if not m:
            LOG.warn("Unrecognized coord format: %s", c)
            continue
        try:
            # Remove empty optional groups and remove pipes from matches
            g = [(s[0:-1] if s[-1] == '|' else s) for s in list(m.groups()) if s is not None and len(s)]
            #LOG.info("Found groups: %s", g)
            if len(g) == 1: # Single lat|lon
                lat, lon = g[0].split('|')
                coord = (float(lat), float(lon))  #, c)
                coords.append(coord)
                LOG.debug("Found lat|lon: %s", coord)
            elif g[3] == 'E' or g[3] == 'W':
                lat = depipe(g[0]) * (1 if g[1].upper() == 'N' else -1)
                lon = depipe(g[2]) * (1 if g[3].upper() == 'E' else -1)
                coord = (lat, lon)  #, c)
                coords.append(coord)
                LOG.debug("Found lat|NS|lon|EW: %s", coord)
            else:
                LOG.warn("Unrecognized coord format: %s (parsed %s)", c, g)
        except Exception as ex:
            LOG.warn("Bad parse of %s: %s", c, ex)
    l = []
    for c in set(coords):  # Dedupe; the reality is non-trivial though...we want to keep only the most precise
        if c[0] > 90 or c[0] < -90 or c[1] > 180 or c[1] < -180 or (c[0] == 0 and c[1] == 0):
            LOG.warn("Invalid lat or lon: %s", c)
        else:
            l.append({"type": "Point", "coordinates": (c[1], c[0])})  # GeoJSON, lon goes first
    return l

def depipe(s):
    """Convert a string of the form DD or DD|MM or DD|MM|SS to decimal degrees"""
    n = 0
    for i in reversed(s.split('|')):
        n = n / 60.0 + float(i)
    return n

def skip_coords(c):
    """Skip coordinate strings that are not valid"""
    if c == "{{coord|LAT|LONG|display=inline,title}}": # Unpopulated coord template
        return True
    if c.find("globe:") >= 0 and c.find("globe:earth") == -1: # Moon, venus, etc.
        return True
    return False
