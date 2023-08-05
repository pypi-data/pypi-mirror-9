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

import os, sys, platform, time, glob
import re
import xml.dom
import xml.dom.minidom
from os.path import dirname
from Constants import *
from UcsHandle import _AffirmativeList
from UcsBase import *

# variable declaration
displayXml=False
outFileFlag=False
outFilePath=None
outFile=None
andCount = 0
orCount = 0
notCount = 0
multiLineMethod = ["<configConfMo","<lsInstantiateNNamedTemplate","<statsClearInterval","<lsClone","<lsTemplatise","<lsInstantiateTemplate","<lsInstantiateNTemplate"]
singleLineMethod = ["</configConfMo","</lsInstantiateNNamedTemplate","</statsClearInterval","</lsClone","</lsTemplatise","</lsInstantiateTemplate","</lsInstantiateNTemplate","/>"]

# class declaration
class ClassStatus:
	none = 0
	created = 1
	modified = 2
	removed = 4
	deleted = 8


### Function Definition

#-------------------------------------- START - OF - GENERIC - FUCNTION -----------------------------------
## Get the ClassID for a given DN
#====================================================
def GetClassIdForDn(dn):
	
	rns = dn.split('/')
	rnCount = len(rns)

	classId = None
	parentClassId =None

	
	for rn in rns:
		classId = GetClassIdForRn(rn, parentClassId)
		if classId == None:
			break
		parentClassId = classId
		
	return classId
#====================== End Of Function <GetClassIdForDn>  ================

### Get the ClassID for a given RN
#====================================================
def GetClassIdForRn(rn, prevClassId=None):
	
	if not prevClassId:
		prevClassId = "TopRoot"
	
	metaClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(prevClassId)
	if (metaClassId == None):
		raise UcsValidationException('[Error]: GetManagedObject: classId [%s] is not valid' %(prevClassId))
		#WriteUcsWarning('[Error]: GetManagedObject: classId [%s] is not valid' %(prevClassId))
		#return None
	
	moMeta = UcsUtils.GetUcsPropertyMeta(metaClassId, "Meta")
	if moMeta == None:
		raise UcsValidationException('[Error]: GetManagedObject: moMeta for classId [%s] is not valid' %(prevClassId))
		#WriteUcsWarning('[Error]: GetManagedObject: moMeta for classId [%s] is not valid' %(prevClassId))
		#return
	
	
	for childClassId in moMeta.childFieldNames:
		
		# 1. If Rn does not contain [, then there is no naming property. Check directly.
		# 2. If Rn contains [, 
		# 2.1) Check if the Rn contains a "-" and ChildClassId.Rn does not, then proceed to next childClassId.
		#		substitute \[[^\]]*\] with .* and do a regex match
		# 2.2) If Rn does not contain a "-", then probably the childClassId has only the naming property 
		#		  without any suffix or perfix. Check for "[*]". Need to see, if there is a possibility of 
		#		  more than one [*] directly under a ClassId 
		
		#childClassId = "orgorg"
		childClassId = UcsUtils.FindClassIdInMoMetaIgnoreCase(childClassId)
		childMoMeta = UcsUtils.GetUcsPropertyMeta(childClassId, "Meta")
		if childMoMeta == None:
			continue
		
		# 2. Check if there is a naming property
		match = re.search(r"(\[[^\]]+\])",childMoMeta.rn)
		if not match:
			if childMoMeta.rn == rn:
				return childMoMeta.name
			continue
		
		
		# 2.1 Check if it has a prefix or suffix
		match = re.search(r"(([^\]]\[)|(\][^\[]))",childMoMeta.rn)
		if match:
			modmetaRn = re.sub(r"\[([^\]]+)\]",r"(?P<\1>.*?)",childMoMeta.rn)
			if re.match(r"\|",modmetaRn):
				modmetaRn = re.sub(r"\|",r"\|",modmetaRn)
				
			pattern = "^" + modmetaRn + "$"
			
			if re.match(pattern,rn):
				return childMoMeta.name
			
		else:
			continue
		
	
	
	for childClassId in moMeta.childFieldNames:
		
		childMoMeta = UcsUtils.GetUcsPropertyMeta(childClassId, "Meta")
		if childMoMeta == None:
			continue
		
		match = re.match("^(\[[^\]]+\])+$",childMoMeta.rn)
		if match:
			return childMoMeta.name
		
	
	return None
#====================== End Of Function <GetClassIdForRn>  ================

### Modify the Property Name
#====================================================
def GetPropName(prop):
	newProp = re.sub('_+','_',re.sub('^_','',re.sub('[/\-: +]','_',re.sub('([a-z0-9])([A-Z])','\g<1>_\g<2>',prop)))).upper()
	return newProp
#====================== End Of Function <GetPropName>  ================

### makes first letter of string capital
#====================================================
def FirstCapital(string):
	string = string[:1].upper() + string[1:]
	return string
#====================== End Of Function <FirstCapital>  ================

### check if node is root node
#================================================
def IsRootNode(dom,tagName):
	rootNodeTagName = dom.documentElement.tagName
	if rootNodeTagName == tagName:
		return True
	else:
		return False
#===================== End Of Function <IsRootNode>  ===================

### get pairnodes in a list
#================================================
def GetPairNodes(rootNode):
	methodElement = rootNode
	inConfigsElementList = methodElement.getElementsByTagName("inConfigs")
	inConfigsElement = inConfigsElementList[0]
	pairElementsList = inConfigsElement.getElementsByTagName("pair")
	return pairElementsList
#====================== End Of Function <GetPairNodes> =================


### use if parent only has single childnode
#================================================
def GetOnlyElementChildNode(node):
	childList = [childNode for childNode in node.childNodes if childNode.nodeType == childNode.ELEMENT_NODE ]
	return childList[0]
#====================== End Of Function <GetOnlyElementChildNode> =============


### use if parent has more than one child
#================================================
def GetElementChildNodes(node):
	childList = [childNode for childNode in node.childNodes if childNode.nodeType == childNode.ELEMENT_NODE ]
	return childList
#====================== End Of Function <GetElementChildNodes> ===============


### used to dump xml on screen
#================================================
def DumpXmlOnScreen(doc):
	global outFilePath, outFileFlag
	xmlNew = doc.toprettyxml(indent=" ")
	xmlNew = re.sub(r"^.*?xml version.*\n","",xmlNew)
	xmlNew = re.sub(r"\n[\s]*\n","\n",xmlNew)
	xmlNew = re.sub(r"^(.*)",r"#\1",xmlNew,flags=re.MULTILINE)
	if outFileFlag:
		outFile = open(outFilePath, 'a')
		print >>outFile, "\n##### Start-Of-XML #####\n%s\n##### End-Of-XML #####" %(xmlNew)
		outFile.close()
	else:
		print "\n##### Start-Of-XML #####\n" + xmlNew + "\n##### End-Of-XML #####\n"
#===================== End Of Function <DumpXmlOnScreen> ================

### create a string of dictionary propertyMap
#================================================
def CreatePythonPropertyMap(propertyMap):
	s = "{"
	for key,value in propertyMap.iteritems():
		s = s + key + ":" + value + ", "

	if s != "{":
		s = s[:-2]  # removes last 2 char
	return (s + "}")
#============================= End Of Function <CreatePythonPropertyMap> ===================

### Returns True if any of the list value present in line
#================================================
def CheckIfAnyListValueInString (listx,line):
	flag = False
	for value in listx:
		if value in line:
			flag = True
			break
	return flag
#============================= End Of Function <CheckIfAnyListValueInString> ===================
#-------------------------------------- END - OF - GENERIC - FUCNTION -----------------------------------


#-------------------------------- START - OF - METHOD SPECIFIC - FUNCTION -------------------------------- 
### Used in function GenerateConfigConfCmdlets
#================================================
def GetConfigConfCmdlet(node,isPairNode):
	propertyMap = {}
	cmdlet = ""
	includeDnInPropMap = False
	
	if node is None:
		return None
	
	classNode = None
	key = ""
	
	if (isPairNode):
		key = node.getAttribute(NamingPropertyId.KEY)
		classNode = GetOnlyElementChildNode(node)
		
		if classNode is None:
			return None
			
	else:
		key = node.getAttribute(NamingPropertyId.DN)
		classNode = node
	
	className = classNode.localName
	cmdletMeta = None
	dn = ""
	
	if classNode.hasAttribute(NamingPropertyId.DN):
		dn = classNode.getAttribute(NamingPropertyId.DN)
	
	moTag = ""
	if classNode.hasChildNodes() and len(GetElementChildNodes(classNode)) > 0 :
		moTag = "mo" 

	cmdlet = FormPythonCmdlet(classNode, key, moTag)
	
	if classNode.hasChildNodes() and len(GetElementChildNodes(classNode)) > 0 :
		callCount = 1
		cmdlet = "handle.StartTransaction()" + "\n" + cmdlet

		for childNode in GetElementChildNodes(classNode):
			subCmdlet = GetConfigConfSubCmdlet(childNode, dn, moTag, callCount)
			callCount += 1
			
			if subCmdlet is not None:
				cmdlet += "\n" + subCmdlet
			else:
				callCount -= 1
			
		cmdlet += "\n" + "handle.CompleteTransaction()"
		
	return cmdlet
#================================= End Of Function <GetConfigConfCmdlet> ==============================

### Used in function GenerateConfigConfCmdlets
#=========================================================================================================
def GetConfigConfSubCmdlet(classNode, parentDn, parentMoTag, parentCallCount, useGenericVersion = False):
	cmdlet = ""
	className = classNode.localName
	cmdletMeta = None
	dn =""
	useParentMo = False ##if the parent mo should be used at this level
	propertyMap = {}

	if classNode.hasAttribute(NamingPropertyId.DN):
		dn = classNode.getAttribute(NamingPropertyId.DN)
	elif classNode.hasAttribute(NamingPropertyId.RN):
		dn = dn = parentDn + "/" + classNode.getAttribute(NamingPropertyId.RN)
	
	count = 1
	tag = parentMoTag + "_" + str(parentCallCount)
	cmdlet = FormPythonSubCmdlet(classNode, dn, tag, parentMoTag)
	
	
	## Recursively cater to subnodes
	for childNode in GetElementChildNodes(classNode):
		subCmdlet = GetConfigConfSubCmdlet(childNode, dn, tag, count)
		count += 1
		if subCmdlet is not None:
			cmdlet += "\n" + subCmdlet
		else:
			count -= 1
	
	return cmdlet
#====================================== End Of Function <GetConfigConfSubCmdlet> =========================================


### Used in function GenerateConfigConfCmdlets
#=====================================================================
def FormPythonCmdlet(classNode, key, tag):
	cmdlet = ""
	classStatus = ClassStatus.none
	propertyMap = {}
	
	if (classNode.hasAttribute(NamingPropertyId.STATUS) and classNode.getAttribute(NamingPropertyId.STATUS) is not None):
		cs = []
		cs = classNode.getAttribute(NamingPropertyId.STATUS).split(',')
		cs = [ x.strip() for x in cs ]
		
		if Status.CREATED in cs: classStatus |= ClassStatus.created
		if Status.MODIFIED in cs: classStatus |= ClassStatus.modified
		if Status.DELETED in cs: classStatus |= ClassStatus.deleted
		if Status.REMOVED in cs: classStatus |= ClassStatus.removed
	else:
		classStatus = ClassStatus.created | ClassStatus.modified

	# support to handle unknown MOs	
	if UcsUtils.FindClassIdInMoMetaIgnoreCase(classNode.localName) == None:
		gmoFlag = True
	else:
		gmoFlag = False
	
	parentDn = dirname(key)
		
	if not gmoFlag:
		peerClassId = FirstCapital(classNode.localName) 
		peerClassIdStr = peerClassId + ".ClassId()"
		dnStr = '.DN'
	else:
		peerClassId = ""
		peerClassIdStr = '"'+(classNode.localName)+'"'
		dnStr = '"dn"'
		
	if GetClassIdForDn(parentDn) == None:
		parentClassId = ""
		parentClassIdStr = "None"
		parentDnStr = '"dn"'
	else:
		parentClassId = GetClassIdForDn(parentDn)
		parentClassIdStr = parentClassId + ".ClassId()"
		parentDnStr = '.DN'
		
		
	## create property map for attributes
	for attr, val in classNode.attributes.items():
		name = attr
		value = '"' + val + '"'
		
		if ( name != NamingPropertyId.DN and name != NamingPropertyId.RN and name != NamingPropertyId.STATUS ):
			
			if name.lower() == "Filter".lower():
				paramNameToUse = "FilterValue"
			else:
				paramNameToUse = name
			
			if paramNameToUse is not None:
				if not gmoFlag and UcsUtils.GetUcsPropertyMeta(peerClassId, FirstCapital(paramNameToUse)) is not None:
					paramNameToUse = peerClassId + '.' + GetPropName(paramNameToUse)
				else:
					paramNameToUse = '"'+ paramNameToUse + '"'
			
			propertyMap[paramNameToUse] = value
					
			

	tagElement = ""
	if tag:
		tagElement = tag + " = "
		
	
	## make cmdlet
	if (classStatus & ClassStatus.deleted == ClassStatus.deleted) or (classStatus & ClassStatus.removed == ClassStatus.removed):
		cmdlet = "obj = handle.GetManagedObject(None, %s, {%s%s:\"%s\"})\n%shandle.RemoveManagedObject(obj)" %(peerClassIdStr, peerClassId, dnStr, key, tagElement) #06Dec
		
	elif (classStatus & ClassStatus.created == ClassStatus.created):
		if not gmoFlag:
			propertyMap[FirstCapital(classNode.localName) + '.DN'] = '"' + key +'"'
		else:
			propertyMap['"dn"'] = '"' + key +'"'
			
		
		#parentDn = dirname(key)
		if (classStatus & ClassStatus.modified == ClassStatus.modified):
			cmdlet = "obj = handle.GetManagedObject(None, %s, {%s%s:\"%s\"})\n%shandle.AddManagedObject(obj, %s, %s, True)" %(parentClassIdStr, parentClassId, parentDnStr, parentDn, tagElement, peerClassIdStr, CreatePythonPropertyMap(propertyMap))  #06Dec
		else:
			cmdlet = "obj = handle.GetManagedObject(None, %s, {%s%s:\"%s\"})\n%shandle.AddManagedObject(obj, %s, %s)" %(parentClassIdStr, parentClassId, parentDnStr, parentDn, tagElement, peerClassIdStr, CreatePythonPropertyMap(propertyMap)) #06Dec
			
	elif (classStatus & ClassStatus.modified == ClassStatus.modified):
		cmdlet = "obj = handle.GetManagedObject(None, %s, {%s%s:\"%s\"})\n%shandle.SetManagedObject(obj, %s, %s)" %(peerClassIdStr, peerClassId, dnStr, key, tagElement, peerClassIdStr, CreatePythonPropertyMap(propertyMap)) #06Dec
		
	else:
		print "Throw Exception XML request status (%s) is invalid." %(classNode.getAttribute(NamingPropertyId.STATUS))
	
	return cmdlet
#======================================= End Of Function <FormPythonCmdlet> ====================================


### Used in function GenerateConfigConfCmdlets
#=====================================================================
def FormPythonSubCmdlet(classNode, key, moTag, parentMoTag):
	cmdlet = ""
	classStatus = ClassStatus.none
	propertyMap = {}
	
	if (classNode.hasAttribute(NamingPropertyId.STATUS) and classNode.getAttribute(NamingPropertyId.STATUS) is not None):
		cs = []
		cs = classNode.getAttribute(NamingPropertyId.STATUS).split(',')
		cs = [ x.strip() for x in cs ]
		
		if Status.CREATED in cs: classStatus |= ClassStatus.created
		if Status.MODIFIED in cs: classStatus |= ClassStatus.modified
		if Status.DELETED in cs: classStatus |= ClassStatus.deleted
		if Status.REMOVED in cs: classStatus |= ClassStatus.removed
	else:
		classStatus = ClassStatus.created | ClassStatus.modified

	# support for unknown MO #06Dec
	if UcsUtils.FindClassIdInMoMetaIgnoreCase(classNode.localName) == None:
		gmoFlag = True
	else:
		gmoFlag = False
		
		
	if not gmoFlag:
		peerClassId = FirstCapital(classNode.localName) 
		peerClassIdStr = peerClassId + ".ClassId()"
		dnStr = '.DN'
	else:
		peerClassId = ""
		peerClassIdStr = '"'+(classNode.localName)+'"'
		dnStr = '"dn"'
		


	## create property map for attributes
	for attr, val in classNode.attributes.items():
		name = attr
		value = '"' + val + '"'
		
		if ( name != NamingPropertyId.DN and name != NamingPropertyId.RN and name != NamingPropertyId.STATUS ):
			if name.lower() == "Filter".lower():
				paramNameToUse = "FilterValue"
			else:
				paramNameToUse = name
			
			if paramNameToUse is not None:
				if not gmoFlag and UcsUtils.GetUcsPropertyMeta(peerClassId, FirstCapital(paramNameToUse)) is not None:
					paramNameToUse = peerClassId + '.' + GetPropName(paramNameToUse)
				else:
					paramNameToUse = '"'+ paramNameToUse + '"'
			
			propertyMap[paramNameToUse] = value
			

	## make cmdlet
	if (classStatus & ClassStatus.deleted == ClassStatus.deleted) or (classStatus & ClassStatus.removed == ClassStatus.removed):
		cmdlet = "obj = handle.GetManagedObject(None, %s, {%s%s:\"%s\"})\n%s = handle.RemoveManagedObject(obj)" %( peerClassIdStr, peerClassId, dnStr, key, moTag) #06Dec
		
	elif (classStatus & ClassStatus.created == ClassStatus.created):
		if not gmoFlag:
			propertyMap[FirstCapital(classNode.localName) + '.DN'] = '"' + key +'"'
		else:
			propertyMap['"dn"'] = '"' + key +'"'		
		
		
		parentDn = dirname(key)
		if (classStatus & ClassStatus.modified == ClassStatus.modified):
			cmdlet = "%s = handle.AddManagedObject(%s, %s, %s, True)" %(moTag, parentMoTag, peerClassIdStr, CreatePythonPropertyMap(propertyMap)) #27Nov #06Dec
		else:
			cmdlet = "%s = handle.AddManagedObject(%s, %s, %s)" %(moTag, parentMoTag, peerClassIdStr, CreatePythonPropertyMap(propertyMap)) #27Nov #06Dec
	elif (classStatus & ClassStatus.Modified == ClassStatus.Modified):
		cmdlet = "obj = handle.GetManagedObject(None, %s, {%s%s:\"%s\"})\n%s = handle.SetManagedObject(obj, %s, %s" %( peerClassIdStr,  peerClassId, dnStr, key, moTag, FirstCapital(classNode.localName), CreatePythonPropertyMap(propertyMap)) #27Nov#06Dec
		
	else:
		print "Throw Exception XML request status (%s) is invalid." %(classNode.getAttribute(NamingPropertyId.STATUS))
	
	return cmdlet
#================================== End Of Function <FormPythonSubCmdlet> ===============================


### Takes xmlstring, and generate script for configConfMos and configConfMos methods.
#=====================================================================================
def GenerateConfigConfCmdlets(xmlString):
	doc = xml.dom.minidom.parseString(xmlString)
	topNode = doc.documentElement
	
	if topNode is None:
		return

	cmdlet = ""
	# Added Later On
	if len(topNode.getElementsByTagName("inConfigs")) <> 0:
		pairNodes = GetElementChildNodes(topNode.getElementsByTagName("inConfigs")[0])
	else:
		pairNodes = None
	
	if pairNodes is None or len(pairNodes) < 1 :
		node = topNode.getElementsByTagName("inConfig")[0]
		if node is None:
			return
		
		node = GetOnlyElementChildNode(node)
		if node is None:
			return
		
		cmdlet = GetConfigConfCmdlet(node, False)
	elif len(pairNodes) > 1:
		tempCmdlet = ""
		tempDn = ""
		tempMo = ""
		count = 0
		dictMos = {}
		
		cmdlet = "handle.StartTransaction()" + "\n"
		
		for node in pairNodes:
			tempDn = node.getAttribute(NamingPropertyId.KEY)
			tempMo = "mo"
			
			if count > 0:
				tempMo += str(count)
			
			if tempDn not in dictMos:
				dictMos[tempDn] = tempMo
			
			##check if parent is already there in dictionary
			childDn = os.path.basename(tempDn)
			parentDn = os.path.dirname(tempDn)
			
			if parentDn in dictMos:
				node.setAttribute(NamingPropertyId.KEY, childDn)
				tempCmdlet = GetConfigConfCmdlet(node, True)
				cmdlet += tempMo + " = " + dictMos[parentDn] + " | " + tempCmdlet + "\n"
			else:
				tempCmdlet = GetConfigConfCmdlet(node, True)
				cmdlet += tempCmdlet + "\n"
			
			count += 1
		
		cmdlet += "handle.CompleteTransaction()"
		
	else:
		cmdlet = GetConfigConfCmdlet(pairNodes[0], True)
		
	if cmdlet is not None:
		return cmdlet #04dec
		
#========================================= End Of Function <GenerateConfigConfCmdlets> ===================================


### Takes xmlstring, and generate script for configResolveDn, configResolveDns, configResolveClass and configResolveClasses methods.
#===========================================================================================================================
def GenerateConfigResolveCmdlet(xmlString, method):
	## create the document object
	doc = xml.dom.minidom.parseString(xmlString)

	cmdlet= ""

	if IsRootNode(doc,method):
		rootNodeElement = doc.documentElement
	else:
		return

	##<configResolveDn>
	if method == "configResolveDn":
		topNode = doc.documentElement
		if topNode is None:
			return

		dn = topNode.getAttribute(NamingPropertyId.DN)
		inHierarchical = ""
		if topNode.hasAttribute("inHierarchical"):
			inHierarchical = topNode.getAttribute("inHierarchical")

		if inHierarchical.lower() == "true":
			inHierarchicalValue = "YesOrNo.TRUE"
		else:
			inHierarchicalValue = "YesOrNo.FALSE"
		
		cmdlet = "handle.ConfigResolveDn(\"%s\", %s)" %(dn, inHierarchicalValue)


	##<configResolveDns>
	elif method == "configResolveDns":
		topNode = doc.documentElement
		if topNode is None:
			return

		inHierarchical = ""
		if topNode.hasAttribute("inHierarchical"):
			inHierarchical = topNode.getAttribute("inHierarchical")
		
		dnNodes = GetElementChildNodes(topNode.getElementsByTagName("inDns")[0])
		if dnNodes is None:
			return

		cmdlet = "dnSet = DnSet()" + "\n"
		tempDn = ""

		for node in dnNodes:
			tempDn = node.getAttribute(NamingPropertyId.VALUE)
			cmdlet += "dn = Dn()\ndn.setattr(\"Value\",\"%s\")\ndnSet.AddChild(dn)\n" %(tempDn)

		if inHierarchical.lower() == "true":
			inHierarchicalValue = "YesOrNo.TRUE"
		else:
			inHierarchicalValue = "YesOrNo.FALSE"
			
		cmdlet += "handle.ConfigResolveDns(dnSet, %s)" %(inHierarchicalValue)	


	##<configResolveClass>
	elif method == "configResolveClass":
		andCount = 0
		orCount = 0
		notCount = 0
		topNode = doc.documentElement
		filterNode = GetOnlyElementChildNode(topNode)
		print filterNode
		if topNode is None or filterNode is None:
			return

		inHierarchical = ""
		if topNode.hasAttribute("inHierarchical") is not None:
			inHierarchical = topNode.getAttribute("inHierarchical")
		
		classId = ""
		if topNode.hasAttribute("classId") is not None:
			classId = topNode.getAttribute("classId")
	
		if inHierarchical.lower() == "true":
			inHierarchicalValue = "YesOrNo.TRUE"
		else:
			inHierarchicalValue = "YesOrNo.FALSE"
		
		cmdlet = "inFilter = FilterFilter()\n" + CreatePythonFilterCode(filterNode, "inFilter") + "handle.ConfigResolveClass(\"%s\", inFilter, %s)" %(classId, inHierarchicalValue)


	##<configResolveClasses>
	elif method == "configResolveClasses":
		topNode = doc.documentElement
		if topNode is None:
			return
		
		inHierarchical = ""
		if topNode.hasAttribute("inHierarchical") is not None:
			inHierarchical = topNode.getAttribute("inHierarchical")
		
		classIdNodes = GetElementChildNodes(topNode.getElementsByTagName("inIds")[0])
		
		cmdlet = "idSet = ClassIdSet()" + "\n"
		tempClassId = ""
		for node in classIdNodes:
			tempClassId = node.getAttribute(NamingPropertyId.VALUE)
			cmdlet += "clsId = ClassId()\nclsId.setattr(\"Value\",\"%s\")\nidSet.AddChild(clsId)\n" %(tempClassId)

		
		if inHierarchical.lower() == "true":
			inHierarchicalValue = "YesOrNo.TRUE"
		else:
			inHierarchicalValue = "YesOrNo.FALSE"
		
		cmdlet += "handle.ConfigResolveClasses(idSet, %s)" %(inHierarchicalValue)

		
	return cmdlet #04dec
#===================================== End Of Function <GenerateConfigResolveCmdlet> ===================================


### provide filter support
#========================================================================================
def CreatePythonFilterCode(parentNode, parentFilterName):
	cmdlet = ""
	filterName = ""
	tempName = ""
	
	for node in GetElementChildNodes(parentNode):
		
		if node.localName == "and":
			tempName = "andFilter" + str(andCount)
			andCount += 1
			cmdlet = tempName + + " = AndFilter()\n" + CreatePythonFilterCode(node, tempName) + parentFilterName + ".AddChild(" + tempName +")\n"
			continue

		if node.localName == "or":
			tempName = "orFilter" + str(orCount)
			orCount += 1
			cmdlet = tempName + + " = OrFilter()\n" + CreatePythonFilterCode(node, tempName) + parentFilterName + ".AddChild(" + tempName +")\n"
			continue

		if node.localName == "not":
			tempName = "notFilter" + str(notCount)
			notCount += 1
			cmdlet = tempName + + " = NotFilter()\n" + CreatePythonFilterCode(node, tempName) + parentFilterName + ".AddChild(" + tempName +")\n"
			continue

		if node.localName == "eq":
			filterName = "eqFilter"

		if node.localName == "ne":
			filterName = "neFilter"

		if node.localName == "gt":
			filterName = "gtFilter"

		if node.localName == "lt":
			filterName = "ltFilter"

		if node.localName == "le":
			filterName = "leFilter"

		if node.localName == "wcard":
			filterName = "wcardFilter"

		if node.localName == "anybit":
			filterName = "anybitFilter"

		if node.localName == "allbits":
			filterName = "allbitsFilter"

		if node.localName == "bw":
			filterName = "bwFilter"

		cmdlet += filterName + " = " + FirstCapital(filterName) + "()\n"
		
		for name, value in node.attributes.items():
			cmdlet += "%s.%s = \"%s\"\n" %(filterName, FirstCapital(name), value)
		
		cmdlet += parentFilterName + ".AddChild(" + filterName + ")\n"
		
	return cmdlet
#========================================= End Of Function <CreatePythonFilterCode> ====================================


### Function to handle method <lsClone> and <lsInstantiateTemplate>
#========================================================================================
def GenerateSingleCloneCmdlets(xmlString, isTemplate):
	### create the document object
	doc = xml.dom.minidom.parseString(xmlString)
	node = None
	
	topNode = doc.documentElement
	
	if topNode is None:
		return
	
	if isTemplate:
		if topNode.localName == "lsInstantiateTemplate":
			node = topNode
	else:
		if topNode.localName == "lsClone":
			node = topNode
	
	dn = ""
	if node.hasAttribute(NamingPropertyId.DN):
		dn = node.getAttribute(NamingPropertyId.DN)
	else:
		print "Attribute 'Dn' not available"   ## writewarning in dotnet
		return
	
	spNewName = ""
	if node.hasAttribute("inServerName"):
		spNewName = node.getAttribute("inServerName")
	else:
		print "Attribute 'inServerName' not available"   ## writewarning in dotnet
		return
	
	destOrg =""
	if node.hasAttribute("inTargetOrg"):
		destOrg = node.getAttribute("inTargetOrg")
	
	spName = re.sub(r"^(org-[\-\.:_a-zA-Z0-9]{1,16}/)*org-[\-\.:_a-zA-Z0-9]{1,16}/ls-","",dn)
	
	sourceOrg = ""
	matchObject = re.match(r"^(org-[\-\.:_a-zA-Z0-9]{1,16}/)*org-[\-\.:_a-zA-Z0-9]{1,16}",dn)
	if matchObject is not None:
		sourceOrg = matchObject.group(0)
	else:
		print "Attribute 'Dn' is corrupt"
		return
	
	cmdlet = ""
	inHierarchical = ""
	if node.hasAttribute("inHierarchical") is not None:
		inHierarchical = node.getAttribute("inHierarchical")
	
	if inHierarchical.lower() == "true":
		inHierarchicalValue = "YesOrNo.TRUE"
	else:
		inHierarchicalValue = "YesOrNo.FALSE"
		
	
	if isTemplate:
		cmdlet = "handle.lsInstantiateTemplate(\"%s\", \"%s\", \"%s\", %s)" %(dn, spNewName, destOrg, inHierarchicalValue)

	else:
		cmdlet = "handle.LsClone(\"%s\", \"%s\", \"%s\", %s)" %(dn, spNewName, destOrg, inHierarchicalValue)

	return cmdlet #04dec
#=================================== End Of Function <GenerateSingleCloneCmdlets> =====================================


### Function to handle method <lsTemplatise>
#========================================================================================
def GenerateLsTemplatiseCmdlets(xmlString):
	doc = xml.dom.minidom.parseString(xmlString)
	node = None
	
	topNode = doc.documentElement
	
	if topNode is None:
		return

	if topNode.localName == "lsTemplatise":
		node = topNode
	else:
		print "Check if Method is <lsTemplatise>"
		return
	
	dn = ""
	if node.hasAttribute(NamingPropertyId.DN):
		dn = node.getAttribute(NamingPropertyId.DN)
	else:
		print "Attribute 'Dn' not available"   ## writewarning in dotnet
		return
	
	spNewName = ""
	if node.hasAttribute("inTemplateName"):
		spNewName = node.getAttribute("inTemplateName")
	else:
		print "Attribute 'inTemplateName' not available"   ## writewarning in dotnet
		return
	
	templateType = ""
	if node.hasAttribute("inTemplateType"):
		templateType = node.getAttribute("inTemplateType")
	else:
		print "Attribute 'inTemplateType' not available"   ## writewarning in dotnet
		return
	
	destOrg = ""
	if node.hasAttribute("inTargetOrg"):
		destOrg = node.getAttribute("inTargetOrg")
	
	spName = re.sub(r"^(org-[\-\.:_a-zA-Z0-9]{1,16}/)*org-[\-\.:_a-zA-Z0-9]{1,16}/ls-","",dn)
	
	sourceOrg = ""
	matchObject = re.match(r"^(org-[\-\.:_a-zA-Z0-9]{1,16}/)*org-[\-\.:_a-zA-Z0-9]{1,16}",dn)
	if matchObject is not None:
		sourceOrg = matchObject.group(0)
	else:
		print "Attribute 'Dn' is corrupt"
		return
	
	cmdlet = ""
	inHierarchical = ""
	if node.hasAttribute("inHierarchical") is not None:
		inHierarchical = node.getAttribute("inHierarchical")
	
	if inHierarchical.lower() == "true":
		inHierarchicalValue = "YesOrNo.TRUE"
	else:
		inHierarchicalValue = "YesOrNo.FALSE"
	
	if destOrg is not None:
		cmdlet = "handle.LsTemplatise(\"%s\", \"%s\", \"%s\", \"%s\", %s)" %(dn, destOrg, spNewName, templateType, inHierarchicalValue)

	else:
		cmdlet = "handle.LsTemplatise(\"%s\", \"org-root\", \"%s\", \"%s\", %s)" %(dn, spNewName, templateType, inHierarchicalValue)

	return cmdlet #04dec
#======================================= End Of Function <GenerateLsTemplatiseCmdlets> =================================


### Function to handle method <lsInstantiateNTemplate> and <lsInstantiateNNamedTemplate>
#========================================================================================
def GenerateMultipleCloneCmdlets(xmlString, isPrefixBased):
	doc = xml.dom.minidom.parseString(xmlString)
	node = None
	
	topNode = doc.documentElement
	#print topNode.localName
	
	if topNode is None:
		return
	
	if isPrefixBased:
		if topNode.localName == "lsInstantiateNTemplate":
			node = topNode
	else:
		if topNode.localName == "lsInstantiateNNamedTemplate":
			node = topNode
	
	dn = ""
	if node.hasAttribute(NamingPropertyId.DN):
		dn = node.getAttribute(NamingPropertyId.DN)
	else:
		print "Attribute 'Dn' not available"   ## writewarning in dotnet
		return
	
	destOrg =""
	if node.hasAttribute("inTargetOrg"):
		destOrg = node.getAttribute("inTargetOrg")

	spName = re.sub(r"^(org-[\-\.:_a-zA-Z0-9]{1,16}/)*org-[\-\.:_a-zA-Z0-9]{1,16}/ls-","",dn)
	
	sourceOrg = ""
	matchObject = re.match(r"^(org-[\-\.:_a-zA-Z0-9]{1,16}/)*org-[\-\.:_a-zA-Z0-9]{1,16}",dn)
	if matchObject is not None:
		sourceOrg = matchObject.group(0)
	else:
		print "Attribute 'Dn' is corrupt"
		return
	
	cmdlet = ""
	inHierarchical = ""
	if node.hasAttribute("inHierarchical") is not None:
		inHierarchical = node.getAttribute("inHierarchical")
	
	if isPrefixBased:
		prefix = ""
		if node.hasAttribute("inServerNamePrefixOrEmpty") is not None:
			prefix = node.getAttribute("inServerNamePrefixOrEmpty")
		else:
			print "Attribute 'inServerNamePrefixOrEmpty' not available"
			return
		
		count = 0
		if node.hasAttribute("inNumberOf") is not None:
			count = node.getAttribute("inNumberOf")
		else:
			print "Attribute 'inNumberOf' not available"
			return
		
		if inHierarchical.lower() == "true":
			inHierarchicalValue = "YesOrNo.TRUE"
		else:
			inHierarchicalValue = "YesOrNo.FALSE"
	
		cmdlet = "handle.LsInstantiateNTemplate(\"%s\", %s, \"%s\", \"%s\", %s)" %(dn, count, spName, destOrg, inHierarchicalValue)

	else:
		dnNodes = GetElementChildNodes(node.getElementsByTagName("inNameSet")[0])
		if dnNodes is None or len(dnNodes)<1:
			print "Xml is corrupt. New names not available"
			return
		
		newNames = "@("
		newNameExists = False
		tempDn = ""
		cmdlet = "dnSet = DnSet()" + "\n"
		
		for dnNode in dnNodes:
			if dnNode.hasAttribute("value"):
				newNameExists = True
				tempDn = dnNode.getAttribute("value")
				newNames += "\"" + tempDn + "\","
				cmdlet += "dn = Dn()\ndn.setattr(\"Value\",\"%s\")\ndnSet.AddChild(dn)\n" %(tempDn)
			else:
				print "Xml is corrupt. New names not available"
				return
		
		if not newNameExists:
			print "Xml is corrupt. New names not available"
			return
		
		newNames = newNames.rstrip(',')
		newNames += ")"
		
		if inHierarchical.lower() == "true":
			inHierarchicalValue = "YesOrNo.TRUE"
		else:
			inHierarchicalValue = "YesOrNo.FALSE"
	
		cmdlet += "handle.LsInstantiateNNamedTemplate(\"%s\", dnSet, \"%s\", %s)" %(dn, destOrg, inHierarchicalValue)

	return cmdlet #04dec
#====================================== End Of Function <GenerateMultipleCloneCmdlets> ======================================


### Function to handle method <statsClearInterval>
#========================================================================================
def GenerateClearIntervalCmdlet(xmlString):
	doc = xml.dom.minidom.parseString(xmlString)
	node = None
	
	topNode = doc.documentElement
	
	if topNode is None:
		return
	
	if topNode.localName == "statsClearInterval":
		node = topNode
	else:
		print "Check if Method is <statsClearInterval>"
		return
	
	cmdlet = ""
	dnNodes = GetElementChildNodes(node.getElementsByTagName("inDns")[0])
	
	if dnNodes is None or len(dnNodes) < 0:
		return
	
	cmdlet = "dnSet = DnSet()" + "\n"
	tempDn = ""
	
	for dnNode in dnNodes:
		tempDn = dnNode.getAttribute(NamingPropertyId.VALUE)
		cmdlet += "dn = Dn()\ndn.setattr(\"Value\",\"%s\")\ndnSet.AddChild(dn)\n" %(tempDn)
	
	cmdlet += "handle.ConfigResolveDns(dnSet)"

	return cmdlet #04dec
#==================================== End Of Function <GenerateClearIntervalCmdlet> =======================================


#-------------------------------- END - OF - METHOD SPECIFIC - FUNCTION -------------------------------- 


### check which function to call for a specific method
#======================================================
def GenerateCmdlets(xmlString):
	cmdlet = ""
	global displayXml, outFilePath
	if displayXml:
		doc = xml.dom.minidom.parseString(xmlString)
		DumpXmlOnScreen(doc)
		
	category = ""
	matchFound = re.match(r"^[\s]*<[\s]*([\S]+)", xmlString)
	if matchFound:
		methodName = matchFound.group(1)
		category = methodName
	else:
		return
	
	if category == "configConfMos" or category == "configConfMo":
		cmdlet = GenerateConfigConfCmdlets(xmlString)
	elif category in ["configResolveDn","configResolveDns","configResolveClass","configResolveClasses"]:
		cmdlet = GenerateConfigResolveCmdlet(xmlString, category)
	elif category == "lsClone":
		cmdlet = GenerateSingleCloneCmdlets(xmlString, False)
	elif category == "lsInstantiateTemplate":
		cmdlet = GenerateSingleCloneCmdlets(xmlString, True)
	elif category == "lsTemplatise":
		cmdlet = GenerateLsTemplatiseCmdlets(xmlString)
	elif category == "lsInstantiateNTemplate":
		cmdlet = GenerateMultipleCloneCmdlets(xmlString, True)
	elif category == "lsInstantiateNNamedTemplate":
		cmdlet = GenerateMultipleCloneCmdlets(xmlString, False)
	elif category == "statsClearInterval":
		cmdlet = GenerateClearIntervalCmdlet(xmlString)
	## 04dec: support for redirecting script output to respective file
	if outFileFlag:
		outFile = open(outFilePath, 'a')
		print >> outFile, '##### Start-Of-PythonScript #####'
		print >> outFile, cmdlet
		print >> outFile, '##### End-Of-PythonScript #####'
		outFile.close()
	else:
		print "##### Start-Of-PythonScript #####"	
		print cmdlet
		print "##### End-Of-PythonScript #####"
	return
#===================================== End Of Function <GenerateCmdlets> ==================================

	
###This Extracts xmlstring from the file and calls the GenerateCmdlets() on this xmlstring.
#======================================================
def ExtractXML(fileStream,line):
	readFlag = False
	requestString = ""
	while line <> "":
		if readFlag and not re.search(r"^\s*$",line):
			requestString += line + "\n"
		
		if CheckIfAnyListValueInString(multiLineMethod, line):
			requestString += line + "\n"
			readFlag = True

		if readFlag and CheckIfAnyListValueInString(singleLineMethod, line):
			readFlag = False
			GenerateCmdlets(requestString)
			requestString = ""
			break
		
		line = fileStream.readline()
#===================================== End Of Function <ExtractXML> ==================================

###Depending on guiLog flag, calls the ExtractXML() internally.
#======================================================
def FindXmlRequestsInFile_test(fileStream, guiLog):
	#print "Inside FindXmlRequestsInFile_test"
	line = fileStream.readline()
	while line <> "":
		if not guiLog:
			ExtractXML(fileStream,line)
		elif "[------------- Sending Request to Server ------------" in line:
			line = fileStream.readline()
			ExtractXML(fileStream, line)
		line = fileStream.readline()
#===================================== End Of Function <FindXmlRequestsInFile_test> ==================================

###checks if path or literalPath present for the respective parameter set and if exists then call FindXmlRequestsInFile_test()
#======================================================
def IfPathOrLiteralPath(path,literalPath, guiLog):
	if path:
		if literalPath:
			print "Parameter <path> takes precedence over <literalPath>"
		filePath = path
	elif literalPath:
		filePath = literalPath
	else:
		print "Please provide path or literalPath"
		return

	fileStream = open(filePath, 'r')
	FindXmlRequestsInFile_test(fileStream, guiLog)
	fileStream.close()
#===================================== End Of Function <IfPathOrLiteralPath> ==================================


### By default this will generate python script for the action in UCSM GUI.
### xml=True & request="xmlstring"	: Generate Python Script for XML Request.
### xml=True & path/LiteralPath		: Generate Python script from the file containing XML Request.
### guiLog=True & path/LiteralPath	: Generate Python script from the UCSM GUI logfile.
### displayXML=True will also dispaly corresponding XML Request.
#======================================================
def ConvertToPython(xml=False,request=None,guiLog=False,path=None,literalPath=None,dumpXml=False,dumpToFile=False,dumpFilePath=None):
	print "### Please review the generated cmdlets before deployment.\n"
	global displayXml, outFileFlag, outFilePath, outFile
	displayXml=dumpXml
	outFileFlag=dumpToFile
	outFilePath=dumpFilePath
	
	if outFileFlag in _AffirmativeList:
		if outFilePath:
			print "### Script Output is in file < " + outFilePath + " >"
			outFile = open(outFilePath, 'w')
			outFile.close()
			#outFile = open(r"c:\work.txt", 'w+')
		else:
			print "Please profide dumpFilePath"
			return
	
	if xml in _AffirmativeList:
		if guiLog in _AffirmativeList:
			print "parameter <xml> takes precedence over <guiLog>"
		
		if request:
			GenerateCmdlets(request)
		elif path or literalPath:
			IfPathOrLiteralPath(path,literalPath,False)
		else:
			print "Please provide request"
			return
	elif guiLog in _AffirmativeList:
		if path or literalPath:
			IfPathOrLiteralPath(path,literalPath,True)
		else:
			print "Please provide path or literalPath"
	else:
		from sys import platform as _platform

		if _platform.lower() == "linux" or _platform.lower() == "linux2":
			# linux
			logFilePath = GetUCSDefaultLogpathLinux()
		elif _platform.lower() == "darwin":
			# OS X
			logFilePath = GetUCSDefaultLogpathOSX()
		elif _platform.lower() == "win32" or _platform.lower() == "win64":
			# Windows...
			logFilePath = GetUCSDefaultLogpathWindows()
		elif "cygwin" in _platform.lower():
			# Cygwin
			logFilePath = GetUCSDefaultLogpathCygwin()
		else:
			print "[Error]: Unsupported OS:",_platform
			logFilePath = None
			return


		## Get the latest logfile
		#logFilePath = r"C:\Users\ragupta4\AppData\LocalLow\Sun\Java\Deployment\log\.ucsm"
		#files = [ file for file in glob.glob(logFilePath + "\\" + "*") if os.path.isfile(file)]

		os.chdir(logFilePath)
		files = [ file for file in glob.glob("centrale_*.log") if os.path.isfile(file)]
		files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
		lastUpdatedFile = files[0]

		fileStream = open(lastUpdatedFile, 'r')
		## read the file till the end
		cnt = 0
		for line in fileStream:
			cnt += 1		
		## Wait indefinitely until receive new line of set and then again wait
		while True:
			line = fileStream.readline()
			if line:
				FindXmlRequestsInFile_test(fileStream, True)
			time.sleep(2)
		fileStream.close()
	
	#if outFilePath:
		#outFile.close()
			
	print "### End of Convert-To-Python ###"
#===================================== End Of Function <ConvertToPython> ==================================

def GetUCSDefaultLogpathWindows ():
	if 'APPDATA' in os.environ.keys():
		logFilePath = os.getenv('APPDATA')
	else:
		print os.name
		raise 'Not windows OS'

	if sys.getwindowsversion()[0] == 6: ## in case OS is Win 2008 or above
		logFilePath = dirname(logFilePath) + "\LocalLow"
	logFilePath += r"\Sun\Java\Deployment\log\.ucsm" + "\\"
	return logFilePath


def GetUCSDefaultLogpathLinux ():
	logFilePath = os.getenv('HOME')
	logFilePath += r"/.java/deployment/log/.ucsm/"
	return logFilePath

def GetUCSDefaultLogpathOSX ():
	logFilePath = os.getenv('HOME')
	logFilePath += r"/Library/Caches/Java/log/.ucsm"
	return logFilePath


## SVN CheckIn3 Added Support for CYGWIN
def GetUCSDefaultLogpathCygwin():
	#from subprocess import Popen, PIPE
	#p = Popen('cat /proc/registry/HKEY_LOCAL_MACHINE/SOFTWARE/Microsoft/Windows\ NT/CurrentVersion/CurrentVersion', shell=True,stdout=PIPE, stderr=PIPE)
	#out, err = p.communicate()
	#OSMajorVersion = out.split('.')[0]
	
	logFilePath = os.getenv('APPDATA')
	logFilePath = logFilePath.replace("\\","/")

	#TODO:
	#if OSMajorVersion == 6: 
	logFilePath = dirname(logFilePath) + "/LocalLow"
	logFilePath += r"/Sun/Java/Deployment/log/.ucsm/"
	return logFilePath

