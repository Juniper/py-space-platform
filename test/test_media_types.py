from jnpr.space import media_types

import pytest

class TestMediaTypes:

    def test_1(self):
        mt = media_types.get_media_type('/api/space/application-management', 'GET', 'Accept')
        assert mt == 'application/vnd.net.juniper.space.application-management+xml;version=1'

    def test_2(self):
        mt = media_types.get_media_type('/api/space/application-management', 'GET', 'Accept', version=2)
        assert mt == 'application/vnd.net.juniper.space.application-management+xml;version=2'

    def test_3(self):
        with pytest.raises(Exception) as excinfo:
            media_types.get_media_type('/api/space/application-management', 'GET', 'Accept', version=22)
        assert excinfo.value.message == 'Version 22 not available for Accept header for GET on /api/space/application-management'

    def test_4(self):
        with pytest.raises(Exception) as excinfo:
            media_types.get_media_type('/api/space/application-management', 'GET', 'Content-Type')
        assert excinfo.value.message == 'Header Content-Type not available for GET on /api/space/application-management'

    def test_5(self):
        with pytest.raises(Exception) as excinfo:
            media_types.get_media_type('/api/space/application-management', 'PUT', 'Content-Type')
        assert excinfo.value.message == 'Method PUT not available on /api/space/application-management'

    def test_6(self):
        with pytest.raises(Exception) as excinfo:
            media_types.get_media_type('/api/space/application-management/junk', 'PUT', 'Content-Type')
        assert excinfo.value.message == 'URL /api/space/application-management/junk not available'

    def test_7(self):
        mt = media_types.get_media_type('/api/space/application-management/applications/123/settings-config', 'PUT', 'Content-Type')
        assert mt == 'application/vnd.net.juniper.space.application-management.settings-config+xml;version=1;charset=UTF-8'
