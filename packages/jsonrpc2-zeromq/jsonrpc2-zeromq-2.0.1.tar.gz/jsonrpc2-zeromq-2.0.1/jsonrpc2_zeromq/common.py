# Part of the jsonrpc2-zeromq-python project.
# (c) 2012 Dan Brown, All Rights Reserved.
# Please see the LICENSE file in the root of this project for license
# information.

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
from future.utils import with_metaclass, native_str_to_bytes, \
    bytes_to_native_str
standard_library.install_aliases()
from builtins import *  # NOQA

import uuid
import json
import re
import logging
import pprint

import zmq


JSON_RPC_VERSION = '2.0'

DEBUG_LOG_OBJECT_INDENT_LEN = 4


package_logger = logging.getLogger('jsonrpc2_zeromq')
package_logger.addHandler(logging.NullHandler())


debug_log_object_indent = ' ' * DEBUG_LOG_OBJECT_INDENT_LEN


def debug_log_object_dump(obj):
    return re.sub(r'(^|\n)', r'\1' + debug_log_object_indent,
                  pprint.pformat(obj,
                                 width=(80 - DEBUG_LOG_OBJECT_INDENT_LEN)))


def _json_default(o):
    if hasattr(o, 'to_dict'):
        return o.to_dict()
    elif hasattr(o, 'isoformat'):
        # Yes, UTC support only for now.
        return o.replace(microsecond=0).isoformat() + 'Z'
    else:
        raise TypeError


def _parse_rpc_message(msg):
    msg_fields = frozenset(list(msg.keys()))
    if msg_fields.issuperset(frozenset(['jsonrpc', 'method'])):
        return Request(msg['method'], msg.get('params', None),
                       id_=msg.get('id', None))
    elif msg_fields.issuperset(frozenset(['jsonrpc', 'id'])) and \
            ('result' in msg_fields or 'error' in msg_fields):
        return Response(msg.get('result', None), msg.get('error', None),
                        msg['id'])
    else:
        return msg


def json_rpc_dumps(o):
    return native_str_to_bytes(json.dumps(o, default=_json_default,
                                          ensure_ascii=True))


def json_rpc_loads(s):
    return json.loads(bytes_to_native_str(s), object_hook=_parse_rpc_message)


_GenerateID = object()


class Request(object):

    def __init__(self, method, params, id_=_GenerateID, notify=False):
        self.method = method
        self.params = params
        if notify:
            self.id = None
        elif id_ == _GenerateID:
            self.id = str(uuid.uuid4())
        else:
            self.id = id_

    @property
    def is_method(self):
        return self.id is not None

    @property
    def is_notification(self):
        return self.id is None

    def to_dict(self):
        data = dict(jsonrpc=JSON_RPC_VERSION,
                    method=self.method,
                    params=self.params)
        if self.id:
            data['id'] = self.id
        return data

    @property
    def method_normalised(self):
        return self.method.lower().replace('-', '_')


class Notification(Request):

    def __init__(self, method, params):
        super(Notification, self).__init__(method, params, id_=None)


class RequestMethod(object):

    def __init__(self, method, client, notify=False):
        self.method = method
        self.client = client
        self.notify = notify

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise ValueError("Cannot be called with both positional and named "
                             "arguments")
        return self.client.request(Request(self.method, args or kwargs,
                                           notify=self.notify))


def handle_request(handler_obj, handler_attr_format, request):
    handler_name = handler_attr_format.format(method=request.method_normalised)
    try:
        handler = handler_obj.__getattribute__(handler_name)
    except AttributeError:
        raise MethodNotFound()

    try:
        if isinstance(request.params, (tuple, list)):
            result = handler(*request.params)
        elif isinstance(request.params, dict):
            result = handler(**request.params)
        else:
            raise InternalError('Parameters supplied as unexpected type')
    except TypeError as e:
        raise InvalidParams(str(e))

    return result


class Response(object):

    def __init__(self, result, error, id_):
        self.result = result
        self.error = error
        self.id = id_

    @property
    def is_error(self):
        return self.error is not None

    def error_exception(self, extra_code_mapping=None):
        cls = rpc_exception_class_for_code(self.error['code'],
                                           extra_code_mapping)
        return cls(self.error['message'], self.error.get('data', None))

    def to_dict(self):
        data = dict(jsonrpc=JSON_RPC_VERSION,
                    result=self.result,
                    error=self.error,
                    id=self.id)
        return {k: v for k, v in list(data.items()) if k == 'result' or
                v is not None}


class RPCErrorMeta(type):

    def __new__(cls, name, bases, d):
        d['friendly_name'] = re.sub(r'(.)([A-Z])(?=[a-z])', r'\1 \2', name)
        out = super(RPCErrorMeta, cls).__new__(cls, name, bases, d)
        if 'error_code' in d and d['error_code'] \
                and d['error_code'] not in RPCError.class_for_error_code:
            RPCError.class_for_error_code[d['error_code']] = out
        return out


class RPCError(with_metaclass(RPCErrorMeta, Exception)):
    error_code = None
    class_for_error_code = {}

    @property
    def error_msg(self):
        try:
            return self.args[0]
        except LookupError:
            return self.friendly_name

    @property
    def error_data(self):
        try:
            return self.args[1]
        except LookupError:
            return None

    def __str__(self):
        out = "Error {0}: {1}".format(self.error_code, self.error_msg)
        if self.error_data:
            out += "\nError data: {0!r}".format(self.error_data)
        return out

    def to_response(self, id_=None):
        return Response(None,
                        dict(code=self.error_code, message=self.error_msg,
                             data=self.error_data),
                        id_)


class ParseError(RPCError):
    error_code = -32700


class InvalidRequest(RPCError):
    error_code = -32600


class MethodNotFound(RPCError):
    error_code = -32601


class InvalidParams(RPCError):
    error_code = -32602


class InternalError(RPCError):
    error_code = -32603


class ServerError(RPCError):
    pass


class ApplicationError(RPCError):
    pass


def rpc_exception_class_for_code(code, extra_code_mapping=None):
    code = code if code else -32099
    code_mapping = RPCError.class_for_error_code.copy()
    if extra_code_mapping:
        code_mapping.update(extra_code_mapping)

    cls = code_mapping.get(int(code), None)
    if cls is not None:
        return cls
    elif code >= -32099 and code <= -32000:
        return ServerError
    else:
        return ApplicationError


class Endpoint(object):

    default_socket_type = None
    error_code_exceptions = None
    logger = None

    socket = None

    def __init__(self, endpoint, socket_type, timeout, context=None,
                 logger=None):
        super(Endpoint, self).__init__()
        self.endpoint = endpoint

        if socket_type:
            self.socket_type = socket_type
        elif self.default_socket_type:
            self.socket_type = self.default_socket_type
        else:
            raise TypeError("Socket type invalid")

        self.timeout = timeout
        self.context = context or zmq.Context.instance()
        self.logger = logger if logger else package_logger

    def close(self):
        self.socket.close()
