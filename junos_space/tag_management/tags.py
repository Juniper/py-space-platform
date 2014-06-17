from .. import space

class Tag(space.Resource):
    """Represents a Tag object"""

    def __init__(self, rest_end_point=None, tag_xml=None, attrs_dict=None):
        super(Tag, self).__init__(rest_end_point, tag_xml, attrs_dict)
        self._service_url = TagManager.service_url
        self._collection_name = "tags"
        self._xml_name = "tag"
        self._media_type = "application/vnd.net.juniper.space.tag-management.tag+xml;version=1;charset=UTF-8"
        self._init_targets()

    def _init_targets(self):
        try:
            targets_href = self.get_href() + "/targets"
            self._collections['targets'] = TagTargetCollection(
                                            self._rest_end_point,
                                            targets_href, self)
        except:
            self._collections['targets'] = TagTargetCollection(
                                            self._rest_end_point,
                                            None, self)

    def __str__(self):
        s = "Tag <name='%s', type=%s>" % (self.name, self.type)
        return s

class TagCollection(space.Collection):
    """Represents a collection of Tags"""

    def __init__(self, rest_end_point, parent):
        super(TagCollection, self).__init__(rest_end_point, 'tags', '/api/space/tag-management/tags', parent)
        self._xml_name = "tags"
        self._media_type = "application/vnd.net.juniper.space.tag-management.tags+xml;version=1;charset=UTF-8"

    def _create_resource(self, xml_data):
        return Tag(self._rest_end_point, xml_data)

class TagTarget(space.Resource):
    """Represents a TagTarget object"""

    def __init__(self, rest_end_point=None, xml_data=None, attrs_dict=None):
        super(TagTarget, self).__init__(rest_end_point, xml_data, attrs_dict)
        self._service_url = TagManager.service_url
        self._collection_name = "targets"
        self._xml_name = "target"
        self._media_type = "application/vnd.net.juniper.space.tag-management.target+xml;version=1;charset=UTF-8"

    def __str__(self):
        s = "TagTarget <uri='%s', href='%s', type=%s>" % (self.uri, self.href, self.type)
        return s

    def delete(self):
        response = self._rest_end_point.delete(self.uri)
        if (response.status_code != 204):
            raise Exception(response.text)

class TagTargetCollection(space.Collection):
    """Represents a collection of TagTargets"""

    def __init__(self, rest_end_point, href, parent):
        super(TagTargetCollection, self).__init__(rest_end_point, 'targets', href, parent)
        self._xml_name = "targets"
        self._media_type = "application/vnd.net.juniper.space.tag-management.targets+xml;version=1;charset=UTF-8"

    def _create_resource(self, xml_data):
        return TagTarget(self._rest_end_point, xml_data)

class TagManager(space.Service):
    """Encapsulates tag-management service"""

    service_name = "tag_management"
    service_url = "/api/space/tag-management"

    def __init__(self, rest_end_point):
        super(TagManager, self).__init__(rest_end_point)
        self._collections['tags'] = TagCollection(rest_end_point, self)
