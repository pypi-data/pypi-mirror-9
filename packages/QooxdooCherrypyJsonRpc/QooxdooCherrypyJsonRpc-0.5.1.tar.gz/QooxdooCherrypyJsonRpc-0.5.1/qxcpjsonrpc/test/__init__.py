'''
@author: saaj

The package's test suite sets the warning filters explicitly. Warnings are converted 
to exceptions.

There are several supposed ways to launch the test suite:

  1) PyDev ``PydevTextTestRunner``
  2) ``setuptools.command.test``command, directly or via ``tox``
  3) ``unittest`` direct module invokation

Because Python warning settings vary across these three, some normalization is required to 
produce the same output. The issue is that there is no other easy way to prevent ``unittest`` 
from settings ``default`` action warning filter, ``unittest.main.TestProgram.warnings``. 
See ``unittest.main.TestProgram.__init__``, ``unittest.runner.TextTestRunner.run``. 
Thus the following is suggested.
  
  1) Doesn't require any handling, because ``unittest.main.TestProgram`` isn't used
  2) Set ``sys.warnoptions`` in ``setup.py``
  3) Call it ``python -Wa -m unittest qxcpjsonrpc.test.suite`` 
'''


import json
import urllib
import decimal
import datetime
import io
import os.path
import hashlib
import warnings
import sys

import cherrypy
from cherrypy.lib import auth_basic

# cherrypy helper uses nose as runner, emulate for standard runner
try:
  import nose #@UnusedImport
except ImportError:
  import types
  sys.modules['nose'] = types.ModuleType('nose')
import cherrypy.test.helper as helper 

import qxcpjsonrpc as rpc


class CustomRequest(rpc.Request):
  
  def serialize(self, obj):
    if isinstance(obj, datetime.date):
      return obj.isoformat()

    return super(CustomRequest, self).serialize(obj)
  
  
class CustomServiceLocator(rpc.ServiceLocator):
  
  def _loadModule(self, modulePath):
    assert modulePath == 'qxcpjsonrpc.test', 'Restriction example'
    
    return super(CustomServiceLocator, self)._loadModule(modulePath)


users = {
  'braithwaite' : 'XpaSS1',
  'burns'       : 'XpaSs2',
  'jones'       : 'XpasS3',
  'carey'       : 'Xpass4',
}
roles = {
  'braithwaite' : 'mogwai',
  'burns'       : 'mogwai',
  'jones'       : 'tool',
  'carey'       : 'tool'
}
config = {
  '/withauth' : {
    'tools.auth_basic.on'            : True,
    'tools.auth_basic.realm'         : 'musicians',
    'tools.auth_basic.checkpassword' : auth_basic.checkpassword_dict(users)
  },
  '/fromtool' : {
    'tools.jsonrpc.on' : True
  }
}
cherrypy.tools.jsonrpc = rpc.ServerTool(locatorClass = CustomServiceLocator)


class Root:
  
  _server = rpc.Server()
  '''Server instance can be shared between threads'''
  
    
  @cherrypy.expose
  def index(self):
    return 'Testing qxcpjsonrpc'
  
  @cherrypy.expose
  def service(self, *args, **kwargs):
    return self._server.run()
  
  @cherrypy.expose
  def withauth(self, *args, **kwargs):
    return self._server.run()
  
  @cherrypy.expose
  def customrequest(self, *args, **kwargs):
    return rpc.Server(CustomRequest).run()
  

def allow(*forRoles):
  # allows access for any of provided roles
  def _allow(method, request):
    userRole = roles[cherrypy.request.login]
    return any(userRole == role for role in forRoles)

  return _allow

def brokenAllow(*forRoles):
  # allows access for any of provided roles
  def _allow(method, request):
    raise AttributeError('Some sort of failure')

  return _allow

class Service(rpc.Service):

  state = []
  
  
  def __init__(self):
    super(Service, self).__init__()

    del self.state[:]
  
  def onException(self, exception):
    self.state.append(('onException', exception))

  def preDispatch(self, request, method):
    self.state.append(('preDispatch', request, method))

  def postDispatch(self, request, method):
    self.state.append(('postDispatch', request, method))

  @rpc.public
  def error(self, type):
    if type == 'sys':
      raise ValueError('Error message')
    elif type == 'app':
      raise rpc.ApplicationError('App error')
    elif type == 'perm':
      raise rpc.PermissionDeniedError('Forbidden')
  
  def internal(self):
    pass
  
  @rpc.fail
  def forbidden(self):
    pass

  @rpc.public
  def add(self, x, y):
    self.state.append(('add', None))
    
    return x + y
  
  @rpc.access(allow('mogwai'))
  def subtract(self, x, y):
    return x - y
  
  @rpc.access(brokenAllow('foo'))
  def authFail(self):
    pass
  
  @rpc.public
  def decimal(self):
    return decimal.Decimal('12.13')
  
  @rpc.public
  def echo(self, value):
    return value
  
  @rpc.public
  def complex(self):
    return 1 - 2j
  
  @rpc.public
  def today(self):
    class Fixed(datetime.tzinfo):
       
      def utcoffset(self, dt):
        return datetime.timedelta(hours = 2)
      
      def dst(self, dt):
        return datetime.timedelta(0)
    
    d = datetime.datetime(2012, 3, 17, 19, 9, 12, 217000)
    
    return (d, d.date(), d.replace(tzinfo = Fixed()))
  
  @rpc.public
  def downloadStringIo(self):
    cherrypy.response.headers['content-type']        = 'application/octet-stream'
    cherrypy.response.headers['content-disposition'] = 'attachment; filename=download.txt'
    
    result = io.StringIO()
    result.write(open(os.path.dirname(__file__) + '/fixture/text', 'rb').read().decode())
    
    return result
  
  @rpc.public
  def downloadFileIo(self):
    cherrypy.response.headers['content-type']        = 'application/octet-stream'
    cherrypy.response.headers['content-disposition'] = 'attachment; filename=download.bin'
    
    return io.FileIO(os.path.dirname(__file__) + '/fixture/binary')
  
  @rpc.public
  def upload(self, passthrough):
    part = cherrypy.request.params['random-binary']
    hash = hashlib.md5(part.file.read()).hexdigest()
    
    # XHR upload IE iframe fallback. Response is accessible only if MIME is set to plain/text.
    cherrypy.response.headers['content-type'] = 'text/plain'
    
    return dict(hash = hash, passthrough = passthrough)


# explicit warning control  
warnings.resetwarnings()
warnings.simplefilter('error')
if sys.version_info >= (3, 0):
  # qxcpjsonrpc.test.suite, okay for polyglot package 
  warnings.filterwarnings('ignore', 'Please use assertRegex instead', DeprecationWarning)
  # qxcpjsonrpc.test.suite: no non-referenced-counting Python implementation targeted
  warnings.filterwarnings('ignore', 'unclosed file <_io.', ResourceWarning)  # @UndefinedVariable
  # cherrypy._cperror: reported #1330
  warnings.filterwarnings('ignore', 'cgi.escape is deprecated, use html.escape instead', DeprecationWarning)
  # cherrypy.wsgiserver.wsgiserver3: reported #1331
  warnings.filterwarnings('ignore', 'unclosed <socket.socket object', ResourceWarning)  # @UndefinedVariable


delattr(helper.CPWebCase, 'test_gc') # don't want the supplement in a test report

class TestCase(helper.CPWebCase):
  
  interactive = False
  
  
  def setUp(self):
    self.__class__.setup_server = classmethod(lambda cls: cherrypy.tree.mount(Root(), config = config))
    # nose setup
    self.setup_class()
    
    del Service.state[:]
    
  def tearDown(self):
    # nose teardown
    self.teardown_class()
    
  def _post(self, method, *args):
    request = json.dumps({
      'id'      : 1,
      'service' : 'qxcpjsonrpc.test.Service',
      'method'  : method,
      'params'  : args
    })
    headers = [('content-length', str(len(request)))]
    
    self.getPage('/service', method = 'post', body = request, headers = headers)
    
