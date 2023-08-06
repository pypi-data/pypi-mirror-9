from cmd2 import *
import requests
from types import MethodType
import readline
import json
import texttable

class stratos(Cmd):
	"Apache Stratos CLI"
	__username = ""
	__password = ""
	__auth = False

	prompt = 'stratos> '
	#Cmd.intro = ""
	Cmd.legalChars = '-'+Cmd.legalChars
	
	#debug = True
	
	Cmd.shortcuts.update({'create-tenant': 'create_tenant'})
	Cmd.shortcuts.update({'deploy-service': 'deploy_service'})
	Cmd.shortcuts.update({'deploy-user': 'deploy_user'})
	Cmd.shortcuts.update({'list-applications': 'list_applications'})
	Cmd.shortcuts.update({'list-service': 'list_service'})
		
	def auth(func):
		"Authenticate"
		def inner(self, *args, **kwargs): #1
			if(self.__auth):
				print "Authenticate"
				return func(self, *args, **kwargs) #2
			else:
				print "Not-Authenticated"
		return inner
		
	def completenames(self, text, *ignored):
		return [a[3:].replace('_','-') for a in self.get_names() if a.replace('_','-').startswith('do-'+text)]



#CLI Commands

	#Command create-tenant
	@options([
		make_option('-u', '--username', type="str", help="Username given to the Tenant"),
		make_option('-f', '--firstname', type="str", help="Tenant's first name"),
		make_option('-l', '--lastname', type="str", help="Tenant's last name"),
		make_option('-p', '--password', type="str", help="Tenant's password"),
		make_option('-d', '--domainname', type="str", help="Tenant's domain name"),
		make_option('-e', '--email', type="str", help="Tenant's email address")
	])
	def do_create_tenant(self, line , opts=None):
		"""Add a tenant with the username: admin, name: Frank Myers,  password: admin123, tenant domain: frank.com and email: foo@bar.com.
		
		eg: create-tenant -u admin -f Frank -l Myers -p admin123 -d frank.com -e foo@bar.com
		"""
		if(opts.username and opts.firstname and opts.lastname and opts.password and opts.domainname and opts.email):
			print("Tenant added successfully. \n Domain:  %s , Username:  %s  " % (opts.domainname, opts.username))
		else:
			print("Some required argument(s) missing")
	@auth
	def do_deploy_service(self, line , opts=None):
		"Illustrate the base class method use."
		print 'hello service'
		
	def do_deploy_user(self, line , opts=None):
		"Illustrate the base class method use."
		print 'hello User'
		
	#Command respositories
	@options([
		make_option('-u', '--username', type="str", help="Username of the user"),
		make_option('-p', '--password', type="str", help="Password of the user")
	])
	def do_user(self, line , opts=None):
		"""Shows the git repositories of the user identified by given username and password.
		
		eg: user -u agentmilindu  -p agentmilindu123
		"""
		if(opts.username and opts.password):
			r = requests.get('https://api.github.com/users/'+opts.username, auth=(opts.username, opts.password))
			user = r.json()
			print('Hi '+user['name']+'! Your email address is '+user['email']+', right? :)')
			
		else:
			print("Some required argument(s) missing")
			
	#Command respositories
	@options([
		make_option('-u', '--username', type="str", help="Username of the user"),
		make_option('-p', '--password', type="str", help="Password of the user")
	])
	def do_repositories(self, line , opts=None):
		"""Shows the git repositories of the user identified by given username and password.
		
		eg: repositories -u agentmilindu  -p agentmilindu123
		"""
		if(opts.username and opts.password):
			r = requests.get('https://api.github.com/users/'+opts.username+'/repos?per_page=5', auth=(opts.username, opts.password))
			repositories = r.json()
			print(json.dumps(repositories))
			for repo in repositories:
				print(repo['name']+" "+repo['language'])
			
		else:
			print("Some required argument(s) missing")


	def do_auth(self, line):
		"Exit"
		self.__auth = True
		
	def do_EOF(self, line):
		"Exit"
		return True
		
	
	
def main():
	readline.set_completer_delims(readline.get_completer_delims().replace('-', ''))
	strts = stratos()

	if len(sys.argv) > 1:
		
		strts.onecmd(' '.join(sys.argv[1:]))
	else:
		#username =  input("Username: ")
		strts.cmdloop()
		#print(username)

if __name__ == '__main__':
	import sys
	main()
