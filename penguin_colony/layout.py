"""Colony layout — positions penguins and renders the full SVG scene."""

import math
import random
from typing import Any, Dict, List

from .colors import get_color
from .penguin import (
    TIER_SCALES,
    activity_days,
    activity_pose,
    penguin_svg,
    star_tier,
)
from .themes import get_theme


def generate_colony(
    repos: List[Dict],
    username: str,
    max_repos: int = 50,
    include_forks: bool = False,
    theme_name: str = "dark",
) -> str:
    """Generate the full colony SVG from a list of GitHub repos.

    Args:
        repos: Raw repo dicts from the GitHub API.
        username: Display name for the colony title.
        max_repos: Maximum number of penguins to render.
        include_forks: Whether to include forked repos.
        theme_name: Visual theme ('dark' or 'light').

    Returns:
        Complete SVG markup as a string.
    """
    theme = get_theme(theme_name)

    # Filter repos
    filtered = [r for r in repos if include_forks or not r.get("fork", False)]
    filtered = filtered[:max_repos]

    if not filtered:
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100">'
            '<text x="200" y="50" text-anchor="middle" fill="#c9d1d9" '
            'font-family="monospace">No repos found 🐧</text></svg>'
        )

    # Grid layout
    cols = min(8, max(3, int(math.sqrt(len(filtered)) * 1.3)))
    cell_w = 130
    cell_h = 140
    padding = 60

    rows = math.ceil(len(filtered) / cols)
    width = cols * cell_w + padding * 2
    height = rows * cell_h + padding * 2 + 80

    # Deterministic random for reproducible output
    rng = random.Random(42)

    # --- Background elements ---
    sky_top, sky_mid, sky_bot = theme["sky"]

    snowflakes = _render_snowflakes(rng, width, height, theme)
    stars_bg = _render_stars(rng, width, theme)
    aurora_svg = _render_aurora(width, theme) if theme.get("aurora") else ""
    ice_svg = _render_ice(rng, width, height, theme)

    total_stars = sum(r.get("stargazers_count", 0) for r in filtered)

    svg_parts: List[str] = [
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{sky_top}"/>
      <stop offset="40%" stop-color="{sky_mid}"/>
      <stop offset="100%" stop-color="{sky_bot}"/>
    </linearGradient>
    <linearGradient id="aurora1" x1="0" y1="0" x2="1" y2="0.3">
      <stop offset="0%" stop-color="#00ff87" stop-opacity="0"/>
      <stop offset="30%" stop-color="#00ff87" stop-opacity="0.12"/>
      <stop offset="50%" stop-color="#60efff" stop-opacity="0.18"/>
      <stop offset="70%" stop-color="#7c5cfc" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#ff6bcd" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="aurora2" x1="0.2" y1="0" x2="0.8" y2="0.5">
      <stop offset="0%" stop-color="#60efff" stop-opacity="0"/>
      <stop offset="40%" stop-color="#60efff" stop-opacity="0.08"/>
      <stop offset="60%" stop-color="#00ff87" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#60efff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="ice_grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{theme["ice"][0]}"/>
      <stop offset="50%" stop-color="{theme["ice"][1]}"/>
      <stop offset="100%" stop-color="{theme["ice"][2]}"/>
    </linearGradient>
    <linearGradient id="ice_top" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{theme["ice_top"][0]}" stop-opacity="{theme["ice_top"][1]}"/>
      <stop offset="100%" stop-color="{theme["ice"][0]}" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="aurora_blur">
      <feGaussianBlur stdDeviation="20"/>
    </filter>
    <filter id="scarf_glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Sky -->
  <rect width="{width}" height="{height}" fill="url(#sky)"/>

  {aurora_svg}
  {stars_bg}
  {snowflakes}
  {ice_svg}

  <!-- Title -->
  <text x="{width // 2}" y="35" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,sans-serif" font-size="18" fill="{theme["title_fill"]}" font-weight="bold" filter="url(#glow)">🐧 {username}&#x27;s Penguin Colony</text>
  <text x="{width // 2}" y="56" text-anchor="middle" font-family="monospace" font-size="11" fill="{theme["subtitle_fill"]}">{len(filtered)} repos · {total_stars:,} total stars</text>
'''
    ]

    # --- Place penguins ---
    for i, repo in enumerate(filtered):
        col = i % cols
        row = i // cols
        x = padding + col * cell_w + cell_w // 2
        y = 80 + padding + row * cell_h

        repo_stars = repo.get("stargazers_count", 0)
        lang = repo.get("language") or ""
        color = get_color(lang)
        tier = star_tier(repo_stars)
        scale = TIER_SCALES[tier]
        days = activity_days(repo.get("pushed_at") or repo.get("updated_at", ""))
        pose = activity_pose(days)
        raw_name = repo.get("name", "")
        name = raw_name if len(raw_name) <= 18 else raw_name[:16] + ".."
        fork = repo.get("fork", False)

        svg_parts.append(
            penguin_svg(
                x,
                y,
                scale,
                color,
                pose,
                name,
                repo_stars,
                fork,
                label_fill=theme["label_fill"],
                star_fill=theme["star_fill"],
                scarf_filter=theme.get("scarf_filter", "scarf_glow"),
            )
        )

    # --- Legend bar ---
    legend_y = height - 35
    lx = padding
    svg_parts.append(
        f'\n  <!-- Legend -->\n'
        f'  <rect x="{lx - 10}" y="{legend_y - 12}" width="{width - padding * 2 + 20}" '
        f'height="22" rx="11" fill="#161b22" opacity="0.8" stroke="#30363d" stroke-width="0.5"/>\n'
        f'  <text x="{width // 2}" y="{legend_y + 3}" text-anchor="middle" '
        f'font-family="monospace" font-size="9" fill="#8b949e">\n'
        f'    📏 size = stars  ·  🧣 scarf = language  ·  🏊 pose = activity  ·  👻 opacity = fork\n'
        f'  </text>'
    )

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


# --- Private helpers for background rendering ---


def _render_snowflakes(
    rng: random.Random, width: int, height: int, theme: Dict[str, Any]
) -> str:
    lo, hi = theme["snow_opacity_range"]
    parts = []
    for _ in range(40):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height - 60)
        sr = round(0.5 + rng.random() * 2, 1)
        so = round(lo + rng.random() * (hi - lo), 2)
        dur = round(3 + rng.random() * 5, 1)
        parts.append(
            f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" opacity="{so}">\n'
            f'      <animate attributeName="cy" from="{sy}" to="{sy + 60}" '
            f'dur="{dur}s" repeatCount="indefinite"/>\n'
            f'      <animate attributeName="opacity" values="{so};{so * 0.3};{so}" '
            f'dur="{dur}s" repeatCount="indefinite"/>\n'
            f"    </circle>"
        )
    return "  <!-- Snow -->\n    " + "\n    ".join(parts) if parts else ""


def _render_stars(rng: random.Random, width: int, theme: Dict[str, Any]) -> str:
    lo, hi = theme["star_bg_opacity_range"]
    y_max = theme["star_bg_y_max"]
    if y_max <= 0:
        return ""
    parts = []
    for _ in range(30):
        sx = rng.randint(0, width)
        sy = rng.randint(5, y_max)
        sr = round(0.4 + rng.random() * 1.2, 1)
        so = round(lo + rng.random() * (hi - lo), 2)
        dur = round(1.5 + rng.random() * 3, 1)
        parts.append(
            f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" opacity="{so}">\n'
            f'      <animate attributeName="opacity" values="{so};{so * 0.2};{so}" '
            f'dur="{dur}s" repeatCount="indefinite"/>\n'
            f"    </circle>"
        )
    return "  <!-- Stars -->\n    " + "\n    ".join(parts) if parts else ""


def _render_aurora(width: int, theme: Dict[str, Any]) -> str:
    w = width
    return (
        f'  <!-- Aurora Borealis -->\n'
        f'  <ellipse cx="{w * 0.3}" cy="40" rx="{w * 0.5}" ry="60" fill="url(#aurora1)" filter="url(#aurora_blur)">\n'
        f'    <animate attributeName="rx" values="{w * 0.5};{w * 0.55};{w * 0.45};{w * 0.5}" dur="8s" repeatCount="indefinite"/>\n'
        f'    <animate attributeName="cy" values="40;50;35;40" dur="6s" repeatCount="indefinite"/>\n'
        f'  </ellipse>\n'
        f'  <ellipse cx="{w * 0.7}" cy="55" rx="{w * 0.4}" ry="45" fill="url(#aurora2)" filter="url(#aurora_blur)">\n'
        f'    <animate attributeName="rx" values="{w * 0.4};{w * 0.35};{w * 0.45};{w * 0.4}" dur="10s" repeatCount="indefinite"/>\n'
        f'    <animate attributeName="cy" values="55;45;60;55" dur="7s" repeatCount="indefinite"/>\n'
        f'  </ellipse>'
    )


def _render_ice(
    rng: random.Random, width: int, height: int, theme: Dict[str, Any]
) -> str:
    ice_y = height - 50
    ice_points = [f"0,{height}"]
    for ix in range(0, width + 20, 20):
        iy = ice_y + rng.randint(-8, 8)
        ice_points.append(f"{ix},{iy}")
    ice_points.append(f"{width},{height}")
    ice_path = " ".join(ice_points)
    return (
        f'  <!-- Ice terrain -->\n'
        f'  <polygon points="{ice_path}" fill="url(#ice_grad)"/>\n'
        f'  <polygon points="{ice_path}" fill="url(#ice_top)"/>'
    )
