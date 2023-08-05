import hmac
import json
import hashlib
import socket
import ssl
import six
import time
import sys
from six.moves import http_client
from six.moves.urllib.parse import urlparse
from .util import AsyncnotiException


def _make_query_string(params):
    builds = list()
    all1 = sorted(params.items(), key=lambda x: x[0])

    for key in all1:
        if type(key[1]) in [list, tuple]:
            for v_key in key[1]:
                builds.append('%s[]=%s' % (key[0], v_key,))
        else:
            builds.append('%s=%s' % (key[0], key[1],))

    return '&'.join(builds)


class Asyncnoti(object):
    def __init__(self, app_key=None, app_secret=None, app_id=None, host=u'http://asyncnoti.com', port=None,
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        if not isinstance(app_key, six.text_type):
            raise TypeError("Key should be %s" % six.text_type)

        if not isinstance(app_secret, six.text_type):
            raise TypeError("Secret should be %s" % six.text_type)

        if not isinstance(app_id, six.text_type):
            raise TypeError("App ID should be %s" % six.text_type)

        if not isinstance(host, six.text_type):
            raise TypeError("Host should be %s" % host)

        if port and not isinstance(port, six.integer_types):
            raise TypeError("Port should be a number")

        o = urlparse(host)

        if not port:
            port = o.port

        self.app_key = app_key
        self.app_secret = app_secret
        self.app_id = app_id
        self.host = o.hostname
        self.port = port
        self.scheme = o.scheme
        self.timeout = timeout

    def trigger(self, channels, event_name, data=None):
        if not data: data = {}
        if type(channels) not in [list, tuple]:
            channels = (channels,)

        if not isinstance(event_name, six.text_type):
            raise TypeError("event_name must be %s" % six.text_type)

        if len(event_name) > 255:
            raise ValueError("event_name too long")

        for channel in channels:
            if not isinstance(channel, six.text_type):
                raise TypeError("Channel should be %s" % six.text_type)

            if len(channel) > 255:
                raise ValueError("Channel too long")

        data_json = json.dumps(data)

        return self._request('/api/v1/apps/%s/events' % self.app_id, 'POST',
                             {'data': data_json,
                              'data_hash': hashlib.sha256(data_json.encode('utf8')).hexdigest(),
                              'name': event_name,
                              'channels': channels,
                             })

    def _request(self, uri, method, params=None):
        params['auth_timestamp'] = '%.0f' % time.time()
        params['auth_key'] = self.app_key

        string_to_sign = '\n'.join([
            method.upper(),
            uri,
            _make_query_string(params)
        ])

        params['auth_signature'] = six.text_type(
            hmac.new(self.app_secret.encode('utf8'), string_to_sign.encode('utf8'), hashlib.sha256).hexdigest())

        status, raw_response = self._http_request(method, uri, params)

        if status >= 300 or status < 200:
            raise AsyncnotiException('Asyncnoti HTTP error %i' % status, status)

        return json.loads(raw_response)

    def _http_request(self, method, uri, request_params):
        if self.scheme == 'https':
            if sys.version_info < (3, 4):
                raise NotImplementedError("SSL requires python >= 3.4")

            ctx = ssl.create_default_context()
            self.http = http_client.HTTPSConnection(self.host, self.port, timeout=self.timeout, context=ctx)
        else:
            self.http = http_client.HTTPConnection(self.host, self.port, timeout=self.timeout)

        request_body = json.dumps(request_params)
        headers = {"Content-Type": "application/json"}

        try:
            self.http.request(method, uri, request_body, headers)
            resp = self.http.getresponse()
            raw_response = resp.read().decode('utf8')
        except http_client.HTTPException as e:
            raise Exception('HTTP client exception: %s' % repr(e))

        return resp.status, raw_response



