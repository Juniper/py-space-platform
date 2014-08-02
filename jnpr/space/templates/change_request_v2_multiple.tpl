{#
  Parameters used:
     - name
         Name for the change-request
     - description
         Description for the change-request
     - devices
         List of objects, each representing a device. Must have the 'href' attribute set.
     - xmlData
         XML configuration that needs to be deployed, formatted as a string
#}

<change-requests>
{%- for d in devices %}
    <change-request>
      <name>{{ name }}</name>
      <description>{{ description }}</description>
      <xmlData>
        <![CDATA[
        {{ xmlData }}
        ]]>
      </xmlData>
      <device href="{{d.href}}"/>
{%- if syncAfterPush %}
      <syncAfterPush>{{ syncAfterPush }}</syncAfterPush>
{%- else %}
      <syncAfterPush>false</syncAfterPush>
{%- endif %}
    </change-request>
{%- endfor %}
</change-requests>