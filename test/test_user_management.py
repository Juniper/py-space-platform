from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest, factory

class TestUserManagement(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_create_user(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        u = factory.make_resource(type_name='user_management.user',
                                        rest_end_point=self.space)
        u.name = 'space_ez'
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

    def test_change_password(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez'})
        assert len(us) == 1
        pwd = us[0].change_password.post(
                                   oldPassword='123Juniper',
                                   newPassword='456Juniper')
        assert pwd.newPassword == '456Juniper'

    def test_change_password_to_temp(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez'})
        assert len(us) == 1
        pwd = us[0].change_password_to_temp.post(old_password='456Juniper')
        assert pwd.value

    def test_get_user_active_sessions(self):
        us = self.space.user_management.users.get(filter_={'name':'super'})
        assert len(us) == 1
        ss = us[0].active_user_sessions.get()
        assert len(ss) >= 0

    def test_add_user_roles(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez'})
        assert len(us) == 1
        num_roles = len(us[0].roles.get())

        rls = self.space.user_management.roles.get()
        assert len(rls) > 1
        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[1].href

        us[0].roles.post([r])

        rls = us[0].roles.get()
        assert len(rls) == num_roles + 1

    def test_delete_user(self):
        us = self.space.user_management.users.get(filter_={'name':'space_ez'})
        assert len(us) == 1
        us[0].delete()

    def test_get_sessions(self):
        ss = self.space.user_management.active_user_sessions.get()
        assert len(ss) >= 0, "No sessions on Space!"

    def test_get_session_details(self):
        ss = self.space.user_management.active_user_sessions.get()
        n = len(ss)
        assert n >= 0, "No sessions on Space!"

        for s in ss[n - 2:]:
            details = s.get()
            assert details

    def test_get_tasks(self):
        tsks = self.space.user_management.tasks.get()
        assert len(tsks) > 0, "No tasks on Space!"

    def test_get_task_details(self):
        tsks = self.space.user_management.tasks.get()
        n = len(tsks)
        assert n > 0, "No tasks on Space!"

        for tsk in tsks[n - 2:]:
            details = tsk.get()
            assert details

    def test_get_capabilities(self):
        cs = self.space.user_management.capabilities.get()
        assert len(cs) > 0, "No capabilities on Space!"

    def test_get_capability_details(self):
        cs = self.space.user_management.capabilities.get()
        n = len(cs)
        assert n > 0, "No capabilities on Space!"

        for c in cs[0:2]:
            details = c.get()
            assert details

    def test_get_capability_roles(self):
        cs = self.space.user_management.capabilities.get()
        n = len(cs)
        assert n > 0, "No capabilities on Space!"

        for c in cs[0:2]:
            rls = c.roles.get()
            assert rls
            for rl in rls:
                details = rl.get()
                assert details.name

    def test_get_capability_tasks(self):
        cs = self.space.user_management.capabilities.get()
        n = len(cs)
        assert n > 0, "No capabilities on Space!"

        for c in cs[0:2]:
            tsks = c.tasks.get()
            assert len(tsks) >= 0
            for tsk in tsks:
                details = tsk.get()
                assert details.name

    def test_get_roles(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0, "No roles on Space!"

    def test_get_role_details(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0, "No roles on Space!"

        for r in rls[0:2]:
            details = r.get()
            assert details

    def test_get_role_capabilities(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0, "No roles on Space!"

        for r in rls[0:2]:
            caps = r.capabilities.get()
            assert caps
            for cap in caps:
                details = cap.get()
                assert details.name

    def test_create_profile(self):
        rls = self.space.user_management.roles.get()
        assert len(rls) > 0

        r = factory.make_resource(type_name='user_management.role',
                                        rest_end_point=self.space)
        r.href = rls[0].href

        p = factory.make_resource(type_name='user_management.profile',
                                        rest_end_point=self.space)
        p.name = 'test_from_space_ez'
        p.description = 'Test from space-ez'
        p.roles = [r]

        p = self.space.user_management.profiles.post(p)
        assert p.roleType

        rls = p.roles.get()
        assert rls[0].href == r.href

    def test_get_profiles(self):
        prs = self.space.user_management.profiles.get()
        assert len(prs) > 0, "No profiles on Space!"

    def test_get_profile_details(self):
        prs = self.space.user_management.profiles.get()
        assert len(prs) > 0, "No profiles on Space!"

        for r in prs[0:2]:
            details = r.get()
            assert details

    def test_get_profile_roles(self):
        prs = self.space.user_management.profiles.get()
        assert len(prs) > 0, "No profiles on Space!"

        for r in prs:
            rls = r.roles.get()
            assert rls
            for r in rls:
                details = r.get()
                assert details.name

    def test_delete_profile(self):
        ps = self.space.user_management.profiles.get(filter_={'name':'test_from_space_ez'})
        assert len(ps) == 1
        ps[0].delete()
