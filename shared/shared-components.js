// Shared Components Loader for Actor Arsenal
// Include this single file to load navigation, HUD, and DOOM effects

(function() {
    'use strict';

    // Determine if we're in a subdirectory
    const isSubdir = window.location.pathname.includes('/actors/');
    const basePath = isSubdir ? '../' : '';
    const sharedPath = basePath + 'shared/';

    // Required CSS variables (ensure they're available)
    const cssVars = `
    <style id="shared-css-vars">
        :root {
            --bg-dark: #0a0a0a;
            --bg-card: #111111;
            --accent-green: #00ff88;
            --accent-red: #ff3366;
            --accent-purple: #9933ff;
            --accent-yellow: #ffcc00;
            --accent-blood: #8B0000;
            --blood-red: #cc0000;
            --text-primary: #ffffff;
            --text-secondary: #888888;
            --border: #222222;
        }
    </style>
    `;

    // Inject CSS variables if not already present
    if (!document.getElementById('shared-css-vars') && !document.querySelector(':root')) {
        document.head.insertAdjacentHTML('afterbegin', cssVars);
    }

    // Load a script dynamically
    function loadScript(src, callback) {
        const script = document.createElement('script');
        script.src = src;
        script.async = false;
        if (callback) script.onload = callback;
        document.head.appendChild(script);
    }

    // Load all components in order
    loadScript(sharedPath + 'navigation.js', function() {
        loadScript(sharedPath + 'doom-effects.js', function() {
            loadScript(sharedPath + 'hud.js');
        });
    });
})();
