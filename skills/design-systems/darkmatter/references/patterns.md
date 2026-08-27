# Screen-level patterns

Cross-cutting composition guidance for darkmatter screens. For component APIs see `components/`; for tokens see `foundations/`.

## Page shell

```tsx
<div className="min-h-screen bg-background text-foreground">
  <header>{/* nav: white wordmark + font-mono links */}</header>
  <main className="mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8">
    {/* sections with py-16 / py-24 rhythm */}
  </main>
  <footer>{/* muted-foreground, font-mono meta */}</footer>
</div>
```

The root layout already sets `bg-background` and the dark theme; you mainly compose `main`.

## Hero

- One `DottedGlowBackground` (or `BackgroundBeams`) as an absolute layer behind `relative z-10` content.
- Display heading in `font-mono`, `text-5xl`–`text-7xl`, `tracking-tight`.
- Eyebrow label in `font-mono uppercase tracking-[0.2em] text-muted-foreground`.
- CTAs: primary `Button` + a `HoverBorderGradient` for the marquee action.
- Keep to a single hero effect — don't stack beams + spotlight + wobble.

## Feature / product grid

`grid gap-6 sm:grid-cols-2 lg:grid-cols-3` of `Card`s or `CardSpotlight`s. Titles in `font-mono`, body in `text-muted-foreground`. Use product accent colors (`oklch(var(--accent-emerald))`, etc.) sparingly to distinguish products.

## Dashboard / app

- `SidebarProvider` + `Sidebar` (auto mobile drawer) for nav.
- `Card`s for panels; `Table` for data (IDs/metrics in `font-mono`).
- `Tabs` to segment views; `Badge` (often `font-mono`) for status chips.
- `sonner` for transient feedback.

## Long-form (blog / docs)

Wrap rendered markdown in `<div className="prose-dark">` — it sets Lora body + Monaspace Xenon headings and constrains line length to ~680px. Don't hand-style headings/paragraphs.

## Voice

Terminal-forward and precise. Lead with `font-mono` for brand/display/labels/metrics; keep paragraphs in `font-sans` (Geist). Muted secondary text (`text-muted-foreground`). Restraint over decoration — the black canvas and mono type do the work; glows are accents.
