#! /usr/bin/python
"""
This script is based on https://github.com/akamai-open/api-kickstart
"""
import ConfigParser,sys,requests, json
from akamai.edgegrid import EdgeGridAuth
from os	import path
from urlparse import urljoin
from pprint import pprint

home = path.expanduser("~")
config_file = "%s/.edgerc" % home
block = "user"
filename = "/tmp/akamai"


def usage (command=""):
	if command in ["test"]:
		print "Usage: %s %s" % (str(sys.argv[0]),str(command))
	elif command in ["command"]:
		print "Usage: %s %s [command]" % (str(sys.argv[0]),str(command))
	elif command in ["config","initiate"]:
		print "Usage: %s %s block [filename]" % (str(sys.argv[0]),str(command))
	elif command in ["export_users","export_groups","export_roles","export_all"]:
		print "Usage: %s %s [filename [config_file[contract]]]" % (str(sys.argv[0]),str(command))
	elif command == "config":
		print "Usage: %s %s" % (str(sys.argv[0]),str(command))
	elif command == "config":
		print "Usage: %s %s" % (str(sys.argv[0]),str(command))
	else:
		print "Usage: %s help|config|initiate|test|export_users|export_groups|export_roles|export_all [argvs]" % str(sys.argv[0])

class BlankDict(dict):
        def __missing__(self, key):
            return ''

class AKAMAI:
	def __init__(self,block,config_file,contract=""):
		filename = config_file
		self.contract = ""
		if not path.exists(filename):
			sure = ""
			while sure !="y" and  sure !="yes":
				sure = raw_input("This Config file don\'t exist. Do you want create it (y/n)?").lower().strip()
				if sure in ["n","no"]:
					print "Exit. Please review filename for configuration"
					exit(4)

			print "Creating config file"
			self.install(block,filename,contract)
		if path.isfile(config_file):
			try:
				config = ConfigParser.ConfigParser()
				config.readfp(open(config_file))
				config.items(block)
			except(ConfigParser.NoSectionError):
				sure = ""
				while sure !="y" and sure !="yes":
					sure = raw_input("Section don\'t exists. Do you want create it (y/n)?").lower().strip()
					if sure == "no" or sure == "n":
						print "Exit. Please review config file in %s" % config_file
						exit(5)
				contract = ""
				print "Creating section"
				if block == "papi":
					contract = ""
				else:
					while contract == "":
						Config = ConfigParser.ConfigParser()
						Config.read(filename)
						if "papi" in Config.sections():
							message = "Do you want Auto Search your contract?\n"
							message += "This requires papi section: "
							sure = raw_input(message).lower().strip()
							if sure in ["yes","y"]:
								contract = AKAMAI("papi",config_file).search_contract()
							if sure in ["no","n"]:
								message = "Insert your contract please:"
								contract = raw_input(message).lower().strip()
							if " " in contract:
								contract = ""
						else:
							message = "Insert your contract please:"
							contract = raw_input(message).lower().strip()
							if " " in contract:
								contract = ""

				self.install(block,filename,contract)
				config = ConfigParser.ConfigParser()
				config.readfp(open(config_file))				
			self.session = ""
			for key, value in config.items(block):
				# ConfigParser lowercases magically
				if key == "client_secret":
					self.client_secret = value
				elif key == "contract":
					self.contract = value
				elif key == "access_token":
					self.access_token = value
				elif key == "client_token":
					self.client_token = value
				elif key == "host":
					self.host = value
				else:
					print "I have no mapping for %s" % key
		else:
			print "Missing configuration file."
			exit()

	def install(self,block,filename,contract):
		Config = ConfigParser.ConfigParser()
		config_items = ["host","access_token","client_secret","client_token"]
		print "Take yours API information from luna control center"
		print "You will need host, access_token, client_secret, client_token"
		# First, if we have a 'default' section protect it here
		if not path.exists(filename):
			myfile = open (filename, "w")
			myfile.write("\n")
			myfile.close()
		with open (filename, "r") as myfile:
 			data=myfile.read().replace('default','----DEFAULT----')
			myfile.close()
		with open (filename, "w") as myfile:
			myfile.write(data)
			myfile.close()

		Config.read(filename)
		config = open(filename,'w')

		if block in Config.sections():
			print "\n\nReplacing section: %s" % block
			Config.remove_section(block)
		else:
			print "\n\nCreating section: %s" % block

		Config.add_section(block)

		for i in config_items:
			var = ""
			while not var:
				message = "Insert your %s please:" % i
				var = raw_input(message).replace("https://", "").replace("/", "").strip()
				if " " in var:
					print "Error"
					var = ""
				else:
					if i == "client_secret":
						Config.set(block,'client_secret',var)
					elif i == "host":
						Config.set(block,'host',var)
					elif i == "access_token":
						Config.set(block,'access_token',var)
					elif i == "client_token":
						Config.set(block,'client_token',var)

		if block != "papi":
			Config.set(block,'contract',contract)

		Config.write(config)
		config.close ()
		config.close ()
		with open (filename, "r") as myfile:
 			data=myfile.read().replace('----DEFAULT----','default')
			myfile.close()
		with open (filename, "w") as myfile:
			myfile.write(data)
			myfile.close()

	def connection(self,block="----DEFAULT----"):
		self.baseurl = '%s://%s/' % ('https', self.host)
		self.session = requests.Session()
		self.session.auth = EdgeGridAuth(self.client_token,self.client_secret,self.access_token)

	def get_info(self,url):
		if not self.session:
			self.connection()
		endpoint_result = self.session.get(urljoin(self.baseurl,url))
	 	result = endpoint_result.json()
	 	dump = json.loads(json.dumps(result), object_hook=BlankDict)
	 	return dump

	def search_contract(self):
		url = "/papi/v0/contracts/"
		result = self.get_info(url)
		contract = result["accountId"].replace("act_", "")
		return contract

	def export_info(self,url,args,filename=""):
		if not filename:
			print "You need to specify a file to export users"
			exit (2)
		if path.exists(filename):
			sure = ""
			while sure !="y" and sure !="n" and sure !="no" and sure !="yes":
				sure = raw_input("This file ("+filename+") exists. Do you want to overwrite it(y/n)? ").lower().strip()
			if sure == "no" or sure == "n":
				print "Exit. Please review filename for exporting users"
				exit(3)
			else:
				print "Exporting..."
		result = self.get_info(url)
		try:	
			if str(result["httpStatus"]) == "403" or str(result["status"]) == "403":
				print "Permisions Error"
				raise SystemExit
			if str(result["status"]) == "401":
				print "Permisions Error"
				raise SystemExit
	 	except (TypeError):
			pass
		with open (filename, "w") as myfile:
			exportados=0
			cabecera = ""
			for i in args:
				if i == "roleAssignments":
					i = "roleName;groupName"
				cabecera = cabecera + i + ";"
			cabecera = cabecera + "\n"
			myfile.write(cabecera)
			while result:
				line = ""
				record = result.pop()
				if "roleAssignments" in args:
					roles = record["roleAssignments"]
					while roles:
						exportados += 1
						role = roles.pop()
						roleName = str(role["roleName"])
						groupName = str(role["groupName"])
						line = ""
						for i in args:
							if i == "lastLoginDate":
								if record[i]:
									line = line + str(record[i]) + ";"
								else:
									line = line + "NEVER;"
							elif i == "roleAssignments":
								line = line + roleName + ";" + groupName + ";"
							elif i == "roleDescription":
								for char in "'":
									record[i] = record[i].replace(char,'')
									record[i] = record[i].replace(u'\x9d',"")
								line = line + str(record[i]) + ";"
							else:
								line = line + str(record[i]) + ";"
						line = line + "\n"
						myfile.write(line)
				else:
					exportados += 1
					line = ""
					for i in args:
						if i == "lastLoginDate":
							if record[i]:
								line = line + str(record[i]) + ";"
							else:
								line = line + ";"
						elif i == "roleDescription":
							for char in "'":
								record[i] = record[i].replace(char,'')
								record[i] = record[i].replace(u'\x9d',"")
							line = line + str(record[i]) + ";"
						else:
							line = line + str(record[i]) + ";"
						line = line + "\n"
						myfile.write(line)
			print "Exported %i lines in %s" % (exportados,filename)		
	


	def export_userscsv (self,filename=""):
		url  = '/user-admin/v1/accounts/'+self.contract+'/users'
		args = ["username","firstName","lastName","phone","contactId","userType","tfaEnabled","tfaConfigured","lastLoginDate","email","roleAssignments"]
		self.export_info(url,args,filename)

	def export_groupscsv (self,filename=""):
		url = '/user-admin/v1/accounts/'+self.contract+'/groups'
		args =["createdBy","topLevelGroup","groupName","parentGroupId","accountId","groupId","createdDate"]
		self.export_info(url,args,filename)


	def export_rolescsv (self,filename=""):
		url = '/user-admin/v1/accounts/'+self.contract+'/roles'
		args = ["roleId","contractTypeId","roleDescription","modifiedBy","modifiedDate","numUsers","type"]
		self.export_info(url,args,filename)


	def export_allcsv (self,filename=""):
		filename_users=filename+"_users"
		self.export_userscsv(filename_users)
		filename_groups=filename+"_groups"
		self.export_groupscsv(filename_groups)
		filename_roles=filename+"_roles"
		self.export_rolescsv(filename_roles)



## Codigo por defecto
if len(sys.argv)>1:
	command = str(sys.argv[1]).lower()
	# Data Validation
	if command in ["test"]:
		arg = [2]
	elif command in ["help"]:
		arg = [2,3]
	elif command in ["config","initiate"]:
		arg = [3,4]
	elif command in ["export_roles","export_groups","export_users","export_all"]:
		arg = [3,4,5]
	else:
		arg = []
		usage()

	if not (len(sys.argv) in arg):
		usage(command)
		exit (99)

	if command == "help":
		if len(sys.argv) == 2:
			usage()
		else:
			command = sys.argv[2]
			usage(command)
	elif command in ["config","initiate"]:
		block = sys.argv[2]
		if len(sys.argv) == 4:
			config_file = sys.argv[3]
		AKAMAI_INSTANCE = AKAMAI (block,config_file)
	elif command in ["export_roles","export_groups","export_users","export_all"]:
		if len(sys.argv) == 3:
			filename = sys.argv[2]
		elif len(sys.argv) == 4:
			filename = sys.argv[2]
			config_file = sys.argv[3]
		elif len(sys.argv) == 5:
			filename = sys.argv[2]
			config_file = sys.argv[3]
			contract = sys.argv[4]
		if command == "export_users":	
			AKAMAI_INSTANCE = AKAMAI (block,config_file).export_userscsv(filename)
		elif command == "export_groups":	
			AKAMAI_INSTANCE = AKAMAI (block,config_file).export_groupscsv(filename)
		elif command == "export_roles":	
			AKAMAI_INSTANCE = AKAMAI (block,config_file).export_rolescsv(filename)
		elif command == "export_all":	
			AKAMAI_INSTANCE = AKAMAI (block,config_file).export_allcsv(filename)
	elif command == "test":
		pass
else:
		usage ()
		exit (99)




