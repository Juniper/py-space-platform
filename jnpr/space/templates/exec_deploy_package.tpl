{#
  Parameters used:
     - devices
         A list of device objects on which the script has to be deployed.
         Each object must have the href attribute set.
     - useAlreadyDownloaded: Boolean (defaults to False)
     - validate: Boolean (defaults to False)
     - bestEffortLoad: Boolean (defaults to False)
     - snapShotRequired: Boolean (defaults to False)
     - rebootDevice: Boolean (defaults to False)
     - rebootAfterXMinutes: Integer (defaults to 0)
     - cleanUpExistingOnDevice: Boolean (defaults to False)
     - removePkgAfterInstallation: Boolean (defaults to False)

#}
<exec-deploy>
  <devices>
{%- for device in devices %}
    <device href= "{{device.href}}" />
{%- endfor %}
  </devices>
  <deployOptions>
{%- if useAlreadyDownloaded %}
    <useAlreadyDownloaded>{{useAlreadyDownloaded}}</useAlreadyDownloaded>
{%- else %}
    <useAlreadyDownloaded>false</useAlreadyDownloaded>
{%- endif %}
{%- if validate %}
    <validate>{{validate}}</validate>
{%- else %}
    <validate>false</validate>
{%- endif %}
{%- if bestEffortLoad %}
    <bestEffortLoad>{{bestEffortLoad}}</bestEffortLoad>
{%- else %}
    <bestEffortLoad>false</bestEffortLoad>
{%- endif %}
{%- if snapShotRequired %}
    <snapShotRequired>{{snapShotRequired}}</snapShotRequired>
{%- else %}
    <snapShotRequired>false</snapShotRequired>
{%- endif %}
{%- if rebootDevice %}
    <rebootDevice>{{rebootDevice}}</rebootDevice>
{%- else %}
    <rebootDevice>false</rebootDevice>
{%- endif %}
{%- if rebootAfterXMinutes %}
    <rebootAfterXMinutes>{{rebootAfterXMinutes}}</rebootAfterXMinutes>
{%- else %}
    <rebootAfterXMinutes>0</rebootAfterXMinutes>
{%- endif %}
{%- if cleanUpExistingOnDevice %}
    <cleanUpExistingOnDevice>{{cleanUpExistingOnDevice}}</cleanUpExistingOnDevice>
{%- else %}
    <cleanUpExistingOnDevice>false</cleanUpExistingOnDevice>
{%- endif %}
{%- if removePkgAfterInstallation %}
    <removePkgAfterInstallation>{{removePkgAfterInstallation}}</removePkgAfterInstallation>
{%- else %}
    <removePkgAfterInstallation>false</removePkgAfterInstallation>
{%- endif %}
  </deployOptions>
</exec-deploy>