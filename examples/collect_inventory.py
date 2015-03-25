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
from __future__ import print_function
import sys
import logging.config
import argparse
import concurrent.futures
import threading
import time
from jnpr.space import rest, factory

remaining = 0
lock = threading.Lock()

def main(args):
    """
    Handles various command line args and call collect_inv() function.
    """
    if args.pem is not None:
        if args.session:
            print("Simulating inventory collection with session-based API access...")
            spc1 = rest.Space(args.space_URL,
                              cert=(args.pem, args.key),
                              use_session=True,
                              profile_file='/tmp/api-responses-session.csv')
            collect_inv(spc1, args.threads)
            spc1.logout()
        else:
            print("Simulating inventory collection with non-session-based API access...")
            spc2 = rest.Space(args.space_URL,
                              cert=(args.pem, args.key),
                              use_session=False,
                              profile_file='/tmp/api-responses.csv')
            collect_inv(spc2, args.threads)
    else:
        if args.session:
            print("Simulating inventory collection with session-based API access...")
            spc1 = rest.Space(args.space_URL,
                              args.user, args.passwd,
                              use_session=True,
                              profile_file='/tmp/api-responses-session.csv')
            collect_inv(spc1, args.threads)
            spc1.logout()
        else:
            print("Simulating inventory collection with non-session-based API access...")
            spc2 = rest.Space(args.space_URL,
                              args.user, args.passwd,
                              use_session=False,
                              profile_file='/tmp/api-responses.csv')
            collect_inv(spc2, args.threads)

def collect_inv(spc, num_threads):
    """
    Get first 200 devices from Space and use a ThreadPoolExecutor to
    collect their inventory.
    """
    global remaining
    devices = spc.device_management.devices.get(
                            filter_={'managedStatus': 'In Sync'},
                            paging={'start': 0, 'limit': 200},
                            sortby=['name', 'platform'])

    print("There are %d devices to process" % len(devices))
    remaining = len(devices)

    with concurrent.futures.ThreadPoolExecutor(max_workers=int(num_threads)) as executor:
        for device in devices:
            f = executor.submit(process_device, spc, device)
            f.add_done_callback(finished)

    print("\nAll Over!!!")

def process_device(spc, device):
    """
    Process inventory collection for a given device.
    """
    try:
        d = device.get();
        print("Processing device: ", device.name)
        me_href = d['managed-elements']['managed-element'].get('href')
        me = factory.fetch_resource(spc, me_href)

        # Fetch Physical Termination Points
        ptps = me.ptps.get()
        for p in ptps:
            p.get()

        # Fetch equipment inventory
        ehs = me.equipment_holders.get()
        for eh in ehs:
            eh.get()

        # Fetch software inventory
        me.software_identities.get()

        # Fetch relevant configuration
        try:
            device.configurations.expanded.post(xpaths=[
                    '/configuration/version',
                    '/configuration/routing-instances',
                    '/configuration/access/radius-server',
                    '/configuration/system/domain-name',
                    '/configuration/routing-options/router-id',
                    '/configuration/interfaces/interface[name="lo0"]'])
        except:
            pass

        return device.name
    except:
        raise Exception("Failed to process %s due to %s" % (device.name, sys.exc_info()[1]))

def finished(f):
    """
    Callback executed when the inv collection work for a device is completed.
    """
    global remaining, lock
    try:
        device_name = f.result()
        with lock:
            remaining -= 1
            print("Finished processing device: %s; %d remaining" % (device_name, remaining))
    except Exception as e:
        import traceback
        traceback.print_exception(sys.exc_info()[0],
                                  sys.exc_info()[1],
                                  sys.exc_info()[2])
        print(e.message)

if __name__ == '__main__':
    logging.config.fileConfig('../test/logging.conf')
    parser = argparse.ArgumentParser()
    parser.add_argument("space_URL", help="URL of the Space instance")
    parser.add_argument("-u", "--user", help="Userid")
    parser.add_argument("-p", "--passwd", help="Password")
    parser.add_argument("-c", "--pem", help="X.509 certificate PEM file")
    parser.add_argument("-k", "--key", help="X.509 certificate key file")
    parser.add_argument("-s", "--session", help="Use session based calls")
    parser.add_argument("-t", "--threads", default=10, help="Number of threads to use")

    args = parser.parse_args()

    start = time.time()
    main(args)
    end = time.time()

    elapsed = end - start
    print("\nIt took %d seconds to complete!" % elapsed)