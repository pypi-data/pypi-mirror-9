from . import session
from . import resources
from . import error
from .page_iterator import CollectionPageIterator

from types import ModuleType
from numbers import Number
import requests
import json
import time

RESOURCE_CLASSES = {}
for name, module in resources.__dict__.items():
    if isinstance(module, ModuleType) and name.capitalize() in module.__dict__:
        RESOURCE_CLASSES[name] = module.__dict__[name.capitalize()]

STATUS_MAP = {}
for name, Klass in error.__dict__.items():
    if isinstance(Klass, type) and issubclass(Klass, error.AsanaError):
        STATUS_MAP[Klass().status] = Klass

class Client:

    RETRY_DELAY = 1.0
    RETRY_BACKOFF = 2.0

    DEFAULTS = {
        'base_url': 'https://app.asana.com/api/1.0',
        'item_limit': None,
        'page_size': 50,
        'poll_interval': 5,
        'max_retries': 5,
        'full_payload': False,
        'iterator_type': 'items'
    }

    CLIENT_OPTIONS  = set(DEFAULTS.keys())
    QUERY_OPTIONS   = set(['limit', 'offset', 'sync'])
    REQUEST_OPTIONS = set(['headers', 'params', 'data'])
    API_OPTIONS     = set(['pretty', 'fields', 'expand'])

    ALL_OPTIONS     = CLIENT_OPTIONS | QUERY_OPTIONS | REQUEST_OPTIONS | API_OPTIONS

    def __init__(self, session=None, auth=None, **options):
        self.session = session or requests.Session()
        self.auth = auth
        self.options = _merge(self.DEFAULTS, options)
        for name, Klass in RESOURCE_CLASSES.items():
            setattr(self, name, Klass(self))

    def request(self, method, path, **options):
        options = self._merge_options(options)
        url = options['base_url'] + path
        retry_count = 0
        request_options = self._parse_request_options(options)
        while True:
            try:
                response = getattr(self.session, method)(url, auth=self.auth, **request_options)
                if response.status_code in STATUS_MAP:
                    raise STATUS_MAP[response.status_code](response)
                else:
                    if options['full_payload']:
                        return response.json()
                    else:
                        return response.json()['data']
            except error.RetryableAsanaError as e:
                if retry_count < options['max_retries']:
                    self.handle_retryable_error(e, retry_count)
                    retry_count += 1
                else:
                    raise e

    def handle_retryable_error(self, e, retry_count):
        if isinstance(e, error.RateLimitEnforcedError):
            time.sleep(e.retry_after)
        else:
            time.sleep(self.RETRY_DELAY * (self.RETRY_BACKOFF ** retry_count))

    def get(self, path, query, **options):
        api_options = self._parse_api_options(options, query_string=True)
        query_options = self._parse_query_options(options)
        parameter_options = self._parse_parameter_options(options)
        query = _merge(query_options, api_options, parameter_options, query) # options in the query takes precendence
        return self.request('get', path, params=query, **options)

    def get_collection(self, path, query, **options):
        options = self._merge_options(options)
        if options['iterator_type'] == 'items':
            return CollectionPageIterator(self, path, query, options).items()
        if options['iterator_type'] == None:
            return self.get(path, query, **options)
        raise Exception('Unknown value for "iterator_type" option: ' + str(options['iterator_type']))

    def post(self, path, data, **options):
        parameter_options = self._parse_parameter_options(options)
        body = {
            'data': _merge(parameter_options, data), # values in the data body takes precendence
            'options': self._parse_api_options(options)
        }
        return self.request('post', path, data=body, headers={'content-type': 'application/json'}, **options)

    def put(self, path, data, **options):
        parameter_options = self._parse_parameter_options(options)
        body = {
            'data': _merge(parameter_options, data), # values in the data body takes precendence
            'options': self._parse_api_options(options)
        }
        return self.request('put', path, data=body, headers={'content-type': 'application/json'}, **options)

    def delete(self, path, data, **options):
        return self.request('delete', path, **options)

    def _merge_options(self, *objects):
        return _merge(self.options, *objects)

    def _parse_query_options(self, options):
        return self._select_options(options, self.QUERY_OPTIONS)

    def _parse_parameter_options(self, options):
        return self._select_options(options, self.ALL_OPTIONS, invert=True)

    def _parse_api_options(self, options, query_string=False):
        api_options = self._select_options(options, self.API_OPTIONS)
        if query_string:
            query_api_options = {}
            for key in api_options:
                if isinstance(api_options[key], (list, tuple)):
                    query_api_options['opt_'+key] = ','.join(api_options[key])
                else:
                    query_api_options['opt_'+key] = api_options[key]
            return query_api_options
        else:
            return api_options

    def _parse_request_options(self, options):
        request_options = self._select_options(options, self.REQUEST_OPTIONS)
        if 'params' in request_options:
            params = request_options['params']
            for key in params:
                if isinstance(params[key], bool):
                    params[key] = json.dumps(params[key])
        if 'data' in request_options:
            # remove empty 'options':
            if 'options' in request_options['data'] and len(request_options['data']['options']) == 0:
                del request_options['data']['options']
            # serialize 'data' to JSON, requests doesn't do this automatically:
            request_options['data'] = json.dumps(request_options['data'])
        return request_options

    def _select_options(self, options, keys, invert=False):
        options = self._merge_options(options)
        result = {}
        for key in options:
            if (invert and key not in keys) or (not invert and key in keys):
                result[key] = options[key]
        return result

    @classmethod
    def basic_auth(Klass, apiKey):
        return Klass(auth=requests.auth.HTTPBasicAuth(apiKey, ''))

    @classmethod
    def oauth(Klass, **kwargs):
        return Klass(session.AsanaOAuth2Session(**kwargs))

def _merge(*objects):
    result = {}
    [result.update(obj) for obj in objects]
    return result
