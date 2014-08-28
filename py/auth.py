import cherrypy
import json
class Secret(object):
	def __init__(self,secret=None):
		self.secret=secret
	def __repr__(self):
		return self.secret
	__str__=__repr__
class SecretRequest(object):
	def __init__(self):
		secret = None
	exposed = True
	@cherrypy.tools.accept(media='text/plain')
	def GET(self):
		if secret!=None:
			return str(self.secret)
		else:
			return json.loads({'Error':'No Secret set.'})
	def POST(self,**kwargs):
		if 'secret' in kwargs:
			self.secret = kwargs['secret']
			self.syncSecret()
			return json.loads({'Success':''})
		else:
			return json.loads({'Error':'No Key Provided'}) 
	def syncSecret(self):
		cherrpy.session['secret']=self.secret
	