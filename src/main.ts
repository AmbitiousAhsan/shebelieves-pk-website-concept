/* Styles are linked directly from index.html so the page renders fully without JS. */

const prefersReducedMotion = (): boolean =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/** Sticky header gets a hairline + shadow only once the page has scrolled. */
function initHeaderState(): void {
  const header = document.querySelector<HTMLElement>('[data-header]');
  if (!header) return;

  const update = (): void => {
    header.classList.toggle('is-stuck', window.scrollY > 8);
  };

  update();
  window.addEventListener('scroll', update, { passive: true });
}

/** Mobile menu: accessible toggle, Escape/backdrop dismissal, focus returned to the button. */
function initMobileMenu(): void {
  const toggle = document.querySelector<HTMLButtonElement>('[data-menu-toggle]');
  const menu = document.querySelector<HTMLElement>('[data-menu]');
  const label = document.querySelector<HTMLElement>('[data-menu-label]');
  const header = document.querySelector<HTMLElement>('[data-header]');
  if (!toggle || !menu) return;

  const setOpen = (open: boolean, restoreFocus = false): void => {
    if (open && header) {
      // The concept notice above the header changes height with the viewport,
      // so the panel is offset from wherever the header actually ends.
      menu.style.setProperty('--menu-offset', `${Math.round(header.getBoundingClientRect().bottom)}px`);
    }
    toggle.setAttribute('aria-expanded', String(open));
    menu.hidden = !open;
    document.body.classList.toggle('is-locked', open);
    if (label) label.textContent = open ? 'Close' : 'Menu';
    if (open) {
      // preventScroll keeps the first link from scrolling itself under the sticky header.
      menu.querySelector<HTMLAnchorElement>('a')?.focus({ preventScroll: true });
    } else if (restoreFocus) {
      toggle.focus();
    }
  };

  toggle.addEventListener('click', () => {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });

  menu.addEventListener('click', (event) => {
    const target = event.target as HTMLElement;
    if (target === menu || target.closest('[data-menu-link]')) setOpen(false);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setOpen(false, true);
    }
  });

  const desktop = window.matchMedia('(min-width: 62rem)');
  desktop.addEventListener('change', (event) => {
    if (event.matches) setOpen(false);
  });
}

/** Marks the nav link whose section currently occupies the viewport. */
function initScrollSpy(): void {
  const links = Array.from(document.querySelectorAll<HTMLAnchorElement>('[data-nav-link]'));
  if (links.length === 0) return;

  const sections = links
    .map((link) => {
      const id = link.getAttribute('href')?.slice(1) ?? '';
      const section = document.getElementById(id);
      return section ? { link, section } : null;
    })
    .filter((entry): entry is { link: HTMLAnchorElement; section: HTMLElement } => entry !== null);

  if (sections.length === 0) return;

  const setCurrent = (active: HTMLAnchorElement | null): void => {
    for (const { link } of sections) {
      if (link === active) {
        link.setAttribute('aria-current', 'true');
      } else {
        link.removeAttribute('aria-current');
      }
    }
  };

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const match = sections.find(({ section }) => section === entry.target);
        if (match) setCurrent(match.link);
      }
    },
    { rootMargin: '-45% 0px -50% 0px', threshold: 0 },
  );

  for (const { section } of sections) observer.observe(section);

  window.addEventListener(
    'scroll',
    () => {
      if (window.scrollY < 120) setCurrent(null);
    },
    { passive: true },
  );
}

/** Subtle enter animation; skipped entirely when motion is reduced. */
function initReveals(): void {
  const items = Array.from(document.querySelectorAll<HTMLElement>('[data-reveal]'));
  if (items.length === 0) return;

  if (prefersReducedMotion() || !('IntersectionObserver' in window)) {
    for (const item of items) item.classList.add('is-visible');
    return;
  }

  const observer = new IntersectionObserver(
    (entries, self) => {
      entries.forEach((entry, index) => {
        if (!entry.isIntersecting) return;
        const element = entry.target as HTMLElement;
        element.style.transitionDelay = `${Math.min(index, 4) * 60}ms`;
        element.classList.add('is-visible');
        self.unobserve(element);
      });
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.12 },
  );

  for (const item of items) observer.observe(item);
}

function initFooterYear(): void {
  const slot = document.querySelector<HTMLElement>('[data-year]');
  if (slot) slot.textContent = String(new Date().getFullYear());
}

initHeaderState();
initMobileMenu();
initScrollSpy();
initReveals();
initFooterYear();
