{#
  Parameters used:
     - script
         A script object which has to be executed.
         The object must have the href attribute set.
     - device
         A device object on which the script has to be executed.
         The object must have the href attribute set.
     - scriptVersionSelected (optional)
         A string identifying the version of the script to be executed.
     - scriptParams
         A dictionary where the keys are parameter names
         and values are parameter values
#}
<exec-scripts>
   <scriptMgmt>
     <script href="{{script.href}}" />
     <device href="{{device.href}}" />
{%- if scriptVersionSelected %}
     <scriptVersionSelected>{{scriptVersionSelected}}</scriptVersionSelected>
{%- endif %}
{%- if scriptParams %}
     <scriptParams>
{%- for key, value in scriptParams.items() %}
       <scriptParam>
         <paramName>{{key}}</paramName>
         <paramValue>{{value}}</paramValue>
       </scriptParam>
{%- endfor %}
     </scriptParams>
{%- endif %}
   </scriptMgmt>
</exec-scripts>