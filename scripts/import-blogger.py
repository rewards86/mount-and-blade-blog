#!/usr/bin/env python3
"""
Blogger-to-Hugo import script for Google Takeout Atom format.

Usage:
    python3 scripts/import-blogger.py feed.atom

Expects Google Takeout format with:
    <blogger:type>POST</blogger:type>
    <blogger:filename>/2023/01/slug.html</blogger:filename>
    <category term="TagName"/>

Output:
    content/posts/*.md
"""

import sys
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from html import unescape

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "blogger": "http://schemas.google.com/blogger/2018",
}


def slug_from_path(path):
    name = path.rstrip("/").split("/")[-1]
    name = re.sub(r"\.html?$", "", name)
    name = re.sub(r"[^a-z0-9\s-]", "", name.lower().strip())
    name = re.sub(r"[\s_]+", "-", name)
    name = re.sub(r"-+", "-", name)
    return name[:80].rstrip("-")


def format_content(html_content):
    if not html_content:
        return ""
    return html_content.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/import-blogger.py feed.atom")
        sys.exit(1)

    xml_path = sys.argv[1]
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "content", "posts")
    os.makedirs(output_dir, exist_ok=True)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    entries = root.findall("atom:entry", NS)

    imported = 0
    skipped = 0
    skipped_no_filename = 0

    for entry in entries:
        # Only process POST type entries
        entry_type = entry.find("blogger:type", NS)
        if entry_type is None or entry_type.text != "POST":
            continue

        # Title
        title_el = entry.find("atom:title", NS)
        title = title_el.text.strip() if title_el is not None and title_el.text else ""

        if not title:
            skipped += 1
            continue

        # Filename for URL
        fn_el = entry.find("blogger:filename", NS)
        filename_path = fn_el.text.strip() if fn_el is not None and fn_el.text else ""

        if not filename_path:
            skipped_no_filename += 1
            continue

        # Published date
        published_el = entry.find("atom:published", NS)
        pub_date = None
        if published_el is not None and published_el.text:
            try:
                pub_date = datetime.strptime(published_el.text[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass

        if pub_date is None:
            pub_date = datetime.now()

        # Updated date
        updated_el = entry.find("atom:updated", NS)
        updated_date = None
        if updated_el is not None and updated_el.text:
            try:
                updated_date = datetime.strptime(updated_el.text[:19], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                pass

        # Content
        content_el = entry.find("atom:content", NS)
        content = format_content(content_el.text if content_el is not None and content_el.text else "")

        # Categories/Tags (from term attribute)
        tags = []
        for cat in entry.findall("atom:category", NS):
            term = cat.get("term", "")
            if term:
                tags.append(term)

        # Extract slug and alias from filename
        slug = slug_from_path(filename_path)
        year = pub_date.strftime("%Y")
        month = pub_date.strftime("%m")

        # Reconstruct original URL for alias
        alias_path = f"/{year}/{month}/{slug}.html"

        # Build frontmatter
        frontmatter = []
        frontmatter.append("---")
        frontmatter.append(f'title: "{title}"')
        frontmatter.append(f"date: {pub_date.isoformat()}")

        if updated_date:
            frontmatter.append(f"lastmod: {updated_date.isoformat()}")

        if tags:
            frontmatter.append("tags:")
            for tag in tags:
                frontmatter.append(f"  - {tag}")

        frontmatter.append(f"slug: \"{slug}\"")

        frontmatter.append("aliases:")
        frontmatter.append(f"  - {alias_path}")

        frontmatter.append("draft: false")
        frontmatter.append("---")
        frontmatter.append("")

        # Write file
        filename = f"{slug}.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(frontmatter))
            if content:
                f.write("\n")
                f.write(content)
                f.write("\n")

        imported += 1
        print(f"  {filename:55s} → {alias_path}")

    print(f"\nDone. {imported} posts imported, {skipped} skipped (no title), {skipped_no_filename} skipped (no filename).")
    print(f"Output: {output_dir}/")


if __name__ == "__main__":
    main()
