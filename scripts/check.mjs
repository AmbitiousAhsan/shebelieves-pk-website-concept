#!/usr/bin/env node
/**
 * Content + integrity gate for the SheBelieves concept preview.
 *
 *   node scripts/check.mjs          → checks the authored source (index.html + public/)
 *   node scripts/check.mjs --dist   → checks the production build in dist/
 *
 * It fails on the things that would actually embarrass this page in front of the
 * founders: missing assets, dead anchors, unsafe external links, story cards that
 * drift from the source manifest, invented claims, or leaked contact details.
 */
import { readFileSync, existsSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { parse } from 'node-html-parser';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DIST_MODE = process.argv.includes('--dist');
const HTML_FILE = DIST_MODE ? path.join(ROOT, 'dist', 'index.html') : path.join(ROOT, 'index.html');
const PUBLIC_DIR = path.join(ROOT, 'public');
const DIST_DIR = path.join(ROOT, 'dist');

const ALLOWED_HOSTS = new Set(['www.instagram.com', 'www.tiktok.com']);

const REQUIRED_COPY = [
  'Independent concept preview · Built from public SheBelieves content for founder feedback.',
  'Find your next brave thing',
  '— and your people.',
  'Twin Cities Sisterhood Community to Connect, Network, Grow Learn Leadership.',
  'Concept &amp; build by Ahsan Khan.',
  'https://www.instagram.com/shebelieves.pk/',
  'https://www.tiktok.com/@shebelieves.pk',
];

const REQUIRED_IDS = ['main', 'top', 'belonging', 'lanes', 'seen', 'first-time', 'join', 'connect'];

const BANNED_PATTERNS = [
  { label: 'placeholder copy', re: /\b(lorem ipsum|todo:|tbd\b|placeholder|coming soon|dummy text)/i },
  { label: 'invented participant metrics', re: /\b\d[\d,.]*\+?\s*(members|women joined|participants|events hosted|happy members)\b/i },
  { label: 'invented rating/testimonial metrics', re: /\b\d(\.\d)?\s*\/\s*5\s*(stars|rating)\b/i },
  { label: 'implied commissioned client relationship', re: /\b(official website of|our client|client project for|commissioned by)\b/i },
  { label: 'unsupported price claim', re: /\b(rs\.?|pkr)\s?\d/i },
  { label: 'published email address', re: /[\w.+-]+@[\w-]+\.[\w.]{2,}/ },
  { label: 'published phone number', re: /\+92[\s\d-]{7,}/ },
];

const errors = [];
const warnings = [];
const fail = (message) => errors.push(message);
const warn = (message) => warnings.push(message);

if (!existsSync(HTML_FILE)) {
  console.error(`✖ ${path.relative(ROOT, HTML_FILE)} not found${DIST_MODE ? ' — run `npm run build` first.' : '.'}`);
  process.exit(1);
}

const html = readFileSync(HTML_FILE, 'utf8');
const doc = parse(html, { comment: false, blockTextElements: { script: true, style: true } });
const manifest = JSON.parse(readFileSync(path.join(PUBLIC_DIR, 'assets', 'story-source-manifest.json'), 'utf8'));

/* ── Local asset references resolve to real files ─────────────────────── */
function resolveLocal(reference) {
  const clean = reference.split('#')[0].split('?')[0];
  if (!clean || clean.startsWith('http') || clean.startsWith('mailto:') || clean.startsWith('data:')) return null;
  const relative = clean.replace(/^\.\//, '').replace(/^\//, '');
  if (DIST_MODE) return path.join(DIST_DIR, relative);
  return relative.startsWith('src/') ? path.join(ROOT, relative) : path.join(PUBLIC_DIR, relative);
}

const references = [
  ...doc.querySelectorAll('img[src]').map((node) => node.getAttribute('src')),
  ...doc.querySelectorAll('script[src]').map((node) => node.getAttribute('src')),
  ...doc.querySelectorAll('link[href]').map((node) => node.getAttribute('href')),
  ...doc.querySelectorAll('a[href]').map((node) => node.getAttribute('href')),
  ...doc.querySelectorAll('meta[content]')
    .filter((node) => /^(og:image|twitter:image)$/.test(node.getAttribute('property') ?? node.getAttribute('name') ?? ''))
    .map((node) => node.getAttribute('content')),
];

for (const reference of new Set(references.filter(Boolean))) {
  const resolved = resolveLocal(reference);
  if (!resolved) continue;
  if (!existsSync(resolved) || !statSync(resolved).isFile()) {
    fail(`missing local asset: ${reference}`);
  }
}

if (DIST_MODE) {
  for (const reference of new Set(references.filter(Boolean))) {
    if (reference.includes('/src/')) fail(`built HTML still points at a source file: ${reference}`);
  }
  const cssLinks = doc.querySelectorAll('link[rel="stylesheet"]');
  if (cssLinks.length !== 1) fail(`expected exactly one bundled stylesheet, found ${cssLinks.length}`);
  const moduleScripts = doc.querySelectorAll('script[type="module"][src]');
  if (moduleScripts.length !== 1) fail(`expected exactly one bundled module script, found ${moduleScripts.length}`);
}

/* ── Head / SEO ───────────────────────────────────────────────────────── */
const title = doc.querySelector('title')?.text.trim() ?? '';
if (title.length < 15 || title.length > 75) fail(`title length ${title.length} is outside 15–75 characters`);

const metaContent = (selector) => doc.querySelector(selector)?.getAttribute('content')?.trim() ?? '';
const description = metaContent('meta[name="description"]');
if (description.length < 70 || description.length > 240) {
  fail(`meta description length ${description.length} is outside 70–240 characters`);
}

const requiredMeta = [
  'meta[name="theme-color"]',
  'meta[name="twitter:card"]',
  'meta[property="og:type"]',
  'meta[property="og:title"]',
  'meta[property="og:description"]',
  'meta[property="og:image"]',
  'meta[property="og:image:alt"]',
];
for (const selector of requiredMeta) {
  if (!metaContent(selector)) fail(`missing or empty ${selector}`);
}

if (doc.querySelector('html')?.getAttribute('lang') !== 'en') fail('html[lang] must be set to "en"');
if (!doc.querySelector('link[rel="icon"]')) fail('missing favicon link');
if (!doc.querySelector('link[rel="apple-touch-icon"]')) fail('missing apple-touch-icon link');
if (!doc.querySelector('link[rel="manifest"]')) fail('missing web app manifest link');

/* ── Landmarks, headings, anchors ─────────────────────────────────────── */
for (const id of REQUIRED_IDS) {
  if (!doc.querySelector(`#${id}`)) fail(`missing required element id: #${id}`);
}

const h1s = doc.querySelectorAll('h1');
if (h1s.length !== 1) fail(`expected exactly one <h1>, found ${h1s.length}`);
if (!doc.querySelector('header')) fail('missing <header> landmark');
if (!doc.querySelector('main#main')) fail('missing <main id="main"> landmark');
if (!doc.querySelector('footer')) fail('missing <footer> landmark');
if (!doc.querySelector('nav[aria-label]')) fail('navigation is missing an aria-label');

const ids = new Set(doc.querySelectorAll('[id]').map((node) => node.getAttribute('id')));
for (const anchor of doc.querySelectorAll('a[href^="#"]')) {
  const target = anchor.getAttribute('href').slice(1);
  if (!ids.has(target)) fail(`anchor points at a missing id: #${target}`);
}

for (const section of doc.querySelectorAll('section')) {
  if (!section.getAttribute('aria-labelledby') && !section.getAttribute('aria-label')) {
    fail('a <section> has no accessible name (aria-label or aria-labelledby)');
  }
}
for (const reference of doc.querySelectorAll('[aria-labelledby]')) {
  const target = reference.getAttribute('aria-labelledby');
  if (!ids.has(target)) fail(`aria-labelledby points at a missing id: ${target}`);
}

const toggle = doc.querySelector('[data-menu-toggle]');
if (!toggle) fail('mobile menu toggle is missing');
else {
  if (toggle.getAttribute('aria-expanded') !== 'false') fail('menu toggle must start with aria-expanded="false"');
  const controls = toggle.getAttribute('aria-controls');
  if (!controls || !ids.has(controls)) fail('menu toggle aria-controls does not resolve');
}

/* ── Images ───────────────────────────────────────────────────────────── */
for (const image of doc.querySelectorAll('img')) {
  const src = image.getAttribute('src') ?? '(no src)';
  const alt = image.getAttribute('alt');
  if (alt === undefined || alt === null) fail(`img without alt attribute: ${src}`);
  else if (alt.trim().length < 8) fail(`img alt text is too thin to be useful: ${src}`);
  if (!image.getAttribute('width') || !image.getAttribute('height')) {
    fail(`img without intrinsic width/height (layout shift): ${src}`);
  }
}

/* ── External links ───────────────────────────────────────────────────── */
for (const link of doc.querySelectorAll('a[href^="http"]')) {
  const href = link.getAttribute('href');
  const url = new URL(href);
  if (!ALLOWED_HOSTS.has(url.host)) fail(`unexpected external host: ${href}`);
  if (link.getAttribute('target') !== '_blank') fail(`external link must open in a new tab: ${href}`);
  const rel = link.getAttribute('rel') ?? '';
  if (!rel.includes('noopener') || !rel.includes('noreferrer')) {
    fail(`external link needs rel="noopener noreferrer": ${href}`);
  }
  if (link.text.trim().length < 3) fail(`external link has no readable label: ${href}`);
}

/* ── Story cards must match the public source manifest ────────────────── */
const manifestBySource = new Map(manifest.map((entry) => [entry.source_url, entry]));
const manifestByAsset = new Map(manifest.map((entry) => [entry.asset.replace(/^\//, ''), entry]));
const usedAssets = new Set();

const storyLinks = doc.querySelectorAll('[data-story-link]');
if (storyLinks.length !== manifest.length) {
  fail(`expected ${manifest.length} story cards (one per manifest entry), found ${storyLinks.length}`);
}

for (const card of storyLinks) {
  const href = card.getAttribute('href');
  if (!manifestBySource.has(href)) {
    fail(`story card links to a URL that is not in the source manifest: ${href}`);
  }
  if (!card.text.includes('From @shebelieves.pk')) {
    fail(`story card is missing the visible "From @shebelieves.pk" credit: ${href}`);
  }
  const image = card.querySelector('img');
  const assetPath = image?.getAttribute('src')?.replace(/^\.\//, '') ?? '';
  const entry = manifestByAsset.get(assetPath);
  if (!entry) {
    fail(`story card image is not a manifest asset: ${assetPath}`);
    continue;
  }
  usedAssets.add(assetPath);
  if (entry.source_url !== href) {
    fail(`story card image ${assetPath} is credited to the wrong post (${href})`);
  }
}

for (const entry of manifest) {
  const assetPath = entry.asset.replace(/^\//, '');
  if (!usedAssets.has(assetPath)) fail(`manifest asset is never shown on the page: ${assetPath}`);
  const onDisk = path.join(DIST_MODE ? DIST_DIR : PUBLIC_DIR, assetPath);
  if (!existsSync(onDisk)) fail(`manifest asset missing on disk: ${assetPath}`);
}

/* Intrinsic sizes in the markup must match the real files in the manifest. */
for (const image of doc.querySelectorAll('img[src*="assets/stories/"]')) {
  const assetPath = image.getAttribute('src').replace(/^\.\//, '');
  const entry = manifestByAsset.get(assetPath);
  if (!entry) continue;
  const [width, height] = entry.dimensions;
  if (Number(image.getAttribute('width')) !== width || Number(image.getAttribute('height')) !== height) {
    fail(
      `img ${assetPath} declares ${image.getAttribute('width')}×${image.getAttribute('height')} but the file is ${width}×${height}`,
    );
  }
}

/* ── Copy guarantees ──────────────────────────────────────────────────── */
for (const phrase of REQUIRED_COPY) {
  if (!html.includes(phrase)) fail(`required copy is missing from the page: "${phrase}"`);
}

const visibleText = (() => {
  const body = doc.querySelector('body');
  if (!body) return '';
  for (const node of body.querySelectorAll('script, style')) node.remove();
  return body.text.replace(/\s+/g, ' ');
})();

for (const { label, re } of BANNED_PATTERNS) {
  const match = visibleText.match(re);
  if (match) fail(`${label} found in visible copy: "${match[0].trim()}"`);
}

if (!/women-only|women only/i.test(visibleText)) fail('the women-only positioning is not stated in the copy');
if (!/twin cities/i.test(visibleText)) fail('the Twin Cities positioning is not stated in the copy');

const wordCount = visibleText.trim().split(/\s+/).length;
if (wordCount < 450) warn(`page copy is only ${wordCount} words — thinner than a finished concept should be`);

/* ── Report ───────────────────────────────────────────────────────────── */
const scope = DIST_MODE ? 'dist/index.html' : 'index.html';
for (const message of warnings) console.warn(`⚠ ${message}`);

if (errors.length > 0) {
  for (const message of errors) console.error(`✖ ${message}`);
  console.error(`\n${errors.length} problem(s) found in ${scope}.`);
  process.exit(1);
}

console.log(
  [
    `✓ ${scope} passed`,
    `  · ${doc.querySelectorAll('img').length} images with alt text and intrinsic sizes`,
    `  · ${storyLinks.length}/${manifest.length} story cards matched to the public source manifest`,
    `  · ${doc.querySelectorAll('a[href^="http"]').length} external links restricted to ${[...ALLOWED_HOSTS].join(', ')}`,
    `  · ${wordCount} words of copy, no banned claims or contact details`,
  ].join('\n'),
);
