{#
  Parameters used:
     - script
         A script object which has to be removed.
         The object must have the href attribute set.
     - device
         A device object on which the script has to be removed.
         The object must have the href attribute set.
     - scriptVersionSelected (optional)
         A string identifying the version of the script to be removed.
#}
<exec-remove>
   <scriptMgmt>
     <script href="{{script.href}}" />
     <device href="{{device.href}}" />
{%- if scriptVersionSelected %}
     <scriptVersionSelected>{{scriptVersionSelected}}</scriptVersionSelected>
{%- endif %}
   </scriptMgmt>
</exec-remove>