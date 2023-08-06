# -*- coding: utf-8 -*-
'''
@author: saaj
'''


import json
import hashlib
import os.path
import base64
import re

from cherrypy._cpcompat import quote, urlencode

import qxcpjsonrpc as rpc
import qxcpjsonrpc.error as error
import qxcpjsonrpc.test as test
from qxcpjsonrpc.date import fromJsonDate, toJsonDate


class TestGeneral(test.TestCase):
  
  def testIndex(self):
    self.getPage('/')
    
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertBody('Testing qxcpjsonrpc')
  
  def testServiceEmpty(self):
    self.getPage('/service')
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertStatus(400)
  
  def testServiceServiceNotFound(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'something.User',
      'method'  : 'do',
      'params'  : []
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    message = '[ServiceNotFoundError] Module "something" not found!' 
    self.assertEqual(message, response['error']['message'])
    self.assertEqual([], test.Service.state, 'No app-level error logging when no service is found')

    
    request = json.dumps({
      'id'      : 1,
      'service' : 'something',
      'method'  : 'do',
      'params'  : []
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    message = '[ServiceNotFoundError] Ambiguous service "something"!' 
    self.assertEqual(message, response['error']['message'])
    self.assertEqual([], test.Service.state, 'No app-level error logging when no service is found')
    
  def testServiceMethodNotFound(self):
    self._post('do')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    service = '<qxcpjsonrpc.test.Service object at 0x[\w]+>'
    pattern = r'\[MethodNotFoundError\] Method "do" not found in service {0}!'.format(service)
    self.assertRegexpMatches(response['error']['message'], pattern)
    
    self.assertEqual('onException', test.Service.state[0][0])
    self.assertTrue(isinstance(test.Service.state[0][1], error.MethodNotFoundError))
    
    
    self._post('state')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    service = '<qxcpjsonrpc.test.Service object at 0x[\w]+>'
    pattern = r'\[MethodNotFoundError\] Method [] in service {0} is not callable!'.format(service)
    self.assertRegexpMatches(response['error']['message'], pattern)
    
    self.assertEqual('onException', test.Service.state[0][0])
    self.assertTrue(isinstance(test.Service.state[0][1], error.MethodNotFoundError))
  
  def testServiceClassNotFound(self):
    request = json.dumps({
      'id'      : 11,
      'service' : 'qxcpjsonrpc.test.Service2',
      'method'  : 'add',
      'params'  : ()
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertIs(None, response['result'])
    self.assertEqual({
      'code'   : 3,
      'origin' : error.ErrorOrigin.Server, 
      'message': '[ClassNotFoundError] Can not get class "Service2" from "qxcpjsonrpc.test"!' 
    }, response['error'])
    self.assertEqual([], test.Service.state)
    
    
    request = json.dumps({
      'id'      : 11,
      'service' : 'qxcpjsonrpc.test.Root',
      'method'  : 'index',
      'params'  : ()
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertIs(None, response['result'])
    self.assertEqual({
      'code'   : 3,
      'origin' : error.ErrorOrigin.Server, 
      'message': '[ClassNotFoundError] "qxcpjsonrpc.test.Root" is not a RPC service!' 
    }, response['error'])
    self.assertEqual([], test.Service.state)
  
  def testServicePostJson(self):
    '''POST payload is a JSON'''
    
    self._post('add', 12, 13)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    self.assertEqual(12 + 13, response['result'])
    
  def testServicePostForm(self):
    '''POST payload is a URL-encoded form'''
    
    request = '_ScriptTransport_id=11&_ScriptTransport_data=' + quote(json.dumps({
      'id'      : 11,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (123, 5)
    }))
    headers = [
      ('content-length', str(len(request))),
      ('content-type',   'application/x-www-form-urlencoded')
    ]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    self.assertEqual(128, response['result'])
    
  def testServicePostTool(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (12, 9)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/fromtool', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    self.assertEqual(12 + 9, response['result'])
    
  def testServiceGet(self):
    request = {
      '_ScriptTransport_data' : json.dumps({
        'id'      : 1,
        'service' : 'qxcpjsonrpc.test.Service',
        'method'  : 'add',
        'params'  : [12, 13]
      }),
      '_ScriptTransport_id' : 1 
    }
    
    self.getPage('/service?' + urlencode(request), method = 'get')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    pattern = re.escape('qx.io.remote.transport.Script._requestFinished(1,sub);').replace('sub', '(.+)')
    self.assertEqual({'error': None, 'id': 1, 'result': 25}, json.loads(re.findall(pattern, self.body.decode())[0]))
    
  def testServiceGetTool(self):
    request = {
      '_ScriptTransport_data' : json.dumps({
        'id'      : 1,
        'service' : 'qxcpjsonrpc.test.Service',
        'method'  : 'add',
        'params'  : [12, 13]
      }),
      '_ScriptTransport_id' : 1 
    }
    
    self.getPage('/fromtool?' + urlencode(request), method = 'get')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    pattern = re.escape('qx.io.remote.transport.Script._requestFinished(1,sub);').replace('sub', '(.+)')
    self.assertEqual({'error': None, 'id': 1, 'result': 25}, json.loads(re.findall(pattern, self.body.decode())[0]))
    
  def testDispatchOrder(self):
    self._post('add', 12, 13)


    self.assertEqual(3, len(test.Service.state))
    
    self.assertIs(test.Service.state[0][1], test.Service.state[2][1], 'same Request object')
    
    item = test.Service.state.pop(0)
    self.assertEqual('preDispatch', item[0])
    self.assertIsInstance(item[1], rpc.Request)
    try:
      self.assertIs(item[2].__func__, test.Service.add.__func__)  # @UndefinedVariable
    except AttributeError:
      # Python 3 compatibility, unbound methods have gone
      self.assertIs(item[2].__func__, test.Service.add)  # @UndefinedVariable
    
    item = test.Service.state.pop(0)
    self.assertEqual('add', item[0])
    self.assertIsNone(item[1])

    item = test.Service.state.pop(0)
    self.assertEqual('postDispatch', item[0])
    self.assertIsInstance(item[1], rpc.Request)
    try:
      self.assertIs(item[2].__func__, test.Service.add.__func__)  # @UndefinedVariable
    except AttributeError:
      # Python 3 compatibility, unbound methods have gone
      self.assertIs(item[2].__func__, test.Service.add)  # @UndefinedVariable
    
  def testSystemError(self):
    self._post('error', 'sys')

    self.assertEqual(3, len(test.Service.state))
    
    self.assertIs(test.Service.state[0][1], test.Service.state[2][1], 'same Request object')
    
    item = test.Service.state.pop(0)
    self.assertEqual('preDispatch', item[0])
    self.assertIsInstance(item[1], rpc.Request)
    
    item = test.Service.state.pop(0)
    self.assertEqual('onException', item[0])
    self.assertIsInstance(item[1], ValueError)

    item = test.Service.state.pop(0)
    self.assertEqual('postDispatch', item[0])
    self.assertIsInstance(item[1], rpc.Request)
    
    response = json.loads(self.body.decode('ascii'))
    self.assertEqual({
      'result' : None, 
      'id'     : 1, 
      'error'  : {
        'origin'  : error.ErrorOrigin.Application, 
        'code'    : error.ErrorCode.Unknown,
        'message' : u'[ApplicationError] Error message',
      } 
    }, response)
    
  def testApplicationError(self):
    self._post('error', 'app')

    self.assertEqual(3, len(test.Service.state))
    
    self.assertIs(test.Service.state[0][1], test.Service.state[2][1], 'same Request object')
    
    item = test.Service.state.pop(0)
    self.assertEqual('preDispatch', item[0])
    self.assertIsInstance(item[1], rpc.Request)
    
    item = test.Service.state.pop(0)
    self.assertEqual('onException', item[0])
    self.assertIsInstance(item[1], rpc.ApplicationError)

    item = test.Service.state.pop(0)
    self.assertEqual('postDispatch', item[0])
    self.assertIsInstance(item[1], rpc.Request)
    
    response = json.loads(self.body.decode('ascii'))
    self.assertEqual({
      'result' : None, 
      'id'     : 1, 
      'error'  : {
        'origin'  : error.ErrorOrigin.Application, 
        'code'    : error.ErrorCode.Unknown,
        'message' : u'[ApplicationError] App error',
      } 
    }, response)
    
  def testPermissionError(self):
    self._post('error', 'perm')

    self.assertEqual(3, len(test.Service.state))
    
    self.assertIs(test.Service.state[0][1], test.Service.state[2][1], 'same Request object')
    
    item = test.Service.state.pop(0)
    self.assertEqual('preDispatch', item[0])
    self.assertIsInstance(item[1], rpc.Request)
    
    item = test.Service.state.pop(0)
    self.assertEqual('onException', item[0])
    self.assertIsInstance(item[1], rpc.PermissionDeniedError)

    item = test.Service.state.pop(0)
    self.assertEqual('postDispatch', item[0])
    self.assertIsInstance(item[1], rpc.Request)
    
    response = json.loads(self.body.decode('ascii'))
    self.assertEqual({
      'result' : None, 
      'id'     : 1, 
      'error'  : {
        'origin'  : error.ErrorOrigin.Server, 
        'code'    : error.ErrorCode.PermissionDenied,
        'message' : u'[PermissionDeniedError] Forbidden',
      } 
    }, response)
    
  def testEmptyDates(self):
    self.assertIs(None, fromJsonDate(None))
    self.assertIs(None, toJsonDate(None))
  
  def testDictParams(self):
    request = json.dumps({
      'id'      : 11,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : dict(x = 123, y = -33)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    self.assertEqual(90, response['result'])
  
  def testUnicodeParams(self):
    expected = [{'record' : u'Ænima'}, {'foo' : u'бар'}]
    
    self._post('echo', expected)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode())
    self.assertTrue(response['error'] is None)
    self.assertEqual(expected, response['result'])
    
    
    # Unencoded utf-8 strings    
    request = (u'{"params": [[{"record": "Ænima"}, {"foo": "бар"}]], ' 
      u'"id": 1, "service": "qxcpjsonrpc.test.Service", "method": "echo"}').encode('utf-8')
    headers = [
      ('content-length', str(len(request))),
      ('content-type',   'application/json; charset=utf-8'),
    ]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode())
    self.assertTrue(response['error'] is None)
    self.assertEqual(expected, response['result'])
  
  def testInvalidHttpMethodHttpError(self):
    self.getPage('/service', method = 'options')
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('Services require JSON-RPC')
  
  def testMalformedServiceHttpError(self):
    request = json.dumps({
      'id'      : 1,
      'service' : False,
      'method'  : 'do',
      'params'  : 'should be list of dict'
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    
  def testMalformedMethodHttpError(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'something.Test',
      'method'  : None,
      'params'  : 'should be list of dict'
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    
  def testMalformedParamsHttpError(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'something.Test',
      'method'  : 'do',
      'params'  : 'should be list of dict'
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    
  def testPostContentLengthHttpError(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (4, -5)
    })
    
    self.getPage('/service', method = 'post', body = request)
    
    self.assertStatus(411)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('Client must specify Content-Length.')
    
    
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (4, -5)
    })
    headers = [('content-length', '-1')]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('No Content-Length header or zero length specified!')
  
  def testPostMalformedPayloadHttpError(self):
    request = 'something=42'
    headers = [
      ('content-length', str(len(request))),
      ('content-type',   'application/x-www-form-urlencoded')
    ]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('Invalid POST request payload!')
        
  def testRequestJsonUnserializationHttpError(self):
    request = '_ScriptTransport_id=1&_ScriptTransport_data=not+a+JSON'
    headers = [
      ('content-length', str(len(request))),
      ('content-type',   'application/x-www-form-urlencoded')
    ]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('Error decoding JSON request: No JSON object could be decoded')
    
  def testResponseJsonSerializationServerError(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'complex',
      'params'  : ()
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    self.assertEqual({
      'code'    : error.ErrorCode.Unknown,
      'origin'  : error.ErrorOrigin.Server, 
      'message' : '[ServerError] Error JSON encoding response: (1-2j) is not JSON serializable' 
    },response['error'])
    
  def testRequestMissingRequiredArgumentHttpError(self):
    request = json.dumps({
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (1, 2)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('[ServerError]: Request does not contain "id"!')
    
    
    request = json.dumps({
      'id'      : 1,
      'method'  : 'add',
      'params'  : (1, 2)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('[ServerError]: Request does not contain "service"!')
    
    
    request = json.dumps({
      'id'      : 2,
      'service' : 'qxcpjsonrpc.test.Service',
      'params'  : (1, 2)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('[ServerError]: Request does not contain "method"!')
    
  def testRequestInvalidRequestIdHttpError(self):
    request = json.dumps({
      'id'      : None,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (1, 2)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('[ServerError]: Request id must be positive integer!')
    
    
    request = json.dumps({
      'id'      : '-1',
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (1, 2)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('[ServerError]: Request id must be positive integer!')
    
    
    request = json.dumps({
      'id'      : 'blah',
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (1, 2)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(400)
    self.assertHeader('content-type', 'text/html;charset=utf-8')
    self.assertInBody('[ServerError]: Request id must be positive integer!')

  def testSystemErrorHttpError(self):
    '''Shouldn't probably happen, as it's hard to produce otherwise'''
    
    class BrokenRequest:
      
      def loadJson(self, s):
        raise RuntimeError('Imagine it is broken')
    
    
    oldClass = test.Root._server._requestClass
    test.Root._server._requestClass = BrokenRequest
    try:
      self._post('add', 12, 13)
      
      self.assertStatus(500)
      self.assertHeader('content-type', 'text/html;charset=utf-8')
      self.assertInBody('Internal server error: Imagine it is broken')
    finally:
      test.Root._server._requestClass = oldClass


class TestAccess(test.TestCase):
  
  def testServiceEmpty(self):
    self.getPage('/withauth')
    self.assertStatus(401)
    self.assertHeader('WWW-Authenticate', 'Basic realm="musicians"')
    
    self.getPage('/withauth', headers = [('Authorization', 'Basic am9uZXM6YmxhaC1ibGFo')])
    self.assertStatus(401)
    
    token = 'Basic {0}'.format(base64.b64encode(b'jones:XpasS3').decode('ascii'))
    self.getPage('/withauth', headers = [('Authorization', token)])
    self.assertStatus(400)
    
  def testServiceMethodInternal(self):
    self._post('internal')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    message = u'[PermissionDeniedError] Access denied on "internal"!' 
    self.assertEqual(message, response['error']['message'])
    
  def testServiceMethodFail(self):
    self._post('forbidden')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    message = u'[PermissionDeniedError] Access denied on "forbidden"!' 
    self.assertEqual(message, response['error']['message'])
    
  def testAccessAllowed(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'subtract',
      'params'  : [13, 12]
    })
    headers = [
      ('content-length', str(len(request))),
      ('authorization', 'Basic {0}'.format(base64.b64encode(b'burns:XpaSs2').decode('ascii')))
    ]
    
    self.getPage('/withauth', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    self.assertEqual(13 - 12, response['result'])
    
  def testBrokenAccessCheck(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'authFail',
      'params'  : []
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    self.assertEqual('[ApplicationError] Some sort of failure', response['error']['message'])
    
    item = test.Service.state.pop(0)
    self.assertEqual('onException', item[0])
    self.assertIsInstance(item[1], AttributeError)
  
  def testAccessForbidden(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'subtract',
      'params'  : [13, 12]
    })
    headers = [
      ('content-length', str(len(request))),
      ('authorization', 'Basic {0}'.format(base64.b64encode(b'jones:XpasS3').decode('ascii')))
    ]
    
    self.getPage('/withauth', method = 'post', body = request, headers = headers)

    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    message = u'[PermissionDeniedError] Access denied on "subtract"!' 
    self.assertEqual(message, response['error']['message'])
    

class TestJsonExtra(test.TestCase):
  
  def testDecimal(self):
    self._post('decimal')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    self.assertEqual(u'12.13', response['result'])
  
  def testDate(self):
    self._post('today')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    
    self.assertEqual([
      u'2012-03-17T19:09:12.217000Z',
      u'2012-03-17T00:00:00Z',
      u'2012-03-17T17:09:12.217000Z'
    ], response['result'])
    
    dates = tuple(map(lambda d: str(test.rpc.fromJsonDate(d)), response['result']))
    self.assertEqual('2012-03-17 19:09:12.217000+00:00', dates[0])
    self.assertEqual('2012-03-17 00:00:00+00:00',        dates[1])
    self.assertEqual('2012-03-17 17:09:12.217000+00:00', dates[2])


class TestCustom(test.TestCase):
  
  def testRequest(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'today',
      'params'  : ()
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/customrequest', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    
    self.assertEqual([
      u'2012-03-17T19:09:12.217000', 
      u'2012-03-17', 
      u'2012-03-17T19:09:12.217000+02:00'
    ], response['result'])
    
  def testServiceLocator(self):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : 'add',
      'params'  : (4, -5)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/fromtool', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    self.assertEqual(-1, response['result'])
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['error'] is None)
    self.assertEqual(-1, response['result'])

    
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test2.Service',
      'method'  : 'add',
      'params'  : (4, -5)
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/fromtool', method = 'post', body = request, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/json')
    
    response = json.loads(self.body.decode('ascii'))
    self.assertTrue(response['result'] is None)
    self.assertEqual({
      'code'    : error.ErrorCode.Unknown,
      'origin'  : error.ErrorOrigin.Server, 
      'message' : '[ServerError] Internal server error: Restriction example' 
    },response['error'])


class TestFile(test.TestCase):
  
  def testDownloadStringIo(self):
    self._post('downloadStringIo')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/octet-stream')

    self.assertEqual(3528, len(self.body))
    self.assertEqual('06184ee1826a72ff03a70905219d7ea4', hashlib.md5(self.body).hexdigest())
  
  def testDownloadFileIo(self):
    self._post('downloadFileIo')
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'application/octet-stream')

    self.assertEqual(16 * 1024, len(self.body))
    self.assertEqual('3da48cc51e8ae6bf254325235395d9cf', hashlib.md5(self.body).hexdigest())
    
  def testUpload(self):
    boundary  = '900150983cd24fb0d6963f7d28e17f72'
    bodyLines = []
    def addLine(name, value, type = None):
      bodyLines.append(('--' + boundary).encode())
      bodyLines.append('Content-Disposition: {0}'.format(name).encode())
      if type:
        bodyLines.append('Content-Type: {0}'.format(type).encode())
      bodyLines.append(b'')
      bodyLines.append(value)
      
    addLine(
      'form-data; name="_ScriptTransport_id"',
      '123'.encode()
    )
    addLine(
      'form-data; name="_ScriptTransport_data"',
      quote(json.dumps({
        'id'      : 1,
        'service' : 'qxcpjsonrpc.test.Service',
        'method'  : 'upload',
        'params'  : [dict(v = 1209)]
      })).encode()
    )
    addLine(
      'form-data; name="random-binary"; filename="upload.bin"',
      open(os.path.dirname(__file__) + '/fixture/binary', 'rb').read(),
      'application/octet-stream',
    )
    bodyLines.append(('--' + boundary + '--').encode())
    
    body    = b'\r\n'.join(bodyLines)
    headers = [
      ('content-type',   'multipart/form-data; boundary={0}'.format(boundary)),
      ('content-length', str(len(body)))
    ]
    
    self.getPage('/service', method = 'post', body = body, headers = headers)
    
    self.assertStatus(200)
    self.assertHeader('content-type', 'text/plain;charset=utf-8')
    
    response = json.loads(self.body.decode())
    self.assertTrue(response['error'] is None)
    self.assertEqual(dict(v = 1209), response['result']['passthrough'])
    self.assertEqual('3da48cc51e8ae6bf254325235395d9cf', response['result']['hash'])

