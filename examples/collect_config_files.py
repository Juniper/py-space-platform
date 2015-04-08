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
import os
import errno
import logging.config
import argparse
from jnpr.space import rest

def main(args):
    spc = rest.Space(args.space_URL, args.user, args.passwd)

    try:
        # Create the output directory
        os.makedirs(os.path.abspath(args.out))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    collect_config_files(spc, args.out)

def collect_config_files(spc, output_dir):
    """
    Get all device config files from Space in batches of 500 each.
    Then collect all versions of each file.
    """
    start = 0
    config_files = []
    while True:
        page = spc.config_file_management.config_files.get(
                                paging={'start': start, 'limit': 500})
        config_files.extend(page)
        start += len(page)
        if len(page) < 500:
            break

    print("There are %d config files to process" % len(config_files))
    for cf in config_files:
        collect_config_file_versions(spc, cf, output_dir)

    print("\nAll Over!!!")

def collect_config_file_versions(spc, cf, output_dir):
    """
    Collect all versions for a given file
    """
    print("Collecting file versions for device: ", cf.deviceName)
    device_path_name = '/'.join([output_dir, str(cf.deviceName)])

    versions = cf.config_file_versions.get()
    for v in versions:
        version_path_name = '/'.join([device_path_name,
                                      str(v.versionId)])
        if os.path.exists(os.path.abspath(version_path_name)):
            continue # We already have stored this version

        cfv = v.get()
        store_version(version_path_name, cfv)

    return cf.deviceName

def store_version(version_path_name, config_file_version):
    """
    Store the given config file version into the local filesystem.
    Each version goes under a separate directory and it contains a MANIFEST.mf
    file in addition to the file which has the configuration text.
    """
    try:
        # Create the directory for this version
        os.makedirs(os.path.abspath(version_path_name))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    #
    # Create a MANIFEST.mf file with details about this version
    #
    mf_name = '/'.join([version_path_name, 'MANIFEST.mf'])
    with open(os.path.abspath(mf_name), 'w') as f:
        f.write('Version Id: %s\n' % str(config_file_version.versionId))
        f.write('Config File Size: %s\n' % \
                str(config_file_version.configFileSize))
        f.write('MD5: %s\n' % str(config_file_version.latestMD5))
        f.write('Creation Time: %s\n' % str(config_file_version.creationTime))
        f.write('Comment: %s\n' % str(config_file_version.comment))

    #
    # Store the configuration text contents for this version into a file.
    # The name of the file is as given by Space and consists of the device
    # name, version id, and creation time stamp.
    #
    contents_file_name = '/'.join([version_path_name,
                                   str(config_file_version.fileName)])
    with open(os.path.abspath(contents_file_name), 'w') as f:
        f.write(config_file_version.content.text)


if __name__ == '__main__':
    logging.config.fileConfig('../test/logging.conf')
    parser = argparse.ArgumentParser()
    parser.add_argument("space_URL", help="URL of the Space instance")
    parser.add_argument("-u", "--user", help="Userid")
    parser.add_argument("-p", "--passwd", help="Password")
    parser.add_argument("-o", "--out", help="Output directory")

    args = parser.parse_args()
    main(args)