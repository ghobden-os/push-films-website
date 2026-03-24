# Push Films Website — Claude Handoff

## Project Overview
Portfolio website for Greg Hobden, film producer. Single-page site with sections: Hero, About, Work (accordion), Early Years (password-protected music videos), and Contact.

## File Structure
- **Sole file**: `/Users/greghobden/push-films-website/index.html` — all HTML, CSS, and JS inline in one file
- **BTS page**: `/Users/greghobden/push-films-website/behind-the-scenes.html` — standalone mosaic photo gallery page, linked from nav
- **Redesign experiment**: `redesign.html` — white/minimal experimental layout (DM Sans, 3-col grid, Vimeo modal). Not linked from nav; accessible at greghobden.com/redesign.html
- **Images**: `/Users/greghobden/push-films-website/images/` — all images and video clips
- **Title cards**: `title-card.html` (name + Producer) and `title-card-2.html` (name + Producer + disciplines) — 1920×1080 HTML files for screenshotting into showreel
- **Favicon**: `favicon.svg` — yellow disc with G, used as browser tab icon on all pages
- **Design system**: `design-system.html` — full visual reference (colours, typography, components, dos & don'ts, handoff guide). Viewable at greghobden.com/design-system.html
- **Design tokens**: `design-tokens.json` — canonical W3C-format token file (colours, type scale, spacing, motion, grid). Currently v1.1.0
- **Logo assets**: `files/logo.html` — yellow disc mark + full lockup variants (DM Sans). `files/favicon.svg` — source SVG
- **PWA**: `manifest.json`, `sw.js`, `apple-touch-icon.svg`, `icon-maskable.svg` — makes site installable as home screen app on iOS/Android
- **Email signature**: `files/email-signature.html` — live preview + Apple Mail install instructions. `files/g-disc.svg` — hosted yellow G disc image used in the signature (44px circle, `#F5D800`, DM Sans G)
- **Type spec**: `files/type-spec.html` — A4 print-ready spec sheet for video editors: DM Sans, colours, name layout, disciplines
- **Corporate one-pager**: `push-films-slide.html` — 1280×720px slide for pitch/presentation use. Light + Dark versions with switcher. Photo drag tool (click and drag to reframe). Yellow 3px bar above contact details. Backed up as `push-films-slide-v1.html`.
- **Corporate one-pager PDF**: `push-films-slide.pdf` — landscape PDF export of the light version (no switcher). Generated via Chrome headless with DM Sans fonts embedded. To regenerate: rebuild `/tmp/push-films-print.html` (single slide, fonts embedded) and run `Google\ Chrome --headless --print-to-pdf=push-films-slide.pdf --no-pdf-header-footer --no-margins --paper-width=13.333 --paper-height=7.5 "file:///tmp/push-films-print.html"`

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

Gallery thumbnail fade-in uses `img.onload` — images stay `opacity:0` until fully loaded, then fade in sharp. If already cached, appears instantly. Do not revert to `requestAnimationFrame` — that showed blurry partially-decoded images.

Clicking a gallery image opens a full-screen lightbox (`#imgLightbox`).

### Lightbox
- Click a gallery image → opens fullscreen lightbox
- **← →** arrow keys navigate between images in the gallery (skips video items)
- **Space** or **Escape** or click anywhere → closes lightbox
- State tracked in `lightboxItems` (array) and `lightboxIndex` (int) module-level variables
- `openLightbox(items, index)` — takes the full items array and the rawIdx of the clicked image

### Work Section Category Order
Automotive → Documentary → Experiential → Luxury → Expo → Sport → Comedy → Everest → The Early Years → Music Videos → Commercials

### Early Years Button
`.early-years-btn` — yellow filled (`background: var(--gold)`), dark text, `padding: 16px 32px`, matches showreel button style. Hover darkens to `#D4B800`.

### Music Video Montage
`.mv-montage` — full-width grid of all 21 music video thumbnails, displayed just above the contact section. 7 columns desktop, 4 columns mobile, 3px gaps, `aspect-ratio: 16/9`, `object-fit: cover`, `opacity: 0.85`. No text, colour. Images hover to `opacity: 0.85` (already at that level — adjust if needed). Images listed in order: amy-winehouse, diana-ross, will-young, busted, Five 2, girls-aloud, klonhertz, oasis-lyla, primal-scream-kowalski, sugababes, the-streets, the-streets-blinded, westlife, snow-patrol, the-killers, atomic-kitten, LOUISE, steps, BOYZONE, A1, Just Jack.

### Performance Warning
Several work thumbnail images are very large (up to 12MB). They have `loading="lazy"` but are uncompressed. Key offenders:
- `ford-explorer-launch.png` — 12MB
- `range-rover-reveal.png` — 8.9MB
- `ford-explorer-world-record.png` — 7.6MB
These should ideally be compressed to under 200KB each.

### Mobile Layout
- `STRIP_SIZE = window.innerWidth < 640 ? 1 : 3` — set once at page load
- On mobile the gallery thumb height matches the film exactly: `calc((100vw - 2 * var(--pad)) * 0.5625)` — the multiplier must be `0.5625` (16:9), not `0.39375` (wrong). The second `@media` `!important` block at end of stylesheet holds the canonical value.
- Film is `width: 100%; padding-bottom: 56.25%; margin: 0` on mobile (overrides desktop 87.5%)
- **Touch device optimisation**: hover preview crossfade images are only preloaded on non-touch devices. Guard: `const isTouch = window.matchMedia('(pointer: coarse)').matches` — if `isTouch && !previewEditMode` the hover handler returns early, preventing unnecessary image downloads on mobile.

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
- McLaren Spider: `1171150653` / gallery: `mclaren` — meta: "Producer — Spain"
- RR Sport Test Track: `1171178087` / gallery: `rrSportTestTrack`
- RR Sport Reveal: `1171150941`
- RR James Corden: `1171151324` / gallery: `corden`
- Discovery Sport: `1171150533` / gallery: `discovery`
- Tata Nexon — 3 Spot Cutdown: `1171541476` / gallery: `tata2`
- Tata Nexon — Performance: `1171541065` / gallery: `tata`
- Iron Maiden: Burning Ambition: no Vimeo — has `data-youtube="BggdJLnSevQ"` (opens YouTube trailer in modal). Credit: **Co-Producer**, meta: "Co-Producer — Feature Documentary — Universal Pictures". Thumbnail `images/burning-ambition.png`. Release: "In cinemas May 7, 2026".
- I Am Ali: `1171150609` — meta: "Producer — Feature Documentary — Universal Pictures"
- Family Tree Milan World Expo: `1171151872` — meta: "Lead Producer / Head of Media — UAE"
- The Turtle Yeosu Expo: `1171157242` — meta: "Lead Producer / Head of Media — UAE"
- Expo 2020 — Dubai: no Vimeo — static entry, image: `images/Dubai 2020 /Expo.png`, no work-meta, `object-position: 52.4% 100%`
- Vashi: `1171158700` / gallery: `vashi`
- Ford Wheels: `1172076463` / gallery: `fordWheels`
- Lexie Limitless: `1171318976` / gallery: `explorer` (data-start="1140", data-last-hold="12000") — meta: "Producer — French Riviera"
- Everest: `1171320476` / gallery: `everest` — meta: "On-Mountain Producer — Nepal / China", thumbnail `object-position: center top`. Altitude referenced as 5,600 metres throughout.
- Bridgestone: `1171158800`
- Football League: `1171158741`
- Golfing 4 Life: `1171158957`
- Sexy Tuesdays: `1171300697`
- Waiting for Conkers: `1171300442`

### YouTube Embeds
Some music videos have been muted by Vimeo's ContentID system (copyrighted audio). These use `data-youtube="VIDEO_ID"` instead of `data-vimeo` and open in the same `#vimeoModal` via a separate click handler that builds a YouTube embed URL:
```js
vimeoFrame.src = 'https://www.youtube.com/embed/' + id + '?autoplay=1&rel=0';
```
- Busted — Year 3000: Vimeo `1175913189` (self-hosted upload via yt-dlp download of YouTube `TZ1c3MsUytc`; original Vimeo `1171144521` muted by ContentID; YouTube embeds also blocked)
- If other music videos lose audio, switch them to YouTube the same way.

### Music Video Vimeo IDs (Early Years section)
- Amy Winehouse — In My Bed: `1171159898`
- Diana Ross — Not Over You Yet: `1171144740`
- Will Young — Friday's Child: `1171146333`
- Busted — Year 3000: YouTube `Tu7HoGZaspo` (not Vimeo)
- Five — Keep On Movin': `1171163096` (special 10s reveal behaviour)
- Girls Aloud — Sound of the Underground: `1171149068`
- Klonhertz — Three Girl Rhumba: `1171142626`
- Oasis — Lyla: `1171141536`
- Primal Scream — Kowalski: `1171148695`
- Sugababes — Round Round: `1171145556`
- The Streets — Fit But You Know It: `1171146145`
- The Streets — Blinded by the Lights: `1171145969`
- Westlife — Flying Without Wings: `1171147332`

### Early Years (Password-Protected Section)
- Password: hashed with SHA-256 via Web Crypto API; plain text never in source
- Hash stored as `PASSWORD_HASH` constant; `checkPassword()` is async
- Film grid hides when a film plays; click the playing screen to return to film selection
- Five video (`1171163096`): plays for 10 seconds from first frame before triggering reveal

### Hero Section
- Background image: `images/Ford%20Mustang%20223.jpg` (1MB JPEG, down from 7MB PNG)
- Preloaded via `<link rel="preload" as="image" href="images/Ford%20Mustang%20223.jpg">` in `<head>`
- `overflow: hidden` removed from `#hero` — was clipping the Iron Maiden card at the bottom
- **Iron Maiden card** (`.hero-film-card`): dark semi-transparent background, yellow border, 128×80px thumbnail, title (14px), date and CTA (12px, date now `--fg` white). Clicks open YouTube trailer in modal. Animates in with the showreel button at 3.3s delay.
- Showreel ID: `1174080790`
- **Image rotation**: 9 images cycle every **15 minutes** via `Math.floor(Date.now() / 900000) % imgs.length`. Preview any with `?hero=N` (0–8).

### Hero Desktop Text Placement — Locked Layout
These positions are confirmed and signed off. Do not adjust without explicit instruction.

**Default heroes (0, 4, 5, 7, 8)** — name block right-of-centre, vertically centred + pushed down:
```css
.hero-main { margin-left: calc(50% + 20px); margin-top: 72px; }
```
- `margin-left: calc(50% + 20px)` — name block starts just right of centre
- `margin-top: 72px` — pushes name block down from vertical centre, creating gap below the absolutely-positioned "Film Producer & Production Consultant" label

**Defender heroes (1, 2)** — same vertical position, shifted further right:
```css
.hero-label-defender .hero-main { margin-left: calc(58% + 20px); }
```

**Explorer (hero=3)** — pinned to top-right, label inside the name block:
```css
.hero-label-explorer .hero-main { margin-top: calc(var(--nav-h) + 72px); margin-bottom: auto; }
.hero-label-explorer .hero-main .hero-rule-top { margin-bottom: 24px; }
```

**Ali (hero=6)** — pinned to top, shifted far right, disc hidden:
```css
.hero-label-ali .hero-main { margin-top: calc(var(--nav-h) + 60px); margin-bottom: auto; margin-left: calc(62% + 20px); }
.hero-label-ali .hero-main .hero-rule-top { align-self: center; margin-bottom: 20px; }
.hero-label-ali .nav-logo { display: none; }  /* disc sits on Ali's forehead — hidden */
```

**"Film Producer & Production Consultant" label** (`.hero-rule-top`):
- Desktop: absolutely positioned at `top: calc(var(--nav-h) + 48px)`, horizontally centred
- Has decorative `::before`/`::after` lines either side
- Explorer & Ali: label moved inside `.hero-main` (static flow), overridden by `.hero-main .hero-rule-top { position: static; }`
- **Mobile: hidden** (`display: none !important`) — too wide for small screens
- **Flex gap fix**: `.hero-rule-top` is a flex container with `gap: 28px`. "Film Producer" text and `<span class="hero-rule-extra">` were separate flex items each receiving the gap. Fixed by wrapping both in a single `<span>` so they form one flex item: `<div class="hero-rule-top"><span>Film Producer<span class="hero-rule-extra"> &amp; Production Consultant</span></span></div>`

### Mobile Hero Layout
The hero has significant mobile-specific overrides in the final `@media (max-width: 640px)` block:
- Background panned to `18% center` to show the car body (not just the wheel/bumper)
- `justify-content: space-between` with `padding-top: calc(var(--nav-h) + 20px)` and `padding-bottom: 52px` — pins content to top and bottom
- Dual gradient overlay: dark at top, clear in middle (car visible), dark at bottom
- Text shadows on all hero text elements for legibility over the image
- Showreel button significantly smaller: `font-size: 8px`, `padding: 10px 18px`
- `.hero-sub` has extra `margin-top` to push it away from the name
- `.hero-rule-top` hidden (`display: none !important`) — "Film Producer & Production Consultant" label not shown on mobile

### Service Worker / Caching
- `sw.js` cache key: `gh-v6` — bump this (e.g. `gh-v7`) any time you need to force all browsers to fetch fresh HTML
- The SW is cache-first for all same-origin requests. If users report seeing stale content, bump the cache version and push.
- Hero image URLs (`/?hero=N`) are cached separately per URL — old SW versions can cause different heroes to show different HTML versions
- After bumping and pushing, a new SW only activates after the first navigation — users see fresh content on the **second** page load. This is normal SW behaviour.

### Nav Logo
- Yellow disc mark: `<a href="#" class="nav-logo">G</a>` — 38px circle, `background: var(--gold)`, DM Sans weight 300, font-size 22px, color `#111111`
- Animates in on page load: `discIn` keyframe — scale from 0 + rotate −720° to full size over 1.2s, `cubic-bezier(0.22, 1, 0.36, 1)`, 0.3s delay
- `favicon.svg` — same yellow disc with G, at repo root

### Custom Cursor
- Hidden on iframe `mouseenter` to prevent cursor getting stranded over Vimeo embeds
- A `MutationObserver` on `document.body` catches dynamically inserted iframes (Vimeo embeds added on accordion open)

### Modal Close Button
- `.video-modal-close` — always yellow (`color: var(--gold)`), `font-size: 10px`, uppercase, top-right of modal overlay

### Reframe Edit Mode (index.html)
- Activated by visiting `greghobden.com/?edit=1`
- All `.work-image` thumbnails get a yellow outline and become draggable to set `object-position`
- "Copy values" button outputs `alt: X% Y%` pairs — paste back to Claude to bake into the HTML
- Tool is JS-only, invisible in normal browsing

### Scroll Progress Bar
- `#scrollProgress` — yellow 2px line at top of page showing scroll position
- `height: 2px; opacity: 0.75`

### Behind the Scenes Page (`behind-the-scenes.html`)
- Standalone dark-theme page, same fonts/CSS variables as index.html
- NOT in the main nav — accessed via direct URL or links
- Fixed `← G` back button (top-left): yellow arrow + yellow disc, animates in with `discIn` (same as nav logo). Returns to main site.
- Yellow scroll progress bar: identical to main site (`#scrollProgress`, 2px, `opacity: 0.75`)
- Linked from nav: `<li><a href="behind-the-scenes.html">Behind the Scenes</a></li>`
- CSS Grid mosaic wall: 4 cols desktop, 3 at 900px, 2 at 600px, 1 at 380px, 3px gaps
- `.wall-label` divs span full width, centred, gold, 13px uppercase — section titles
- Sections (in order): Ford Ranger Raptor, Land Rover Defender, Land Rover Discovery Sport, McLaren Spider, Lexie Limitless, Range Rover Sport, Range Rover James Corden, Go Faster (Ford Wheels), Ford Mustang, Vashi Diamonds, Tata Nexon, Miscellaneous, Everest — West Ridge Expedition
- Edit mode: activated by **Shift+E** (not `?edit=1`). Toolbar appears bottom-right. Drag-to-reframe, delete tiles, localStorage persistence (`bts-edits-v1`), export report.
- Each tile shows section name + index number (e.g. "Everest #3") when in edit mode — use this to identify images to remove
- Videos lazy-load via `data-src` / IntersectionObserver — `src` is only set when the video enters the viewport
- Lightbox with ← → arrow navigation, counter, spacebar/Escape to close
- Object-position reframes baked directly into `style` attributes on `<img>` tags after each edit session export
- **Image numbering**: global image count (all `<img loading="lazy">` tags in order) used for bulk removals — e.g. "remove image 139"

### Typewriter Effect
Hero section has a typewriter animation synced to Web Audio API click sounds via `scheduleClick(atTime)`.

### Contact Section
- Email button: `ghobden@mac.com` — styled as yellow filled button
- LinkedIn button: `https://www.linkedin.com/in/greg-hobden-340a913/` — styled as yellow filled button
- Both use `.contact-link` — must include `-webkit-appearance: none; appearance: none;` to strip Safari's default button UA styles (white background, inconsistent sizing). Also needs explicit `font-weight: 500; line-height: 1; -webkit-text-size-adjust: 100%; text-size-adjust: 100%;` to prevent iOS auto-scaling `mailto:` links to a different size than other links.

### Email Signature
- File: `files/email-signature.html` — preview page + install instructions
- Disc: hosted SVG at `files/g-disc.svg` (44px, `#F5D800`, DM Sans G) — used as `<img>` in signature so it survives email client rendering
- Current details: `ghobden@mac.com` · `07802 179 515` · `greghobden.com`
- Title line: Film Producer (no Push Films, no LinkedIn)
- Apple Mail install: must edit `.mailsignature` file directly on disk (copy-paste strips CSS). Steps on the page. Lock the file after editing or Mail overwrites it.
- Yellow vertical rule: `border-left: 2px solid #F5D800` on the `<td>` — only renders correctly via the direct file method, not via paste

## Key CSS Variables
```css
--bg: #080808; --fg: #EDEDE8; --mid: #888888; --dim: #1C1C1C;
--rule: #1E1E1E; --gold: #F5D800;
--font-serif: 'DM Sans', sans-serif;
--font-sans: 'DM Sans', sans-serif;
--pad: clamp(24px, 5vw, 80px); --gap: clamp(72px, 10vw, 140px);
```

## Typography
Single font loaded via Google Fonts:
- **DM Sans** (weights 300, 400, 500) — both `var(--font-serif)` and `var(--font-sans)` — used throughout for all text
  - Weight 300: captions, fine detail
  - Weight 400: body text, hero sub-headings
  - Weight 500: headings, nav links, UI labels

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

## Logo / Brand Identity — Status & Process

### Current live mark
The nav uses a **yellow disc G** — `background: #F5D800`, DM Sans weight 300, 38px circle, dark G letterform. This is the active brand mark on the site. Reference assets in `files/logo.html` (disc + full lockup variants) and `files/favicon.svg`.

### What's been tried (do not repeat these)
Three batches of cinematic logo concepts were built in HTML/SVG and are live at:
- `logo-preview.html` — Batch I: 3 GH monogram concepts, Outfit font. User disliked the font.
- `logo-preview-2.html` — Batch II: 4 cinematic concepts (Widescreen, Iris, Title Card, Hairline), Cormorant Garamond. User disliked the font.
- `logo-preview-3.html` — Batch III: 4 concepts (Leader, Stamp, Wipe, Title Card), Cinzel font, dark bronze `#7A5C1E` for accent on light panels. User still not happy with overall direction.

### Key lesson: wrong tool for this job
Generating logos in SVG/HTML is designing blind — Claude cannot see what it produces. Each iteration requires a commit, deploy wait, and browser review. This is a poor design loop.

### Recommended process going forward
1. **Find a direction first** — use an AI image generator (Adobe Firefly, Midjourney, DALL-E) to rapidly explore visual feelings. Prompt: *"Minimal film producer logo, initials GH, [style reference], dark background, cinematic"*. Bring a reference image back.
2. **Or use Figma (free)** — Figma Community has free logo kit templates. Drag type, try fonts, arrange marks, see it instantly.
3. **Then bring it to Claude** — once a direction is chosen visually, implement it precisely in code.

### Yellow on light backgrounds
`#F5D800` is unreadable on pale backgrounds. Use `#7A5C1E` (dark bronze) on light panels — same hue family, legible. Established in logo-preview-3.html and documented in `color.semantic.accent.onLight` token.

### Fonts tried and rejected (for logo work)
- **Outfit** — too generic, not cinematic enough
- **Cormorant Garamond** — too editorial/literary, not quite right
- **Cinzel** — Roman inscription, genuinely cinematic but user still not satisfied with overall direction

## Playwright / Browser Testing
- **Always use WebKit (Safari engine)** — Chrome conflicts with the existing Chrome session on this machine and fails to launch.
- `.mcp.json` sets `"--browser", "webkit"` — this is the correct Playwright identifier for Safari. Do not use `"safari"` as the value; Playwright does not recognise it.
- If the browser fails to launch, run `mcp__playwright__browser_install` then retry `mcp__playwright__browser_navigate`.
- After any change to `.mcp.json`, the MCP server must restart (reload the Claude Code session) to pick up the new config.

## Known Quirks
- Vimeo IDs were historically swapped between Raptor and Explorer — double-check if something plays the wrong film
- HEIC files don't work in browsers — always use the `.jpg` equivalent
- The `work-expand` full-bleed technique: negative margins + padding (`margin-left: calc(var(--pad) * -1)` etc.) — not `100vw/transform`
- iOS autoplay is permanently blocked for cross-origin Vimeo iframes — any attempt to force it (play(), setMuted(), autoplay=1, controls=0) causes an infinite spinner. Leave it as-is.
- The accordion desktop CSS comes after the first mobile media query — always use the second `!important` media block at end of `<style>` for mobile accordion overrides
- Pausing a film collapses the accordion (same as ending) — this is intentional
- Vimeo ContentID auto-mutes copyrighted music — if a music video has no audio, switch it to a YouTube embed using `data-youtube` attribute
- BTS section label "Go Faster" = Ford Wheels shoot (not a separate project)
