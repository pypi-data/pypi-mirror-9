"""
python-phabricator3

https://github.com/Konvexum/python-phabricator3

Code/Pull Requests from:
    vilhelmk
    lifeisstillgood
    marcqualie
"""

try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('phabricator').version
except:
    __version__ = 'unknown'

import copy
import hashlib
import json
import os
import re
import socket
import time
import requests
from urllib import parse

from collections import defaultdict

__all__ = ['Phabricator']

# Default phabricator interfaces
INTERFACES = json.loads(open(os.path.join(os.path.dirname(__file__), 'interfaces.json'), 'r').read())

# Load ~/.arcrc if it exists
try:
    ARCRC = json.loads(open(os.path.join(os.path.expanduser('~'),
                                         (os.path.join('AppData', 'Roaming') if os.name == 'nt' else ''),
                                         '.arcrc'), 'r').read())
except IOError:
    ARCRC = None

# Map Phabricator types to Python types
PARAM_TYPE_MAP = {
    # int types
    'int': int,
    'uint': int,
    'revisionid': int,
    'revision_id': int,
    'diffid': int,
    'diff_id': int,
    'id': int,

    # bool types
    'bool': bool,

    # dict types
    'map': dict,
    'dict': dict,

    # list types
    'list': list,

    # tuple types
    'pair': tuple,

    # str types
    'str': str,
    'string': str,
    'phid': str,
    'guids': str,
    'type': str,
    'enum': str,
}

STR_RE = re.compile(r'([a-zA-Z_]+)')


def map_param_type(param_type):
    """
    Perform param type mapping
    This requires a bit of logic since this isn't standardized.
    If a type doesn't map, assume str
    """
    m = STR_RE.match(param_type)
    main_type = m.group(0)

    if main_type in ('list', 'array'):
        info = param_type.replace(' ', '').split('<', 1)

        # Handle no sub-type: "required list"
        sub_type = info[1] if len(info) > 1 else 'str'

        # Handle list of pairs: "optional list<pair<callsign, path>>"
        sub_match = STR_RE.match(sub_type)
        sub_type = sub_match.group(0).lower()

        return [PARAM_TYPE_MAP.setdefault(sub_type, str)]

    return PARAM_TYPE_MAP.setdefault(main_type, str)


def parse_interfaces(interfaces):
    """
    Parse the conduit.query json dict response
    This performs the logic of parsing the non-standard params dict
        and then returning a dict Resource can understand
    """
    parsed_interfaces = defaultdict(dict)

    for m, d in interfaces.items():
        app, func = m.split('.', 1)

        method = parsed_interfaces[app][func] = {}

        # Make default assumptions since these aren't provided by Phab
        method['formats'] = ['json', 'human']
        method['method'] = 'POST'

        method['optional'] = {}
        method['required'] = {}

        for name, type_info in dict(d['params']).items():
            # Usually in the format: <optionality> <param_type>
            info_pieces = type_info.split(' ', 1)

            # If optionality isn't specified, assume required
            if info_pieces[0] not in ('optional', 'required'):
                optionality = 'required'
                param_type = info_pieces[0]
            # Just make an optional string for "ignored" params
            elif info_pieces[0] == 'ignored':
                optionality = 'optional'
                param_type = 'string'
            else:
                optionality = info_pieces[0]
                param_type = info_pieces[1]

            # This isn't validated by the client
            if param_type.startswith('nonempty'):
                optionality = 'required'
                param_type = param_type[9:]

            method[optionality][name] = map_param_type(param_type)

    return dict(parsed_interfaces)


class InterfaceNotDefined(NotImplementedError):
    pass


class APIError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '{}: {}'.format(self.code, self.message)


class InvalidAccessToken(APIError):
    pass


class Result(object):
    def __init__(self, response):
        self.response = response

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self.response))

    def __iter__(self):
        for r in self.response:
            yield r

    def __getitem__(self, key):
        return self.response[key]

    def __getattr__(self, key):
        return self.response[key]

    def __getstate__(self):
        return self.response

    def __setstate__(self, state):
        self.response = state

    def __len__(self):
        return len(self.response.keys())

    def keys(self):
        return self.response.keys()

    def iteritems(self):
        for k, v in self.response.items():
            yield k, v

    def itervalues(self):
        for v in self.response.values():
            yield v


class Resource(object):
    def __init__(self, api, interface=None, endpoint=None, method=None):
        self.api = api
        self.interface = interface or copy.deepcopy(parse_interfaces(INTERFACES))
        self.endpoint = endpoint
        self.method = method

    def __getattr__(self, attr):
        if attr in getattr(self, '__dict__'):
            return getattr(self, attr)
        interface = self.interface
        if attr not in interface:
            interface[attr] = {}
        return Resource(self.api, interface[attr], attr, self.endpoint)

    def __call__(self, **kwargs):
        return self._request(**kwargs)

    def _request(self, **kwargs):
        # Check for missing variables
        resource = self.interface

        def validate_kwarg(key, target):
            # Non empty is a special type
            if target == 'nonempty':
                if not key:
                    return False
                else:
                    return True

            # Always allow list
            if isinstance(key, list):
                return all([validate_kwarg(x, target[0]) for x in key])
            return isinstance(key, target)

        for k in resource.get('required', []):
            if k not in [x.split(':')[0] for x in kwargs.keys()]:
                raise ValueError('Missing required argument: {}'.format(k))
            if isinstance(kwargs.get(k), list) and not isinstance(resource['required'][k], list):
                raise ValueError('Wrong argument type: {} is not a list'.format(k))
            elif not validate_kwarg(kwargs.get(k), resource['required'][k]):
                if isinstance(resource['required'][k], list):
                    raise ValueError('Wrong arguemnt type: {} is not a list of {}'.format(k, resource['required'][k][0]))
                raise ValueError('Wrong arguemnt type: {} is not a {}'.format(k, resource['required'][k]))

        conduit = self.api._conduit

        if conduit:
            # Already authenticated, add session key to json data
            kwargs['__conduit__'] = conduit
        elif self.method == 'conduit' and self.endpoint == 'connect':
            # Not authenticated, requesting new session key
            token = str(int(time.time()))
            kwargs['authToken'] = token
            kwargs['authSignature'] = self.api.generate_hash(token)
        else:
            # Authorization is required, silently auth the user
            self.api.connect()
            kwargs['__conduit__'] = self.api._conduit

        response = requests.post('{}{}.{}'.format(self.api.host, self.method, self.endpoint), data={
            'params': json.dumps(kwargs),
            'output': self.api.response_format
        }, headers={
            'User-Agent': 'python-phabricator3/{}'.format(self.api.clientVersion),
            'Content-Type': 'application/x-www-form-urlencoded'
        })

        return Result(response.json()['result'])

    def _parse_response(self, data):
        # Process the response back to python
        parsed = self.api.formats[self.api.response_format](data)

        # Errors return 200, so check response content for exception
        if parsed['error_code']:
            raise APIError(parsed['error_code'], parsed['error_info'])

        return parsed


class Phabricator(Resource):
    formats = {
        'json': lambda x: json.loads(x),
    }

    def __init__(self, username=None, certificate=None, host=None,
                 timeout=5, response_format='json', **kwargs):

        # Set values in ~/.arcrc as defaults
        if ARCRC:
            self.host = host if host else list(ARCRC['hosts'].keys())[0]
            self.username = username if username else ARCRC['hosts'][self.host]['user']
            self.certificate = certificate if certificate else ARCRC['hosts'][self.host]['cert']
        else:
            self.host = host
            self.username = username
            self.certificate = certificate

        self.timeout = timeout
        self.response_format = response_format
        self.client = 'python-phabricator'
        self.clientVersion = 1
        self.clientDescription = socket.gethostname() + ':python-phabricator3'
        self._conduit = None

        super(Phabricator, self).__init__(self)

    def _request(self, **kwargs):
        raise SyntaxError('You cannot call the Conduit API without a resource.')

    def connect(self):
        auth = Resource(api=self, method='conduit', endpoint='connect')

        response = auth(user=self.username, host=self.host,
                        client=self.client, clientVersion=self.clientVersion)

        self._conduit = {
            'sessionKey': response.sessionKey,
            'connectionID': response.connectionID
        }

    def generate_hash(self, token):
        return hashlib.sha1((token + self.api.certificate).encode('utf-8')).hexdigest()

    def update_interfaces(self):
        query = Resource(api=self, method='conduit', endpoint='query')

        interfaces = query()

        self.interface = parse_interfaces(interfaces)
