import cherrypy
import os, os.path
import jinja2
import requests
import json
import cgi
import tempfile
from shutil import move
from mimetypes import guess_type as getType

staticRoot = os.path.dirname(os.path.abspath(os.getcwd()))
staticPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'static/')
templates = jinja2.Environment(loader=jinja2.FileSystemLoader(staticPath+'html'))
syncIp = "127.0.0.1:8888"
syncAddr = "http://"+syncIp+"/api"
class FileFieldStorage(cgi.FieldStorage):
	def make_file(self,binary=None):
		return tempfile.NamedTemporaryFile()
def noBodyProcess():
	cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)
class Main(object):
	@cherrypy.expose
	def index(self):
		indexTemplate = templates.get_template('index.html')
		# return staticPath+'html'+' | '+staticRoot
		folders = self.btSync(method='get_folders')
		return indexTemplate.render(folders=json.loads(folders))
	@cherrypy.expose
	def folder(self,*args):
		indexTemplate = templates.get_template('index.html')
		if len(args)==0:
			path=''
		else:
			files = None
			path = '/'.join(args)
			if path[0]!='/':
				path = '/'+path
			secrets = json.loads(self.btSync(method='get_folders'))
			secret = None
			for item in secrets:
				if item['dir'] in path:
					secret = item['secret']
					path=path.replace(item['dir'],"")
		files = self.btSync(method='get_files',secret=secret,path=path)
		return indexTemplate.render(folders=json.loads(files))
	@cherrypy.expose
	def dirExists(self,path,create=False):
		if type(create)!=bool:
			if create.lower() == 'false':
				create = False
			elif create.lower() == 'true':
				create = True
		if os.path.exists(path) and os.path.isdir(path):
			return 'true'
		elif create and not os.path.exists(path):
			check = os.path.abspath(os.path.join(path, os.pardir))
			if (os.access(path,os.R_OK) and os.access(path,os.W_OK)) or (os.access(check,os.R_OK) and os.access(check,os.W_OK)):
				os.makedirs(path)
				return 'true'
			else:
				return 'notAllowed'
		else:
			return 'false'
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
			if self.pathInSync(path):
				f = file(path)			
				cherrypy.response.headers['Content-Type'] = getType(path)[0]
				return f
			else:
				raise cherrypy.HTTPError(403)
		except IOError:
			return json.dumps({'Error':"File doesn't exist."})
	def pathInSync(self,path):
		result = json.loads(self.btSync(method='get_folders'))
		folders = [item['dir'] for item in result]
		for item in folders:
			if item in path:
				return True
		return False
	def pathExists(self,path,removeFileName=True):
		if removeFileName:
			q = path.split('/')
			del q[len(q)-1]	
			path = '/'.join(q[:len(q)-2])
		if self.dirExists(path) or (os.path.exists() and os.path.isfile(path)):
			return True
		return False
	@cherrypy.expose
	@cherrypy.tools.noBodyProcess()
	def upload(self,f=None,path=None):
		# f.seek(0,0)
		h = {}
		for key in cherrypy.request.headers:
			h[key.lower()] = cherrypy.request.headers[key]
		formFields = FileFieldStorage(fp=cherrypy.request.rfile,headers=h,environ={'REQUEST_METHOD':'POST'},keep_blank_values=True)
		if 'f' in formFields and 'path' in formFields:
			f = formFields['f']
			path = formFields.getvalue('path')
			if self.pathInSync(path) and self.pathExists(path):
				if hasattr(f.file,'name'):
					move(f.file.name,path)
				else:
					f = open(path,'w')
					f.file.seek(0,0)
					f.write(f.file.read())
					f.close()
			else:
				raise cherrypy.HTTPError(400,message="path is not valid")
		else:
			raise cherrypy.HTTPError(400,message="f and or path were not found in your request")
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
application = cherrypy.tree.mount(Main(),'/',config=config)
if __name__=='__main__':
	cherrypy.engine.start()
	cherrypy.engine.block()

	cherrypy.server.socket_host='0.0.0.0'
	
	