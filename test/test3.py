from __future__ import print_function
import logging.config
import traceback

from jnpr.space import rest as rest
from jnpr.space import resource as resource

if __name__ == "__main__":
    # Initialize logging
    logging.config.fileConfig('./logging.conf')

    # Create a Space REST end point
    url = 'https://10.155.67.76'
    user = 'super'
    passwd = '123juniper'
    my_space = rest.Space(url, user, passwd)

    print("Hello")
    try:
        tags_list = my_space.tag_management.tags.get()
        for t in tags_list:
            print("Getting details of <%s, %s>" % (t.name, t.type))
            tag_details = t.get()
            print(tag_details)
            print("Getting targets for <%s, %s>" % (t.name, t.type))
            try:
                for tgt in t.targets.get():
                    print(tgt)
                    tgt_copy = resource.Resource(type_name='tag_management.target',
                                                 rest_end_point=my_space,
                                                 attributes={'href': tgt.href}
                                                 )

                    tgt.delete()
                    print("Removed target ", tgt.uri)

                    tgt = t.targets.post(tgt_copy)
                    print("Added target back ", tgt.uri)
            except Exception as e:
                traceback.print_exc()
                print(e, "Failed to test targets")

            if (t.name.startswith("NewTag")):
                t.delete()
    except Exception as e:
        traceback.print_exc()
        print("Failed to get tags and operate on their targets")

    new_tag = resource.Resource(type_name='tag_management.tag',
                                rest_end_point=my_space)
    new_tag.name = 'NewTag'
    new_tag.type = 'private'
    new_tag = my_space.tag_management.tags.post(new_tag)

    print("Created <%s, %s>" % (new_tag.name, new_tag.type))

    new_tag.name = 'ChangedName'
    new_tag.type = 'public'
    new_tag.put()

    print("Changed Tag is <%s, %s>" % (new_tag.name, new_tag.type))

    new_tag.delete()

    print("Deleted <%s, %s>" % (new_tag.name, new_tag.type))
