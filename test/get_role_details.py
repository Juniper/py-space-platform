'''
Created on 23-Sep-2014

@author: rjoyce
'''
import logging.config
import argparse
from jnpr.space import rest

def print_role_details(spc, role):
    print "\n%s" % role.title
    tasks = role.tasks.get()
    for t in tasks:
        task_detail = t.get()
        print "\t%s (%s)" % (task_detail.title, task_detail.name)

def main(spc, role_name):
    roles_list = spc.user_management.roles.get()
    for role in roles_list:
        if (role_name == 'all') or (role.name == role_name):
            print_role_details(spc, role)

if __name__ == '__main__':
    logging.config.fileConfig('./logging.conf')
    parser = argparse.ArgumentParser()
    parser.add_argument("space_URL", help="URL of the Space instance")
    parser.add_argument("space_user", help="Userid")
    parser.add_argument("space_password", help="Password")
    parser.add_argument("role_name", help="Role Name. Use 'all' to print details of all roles.")
    args = parser.parse_args()

    spc = rest.Space(args.space_URL, args.space_user, args.space_password)
    main(spc, args.role_name)