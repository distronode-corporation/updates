#!/usr/bin/env python3
"""Check every Sparkle appcast in this repository.

    python3 .github/scripts/check-feeds.py              # check every **/appcast.xml
    python3 .github/scripts/check-feeds.py --self-test  # prove each rule fires

A feed is refused when it is not well-formed XML, is not an RSS 2.0 document with one
channel, or has an item that lacks a field Sparkle needs: `sparkle:version` (digits),
`sparkle:shortVersionString`, `sparkle:minimumSystemVersion`, `pubDate`, and an
`enclosure` whose `url` is a download from a GitHub Release of this organisation, with
a byte `length`, a `type` and a base64 Ed25519 `sparkle:edSignature`. Builds must be
unique and listed newest first, which is the order the release workflow writes.

Standard library only, so it runs on any runner without an install step.
"""

from __future__ import annotations

import re
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SPARKLE = "http://www.andymatuschak.org/xml-namespaces/sparkle"
S = f"{{{SPARKLE}}}"
RELEASE_URL = re.compile(
    r"https://github\.com/distronode-corporation/[A-Za-z0-9._-]+/releases/download/v[0-9][0-9.]*/[A-Za-z0-9._-]+\.dmg"
)
SIGNATURE = re.compile(r"[A-Za-z0-9+/]{86}==")


def check_feed(path: Path) -> list[str]:
    """Every problem with one feed, or an empty list."""
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        return [f"{path}: not well-formed XML ({error})"]
    problems: list[str] = []
    if root.tag != "rss" or root.get("version") != "2.0":
        problems.append(f"{path}: the root is not <rss version=\"2.0\">")
    channels = root.findall("channel")
    if len(channels) != 1:
        return problems + [f"{path}: expected one <channel>, found {len(channels)}"]
    channel = channels[0]
    for name in ("title", "link", "description"):
        if not (channel.findtext(name) or "").strip():
            problems.append(f"{path}: the channel has no <{name}>")
    builds: list[int] = []
    for index, item in enumerate(channel.findall("item"), start=1):
        where = f"{path}: item {index}"
        version = (item.findtext(f"{S}version") or "").strip()
        if not version.isdigit():
            problems.append(f"{where}: sparkle:version '{version}' is not a build number")
        else:
            builds.append(int(version))
        for name in ("shortVersionString", "minimumSystemVersion"):
            if not (item.findtext(f"{S}{name}") or "").strip():
                problems.append(f"{where}: no sparkle:{name}")
        for name in ("title", "pubDate"):
            if not (item.findtext(name) or "").strip():
                problems.append(f"{where}: no <{name}>")
        enclosures = item.findall("enclosure")
        if len(enclosures) != 1:
            problems.append(f"{where}: expected one <enclosure>, found {len(enclosures)}")
            continue
        enclosure = enclosures[0]
        if not RELEASE_URL.fullmatch(enclosure.get("url", "")):
            problems.append(f"{where}: enclosure url '{enclosure.get('url', '')}' is not a GitHub Release .dmg")
        if not enclosure.get("length", "").isdigit() or enclosure.get("length") == "0":
            problems.append(f"{where}: enclosure length '{enclosure.get('length', '')}' is not a size in bytes")
        if not enclosure.get("type"):
            problems.append(f"{where}: enclosure has no type")
        if not SIGNATURE.fullmatch(enclosure.get(f"{S}edSignature", "")):
            problems.append(f"{where}: enclosure sparkle:edSignature is not a base64 Ed25519 signature")
    if len(set(builds)) != len(builds):
        problems.append(f"{path}: a build is listed twice")
    if builds != sorted(builds, reverse=True):
        problems.append(f"{path}: items are not newest first")
    return problems


def check_tree(root: Path) -> list[str]:
    feeds = sorted(root.rglob("appcast.xml"))
    problems: list[str] = []
    if not feeds:
        problems.append(f"{root}: no appcast.xml anywhere")
    for feed in feeds:
        problems += check_feed(feed)
    cname = root / "CNAME"
    if not cname.is_file() or cname.read_text().strip() != "updates.distronode.com":
        problems.append("CNAME is not 'updates.distronode.com', which the Pages custom domain needs")
    if not (root / ".nojekyll").is_file():
        problems.append(".nojekyll is missing, so Pages would run Jekyll over the feeds")
    return problems


GOOD_ITEM = """
    <item>
      <title>Version 1.1</title>
      <pubDate>Mon, 05 Oct 2026 12:00:00 +0000</pubDate>
      <sparkle:version>{build}</sparkle:version>
      <sparkle:shortVersionString>1.1</sparkle:shortVersionString>
      <sparkle:minimumSystemVersion>14.0</sparkle:minimumSystemVersion>
      <enclosure url="https://github.com/distronode-corporation/district-macos/releases/download/v1.1/DistrictAI-1.1-{build}.dmg"
        length="1234" type="application/octet-stream" sparkle:edSignature="{sig}"/>
    </item>"""


def _feed(*items: str) -> str:
    return (
        f'<?xml version="1.0" encoding="utf-8"?>\n<rss xmlns:sparkle="{SPARKLE}" version="2.0"><channel>'
        "<title>t</title><link>https://updates.distronode.com/x.xml</link><description>d</description>"
        + "".join(items)
        + "</channel></rss>\n"
    )


def self_test() -> int:
    sig = "A" * 86 + "=="
    cases = {
        "empty channel": (_feed(), True),
        "one good item": (_feed(GOOD_ITEM.format(build=20030, sig=sig)), True),
        "newest first": (_feed(GOOD_ITEM.format(build=20031, sig=sig), GOOD_ITEM.format(build=20030, sig=sig)), True),
        "oldest first": (_feed(GOOD_ITEM.format(build=20030, sig=sig), GOOD_ITEM.format(build=20031, sig=sig)), False),
        "duplicate build": (_feed(GOOD_ITEM.format(build=20030, sig=sig), GOOD_ITEM.format(build=20030, sig=sig)), False),
        "bad signature": (_feed(GOOD_ITEM.format(build=20030, sig="short")), False),
        "foreign url": (_feed(GOOD_ITEM.format(build=20030, sig=sig).replace("github.com/distronode-corporation", "example.com")), False),
        "no build": (_feed(GOOD_ITEM.format(build="", sig=sig)), False),
        "not xml": ("<rss><channel>", False),
    }
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, (text, ok) in cases.items():
            path = Path(tmp) / "appcast.xml"
            path.write_text(text)
            problems = check_feed(path)
            if (not problems) != ok:
                failures += 1
                print(f"SELF-TEST FAILED - {name}: expected {'no problems' if ok else 'a problem'}, got {problems}")
            else:
                print(f"self-test ok - {name}")
    return 1 if failures else 0


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
    problems = check_tree(ROOT)
    for problem in problems:
        print(f"FATAL - {problem}")
    if not problems:
        for feed in sorted(ROOT.rglob("appcast.xml")):
            count = len(ET.parse(feed).getroot().findall("channel/item"))
            print(f"{feed.relative_to(ROOT)}: well-formed, {count} item(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
