import requests

try:
	import simplejson as json
except ImportError:
	import json
try:
	from .access import main as login 

except:
	from access import main as login 

API_URL='https://api.github.com'

class GitHubGist(object):
	def __init__(self,username,password):
		self.accessToken=login(username,password)
	
	@staticmethod
	def Gist(description,content,name,token=None):
		public=True
		url=API_URL+'/gists'

		if token is None:
			authtoken=None
		else:
			authtoken=token
		token='token {0}'.format(authtoken)
		data=json.dumps({"description":description,"public":public,"files":{name:{"content":content}}})

		if token is None:
			r=requests.post(url,data=data)
		else:
			r=requests.post(url,headers={'Authorization':token},data=data)

		uniqueID=r.json()['url']
		gistLink="http://gist.github.com/{0}".format(uniqueID.split('/')[-1])
		return gistLink
	@staticmethod
	def GistFromFile(description,file):
		with open(file,'r') as f:
			content=f.read()
		return self.Gist(description,content,file)
	def createGist(self,description,content,name):
		return self.Gist(description,content,name,self.accessToken)
	def createGistFromFile(self,description,file):
		with open(file,'r') as f:
			content=f.read()
		return self.Gist(description,content,file,self.accessToken)
	@staticmethod
	def getGistsLinks(username):
		url='{0}/users/{1}/gists'.format(API_URL,username)
		data=requests.get(url).json()
		return [a['url'] for a in data]
	@staticmethod
	def getGistsData(username):
		url='{0}/users/{1}/gists'.format(API_URL,username)
		data=requests.get(url).json()
		return data
		
if __name__=='__main__':
	github = GitHubGist(username='geekpradd',password='Armyschool123')
	link = github.getGists('geekpradd')
	print(link)