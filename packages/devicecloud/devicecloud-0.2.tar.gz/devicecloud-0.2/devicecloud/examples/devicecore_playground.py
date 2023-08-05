# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2014 Etherios, Inc. All rights reserved.
# Etherios, Inc. is a Division of Digi International.
from getpass import getpass

from devicecloud import DeviceCloud
from devicecloud.devicecore import dev_mac, group_path


def get_authenticated_dc():
    while True:
        user = raw_input("username: ")
        password = getpass("password: ")
        dc = DeviceCloud(user, password,
                         base_url="https://login.etherios.com")
        if dc.has_valid_credentials():
            print ("Credentials accepted!")
            return dc
        else:
            print ("Invalid username or password provided, try again")


def show_group_tree(dc):
    stats = {}  # group -> devices count including children
    def count_nodes(group):
        count_for_this_node = \
            len(list(dc.devicecore.get_devices(group_path == group.get_path())))
        subnode_count = 0
        for child in group.get_children():
            subnode_count += count_nodes(child)
        total = count_for_this_node + subnode_count
        stats[group] = total
        return total
    count_nodes(dc.devicecore.get_group_tree_root())
    print(stats)
    dc.devicecore.get_group_tree_root().print_subtree()


if __name__ == '__main__':
    dc = get_authenticated_dc()
    devices = dc.devicecore.get_devices(
        (dev_mac == '00:40:9D:50:B0:EA')
    )
    for dev in devices:
        print(dev)

    show_group_tree(dc)
