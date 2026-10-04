[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/distronode-corporation/updates/badge)](https://scorecard.dev/viewer/?uri=github.com/distronode-corporation/updates)

# Distronode update feeds

The update feeds of Distronode's desktop apps, served by GitHub Pages at
<https://updates.distronode.com>. Each feed is a [Sparkle](https://sparkle-project.org)
appcast: the list of releases an installed copy checks for updates.

| App | Feed | Releases |
|---|---|---|
| District AI for macOS (direct download) | <https://updates.distronode.com/district/macos/appcast.xml> | [district-macos Releases](https://github.com/distronode-corporation/district-macos/releases) |

The Mac App Store build of District AI does not use this feed; the App Store updates it.

## How a feed is written

Nobody edits a feed by hand. The app's release workflow (district-macos's
[`publish.yml`](https://github.com/distronode-corporation/district-macos/blob/main/.github/workflows/publish.yml))
adds one item per release once the maintainers have approved it, and pushes the result
here with a deploy key that can write to this repository only. Each item points at a
`.dmg` attached to an immutable GitHub Release of the app, carries the update's EdDSA
signature, and is checked against the key built into the app before it is pushed.

An installed copy trusts an update only if its EdDSA signature verifies against the
public key it shipped with, so a change to a feed alone cannot make the app install
anything. To check a download yourself:

```sh
gh attestation verify DistrictAI-<version>-<build>.dmg --repo distronode-corporation/district-macos
```

## Layout

```
CNAME                      updates.distronode.com, the Pages custom domain
.nojekyll                  serve the files as they are, without a Jekyll build
district/macos/appcast.xml District AI for macOS
```

## Contributing, security and conduct

- [SECURITY.md](SECURITY.md): report vulnerabilities privately, not in an issue.
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- [SUPPORT](.github/SUPPORT.md): where questions, bugs and account problems go.

Bugs in an app's updates belong to that app's repository, for District AI for macOS
[district-macos](https://github.com/distronode-corporation/district-macos/issues).
Questions about a District AI account, number or bill go to
[District AI support](https://www.distronode.com/support).

## License and trademarks

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

District AI, Distronode and the District AI and Distronode logos and app icons are
trademarks of Distronode Corporation. They are not licensed under the Apache License 2.0.
