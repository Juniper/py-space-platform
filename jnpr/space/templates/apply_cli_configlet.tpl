{#
  Parameters used:
     - configletId
         Id of the configlet that needs to be applied
     - parameters
         A dictionary where the keys are parameter names
         and values are parameter values
#}
<cli-configlet-mgmt>
  <configletId>{{ configletId }}</configletId>
{% for key, value in parameters.items() %}
  <cli-configlet-param>
    <parameter>{{ key }}</parameter>
    <param-value>{{ value }}</param-value>
  </cli-configlet-param>
{% endfor %}
</cli-configlet-mgmt>