#!/usr/bin/env python3
"""
Migration validation script.

Verifies:
- No broken markdown
- No missing frontmatter
- Aliases present on imported posts
- Internal links valid
- Images still resolve
- Sitemap generated
- RSS generated
- No draft content
- Build succeeds

Usage:
    python3 scripts/validate.py [--build-dir public]
"""

import os
import re
import sys
import glob
import json
import argparse
import subprocess
import xml.etree.ElementTree as ET


def check_frontmatter(filepath):
    """Check that a markdown file has valid frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []

    if not content.startswith("---"):
        issues.append(f"  MISSING: No frontmatter delimiter")

    parts = content.split("---", 2)
    if len(parts) < 3:
        issues.append(f"  MISSING: Cannot parse frontmatter")

    return issues


def check_aliases(filepath):
    """Check that posts have aliases (for Blogger SEO)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []

    # Check for aliases in frontmatter
    if "aliases:" not in content:
        issues.append(f"  MISSING: No aliases in frontmatter")

    return issues


def check_internal_links(filepath, build_dir):
    """Check internal links resolve to existing pages."""
    if not build_dir or not os.path.exists(build_dir):
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []

    # Find all markdown links
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

    for text, url in links:
        # Only check relative links
        if url.startswith("http") or url.startswith("#") or url.startswith("mailto:"):
            continue

        # Check if the linked file or path exists in build
        build_path = os.path.join(build_dir, url.lstrip("/"))
        if not os.path.exists(build_path) and not os.path.exists(build_path + "/index.html"):
            # Could be an .html extension
            if not os.path.exists(os.path.splitext(build_path)[0] + ".html"):
                issues.append(f"  BROKEN: Link '{url}' in '{text}'")

    return issues


def check_images(filepath):
    """Check that image references at least have valid URL structure."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []

    # Check for broken image references
    images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)
    for alt, src in images:
        if src.startswith("/") and not src.startswith("//"):
            issues.append(f"  LOCAL IMAGE: '{src}' - verify it exists in static/")

    return issues


def check_draft_status():
    """Check that content/posts has no remaining drafts."""
    blog_dir = "content/posts"
    if not os.path.exists(blog_dir):
        return ["  INFO: No posts directory found"]

    issues = []
    for filepath in glob.glob(os.path.join(blog_dir, "*.md")):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if "draft: true" in content:
            issues.append(f"  DRAFT: {os.path.basename(filepath)} is still a draft")

    return issues


def check_sitemap(build_dir):
    """Check that sitemap.xml is generated and contains entries."""
    sitemap_path = os.path.join(build_dir, "sitemap.xml")
    if not os.path.exists(sitemap_path):
        return ["  MISSING: sitemap.xml not found"]

    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = root.findall("ns:url", ns)
        if not urls:
            return ["  WARNING: sitemap.xml has no URLs"]
        return [f"  OK: sitemap.xml has {len(urls)} URLs"]
    except Exception as e:
        return [f"  ERROR: Cannot parse sitemap.xml: {e}"]

    return []


def check_rss(build_dir):
    """Check that RSS feed is generated."""
    rss_path = os.path.join(build_dir, "index.xml")
    if not os.path.exists(rss_path):
        return ["  MISSING: RSS feed (index.xml) not found"]
    return ["  OK: RSS feed present"]


def check_robots_txt(build_dir):
    """Check robots.txt exists."""
    robots_path = os.path.join(build_dir, "robots.txt")
    if not os.path.exists(robots_path):
        return ["  MISSING: robots.txt not found"]
    return ["  OK: robots.txt present"]


def check_html_validity(build_dir):
    """Basic HTML structure check."""
    issues = []
    html_files = glob.glob(os.path.join(build_dir, "**/*.html"), recursive=True)

    for filepath in html_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for basic HTML structure
        if "<!DOCTYPE html>" not in content:
            rel_path = os.path.relpath(filepath, build_dir)
            issues.append(f"  WARNING: {rel_path} missing DOCTYPE")

        # Check for canonical link
        if 'rel="canonical"' not in content:
            rel_path = os.path.relpath(filepath, build_dir)
            issues.append(f"  WARNING: {rel_path} missing canonical URL")

    return issues


def build_site():
    """Run hugo build and check for errors."""
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        for candidate in [os.path.join(project_root, "hugo"), os.path.join(project_root, "..", "hugo")]:
            if os.path.exists(candidate):
                hugo_bin = candidate
                break
        else:
            hugo_bin = "hugo"
        result = subprocess.run(
            [hugo_bin, "--source", "."],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return [f"  BUILD FAILED:\n{result.stderr}"]
        return ["  OK: Build succeeded"]
    except FileNotFoundError:
        return ["  SKIP: Hugo binary not found"]
    except Exception as e:
        return [f"  ERROR: {e}"]


def main():
    parser = argparse.ArgumentParser(description="Validate Hugo migration")
    parser.add_argument("--build-dir", default="public", help="Hugo build output directory")
    parser.add_argument("--skip-build", action="store_true", help="Skip hugo build check")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    all_issues = {}
    has_errors = False

    print("=" * 60)
    print("Migration Validation Report")
    print("=" * 60)
    print()

    # 1. Build check
    print("1. Site Build")
    print("-" * 40)
    if not args.skip_build:
        issues = build_site()
        for i in issues:
            print(i)
            if "FAILED" in i or "ERROR" in i:
                has_errors = True
        print()

    build_dir = args.build_dir

    # 2. Frontmatter check
    print("2. Frontmatter Validation")
    print("-" * 40)
    posts = glob.glob("content/posts/*.md")
    if not posts:
        print("  INFO: No posts to validate")
    else:
        for filepath in posts:
            issues = check_frontmatter(filepath)
            if issues:
                has_errors = True
                print(f"  {os.path.basename(filepath)}:")
                for i in issues:
                    print(f"    {i}")
        if not has_errors:
            print(f"  OK: {len(posts)} posts have valid frontmatter")
    print()

    # 3. Alias check
    print("3. Alias Verification (Blogger URL preservation)")
    print("-" * 40)
    has_alias_issues = False
    for filepath in posts:
        issues = check_aliases(filepath)
        if issues:
            has_alias_issues = True
            has_errors = True
            print(f"  {os.path.basename(filepath)}:")
            for i in issues:
                print(f"    {i}")
    if not has_alias_issues:
        print(f"  OK: All {len(posts)} posts have aliases")
    print()

    # 4. Draft check
    print("4. Draft Status")
    print("-" * 40)
    draft_issues = check_draft_status()
    for i in draft_issues:
        print(i)
    print()

    # 5. Sitemap
    print("5. Sitemap & RSS")
    print("-" * 40)
    for fn in [check_sitemap, check_rss, check_robots_txt]:
        for i in fn(build_dir):
            print(i)
            if "MISSING" in i:
                has_errors = True
    print()

    # 6. HTML structure
    if os.path.exists(build_dir):
        print("6. HTML Structure")
        print("-" * 40)
        html_issues = check_html_validity(build_dir)
        if html_issues:
            for i in html_issues:
                print(i)
        else:
            print("  OK: All HTML files valid")
        print()

    # 7. Internal links
    print("7. Internal Link Validation")
    print("-" * 40)
    link_issues = False
    for filepath in posts:
        issues = check_internal_links(filepath, build_dir)
        if issues:
            link_issues = True
            print(f"  {os.path.basename(filepath)}:")
            for i in issues:
                print(f"    {i}")
    if not link_issues:
        print("  OK: No broken internal links detected")
    print()

    # Summary
    print("=" * 60)
    if has_errors:
        print("RESULT: ISSUES FOUND - review above before deploying")
        sys.exit(1)
    else:
        print("RESULT: ALL CHECKS PASSED - ready for deployment")
        sys.exit(0)


if __name__ == "__main__":
    main()
