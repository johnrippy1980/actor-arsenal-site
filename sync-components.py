#!/usr/bin/env python3
"""
Sync navigation and HUD across all HTML pages to match the homepage.
This script updates the nav, HUD, and their CSS in all pages.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path('/Users/jrippy/actor-arsenal-site')

# The canonical navigation HTML (from homepage, for root-level pages)
NAV_ROOT = '''    <nav>
        <div class="container">
            <a href="index.html" class="logo"><img src="images/logo.png" alt="Doomguy" class="logo-img"> ACTOR ARSENAL</a>
            <div class="nav-links">
                <a href="compare.html">Compare</a>
                <a href="api-docs.html">API Docs</a>
                <a href="faq.html">FAQ</a>
                <a href="partners.html">Weapons Locker</a>
                <a href="play-doom.html" style="color: var(--accent-red);">PLAY DOOM</a>
                <!-- Difficulty Selector -->
                <div class="difficulty-selector">
                    <button class="difficulty-btn" id="difficultyBtn">HURT ME PLENTY</button>
                    <div class="difficulty-menu" id="difficultyMenu">
                        <button class="difficulty-option" data-difficulty="baby">I'M TOO YOUNG TO DIE</button>
                        <button class="difficulty-option" data-difficulty="easy">HEY, NOT TOO ROUGH</button>
                        <button class="difficulty-option active" data-difficulty="medium">HURT ME PLENTY</button>
                        <button class="difficulty-option" data-difficulty="hard">ULTRA-VIOLENCE</button>
                        <button class="difficulty-option" data-difficulty="nightmare">NIGHTMARE!</button>
                    </div>
                </div>
                <button class="music-btn" id="musicBtn" onclick="toggleMusic()" title="Play Music">🔇</button>
                <a href="https://apify.com/alizarin_refrigerator-owner?fpr=kqpn7" class="cta-button" target="_blank" rel="noopener">View on Apify</a>
            </div>
        </div>
    </nav>'''

# Navigation for actor pages (with ../ paths)
NAV_ACTORS = '''    <nav>
        <div class="container">
            <a href="../index.html" class="logo"><img src="../images/logo.png" alt="Doomguy" class="logo-img"> ACTOR ARSENAL</a>
            <div class="nav-links">
                <a href="../compare.html">Compare</a>
                <a href="../api-docs.html">API Docs</a>
                <a href="../faq.html">FAQ</a>
                <a href="../partners.html">Weapons Locker</a>
                <a href="../play-doom.html" style="color: var(--accent-red);">PLAY DOOM</a>
                <!-- Difficulty Selector -->
                <div class="difficulty-selector">
                    <button class="difficulty-btn" id="difficultyBtn">HURT ME PLENTY</button>
                    <div class="difficulty-menu" id="difficultyMenu">
                        <button class="difficulty-option" data-difficulty="baby">I'M TOO YOUNG TO DIE</button>
                        <button class="difficulty-option" data-difficulty="easy">HEY, NOT TOO ROUGH</button>
                        <button class="difficulty-option active" data-difficulty="medium">HURT ME PLENTY</button>
                        <button class="difficulty-option" data-difficulty="hard">ULTRA-VIOLENCE</button>
                        <button class="difficulty-option" data-difficulty="nightmare">NIGHTMARE!</button>
                    </div>
                </div>
                <button class="music-btn" id="musicBtn" onclick="toggleMusic()" title="Play Music">🔇</button>
                <a href="https://apify.com/alizarin_refrigerator-owner?fpr=kqpn7" class="cta-button" target="_blank" rel="noopener">View on Apify</a>
            </div>
        </div>
    </nav>'''

# The canonical HUD HTML (for root-level pages)
HUD_ROOT = '''    <!-- DOOM HUD (Classic Metal Style) -->
    <div class="doom-hud">
        <div class="hud-section">
            <div class="hud-stat">
                <div class="hud-value hud-ammo" id="hudAmmo">150,000</div>
                <div class="hud-label">KILLS</div>
            </div>
        </div>
        <div class="hud-section">
            <div class="hud-stat">
                <div class="hud-value hud-health" id="hudHealth">100%</div>
                <div class="hud-label">HEALTH</div>
            </div>
        </div>
        <div class="hud-face-container">
            <img src="images/logo.png" class="hud-face" id="hudFace" alt="Doomguy">
        </div>
        <div class="hud-section">
            <div class="hud-stat">
                <div class="hud-value hud-armor" id="hudArmor">304</div>
                <div class="hud-label">ACTORS</div>
            </div>
        </div>
        <div class="hud-section">
            <div class="hud-stat">
                <div class="hud-value hud-secrets" id="hudSecrets">3/3</div>
                <div class="hud-label">SECRETS</div>
            </div>
        </div>
    </div>'''

# HUD for actor pages (with ../ paths)
HUD_ACTORS = '''    <!-- DOOM HUD (Classic Metal Style) -->
    <div class="doom-hud">
        <div class="hud-section">
            <div class="hud-stat">
                <div class="hud-value hud-ammo" id="hudAmmo">150,000</div>
                <div class="hud-label">KILLS</div>
            </div>
        </div>
        <div class="hud-section">
            <div class="hud-stat">
                <div class="hud-value hud-health" id="hudHealth">100%</div>
                <div class="hud-label">HEALTH</div>
            </div>
        </div>
        <div class="hud-face-container">
            <img src="../images/logo.png" class="hud-face" id="hudFace" alt="Doomguy">
        </div>
        <div class="hud-section">
            <div class="hud-stat">
                <div class="hud-value hud-armor" id="hudArmor">304</div>
                <div class="hud-label">ACTORS</div>
            </div>
        </div>
        <div class="hud-section">
            <div class="hud-stat">
                <div class="hud-value hud-secrets" id="hudSecrets">3/3</div>
                <div class="hud-label">SECRETS</div>
            </div>
        </div>
    </div>'''

# Canonical CSS for difficulty selector and music button (from homepage)
NAV_CSS = '''        /* ===== DIFFICULTY SELECTOR ===== */
        .difficulty-selector {
            position: relative;
            display: inline-block;
        }
        .difficulty-btn, .music-btn {
            background: transparent;
            border: 1px solid var(--accent-red);
            color: var(--accent-red);
            padding: 0.4rem 0.8rem;
            font-family: 'Press Start 2P', cursive;
            font-size: 0.5rem;
            cursor: pointer;
            transition: all 0.3s;
        }
        .music-btn {
            font-size: 1.2rem;
            padding: 0.4rem 0.8rem;
            margin-left: 0.5rem;
            border: 2px solid var(--accent-yellow);
            color: var(--accent-yellow);
            background: rgba(255, 204, 0, 0.1);
            animation: musicPulse 2s ease-in-out infinite;
            position: relative;
        }
        .music-btn::after {
            content: 'E1M1';
            position: absolute;
            bottom: -18px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.4rem;
            color: var(--accent-yellow);
            white-space: nowrap;
        }
        .music-btn.playing {
            background: var(--accent-yellow);
            color: #000;
            animation: none;
            box-shadow: 0 0 15px var(--accent-yellow);
        }
        .music-btn.playing::after {
            content: 'PLAYING';
        }
        @keyframes musicPulse {
            0%, 100% { box-shadow: 0 0 5px var(--accent-yellow); }
            50% { box-shadow: 0 0 20px var(--accent-yellow), 0 0 30px var(--accent-red); }
        }
        .difficulty-btn:hover, .music-btn:hover {
            background: var(--accent-red);
            color: #000;
        }
        .music-btn:hover {
            background: var(--accent-yellow);
            color: #000;
        }
        .difficulty-menu {
            position: absolute;
            top: 100%;
            right: 0;
            background: #111;
            border: 1px solid var(--accent-red);
            display: none;
            flex-direction: column;
            min-width: 200px;
            z-index: 1002;
        }
        .difficulty-menu.show { display: flex; }
        .difficulty-option {
            padding: 0.8rem;
            color: #888;
            font-family: 'Press Start 2P', cursive;
            font-size: 0.5rem;
            cursor: pointer;
            border: none;
            background: transparent;
            text-align: left;
            transition: all 0.2s;
        }
        .difficulty-option:hover {
            background: var(--accent-red);
            color: #000;
        }
        .difficulty-option.active {
            color: var(--accent-yellow);
        }'''

# Files to skip
SKIP_FILES = ['index.html']  # Homepage is the canonical source


def replace_nav(content, is_actor_page):
    """Replace the navigation block with the canonical version."""
    nav_template = NAV_ACTORS if is_actor_page else NAV_ROOT
    pattern = r'<nav>[\s\S]*?</nav>'
    if re.search(pattern, content):
        return re.sub(pattern, nav_template.strip(), content)
    return content


def find_hud_block(content):
    """Find the doom-hud div block by counting opening/closing tags."""
    marker = '<div class="doom-hud">'
    idx = content.find(marker)
    if idx < 0:
        return None, None

    comment_idx = content.rfind('<!--', max(0, idx - 100), idx)
    if comment_idx >= 0 and 'DOOM HUD' in content[comment_idx:idx]:
        start_idx = comment_idx
    else:
        start_idx = idx

    count = 0
    i = idx
    while i < len(content):
        if content[i:i+4] == '<div':
            count += 1
            i += 4
        elif content[i:i+6] == '</div>':
            count -= 1
            i += 6
            if count == 0:
                return start_idx, i
        else:
            i += 1
    return None, None


def replace_hud(content, is_actor_page):
    """Replace the HUD block with the canonical version."""
    hud_template = HUD_ACTORS if is_actor_page else HUD_ROOT
    start, end = find_hud_block(content)
    if start is not None and end is not None:
        return content[:start] + hud_template.strip() + content[end:]
    return content


def add_hud_if_missing(content, is_actor_page):
    """Add HUD before closing </body> if it doesn't exist."""
    if '<div class="doom-hud">' not in content:
        hud_template = HUD_ACTORS if is_actor_page else HUD_ROOT
        content = re.sub(r'(</body>)', '\n' + hud_template + '\n\\1', content)
    return content


def replace_nav_css(content):
    """Replace the difficulty selector and music button CSS with canonical version."""
    # Pattern to find the difficulty selector CSS block
    # This matches from "/* ===== DIFFICULTY SELECTOR =====" to the end of .difficulty-option.active block
    pattern = r'/\*\s*=+\s*DIFFICULTY SELECTOR\s*=+\s*\*/[\s\S]*?\.difficulty-option\.active\s*\{[^}]*\}'

    if re.search(pattern, content):
        return re.sub(pattern, NAV_CSS.strip(), content)

    # If the old pattern doesn't exist, look for individual classes and replace them
    # First check for separate .difficulty-selector block
    old_patterns = [
        r'\.difficulty-selector\s*\{[^}]*\}',
        r'\.difficulty-btn\s*\{[^}]*\}',
        r'\.difficulty-btn:hover\s*\{[^}]*\}',
        r'\.difficulty-menu\s*\{[^}]*\}',
        r'\.difficulty-menu\.show\s*\{[^}]*\}',
        r'\.difficulty-option\s*\{[^}]*\}',
        r'\.difficulty-option:hover\s*\{[^}]*\}',
        r'\.difficulty-option\.active\s*\{[^}]*\}',
        r'\.music-btn\s*\{[^}]*\}',
        r'\.music-btn::after\s*\{[^}]*\}',
        r'\.music-btn\.playing\s*\{[^}]*\}',
        r'\.music-btn\.playing::after\s*\{[^}]*\}',
        r'\.music-btn:hover\s*\{[^}]*\}',
        r'@keyframes\s+musicPulse\s*\{[^}]*\{[^}]*\}[^}]*\}',
    ]

    # Remove all old nav CSS
    for pat in old_patterns:
        content = re.sub(pat, '', content)

    # Find </style> and insert CSS before it (if CSS was removed)
    if '.difficulty-selector' not in content:
        content = re.sub(r'(</style>)', NAV_CSS + '\n    \\1', content, count=1)

    return content


def process_file(file_path):
    """Process a single HTML file."""
    rel_path = file_path.relative_to(BASE_DIR)
    is_actor_page = 'actors' in str(rel_path)

    print(f"Processing: {rel_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Replace navigation HTML
        content = replace_nav(content, is_actor_page)

        # Replace navigation CSS
        content = replace_nav_css(content)

        # Replace HUD
        content = replace_hud(content, is_actor_page)

        # Add HUD if missing
        content = add_hud_if_missing(content, is_actor_page)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ Updated")
        else:
            print(f"  - No changes needed")

    except Exception as e:
        print(f"  ✗ Error: {e}")


def main():
    html_files = list(BASE_DIR.glob('*.html')) + list(BASE_DIR.glob('actors/*.html'))
    html_files = [f for f in html_files if f.name not in SKIP_FILES]

    print(f"Found {len(html_files)} files to process")
    print("=" * 50)

    for file_path in sorted(html_files):
        process_file(file_path)

    print("=" * 50)
    print("Done! All pages now match the homepage navigation and HUD.")


if __name__ == '__main__':
    main()
