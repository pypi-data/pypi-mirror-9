#!/usr/bin/python

# Copyright 2013 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import urllib2
import xml
import sys, os, time
from xml.dom.minidom import *
from Constants import *
from threading import Timer, Condition, Lock, Thread
from Queue import Queue
import datetime
import signal

_AffirmativeList = ['true', 'True', 'TRUE', True, 'yes', 'Yes', 'YES']
defaultUcs = {}

class UcsHandle:
	"""
	UcsHandle class handles all the Session and Xml request related functionality.
	
	This class provides all the functionality related to session creation/refresh/destroy, transactions, xml/xmlRaw request handling, 
	event channel handling, starting KVM/Gui Session, BackUp ucs, Import Ucs BackUp, Firmware Upgrade, Generating Tech Support File, 
	Compare and synchronize managed objects and Get/Set/Add/Remove operations on managed objects.
	"""
	def __init__(self):
		from Ucs import ConfigMap
		self._name = None
		self._noSsl = False
		self._port = 443
		self._username = None
		self._password = None
		self._cookie = None
		self._domains = None
		self._lastUpdateTime = None
		self._ucs = None
		self._priv = None
		self._refreshPeriod = None
		self._sessionId = None
		self._transactionInProgress = None
		self._version = None
		self._virtualIpv4Address = None
		self.proxy = None
		self._lockObject = None
		self._preventLogout = False
		self._refreshTimer = None
		self._configMap = ConfigMap()
		self._wbs = []
		self._wbslock = None
		self._enqueueThread = None
		self._enqueueThreadSignal = Condition()
		self._watchWebResponse = None
		self._dequeueThread = None
		self._proxy = None
		self._dumpXml = False
		
	def SetDumpXml(self):
		""" SetDumpXml method sets the flag at handle level to display XML request and response. """
		self._dumpXml = True
	
	def UnsetDumpXml(self):
		""" UnsetDumpXml method sets the flag at handle level to hide XML request and response. """
		self._dumpXml = False

	def Uri(self):
		"""	Constructs the connection URI from name, noSsl and port instance variables.	"""
		return ("%s://%s%s" % (("https","http")[self._noSsl == True], self._name, (":" + str(self._port),"")[(((self._noSsl == False) and  (self._port == 80)) or ((self._noSsl == True) and (self._port == 443)))]))

	def StartTransaction(self):
		"""
		Starts a transaction.
		
		Any modification query (i.e. configConfMo or configConfMos) will be stored locally in configMap, till completeTransaction or 
		undoTransaction is not called.
		All other queries will be sent normally to UCS.
		"""
		self._transactionInProgress = True

	def UndoTransaction(self):
		"""	Cancels any running transaction. """
		from Ucs import ConfigMap
		self._transactionInProgress = False
		self._configMap = ConfigMap()

	def CompleteTransaction(self, dumpXml=None):
		"""
		Completes a transaction.
		
		This method completes a transaction by sending the final configuration (modification queries stored in configMap) to UCS and 
		returns the result.
        """
		from Ucs import ConfigMap, Pair
		from UcsBase import ManagedObject,WriteUcsWarning,WriteObject,UcsException
		
		self._transactionInProgress = False
		ccm = self.ConfigConfMos(self._configMap, YesOrNo.FALSE, dumpXml)
		self._configMap = ConfigMap()
		if ccm.errorCode == 0:
			moList = []
			for child in ccm.OutConfigs.GetChild():
				if (isinstance(child, Pair) == True):
					for mo in child.GetChild():
						moList.append(mo)
				elif (isinstance(child, ManagedObject) == True):
					moList.append(child)
			#WriteObject(moList)
			return moList
		else:
			#raise Exception('[Error]: CompleteTransaction [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)
			raise UcsException(ccm.errorCode, ccm.errorDescr)

	def XmlQuery(self, method, options, dumpXml=None):
		"""
		Accepts any ExternalMethod stores any modification query locally if transaction is in progress (and returns temporary result)
        prepares xml query as per the writeXmlOption from external method. Opens a connection to url, sends the xmlQuery string to url 
        location, and returns result. Prepares objects from xml query result and returns external method response.
        """
		from UcsBase import ExternalMethod,ManagedObject,UcsUtils
		from Ucs import ConfigConfig, Pair, ConfigMap
		from MoMeta import _ManagedObjectMeta
		from MethodMeta import _MethodFactoryMeta

		if ((self._transactionInProgress == True) and (method.propMoMeta.xmlAttribute in [NamingId.CONFIG_CONF_MO, NamingId.CONFIG_CONF_MOS])):
			if (method.propMoMeta.xmlAttribute == NamingId.CONFIG_CONF_MO):
				ccm = method
				ccmResponse = ExternalMethod(NamingId.CONFIG_CONF_MO)
				ccmResponse.setattr("Dn", ccm.Dn)
				ccmResponse.InConfig = ConfigConfig()

				pair = Pair()
				pair.Key = ccm.Dn
				for mo in ccm.InConfig.GetChild():
					if (isinstance(mo, ManagedObject) == True):
						pair.AddChild(mo.Clone())

						clone = mo.Clone()
						clone.MarkClean()
						clone.SetHandle(self)

						ccmResponse.InConfig.AddChild(clone)
				self._configMap.AddChild(pair)

				ccmResponse.setattr("OutConfig", ccmResponse.getattr("InConfig"))
				ccmResponse.setattr("InConfig", None)
				ccmResponse.response = "yes"
				return ccmResponse
			else:
				ccm = method
				ccmResponse = ExternalMethod(NamingId.CONFIG_CONF_MOS)
				ccmResponse.InConfigs = ConfigMap()

				for pair in ccm.InConfigs.GetChild():
					if (isinstance(pair, Pair) == True):
						self._configMap.AddChild(pair.Clone())
						clone = pair.Clone()
						for mo in clone.GetChild():
							if (isinstance(mo, ManagedObject) == True):
								mo.MarkClean()
								mo.SetHandle(self)
						ccmResponse.InConfigs.AddChild(clone)
				ccmResponse.setattr("OutConfigs", ccmResponse.getattr("InConfigs"))
				ccmResponse.setattr("InConfigs", None)
				ccmResponse.response = "yes"
				return ccmResponse
		else:
			try:				
				if (dumpXml == None):
					dumpXml = self._dumpXml
				
				w = xml.dom.minidom.Document()
				w.appendChild(method.WriteXml(w, options))
				uri = self.Uri() + '/nuova'
				if (dumpXml in _AffirmativeList):
					print '%s ====> %s' % (self._ucs, w.toxml())
				
				if (self._proxy is None):
					if(self._noSsl):
						req = urllib2.Request(url=uri,data=w.toxml())
						opener = urllib2.build_opener(SmartRedirectHandler())
						f = opener.open(req)
						#print "##", f , "##"
						
						if type(f) is list:
							if(len(f) == 2 and f[0] == 302):
								#self._noSsl = False
								#uri = self.Uri() + '/nuova'
								uri = f[1]
								req = urllib2.Request(url=uri,data=w.toxml())
								f = urllib2.urlopen(req)						
								#print "status code is:",f[0]
								#print "location is:", f[1]
					else:
						req = urllib2.Request(url=uri,data=w.toxml())
						opener = urllib2.build_opener()
						f = opener.open(req)
						#f = urllib2.urlopen(req)
				else:
					
					proxy_handler = urllib2.ProxyHandler({'http': self._proxy, 'https': self._proxy})
	
					if(self._noSsl):
						req = urllib2.Request(url=uri,data=w.toxml())
						opener = urllib2.build_opener(proxy_handler, SmartRedirectHandler())
						f = opener.open(req)
						
						if type(f) is list:
							if(len(f) == 2 and f[0] == 302):
								#self._noSsl = False
								#uri = self.Uri() + '/nuova'
								uri = f[1]
								req = urllib2.Request(url=uri,data=w.toxml())
								opener = urllib2.build_opener(proxy_handler)
								f = opener.open(req)
								#f = urllib2.urlopen(req)						
								#print "status code is:",f[0]
								#print "location is:", f[1]
					else:
						req = urllib2.Request(url=uri,data=w.toxml())
						opener = urllib2.build_opener(proxy_handler)
						f = opener.open(req)
				
				rsp = f.read()
				if (dumpXml in _AffirmativeList):
					print '%s <==== %s' % (self._ucs, rsp)
	
				#method = method.propMoMeta.name
				response = ExternalMethod(method.propMoMeta.name)
				doc = parseString(rsp)
				response.LoadFromXml(doc.childNodes[0], self)
				return response
			#For catching URLError and returning string representation of URLError class as there is no
			#message attribute in this class.
#			except urllib2.URLError, e:
#				response = ExternalMethod(method.propMoMeta.name)
#				response.getErrorResponse("300",str(e))
#				return response
#			#For catching HTTPError and returning msg attribute of this class.
#			except urllib2.HTTPError, e:
#				response = ExternalMethod(method.propMoMeta.name)
#				response.getErrorResponse(e.code,e.msg)
#				return response
#			#Wide Catch block for catching all type of exception objects.
#			except Exception, e:
#				response = ExternalMethod( method.propMoMeta.name)
#				response.getErrorResponse("300",e.message)
#				return response
			except Exception, e:
				raise
		
	def XmlRawQuery(self, xml, dumpXml=None):
		"""	Accepts xmlQuery String and returns xml response String. No object manipulation is done in this method.	"""
		
		if (dumpXml == None):
			dumpXml = self._dumpXml
		
		uri = self.Uri() + '/nuova'
		if (dumpXml in _AffirmativeList):
			print '%s ====> %s' % (self._ucs, xml)
		#req = urllib2.Request(url=uri,data=xml)
		#f = urllib2.urlopen(req)
		w = xml.dom.minidom.Document()
		
		if(self._noSsl):
			req = urllib2.Request(url=uri,data=w.toxml())
			opener = urllib2.build_opener(SmartRedirectHandler())
			f = opener.open(req)
			#print "##", f , "##"
			
			if type(f) is list:
				if(len(f) == 2 and f[0] == 302):
					#self._noSsl = False
					#uri = self.Uri() + '/nuova'
					uri = f[1]
					req = urllib2.Request(url=uri,data=w.toxml())
					f = urllib2.urlopen(req)						
					#print "status code is:",f[0]
					#print "location is:", f[1]
		else:
			req = urllib2.Request(url=uri,data=w.toxml())
			f = urllib2.urlopen(req)
		
		rsp = f.read()
		if (dumpXml in _AffirmativeList):
			print '%s <==== %s' % (self._ucs, rsp)
		return rsp

	def Login(self, name, username=None, password=None, noSsl=False, port=None, dumpXml=None, proxy=None, autoRefresh=YesOrNo.FALSE):
		"""
		Login method authenticates and connects to UCS.
		
		- name specifies the IP Address IMC Server.
		- username specifies the username credential.
		- password specifies the password credential.
		- noSsl specifies if the connection is made via http(True) or https(False). Default is False.
		- port specifies the port. Default is 80(http) or 443(https).
		- proxy specifies if the is made via proxy.
		- autoRefresh specifes to True to keep the cookie alive.Default is False.		
		"""
		from UcsBase import ManagedObject,UcsUtils,WriteUcsWarning,UcsException,UcsValidationException
		from Mos import FirmwareRunning
		import getpass
		
		if (name == None):
			#raise Exception('[Error]: Hostname/IP was not specified')
			raise UcsValidationException('Hostname/IP was not specified')

		if (username == None):
			username = raw_input("Username: ")

		if (password == None):
			password = getpass.getpass()

		if (self._cookie != None):
			self.Logout(dumpXml)

		ucs = name
		self._name = name
		self._username = username
		self._password = password
		self._noSsl = noSsl
		if (port != None):
			self._port = port
		elif (noSsl == True):
			self._port = 80
		else:
			self._port = 443
		
		if (proxy != None):
			self._proxy = proxy
			
		self._cookie = ""
		response = self.AaaLogin(username, password, dumpXml)

		if (response == None):
			return False
		if (response.errorCode != 0):
			ucs = None
			virtualIpv4Address = None
			self._name = None
			self._username = None
			self._password = None
			self._noSsl = False
			self._port = 443
			#raise Exception('[Error]: Login : Connection to <%s> Failed' %(name))
			raise UcsException(response.errorCode, response.errorDescr)

		self._cookie = response.OutCookie
		self._lastUpdateTime = str(time.asctime())
		self._domains = response.OutDomains
		self._priv = response.OutPriv.split(',')
		self._refreshPeriod = int(response.OutRefreshPeriod)
		self._sessionId = response.OutSessionId
		self._version = UcsVersion(response.OutVersion)

		crDn = self.ConfigResolveDn(ManagedObject(NamingId.TOP_SYSTEM).MakeRn(), False, dumpXml)
		if (crDn.errorCode == 0):
			for ts in crDn.OutConfig.GetChild():
				self._ucs = ts.Name
				self._virtualIpv4Address = ts.Address

		if ((response.OutVersion == "") or (response.OutVersion == None)):
			firmwareObj = ManagedObject(NamingId.FIRMWARE_RUNNING)
			firmwareObj.Deployment = FirmwareRunning.CONST_DEPLOYMENT_SYSTEM
			rnArray = [ManagedObject(NamingId.TOP_SYSTEM).MakeRn(), ManagedObject(NamingId.MGMT_CONTROLLER).MakeRn(), firmwareObj.MakeRn()]
			crDn = self.ConfigResolveDn(UcsUtils.MakeDn(rnArray), False, dumpXml)
			if (crDn.errorCode == 0):
				for fr in crDn.OutConfig.GetChild():
					self._version = UcsVersion(fr.Version)

		if autoRefresh in _AffirmativeList:
			self._Start_refresh_timer()

		if self._ucs not in defaultUcs.keys():
			defaultUcs[self._ucs] = self
		return True

	def Logout(self, dumpXml = None):
		""" Logout method disconnects from UCS. """
		from UcsBase import UcsException
		if (self._cookie == None):
			return True

		if self._refreshTimer:
			self._refreshTimer.cancel()

		response = self.AaaLogout(dumpXml)
		self._cookie = None
		self._lastUpdateTime = str(time.asctime())
		self._domains = None
		self._priv = None
		self._sessionId = None
		self._version = None

		if self._ucs in defaultUcs.keys():
			del defaultUcs[self._ucs]

		if (response.errorCode != 0):
			raise UcsException(response.errorCode, response.errorDescr)
			#raise Exception('[Error]: Logout [Code]:' + response.errorCode + '[Description]:' + response.errorDescr)
		
		return True

	def _Start_refresh_timer(self):
		""" Internal method to support auto-refresh functionality. """
		if self._refreshPeriod > 60:
			interval = self._refreshPeriod-60
		else:
			interval = 60
		self._refreshTimer = Timer(self._refreshPeriod, self.Refresh)
		#TODO:handle exit and logout active connections. revert from daemon then
		self._refreshTimer.setDaemon(True)
		self._refreshTimer.start()

	def _Stop_refresh_timer(self):
		""" Internal method to support auto-refresh functionality. """
		if self._refreshTimer != None:
			self._refreshTimer.cancel()
			self._refreshTimer = None
			
	def Refresh(self, autoRelogin=False, dumpXml=YesOrNo.FALSE):
		"""
		Sends the aaaRefresh query to the UCS to refresh the connection (to prevent session expiration).
		"""	
		self._Stop_refresh_timer()
			
		response = self.AaaRefresh(self._username, self._password, dumpXml)
		if (response.errorCode != 0):
			self._cookie = None
			if (autoRelogin):
				return self.Login(self._name, self._username, self._password, self._noSsl, self._port, dumpXml, self._proxy, autoRefresh=YesOrNo.TRUE)
			return False

		self._domains = response.OutDomains
		self._priv = response.OutPriv.split(',')
		self._refreshPeriod = int(response.OutRefreshPeriod)
		self._cookie = response.OutCookie

		#re-enable the timer
		self._Start_refresh_timer()
		return True

	def _enqueue_function(self):
		"""
		Internal method used by AddEventHandler.
		
		Provides functionality of enqueue/dequeue of the events and triggering callbacks. 
		 """
		from UcsBase import _GenericMO, UcsUtils, WriteObject
		myThread = self._enqueueThread
		self._enqueueThreadSignal.acquire()
		try:
			xmlQuery = '<eventSubscribe cookie="' + self._cookie + '"/>'
			uri = self.Uri() + '/nuova'
			req = urllib2.Request(url=uri,data=xmlQuery)
			self._watchWebResponse = urllib2.urlopen(req)
			self._enqueueThreadSignal.notify()
			self._enqueueThreadSignal.release()
			
		except:
			self._enqueueThread = None
			self._enqueueThreadSignal.notify()
			self._enqueueThreadSignal.release()
			return

		try:
			sr = self._watchWebResponse
			while (self._watchWebResponse and len(self._wbs)):
				if self._cookie == None:
					break
				rsp = sr.readline()
				rsp = sr.read(int(rsp))
				#TODO:LoadFromXml with raw xml string, if possible
				#doc = xml.dom.minidom.parseString(rsp)
				#rootNode = doc.documentElement

				gmo = _GenericMO(loadXml = rsp)#Creating Generic Mo
				#gmo.LoadFromXml(rootNode)
				classId = gmo.classId

				if UcsUtils.WordL(classId) == NamingId.CONFIG_MO_CHANGE_EVENT:#Checks if the managed object is of type configMoChangeEvent and adds to queue.
					if myThread == self._enqueueThread:
						for inconfig in gmo.GetChildClassId("inconfig"):
							for moObj in inconfig.GetChild():
								mce = None
								for wb in self._wbs:
									if mce == None:
										mce = UcsMoChangeEvent(eventId = gmo.properties["inEid"], mo = moObj.ToManagedObject(), changeList = moObj.properties.keys())
									if (wb.fmce(mce)):#TODO: Need to add Filter Support.
										self._enqueueThreadSignal.acquire()#Acquire the Lock
										wb.Enqueue(mce)
										mce = None
										self._enqueueThreadSignal.notify()#Notify
										self._enqueueThreadSignal.release()#Release the Lock

				elif UcsUtils.WordL(classId) == NamingId.METHOD_VESSEL:#Checks if the managed object is of type methodVessel and adds to queue.
					if myThread == self._enqueueThread:
						for instimuli in gmo.GetChildClassId("inStimuli"):
							for cmce in instimuli.GetChildClassId("configMoChangeEvent"):
								for inconfig in cmce.GetChildClassId("inconfig"):
									for moObj in inconfig.GetChild():
										mce = None
										for wb in self._wbs:
											if mce == None:
												mce = UcsMoChangeEvent(eventId = cmce.properties["inEid"], mo = moObj.ToManagedObject(), changeList = moObj.properties.keys())
											if (wb.fmce(mce)):#TODO: Need to add Filter Support.
												self._enqueueThreadSignal.acquire()#Acquire the Lock
												wb.Enqueue(mce)
												mce = None
												self._enqueueThreadSignal.notify()#Notify
												self._enqueueThreadSignal.release()#Release the Lock
			
			self._enqueueThread = None
			self._watchWebResponse = None
			#if self._enqueueThreadSignal._is_owned():
			self._enqueueThreadSignal.acquire()#Acquire the Lock
			self._enqueueThreadSignal.notifyAll()
			self._enqueueThreadSignal.release()

		except Exception, err:
			if (self._wbslock == None):
				self._wbslock = Lock()
			self._wbslock.acquire()
			for wb in self._wbs:
				wb.errorCode = -1
			self._wbslock.release()
			self._enqueueThread = None
			self._watchWebResponse = None
			#if self._enqueueThreadSignal._is_owned():
			self._enqueueThreadSignal.acquire()#Acquire the Lock
			self._enqueueThreadSignal.notifyAll()
			self._enqueueThreadSignal.release()

	def _start_enqueue_thread(self):
		""" Internal method to start the enqueue thread which adds the events in an internal queue. """
		self._enqueueThreadSignal.acquire()
		self._enqueueThread = Thread(target=self._enqueue_function)
		self._enqueueThread.daemon = True
		self._enqueueThread.start()
		self._enqueueThreadSignal.wait()
		self._enqueueThreadSignal.release()

	def _add_watch_block(self, params, filterCb, capacity = 500, cb=None):
		""" Internal method to add a watch block for starting event monitoring. """
		if (self._wbslock == None):
			self._wbslock = Lock()

		self._wbslock.acquire()
		wb = WatchBlock(params, filterCb, capacity, cb)#Add a List of Watchers
		if ((wb != None) and (wb.cb == None)):
			wb.cb = wb._dequeue_default_cb

		self._wbs.append(wb)
		self._wbslock.release()

		if self._cookie == None:
			return None
		if wb != None and len(self._wbs) == 1 and wb.params["pollSec"] == None:
			self._start_enqueue_thread()
		if self._enqueueThread == None:
			return wb

		self._enqueueThreadSignal.acquire()
		self._enqueueThreadSignal.notify()#Notify
		self._enqueueThreadSignal.release()#Release the Lock

		return wb

	def _remove_watch_block(self, wb):
		""" Internal method to remove a watch block for stopping event monitoring. """
		if (self._wbslock == None):
			self._wbslock = Lock()

		self._wbslock.acquire()
		self._wbs.remove(wb)
		if len(self._wbs) == 0:
			self._stop_enqueue_thread()
			self._stop_dequeue_thread()

		self._wbslock.release()

	def _stop_enqueue_thread(self):
		""" Internal method to stop the enqueue thread. """
		self._enqueueThread = None
		self._watchWebResponse = None

	@staticmethod
	def _stop_wb_callback(signal, frame):
		for ucs in defaultUcs.keys():
			if (defaultUcs[ucs]._wbs):
				del defaultUcs[ucs]._wbs[:]
			if (defaultUcs[ucs]._enqueueThread):
				defaultUcs[ucs]._stop_dequeue_thread()
			if (defaultUcs[ucs]._dequeueThread):
				defaultUcs[ucs]._stop_enqueue_thread()
		return

	def AddEventHandler(self, classId = None, managedObject = None, prop = None, successValue = [], failureValue = [], transientValue = [], pollSec = None, timeoutSec=None, callBack=None):
		"""
		Adds an event handler.
		
		An event handler can be added using this method where an user can subscribe for the event channel from UCS and can monitor those events for any 
		specific success value or failure value for a managed object.
		- classId specifies the class name for which events should be monitored.
		- managedObject specifies a particular managed object that user wants to monitor. prop specifies the the property of the managed object which will
		  be monitored. successValue, failureValue, transientValue specifies the respective scenarios(success, failure etc) about the prop of managed object.
		- pollSec specifies the time in seconds for polling event.
		- timeoutSec specifies the time after which method should stop polling or timeOut.
		- callBack specifies the call Back Method or operation that can be given to this method
		"""
		from UcsBase import WriteObject, _GenericMO, UcsUtils, WriteUcsWarning, UcsValidationException
		if (self._transactionInProgress):
			raise UcsValidationException("UCS transaction in progress. Cannot execute WatchUcs. Complete or Undo UCS transaction.")
			#WriteUcsWarning("UCS transaction in progress. Cannot execute WatchUcs. Complete or Undo UCS transaction.")
			#return False

		if (classId != None and managedObject == None):
			if (UcsUtils.FindClassIdInMoMetaIgnoreCase(classId) == None):
				raise UcsValidationException("Invalid ClassId %s specified." %(classId))
				#raise Exception("Invalid ClassId %s specified." %(classId))
		
		elif (managedObject != None and classId == None):
			if (UcsUtils.FindClassIdInMoMetaIgnoreCase(managedObject.getattr("classId")) == None):
				raise UcsValidationException("Object of unknown ClassId %s provided." %(managedObject.getattr("classId")))
				#raise Exception("Object of unknown ClassId %s provided." %(managedObject.getattr("classId")))
			
			if prop == None:
				raise UcsValidationException("prop parameter is not provided.")
				#raise Exception("prop parameter is not provided.")
			
			propMeta = UcsUtils.GetUcsPropertyMeta(managedObject.getattr("classId"), UcsUtils.WordU(prop))
			if propMeta == None:
				raise UcsValidationException("Unknown Property %s provided." %(prop))
				#raise Exception("Unknown Property %s provided." %(prop))
			
			if not successValue:
				raise UcsValidationException("successValue parameter is not provided.")
				#raise Exception("successValue parameter is not provided.")
			
		elif (classId != None and managedObject != None):
			raise UcsValidationException("You cannot provide both classId and mandgedObject")
			#raise Exception("You cannot provide both classId and mandgedObject")

		wb = None
		paramDict = {'classId':classId, 'managedObject':managedObject, 'prop':prop, 'successValue':successValue, 'failureValue':failureValue, 'transientValue':transientValue, 'pollSec':pollSec, 'timeoutSec':timeoutSec, 'callBack':callBack, 'startTime':datetime.datetime.now()}

		if (classId == None and managedObject == None):
			def WatchUcsAllFilter(mce):
				return True
			wb = self._add_watch_block(params = paramDict, filterCb = WatchUcsAllFilter, cb = callBack)
		elif (classId != None and managedObject == None):
			def WatchUcsTypeFilter(mce):
				if ((mce.mo.getattr("classId")).lower() == classId.lower()):
					return True
				return False
			wb = self._add_watch_block(params = paramDict, filterCb = WatchUcsTypeFilter, cb = callBack)
		elif (classId == None and managedObject != None):
			if (pollSec == None):
				def WatchUcsMoFilter(mce):
					if (mce.mo.getattr("Dn") == managedObject.getattr("Dn")):
						return True
					return False
				wb = self._add_watch_block(params = paramDict, filterCb = WatchUcsMoFilter, cb = callBack)
			else:
				def WatchUcsNoneFilter(mce):
					return False
				wb = self._add_watch_block(params = paramDict, filterCb = WatchUcsNoneFilter, cb = callBack)

		signal.signal(signal.SIGINT, self._stop_wb_callback)

		if (wb == None):
			raise UcsValidationException("Error adding WatchBlock...")
			#raise Exception("Error adding WatchBlock...")

		if wb != None and len(self._wbs) == 1:
			self._start_dequeue_thread()

		return wb

	def RemoveEventHandler(self, wb):
		"""	Removes an event handler. """
		from UcsBase import WriteUcsWarning
		if wb in self._wbs:
			self._remove_watch_block(wb)
		else:
			WriteUcsWarning("Event handler not found")

	def GetEventHandlers(self):
		"""	Returns the list of event handlers.	"""
		return self._wbs

	def _start_dequeue_thread(self):
		""" Internal method to start dequeue thread. """
		self._dequeueThread = Thread(target=self._dequeue_function)
		self._dequeueThread.daemon = True
		self._dequeueThread.start()

	def _stop_dequeue_thread(self):
		""" Internal method to stop dequeue thread. """
		self._dequeueThread = None

	def _dequeue_function(self):
		""" Internal method to dequeue to events. """
		from UcsBase import WriteUcsWarning, _GenericMO, WriteObject, UcsUtils
		while len(self._wbs):
			lowestTimeout = None
			for wb in self._wbs:
				pollSec = wb.params["pollSec"]
				managedObject = wb.params["managedObject"]
				timeoutSec = wb.params["timeoutSec"]
				transientValue = wb.params["transientValue"]
				successValue = wb.params["successValue"]
				failureValue = wb.params["failureValue"]
				prop = wb.params["prop"]
				startTime =	wb.params["startTime"]

				gmo = None
				pmo = None
				mce = None

				if (pollSec != None and managedObject != None):
					crDn = self.ConfigResolveDn(managedObject.getattr("Dn"), inHierarchical=YesOrNo.FALSE, dumpXml=YesOrNo.FALSE)
					if (crDn.errorCode != 0):
						#TODO: Add Warning/Error messages in Logger.
						WriteUcsWarning('[Error]: WatchUcs [Code]:' + crDn.errorCode + ' [Description]:' + crDn.errorDescr)
						continue

					for eachMo in crDn.OutConfig.GetChild():
						pmo = eachMo
					if pmo == None:
						#TODO: Add Warning/Error messages in Logger.
						WriteUcsWarning('Mo ' + managedObject.getattr("Dn") + ' not found.')
						continue

					gmo = _GenericMO(mo=pmo, option=WriteXmlOption.All)
				else:
					ts = datetime.datetime.now() - startTime
					timeoutMs = 0
					if (timeoutSec != None):
						if (ts.seconds>=timeoutSec):#TimeOut
							self._remove_watch_block(wb)
							continue
						timeoutMs = (timeoutSec - ts.seconds)

						if (lowestTimeout == None):
							lowestTimeout = timeoutMs
						else:
							if (lowestTimeout > timeoutMs):
								lowestTimeout = timeoutMs

					if (timeoutMs > 0):
						mce = wb.Dequeue(timeoutMs)
					else:
						mce = wb.Dequeue(2147483647)
					if mce == None:
						#break
						continue

				if (managedObject == None):#Means parameterset is not Mo
					if wb.cb != None:
						wb.cb(mce)
					continue

				if mce != None:
					gmo = _GenericMO(mo = mce.mo, option = WriteXmlOption.All)

				attributes = []
				if mce == None:
					attributes = gmo.properties.keys()
				else:
					attributes = mce.changeList
				if prop.lower() in (attr.lower() for attr in attributes):
					if (len(successValue) > 0 and gmo.GetAttribute(UcsUtils.WordU(prop)) in successValue):
						if mce != None:
							if wb.cb != None:
								wb.cb(mce)
						else:
							if wb.cb != None:
								wb.cb(UcsMoChangeEvent(eventId = 0, mo = pmo, changeList = prop))

						if wb != None:
							self._remove_watch_block(wb)
							wb = None
							break

						#return
						continue
					if (len(failureValue) > 0 and gmo.GetAttribute(UcsUtils.WordU(prop)) in failureValue):
						#TODO: Add Warning/Error messages in Logger.
						WriteUcsWarning('Encountered error value ' + gmo.GetAttribute(UcsUtils.WordU(prop)) + ' for property ' + prop + '.')
						if mce != None:
							if wb.cb != None:
								wb.cb(mce)
						else:
							if wb.cb != None:
								wb.cb(UcsMoChangeEvent(eventId = 0, mo = pmo, changeList = prop))

						if wb != None:
							self._remove_watch_block(wb)#TODO: implement removeStop call back
							wb = None
							break
						
						continue
					if ((len(transientValue) > 0) and (not gmo.GetAttribute(UcsUtils.WordU(prop)) in transientValue)):
						#TODO: Add Warning/Error messages in Logger.
						WriteUcsWarning('Encountered unknown value ' + gmo.GetAttribute(UcsUtils.WordU(prop)) + ' for property ' + prop + '.')
						if mce != None:
							if wb.cb != None:
								wb.cb(mce)
						else:
							if wb.cb != None:
								wb.cb(UcsMoChangeEvent(eventId = 0, mo = pmo, changeList = prop))

						if wb != None:
							self._remove_watch_block(wb)#TODO: implement removeStop call back
							wb = None
							break
						
						continue

				if (pollSec != None):
					pollMs = pollSec
					if (timeoutSec != None):
						pts = datetime.datetime.now() - startTime
						if (pts.seconds>=timeoutSec):#TimeOut
							break
						timeoutMs = (timeoutSec - pts.seconds)

						if (timeoutMs < pollSec):
							pollMs = pts.seconds

					#time.sleep(pollMs)
					if (lowestTimeout == None):
						lowestTimeout = pollMs
					else:
						if (lowestTimeout > pollMs):
							lowestTimeout = pollMs
							
			if len(self._wbs):
				self._dequeue_wait(lowestTimeout)
		return

	def _dequeue_wait(self, timeout=None):
		self._enqueueThreadSignal.acquire()
		if (timeout != None):
			self._enqueueThreadSignal.wait(timeout)
		else:
			self._enqueueThreadSignal.wait()
		self._enqueueThreadSignal.release()

	def StartKvmSession(self, serviceProfile = None, blade = None, rackUnit = None, frameTitle = None, dumpXml=None):
		"""
		Starts KVM session.
		
		launches the KVM session for the specific service profile, blade or rackUnit.
		- serviceProfile specifies an object of type lsServer. Launches KVM session with which the service profile is associated. 
		- blade specifies an object of type computeBlade. Launches KVM session of blade server.
		- rackUnit specifies an object of type computeRackUnit. Launches KVM session of rack Unit.
		- frameTitle specifies the title of the frame window.
		"""
		from UcsBase import WriteUcsWarning, _GenericMO, UcsUtils, UcsValidationException, UcsException
		from Mos import MgmtIf
		import os, subprocess, urllib
		
		if (self._transactionInProgress):
			raise UcsValidationException("UCS transaction in progress. Cannot execute StartKvmSession. Complete or Undo UCS transaction.")
			#raise Exception("UCS transaction in progress. Cannot execute StartKvmSession. Complete or Undo UCS transaction.")
		
		if ((blade != None and rackUnit!= None) or (serviceProfile != None and rackUnit!= None) or (blade != None and serviceProfile != None)):
			raise UcsValidationException("Please provide only one parameter from blade, rackUnit and service profile.")
			#raise Exception("Please provide only one parameter from blade, rackUnit and service profile.")
		
		if (serviceProfile == None and blade == None and rackUnit == None):
			raise UcsValidationException("Please provide at least one parameter from blade, rackUnit and service profile.")
			#raise Exception("Please provide at least one parameter from blade, rackUnit and service profile.")
		
		minVersion = UcsVersion('1.4(1a)')
		if self._version < minVersion:
			raise UcsValidationException("StartKvmSession not supported for Ucs version older than %s. You are connected to Ucs Version %s" %(minVersion, self._version))
			#raise Exception("StartKvmSession not supported for Ucs version older than %s. You are connected to Ucs Version %s" %(minVersion, self._version))
		
		PARAM_CENTRALE_PASSWORD = "centralePassword"
		PARAM_CENTRALE_USER = "centraleUser"
		PARAM_DN = "dn"
		PARAM_FRAME_TITLE = "frameTitle"
		PARAM_KVM_IP_ADDR = "kvmIpAddr"
		PARAM_KVM_PASSWORD = "kvmPassword"
		PARAM_KVM_PN_DN = "kvmPnDn"
		PARAM_KVM_USER = "kvmUser"
		PARAM_TEMP_UNPW = "tempunpw"
		PARAM_KVM_DN = "kvmDn"
		
		_lock = Lock()
		sp_bool = False
		nvc = {}
		dn = None
		pnDn = None
		ipAddress = None
		
		if ((blade != None) or (rackUnit!= None)):
			if (blade != None):
				pnDn = blade.getattr("Dn")
			else:
				pnDn = rackUnit.getattr("Dn")
			
			nvc[PARAM_DN] = pnDn
			if (frameTitle == None):
				frameTitle = self._ucs + ':' + pnDn + ' KVM Console'
				
			nvc[PARAM_FRAME_TITLE] = frameTitle
			nvc[PARAM_KVM_PN_DN] = pnDn
			
			cs = self.ConfigScope(dn = pnDn, inClass = NamingId.MGMT_IF, inFilter = None, inRecursive = YesOrNo.FALSE, inHierarchical = YesOrNo.FALSE, dumpXml = dumpXml)
			if (cs.errorCode == 0):
				for mgmtIf in cs.OutConfigs.GetChild():
					if ((mgmtIf.getattr("Subject") == MgmtIf.CONST_SUBJECT_BLADE) and (mgmtIf.getattr("AdminState") == MgmtIf.CONST_ADMIN_STATE_ENABLE)):
						ipAddress = mgmtIf.getattr("ExtIp")
			else:
				raise UcsException(cs.errorCode, cs.errorDescr)
				#raise Exception('[Error]: StartKvmSession [Code]:' + cs.errorCode + ' [Description]:' + cs.errorDescr)
			
			#If the blade does not have an IP, check if a service profile is associated
			if ((ipAddress == None) or (ipAddress == '0.0.0.0')):
				crDn = self.ConfigResolveDn(pnDn, inHierarchical=YesOrNo.TRUE, dumpXml=dumpXml)
				if (crDn.errorCode != 0):
					raise UcsException(crDn.errorCode, crDn.errorDescr)
					#raise Exception('[Error]: StartKvmSession [Code]:' + crDn.errorCode + ' [Description]:' + crDn.errorDescr)

				for mo in crDn.OutConfig.GetChild():
					dn = mo.getattr("AssignedToDn")
				if dn != None:
					sp_bool = True

		if (sp_bool or serviceProfile != None):
			if dn == None:
				dn = serviceProfile.getattr("Dn")
				if (frameTitle == None):
					frameTitle = self._ucs + ':' + dn + ' KVM Console'
				nvc[PARAM_FRAME_TITLE] = frameTitle
			
			nvc[PARAM_KVM_DN] = dn
			crDn = self.ConfigResolveDn(dn, inHierarchical=YesOrNo.TRUE, dumpXml=dumpXml)
			if (crDn.errorCode != 0):
				raise UcsException(crDn.errorCode, crDn.errorDescr)
				#raise Exception('[Error]: StartKvmSession [Code]:' + crDn.errorCode + ' [Description]:' + crDn.errorDescr)
			
			spMo = None
			for mo in crDn.OutConfig.GetChild():
				spMo = mo
			if spMo == None:
				raise Exception('Service Profile not found.')
			
			if spMo.getattr("PnDn") == None:
				raise UcsValidationException('Service Profile is not associated with blade or rackUnit.')
				#raise Exception('Service Profile is not associated with blade or rackUnit.')
			
			pnDn = spMo.getattr("PnDn")
			nvc[PARAM_DN] = pnDn
			
			crc = self.ConfigResolveChildren('vnicIpV4Addr', dn, None, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)#TODO:replace classId with proper constantafter generating mos.py or Constant.py
			if (crc.errorCode == 0):
				for mo in crc.OutConfigs.GetChild():
					gmo = _GenericMO(mo=mo, option=WriteXmlOption.All)
					if not('Addr' in gmo.properties.keys()):
						continue
					
					ipAddress = gmo.GetAttribute('Addr')
					if ipAddress != None:
						break
			else:
				raise UcsException(crc.errorCode, crc.errorDescr)
				#raise Exception('[Error]: StartKvmSession [Code]:' + crc.errorCode + ' [Description]:' + crc.errorDescr)
			
		if (((ipAddress == None) or (ipAddress == '0.0.0.0')) and (serviceProfile != None )):	
			cs = self.ConfigScope(dn = pnDn, inClass = NamingId.MGMT_IF, inFilter = None, inRecursive = YesOrNo.FALSE, inHierarchical = YesOrNo.FALSE, dumpXml = dumpXml)
			if (cs.errorCode == 0):
				for mgmtIf in cs.OutConfigs.GetChild():
					if ((mgmtIf.getattr("Subject") == MgmtIf.CONST_SUBJECT_BLADE) and (mgmtIf.getattr("AdminState") == MgmtIf.CONST_ADMIN_STATE_ENABLE)):
						ipAddress = mgmtIf.getattr("ExtIp")
			else:
				raise UcsException(cs.errorCode, cs.errorDescr)
				#raise Exception('[Error]: StartKvmSession [Code]:' + cs.errorCode + ' [Description]:' + cs.errorDescr)
		
		if ((ipAddress == None) or (ipAddress == '0.0.0.0')):
			raise UcsValidationException("No assigned IP address to use.")
			#raise Exception("No assigned IP address to use.")
		
		nvc[PARAM_KVM_IP_ADDR] = ipAddress
		cat = self.AaaGetNComputeAuthTokenByDn(pnDn, 2, dumpXml = dumpXml)
		if (cat.errorCode == 0):
			nvc[PARAM_CENTRALE_PASSWORD] = cat.OutTokens.split(',')[0]
			nvc[PARAM_CENTRALE_USER] = cat.OutUser
			nvc[PARAM_KVM_PASSWORD] = cat.OutTokens.split(',')[1]
			nvc[PARAM_KVM_USER] = cat.OutUser
		else:
			raise UcsException(cat.errorCode, cat.errorDescr)
			#raise Exception('[Error]: StartKvmSession [Code]:' + cat.errorCode + ' [Description]:' + cat.errorDescr)
		
		
		nvc[PARAM_TEMP_UNPW] = "true"
		kvmUrl = '%s/ucsm/kvm.jnlp?%s' %(self.Uri(), urllib.urlencode(nvc))
		
		installPath = UcsUtils.GetJavaInstallationPath()
		if installPath != None:
			subprocess.call([installPath, kvmUrl])
		else:
			#TODO: Add Warning/Error messages in Logger.
			WriteUcsWarning("Java is not installed on System.")
			p = subprocess.Popen(kvmUrl)
	
	def StartGuiSession(self):
		"""	Launches the UCSM GUI via specific UCS handle. """
		from UcsBase import WriteUcsWarning, UcsUtils, UcsValidationException
		import urllib, tempfile, fileinput, os, subprocess, platform
		
		osSupport = ["Windows","Linux","Microsoft"]
		
		if platform.system() not in osSupport:
			raise UcsValidationException("Currently works with Windows OS and Ubuntu")
			#raise Exception("Currently works with Windows OS and Ubuntu")
		
		try:
			javawsPath = UcsUtils.GetJavaInstallationPath()
			#print r"%s" %(javawsPath)
			if javawsPath != None:
				
				url = "%s/ucsm/ucsm.jnlp" %(self.Uri())
				source = urllib.urlopen(url).read()
				
				jnlpdir = tempfile.gettempdir()
				jnlpfile = os.path.join(jnlpdir, "temp.jnlp")
				
				if os.path.exists(jnlpfile):
					os.remove(jnlpfile)
				
				jnlpFH = open(jnlpfile, "w+")
				jnlpFH.write(source)
				jnlpFH.close()
				
				for line in fileinput.input(jnlpfile, inplace=1):
					if re.search(r'^\s*</resources>\s*$', line):
							print '\t<property name="log.show.encrypted" value="true"/>'
					print line,
				
				subprocess.call([javawsPath, jnlpfile])
				
				if os.path.exists(jnlpfile):
					os.remove(jnlpfile)
			else:
				return None
				
		except Exception, err:
			fileinput.close()
			if os.path.exists(jnlpfile):
				os.remove(jnlpfile)
			raise
			#WriteUcsWarning("Not able to start Gui Session.")
			
	def BackupUcs(self, type, pathPattern, timeoutSec = 600, preservePooledValues = False, dumpXml=None):
		"""
		Creates and downloads the backup of UCS.
		
		- type specifies the type of backup i.e. fullstate/config-logical/config-system/config-all.
		- pathPattern specifies the path of the Backup file. 
		- timeoutSec specifies the time in seconds for which method waits for the backUp file to generate else exit.
		"""
		from UcsBase import WriteUcsWarning, UcsUtils, ManagedObject, WriteObject, UcsUtils, UcsValidationException, UcsException
		from Mos import TopSystem, MgmtBackup
		from Ucs import ConfigConfig
		import os, platform
		
		if (self._transactionInProgress):
			raise UcsValidationException("UCS transaction in progress. Cannot execute BackupUcs. Complete or Undo UCS transaction.")
			#raise Exception("UCS transaction in progress. Cannot execute BackupUcs. Complete or Undo UCS transaction.")
		if (type== None or pathPattern == None):
			raise UcsValidationException("type or pathPattern parameter is not provided.")
			#raise Exception("Please provide type/pathPattern parameter.")
		if type=="fullstate" and not pathPattern.endswith('.tar.gz'):
			raise UcsValidationException('pathPattern should end with .tar.gz')
		elif not pathPattern.endswith('.xml'):
			raise UcsValidationException('pathPattern should end with .xml')
		
		directory = os.path.dirname(pathPattern)
		if not (os.path.exists(directory)):
			os.makedirs(directory)
		hostname = platform.node().lower() + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
		mgmtBackup = ManagedObject(NamingId.MGMT_BACKUP)
		mgmtBackup.Hostname = hostname
		dn = UcsUtils.MakeDn([ManagedObject(NamingId.TOP_SYSTEM).MakeRn(), mgmtBackup.MakeRn()])
			
		if (type == MgmtBackup.CONST_TYPE_FULL_STATE or type == MgmtBackup.CONST_TYPE_CONFIG_SYSTEM):
			preservePooledValues = False
		
		mgmtBackup = ManagedObject(NamingId.MGMT_BACKUP)
		mgmtBackup.AdminState = MgmtBackup.CONST_ADMIN_STATE_ENABLED
		mgmtBackup.Dn = dn
		mgmtBackup.Status = Status.CREATED
		mgmtBackup.Proto = MgmtBackup.CONST_PROTO_HTTP
		mgmtBackup.Type = type
		mgmtBackup.RemoteFile = pathPattern
		
		if (preservePooledValues):
			mgmtBackup.PreservePooledValues = MgmtBackup.CONST_PRESERVE_POOLED_VALUES_YES
		else:
			mgmtBackup.PreservePooledValues = MgmtBackup.CONST_PRESERVE_POOLED_VALUES_NO

		inConfig = ConfigConfig()
		inConfig.AddChild(mgmtBackup)
		ccm = self.ConfigConfMo(dn = dn, inConfig = inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
		if (ccm.errorCode != 0):
			raise UcsException(ccm.errorCode, ccm.errorDescr)
			#raise Exception('[Error]: BackupUcs [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)

		duration = timeoutSec
		poll_interval = 2
		
		#Checking for the backup to compete.
		adminStateTemp = None
		crDn = None
		while (True):
			crDn = self.ConfigResolveDn(dn, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
			if (crDn.errorCode == 0):
				for eachMgmtDn in crDn.OutConfig.GetChild():
					adminStateTemp = eachMgmtDn.AdminState
			else:
				raise UcsException(crDn.errorCode, crDn.errorDescr)
				#raise Exception('[Error]: BackupUcs [Code]:' + crDn.errorCode + ' [Description]:' + crDn.errorDescr)
			
			#Break condition:- if state id disabled then break
			if(adminStateTemp == MgmtBackup.CONST_ADMIN_STATE_DISABLED):
				break
			
			time.sleep(min(duration, poll_interval))
			duration = max(0, (duration-poll_interval))
			
			if duration == 0:
				mgmtBackup = ManagedObject(NamingId.MGMT_BACKUP)
				mgmtBackup.Dn = dn
				mgmtBackup.Status = Status.DELETED
				inConfig.AddChild(mgmtBackup)
				ccm = self.ConfigConfMo(dn = dn, inConfig = inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
				if (ccm.errorCode != 0):
					raise UcsException(ccm.errorCode, ccm.errorDescr)
					#raise Exception('[Error]: BackupUcs [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)
				raise UcsValidationException('BackupUcs timed out')
				#raise Exception('BackupUcs timed out')
			
		WriteObject(crDn.OutConfig.GetChild())#BackUp Complete.
		
		fileSource = "backupfile/" + os.path.basename(pathPattern)
		
		try:
			UcsUtils.DownloadFile(self, fileSource, pathPattern)
		except Exception, err:
			WriteUcsWarning(str(err))
		
		inConfig = ConfigConfig()
		mgmtBackup = ManagedObject(NamingId.MGMT_BACKUP)
		mgmtBackup.Dn = dn
		mgmtBackup.Status = Status.DELETED
		inConfig.AddChild(mgmtBackup)
		ccm = self.ConfigConfMo(dn = dn, inConfig = inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
		if (ccm.errorCode != 0):
			raise UcsException(ccm.errorCode, ccm.errorDescr)
			#raise Exception('[Error]: BackupUcs [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)
		
		return crDn.OutConfig.GetChild()
	
	
	def ImportUcsBackup(self, path=None, merge=False, dumpXml=False):
		"""
		Imports backUp.
		
		This operation will upload the UCSM backup taken earlier via GUI or BackupUcs operation for all configuration, system configuration, and 
		logical configuration files. User can perform an import while the system is up and running.
		- path specifies path of the backup file.
		- merge specifies whether to merge the backup configuration with the existing UCSM configuration. 
		"""
		from UcsBase import WriteUcsWarning, UcsUtils, ManagedObject, WriteObject, UcsUtils, UcsException, UcsValidationException
		from Ucs import ConfigConfig
		from Mos import MgmtImporter
		from datetime import datetime
		
		if (self._transactionInProgress):
			raise UcsValidationException("UCS transaction in progress. Cannot execute ImportUcsBackup. Complete or Undo UCS transaction.")
			#raise Exception("UCS transaction in progress. Cannot execute ImportUcsBackup. Complete or Undo UCS transaction.")

		if not path:
			raise UcsValidationException("path parameter is not provided.")
			#raise Exception("Please provide path")
		
		if not os.path.exists(path):
			raise UcsValidationException("Backup File not found <%s>" %(path))
			#raise Exception("Backup File not found <%s>" %(path))
		
		dn = None
		filePath = path
		localFile = os.path.basename(filePath)
		
		topSystem = ManagedObject(NamingId.TOP_SYSTEM)
		mgmtImporter = ManagedObject(NamingId.MGMT_IMPORTER)
		
		mgmtImporter.Hostname = os.environ['COMPUTERNAME'].lower() + datetime.now().strftime('%Y%m%d%H%M')
		dn = UcsUtils.MakeDn([topSystem.MakeRn(), mgmtImporter.MakeRn()])
		
		mgmtImporter.Dn = dn
		mgmtImporter.Status = Status.CREATED
		mgmtImporter.RemoteFile = filePath
		mgmtImporter.Proto = MgmtImporter.CONST_PROTO_HTTP
		mgmtImporter.AdminState = MgmtImporter.CONST_ADMIN_STATE_ENABLED

		if merge:
			mgmtImporter.Action = MgmtImporter.CONST_ACTION_MERGE
		else:
			mgmtImporter.Action = MgmtImporter.CONST_ACTION_REPLACE
		
		inConfig = ConfigConfig()
		inConfig.AddChild(mgmtImporter)
		
		uri = "%s/operations/file-%s/importconfig.txt" %(self.Uri(),localFile)
		
		if sys.version_info < (2, 6):
			uploadFileHandle = open(filePath,'rb')
			stream = uploadFileHandle.read()
		else:	
			progress = Progress()
			stream = file_with_callback(filePath, 'rb', progress.update, filePath)
		
		request = urllib2.Request(uri)
		request.add_header('Cookie','ucsm-cookie=%s' %(self._cookie))
		request.add_data(stream)
		
		response = urllib2.urlopen(request).read()
		
		if not response:
			raise UcsValidationException("Unable to upload properly.")
			#WriteUcsWarning("Unable to upload properly.")
		
		ccm = self.ConfigConfMo(dn = dn, inConfig = inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
		
		if (ccm.errorCode != 0):
			raise UcsException(ccm.errorCode, ccm.errorDescr)
			#raise Exception('[Error]: BackupUcs [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)
		
		return ccm.OutConfig.GetChild()

	def SendUcsFirmware(self,path=None,dumpXml=False):
		"""
		Uploads a specific CCO Image on UCS.
		
		- path specifies the path of the image to be uploaded.
		"""
		from UcsBase import WriteUcsWarning, UcsUtils, ManagedObject, WriteObject, UcsUtils, UcsValidationException, UcsException
		from Ucs import ConfigConfig
		from Mos import FirmwareDownloader

		if (self._transactionInProgress):
			raise UcsValidationException("UCS transaction in progress. Cannot execute SendUcsFirmware. Complete or Undo UCS transaction.")
			#raise Exception("UCS transaction in progress. Cannot execute SendUcsFirmware. Complete or Undo UCS transaction.")

		if not path:
			raise UcsValidationException("path parameter is not provided.")
			#raise Exception("Please provide path")
		
		if not os.path.exists(path):
			raise UcsValidationException("Image not found <%s>" %(path))
			#raise Exception("Image not found <%s>" %(path))	
				
		dn = None
		filePath = path
		localFile = os.path.basename(filePath)
		
		# Exit if image already exist on UCSM 
		topSystem = ManagedObject(NamingId.TOP_SYSTEM)
		firmwareCatalogue = ManagedObject(NamingId.FIRMWARE_CATALOGUE)
		firmwareDistributable = ManagedObject(NamingId.FIRMWARE_DISTRIBUTABLE)
		firmwareDistributable.Name = localFile								
	
		dn = UcsUtils.MakeDn([topSystem.MakeRn(), firmwareCatalogue.MakeRn(), firmwareDistributable.MakeRn()])
		crDn = self.ConfigResolveDn(dn, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
		
		if ( crDn.OutConfig.GetChildCount() > 0 ):
			raise UcsValidationException("Image file <%s> already exist on FI." %(filePath))
			#raise Exception("Image file <%s> already exist on FI." %(filePath))
		
		# Create object of type <firmwareDownloader>
		firmwareDownloader = ManagedObject(NamingId.FIRMWARE_DOWNLOADER)
		firmwareDownloader.FileName = localFile
		dn = UcsUtils.MakeDn([topSystem.MakeRn(), firmwareCatalogue.MakeRn(), firmwareDownloader.MakeRn()])
		
		firmwareDownloader.Dn = dn
		firmwareDownloader.Status = Status.CREATED
		firmwareDownloader.FileName = localFile
		firmwareDownloader.Server = FirmwareDownloader.CONST_PROTOCOL_LOCAL
		firmwareDownloader.Protocol = FirmwareDownloader.CONST_PROTOCOL_LOCAL
		
		inConfig = ConfigConfig()
		inConfig.AddChild(firmwareDownloader)
		
		uri = "%s/operations/file-%s/image.txt" %(self.Uri(),localFile)
	
		progress = Progress()
		stream = file_with_callback(filePath, 'rb', progress.update, filePath)
		request = urllib2.Request(uri)
		request.add_header('Cookie','ucsm-cookie=%s' %(self._cookie))
		request.add_data(stream)
		
		response = urllib2.urlopen(request).read()
		if not response:
			raise UcsValidationException("Unable to upload properly.")
			#WriteUcsWarning("Unable to upload properly.")
		
		ccm = self.ConfigConfMo(dn = dn, inConfig = inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
		if (ccm.errorCode != 0):
			raise UcsException(ccm.errorCode, ccm.errorDescr)
		
		return ccm.OutConfig.GetChild()
		
	def GetTechSupport(self, pathPattern , ucsManager=False, ucsMgmt=False, chassisId=None, cimcId=None, adapterId=None, iomId=None, fexId=None, rackServerId=None, rackAdapterId=None, timeoutSec=600, removeFromUcs=False, dumpXml=None):
		"""
		Creates and downloads the technical support data for the respective UCSM.
		
		- pathPattern specifies the path of the tech support file to be downloaded. File should be a tar file.
		- ucsManager, if provided as True then technical support data for the entire UCSM instance will be created and downloaded.
		- ucsMgmt, if provided as True then technical support data for the entire UCSM management services(excluding fabric interconnects)
		  will be created and downloaded.
		- chassisId specifies the chassis Id.
		- cimcId for a specific chassis. Can be 'all' also.
		- adapterId for a specific chassis. Can be 'all' also.
		- iomId for a specific chassis. Can be 'all' also.
		- fexId specifies the Id of a fabric extender.
		- rackServerId specifies the Id of a rack server.
		- rackAdapterId specifies the adaptor Id for a specific rack server. Can be 'all' also.
		- timeoutSec specifies the time in seconds after that the operation will terminate.
		- removeFromUcs, if specified as True then the techincal support data file will be removed from the UCS.
		"""
		from UcsBase import WriteUcsWarning, UcsUtils, ManagedObject, WriteObject, UcsUtils, UcsValidationException, UcsException
		from Mos import SysdebugTechSupport, SysdebugTechSupportCmdOpt
		from Ucs import ConfigConfig
		import os
		
		if (self._transactionInProgress):
			raise UcsValidationException("UCS transaction in progress. Cannot execute GetTechSupport. Complete or Undo UCS transaction.")
			#raise Exception("UCS transaction in progress. Cannot execute GetTechSupport. Complete or Undo UCS transaction.")
		
		if (pathPattern == None):
			raise UcsValidationException("pathPattern parameter is not provided.")
			#raise Exception("Please provide pathPattern parameter.")
		
		if not pathPattern.endswith('.tar'):
			raise UcsValidationException('pathPattern should end with .tar')
		
		directory = os.path.dirname(pathPattern)
		if not (os.path.exists(directory)):
			os.makedirs(directory)
		
		inConfig = ConfigConfig()
		techSupportObj = None
		
		dt1 = datetime.datetime(1970, 1, 1, 12, 0, 0, 0)
		dt2 = datetime.datetime.utcnow()
		
		ds = (dt2-dt1)
		creationTS = (ds.microseconds/1000000) + (ds.days*24*60*60) + ds.seconds#Converting timedelta in to total seconds for Python version compatibility.
		sysdebug = ManagedObject(NamingId.SYSDEBUG_TECH_SUPPORT)
		sysdebug.CreationTS = str(creationTS)
		dn = UcsUtils.MakeDn([ManagedObject(NamingId.TOP_SYSTEM).MakeRn(), ManagedObject(NamingId.SYSDEBUG_TECH_SUP_FILE_REPOSITORY).MakeRn(), sysdebug.MakeRn()])
		
		sysdebugTechSupport = ManagedObject(NamingId.SYSDEBUG_TECH_SUPPORT)
		sysdebugTechSupport.DN = dn
		sysdebugTechSupport.AdminState = SysdebugTechSupport.CONST_ADMIN_STATE_START
		sysdebugTechSupport.CreationTS = str(creationTS)
		sysdebugTechSupport.Status = Status.CREATED

		sysdebugTechSupportCmdOpt = ManagedObject(NamingId.SYSDEBUG_TECH_SUPPORT_CMD_OPT)
		
		#Parameter Set UCSM
		if (ucsManager):			
			sysdebugTechSupportCmdOpt.MajorOptType = SysdebugTechSupportCmdOpt.CONST_MAJOR_OPT_TYPE_UCSM
			sysdebugTechSupportCmdOpt.Rn = sysdebugTechSupportCmdOpt.MakeRn()
			
			sysdebugTechSupport.AddChild(sysdebugTechSupportCmdOpt)
		elif (ucsMgmt):			
			sysdebugTechSupportCmdOpt.MajorOptType = SysdebugTechSupportCmdOpt.CONST_MAJOR_OPT_TYPE_UCSM_MGMT
			sysdebugTechSupportCmdOpt.Rn = sysdebugTechSupportCmdOpt.MakeRn()
			
			sysdebugTechSupport.AddChild(sysdebugTechSupportCmdOpt)
		elif (chassisId != None):
			if (cimcId != None):
				sysdebugTechSupportCmdOpt.ChassisCimcId = str(cimcId)
				sysdebugTechSupportCmdOpt.ChassisId = str(chassisId)
				sysdebugTechSupportCmdOpt.MajorOptType = SysdebugTechSupportCmdOpt.CONST_MAJOR_OPT_TYPE_CHASSIS
				if (adapterId == None):
					sysdebugTechSupportCmdOpt.CimcAdapterId = SysdebugTechSupportCmdOpt.CONST_CIMC_ADAPTER_ID_ALL
				else:
					sysdebugTechSupportCmdOpt.CimcAdapterId = str(adapterId)
				sysdebugTechSupportCmdOpt.Rn = sysdebugTechSupportCmdOpt.MakeRn()
				
				sysdebugTechSupport.AddChild(sysdebugTechSupportCmdOpt)
			elif (iomId != None):
				sysdebugTechSupportCmdOpt.ChassisIomId = str(iomId)
				sysdebugTechSupportCmdOpt.ChassisId = str(chassisId)
				sysdebugTechSupportCmdOpt.MajorOptType = SysdebugTechSupportCmdOpt.CONST_MAJOR_OPT_TYPE_CHASSIS
				sysdebugTechSupportCmdOpt.Rn = sysdebugTechSupportCmdOpt.MakeRn()
				
				sysdebugTechSupport.AddChild(sysdebugTechSupportCmdOpt)
		elif (rackServerId != None):
			sysdebugTechSupportCmdOpt.RACK_SERVER_ID = str(iomId)
			if (rackAdapterId == None):
				sysdebugTechSupportCmdOpt.RACK_SERVER_ADAPTER_ID = SysdebugTechSupportCmdOpt.CONST_RACK_SERVER_ADAPTER_ID_ALL
			else:
				sysdebugTechSupportCmdOpt.RACK_SERVER_ADAPTER_ID = str(rackAdapterId)
			sysdebugTechSupportCmdOpt.MajorOptType = SysdebugTechSupportCmdOpt.CONST_MAJOR_OPT_TYPE_SERVER
			sysdebugTechSupportCmdOpt.Rn = sysdebugTechSupportCmdOpt.MakeRn()
			
			sysdebugTechSupport.AddChild(sysdebugTechSupportCmdOpt)
		elif (fexId != None):
			sysdebugTechSupportCmdOpt.FAB_EXT_ID = str(iomId)
			sysdebugTechSupportCmdOpt.MajorOptType = SysdebugTechSupportCmdOpt.CONST_MAJOR_OPT_TYPE_FEX
			sysdebugTechSupportCmdOpt.Rn = sysdebugTechSupportCmdOpt.MakeRn()
			
			sysdebugTechSupport.AddChild(sysdebugTechSupportCmdOpt)
			
		if (sysdebugTechSupport.GetChildCount() == 0):
			sysdebugTechSupport = None
			sysdebugTechSupportCmdOpt = None
			inConfig = None
		else:
			inConfig.AddChild(sysdebugTechSupport)
			
		ccm = self.ConfigConfMo(dn = dn, inConfig = inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
		
		duration = timeoutSec
		poll_interval = 2
		crd = None
		if (ccm.errorCode == 0):
			#WriteUcsWarning('Waiting for the Tech Support file to become available (this may take several minutes).')
			status = False
			while (True):
				crd = self.ConfigResolveDn(dn, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
				if (crd.errorCode == 0):
					if (crd.OutConfig.GetChildCount() > 0):
						for techSupport in crd.OutConfig.GetChild():
							if (techSupport.OperState == SysdebugTechSupport.CONST_OPER_STATE_AVAILABLE):
								status = True
					else:
						raise UcsValidationException('Failed to create the TechSupport file.')
						#raise Exception('Failed to create the TechSupport file.')
					
				else:
					raise UcsException(crd.errorCode, crd.errorDescr)
					#raise Exception('[Error]: GetTechSupport [Code]:' + crd.errorCode + ' [Description]:' + crd.errorDescr)
				
				
				if(status):
					break
				
				time.sleep(min(duration, poll_interval))
				duration = max(0, (duration-poll_interval))
				
				if duration == 0:
					inConfig = ConfigConfig()
					sysdebugTechSupport = ManagedObject(NamingId.SYSDEBUG_TECH_SUPPORT)
					sysdebugTechSupport.DN = dn
					sysdebugTechSupport.Status = Status.DELETED
					inConfig.AddChild(sysdebugTechSupport)
					ccmi = self.ConfigConfMo(dn = dn, inConfig = inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
					if (ccmi.errorCode != 0):
						WriteUcsWarning('[Error]: GetTechSupport [Code]:' + ccmi.errorCode + ' [Description]:' + ccmi.errorDescr)
					raise UcsValidationException('TechSupport file generation timed out')
					#raise Exception('TechSupport file generation timed out')
			
			#WriteObject(crd.OutConfig.GetChild())
			for item in crd.OutConfig.GetChild():
				fileSource = "techsupport/" + item.Name
			
				try:
					UcsUtils.DownloadFile(self, fileSource, pathPattern)
				except Exception, err:
					WriteUcsWarning(str(err))
			
				if (removeFromUcs):
					inConfig = ConfigConfig()
					sysdebugTechSupport = ManagedObject(NamingId.SYSDEBUG_TECH_SUPPORT)
					sysdebugTechSupport.DN = item.Dn
					sysdebugTechSupport.Status = Status.DELETED
					inConfig.AddChild(sysdebugTechSupport)
					ccmi = self.ConfigConfMo(dn = item.Dn, inConfig = inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=dumpXml)
					if (ccmi.errorCode != 0):
						raise UcsException(ccmi.errorCode, ccmi.errorDescr)
						#raise Exception('[Error]: GetTechSupport [Code]:' + ccmi.errorCode + ' [Description]:' + ccmi.errorDescr)
		
		else:
			raise UcsException(ccm.errorCode, ccm.errorDescr)
			#raise Exception('[Error]: GetTechSupport [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)
		
		return crd.OutConfig.GetChild()

	def SyncManagedObject(self, difference, deleteNotPresent=False, noVersionFilter=False, dumpXml=None):
		"""
		Syncs Managed Object.
		
		Method takes the difference object (output of CompareManagedObject) and applies the differences on reference Managed Object.
		- difference specifies the Difference object (output of ComparesManagedObject) which has differences of the properties of two or more Managed Objects.
		- deleteNotPresent, if set as True, any missing MOs in reference Managed Object set will be deleted.
		- noVersionFilter, If set as True, minversion for Mos or properties to be added in reference Managed Object will not be checked.
		"""
		from UcsBase import WriteUcsWarning, WriteObject, UcsUtils, ManagedObject, AbstractFilter, GenericMO, SyncAction, UcsException, UcsValidationException
		from Ucs import ClassFactory, Pair, ConfigMap
		
		if ((difference == None) or (isinstance(difference, list) and (len(difference) == 0))):
			raise UcsValidationException("difference object parameter is not provided.")
			#raise Exception("[Error]: SyncManagedObject: Difference Object can not be Null")

		configMap = ConfigMap()

		configDoc = xml.dom.minidom.parse(UcsUtils.GetSyncMoConfigFilePath())
		
		moConfigMap = {}
		moConfigMap = UcsUtils.GetSyncMoConfig(configDoc)

		for moDiff in difference:
			mo = moDiff.InputObject
			classId = mo.classId
			gMoDiff = None
			metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
			if metaClassId == None:
				#TODO: Add Warning/Error messages in Logger.
				WriteUcsWarning("Ignoring [%s]. Unknown ClassId [%s]." %(moDiff.InputObject.getattr("Dn"), classId))
				continue
			
			moConfigs = []
			moConfig = None
			
			if UcsUtils.WordL(classId) in moConfigMap:
				moConfigs = moConfigMap[UcsUtils.WordL(classId)]
						
			if moConfigs:
				for conf in moConfigs:
					if (self._version.CompareTo(conf.getActionVersion()) == 0):
						moConfig=conf
			
			#Removes Difference Object.
			if ((moDiff.SideIndicator == UcsMoDiff.REMOVE) and (deleteNotPresent)):
				
				if (moConfig is not None and moConfig.getAction() == SyncAction.ignore and moConfig.getStatus() is not None and moConfig.getStatus().contains(Status.DELETED)):
					if (moConfig.getIgnoreReason() is None or len(moConfig.getIgnoreReason()) == 0):
						continue
				
					ir = moConfig.getIgnoreReason()
					try:
						for prop in ir:
							propValue = ir[prop]
							if mo.getattr(prop):
								attrValue = mo.getattr(prop)
							else:
								attrValue = None
							
							if (not propValue or not attrValue or propValue != attrValue):
								ignore = False
								break
					except Exception, err:
						ignore = False
					
					if ignore:
						continue
				
				gMoDiff = ManagedObject(classId)
				gMoDiff.setattr("Dn", mo.getattr("Dn"))
				gMoDiff.setattr("Status", Status().DELETED)
				gMoDiff = GenericMO(gMoDiff, WriteXmlOption.AllConfig)#gMoDiff should be generic object

			if moDiff.SideIndicator == UcsMoDiff.ADD_MODIFY:
				gMoDiff = ManagedObject(classId)
				addExists = False
				moMeta = UcsUtils.IsPropertyInMetaIgnoreCase(classId, "Meta")

				if((moMeta != None) and ('Add' in moMeta.verbs)):
					addExists = True

				#Add Difference Object.
				if ((addExists) and ((moDiff.DiffProperty == None) or (len(moDiff.DiffProperty) == 0))):
					if (moConfig is not None and moConfig.getAction() == SyncAction.ignore and moConfig.getStatus() is not None and moConfig.getStatus().contains(Status.CREATED)):
						if (moConfig.getIgnoreReason() is None or len(moConfig.getIgnoreReason()) == 0):
							continue
						ir = moConfig.getIgnoreReason()
						try:
							for prop in ir:
								propValue = ir[prop]
								if mo.getattr(prop):
									attrValue = mo.getattr(prop)
								else:
									attrValue = None
								
								if (not propValue or not attrValue or propValue != attrValue):
									ignore = False
									break
						except Exception, err:
							ignore = False
						
						if ignore:
							continue
				
					for prop in mo.__dict__.keys():
						propMoMeta = UcsUtils.IsPropertyInMetaIgnoreCase(classId, prop)
						if (propMoMeta != None):
							if (prop.lower() == "rn" or prop.lower() == "dn" or propMoMeta.access == UcsPropertyMeta.ReadOnly):
								continue
							exclude = False
							if (moConfig is not None  and moConfig.getExcludeList() is not None):
								for exProp in moConfig.getExcludeList():
									if prop.lower() == exProp.lower():
										exclude = True
							if not exclude:
								gMoDiff.setattr(propMoMeta.name, mo.getattr(prop))
					
					gMoDiff.setattr("Dn", mo.getattr("Dn"))

					if (moConfig is not None and moConfig.getAction() == SyncAction.statusChange):
						gMoDiff.setattr("Status", moConfig.getStatus())
					else:
						gMoDiff.setattr("Status", Status().CREATED)

					gMoDiff = GenericMO(gMoDiff, WriteXmlOption.AllConfig)#gMoDiff should be generic object
					if (not noVersionFilter):
						hReference = mo.GetHandle()
						if ((hReference != None) and (hReference._version != None)):
							gMoDiff.FilterVersion(hReference._version)

				#Modify the Managed Object
				else:
					
					if (moConfig is not None and moConfig.getAction() == SyncAction.ignore and moConfig.getStatus() is not None and moConfig.getStatus().contains(Status.DELETED)):
						if (moConfig.getIgnoreReason() is None or len(moConfig.getIgnoreReason()) == 0):
							continue
					
						ir = moConfig.getIgnoreReason()
						try:
							for prop in ir:
								propValue = ir[prop]
								if mo.getattr(prop):
									attrValue = mo.getattr(prop)
								else:
									attrValue = None
								
								if (not propValue or not attrValue or propValue != attrValue):
									ignore = False
									break
						except Exception, err:
							ignore = False
						
						if ignore:
							continue
					
					if ((moDiff.DiffProperty == None) or (len(moDiff.DiffProperty) == 0)):
						#TODO: Add Warning/Error messages in Logger.
						WriteUcsWarning('Add not supported for classId ' + classId +'. Reverting to modify.')
						continue

					finalDiffPropStr = None
					finalDiffProps = moDiff.DiffProperty
					gMoDiff = ManagedObject(classId)
					for diffprop in finalDiffProps:
						exclude = False
						if (moConfig is not None and moConfig.getExcludeList() is not None):
							for exProp in moConfig.getExcludeList():
								if diffprop.lower() == exProp.lower():
										exclude = True
						if not exclude:
							finalDiffPropStr = finalDiffPropStr + ","
								
					for prop in finalDiffProps:
						propMoMeta = UcsUtils.IsPropertyInMetaIgnoreCase(classId, prop)
						if (propMoMeta != None):
							if (prop.lower() == "rn" or prop.lower() == "dn" or propMoMeta.access == UcsPropertyMeta.ReadOnly):
								continue
							exclude = False
							if (moConfig is not None and moConfig.getExcludeList() is not None):
								for exProp in moConfig.getExcludeList():
									if diffprop.lower() == exProp.lower():
											exclude = True
							if not exclude:
								gMoDiff.setattr(propMoMeta.name, mo.getattr(prop))

					gMoDiff.setattr("Dn", mo.getattr("Dn"))
					gMoDiff.setattr("Status", Status().MODIFIED)
					
					gMoDiff = GenericMO(gMoDiff, WriteXmlOption.AllConfig)#gMoDiff should be generic object to apply FilterVersion on it.
					
			#TODO: NoversionFilter functionality discussion.
			if ((gMoDiff != None) and (not noVersionFilter)):
				gMoMeta = UcsUtils.GetUcsPropertyMeta(gMoDiff.classId, "Meta")
				if ((gMoMeta != None) and (self._version != None)):
					if self._version < gMoMeta.version:
						#TODO: Add Warning/Error messages in Logger.
						WriteUcsWarning('Ignoring unsupported classId %s for Dn %s.'  %(gMoDiff.classId, gMoDiff.getattr("Dn")))
						gMoDiff = None

					if ((gMoDiff != None) and (self._version != None)):
						gMoDiff.FilterVersion(self._version)
				
			if (gMoDiff != None):
				if gMoDiff.__dict__.has_key("_excludePropList"):
					for prop in gMoDiff.__dict__["_excludePropList"]:
						if prop == "XtraProperty":
							gMoDiff.__dict__[prop] = {}
							continue
						gMoDiff.__dict__[prop] = None

			if (gMoDiff != None):
				pair = Pair()
				pair.setattr("Key", gMoDiff.getattr("Dn"))
				pair.AddChild(gMoDiff)
				configMap.AddChild(pair)

		if configMap.GetChildCount() == 0:
			return None

		ccm = self.ConfigConfMos(configMap, False, dumpXml)
		if ccm.errorCode == 0:
			moList = []
			for child in ccm.OutConfigs.GetChild():
				if (isinstance(child, Pair) == True):
					for mo in child.GetChild():
						moList.append(mo)
				elif (isinstance(child, ManagedObject) == True):
					moList.append(child)
			#WriteObject(moList)
			return moList
		else:
			raise UcsException(ccm.errorCode, ccm.errorDescr)
			#raise Exception('[Error]: SyncManagedObject [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)

	def GetManagedObject(self, inMo=None, classId=None, params=None, inHierarchical=False, dumpXml=None):
		"""
		Gets Managed Object from UCS.
		
		- inMo, if provided, it acts as a parent for the present operation. It should be None unless a user wants to define a parent scope. 
		  It can be a single MO or a list containing multiple managed objects.
		- classId of the managed object/s to get.
		- params contains semicolon (;) separated list of key/value pairs(key=value), that are used as filters for selecting specific managed 
		  objects. The key should be a valid property of the managed object to be retrieved.
		- inHierarchical, Explores hierarchy if true, else returns managed objects at a single level.
		"""
		from Ucs import ClassFactory,Dn,DnSet,OrFilter,EqFilter,AndFilter,WcardFilter,FilterFilter
		from Mos import LsServer
		from UcsBase import WriteUcsWarning,WriteObject,UcsUtils,ManagedObject,AbstractFilter,UcsException,UcsValidationException

		if params != None:
			keys = params.keys()
		else:
			keys = []

		if (classId != None and classId != ""):
			#ClassId param set
			metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
			if (metaClassId == None):
				metaClassId = classId
				moMeta = UcsMoMeta(UcsUtils.WordU(classId), UcsUtils.WordL(classId), "", "", "InputOutput", ManagedObject.DUMMYDIRTY, [], [], [], [])
			else:
				moMeta = UcsUtils.GetUcsPropertyMeta(metaClassId, "Meta")

			if moMeta == None:
				raise UcsValidationException('[Error]: GetManagedObject: moMeta for classId [%s] is not valid' %(classId))
				#raise Exception('[Error]: GetManagedObject: moMeta for classId [%s] is not valid' %(classId))

			#process the filter argument and make filterfilter
			orFilter = OrFilter()

			if ((inMo != None) and (isinstance(inMo, list)) and (len(inMo) > 0)):
				for mo in inMo:
					andFilter = AndFilter()
					for key in keys:
						propMoMeta = UcsUtils.IsPropertyInMetaIgnoreCase(metaClassId,key)
						if (propMoMeta != None):
							attrName = propMoMeta.xmlAttribute
						else:
							attrName = key

						eqFilter = EqFilter()
						eqFilter.Class = UcsUtils.WordL(metaClassId)
						eqFilter.Property = attrName
						eqFilter.Value = str(params[key])
						andFilter.AddChild(eqFilter)

					lkupDn = mo.getattr("Dn")
					if (lkupDn == None):
						if (isinstance(mo, LsServer) == True):
							lkupDn = "root"
						continue
					wcardFilter = WcardFilter()
					wcardFilter.Class = UcsUtils.WordL(metaClassId)
					wcardFilter.Property = UcsUtils.WordL(NamingId.DN)
					wcardFilter.Value = "^" + re.escape(lkupDn) +"/[^/]+$"
					andFilter.AddChild(wcardFilter)

					if (andFilter.GetChildCount() > 1):
						orFilter.AddChild(UcsUtils.HandleFilterMaxComponentLimit(self, andFilter))
					elif (andFilter.GetChildCount() == 1):
						for filter in andFilter.GetChild():
							if (isinstance(filter, AbstractFilter) == True):
								orFilter.AddChild(filter)

			else:
				andFilter = AndFilter()
				for key in keys:
					propMoMeta = UcsUtils.IsPropertyInMetaIgnoreCase(metaClassId,key)
					if (propMoMeta != None):
						attrName = propMoMeta.xmlAttribute
					else:
						attrName = key

					eqFilter = EqFilter()
					eqFilter.Class = UcsUtils.WordL(metaClassId)
					eqFilter.Property = attrName
					eqFilter.Value = str(params[key])
					andFilter.AddChild(eqFilter)

				if (andFilter.GetChildCount() > 1):
					orFilter.AddChild(UcsUtils.HandleFilterMaxComponentLimit(self, andFilter))
				elif (andFilter.GetChildCount() == 1):
					for filter in andFilter.GetChild():
						if (isinstance(filter, AbstractFilter) == True):
							orFilter.AddChild(filter)

			inFilter = None
			if (orFilter.GetChildCount() > 1):
				inFilter = FilterFilter()
				inFilter.AddChild(UcsUtils.HandleFilterMaxComponentLimit(self, orFilter))
			elif  (orFilter.GetChildCount() == 1):
				inFilter = FilterFilter()
				for filter in orFilter.GetChild():
					if (isinstance(filter, AbstractFilter) == True):
						inFilter.AddChild(filter)

			crc = self.ConfigResolveClass(moMeta.xmlAttribute, inFilter, inHierarchical, dumpXml)
			if crc.errorCode == 0:
				moList = []
				currentMoList = crc.OutConfigs.GetChild()
				while (len(currentMoList) > 0):
					childMoList = []
					for mo in currentMoList:
						moList.append(mo)
						while (mo.GetChildCount() > 0):
							for child in mo.GetChild():
								mo.RemoveChild(child)
								if (child.__dict__.has_key('Dn')):
									if (child.Dn == None or child.Dn == ""):
										child.setattr("Dn", mo.Dn + '/' + child.Rn)
										child.MarkClean()
								else:
									child.setattr("Dn", mo.Dn + '/' + child.Rn)
									child.MarkClean()
								childMoList.append(child)
								break
					currentMoList = childMoList

				#WriteObject(moList)
				return moList
			else:
				raise UcsException(crc.errorCode, crc.errorDescr)
				#raise Exception('[Error]: GetManagedObject [Code]:' + crc.errorCode + ' [Description]:' + crc.errorDescr)
			#return None
		else:
			#Dn param set
			dnSet = DnSet()
			dn = Dn()
			for key in keys:
				if (key.lower() == "dn"):
					dn.setattr("Value", params[key])

			if (dn.getattr("Value") == None or dn.getattr("Value") == ""):
				raise UcsValidationException("classId or dn parameter is not provided.")
				#raise Exception('[Warning]: GetManagedObject: ClassId or DN is mandatory')

			dnSet.AddChild(dn)
			crDns = self.ConfigResolveDns(dnSet, inHierarchical, dumpXml)
			if (crDns.errorCode == 0):
				moList = []
				if (inHierarchical == True):
					currentMoList = crDns.OutConfigs.GetChild()
					while (len(currentMoList) > 0):
						childMoList = []
						for mo in currentMoList:
							moList.append(mo)
							while (mo.GetChildCount() > 0):
								for child in mo.GetChild():
									mo.RemoveChild(child)
									if (child.__dict__.has_key('Dn')):
										if (child.Dn == None or child.Dn == ""):
											child.setattr("Dn", mo.Dn + '/' + child.Rn)
											child.MarkClean()
									else:
										child.setattr("Dn", mo.Dn + '/' + child.Rn)
										child.MarkClean()
									childMoList.append(child)
									break
						currentMoList = childMoList
				else:
					moList = crDns.OutConfigs.GetChild()
				sortedMoList = sorted(moList, lambda x,y: cmp(x.Dn, y.Dn))
				#WriteObject(moList)
				return sortedMoList
			else:
				raise UcsException(crDns.errorCode, crDns.errorDescr)
				#raise Exception('[Error]: GetManagedObject [Code]:' + crDns.errorCode + ' [Description]:' + crDns.errorDescr)
	

	def AddManagedObject(self, inMo=None, classId=None, params=None, modifyPresent=False, dumpXml=None):
		"""
		Adds a Managed Object to UCS.
		
		- inMo, if provided, it acts as a parent for the present operation. It should be None unless a user wants to define a parent scope. 
		  It can be a single MO or a list containing multiple managed objects.
		- classId of the managed object/s to be added.
		- params contains semicolon (;) separated list of key/value pairs(key=value), that are used as filters for selecting specific managed 
		  objects. The key should be a valid property of the managed object to be added.
		- modifyPresent ensures that the add API modify the managed object, if it already exits, instead of returning an error.
		"""
		from UcsBase import UcsUtils,ManagedObject,WriteUcsWarning,WriteObject,UcsException,UcsValidationException
		from Ucs import ClassFactory,Pair,ConfigMap

		unknownMo = False
		if (classId == None or classId == ""):
			raise UcsValidationException("classId parameter is not provided.")
			#raise Exception('[Error]: AddManagedObject [Description]: classId is Null')
		
		metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
		if (metaClassId != None):
			classId = metaClassId
			moMeta = UcsUtils.GetUcsPropertyMeta(classId, "Meta")
		else:
			unknownMo = True

		configMap = ConfigMap()
		rn = None
		dn = None
		#moMeta = UcsUtils.GetUcsPropertyMeta(classId, "Meta")
		if params != None:
			keys = params.keys()
		else:
			keys = []

		if (not unknownMo):
			rn = moMeta.rn
			for prop in UcsUtils.GetUcsPropertyMetaAttributeList(classId):
				propMeta = UcsUtils.GetUcsPropertyMeta(classId, prop)
				if (propMeta.access != UcsPropertyMeta.Naming):
					continue
				namingPropFound = False
				for k in keys:
					if (k.lower() == prop.lower()):
						rn = re.sub('\[%s\]' % prop,'%s' % params[k], rn)
						namingPropFound = True
						break

				if (namingPropFound == False):
					#TODO: Add Warning/Error messages in Logger.
					WriteUcsWarning("[Warning]: AddManagedObject [Description]:Expected Naming Property %s for ClassId %s not found" %(prop, classId))
					rn = re.sub('\[%s\]' % prop,'%s' % "", rn)

		obj = ManagedObject(classId)

		for prop in keys:
			if (not unknownMo):
				propMoMeta = UcsUtils.IsPropertyInMetaIgnoreCase(classId, prop)
				if (propMoMeta != None):
					if (prop.lower() == "rn" or prop.lower() == "dn"):
						pass
					elif (propMoMeta.access == UcsPropertyMeta.ReadOnly):
						#TODO: Add Warning/Error messages in Logger.
						WriteUcsWarning("[Warning]: AddManagedObject [Description]:Attempt to add non-writeable property %s in Class %s" %(prop, classId))

					if (prop.lower() == "rn"):
						if ((inMo == None) or (not isinstance(inMo, list)) or (len(inMo) == 0)):
							#TODO: Add Warning/Error messages in Logger.
							WriteUcsWarning("[Warning]: AddManagedObject [Description]:Ignoring Rn since no parent provided")
						if (rn != params[prop]):
							#TODO: Add Warning/Error messages in Logger.
							WriteUcsWarning("[Warning]: AddManagedObject [Description]:Rn Mismatch. Provided %s Computed %s. Ignoring Computed Rn" %(params[prop], rn))
							rn = params[prop]#bug fix. if Rn and Name are both provided by user then Rn will get preference.

					if (prop.lower() == "dn"):
						dn = params[prop]

					obj.setattr(propMoMeta.name, str(params[prop]))
				else:
					#Known MO - Unknown Property
					obj.setattr(UcsUtils.WordL(prop), str(params[prop]))
			else:
				#Unknown MO
				if (prop.lower() == "dn"):
					dn = params[prop]

				if prop.lower() == "rn":
					rn = params[prop]
				if rn==None:
					rn=""

				obj.setattr(UcsUtils.WordL(prop), str(params[prop]))

		if modifyPresent in _AffirmativeList:
			obj.setattr("Status", '%s,%s' %(Status().CREATED,Status().MODIFIED))
		else:
			obj.setattr("Status", Status().CREATED)

		if (dn != None and dn != ""):
			obj.setattr("Dn", dn)
			pair = Pair()
			#pair.setattr("Key", obj.Dn)
			pair.setattr("Key", obj.getattr("Dn"))
			pair.AddChild(obj)
			configMap.AddChild(pair)
		elif ((inMo != None) and (isinstance(inMo, list)) and (len(inMo) > 0)):
			for mo in inMo:
				pdn = mo.getattr("Dn")
				if pdn != None:
					obj.setattr("Dn", pdn + '/' +rn)
					pair = Pair()
					#pair.setattr("Key", obj.Dn)
					pair.setattr("Key", obj.getattr("Dn"))
					pair.AddChild(obj.Clone())
					configMap.AddChild(pair)

		if configMap.GetChildCount() == 0:
			raise UcsValidationException('[Warning]: AddManagedObject [Description]: Nothing to Add')
			#raise Exception('[Warning]: AddManagedObject [Description]: Nothing to Add')

		ccm = self.ConfigConfMos(configMap, False, dumpXml)
		if ccm.errorCode == 0:
			moList = []
			for child in ccm.OutConfigs.GetChild():
				if (isinstance(child, Pair) == True):
					for mo in child.GetChild():
						moList.append(mo)
				elif (isinstance(child, ManagedObject) == True):
					moList.append(child)
			#WriteObject(moList)
			return moList
		else:
			raise UcsException(ccm.errorCode, ccm.errorDescr)
			#raise Exception('[Error]: AddManagedObject [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)
	
	def SetManagedObject(self, inMo, classId=None, params=None, dumpXml=None):
		"""
		Modifies Managed Object in UCS.
		
		- inMo, if provided, it acts as the target object for the present operation. It should be None unless a user wants to provide an 
		  inMo. It can be a single MO or a list containing multiple managed objects.
		- classId of the managed object/s to be modified.
		- params contains semicolon (;) separated list of key/value pairs(key=value), that are used as filters for selecting specific managed 
		  objects. The key should be a valid property of the managed object to be modified.
		"""
		from UcsBase import UcsUtils,ManagedObject,WriteUcsWarning,WriteObject,UcsException,UcsValidationException
		from Ucs import ClassFactory,Pair,ConfigMap
		
		if params != None:
			keys = params.keys()
		else:
			keys = []

		unknownMo = False
		dn = None
		obj = None
		configMap = None
		dnParamSet = False

		if (classId != None and classId != ""):
			metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
			if (metaClassId != None):
				classId = metaClassId
				moMeta = UcsUtils.GetUcsPropertyMeta(classId, "Meta")
			else:
				unknownMo = True

			for k in keys:
				if (k.lower() == "dn"):
					# ClassId And Dn Specified - No Parent Necessary
					dnParamSet = True
					dn = params[k]
					obj = ManagedObject(classId)
					for prop in keys:
						propMoMeta = UcsUtils.IsPropertyInMetaIgnoreCase(classId, prop)
						if (propMoMeta != None):
							if (prop.lower() == "rn" or prop.lower() == "dn"):
								pass
							elif (propMoMeta.access == UcsPropertyMeta.ReadOnly):
								#TODO: Add Warning/Error messages in Logger.
								WriteUcsWarning("[Warning]: SetManagedObject [Description] Attempt to set non-writable property %s in Class %s" %(prop, classId))

							obj.setattr(propMoMeta.name, str(params[prop]))
						else:
							#Sets the unknown property/value as XtraProperty in obj
							obj.setattr(UcsUtils.WordL(prop), str(params[prop]))

					obj.setattr("Dn", dn)
					obj.setattr("Status", Status().MODIFIED)
					pair = Pair()
					pair.setattr("Key", obj.getattr("Dn"))
					pair.AddChild(obj)
					configMap = ConfigMap()
					configMap.AddChild(pair)

		if (dnParamSet == False):
			# ClassId is None, inMo Necessary
			if ((inMo == None) or (not isinstance(inMo, list)) or (len(inMo) == 0)):
				if (classId == None or classId == ""):
					raise UcsValidationException('[Error]: SetManagedObject [Description]: inMo and ClassId are both not specified')
					#raise Exception('[Error]: SetManagedObject [Description]: inMo and ClassId are both not specified')
				else:
					raise UcsValidationException('[Error]: SetManagedObject [Description]: inMo and Dn are both not specified')
					#raise Exception('[Error]: SetManagedObject [Description]: inMo and Dn are both not specified')

			configMap = ConfigMap()
			for mo in inMo:
				obj = ManagedObject(mo.propMoMeta.name)
				dn = mo.getattr("Dn")

				if (classId == None or classId == ""):
					classId = mo.propMoMeta.name
				elif (classId.lower() != (mo.propMoMeta.name).lower()):#check that classId(just in case classId have value) and parentMo's classId is equal.
					#TODO: Add Warning/Error messages in Logger.
					WriteUcsWarning("[Warning]: SetManagedObject [Description] ClassId does not match with inMo's classId.")
					classId = mo.propMoMeta.name

				for prop in keys:
					propMoMeta = UcsUtils.IsPropertyInMetaIgnoreCase(classId, prop)
					if (propMoMeta != None):
						if (prop.lower() == "rn" or prop.lower() == "dn"):
							pass
						elif (propMoMeta.access == UcsPropertyMeta.ReadOnly):
							#TODO: Add Warning/Error messages in Logger.
							WriteUcsWarning("[Warning]: SetManagedObject [Description] Attempt to set non-writeable property %s in Class %s" %(prop, classId))

						obj.setattr(propMoMeta.name, str(params[prop]))
					else:
						#Sets the unknown property/value as XtraProperty in obj
						obj.setattr(UcsUtils.WordL(prop), str(params[prop]))

				obj.setattr("Dn", dn)
				obj.setattr("Status", Status().MODIFIED)
				pair = Pair()
				pair.setattr("Key", obj.getattr("Dn"))
				pair.AddChild(obj)
				configMap.AddChild(pair)

		if (configMap != None):
			ccm = self.ConfigConfMos(configMap, YesOrNo.FALSE, dumpXml)
			if ccm.errorCode == 0:
				moList = []
				for child in ccm.OutConfigs.GetChild():
					if (isinstance(child, Pair) == True):
						for mo in child.GetChild():
							moList.append(mo)
					elif (isinstance(child, ManagedObject) == True):
						moList.append(child)
				#WriteObject(moList)
				return moList
			else:
				raise UcsException(ccm.errorCode, ccm.errorDescr)
				#raise Exception('[Error]: SetManagedObject [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)
	

	def RemoveManagedObject(self, inMo=None, classId=None, params=None, dumpXml=None):
		"""
		Removes Managed Object in UCS.
		
		- inMo, if provided, it acts as the target object for the present operation. It should be None unless a user wants to provide an 
		  inMo. It can be a single MO or a list containing multiple managed objects.
		- classId of the managed object/s to be removed.
		- params contains semicolon (;) separated list of key/value pairs(key=value), that are used as filters for selecting specific managed 
		  objects. The key should be a valid property of the managed object to be modified.
		"""
		from UcsBase import UcsUtils,ManagedObject,WriteUcsWarning,WriteObject,UcsException,UcsValidationException
		from Ucs import ClassFactory,Pair,ConfigMap

		if params != None:
			keys = params.keys()
		else:
			keys = []

		configMap = ConfigMap()
		if ((inMo != None) and (isinstance(inMo, list)) and (len(inMo) > 0)):
			for mo in inMo:
				pair = Pair()
				pair.setattr("Key",mo.getattr("Dn"))
				obj = ManagedObject(mo.classId)
				obj.setattr("Status",Status().DELETED)
				pair.AddChild(obj)

				configMap.AddChild(pair)

		elif (classId != None):
			pair = Pair()
			metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
			if metaClassId != None:
				classId = metaClassId
			for prop in keys:
				if (prop.lower() == "dn"):
					pair.setattr("Key", params[prop])
			if (pair.getattr("Key") == None):
				raise UcsValidationException('[Error]: RemoveManagedObject [Description]: Dn missing in propertyMap')
				#raise Exception('[Error]: RemoveManagedObject [Description]: Dn missing in propertyMap')
			
			obj = ManagedObject(classId)
			obj.setattr("Status", Status().DELETED)
			pair.AddChild(obj)
			configMap.AddChild(pair)

		if configMap.GetChildCount() == 0:
			raise UcsValidationException('[Warning]: RemoveManagedObject [Description]: (inMO) or (ClassId and Dn) missing')
			#raise Exception('[Warning]: RemoveManagedObject [Description]: (inMO) or (ClassId and Dn) missing')

		ccm = self.ConfigConfMos(configMap, False, dumpXml)
		if ccm.errorCode == 0:
			moList = []
			for child in ccm.OutConfigs.GetChild():
				if (isinstance(child, Pair) == True):
					for mo in child.GetChild():
						moList.append(mo)
				elif (isinstance(child, ManagedObject) == True):
					moList.append(child)
			#WriteObject(moList)
			return moList
		else:
			raise UcsException(ccm.errorCode, ccm.errorDescr)
			#raise Exception('[Error]: RemoveManagedObject [Code]:' + ccm.errorCode + ' [Description]:' + ccm.errorDescr)
		

	def AaaChangeSelfPassword(self, inConfirmNewPassword, inNewPassword, inOldPassword, inUserName, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaChangeSelfPassword")

		method.Cookie = self._cookie
		method.InConfirmNewPassword = inConfirmNewPassword
		method.InNewPassword = inNewPassword
		method.InOldPassword = inOldPassword
		method.InUserName = inUserName

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaCheckComputeAuthToken(self, inToken, inUser, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaCheckComputeAuthToken")

		method.Cookie = self._cookie
		method.InToken = inToken
		method.InUser = inUser

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaCheckComputeExtAccess(self, inDn, inUser, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaCheckComputeExtAccess")

		method.Cookie = self._cookie
		method.InDn = inDn
		method.InUser = inUser

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaGetAuthTokenClient(self, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaGetAuthTokenClient")

		method.InCookie = self._cookie

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaGetKVMLaunchUrl(self, inIpv4, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaGetKVMLaunchUrl")

		method.InCookie = self._cookie
		method.InIpv4 = inIpv4

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaGetNComputeAuthTokenByDn(self, inDn, inNumberOf, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaGetNComputeAuthTokenByDn")

		method.Cookie = self._cookie
		method.InDn = inDn
		method.InNumberOf = str(inNumberOf)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaKeepAlive(self, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaKeepAlive")

		method.Cookie = self._cookie

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaLogin(self, inName, inPassword, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaLogin")

		method.InName = inName
		method.InPassword = inPassword

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaLogout(self, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaLogout")

		method.InCookie = self._cookie

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaRefresh(self, inName, inPassword, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaRefresh")

		method.InCookie = self._cookie
		method.InName = inName
		method.InPassword = inPassword

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaTokenLogin(self, inName, inToken, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaTokenLogin")

		method.Cookie = self._cookie
		method.InName = inName
		method.InToken = inToken

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def AaaTokenRefresh(self, inName, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("AaaTokenRefresh")

		method.InCookie = self._cookie
		method.InName = inName

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeBootPnuOs(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeBootPnuOs")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeConfigureCMCLIF(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeConfigureCMCLIF")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeCreateHVVnic(self, inBladeSlotId, inChassisId, inConfig, inSwId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeCreateHVVnic")

		method.Cookie = self._cookie
		method.InBladeSlotId = str(inBladeSlotId)
		method.InChassisId = str(inChassisId)
		method.InConfig = inConfig
		method.InSwId = inSwId

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeCreateSfish(self, inBladeSlotId, inChassisId, inConfig, inSwId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeCreateSfish")

		method.Cookie = self._cookie
		method.InBladeSlotId = str(inBladeSlotId)
		method.InChassisId = str(inChassisId)
		method.InConfig = inConfig
		method.InSwId = inSwId

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeCreateVMVnic(self, inBladeSlotId, inChassisId, inConfig, inSwId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeCreateVMVnic")

		method.Cookie = self._cookie
		method.InBladeSlotId = str(inBladeSlotId)
		method.InChassisId = str(inChassisId)
		method.InConfig = inConfig
		method.InSwId = inSwId

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeDeleteHVVnic(self, inVnicDn, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeDeleteHVVnic")

		method.Cookie = self._cookie
		method.InVnicDn = inVnicDn

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeDeleteSfish(self, inVmSwitchDn, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeDeleteSfish")

		method.Cookie = self._cookie
		method.InVmSwitchDn = inVmSwitchDn

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeDeleteVMVnic(self, inVnicDn, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeDeleteVMVnic")

		method.Cookie = self._cookie
		method.InVnicDn = inVnicDn

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeGetAdaptorConnectivity(self, inFruModel, inFruSerial, inFruVendor, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeGetAdaptorConnectivity")

		method.Cookie = self._cookie
		method.InFruModel = inFruModel
		method.InFruSerial = inFruSerial
		method.InFruVendor = inFruVendor

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeGetPnuOSInventory(self, inFruModel, inFruSerial, inFruVendor, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeGetPnuOSInventory")

		method.Cookie = self._cookie
		method.InFruModel = inFruModel
		method.InFruSerial = inFruSerial
		method.InFruVendor = inFruVendor

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeGetSwitchApeFru(self, inSwId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeGetSwitchApeFru")

		method.Cookie = self._cookie
		method.InSwId = inSwId

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeInjectStimuli(self, inFromSvc, inStimuli, inToSvc, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeInjectStimuli")

		method.Cookie = self._cookie
		method.InFromSvc = str(inFromSvc)
		method.InStimuli = inStimuli
		method.InToSvc = str(inToSvc)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeInsertNewChassis(self, inConfig, inIsRefresh, inSwId, inSwPortId, inSwSlotId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeInsertNewChassis")

		method.Cookie = self._cookie
		method.InConfig = inConfig
		method.InIsRefresh = str(inIsRefresh)
		method.InSwId = inSwId
		method.InSwPortId = str(inSwPortId)
		method.InSwSlotId = str(inSwSlotId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeInsertNewFex(self, inConfig, inIsRefresh, inSwId, inSwPortId, inSwSlotId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeInsertNewFex")

		method.Cookie = self._cookie
		method.InConfig = inConfig
		method.InIsRefresh = str(inIsRefresh)
		method.InSwId = inSwId
		method.InSwPortId = str(inSwPortId)
		method.InSwSlotId = str(inSwSlotId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeInsertNewRack(self, inConfig, inFxId, inFxPortId, inFxSlotId, inIsRefresh, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeInsertNewRack")

		method.Cookie = self._cookie
		method.InConfig = inConfig
		method.InFxId = str(inFxId)
		method.InFxPortId = str(inFxPortId)
		method.InFxSlotId = str(inFxSlotId)
		method.InIsRefresh = str(inIsRefresh)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeIssueChassisId(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeIssueChassisId")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeIssueFexId(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeIssueFexId")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeIssueRackId(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeIssueRackId")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeMcGet(self, inMcAddress, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeMcGet")

		method.Cookie = self._cookie
		method.InMcAddress = inMcAddress

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeMcGetBiosTokens(self, inChassisId, inSlotId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeMcGetBiosTokens")

		method.Cookie = self._cookie
		method.InChassisId = str(inChassisId)
		method.InSlotId = str(inSlotId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeMcGetParam(self, inMcAddress, inParam, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeMcGetParam")

		method.Cookie = self._cookie
		method.InMcAddress = inMcAddress
		method.InParam = str(inParam)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeMcGetSmbios(self, inChassisId, inSlotId, inUpdateCnt, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeMcGetSmbios")

		method.Cookie = self._cookie
		method.InChassisId = str(inChassisId)
		method.InSlotId = str(inSlotId)
		method.InUpdateCnt = inUpdateCnt

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeMcSet(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeMcSet")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeMuxOffline(self, inChId, inMuxSlotId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeMuxOffline")

		method.Cookie = self._cookie
		method.InChId = str(inChId)
		method.InMuxSlotId = str(inMuxSlotId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeSetAdaptorFirmwareVersion(self, inAdaptorFwVersion, inAdaptorSerial, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeSetAdaptorFirmwareVersion")

		method.Cookie = self._cookie
		method.InAdaptorFwVersion = inAdaptorFwVersion
		method.InAdaptorSerial = inAdaptorSerial

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeSetApeSensorReading(self, inChassisId, inFaultLevel, inOperation, inSensorName, inServerId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeSetApeSensorReading")

		method.Cookie = self._cookie
		method.InChassisId = str(inChassisId)
		method.InFaultLevel = str(inFaultLevel)
		method.InOperation = str(inOperation)
		method.InSensorName = str(inSensorName)
		method.InServerId = str(inServerId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeSetFlexFlashControllerFirmwareVersion(self, inIpAddr, inVersion, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeSetFlexFlashControllerFirmwareVersion")

		method.Cookie = self._cookie
		method.InIpAddr = str(inIpAddr)
		method.InVersion = inVersion

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeSetFlexFlashControllerState(self, inControllerState, inIpAddr, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeSetFlexFlashControllerState")

		method.Cookie = self._cookie
		method.InControllerState = str(inControllerState)
		method.InIpAddr = str(inIpAddr)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeSetFlexFlashVirtualRaidInformation(self, inConrtollerId, inIpAddr, inRaidHealth, inRaidState, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeSetFlexFlashVirtualRaidInformation")

		method.Cookie = self._cookie
		method.InConrtollerId = str(inConrtollerId)
		method.InIpAddr = str(inIpAddr)
		method.InRaidHealth = str(inRaidHealth)
		method.InRaidState = str(inRaidState)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeSetServerLifeCycle(self, inFruModel, inFruSerial, inFruVendor, inServerLc, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeSetServerLifeCycle")

		method.Cookie = self._cookie
		method.InFruModel = inFruModel
		method.InFruSerial = inFruSerial
		method.InFruVendor = inFruVendor
		method.InServerLc = inServerLc

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeSetSwitchInventory(self, inConfig, inSwId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeSetSwitchInventory")

		method.Cookie = self._cookie
		method.InConfig = inConfig
		method.InSwId = inSwId

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeUpdateApeFirmwareParamTable(self, inFieldName, inIpAddr, inVersion, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeUpdateApeFirmwareParamTable")

		method.Cookie = self._cookie
		method.InFieldName = str(inFieldName)
		method.InIpAddr = inIpAddr
		method.InVersion = inVersion

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeUpdateBIOSFirmwareVersion(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeUpdateBIOSFirmwareVersion")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ApeUpdateStorageCtlrFirmwareVersion(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ApeUpdateStorageCtlrFirmwareVersion")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ComputeGetInventory(self, inFaultsOnly, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ComputeGetInventory")

		method.Cookie = self._cookie
		method.InFaultsOnly = inFaultsOnly

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ComputeSubscribe(self, inCategory, inPolicyMapSchema, inProvider, inSchemaInfo, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ComputeSubscribe")

		method.Cookie = self._cookie
		method.InCategory = inCategory
		method.InPolicyMapSchema = inPolicyMapSchema
		method.InProvider = inProvider
		method.InSchemaInfo = inSchemaInfo

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigCheckCompatibility(self, dn, inBladePackVersion, inDetailResult, inInfraPackVersion, inRackPackVersion, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigCheckCompatibility")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InBladePackVersion = inBladePackVersion
		method.InDetailResult = inDetailResult
		method.InInfraPackVersion = inInfraPackVersion
		method.InRackPackVersion = inRackPackVersion

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigCheckConformance(self, dn, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigCheckConformance")

		method.Cookie = self._cookie
		method.Dn = dn

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigCheckFirmwareUpdatable(self, inUpdatableDns, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigCheckFirmwareUpdatable")

		method.Cookie = self._cookie
		method.InUpdatableDns = inUpdatableDns

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigConfFiltered(self, classId, inConfig, inFilter, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigConfFiltered")

		metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
		if (metaClassId != None):
			classId = UcsUtils.WordL(metaClassId)
		else:
			classId = UcsUtils.WordL(classId)
		method.ClassId = classId
		method.Cookie = self._cookie
		method.InConfig = inConfig
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigConfMo(self, dn, inConfig, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigConfMo")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InConfig = inConfig
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigConfMoGroup(self, inConfig, inDns, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigConfMoGroup")

		method.Cookie = self._cookie
		method.InConfig = inConfig
		method.InDns = inDns
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigConfMos(self, inConfigs, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigConfMos")

		method.Cookie = self._cookie
		method.InConfigs = inConfigs
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigConfRename(self, dn, inNewName, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigConfRename")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InNewName = inNewName

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigEstimateImpact(self, inConfigs, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigEstimateImpact")

		method.Cookie = self._cookie
		method.InConfigs = inConfigs

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigFindDependencies(self, dn, inReturnConfigs, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigFindDependencies")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InReturnConfigs = inReturnConfigs

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigFindDnsByClassId(self, classId, inFilter, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigFindDnsByClassId")

		metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
		if (metaClassId != None):
			classId = UcsUtils.WordL(metaClassId)
		else:
			classId = UcsUtils.WordL(classId)
		method.ClassId = classId
		method.Cookie = self._cookie
		method.InFilter = inFilter

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigFindHostPackDependencies(self, dn, inHostPackDns, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigFindHostPackDependencies")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHostPackDns = inHostPackDns

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigFindPermitted(self, dn, inClassId, inFilter, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigFindPermitted")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InClassId = inClassId
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigGetEstimateImpact(self, inConfigs, inImpactAnalyzerId, inSourceConnectorId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigGetEstimateImpact")

		method.Cookie = self._cookie
		method.InConfigs = inConfigs
		method.InImpactAnalyzerId = inImpactAnalyzerId
		method.InSourceConnectorId = str(inSourceConnectorId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigGetRemotePolicies(self, inContext, inPolicyDigests, inStimulusId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigGetRemotePolicies")

		method.Cookie = self._cookie
		method.InContext = inContext
		method.InPolicyDigests = inPolicyDigests
		method.InStimulusId = str(inStimulusId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigGetXmlFile(self, inFilePath, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigGetXmlFile")

		method.Cookie = self._cookie
		method.InFilePath = inFilePath

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigGetXmlFileStr(self, inFilePath, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigGetXmlFileStr")

		method.Cookie = self._cookie
		method.InFilePath = inFilePath

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigInstallAllImpact(self, dn, inBladePackVersion, inHostPackDns, inInfraPackVersion, inRackPackVersion, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigInstallAllImpact")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InBladePackVersion = inBladePackVersion
		method.InHostPackDns = inHostPackDns
		method.InInfraPackVersion = inInfraPackVersion
		method.InRackPackVersion = inRackPackVersion

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigMoChangeEvent(self, inConfig, inEid, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigMoChangeEvent")

		method.Cookie = self._cookie
		method.InConfig = inConfig
		method.InEid = str(inEid)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigRefreshIdentity(self, dn, inIdType, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigRefreshIdentity")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InIdType = inIdType

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigReleaseResolveContext(self, inContext, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigReleaseResolveContext")

		method.Cookie = self._cookie
		method.InContext = str(inContext)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigRenewResolveContext(self, inContext, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigRenewResolveContext")

		method.Cookie = self._cookie
		method.InContext = str(inContext)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveChildren(self, classId, inDn, inFilter, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveChildren")

		metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
		if (metaClassId != None):
			classId = UcsUtils.WordL(metaClassId)
		else:
			classId = UcsUtils.WordL(classId)
		method.ClassId = classId
		method.Cookie = self._cookie
		method.InDn = inDn
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveChildrenSorted(self, classId, inDn, inFilter, inSize, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveChildrenSorted")

		metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
		if (metaClassId != None):
			classId = UcsUtils.WordL(metaClassId)
		else:
			classId = UcsUtils.WordL(classId)
		method.ClassId = classId
		method.Cookie = self._cookie
		method.InDn = inDn
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InSize = str(inSize)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveClass(self, classId, inFilter, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveClass")

		metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
		if (metaClassId != None):
			classId = UcsUtils.WordL(metaClassId)
		else:
			classId = UcsUtils.WordL(classId)
		method.ClassId = classId
		method.Cookie = self._cookie
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveClassSorted(self, classId, inFilter, inSize, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveClassSorted")

		metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(classId)
		if (metaClassId != None):
			classId = UcsUtils.WordL(metaClassId)
		else:
			classId = UcsUtils.WordL(classId)
		method.ClassId = classId
		method.Cookie = self._cookie
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InSize = str(inSize)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveClasses(self, inIds, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveClasses")

		method.Cookie = self._cookie
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InIds = inIds

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveClassesSorted(self, inIds, inSize, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveClassesSorted")

		method.Cookie = self._cookie
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InIds = inIds
		method.InSize = str(inSize)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveContext(self, inContext, inSize, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveContext")

		method.Cookie = self._cookie
		method.InContext = str(inContext)
		method.InSize = str(inSize)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveDn(self, dn, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveDn")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveDns(self, inDns, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveDns")

		method.Cookie = self._cookie
		method.InDns = inDns
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigResolveParent(self, dn, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigResolveParent")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def ConfigScope(self, dn, inClass, inFilter, inRecursive, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("ConfigScope")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InClass = inClass
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InRecursive = inRecursive

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def EventRegisterEventChannel(self, inDn, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("EventRegisterEventChannel")

		method.Cookie = self._cookie
		method.InDn = inDn

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def EventRegisterEventChannelResp(self, inCtx, inDn, inReqID, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("EventRegisterEventChannelResp")

		method.Cookie = self._cookie
		method.InCtx = inCtx
		method.InDn = inDn
		method.InReqID = str(inReqID)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def EventSendEvent(self, inDn, inEvent, inReqId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("EventSendEvent")

		method.Cookie = self._cookie
		method.InDn = inDn
		method.InEvent = inEvent
		method.InReqId = str(inReqId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def EventSendHeartbeat(self, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("EventSendHeartbeat")

		method.Cookie = self._cookie

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def EventSubscribe(self, inFilter, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("EventSubscribe")

		method.Cookie = self._cookie
		method.InFilter = inFilter

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def EventUnRegisterEventChannel(self, inDn, inReqID, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("EventUnRegisterEventChannel")

		method.Cookie = self._cookie
		method.InDn = inDn
		method.InReqID = str(inReqID)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def EventUnsubscribe(self, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("EventUnsubscribe")

		method.Cookie = self._cookie

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def FaultAckFault(self, inId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("FaultAckFault")

		method.Cookie = self._cookie
		method.InId = str(inId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def FaultAckFaults(self, inIds, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("FaultAckFaults")

		method.Cookie = self._cookie
		method.InIds = inIds

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def FaultResolveFault(self, inId, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("FaultResolveFault")

		method.Cookie = self._cookie
		method.InId = str(inId)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def FsmDebugAction(self, dn, inDirective, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("FsmDebugAction")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InDirective = inDirective

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def LoggingSyncOcns(self, inFromOrZero, inToOrZero, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("LoggingSyncOcns")

		method.Cookie = self._cookie
		method.InFromOrZero = str(inFromOrZero)
		method.InToOrZero = str(inToOrZero)

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def LsClone(self, dn, inServerName, inTargetOrg, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("LsClone")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InServerName = inServerName
		method.InTargetOrg = inTargetOrg

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def LsInstantiateNNamedTemplate(self, dn, inErrorOnExisting, inNameSet, inTargetOrg, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("LsInstantiateNNamedTemplate")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InErrorOnExisting = inErrorOnExisting
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InNameSet = inNameSet
		method.InTargetOrg = inTargetOrg

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def LsInstantiateNTemplate(self, dn, inNumberOf, inServerNamePrefixOrEmpty, inTargetOrg, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("LsInstantiateNTemplate")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InNumberOf = str(inNumberOf)
		method.InServerNamePrefixOrEmpty = inServerNamePrefixOrEmpty
		method.InTargetOrg = inTargetOrg

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def LsInstantiateTemplate(self, dn, inErrorOnExisting, inServerName, inTargetOrg, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("LsInstantiateTemplate")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InErrorOnExisting = inErrorOnExisting
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InServerName = inServerName
		method.InTargetOrg = inTargetOrg

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def LsResolveTemplates(self, dn, inExcludeIfBound, inFilter, inType, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("LsResolveTemplates")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InExcludeIfBound = inExcludeIfBound
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InType = inType

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def LsTemplatise(self, dn, inTargetOrg, inTemplateName, inTemplateType, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("LsTemplatise")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InTargetOrg = inTargetOrg
		method.InTemplateName = inTemplateName
		method.InTemplateType = inTemplateType

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def MethodVessel(self, inStimuli, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("MethodVessel")

		method.Cookie = self._cookie
		method.InStimuli = inStimuli

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def MgmtResolveBackupFilenames(self, inBackupSource, inType, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("MgmtResolveBackupFilenames")

		method.Cookie = self._cookie
		method.InBackupSource = inBackupSource
		method.InType = inType

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def OrgResolveElements(self, dn, inClass, inFilter, inSingleLevel, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("OrgResolveElements")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InClass = inClass
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InSingleLevel = inSingleLevel

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def OrgResolveLogicalParents(self, dn, inSingleLevel, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("OrgResolveLogicalParents")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InSingleLevel = inSingleLevel

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def PolicyResolveNames(self, inClientConnectorDn, inContext, inFilter, inPolicyType, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("PolicyResolveNames")

		method.Cookie = self._cookie
		method.InClientConnectorDn = inClientConnectorDn
		method.InContext = inContext
		method.InFilter = inFilter
		method.InPolicyType = inPolicyType

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def PolicySetCentraleStorage(self, inData, inOper, inSide, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("PolicySetCentraleStorage")

		method.Cookie = self._cookie
		method.InData = inData
		method.InOper = str(inOper)
		method.InSide = inSide

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def PoolResolveInScope(self, dn, inClass, inFilter, inSingleLevel, inHierarchical=YesOrNo.FALSE, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("PoolResolveInScope")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InClass = inClass
		method.InFilter = inFilter
		method.InHierarchical = (("false", "true")[inHierarchical in _AffirmativeList])
		method.InSingleLevel = inSingleLevel

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def StatsClearInterval(self, inDns, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("StatsClearInterval")

		method.Cookie = self._cookie
		method.InDns = inDns

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def StatsResolveThresholdPolicy(self, dn, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("StatsResolveThresholdPolicy")

		method.Cookie = self._cookie
		method.Dn = dn

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def StatsSubscribe(self, inCategory, inProvider, inSchemaInfo, inTimeInterval, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("StatsSubscribe")

		method.Cookie = self._cookie
		method.InCategory = inCategory
		method.InProvider = inProvider
		method.InSchemaInfo = inSchemaInfo
		method.InTimeInterval = inTimeInterval

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def SwatExample(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("SwatExample")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def SwatGetstats(self, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("SwatGetstats")

		method.Cookie = self._cookie

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def SwatInject(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("SwatInject")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def SyntheticFSObjInventory(self, dn, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("SyntheticFSObjInventory")

		method.Cookie = self._cookie
		method.Dn = dn
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def SyntheticFSObjInventoryB(self, inConfig, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("SyntheticFSObjInventoryB")

		method.Cookie = self._cookie
		method.InConfig = inConfig

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def SyntheticTestTx(self, inConfig, inTest, inWhat, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("SyntheticTestTx")

		method.Cookie = self._cookie
		method.InConfig = inConfig
		method.InTest = inTest
		method.InWhat = inWhat

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None

	def TrigPerformTokenAction(self, inContext, inOwnership, inSchedName, inTokenAction, inTokenId, inTriggerableDn, inWindowName, inWindowType, dumpXml=None):
		from UcsBase import ExternalMethod,UcsUtils,WriteUcsWarning
		method = ExternalMethod("TrigPerformTokenAction")

		method.Cookie = self._cookie
		method.InContext = inContext
		method.InOwnership = inOwnership
		method.InSchedName = inSchedName
		method.InTokenAction = inTokenAction
		method.InTokenId = str(inTokenId)
		method.InTriggerableDn = inTriggerableDn
		method.InWindowName = inWindowName
		method.InWindowType = inWindowType

		response = self.XmlQuery(method, WriteXmlOption.Dirty, dumpXml)

		if (response != None):
			return response
		return None


class UcsVersion:
	"""	This class handles the operations related to the UcsVersions. It provides functionality to compare Ucs version objects. """
	def __init__(self, version):
		if (version == None):
			return None

		matchObj = re.match("""^(?P<major>[1-9][0-9]{0,2})\.(?P<minor>(([0-9])|([1-9][0-9]{0,1})))\((?P<mr>(([0-9])|([1-9][0-9]{0,2})))\.(?P<patch>(([0-9])|([1-9][0-9]{0,4})))\)$""",version,0)
		if matchObj:
			self.major = matchObj.group("major")
			self.minor = matchObj.group("minor")
			self.mr = matchObj.group("mr")
			self.patch = matchObj.group("patch")
			return

		matchObj = re.match("""^(?P<major>[1-9][0-9]{0,2})\.(?P<minor>(([0-9])|([1-9][0-9]{0,1})))\((?P<mr>(([0-9])|([1-9][0-9]{0,2})))(?P<patch>[a-z])\)$""", version, 0)
		if matchObj:
			self.major = matchObj.group("major")
			self.minor = matchObj.group("minor")
			self.mr = matchObj.group("mr")
			self.patch = matchObj.group("patch")
			return

		matchObj = re.match("""^(?P<major>[1-9][0-9]{0,2})\.(?P<minor>(([0-9])|([1-9][0-9]{0,1})))\((?P<mr>(([0-9])|([1-9][0-9]{0,2})))\)$""",version,0)
		if matchObj:
			self.major = matchObj.group("major")
			self.minor = matchObj.group("minor")
			self.mr = matchObj.group("mr")
			return

	def CompareTo(self, version):
		if (version == None or not isinstance(version,UcsVersion)):
			return 1

		if (self.major != version.major):
			return ord(self.major) - ord(version.major)
		if (self.minor != version.minor):
			return ord(self.minor) - ord(version.major)
		if (self.mr != version.mr):
			return ord(self.mr) - ord(version.mr)
		return ord(self.patch) - ord(version.patch)

	def __gt__(self,version):
		return (self.CompareTo(version) > 0)

	def __lt__(self,version):
		return (self.CompareTo(version) < 0)

	def __ge__(self,version):
		return (self.CompareTo(version) >= 0)

	def __le__(self,version):
		return (self.CompareTo(version) <= 0)
	

class UcsPropertyRestriction:
	""" This class handles the restriction information of the properties of managed object. """
	def __init__(self, minLength=None, maxLength=None, pattern=None, valueSet=None, rangeVal=None):
		self.minLength = minLength
		self.maxLength = maxLength
		self.pattern = pattern
		self.rangeVal = rangeVal
		self.valueSet = valueSet
		self.rangeRoc = None
		self.valueSetRoc = None

class UcsPropertyMeta:
	"""	This class handles the meta information of the properties of managed Object. """
	Naming = 0
	CreateOnly = 1
	ReadOnly = 2
	ReadWrite = 3
	Internal = 4

	def __init__(self,name, xmlAttribute, fieldType, version, access, mask, minLength, maxLength, pattern, valueSet, rangeVal):
		self.name = name
		self.xmlAttribute = xmlAttribute
		self.fieldType = fieldType
		self.version = version
		self.access = access
		self.mask = mask
		self.restriction = UcsPropertyRestriction(minLength, maxLength, pattern, valueSet, rangeVal)

	def ValidatePropertyValue(self,inputVal):
		if (inputVal == None):
			return False

		if ((self.restriction.minLength != None) and (len(inputVal) < self.restriction.minLength)):
			return False

		if ((self.restriction.maxLength != None) and (len(inputVal) > self.restriction.maxLength)):
			return False

		if ((self.restriction.rangeVal != None) and (len(self.restriction.rangeVal) > 0)):
			for s in self.restriction.rangeVal:
				match = re.match("""^(?P<min>[0-9]{1,})\-(?P<max>[0-9]{1,})$""", s, 0)
				if match:
					min = match.group("min")
					max = match.group("max")
				else:
					continue

				if ((min <= inputVal) and (max >= inputVal)):
					return True

		if ((self.restriction.valueSet != None) and (len(self.restriction.valueSet) > 0)):
			for s in self.restriction.valueSet:
				if (s == inputVal):
					return True

		if (self.restriction.pattern != None):
			#match = re.match('"""' + self.restriction.pattern + '"""', inputVal, 0)
			match = re.match(re.escape('"""' + self.restriction.pattern + '"""'), inputVal, 0)
			if match:
				return True

		if (((self.restriction.rangeVal) != None and (len(self.restriction.rangeVal) > 0)) or ((self.restriction.valueSet != None) and (len(self.restriction.valueSet) > 0)) or (self.restriction.pattern != None)):
			return True

class UcsMoMeta:
	"""	This class handles the meta information of the managed Object. """
	ACCESS_TYPE_IO = "InputOutput"
	ACCESS_TYPE_OUTPUTONLY = "OutputOnly"

	def __init__(self, name, xmlAttribute, rn, version, io, mask, fieldNames, childFieldNames, verbs, access):
		self.name = name
		self.xmlAttribute = xmlAttribute
		self.rn = rn
		self.version = version
		self.io = io
		self.mask = mask
		self.fieldNames = fieldNames
		self.childFieldNames = childFieldNames
		self.verbs = verbs
		self.access = access

class WriteXmlOption:
	All = 0
	AllConfig = 1
	Dirty = 2

class UcsFactoryMeta:
	""" This class handles the meta information of the properties of external method Object. """
	def __init__(self, name, xmlAttribute, fieldType, version, io, isComplexType):
		self.name = name
		self.xmlAttribute = xmlAttribute
		self.fieldType = fieldType
		self.version = version
		self.io = io
		self.isComplexType = isComplexType

class UcsFactoryMethodMeta:
	""" This class handles the meta information of the meta property of external method Object. """
	def __init__(self, name, xmlAttribute, version):
		self.name = name
		self.xmlAttribute = xmlAttribute
		self.version = version

class CompareStatus:
	""" Internal class to support CompareUcsManagedObject functionality. """
	TypesDifferent = 0
	PropsDifferent = 1
	Equal = 2

class UcsMoDiff:
	"""
	This class structures an object which will be creatd by CompareManagedObject and contains all the information about the difference object which
	will be used by the SyncManagedObject method.
	"""
	REMOVE = "<="
	ADD_MODIFY = "=>"
	EQUAL = "=="

	def __init__(self, inputObject, sideIndicator, diffProperty=None, refValues=None, diffValues=None):
		self.InputObject = inputObject
		self.Dn = inputObject.Dn
		self.SideIndicator = sideIndicator
		self.DiffProperty = diffProperty
		#if(refValues != None):
		self.refPropValues = refValues
		#if(diffValues != None):
		self.diffPropValues = diffValues

class UcsMoChangeEvent:
	"""
	This class provides strcuture to save an event generated for any change, its associated managed object and property change list. This functionality is used 
	during AddEventHandler.
	"""
	def __init__(self, eventId=None, mo=None, changeList=[]):
		self.eventId = eventId
		self.mo = mo
		self.changeList = changeList

class WatchBlock:
	"""
	This class handles the functionality about the Event Handling/Watch block. Enqueue/Dequeue fuctionality of events is handled by this class. This functionality is 
	used during AddEventHandler.
	"""
	def __init__(self, params, fmce, capacity, cb):
		self.fmce = fmce
		self.cb = cb
		self.capacity = capacity
		self.params = params
		self.overflow = False
		self.errorCode = 0#TODO: when set errorCode condition should call notify according to PowerTool

		self.changeEvents = Queue()#infinite size Queue
		self.are = Condition()

	def Dequeue(self, millisecondsTimeout):
		while True:
			#self.are.acquire()
			if self.changeEvents.empty():
				#startTime =	datetime.datetime.now()#measure time at this point
				#self.are.wait(millisecondsTimeout)#codition will either timeout or receive signal
				#ts = datetime.datetime.now() - startTime
				#if (ts.seconds>=millisecondsTimeout):#TimeOut
				#	self.are.release()
				#	return None
				#if self.are.wait(millisecondsTimeout):
					#self.are.release()
				return None

			if self.errorCode != 0:
				#self.are.release()
				return None

			self.are.acquire()
			if not self.changeEvents.empty():
				moCE = self.changeEvents.get()
				self.are.release()
				return moCE

	def Enqueue(self, cmce):
		self.are.acquire()

		if self.changeEvents.maxsize < self.capacity:
			self.changeEvents.put(cmce)
		else:
			self.overflow = True

		self.are.notify()
		self.are.release()

	def _dequeue_default_cb(self, mce):
		tabsize = 8
		print "\n"
		print 'EventId'.ljust(tabsize*2) + ':' + str(mce.eventId)
		print 'ChangeList'.ljust(tabsize*2) + ':' + str(mce.changeList)
		print 'ClassId'.ljust(tabsize*2) + ':' + str(mce.mo.classId)
		#print mce.eventId
		#print mce.changeList
		#print mce.mo.classId


def CompareManagedObject(referenceObject, differenceObject, excludeDifferent=YesOrNo.FALSE, includeEqual=YesOrNo.FALSE, noVersionFilter=YesOrNo.FALSE, includeOperational=YesOrNo.FALSE, xlateOrg=None, xlateMap=None):
	"""
	Compares managed objects.
	
	- referenceObject specifies objects used as a reference for comparison.
	- differenceObject specifies objects that are compared to the reference objects.
	- excludeDifferent, if set as True then displays only the properties of compared objects that are equal.
	- includeEqual, set as True to display properties of compared objects that are equal. By default, only properties that differ between the 
	  reference and difference objects are displayed.
	- noVersionFilter, set as True to ignore minimum version in properties.
	- includeOperational, set as True to include operational properties.
	- xlateOrg specifies the translation org to be used.
	- xlateMap specifies translation map with DNs of entities that needs to be translated.
	"""
	from UcsBase import UcsUtils, WriteUcsWarning, GenericMO
	from Mos import OrgOrg
	referenceDict = {}
	differenceDict = {}

	if ((referenceObject != None) and (isinstance(referenceObject,list)) and (len(referenceObject) > 0)):
		for mo in referenceObject:
			if mo == None:
				continue

			moMeta = UcsUtils.IsPropertyInMetaIgnoreCase(mo.propMoMeta.name, "Meta")
			if (moMeta != None):
				if (moMeta.io == UcsMoMeta.ACCESS_TYPE_OUTPUTONLY):
					#WriteUcsWarning('[Warning]: Ignoring [%s]. Non-configurable class [%s]' %(mo.Dn, mo.propMoMeta.name))
					continue
				if ((moMeta.io == UcsMoMeta.ACCESS_TYPE_IO) and (len(moMeta.access) == 1 ) and (moMeta.access[0] == "read-only") ):
					#WriteUcsWarning('[Warning]: Ignoring read-only MO  [%s]. Class [%s]' %(mo.Dn, mo.propMoMeta.name))
					continue

			referenceDict[mo.Dn] = mo

	if ((differenceObject != None) and (isinstance(differenceObject, list)) and (len(differenceObject) > 0)):
		for mo in differenceObject:
			if mo == None:
				continue

			moMeta = UcsUtils.IsPropertyInMetaIgnoreCase(mo.propMoMeta.name, "Meta")
			if (moMeta != None):
				if (moMeta.io == UcsMoMeta.ACCESS_TYPE_OUTPUTONLY):
					#WriteUcsWarning('[Warning]: Ignoring [%s]. Non-configurable class [%s]' %(mo.Dn, mo.propMoMeta.name))
					continue
				if ((moMeta.io == UcsMoMeta.ACCESS_TYPE_IO) and (len(moMeta.access) == 1 ) and (moMeta.access[0] == "read-only") ):
					#WriteUcsWarning('[Warning]: Ignoring read-only MO  [%s]. Class [%s]' %(mo.Dn, mo.propMoMeta.name))
					continue

			translatedMo = TranslateManagedObject(mo, xlateOrg, xlateMap)
			differenceDict[translatedMo.Dn] = translatedMo

	dnList = []
	for key in referenceDict.keys():
		dnList.append(key)
	for key in differenceDict.keys():
		if key not in referenceDict.keys():
			dnList.append(key)
	dnList = sorted(dnList)
	diffOutput = []

	for dn in dnList:
		if dn not in differenceDict.keys():
			if excludeDifferent not in _AffirmativeList:
				moDiff = UcsMoDiff(referenceDict[dn], UcsMoDiff.REMOVE)
				diffOutput.append(moDiff)
		elif dn not in referenceDict.keys():
			if excludeDifferent not in _AffirmativeList:
				moDiff = UcsMoDiff(differenceDict[dn], UcsMoDiff.ADD_MODIFY)
				diffOutput.append(moDiff)
		else:
			diffProps = []
			option = WriteXmlOption.AllConfig
			if includeOperational in _AffirmativeList:
				option = WriteXmlOption.All
			gmoReference = GenericMO(referenceDict[dn], option)
			gmoDifference = GenericMO(differenceDict[dn], option)
			if (not noVersionFilter):
				handle = gmoReference.GetHandle()
				if ((handle != None) and (handle._version != None)):
					gmoReference.FilterVersion(handle._version)

				handle = gmoDifference.GetHandle()
				if ((handle != None) and (handle._version != None)):
					gmoDifference.FilterVersion(handle._version)

			diffStatus = Compare(gmoReference, gmoDifference, diffProps)
			if ((diffStatus == CompareStatus.Equal) and (includeEqual in _AffirmativeList)):
				moDiff = UcsMoDiff(referenceDict[dn], UcsMoDiff.EQUAL)
				diffOutput.append(moDiff)
			elif ((diffStatus == CompareStatus.TypesDifferent) and (excludeDifferent not in _AffirmativeList)):
				moDiff = UcsMoDiff(referenceDict[dn], UcsMoDiff.REMOVE)
				diffOutput.append(moDiff)
				moDiff = UcsMoDiff(referenceDict[dn], UcsMoDiff.ADD_MODIFY)
				diffOutput.append(moDiff)
			elif ((diffStatus == CompareStatus.PropsDifferent) and (excludeDifferent not in _AffirmativeList)):
				refValues = {}
				diffValues = {}
				for prop in diffProps:
					refValues[prop] = gmoReference.getattr(prop)
					diffValues[prop] = gmoDifference.getattr(prop)
				moDiff = UcsMoDiff(differenceDict[dn], UcsMoDiff.ADD_MODIFY, diffProps, refValues, diffValues)
				diffOutput.append(moDiff)

	return diffOutput

def Compare(fromMo, toMo, diff):
	""" Internal method to support CompareManagedObject functionality. """
	from UcsBase import UcsUtils
	if (fromMo.classId != toMo.classId):
		return CompareStatus.TypesDifferent

	for prop in UcsUtils.GetUcsPropertyMetaAttributeList(str(fromMo.classId)):
		propMeta = UcsUtils.IsPropertyInMetaIgnoreCase(fromMo.classId, prop)
		if propMeta != None:
			if ((propMeta.access == UcsPropertyMeta.Internal) or (propMeta.access == UcsPropertyMeta.ReadOnly) or (prop in toMo._excludePropList)):
				continue
			if ((toMo.__dict__.has_key(prop)) and (fromMo.getattr(prop) != toMo.getattr(prop))):
				diff.append(prop)

	if (len(diff) > 0):
		return CompareStatus.PropsDifferent

	return CompareStatus.Equal

def TranslateManagedObject(mObj, xlateOrg, xlateMap):
	""" Method used to translate a managedobject. This method is used in CompareManagedObject. """
	from UcsBase import UcsUtils, WriteUcsWarning
	from Mos import OrgOrg

	xMO = mObj.Clone()
	xMO.SetHandle(mObj.GetHandle())
	if (xlateOrg != None):
		matchObj = re.match(r'^(org-[\-\.:_a-zA-Z0-9]{1,16}/)*org-[\-\.:_a-zA-Z0-9]{1,16}', xMO.Dn)
		if matchObj:
			if UcsUtils.WordL(xMO.classId) == OrgOrg.ClassId():
				orgMoMeta = UcsUtils.GetUcsPropertyMeta(UcsUtils.WordU(OrgOrg.ClassId()), "Meta")
				if orgMoMeta == None:
					#TODO: Add Warning/Error messages in Logger.
					WriteUcsWarning('[Warning]: Could not translate [%s]' %(xMO.Dn))
					return xMO

				#Check for naming property
				matchObj1 = re.findall(r'(\[[^\]]+\])', orgMoMeta.rn)
				if matchObj1:
					UpdateMoDnAlongWithNamingProperties(xMO, orgMoMeta, xlateOrg)
				else:
					newDn = re.sub("%s"%(matchObj.group(0)), "%s"%(xlateOrg), xMO.Dn)
					#print "Translating", xMO.Dn, " => ", newDn
					xMO.Dn = newDn
			else:
				newDn = re.sub("^%s/"%(matchObj.group(0)), "%s/"%(xlateOrg), xMO.Dn)
				#print "Translating", xMO.Dn, " => ", newDn
				xMO.Dn = newDn

	if (xlateMap != None):
		originalDn = xMO.Dn
		if originalDn in xlateMap.keys():
			xMoMeta = UcsUtils.GetUcsPropertyMeta(UcsUtils.WordU(xMO.classId), "Meta")
			if xMoMeta == None:
				#TODO: Add Warning/Error messages in Logger.
				WriteUcsWarning('[Warning]: Could not translate [%s]' %(originalDn))
				return xMO

			#Check for naming property
			matchObj = re.findall(r'(\[[^\]]+\])', xMoMeta.rn)
			if matchObj:
				UpdateMoDnAlongWithNamingProperties(xMO, xMoMeta, xlateMap[originalDn])
			else:
				#print "Translating", xMO.Dn, " => ", xlateMap[originalDn]
				xMO.Dn = xlateMap[originalDn]
		else:
			originalDn = re.sub(r'[/]*[^/]+$', '', originalDn)
			while (originalDn != None or originalDn == ""):
				if (not(originalDn in xlateMap.keys())):
					originalDn = re.sub(r'[/]*[^/]+$', '', originalDn)
					continue

				newDn = re.sub("^%s/"%(originalDn), "%s/"%(xlateMap[originalDn]), xMO.Dn)
				#print "Translating", xMO.Dn, " => ", newDn
				xMO.Dn = newDn
				break

	return xMO

def UpdateMoDnAlongWithNamingProperties(mo, orgMoMeta, newDn):
	mo.Dn = newDn
	newRn = re.sub(r'^.*/', '', newDn)
	modmetaRn = re.sub(r'\[([^\]]+)\]', r'(?P<\1>.*?)', orgMoMeta.rn)
	matchObj = re.match(r'\|', modmetaRn)
	if matchObj:
		modmetaRn = re.sub(r'\|', r'\|', modmetaRn)

	pattern = "^" + modmetaRn + "$"
	matchObj = re.match(pattern, newRn)
	namePropDict = matchObj.groupdict()
	for groupName in namePropDict.keys():
		UpdateNamedPropertyField(mo, groupName, namePropDict[groupName])

def UpdateNamedPropertyField(mo, fieldName, fieldValue):
	from UcsBase import UcsUtils, WriteUcsWarning
	propertyMeta = UcsUtils.IsPropertyInMetaIgnoreCase(mo.classId, fieldName)
	if ((propertyMeta != None) and (propertyMeta.access == UcsPropertyMeta.Naming)):
		#WriteUcsWarning('Translating [%s] from [%s] => [%s]' %(fieldName, mo.getattr(fieldName), fieldValue))
		mo.setattr(fieldName, fieldValue)

def ExportUcsSession(filePath, key, merge=YesOrNo.FALSE):
	"""
	Stores the credential of currently logged in UCS in current session to a file. Password will be stored in encrypted format using key.
	
	- filePath specifies the path of the credential file.
	- key specifies any string used for secure encryption.
	- merge should be set as False unless user wants to append the existing credential file with new credential.
	"""
	from UcsBase import UcsUtils, WriteUcsWarning,UcsValidationException
	#from p3 import p3_encrypt, p3_decrypt
	
	if filePath is None:
		raise UcsValidationException("filePath parameter is not provided.")
		#raise Exception('[Error]: Please provide filePath')
	
	if key is None:
		raise UcsValidationException("key parameter is not provided.")
		#raise Exception('[Error]: Please provide key')		
	
	doc = xml.dom.minidom.Document()
	nodeList = None
	
	if merge in _AffirmativeList and os.path.isfile(filePath):#isfile() checks for file. exists() return true for directory as well
		doc =  xml.dom.minidom.parse(filePath)
		#nodeList = doc.documentElement._get_childNodes()
		nodeList = doc.documentElement.childNodes
	else:
		doc.appendChild(doc.createElement(UcsLoginXml.UCS_HANDLES))

	
	hUcsArray = defaultUcs.values()
	
	if hUcsArray != None:
		for hUcs in hUcsArray:
			updated = False
			if nodeList != None:
				for childNode in nodeList:
					if (childNode.nodeType != Node.ELEMENT_NODE):
						continue
					
					elem = childNode
					if ((not elem.hasAttribute(UcsLoginXml.NAME)) or (not elem.hasAttribute(UcsLoginXml.USER_NAME))):
						continue
					if ((elem.getAttribute(UcsLoginXml.NAME) != hUcs._name) or (elem.getAttribute(UcsLoginXml.USER_NAME) != hUcs._username)):
						continue

					if hUcs._noSsl:
						elem.setAttribute(UcsLoginXml.NO_SSL, hUcs._noSsl)
					elif elem.hasAttribute(UcsLoginXml.NO_SSL):
						elem.removeAttribute(UcsLoginXml.NO_SSL)

					if ((hUcs._noSsl and (hUcs._port != 80)) or ((not hUcs._noSsl) and (hUcs._port != 443))):
						elem.setAttribute(UcsLoginXml.PORT, hUcs._port)
					elif elem.hasAttribute(UcsLoginXml.PORT):
						elem.removeAttribute(UcsLoginXml.PORT)

					#elem.setAttribute(UcsLoginXml.PASSWORD, p3_encrypt(hUcs._password,key))
					elem.setAttribute(UcsLoginXml.PASSWORD, UcsUtils.EncryptPassword(hUcs._password,key))
					
					updated = True
					break
				
			if updated:
				continue
			
			node = doc.createElement(UcsLoginXml.UCS)
			attr = doc.createAttribute(UcsLoginXml.NAME)
			attr.value = hUcs._name
			node.setAttributeNode(attr)
			attr = doc.createAttribute(UcsLoginXml.USER_NAME)
			attr.value = hUcs._username
			node.setAttributeNode(attr)
			
			if hUcs._noSsl:
				attr = doc.createAttribute(UcsLoginXml.NO_SSL)
				attr.value = hUcs._noSsl
				node.setAttributeNode(attr)
				
			if ((hUcs._noSsl and (hUcs._port != 80)) or ((not hUcs._noSsl) and (hUcs._port != 443))):
				attr = doc.createAttribute(UcsLoginXml.PORT)
				attr.value = hUcs._port
				node.setAttributeNode(attr)		
				
			attr = doc.createAttribute(UcsLoginXml.PASSWORD)
			#attr.value = p3_encrypt(hUcs._password,key)
			attr.value = UcsUtils.EncryptPassword(hUcs._password,key)
			node.setAttributeNode(attr)
			
			doc.documentElement.insertBefore(node, doc.documentElement.lastChild)
	
	
	xmlNew = doc.toprettyxml(indent=" ")
	xmlNew = re.sub(r"^.*?xml version.*\n","",xmlNew)
	xmlNew = re.sub(r"\n[\s]*\n","\n",xmlNew)
	xmlNew = re.sub(r"^(.*)",r"\1",xmlNew, re.MULTILINE)
		
	f = open(filePath, 'w')
	f.write(xmlNew)
	f.close()

	

def ImportUcsSession(filePath, key):
	"""
	This operation will do a login to each UCS which is present in credential file.
	
	- filePath specifies the path of the credential file.
	- key specifies string used for secure encryption while ExportUcsSession operation.
	"""
	from UcsBase import UcsUtils, WriteUcsWarning, UcsValidationException
	#from p3 import p3_encrypt, p3_decrypt
	
	if filePath is None:
		raise UcsValidationException("filePath parameter is not provided.")
		#raise Exception('[Error]: Please provide filePath')

	if key is None:
		raise UcsValidationException("key parameter is not provided.")
		#raise Exception('[Error]: Please provide key')
		
	if not os.path.isfile(filePath) or not os.path.exists(filePath):
		raise UcsValidationException('[Error]: File <%s> does not exist ' %(filePath))
		#raise Exception('[Error]: File <%s> does not exist ' %(filePath))
	
	doc = xml.dom.minidom.parse(filePath)
	topNode = doc.documentElement
	#print topNode.localName
	
	if topNode is None or topNode.localName != UcsLoginXml.UCS_HANDLES:
		return None
	
	if(topNode.hasChildNodes()):
		#childList = topNode._get_childNodes()
		#childCount = childList._get_length()
		childList = topNode.childNodes
		childCount = len(childList)
		for i in range(childCount):
			childNode = childList.item(i)
			if (childNode.nodeType != Node.ELEMENT_NODE):
				continue
			
			if childNode.localName != UcsLoginXml.UCS:
				continue
			
			lName = None
			lUsername = None
			lPassword = None
			lNoSsl = False
			lPort = None
			
			if childNode.hasAttribute(UcsLoginXml.NAME):
				lName = childNode.getAttribute(UcsLoginXml.NAME)
				
			if childNode.hasAttribute(UcsLoginXml.USER_NAME):
				lUsername = childNode.getAttribute(UcsLoginXml.USER_NAME)
			
			if childNode.hasAttribute(UcsLoginXml.PASSWORD):
				#lPassword = p3_decrypt(childNode.getAttribute(UcsLoginXml.PASSWORD), key)
				lPassword = UcsUtils.DecryptPassword(childNode.getAttribute(UcsLoginXml.PASSWORD), key)
							
			if childNode.hasAttribute(UcsLoginXml.NO_SSL):
				lNoSsl = childNode.getAttribute(UcsLoginXml.NO_SSL)
			
			if childNode.hasAttribute(UcsLoginXml.PORT):
				lPort = childNode.getAttribute(UcsLoginXml.PORT)
			
			# Process Login
			if ((lName is None) or (lUsername == None) or (lPassword == None)):
				#WriteUcsWarning("[Warning] Insufficient information for login ...")
				continue
			try:
				
				handle = UcsHandle()
				handle.Login(name=lName, username=lUsername, password=lPassword, noSsl=lNoSsl, port=lPort)
				
				
			except Exception, err:
				#TODO: Add Warning/Error messages in Logger.
				WriteUcsWarning("[Connection Error<%s>] %s" %(lName,str(err)))
				#print "Exception:", str(err)

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
	""" Class to handle connection to UCS via redirection. """
	def http_error_301(self, req, fp, code, msg, headers):  
		#result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)			  
		respStatus = [code, headers.dict["location"]]							
		return respStatus

	def http_error_302(self, req, fp, code, msg, headers):  
		#result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)			  
		respStatus = [code, headers.dict["location"]]
		#print respStatus								
		return respStatus 


class UcsLoginXml:
	""" Internal class to support Export and Import UCS Session. """
	UCS_HANDLES = "ucshandles"
	UCS = "ucs"
	NAME = "name"
	USER_NAME = "username"
	NO_SSL = "nossl"
	PORT = "port"
	PASSWORD = "password"

class Progress(object):
	def __init__(self):
		self._seen = 0.0

	def update(self, total, size, name):
		from sys import stdout
		self._seen += size
		#pct = (self._seen / total) * 100.0
		#print '%s progress: %.2f' % (name, pct)
		status = r"%10d  [%3.2f%%]" % (self._seen, self._seen * 100 / total)
		status = status + chr(8)*(len(status)+1)
		stdout.write("\r%s" % status)
		stdout.flush()

class file_with_callback(file):
	def __init__(self, path, mode, callback, *args):
		file.__init__(self, path, mode)
		#self.seek(0, os.SEEK_END)
		self.seek(0, 2)
		self._total = self.tell()
		self.seek(0)
		self._callback = callback
		self._args = args

	def __len__(self):
		return self._total

	def read(self, size):
		data = file.read(self, size)
		self._callback(self._total, len(data), *self._args)
		return data
