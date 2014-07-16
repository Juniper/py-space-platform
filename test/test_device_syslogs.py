import logging.config
import ConfigParser
import pytest
import time

from jnpr.space import rest
from jnpr.space import async

_task_id = 0

@pytest.fixture
def task_id():
    global _task_id
    return _task_id

class TestDeviceSyslogs:

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

    def test_get_syslog_events(self):
        tm = async.TaskMonitor(self.space, 'test_SYSLOG_q')
        devices_list = self.space.device_management.devices.get(
                            filter_={'managedStatus': 'In Sync'})
        assert len(devices_list) > 0, "Not enough devices on Space"

        try:
            result = self.space.device_management.devices.get_syslog_events.post(
                        task_monitor=tm,
                        devices=devices_list,
                        text_patterns=['roshan', 'joyce'])

            from pprint import pprint
            pprint(result)

            assert result.id > 0, "Device Get Syslog Events execution Failed"

            global _task_id
            _task_id = result.id

        finally:
            tm.delete()

    def test_stop_syslog_events(self, task_id):
        my_task_id = task_id
        print my_task_id
        assert my_task_id > 0

        time.sleep(30)

        result = self.space.device_management.devices.stop_syslog_events.post(
                    id = my_task_id)
        from pprint import pprint
        pprint(result)
