{#
  Parameters used:
     - devices
         List of device objects on which credentials need to be changed.
         The object must have an attribute named 'href'
     - user_name
       Target user password to be chnaged. 
     - password
         New password
     - re_authenticate 
         if True, Space drops existing SSH connection to the given devices. 
     - change_to
         Change to auth type : allowed values are: CREDENTIAL or KEY. If authtype is changed from CRDENTIAL to KEY, the auth type is changed in Space DB to become KEY for these devices. Space public RSA key is configured on the given devices under the given user_Name.
     - change_on_device
         True/False. Whether to change the password on the device. New userid/password is always stored in DB. This paramter must be True when authtype change_to paramater is changed from CREDENTIAL to KEY. 
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
