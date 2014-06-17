import json
from .. import space

from pprint import pprint

class Tag(space.Resource):
    """Represents a Tag object"""

    def __init__(self, rest_end_point=None, tag_xml=None, attrs_dict=None):
        super(Tag, self).__init__(rest_end_point, tag_xml, attrs_dict)
        self._service_url = TagManager.service_url
        self._collection_name = "tags"
        self._xml_name = "tag"
        self._media_type = "application/vnd.net.juniper.space.tag-management.tag+xml;version=1;charset=UTF-8"

    def __str__(self):
        s = "Tag <name='%s', type=%s>" % (self.name, self.type)
        return s

class TagCollection(space.Collection):
    """Represents a collection of Tags"""

    def __init__(self, rest_end_point):
        super(TagCollection, self).__init__(rest_end_point, 'tags', '/api/space/tag-management/tags')

    def _create_resource(self, xml_data):
        return Tag(self._rest_end_point, xml_data)


class TagManager(space.Service):
    """Encapsulates tag-management service"""

    service_name = "tag_management"
    service_url = "/api/space/tag-management"

    def __init__(self, rest_end_point):
        super(TagManager, self).__init__(rest_end_point)
        self._collections['tags'] = TagCollection(rest_end_point)
