#!/usr/bin/env python3
"""
Actor Arsenal Sync Script
=========================
Syncs all Apify actors with the Actor Arsenal website.

Features:
- Fetches all actors from Apify API
- Compares with existing site actors
- Creates missing actor pages with full SEO
- Updates actors.json, sitemap.xml, and counts
- Handles Apify readme markdown conversion

Usage:
    python3 sync_actors.py
    python3 sync_actors.py --dry-run  # Preview changes without writing
"""

import json
import os
import sys
import re
import html
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.error

# Configuration
SITE_DIR = Path(__file__).parent
ACTORS_DIR = SITE_DIR / "actors"
ACTORS_JSON = SITE_DIR / "actors.json"
ACTORS_FULL_JSON = SITE_DIR / "actors-full.json"
SITEMAP_XML = SITE_DIR / "sitemap.xml"
INDEX_HTML = SITE_DIR / "index.html"
API_HTML = SITE_DIR / "api.html"

APIFY_API_BASE = "https://api.apify.com/v2"
APIFY_USERNAME = "alizarin_refrigerator-owner"
SITE_BASE_URL = "https://actor-arsenal-site.vercel.app"

# Get Apify token from environment (try both common names)
APIFY_TOKEN = os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN", "")


def fetch_apify_actors() -> list[dict]:
    """Fetch all actors from Apify API for the user."""
    actors = []
    offset = 0
    limit = 100

    print(f"Fetching actors from Apify API for {APIFY_USERNAME}...")

    while True:
        url = f"{APIFY_API_BASE}/acts?offset={offset}&limit={limit}&my=true"
        if APIFY_TOKEN:
            url += f"&token={APIFY_TOKEN}"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode())
                items = data.get("data", {}).get("items", [])

                if not items:
                    break

                actors.extend(items)
                print(f"  Fetched {len(actors)} actors so far...")

                if len(items) < limit:
                    break

                offset += limit
        except urllib.error.HTTPError as e:
            print(f"  API Error: {e.code} - {e.reason}")
            break
        except Exception as e:
            print(f"  Error fetching actors: {e}")
            break

    print(f"  Total actors found: {len(actors)}")
    return actors


def load_existing_actors() -> dict:
    """Load existing actors from actors.json."""
    if ACTORS_JSON.exists():
        with open(ACTORS_JSON, "r") as f:
            actors = json.load(f)
            return {a["id"]: a for a in actors}
    return {}


def fetch_actor_readme(actor_id: str) -> str:
    """Fetch the README content for an actor."""
    url = f"{APIFY_API_BASE}/acts/{actor_id}"
    if APIFY_TOKEN:
        url += f"?token={APIFY_TOKEN}"

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data.get("data", {}).get("readme", "") or ""
    except Exception as e:
        print(f"    Warning: Could not fetch readme for {actor_id}: {e}")
        return ""


def markdown_to_html(md: str) -> str:
    """Convert markdown to HTML (basic conversion)."""
    if not md:
        return ""

    lines = md.split("\n")
    html_lines = []
    in_code_block = False
    in_list = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                lang = line.strip()[3:] or ""
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(html.escape(line))
            continue

        # Headers
        if line.startswith("# "):
            html_lines.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("#### "):
            html_lines.append(f"<h4>{html.escape(line[5:])}</h4>")
        # Lists
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = line.strip()[2:]
            html_lines.append(f"<li>{html.escape(content)}</li>")
        elif line.strip().startswith(tuple(f"{i}. " for i in range(1, 20))):
            if not in_list:
                html_lines.append("<ol>")
                in_list = True
            content = re.sub(r"^\d+\.\s*", "", line.strip())
            html_lines.append(f"<li>{html.escape(content)}</li>")
        else:
            if in_list and line.strip() == "":
                html_lines.append("</ul>" if html_lines[-2].startswith("<ul>") or "<li>" in html_lines[-1] else "</ol>")
                in_list = False
            elif line.strip():
                html_lines.append(f"<p>{html.escape(line)}</p>")

    # Close any open lists
    if in_list:
        html_lines.append("</ul>")

    result = "\n".join(html_lines)

    # Convert inline markdown
    # Bold
    result = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", result)
    result = re.sub(r"__(.+?)__", r"<strong>\1</strong>", result)
    # Italic
    result = re.sub(r"\*(.+?)\*", r"<em>\1</em>", result)
    result = re.sub(r"_(.+?)_", r"<em>\1</em>", result)
    # Inline code
    result = re.sub(r"`(.+?)`", r"<code>\1</code>", result)
    # Links
    result = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', result)

    return result


def sanitize_slug(name: str) -> str:
    """Create a URL-safe slug from actor name."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def generate_actor_page(actor: dict, readme_html: str) -> str:
    """Generate a full HTML page for an actor."""
    actor_id = actor.get("id", "")
    name = actor.get("name", "")
    title = actor.get("title", name.replace("-", " ").title())
    description = actor.get("description", "")[:300]
    picture_url = actor.get("pictureUrl", "") or f"../images/{name}.png"
    categories = actor.get("categories", ["SCRAPER"])
    category = categories[0] if categories else "SCRAPER"

    # Escape for HTML/meta
    title_escaped = html.escape(title)
    desc_escaped = html.escape(description.replace("\n", " ")[:160])

    # Build the page
    template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_escaped} | Actor Arsenal</title>
    <meta name="description" content="{desc_escaped}">

    <!-- Canonical URL -->
    <link rel="canonical" href="{SITE_BASE_URL}/actors/{name}.html">
    <meta name="robots" content="index, follow">

    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{SITE_BASE_URL}/actors/{name}.html">
    <meta property="og:title" content="{title_escaped} | Actor Arsenal">
    <meta property="og:description" content="{desc_escaped}">
    <meta property="og:image" content="{picture_url}">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title_escaped}">
    <meta name="twitter:description" content="{desc_escaped[:100]}">

    <!-- Schema.org SoftwareApplication -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "{title_escaped}",
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Cloud (Apify Platform)",
        "description": "{desc_escaped}",
        "url": "{SITE_BASE_URL}/actors/{name}.html",
        "author": {{
            "@type": "Person",
            "name": "John Rippy"
        }},
        "offers": {{
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        }}
    }}
    </script>

    <!-- BreadcrumbList Schema -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {{
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "{SITE_BASE_URL}/"
            }},
            {{
                "@type": "ListItem",
                "position": 2,
                "name": "{title_escaped}",
                "item": "{SITE_BASE_URL}/actors/{name}.html"
            }}
        ]
    }}
    </script>

<link rel="icon" type="image/png" href="../images/logo.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0a0a0a;
            --bg-card: #111111;
            --bg-code: #1a1a2e;
            --accent-green: #00ff88;
            --accent-red: #ff3366;
            --accent-purple: #9933ff;
            --text-primary: #ffffff;
            --text-secondary: #888888;
            --border: #222222;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Space Grotesk', sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 0 2rem; }}
        nav {{
            position: fixed;
            top: 0; width: 100%;
            padding: 1rem 0;
            background: rgba(10, 10, 10, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            z-index: 1000;
        }}
        nav .container {{ display: flex; justify-content: space-between; align-items: center; max-width: 1400px; }}
        .logo {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--accent-green);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .logo-img {{ width: 40px; height: auto; image-rendering: pixelated; }}
        .nav-links {{ display: flex; gap: 2rem; align-items: center; }}
        .nav-links a {{ color: var(--text-secondary); text-decoration: none; transition: color 0.3s; }}
        .nav-links a:hover {{ color: var(--accent-green); }}
        .cta-button {{
            background: var(--accent-green);
            color: var(--bg-dark);
            padding: 0.5rem 1rem;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 600;
        }}
        .cta-button:hover {{ background: #00cc6a; }}
        .actor-header {{
            padding: 8rem 0 3rem;
            border-bottom: 1px solid var(--border);
        }}
        .actor-header-content {{
            display: flex;
            gap: 2rem;
            align-items: flex-start;
        }}
        .actor-icon {{
            width: 80px;
            height: 80px;
            border-radius: 12px;
            object-fit: cover;
        }}
        .actor-info {{ flex: 1; }}
        .actor-title {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        .actor-category {{
            display: inline-block;
            background: rgba(153, 51, 255, 0.2);
            color: var(--accent-purple);
            padding: 0.25rem 0.75rem;
            border-radius: 50px;
            font-size: 0.875rem;
            margin-bottom: 1rem;
        }}
        .actor-description {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }}
        .actor-actions {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
        }}
        .btn-primary {{
            background: var(--accent-green);
            color: var(--bg-dark);
        }}
        .btn-primary:hover {{ background: #00cc6a; }}
        .btn-secondary {{
            background: transparent;
            color: var(--accent-green);
            border: 1px solid var(--accent-green);
        }}
        .btn-secondary:hover {{ background: rgba(0, 255, 136, 0.1); }}
        .content {{
            padding: 3rem 0;
        }}
        .content h1, .content h2, .content h3, .content h4 {{
            color: var(--accent-green);
            margin: 2rem 0 1rem;
        }}
        .content h1 {{ font-size: 1.75rem; }}
        .content h2 {{ font-size: 1.5rem; }}
        .content h3 {{ font-size: 1.25rem; }}
        .content p {{ margin-bottom: 1rem; color: var(--text-secondary); }}
        .content ul, .content ol {{ margin: 1rem 0 1rem 2rem; color: var(--text-secondary); }}
        .content li {{ margin-bottom: 0.5rem; }}
        .content pre {{
            background: var(--bg-code);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            overflow-x: auto;
            margin: 1rem 0;
        }}
        .content code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
        }}
        .content a {{ color: var(--accent-green); }}
        .content strong {{ color: var(--text-primary); }}
        .content blockquote {{
            border-left: 3px solid var(--accent-purple);
            padding-left: 1rem;
            margin: 1rem 0;
            color: var(--text-secondary);
            font-style: italic;
        }}
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-secondary);
            text-decoration: none;
            margin-bottom: 2rem;
        }}
        .back-link:hover {{ color: var(--accent-green); }}
        footer {{
            border-top: 1px solid var(--border);
            padding: 2rem 0;
            text-align: center;
            color: var(--text-secondary);
        }}
        footer a {{ color: var(--accent-green); }}
        @media (max-width: 768px) {{
            .actor-header-content {{ flex-direction: column; }}
            .actor-icon {{ width: 60px; height: 60px; }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="../index.html" class="logo">
                <img src="../images/logo.png" alt="Actor Arsenal" class="logo-img">
                Actor Arsenal
            </a>
            <div class="nav-links">
                <a href="../index.html#actors">Actors</a>
                <a href="../api.html">API</a>
                <a href="https://apify.com/alizarin_refrigerator-owner" target="_blank" class="cta-button">View on Apify</a>
            </div>
        </div>
    </nav>

    <header class="actor-header">
        <div class="container">
            <a href="../index.html" class="back-link">
                &larr; Back to all actors
            </a>
            <div class="actor-header-content">
                <img src="{picture_url}" alt="{title_escaped}" class="actor-icon">
                <div class="actor-info">
                    <h1 class="actor-title">{title_escaped}</h1>
                    <span class="actor-category">{category}</span>
                    <p class="actor-description">{html.escape(description[:300])}</p>
                    <div class="actor-actions">
                        <a href="https://apify.com/alizarin_refrigerator-owner/{name}" target="_blank" class="btn btn-primary">Run on Apify</a>
                        <a href="https://apify.com/alizarin_refrigerator-owner/{name}/api" target="_blank" class="btn btn-secondary">View API</a>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <main class="content">
        <div class="container">
            {readme_html if readme_html else f"<p>This actor helps you {description.lower()}</p>"}
        </div>
    </main>

    <footer>
        <div class="container">
            <p>Actor Arsenal by <a href="https://apify.com/alizarin_refrigerator-owner">John Rippy</a> | 2025 Zapier Automation Hero</p>
        </div>
    </footer>
</body>
</html>'''

    return template


def update_actors_json(actors: list[dict]) -> None:
    """Update actors.json with all actors."""
    # Sort actors: featured first, then alphabetically
    featured_ids = {
        "LF3BPd0DBfXIgI0uA",  # god-mode-intel-mcp
        "RZYvUKdgTvtDbIdp5",  # god-mode-intel-mcp-v2
        "lHYBnEnMRiPkcPIoh",  # local-business-intelligence-suite
        "9xFBhFLdlWyXKRkLA",  # lbis-pro
    }

    simplified = []
    for actor in actors:
        simplified.append({
            "id": actor.get("id", ""),
            "name": actor.get("name", ""),
            "title": actor.get("title", actor.get("name", "").replace("-", " ").title()),
            "description": actor.get("description", ""),
            "pictureUrl": actor.get("pictureUrl", f"images/{actor.get('name', '')}.png"),
            "categories": actor.get("categories", ["SCRAPER"])
        })

    # Sort: featured first, then alphabetically by name
    simplified.sort(key=lambda x: (
        0 if x["id"] in featured_ids else 1,
        x["name"].lower()
    ))

    with open(ACTORS_JSON, "w") as f:
        json.dump(simplified, f, indent=2)

    print(f"  Updated actors.json with {len(simplified)} actors")


def update_sitemap(actors: list[dict]) -> None:
    """Update sitemap.xml with all actors."""
    today = datetime.now().strftime("%Y-%m-%d")

    urls = [
        f'''  <url>
    <loc>{SITE_BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>''',
        f'''  <url>
    <loc>{SITE_BASE_URL}/api.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>'''
    ]

    for actor in actors:
        name = actor.get("name", "")
        if name:
            urls.append(f'''  <url>
    <loc>{SITE_BASE_URL}/actors/{name}.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
  </url>''')

    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>'''

    with open(SITEMAP_XML, "w") as f:
        f.write(sitemap)

    print(f"  Updated sitemap.xml with {len(urls)} URLs")


def update_actor_count(count: int) -> None:
    """Update actor count in index.html and api.html."""
    for html_file in [INDEX_HTML, API_HTML]:
        if not html_file.exists():
            continue

        content = html_file.read_text()

        # Update various count patterns
        patterns = [
            (r'\d+ Apify Actors', f'{count} Apify Actors'),
            (r'\d+ battle-tested Apify actors', f'{count} battle-tested Apify actors'),
            (r'"description": "\d+', f'"description": "{count}'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        html_file.write_text(content)
        print(f"  Updated actor count in {html_file.name}")


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("DRY RUN MODE - No files will be modified\n")

    print("=" * 60)
    print("Actor Arsenal Sync Script")
    print("=" * 60)

    # Step 1: Fetch actors from Apify
    print("\n[1/5] Fetching actors from Apify API...")
    apify_actors = fetch_apify_actors()

    if not apify_actors:
        print("ERROR: No actors found from Apify API.")
        print("Make sure APIFY_TOKEN environment variable is set.")
        sys.exit(1)

    # Step 2: Load existing actors
    print("\n[2/5] Loading existing site actors...")
    existing = load_existing_actors()
    print(f"  Found {len(existing)} actors on site")

    # Step 3: Find missing actors
    print("\n[3/5] Comparing actors...")
    new_actors = []
    updated_actors = []

    for actor in apify_actors:
        actor_id = actor.get("id", "")
        if actor_id not in existing:
            new_actors.append(actor)
        else:
            updated_actors.append(actor)

    print(f"  New actors to add: {len(new_actors)}")
    print(f"  Existing actors to update: {len(updated_actors)}")

    if new_actors:
        print("\n  New actors:")
        for actor in new_actors[:10]:
            print(f"    - {actor.get('name', 'unknown')}")
        if len(new_actors) > 10:
            print(f"    ... and {len(new_actors) - 10} more")

    # Step 4: Generate missing pages
    print("\n[4/5] Generating actor pages...")

    if not dry_run:
        ACTORS_DIR.mkdir(exist_ok=True)

        for i, actor in enumerate(new_actors):
            name = actor.get("name", "")
            actor_id = actor.get("id", "")

            print(f"  Creating page for {name}...")

            # Fetch readme
            readme = fetch_actor_readme(actor_id)
            readme_html = markdown_to_html(readme)

            # Generate page
            page_html = generate_actor_page(actor, readme_html)

            # Write page
            page_path = ACTORS_DIR / f"{name}.html"
            page_path.write_text(page_html)

            print(f"    Created: actors/{name}.html")
    else:
        print("  [DRY RUN] Would create pages for new actors")

    # Step 5: Update JSON, sitemap, and counts
    print("\n[5/5] Updating site files...")

    all_actors = apify_actors

    if not dry_run:
        update_actors_json(all_actors)
        update_sitemap(all_actors)
        update_actor_count(len(all_actors))
    else:
        print(f"  [DRY RUN] Would update actors.json with {len(all_actors)} actors")
        print(f"  [DRY RUN] Would update sitemap.xml with {len(all_actors) + 2} URLs")
        print(f"  [DRY RUN] Would update actor count to {len(all_actors)}")

    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)
    print(f"\nTotal actors: {len(all_actors)}")
    print(f"New pages created: {len(new_actors)}")

    if not dry_run:
        print("\nNext steps:")
        print("  1. Review changes: git diff")
        print("  2. Commit: git add -A && git commit -m 'Sync actors'")
        print("  3. Deploy: git push")


if __name__ == "__main__":
    main()
