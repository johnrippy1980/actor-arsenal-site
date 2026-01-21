// Shared DOOM HUD Component for Actor Arsenal
// This script injects the consistent HUD across all pages

(function() {
    'use strict';

    // Determine if we're in a subdirectory (like /actors/)
    const isSubdir = window.location.pathname.includes('/actors/');
    const basePath = isSubdir ? '../' : '';

    // HUD HTML template
    const hudHTML = `
    <!-- DOOM HUD (Classic Metal Style) -->
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
            <img src="${basePath}images/logo.png" class="hud-face" id="hudFace" alt="Doomguy">
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
    </div>
    `;

    // HUD CSS
    const hudCSS = `
    <style id="shared-hud-styles">
        /* ===== DOOM HUD (Classic Grey Metal Style) ===== */
        .doom-hud {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 80px;
            background:
                repeating-linear-gradient(
                    90deg,
                    #5a5a5a 0px, #5a5a5a 2px,
                    #6a6a6a 2px, #6a6a6a 4px,
                    #4a4a4a 4px, #4a4a4a 6px,
                    #555 6px, #555 8px
                ),
                linear-gradient(180deg, #6a6a6a 0%, #4a4a4a 50%, #3a3a3a 100%);
            border-top: 4px solid #7a7a7a;
            border-bottom: 4px solid #2a2a2a;
            box-shadow:
                inset 0 2px 0 #8a8a8a,
                inset 0 -2px 0 #2a2a2a,
                0 -4px 8px rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1001;
            font-family: 'Press Start 2P', cursive;
            padding: 0;
            gap: 0;
        }
        .hud-section {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            background:
                linear-gradient(180deg, #5a5a5a 0%, #3a3a3a 100%);
            border-left: 3px solid #6a6a6a;
            border-right: 3px solid #2a2a2a;
            border-top: 2px solid #7a7a7a;
            border-bottom: 2px solid #1a1a1a;
            padding: 0 1.5rem;
            position: relative;
        }
        .hud-section::before {
            content: '';
            position: absolute;
            top: 4px;
            left: 4px;
            right: 4px;
            bottom: 4px;
            background: linear-gradient(180deg, #4a4a4a 0%, #2a2a2a 100%);
            border: 2px solid #1a1a1a;
            border-radius: 2px;
            z-index: -1;
        }
        .hud-stat {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 0 0.5rem;
        }
        .hud-value {
            font-size: 1.8rem;
            text-shadow: 2px 2px 0 #000, -1px -1px 0 #000;
            letter-spacing: 2px;
        }
        .hud-label {
            font-size: 0.5rem;
            color: #888;
            text-shadow: 1px 1px 0 #000;
            text-transform: uppercase;
        }
        .hud-face-container {
            width: 70px;
            height: 70px;
            background: linear-gradient(180deg, #4a4a4a 0%, #2a2a2a 100%);
            border: 3px solid #5a5a5a;
            border-bottom-color: #1a1a1a;
            border-right-color: #1a1a1a;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 1rem;
        }
        .hud-face {
            width: 60px;
            height: 60px;
            image-rendering: pixelated;
        }
        .hud-ammo { color: #ffcc00; }
        .hud-health { color: #ff3333; }
        .hud-armor { color: #00ff88; }
        .hud-secrets { color: #ff6600; }

        /* Add padding for HUD */
        body { padding-bottom: 90px; }
    </style>
    `;

    // Function to inject HUD
    function injectHUD() {
        // Add CSS first
        if (!document.getElementById('shared-hud-styles')) {
            document.head.insertAdjacentHTML('beforeend', hudCSS);
        }

        // Check if HUD already exists
        if (!document.querySelector('.doom-hud')) {
            // Insert at end of body
            document.body.insertAdjacentHTML('beforeend', hudHTML);
        }

        // Initialize HUD interactivity
        initHUD();
    }

    // HUD interactivity
    function initHUD() {
        // Increment kills on clicks
        let kills = 150000;
        document.addEventListener('click', function(e) {
            // Don't count navigation clicks
            if (e.target.closest('a') || e.target.closest('button') || e.target.closest('nav')) return;

            kills += Math.floor(Math.random() * 10) + 1;
            const hudAmmo = document.getElementById('hudAmmo');
            if (hudAmmo) {
                hudAmmo.textContent = kills.toLocaleString();
                hudAmmo.classList.add('increment');
                setTimeout(() => hudAmmo.classList.remove('increment'), 100);
            }
        });

        // Secrets tracking
        let secretsFound = parseInt(localStorage.getItem('secretsFound') || '0');
        const totalSecrets = 3;
        updateSecrets(secretsFound, totalSecrets);

        // Listen for secret discovery events
        document.addEventListener('secretFound', function(e) {
            secretsFound = Math.min(secretsFound + 1, totalSecrets);
            localStorage.setItem('secretsFound', secretsFound.toString());
            updateSecrets(secretsFound, totalSecrets);
        });
    }

    function updateSecrets(found, total) {
        const hudSecrets = document.getElementById('hudSecrets');
        if (hudSecrets) {
            hudSecrets.textContent = `${found}/${total}`;
        }
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectHUD);
    } else {
        injectHUD();
    }
})();
