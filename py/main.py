import cherrypy
import auth
import os, os.path
import jinja2
staticRoot = os.path.dirname(os.path.abspath(os.getcwd()))
staticPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'static/')
templates = jinja2.Environment(loader=jinja2.FileSystemLoader(staticPath+'html'))

class Main(object):
	# secret = SecretRequest
	def __init__(self):
		self.secret = auth.SecretRequest()
	@cherrypy.expose
	def index(self):
		indexTemplate = templates.get_template('index.html')
		return indexTemplate.render()
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