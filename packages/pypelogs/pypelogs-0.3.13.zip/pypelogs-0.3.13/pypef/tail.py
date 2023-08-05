import logging
import g11pyutils as utils
LOG = logging.getLogger("tail")


class Tail(object):
    """Implements the equivalent of Unix 'tail' command.

    Use with n=(number of lines) to display the last 'n' events.
    Use with n=+(number of lines) to skip the first 'n' events but forward all others.
    """
    def __init__(self, spec=None, n=10):
        opts = utils.to_dict(spec)
        n_arg = opts["n"] if opts and opts.has_key("n") else n
        self.skip_mode = False
        if utils.is_str_type(n_arg):
            if n_arg[0] == '+':
                self.skip_mode = True
                n_arg = n_arg[1:]
        self.n = int(n_arg)
        if not self.skip_mode:
            self.buff = [None for i in range(0, self.n)]  # Event ring buffer

    def filter(self, events):
        count = 0
        if self.skip_mode:
            for e in events:
                if count >= self.n:
                    yield e
                count += 1
        else:
            for e in events:
                self.buff[count % self.n] = e
                count += 1
            for i in range(0, self.n):
                yield self.buff[(count + i) % self.n]



