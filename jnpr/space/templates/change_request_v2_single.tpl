{#
  Parameters used:
     - name
         Name for the change-request
     - description
         Description for the change-request
     - device
         Object representing a device. Must have the 'href' attribute set.
     - xmlData
         XML configuration that needs to be deployed, formatted as a string
#}

<change-request>
  <name>{{ name }}</name>
  <description>{{ description }}</description>
  <xmlData>
    <![CDATA[
    {{ xmlData }}
    ]]>
  </xmlData>
  <device href="{{device.href}}"/>
{%- if syncAfterPush %}
  <syncAfterPush>{{ syncAfterPush }}</syncAfterPush>
{%- else %}
  <syncAfterPush>false</syncAfterPush>
{%- endif %}
</change-request>