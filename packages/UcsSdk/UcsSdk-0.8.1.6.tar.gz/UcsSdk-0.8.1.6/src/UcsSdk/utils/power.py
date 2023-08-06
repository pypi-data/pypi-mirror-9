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

class UcsPower(object):
    """Cisco UCS Power helper."""

    def __init__(self, helper):
        """Initialize with UCS Manager details.

            :param helper: Ucs helper object
            """
        self.helper = helper

    def get_power_state(self):
        """Get current power state of this node

            :param node: Ironic node one of :class:`ironic.db.models.Node`
            :raises: InvalidParameterValue if required Ucs parameters are
                missing
            :raises: UcsServiceUnavailable on an error from Ucs.
            :returns: Power state of the given node
            """
        rn_array = [self.helper.service_profile,
             ManagedObject(NamingId.LS_POWER).MakeRn()]
        try:
            ls_power = ucs_helper.get_managed_object(
                           self.helper.handles[self.helper.hostname],
                           LsPower.ClassId(),
                           {LsPower.DN: UcsUtils.MakeDn(rn_array)})
            if not ls_power:
                raise exception.UcsOperationError("get_power_state",
                          "Failed to get LsPower MO, configure valid "
                          "service-profile")
            return ls_power[0].getattr(LsPower.STATE)
        except UcsException as ex:
            raise exception.UcsOperationError(message=ex)

    def set_power_state(self, desired_state):
        """Set power state of this node

            :param node: Ironic node one of :class:`ironic.db.models.Node`
            :raises: InvalidParameterValue if required seamicro parameters are
                missing.
            :raises: UcsServiceUnavailable on an error from UcsHandle Client.
            :returns: Power state of the given node
            """
        rn_array = [self.helper.service_profile,
             ManagedObject(NamingId.LS_POWER).MakeRn()]
        try:
            ls_power = ucs_helper.get_managed_object(self.helper.handles[self.helper.hostname],
                                  LsPower.ClassId(),
                                  {LsPower.DN: UcsUtils.MakeDn(rn_array)})
            if not ls_power:
                raise exception.UcsOperationError("set_power_state",
                          "Failed to get power MO,"
                          " configure valid service-profile.")
            else:
                ls_power_set = self.helper.handles[self.helper.hostname].SetManagedObject(
                                    ls_power,
                                    LsPower.ClassId(),
                                    {LsPower.STATE: desired_state},
                                    dumpXml=YesOrNo.TRUE
                                    )
                if ls_power_set:
                    power = ls_power_set.pop()
                    return power.getattr(LsPower.STATE)
                else:
                    return states.ERROR
        except Exception as ex:
            raise exception.UcsOperationError("set_power_state",
                  "Failed to get power MO,"
                  "configure valid servie-profile.")

    def reboot(self):
        """Hard reset the power of this node.
           """
        self.set_power_state(LsPower.CONST_STATE_HARD_RESET_IMMEDIATE)
