{#
  Parameters used:
     - devices
         List of device objects on which to listen for syslogs.
         The object must have an attribute named 'href'
     - text_patterns
         List of text-pattern strings to grep for syslogs
#}
<get-syslog-events>
    <devices>
{%- for d in devices %}
        <device href="{{d.href}}"></device>
{%- endfor %}
    </devices>
    <text-patterns>
{%- for tp in text_patterns %}
        <text-pattern>{{tp}}</text-pattern>
{%- endfor %}
  </text-patterns>
</get-syslog-events>