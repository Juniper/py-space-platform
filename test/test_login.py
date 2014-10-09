import ConfigParser
import pytest

from jnpr.space import rest, factory

class TestLogin:

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = ConfigParser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd, use_session=True)

    def test_create_user(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        u = factory.make_resource(type_name='user_management.user',
                                        rest_end_point=self.space)
        u.name = 'space_ez1'
        u.firstName = 'Space'
        u.lastName = 'EZ'
        u.password = '123Juniper'
        u.primaryEmail = 'space_ez@juniper.net'
        u.roles = [r]
        u.read_only = False

        u = self.space.user_management.users.post(u)
        assert u.id > 0

        rls = u.roles.get()
        assert rls[0].href == r.href

    def test_logout_1(self):
        self.space.logout()
        with pytest.raises(Exception):
            self.space.user_management.users.get(filter_={'name':'super'})

    def test_login(self):
        self.space.login()

    def test_change_password(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez1'})
        assert len(us) == 1
        pwd = us[0].change_password.post(
                                   oldPassword='123Juniper',
                                   newPassword='456Juniper')
        assert pwd.newPassword == '456Juniper'

    def test_get_user_active_sessions(self):
        us = self.space.user_management.users.get(filter_={'name':'super'})
        assert len(us) == 1
        ss = us[0].active_user_sessions.get()
        assert len(ss) >= 0

    def test_delete_user(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez1'})
        assert len(us) == 1
        us[0].delete()

    def test_logout(self):
        self.space.logout()
        with pytest.raises(Exception):
            self.space.user_management.users.get(filter_={'name':'super'})

    def test_login_logout_loop(self):
        for i in range(1,10):
            self.space.login()
            users_list = self.space.user_management.users.get()
            assert len(users_list) > 0
            self.space.logout()
            #with pytest.raises(Exception):
            self.space.user_management.users.get()
