{#
  Parameters used:
     - devices
         A list of devices. Each must have href set.
#}
<installeventprofile>
  <devices>
{%- for d in devices %}
    <device href="{{d.get('href')}}"/>
{%- endfor %}
  </devices>
  <neverStoreScriptBundle>false</neverStoreScriptBundle>
  <removeScriptBundle>false</removeScriptBundle>
</installeventprofile>