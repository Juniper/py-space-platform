from junos_space import space
from junos_space.tag_management import tags
import logging

from lxml import etree

if __name__ == "__main__":
    # Initialize logging
    logging.config.fileConfig('./junos_space/logging.conf')

    # Create a Space REST end point
    url = 'https://10.204.79.100'
    user = 'super'
    passwd = '123juniper'
    my_space = space.Space(url, user, passwd)

    print "Hello"
    tags_list = my_space.tag_management.tags.get()
    for t in tags_list:
        print "Getting details of", etree.tostring(t._data)
        tag_details = t.get()
        print tag_details
        print "Targets are: ", t.targets
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
