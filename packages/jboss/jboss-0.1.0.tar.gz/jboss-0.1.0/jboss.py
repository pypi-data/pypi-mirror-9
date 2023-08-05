""" JBoss API client. """

# Package information
# ===================
import json
import logging
from contextlib import contextmanager
from functools import wraps

import requests as rs
import requests_cache as rc


__version__ = "0.1.0"
__project__ = "jboss"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


logger = logging.getLogger(__name__)
rs_logger = logging.getLogger('requests')

if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


def _curry_method(method, *cargs, **ckwargs):
    """ Curry an object method. """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        args = cargs + args
        kwargs.update(ckwargs)
        return method(self, *args, **kwargs)

    return wrapper


class APIException(Exception):

    """ Implement an exception in API processing. """

    pass


class APIDescriptor(object):

    """ Proxy the API methods. """

    __methods = 'get', 'post', 'put', 'patch', 'delete', 'head'

    def __init__(self, client):
        """ Initialize the descriptor. """
        self.__client = client
        self.__method = 'GET'
        self.__session = []

    def __getattr__(self, method):
        """ Store the queried method to current session. """
        method = str(method)
        if method.lower() in self.__methods:
            self.__method = method.upper()
        else:
            self.__session.append(method)
        return self

    __getitem__ = __getattr__

    @property
    def __url(self):
        """ Return current uri. """
        return "/".join(self.__session)

    def __str__(self):
        """ Represent the descriptor as string. """
        return "%s %s" % (self.__method, self.__url)

    def __repr__(self):
        """ Represent the descriptor as string. """
        return 'API %s' % self

    def __call__(self, **data):
        """ Make request to JBoss API. """
        kwargs = dict(data=data)
        if self.__method.lower() == 'get':
            data = dict(
                (k, v if not isinstance(v, (list, tuple)) else ','.join(v))
                for (k, v) in data.items())
            kwargs = dict(params=data)

        return self.__client.request(self.__method, self.__url, **kwargs)


class APIClient(object):

    """ Client for JBoss API. """

    exception = APIException

    default_options = dict(
        accept='application/json',
        api_root='https://localhost/jbpm-console/rest',
        authorization=None,
        cache=None,
        loglevel='info',
        user_agent='JBOSS-Client v.%s' % __version__,
    )

    def __init__(self, **options):
        """ Initialize the options. """
        self.options = dict(self.default_options)
        self.options.update(options)

    @property
    def headers(self):
        """ Get default request headers. """
        _headers = {
            'Accept': self.options['accept'],
            'User-Agent': self.options['user_agent'],
            'Content-type': 'application/json',
        }
        if self.options.get('authorization'):
            _headers['Authorization'] = self.options['authorization']
        return _headers

    def request(self, method, url, params=None, headers=None, to_json=True, data=None, **kwargs):
        """ Make request to JBoss API. """
        loglevel = self.options.get('loglevel', 'info')
        logger.setLevel(loglevel.upper())
        rs_logger.setLevel(loglevel.upper())
        logger.debug("Params: %s", params)
        logger.debug("Data: %s", data)

        # Instal cache if the option is defined
        if self.options['cache']:
            rc.install_cache(self.options['cache'])

        url = '%s/%s' % (self.options['api_root'], url.strip('/'))

        _headers = self.headers
        _headers.update(headers or {})

        logger.debug("Headers: %s", _headers)

        if data:
            data = json.dumps(data)

        try:
            response = rs.api.request(
                method, url, params=params, headers=_headers, data=data, **kwargs)
            logger.debug(response.content)
            response.raise_for_status()
            if to_json:
                response = response.json()

        except (ValueError, rs.HTTPError, rs.ConnectionError) as exc:
            if locals().get('response') is not None:
                message = "%s: %s" % (response.status_code, response.content)
                raise APIException(message)
            raise APIException(exc)

        # Uninstall cache
        if self.options['cache']:
            rc.uninstall_cache()

        return response

    get = _curry_method(request, 'GET')
    post = _curry_method(request, 'POST')
    put = _curry_method(request, 'PUT')
    head = _curry_method(request, 'HEAD')
    patch = _curry_method(request, 'PATCH')
    delete = _curry_method(request, 'DELETE')

    @contextmanager
    def ctx(self, **options):
        """ Redefine context. """
        _opts = dict(self.options)
        try:
            self.options.update(options)
            yield self
        finally:
            self.options = _opts
            if not self.options['cache'] and type(self).cache_installed:
                rc.uninstall_cache()

    @property
    def api(self):
        """ Create API Descriptor. """
        return APIDescriptor(self)
