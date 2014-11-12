{#
  Parameters used:
     - devices
         List of device objects on which credentials need to be changed.
         The object must have an attribute named 'href'
     - user_name
     - password
         Current password
     - change_to
         New password
     - change_on_device
         True/False. Whether to change it on the device.
#}
<change-credentials>
   <devices>
{%- for d in devices %}
     <device href="{{d.href}}"></device>
{%- endfor %}
   </devices>
   <user-name>{{user_name}}</user-name>
   <password>{{password}}</password>
   <change-to>{{change_to}}</change-to>
{%- if change_on_device %}
   <change-on-device>{{change_on_device|lower}}</change-on-device>
{% endif -%}
</change-credentials>