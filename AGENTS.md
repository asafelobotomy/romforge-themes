# romforge-themes

Community themes for the fullscreen mode of romforge. Data only: each theme is a folder of CSS, JSON and images; there is no build.

## Commands
CI (`.github/workflows/check.yml`) runs these three; run them before every commit:
- `romforge-cli themes index . --check` (verifies every theme as romforge does and that `themes.json` is current). `romforge-cli` comes from `cargo install --git https://github.com/asafelobotomy/romforge romforge-cli --locked` (needs `libudev-dev`).
- `python3 tools/audit.py .` (colour contrast, unused fonts and options, card-rule specificity, preview size).
- `python3 tools/readme.py . --check` (README theme list is current).
Regenerate instead of hand-editing: `romforge-cli themes index .` (writes `themes.json`) and `python3 tools/readme.py` (rewrites the README theme section between the `themes:start` markers).

## Layout
- `themes/<id>/`: `theme.json` (manifest: name, version, licence, schemes, options), `theme.css`, optional `preview.png` (1280x720), `img/`, `fonts/`. Folder name = id: lower-case letters, digits, dashes.
- `themes.json`: generated index. `tools/`: `audit.py`, `readme.py`. `docs/`: pictures used by the README.

## Conventions
- Commit `themes.json` and `README.md` together with the theme change.
- Raise `"version"` in `theme.json` with every change to a theme (romforge offers updates by version); `"licence"` is required, plus `"licence_url"` where it is read.
- Themes are data, not code: no `@import`, no links outside the folder, no URLs to other sites, no CSS escapes. At most 256 KB of CSS and 8 MB per theme. Only png, jpg, webp, svg, woff2, woff, ttf files; no other files (e.g. `LICENSES.md`); record licences in the theme description or a comment heading `theme.css`.
- No console makers' logos, trademarks or box art; fonts and pictures only under a licence that allows sharing.
- Card rules must be written `:scope [data-fs-card]` / `:scope [data-fs-row]` so they outrank romforge's own card style.
- Try a theme locally: `ROMFORGE_THEMES_INDEX=~/romforge-themes romforge-app`.
- The format reference is romforge's GUIDE.md (fullscreen themes section), in the romforge repository, not here.
