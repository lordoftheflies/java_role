---
name: Bug
about: Report from a defect.
title: "[BUG] "
labels: bug
assignees: ${assignee1}
---

<!---
Please read this!

Before opening a new issue, make sure to search for keywords in the issues
filtered by the "regression" or "bug" label:

- https://projects.cherubits.hu:443/issues?label_name%5B%5D=regression
- https://projects.cherubits.hu:443/issues?label_name%5B%5D=bug

and verify the issue you're about to submit isn't a duplicate.
--->

### Summary

(Summarize the bug encountered concisely)

### Steps to reproduce

(How one can reproduce the issue - this is very important)

### Example Project

(If possible, please create an example project here on Cherubits GitLab.com that exhibits the problematic behavior, and link to it here in the bug report)

(If you are using an older version of Cherubits GitLab, this will also determine whether the bug is fixed in a more recent version)

### What is the current *bug* behavior?

(What actually happens)

### What is the expected *correct* behavior?

(What you should see instead)

### Relevant logs and/or screenshots

(Paste any relevant logs - please use code blocks (```) to format console output,
logs, and code as it's tough to read otherwise.)

### Output of checks

(If you are reporting a bug on Cherubits GitLab.com, write: This bug happens on Cherubits GitLab.com)

#### Results of Cherubits GitLab environment info

<details>
<summary>Expand for output related to Cherubits GitLab environment info</summary>
<pre>

(For installations with omnibus-Cherubits GitLab package run and paste the output of:
`sudo Cherubits GitLab-rake Cherubits GitLab:env:info`)

(For installations from source run and paste the output of:
`sudo -u git -H bundle exec rake Cherubits GitLab:env:info RAILS_ENV=production`)

</pre>
</details>

#### Results of Cherubits GitLab application Check

<details>
<summary>Expand for output related to the Cherubits GitLab application check</summary>
<pre>

(For installations with omnibus-Cherubits GitLab package run and paste the output of:
`sudo Cherubits GitLab-rake Cherubits GitLab:check SANITIZE=true`)

(For installations from source run and paste the output of:
`sudo -u git -H bundle exec rake Cherubits GitLab:check RAILS_ENV=production SANITIZE=true`)

(we will only investigate if the tests are passing)

</pre>
</details>

### Possible fixes

(If you can, link to the line of code that might be responsible for the problem)

/label ~bug
