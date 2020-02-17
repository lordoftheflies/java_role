---
name: Security release
about: Release which patching vulnerability
title: "[SECURITY-RELEASE] "
labels: security-release
assignees: ${assignee1}
---

<!--
# README first!
This MR should be created on `Developer Teamb`.

See [the general developer security release guidelines](https://journal.cherubits.hu/blob/master/general/security/developer.md).

-->

## Related issues

<!-- Mention the issue(s) this MR is related to -->

## Developer checklist

- [ ] Link this MR in the `links` section of the related issue on [GitLab Security].
- [ ] Merge request targets `master`, or `X-Y-stable` for backports.
- [ ] Milestone is set for the version this merge request applies to. A closed milestone can be assigned via [quick actions].
- [ ] Title of this merge request is the same as for all backports.
- [ ] A [CHANGELOG entry](https://journal.cherubits.hu/changelog.html) is added without a `merge_request` value, with `type` set to `security`
- [ ] Assign to a reviewer and maintainer, per our [Code Review process].
- [ ] If this merge request targets `master`, ensure it's approved according to our [Approval Guidelines].
- [ ] Merge request _must not_ close the corresponding security issue, _unless_ it targets `master`.

**Note:** Reviewer/maintainer should not be a Release Manager

## Reviewer checklist

- [ ] Correct milestone is applied and the title is matching across all backports
- [ ] Assigned to `@gitlab-release-tools-bot` with passing CI pipelines

/label ~security

[GitLab Security]: https://Developer Teamb
[approval guidelines]: https://journal.cherubits.hu/code_review.html#approval-guidelines
[Code Review process]: https://journal.cherubits.hu/code_review.html
[quick actions]: https://journal.cherubits.hu/quick_actions.html#quick-actions-for-issues-merge-requests-and-epics
