import logging
from datetime import datetime
from pypein import MongoDBIn

LOG = logging.getLogger("MongoDB")


class MongoDBOut(MongoDBIn):

    def process(self, pin):
        buff = []
        for e in pin:
            if self.id_field:  # Set ID if an ID field was specified
                e['_id'] = e.pop(self.id_field)
            if self.updated_field and self.updated_field in e:
                try:
                    uf = e[self.updated_field]
                    e['_updated'] = uf if isinstance(uf, datetime) else parse_iso8601(uf)
                    if self.updated_field != '_updated':
                        e.pop(self.updated_field)  # Only if 1st step completes
                except Exception as ex:
                    LOG.warn("Exception parsing updated date: %s, %s" % (ex, ex.message))
            LOG.debug("Inserting %s", e)
            buff.append(e)
            if len(buff) >= self.buffer:
                self.send(buff)
                buff = []
        if buff:
            self.send(buff)

    def send(self, docs):
        c = self.collection()
        while True:
            try:
                if self.upsert:
                    inserts = []
                    upserts = []
                    for d in docs:
                        if '_id' in d:
                            upserts.append(d)
                        else:
                            inserts.append(d)
                    if inserts:
                        LOG.info("Inserting %s new docs" % len(docs))
                        c.insert(inserts)
                    if upserts:
                        LOG.info("Upserting %s docs" % len(docs))
                        bulk = c.initialize_ordered_bulk_op()
                        for u in upserts:
                            bulk.find({'_id': u.pop('_id')}).upsert().update({'$set': u})
                        bulk.execute()
                else:
                    LOG.info("Inserting %s docs" % len(docs))
                    c.insert(docs, manipulate=False, continue_on_error=True)
                break
            except self.pymongo_errors.DuplicateKeyError as dke:
                LOG.warn(dke)
                break
            except Exception as ex:
                LOG.warn("Bulk insert failed: %s", ex)
                if self.is_connect_err(ex):
                    self.conn.reconnect()
                else:
                    break


def parse_iso8601(s):
    """Parses a standard ISO8601 date into a python datetime for insertion into MongoDB"""
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')