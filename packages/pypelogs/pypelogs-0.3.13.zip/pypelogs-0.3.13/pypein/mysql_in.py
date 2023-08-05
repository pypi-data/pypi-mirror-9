import g11pyutils as utils
import logging
import re

LOG = logging.getLogger("MySQLIn")
CONN_STR = re.compile(r'(\w+):(.+)@([^/]+)/([\w_]+)')


class MySQLIn(object):
    """
    Input from a MySQL database, taking a connection string and query as the spec.  For example:
    'mysql:user:passwd@127.0.0.1/mydb,select * from feeds'
    Each row in the query result becomes an event in the input.

    Requires the Oracle Python connector for MySQL: http://dev.mysql.com/downloads/connector/python/
    """
    def __init__(self, spec):
        # Defer import until we need it
        import mysql.connector
        self.mysql = mysql.connector

        conn_str, self.query = spec.split(",", 1)
        # Massage the connection string
        m = CONN_STR.match(conn_str)
        if not m:
            raise ValueError("Unrecognized connection string format: '%s'" % conn_str)
        username, password, host, db = m.group(1), m.group(2), m.group(3), m.group(4)
        n = host.find(':')
        if n >= 0:
            port = host[n+1:]
            host = host[0:n]
        else:
            port = 3306
        if len(host) == 0:
            host = '127.0.0.1'

        LOG.info("Connecting to %s@%s/%s" % (username, host, db))
        self.user = username
        self.password = password
        self.host = host
        self.port = port
        self.database = db

        def do_connect():
            return self.do_connect()

        def do_close(conn):
            return self.do_close(conn)
        self.conn = utils.Connector(do_connect, do_close)
        self.conn.connect()

    def do_connect(self):
        conn = self.mysql.connect(user=self.user, password=self.password,
                              host=self.host, port=self.port,
                              database=self.database)
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
            LOG.error("Error-Message: %s", err.message)
        finally:
            self.conn.close()
        LOG.info("MySQL query yielded %s rows" % yielded)
