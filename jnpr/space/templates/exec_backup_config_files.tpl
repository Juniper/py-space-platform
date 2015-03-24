{#
  Parameters used:
     - devices
         A list of device objects on which the backup has to be taken.
         The object must have the 'key' attribute set.
#}
<exec-backup>
    <devices>
{%- for d in devices %}
       <device>
         <deviceId>{{d.key}}</deviceId>
       </device>
{%- endfor %}
    </devices>
</exec-backup>