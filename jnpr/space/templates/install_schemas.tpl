{#
  Parameters used:
     - schemas
         A list of dicts indicating which schemas need to be installed.
         Each dict must have the 'device-family' and 'release' keys set.
         It also must have the 'schema-location' attribute set, if installing
         from a previously uploaded tgz file.
#}

<install-schemas-request>
     <schemas>
{%- for s in schemas %}
       <schema>
{%- if 'schema-location' in s %}
           <schema-location>{{s['schema-location']}}</schema-location>
{%- endif %}
           <device-family>{{s['device-family']}}</device-family>
           <release>{{s['release']}}</release>
       </schema>
{%- endfor %}
     </schemas>
</install-schemas-request>