# Security Policy

## Reporting a vulnerability

Please report privately, not in a public issue.

- **Preferred:** GitHub's private vulnerability reporting. Open the repository's
  **Security** tab and choose **Report a vulnerability**, or go straight to
  <https://github.com/distronode-corporation/updates/security/advisories/new>.
- **Fallback:** email **opensource@distronode.com** if you cannot use GitHub.

Include what you did, what happened, and what you expected. Never include a real token,
session or anyone's personal data. There is no paid bug bounty; what you get is credit
in the fix, if you want it.

## What protects an update

- Every feed item points at an asset of an **immutable GitHub Release** of the app,
  with a build provenance attestation (`gh attestation verify`).
- The app installs an update only if its **EdDSA signature** verifies against the
  public key built into the installed copy; the release workflow checks each signature
  against that key before it writes the item.
- Only the app's release workflow writes here, through a **deploy key scoped to this
  repository**, held as a secret of that workflow's protected `release` environment.

## Scope

In scope: a way to make a feed point an installed app at code not built and signed by
the app's own release workflow, to serve something other than this repository's
content at updates.distronode.com, or to write to this repository without the
maintainers' approval. Vulnerabilities in an app itself belong to that app's
repository (for District AI for macOS,
<https://github.com/distronode-corporation/district-macos/security/advisories/new>).
