import space
import jobs
import xml.etree.ElementTree as ET
import time

class ProgressUpdate:
    """Encapsulates a progress update message for a task"""
    def __init__(self, text):
        root = ET.fromstring(text)
        self.task_id = root.find("taskId").text
        self.state = root.find("state").text
        self.status = root.find("status").text
        self.percentage = root.find("percentage").text

    def __str__(self):
        return "ProgressUpdate{task=%s, state=%s, status=%s, percentage=%s}" % \
          (self.task_id, self.state, self.status, self.percentage)

class TaskMonitor:
    """Encapsulates the logic required to monitor the progress of tasks"""
    def __init__(self, spc, qname, wait_time=10, max_retries=18):
        self.spc = spc
        self.qname = qname
        self.wait_time = wait_time
        self.max_retries = max_retries

    def create_q(self):
        """Create a new hornet-q for this task monitor"""
        headers = {
            "content-type": "application/hornetq.jms.queue+xml",
        }
        url = "/api/hornet-q/queues"
        body = """<queue name="%s"><durable>false</durable></queue>""" % self.qname
        response = self.spc.post(url, headers, body)
        if ((response.status_code == 201) or (response.status_code == 412)):
            self.hornetq_location = "http://localhost:8080/api/hornet-q/queues/jms.queue." + self.qname
        else:
            print response.status_code
            raise Exception(response.text)

    def create_pull_consumer(self):
        """Create a new pull message consumer"""
        url = "/api/hornet-q/queues/jms.queue." + self.qname + "/pull-consumers"
        response = self.spc.post(url, headers={}, body=None)
        if (response.status_code == 201):
            self.next_msg_url = self.transform(response.headers["msg-consume-next"])
        else:
            raise Exception("Failed to create message consumer")

    def transform(self, url):
        start = url.find("/api")
        return url[start:]
    
    def pull_message(self):
        """Try to pull the next message from the queue"""
        headers = {"accept-wait": self.wait_time}
        response = self.spc.post(self.next_msg_url, headers, body=None)
        next = response.headers["msg-consume-next"]
        if (next):
            self.next_msg_url = self.transform(next)
            
        if (response.status_code == 200):
            return ProgressUpdate(response.text)

    def wait_for_task(self, task_id):
        """Get progress updates till the given task completes"""
        num_consecutive_attempts = 0
        while (num_consecutive_attempts < self.max_retries):
            pu = self.pull_message()
            if (not pu):
                print "No progress updates in %d seconds" % self.wait_time
                num_consecutive_attempts += 1
                time.sleep(self.wait_time)
                continue
            
            if (task_id != pu.task_id):
                continue

            #print "Got: ", pu
            if (pu.state == "DONE"):
                return pu
            
        raise Exception("Task %s does not seem to be progressing" % task_id)

    def wait_for_tasks(self, task_id_list, job_mgr):
        """Wait till all tasks in the given list completes"""
        num_consecutive_attempts = 0
        job_ids_to_fetch = task_id_list[:]
        jobs_to_return = []
        while (num_consecutive_attempts < self.max_retries):
            jobs_list = job_mgr.get_jobs(job_ids_to_fetch)
            for j in jobs_list:
                if (j.state == "DONE"):
                    job_ids_to_fetch.remove(j.id)
                    jobs_to_return.append(j)

            if (len(jobs_to_return) < len(task_id_list)):
                time.sleep(self.wait_time)
                continue
            else:
                return jobs_to_return

        raise Exception("Jobs do not seem to complete")
        
    def cleanup(self):
        """Cleanup by deleting the hornetq"""
        url = "/api/hornet-q/queues/jms.queue." + self.qname
        response = self.spc.delete(url)
        if (response.status_code != 204):
            raise Exception("Failed to delete hornetq")
        
if __name__ == "__main__":
    pu = ProgressUpdate("""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <progress-update xsi:type="parallel-progress" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
             <taskId>2621452</taskId>
             <state>INPROGRESS</state>
             <status>UNDETERMINED</status>
             <percentage>50.0</percentage>
             <subTask xsi:type="percentage-complete">
              <state>DONE</state>
               <status>SUCCESS</status>
              <percentage>75.0</percentage>
             </subTask>
            </progress-update>""")

    print pu.task_id, pu.state, pu.status, pu.percentage
    
    spc = space.Space()
    tm = TaskMonitor(spc, "testq", 2, 10)
    tm.create_q()

    print tm.hornetq_location

    tm.create_pull_consumer()
    print tm.next_msg_url

    print "Waiting for task 111 to complete..."
    try:
        tm.wait_for_task("111")
    except Exception as e:
        print e
    
    tm.cleanup()

    print "Cleaned up"
