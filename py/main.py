import cherrypy
from auth import Secret,SecretRequest
import os, os.path
staticRoot = os.path.dirname(os.path.abspath(os.getcwd()))
staticPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'static/')
class Main(object):
	# secret = SecretRequest
	def __init__(self):
		self.secret = SecretRequest()
	@cherrypy.expose
	def index(self):
		return file(staticPath+'html/index.html')
if __name__=='__main__':
	config = {
		'/':{
			'tools.sessions.on':True,
			'tools.staticdir.root':staticRoot,
		},
		'/secret':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
			'tools.response_headers.on':True,
			'tools.response_headers.headers': [('Content-Type', 'text/plain')],
		},
		'/static':{
			'tools.staticdir.on':True,
			'tools.staticdir.dir':'./static/'
		}
	}
	cherrypy.tree.mount(Main(),'/',config=config)
	cherrypy.engine.start()
	cherrypy.engine.block()