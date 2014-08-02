{#
  Parameters used:
     - deviceId
         Id of the device on which this configlet is to be applied
     - parameters
         A dictionary where the keys are parameter names
         and values are parameter values
#}
<cli-configlet-mgmt>
  <deviceId>{{ deviceId }}</deviceId>
{% for key, value in parameters.iteritems() %}
  <cli-configlet-param>
    <parameter>{{ key }}</parameter>
    <param-value>{{ value }}</param-value>
  </cli-configlet-param>
{% endfor %}
</cli-configlet-mgmt>