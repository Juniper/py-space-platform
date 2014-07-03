import logging.config
import ConfigParser

import pytest

from jnpr.space.platform.core import rest, resource

class TestTag:

    def setup_class(self):
        # Initialize logging
        logging.config.fileConfig('./logging.conf')

        # Extract Space URL, userid, password from config file
        config = ConfigParser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)
        try:
            tags_list = self.space.tag_management.tags.get(
                        filter_ = "name starts-with 'ApiTestTag'")
            for t in tags_list:
                t.delete()
        except:
            pass

    def test_create_resource_error_1(self):
        with pytest.raises(Exception):
            resource.Resource(type_name='tag_management-tag',
                                rest_end_point=self.space)

    def test_create_resource_error_2(self):
        with pytest.raises(Exception):
            resource.Resource(type_name='tagg_management.tag',
                                rest_end_point=self.space)

    def test_create_resource_error_3(self):
        with pytest.raises(Exception):
            resource.Resource(type_name='tag_management.tagg',
                                rest_end_point=self.space)

    def test_create_delete_tag(self):
        new_tag = resource.Resource(type_name='tag_management.tag',
                                rest_end_point=self.space)
        new_tag.name = 'ApiTestTag'
        new_tag.type = 'private'
        new_tag = self.space.tag_management.tags.post(new_tag)

        print "Created <%s, %s>" % (new_tag.name, new_tag.type)

        assert new_tag.id > 0, "Tag creation failed"

        new_tag.delete()

    def test_create_10_tags(self):
        types = ['public', 'private']
        for i in range(10):
            new_tag = resource.Resource(type_name='tag_management.tag',
                                rest_end_point=self.space)
            new_tag.name = 'ApiTestTag' + str(i)
            new_tag.type = types[i % 2]
            new_tag = self.space.tag_management.tags.post(new_tag)

        assert i == 9, "Failed to create 10 tags"

    def test_get_all_tags(self):
        tags_list = self.space.tag_management.tags.get()
        for t in tags_list:
            print "Got tag <%s, %s>" % (t.name, t.type)

        assert len(tags_list) > 10, "Failed to get all tags on Space?"

    def test_get_public_tags(self):
        tags_list = self.space.tag_management.tags.get(
                        filter_ = {'type': 'public'})
        for t in tags_list:
            print "Got public tag <%s, %s>" % (t.name, t.type)

        assert len(tags_list) >= 5, "Failed to get all public tags on Space"

    def test_get_private_tags(self):
        tags_list = self.space.tag_management.tags.get(
                        filter_ = {'type': 'private'})
        for t in tags_list:
            print "Got private tag <%s, %s>" % (t.name, t.type)

        assert len(tags_list) >= 5, "Failed to get all private tags on Space"

    def test_assign_tag_on_1_device(self):
        tags_list = self.space.tag_management.tags.get(
                        filter_ = {'name': 'ApiTestTag1'})
        assert tags_list[0].name == 'ApiTestTag1', "No tag ApiTestTag1"

        devices_list = self.space.device_management.devices.get()
        assert len(devices_list) > 0, "Not enough devices on Space"

        my_target = resource.Resource('tag_management.target', self.space)
        my_target.href = devices_list[0].href

        tags_list[0].targets.post(my_target)

        targets_list = tags_list[0].targets.get()
        assert len(targets_list) == 1

    def test_delete_tag_on_1_device(self):
        tags_list = self.space.tag_management.tags.get(
                        filter_ = {'name': 'ApiTestTag1'})
        assert tags_list[0].name == 'ApiTestTag1', "No tag ApiTestTag1"

        targets_list = tags_list[0].targets.get()
        assert len(targets_list) == 1

        targets_list[0].delete()

    def test_assign_tag_on_2_devices(self):
        tags_list = self.space.tag_management.tags.get(
                        filter_ = {'name': 'ApiTestTag2'})
        assert tags_list[0].name == 'ApiTestTag2', "No tag ApiTestTag2"

        devices_list = self.space.device_management.devices.get()
        assert len(devices_list) > 1, "Not enough devices on Space"

        my_targets = [resource.Resource('tag_management.target', self.space),
                      resource.Resource('tag_management.target', self.space)]
        my_targets[0].href = devices_list[0].href
        my_targets[1].href = devices_list[1].href

        tags_list[0].targets.post(my_targets)

        targets_list = tags_list[0].targets.get()
        assert len(targets_list) == len(my_targets)

    def test_delete_tag_on_2_devices(self):
        tags_list = self.space.tag_management.tags.get(
                        filter_ = {'name': 'ApiTestTag2'})
        assert tags_list[0].name == 'ApiTestTag2', "No tag ApiTestTag2"

        targets_list = tags_list[0].targets.get()
        assert len(targets_list) == 2

        targets_list[0].delete()
        targets_list[1].delete()

    def test_delete_10_tags(self):
        tags_list = self.space.tag_management.tags.get(
                        filter_ = "name starts-with 'ApiTestTag'")
        for t in tags_list:
            t.delete()
            print "Deleted tag <%s, %s>" % (t.name, t.type)
