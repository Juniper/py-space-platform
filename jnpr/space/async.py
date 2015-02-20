import time

from jnpr.space import xmlutil

class TaskMonitor:
    """
    Encapsulates the logic required to monitor the progress of tasks using
    a hornet-q. An instance of this class acts as a wrapper over a hornet-q.
    When you instantiate this class, it internally creates a hornet-q with
    the given ``qname``. You can then use this ``TaskMonitor`` instance when
    invoking asynchronous APIs using the SpaceEZ library. Each asynchronous API
    invocation will create a new task (a.k.a Job) in Junos Space. You can wait
    for a single task to complete using the ``wait_for_task`` method which
    returns the ``ProgressUpdate`` message for the task with completion state
    and status of the task. If you use the same ``TaskMonitor`` object to
    create multiple tasks, you can wait for the completion of all of them
    using the ``wait_for_tasks`` method which returns a list of
    ``ProgressUpdate`` messages - one for each task.

    The snippet below shows an example where a TaskMonitor is used in creating
    a discover-devices task and waiting for its completion:

        >>> s = rest.Space(url='https://1.1.1.1', user='super', passwd='password')
        >>> devs = s.device_management.devices.get()
        >>> tm = async.TaskMonitor(s, 'test_DD_q')
        >>> result = s.device_management.discover_devices.post(
                task_monitor=tm,
                hostName='test-host-name',
                manageDiscoveredSystemsFlag=True,
                userName='regress', password='MaRtInI')
        >>> pu = tm.wait_for_task(result.id)
        >>> print pu.state, pu.status

    .. note::
        If you use multi-threaded programming, make sure that you **do not**
        share a ``TaskMonitor`` instance across multiple threads. You should
        use separate ``TaskMonitor`` objects for separate threads.
    """

    def __init__(self, rest_end_point, qname,
                 wait_time=10, max_consecutive_attempts=10):
        """Creates an instance of this class to encapsulate a hornet-q.

        :param rest_end_point: An instance of ``rest.Space`` class which
            encapsulates a Junos Space system on which tasks need to be
            monitored.
        :type url: rest.Space
        :param str qname: The name of the underlying hornet-q.
        :param int wait_time: Number of seconds to sleep between trying to pull
            progress-update messages from the hornet-q. This is also used as
            the value of the ``accept-wait`` header when pulling messages from
            the hornet-q. The default value of this argument is 10.
        :param int max_consecutive_attempts: The maximum number of consecutive
            attempts that will be made to pull progress-update messages from
            the hornet-q. This defaults to 10. We will consider the task as
            hanging if we are not able to pull a progress-update message from
            the hornet-q after this many attempts.

        :returns:  An instance of this class encapsulating a hornet-q with the
            given name (``qname``).
        """
        self._rest_end_point = rest_end_point
        self.qname = qname
        self.wait_time = wait_time
        self.max_consecutive_attempts = max_consecutive_attempts
        self._create_q()
        self._create_pull_consumer()

    def get_queue_url(self):
        """
        Returns the full URL for the encapsulated hornet-q
        """
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
        """
        Pull the next message from the hornet-q. It specifies an ``accept-wait``
        header with the value that was given as the ``wait_time`` argument in
        the constructor so that the pull waits for this many seconds on the
        server side waiting for a message.

        :returns:  If a message is pulled, it is parsed into a Python object
            and returned. If no message was pulled, returns ``None``.

        """

        headers = {"accept-wait": self.wait_time}
        response = self._rest_end_point.post(self.next_msg_url, headers, body=None)
        next_msg = response.headers["msg-consume-next"]
        if next_msg:
            self.next_msg_url = self._strip_uri(next_msg)

        if response.status_code == 200:
            #xml = xmlutil.cleanup(response.text)
            xml = response.content
            return xmlutil.xml2obj(xml)

    def wait_for_task(self, task_id):
        """
        Waits for the given task to complete by periodically pulling
        progress-update messages from the hornet-q and checking if the message
        indicates that the task is Done. The time between consecutive pulls
        is the value given as the ``wait_time`` argument in the constructor.
        The maximum number of consecutive pulls is determined by the
        ``max_consecutive_attempts`` argument in the constructor. If we're
        unable to pull a progress-update message from hornet-q after this many
        consecutive attempts, we will consider the task as hanging and this
        method will raise an Exception.

        .. note::
            You should use this method only when you have created one task using
            this TaskMonitor object. If you created multiple tasks, you must
            use the wait_for_tasks() method to wait for their completion.

        :returns:  The progress-update message indicating task completion is
            parsed into a Python object and returned.
        """

        num_consecutive_attempts = 0
        while num_consecutive_attempts < self.max_consecutive_attempts:
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
        """
        Waits for all the tasks in the given list to complete by periodically
        pulling progress-update messages from the hornet-q and checking if the
        message indicates that any of the given tasks is Done. The time between
        consecutive pulls is the value given as the ``wait_time`` argument in
        the constructor.

        The maximum number of consecutive pulls is determined by the
        ``max_consecutive_attempts`` argument in the constructor. If we're
        unable to pull a progress-update message from hornet-q after this many
        consecutive attempts, we will consider the tasks as hanging and this
        method will raise an Exception.

        :returns:  A list of progress-update messages indicating the completion
            state and status of all the given tasks. Each entry in the list is
            a Python object parsed from a progress-update message..
        """

        num_consecutive_attempts = 0
        task_results = []

        while len(task_results) < len(task_id_list):
            pu = self.pull_message()
            if not pu:
                num_consecutive_attempts += 1
                if num_consecutive_attempts > self.max_consecutive_attempts:
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

        try:
            for s in pu.subTask:
                if s.state != "DONE":
                    return False

            return True
        except AttributeError:
            return False

    def delete(self):
        """
        Cleanup by deleting the hornet-q encapsulated by this object.
        """

        url = "/api/hornet-q/queues/jms.queue." + self.qname
        response = self._rest_end_point.delete(url)
        if (response.status_code != 204):
            raise Exception("Failed to delete hornetq")