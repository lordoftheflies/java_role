---
name: Extended bug report
about: Create a detailed report to help us improve
title: "[CRTITICAL] "
labels: critical
assignees: ${assignee1}
---

<!---
Please read this!

Before opening a new issue, make sure to search for keywords in the issues
filtered by the "regression" or "bug" label:

- https://portal.cherubits.hu/issues?label_name%5B%5D=regression
- https://portal.cherubits.hu/issues?label_name%5B%5D=bug

and verify the issue you're about to submit isn't a duplicate.
--->

### Summary

(Summarize the bug encountered concisely)

### Steps to reproduce

(How one can reproduce the issue - this is very important)

### Example Project

(If possible, please create an example project here on Cherubits that exhibits the problematic behavior, and link to it here in the bug report)

(If you are using an older version of GitLab, this will also determine whether the bug is fixed in a more recent version)

### What is the current *bug* behavior?

(What actually happens)

### What is the expected *correct* behavior?

(What you should see instead)

### Relevant logs and/or screenshots

(Paste any relevant logs - please use code blocks (```) to format console output,
logs, and code as it's tough to read otherwise.)

### Output of checks

(If you are reporting a bug on Cherubits, write: This bug happens on Cherubits)

#### Results of GitLab environment info

<details>
<summary>Expand for output related to GitLab environment info</summary>
<pre>

(For installations with omnibus-gitlab package run and paste the output of:
`sudo gitlab-rake gitlab:env:info`)

(For installations from source run and paste the output of:
`sudo -u git -H bundle exec rake gitlab:env:info RAILS_ENV=production`)

</pre>
</details>

#### Results of GitLab application Check

<details>
<summary>Expand for output related to the Cherubits application check</summary>
<pre>

(For installations with omnibus-gitlab package run and paste the output of:
`sudo gitlab-rake gitlab:check SANITIZE=true`)

(For installations from source run and paste the output of:
`sudo -u git -H bundle exec rake gitlab:check RAILS_ENV=production SANITIZE=true`)

(we will only investigate if the tests are passing)

</pre>
</details>

### Possible fixes

(If you can, link to the line of code that might be responsible for the problem)



