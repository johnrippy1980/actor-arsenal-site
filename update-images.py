#!/usr/bin/env python3
"""
Update Actor Arsenal HTML to use Apify pictureUrl instead of local images.
"""

import json
import re
import os

def load_actors():
    """Load actors.json and create a mapping of name -> pictureUrl"""
    with open('actors.json', 'r') as f:
        actors = json.load(f)

    # Create mapping by actor name (slug)
    mapping = {}
    for actor in actors:
        name = actor.get('name', '')
        picture_url = actor.get('pictureUrl', '')
        if name and picture_url:
            mapping[name] = picture_url
            # Also add shortened versions (first 2-3 words)
            parts = name.split('-')
            if len(parts) >= 2:
                short_name = '-'.join(parts[:2])
                if short_name not in mapping:
                    mapping[short_name] = picture_url
                short_name = '-'.join(parts[:3])
                if short_name not in mapping:
                    mapping[short_name] = picture_url

    # Manual mappings for HTML names that don't match JSON names
    manual_mappings = {
        'angi-angie-s-list-scraper': 'angi-scraper',
        'bbb-advanced-scraper': 'bbb-scraper',
        'doordash-store-details-scraper': 'doordash-scraper',
        'facebook-photos-scraper': 'facebook-page-post-scraper',
        'facebook-posts-scraper': 'facebook-page-post-scraper',
        'facebook-search-scraper': 'facebook-page-post-scraper',
        'grubhub-restaurant-scraper': 'grubhub-scraper',
        'houzz-professional-scraper': 'houzz-scraper',
        'manta-business-search-scraper': 'manta-scraper',
        'moz-local-listing-checker---nap-consistency-audit': 'moz-listing-checker',
        'nextdoor-business-scraper': 'nextdoor-scraper',
        'web-scraper': 'website-crawler',
        'website-content-crawler': 'website-crawler',
        'google-search-scraper': 'google-serp-scraper',
        'instagram-profile-scraper': 'instagram-scraper',
        'linkedin-company-scraper': 'linkedin-company-profile-scraper',
        'e-commerce-intelligence-made-simple': 'shopify-store-analyzer',
        'shopify-store-analyzer': 'shopify-store-analyzer',
    }

    # Apply manual mappings
    for html_name, json_name in manual_mappings.items():
        # Find the JSON name in mapping and create alias
        for key, url in list(mapping.items()):
            if key.startswith(json_name) or json_name in key:
                mapping[html_name] = url
                break

    return mapping

def update_index_html(actor_images):
    """Update index.html to use Apify image URLs"""
    with open('index.html', 'r') as f:
        html = f.read()

    # Pattern to match: <img src="images/ACTOR-NAME.png"
    # and replace with: <img src="APIFY_URL"
    pattern = r'<img src="images/([^"]+)\.png" alt="" class="actor-img"'

    def find_best_match(actor_name, actor_images):
        """Find the best matching actor from the mapping"""
        # Exact match
        if actor_name in actor_images:
            return actor_images[actor_name]

        # Try partial match - actor_name is a prefix
        for key, url in actor_images.items():
            if key.startswith(actor_name):
                return url

        # Try partial match - actor_name contains key
        for key, url in actor_images.items():
            if actor_name.startswith(key):
                return url

        return None

    def replace_image(match):
        actor_name = match.group(1)
        picture_url = find_best_match(actor_name, actor_images)
        if picture_url:
            return f'<img src="{picture_url}" alt="" class="actor-img"'
        else:
            # Keep original if no mapping found
            return match.group(0)

    updated_html = re.sub(pattern, replace_image, html)

    with open('index.html', 'w') as f:
        f.write(updated_html)

    return html != updated_html

def update_actor_pages(actor_images):
    """Update individual actor HTML pages"""
    actors_dir = 'actors'
    if not os.path.exists(actors_dir):
        return 0

    updated_count = 0
    for filename in os.listdir(actors_dir):
        if not filename.endswith('.html'):
            continue

        filepath = os.path.join(actors_dir, filename)
        actor_name = filename.replace('.html', '')

        if actor_name not in actor_images:
            continue

        with open(filepath, 'r') as f:
            html = f.read()

        # Update image references in actor detail pages
        pattern = r'<img[^>]+src="[^"]*images/[^"]+\.png"[^>]*class="[^"]*actor-img[^"]*"'
        replacement = f'<img src="{actor_images[actor_name]}" alt="" class="actor-img"'

        # Also try pattern for other image references
        pattern2 = rf'src="\.\.?/images/{re.escape(actor_name)}\.png"'
        replacement2 = f'src="{actor_images[actor_name]}"'

        updated_html = re.sub(pattern, replacement, html)
        updated_html = re.sub(pattern2, replacement2, updated_html)

        if html != updated_html:
            with open(filepath, 'w') as f:
                f.write(updated_html)
            updated_count += 1

    return updated_count

def main():
    print("Loading actors.json...")
    actor_images = load_actors()
    print(f"Found {len(actor_images)} actors with pictureUrl")

    print("\nUpdating index.html...")
    if update_index_html(actor_images):
        print("  index.html updated!")
    else:
        print("  No changes needed in index.html")

    print("\nUpdating individual actor pages...")
    count = update_actor_pages(actor_images)
    print(f"  Updated {count} actor pages")

    print("\nDone!")

if __name__ == "__main__":
    main()
