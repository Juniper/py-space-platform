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
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest, async, factory

class TestConfigFiles(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_exec_backup(self):
        dlist = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                              'connectionStatus': 'up'})
        assert len(dlist) > 1, 'Not enough connected junos devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_cfm_q')
        try:
            task = self.space.config_file_management.exec_backup.post(task_monitor=tm,
                                                                      devices=dlist)
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()

    def test_get_config_files(self):
        cflist = self.space.config_file_management.config_files.get()
        assert len(cflist) > 1

    def test_get_config_file_details(self):
        cflist = self.space.config_file_management.config_files.get()
        assert len(cflist) > 1
        for cf in cflist[0:2]:
            detail = cf.get()
            assert cf.id == detail.id

    def test_get_config_file_versions(self):
        cflist = self.space.config_file_management.config_files.get()
        assert len(cflist) > 1
        for cf in cflist[0:2]:
            versions = cf.config_file_versions.get()
            assert len(versions) >= 1

    def test_get_config_file_version_details(self):
        cflist = self.space.config_file_management.config_files.get()
        assert len(cflist) > 1
        for cf in cflist[0:2]:
            versions = cf.config_file_versions.get()
            assert len(versions) >= 1
            for v in versions:
                detail = v.get()
                assert detail.content is not None
                assert detail.configFileSize > 0

    def test_versions_diff(self):
        cflist = self.space.config_file_management.config_files.get()
        assert len(cflist) > 1

        h1 = cflist[0].latest_version.get('href')
        h2 = cflist[1].latest_version.get('href')
        result = self.space.config_file_management.versions_diff.post(href1=h1,
                                                                      href2=h2)
        for d in result.diffs.diff:
            print(d.reason, d.lineNumber)

    def test_exec_restore(self):
        cflist = self.space.config_file_management.config_files.get()
        assert len(cflist) > 1
        lvs = []
        for cf in cflist[0:2]:
            h = cf.latest_version.get('href')
            lv = factory.fetch_resource(self.space, h)
            lvs.append(lv)

        tm = async.TaskMonitor(self.space, 'test_cfm_q')
        try:
            task = self.space.config_file_management.exec_restore.post(task_monitor=tm,
                                                                       restore_type='MERGE',
                                                                       config_file_versions=lvs)
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()
