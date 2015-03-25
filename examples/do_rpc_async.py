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
import logging.config
import configparser

from jnpr.space import rest, async

def main(my_space):
    """
    Gets all connected Junos devices from Space. Then invokes the
    <get-commit-information> RPC on all of them asynchronously and waits for
    all those tasks to complete. Then it prints the results from each RPC.
    """
    devices = my_space.device_management.devices.\
              get(filter_={'deviceFamily': 'junos',
                            'connectionStatus': 'up'})

    tm = async.TaskMonitor(my_space, 'test_rpc_q')
    try:
        task_ids = []
        for d in devices:
            print(d.name, d.ipAddr, d.platform)
            result = d.exec_rpc_async.post(
                                           task_monitor=tm,
                                           rpcCommand="<get-commit-information/>"
                                           )

            assert result.id > 0, "Async RPC execution Failed"
            task_ids.append(result.id)

        # Wait for all tasks to complete
        pu_list = tm.wait_for_tasks(task_ids)
        for pu in pu_list:
            assert (pu.state == "DONE" and pu.status == "SUCCESS" and
                    str(pu.percentage) == "100.0")

            # Print the RPC result for each
            print(pu.data)
    finally:
        tm.delete()

if __name__ == "__main__":
    # Initialize logging
    logging.config.fileConfig('../test/logging.conf')

    # Extract Space URL, userid, password from config file
    config = configparser.RawConfigParser()
    config.read("../test/test.conf")
    url = config.get('space', 'url')
    user = config.get('space', 'user')
    passwd = config.get('space', 'passwd')

    # Create a Space REST end point
    space = rest.Space(url, user, passwd)
    main(space)