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


class BlankDict(dict):
        def __missing__(self, key):
            return ''

class AKAMAI:
	def __init__(self,block,config_file,contract=""):
		filename = config_file
		if not path.exists(filename):
			sure = ""
			while sure !="y" and sure !="n" and sure !="no" and sure !="yes":
				sure = raw_input("This Config file don\'t exist. Do you want create it (y/n)?").lower().strip()
			if sure == "no" or sure == "n":
				print "Exit. Please review filename for exporting users"
				exit(4)
			else:
				print "Creating config file"
				self.install(block,filename)
		if path.isfile(config_file):
			try:
				config = ConfigParser.ConfigParser()
				config.readfp(open(config_file))
				config.items(block)
			except(ConfigParser.NoSectionError):
				sure = ""
				while sure !="y" and sure !="n" and sure !="no" and sure !="yes":
					sure = raw_input("Section don\'t exists. Do you want create it (y/n)?").lower().strip()
				if sure == "no" or sure == "n":
					print "Exit. Please review config file in %s" % config_file
					exit(5)
				else:
					print "Creating section"
					self.install(block,filename)
					config = ConfigParser.ConfigParser()
					config.readfp(open(config_file))				
			self.session = ""
			for key, value in config.items(block):
				# ConfigParser lowercases magically
				if key == "example":
					print "This is an EXAMPLE!!! Create your on config file and change this attribute"
					exit()
				elif key == "client_secret":
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

	def install(self,block,filename):
		Config = ConfigParser.ConfigParser()
		config_items = ["host","access_token","client_secret","client_token","contract"]
		print "Take yours API information from luna control center"
		print "You will need host, access_token, client_secret, client_token, contract"
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
				var = raw_input(message).strip()
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
					elif i == "contract":
						Config.set(block,'contract',var)
		Config.write(config)
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

	def contracts (self):
		if not self.session:
			self.connection()
		contracts_url = '/billing-usage/v1/reportSources'
		endpoint_result = self.session.get(urljoin(self.baseurl,contracts_url))
	 	contracts_result = endpoint_result.json()
	 	contracts_dump = json.loads(json.dumps(contracts_result), object_hook=BlankDict)
	 	return contracts_dump

	def users(self):
		if not self.session:
			self.connection()
	 	user_url = '/user-admin/v1/accounts/'+self.contract+'/users'
		endpoint_result = self.session.get(urljoin(self.baseurl,user_url))
	 	user_result = endpoint_result.json()
	 	user_dump = json.loads(json.dumps(user_result), object_hook=BlankDict)
	 	return user_dump

	def groups(self):
		if not self.session:
			self.connection()
	 	group_url = '/user-admin/v1/accounts/'+self.contract+'/groups'
		endpoint_result = self.session.get(urljoin(self.baseurl,group_url))
	 	group_result = endpoint_result.json()
	 	group_dump = json.loads(json.dumps(group_result), object_hook=BlankDict)
	 	return group_dump

	def roles(self):
		if not self.session:
			self.connection()
	 	roles_url = '/user-admin/v1/accounts/'+self.contract+'/roles'
		endpoint_result = self.session.get(urljoin(self.baseurl,roles_url))
	 	roles_result = endpoint_result.json()
	 	roles_dump = json.loads(json.dumps(roles_result), object_hook=BlankDict)
	 	return roles_dump

	def retrieve_contracts(self):
		contracts = []
		result = self.contracts()
		try:	
			if str(result["httpStatus"]) == "403":
				print "Permisions Error"
				raise SystemExit
			if str(result["status"]) == "401":
				print "Permisions Error"
				raise SystemExit
	 	except (TypeError):
			pass
		result = result["contents"]
		while result:
			r = result.pop()
			if r["type"] == "contract":
				print r["id"]

	def export_contractscsv (self,filename=""):
		if not filename:
			print "You need to specify a file to export users"
			exit (2)
		if path.exists(filename):
			sure = ""
			while sure !="y" and sure !="n" and sure !="no" and sure !="yes":
				sure = raw_input("This file ("+filename+") exists. Do you want to overwrite it(y/n)? ").lower().strip()
			if sure == "no" or sure == "n":
				print "Exit. Please review filename for exporting contracts"
				exit(3)
			else:
				print "Exporting contracts..."
		result = self.contracts()
		try:	
			if str(result["httpStatus"]) == "403":
				print "Permisions Error"
				raise SystemExit
			if str(result["status"]) == "401":
				print "Permisions Error"
				raise SystemExit
	 	except (TypeError):
			pass
		with open (filename, "w") as myfile:
			cabecera = " CONTRACTs "
	 		myfile.write(cabecera.center(50,"=")+"\n")
	 		myfile.write("id;type;name\n")
	 		exportados=0
	 		result = result["contents"]
	 		while result:
	 			exportados +=1
	 			contracts = result.pop()
	 			contractType = contracts["type"]
	 			contractId = contracts["id"]
	 			contractName = contracts["Name"]
	 			myfile.write(contractId+";"+contractType+";"+contractName)
		print "%i Roles exported in %s" % (exportados,filename)

	def export_userscsv (self,filename=""):
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
				print "Exporting users..."
		result = self.users()
		try:	
			if str(result["httpStatus"]) == "403":
				print "Permisions Error"
				raise SystemExit
			if str(result["status"]) == "401":
				print "Permisions Error"
				raise SystemExit
	 	except (TypeError):
			pass
		with open (filename, "w") as myfile:
			cabecera = " USERS FOR CONTRACT "
	 		myfile.write(cabecera.center(50,"=")+"\n")
	 		myfile.write("Username;FirstName;LastName;Phone;Role;Group;Email;userType;2faEnabled;2faConfigured;lastLogin\n")
	 		exportados=0
	 		while result:
				exportados += 1
				user = result.pop()
				username= str(user["username"])
				firstname = str(user["firstName"])
				lastname = str(user["lastName"])
				phone = str(user["phone"])
				contactId = str(user["contactId"])
				userType = str(user["userType"])
				twofaEnabled = str(user["tfaEnabled"])
				twofaConfigured = str(user["tfaConfigured"])
				if user["lastLoginDate"]:
					lastlogin = str(user["lastLoginDate"])
				else:
					lastlogin = str("")
				email = str(user["email"])
				roles = user["roleAssignments"]
				while roles:
					j = roles.pop()
					role = str(j["roleName"])
					group = str(j["groupName"])
				myfile.write(username+";"+firstname+";"+lastname+";"+phone+";"+role+";"+group+";"+email+";"+userType+";"+twofaEnabled+";"+twofaConfigured+";"+lastlogin+"\n")
		print "%i Users exported in %s" % (exportados,filename)

	def export_groupscsv (self,filename=""):
		if not filename:
			print "You need to specify a file to export users"
			exit (2)
		if path.exists(filename):
			sure = ""
			while sure !="y" and sure !="n" and sure !="no" and sure !="yes":
				sure = raw_input("This file ("+filename+") exists. Do you want to overwrite it(y/n)? ").lower().strip()
			if sure == "no" or sure == "n":
				print "Exit. Please review filename for exporting Groups"
				exit(3)
			else:
				print "Exporting groups..."
		result = self.groups()
		try:	
			if str(result["httpStatus"]) == "403":
				print "Permisions Error"
				raise SystemExit
			if str(result["status"]) == "401":
				print "Permisions Error"
				raise SystemExit
	 	except (TypeError):
			pass
		with open (filename, "w") as myfile:
			cabecera = " GROUPS FOR CONTRACT "
	 		myfile.write(cabecera.center(50,"=")+"\n")
	 		myfile.write("GroupID;accountId;groupName;topLevelGroup;parentGroupId;createdBy;createdDate\n")
	 		exportados = 0
			while result:
				exportados +=1
				group = result.pop()
				createdBy = str(group["createdBy"])
				topLevelGroup = str(group["topLevelGroup"])
				groupName = str(group["groupName"])
				parentGroupId = str(group["parentGroupId"])
				accountId = str(group["accountId"])
				groupId = str(group["groupId"])
				createdDate = str(group["createdDate"])
				myfile.write(groupId+";"+accountId+";"+groupName+";"+topLevelGroup+";"+parentGroupId+";"+createdBy+";"+createdDate+"\n")
			print "%i Groups exported in %s" % (exportados,filename)


	def export_rolescsv (self,filename=""):
		if not filename:
			print "You need to specify a file to export users"
			exit (2)
		if path.exists(filename):
			sure = ""
			while sure !="y" and sure !="n" and sure !="no" and sure !="yes":
				sure = raw_input("This file ("+filename+") exists. Do you want to overwrite it(y/n)? ").lower().strip()
			if sure == "no" or sure == "n":
				print "Exit. Please review filename for exporting Roles"
				exit(3)
			else:
				print "Exporting roles..."
		result = self.roles()
		try:	
			if str(result["httpStatus"]) == "403":
				print "Permisions Error"
				raise SystemExit
			if str(result["status"]) == "401":
				print "Permisions Error"
				raise SystemExit
	 	except (TypeError):
			pass
		with open (filename, "w") as myfile:
			cabecera = " ROLES FOR CONTRACT "
	 		myfile.write(cabecera.center(50,"=")+"\n")
	 		myfile.write("roles_dump;roleName;roleDescription;contractTypeId;numUsers;type;modifiedBy;modifiedDate\n")
	 		exportados = 0
			while result:
				exportados += 1
				role = result.pop()
				roleId = str(role["roleId"])
				contractTypeId = str(role["contractTypeId"])
				roleDescription = role["roleDescription"]
				for char in "'":
					roleDescription = roleDescription.replace(char,'')
				## FIX por a error that I cant understand
				roleDescription = roleDescription.replace(u'\x9d',"")
				modifiedBy = str(role["modifiedBy"])
				modifiedDate = str(role["modifiedDate"])
				numUsers = str(role["numUsers"])
				roleName = str(role["roleName"])
				roletype = str(role["type"])
				myfile.write(roleId+";"+roleName+";"+roleDescription+";"+contractTypeId+";"+numUsers+";"+roletype+";"+modifiedBy+";"+modifiedDate+"\n")
			print "%i Roles exported in %s" % (exportados,filename)

	def export_allcsv (self,filename=""):
		filename_users=filename+"_users"
		self.export_userscsv(filename_users)
		filename_groups=filename+"_groups"
		self.export_groupscsv(filename_groups)
		filename_roles=filename+"_roles"
		self.export_rolescsv(filename_roles)
		filename_contracts=filename+"_contracts"
		self.export_contractscsv(filename_contracts)


## Codigo por defecto
if len(sys.argv)>1:
	command = str(sys.argv[1]).lower()

	if command == "test":
		print "Test"
	elif command == "iniciate":
		if len(sys.argv)==3:
			block = sys.argv[2]
		elif len(sys.argv)==2:
			block = "user" 
		else:
			print "error"
			exit(1)
		AKAMAI_instance = AKAMAI (block,config_file)
	elif command == "export_users":
		block = "user"
		if len(sys.argv)==3:
			AKAMAI_instance = AKAMAI(block,config_file).export_userscsv(sys.argv[2])
		elif len(sys.argv)==4:
			contract = sys.argv[3]
			AKAMAI_instance = AKAMAI(block,config_file,contract).export_userscsv(sys.argv[2])
		elif len(sys.argv)==5:
			contract = sys.argv[3]
			config_file = sys.argv[4]
			AKAMAI_instance = AKAMAI(block,config_file,contract).export_userscsv(sys.argv[2])
		else:
			print "%s %s export_file [contract [config_file]]]" % (sys.argv[0], sys.argv[1])
			exit(1)
	elif command == "export_groups":
		block = "user"
		if len(sys.argv)==3:
			AKAMAI_instance = AKAMAI(block,config_file).export_groupsscsv(sys.argv[2])
		elif len(sys.argv)==4:
			contract = sys.argv[3]
			AKAMAI_instance = AKAMAI(block,config_file,contract).export_groupscsv(sys.argv[2])
		elif len(sys.argv)==5:
			contract = sys.argv[3]
			config_file = sys.argv[4]
			AKAMAI_instance = AKAMAI(block,config_file,contract).export_groupscsv(sys.argv[2])
		else:
			print "%s %s export_file [contract [config_file]]]" % (sys.argv[0], sys.argv[1])
			exit(1)
	elif command == "export_roles":
		block = "user"
		if len(sys.argv)==3:
			AKAMAI_instance = AKAMAI(block,config_file).export_rolescsv(sys.argv[2])
		elif len(sys.argv)==4:
			contract = sys.argv[3]
			AKAMAI_instance = AKAMAI(block,config_file,contract).export_rolescsv(sys.argv[2])
		elif len(sys.argv)==5:
			contract = sys.argv[3]
			config_file = sys.argv[4]
			AKAMAI_instance = AKAMAI(block,config_file,contract).export_rolesscsv(sys.argv[2])
		else:
			print "%s %s export_file [contract [config_file]]]" % (sys.argv[0], sys.argv[1])
			exit(1)
	elif command == "export_all":
		block = "user"
		if len(sys.argv)==3:
			AKAMAI_instance = AKAMAI(block,config_file).export_allcsv(sys.argv[2])
		elif len(sys.argv)==4:
			contract = sys.argv[3]
			AKAMAI_instance = AKAMAI(block,config_file,contract).export_allcsv(sys.argv[2])
		elif len(sys.argv)==5:
			contract = sys.argv[3]
			config_file = sys.argv[4]
			AKAMAI_instance = AKAMAI(block,config_file,contract).export_allcsv(sys.argv[2])
		else:
			print "%s %s export_file [contract [config_file]]]" % (sys.argv[0], sys.argv[1])
			exit(1)
	elif command == "config":
		if len(sys.argv)==3:
			block = sys.argv[2]
		elif len(sys.argv)==2:
			block = "user" 
		else:
			print "error"
			exit(1)
		install(config_file,block)
else:
	print "Usage: %s config|initiate|test|export_users|export_groups|export_roles|export_all [argvs]" % str(sys.argv[0])
	AKAMAI_instance = AKAMAI("iser",config_file).export_userscsv("/tmp/users.txt")
	AKAMAI_instance = AKAMAI("iser",config_file).export_groupscsv("/tmp/groups.txt")
	AKAMAI_instance = AKAMAI("billing",config_file).export_contractscsv("/tmp/contracts.txt")
	AKAMAI_instance = AKAMAI("iser",config_file).export_rolescsv("/tmp/roles.txt")

	exit(99)



