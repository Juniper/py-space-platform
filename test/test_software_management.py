from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest, async

class TestSoftwareManagement(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_get_packages(self):
        pkgs = self.space.software_management.packages.get()
        assert len(pkgs) > 0, "No packages on Space!"

    def test_get_package_details(self):
        pkgs = self.space.software_management.packages.get()
        assert len(pkgs) > 0, "No packages on Space!"

        for p in pkgs[0:1]:
            details = p.get()
            assert details

    """
    def test_stage_package(self):
        pkgs = self.space.software_management.packages.get()
        assert len(pkgs) >= 1, "No packages present on Space!"

        devs = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                              'connectionStatus': 'up'})
        assert len(devs) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_pkg_stage_q')
        try:
            task = pkgs[0].exec_stage.post(task_monitor=tm, devices=devs[:1])
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()
    """

    def test_package_associations(self):
        pkgs = self.space.software_management.packages.get()
        assert len(pkgs) > 0, "No packages present on Space!"

        devices = pkgs[0].associated_devices.get()
        assert len(devices) >= 0, "No associations"

    def test_verify_package(self):
        pkgs = self.space.software_management.packages.get()
        assert len(pkgs) >= 1, "No packages present on Space!"

        devs = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                              'connectionStatus': 'up'})
        assert len(devs) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_pkg_verify_q')
        try:
            task = pkgs[0].exec_verify.post(task_monitor=tm, devices=devs[:1])
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()

    """
    def test_remove_package(self):
        pkgs = self.space.software_management.packages.get()
        assert len(pkgs) >= 1, "No packages present on Space!"

        devs = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                              'connectionStatus': 'up'})
        assert len(devs) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_pkg_verify_q')
        try:
            task = pkgs[0].exec_remove.post(task_monitor=tm, devices=devs[:1])
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()
    """
