"""Command-line interface for penguin-colony."""

import argparse
import json
import os
import sys
from typing import List, Optional

from . import __version__
from .github import fetch_repos
from .layout import generate_colony
from .penguin import POSE_LABELS, TIER_NAMES, activity_days, activity_pose, star_tier
from .themes import AVAILABLE_THEMES


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="penguin-colony",
        description="Generate a penguin colony SVG from GitHub repos",
    )
    parser.add_argument("username", help="GitHub username or org")
    parser.add_argument(
        "-o", "--output", default=None, help="Output file (default: stdout)"
    )
    parser.add_argument(
        "-n",
        "--max-repos",
        type=int,
        default=50,
        help="Max repos to show (default: 50)",
    )
    parser.add_argument(
        "--forks", action="store_true", help="Include forked repos"
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN"),
        help="GitHub token (default: $GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--theme",
        choices=AVAILABLE_THEMES,
        default="dark",
        help="Visual theme (default: dark)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output repo data as JSON instead of SVG",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """Entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    repos = fetch_repos(args.username, args.token)

    if args.json:
        summary = []
        for r in repos:
            if not args.forks and r.get("fork"):
                continue
            days = activity_days(
                r.get("pushed_at") or r.get("updated_at", "")
            )
            summary.append(
                {
                    "name": r["name"],
                    "stars": r.get("stargazers_count", 0),
                    "language": r.get("language"),
                    "tier": TIER_NAMES[star_tier(r.get("stargazers_count", 0))],
                    "pose": POSE_LABELS[activity_pose(days)],
                    "fork": r.get("fork", False),
                    "days_since_push": days,
                }
            )
        print(json.dumps(summary[: args.max_repos], indent=2))
        return

    svg = generate_colony(
        repos,
        args.username,
        max_repos=args.max_repos,
        include_forks=args.forks,
        theme_name=args.theme,
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(svg)
        print(f"Colony saved to {args.output}", file=sys.stderr)
    else:
        print(svg)


if __name__ == "__main__":
    main()
