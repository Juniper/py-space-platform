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

from jnpr.space import rest

def main(spc):
    """
    Gets all Roles from Space. For each, it gets details and prints the
    name of the role and all tasks that are part of that role.
    """
    roles_list = spc.user_management.roles.get()
    for role in roles_list:
        print("\n%s" % role.title)
        tasks = role.tasks.get()
        for t in tasks:
            task_detail = t.get()
            print("\t%s (%s)" % (task_detail.title, task_detail.name))

if __name__ == '__main__':
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