import g11pyutils as utils
import logging

LOG = logging.getLogger("Oracle")

CX_ORACLE_ERROR = None
try:
    import cx_Oracle
except ImportError as ex:
    CX_ORACLE_ERROR = ex

class Oracle(object):
    def __init__(self, spec):
        if CX_ORACLE_ERROR:
            raise CX_ORACLE_ERROR
        self.conn_str, self.query = spec.split(",")
        def do_connect():
            return self.do_connect()
        def do_close(conn):
            return self.do_close(conn)
        self.conn = utils.Connector(do_connect, do_close)
        self.conn.connect()

    def do_connect(self):
        ora_client = cx_Oracle.connect(self.conn_str)
        return ora_client

    def do_close(self, conn):
        conn.close()

    def __iter__(self):
        cursor = self.conn.conn.cursor()
        try:
            cursor.execute(self.query)
            keys = [d[0] for d in cursor.description]
            for r in cursor.fetchall():
                e = {}
                for i in range(0, len(keys)):
                    e[keys[i]] = r[i]
                yield e
        except cx_Oracle.DatabaseError as exc:
            error, = exc.args
            LOG.error("Oracle-Error-Code:", error.code)
            LOG.error("Oracle-Error-Message:", error.message)
        finally:
            self.conn.close()