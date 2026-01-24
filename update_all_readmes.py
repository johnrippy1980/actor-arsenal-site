#!/usr/bin/env python3
"""
Update ALL Actor Arsenal HTML pages with README content from Apify actors.
Automatically matches local folder names to HTML file names.
"""

import os
import re
import json
from pathlib import Path

APIFY_ACTORS_DIR = Path('/Users/jrippy/seo-dashboard-app/apify-actors')
ARSENAL_ACTORS_DIR = Path('/Users/jrippy/actor-arsenal-site/actors')

# Manual mappings for folder names that differ from HTML names
FOLDER_TO_HTML_OVERRIDES = {
    'tiktok-scraper': 'tiktok-creator-video-scraper.html',
    'youtube-scraper': 'youtube-channel-video-scraper.html',
    'semrush-keyword-research': 'semrush-keyword-research---volume-difficulty-related.html',
    'semrush-domain-overview': 'semrush-domain-overview---authority-score-traffic-keywords.html',
    'semrush-backlink-analyzer': 'semrush-backlink-analyzer---referring-domains-link-quality.html',
    'semrush-competitor-analysis': 'semrush-competitor-analysis---discover-compare-competitors.html',
    'semrush-position-tracker': 'semrush-position-tracker---keyword-rankings-serp-features.html',
    'semrush-traffic-analytics': 'semrush-traffic-analytics---visits-sources-engagement.html',
    'semrush-content-gap': 'semrush-content-gap-analysis---find-missing-keywords.html',
    'airtable-api': 'airtable-api---database-records-automation.html',
    'notion-api': 'notion-api---database-page-automation.html',
    'amazon-product-scraper': 'amazon-product-scraper-product-intelligence-at-scale.html',
    'linkedin-jobs-scraper': 'linkedin-jobs-scraper-b2b-hiring-intent-signals.html',
    'podcast-charts-scraper': 'podcast-charts-scraper-creator-economy-intelligence.html',
    'shopify-store-analyzer': 'shopify-store-analyzer-e-commerce-intelligence-made-simple.html',
    'tiktok-shop-scraper': 'tiktok-shop-scraper-e-commerce-intelligence-at-scale.html',
    'indeed-jobs-scraper': 'indeed-jobs-scraper-b2b-hiring-intent-signals.html',
    'firecrawl-pro': 'firecrawl-pro-advanced-web-scraping-full-firecrawl-features.html',
    'website-change-monitor': 'firecrawl-website-change-monitor---track-page-changes-with-ai.html',
    'influencer-strategy-generator': 'influencer-strategy-generator---ai-powered-campaign-planning.html',
    'influencer-discovery': 'influencer-discovery---find-influencers-across-social-platforms.html',
    'stitch-landing-page-generator': 'google-stitch-ai-landing-page-generator.html',
    'hubspot-company-matcher': 'hubspot-company-enrichment-fuzzy-matcher-for-clay.html',
    'square-merchant-finder': 'square-merchant-finder-discover-businesses-using-square.html',
    'god-mode-intel-mcp': 'god-mode---marketing-intelligence-mcp.html',
    'theknot-vendor-scraper': 'the-knot-wedding-vendor-data-scraper.html',
    'bing-maps-scraper': 'bing-maps-scraper-extract-local-business-data.html',
    'avvo-scraper': 'avvo-avvo-com-attorney-scraper.html',
    'apple-maps-scraper': 'apple-maps-business-listings-scraper.html',
    'huggingface-master': 'hugging-face-master.html',
    'huggingface-text': 'hugging-face-text.html',
    'huggingface-image': 'hugging-face-image-ai.html',
    'huggingface-audio': 'hugging-face-audio-ai.html',
    'huggingface-hub': 'hugging-face-hub.html',
    'multi-carrier-tracking': 'multi-carrier-package-tracking-usps-ups-fedex.html',
    'shipping-rate-comparison': 'shipping-rate-comparison-usps-ups-fedex.html',
    'shipping-location-finder': 'shipping-location-finder-usps-ups-fedex.html',
    'unified-ats-api': 'unified-ats-api-ashby-breezy-hr-workable.html',
    'supabase-api': 'supabase-api-database-storage-auth-project-management.html',
    'vercel-api': 'vercel-api-deployments-projects-domains-env-vars.html',
    'clickup-api': 'clickup-api-tasks-projects-spaces-time-tracking.html',
    'cloudflare-api': 'cloudflare-api---dns-zones-cache-security.html',
    'leonardo-ai-api': 'leonardo-ai-api---image-generation-upscaling-custom-models.html',
    'remarketing-master': 'remarketing-master---multi-platform-audience-builder.html',
    'facebook-custom-audiences': 'facebook-custom-audiences-lookalikes-hash-pii-automatically.html',
    'google-customer-match': 'google-customer-match-ads-audiences.html',
    'tiktok-custom-audiences': 'tiktok-ads-api---custom-audiences-lookalikes-w-auto-hashing.html',
    'offline-conversions-master': 'offline-conversions-master---multi-platform-event-distribution.html',
    'facebook-conversions-api': 'facebook-conversions-api-capi---server-side-events.html',
    'google-offline-conversions': 'google-ads-offline-conversions---gclid-enhanced-conversions.html',
    'linkedin-conversions-api': 'linkedin-conversions-api---b2b-offline-attribution.html',
    'tiktok-events-api': 'tiktok-events-api---server-side-conversions.html',
    'microsoft-offline-conversions': 'microsoft-ads-offline-conversions---bing-msclkid-tracking.html',
    'pinterest-conversions-api': 'pinterest-conversions-api---server-side-events.html',
    'snapchat-conversions-api': 'snapchat-conversions-api---server-side-events.html',
    'ringcentral-api': 'ringcentral-api-actor.html',
    'callrail-api': 'callrail-api-actor.html',
    'twilio-api': 'twilio-api-actor.html',
    'zoom-api': 'zoom-api-actor.html',
    'gov-research-mcp': 'government-research-mcp-server---unified-data-access.html',
    'va-benefits-api': 'va-benefits-api---veterans-benefits-eligibility-status.html',
    'ebenefits-va-api': 'ebenefits-va-gov-api.html',
    'military-onesource-api': 'military-onesource-api-counseling-pcs-education-benefits.html',
    'veteran-crisis-api': 'veteran-crisis-resources-api.html',
    'military-installation-api': 'military-installation-finder-api---base-facility-information.html',
    'veterans-employment-api': 'veterans-employment-api---career-transition-job-resources.html',
    'military-family-api': 'military-family-support-api---family-resources-services.html',
    'wounded-warrior-api': 'wounded-warrior-resources-api---support-for-injured-veterans.html',
    'military-records-api': 'military-records-api---service-records-verification.html',
    'mindbody-api': 'mindbody-api-fitness-wellness-business-data.html',
    'servicetitan-api': 'servicetitan-api-hvac-plumbing-electrical-contractor-data.html',
    'acuity-api': 'acuity-scheduling-api-appointments-booking-data-access.html',
    'housecallpro-api': 'housecall-pro-api---home-services-contractor-data.html',
    'zenoti-api': 'zenoti-api-enterprise-spa-salon-management.html',
    'jobber-api': 'jobber-api-field-service-management-jobs-invoices-quotes-etc.html',
    'vagaro-api': 'vagaro-api-salon-spa-fitness-business-data.html',
    'servicefusion-api': 'service-fusion-api-field-service-management.html',
    'marianatek-api': 'mariana-tek-api-boutique-fitness-studio-data.html',
    'gymdesk-api': 'gymdesk-api-martial-arts-specialty-fitness.html',
    'clubos-api': 'club-os-api-gym-crm-lead-management.html',
    'gymmaster-api': 'gymmaster-gym-fitness-club-management-api.html',
    'nih-grants-api': 'nih-grants-api-research-funding-data-for-grants-publications.html',
    'clinicaltrials-api': 'clinicaltrials-gov-api---clinical-study-data.html',
    'pubmed-api': 'pubmed-ncbi-databases-api.html',
    'fred-api': 'fred-api---federal-reserve-economic-data.html',
    'sec-edgar-api': 'sec-edgar-api---company-filings-financial-data.html',
    'grants-gov-api': 'grants-gov-api---federal-grant-opportunities.html',
    'uspto-api': 'uspto-api---patent-trademark-data.html',
    'bls-api': 'bls-api---bureau-of-labor-statistics-data.html',
    'cdc-api': 'cdc-api-public-health-disease-database.html',
    'noaa-api': 'noaa-api---weather-climate-ocean-data-actor.html',
    'worldbank-api': 'world-bank-api---global-development-database.html',
    'datagov-api': 'data-gov-api---us-open-government-datasets.html',
    'npi-registry': 'npi-registry---healthcare-provider-search.html',
    'sam-gov-contracts': 'sam-gov-contracts---federal-opportunities-search.html',
    'dnb-api': 'd-b-duns-lookup-company-intelligence.html',
    'census-api': 'us-census-bureau-demographics-population-data-api.html',
    'sba-api': 'sba-api---small-business-size-standards-eligibility.html',
    'design-pickle': 'design-pickle-api---professional-design-request-automation.html',
    'canva-connect': 'canva-connect-api---design-automation-export.html',
    'figma-api': 'figma-api---design-asset-extraction-export.html',
    'calendly-api': 'calendly-api---scheduling-booking-automation.html',
    'eventbrite-api': 'eventbrite-api---event-attendee-management.html',
    'quickbooks-api': 'quickbooks-online-accounting-api.html',
    'greenhouse-ats': 'greenhouse-ats-api-harvest-api.html',
    'influencer-analyzer': 'deep-influencer-analyzer-actor.html',
    'nba-api': 'nba-api---basketball-statistics.html',
    'nfl-api': 'nfl-api---football-statistics.html',
    'ncaa-api': 'ncaa-api---college-sports.html',
    'indexnow-submitter': 'indexnow-url-submitter.html',
    'nlweb-checker': 'nlweb-compliance-checker.html',
    'lottery-analyzer': 'lottery-analyzer---powerball-mega-millions.html',
    'gtmetrix-tester': 'gtmetrix-performance-tester.html',
    'moz-listing-checker': 'moz-local-listing-checker---nap-consistency-audit.html',
    'technical-seo-mcp-server': 'ai-technical-seo-mcp-server.html',
    'trustpilot-scraper': 'enterprise-grade-trustpilot-scraper.html',
    'competitor-monitor': 'ai-competitor-monitor.html',
    'citation-checker': 'citation-checker-ai.html',
    'google-ads-transparency': 'google-ads-transparency-competitor-ad-intelligence-at-scale.html',
    'meta-ad-library': 'meta-ad-library-facebook-instagram-ad-intelligence.html',
    'people-also-ask-scraper': 'people-also-ask-scraper-content-ideation-goldmine.html',
    'dad-joke-texter': 'dad-joke-fart-joke-texter.html',
    'firecrawl-search': 'firecrawl-search---llm-ready-content.html',
}


def markdown_to_html(md_content: str) -> str:
    """Convert markdown to HTML manually, skipping the first H1 title."""
    lines = md_content.split('\n')
    if lines and lines[0].startswith('# '):
        lines = lines[1:]
    md_content = '\n'.join(lines)

    html = md_content

    # Convert code blocks
    def code_block_repl(match):
        lang = match.group(1) or ''
        code = match.group(2).strip()
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code class="language-{lang}">{code}</code></pre>'

    html = re.sub(r'```(\w*)\n(.*?)```', code_block_repl, html, flags=re.DOTALL)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Convert headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Convert bold
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)

    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', html)

    # Convert tables
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

        for line in lines[2:]:
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

    # Convert lists
    def ul_repl(match):
        items = match.group(0)
        list_items = re.findall(r'^[-*] (.+)$', items, re.MULTILINE)
        return '<ul>\n' + '\n'.join(f'<li>{item}</li>' for item in list_items) + '\n</ul>'

    html = re.sub(r'(?:^[-*] .+$\n?)+', ul_repl, html, flags=re.MULTILINE)

    def ol_repl(match):
        items = match.group(0)
        list_items = re.findall(r'^\d+\. (.+)$', items, re.MULTILINE)
        return '<ol>\n' + '\n'.join(f'<li>{item}</li>' for item in list_items) + '\n</ol>'

    html = re.sub(r'(?:^\d+\. .+$\n?)+', ol_repl, html, flags=re.MULTILINE)

    html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)

    # Convert paragraphs
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

    # Clean up
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


def find_html_file(folder_name: str) -> Path:
    """Find the corresponding HTML file for a folder."""
    # Check override mapping first
    if folder_name in FOLDER_TO_HTML_OVERRIDES:
        html_file = ARSENAL_ACTORS_DIR / FOLDER_TO_HTML_OVERRIDES[folder_name]
        if html_file.exists():
            return html_file

    # Try exact match
    html_file = ARSENAL_ACTORS_DIR / f"{folder_name}.html"
    if html_file.exists():
        return html_file

    # Try finding by searching
    for html_path in ARSENAL_ACTORS_DIR.glob('*.html'):
        html_name = html_path.stem.lower().replace('-', '')
        folder_normalized = folder_name.lower().replace('-', '')
        if html_name == folder_normalized or html_name.startswith(folder_normalized):
            return html_path

    return None


def update_actor_html(folder_name: str, readme_path: Path, html_path: Path) -> bool:
    """Update an actor's HTML page with README content."""
    # Read README
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    content_html = markdown_to_html(readme_content)

    # Read HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Find and replace content section
    pattern = r'(<section class="content">\s*<div class="container">)(.*?)(</div>\s*</section>)'

    def replacement(match):
        prefix = match.group(1)
        suffix = match.group(3)

        title_match = re.search(r'^# (.+)$', readme_content, re.MULTILINE)
        title = title_match.group(1) if title_match else folder_name.replace('-', ' ').title()

        new_content = f'\n            <h1>{title}</h1>\n{content_html}\n        '
        return prefix + new_content + suffix

    new_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

    if new_html == html_content:
        return False

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    return True


def main():
    print("Updating ALL Actor Arsenal HTML pages...\n")

    updated = 0
    skipped = 0
    no_readme = 0
    no_html = 0

    # Get all actor folders
    for folder in sorted(APIFY_ACTORS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        if folder.name.startswith('_') or folder.name in ['scripts', 'shared']:
            continue

        # Find README
        readme_path = folder / '.actor' / 'README.md'
        if not readme_path.exists():
            readme_path = folder / 'README.md'
        if not readme_path.exists():
            no_readme += 1
            continue

        # Find HTML
        html_path = find_html_file(folder.name)
        if not html_path:
            no_html += 1
            continue

        try:
            if update_actor_html(folder.name, readme_path, html_path):
                print(f"  ✓ {folder.name} -> {html_path.name}")
                updated += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ✗ {folder.name}: {e}")

    print(f"\n=== Summary ===")
    print(f"Updated: {updated}")
    print(f"No changes needed: {skipped}")
    print(f"No README found: {no_readme}")
    print(f"No HTML found: {no_html}")


if __name__ == '__main__':
    main()
