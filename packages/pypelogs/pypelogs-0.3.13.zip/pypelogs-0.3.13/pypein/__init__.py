from .csv_in import CSVIn
from .flickr import Flickr
from .http import HTTP, HTTPS
from .instagram_in import Instagram
from .json_in import JSON
from .mongodb import MongoDBGeo, MongoDBIn
from .mysql_in import MySQLIn
from .nginx import Nginx
from .oracle import Oracle
from .postgresql import Postgresql
from .text import Text
from .twitter import Twitter
from .wikip import WikipArticles, WikipGeo

CLASSES = {
    'csv':    CSVIn,
    'flickr': Flickr,
    'http':   HTTP,
    'https':  HTTPS,
    'ig':     Instagram,
    'json':   JSON,
    'mongeo': MongoDBGeo,
    'mysql':  MySQLIn,
    'nginx':  Nginx,
    'ora':    Oracle,
    'pgsql':  Postgresql,
    'text':   Text,
    'twitter': Twitter,
    'wikip':  WikipArticles,
    'wikig':  WikipGeo,
}

def register(s, clz):
    CLASSES[s] = clz


def input_for(s):
    spec_args = s.split(':', 1)
    clz = CLASSES.get(spec_args[0])
    if not clz:
        raise ValueError("No such input type: %s", spec_args[0])
    return clz() if len(spec_args) == 1 else clz(spec_args[1])
