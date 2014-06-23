'''
Created on 20-Jun-2014

@author: rjoyce
'''
from jnpr.space.platform.core import rest
from jnpr.space.platform.tag_management import tags

import logging.config

if __name__ == "__main__":
    # Initialize logging
    logging.config.fileConfig('./junos_space/logging.conf')

    # Create a Space REST end point
    my_space = rest.Space(url='https://10.204.79.100',
                           user='super', passwd='123Juniper')

    try:
        # Create a new public tag named 'Bangalore'
        new_tag = tags.Tag(my_space)
        new_tag.name = 'Bangalore11'
        new_tag.type = 'public'
        new_tag = my_space.tag_management.tags.post(new_tag)

        # Get all devices from Space matching a filter
        filter_str = "name contains '-BLR-'"
        devices_list = my_space.device_management.devices.get(filter_=filter_str)
        for d in devices_list:
            new_tag.targets.post(tags.Target(attrs_dict={'href': d.href}))

    finally:
        print "Completed working with ", new_tag
        new_tag.delete()
