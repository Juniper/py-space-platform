import logging.config
import ConfigParser

from jnpr.space.platform.core import rest

class TestJobs:

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

    def test_get_first_2_jobs(self):
        jobs_list = self.space.job_management.jobs.get(
                        paging={'start': 0, 'limit': 2})
        print len(jobs_list)
        assert len(jobs_list) == 2, "Not enough jobs on Space"

    def test_get_next_2_jobs(self):
        jobs_list = self.space.job_management.jobs.get(
                        paging={'start': 2, 'limit': 2})
        print len(jobs_list)
        assert len(jobs_list) == 2, "Not enough jobs on Space"

    def test_get_2_jobs(self):
        jobs_list = self.space.job_management.jobs.get(
                        paging={'limit': 2})
        print len(jobs_list)
        assert len(jobs_list) == 2, "Not enough jobs on Space"

    def test_get_1_DONE_job(self):
        jobs_list = self.space.job_management.jobs.get(
                        filter_={'job-state': 'DONE'},
                        paging={'limit': 1})
        print len(jobs_list)
        assert len(jobs_list) == 1, "Not enough DONE jobs on Space"

    def test_get_all_DD_job(self):
        jobs_list = self.space.job_management.jobs.get(
                        filter_={'job-type': 'Discover Network Elements'})
        print len(jobs_list)
        assert len(jobs_list) > 1, "Not enough DD jobs on Space"

    def test_get_progress_update(self):
        jobs_list = self.space.job_management.jobs.get(
                        filter_={'job-state': 'DONE'},
                        paging={'limit': 1})
        print len(jobs_list)
        assert len(jobs_list) == 1, "Not enough DONE jobs on Space"

        pu = jobs_list[0].progress_update.get()
        summary = pu['data']
        print pu.state, pu.status, pu.percentage, summary

    def test_cancel_job(self):
        jobs_list = self.space.job_management.jobs.get(
                        filter_={'job-state': 'DONE'},
                        paging={'limit': 1})
        print len(jobs_list)
        assert len(jobs_list) == 1, "Not enough DONE jobs on Space"

        import pytest
        with pytest.raises(rest.RestException) as exc:
            jobs_list[0].cancel.post()

        assert exc.value.response.status_code == 412
