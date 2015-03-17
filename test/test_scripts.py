from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import object
import configparser

from jnpr.space import rest, factory, async

class TestScripts(object):

    def setup_class(self):
        # Extract Space URL, userid, password from config file
        config = configparser.RawConfigParser()
        config.read("./test.conf")
        url = config.get('space', 'url')
        user = config.get('space', 'user')
        passwd = config.get('space', 'passwd')

        # Create a Space REST end point
        self.space = rest.Space(url, user, passwd)

    def test_create_script(self):
        s = factory.make_resource(type_name='script_management.script',
                                        rest_end_point=self.space)
        s.scriptName = 'Interface_status_space_ez.slax'
        s.scriptContents = POST_SCRIPT_CONTENT

        s = self.space.script_management.scripts.post(s)
        assert s.id

    def test_modify_script(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"

        s[0].scriptContents = PUT_SCRIPT_CONTENT
        s[0].comment = "Testing changes"
        s[0].put()

    def test_deploy_script(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"

        d = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                                    'connectionStatus': 'up'})
        assert len(d) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_script_deploy_q')
        try:
            task = self.space.script_management.scripts.exec_deploy.post(task_monitor=tm, script=s[0], device=d[0])
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()

    def test_enable_script(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"

        d = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                                    'connectionStatus': 'up'})
        assert len(d) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_script_enable_q')
        try:
            task = self.space.script_management.scripts.exec_enable.post(task_monitor=tm, script=s[0], device=d[0])
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()

    def test_execute_script(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"

        d = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                                    'connectionStatus': 'up'})
        assert len(d) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_script_exec_q')
        try:
            task = self.space.script_management.scripts.exec_scripts.post(task_monitor=tm,
                                          script=s[0],
                                          device=d[0],
                                          scriptParams={'interface': 'ge-0/0/0.0'})
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()

    def test_disable_script(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"

        d = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                                    'connectionStatus': 'up'})
        assert len(d) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_script_disable_q')
        try:
            task = self.space.script_management.scripts.exec_disable.post(task_monitor=tm, script=s[0], device=d[0])
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()

    def test_verify_script(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"

        d = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                                    'connectionStatus': 'up'})
        assert len(d) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_script_verify_q')
        try:
            task = self.space.script_management.scripts.exec_verify.post(task_monitor=tm, script=s[0], device=d[0])
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()

    def test_view_script_associations(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"

        devices = s[0].view_associated_devices.get()
        assert len(devices) == 1, "Incorrect associations"

    def test_remove_script(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"

        d = self.space.device_management.devices.get(filter_={'deviceFamily': 'junos',
                                                                    'connectionStatus': 'up'})
        assert len(d) > 1, 'Not enough connected devices present on Space!'

        tm = async.TaskMonitor(self.space, 'test_script_remove_q')
        try:
            task = self.space.script_management.scripts.exec_remove.post(task_monitor=tm, script=s[0], device=d[0])
            assert task.id > 0

            pu = tm.wait_for_task(task.id)
            assert pu
        finally:
            tm.delete()
    """
    def test_get_by_context(self):
        s = self.space.script_management.scripts.scripts_by_context.post(
                        context='/device')
        assert len(s) >= 0
    """

    def test_get_scripts(self):
        scrpts = self.space.script_management.scripts.get()
        assert len(scrpts) > 0, "No scripts on Space!"

    def test_get_script_details(self):
        scrpts = self.space.script_management.scripts.get()
        n = len(scrpts)
        assert n > 0, "No scripts on Space!"

        for s in scrpts[0:1]:
            details = s.get()
            assert details

    def test_get_script_contents(self):
        scrpts = self.space.script_management.scripts.get()
        assert len(scrpts) > 0, "No scripts on Space!"

        for s in scrpts[0:1]:
            c = s.contents.get()
            assert c.scriptContents

    def test_get_script_params(self):
        scrpts = self.space.script_management.scripts.get()
        assert len(scrpts) > 0, "No scripts on Space!"

        for s in scrpts[0:1]:
            params = s.parameters.get()
            for p in params:
                assert p.parameter

    def test_delete_script(self):
        s = self.space.script_management.scripts.get(filter_={'scriptName': 'Interface_status_space_ez.slax'})
        assert len(s) == 1, "Test script not present on Space!"
        s[0].delete()

POST_SCRIPT_CONTENT = """<![CDATA[
/*
 *  show_interface_staus.slax
 *
 *  Created by Todd Okolowicz (tokolowicz@juniper.net) on 20090713.
 *  Copyright (c) 2009 Juniper Networks. All rights reserved.
 *
 *  Version History
 *  ===============
 *  v1.0     Initial release.
 *
 */

version 1.0;

ns junos = "http://xml.juniper.net/junos/*/junos";
ns xnm = "http://xml.juniper.net/xnm/1.1/xnm";
ns jcs = "http://xml.juniper.net/junos/commit-scripts/1.0";

import "../import/junos.xsl";

/* This is imported into JUNOS as a CLI option */
var $arguments = {
    <argument> {
    <name> "interface";
        <description> "Name of logical interface (e.g. ge-0/0/0.0)";
    }
}

/* Command-line argument */
param $interface;

match / {
    <op-script-results> {

        /* Send JUNOS XML API Element via jcs:invoke */
        var $results1 = jcs:invoke( "get-interface-information" );

        /* Send JUNOS XML API Element via jcs:invoke */
        var $command-rpc = <command> "show ethernet-switching interfaces";
        var $results2 = jcs:invoke( $command-rpc );

     /* This is a functional code block that uses a regular
       * expression to check the interface cli option for correct syntax. I
      * disabled it and opted for the code block below. The regex is a
      * hard-coded and does not account for all possible hardware
      * configurations (i.e. EX3200 vs. EX4200, uplink vs. no uplink, 1GbE
      * or 10GbE uplink, Virtual Chassis or stand-alone, etc.) It is more
      * accurate to compare the cli input vs. the list of Ethernet switching
      * interfaces actually enabled in the system. I left the regex code block
      * in for code re-use in future scripts and learning purposes.

      * Error check for incorrect interface syntax using a regex.
        if ( not ( jcs:empty ( $interface ) ) and jcs:empty ( jcs:regex ( "[xg]e-[0-9]/[0-1]/(([0-9])|([1-3][0-9])|(4[0-7])).0", $interface ) ) ) {
            <xsl:message terminate="yes"> "The interface " _ $interface _ " isn't valid.\nUsage example: op show_interface_status interface ge-0/0/0.0";
        }
      */

        var $matching-interface = $results2/interface [ interface-name == $interface ];
        if( not ( jcs:empty ($interface ) ) and jcs:empty ( $matching-interface ) ) {
            <xsl:message terminate="yes"> "The interface " _ $interface _ " isn't valid.\nUsage example: op show_interface_status interface ge-0/0/0.0";
        }

     /* Create node list based on location path, loop through each node */
        <output> jcs:printf("%-15s%-7s%-15s%-12s%-12s%-15s", "Interface", "Status", "VLAN Members", "Port-mode", "Speed", "Duplex" );
            for-each ( $results2/interface [ string-length($interface)==0 or interface-name=$interface ] ) {
                var $first-vlan = interface-vlan-member-list/interface-vlan-member/interface-vlan-name [position() == 1 ];
                var $interface-name = interface-name;
                var $status = interface-state;
                var $vlan-tagness = interface-vlan-member-list/interface-vlan-member/interface-vlan-member-tagness;
                var $logical-interface = $results1/physical-interface/logical-interface [name==$interface-name];
                <output> jcs:printf("%-15s%-7s%-15s%-12s%-12s%-15s", $interface-name, $status, $first-vlan, $vlan-tagness, $logical-interface/../speed, $logical-interface/../duplex );
                /* Second for-each loop embedded within first to create node-list of additional vlans possibly assigned to trunk interfaces */
                for-each ( ./interface-vlan-member-list/interface-vlan-member[position() != 1 ] ) {
                    <output> jcs:printf("%-22s%-12s", "", ./interface-vlan-name );
                }
            }
    }
}
]]>"""

PUT_SCRIPT_CONTENT = """<![CDATA[
/*
 *  show_interface_staus.slax
 *
 *  Created by Todd Okolowicz (tokolowicz@juniper.net) on 20090713.
 *  Copyright (c) 2009 Juniper Networks. All rights reserved.
 *
 *  Version History
 *  ===============
 *  v1.0     Initial release.
 *  v1.1     Testing changes.
 *
 */

version 1.1;

ns junos = "http://xml.juniper.net/junos/*/junos";
ns xnm = "http://xml.juniper.net/xnm/1.1/xnm";
ns jcs = "http://xml.juniper.net/junos/commit-scripts/1.0";

import "../import/junos.xsl";

/* This is imported into JUNOS as a CLI option */
var $arguments = {
    <argument> {
    <name> "interface";
        <description> "Name of logical interface (e.g. ge-0/0/0.0)";
    }
}

/* Command-line argument */
param $interface;

match / {
    <op-script-results> {

        /* Send JUNOS XML API Element via jcs:invoke */
        var $results1 = jcs:invoke( "get-interface-information" );

        /* Send JUNOS XML API Element via jcs:invoke */
        var $command-rpc = <command> "show ethernet-switching interfaces";
        var $results2 = jcs:invoke( $command-rpc );

     /* This is a functional code block that uses a regular
       * expression to check the interface cli option for correct syntax. I
      * disabled it and opted for the code block below. The regex is a
      * hard-coded and does not account for all possible hardware
      * configurations (i.e. EX3200 vs. EX4200, uplink vs. no uplink, 1GbE
      * or 10GbE uplink, Virtual Chassis or stand-alone, etc.) It is more
      * accurate to compare the cli input vs. the list of Ethernet switching
      * interfaces actually enabled in the system. I left the regex code block
      * in for code re-use in future scripts and learning purposes.

      * Error check for incorrect interface syntax using a regex.
        if ( not ( jcs:empty ( $interface ) ) and jcs:empty ( jcs:regex ( "[xg]e-[0-9]/[0-1]/(([0-9])|([1-3][0-9])|(4[0-7])).0", $interface ) ) ) {
            <xsl:message terminate="yes"> "The interface " _ $interface _ " isn't valid.\nUsage example: op show_interface_status interface ge-0/0/0.0";
        }
      */

        var $matching-interface = $results2/interface [ interface-name == $interface ];
        if( not ( jcs:empty ($interface ) ) and jcs:empty ( $matching-interface ) ) {
            <xsl:message terminate="yes"> "The interface " _ $interface _ " isn't valid.\nUsage example: op show_interface_status interface ge-0/0/0.0";
        }

     /* Create node list based on location path, loop through each node */
        <output> jcs:printf("%-15s%-7s%-15s%-12s%-12s%-15s", "Interface", "Status", "VLAN Members", "Port-mode", "Speed", "Duplex" );
            for-each ( $results2/interface [ string-length($interface)==0 or interface-name=$interface ] ) {
                var $first-vlan = interface-vlan-member-list/interface-vlan-member/interface-vlan-name [position() == 1 ];
                var $interface-name = interface-name;
                var $status = interface-state;
                var $vlan-tagness = interface-vlan-member-list/interface-vlan-member/interface-vlan-member-tagness;
                var $logical-interface = $results1/physical-interface/logical-interface [name==$interface-name];
                <output> jcs:printf("%-15s%-7s%-15s%-12s%-12s%-15s", $interface-name, $status, $first-vlan, $vlan-tagness, $logical-interface/../speed, $logical-interface/../duplex );
                /* Second for-each loop embedded within first to create node-list of additional vlans possibly assigned to trunk interfaces */
                for-each ( ./interface-vlan-member-list/interface-vlan-member[position() != 1 ] ) {
                    <output> jcs:printf("%-22s%-12s", "", ./interface-vlan-name );
                }
            }
    }
}
]]>"""
