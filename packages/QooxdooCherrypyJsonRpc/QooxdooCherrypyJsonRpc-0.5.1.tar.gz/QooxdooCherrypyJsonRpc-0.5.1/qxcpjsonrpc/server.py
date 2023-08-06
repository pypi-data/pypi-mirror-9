'''

  QooxdooCherrypyJsonRpc

  Based on:
    http://qooxdoo.org/contrib/project#rpcpython

  License:
    LGPL: http://www.gnu.org/licenses/lgpl.html
    EPL: http://www.eclipse.org/org/documents/epl-v10.php

  Authors:
    * Viktor Ferenczi (python@cx.hu)
    * Christian Boulanger (cboulanger)
    * saaj (mail@saaj.me)


  This is the main module that provides classes for server, request and service. 
  
  ``Server`` is responisble for high-level dispatching, *GET* and *POST*,
  and for handling errors that could not be gracefully handled during request
  processing, i.e. within the rpc protocol itself.
  
  ``Request`` unpacks the protocol JSON payload, initiates requested method 
  invocation via ``ServiceLocator.callFrom(request)``, handles errors
  within the protocol, and determines proper return, JSON or binary. 
  
  ``Service`` is an abstract class with end-user services must inherite from.
  
  This module is NOT intended for direct import. Import symbols from qxcpjsonrpc.

'''


import json
import datetime
import decimal
import logging
import traceback

import cherrypy
from cherrypy._cpcompat import unquote, unicodestr, basestring

from .error import Error, ServerError
from .date import toJsonDate
from .locator import ServiceLocator


__all__ = 'Request', 'Server', 'ServerTool', 'Service'


class Request(object):
  '''JSON-RPC request. Request object stores all important information
  about the request. 

  Request objects can be reused to achieve better performance. The server
  can use one Request object for all requests from the same client on the
  same logical connection. It's not allowed to share Request objects
  between multiple threads, since they are not thread safe, no locking
  mechanism is implemented.

  The server's request handler must load request data by calling the
  load() or loadJson() method of the Request instance. Then the request
  can be processed by calling the process() method. Finally the request
  object should be cleared by calling clear() on it. This is not required,
  but helps to prevent hard-to-debug errors and lower memory footprint.

  Request objects has human readable representation for easy logging and
  debugging.
  
  Request attributes defined as slots for better performance:

    :id:       current request's ID or None if no request has been loaded
    :service:  service name
    :method:   method name or path with dots
    :params:   list or dictionary of parameters to be passed to the method or []
    :data:     server_data or None
    :domain:   domain name or None if the current transport does not support domains
  
  This module is NOT intended for direct import. Import symbols from qxcpjsonrpc.
    
  '''

  __slots__ = 'id', 'service', 'method', 'params', 'data', 'domain'
  

  def __init__(self):
    '''Initialize common request attributes.'''

    self.clear()

  def __repr__(self):
    attributes = u', '.join(u'{0}={1!r}'.format(k, getattr(self, k)) for k in self.__slots__)
    return u'{0}({1})'.format(self.__class__.__name__, attributes)

  def clear(self):
    '''Clear request data. Should be called after each request handling.'''

    self.id      = None
    self.domain  = None
    self.service = None
    self.method  = None
    self.params  = None
    self.data    = None

  def load(self, **kwargs):
    '''Load request from keyword arguments'''

    # Check for required request arguments
    for n in ('id', 'service', 'method'):
      if n not in kwargs:
        raise ServerError('Request does not contain "{0}"!'.format(n))

    # Extract request arguments with defaults
    self.id      = kwargs['id']
    self.service = kwargs['service']
    self.method  = kwargs['method']
    self.params  = kwargs.get('params', [])
    self.data    = kwargs.get('server_data', None)

    # Check type of request arguments
    if not isinstance(self.service, basestring):
      raise ServerError('Service name is not a string: {0!r}'.format(self.service))
    if not isinstance(self.method, basestring):
      raise ServerError('Method name is not a string: {0!r}'.format(self.method))
    if not isinstance(self.params, (list, dict)):
      raise ServerError('Parameters are not list or dictionary: {0!r}'.format(self.params))

    # Check request id value
    try:
      assert int(self.id) > 0
    except (ValueError, TypeError, AssertionError): 
      raise ServerError('Request id must be positive integer!')

  def loadJson(self, s):
    '''Load request from JSON request string'''

    # Decode JSON request as Python object
    try:
      request = json.loads(s)
    except ValueError as ex:
      raise ServerError('Error decoding JSON request: {0}'.format(ex))

    # Load request
    self.load(**request)

  def log(self, message, error):
    cherrypy.log(message, severity = logging.DEBUG if not error else logging.ERROR)
    
  def serialize(self, obj):
    '''Serialization for objects that not handled by json package''' 
    
    if isinstance(obj, datetime.date):
      return toJsonDate(obj)

    if isinstance(obj, decimal.Decimal):
      return str(obj)

    raise TypeError(u'{0!r} is not JSON serializable'.format(obj))

  def process(self, locator):
    '''Process request, returns JSON-RPC response object (not JSON string).'''

    assert self.id is not None, 'Load request into this instance before processing!'

    self.log('REQUEST: {0!r}'.format(self), False)

    try:
      result = locator.callFrom(self)
    except Error as ex:
      message = 'REQUEST: {0!r}\nAPPLICATION ERROR [{1}]: {2}\nTRACEBACK:\n{3}'
      self.log(message.format(self, ex.__class__.__name__, ex, traceback.format_exc()), True)

      response = dict(id = self.id, result = None, error = ex.getJsonRpcError())
    except Exception as ex:
      message = 'REQUEST: {0!r}\nINTERNAL SERVER ERROR [{1}]: {2}\nTRACEBACK:\n{3}'
      self.log(message.format(self, ex.__class__.__name__, ex, traceback.format_exc()), True)

      ex = ServerError('Internal server error: {0}'.format(ex))
      response = dict(id = self.id, result = None, error = ex.getJsonRpcError())
    else:
      response = dict(id = self.id, result = result, error = None)

    self.log('RESPONSE: {0}'.format(response), False)
    
    if hasattr(response['result'], 'read'):
      if hasattr(response['result'], 'seek'):
        response['result'].seek(0)
      response = response['result'].read()
      
      if isinstance(response, unicodestr):
        response = response.encode('utf-8') 
    else:
      # iframe response case
      if cherrypy.response.headers['content-type'] != 'text/plain':
        cherrypy.response.headers['content-type'] = 'application/json'
      try:
        response = json.dumps(response, default = self.serialize).encode()
      except TypeError as ex:
        ex = ServerError('Error JSON encoding response: {0}'.format(ex))
        response = dict(id = self.id, result = None, error = ex.getJsonRpcError())
        response = json.dumps(response).encode()

    return response


class Server(object):
  '''HTTP JSON-RPC server backend for qooxdoo and other json-rpc clients'''

  _requestClass = None
  '''Request class'''
  
  _locator = None
  '''Service locator object'''
   

  def __init__(self, requestClass = Request, locatorClass = ServiceLocator):
    '''Creates a rpc server:
    
       requestClass: class of request object, provides override for custom serialization
       locatorClass: class of service locator object, provides override for custom service lookup
     '''
    
    self._requestClass = requestClass
    self._locator      = locatorClass()

  def _get(self, request):
    # Determine request domain
    request.domain = cherrypy.request.headers.get('host', None)

    # Expand ScriptTransport arguments if any
    scriptTransportId   = cherrypy.request.params.get('_ScriptTransport_id', None)    # @UndefinedVariable
    scriptTransportData = cherrypy.request.params.get('_ScriptTransport_data', None)  # @UndefinedVariable

    # Determine transport type
    if scriptTransportId and scriptTransportData:
      # ScriptTransport, JSON encoded request object is in _ScriptTransport_data
      request.loadJson(scriptTransportData)
      # Handle request
      response = request.process(self._locator)
      # Encode qooxdoo specific ScriptTransport response, if only response is JSON
      if cherrypy.response.headers.get('content-type') == 'application/json':
        callback = 'qx.io.remote.transport.Script._requestFinished'
        response = b''.join(('{0}({1},'.format(callback, scriptTransportId).encode(), response, b');'))
    else:
      raise cherrypy.HTTPError(400, 'Missing script transport query parameters!')

    return response

  def _post(self, request):
    # Determine request domain
    request.domain = cherrypy.request.headers.get('host', None)

    # Read POST data
    contentLength = int(cherrypy.request.headers.get('content-length', '0'))
    if contentLength < 1:
      raise cherrypy.HTTPError(400, 'No Content-Length header or zero length specified!')
    formData = cherrypy.request.body.read()

    # Slices in place of indices for empty string.
    if formData[:1] == b'{' and formData[-1:] == b'}':
      # Normal json request 
      jsonData = formData.decode('utf-8')
    elif all(k in cherrypy.request.params for k in ('_ScriptTransport_data', '_ScriptTransport_id')):
      # URL-encoded form, e.g. upload
      jsonData = unquote(cherrypy.request.params['_ScriptTransport_data'])
    else:
      raise cherrypy.HTTPError(400, 'Invalid POST request payload!')

    # Load requst from JSON
    request.loadJson(jsonData)

    # Handle request
    return request.process(self._locator)

  def run(self):
    try:
      request = self._requestClass()
      if cherrypy.request.method == 'GET':
        return self._get(request)
      elif cherrypy.request.method == 'POST':
        return self._post(request)
      else:
        raise cherrypy.HTTPError(400, 'Services require JSON-RPC')
    except cherrypy.HTTPError:
      raise
    except ServerError as ex:
      cherrypy.log(traceback = True, severity = logging.ERROR)
      raise cherrypy.HTTPError(400, '[{0}]: {1}'.format(ex.__class__.__name__, ex))
    except Exception as ex:
      cherrypy.log(traceback = True, severity = logging.ERROR)
      raise cherrypy.HTTPError(500, 'Internal server error: {0}'.format(ex))


class ServerTool(cherrypy._cptools.HandlerTool):
  
  _server = None
  '''Instance of ``Server`` shared for all requests.'''
  
  
  def __init__(self, **kwargs):
    cherrypy._cptools.HandlerTool.__init__(self, self.callable)
    self._server = Server(**kwargs)
    
  def callable(self):
    cherrypy.serving.response.body = self._server.run() 
    return cherrypy.serving.response.body


class Service(object):
  '''Abstract class of a service'''

  def onException(self, exception):
    pass

  def preDispatch(self, request, method):
    pass

  def postDispatch(self, request, method):
    pass

