import cherrypy
import os, os.path
import jinja2
import requests
import json
from mimetypes import guess_type as getType

staticRoot = os.path.dirname(os.path.abspath(os.getcwd()))
staticPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'static/')
templates = jinja2.Environment(loader=jinja2.FileSystemLoader(staticPath+'html'))
syncIp = "127.0.0.1:8888"
syncAddr = "http://"+syncIp+"/api"
class Main(object):
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
	@cherrypy.expose
	def getFile(self,*args):
		try:
			path = '/'.join(args)
			#A fix to start at the root of the drive.
			if path[0]!='/':
				path = '/'+path
			print path
			if self.pathInSync(path):
				f = file(path)			
				cherrypy.response.headers['Content-Type'] = getType(path)[0]
				return f
			else:
				print 'nope'
				raise cherrypy.HTTPError(403)
		except IOError:
			print "hm"
			return json.dumps({'Error':"File doesn't exist."})
	def pathInSync(self,path):
		result = json.loads(self.btSync(method='get_folders'))
		folders = [item['dir'] for item in result]
		for item in folders:
			if item in path:
				return True
		return False
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
	cherrypy.server.socket_host='0.0.0.0'
	cherrypy.tree.mount(Main(),'/',config=config)
	cherrypy.engine.start()
	cherrypy.engine.block()