# Examples

This package contains working examples that use this library to accomplish different things.
All these examples are designed to work both in **Python 2.7+** and in **Python 3.3+** using the __future__ package.

You can find brief descriptions about some of these examples below:

| Module        | Description|
| :------------ |:-------------|
| collect_config_files.py | Collects all versions of all device config files archived by the Config File Management service on Space and stores them into the local file system.|
| collect_inventory.py | Collects physical inventory and portions of the config for all devices in a Space cluster. It uses a thread-pool of workers to do it concurrently.|
| do_rpc_async.py      | Invokes an RPC on multiple devices asynchronosly and collects results from all of them.|
| get_devices_in_domains.py | Gets all devices from a Space cluster and prints their name and the name of the domain to which they belong.|
| get_role_details.py | Gets and prints all roles from a Space cluster and prints the role name and the tasks that are part of each.|
| tag_by_location.py | Examines the snmp/location configured on each device, automatically creates a public tag with the configured value, and assigns this tag to the device.|
