'''
Created on 20-Jun-2014

@author: rjoyce
'''
from jnpr.space.platform.core import rest, resource

import logging.config

if __name__ == "__main__":
    # Initialize logging
    logging.config.fileConfig('./logging.conf')

    # Create a Space REST end point
    my_space = rest.Space(url='https://10.204.79.100',
                           user='super', passwd='123Juniper')

    try:
        # Create a new public tag named 'Bangalore'
        new_tag = resource.Resource('tag_management.tag', my_space)
        new_tag.name = 'Bangalore11'
        new_tag.type = 'public'
        new_tag = my_space.tag_management.tags.post(new_tag)

        # Get all devices from Space matching a filter
        filter_str = "name contains 'jtme-'"
        devices_list = my_space.device_management.devices.get(filter_=filter_str)
        for d in devices_list:
            new_tag.targets.post(resource.Resource(
                                                   'tag_management.target',
                                                   my_space,
                                                   attributes={'href': d.href}
                                                   )
                                 )

    finally:
        print "Completed working with ", new_tag
        new_tag.delete()
