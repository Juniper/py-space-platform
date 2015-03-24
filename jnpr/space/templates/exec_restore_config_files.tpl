{#
  Parameters used:
     - restore_type
        MERGE
     - config_file_versions
        A list of config_file_version objects which need to be restored.
        Each object must have the 'id' and 'versionId' attribute set.
#}

<exec-restore>
  <exec-restore-specs>
{%- for f in config_file_versions %}
    <exec-restore-spec>
      <restoreType>{{restore_type}}</restoreType>
      <latestVersion>{{f.versionId}}</latestVersion>
      <id>{{f.id}}</id>
    </exec-restore-spec>
{%- endfor %}
  </exec-restore-specs>
</exec-restore>