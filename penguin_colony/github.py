"""GitHub API integration for fetching repository data."""

import json
import sys
import urllib.request
import urllib.error
from typing import Dict, List, Optional


def fetch_repos(
    username: str, token: Optional[str] = None
) -> List[Dict]:
    """Fetch all public repos for a user/org via GitHub REST API.

    Args:
        username: GitHub username or organization name.
        token: Optional GitHub personal access token (avoids rate limits).

    Returns:
        List of repository dicts from the GitHub API.
    """
    repos: List[Dict] = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{username}/repos"
            f"?per_page=100&page={page}&sort=stars&direction=desc"
        )
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
