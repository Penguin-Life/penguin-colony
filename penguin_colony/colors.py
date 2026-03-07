"""Language → scarf color mapping (GitHub linguist palette)."""

# Sourced from https://github.com/github-linguist/linguist/blob/master/lib/linguist/languages.yml
LANG_COLORS = {
    "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6",
    "Python": "#3572A5",
    "Rust": "#dea584",
    "Go": "#00ADD8",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "C#": "#178600",
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
    "Scala": "#c22d40",
    "Haskell": "#5e5086",
    "Elixir": "#6e4a7e",
    "Clojure": "#db5855",
    "R": "#198CE7",
    "MATLAB": "#e16737",
    "Perl": "#0298c3",
    "Objective-C": "#438eff",
    "Assembly": "#6E4C13",
    "Vim Script": "#199f4b",
    "Makefile": "#427819",
    "Dockerfile": "#384d54",
    "Nix": "#7e7eff",
    "Terraform": "#5c4ee5",
    "HCL": "#844FBA",
    "PowerShell": "#012456",
    "Groovy": "#4298b8",
    "Julia": "#a270ba",
    "Crystal": "#000100",
    "Nim": "#ffc200",
    "OCaml": "#3be133",
    "F#": "#b845fc",
    "Erlang": "#B83998",
    "Fortran": "#4d41b1",
    "COBOL": "#005ca5",
    "Jupyter Notebook": "#DA5B0B",
    "SCSS": "#c6538c",
    "Less": "#1d365d",
    "Svelte": "#ff3e00",
    "Astro": "#ff5a03",
    "Lex": "#DBCA00",
    "V": "#4f87c4",
    "Odin": "#60AFFE",
    "Mojo": "#ff4c1a",
}

DEFAULT_COLOR = "#6e7681"


def get_color(language: str) -> str:
    """Get scarf color for a language, falling back to default grey."""
    if not language:
        return DEFAULT_COLOR
    return LANG_COLORS.get(language, DEFAULT_COLOR)
