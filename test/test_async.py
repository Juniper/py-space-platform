import logging.config
import ConfigParser

from jnpr.space.platform.core import rest, async

class TestAsync:

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

    def test_create_only(self):
        tm = async.TaskMonitor(self.space, 'testq')
        assert tm is not None
        assert tm._hornetq_location == 'http://localhost:8080/api/hornet-q/queues/jms.queue.testq'

    def test_create_delete(self):
        tm = async.TaskMonitor(self.space, 'testqq')
        assert tm is not None
        assert tm._hornetq_location == 'http://localhost:8080/api/hornet-q/queues/jms.queue.testqq'
        tm.delete()

    def test_pull_msg(self):
        tm = async.TaskMonitor(self.space, 'testqqq', wait_time=2)
        msg = tm.pull_message()
        assert msg is None
        tm.delete()

    def test_wait_for_task(self):
        tm = async.TaskMonitor(self.space, 'testqqqq', wait_time=1, max_retries=10)
        err = None
        task_id = 100

        try:
            tm.wait_for_task(task_id)
        except Exception as e:
            err = e.message
            pass

        assert err == "Task %s does not seem to be progressing" % task_id
        tm.delete()