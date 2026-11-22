# Security model

How the update feeds here protect the people who install updates from them. To report a
vulnerability, see [SECURITY.md](SECURITY.md).

## EdDSA signatures on every update

Each item in a feed (for example `district/macos/appcast.xml`) carries a
`sparkle:edSignature` on its `<enclosure>`: an Ed25519 signature over the `.dmg` it
points at. An installed copy of the app installs an update only if that signature
verifies against the EdDSA public key built into the app it shipped with. The public
key lives in the app, in its own repository
([district-macos](https://github.com/distronode-corporation/district-macos) for
District AI for Mac), not in this repository, so a change to a feed alone cannot make
the app install anything.

## How a feed is written

- Only the app's release workflow (district-macos's `publish.yml`) writes a feed, after
  the maintainers approve the release. It pushes here with a deploy key that can write
  to this repository only.
- Before it pushes, the workflow checks each new item against the key built into the
  app.
- Each item points at a `.dmg` on an immutable GitHub Release of the app.
- Nobody edits a feed by hand, and pull requests that change a feed are not accepted.

## Checks in this repository

[`check.yml`](.github/workflows/check.yml) runs `.github/scripts/check-feeds.py` on every
push and pull request. It refuses a feed that is not well-formed RSS 2.0, or has an
item without a build number, a GitHub Release `.dmg` URL of this organisation, a byte
length, or a base64 Ed25519 `sparkle:edSignature`. These checks report after a push to
`main` rather than gate it, because the release workflow pushes with a deploy key; the
release workflow runs the same feed checks itself before it pushes.

## Checking a download yourself

```sh
gh attestation verify DistrictAI-<version>-<build>.dmg --repo distronode-corporation/district-macos
```
