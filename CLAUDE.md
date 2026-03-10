# Push Films Website — Claude Handoff

## Project Overview
Portfolio website for Greg Hobden, film producer. Single-page site with sections: Hero, About, Work (accordion), Early Years (password-protected music videos), and Contact.

## File Structure
- **Sole file**: `/Users/greghobden/push-films-website/index.html` — all HTML, CSS, and JS inline in one file
- **Images**: `/Users/greghobden/push-films-website/images/` — all images and video clips
- **Title cards**: `title-card.html` (name + Producer) and `title-card-2.html` (name + Producer + disciplines) — 1920×1080 HTML files for screenshotting into showreel

## Deployment Pipeline
- Git → GitHub (`ghobden-os/push-films-website`) → Netlify (auto-deploys on push to `main`)
- Always commit and push when the user confirms — do not wait to be asked twice
- Always `git add` image files explicitly when they are newly referenced; they are often not yet tracked

## Filename Gotchas
- Filenames with spaces must be URL-encoded in HTML (e.g. `EWR (12).jpg` → `images/EWR%20(12).jpg`)
- Some EVEREST images have a leading space: ` EVEREST19.jpg` — the space is part of the filename
- When adding images to git, quote filenames with spaces: `git add "images/EWR (12).jpg"`
- GitHub hard limit is 100MB per file, warning at 50MB — check video sizes with `du -m` before committing and exclude large MOVs
- Folder names with trailing spaces (e.g. `RAPTOR `, `DISCOVERY `) are URL-encoded as `RAPTOR%20`, `DISCOVERY%20` in src paths

## Architecture

### Accordion (Work Section)
Each work item is an `<article class="work-item accordion" data-vimeo="XXXXXXX" data-gallery="key">`.

Optional data attributes on the article:
- `data-start="1140"` — seeks Vimeo to that timestamp (seconds) on open
- `data-last-hold="12000"` — ms to hold the final gallery strip before hiding (default 16000)

When clicked it expands to show:
- **Film** (Vimeo iframe) — 87.5% width centred on desktop, 100% width on mobile
- **Gallery strip** of thumbnails below — 3 at a time on desktop, 1 at a time on mobile — auto-advancing every **7s** by default
- After one full loop the gallery hides and the film plays solo full width
- When the film ends **or is paused**, the accordion auto-collapses
- Only one accordion can be open at a time (`currentlyExpanded` global)

Gallery items support a `position` property for per-image `object-position` cropping:
```js
{type:'image', src:'images/foo.jpg', position:'50% 30%'}
```
All gallery images default to `object-position: top` via CSS.

Clicking a gallery image opens a full-screen lightbox (`#imgLightbox`).

### Lightbox
- Click a gallery image → opens fullscreen lightbox
- **← →** arrow keys navigate between images in the gallery (skips video items)
- **Space** or **Escape** or click anywhere → closes lightbox
- State tracked in `lightboxItems` (array) and `lightboxIndex` (int) module-level variables
- `openLightbox(items, index)` — takes the full items array and the rawIdx of the clicked image

### Work Section Category Order
Documentary → Automotive → Experiential → Luxury → Expo → Sport → Comedy → Everest → The Early Years → Music Videos → Commercials

### Mobile Layout
- `STRIP_SIZE = window.innerWidth < 640 ? 1 : 3` — set once at page load
- On mobile the gallery thumb height matches the film exactly: `calc((100vw - 2 * var(--pad)) * 0.5625)`
- Film is `width: 100%; padding-bottom: 56.25%; margin: 0` on mobile (overrides desktop 87.5%)

### CSS Cascade Warning
The accordion expand CSS (`.expand-film`, `.expand-gallery-strip`, `.expand-gallery-thumb`) lives at ~line 590, **after** the first `@media (max-width: 640px)` block at ~line 558. Equal-specificity rules later in the file win, so the mobile overrides in that first block were being silently ignored. Fix: there is a **second** `@media (max-width: 640px)` block at the very end of `<style>` (just before `</style>`) with `!important` that correctly overrides the accordion desktop rules. Always add mobile accordion overrides there, not in the first media block.

### Vimeo — iOS Safari Behaviour
iOS Safari blocks cross-origin iframe autoplay. The code detects iOS and:
- Omits `autoplay=1` from the URL (causes infinite spinner on iOS if present)
- Lets Vimeo load with its native play button — user taps once to play

**Do not add** `controls=0` (removes the play button, causing infinite spinner), `vimeoPlayer.play()` (causes spinner), or `setVolume()`/`setMuted()` SDK calls (all cause the same infinite spinner on iOS). The Vimeo SDK is loaded at the bottom of `<body>` — this is correct; moving it earlier blocks page JS on slow connections.

Desktop: `autoplay=1` works normally.

```js
const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent);
const autoplay = isIOS ? '' : '&autoplay=1';
frame.src = 'https://player.vimeo.com/video/' + vimeoId + '?playsinline=1&title=0&byline=0&portrait=0' + autoplay + vimeoStart;
```

### Gallery Definitions
Galleries are defined in the `galleries` JS object. Key names match `data-gallery` attributes on accordion items. Each gallery has `{ items: [...] }` and optionally:
- `stripDurations: [ms, ms, ...]` — per-strip-group hold times in ms; overrides the 7s default for specific strips; unspecified strips fall back to 7s; last strip always uses `lastHoldMs`

Example with custom strip timing (raptor — syncs clip to film at 23s, holds 15s):
```js
raptor: {
    stripDurations: [7667, 7667, 7666, 15000],
    items: [...]
}
```

### Vimeo IDs (Work Section)
- Ford Ranger Raptor: `1171157858` / gallery: `raptor`
- Ford Explorer: `1171170029` / gallery: `lexieGreen`
- Land Rover Defender: `1171151952` / gallery: `defender`
- McLaren Spider: `1171150653` / gallery: `mclaren`
- RR Sport Test Track: `1171178087` / gallery: `rrSportTestTrack`
- RR Sport Reveal: `1171150941`
- RR James Corden: `1171151324` / gallery: `corden`
- Discovery Sport: `1171150533` / gallery: `discovery`
- Tata Nexon — 3 Spot Cutdown: `1171541476` / gallery: `tata2`
- Tata Nexon — Performance: `1171541065` / gallery: `tata`
- I Am Ali: `1171150609`
- Family Tree Milan World Expo: `1171151872`
- The Turtle Yeosu Expo: `1171157242`
- Vashi: `1171158700` / gallery: `vashi`
- Ford Wheels: `1172076463` / gallery: `fordWheels`
- Lexie Limitless: `1171318976` / gallery: `explorer` (data-start="1140", data-last-hold="12000")
- Everest: `1171320476` / gallery: `everest`
- Bridgestone: `1171158800`
- Football League: `1171158741`
- Golfing 4 Life: `1171158957`
- Sexy Tuesdays: `1171300697`
- Waiting for Conkers: `1171300442`

### Early Years (Password-Protected Section)
- Password: hashed with SHA-256 via Web Crypto API; plain text never in source
- Hash stored as `PASSWORD_HASH` constant; `checkPassword()` is async
- Film grid hides when a film plays; click the playing screen to return to film selection
- Five video (`1171163096`): plays for 10 seconds from first frame before triggering reveal

### Hero Image
- Background image: `images/Ford%20Mustang%20223.jpg` (1MB JPEG, down from 7MB PNG)
- Preloaded via `<link rel="preload" as="image" href="images/Ford%20Mustang%20223.jpg">` in `<head>`

### Typewriter Effect
Hero section has a typewriter animation synced to Web Audio API click sounds via `scheduleClick(atTime)`.

### Contact Section
- Email: `pushfilms@icloud.com`
- LinkedIn URL: `https://www.linkedin.com/in/greg-hobden-340a913/`
- Both styled as gold filled buttons: `.contact-link { background: var(--gold); color: #080808; }`

## Key CSS Variables
```css
--bg: #080808; --fg: #EDEDE8; --mid: #888888; --dim: #1C1C1C;
--rule: #1E1E1E; --gold: #C4A46B;
--font-serif: 'Outfit', sans-serif;
--font-sans: 'Manrope', sans-serif;
--pad: clamp(24px, 5vw, 80px); --gap: clamp(72px, 10vw, 140px);
```

## Typography
Two fonts loaded via Google Fonts:
- **Outfit** (weights 400, 500) — `var(--font-serif)` — headings, hero name, work titles, category headers
- **Manrope** (weights 300, 500) — `var(--font-sans)` — body text, descriptions, nav

## Working Conventions
- Always read a file before editing it
- Commit messages should be concise and descriptive
- Image crop adjustments use `position:'50% X%'` on gallery items — "down by X%" means increase the Y%, "up by X%" means decrease it
- Position adjustment labels use posKey convention: `galleryKey-index` (0-based), e.g. `everest-3` = 4th item in everest gallery
- Desktop film iframe wrapper: `width: 87.5%; margin: 0 auto; padding-bottom: 49.21875%; height: 0`
- Mobile film: `width: 100%; padding-bottom: 56.25%; margin: 0` (via `!important` in end-of-stylesheet media block)
- Gallery strip shows 3 thumbs on desktop, 1 on mobile (`STRIP_SIZE`), each `aspect-ratio: 3/2` desktop / `16/9` height-matched on mobile
- Inline gallery video clips are muted with no controls
- `object-position: top` is the default for all gallery images (shows heads/faces)
- Work descriptions are `color: #999`
- All `<img src="images/...">` tags have `loading="lazy"`

## Known Quirks
- Vimeo IDs were historically swapped between Raptor and Explorer — double-check if something plays the wrong film
- HEIC files don't work in browsers — always use the `.jpg` equivalent
- The `work-expand` full-bleed technique: negative margins + padding (`margin-left: calc(var(--pad) * -1)` etc.) — not `100vw/transform`
- iOS autoplay is permanently blocked for cross-origin Vimeo iframes — any attempt to force it (play(), setMuted(), autoplay=1, controls=0) causes an infinite spinner. Leave it as-is.
- The accordion desktop CSS comes after the first mobile media query — always use the second `!important` media block at end of `<style>` for mobile accordion overrides
- Pausing a film collapses the accordion (same as ending) — this is intentional
