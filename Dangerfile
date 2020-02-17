warn "#{gitlab.html_link("package.json")} was edited." if git.modified_files.include? "package.json"

warn "#{gitlab.html_link("package-lock.json")} was edited." if git.modified_files.include? "package-lock.json"


if git.modified_files.include? "config/*.js"
  config_files = git.modified_files.select { |path| path.include? "config/" }
  message "This MR changes #{ gitlab.html_link(config_files) }"
end

message "Welcome, Lordoftheflies." if gitlab.mr_author == "lordoftheflies"

can_merge = gitlab.mr_json["mergeable"]
warn("This MR cannot be merged yet.") unless can_merge

has_milestone = gitlab.mr_json["milestone"] != nil
warn("This MR does not refer to an existing milestone", sticky: true) unless has_milestone

failure "Please re-submit this MR to develop, we may have already fixed your issue." if gitlab.branch_for_merge != "develop"

failure "Please provide a summary in the Merge Request description" if gitlab.mr_body.length < 5

warn "This MR does not have any assignees yet." unless gitlab.mr_json["assignee"]

failure "Please add labels to this MR" if gitlab.mr_labels.empty?

declared_trivial = (gitlab.mr_title + gitlab.mr_body).include?("#trivial")

warn "MR is classed as Work in Progress" if gitlab.mr_title.include? "[WIP]"
