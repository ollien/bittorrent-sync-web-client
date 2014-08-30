import cherrypy
import auth
import os, os.path
import jinja2
import requests
import json

staticRoot = os.path.dirname(os.path.abspath(os.getcwd()))
staticPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'static/')
templates = jinja2.Environment(loader=jinja2.FileSystemLoader(staticPath+'html'))
syncIp = "127.0.0.1:8888"
syncAddr = "http://"+syncIp+"/api"
class Main(object):
	# secret = SecretRequest
	def __init__(self):
		self.secret = auth.SecretRequest()
	@cherrypy.expose
	def index(self):
		indexTemplate = templates.get_template('index.html')
		folders = self.btSync(method='get_folders')
		return indexTemplate.render(folders=json.loads(folders))
	@cherrypy.expose
	def folder(self,secret,path=""):
		indexTemplate = templates.get_template('index.html')
		files = self.btSync(method='get_files',secret=secret,path=path)
		return indexTemplate.render(folders=json.loads(files))
	@cherrypy.expose
	def hello(self):
		return "hello world"
	@cherrypy.expose(['sync'])
	#BitTorrentSync API, pass in variables for the methods, eg method=get_folders and secret=secret
	def btSync(self,**kwargs):
		r = requests.get(syncAddr,params=kwargs)
		return r.text
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