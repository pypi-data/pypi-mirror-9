'''
@author: saaj
'''


import cherrypy
import qxcpjsonrpc as rpc


class Test(rpc.Service):

  @rpc.public
  def add(self, x, y):
    return x + y


config = {
  '/service' : {
    'tools.jsonrpc.on' : True
  },
  '/resource' : {
    'tools.staticdir.on'  : True,
    'tools.staticdir.dir' : '/path/to/your/built/qooxdoo/app'
  }
}


if __name__ == '__main__':
  cherrypy.tools.jsonrpc = rpc.ServerTool()
  cherrypy.quickstart(config = config)
  
