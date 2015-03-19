{#
  Parameters used:
     - devices
         A list of device objects on which the template has to be deployed.
         Each object must have the href and key attributes set.
     - resolved_variables
         A dictionary where the keys are device objects.
         and values are dictionaries. Each dictionary has variable names as
         keys and each value can be a list or a single item.
#}
<exec-deploy-request>
     <devices>
{%- for d in devices %}
           <device href="{{d.href}}"/>
{%- endfor %}
     </devices>
{%- if resolved_variables %}
     <resolved-variables>
{%- for d in devices %}
           <device>
               <device-id>{{d.key}}</device-id>
               <variables>
{%- for key, value in resolved_variables[d.key].items() %}
                     <variable>
{%- if value is string %}
                         <values>
                               <value>{{value}}</value>
                         </values>
{%- else %}
                         <values>
{%- for v in value %}
                               <value>{{v}}</value>
{%- endfor %}
                         </values>
{%- endif %}
                         <name>{{key}}</name>
                     </variable>
{%- endfor %}
               </variables>
           </device>
{%- endfor %}
     </resolved-variables>
{%- endif %}
</exec-deploy-request>