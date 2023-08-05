import logging
import g11pyutils as utils
LOG = logging.getLogger("split")


class Split(object):
    """Splits a named field using a delimiter, and then assigns splits
    to new fields using Python list syntax, as in:

    split:text,COMMA,dir=[0:-1],file=[-1]"""

    DELIMS = { "comma" : ','}
    @staticmethod
    def delim_for(s):
        return Split.DELIMS.get(s.lower(), s);

    def __init__(self, spec):
        args = spec.split(",", 2)
        self.field = args[0] # Field to split
        self.delim = Split.delim_for(args[1]) # Delimiter
        self.fields = utils.to_dict(args[2]) # Field assignments

    def filter(self, events):
        for e in events:
            prop = e.get(self.field)
            if prop:
                l = prop.split(self.delim)
                for k, v in self.fields.iteritems():
                    r = eval('l'+v)
                    if isinstance(r, list):
                        r = self.delim.join(r)
                    e[k] = r
            yield e

