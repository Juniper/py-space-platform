'''
Created on 8-Oct-2014

@author: rjoyce
'''
import logging.config
import argparse
from jnpr.space import rest

def list_devices_in_all_domains(spc):
    devices_list = spc.device_management.devices.get()
    for device in devices_list:
        print "%s, %s" % (device.domain_name, device.name)

if __name__ == '__main__':
    logging.config.fileConfig('./logging.conf')
    parser = argparse.ArgumentParser()
    parser.add_argument("space_URL", help="URL of the Space instance")
    parser.add_argument("space_user", help="Userid")
    parser.add_argument("space_password", help="Password")
    args = parser.parse_args()

    spc = rest.Space(args.space_URL, args.space_user, args.space_password)
    list_devices_in_all_domains(spc)