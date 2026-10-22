# Adding a theme

A theme is a folder in `themes/<id>/`. The folder's name is the theme's id:
lower-case letters, digits and dashes.

```
themes/my-theme/
  theme.json     the manifest: name, version, licence, schemes, options
  theme.css      one stylesheet
  preview.png    1280×720, how it looks (optional, but please add one)
  img/ fonts/    any pictures and fonts it uses (png, jpg, webp, svg, woff2, woff, ttf)
```

The theme format, its variables and its `data-fs-*` hooks are in romforge's
[guide](https://github.com/asafelobotomy/romforge/blob/main/GUIDE.md#fullscreen-themes).
Here it also needs a `"version"` (raise it with every change, so romforge
offers the update) and a `"licence"`, with `"licence_url"` where it is read.

## Try it

Copy the folder into your own themes folder (romforge's Settings → Display
opens it) and pick it in the fullscreen mode; it reloads as you edit. Or
point romforge at your checkout of this repository:

```bash
ROMFORGE_THEMES_INDEX=~/romforge-themes romforge-app
```

## Before a pull request

```bash
romforge-cli themes index .      # writes themes.json, checking every theme
```

Commit `themes.json` with your theme. The check workflow runs
`romforge-cli themes index . --check`: the same checks romforge makes before
it installs anything.

## The rules

- **A licence that lets others share it.** Any open licence works (CC0, CC BY,
  CC BY-SA, MIT…). Non-commercial ones (CC BY-NC) are allowed and shown as
  they are.
- **Only what you may share.** No console makers' logos, trademarks or box
  art; pictures and fonts only under a licence that allows it, named in the
  theme's description or in a comment heading `theme.css` (romforge
  refuses any other file in a theme, so a `LICENSES.md` can't go there).
- **Data, not code.** No scripts: romforge refuses `@import`, links out of
  the theme's folder, URLs to other sites, and CSS escapes.
- **At most 256 KB of CSS and 8 MB in all.**
- **A preview without logos.** romforge draws platform logos from Wikidata;
  take the screenshot on a library with platforms that have none (ScummVM
  shows as plain "SVM"), or crop them out.
