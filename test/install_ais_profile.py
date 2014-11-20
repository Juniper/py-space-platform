'''
Created on 14-Nov-2014

@author: rjoyce
'''

import signal
import logging.config
import ConfigParser
import argparse
import getpass
import time
import re
import csv

from jnpr.space import rest, async, factory

INTERRUPTED = False

def wait_for_jobs(spc, tasks):
    done_jobs = {}
    while len(done_jobs) < len(tasks):
        print "Waiting for %d jobs to complete..." % (len(tasks) - len(done_jobs))
        time.sleep(60)
        for device_name in tasks.keys():
            task = tasks[device_name]
            if task.id not in done_jobs.keys():
                job = factory.fetch_resource(spc, task.get('href'))
                print job.name, job['job-state']
                if job['job-state'] == "DONE":
                    done_jobs[task.id] = job

    return done_jobs

def install_on_each_batch(spc, event_profile, batch, outfilename):
    tm = async.TaskMonitor(spc, 'test_ais_q')

    try:
        tasks = {}
        for device in batch:
            task = event_profile.installEventProfile.post(task_monitor=tm,
                                                   devices=[device])
            tasks[device.hostName] = task
            print "Created task %d for device %s" % (task.id, device.hostName)

        jobs = wait_for_jobs(spc, tasks)

        with open(outfilename, "a+") as outfile:
            for device_name in tasks.keys():
                job = jobs[tasks[device_name].id]
                outfile.write("%s, %s, %s, %s, %s\r\n" %
                              (device_name,
                               job.name,
                               job['start-time'],
                               job['end-time'],
                               job['job-status']
                              )
                             )
    finally:
        tm.delete()

def install(spc, event_profile, target_devices, batch_size, outfile):
    N = batch_size
    batches = [target_devices[i:i+N] for i in xrange(0, len(target_devices), N)]
    for batch in batches:
        if INTERRUPTED:
            print "Exiting due to interrupt..."
            return
        install_on_each_batch(spc, event_profile, batch, outfile)

def get_event_profile(spc, config):
    ep_name = config.get('ais', 'event_profile_name')
    if ep_name is None:
        raise Exception("Config file should specify 'event_profile_name' under [ais]")

    eps = spc.servicenow.event_profile_management.eventProfiles.get(
                    filter_ = {'profileName': ep_name})
    if len(eps) == 0:
        raise Exception('No AIS event profile with the given name!')

    return eps[0]

def get_target_devices(spc, config):
    target_devices_map = {}
    ais_version_regex = None

    if config.has_option('target_devices', 'csv_file'):
        if config.has_option('target_devices', 'ais_version_regex'):
            raise Exception("Config file should specify only one of 'csv_file' or 'ais_version_regex' under [target_devices]")
        target_devices_csv = config.get('target_devices', 'csv_file')
        with open(target_devices_csv, "r") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                for col in row:
                    target_devices_map[col] = col
    else:
        if config.has_option('target_devices', 'ais_version_regex'):
            ais_version_regex = config.get('target_devices', 'ais_version_regex')
        else:
            raise Exception("Config file should specify one of 'csv_file' or 'ais_version_regex' under [target_devices]")

    pg_start = 0
    pg_size = config.getint('target_devices', 'page_size')

    target_devices = []
    while True:
        devices = spc.servicenow.device_management.devices.get(
                                                               paging={
                                                                       'start': pg_start,
                                                                       'limit': pg_size
                                                                      }
                                                               )
        for d in devices:
            try:
                if ais_version_regex:
                    if re.match(ais_version_regex, d.scriptBundle.text):
                        target_devices.append(d)
                else:
                    if target_devices_map.has_key(d.hostName):
                        target_devices.append(d)
            except AttributeError:
                target_devices.append(d)

        if len(devices) < pg_size:
            break
        else:
            pg_start = pg_start + pg_size

    return target_devices

def signal_handler(signal, frame):
    print('Processing interrupt. Will exit after the current batch of jobs complete!')
    global INTERRUPTED
    INTERRUPTED = True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf", required=True, help="Full pathname of the config file")
    args = parser.parse_args()

    logging.config.fileConfig(args.conf)

    # Extract parameters from config file
    config = ConfigParser.RawConfigParser()
    config.read(args.conf)
    url = config.get('space', 'url')
    user = config.get('space', 'user')
    if config.has_option('space', 'passwd'):
        passwd = config.get('space', 'passwd')
    else:
        passwd = getpass.getpass()

    outfile = config.get('output', 'file_name')
    if outfile is None:
        raise Exception("Config file should specify one of 'file_name' under [output]")

    with open(outfile, "w") as out:
        out.write("#Device Name, Job Name, Start Day, Start Time, End Day, End Time, Job Status\r\n")

    spc = rest.Space(url, user, passwd, use_session=True)

    ep = get_event_profile(spc, config)
    target_devices = get_target_devices(spc, config)
    if len(target_devices) == 0:
        raise Exception("No target devices selected for installation!")

    batch_size = config.getint('target_devices', 'batch_size')

    try:
        signal.signal(signal.SIGINT, signal_handler)
        install(spc, ep, target_devices, batch_size, outfile)
    except Exception as e:
        print e