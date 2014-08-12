{#
  Parameters used:
     - devices
         A list of device objects from which the script has to be removed.
         Each object must have the href attribute set.

#}
<exec-remove>
  <devices>
{%- for device in devices %}
    <device href= "{{device.href}}" />
{%- endfor %}
  </devices>
</exec-deploy>