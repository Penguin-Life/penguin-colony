#!/usr/bin/env python3
"""
penguin-colony: Visualize GitHub repos as a penguin colony SVG.
Each repo becomes a penguin. Stars → size, activity → pose, language → scarf color.
"""

import argparse
import json
import math
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# Language → scarf color mapping
LANG_COLORS = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Python": "#3572A5",
    "Rust": "#dea584",
    "Go": "#00ADD8",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "Ruby": "#701516",
    "PHP": "#4F5D95",
    "Swift": "#F05138",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Vue": "#41b883",
    "Solidity": "#AA6746",
    "Lua": "#000080",
    "Zig": "#ec915c",
}
DEFAULT_COLOR = "#6e7681"

# Penguin size tiers based on stars
def star_tier(stars):
    if stars >= 1000: return 3  # emperor
    if stars >= 100: return 2   # king
    if stars >= 10: return 1    # adelie
    return 0                     # little blue

TIER_NAMES = ["Little Blue", "Adélie", "King", "Emperor"]
TIER_SCALES = [0.7, 0.9, 1.1, 1.4]

def activity_days(updated_at):
    """Days since last update."""
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except:
        return 999

def activity_pose(days):
    """0=swimming(very active), 1=walking, 2=standing, 3=sleeping"""
    if days <= 7: return 0
    if days <= 30: return 1
    if days <= 180: return 2
    return 3

POSE_LABELS = ["Swimming 🏊", "Walking 🚶", "Standing 🧍", "Sleeping 💤"]

def fetch_repos(username, token=None):
    """Fetch all public repos for a user/org."""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&sort=stars&direction=desc"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "penguin-colony")
        if token:
            req.add_header("Authorization", f"token {token}")
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                if not data:
                    break
                repos.extend(data)
                if len(data) < 100:
                    break
                page += 1
        except urllib.error.HTTPError as e:
            print(f"Error fetching repos: {e.code} {e.reason}", file=sys.stderr)
            sys.exit(1)
    return repos

def penguin_svg(x, y, scale, scarf_color, pose, name, stars, fork):
    """Generate SVG for a single penguin."""
    s = scale
    opacity = 0.5 if fork else 1.0

    # Pose adjustments
    tilt = {0: -20, 1: -8, 2: 0, 3: 8}[pose]
    eye_state = "closed" if pose == 3 else "open"

    # Z indicators (positioned relative to penguin group)
    zzz = ""
    if pose == 3:
        zzz = f'''<text x="{x + 22*s}" y="{y - 48*s}" font-size="{11*s}" fill="#8b949e" font-weight="bold" opacity="0.8">z</text>
    <text x="{x + 32*s}" y="{y - 58*s}" font-size="{14*s}" fill="#8b949e" font-weight="bold" opacity="0.55">z</text>
    <text x="{x + 40*s}" y="{y - 66*s}" font-size="{17*s}" fill="#8b949e" font-weight="bold" opacity="0.3">z</text>'''

    # Swimming wave
    wave = ""
    if pose == 0:
        wave = f'''<ellipse cx="{x}" cy="{y + 30*s}" rx="{24*s}" ry="{6*s}" fill="#58a6ff" opacity="0.3"/>
    <ellipse cx="{x - 8*s}" cy="{y + 32*s}" rx="{18*s}" ry="{4*s}" fill="#79c0ff" opacity="0.2"/>'''

    # Pose-specific flipper angles and feet offsets
    if pose == 0:  # Swimming - flippers out wide, no feet visible
        flipper_l, flipper_r = -45, 45
        feet_html = ""
    elif pose == 1:  # Walking - one flipper forward, feet offset
        flipper_l, flipper_r = -20, 15
        feet_html = f'''<ellipse cx="{-10*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>
    <ellipse cx="{6*s}" cy="{28*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>'''
    elif pose == 3:  # Sleeping - flippers tucked
        flipper_l, flipper_r = 5, -5
        feet_html = f'''<ellipse cx="{-8*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>
    <ellipse cx="{8*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>'''
    else:  # Standing - neutral
        flipper_l, flipper_r = 12, -12
        feet_html = f'''<ellipse cx="{-8*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>
    <ellipse cx="{8*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>'''

    # Idle animation for standing/walking
    idle_anim = ""
    if pose == 2:  # standing - gentle bob
        idle_anim = f'<animateTransform attributeName="transform" type="translate" values="0,0;0,-2;0,0" dur="3s" repeatCount="indefinite" additive="sum"/>'
    elif pose == 1:  # walking - sway
        idle_anim = f'<animateTransform attributeName="transform" type="rotate" values="-2,0,0;2,0,0;-2,0,0" dur="1.5s" repeatCount="indefinite" additive="sum"/>'
    elif pose == 0:  # swimming - bounce
        idle_anim = f'<animateTransform attributeName="transform" type="translate" values="0,0;2,-3;0,0;-2,-3;0,0" dur="2s" repeatCount="indefinite" additive="sum"/>'

    penguin = f'''<g transform="translate({x},{y}) rotate({tilt})" opacity="{opacity}">
    {idle_anim}
    <!-- Shadow -->
    <ellipse cx="0" cy="{27*s}" rx="{16*s}" ry="{4*s}" fill="black" opacity="0.3"/>
    <!-- Body -->
    <ellipse cx="0" cy="0" rx="{18*s}" ry="{25*s}" fill="#1b1f23"/>
    <ellipse cx="{-6*s}" cy="{-5*s}" rx="{4*s}" ry="{12*s}" fill="#2a2f35" opacity="0.4"/>
    <!-- Belly -->
    <ellipse cx="0" cy="{3*s}" rx="{12*s}" ry="{18*s}" fill="white"/>
    <ellipse cx="{-2*s}" cy="{0*s}" rx="{8*s}" ry="{12*s}" fill="#f0f6fc" opacity="0.3"/>
    <!-- Head -->
    <circle cx="0" cy="{-28*s}" r="{13*s}" fill="#1b1f23"/>
    <circle cx="{-4*s}" cy="{-32*s}" r="{5*s}" fill="#2a2f35" opacity="0.3"/>
    <!-- Cheeks -->
    <circle cx="{-9*s}" cy="{-25*s}" r="{3.5*s}" fill="#ff9fb3" opacity="0.35"/>
    <circle cx="{9*s}" cy="{-25*s}" r="{3.5*s}" fill="#ff9fb3" opacity="0.35"/>
    <!-- Eyes -->
    {f'<circle cx="{-5*s}" cy="{-30*s}" r="{3*s}" fill="white"/><circle cx="{5*s}" cy="{-30*s}" r="{3*s}" fill="white"/><circle cx="{-4*s}" cy="{-29.5*s}" r="{1.5*s}" fill="#1b1f23"/><circle cx="{6*s}" cy="{-29.5*s}" r="{1.5*s}" fill="#1b1f23"/><circle cx="{-3.5*s}" cy="{-30*s}" r="{0.6*s}" fill="white"/><circle cx="{6.5*s}" cy="{-30*s}" r="{0.6*s}" fill="white"/>' if eye_state == "open" else f'<path d="M{-8*s},{-29*s} Q{-5*s},{-27*s} {-2*s},{-29*s}" stroke="white" stroke-width="{1.8*s}" fill="none" stroke-linecap="round"/><path d="M{2*s},{-29*s} Q{5*s},{-27*s} {8*s},{-29*s}" stroke="white" stroke-width="{1.8*s}" fill="none" stroke-linecap="round"/>'}
    <!-- Beak -->
    <polygon points="{-3.5*s},{-24*s} {3.5*s},{-24*s} 0,{-19*s}" fill="#f9826c"/>
    <polygon points="{-2*s},{-23.5*s} {2*s},{-23.5*s} 0,{-20.5*s}" fill="#ffb499" opacity="0.4"/>
    <!-- Scarf (with glow) -->
    <rect x="{-15*s}" y="{-17*s}" width="{30*s}" height="{6*s}" rx="{3*s}" fill="{scarf_color}" filter="url(#scarf_glow)"/>
    <rect x="{9*s}" y="{-17*s}" width="{5*s}" height="{14*s}" rx="{2.5*s}" fill="{scarf_color}" filter="url(#scarf_glow)"/>
    <rect x="{-15*s}" y="{-17*s}" width="{30*s}" height="{2.5*s}" rx="{1.5*s}" fill="white" opacity="0.2"/>
    <!-- Feet -->
    {feet_html}
    <!-- Flippers -->
    <ellipse cx="{-20*s}" cy="{-2*s}" rx="{5*s}" ry="{14*s}" fill="#1b1f23" transform="rotate({flipper_l})"/>
    <ellipse cx="{20*s}" cy="{-2*s}" rx="{5*s}" ry="{14*s}" fill="#1b1f23" transform="rotate({flipper_r})"/>
  </g>
  <!-- Label -->
  <text x="{x}" y="{y + 42*s}" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,monospace" font-size="{10*s}" fill="#e6edf3" font-weight="600">{name}</text>
  <text x="{x}" y="{y + 54*s}" text-anchor="middle" font-family="monospace" font-size="{9*s}" fill="#f0883e">{'⭐ ' + str(stars) if stars > 0 else '🥚'}</text>
  {zzz}
  {wave}'''
    return penguin

def generate_colony(repos, username, max_repos=50, include_forks=False):
    """Generate full colony SVG."""
    # Filter
    filtered = [r for r in repos if include_forks or not r.get("fork", False)]
    filtered = filtered[:max_repos]

    if not filtered:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="100"><text x="200" y="50" text-anchor="middle" fill="#c9d1d9" font-family="monospace">No repos found 🐧</text></svg>'

    # Layout: grid with some randomness for organic feel
    cols = min(8, max(3, int(math.sqrt(len(filtered)) * 1.3)))
    cell_w = 130
    cell_h = 140
    padding = 60

    rows = math.ceil(len(filtered) / cols)
    width = cols * cell_w + padding * 2
    height = rows * cell_h + padding * 2 + 80  # extra for title

    # Background with aurora, snow, and ice
    import random
    rng = random.Random(42)  # deterministic

    # Generate snowflakes
    snowflakes = ""
    for i in range(40):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height - 60)
        sr = round(0.5 + rng.random() * 2, 1)
        so = round(0.2 + rng.random() * 0.5, 2)
        dur = round(3 + rng.random() * 5, 1)
        snowflakes += f'''<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" opacity="{so}">
      <animate attributeName="cy" from="{sy}" to="{sy+60}" dur="{dur}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="{so};{so*0.3};{so}" dur="{dur}s" repeatCount="indefinite"/>
    </circle>\n    '''

    # Generate twinkling stars
    stars_bg = ""
    for i in range(30):
        sx = rng.randint(0, width)
        sy = rng.randint(5, 70)
        sr = round(0.4 + rng.random() * 1.2, 1)
        so = round(0.3 + rng.random() * 0.6, 2)
        dur = round(1.5 + rng.random() * 3, 1)
        stars_bg += f'''<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" opacity="{so}">
      <animate attributeName="opacity" values="{so};{so*0.2};{so}" dur="{dur}s" repeatCount="indefinite"/>
    </circle>\n    '''

    # Ice terrain points
    ice_y = height - 50
    ice_points = [f"0,{height}"]
    for ix in range(0, width + 20, 20):
        iy = ice_y + rng.randint(-8, 8)
        ice_points.append(f"{ix},{iy}")
    ice_points.append(f"{width},{height}")
    ice_path = " ".join(ice_points)

    svg_parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#020817"/>
      <stop offset="40%" stop-color="#0a1628"/>
      <stop offset="100%" stop-color="#111d2e"/>
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
      <stop offset="0%" stop-color="#1a2744"/>
      <stop offset="50%" stop-color="#0f1b2d"/>
      <stop offset="100%" stop-color="#080e1a"/>
    </linearGradient>
    <linearGradient id="ice_top" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#1a2744" stop-opacity="0"/>
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

  <!-- Aurora Borealis -->
  <ellipse cx="{width*0.3}" cy="40" rx="{width*0.5}" ry="60" fill="url(#aurora1)" filter="url(#aurora_blur)">
    <animate attributeName="rx" values="{width*0.5};{width*0.55};{width*0.45};{width*0.5}" dur="8s" repeatCount="indefinite"/>
    <animate attributeName="cy" values="40;50;35;40" dur="6s" repeatCount="indefinite"/>
  </ellipse>
  <ellipse cx="{width*0.7}" cy="55" rx="{width*0.4}" ry="45" fill="url(#aurora2)" filter="url(#aurora_blur)">
    <animate attributeName="rx" values="{width*0.4};{width*0.35};{width*0.45};{width*0.4}" dur="10s" repeatCount="indefinite"/>
    <animate attributeName="cy" values="55;45;60;55" dur="7s" repeatCount="indefinite"/>
  </ellipse>

  <!-- Stars -->
  {stars_bg}

  <!-- Snow -->
  {snowflakes}

  <!-- Ice terrain -->
  <polygon points="{ice_path}" fill="url(#ice_grad)"/>
  <polygon points="{ice_path}" fill="url(#ice_top)"/>

  <!-- Title -->
  <text x="{width//2}" y="35" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,sans-serif" font-size="18" fill="white" font-weight="bold" filter="url(#glow)">🐧 {username}&#x27;s Penguin Colony</text>
  <text x="{width//2}" y="56" text-anchor="middle" font-family="monospace" font-size="11" fill="#8b949e">{len(filtered)} repos · {sum(r.get("stargazers_count",0) for r in filtered):,} total stars</text>
''']

    # Place penguins
    for i, repo in enumerate(filtered):
        col = i % cols
        row = i // cols
        x = padding + col * cell_w + cell_w // 2
        y = 80 + padding + row * cell_h

        stars = repo.get("stargazers_count", 0)
        lang = repo.get("language") or ""
        color = LANG_COLORS.get(lang, DEFAULT_COLOR)
        tier = star_tier(stars)
        scale = TIER_SCALES[tier]
        days = activity_days(repo.get("pushed_at") or repo.get("updated_at", ""))
        pose = activity_pose(days)
        raw_name = repo.get("name", "")
        name = raw_name if len(raw_name) <= 18 else raw_name[:16] + ".."
        fork = repo.get("fork", False)

        svg_parts.append(penguin_svg(x, y, scale, color, pose, name, stars, fork))

    # Legend - styled bar
    legend_y = height - 35
    lx = padding
    svg_parts.append(f'''
  <!-- Legend -->
  <rect x="{lx - 10}" y="{legend_y - 12}" width="{width - padding*2 + 20}" height="22" rx="11" fill="#161b22" opacity="0.8" stroke="#30363d" stroke-width="0.5"/>
  <text x="{width//2}" y="{legend_y + 3}" text-anchor="middle" font-family="monospace" font-size="9" fill="#8b949e">
    📏 size = stars  ·  🧣 scarf = language  ·  🏊 pose = activity  ·  👻 opacity = fork
  </text>''')

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)

def main():
    parser = argparse.ArgumentParser(description="Generate a penguin colony SVG from GitHub repos")
    parser.add_argument("username", help="GitHub username or org")
    parser.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    parser.add_argument("-n", "--max-repos", type=int, default=50, help="Max repos to show")
    parser.add_argument("--forks", action="store_true", help="Include forked repos")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token")
    parser.add_argument("--json", action="store_true", help="Output repo data as JSON instead")
    args = parser.parse_args()

    repos = fetch_repos(args.username, args.token)

    if args.json:
        summary = []
        for r in repos:
            if not args.forks and r.get("fork"):
                continue
            days = activity_days(r.get("pushed_at") or r.get("updated_at", ""))
            summary.append({
                "name": r["name"],
                "stars": r.get("stargazers_count", 0),
                "language": r.get("language"),
                "tier": TIER_NAMES[star_tier(r.get("stargazers_count", 0))],
                "pose": POSE_LABELS[activity_pose(days)],
                "fork": r.get("fork", False),
                "days_since_push": days,
            })
        print(json.dumps(summary[:args.max_repos], indent=2))
        return

    svg = generate_colony(repos, args.username, args.max_repos, args.forks)

    if args.output:
        with open(args.output, "w") as f:
            f.write(svg)
        print(f"Colony saved to {args.output}", file=sys.stderr)
    else:
        print(svg)

if __name__ == "__main__":
    main()
