import os
import requests
import logging

LOG = logging.getLogger(os.path.basename(__file__))


class HTTP(object):
    """Fetches Web URLs to a directory, where the URL is pulled from one of the event fields.

    example:

    python pypelogs.py flickr:/cygdrive/c/git/GPSPressServer/data/flickr.creds \
    'exec:e["url"]="https://farm%s.staticflickr.com/%s/%s_%s_b.jpg"%(e["farm"],e["server"],e["id"],e["secret"])' \
    keep:url http:./flickr/photos
    """

    def __init__(self, spec=None):
        """
        Creates a http output. Spec is of the form "output_dir,url_key", where output_dir is where
        files will be written, and url_key is the field name for each event that contains the URL to fetch.

        If url_key is not provided, then "url" is the expected key.
        If output_dir is not provided, then the current directory is used as output
        """
        args = spec.split(',', 1) if spec else []
        if not args:
            self.dir = os.curdir
        else:
            self.dir = os.path.abspath(args[0])
            if not os.path.isdir(self.dir):
                if os.path.exists(self.dir):
                    raise ValueError("%s is not a directory" % args[0])
                else:
                    LOG.info("Creating directory %s" % self.dir)
                    os.makedirs(self.dir)
        if len(args) > 1:
            self.key = args[1]
        else:
            self.key = 'url'

    def process(self, events):
        for e in events:
            url = e[self.key]
            fname = url.rsplit('/', 1)[-1]
            outpath = os.path.join(self.dir, fname)
            LOG.info("Fetching %s to %s" % (url, outpath))
            try:
                r = requests.get(url, stream=True)
                if r.status_code == 200:
                    with open(outpath, 'wb') as fo:
                        for chunk in r.iter_content(1024):
                            fo.write(chunk)
            except Exception as ex:
                LOG.warn("Failed to fetch %s: %s" % (url, ex))
