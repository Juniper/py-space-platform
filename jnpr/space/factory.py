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

A module with functions using which new resource objects can be created.
Resources are instances of jnpr.space.resource.Resource.
"""
from __future__ import unicode_literals
from jnpr.space import rest, resource, xmlutil

def make_resource(type_name, rest_end_point,
                  xml_data=None, attributes=None, parent=None):
    """Creates a new instance of jnpr.space.resource.Resource based on the
    given parameters. This method creates it in-memory locally and *not* on
    the Space server. The post() method must be invoked on the Resource object
    to get it created on the Space server.

    :param str type_name: Fully qualified type name for the Resource to be
        created. It is of the format ``<service_name>.<resource_type>``.
        Some examples are:

            * ``device_management.device``
            * ``user_management.user``

    :param rest_end_point: A *Space* object encapsulating the Junos
        Space cluster which is to contain this resource.
    :type rest_end_point: jnpr.space.rest.Space

    :param lxml.etree.Element xml_data:  The state of the resource as an
        XML object. This defaults to ``None``.

    :param dict attributes:  The state of the resource as a dict where the
        keys are attribute names and values are attribute values.
        This defaults to ``None``.

    :param parent: The parent object of this resource. This defaults to
        ``None``.
    :type parent: jnpr.space.collection.Collection

    :returns: A new instance of jnpr.space.resource.Resource

    """
    return resource.Resource(type_name,
                             rest_end_point,
                             xml_data,
                             attributes,
                             parent)

def fetch_resource(rest_end_point, href):
    """This is the method you should use to create a Resource instance if you
    have the href for it. It gets the current state of the resource with the
    given *href*. Once the current state is fetched from the Space server, this
    method creates a new instance of ``jnpr.space.resource.Resource`` with this
    state and returns it.

    :param rest_end_point: A *Space* object encapsulating the Junos
        Space cluster which contains this resource.
    :type rest_end_point: jnpr.space.rest.Space

    :param str href: The href of the resource that needs to be fetched.

    :returns: A new instance of jnpr.space.resource.Resource

    :raises: ``jnpr.space.rest.RestException`` if the GET request results in an
        error response. The exception's ``response`` attribute will have the
        full response from Space.
    """
    response = rest_end_point.get(href)
    if response.status_code != 200:
        raise rest.RestException("GET failed on %s" % href, response)

    media_type = response.headers['content-type']
    end = media_type.index('+')
    parts = media_type[:end].split('.')
    app_ = parts[len(parts)-3]
    service_ = parts[len(parts)-2]
    type_ = parts[len(parts)-1]

    if app_ == 'space':
        type_name = xmlutil.unmake_xml_name('.'.join([service_, type_]))
    else:
        type_name = xmlutil.unmake_xml_name('.'.join([app_, service_, type_]))

    xml_data = xmlutil.get_xml_obj_from_response(response)
    return make_resource(type_name, rest_end_point, xml_data)
