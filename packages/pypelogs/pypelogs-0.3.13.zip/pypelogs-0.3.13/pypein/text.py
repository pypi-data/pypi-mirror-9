import g11pyutils as utils
class Text(object):
    def __init__(self, f=None):
        self.fo = utils.fopen(f)

    def __iter__(self):
        for line in self.fo:
            yield { "text" : line.strip() }