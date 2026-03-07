"""penguin-colony — Visualize GitHub repos as a penguin colony SVG."""

__version__ = "1.1.0"

from .layout import generate_colony  # noqa: F401
from .github import fetch_repos  # noqa: F401
