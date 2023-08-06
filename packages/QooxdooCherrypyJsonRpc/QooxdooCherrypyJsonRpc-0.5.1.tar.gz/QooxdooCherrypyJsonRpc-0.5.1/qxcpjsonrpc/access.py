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


  This module provides accessibilty and access control classes and decorators.

  According to the Apache httpd manual:

  http://httpd.apache.org/docs/1.3/howto/auth.html

    Apache has three distinct ways of dealing with the question of whether a
    particular request for a resource will result in that resource actually be
    returned. These criteria are called Authorization, Authentication, and
    Access control.
  
    Authentication is any process by which you verify that someone is who they
    claim they are. This usually involves a username and a password, but can
    include any other method of demonstrating identity, such as a smart card,
    retina scan, voice recognition, or fingerprints. Authentication is
    equivalent to showing your drivers license at the ticket counter at
    the airport.
  
    Authorization is finding out if the person, once identified, is permitted
    to have the resource. This is usually determined by finding out if that
    person is a part of a particular group, if that person has paid admission,
    or has a particular level of security clearance. Authorization is
    equivalent to checking the guest list at an exclusive party, or checking
    for your ticket when you go to the opera.
  
    Finally, access control is a much more general way of talking about
    controlling access to a web resource. Access can be granted or denied
    based on a wide variety of criteria, such as the network address of the
    client, the time of day, the phase of the moon, or the browser which the
    visitor is using. Access control is analogous to locking the gate at closing
    time, or only letting people onto the ride who are more than 48 inches
    tall - it's controlling entrance by some arbitrary condition which may or
    may not have anything to do with the attributes of the particular visitor.

  The JSON-RPC server itself does not provide any fixed authentication or
  authorization scheme.

  Authentication should be done by the application (service) before the client
  tries to access protected content.

  Access control can be used to allow or deny calling of methods. Undecorated
  methods cannot be called by the JSON-RPC clients. All externally accessible
  methods must be marked with access control decorators. Default decorators
  specify basic access rights:

    public : any client can call this method
    fail   : the method cannot be called (access denied)

  Complex access rights depending on authenticated user, the client's address
  or anything else can be added by providing a simple access check function,
  such as:

  def isAdmin(method, request):
    """Access is granted only to administrator"""
    return cherrypy.request.login == 'admin'

  Usage:

  @access(isAdmin)
  def restrictedMethod(...):
    ...

  Access checkers can be chained by simply using more decorators. Access is
  granted if **all** checkers allow it. For example:

  @access(isUser)
  @access(isAdmin)
  def userMethod(...):
    ...

  Methods can be temporarily disabled this way (for debugging, etc.):

  @fail
  @allOtherDecorators
  def fn(...):
    ...

  This module is NOT intended for direct import. Import symbols from qxcpjsonrpc.

'''


__all__ = 'access', 'public', 'fail', 'MethodAccessibility', 'MethodAuthorization'


class MethodAccessibility:
  '''Method Accessibility values'''

  @staticmethod
  def Public(method, request):
    return True

  @staticmethod
  def Fail(method, request):
    return False

  default = Fail
  '''Default accessibility for undecorated methods'''


class MethodAuthorization:

  CheckerAttributeName = '_qxcpjsonrpc_access_checkers_'
  '''Method attribute name for the access checker list'''

  default = [MethodAccessibility.default]
  '''Default checkers for undecorated methods'''


  @classmethod
  def getCheckers(cls, method):
    '''Get access checker list of the passed method'''
    
    return getattr(method, cls.CheckerAttributeName, cls.default)

  @classmethod
  def append(cls, fn, checker):
    '''Adds access checker to the function's list'''

    if not hasattr(fn, cls.CheckerAttributeName):
      setattr(fn, cls.CheckerAttributeName, [])
      
    getattr(fn, cls.CheckerAttributeName).append(checker)

  @classmethod  
  def authorize(cls, method, request):
    '''Check if access is allowed'''
    
    return all(ac(method, request) for ac in cls.getCheckers(method))


def access(accessChecker):
  '''Generic decorator to define method accessibility. Access checker is a 
  function with args (method, request) that returns True if access is granted 
  to the passed method for the request specified, False otherwise.'''

  def f(fn):
    MethodAuthorization.append(fn, accessChecker)
    return fn

  return f

public = access(MethodAccessibility.Public)
'''The decorated method may be called from any session, and without any
checking of who the referer is. Access is granted.'''

fail = access(MethodAccessibility.Fail)
'''Access is explicitly denied.'''

