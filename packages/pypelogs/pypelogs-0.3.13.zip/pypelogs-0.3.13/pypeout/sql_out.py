import g11pyutils as utils


class SQLOut(object):
    def __init__(self, spec=""):
        args = spec.split(",", 1)
        self.opts = {} if len(args) == 1 else utils.to_dict(args[1])
        self.fo = utils.fout(args[0], self.opts.get("enc"))

    @staticmethod
    def quote(s):
        s = s.replace("'", "\\'")
        return "'"+s+"'"

    def process(self, events):
        events = utils.HasNextIter(events)
        table = self.opts.get('table')
        if self.opts.get("truncate"):
            self.fo.write("TRUNCATE TABLE %s;\n" % table)

        first = True
        keys = None
        for e in events:
            if first:
                first = False
                keys = e.keys()
                if table:
                    self.fo.write("INSERT INTO %s(%s) VALUES\n" % (table, ",".join(keys)))
            self.fo.write("(")
            self.fo.write(",".join([SQLOut.quote(e[k]) for k in keys]))
            self.fo.write(")%s\n" % ("," if events.has_next() else ";" if table else ""))
            self.fo.flush()
