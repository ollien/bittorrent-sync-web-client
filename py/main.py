
import cherrypy
import os, os.path
import jinja2
import requests
import json
import cgi
import tempfile
import re
import uuid
from shutil import move


staticRoot = os.path.dirname(os.path.abspath(os.getcwd()))
staticPath = os.path.join(os.path.dirname(os.path.abspath(os.getcwd())),'static/')
templates = jinja2.Environment(loader=jinja2.FileSystemLoader(staticPath+'html'))
syncIp = "127.0.0.1:8888"
syncAddr = "http://"+syncIp+"/api"
basePath = "/mnt/bakery" # A specific string that is needed to be stripped from my file path
publicPath = "public/" #The location of all public symlinks
class FileFieldStorage(cgi.FieldStorage):
	def make_file(self,binary=None):
		return tempfile.NamedTemporaryFile(delete=True)
def noBodyProcess():
	cherrypy.request.process_request_body = False

cherrypy.tools.noBodyProcess = cherrypy.Tool('before_request_body', noBodyProcess)
class Main(object):
	@cherrypy.expose
	def index(self):
		return self.folder();
		# indexTemplate = templates.get_template('index.html')
		# return staticPath+'html'+' | '+staticRoot
		# folders = self.btSync(method='get_folders')
		# return indexTemplate.render(folders=json.loads(folders))
	@cherrypy.expose
	def folder(self,*args):
		indexTemplate = templates.get_template('index.html')
		response = None
		if len(args)==0:
			path=''
			response = self.btSync(method='get_folders')
			response = json.loads(response)
			response = sorted(response, key=lambda k: k['dir'])
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
			response = self.btSync(method='get_files',secret=secret,path=path)
			response = json.loads(response)	
			response = sorted(response, key=lambda k: k['name'])
		return indexTemplate.render(folders=response)
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
					# return cherrypy.lib.static.serve_file(path,"application/x-download",os.path.basename(path))
					# cherrypy.response.headers.clear()
					# cherrypy.response.headers['X-Sendfile'] = os.path.basename(path)
					# cherrypy.response.status = 200
					p = path.replace(basePath,"")
					cherrypy.response.headers.update({
					  'X-Accel-Redirect'    : '/download/{0}'.format(p),
					  'Content-Disposition' : 'attachment; filename={0}'.format(os.path.basename(path)),
					  'Content-Type'        : 'application/octet-stream'
					})
					# return "goign"
				# f = file(path)
				# cherrypy.response.headers['Content-Type'] = getType(path)[0]
				# return f
			else:
				raise cherrypy.HTTPError(403)
		except IOError,e:
			return json.dumps({'Error':"IO Error. "+str(e)})
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
	def manualListDir(self,path):
		indexTemplate = templates.get_template('index.html')
		if self.pathInSync(path):
			folders = os.listdir(path)
			return indexTemplate.render(folders=None)
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
			search = re.search('------WebKitFormBoundary.{16}--\Z',path)
			if search != None:
				path = path.replace(search.group(),'')
			path = path.rstrip()
			if self.pathInSync(path) and self.pathExists(path):
				if hasattr(f.file,'name'):
					move(f.file.name,path)
					os.chmod(path,0776)
					# os.remove(f.file.name)
					return 'moved.'
			else:
				raise cherrypy.HTTPError(400,message="path is not valid")
		else:
			raise cherrypy.HTTPError(400,message="f and or path were not found in your request")
	@cherrypy.expose
	def 	file_exists(self,path):
		if os.path.exists(path):
			return 'true'
		return 'false'
	@cherrypy.expose
	def find_secret(self,path):
		secrets = json.loads(self.btSync(method='get_folders'))
		for item in secrets:
			if item['dir'] in path:
				return item['secret']
	@cherrypy.expose
	def delete(self,path):
		if self.pathInSync(path):
			os.remove(path)
			return json.dumps({"error":0})
		return json.dumps({"error":1})
	def fileInPublic(self,path):
		p = os.path.join(basePath,publicPath)
		if p in path:
			return True
		else:
			return False
	@cherrypy.expose
	def public(self,f):
		path = os.path.join(basePath,publicPath,f)
		if self.fileInPublic(path):
			try:
				os.stat(path)
			except OSError:
				return "File does not exist."
			cherrypy.response.headers.update({
			  'X-Accel-Redirect'    : '/download/'+os.path.join(publicPath,f),
			  'Content-Disposition' : 'attachment; filename='+os.path.basename(os.readlink(path)),
			  'Content-Type'        : 'application/octet-stream'
			})		
			# return "boom goes the dynamite!"
		else: #This shoudl never actually happen, but it's just a safeguard.
			return "File is not shared publicly"
	@cherrypy.expose
	def makePublic(self,path):
		if self.pathInSync(path):
			uid = uuid.uuid4().hex
			p = os.path.join(basePath,publicPath,'1234')
			os.symlink(path,os.path.join(basePath,publicPath,uid))
			return json.dumps({"error":0,"url":'/public/'+uid})
		return json.dumps({"error":1})
config = {
	'/':{
		'tools.staticdir.root':staticRoot,
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
	
	