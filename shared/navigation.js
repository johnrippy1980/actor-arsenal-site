// Shared Navigation Component for Actor Arsenal
// This script injects the consistent navigation bar across all pages

(function() {
    'use strict';

    // Determine if we're in a subdirectory (like /actors/)
    const isSubdir = window.location.pathname.includes('/actors/');
    const basePath = isSubdir ? '../' : '';

    // Navigation HTML template
    const navHTML = `
    <nav>
        <div class="container">
            <a href="${basePath}index.html" class="logo"><img src="${basePath}images/logo.png" alt="Doomguy" class="logo-img"> ACTOR ARSENAL</a>
            <div class="nav-links">
                <a href="${basePath}compare.html">Compare</a>
                <a href="${basePath}api-docs.html">API Docs</a>
                <a href="${basePath}faq.html">FAQ</a>
                <a href="${basePath}partners.html">Weapons Locker</a>
                <a href="${basePath}play-doom.html" style="color: var(--accent-red);">PLAY DOOM</a>
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
    </nav>
    `;

    // Navigation CSS (includes difficulty selector and music button styles)
    const navCSS = `
    <style id="shared-nav-styles">
        nav {
            position: fixed;
            top: 0;
            width: 100%;
            padding: 1rem 0;
            background: rgba(10, 10, 10, 0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border);
            z-index: 1000;
        }
        nav .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        .logo {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--accent-green);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .logo-img {
            width: 40px;
            height: auto;
            image-rendering: pixelated;
        }
        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }
        .nav-links a {
            color: var(--text-secondary);
            text-decoration: none;
            transition: color 0.3s;
        }
        .nav-links a:hover {
            color: var(--accent-green);
        }
        .cta-button {
            background: var(--accent-green);
            color: var(--bg-dark);
            padding: 0.5rem 1rem;
            border-radius: 4px;
            text-decoration: none;
            font-weight: 600;
        }
        .cta-button:hover {
            background: #00cc6a;
        }

        /* ===== DIFFICULTY SELECTOR ===== */
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
        }
    </style>
    `;

    // Find existing nav and replace, or insert at start of body
    function injectNavigation() {
        // Add CSS first
        if (!document.getElementById('shared-nav-styles')) {
            document.head.insertAdjacentHTML('beforeend', navCSS);
        }

        // Check if there's an existing nav to replace
        const existingNav = document.querySelector('nav');
        if (existingNav) {
            existingNav.outerHTML = navHTML;
        } else {
            // Insert at start of body
            document.body.insertAdjacentHTML('afterbegin', navHTML);
        }

        // Initialize difficulty selector functionality
        initDifficultySelector();
    }

    // Difficulty selector functionality
    function initDifficultySelector() {
        const difficultyBtn = document.getElementById('difficultyBtn');
        const difficultyMenu = document.getElementById('difficultyMenu');

        if (difficultyBtn && difficultyMenu) {
            difficultyBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                difficultyMenu.classList.toggle('show');
            });

            document.querySelectorAll('.difficulty-option').forEach(option => {
                option.addEventListener('click', function() {
                    document.querySelectorAll('.difficulty-option').forEach(o => o.classList.remove('active'));
                    this.classList.add('active');
                    difficultyBtn.textContent = this.textContent;
                    difficultyMenu.classList.remove('show');

                    // Store preference
                    localStorage.setItem('doomDifficulty', this.dataset.difficulty);

                    // Trigger difficulty change event
                    document.dispatchEvent(new CustomEvent('difficultyChange', {
                        detail: { difficulty: this.dataset.difficulty }
                    }));
                });
            });

            // Close menu when clicking outside
            document.addEventListener('click', function() {
                difficultyMenu.classList.remove('show');
            });

            // Restore saved difficulty
            const savedDifficulty = localStorage.getItem('doomDifficulty');
            if (savedDifficulty) {
                const savedOption = document.querySelector(`[data-difficulty="${savedDifficulty}"]`);
                if (savedOption) {
                    document.querySelectorAll('.difficulty-option').forEach(o => o.classList.remove('active'));
                    savedOption.classList.add('active');
                    difficultyBtn.textContent = savedOption.textContent;
                }
            }
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectNavigation);
    } else {
        injectNavigation();
    }
})();
