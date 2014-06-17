from junos_space import space
from junos_space.tag_management import tags
import logging

if __name__ == "__main__":
    # Initialize logging
    logging.config.fileConfig('./junos_space/logging.conf')

    # Create a Space REST end point
    url = 'https://10.204.79.100'
    user = 'super'
    passwd = '123juniper'
    my_space = space.Space(url, user, passwd)

    print "Hello"
    tags_list = my_space.tag_management.tags.get(get_filter={'name' : 'NewTag'})
    for t in tags_list:
        print "Getting details of ", t
        tag_details = t.get()
        print tag_details
        print "Getting targets for ", t
        try:
            for tgt in t.targets.get():
                print tgt
                tgt.delete()
                print "Removed target ", tgt
                tgt = t.targets.post(tgt)
                print "Added target back ", tgt
        except:
            print "Failed to test targets"

        if (t.name.startswith("NewTag")):
            t.delete()

    new_tag = my_space.tag_management.tags.post(
                    tags.Tag(attrs_dict={'name': 'NewTag', 'type': 'private'})
                )

    print "Created ", new_tag

    new_tag.put(tags.Tag(attrs_dict={'name': 'ChangedName', 'type': 'public'}))

    print "Changed Tag is ", new_tag

    new_tag.delete()

    print "Deleted ", new_tag

    devices_list = my_space.device_management.devices.get()
    for d in devices_list:
        print "Getting details of ", d
        print d.get()

    new_tag = my_space.tag_management.tags.post(
                    tags.Tag(my_space,
                             attrs_dict={'name': 'NewTag', 'type': 'private'})
                )

    print "Created ", new_tag, " again..."

    new_tag.targets.post([
                tags.TagTarget(attrs_dict={'href': devices_list[0].href}),
                tags.TagTarget(attrs_dict={'href': devices_list[1].href})
            ])

    print "Assigned targets..."
    for tgt in new_tag.targets.get():
        print tgt
