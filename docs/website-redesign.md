# Website redesign

## Intent and visual direction

The previous website presented autodev as a rigid protocol with broad mechanical guarantees. The current skill is an optional workflow for consequential changes: shared understanding of intent, actual implementation, and the basis and limits of verification. The website now follows that positioning in English and Chinese.

The user's Landable reference established the experience: deliberate visual identity, localized ambient particles at each chapter, reversible particle transitions, and actual scroll-distance holds before and after every transition. Autodev uses layered system blueprints and a continuous evidence path rather than Landable's repository constellation.

- Midnight ink `#080f25`, raised surface `#101a34`, cold white `#edf1ff`, blueprint blue `#b3c2ff`, implemented mint `#8bd7c7`, human decision gold `#ddbf87`.
- Locally hosted Manrope with system Chinese fonts. The font license is included.
- Five independently composed chapters: purpose, Clarify/Loop/Handoff, task-specific deliverables, recorded measurements, and installation.
- Illustrative system paths distinguish agreed design, implemented work, unfinished work, and unverified ledger integration. Task selection changes both explanatory text and the artifact schematic.
- Measured case SVGs are unchanged. Their original dimensions are preserved, and each opens at full size. The cann2026 target miss and verification-service outage remain explicit.

## Implementation

`web/index.html` provides readable English content without JavaScript. `styles.css` contains the reading layout; `app.js` handles language, selections, navigation, and clipboard feedback. The existing language preference key, installation command, diagram URLs, and buildless GitHub Pages deployment are preserved.

`story.js`, `story.css`, and `story-motion.mjs` adapt the Landable motion engine to Autodev's actual SVG and text geometry:

- Each transition holds the outgoing scene over 0–20%, morphs over 20–80%, and holds the incoming scene over 80–100% of its scroll distance. Native scrolling remains available; wheel and touch events are not intercepted.
- Long chapters receive their full native reading distance before the next handover. Resting positions have per-chapter padding and separate layouts for desktop, tablet, and phone. Phones put the workflow/artifact graphics ahead of their longer explanations.
- Target masks rebuild after viewport, font, language, and selected-content changes. Hidden artifact variants are excluded from sampling. Browser scroll anchoring is disabled inside the enhanced story to avoid layout-induced camera jumps.
- Particle positions along a transition depend on scroll progress. Ambient motion remains local while text and camera hold still. Rendering uses up to 2,400 desktop or 1,200 phone particles, at capped backing resolution, with ambient drawing limited to 28 Hz.
- Hidden tabs and offscreen stages stop rendering. Reduced motion, data saving, unavailable canvas, or viewports shorter than 560px use the reading layout. Mobile navigation and essential content remain available without JavaScript.
- Keyboard navigation, visible focus, Escape, chapter links, history, persistent language, and denied storage/clipboard have explicit handling. Clipboard failure gives manual instructions.

## Verification on 2026-10-24

- Python suite: 196 tests passed. No skill runtime or benchmark sources were changed.
- Motion suite: six tests passed, covering exact holds, refresh-rate-independent damping, reading ranges, scene boundaries, deterministic reversal, and bounded ambient motion.
- Browser suite: 325 assertions passed across EN/中文, five chapters, and seven sizes: 1440×960, 1440×768, 1024×768, 800×700, 667×700, 390×844, and 320×740. It checks horizontal overflow, header clearance, living particles, full reading distance, controls, keyboard focus, clipboard, all transition plateaus, reverse scroll, reduced motion, short landscape, language persistence, denied APIs, JavaScript-disabled reading, and data saving.
- The browser reported no JavaScript exceptions or failed resources. The 26 static page links/resources resolve, and 13 static IDs are unique. Both measured case assets match their documentation sources byte for byte.
- Screenshots were inspected at desktop, narrow, and phone widths, including the stable landing of each chapter. Chinese heading wrapping received a final visual check.
- This verifies the local website in Chromium. It does not establish Safari/Firefox behavior, a deployed Pages release, or the general effectiveness of the skill.

Run from the repository root:

```sh
python3 -m http.server 4191 --bind 127.0.0.1 --directory web
```

In another terminal:

```sh
node --test tests/story-motion.test.mjs
python3 -m unittest discover -s tests
node tests/website.browser.cjs
```

The browser suite requires an available `playwright` module and compatible Chromium. Set `AUTODEV_PLAYWRIGHT_MODULE` to an installed module path and `AUTODEV_BROWSER_PATH` to a compatible executable when they are outside normal resolution. `AUTODEV_SITE_URL` overrides the local address, and `AUTODEV_RESULTS_FILE` optionally saves detailed assertion results.

The user approved publication on 2026-10-24. GitHub Pages release status is recorded by the deployment workflow.
