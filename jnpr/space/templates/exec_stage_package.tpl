{#
  Parameters used:
     - devices
         A list of device objects on which the script has to be staged.
         Each object must have the href attribute set.
     - cleanUpExistingOnDevice: Boolean (defaults to False)

#}
<exec-stage>
  <devices>
{%- for device in devices %}
    <device href= "{{device.href}}" />
{%- endfor %}
  </devices>
  <deployOptions>
{%- if cleanUpExistingOnDevice %}
    <cleanUpExistingOnDevice>{{cleanUpExistingOnDevice}}</cleanUpExistingOnDevice>
{%- else %}
    <cleanUpExistingOnDevice>false</cleanUpExistingOnDevice>
{%- endif %}
  </deployOptions>
</exec-stage>