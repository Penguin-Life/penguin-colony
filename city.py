#!/usr/bin/env python3
"""
PenguinCity 🏰🐧 — RPG + City Builder for your projects.

Every project is a building. Every commit is a heartbeat. Your city grows
as you ship code, keep servers alive, and conquer quests.

Usage:
  city.py init [--name NAME]          Initialize your city
  city.py status                      Show city dashboard (ASCII)
  city.py render [-o FILE]            Generate full SVG city map
  city.py add <name> [--type TYPE] [--url URL] [--server SERVER] [--path PATH]
  city.py scan [--server SERVER]      Auto-discover projects from servers
  city.py github <username>           Import GitHub repos as buildings
  city.py quest                       Show active quests
  city.py quest complete <id>         Complete a quest
  city.py event                       Check for random events
  city.py log                         Show recent city history
  city.py demolish <name>             Remove a building
"""

import argparse
import json
import math
import os
import random
import sys
import hashlib
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────

CITY_FILE = os.environ.get("PENGUIN_CITY_FILE",
    os.path.expanduser("~/.openclaw/workspace/penguin-city/city.json"))

BUILDING_TYPES = {
    "website":  {"icon": "🏪", "category": "commerce",  "base_xp": 10, "evolve": ["Stall", "Shop", "Mall", "Trade Hub"]},
    "api":      {"icon": "🔨", "category": "industry",  "base_xp": 12, "evolve": ["Workshop", "Factory", "Refinery", "Tech Spire"]},
    "bot":      {"icon": "🗼", "category": "military",  "base_xp": 15, "evolve": ["Watchtower", "Barracks", "Fortress", "Intelligence HQ"]},
    "game":     {"icon": "🎮", "category": "entertainment", "base_xp": 8, "evolve": ["Arcade", "Arena", "Colosseum", "Wonder"]},
    "tool":     {"icon": "⚙️", "category": "utility",   "base_xp": 10, "evolve": ["Shed", "Depot", "Warehouse", "Portal"]},
    "blog":     {"icon": "📜", "category": "culture",   "base_xp": 6,  "evolve": ["Scroll Stand", "Library", "Archive", "Grand Library"]},
    "repo":     {"icon": "📦", "category": "district",  "base_xp": 5,  "evolve": ["Tent", "Cabin", "House", "Manor"]},
    "defi":     {"icon": "🏦", "category": "finance",   "base_xp": 20, "evolve": ["Money Changer", "Bank", "Vault", "Central Mint"]},
    "infra":    {"icon": "🏗️", "category": "utility",   "base_xp": 14, "evolve": ["Scaffolding", "Foundation", "Tower", "Citadel"]},
}

TITLE_LADDER = [
    (0,    "Homeless Penguin"),
    (50,   "Village Founder"),
    (150,  "Town Builder"),
    (400,  "City Architect"),
    (800,  "Urban Planner"),
    (1500, "Metropolitan Lord"),
    (3000, "Empire Architect"),
    (6000, "Legendary Constructor"),
    (10000, "Penguin God-Emperor"),
]

WEATHER_STATES = [
    ("☀️",  "Clear Skies",       "All systems operational"),
    ("⛅",  "Partly Cloudy",     "Minor issues detected"),
    ("🌧️", "Rainy",             "Some projects need attention"),
    ("⛈️",  "Thunderstorm",      "Multiple systems degraded"),
    ("🌨️", "Snowstorm",         "Critical issues present"),
    ("🌈",  "Rainbow",           "Everything is perfect!"),
]

RANDOM_EVENTS = [
    {"id": "gold_rush",    "name": "🪙 Gold Rush!",         "desc": "A whale bought your token! All finance buildings +50 XP.", "xp": 50, "filter": "finance"},
    {"id": "penguin_fest", "name": "🎪 Penguin Festival",    "desc": "Citizens celebrate! City +100 XP.",                       "xp": 100, "filter": None},
    {"id": "meteor",       "name": "☄️ Meteor Shower",       "desc": "Beautiful lights! Culture buildings +30 XP.",              "xp": 30, "filter": "culture"},
    {"id": "ice_storm",    "name": "🧊 Ice Storm",           "desc": "Brr! All sleeping buildings freeze. Wake them up!",       "xp": -20, "filter": "sleeping"},
    {"id": "explorer",     "name": "🧭 Explorer Penguin",    "desc": "A wanderer arrives with gifts! Random building +40 XP.",  "xp": 40, "filter": "random"},
    {"id": "bug_swarm",    "name": "🐛 Bug Swarm!",          "desc": "Bugs invade! Fix issues to defend. City -30 XP.",         "xp": -30, "filter": None},
    {"id": "northern_lights","name": "🌌 Northern Lights",   "desc": "Rare aurora! All buildings +20 XP.",                      "xp": 20, "filter": None},
    {"id": "treasure",     "name": "💎 Buried Treasure",     "desc": "Penguins found gems under the ice! +80 XP.",              "xp": 80, "filter": None},
    {"id": "pirate_raid",  "name": "🏴‍☠️ Pirate Raid",        "desc": "Pirates attack the harbor! Commerce buildings -25 XP.",   "xp": -25, "filter": "commerce"},
    {"id": "innovation",   "name": "💡 Innovation Boom",     "desc": "A breakthrough! Industry buildings +60 XP.",              "xp": 60, "filter": "industry"},
]

QUEST_TEMPLATES = [
    {"id": "deploy",       "name": "Ship It!",              "desc": "Deploy any project update",           "xp": 30, "icon": "🚀"},
    {"id": "uptime_week",  "name": "Iron Wall",             "desc": "Keep all sites up for 7 days straight","xp": 80, "icon": "🛡️"},
    {"id": "new_project",  "name": "Groundbreaking",        "desc": "Start a new project",                 "xp": 50, "icon": "🏗️"},
    {"id": "fix_bug",      "name": "Exterminator",          "desc": "Fix a bug in any project",            "xp": 25, "icon": "🔧"},
    {"id": "write_docs",   "name": "Lorekeeper",            "desc": "Write documentation for a project",   "xp": 20, "icon": "📚"},
    {"id": "optimize",     "name": "Speed Demon",           "desc": "Optimize performance of any service",  "xp": 40, "icon": "⚡"},
    {"id": "cleanup",      "name": "Spring Cleaning",       "desc": "Remove dead code or unused files",     "xp": 15, "icon": "🧹"},
    {"id": "security",     "name": "Guardian",              "desc": "Fix a security vulnerability",         "xp": 60, "icon": "🔒"},
    {"id": "collab",       "name": "Alliance",              "desc": "Merge a PR or collaborate on code",    "xp": 35, "icon": "🤝"},
    {"id": "streak_3",     "name": "Hat Trick",             "desc": "Complete 3 quests in one day",          "xp": 100,"icon": "🎩"},
]

ACHIEVEMENTS = [
    {"id": "first_building",  "name": "First Brick",        "desc": "Build your first building",           "icon": "🧱"},
    {"id": "five_buildings",  "name": "Small Town",          "desc": "Have 5 buildings",                    "icon": "🏘️"},
    {"id": "ten_buildings",   "name": "Growing City",        "desc": "Have 10 buildings",                   "icon": "🌆"},
    {"id": "twenty_buildings","name": "Metropolis",          "desc": "Have 20 buildings",                   "icon": "🏙️"},
    {"id": "first_lvl3",     "name": "Skyscraper",          "desc": "Upgrade any building to level 3",     "icon": "🏢"},
    {"id": "first_lvl4",     "name": "Wonder of the World", "desc": "Max out a building (level 4)",        "icon": "🗿"},
    {"id": "quest_10",       "name": "Adventurer",          "desc": "Complete 10 quests",                  "icon": "⚔️"},
    {"id": "quest_50",       "name": "Legend",              "desc": "Complete 50 quests",                  "icon": "👑"},
    {"id": "xp_1000",        "name": "Millennial Penguin",  "desc": "Earn 1000 total XP",                  "icon": "💫"},
    {"id": "xp_5000",        "name": "Eternal Builder",     "desc": "Earn 5000 total XP",                  "icon": "✨"},
    {"id": "survivor",       "name": "Survivor",            "desc": "Survive 5 negative events",           "icon": "🏆"},
    {"id": "lucky",          "name": "Fortune's Favorite",  "desc": "Trigger 5 positive events",           "icon": "🍀"},
]

# ── City State ─────────────────────────────────────────────────────────

def default_city(name="PenguinCity"):
    return {
        "version": 2,
        "name": name,
        "founded": datetime.now(timezone.utc).isoformat(),
        "mayor": {
            "name": "Mayor",
            "title": "Homeless Penguin",
            "xp": 0,
            "level": 1,
            "quests_completed": 0,
            "events_survived": 0,
            "events_blessed": 0,
        },
        "buildings": [],
        "quests": [],
        "achievements": [],
        "log": [],
        "last_event": None,
        "last_quest_refresh": None,
        "population": 0,
        "gold": 100,
    }

def load_city():
    try:
        with open(CITY_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_city(city):
    Path(CITY_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(CITY_FILE, "w") as f:
        json.dump(city, f, indent=2, ensure_ascii=False)

def add_log(city, msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    city["log"].append({"ts": ts, "msg": msg})
    if len(city["log"]) > 100:
        city["log"] = city["log"][-100:]

# ── XP & Leveling ─────────────────────────────────────────────────────

def calc_level(xp):
    level = 1
    title = TITLE_LADDER[0][1]
    for threshold, t in TITLE_LADDER:
        if xp >= threshold:
            title = t
            level += 1
    return min(level, len(TITLE_LADDER)), title

def xp_for_next(xp):
    for threshold, _ in TITLE_LADDER:
        if xp < threshold:
            return threshold
    return TITLE_LADDER[-1][0]

def grant_xp(city, amount, reason=""):
    city["mayor"]["xp"] += amount
    if city["mayor"]["xp"] < 0:
        city["mayor"]["xp"] = 0
    old_level = city["mayor"]["level"]
    new_level, new_title = calc_level(city["mayor"]["xp"])
    city["mayor"]["level"] = new_level
    city["mayor"]["title"] = new_title
    if new_level > old_level:
        add_log(city, f"🎉 LEVEL UP! Now Lv.{new_level} — {new_title}")
    if reason:
        sign = "+" if amount >= 0 else ""
        add_log(city, f"{sign}{amount} XP: {reason}")

# ── Buildings ──────────────────────────────────────────────────────────

def building_level(b):
    xp = b.get("xp", 0)
    if xp >= 200: return 4
    if xp >= 80: return 3
    if xp >= 30: return 2
    return 1

def building_status(b):
    """Determine building health from last_active timestamp."""
    last = b.get("last_active")
    if not last:
        return "abandoned"
    try:
        dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
        days = (datetime.now(timezone.utc) - dt).days
    except:
        return "unknown"
    if days <= 3:   return "thriving"
    if days <= 14:  return "active"
    if days <= 60:  return "idle"
    return "abandoned"

STATUS_ICONS = {
    "thriving": "🟢",
    "active": "🟡",
    "idle": "🟠",
    "abandoned": "🔴",
    "unknown": "⚪",
}

STATUS_LABELS = {
    "thriving": "Thriving",
    "active": "Active",
    "idle": "Idle",
    "abandoned": "Abandoned",
    "unknown": "Unknown",
}

def add_building(city, name, btype="repo", url=None, server=None, path=None, stars=0):
    # Check duplicate
    for b in city["buildings"]:
        if b["name"].lower() == name.lower():
            return None, f"Building '{name}' already exists!"

    bt = BUILDING_TYPES.get(btype, BUILDING_TYPES["repo"])
    building = {
        "name": name,
        "type": btype,
        "url": url,
        "server": server,
        "path": path,
        "xp": min(stars, 200) if stars else 0,
        "created": datetime.now(timezone.utc).isoformat(),
        "last_active": datetime.now(timezone.utc).isoformat(),
        "upgrades": 0,
    }
    city["buildings"].append(building)
    grant_xp(city, bt["base_xp"], f"Built {bt['icon']} {name}")
    city["population"] += random.randint(5, 20)
    check_achievements(city)
    return building, None

# ── Quests ─────────────────────────────────────────────────────────────

def refresh_quests(city, force=False):
    last = city.get("last_quest_refresh")
    now = datetime.now(timezone.utc)

    if not force and last:
        try:
            last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
            if (now - last_dt).total_seconds() < 86400:
                return  # Already refreshed today
        except:
            pass

    # Pick 3 random quests
    available = [q for q in QUEST_TEMPLATES if q["id"] not in [aq["id"] for aq in city["quests"] if not aq.get("completed")]]
    if len(available) < 3:
        available = QUEST_TEMPLATES.copy()

    rng = random.Random(now.strftime("%Y-%m-%d"))
    picks = rng.sample(available, min(3, len(available)))

    city["quests"] = [q for q in city["quests"] if q.get("completed")][-20:]  # keep last 20 completed
    for p in picks:
        city["quests"].append({**p, "completed": False, "assigned": now.isoformat()})

    city["last_quest_refresh"] = now.isoformat()

def complete_quest(city, quest_id):
    for q in city["quests"]:
        if q["id"] == quest_id and not q.get("completed"):
            q["completed"] = True
            q["completed_at"] = datetime.now(timezone.utc).isoformat()
            grant_xp(city, q["xp"], f"Quest: {q['icon']} {q['name']}")
            city["mayor"]["quests_completed"] += 1
            check_achievements(city)
            return q
    return None

# ── Events ─────────────────────────────────────────────────────────────

def trigger_event(city):
    now = datetime.now(timezone.utc)
    last = city.get("last_event")
    if last:
        try:
            last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
            if (now - last_dt).total_seconds() < 14400:  # 4 hour cooldown
                return None
        except:
            pass

    # 30% chance of event
    if random.random() > 0.30:
        return None

    event = random.choice(RANDOM_EVENTS)
    city["last_event"] = now.isoformat()
    add_log(city, f"{event['name']}: {event['desc']}")

    # Apply XP
    if event["filter"] is None:
        grant_xp(city, event["xp"], event["name"])
    elif event["filter"] == "random" and city["buildings"]:
        b = random.choice(city["buildings"])
        b["xp"] = max(0, b.get("xp", 0) + event["xp"])
        add_log(city, f"  → Applied to {b['name']}")
    elif event["filter"] == "sleeping":
        for b in city["buildings"]:
            if building_status(b) in ("idle", "abandoned"):
                b["xp"] = max(0, b.get("xp", 0) + event["xp"])
    else:
        for b in city["buildings"]:
            bt = BUILDING_TYPES.get(b["type"], {})
            if bt.get("category") == event["filter"]:
                b["xp"] = max(0, b.get("xp", 0) + event["xp"])

    if event["xp"] >= 0:
        city["mayor"]["events_blessed"] += 1
    else:
        city["mayor"]["events_survived"] += 1

    check_achievements(city)
    return event

# ── Achievements ───────────────────────────────────────────────────────

def check_achievements(city):
    unlocked = set(city.get("achievements", []))
    buildings = city["buildings"]
    mayor = city["mayor"]

    checks = {
        "first_building":   len(buildings) >= 1,
        "five_buildings":   len(buildings) >= 5,
        "ten_buildings":    len(buildings) >= 10,
        "twenty_buildings": len(buildings) >= 20,
        "first_lvl3":       any(building_level(b) >= 3 for b in buildings),
        "first_lvl4":       any(building_level(b) >= 4 for b in buildings),
        "quest_10":         mayor.get("quests_completed", 0) >= 10,
        "quest_50":         mayor.get("quests_completed", 0) >= 50,
        "xp_1000":          mayor.get("xp", 0) >= 1000,
        "xp_5000":          mayor.get("xp", 0) >= 5000,
        "survivor":         mayor.get("events_survived", 0) >= 5,
        "lucky":            mayor.get("events_blessed", 0) >= 5,
    }

    newly_unlocked = []
    for ach in ACHIEVEMENTS:
        if ach["id"] not in unlocked and checks.get(ach["id"], False):
            unlocked.add(ach["id"])
            newly_unlocked.append(ach)
            add_log(city, f"🏆 Achievement Unlocked: {ach['icon']} {ach['name']}")

    city["achievements"] = list(unlocked)
    return newly_unlocked

# ── Weather ────────────────────────────────────────────────────────────

def calc_weather(city):
    if not city["buildings"]:
        return WEATHER_STATES[0]

    statuses = [building_status(b) for b in city["buildings"]]
    abandoned = statuses.count("abandoned") + statuses.count("idle")
    ratio = abandoned / len(statuses)

    if ratio == 0:
        return WEATHER_STATES[5]  # Rainbow — perfect!
    elif ratio < 0.15:
        return WEATHER_STATES[0]  # Clear
    elif ratio < 0.3:
        return WEATHER_STATES[1]  # Partly cloudy
    elif ratio < 0.5:
        return WEATHER_STATES[2]  # Rainy
    elif ratio < 0.7:
        return WEATHER_STATES[3]  # Thunderstorm
    else:
        return WEATHER_STATES[4]  # Snowstorm

# ── GitHub Import ──────────────────────────────────────────────────────

def import_github(city, username):
    """Import GitHub repos as buildings."""
    import urllib.request
    import urllib.error

    token = os.environ.get("GITHUB_TOKEN")
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}&sort=stars&direction=desc"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github.v3+json")
        req.add_header("User-Agent", "penguin-city")
        if token:
            req.add_header("Authorization", f"token {token}")
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                if not data: break
                repos.extend(data)
                if len(data) < 100: break
                page += 1
        except urllib.error.HTTPError as e:
            print(f"GitHub API error: {e.code}", file=sys.stderr)
            return 0

    added = 0
    for r in repos:
        if r.get("fork"): continue
        name = r["name"]
        stars = r.get("stargazers_count", 0)
        lang = r.get("language", "")

        # Guess building type from repo metadata
        desc = (r.get("description") or "").lower()
        topics = r.get("topics", [])
        btype = "repo"
        if any(w in desc for w in ["api", "server", "backend"]):
            btype = "api"
        elif any(w in desc for w in ["bot", "telegram", "discord"]):
            btype = "bot"
        elif any(w in desc for w in ["game", "play"]):
            btype = "game"
        elif any(w in desc for w in ["blog", "post", "write"]):
            btype = "blog"
        elif any(w in desc for w in ["tool", "cli", "util"]):
            btype = "tool"
        elif any(w in desc for w in ["defi", "swap", "token", "contract"]):
            btype = "defi"
        elif r.get("has_pages"):
            btype = "website"

        # Set last_active from pushed_at
        pushed = r.get("pushed_at") or r.get("updated_at", "")

        existing = [b for b in city["buildings"] if b["name"].lower() == name.lower()]
        if existing:
            # Update existing building
            b = existing[0]
            b["last_active"] = pushed
            b["xp"] = max(b.get("xp", 0), min(stars, 200))
            continue

        building, err = add_building(city, name, btype, url=r.get("html_url"), stars=stars)
        if building:
            building["last_active"] = pushed
            building["github"] = True
            added += 1

    return added

# ── ASCII Renderer ─────────────────────────────────────────────────────

def render_ascii(city):
    mayor = city["mayor"]
    level, title = calc_level(mayor["xp"])
    next_xp = xp_for_next(mayor["xp"])
    weather = calc_weather(city)

    # XP bar
    if next_xp > 0:
        pct = min(mayor["xp"] / next_xp, 1.0)
    else:
        pct = 1.0
    bar_len = 20
    filled = int(pct * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)

    lines = []
    lines.append(f"╔══════════════════════════════════════════╗")
    lines.append(f"║  🏰 {city['name']}   {weather[0]} {weather[1]:<16}  ║")
    lines.append(f"╠══════════════════════════════════════════╣")
    lines.append(f"║  👤 {mayor['name']}  Lv.{level} [{title}]")
    lines.append(f"║  ⚡ {bar} {mayor['xp']}/{next_xp} XP")
    lines.append(f"║  👥 {city.get('population', 0)} citizens  🪙 {city.get('gold', 0)} gold")
    lines.append(f"║  🏆 {len(city.get('achievements', []))} achievements  📜 {mayor.get('quests_completed', 0)} quests done")
    lines.append(f"╠══════════════════════════════════════════╣")

    if city["buildings"]:
        lines.append(f"║  🏗️ Buildings ({len(city['buildings'])})")
        lines.append(f"║  {'─' * 38}")

        # Sort: thriving first, then abandoned last
        status_order = {"thriving": 0, "active": 1, "idle": 2, "abandoned": 3, "unknown": 4}
        sorted_buildings = sorted(city["buildings"],
            key=lambda b: (status_order.get(building_status(b), 5), -b.get("xp", 0)))

        for b in sorted_buildings:
            bt = BUILDING_TYPES.get(b["type"], BUILDING_TYPES["repo"])
            lvl = building_level(b)
            status = building_status(b)
            evo_name = bt["evolve"][lvl - 1] if lvl <= len(bt["evolve"]) else bt["evolve"][-1]
            stars = "⭐" * lvl
            lines.append(f"║  {STATUS_ICONS[status]} {bt['icon']} {b['name']:<16} {evo_name:<14} {stars}")
    else:
        lines.append(f"║  🏗️ No buildings yet! Use 'add' or 'github'")

    # Active quests
    active_quests = [q for q in city.get("quests", []) if not q.get("completed")]
    if active_quests:
        lines.append(f"╠══════════════════════════════════════════╣")
        lines.append(f"║  📋 Active Quests")
        for q in active_quests:
            lines.append(f"║  {q['icon']} {q['name']:<20} +{q['xp']} XP")
            lines.append(f"║     {q['desc']}")

    lines.append(f"╚══════════════════════════════════════════╝")
    return "\n".join(lines)

# ── SVG Renderer ───────────────────────────────────────────────────────

def render_svg(city):
    """Generate a full city SVG with buildings, terrain, and atmosphere."""
    mayor = city["mayor"]
    level, title = calc_level(mayor["xp"])
    weather = calc_weather(city)
    buildings = city["buildings"]

    if not buildings:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="200"><rect width="600" height="200" fill="#0a1628"/><text x="300" y="100" text-anchor="middle" fill="white" font-family="monospace" font-size="16">🏰 Empty city. Add some buildings! 🐧</text></svg>'

    # Layout
    cols = min(8, max(3, int(math.sqrt(len(buildings)) * 1.2)))
    cell_w = 150
    cell_h = 180
    padding = 80
    header_h = 100
    footer_h = 60

    rows = math.ceil(len(buildings) / cols)
    width = cols * cell_w + padding * 2
    height = header_h + rows * cell_h + padding + footer_h

    rng = random.Random(city.get("founded", "seed"))

    # Time-based sky (uses local hour concept)
    hour = datetime.now().hour
    if 6 <= hour < 18:
        sky_top, sky_mid, sky_bot = "#1a0533", "#0c1e3d", "#162d50"
        star_opacity = 0.3
    elif 18 <= hour < 21:
        sky_top, sky_mid, sky_bot = "#1a0533", "#2d1b4e", "#0f1d32"
        star_opacity = 0.6
    else:
        sky_top, sky_mid, sky_bot = "#020817", "#0a1628", "#111d2e"
        star_opacity = 1.0

    # Stars background
    stars_bg = ""
    for _ in range(50):
        sx, sy = rng.randint(0, width), rng.randint(5, header_h)
        sr = round(0.3 + rng.random() * 1.5, 1)
        so = round((0.2 + rng.random() * 0.6) * star_opacity, 2)
        dur = round(1.5 + rng.random() * 4, 1)
        stars_bg += f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" opacity="{so}"><animate attributeName="opacity" values="{so};{so*0.2};{so}" dur="{dur}s" repeatCount="indefinite"/></circle>\n'

    # Snowflakes
    snow = ""
    for _ in range(30):
        sx = rng.randint(0, width)
        sy = rng.randint(0, height - 60)
        sr = round(0.5 + rng.random() * 2, 1)
        dur = round(4 + rng.random() * 6, 1)
        snow += f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="white" opacity="0.3"><animate attributeName="cy" from="{sy}" to="{sy+80}" dur="{dur}s" repeatCount="indefinite"/></circle>\n'

    # Ground with parallax ice layers
    ground_y = header_h + rows * cell_h + padding - 40
    ground = f'''
    <rect x="0" y="{ground_y}" width="{width}" height="{height - ground_y}" fill="#0a1220"/>
    <rect x="0" y="{ground_y}" width="{width}" height="6" fill="#3b82f6" opacity="0.15"/>
    <rect x="0" y="{ground_y+3}" width="{width}" height="2" fill="#60a5fa" opacity="0.08"/>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{sky_top}"/>
      <stop offset="50%" stop-color="{sky_mid}"/>
      <stop offset="100%" stop-color="{sky_bot}"/>
    </linearGradient>
    <linearGradient id="aurora1" x1="0" y1="0" x2="1" y2="0.3">
      <stop offset="0%" stop-color="#00ff87" stop-opacity="0"/>
      <stop offset="30%" stop-color="#00ff87" stop-opacity="0.12"/>
      <stop offset="50%" stop-color="#60efff" stop-opacity="0.18"/>
      <stop offset="70%" stop-color="#7c5cfc" stop-opacity="0.1"/>
      <stop offset="100%" stop-color="#ff6bcd" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <filter id="aurora_blur"><feGaussianBlur stdDeviation="20"/></filter>
    <filter id="building_shadow"><feDropShadow dx="2" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.5"/></filter>
  </defs>

  <!-- Sky -->
  <rect width="{width}" height="{height}" fill="url(#sky)"/>

  <!-- Aurora -->
  <ellipse cx="{width*0.3}" cy="40" rx="{width*0.5}" ry="60" fill="url(#aurora1)" filter="url(#aurora_blur)">
    <animate attributeName="rx" values="{width*0.5};{width*0.55};{width*0.45};{width*0.5}" dur="8s" repeatCount="indefinite"/>
  </ellipse>

  <!-- Stars -->
  {stars_bg}

  <!-- Snow -->
  {snow}

  <!-- Ground -->
  {ground}

  <!-- Header -->
  <text x="{width//2}" y="35" text-anchor="middle" font-family="'Segoe UI',system-ui,sans-serif" font-size="22" fill="white" font-weight="bold" filter="url(#glow)">🏰 {city["name"]}</text>
  <text x="{width//2}" y="58" text-anchor="middle" font-family="monospace" font-size="12" fill="#8b949e">
    {weather[0]} {weather[1]}  ·  👤 {mayor["name"]} Lv.{level} [{title}]  ·  👥 {city.get("population",0)} citizens
  </text>
  <text x="{width//2}" y="78" text-anchor="middle" font-family="monospace" font-size="11" fill="#6e7681">
    {len(buildings)} buildings  ·  ⚡ {mayor["xp"]} XP  ·  🏆 {len(city.get("achievements",[]))} achievements
  </text>
'''

    # Sort buildings by XP (biggest in back)
    sorted_b = sorted(buildings, key=lambda b: b.get("xp", 0))

    for i, b in enumerate(sorted_b):
        col = i % cols
        row = i // cols
        cx = padding + col * cell_w + cell_w // 2
        cy = header_h + row * cell_h + 60

        bt = BUILDING_TYPES.get(b["type"], BUILDING_TYPES["repo"])
        lvl = building_level(b)
        status = building_status(b)
        evo_name = bt["evolve"][lvl - 1] if lvl <= len(bt["evolve"]) else bt["evolve"][-1]

        # Building size scales with level
        scale = 0.6 + lvl * 0.2
        bw = int(40 * scale)
        bh = int(60 * scale)

        # Status-based colors
        status_colors = {
            "thriving": ("#4ade80", "#22c55e"),
            "active":   ("#facc15", "#eab308"),
            "idle":     ("#fb923c", "#f97316"),
            "abandoned":("#ef4444", "#dc2626"),
            "unknown":  ("#9ca3af", "#6b7280"),
        }
        color1, color2 = status_colors.get(status, ("#9ca3af", "#6b7280"))

        # Building shape varies by category
        cat = bt.get("category", "district")
        if cat == "commerce":
            building_shape = f'''
            <rect x="{cx-bw//2}" y="{cy-bh}" width="{bw}" height="{bh}" rx="3" fill="#1e293b" stroke="{color1}" stroke-width="1.5" filter="url(#building_shadow)"/>
            <rect x="{cx-bw//2+3}" y="{cy-bh+4}" width="{bw-6}" height="{bh//3}" rx="2" fill="{color1}" opacity="0.2"/>
            <rect x="{cx-bw//2}" y="{cy-bh}" width="{bw}" height="4" fill="{color1}" opacity="0.6"/>'''
        elif cat == "industry":
            building_shape = f'''
            <rect x="{cx-bw//2}" y="{cy-bh}" width="{bw}" height="{bh}" rx="2" fill="#1e293b" stroke="{color1}" stroke-width="1.5" filter="url(#building_shadow)"/>
            <rect x="{cx-bw//2+bw-8}" y="{cy-bh-15}" width="6" height="15" fill="#374151"/>
            <circle cx="{cx-bw//2+bw-5}" cy="{cy-bh-15}" r="4" fill="{color1}" opacity="0.4"/>'''
        elif cat == "military":
            building_shape = f'''
            <rect x="{cx-bw//2}" y="{cy-bh}" width="{bw}" height="{bh}" rx="2" fill="#1e293b" stroke="{color1}" stroke-width="1.5" filter="url(#building_shadow)"/>
            <polygon points="{cx},{cy-bh-12} {cx-bw//3},{cy-bh} {cx+bw//3},{cy-bh}" fill="#374151" stroke="{color1}" stroke-width="1"/>'''
        elif cat == "entertainment":
            building_shape = f'''
            <rect x="{cx-bw//2}" y="{cy-bh}" width="{bw}" height="{bh}" rx="6" fill="#1e293b" stroke="{color1}" stroke-width="1.5" filter="url(#building_shadow)"/>
            <circle cx="{cx}" cy="{cy-bh-5}" r="{bw//4}" fill="{color1}" opacity="0.15"/>'''
        elif cat == "finance":
            building_shape = f'''
            <rect x="{cx-bw//2}" y="{cy-bh}" width="{bw}" height="{bh}" fill="#1e293b" stroke="{color1}" stroke-width="2" filter="url(#building_shadow)"/>
            <rect x="{cx-bw//2}" y="{cy-bh}" width="{bw}" height="8" fill="{color1}" opacity="0.5"/>
            <line x1="{cx-bw//4}" y1="{cy-bh+8}" x2="{cx-bw//4}" y2="{cy}" stroke="{color2}" stroke-width="1" opacity="0.3"/>
            <line x1="{cx+bw//4}" y1="{cy-bh+8}" x2="{cx+bw//4}" y2="{cy}" stroke="{color2}" stroke-width="1" opacity="0.3"/>'''
        else:
            building_shape = f'''
            <rect x="{cx-bw//2}" y="{cy-bh}" width="{bw}" height="{bh}" rx="3" fill="#1e293b" stroke="{color1}" stroke-width="1.5" filter="url(#building_shadow)"/>'''

        # Windows (lit if active)
        windows = ""
        win_rows = min(lvl, 3)
        for wr in range(win_rows):
            for wc in range(2):
                wx = cx - bw//4 + wc * bw//2
                wy = cy - bh + 15 + wr * (bh // 4)
                win_lit = status in ("thriving", "active")
                wcolor = "#fef08a" if win_lit else "#1e293b"
                wopacity = 0.8 if win_lit else 0.3
                windows += f'<rect x="{wx-3}" y="{wy}" width="6" height="6" fill="{wcolor}" opacity="{wopacity}"/>'
                if win_lit:
                    windows += f'<rect x="{wx-3}" y="{wy}" width="6" height="6" fill="{wcolor}" opacity="0.3"><animate attributeName="opacity" values="0.3;0.6;0.3" dur="{2+rng.random()*3:.1f}s" repeatCount="indefinite"/></rect>'

        # Status indicator
        status_light = f'<circle cx="{cx+bw//2+6}" cy="{cy-bh+6}" r="3" fill="{color1}"><animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite"/></circle>'

        # Label
        display_name = b["name"] if len(b["name"]) <= 14 else b["name"][:12] + ".."
        label = f'''
        <text x="{cx}" y="{cy+16}" text-anchor="middle" font-family="monospace" font-size="10" fill="#e6edf3" font-weight="600">{display_name}</text>
        <text x="{cx}" y="{cy+30}" text-anchor="middle" font-family="monospace" font-size="8" fill="#8b949e">{bt["icon"]} {evo_name} {"⭐"*lvl}</text>'''

        svg += f'''
  <!-- {b["name"]} -->
  <g>{building_shape}{windows}{status_light}{label}</g>'''

    # Footer
    svg += f'''

  <!-- Footer -->
  <rect x="{padding-10}" y="{height-footer_h+5}" width="{width-padding*2+20}" height="22" rx="11" fill="#161b22" opacity="0.8" stroke="#30363d" stroke-width="0.5"/>
  <text x="{width//2}" y="{height-footer_h+20}" text-anchor="middle" font-family="monospace" font-size="9" fill="#8b949e">
    🟢 thriving  🟡 active  🟠 idle  🔴 abandoned  ·  building size = level  ·  lit windows = alive
  </text>
</svg>'''
    return svg

# ── CLI ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="🏰 PenguinCity — RPG City Builder for your projects")
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Initialize your city")
    p_init.add_argument("--name", default="PenguinCity", help="City name")

    # status
    sub.add_parser("status", help="Show city dashboard")

    # render
    p_render = sub.add_parser("render", help="Generate SVG city map")
    p_render.add_argument("-o", "--output", default=None)

    # add
    p_add = sub.add_parser("add", help="Add a building")
    p_add.add_argument("name", help="Building name")
    p_add.add_argument("--type", default="repo", choices=list(BUILDING_TYPES.keys()))
    p_add.add_argument("--url", default=None)
    p_add.add_argument("--server", default=None)
    p_add.add_argument("--path", default=None)

    # github
    p_gh = sub.add_parser("github", help="Import GitHub repos")
    p_gh.add_argument("username")

    # quest
    p_quest = sub.add_parser("quest", help="Quest board")
    p_quest.add_argument("action", nargs="?", default="list", choices=["list", "complete", "refresh"])
    p_quest.add_argument("quest_id", nargs="?")

    # event
    sub.add_parser("event", help="Check for random events")

    # log
    p_log = sub.add_parser("log", help="City history")
    p_log.add_argument("-n", type=int, default=15)

    # demolish
    p_demo = sub.add_parser("demolish", help="Remove a building")
    p_demo.add_argument("name")

    args = parser.parse_args()

    if args.command == "init":
        if os.path.exists(CITY_FILE):
            print(f"City already exists at {CITY_FILE}!")
            print("Delete it first if you want to start over.")
            return
        city = default_city(args.name)
        add_log(city, f"🏰 {args.name} was founded!")
        save_city(city)
        print(f"🏰 {args.name} founded! You are the mayor.")
        print(f"Next: add buildings with 'city.py add' or import from GitHub with 'city.py github <user>'")
        return

    # All other commands need existing city
    city = load_city()
    if not city:
        print("No city found! Run 'city.py init' first.", file=sys.stderr)
        sys.exit(1)

    if args.command == "status":
        refresh_quests(city)
        event = trigger_event(city)
        save_city(city)
        print(render_ascii(city))
        if event:
            print(f"\n⚡ EVENT: {event['name']}")
            print(f"   {event['desc']}")

    elif args.command == "render":
        svg = render_svg(city)
        if args.output:
            with open(args.output, "w") as f:
                f.write(svg)
            print(f"City map saved to {args.output}", file=sys.stderr)
        else:
            print(svg)

    elif args.command == "add":
        building, err = add_building(city, args.name, args.type, args.url, args.server, args.path)
        if err:
            print(f"❌ {err}")
        else:
            bt = BUILDING_TYPES[args.type]
            lvl = building_level(building)
            print(f"🏗️ Built {bt['icon']} {args.name} — {bt['evolve'][0]}!")
            print(f"   Type: {args.type} | XP: {building['xp']} | Level: {lvl}")
        save_city(city)

    elif args.command == "github":
        print(f"🐙 Fetching repos for {args.username}...")
        added = import_github(city, args.username)
        save_city(city)
        print(f"✅ Imported {added} new repos as buildings ({len(city['buildings'])} total)")

    elif args.command == "quest":
        if args.action == "refresh":
            refresh_quests(city, force=True)
            save_city(city)
            print("📋 Quests refreshed!")
        elif args.action == "complete" and args.quest_id:
            q = complete_quest(city, args.quest_id)
            if q:
                print(f"✅ Quest completed: {q['icon']} {q['name']} (+{q['xp']} XP)")
            else:
                print(f"❌ Quest '{args.quest_id}' not found or already completed")
                active = [q for q in city["quests"] if not q.get("completed")]
                if active:
                    print("Active quests:", ", ".join(f"{q['id']}" for q in active))
            save_city(city)
        else:
            refresh_quests(city)
            save_city(city)
            active = [q for q in city["quests"] if not q.get("completed")]
            if active:
                print("📋 Active Quests:")
                for q in active:
                    print(f"  {q['icon']} {q['name']:<20} +{q['xp']} XP")
                    print(f"     {q['desc']}")
                    print(f"     ID: {q['id']}")
            else:
                print("No active quests. Use 'quest refresh' to get new ones.")

    elif args.command == "event":
        event = trigger_event(city)
        if event:
            print(f"⚡ {event['name']}")
            print(f"   {event['desc']}")
            print(f"   XP: {'+' if event['xp'] >= 0 else ''}{event['xp']}")
        else:
            print("Nothing happened... (events have a cooldown)")
        save_city(city)

    elif args.command == "log":
        logs = city.get("log", [])[-args.n:]
        if logs:
            print("📜 City Log:")
            for entry in logs:
                print(f"  [{entry['ts']}] {entry['msg']}")
        else:
            print("No history yet.")

    elif args.command == "demolish":
        found = None
        for i, b in enumerate(city["buildings"]):
            if b["name"].lower() == args.name.lower():
                found = i
                break
        if found is not None:
            removed = city["buildings"].pop(found)
            bt = BUILDING_TYPES.get(removed["type"], BUILDING_TYPES["repo"])
            add_log(city, f"🏚️ Demolished {bt['icon']} {removed['name']}")
            print(f"🏚️ {removed['name']} has been demolished.")
            save_city(city)
        else:
            print(f"❌ Building '{args.name}' not found")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
