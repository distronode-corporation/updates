# Contributing

The feeds here are written by the apps' release workflows, never by hand, so this
repository does not take pull requests that change a feed: a hand-edited item would
point installed apps at a release the workflow did not check. A change to the
repository itself (this documentation, the checks in `.github/workflows/`) is welcome
as a pull request.

Every pull request and every push to `main` runs [`check.yml`](.github/workflows/check.yml):

- every feed is well-formed and every item carries the fields Sparkle needs, with its
  download on a GitHub Release of the app;
- `CNAME` and `.nojekyll` are in place;
- no em or en dashes in any file (use commas, periods or parentheses);
- `zizmor` over the workflows and `gitleaks` over the history.

Bugs in an app or its updates go to that app's repository; see [SUPPORT](.github/SUPPORT.md).
