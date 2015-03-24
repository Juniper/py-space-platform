{#
  Parameters used:
     - dmi_schema_infos
         A list of objects indicating which schemas need to be deleted.
         Each object must have the os_version and dev_family attributes set.
#}

<delete-schemas>
     <dmi-schema-infos>
{%- for d in dmi_schema_infos %}
       <dmi-schema-info>
           <os-version>{{d.os_version}}</os-version>
           <dev-family>{{d.dev_family}}</dev-family>
       </dmi-schema-info>
{%- endfor %}
     </dmi-schema-infos>
</delete-schemas>