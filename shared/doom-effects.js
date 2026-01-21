// Shared DOOM Visual Effects for Actor Arsenal
// CRT overlay, vignette, pain flash, demons, and more

(function() {
    'use strict';

    // Determine if we're in a subdirectory (like /actors/)
    const isSubdir = window.location.pathname.includes('/actors/');
    const basePath = isSubdir ? '../' : '';

    // Visual effects HTML
    const effectsHTML = `
    <!-- CRT Scanlines -->
    <div class="crt-overlay"></div>

    <!-- Red Vignette -->
    <div class="vignette"></div>

    <!-- Pain Flash -->
    <div class="pain-flash" id="painFlash"></div>

    <!-- Imp Sprites -->
    <img src="${basePath}images/imp-front.png" class="demon-left" id="demonLeft" alt="Imp">
    <img src="${basePath}images/imp-front.png" class="demon-right" id="demonRight" alt="Imp">
    `;

    // Effects CSS
    const effectsCSS = `
    <style id="shared-effects-styles">
        /* ===== CRT SCANLINE OVERLAY ===== */
        .crt-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9998;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.3),
                rgba(0, 0, 0, 0.3) 1px,
                transparent 1px,
                transparent 3px
            );
            opacity: 0.6;
        }

        /* ===== RED VIGNETTE ===== */
        .vignette {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9997;
            background: radial-gradient(ellipse at center, transparent 40%, rgba(139, 0, 0, 0.3) 100%);
        }

        /* ===== PAIN FLASH ===== */
        .pain-flash {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9996;
            background: rgba(255, 0, 0, 0);
            transition: background 0.1s;
        }
        .pain-flash.active {
            background: rgba(255, 0, 0, 0.3);
        }

        /* ===== SCREEN SHAKE ===== */
        @keyframes screenShake {
            0%, 100% { transform: translate(0, 0); }
            10% { transform: translate(-2px, -1px); }
            20% { transform: translate(2px, 1px); }
            30% { transform: translate(-1px, 2px); }
            40% { transform: translate(1px, -2px); }
            50% { transform: translate(-2px, 1px); }
            60% { transform: translate(2px, -1px); }
            70% { transform: translate(-1px, -2px); }
            80% { transform: translate(1px, 2px); }
            90% { transform: translate(-2px, -1px); }
        }
        .shake {
            animation: screenShake 0.3s ease-in-out;
        }

        /* ===== DEMON SPRITES ===== */
        .demon-left, .demon-right {
            position: fixed;
            bottom: 70px;
            width: 80px;
            height: 100px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s, transform 0.3s;
            image-rendering: pixelated;
        }
        .demon-left {
            left: -80px;
            transform: scaleX(-1);
        }
        .demon-right {
            right: -80px;
        }
        .demon-left.peek {
            left: -20px;
            opacity: 1;
        }
        .demon-right.peek {
            right: -20px;
            opacity: 1;
        }

        /* ===== KILL COUNTER ANIMATION ===== */
        .kill-counter {
            display: inline-block;
            transition: transform 0.1s;
        }
        .kill-counter.increment {
            transform: scale(1.3);
            color: var(--accent-red);
        }
        #hudAmmo.increment {
            transform: scale(1.1);
        }

        /* ===== BLOOD SPLATTER ===== */
        .blood-splat {
            position: fixed;
            pointer-events: none;
            z-index: 9990;
            font-size: 2rem;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .blood-splat.show {
            animation: splatAnim 0.5s ease-out forwards;
        }
        @keyframes splatAnim {
            0% { transform: scale(0) rotate(0deg); opacity: 1; }
            50% { transform: scale(1.5) rotate(180deg); opacity: 0.8; }
            100% { transform: scale(1) rotate(360deg); opacity: 0; }
        }

        /* ===== DOOM TEXT ===== */
        .doom-text {
            font-family: 'Press Start 2P', cursive;
            text-shadow: 3px 3px 0 #8B0000, 6px 6px 0 rgba(0,0,0,0.5);
            letter-spacing: 2px;
        }
    </style>
    `;

    // Sound effects (preloaded)
    let doomSounds = null;
    let doomMusic = null;
    let musicPlaying = false;

    function initSounds() {
        try {
            doomSounds = {
                pickup: new Audio(basePath + 'sounds/pickup.wav'),
                door: new Audio(basePath + 'sounds/door.wav'),
                chainsaw: new Audio(basePath + 'sounds/chainsaw.wav'),
                secret: new Audio(basePath + 'sounds/secret.wav'),
                imp: new Audio(basePath + 'sounds/imp.wav'),
                death: new Audio(basePath + 'sounds/death.wav'),
                shotgun: new Audio(basePath + 'sounds/shotgun.wav')
            };

            doomMusic = new Audio(basePath + 'sounds/e1m1.mp3');
            doomMusic.loop = true;

            // Preload sounds
            Object.values(doomSounds).forEach(sound => {
                sound.volume = 0.3;
                sound.preload = 'auto';
            });
            if (doomMusic) doomMusic.volume = 0.3;
        } catch (e) {
            console.log('Sound initialization skipped');
        }
    }

    // Toggle music function (exposed globally)
    window.toggleMusic = function() {
        const musicBtn = document.getElementById('musicBtn');
        if (!doomMusic) {
            initSounds();
        }

        if (musicPlaying) {
            doomMusic.pause();
            musicPlaying = false;
            if (musicBtn) {
                musicBtn.textContent = '🔇';
                musicBtn.classList.remove('playing');
            }
        } else {
            doomMusic.play().then(() => {
                musicPlaying = true;
                if (musicBtn) {
                    musicBtn.textContent = '🔊';
                    musicBtn.classList.add('playing');
                }
            }).catch(e => console.log('Music play failed:', e));
        }
    };

    // Play sound function (exposed globally)
    window.playDoomSound = function(soundName) {
        if (!doomSounds) initSounds();
        if (doomSounds && doomSounds[soundName]) {
            doomSounds[soundName].currentTime = 0;
            doomSounds[soundName].play().catch(() => {});
        }
    };

    // Pain flash function
    window.triggerPainFlash = function() {
        const flash = document.getElementById('painFlash');
        if (flash) {
            flash.classList.add('active');
            setTimeout(() => flash.classList.remove('active'), 100);
        }
    };

    // Screen shake function
    window.triggerScreenShake = function() {
        document.body.classList.add('shake');
        setTimeout(() => document.body.classList.remove('shake'), 300);
    };

    // Inject effects
    function injectEffects() {
        // Add CSS
        if (!document.getElementById('shared-effects-styles')) {
            document.head.insertAdjacentHTML('beforeend', effectsCSS);
        }

        // Check if effects already exist
        if (!document.querySelector('.crt-overlay')) {
            // Insert effects at start of body (after nav if present)
            const nav = document.querySelector('nav');
            if (nav) {
                nav.insertAdjacentHTML('afterend', effectsHTML);
            } else {
                document.body.insertAdjacentHTML('afterbegin', effectsHTML);
            }
        }

        // Initialize demon peek behavior
        initDemons();
    }

    // Demon peek on idle
    function initDemons() {
        const demonLeft = document.getElementById('demonLeft');
        const demonRight = document.getElementById('demonRight');
        let idleTimer = null;

        function resetIdleTimer() {
            clearTimeout(idleTimer);
            // Hide demons when user is active
            if (demonLeft) demonLeft.classList.remove('peek');
            if (demonRight) demonRight.classList.remove('peek');

            // Show demons after 10 seconds of inactivity
            idleTimer = setTimeout(() => {
                if (Math.random() > 0.5 && demonLeft) {
                    demonLeft.classList.add('peek');
                } else if (demonRight) {
                    demonRight.classList.add('peek');
                }
                // Play imp sound occasionally
                if (Math.random() > 0.7) {
                    window.playDoomSound('imp');
                }
            }, 10000);
        }

        // Track user activity
        ['mousemove', 'keydown', 'click', 'scroll'].forEach(event => {
            document.addEventListener(event, resetIdleTimer);
        });

        // Initial timer
        resetIdleTimer();
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectEffects);
    } else {
        injectEffects();
    }
})();
