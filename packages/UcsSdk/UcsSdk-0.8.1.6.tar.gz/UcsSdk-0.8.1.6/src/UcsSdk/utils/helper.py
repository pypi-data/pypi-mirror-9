#    Copyright 2014, Cisco Systems.

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Common functionalities shared between different UCS modules.
"""

import functools
from UcsSdk import *
from UcsSdk.utils import exception


def create_dn_in_filter(filter_class, filter_value, helper):
    """ Creates filter object for given class name, and DN values."""
    in_filter = FilterFilter()
    in_filter.AddChild(create_dn_wcard_filter(filter_class, filter_value))
    return in_filter


def create_dn_wcard_filter(filter_class, filter_value):
    """ Creates wild card filter object for given class name, and values.
        :param filter_class: class name
	:param filter_value: filter property value
	:return WcardFilter: WcardFilter object
        """
    wcard_filter = WcardFilter()
    wcard_filter.Class = filter_class
    wcard_filter.Property = "dn"
    wcard_filter.Value = filter_value
    return wcard_filter


def generate_ucsm_handle(hostname, username, password, helper):
    """ Creates UCS Manager handle object and establishes a session with 
        UCS Manager.
        :param hostname: UCS Manager hostname or IP-address
        :param username: Username to login to UCS Manager
        :param password: Login user password
	:returns ucs_handle: active connection to UCS Manager
	:raises UcsServiceUnavailable: In case service is available.
	"""
    ucs_handle = UcsHandle()
    try:
        success = ucs_handle.Login(hostname, username, password)
        helper.handles[hostname] = ucs_handle
    except UcsException as e:
        print("Cisco client exception %(msg)s" % (e.message))
        raise exception.UcsServiceUnavailable(message=e.message)
    return success, ucs_handle


def get_managed_object(handle, class_id, params, inMo=None, in_heir=False,
                       dump=True):
    """Get the specified MO from UCS Manager.

        :param managed_object: MO classid
        :in_filter: input filter value
        :returns: Managed Object
        :raises: UcsException in case of failure.
        """
    return handle.GetManagedObject(inMo, class_id, params,
                      inHierarchical=in_heir,
                      dumpXml=dump)


def get_resolve_class(handle, class_id,
                      in_filter, in_heir=False, dump=YesOrNo.TRUE):
    return handle.ConfigResolveClass(
        class_id, in_filter,
        inHierarchical=in_heir,
        dumpXml=dump)


def config_managed_object(p_dn, p_class_id, class_id,
                          mo_config, mo_dn, handle=None, delete=True):
    """Configure the specified MO in UCS Manager.

        :param uuid: MO config
        :param p_dn: parent MO DN
        :param p_class_id: parent MO class ID
        :param class_id: MO class ID
        :param MO configuration: MO config
        :param mo_dn: MO DN value
        :param handle: optional UCS Manager handle object
        :returns: Managed Object
        :raises: UcsOperationError in case of failure.
        """
    if handle is None:
        handle = self.handles[self.hostname]

    try:
        res = handle.GetManagedObject(None, p_class_id, {"Dn": p_dn},
                                      dumpXml=YesOrNo.TRUE)
        mo_res = handle.GetManagedObject(res, class_id, {"Dn": mo_dn},
                                         dumpXml=YesOrNo.TRUE)
        result = None
        if mo_res and class_id != LsbootPolicy.ClassId() and delete:
            print(_("Mo exists, delete and recreate"))
            remove_resp = handle.RemoveManagedObject(mo_res)
            if not remove_resp:
                print(_("Cisco client exception: "
                    "Failed to remove ManagedObject."))

        if not delete: 
            result = handle.SetManagedObject(mo_res, class_id, mo_config,
                                         dumpXml=YesOrNo.TRUE)
        else:
            result = handle.AddManagedObject(res, class_id, mo_config,
                                         dumpXml=YesOrNo.TRUE)
        return result

    except UcsException as ex:
        print(_("Cisco client exception: %(msg)s"), {'msg': ex})
        raise exception.UcsOperationError('config_managed_object', error=ex)


class CiscoUcsHelper(object):
    """Cisco UCS helper."""

    def __init__(self, hostname=None, username=None, password=None):
        """Initialize with UCS Manager details.

            :param hostname: UCS Manager hostname or ipaddress
            :param username: Username to login to UCS Manager
            :param password: Login user password
            """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.service_profile = None
        self.handles = {}

