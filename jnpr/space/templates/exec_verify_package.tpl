{#
  Parameters used:
     - devices
         A list of device objects on which the script has to be verified.
         Each object must have the href attribute set.

#}
<exec-verify>
  <devices>
{%- for device in devices %}
    <device href= "{{device.href}}" />
{%- endfor %}
  </devices>
</exec-verify>