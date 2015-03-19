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
from builtins import str
import os
import yaml
import re

media_type_versions = None

def get_media_type(url, method, header, version=None, app_name=None):
    """
    Returns the requested media-type read from the yaml file.
    """
    global media_type_versions
    if media_type_versions is None:
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        file_name = dir_path + '/descriptions/'
        if app_name is not None:
            file_name = file_name + 'apps/' + app_name + '/media_type_versions.yml'
        else:
            file_name = file_name + '/media_type_versions.yml'
        with open(file_name) as mt_file:
            media_type_versions = yaml.load(mt_file)

    url = re.sub(r'\d+', '{id}', url)
    if url in media_type_versions:
        if method in media_type_versions[url]:
            if header in media_type_versions[url][method]:
                if version is not None:
                    try:
                        return media_type_versions[url][method][header][str(version)]
                    except KeyError:
                        raise Exception('Version %s not available for %s header for %s on %s' %
                                        (str(version), header, method, url))
                else:
                    d = media_type_versions[url][method][header]
                    return d[sorted(d)[0]]
            else:
                raise Exception('Header %s not available for %s on %s' % (header, method, url))
        else:
            raise Exception('Method %s not available on %s' % (method, url))
    else:
        raise Exception('URL %s not available' % (url))
