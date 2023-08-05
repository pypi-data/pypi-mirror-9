import logging
import json
import datetime

LOG = logging.getLogger("Flickr")


class Flickr(object):
    """
    Input from the Flickr API.  Uses the flickrapi package from PIP ( http://stuvel.eu/flickrapi )

    Usage:
        flickr:credsfile,command,args

    The credsfile is a JSON credentials file containing the Flickr API key and secret:
    {
    'api_key': '....',
    'api_secret': '....'
    }

    Supported commands are:
        interesting
        photo,(id)
        search,arg1=val1,arg2=val2...

    """
    def __init__(self, spec):
        # Defer import until we need it
        try:
            import flickrapi
            tokens = spec.split(',')
            creds_fname = tokens[0]
            if len(tokens) > 1:
                self.cmd = tokens[1]
            else:
                raise ValueError("Spec must inlude a command.")
            self.args = tokens[2:] if len(tokens) > 2 else []
            # Parse creds file
            with open(creds_fname, "r") as fo:
                creds = eval(fo.read())
            LOG.info("Using creds: %s" % creds)
            self.flickr = flickrapi.FlickrAPI(creds['api_key'], creds['api_secret'], format='json')
        except ImportError as ex:
            LOG.error("Use of this input requires installing the flickrapi module ('pip install flickrapi')")
            raise ex

    def __iter__(self):
        try:
            yielded = 0
            rsp = getattr(self, self.cmd)(self.args)
            for e in rsp:
                yielded += 1
                yield e
            LOG.info("Method '%s' yielded %s rows" % (self.cmd, yielded))
        except Exception as err:
            LOG.exception(err)

    def photo(self, args):
        """
        Retrieves metadata for a specific photo.

        flickr:(credsfile),photo,(photo_id)
        """
        rsp = self._load_rsp(self.flickr.photos_getInfo(photo_id=args[0]))
        p = rsp['photo']
        yield self._prep(p)

    def search(self, args):
        """
        Executes a search

        flickr:(credsfile),search,(arg1)=(val1),(arg2)=(val2)...
        """
        kwargs = {}
        for a in args:
            k, v = a.split('=')
            kwargs[k] = v
        return self._paged_api_call(self.flickr.photos_search, kwargs)

    def interesting(self, args=None):
        """
        Gets interesting photos.

        flickr:(credsfile),interesting

        """
        kwargs = {'extras':  ','.join(args) if args else 'last_update,geo,owner_name,url_sq'}
        return self._paged_api_call(self.flickr.interestingness_getList, kwargs)

    def search_groups(self, args):
        """
        Executes a search

        flickr:(credsfile),search,(arg1)=(val1),(arg2)=(val2)...
        """
        kwargs = {'text': args[0]}
        return self._paged_api_call(self.flickr.groups_search, kwargs, 'group')

    def group(self, args):
        """
        Executes a search

        flickr:(credsfile),search,(arg1)=(val1),(arg2)=(val2)...
        """
        kwargs = {'group_id': args[0]}
        return self._paged_api_call(self.flickr.groups_pools_getPhotos, kwargs)

    def _paged_api_call(self, func, kwargs, item_type='photo'):
        """
        Takes a Flickr API function object and dict of keyword args and calls the
        API call repeatedly with an incrementing page value until all contents are exhausted.
        Flickr seems to limit to about 500 items.
        """
        page = 1
        while True:
            LOG.info("Fetching page %s" % page)
            kwargs['page'] = page
            rsp = self._load_rsp(func(**kwargs))
            if rsp["stat"] == "ok":
                plural = item_type + 's'
                if plural in rsp:
                    items = rsp[plural]
                    if int(items["page"]) < page:
                        LOG.info("End of Flickr pages (%s pages with %s per page)" % (items["pages"], items["perpage"]))
                        break
                    for i in items[item_type]:
                        yield self._prep(i)
                else:
                    yield rsp
                page += 1
            else:
                yield [rsp]
                break

    @staticmethod
    def _prep(e):
        """
        Normalizes lastupdate to a timestamp, and constructs a URL from the embedded attributes.
        """
        if 'lastupdate' in e:
            e['lastupdate'] = datetime.datetime.fromtimestamp(int(e['lastupdate']))
        for k in ['farm', 'server', 'id', 'secret']:
            if not k in e:
                return e
        e["url"] = "https://farm%s.staticflickr.com/%s/%s_%s_b.jpg" % (e["farm"], e["server"], e["id"], e["secret"])
        return e

    @staticmethod
    def _load_rsp(rsp):
        """
        Converts raw Flickr string response to Python dict
        """
        first = rsp.find('(') + 1
        last = rsp.rfind(')')
        return json.loads(rsp[first:last])
