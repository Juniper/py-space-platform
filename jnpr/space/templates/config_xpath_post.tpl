{#
  Parameters used:
     - xpaths
         A list of xpath expressions as strings
#}
<xpaths>
{% for X in xpaths %}
  <xpath>{{ X }}</xpath>
{% endfor %}
</xpaths>