# Roadmap

This roadmap covers the next twelve months, to November 2027.

This repository serves the Sparkle update feeds of Distronode's desktop apps from
`updates.distronode.com`. The feeds are written by the apps' release workflows, so the
plan is about keeping that path safe and checked.

## Planned

- Keep `check.yml` passing on every push and pull request: every feed well-formed with
  the fields Sparkle needs and its download URL in the form of a GitHub Release asset (the
  check reads the URL's form; it does not fetch the download), `CNAME` and
  `.nojekyll` in place, no em or en dashes, zizmor and gitleaks.
- Add a feed when another Distronode desktop app ships a direct download that updates
  with Sparkle, written by that app's release workflow the same way.

## Not planned

- Hand-edited feeds, or pull requests that change a feed.
- Downloads hosted here: every feed item points at a `.dmg` on a GitHub Release of the
  app.
- A feed for the Mac App Store build; the App Store updates it.
- Content at the root of `updates.distronode.com`.
