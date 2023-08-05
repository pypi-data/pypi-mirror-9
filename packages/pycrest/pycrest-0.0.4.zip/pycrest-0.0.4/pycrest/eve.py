import os
import base64
import requests
import time
import zlib
from pycrest import version
from pycrest.compat import bytes_, text_
from pycrest.errors import APIException
from pycrest.weak_ciphers import WeakCiphersAdapter

try:
    from urllib.parse import urlparse, urlunparse, parse_qsl
except ImportError:  # pragma: no cover
    from urlparse import urlparse, urlunparse, parse_qsl

try:
    import pickle
except ImportError:  # pragma: no cover
    import cPickle as pickle

try:
    from urllib.parse import quote
except ImportError:  # pragma: no cover
    from urllib import quote
import logging
import re

logger = logging.getLogger("pycrest.eve")
cache_re = re.compile(r'max-age=([0-9]+)')


class APICache(object):
    def put(self, key, value):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def invalidate(self, key):
        raise NotImplementedError


class FileCache(APICache):
    def __init__(self, path):
        self._cache = {}
        self.path = path
        if not os.path.isdir(self.path):
            os.mkdir(self.path, 0o700)

    def _getpath(self, key):
        return os.path.join(self.path, str(hash(key)) + '.cache')

    def put(self, key, value):
        with open(self._getpath(key), 'wb') as f:
            f.write(zlib.compress(pickle.dumps(value, -1)))
        self._cache[key] = value

    def get(self, key):
        if key in self._cache:
            return self._cache[key]

        try:
            with open(self._getpath(key), 'rb') as f:
                return pickle.loads(zlib.decompress(f.read()))
        except IOError as ex:
            if ex.errno == 2:  # file does not exist (yet)
                return None
            else:
                raise

    def invalidate(self, key):
        self._cache.pop(key, None)

        try:
            os.unlink(self._getpath(key))
        except OSError as ex:
            if ex.errno == 2:  # does not exist
                pass
            else:
                raise


class DictCache(APICache):
    def __init__(self):
        self._dict = {}

    def get(self, key):
        return self._dict.get(key, None)

    def put(self, key, value):
        self._dict[key] = value

    def invalidate(self, key):
        self._dict.pop(key, None)


class APIConnection(object):
    def __init__(self, additional_headers=None, user_agent=None, cache_dir=None):
        # Set up a Requests Session
        session = requests.Session()
        if additional_headers is None:
            additional_headers = {}
        if user_agent is None:
            user_agent = "PyCrest/{0}".format(version)
        session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json",
        })
        session.headers.update(additional_headers)
        session.mount('https://public-crest.eveonline.com',
                WeakCiphersAdapter())
        self._session = session
        self.cache_dir = cache_dir
        if self.cache_dir:
            self.cache = FileCache(self.cache_dir)
        else:
            self.cache = DictCache()

    def get(self, resource, params=None):
        logger.debug('Getting resource %s', resource)
        if params is None:
            params = {}

        # remove params from resource URI (needed for paginated stuff)
        parsed_uri = urlparse(resource)
        qs = parsed_uri.query
        resource = urlunparse(parsed_uri._replace(query=''))
        prms = {}
        for tup in parse_qsl(qs):
            prms[tup[0]] = tup[1]

        # params supplied to self.get() override parsed params
        for key in params:
            prms[key] = params[key]

        # check cache
        key = (resource, frozenset(self._session.headers.items()), frozenset(prms.items()))
        cached = self.cache.get(key)
        if cached and cached['expires'] > time.time():
            logger.debug('Cache hit for resource %s (params=%s)', resource, prms)
            return cached['payload']
        elif cached:
            logger.debug('Cache stale for resource %s (params=%s)', resource, prms)
            self.cache.invalidate(key)
        else:
            logger.debug('Cache miss for resource %s (params=%s', resource, prms)

        logger.debug('Getting resource %s (params=%s)', resource, prms)
        res = self._session.get(resource, params=prms)
        if res.status_code != 200:
            raise APIException("Got unexpected status code from server: %i" % res.status_code)

        ret = res.json()

        # cache result
        key = (resource, frozenset(self._session.headers.items()), frozenset(prms.items()))
        expires = self._get_expires(res)
        if expires > 0:
            self.cache.put(key, {'expires': time.time() + expires, 'payload': ret})

        return ret

    def _get_expires(self, response):
        if 'Cache-Control' not in response.headers:
            return 0
        if any([s in response.headers['Cache-Control'] for s in ['no-cache', 'no-store']]):
            return 0
        match = cache_re.search(response.headers['Cache-Control'])
        if match:
            return int(match.group(1))
        return 0


class EVE(APIConnection):
    def __init__(self, **kwargs):
        self.api_key = kwargs.pop('api_key', None)
        self.client_id = kwargs.pop('client_id', None)
        self.redirect_uri = kwargs.pop('redirect_uri', None)
        if kwargs.pop('testing', False):
            self._public_endpoint = "http://public-crest-sisi.testeveonline.com/"
            self._authed_endpoint = "https://api-sisi.testeveonline.com/"
            self._image_server = "https://image.testeveonline.com/"
            self._oauth_endpoint = "https://sisilogin.testeveonline.com/oauth"
        else:
            self._public_endpoint = "https://public-crest.eveonline.com/"
            self._authed_endpoint = "https://crest-tq.eveonline.com/"
            self._image_server = "https://image.eveonline.com/"
            self._oauth_endpoint = "https://login.eveonline.com/oauth"
        self._endpoint = self._public_endpoint
        self._cache = {}
        self._data = None
        APIConnection.__init__(self, cache_dir=kwargs.pop('cache_dir', None), **kwargs)

    def __call__(self):
        if not self._data:
            self._data = APIObject(self.get(self._endpoint), self)
        return self._data

    def __getattr__(self, item):
        return self._data.__getattr__(item)

    def auth_uri(self, scopes=None, state=None):
        s = [] if not scopes else scopes
        return "%s/authorize?response_type=code&redirect_uri=%s&client_id=%s%s%s" % (
            self._oauth_endpoint,
            quote(self.redirect_uri, safe=''),
            self.client_id,
            "&scope=%s" % ','.join(s) if scopes else '',
            "&state=%s" % state if state else ''
        )

    def _authorize(self, params):
        auth = text_(base64.b64encode(bytes_("%s:%s" % (self.client_id, self.api_key))))
        headers = {"Authorization": "Basic %s" % auth}
        res = self._session.post("%s/token" % self._oauth_endpoint, params=params, headers=headers)
        if res.status_code != 200:
            raise APIException("Got unexpected status code from API: %i" % res.status_code)
        return res.json()

    def authorize(self, code):
        res = self._authorize(params={"grant_type": "authorization_code", "code": code})
        return AuthedConnection(res,
                                self._authed_endpoint,
                                self._oauth_endpoint,
                                self.client_id,
                                self.api_key,
                                cache_dir=self.cache_dir)

    def refr_authorize(self, refresh_token):
        res = self._authorize(params={"grant_type": "refresh_token", "refresh_token": refresh_token})
        return AuthedConnection({'access_token': res['access_token'],
                                 'refresh_token': refresh_token,
                                 'expires_in': res['expires_in']},
                                self._authed_endpoint,
                                self._oauth_endpoint,
                                self.client_id,
                                self.api_key,
                                cache_dir=self.cache_dir)

    def temptoken_authorize(self, access_token, expires_in, refresh_token):
        return AuthedConnection({'access_token': access_token,
                                 'refresh_token': refresh_token,
                                 'expires_in': expires_in},
                                self._authed_endpoint,
                                self._oauth_endpoint,
                                self.client_id,
                                self.api_key,
                                cache_dir=self.cache_dir)


class AuthedConnection(EVE):
    def __init__(self, res, endpoint, oauth_endpoint, client_id=None, api_key=None, **kwargs):
        EVE.__init__(self, **kwargs)
        self.client_id = client_id
        self.api_key = api_key
        self.token = res['access_token']
        self.refresh_token = res['refresh_token']
        self.expires = int(time.time()) + res['expires_in']
        self._oauth_endpoint = oauth_endpoint
        self._endpoint = endpoint
        self._session.headers.update({"Authorization": "Bearer %s" % self.token})

    def __call__(self):
        if not self._data:
            if int(time.time()) >= self.expires:
                self.refresh()
            self._data = APIObject(self.get(self._endpoint), self)
        return self._data

    def whoami(self):
        if 'whoami' not in self._cache:
            self._cache['whoami'] = self.get("https://login.eveonline.com/oauth/verify")
        return self._cache['whoami']

    def refresh(self):
        res = self._authorize(params={"grant_type": "refresh_token", "refresh_token": self.refresh_token})
        self.token = res['access_token']
        self.expires = int(time.time()) + res['expires_in']
        self._session.headers.update({"Authorization": "Bearer %s" % self.token})
        return self  # for backwards compatibility


class APIObject(object):
    def __init__(self, parent, connection):
        self._dict = {}
        self.connection = connection
        for k, v in parent.items():
            if type(v) is dict:
                self._dict[k] = APIObject(v, connection)
            elif type(v) is list:
                self._dict[k] = self._wrap_list(v)
            else:
                self._dict[k] = v

    def _wrap_list(self, list_):
        new = []
        for item in list_:
            if type(item) is dict:
                new.append(APIObject(item, self.connection))
            elif type(item) is list:
                new.append(self._wrap_list(item))
            else:
                new.append(item)
        return new

    def __getattr__(self, item):
        return self._dict[item]

    def __call__(self, **kwargs):
        # Caching is now handled by APIConnection
        if 'href' in self._dict:
            return APIObject(self.connection.get(self._dict['href'], params=kwargs), self.connection)
        else:
            return self

    def __str__(self):  # pragma: no cover
        return self._dict.__str__()

    def __repr__(self):  # pragma: no cover
        return self._dict.__repr__()
