import logging.config
#import yaml

from jnpr.space.platform.v0.core import rest
from jnpr.space.platform.v0.tag_management import tags

if __name__ == "__main__":
    # Initialize logging
    logging.config.fileConfig('./logging.conf')

    # Create a Space REST end point
    url = 'https://10.204.79.100'
    user = 'super'
    passwd = '123Juniper'
    my_space = rest.Space(url, user, passwd)

    #print yaml.dump(my_space)

    print "Hello"
    try:
        tags_list = my_space.tag_management.tags.get(filter_=
                                                     {'name' : 'NewTag',
                                                      'type' : 'private'})
        for t in tags_list:
            print "Getting details of ", t
            tag_details = t.get()
            print tag_details
            print "Getting targets for ", t
            try:
                for tgt in t.targets.get():
                    print tgt
                    tgt_copy = tags.Target(attrs_dict={'href': tgt.href})

                    tgt.delete()
                    print "Removed target ", tgt

                    tgt = t.targets.post(tgt_copy)
                    print "Added target back ", tgt
            except:
                print "Failed to test targets"

            if (t.name.startswith("NewTag")):
                t.delete()
    except:
        print "Failed to get tags and operate on their targets"

    new_tag = tags.Tag()
    new_tag.name = 'NewTag'
    new_tag.type = 'private'
    new_tag = my_space.tag_management.tags.post(new_tag)

    print "Created ", new_tag

    new_tag.name = 'ChangedName'
    new_tag.type = 'public'
    new_tag.put()

    print "Changed Tag is ", new_tag

    new_tag.delete()

    print "Deleted ", new_tag

    devices_list = my_space.device_management.devices.get()
    for d in devices_list:
        print "Getting details of ", d
        print d.get().hostName

    new_tag = my_space.tag_management.tags.post(
                                                tags.Tag(
                                                    my_space,
                                                    attrs_dict=
                                                        {'name': 'NewTag',
                                                         'type': 'private'}
                                                    )
                                                )

    print "Created ", new_tag, " again..."

    new_tag.targets.post([
                tags.Target(attrs_dict={'href': devices_list[0].href}),
                tags.Target(attrs_dict={'href': devices_list[1].href})
            ])

    print "Assigned targets..."
    for tgt in new_tag.targets.get():
        print tgt
