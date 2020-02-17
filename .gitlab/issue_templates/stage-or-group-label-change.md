---
name: Stage or group label change
about: Modify label of stage or group.
title: "[STAGE-OR-GROUP-LABEL-CHANGE] "
labels: stage-or-group-label-change
assignees: ${assignee1}
---

## Summary

This template is for the following types of label changes

* Adding a new Stage or Group
* Renaming an existing Stage or Group

For every case above, the Engineering Productivity team needs to ensure that:

* The label change is factored into the triage mechanism.
* Engineering Dashboards at <https://quality.gitlab.cherubits.hu> are updated.
* Old labels are migrated correctly on affected issues and merge requests.

### Action items

* [ ] (If applicable) Dashboard creation: create or update the stage/group in <https://analytics.cherubits.hu/master/lib/insights.rb>.
* [ ] (If applicable) Label migration on existing issues and merge requests: apply the new label to opened & closed issues, and open & merged merge requests.
* [ ] (If applicable) Archive the old label with renaming and adding "DEPRECATED" at the end of the label name.
* [ ] (If applicable) Delete the old dashboard views using the deprecated labels.
* [ ] (If applicable) Update the group triage package definition to use the new label


/cc @gl-quality/eng-prod
/label ~Quality ~"label change"
