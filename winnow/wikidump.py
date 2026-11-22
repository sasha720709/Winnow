"""Stream articles out of a Wikipedia XML dump (.xml.bz2).

Plumbing, written by Claude at Sasha's request (see README). It only hands
out raw (id, title, wikitext) per article; cleaning the markup is Sasha's.

Usage:
    python -m winnow.wikidump data/enwiki-latest-pages-articles1.xml-....bz2 5
"""

import bz2
import sys
import xml.etree.ElementTree as ET


def iter_articles(path):
    """Yield (page_id, title, wikitext) for every real article in the dump.

    Skips pages outside the main namespace (talk, user, category, ...)
    and redirects. Reads the file as a stream, so memory stays flat no
    matter how big the dump is.
    """
    with bz2.open(path, "rb") as f:
        # "start" events are needed only to grab the root element once.
        events = ET.iterparse(f, events=("start", "end"))
        _, root = next(events)

        # Every tag carries the namespace from the root, for example
        # "{http://www.mediawiki.org/xml/export-0.11/}page".
        ns = root.tag[: root.tag.index("}") + 1]
        page_tag = ns + "page"

        for event, elem in events:
            if event != "end" or elem.tag != page_tag:
                continue

            # The <page> is complete here: all its children are inside.
            is_article = elem.findtext(ns + "ns") == "0"
            is_redirect = elem.find(ns + "redirect") is not None
            if is_article and not is_redirect:
                page_id = int(elem.findtext(ns + "id"))
                title = elem.findtext(ns + "title")
                text = elem.findtext(f"{ns}revision/{ns}text") or ""
                yield page_id, title, text

            # Free memory: drop this page's contents, and drop the root's
            # reference to it (the root keeps every child it has seen).
            elem.clear()
            root.clear()


def main():
    path = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    for i, (page_id, title, text) in enumerate(iter_articles(path)):
        if i == limit:
            break
        print(f"[{page_id}] {title}  ({len(text):,} chars)")
        print(text[:200].replace("\n", " "))
        print()


if __name__ == "__main__":
    main()
