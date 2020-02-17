---
name: Change category label
about: This issue tracking category changes.
title: "[CATEGORY-LABEL-CHANGE] "
labels: category-label-change
assignees: ${assignee1}
---

## Summary

This template is for new or renaming Category labels. This review helps to ensure there will be no impact with triage automation and reports.

### Action items

* [ ] Link the merge request to www-gitlab-com for the [category.yml](https://portal.cherubits.hu/blob/master/data/categories.yml) change
* [ ] (If applicable) Label migration on existing issues and merge requests: apply the new label to opened & closed issues, and open & merged merge requests.
* [ ] (If applicable) Rename the old label by adding `[DEPRECATED]` at the end of the label name, like ~"CI/CD [DEPRECATED]".


/cc @gl-quality/eng-prod
/label ~Quality ~"label change"
