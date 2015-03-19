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
from builtins import object
from jnpr.space import media_types

import pytest

class TestMediaTypes(object):

    def test_1(self):
        mt = media_types.get_media_type('/api/space/application-management', 'GET', 'Accept')
        assert mt == 'application/vnd.net.juniper.space.application-management+xml;version=1'

    def test_2(self):
        mt = media_types.get_media_type('/api/space/application-management', 'GET', 'Accept', version=2)
        assert mt == 'application/vnd.net.juniper.space.application-management+xml;version=2'

    def test_3(self):
        with pytest.raises(Exception) as excinfo:
            media_types.get_media_type('/api/space/application-management', 'GET', 'Accept', version=22)
        assert excinfo.value.args[0] == 'Version 22 not available for Accept header for GET on /api/space/application-management'

    def test_4(self):
        with pytest.raises(Exception) as excinfo:
            media_types.get_media_type('/api/space/application-management', 'GET', 'Content-Type')
        assert excinfo.value.args[0] == 'Header Content-Type not available for GET on /api/space/application-management'

    def test_5(self):
        with pytest.raises(Exception) as excinfo:
            media_types.get_media_type('/api/space/application-management', 'PUT', 'Content-Type')
        assert excinfo.value.args[0] == 'Method PUT not available on /api/space/application-management'

    def test_6(self):
        with pytest.raises(Exception) as excinfo:
            media_types.get_media_type('/api/space/application-management/junk', 'PUT', 'Content-Type')
        assert excinfo.value.args[0] == 'URL /api/space/application-management/junk not available'

    def test_7(self):
        mt = media_types.get_media_type('/api/space/application-management/applications/123/settings-config', 'PUT', 'Content-Type')
        assert mt == 'application/vnd.net.juniper.space.application-management.settings-config+xml;version=1;charset=UTF-8'
