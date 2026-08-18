# DESIGN.md — SheBelieves.pk Website v1

*Status: Directional system; final identity requires founder approval and original brand assets.*

## Design Idea

**Brave belonging outdoors.** The website should feel like a trusted invitation from a capable older sister: energetic enough to inspire action, calm enough for parents to trust, and real enough to avoid generic “women empowerment” branding.

Do not default to pink gradients, stock photos of boardrooms, raised-fist clichés, or polished NGO imagery. Use real Pakistani girls and women moving, laughing, learning, and leading together.

## Core Tokens

### Color
| Token | Hex | Use |
|---|---:|---|
| Forest | `#1D4D3E` | Primary brand, headers, buttons, trust |
| Coral | `#E76F5E` | Energy, highlights, active states |
| Sun | `#F2C75C` | Warm accent, badges, small details |
| Sky | `#B9DEE2` | Calm secondary backgrounds |
| Cream | `#FFF8ED` | Main page background |
| Ink | `#16231F` | Body copy |
| White | `#FFFFFF` | Cards and contrast surfaces |
| Mist | `#E8EFEA` | Dividers and quiet sections |
| Error | `#B63D3D` | Form errors only |

Accessibility: body text must meet WCAG AA contrast. Use Forest or Ink on Cream/White. Never set Coral or Sun as small body text on light backgrounds.

### Typography
- **Display:** Fraunces 600/700 — expressive, human, editorial.
- **Body/UI:** Manrope 400/500/600/700 — clear, modern, friendly.
- **Urdu support if added:** Noto Nastaliq Urdu for editorial Urdu; Noto Sans Arabic for compact UI.
- Keep body copy at 18px desktop / 16px mobile minimum.

### Spacing
Use an 8px base scale: `8, 16, 24, 32, 48, 64, 96`.

### Radius
- Small controls: 10px
- Cards: 18px
- Image containers: 24px
- Pills/badges: 999px

### Shadows
Keep subtle. Prefer border + tonal surface over floating glass cards.

## Layout
- Mobile first.
- Content max width: 1180px.
- Reading width: 720px.
- 12-column desktop grid; 4-column mobile grid.
- Hero should show a real group experience, not a single posed founder portrait.
- Alternate dense information sections with image-led breathing space.

## Core Components

### Header
- Logo left.
- Links: Experiences, Events, Our Story, Partner, Safety.
- Primary button: **See Upcoming Events**.
- Mobile menu must preserve the CTA.

### Event Card
Required fields:
- Event name
- Date/time
- Location zone (exact location may be revealed after registration for safety)
- Age range
- Difficulty
- Price and inclusions
- Seats status
- Lead facilitator
- CTA

### Trust Strip
Use verified facts only: women-only, trained/female facilitators if confirmed, clear event details, guardian consent for minors, support contact. Do not use numerical impact claims until verified.

### Programme Pillar Cards
Three pillars: Move, Grow, Belong. Each card gets one candid image, one sentence, and sample formats.

### Story Card
A participant image + first name/age range + approved quote + event + permission state. Never publish minors without guardian consent.

### Partner Card
Logo, relationship type, short factual contribution. Do not imply formal partnerships from event attendance or social mentions.

### Forms
- One column.
- Persistent labels; placeholders are examples only.
- Explain why sensitive information is requested.
- Error messages must say how to fix the issue.
- Confirmation page must state what happens next and when.

## Photography Direction

### Style
- Candid, documentary, warm daylight.
- Show action, friendship, preparation, and leadership.
- Keep Pakistani context visible without turning it into decoration.
- Include modest clothing naturally; do not frame it as a problem or novelty.
- Show beginners as well as confident participants.

### Required Shot List
1. Hero landscape: 4–8 participants moving outdoors, faces visible with consent.
2. Welcome moment: facilitator greeting a first-timer.
3. Safety moment: briefing, route check, gear, or buddy pairing.
4. Movement: hike, sport, horse riding, or warm-up.
5. Growth: workshop, panel, goal setting, creative activity.
6. Belonging: snack break, laughter, group circle, new friendships.
7. Founder/team portraits: environmental, not corporate headshots.
8. Parent-trust image: supervised activity or organizer briefing.
9. Partner image: real collaboration in action.
10. Vertical crops for mobile and Instagram continuity.

### Image Deliverables
- Hero: 2400×1600 landscape, WebP + original.
- Event cards: 1600×900.
- Stories: 1200×1500 portrait.
- Team: 1200×1200.
- Open Graph: 1200×630.
- Favicon/app icon: 512×512 master.
- Logo: SVG, dark, light, and one-color variants.

## Motion
- Use short fades/slides under 250ms.
- Respect `prefers-reduced-motion`.
- No autoplay background video on mobile.
- Movement should support orientation, not decoration.

## Accessibility & Privacy
- Keyboard navigation and visible focus states.
- Alt text describes the activity, not appearance.
- Captions/transcripts for video.
- Consent records for every identifiable participant.
- For minors: guardian approval, no exact routine/location exposure, no public surname by default.

## Visual QA Checklist
- Real assets, no lorem ipsum.
- No unsupported stats or fake testimonials.
- Every event communicates safety, level, inclusions, and next step.
- Text remains readable at 200% zoom.
- Mobile CTA is reachable without hunting.
- Empty events state offers a waitlist, not a dead page.
