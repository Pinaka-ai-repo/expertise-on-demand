# Expertise on Demand

Source for **[www.tonysharma.com](https://www.tonysharma.com/)** —
the expert-network advisor profile for Mohit Sharma (ACMA, CGMA).

Static site, no build toolchain, no dependencies at runtime. GitHub Pages serves it on the custom domain in `CNAME`,
building from `main` at the repository root.

## Layout

| Path | Purpose |
|---|---|
| `index.html` | The whole page — markup, design tokens, and CSS inline. Generated. |
| `assets/` | Fonts (Inter, Syne, JetBrains Mono — latin subsets), network logos, headshot, share card |
| `build.py` | Regenerates `index.html` |
| `groups.json` | The 315 advisory topics, grouped into 15 domains |
| `networks.json` | The 13 expert networks shown in the logo rows |

## Editing

Change copy or layout in `build.py`; change the topic list in `groups.json`;
change the logo rows in `networks.json`. Then:

```bash
python3 build.py
```

That rewrites `index.html`. Commit and push — Pages redeploys in about a minute.

## Notes

- Light and dark palettes are authored separately, not inverted, and follow the
  system setting via `prefers-color-scheme`.
- Network logos sit on a light plate in both themes: most of the source marks ship
  with an opaque white background, so a dark-mode filter would flatten them.
- All motion is gated behind `prefers-reduced-motion`; the logo rows become a
  scroll-snap carousel when motion is reduced.
