## Contributing

First off, thanks for taking the time to contribute!

The following is a set of guidelines for contributing to this repository. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

### I don't care about this whole thing, I just have a simple question!

If you need an answer, you can either:
  1. Open an issue and assign to it the `question` label, or
  2. If you need a faster response, either join [the Slack channel](https://cherubits.slack.com/) and get an invite then ask your question there

### How can I contribute?

#### Reporting bugs

Before reporting a bug, please make sure it hasn't already been reported by visiting the
[issue section](https://gitlab.cherubits.hu/%project_path%/issues).

If the bug you found hasn't been reported yet, create a new issue and assign it the proper label(s).
Besides this, there isn't any specific guideline on how the bugs should be reported, Just be sure
to be as clear as possible when describing it.

#### Suggesting enhancements

Same as the bug reporting. First of all, check if the enhancement has already been suggested.
If it doesn't exist, create a new issue and give it the `enhancement` label, plus any other proper label.

Keep in mind that what you may find useful might be completely useless for other users,
so please, make sure that the enhancement can actually be useful for everyone before proposing it.
If you find that it is actually useful only for you, consider forking the project and implementing that
enhancement just for yourself.

### Styleguides

#### Commit messages

This project follows the [Udacity Git Commit Message Style Guide](https://udacity.github.io/git-styleguide/) and [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/),
so make sure to read and use it properly. Besides that, also make sure to include `[ci skip]` or `[skip ci]`
in the commit title when only changing documentation.

#### Merge-Requests

  - Specify what has been changed/added/removed
  - Write a short and concise title. Be more specific in the description
  - Do not include issue numbers in the PR title
  - Be sure to follow all the project coding guidelines. TSLint will definitely give you a big help with this
  - End all files with a newline
  - Add configuration dependencies as devDependencies, and frontend dependencies as normal dependencies
  - Avoid platform-dependent code

#### Basic Code Review Checklist

Let’s discuss the basic code review checklist, which can be very handy if you are a beginner in code reviews and/or during initial code reviews.

While reviewing the code, ask yourself the following basic questions:

* Am I able to understand the code easily?
* Is the code written following the coding standards/guidelines?
* Is the same code duplicated more than twice?
* Can I unit test / debug the code easy to find the root cause?
* Is this function or class too big? If yes, is the function or class having too many responsibilities?
* If you feel that the answer is not satisfactory to any of the above questions, then you can suggest/recommend code changes.

More information: [Detailed Code Review Checklist]()