# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2014 Etherios, Inc. All rights reserved.
# Etherios, Inc. is a Division of Digi International.

"""Server Command Interface functionality"""
from devicecloud.apibase import APIBase
import six


SCI_TEMPLATE = """\
<sci_request version="1.0">
  <{operation}{synchronous}{cache}{sync_timeout}{allow_offline}{wait_for_reconnect}>
    <targets>
      {targets}
    </targets>
    {payload}
  </{operation}>
</sci_request>
""".replace("  ", "").replace("\r", "").replace("\n", "")  # two spaces is indentation


class TargetABC(object):
    """Abstract base class for all target types"""


class DeviceTarget(TargetABC):
    """Target a specific device"""

    def __init__(self, device_id):
        self._device_id = device_id

    def to_xml(self):
        return '<device id="{}"/>'.format(self._device_id)


class AllTarget(TargetABC):
    """Target all devices"""

    def __init__(self):
        pass

    def to_xml(self):
        return '<device id="all"/>'


class TagTarget(TargetABC):
    """Target devices having a specific tag"""

    def __init__(self, tag):
        self._tag = tag

    def to_xml(self):
        return '<device tag="{}"/>'.format(self._tag)


class GroupTarget(TargetABC):
    """Target devices in a specific group"""

    def __init__(self, group):
        self._group = group

    def to_xml(self):
        return '<group path="{}">'.format(self._group)


class ServerCommandInterfaceAPI(APIBase):
    """Encapsulate Server Command Interface API"""

    def send_sci(self, operation, target, payload, reply=None, synchronous=None, sync_timeout=None,
                 cache=None, allow_offline=None, wait_for_reconnect=None):
        """Send SCI request to 1 or more targets

        :param str operation: The operation is one of {send_message, update_firmware, disconnect, query_firmware_targets,
            file_system, data_service, and reboot}
        :param target: The device(s) to be targeted with this request
        :type target: :class:`~.TargetABC` or list of :class:`~.TargetABC` instances

        TODO: document other params

        """
        if not isinstance(payload, six.string_types):
            raise TypeError("payload is required to be string")

        # validate targets and bulid targets xml section
        try:
            iter(target)
            targets = target
        except TypeError:
            targets = [target, ]
        if not all(isinstance(t, TargetABC) for t in targets):
            raise TypeError("Target(s) must each be instances of TargetABC")
        targets_xml = "".join(t.to_xml() for t in targets)

        # reply argument
        if not isinstance(reply, (type(None), six.string_types)):
            raise TypeError("reply must be either None or a string")
        if reply is not None:
            reply_xml = ' reply="{}"'.format(reply)
        else:
            reply_xml = ''

        # synchronous argument
        if not isinstance(synchronous, (type(None), bool)):
            raise TypeError("synchronous expected to be either None or a boolean")
        if synchronous is not None:
            synchronous_xml = ' synchronous="{}"'.format('true' if synchronous else 'false')
        else:
            synchronous_xml = ''

        # sync_timeout argument
        # TODO: What units is syncTimeout in?  seconds?
        if not sync_timeout is None or isinstance(sync_timeout, six.integer_types):
            raise TypeError("sync_timeout expected to either be None or a number")
        if sync_timeout is not None:
            sync_timeout_xml = ' syncTimeout="{}"'.format(sync_timeout)
        else:
            sync_timeout_xml = ''

        # cache argument
        if not isinstance(cache, (type(None), bool)):
            raise TypeError("cache expected to either be None or a boolean")
        if cache is not None:
            cache_xml = ' cache="{}"'.format('true' if cache else 'false')
        else:
            cache_xml = ''

        # allow_offline argument
        if not isinstance(allow_offline, (type(None), bool)):
            raise TypeError("allow_offline is expected to be either None or a boolean")
        if allow_offline is not None:
            allow_offline_xml = ' allowOffline="{}"'.format('true' if allow_offline else 'false')
        else:
            allow_offline_xml = ''

        # wait_for_reconnect argument
        if not isinstance(wait_for_reconnect, (type(None), bool)):
            raise TypeError("wait_for_reconnect expected to be either None or a boolean")
        if wait_for_reconnect is not None:
            wait_for_reconnect_xml = ' waitForReconnect="{}"'.format('true' if wait_for_reconnect else 'false')
        else:
            wait_for_reconnect_xml = ''

        full_request = SCI_TEMPLATE.format(
            operation=operation,
            targets=targets_xml,
            reply=reply_xml,
            synchronous=synchronous_xml,
            sync_timeout=sync_timeout_xml,
            cache=cache_xml,
            allow_offline=allow_offline_xml,
            wait_for_reconnect=wait_for_reconnect_xml,
            payload=payload
        )

        # TODO: do parsing here?
        return self._conn.post("/ws/sci", full_request)
