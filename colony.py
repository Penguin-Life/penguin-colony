#!/usr/bin/env python3
"""
penguin-colony: Visualize GitHub repos as a penguin colony SVG.

Backwards-compatible entry point. Delegates to the penguin_colony package.
For new usage, prefer:
    python -m penguin_colony <username>
    # or after pip install:
    penguin-colony <username>
"""

from penguin_colony.cli import main

if __name__ == "__main__":
    main()
