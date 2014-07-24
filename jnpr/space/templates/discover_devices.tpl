{#
  Parameters used:
     - hostName
     - ipAddress
     - upperIp
     - lowerIp
     - baseIp
     - subnetMask
     - usePing = True
     - useSnmp = True
     - snmpV1Setting
        - communityName
     - snmpV2CSetting
        - communityName
     - snmpV3Setting
        - userName
        - authenticationType
        - privacyType
        - authenticationPassword
        - privacyPassword
     - manageDiscoveredSystemsFlag
     - sshCredential
        - userName
        - password
#}

{% macro snmp_v3_setting(params) -%}
  <snmpV3Setting>
{% if 'userName' in params %}
    <userName>{{params.userName}}</userName>
{% endif %}
{% if 'authenticationType' in params %}
    <authenticationType>{{params.authenticationType}}</authenticationType>
{% endif %}
{% if 'privacyType' in params %}
    <privacyType>{{params.privacyType}}</privacyType>
{% endif %}
{% if 'authenticationPassword' in params %}
    <authenticationPassword>{{params.authenticationPassword}}</authenticationPassword>
{% endif %}
{% if 'privacyPassword' in params %}
    <privacyPassword>{{params.privacyPassword}}</privacyPassword>
{% endif %}
  </snmpV3Setting>
{%- endmacro %}

{% macro snmp_v2c_setting(communityName) -%}
  <snmpV2CSetting>
    <communityName>{{communityName}}</communityName>
  </snmpV2CSetting>
{%- endmacro %}

{% macro snmp_v1_setting(communityName) -%}
  <snmpV1Setting>
    <communityName>{{communityName}}</communityName>
  </snmpV1Setting>
{%- endmacro %}

{% macro host_name_discovery_target(hostName) -%}
  <hostNameDiscoveryTarget>
    <hostName>{{hostName}}</hostName>
  </hostNameDiscoveryTarget>
{%- endmacro %}

{% macro ip_address_discovery_target(ipAddress) -%}
  <ipAddressDiscoveryTarget>
    <ipAddress>{{ipAddress}}</ipAddress>
  </ipAddressDiscoveryTarget>
{%- endmacro %}

{% macro ip_range_discovery_target(upperIp, lowerIp) -%}
  <ipRangeDiscoveryTarget>
    <upperIp>{{upperIp}}</upperIp>
    <lowerIp>{{lowerIp}}</lowerIp>
  </ipRangeDiscoveryTarget>
{%- endmacro %}

{% macro ip_subnet_discovery_target(baseIp, subnetMask) -%}
  <ipSubnetDiscoveryTarget>
    <baseIp>{{baseIp}}</baseIp>
    <subnetMask>{{subnetMask}}</subnetMask>
  </ipSubnetDiscoveryTarget>
{%- endmacro %}

{% macro ssh_credential(userName, password) -%}
  <sshCredential>
    <userName>{{userName}}</userName>
    <password>{{password}}</password>
  </sshCredential>
{%- endmacro %}

{% macro flags(usePing, useSnmp, manageDiscoveredSystemsFlag) -%}
  <usePing>{{usePing}}</usePing>
  <useSnmp>{{useSnmp}}</useSnmp>
  <manageDiscoveredSystemsFlag>{{manageDiscoveredSystemsFlag}}</manageDiscoveredSystemsFlag>
{%- endmacro %}

<discover-devices>
{% if hostName %}
{{ host_name_discovery_target(hostName) }}
{% elif ipAddress %}
{{ ip_address_discovery_target(ipAddress) }}
{% elif baseIp %}
{{ ip_subnet_discovery_target(baseIp, subnetMask) }}
{% elif upperIp %}
{{ ip_range_discovery_target(upperIp, lowerIp) }}
{% endif %}
{% if usePing %}
  <usePing>{{usePing}}</usePing>
{% endif %}
{% if manageDiscoveredSystemsFlag %}
  <manageDiscoveredSystemsFlag>{{manageDiscoveredSystemsFlag}}</manageDiscoveredSystemsFlag>
{% endif %}
{{ ssh_credential(userName, password) }}
{% if useSnmp and snmpV1Setting %}
  <useSnmp>{{useSnmp}}</useSnmp>
  {{ snmp_v1_setting(snmpV1Setting['communityName']) }}
{% elif useSnmp and snmpV2CSetting %}
  <useSnmp>{{useSnmp}}</useSnmp>
  {{ snmp_v2c_setting(snmpV2CSetting['communityName']) }}
{% elif useSnmp and snmpV3Setting %}
  <useSnmp>{{useSnmp}}</useSnmp>
  {{ snmp_v3_setting(snmpV3Setting) }}
{% endif %}
</discover-devices>