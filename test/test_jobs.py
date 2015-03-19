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
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest

class TestJobs(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_get_first_2_jobs(self):
        jobs_list = self.space.job_management.jobs.get(
                        paging={'start': 0, 'limit': 2})
        print(len(jobs_list))
        assert len(jobs_list) == 2, "Not enough jobs on Space"

    def test_get_next_2_jobs(self):
        jobs_list = self.space.job_management.jobs.get(
                        paging={'start': 2, 'limit': 2})
        print(len(jobs_list))
        assert len(jobs_list) == 2, "Not enough jobs on Space"

    def test_get_2_jobs(self):
        jobs_list = self.space.job_management.jobs.get(
                        paging={'limit': 2})
        print(len(jobs_list))
        assert len(jobs_list) == 2, "Not enough jobs on Space"

    def test_get_1_DONE_job(self):
        jobs_list = self.space.job_management.jobs.get(
                        filter_={'job-state': 'DONE'},
                        paging={'limit': 1})
        print(len(jobs_list))
        assert len(jobs_list) == 1, "Not enough DONE jobs on Space"

    def test_get_all_DD_job(self):
        jobs_list = self.space.job_management.jobs.get(
                        filter_={'job-type': 'Discover Network Elements'})
        print(len(jobs_list))
        assert len(jobs_list) > 1, "Not enough DD jobs on Space"

    def test_get_progress_update(self):
        jobs_list = self.space.job_management.jobs.get(
                        filter_={'job-state': 'DONE'},
                        paging={'limit': 1})
        print(len(jobs_list))
        assert len(jobs_list) == 1, "Not enough DONE jobs on Space"

        pu = jobs_list[0].progress_update.get()
        summary = pu['data']
        print(pu.state, pu.status, pu.percentage, summary)

    def test_cancel_job(self):
        jobs_list = self.space.job_management.jobs.get(
                        filter_={'job-state': 'DONE'},
                        paging={'limit': 1})
        print(len(jobs_list))
        assert len(jobs_list) == 1, "Not enough DONE jobs on Space"

        import pytest
        with pytest.raises(rest.RestException) as exc:
            jobs_list[0].cancel.post()

        assert exc.value.response.status_code == 412
