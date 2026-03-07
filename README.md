# 🐧 penguin-colony

> **Visualize your GitHub repos as an adorable penguin colony.**
> Stars → size. Language → scarf. Activity → pose. Fork → ghost.

<div align="center">

![Penguin Colony Demo](https://raw.githubusercontent.com/Penguin-Life/penguin-colony/main/examples/penguin-life.svg)

[![CI](https://github.com/Penguin-Life/penguin-colony/actions/workflows/ci.yml/badge.svg)](https://github.com/Penguin-Life/penguin-colony/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://python.org)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#)
[![GitHub Stars](https://img.shields.io/github/stars/Penguin-Life/penguin-colony?style=social)](https://github.com/Penguin-Life/penguin-colony)

</div>

---

## ✨ What is this?

`penguin-colony` turns your GitHub profile into a living, breathing colony of penguins — each one representing a repository. Embed it in your profile README for an instant conversation-starter.

Every penguin encodes real data:

| Visual | Meaning | Details |
|--------|---------|---------|
| 📏 **Size** | Stars | Little Blue → Adélie → King → Emperor |
| 🧣 **Scarf color** | Primary language | 55+ languages mapped to GitHub colors |
| 🏊 **Pose** | Recent activity | Swimming → Walking → Standing → Sleeping |
| 👻 **Opacity** | Fork status | Forks appear translucent |

The background is a procedurally-generated Antarctic scene — aurora borealis, falling snow, twinkling stars, and an ice shelf — all animated in pure SVG, no images, no JS.

---

## 🚀 Quick Start

### Install via pip

```bash
pip install penguin-colony
penguin-colony <github-username> -o colony.svg
```

### Or run directly (zero install)

```bash
# No install needed — pure Python stdlib, no dependencies
python3 colony.py <github-username> -o colony.svg
```

### Examples

```bash
# Your own profile
penguin-colony torvalds -o colony.svg

# Light theme (for light-mode GitHub profiles)
penguin-colony vercel --theme light -o colony.svg

# Limit to top 20 repos
penguin-colony facebook -n 20 -o colony.svg

# Include forked repos (shown as translucent ghosts)
penguin-colony octocat --forks -o colony.svg

# Use a GitHub token (avoids rate limits)
GITHUB_TOKEN=ghp_xxx penguin-colony your-username -o colony.svg

# Output raw JSON (repo data with tier/pose info)
penguin-colony your-username --json
```

---

## 📌 Add to Your GitHub Profile README

### Option 1: GitHub Action (recommended — auto-updates daily)

Add this to your profile repo (`<username>/<username>`):

```yaml
# .github/workflows/colony.yml
name: Update Penguin Colony

on:
  schedule:
    - cron: '0 6 * * *'   # daily at 06:00 UTC
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  colony:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate colony
        uses: Penguin-Life/penguin-colony@v1
        with:
          # username: defaults to repo owner
          # theme: dark
          # max-repos: 50

      - name: Commit SVG
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add colony.svg
          git diff --cached --quiet || git commit -m "🐧 Update penguin colony"
          git push
```

Then in your README:

```markdown
![My Penguin Colony](colony.svg)
```

### Option 2: Manual

```bash
python3 colony.py <your-username> -o colony.svg
# commit and push colony.svg to your profile repo
```

---

## 🎨 Themes

| Theme | Preview | Best for |
|-------|---------|----------|
| `dark` (default) | Antarctic night — aurora, stars, snow | Dark-mode GitHub |
| `light` | Daytime Antarctic — blue sky, soft ice | Light-mode GitHub |

```bash
penguin-colony your-username --theme light -o colony.svg
```

---

## 📸 Gallery

| User | Command |
|------|---------|
| **Penguin-Life** | `penguin-colony Penguin-Life` |
| **vercel** (top 20) | `penguin-colony vercel -n 20` |

![Penguin-Life](https://raw.githubusercontent.com/Penguin-Life/penguin-colony/main/examples/penguin-life.svg)

Try it with any user or org — the more repos, the bigger the colony!

```bash
# Try these:
penguin-colony torvalds -o torvalds.svg
penguin-colony facebook -n 30 -o facebook.svg
penguin-colony sindresorhus -o sindresorhus.svg
```

---

## 🐧 Visual Encoding

### Penguin Sizes (Stars)

| Tier | Stars | Scale |
|------|-------|-------|
| 🔵 Little Blue | < 10 | 0.7× |
| 🐧 Adélie | 10–99 | 0.9× |
| 👑 King | 100–999 | 1.1× |
| 🏔️ Emperor | 1000+ | 1.4× |

### Scarf Colors (Language)

The scarf glows in your repo's primary language color — same palette as GitHub's linguist dots. 55+ languages are mapped.

`JavaScript` 🟡 · `TypeScript` 🔵 · `Python` 🔷 · `Rust` 🟠 · `Go` 💠 · `Ruby` 🔴 · `Swift` 🟥 · `Svelte` 🔴 · `Astro` 🟠 · and 46 more...

### Poses (Activity)

| Pose | Days Since Push | Vibe |
|------|----------------|------|
| 🏊 Swimming | ≤ 7 days | Actively maintained |
| 🚶 Walking | 8–30 days | Recent activity |
| 🧍 Standing | 31–180 days | Stable / dormant |
| 💤 Sleeping | 180+ days | Archived / forgotten |

Sleeping penguins get `z z z` floating above their heads. 🥹

---

## ⚙️ CLI Reference

```
usage: penguin-colony [-h] [-o OUTPUT] [-n MAX_REPOS] [--forks]
                      [--token TOKEN] [--theme {dark,light}] [--json]
                      [--version]
                      username

positional arguments:
  username              GitHub username or org

options:
  -o, --output FILE     Output SVG file (default: stdout)
  -n, --max-repos N     Max repos to display (default: 50)
  --forks               Include forked repos (shown as ghosts)
  --token TOKEN         GitHub API token (or set GITHUB_TOKEN env var)
  --theme {dark,light}  Visual theme (default: dark)
  --json                Output repo data as JSON instead of SVG
  --version             Show version number
```

---

## 🏗️ Project Structure

```
penguin-colony/
├── colony.py              # Backwards-compatible entry point
├── pyproject.toml          # Package config (pip installable)
├── action.yml              # Reusable GitHub Action
├── penguin_colony/
│   ├── __init__.py         # Version + public API
│   ├── __main__.py         # python -m penguin_colony
│   ├── cli.py              # Argument parsing + CLI
│   ├── github.py           # GitHub API client
│   ├── penguin.py          # Penguin SVG rendering
│   ├── layout.py           # Colony scene composition
│   ├── themes.py           # Theme definitions
│   └── colors.py           # 55+ language → color mapping
├── examples/               # Pre-generated SVGs
└── .github/workflows/
    ├── ci.yml              # Test matrix (Python 3.8/3.10/3.12)
    └── colony.yml          # Auto-update colony SVG daily
```

---

## 🤝 Contributing

PRs welcome! Some ideas:

- 🎨 New themes (ocean? sunset? space?)
- 🌍 More language → color mappings
- 🏔️ Different terrain modes
- 📊 Org-level views (group repos by team/topic)
- 🎭 More penguin poses or accessories

---

## 📄 License

[MIT](LICENSE) — © 2026 Penguin-Life

---

<div align="center">

Made with ❄️ and 🐧 by [Penguin-Life](https://github.com/Penguin-Life)

*If this made you smile, give it a ⭐ — it helps little penguins find their forever homes.*

</div>
