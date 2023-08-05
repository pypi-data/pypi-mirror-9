"""
Server related functions.  

These server related functions generally align one-for-one with published API calls categorized in the account category

API v2 - https://t3n.zendesk.com/forums/21613150-Servers

Server object variables:

	server.id
	server.description
	server.cpu
	server.power_state
	server.memory
	server.storage
	server.group_id
	server.is_template
	server.location_id
	server.name
	server.os
	server.os_type
	server.status
	server.type
	server.storage_type
	server.in_maintenance_mode
	server.reserved_drive_paths
	server.adding_cpu_requires_reboot
	server.adding_memory_requires_reboot

Server object variables available but access subject to change with future releases:

	server.custom_fields
	server.change_info
	server.alert_policies
	server.ip_addresses

"""

# vCur:
# TODO - Link to Public IP class

# vNext:
# TODO - cpuAutoscalePolicy - need API spec 404
# TODO - AntiAffinity policy - need API spec put call 400 
# TODO - Statistics - need API spec get call 500
# TODO - Billing (server, group, account) - need API spec
# TODO - Server pricing (/v2/billing/btdi/serverPricing/wa1btdiapi207) returns array with static hourly pricing
# TODO - Change Server (Update) - need API spec
# TODO - Validation tasks with Server.Create
# TODO - create server capture and resolve alias via uuid
# TODO - Scheduled activities
# TODO - create a packages class.  Pass in for execute package, create, and clone
# TODO - remove constructor server_obj if not used
# TODO - Servers search by custom field
# TODO - Servers.CreateSnapshot, Servers.Delete

import re
import math
import json
import time
import clc


class Servers(object):

	def __init__(self,servers_lst,alias=None):
		"""Container class for one or more servers.

		Behaves differently than the other container classes like Groups where the *_lst
		parameter can fully define the object.  All we have is the server name on construction.
		We will lazily create server objects as needed since each requires a seperate API call.

		>>> clc.v2.Servers(["NY1BTDIPHYP0101","NY1BTDIWEB0101"])
		<clc.APIv2.server.Servers object at 0x105fa27d0>

		"""

		if alias:  self.alias = alias
		else:  self.alias = clc.v2.Account.GetAlias()

		self.servers_lst = servers_lst


	def Servers(self,cached=True):
		"""Returns list of server objects, populates if necessary.
		
		>>> clc.v2.Servers(["NY1BTDIPHYP0101","NY1BTDIWEB0101"]).Servers()
		[<clc.APIv2.server.Server object at 0x1065b0d50>, <clc.APIv2.server.Server object at 0x1065b0e50>]
		>>> print _[0]
		NY1BTDIPHYP0101

		"""

		if not hasattr(self,'_servers') or not cached:
			self._servers = []
			for server in self.servers_lst:
				self._servers.append(Server(id=server,alias=self.alias))

		return(self._servers)


	def __getattr__(self,key):
		if key == 'servers':  return(self.Servers())
		else:  raise(AttributeError("'%s' instance has no attribute '%s'" % (self.__class__.__name__,key)))


	def _Operation(self,operation):
		"""Execute specified operations task against one or more servers.

		Returns a clc.v2.Requests object.  If error due to server(s) already being in
		the requested state this is not raised as an error at this level.

		>>> clc.v2.Servers(["NY1BTDIPHYP0101","NY1BTDIWEB0101"]).Pause()
		<clc.APIv2.queue.Requests object at 0x105fea7d0>
		>>> _.WaitUntilComplete()
		0

		"""

		try:
			return(clc.v2.Requests(clc.v2.API.Call('POST','operations/%s/servers/%s' % (self.alias,operation),
			                                       json.dumps(self.servers_lst)),alias=self.alias))
		except clc.APIFailedResponse as e:
			# Most likely a queue add error presented as a 400.  Let Requests parse this
			return(clc.v2.Requests(e.response_json,alias=self.alias))


	def Pause(self):  return(self._Operation('pause'))
	def ShutDown(self):  return(self._Operation('shutDown'))
	def Reboot(self):  return(self._Operation('reboot'))
	def Reset(self):  return(self._Operation('reset'))
	def PowerOn(self):  return(self._Operation('powerOn'))
	def PowerOff(self):  return(self._Operation('powerOff'))
	def StartMaintenance(self):  return(self._Operation('startMaintenance'))
	def StopMaintenance(self):  return(self._Operation('stopMaintenance'))



class Server(object):


	def __init__(self,id,alias=None,server_obj=None):
		"""Create Server object.

		https://t3n.zendesk.com/entries/32859214-Get-Server

		#If parameters are populated then create object location.  
		#Else if only id is supplied issue a Get Policy call

		# successful creation
		>>> clc.v2.Server("CA3BTDICNTRLM01")
		<clc.APIv2.server.Server object at 0x10c28fe50>
		>>> print _
		CA3BTDICNTRLM01

		# error.  API returns 404 when server does not exist, we raise exception
		>>> clc.v2.Server(alias='BTDI',id='WA1BTDIKRT01')
		clc.CLCException: Server does not exist

		"""

		self.id = id
		self.capabilities = None

		if alias:  self.alias = alias
		else:  self.alias = clc.v2.Account.GetAlias()

		if server_obj:  self.data = server_obj
		else:  
			try:
				self.data = clc.v2.API.Call('GET','servers/%s/%s' % (self.alias,self.id),{})
			except clc.APIFailedResponse as e:
				if e.response_status_code==404:  raise(clc.CLCException("Server does not exist"))

		# API call switches between GB and MB.  Change to all references are in GB and we drop the units
		self.data['details']['memoryGB'] = int(math.floor(self.data['details']['memoryMB']/1024))


	def _Capabilities(self,cached=True):
		if not self.capabilities or not cached:
			self.capabilities = clc.v2.API.Call('GET','servers/%s/%s/capabilities' % (self.alias,self.name))

		return(self.capabilities)


	def __getattr__(self,var):
		if var in ('memory','storage'):  key = var+'GB'
		else:  key = re.sub("_(.)",lambda pat: pat.group(1).upper(),var)

		if key in self.data:  return(self.data[key])
		elif key in self.data['details']:  return(self.data['details'][key])
		elif key in ("reservedDrivePaths", "addingCpuRequiresReboot", "addingMemoryRequiresReboot"):  return(self._Capabilities()[key])
		else:  raise(AttributeError("'%s' instance has no attribute '%s'" % (self.__class__.__name__,key)))


	def Account(self):
		"""Return account object for account containing this server.

		>>> clc.v2.Server("CA3BTDICNTRLM01").Account()
		<clc.APIv2.account.Account instance at 0x108789878>
		>>> print _
		BTDI
		
		"""

		return(clc.v2.Account(alias=self.alias))


	def Group(self):
		"""Return group object for group containing this server.

		>>> clc.v2.Server("CA3BTDICNTRLM01").Group()
		<clc.APIv2.group.Group object at 0x10b07b7d0>
		>>> print _
		Ansible Managed Servers

		"""

		return(clc.v2.Group(id=self.groupId,alias=self.alias))

	
	def Alerts(self):
		"""Returns an Alerts object containing all alerts mapped to this server.

		>>> clc.v2.Server("NY1BTDIPHYP0101").Alerts()
		<clc.APIv2.alert.Alerts object at 0x1065b0150>
		"""

		return(clc.v2.Alerts(self.alert_policies))


	def Credentials(self):
		"""Returns the administrative credentials for this server.

		>>> clc.v2.Server("NY1BTDIPHYP0101").Credentials()
		{u'userName': u'administrator', u'password': u'dszkjh498s^'}

		"""

		return(clc.v2.API.Call('GET','servers/%s/%s/credentials' % (self.alias,self.name)))


	def _Operation(self,operation):
		"""Execute specified operations task against one or more servers.

		Returns a clc.v2.Requests object.  If error due to server(s) already being in
		the requested state this is not raised as an error at this level.
		>>> clc.v2.Server(alias='BTDI',id='WA1BTDIKRT02').PowerOn().WaitUntilComplete()
		0

		"""

		try:
			return(clc.v2.Requests(clc.v2.API.Call('POST','operations/%s/servers/%s' % (self.alias,operation),'["%s"]' % self.id),alias=self.alias))
		except clc.APIFailedResponse as e:
			# Most likely a queue add error presented as a 400.  Let Requests parse this
			return(clc.v2.Requests(e.response_json,alias=self.alias))


	def Pause(self):  return(self._Operation('pause'))
	def ShutDown(self):  return(self._Operation('shutDown'))
	def Reboot(self):  return(self._Operation('reboot'))
	def Reset(self):  return(self._Operation('reset'))
	def PowerOn(self):  return(self._Operation('powerOn'))
	def PowerOff(self):  return(self._Operation('powerOff'))
	def StartMaintenance(self):  return(self._Operation('startMaintenance'))
	def StopMaintenance(self):  return(self._Operation('stopMaintenance'))


	def ExecutePackage(self,package_id,parameters={}):
		"""Execute an existing Bluerprint package on the server.

		https://t3n.zendesk.com/entries/59727040-Execute-Package

		Requires package ID, currently only available by browsing control and browsing
		for the package itself.  The UUID parameter is the package ID we need.

		>>> clc.v2.Server(alias='BTDI',id='WA1BTDIKRT06'). \
		           ExecutePackage(package_id="77ab3844-579d-4c8d-8955-c69a94a2ba1a",parameters={}). \
				   WaitUntilComplete()
		0

		"""

		return(clc.v2.Requests(clc.v2.API.Call('POST','operations/%s/servers/executePackage' % (self.alias),
		                                       json.dumps({'servers': [self.id], 'package': {'packageId': package_id, 'parameters': parameters}}))))


	def GetSnapshots(self):
		"""Returns list of all snapshot names.

		>>> clc.v2.Server("WA1BTDIAPI219").GetSnapshots()
		[u'2015-01-10.02:10:38']
		"""

		return([obj['name'] for obj in self.data['details']['snapshots']])


	def CreateSnapshot(self,delete_existing=True,expiration_days=7):
		"""Take a Hypervisor level snapshot retained for between 1 and 10 days (7 is default).
		Currently only one snapshop may exist at a time, thus will delete snapshots if one already
		exists before taking this snapshot.

		>>> clc.v2.Server("WA1BTDIAPI219").CreateSnapshot(2)
		<clc.APIv2.queue.Requests object at 0x10d106cd0>
		>>> _.WaitUntilComplete()
		0

		"""

		if len(self.data['details']['snapshots']):  
			if delete_existing:  self.DeleteSnapshot()
			else:  raise(clc.CLCException("Snapshot already exists cannot take another"))

		return(clc.v2.Requests(clc.v2.API.Call('POST','operations/%s/servers/createSnapshot' % (self.alias),
											   {'serverIds': self.id, 'snapshotExpirationDays': expiration_days})))


	def DeleteSnapshot(self,names=None):
		"""Removes an existing Hypervisor level snapshot.

		Supply one or more snapshot names to delete them concurrently.
		If no snapshot names are supplied will delete all existing snapshots.

		>>> clc.v2.Server(alias='BTDI',id='WA1BTDIKRT02').DeleteSnapshot().WaitUntilComplete()
		0

		"""

		if names is None:  names = self.GetSnapshots()

		requests_lst = []
		for name in names:
			name_links = [obj['links'] for obj in self.data['details']['snapshots'] if obj['name']==name][0]
			requests_lst.append(clc.v2.Requests(clc.v2.API.Call('DELETE',[obj['href'] for obj in name_links if obj['rel']=='delete'][0])))
			
		return(sum(requests_lst))


	def RestoreSnapshot(self,name=None):
		"""Restores an existing Hypervisor level snapshot.

		Supply snapshot name to restore
		If no snapshot name is supplied will restore the first snapshot found

		>>> clc.v2.Server(alias='BTDI',id='WA1BTDIKRT02').RestoreSnapshot().WaitUntilComplete()
		0

		"""

		if not len(self.data['details']['snapshots']):  raise(clc.CLCException("No snapshots exist"))
		if name is None:  name = self.GetSnapshots()[0]

		name_links = [obj['links'] for obj in self.data['details']['snapshots'] if obj['name']==name][0]
		return(clc.v2.Requests(clc.v2.API.Call('POST',[obj['href'] for obj in name_links if obj['rel']=='restore'][0])))


	@staticmethod
	def Create(name,cpu,memory,template,group_id,network_id,alias=None,password=None,ip_address=None,
	           storage_type="standard",type="standard",primary_dns=None,secondary_dns=None,
			   additional_disks=[],custom_fields=[],ttl=None,managed_os=False,description=None,
			   source_server_password=None,cpu_autoscale_policy_id=None,anti_affinity_policy_id=None,
			   packages=[]):  
		"""Creates a new server.

		https://t3n.zendesk.com/entries/59565550-Create-Server

		Set ttl as number of seconds before server is to be terminated.  Must be >3600

		>>> d = clc.v2.Datacenter()
		>>> clc.v2.Server.Create(name="api2",cpu=1,memory=1,group_id="wa1-4416",
	                             template=d.Templates().Search("centos-6-64")[0].id,
						         network_id=d.Networks().networks[0].id).WaitUntilComplete()
		0

		"""

		if not alias:  alias = clc.v2.Account.GetAlias()

		if not description:  description = name
		if type.lower() not in ("standard","hyperscale"):  raise(clc.CLCException("Invalid type"))
		if storage_type.lower() not in ("standard","premium"):  raise(clc.CLCException("Invalid storage_type"))
		if storage_type.lower() == "premium" and type.lower() == "hyperscale":  raise(clc.CLCException("Invalid type/storage_type combo"))
		if ttl and ttl<=3600: raise(clc.CLCException("ttl must be greater than 3600 seconds"))
		if ttl: ttl = clc.v2.time_utils.SecondsToZuluTS(int(time.time())+ttl)
		# TODO - validate custom_fields as a list of dicts with an id and a value key
		# TODO - validate template exists
		# TODO - validate additional_disks as a list of dicts with a path, sizeGB, and type (partitioned,raw) keys
		# TODO - validate addition_disks path not in template reserved paths
		# TODO - validate antiaffinity policy id set only with type=hyperscale

		return(clc.v2.Requests(clc.v2.API.Call('POST','servers/%s' % (alias),
		         json.dumps({'name': name, 'description': description, 'groupId': group_id, 'sourceServerId': template,
							 'isManagedOS': managed_os, 'primaryDNS': primary_dns, 'secondaryDNS': secondary_dns, 
							 'networkId': network_id, 'ipAddress': ip_address, 'password': password,
							 'sourceServerPassword': source_server_password, 'cpu': cpu, 'cpuAutoscalePolicyId': cpu_autoscale_policy_id,
							 'memoryGB': memory, 'type': type, 'storageType': storage_type, 'antiAffinityPolicyId': anti_affinity_policy_id,
							 'customFields': custom_fields, 'additionalDisks': additional_disks, 'ttl': ttl, 'packages': packages}))))


	def Clone(self,network_id,name=None,cpu=None,memory=None,group_id=None,alias=None,password=None,ip_address=None,
	          storage_type=None,type=None,primary_dns=None,secondary_dns=None,
			  custom_fields=None,ttl=None,managed_os=False,description=None,
			  source_server_password=None,cpu_autoscale_policy_id=None,anti_affinity_policy_id=None,
			  packages=[],count=1):  
		"""Creates one or more clones of existing server.

		https://t3n.zendesk.com/entries/59565550-Create-Server

		Set ttl as number of seconds before server is to be terminated.

		* - network_id is currently a required parameter.  This will change to optional once APIs are available to
		    return the network id of self.
		* - if no password is supplied will reuse the password of self.  Is this the expected behavior?  Take note
		    there is no way to for a system generated password with this pattern since we cannot leave as None
		* - any DNS settings from self aren't propogated to clone since they are unknown at system level and
		    the clone process will touch them
		* - no change to the disk layout we will clone all
		* - clone will not replicate managed OS setting from self so this must be explicitly set

		>>> d = clc.v2.Datacenter()
		>>> clc.v2.Server(alias='BTDI',id='WA1BTDIAPI207').Clone(network_id=d.Networks().networks[0].id,count=2)
		0

		"""

		if not name:  name = re.search("%s(.+)\d{2}$" % self.alias,self.name).group(1)
		if not description and self.description:  description = self.description
		if not cpu:  cpu = self.cpu
		if not memory:  memory = self.memory
		if not group_id:  group_id = self.group_id
		if not alias:  alias = self.alias
		if not source_server_password: source_server_password = self.Credentials()['password']
		if not password: password = source_server_password	# is this the expected behavior?
		if not storage_type:  storage_type = self.storage_type
		if not type:  type = self.type
		if not storage_type:  storage_type = self.storage_type
		if not custom_fields and len(self.custom_fields): custom_fields = self.custom_fields
		if not description:  description = self.description
		# TODO - #if not cpu_autoscale_policy_id:  cpu_autoscale_policy_id = 
		# TODO - #if not anti_affinity_policy_id:  anti_affinity_policy_id =
		# TODO - need to get network_id of self, not currently exposed via API :(

		requests_lst = []
		for i in range(0,count):
			requests_lst.append(Server.Create( \
			            name=name,cpu=cpu,memory=memory,group_id=group_id,network_id=network_id,alias=self.alias,
						password=password,ip_address=ip_address,storage_type=storage_type,type=type,
						primary_dns=primary_dns,secondary_dns=secondary_dns,
						custom_fields=custom_fields,ttl=ttl,managed_os=managed_os,description=description,
                        source_server_password=source_server_password,cpu_autoscale_policy_id=cpu_autoscale_policy_id,
						anti_affinity_policy_id=anti_affinity_policy_id,packages=packages,
						template=self.id))

		return(sum(requests_lst))


	def Update(self):
		"""Update group

		*TODO* API not yet documented

		"""

		#return(clc.v2.Requests(clc.v2.API.Call('PATCH','servers/%s/%s' % (self.alias,self.id),
		#         json.dumps({'description': 'new'}),debug=True)))

		raise(Exception("Not implemented"))



	def Delete(self):
		"""Delete server.

		https://t3n.zendesk.com/entries/59220824-Delete-Server

		>>> clc.v2.Server("WA1BTDIAPI219").Delete().WaitUntilComplete()
		0
		
		"""
		return(clc.v2.Requests(clc.v2.API.Call('DELETE','servers/%s/%s' % (self.alias,self.id))))


	def __str__(self):
		return(self.data['name'])

