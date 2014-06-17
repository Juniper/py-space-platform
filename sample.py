import junos_space
from junos_space import space, devices, tags, jobs, task_monitor
import sys
import optparse
from optparse import OptionParser
import ConfigParser
import logging
     
def main():

    # Initialize logging
    logging.config.fileConfig('./logging.conf')

    # Extract Space URL, userid, password from config file 
    config = ConfigParser.RawConfigParser()
    config.read("./test.conf")
    url = config.get('space', 'url')
    user = config.get('space', 'user')
    passwd = config.get('space', 'passwd')

    # Extract cmd line args and options
    (options, args) = process_cmd_line()
        
    # Create a Space REST end point
    my_space = space.Space(url, user, passwd)

    tags_list = my_space.tag_management.tags.get(filter=dict([('name', options.tag_name), ('type', 'public')]))
    if (len(tags_list) == 0):
        print "There are no public tags with the name %s" % options.tag_name
        sys.exit(1)

    devices_list = my_space.device_management.devices.get(filter=dict([('TAG', options.tag_name)]))
    if (len(devices_list) == 0):
        print "There are no devices with the tag %s" % options.tag_name
        sys.exit(1)
        
    monitor = task_monitor.TaskMonitor(spc, "execCommandQ")
    try:
        monitor.create_q()
        monitor.create_pull_consumer()
        task_ids = []
        for device in devices_list:
            print "Initiaing execution of \"%s\" on device %s..." % (args[0], d.name)

            rpc_name = "<command>" + args[0] + "</command>"
            task_id = device.rpc.post(rpc_name, queue=monitor.hornetq_location)
            print "\tCreated task %s for device %s" % (task_id, device.name)
            task_ids.append(task_id)

        print "Waiting for %d tasks to complete..." % len(task_ids)
        tasks = monitor.wait_for_tasks(task_ids)
        for t in tasks:
            print "\t", t

    except Exception as e:
        print e
    finally:
        print "Done"
        monitor.cleanup()

def process_cmd_line():
    """Parse command line args and options"""
    parser = OptionParser()
    parser.add_option("-t", "--tag", dest="tag_name", default=None,
                    help="Tag on the devices to be deployed with this template.")
    
    (options, args) = parser.parse_args()
    
    if ((options.tag_name == None) or
        len(args) == 0):
        parser.print_help()
        sys.exit(1)

    return (options, args)

if __name__ == "__main__":
    main()
