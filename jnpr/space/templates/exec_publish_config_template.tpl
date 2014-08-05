{#
  Parameters used:
     - devices
         A list of device objects to which the template has to be published.
         Each object must have the href and key attributes set.
     - resolved_variables
         A dictionary where the keys are device objects.
         and values are dictionaries. Each dictionary has variable names as
         keys and each value can be a list or a single item.
#}
<exec-publish-request>
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
{%- for key, value in resolved_variables[d.key].iteritems() %}
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
</exec-publish-request>