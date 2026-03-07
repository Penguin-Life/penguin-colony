"""Theme definitions for colony backgrounds."""

from typing import Dict, Any

# Each theme defines colors/settings for the Antarctic scene
THEMES: Dict[str, Dict[str, Any]] = {
    "dark": {
        "sky": ("#020817", "#0a1628", "#111d2e"),
        "aurora": True,
        "aurora1_colors": ("#00ff87", "#60efff", "#7c5cfc", "#ff6bcd"),
        "aurora1_opacity": (0.0, 0.12, 0.18, 0.1, 0.0),
        "aurora2_colors": ("#60efff", "#00ff87"),
        "aurora2_opacity": (0.0, 0.08, 0.15, 0.0),
        "ice": ("#1a2744", "#0f1b2d", "#080e1a"),
        "ice_top": ("#3b82f6", 0.2),
        "title_fill": "white",
        "subtitle_fill": "#8b949e",
        "label_fill": "#e6edf3",
        "star_fill": "#f0883e",
        "snow_opacity_range": (0.2, 0.5),
        "star_bg_opacity_range": (0.3, 0.6),
        "star_bg_y_max": 70,
        "scarf_filter": "scarf_glow",
    },
    "light": {
        "sky": ("#87CEEB", "#B0E0E6", "#E0F0FF"),
        "aurora": False,
        "ice": ("#e8f4f8", "#d1ecf1", "#c3e6f0"),
        "ice_top": ("#ffffff", 0.4),
        "title_fill": "#1a1a2e",
        "subtitle_fill": "#555555",
        "label_fill": "#2d2d2d",
        "star_fill": "#e67e22",
        "snow_opacity_range": (0.15, 0.35),
        "star_bg_opacity_range": (0.0, 0.0),  # no stars in daytime
        "star_bg_y_max": 0,
        "scarf_filter": "scarf_glow",
    },
}

AVAILABLE_THEMES = list(THEMES.keys())


def get_theme(name: str) -> Dict[str, Any]:
    """Get a theme by name. Raises ValueError for unknown themes."""
    if name not in THEMES:
        raise ValueError(
            f"Unknown theme '{name}'. Available: {', '.join(AVAILABLE_THEMES)}"
        )
    return THEMES[name]
