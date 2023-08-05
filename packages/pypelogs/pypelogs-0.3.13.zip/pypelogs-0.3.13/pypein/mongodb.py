import g11pyutils as utils
import logging

LOG = logging.getLogger("MongoDBIn")


class MongoDBIn(object):
    def __init__(self, spec, host='127.0.0.1', port=27017, buff=1000, id_field=None, updated_field='_updated',
                 upsert=False):
        """
        Constructs a MongoDB output
        :param spec: A string for embedding options, e.g. 'host=example.com,port=80,id=_id,ts=created:updated
        :param host: The MongoDB host, defaults to localhost
        :param port: The MongoDB port, defaults to 27017, the default MongoDB port
        :param buff: The number of documents to accumulate for each DB TX
        :param id_field: The event field that should be used as the ID
        """
        import pymongo
        LOG.warn(pymongo.get_version_string())
        args = spec.split(",", 1)
        self.db_name, self.coll = args[0].split(".")
        opts = utils.to_dict(args[1]) if len(args) > 1 else {}
        self.host = opts.get("host", host)
        self.port = opts.get("port", port)
        self.buffer = opts.get("b", buff)
        self.id_field = opts.get("id", id_field)
        self.updated_field = opts.get("updated", updated_field)
        self.upsert = ('%s' % opts.get("upsert", upsert)).lower() == "true"
        self.pymongo_client = pymongo.MongoClient
        self.pymongo_errors = pymongo.errors

        def do_connect():
            return self.do_connect()

        def do_close():
            return self.do_close(self.conn)

        self.conn = utils.Connector(do_connect, do_close)
        self.conn.connect()

    def do_connect(self):
        mongo_client = self.pymongo_client(self.host, self.port)
        self.collection(mongo_client)  # verify
        return mongo_client

    def db(self, cli=None):
        mongo_client = cli if cli else self.conn.c()
        if not mongo_client:
            raise Exception("Not connected")
        if not self.db_name in mongo_client.database_names():
            raise ValueError("No database named '%s'", self.db_name)
        return mongo_client[self.db_name]

    def collection(self, cli=None):
        db = self.db(cli)
        if not self.coll in db.collection_names():
            raise ValueError("Database '%s' has no collection named '%s'" % (self.db, self.coll))
        return db[self.coll]

    def do_close(self, conn):
        conn.close()

    @staticmethod
    def is_connect_err(ex):
        if repr(ex).find('E11000') >= 0:
            return False
        return True


class MongoDBGeo(MongoDBIn):
    def __init__(self, spec, host='127.0.0.1', port=27017, buff=1000):
        super(MongoDBGeo, self).__init__(spec, host, port, buff)
        from bson.son import SON
        self.SON = SON
        args = spec.split(",", 1)
        if len(args) > 1:
            opts = utils.to_dict(args[1])
            self.coords = [float(c) for c in opts.get("coords").split(':')]
        else:
            self.coords = []

    def __iter__(self):
        if len(self.coords) == 2:  # Geonear
            for r in self.db().command(self.SON([('geoNear', self.coll), ('near', [self.coords[1], self.coords[0]]),
                                                 ('spherical', True)]))['results']:
                doc = r['obj']
                doc['dis'] = r['dis']
                doc['_id'] = repr(doc['_id'])
                yield doc
        else:
            if len(self.coords) == 0:  # Bounding box of lat1:lon1:lat2:lon2
                # TODO: implement
                pass
            elif len(self.coords) == 3:  # geonear lat:lon:results
                q = {"loc": {"$within": {"$center": [[0, 0], 6]}}}
                for doc in self.collection().find(q):
                    yield doc
