# Copyright 2014 OpenStack Foundation
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from UcsSdk import *
from UcsSdk.utils import helper as ucs_helper
from UcsSdk.utils import exception

class BootDeviceHelper(object):
    """Cisco UCS Service Profile Boot Device helper."""

    def __init__(self, helper=None):
        """Initialize with UCS Manager details.

            :param helper: helper object
            :param password: Login user password
            """
        self.helper = helper

    def _set_boot_device(self, device, persistent):
        """Set the boot device for the node.

            Set the boot device to use on next reboot of the node.
            :param device: the boot device, one of
            :mod:`ironic.common.boot_devices`.
            :param persistent: Boolean value. True if the boot device will
                persist to all future boots, False if not.
                Default: False. Ignored by this driver.
            :raises: UcsOperationError if it UCS Manager reports any error.
            """
        sp_rn = self.helper.service_profile
        dn, sp_rn = sp_rn.split("/ls-", -1)
        boot_policy_rn = "boot-policy-" + "Ironic-" + sp_rn
        boot_policy_dn = UcsUtils.MakeDn([dn, boot_policy_rn])
        boot_policy_cfg = {
                LsbootPolicy.NAME: "Ironic-" + sp_rn,
                LsbootPolicy.PURPOSE: "operational",
                LsbootPolicy.REBOOT_ON_UPDATE: "no",
                LsbootPolicy.ENFORCE_VNIC_NAME: "no"
                }

        operation = "set_boot_device"
        try:
            ucs_helper.config_managed_object(dn,
                              OrgOrg.ClassId(),
                              LsbootPolicy.ClassId(),
                              boot_policy_cfg,
                              boot_policy_dn,
                              self.helper.handles[self.helper.hostname])
        except UcsException as ex:
            raise exception.UcsOperationError(operation=operation, error=ex)

        if device == 'cdrom':
            boot_vm_dn = UcsUtils.MakeDn([boot_policy_dn,
                             "read-only-vm"])
            boot_vm_list = {'Order': 1}
            try:
                ucs_helper.config_managed_object(boot_policy_dn,
                                 LsbootPolicy.ClassId(),
                                 LsbootVirtualMedia.ClassId(),
                                 boot_vm_list, boot_vm_dn,
                                 self.helper.handles[self.helper.hostname])
            except UcsException as ex:
                print(_("Cisco client exception: %(msg)s."), {'msg': ex})
                raise exception.UcsOperationError(operation=operation,
                                                  error=ex)
        elif device == 'pxe':
            boot_lan_dn = UcsUtils.MakeDn([boot_policy_dn,
                              "lan"])
            boot_lan_img_path_cfg = {'Type': 'primary', 'VnicName': 'eth0'}
            boot_lan_cfg = {'Type': 'lan',
                            'Access': 'read-only',
                            'Prot': 'pxe',
                            'Order': 1}
            image_path_dn = UcsUtils.MakeDn([boot_lan_dn,
                                "path-primary"])
            try:
                print(_(boot_lan_cfg))
                print(_(boot_lan_img_path_cfg))
                ucs_helper.config_managed_object(boot_policy_dn,
                               LsbootPolicy.ClassId(),
                               LsbootLan.ClassId(),
                               boot_lan_cfg, boot_lan_dn,
                               self.helper.handles[self.helper.hostname])
                ucs_helper.config_managed_object(boot_lan_dn,
                              LsbootLan.ClassId(),
                              LsbootLanImagePath.ClassId(),
                              boot_lan_img_path_cfg,
                              image_path_dn,
                              self.helper.handles[self.helper.hostname])
            except UcsException as ex:
                print(_("Cisco client exception: %(msg)s."),{'msg': ex})
                raise exception.UcsOperationError(operation=operation,
                                                  error=ex)
        elif device == 'disk':
            boot_storage_dn = UcsUtils.MakeDn([boot_policy_dn,
                                  "storage"])
            boot_storage_cfg = {'Order': 1}
            boot_local_storage_dn = (UcsUtils.MakeDn([boot_storage_dn,
                    "local-storage"]))
            try:
                ucs_helper.config_managed_object(boot_policy_dn,
                    LsbootPolicy.ClassId(),
                    LsbootStorage.ClassId(),
                    boot_storage_cfg, boot_storage_dn,
                    self.helper.handles[self.helper.hostname])

                ucs_helper.config_managed_object(boot_storage_dn,
                    LsbootStorage.ClassId(),
                    LsbootLocalStorage.ClassId(), {},
                    boot_local_storage_dn,
                    self.helper.handles[self.helper.hostname])
            except UcsException as ex:
                print(_("Cisco client exception: %(msg)s."), {'msg': ex})
                raise exception.UcsOperationError(operation=operation,
                                                  error=ex)
        try:
            ucs_helper.config_managed_object(
                     "org-root",
                     OrgOrg.ClassId(), LsServer.ClassId(),
                     {'BootPolicyName': "Ironic-" + sp_rn},
                     "org-root/ls-devstack",
                     self.helper.handles[self.helper.hostname], delete=False)
        except UcsException as ex:
            print(_("Cisco client exception: %(msg)s."), {'msg': ex})
            raise exception.UcsOperationError(operation=operation,
                                              error=ex)

    def get_boot_device(self):
        """Get the current boot device for the node.

            Provides the current boot device of the node. Be aware that not
            all drivers support this.

            :raises: InvalidParameterValue if any connection parameters are
                incorrect.
            :raises: MissingParameterValue if a required parameter is missing
            :returns: a dictionary containing:

            :boot_device: the boot device, one of
            :mod:`ironic.common.boot_devices` or None if it is unknown.
            :persistent: Whether the boot device will persist to all
                future boots or not, None if it is unknown.
            """
        operation = 'get_boot_device'
        try:
            boot_device = None
            ls_server = ucs_helper.get_managed_object(
                              self.helper.handles[self.helper.hostname],
                              LsServer.ClassId(),
                              {LsServer.DN: self.helper.service_profile})
            if not ls_server:
                raise exception.UcsOperationError(operation=operation,
                          error="Failed to get power MO, "
                          "configure valid service-profile.")
            for server in ls_server:
                in_filter = ucs_helper.create_dn_in_filter(
                    LsbootDef.ClassId(), "%s/" %
                    server.getattr(LsServer.PN_DN),
                    self)

                lsboot_def = ucs_helper.get_resolve_class(
                     self.helper.handles[self.helper.hostname],
                     LsbootDef.ClassId(), in_filter, in_heir=True)

                if lsboot_def.errorCode == 0:
                    for boot_def in lsboot_def.OutConfigs.GetChild():
                        boot_orders = boot_def.GetChild()
                        for boot_order in boot_orders:
                            if boot_order.getattr("Order") == "1":
                                boot_device = boot_order.getattr("Type")
                                break
            return {'boot_device': boot_device, 'persistent': None}
        except UcsException as ex:
            print(_("Cisco client exception: %(msg)s."), {'msg': ex})
            raise exception.UcsOperationError(operation=operation, error=ex)
