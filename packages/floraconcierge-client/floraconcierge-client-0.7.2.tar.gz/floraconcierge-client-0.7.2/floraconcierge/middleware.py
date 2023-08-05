from importlib import import_module
import sys

from django.conf import settings
from django.http import Http404
from django.utils import six

from floraconcierge import shortcuts
from floraconcierge.apiauth.models import User
from floraconcierge.cache import get_request_cache, new_request_cache
from floraconcierge.client import ApiClient
from floraconcierge.errors import ResultObjectNotFoundError, MiddlewareError


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.

    Helper function from django 1.7
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

    try:
        # noinspection PyUnboundLocalVariable
        module = import_module(module_path)
    except ImportError, e:
        six.reraise(ImportError, ImportError('%s. Tried to import %s' % (e.message, module_path)), sys.exc_info()[2])

    try:
        # noinspection PyUnboundLocalVariable
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            dotted_path, class_name)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])


def initialize_apiclient(request):
    err_pattern = 'floraconcierge.middleware.ApiClientMiddleware requires to be set settings.%s'

    api_id = getattr(settings, 'FLORACONCIERGE_API_ID', None)
    if not api_id:
        raise ValueError(err_pattern % 'FLORACONCIERGE_API_ID')

    secret = getattr(settings, 'FLORACONCIERGE_API_SECRET', None)
    if not secret:
        raise ValueError(err_pattern % 'FLORACONCIERGE_API_SECRET')

    client = ApiClient(api_id, secret)

    sess_env = request.session.get("__floraconcierge_api_env", None)
    restored = False
    if sess_env:
        client.env = sess_env
        restored = True

    init_env = getattr(settings, 'FLORACONCIERGE_API_INIT_ENV', None)
    if init_env:
        init_env = import_string(init_env)
        env = init_env(client, request, restored)
        if env:
            client.env = env

    return client


class ApiClientMiddleware(object):
    def process_request(self, request):
        init = getattr(settings, 'FLORACONCIERGE_API_INIT_CLIENT', None)
        if init:
            init = import_string(init)
            client = init(request)
        else:
            client = initialize_apiclient(request)

        request.api = client
        request.apienv = client.env

        shortcuts.activate(client)

    def process_response(self, request, response):
        if hasattr(request, 'apienv'):
            # Support api user authentication
            if isinstance(request.user, User) and request.user.info:
                request.apienv.user_auth_key = request.user.info.auth.auth_key
            else:
                request.apienv.user_auth_key = ''

            request.session['__floraconcierge_api_env'] = request.apienv

        return response


class ApiObjectNotFound404(object):
    def process_exception(self, request, exception):
        if isinstance(exception, ResultObjectNotFoundError):
            raise Http404


_cache_cls = None


class RequestCacheMiddleware(object):
    @staticmethod
    def cache_cls():
        global _cache_cls

        if not _cache_cls:
            cls = getattr(settings, 'FLORACONCIERGE_CACHE_CLASS', None)
            if not cls:
                raise MiddlewareError('Please define FLORACONCIERGE_CACHE_CLASS in settings for RequestCacheMiddleware')

            _cache_cls = import_string(cls)

        return _cache_cls

    def process_request(self, request):
        try:
            cache = get_request_cache()
        except MiddlewareError:
            cache = new_request_cache(self.cache_cls())

        cache.clear()
        request.cache = cache
