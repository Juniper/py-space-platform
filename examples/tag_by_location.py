"""
DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER

Copyright (c) 2015 Juniper Networks, Inc.
All rights reserved.

Use is subject to license terms.

Licensed under the Apache License, Version 2.0 (the ?License?); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.
"""
from __future__ import unicode_literals
from __future__ import print_function
import logging.config
import configparser

from jnpr.space import rest, factory

def main(my_space):
    """
    Gets all connected Junos devices from Space. Then gets the snmp/location
    configured on each. If this configuration is present, it creates a public
    tag with this value and assign the tag to the device.
    """
    devices_list = my_space.device_management.devices.\
                   get(filter_={'deviceFamily': 'junos',
                                'connectionStatus': 'up'})
    for d in devices_list:
        print(d.name, d.ipAddr, d.platform)
        c = d.configurations.expanded.post(xpaths=['configuration/snmp/location'])
        try:
            tag_device(my_space, d, c.configuration.location)
        except AttributeError:
            print("Device %s does not have location configured" % d.name)

def tag_device(spc, device, tag_name):
    try:
        # Check if a tag exists already with the given name
        tag = spc.tag_management.tags.get(filter_={'name': tag_name})[0]
    except:
        # Create a new public tag with the given name
        tag = factory.make_resource('tag_management.tag', spc)
        tag.name, tag.type = tag_name, 'public'
        tag = spc.tag_management.tags.post(tag)

    """
    Create a new target for this tag, pointing to the given device.
    In other words, assign this tag to this device
    """
    target = factory.make_resource('tag_management.target', spc)
    target.href = device.href
    tag.targets.post(target)

if __name__ == "__main__":
    # Initialize logging
    logging.config.fileConfig('../test/logging.conf')

    # Extract Space URL, userid, password from config file
    config = configparser.RawConfigParser()
    config.read("../test/test.conf")
    url = config.get('space', 'url')
    user = config.get('space', 'user')
    passwd = config.get('space', 'passwd')

    # Create a Space REST end point
    space = rest.Space(url, user, passwd)
    main(space)
