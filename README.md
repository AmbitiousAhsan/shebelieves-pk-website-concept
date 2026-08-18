# SheBelieves.pk — single-page website concept

An independent, research-backed single-page concept for **SheBelieves**, a women-only Twin Cities
(Islamabad / Rawalpindi) sisterhood community. It is a static site: Vite, TypeScript, hand-written
semantic HTML and CSS, no framework and no runtime dependencies.

> **Status:** Independent concept preview, built from public SheBelieves content for founder
> feedback. It is not an official SheBelieves website and not a commissioned client project.

## What is on the page

1. Concept-preview notice.
2. Sticky, keyboard-accessible header with the supplied logo, anchor navigation, Instagram CTA and a
   mobile menu.
3. Hero — “Find your next brave thing — and your people.” with an editorial photo composition.
4. Move · Create · Connect · Grow identity strip.
5. Manifesto: why belonging, not the activity, is the real product.
6. Six experience lanes — Adventure, Sport, Create, Reset, Gather, Give Back.
7. “Seen in the community” — eight real frames, each linking to its exact public source post.
8. First-timer section answering “Can I come alone?” without inventing operational promises.
9. Three-step path: discover on social → DM and check details → show up.
10. Final CTA (Instagram + TikTok) and a footer with source attribution and credits.

## Requirements

- Node.js 20.19+ or 22.12+ (developed on Node 24)
- npm 10+

## Setup

```bash
npm install
npm run dev        # http://127.0.0.1:5173
```

## Scripts

| Script | What it does |
| --- | --- |
| `npm run dev` | Vite dev server with hot reload |
| `npm run build` | Production build into `dist/` |
| `npm run preview` | Serves the built `dist/` locally |
| `npm run typecheck` | `tsc --noEmit` in strict mode |
| `npm run check` | Typecheck **plus** the content/integrity gate against `index.html` |
| `npm run check:dist` | Same gate against the built `dist/index.html` |
| `npm run verify` | check → build → check:dist (the full gate) |

### What `npm run check` actually enforces

`scripts/check.mjs` is not a formality. It fails the build when:

- a referenced image, icon, stylesheet, script or manifest file does not exist on disk;
- an in-page anchor, `aria-labelledby` or `aria-controls` target does not resolve;
- an image is missing alt text or intrinsic `width`/`height`;
- a story card links to a URL that is not in `public/assets/story-source-manifest.json`, is credited
  to the wrong post, or is missing the visible “From @shebelieves.pk” label;
- the declared image dimensions drift from the real files in the manifest;
- an external link is not `target="_blank" rel="noopener noreferrer"`, or points anywhere other than
  the official Instagram/TikTok accounts;
- required copy (hero headline, concept notice, public bio, credits) is missing;
- the copy contains placeholders, invented metrics, prices, an email address or a phone number;
- SEO/head essentials (title, description, theme colour, Open Graph, favicon, manifest, `lang`,
  single `<h1>`, landmarks) are missing.

## Build and deployment

```bash
npm run verify     # check + build + dist check
```

The output in `dist/` is fully static. `vite.config.ts` sets `base: './'`, so every asset reference
is relative and the **same build works both at a domain root and under a subpath** such as
`https://example.com/shebelieves-preview/` or GitHub Pages project hosting — no rebuild or
environment variable needed. Bundled JS/CSS lands in `dist/build/` so it can never collide with the
copied `public/assets/` tree.

Deploy by copying `dist/` to any static host (nginx location, Netlify, GitHub Pages, S3). Nothing on
this page needs a server runtime, a database or an API key.

## Brand assets

`scripts/build_brand_assets.py` derives everything from the supplied logo file
(`public/assets/shebelieves-logo.webp`) and the selected story frames:

- `public/assets/brand/shebelieves-logo.png` — the same lockup with the flat white studio background
  converted to alpha (nothing redrawn or recoloured);
- `public/assets/brand/wing-mark.png`, `icon-192/512`, `apple-touch-icon`, `public/favicon.ico` —
  square icons built from a crop of the logo's wing;
- `public/assets/og-cover.jpg` — the 1200×630 social card.

It also re-crops `climbing-courage.webp` so a third-party TikTok username that was visible in the
original overlay is not republished here. Run it with any Python 3 that has Pillow installed:

```bash
python3 scripts/build_brand_assets.py
```

The colour palette (deep ink `#011246`, magenta `#C11458`, warm off-white `#FBF6EF`) is sampled from
the logo file itself; `src/styles/tokens.css` is the single source of truth for it. Type is
self-hosted Fraunces + Manrope via `@fontsource-variable`, so the page makes no third-party font
requests.

## Content sources

Every photograph, activity, quote and link on the page comes from public SheBelieves channels:

- Instagram: <https://www.instagram.com/shebelieves.pk/>
- TikTok: <https://www.tiktok.com/@shebelieves.pk>
- Per-image source index: `public/assets/story-source-manifest.json` (also linked from the page)
- Research notes behind the copy: `research/social-content-library.md`,
  `research/website-asset-pack.md`, `research/DESIGN.md`

The public bio quoted on the page — “Twin Cities Sisterhood Community to Connect, Network, Grow
Learn Leadership.” — is SheBelieves' own.

## Ethical use

- **Nothing is invented.** No upcoming events, participant counts, testimonials, prices, partners,
  safety procedures or impact metrics appear anywhere, because none of those are publicly verified.
  The check script actively blocks them from creeping in later.
- **No implied client relationship.** The page states, in the header and the footer, that it is an
  independent concept preview built for founder feedback.
- **No private contact details.** Only the public Instagram and TikTok accounts are linked; no
  personal or founder email address or phone number is published.
- **Images belong to SheBelieves and to the women in them.** They are used here as public-source
  references with a visible “From @shebelieves.pk” credit and a link to the original post. If the
  SheBelieves team asks for any image, quote or the preview itself to be taken down or changed, that
  request wins immediately.
- **Before anything goes public beyond founder review**, confirm: photo permissions, founder and
  team names, service area, activity list, age eligibility, and whether the preview may be used as a
  portfolio case study.

Concept & build by Ahsan Khan.
