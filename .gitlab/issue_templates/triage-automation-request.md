---
name: Triage automation request
about: Automation of triage step.
title: "[TRIAGE-AUTOMATION-REQUEST] "
labels: triage-automation-request
assignees: ${assignee1}
---


## Summary

This issue is for requesting triage automation on a given project. Please link to the project needed and select from a list of triage automation rules to be added.

Project: LINK_TO_PROJECT

* Automation that does not require an assignee.
  * Rescheduling of milestones (milestone grooming)
  * Labelling ~"missed-deliverable" and `missed:x.y` based on the scheduled milestone.
  * Labelling ~"bug" on ~"regression" and on `regression:x.y`.
  * Labelling ~"Accepting merge requests" for unassigned issues with a milestone.
  * Labelling ~"P1" and ~"S1" on ~"master:broken".
  * Labelling ~"missed-SLO" on issues with ~"bug" past SLO priority target.
  * Discovery of potential and popular proposals.
  * Remind people to add labels if an issue has no labels.
* [ ] Triage packages
   * Unlabelled issue triage packages, please list assignee: ASSIGNEE_NEEDED
   * Community Merge Requests, please list coaches: COACHES_LIST
   * Group triage packages
* WIP: Infer stage and group labels from subject labels
