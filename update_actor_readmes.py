#!/usr/bin/env python3
"""
Update Actor Arsenal HTML pages with updated README content from Apify actors.
Converts Markdown to HTML and replaces the content section in each actor page.
"""

import os
import re
import json
from pathlib import Path

# Mapping of local folder names to Actor Arsenal HTML file names
ACTOR_MAPPING = {
    'linkedin-profile-scraper': 'linkedin-profile-scraper.html',
    'linkedin-post-scraper': 'linkedin-post-scraper.html',
    'tiktok-scraper': 'tiktok-creator-video-scraper.html',
    'glassdoor-scraper': 'glassdoor-scraper.html',
    'yelp-scraper': 'yelp-scraper.html',
    'reddit-scraper': 'reddit-scraper.html',
    'youtube-scraper': 'youtube-channel-video-scraper.html',
    'google-maps-scraper': 'google-maps-scraper.html',
    'google-serp-scraper': 'google-serp-scraper.html',
    'local-seo-mcp-server': 'local-seo-mcp-server.html',
    'semrush-keyword-research': 'semrush-keyword-research---volume-difficulty-related.html',
    'airtable-api': 'airtable-api---database-records-automation.html',
    'notion-api': 'notion-api---database-page-automation.html',
    'firecrawl-website-crawler': 'firecrawl-website-crawler.html',
    'firecrawl-site-mapper': 'firecrawl-site-mapper.html',
    'fire-enrich': 'fire-enrich.html',
    'firecrawl-agent': 'firecrawl-agent.html',
}

APIFY_ACTORS_DIR = Path('/Users/jrippy/seo-dashboard-app/apify-actors')
ARSENAL_ACTORS_DIR = Path('/Users/jrippy/actor-arsenal-site/actors')

def markdown_to_html(md_content: str) -> str:
    """Convert markdown to HTML manually, skipping the first H1 title."""
    # Remove the first line if it's a title (# Title)
    lines = md_content.split('\n')
    if lines and lines[0].startswith('# '):
        lines = lines[1:]
    md_content = '\n'.join(lines)

    html = md_content

    # Convert code blocks first (```json ... ```)
    def code_block_repl(match):
        lang = match.group(1) or ''
        code = match.group(2).strip()
        # Escape HTML entities
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-{lang}">{code}</code></pre>'

    html = re.sub(r'```(\w*)\n(.*?)```', code_block_repl, html, flags=re.DOTALL)

    # Convert inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Convert headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Convert bold
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)

    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', html)

    # Convert tables (simple)
    def table_repl(match):
        table_text = match.group(0)
        lines = [l.strip() for l in table_text.strip().split('\n') if l.strip()]
        if len(lines) < 2:
            return table_text

        result = '<table>\n<thead>\n<tr>'
        headers = [h.strip() for h in lines[0].split('|') if h.strip()]
        for h in headers:
            result += f'<th>{h}</th>'
        result += '</tr>\n</thead>\n<tbody>\n'

        for line in lines[2:]:  # Skip header separator
            if '---' in line:
                continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            result += '<tr>'
            for c in cells:
                result += f'<td>{c}</td>'
            result += '</tr>\n'
        result += '</tbody>\n</table>'
        return result

    html = re.sub(r'(?:^\|.+\|$\n?)+', table_repl, html, flags=re.MULTILINE)

    # Convert unordered lists
    def ul_repl(match):
        items = match.group(0)
        list_items = re.findall(r'^[-*] (.+)$', items, re.MULTILINE)
        return '<ul>\n' + '\n'.join(f'<li>{item}</li>' for item in list_items) + '\n</ul>'

    html = re.sub(r'(?:^[-*] .+$\n?)+', ul_repl, html, flags=re.MULTILINE)

    # Convert numbered lists
    def ol_repl(match):
        items = match.group(0)
        list_items = re.findall(r'^\d+\. (.+)$', items, re.MULTILINE)
        return '<ol>\n' + '\n'.join(f'<li>{item}</li>' for item in list_items) + '\n</ol>'

    html = re.sub(r'(?:^\d+\. .+$\n?)+', ol_repl, html, flags=re.MULTILINE)

    # Convert horizontal rules
    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)

    # Convert paragraphs (text blocks separated by blank lines)
    paragraphs = []
    current = []
    for line in html.split('\n'):
        line = line.strip()
        if not line:
            if current:
                text = ' '.join(current)
                if not text.startswith('<') or text.startswith('<strong>') or text.startswith('<a ') or text.startswith('<code>'):
                    paragraphs.append(f'<p>{text}</p>')
                else:
                    paragraphs.append(text)
                current = []
        else:
            if line.startswith('<h') or line.startswith('<pre') or line.startswith('<ul') or line.startswith('<ol') or line.startswith('<table') or line.startswith('<hr'):
                if current:
                    text = ' '.join(current)
                    paragraphs.append(f'<p>{text}</p>')
                    current = []
                paragraphs.append(line)
            else:
                current.append(line)

    if current:
        text = ' '.join(current)
        paragraphs.append(f'<p>{text}</p>')

    html = '\n'.join(paragraphs)

    # Clean up empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    html = re.sub(r'<p>(<h[123]>)', r'\1', html)
    html = re.sub(r'(</h[123]>)</p>', r'\1', html)
    html = re.sub(r'<p>(<pre)', r'\1', html)
    html = re.sub(r'(</pre>)</p>', r'\1', html)
    html = re.sub(r'<p>(<ul)', r'\1', html)
    html = re.sub(r'(</ul>)</p>', r'\1', html)
    html = re.sub(r'<p>(<ol)', r'\1', html)
    html = re.sub(r'(</ol>)</p>', r'\1', html)
    html = re.sub(r'<p>(<table)', r'\1', html)
    html = re.sub(r'(</table>)</p>', r'\1', html)
    html = re.sub(r'<p>(<hr>)', r'\1', html)

    return html

def update_actor_html(actor_folder: str, html_filename: str) -> bool:
    """Update an actor's HTML page with new README content."""
    readme_path = APIFY_ACTORS_DIR / actor_folder / '.actor' / 'README.md'
    html_path = ARSENAL_ACTORS_DIR / html_filename

    if not readme_path.exists():
        print(f"  README not found: {readme_path}")
        return False

    if not html_path.exists():
        print(f"  HTML not found: {html_path}")
        return False

    # Read the README
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # Convert to HTML
    content_html = markdown_to_html(readme_content)

    # Read the existing HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Find and replace the content section
    # Pattern: <section class="content">...<div class="container">CONTENT</div>...</section>
    pattern = r'(<section class="content">\s*<div class="container">)(.*?)(</div>\s*</section>)'

    def replacement(match):
        prefix = match.group(1)
        suffix = match.group(3)

        # Get the title from the first h1 in README
        title_match = re.search(r'^# (.+)$', readme_content, re.MULTILINE)
        title = title_match.group(1) if title_match else actor_folder.replace('-', ' ').title()

        # Build the new content
        new_content = f'\n            <h1>{title}</h1>\n{content_html}\n        '

        return prefix + new_content + suffix

    new_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

    if new_html == html_content:
        print(f"  No changes made (pattern not matched)")
        return False

    # Write the updated HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    return True

def main():
    print("Updating Actor Arsenal HTML pages with new README content...\n")

    updated = 0
    failed = 0

    for actor_folder, html_filename in ACTOR_MAPPING.items():
        print(f"Processing {actor_folder}...")
        if update_actor_html(actor_folder, html_filename):
            print(f"  ✓ Updated {html_filename}")
            updated += 1
        else:
            print(f"  ✗ Failed to update {html_filename}")
            failed += 1

    print(f"\nDone! Updated: {updated}, Failed: {failed}")

if __name__ == '__main__':
    main()
