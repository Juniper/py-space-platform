import time

from jnpr.space import xmlutil

class TaskMonitor:
    """Encapsulates the logic required to monitor the progress of tasks"""

    def __init__(self, rest_end_point, qname, wait_time=10, max_retries=18):
        self._rest_end_point = rest_end_point
        self.qname = qname
        self.wait_time = wait_time
        self.max_retries = max_retries
        self._create_q()
        self._create_pull_consumer()

    def get_queue_url(self):
        return self._hornetq_location

    def _create_q(self):
        """Create a new hornet-q for this task monitor"""

        headers = {
            "content-type": "application/hornetq.jms.queue+xml",
        }
        url = "/api/hornet-q/queues"
        body = """<queue name="%s"><durable>false</durable></queue>""" % self.qname
        response = self._rest_end_point.post(url, headers, body)
        if ((response.status_code == 201) or (response.status_code == 412)):
            self._hornetq_location = "http://localhost:8080/api/hornet-q/queues/jms.queue." + self.qname
        else:
            print response.status_code
            raise Exception(response.text)

    def _create_pull_consumer(self):
        """Create a new pull message consumer"""

        url = "/api/hornet-q/queues/jms.queue." + self.qname
        self._rest_end_point.head(url)

        url = url + "/pull-consumers"
        response = self._rest_end_point.post(url, headers={}, body=None)
        if (response.status_code == 201):
            self.next_msg_url = self._strip_uri(response.headers["msg-consume-next"])
        else:
            raise Exception("Failed to create message consumer")

    def _strip_uri(self, url):
        start = url.find("/api")
        return url[start:]

    def pull_message(self):
        """Try to pull the next message from the queue"""

        headers = {"accept-wait": self.wait_time}
        response = self._rest_end_point.post(self.next_msg_url, headers, body=None)
        next_msg = response.headers["msg-consume-next"]
        if next_msg:
            self.next_msg_url = self._strip_uri(next_msg)

        if response.status_code == 200:
            #xml = xmlutil.cleanup(response.text)
            xml = response.text
            return xmlutil.xml2obj(xml)

    def wait_for_task(self, task_id):
        """Get progress updates till the given task completes"""

        num_consecutive_attempts = 0
        while num_consecutive_attempts < self.max_retries:
            pu = self.pull_message()
            if not pu:
                num_consecutive_attempts += 1
                time.sleep(self.wait_time)
                continue
            else:
                num_consecutive_attempts = 0

            if task_id != pu.taskId:
                continue

            if self._task_is_done(pu):
                return pu

        raise Exception("Task %s does not seem to be progressing" % task_id)

    def wait_for_tasks(self, task_id_list):
        """Wait till all tasks in the given list completes"""

        num_consecutive_attempts = 0
        task_results = []

        while len(task_results) < len(task_id_list):
            pu = self.pull_message()
            if not pu:
                num_consecutive_attempts += 1
                if num_consecutive_attempts > self.max_retries:
                    break

                time.sleep(self.wait_time)
                continue
            else:
                num_consecutive_attempts = 0

            if pu.taskId in task_id_list:
                if self._task_is_done(pu):
                    task_results.append(pu)

        return task_results

    def _task_is_done(self, pu):
        if pu.state == "DONE":
            return True

        if pu.subTask is not None:
            for s in pu.subTask:
                if s.state != "DONE":
                    return False

            return True

        return False

    def delete(self):
        """Cleanup by deleting the hornetq"""

        url = "/api/hornet-q/queues/jms.queue." + self.qname
        response = self._rest_end_point.delete(url)
        if (response.status_code != 204):
            raise Exception("Failed to delete hornetq")