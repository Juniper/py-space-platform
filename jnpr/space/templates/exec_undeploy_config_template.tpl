{#
  Parameters used:
     - devices
         A list of device objects on which the template has to be undeployed.
         Each object must have the href attribute set.
#}
<exec-undeploy-request>
     <devices>
{%- for d in devices %}
           <device href="{{d.href}}"/>
{%- endfor %}
     </devices>
</exec-undeploy-request>