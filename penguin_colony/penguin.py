"""Penguin SVG generation — one penguin per repo."""

from datetime import datetime, timezone
from typing import List, Tuple

# --- Star tiers ---

TIER_NAMES: List[str] = ["Little Blue", "Adélie", "King", "Emperor"]
TIER_SCALES: List[float] = [0.7, 0.9, 1.1, 1.4]


def star_tier(stars: int) -> int:
    """Map star count to penguin size tier (0–3)."""
    if stars >= 1000:
        return 3  # Emperor
    if stars >= 100:
        return 2  # King
    if stars >= 10:
        return 1  # Adélie
    return 0  # Little Blue


# --- Activity / pose ---

POSE_LABELS: List[str] = [
    "Swimming 🏊",
    "Walking 🚶",
    "Standing 🧍",
    "Sleeping 💤",
]


def activity_days(updated_at: str) -> int:
    """Days since a repo was last pushed/updated."""
    try:
        dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return 999


def activity_pose(days: int) -> int:
    """Map days-since-push to a pose index (0–3)."""
    if days <= 7:
        return 0  # swimming
    if days <= 30:
        return 1  # walking
    if days <= 180:
        return 2  # standing
    return 3  # sleeping


# --- SVG rendering for a single penguin ---


def penguin_svg(
    x: float,
    y: float,
    scale: float,
    scarf_color: str,
    pose: int,
    name: str,
    stars: int,
    fork: bool,
    label_fill: str = "#e6edf3",
    star_fill: str = "#f0883e",
    scarf_filter: str = "scarf_glow",
) -> str:
    """Generate SVG markup for one penguin.

    Args:
        x, y: Center position in the SVG coordinate space.
        scale: Size multiplier (from star tier).
        scarf_color: Hex color for the scarf (from language).
        pose: 0=swimming, 1=walking, 2=standing, 3=sleeping.
        name: Repository name (displayed as label).
        stars: Star count (displayed below name).
        fork: Whether the repo is a fork (renders translucent).
        label_fill: Text color for the repo name.
        star_fill: Text color for the star count.
        scarf_filter: SVG filter id for scarf glow.
    """
    s = scale
    opacity = 0.5 if fork else 1.0

    # Pose adjustments
    tilt = {0: -20, 1: -8, 2: 0, 3: 8}[pose]
    eye_state = "closed" if pose == 3 else "open"

    # Zzz for sleeping penguins
    zzz = ""
    if pose == 3:
        zzz = (
            f'<text x="{x + 22*s}" y="{y - 48*s}" font-size="{11*s}" '
            f'fill="#8b949e" font-weight="bold" opacity="0.8">z</text>\n'
            f'    <text x="{x + 32*s}" y="{y - 58*s}" font-size="{14*s}" '
            f'fill="#8b949e" font-weight="bold" opacity="0.55">z</text>\n'
            f'    <text x="{x + 40*s}" y="{y - 66*s}" font-size="{17*s}" '
            f'fill="#8b949e" font-weight="bold" opacity="0.3">z</text>'
        )

    # Swimming wave
    wave = ""
    if pose == 0:
        wave = (
            f'<ellipse cx="{x}" cy="{y + 30*s}" rx="{24*s}" ry="{6*s}" '
            f'fill="#58a6ff" opacity="0.3"/>\n'
            f'    <ellipse cx="{x - 8*s}" cy="{y + 32*s}" rx="{18*s}" ry="{4*s}" '
            f'fill="#79c0ff" opacity="0.2"/>'
        )

    # Flipper angles & feet per pose
    if pose == 0:  # Swimming
        flipper_l, flipper_r = -45, 45
        feet_html = ""
    elif pose == 1:  # Walking
        flipper_l, flipper_r = -20, 15
        feet_html = (
            f'<ellipse cx="{-10*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>\n'
            f'    <ellipse cx="{6*s}" cy="{28*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>'
        )
    elif pose == 3:  # Sleeping
        flipper_l, flipper_r = 5, -5
        feet_html = (
            f'<ellipse cx="{-8*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>\n'
            f'    <ellipse cx="{8*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>'
        )
    else:  # Standing
        flipper_l, flipper_r = 12, -12
        feet_html = (
            f'<ellipse cx="{-8*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>\n'
            f'    <ellipse cx="{8*s}" cy="{26*s}" rx="{6*s}" ry="{3*s}" fill="#f9826c"/>'
        )

    # Idle animation per pose
    idle_anim = ""
    if pose == 2:
        idle_anim = (
            '<animateTransform attributeName="transform" type="translate" '
            'values="0,0;0,-2;0,0" dur="3s" repeatCount="indefinite" additive="sum"/>'
        )
    elif pose == 1:
        idle_anim = (
            '<animateTransform attributeName="transform" type="rotate" '
            'values="-2,0,0;2,0,0;-2,0,0" dur="1.5s" repeatCount="indefinite" additive="sum"/>'
        )
    elif pose == 0:
        idle_anim = (
            '<animateTransform attributeName="transform" type="translate" '
            'values="0,0;2,-3;0,0;-2,-3;0,0" dur="2s" repeatCount="indefinite" additive="sum"/>'
        )

    # Eyes
    if eye_state == "open":
        eyes = (
            f'<circle cx="{-5*s}" cy="{-30*s}" r="{3*s}" fill="white"/>'
            f'<circle cx="{5*s}" cy="{-30*s}" r="{3*s}" fill="white"/>'
            f'<circle cx="{-4*s}" cy="{-29.5*s}" r="{1.5*s}" fill="#1b1f23"/>'
            f'<circle cx="{6*s}" cy="{-29.5*s}" r="{1.5*s}" fill="#1b1f23"/>'
            f'<circle cx="{-3.5*s}" cy="{-30*s}" r="{0.6*s}" fill="white"/>'
            f'<circle cx="{6.5*s}" cy="{-30*s}" r="{0.6*s}" fill="white"/>'
        )
    else:
        eyes = (
            f'<path d="M{-8*s},{-29*s} Q{-5*s},{-27*s} {-2*s},{-29*s}" '
            f'stroke="white" stroke-width="{1.8*s}" fill="none" stroke-linecap="round"/>'
            f'<path d="M{2*s},{-29*s} Q{5*s},{-27*s} {8*s},{-29*s}" '
            f'stroke="white" stroke-width="{1.8*s}" fill="none" stroke-linecap="round"/>'
        )

    star_label = f"⭐ {stars}" if stars > 0 else "🥚"

    return f'''<g transform="translate({x},{y}) rotate({tilt})" opacity="{opacity}">
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
    {eyes}
    <!-- Beak -->
    <polygon points="{-3.5*s},{-24*s} {3.5*s},{-24*s} 0,{-19*s}" fill="#f9826c"/>
    <polygon points="{-2*s},{-23.5*s} {2*s},{-23.5*s} 0,{-20.5*s}" fill="#ffb499" opacity="0.4"/>
    <!-- Scarf -->
    <rect x="{-15*s}" y="{-17*s}" width="{30*s}" height="{6*s}" rx="{3*s}" fill="{scarf_color}" filter="url(#{scarf_filter})"/>
    <rect x="{9*s}" y="{-17*s}" width="{5*s}" height="{14*s}" rx="{2.5*s}" fill="{scarf_color}" filter="url(#{scarf_filter})"/>
    <rect x="{-15*s}" y="{-17*s}" width="{30*s}" height="{2.5*s}" rx="{1.5*s}" fill="white" opacity="0.2"/>
    <!-- Feet -->
    {feet_html}
    <!-- Flippers -->
    <ellipse cx="{-20*s}" cy="{-2*s}" rx="{5*s}" ry="{14*s}" fill="#1b1f23" transform="rotate({flipper_l})"/>
    <ellipse cx="{20*s}" cy="{-2*s}" rx="{5*s}" ry="{14*s}" fill="#1b1f23" transform="rotate({flipper_r})"/>
  </g>
  <!-- Label -->
  <text x="{x}" y="{y + 42*s}" text-anchor="middle" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,monospace" font-size="{10*s}" fill="{label_fill}" font-weight="600">{name}</text>
  <text x="{x}" y="{y + 54*s}" text-anchor="middle" font-family="monospace" font-size="{9*s}" fill="{star_fill}">{star_label}</text>
  {zzz}
  {wave}'''
