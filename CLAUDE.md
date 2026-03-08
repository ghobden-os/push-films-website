# Push Films Website — Claude Handoff

## Project Overview
Portfolio website for Greg Hobden, film producer. Single-page site with sections: Hero, About, Work (accordion), Early Years (password-protected music videos), and Contact.

## File Structure
- **Sole file**: `/Users/greghobden/push-films-website/index.html` — all HTML, CSS, and JS inline in one file
- **Images**: `/Users/greghobden/push-films-website/images/` — all images and video clips

## Deployment Pipeline
- Git → GitHub (`ghobden-os/push-films-website`) → Netlify (auto-deploys on push to `main`)
- Always commit and push when the user confirms — do not wait to be asked twice
- Always `git add` image files explicitly when they are newly referenced; they are often not yet tracked

## Filename Gotchas
- Filenames with spaces must be URL-encoded in HTML (e.g. `EWR (12).jpg` → `images/EWR%20(12).jpg`)
- Some EVEREST images have a leading space: ` EVEREST19.jpg` — the space is part of the filename
- When adding images to git, quote filenames with spaces: `git add "images/EWR (12).jpg"`

## Architecture

### Accordion (Work Section)
Each work item is an `<article class="work-item accordion" data-vimeo="XXXXXXX" data-gallery="key">`.

When clicked it expands to show:
- **Film** (Vimeo iframe) full width at top
- **Gallery strip** of 3 thumbnail images/clips below, auto-advancing in groups of 3 every 3.5s
- After one full loop the gallery hides and the film plays solo full width
- When the film ends the accordion auto-collapses
- Only one accordion can be open at a time (`currentlyExpanded` global)

Gallery items support a `position` property for per-image `object-position` cropping:
```js
{type:'image', src:'images/foo.jpg', position:'50% 30%'}
```
All gallery images default to `object-position: top` via CSS.

### Gallery Definitions
Galleries are defined in the `galleries` JS object. Key names match `data-gallery` attributes on accordion items. Each gallery has `{ items: [...] }` and optionally `{ vimeo: 'ID', items: [...] }`.

### Vimeo IDs (Work Section)
- Ford Ranger Raptor: `1171157858` / gallery: `raptor`
- Ford Explorer: `1171170029` / gallery: `lexieGreen`
- Land Rover Defender: `1171151952` / gallery: `defender`
- McLaren Spider: `1171150653`
- RR Sport Test Track: `1171178087` / gallery: `rrSportTestTrack`
- RR Sport Reveal: `1171150941`
- RR James Corden: `1171151324` / gallery: `corden`
- Discovery Sport: `1171150533`
- Tata Nexon: gallery: `tata` (no vimeo)
- I Am Ali: `1171150609`
- Family Tree Milan: `1171151872`
- The Turtle Yeosu: `1171157242`
- Vashi: `1171158700` / gallery: `vashi`
- Ford Wheels: gallery: `fordWheels` (no vimeo)
- Lexie Limitless: `1171318976` / gallery: `explorer`
- Everest: `1171320476` / gallery: `everest`
- Bridgestone: `1171158800`
- Football League: `1171158741`
- Golfing 4 Life: `1171158957`
- Sexy Tuesdays: `1171300697`
- Waiting for Conkers: `1171300442`

### Early Years (Password-Protected Section)
- Password: stored in JS, section hidden behind password gate
- Film grid hides when a film plays; click the playing screen to return to film selection
- Five video (`1171163096`): plays for 10 seconds from first frame before triggering reveal

### Typewriter Effect
Hero section has a typewriter animation synced to Web Audio API click sounds via `scheduleClick(atTime)`.

## Key CSS Variables
```css
--bg: #080808; --fg: #EDEDE8; --mid: #555555; --dim: #1C1C1C;
--rule: #1E1E1E; --gold: #C4A46B;
--font-serif: 'Cormorant Garamond'; --font-sans: 'Inter';
--pad: clamp(24px, 5vw, 80px); --gap: clamp(72px, 10vw, 140px);
```

## Working Conventions
- Always read a file before editing it
- Commit messages should be concise and descriptive
- Image crop adjustments use `position:'50% X%'` on gallery items — "down by X%" means increase the Y%, "up by X%" means decrease it
- The accordion expand panel uses `width: 100vw; left: 50%; transform: translateX(-50%)` to break out of the container for full-width display
- Gallery strip shows 3 thumbnails at a time (`STRIP_SIZE = 3`), advances by 3
- Inline gallery video clips are muted with no controls
- `object-position: top` is the default for all gallery images (shows heads/faces)

## Known Quirks
- Vimeo IDs were historically swapped between Raptor and Explorer — double-check if something plays the wrong film
- HEIC files don't work in browsers — always use the `.jpg` equivalent
- The `work-expand` full-bleed technique: `width:100vw; position:relative; left:50%; transform:translateX(-50%); padding-left:var(--pad); padding-right:var(--pad)`
