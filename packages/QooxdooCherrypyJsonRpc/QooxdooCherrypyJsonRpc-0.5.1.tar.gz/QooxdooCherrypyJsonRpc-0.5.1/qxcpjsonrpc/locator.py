'''

  QooxdooCherrypyJsonRpc

  License:
    LGPL: http://www.gnu.org/licenses/lgpl.html
    EPL: http://www.eclipse.org/org/documents/epl-v10.php

  Authors:
    * saaj (mail@saaj.me)


  Service locator module. It is responsibe for finding the service by its 
  full path, for example ``path.to.my.Service``, and calling requested method
  with all the required error handling and access control. 
  
  This module is NOT intended for direct import. Import symbols from qxcpjsonrpc.

'''


import sys
import importlib

from .error import Error, ApplicationError, PermissionDeniedError
from .error import ServiceNotFoundError, ClassNotFoundError, MethodNotFoundError
from .access import MethodAuthorization


__all__ = 'ServiceLocator',


class ServiceLocator(object):
  
  __cache = {}
  '''Service class cache'''
  
  
  def callFrom(self, request):
    '''Find service and method from request attributes, check access, 
    invoke with dispatch hooks, handle errors, return result'''
    
    # Whether ``serviceObj.onException(ex)`` was called
    exceptionPassed = False 
    
    serviceObj = self._getService(request.service)
    try:
      methodObj = self._getMethod(serviceObj, request.method)
  
      # Authorize access using method access checkers
      if not MethodAuthorization.authorize(methodObj, request):
        raise PermissionDeniedError('Access denied on "{0}"!'.format(request.method))
  
      # Build positional and keyword arguments passed to the method, sanitized in server.Request.load
      if isinstance(request.params, list):
        args   = request.params
        kwargs = {}
      elif isinstance(request.params, dict):
        args   = []
        kwargs = request.params

      # Call method with hooks
      serviceObj.preDispatch(request, methodObj)
      try:
        return methodObj(*args, **kwargs)
      except Exception as ex:
        serviceObj.onException(ex)
        exceptionPassed = True
        raise
      finally:
        serviceObj.postDispatch(request, methodObj)
    except Error as ex:
      if not exceptionPassed:
        serviceObj.onException(ex)
      # Bypass package internal errors
      raise
    except Exception as ex:
      if not exceptionPassed:
        serviceObj.onException(ex)
      # Wrap system errors
      if sys.version_info >= (3,):
        raise ApplicationError(ex).with_traceback(sys.exc_info()[2])
      else:
        exec('raise ApplicationError, ex, sys.exc_info()[2]')
  
  def _loadClass(self, fullName):
    '''Retrieve a class object from a full dotted-package-class name'''

    # Parse out module and class
    lastDot = fullName.rfind(u'.')
    if lastDot != -1:
      className  = fullName[lastDot + 1:]
      moduleName = fullName[:lastDot]
    else:
      raise ServiceNotFoundError('Ambiguous service "{0}"!'.format(fullName))

    moduleObj = self._loadModule(moduleName)
    
    try:
      classObj = getattr(moduleObj, className)
    except AttributeError:
      raise ClassNotFoundError('Can not get class "{0}" from "{1}"!'.format(className, moduleName))

    from .server import Service
    if not issubclass(classObj, Service):
      raise ClassNotFoundError('"{0}" is not a RPC service!'.format(fullName))

    return classObj

  def _loadModule(self, modulePath):
    '''Import a module programmatically'''
    
    try:
      moduleObj = sys.modules[modulePath]
    except KeyError:
      try:
        moduleObj = importlib.import_module(modulePath)
      except ImportError:
        raise ServiceNotFoundError('Module "{0}" not found!'.format(modulePath))

    return moduleObj
  
  def _getService(self, name):
    '''Get service by full name. Note that cached are service classes, not service instances.'''
    
    if name not in self.__cache:
      self.__cache[name] = self._loadClass(name)

    return self.__cache[name]()
        
  def _getMethod(self, serviceObj, methodName):
    '''Get method by name from service object'''

    try:
      methodObj = getattr(serviceObj, methodName)
      
      if not callable(methodObj):
        values = methodObj, serviceObj
        raise MethodNotFoundError('Method {0!r} in service {1!r} is not callable!'.format(*values))
      
      return methodObj
    except AttributeError:
      values = methodName, serviceObj
      raise MethodNotFoundError('Method "{0}" not found in service {1!r}!'.format(*values))

