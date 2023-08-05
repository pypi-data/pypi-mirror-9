import g11pyutils as utils
import logging
import re

LOG = logging.getLogger("Postresql")
CONN_STR = re.compile(r'(\w+):(.+)@([^/]+)/([\w_]+)')


class Postgresql(object):
    """
    Input from a Postrgresql database, taking a connection string and query as the spec.  For example:
    'pgsql:user:passwd/127.0.0.1/mydb,select * from feeds'
    Each row in the query result becomes an event in the input.
    """
    def __init__(self, spec):
        # Defer import until we need it
        import psycopg2
        self.psycopg2 = psycopg2

        conn_str, self.query = spec.split(",", 1)
        # Massage the connection string
        m = CONN_STR.match(conn_str)
        if not m:
            raise ValueError("Unrecognized connection string format: '%s'" % conn_str)
        username, password, host, db = m.group(1), m.group(2), m.group(3), m.group(4)
        LOG.info("Connecting to %s@%s/%s" % (username, host, db))
        self.conn_str="host='%s' dbname='%s' user='%s' password='%s'" % (host, db, username, password)
        def do_connect():
            return self.do_connect()
        def do_close(conn):
            return self.do_close(conn)
        self.conn = utils.Connector(do_connect, do_close)
        self.conn.connect()

    def do_connect(self):
        conn = self.psycopg2.connect(self.conn_str)
        return conn

    def do_close(self, conn):
        conn.close()

    def __iter__(self):
        cursor = self.conn.conn.cursor()
        yielded = 0
        try:
            cursor.execute(self.query)
            keys = [d[0] for d in cursor.description]
            for r in cursor.fetchall():
                e = {}
                for i in range(0, len(keys)):
                    e[keys[i]] = r[i]
                yielded += 1
                yield e
        except Exception as err:
            #error, = exc.args
            #LOG.error("Postgresql-Error-Code:", err.code)
            LOG.error("Error-Message: %s", err.message)
        finally:
            self.conn.close()
        LOG.info("Postrgresql query yielded %s rows" % yielded)
