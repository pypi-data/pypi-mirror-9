from pypein import MySQLIn
import logging


LOG = logging.getLogger("MySQLOut")
BUCKET_SIZE = 100


class MySQLOut(MySQLIn):
    """
    Supports upserting of data into MySQL.  Unlike the SQL output, this does a non-standard 'upsert' operation
    that can update rows.  Example usage:

    mysql:username:password@host:port/db,upsert,table,key

    The incoming events are expected to be compatible with the target table, and key indicates the field that
    will be used to determine whether the action is an insert or update.
    """
    def __init__(self, spec=""):
        super(MySQLOut, self).__init__(spec)
        cmd, self.table, self.key = self.query.split(',')
        if cmd != 'upsert':
            raise Exception("Only the 'upsert' command is currently supported")

    def process(self, events):
        bucket = []
        for event in events:
            bucket.append(event)
            if len(bucket) >= BUCKET_SIZE:
                self.upsert(bucket)
                bucket = []
        if len(bucket):
            self.upsert(bucket)

    def upsert(self, events):
        """Inserts/updates the given events into MySQL"""
        existing = self.get_existing_keys(events)
        inserts = [e for e in events if not e[self.key] in existing]
        updates = [e for e in events if e[self.key] in existing]
        self.insert(inserts)
        self.update(updates)

    def get_existing_keys(self, events):
        """Returns the list of keys from the given event source that are already in the DB"""
        data = [e[self.key] for e in events]
        ss = ','.join(['%s' for _ in data])
        query = 'SELECT %s FROM %s WHERE %s IN (%s)' % (self.key, self.table, self.key, ss)
        cursor = self.conn.conn.cursor()
        cursor.execute(query, data)
        LOG.info("%s (data: %s)", query, data)
        existing = [r[0] for r in cursor.fetchall()]
        LOG.info("Existing IDs: %s" % existing)
        return set(existing)

    def insert(self, events):
        """Constructs and executes a MySQL insert for the given events."""
        if not len(events):
            return
        keys = sorted(events[0].keys())
        ss = ','.join(['%s' for _ in keys])
        query = 'INSERT INTO %s (%s) VALUES ' % (self.table, ','.join(keys))
        data = []
        for event in events:
            query += '(%s),' % ss
            data += [event[k] for k in keys]
        query = query[:-1] + ';'
        LOG.info("%s (data: %s)", query, data)
        conn = self.conn.conn
        cursor = conn.cursor()
        cursor.execute(query, data)
        conn.commit()

    def update(self, events):
        if not len(events):
            return
        # Get all non-key properties (by sampling 1st event)
        props = [p for p in sorted(events[0].keys()) if p != self.key]
        conn = self.conn.conn
        for event in events:
            query = 'UPDATE %s SET' % self.table
            for prop in props:
                query += ' %s=%%(%s)s,' % (prop, prop)
            query = query[:-1]
            query += ' WHERE %s = %%(%s)s;' % (self.key, self.key)
            LOG.info("%s (data: %s)", query, event)
            cursor = conn.cursor()
            cursor.execute(query, event)
            cursor.close()
        # Make sure data is committed to the database
        conn.commit()
