"""World data: items, weapons, locations, NPCs, recipes, enemies, weather, endings."""

from typing import Any, Dict, List

KID_NAMES = ["Eli", "Jun", "Rae", "Nico", "Sam"]

WEAPONS: Dict[str, Dict[str, Any]] = {
    "fists": {"name": "Bare Hands", "dmg": 4},
    "pipe": {"name": "Pipe Club", "dmg": 8},
    "crowbar": {"name": "Crowbar", "dmg": 11},
    "pistol": {"name": "Pistol", "dmg": 16, "ranged": True},
}

ITEMS: Dict[str, Dict[str, str]] = {
    "pipe": {"name": "Pipe Club", "desc": "Heavy plumbing. Honest work."},
    "crowbar": {"name": "Crowbar", "desc": "Opens doors. Closes arguments."},
    "pistol": {"name": "Pistol", "desc": "Six hopes and a click."},
    "mask": {"name": "Filter Mask", "desc": "Cuts infection from the air, not from teeth."},
    "radio_parts": {"name": "Radio Parts", "desc": "Tubes, wire, a cracked crystal."},
    "lena_notes": {"name": "Voss Notes", "desc": "Half a treatment. Half a confession."},
    "holy_charm": {"name": "Wooden Charm", "desc": "Miriam pressed it into your hand."},
    "tunnel_key": {"name": "Tunnel Key", "desc": "Ghost's shortcut under the city."},
    "molotov": {"name": "Molotov", "desc": "One bright, stupid miracle."},
    "antibiotics": {"name": "Antibiotics", "desc": "Bitter. Real. Finite."},
    "photo": {"name": "School Photo", "desc": "A class that will not come back."},
    "halcyon_map": {"name": "Halcyon Leaflet", "desc": "SAFE ZONE. BRING THE LIVING."},
}

LOCATIONS: Dict[str, Dict[str, Any]] = {
    "Home Base": {"id": "base", "risk": 0.05, "loot": "none", "blurb": "Boards, a kettle, a door that still closes."},
    "Streets": {"id": "streets", "risk": 0.25, "loot": "mixed", "blurb": "Cars like shed skins. Windows like broken teeth."},
    "Abandoned Mall": {"id": "mall", "risk": 0.40, "loot": "food", "blurb": "A temple of wanting. The mannequins have not moved. You hope."},
    "Hospital": {"id": "hospital", "risk": 0.45, "loot": "meds", "blurb": "The smell is sweet and wrong. Charts still hang on doors."},
    "Radio Tower": {"id": "radio", "risk": 0.35, "loot": "parts", "blurb": "A needle in the sky. Channel 7 still breathes."},
    "Warehouse": {"id": "warehouse", "risk": 0.40, "loot": "scrap", "blurb": "Iron guts of the old world. Something lives in the aisles."},
    "Church": {"id": "church", "risk": 0.20, "loot": "morale", "blurb": "Candles burned to nubs. Someone still keeps the aisle clear."},
    "Subway Tunnels": {"id": "subway", "risk": 0.50, "loot": "stealth", "blurb": "Dark that has weight. Trains sleep like whales."},
    "Military Checkpoint": {"id": "checkpoint", "risk": 0.55, "loot": "ammo", "blurb": "Sandbags, a dead generator, a sign that says HALCYON 18km."},
    "School": {"id": "school", "risk": 0.30, "loot": "story", "blurb": "Tiny chairs. A bell that will not ring."},
    "Docks": {"id": "docks", "risk": 0.35, "loot": "escape", "blurb": "Black water. A boat that might still be a boat."},
    "Gas Station": {"id": "gas", "risk": 0.30, "loot": "fuel", "blurb": "Pumps frozen at $0.00. The lot is a killing floor."},
}

NPC_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "marcus": {
        "id": "marcus",
        "name": 'Marcus "Radio" Hale',
        "short": "Marcus",
        "role": "Broadcaster",
        "color": "#6ec8ff",
        "voice": "He still leaves a beat before the last word, like the legal ID is coming.",
    },
    "lena": {
        "id": "lena",
        "name": "Dr. Lena Voss",
        "short": "Lena",
        "role": "Scientist",
        "color": "#9dffb0",
        "voice": "Precise. Tired of being believed only when it is too late.",
    },
    "kid": {
        "id": "kid",
        "name": "The Kid",
        "short": "Kid",
        "role": "Child",
        "color": "#ffe08a",
        "voice": "Asks the questions you have been stepping around.",
    },
    "butcher": {
        "id": "butcher",
        "name": "The Butcher",
        "short": "Butcher",
        "role": "Scavenger",
        "color": "#ff6b6b",
        "voice": "Friendly the way a cleaver is friendly: useful, until it is not.",
    },
    "miriam": {
        "id": "miriam",
        "name": "Sister Miriam",
        "short": "Miriam",
        "role": "Believer",
        "color": "#d4b5ff",
        "voice": "Gentle. Uncompromising. She has already buried everyone once.",
    },
    "ghost": {
        "id": "ghost",
        "name": "Ghost",
        "short": "Ghost",
        "role": "Scout",
        "color": "#a0b4c8",
        "voice": "Does not speak. The throat wound is old. The eyes are not.",
    },
}

RECIPES: List[Dict[str, Any]] = [
    {
        "id": "pipe",
        "name": "Pipe Club",
        "cost": {"scrap": 2},
        "give_item": "pipe",
        "weapon": "pipe",
        "log": "You wrap tape around a length of pipe. It hums when it hits.",
    },
    {
        "id": "barricade",
        "name": "Barricade",
        "cost": {"scrap": 3},
        "fort": 1,
        "log": "Another board. Another nail. The door looks less like an apology.",
    },
    {
        "id": "rain",
        "name": "Rain Catcher",
        "cost": {"scrap": 3},
        "flag": "rain_catcher",
        "log": "Tarps and gutters. The sky owes you now.",
    },
    {
        "id": "garden",
        "name": "Planter Boxes",
        "cost": {"scrap": 2, "food": 1},
        "flag": "garden",
        "log": "You plant like a person who expects a next month.",
    },
    {
        "id": "alarm",
        "name": "Tin Alarm",
        "cost": {"scrap": 2},
        "flag": "alarm",
        "log": "Cans on a wire. A cheap choir for the end of the world.",
    },
    {
        "id": "medbay",
        "name": "Med Station",
        "cost": {"scrap": 4, "medkits": 1},
        "flag": "medbay",
        "log": "Clean cloth, boiled water, a place to be afraid with better odds.",
    },
    {
        "id": "radio",
        "name": "Boost the Radio",
        "cost": {"scrap": 2},
        "need_item": "radio_parts",
        "flag": "radio_repaired",
        "log": "Channel 7 comes in like a person sitting down across from you.",
    },
    {
        "id": "mask",
        "name": "Filter Mask",
        "cost": {"scrap": 2},
        "give_item": "mask",
        "log": "You tape charcoal into a snout. You look like a plague doctor. Fitting.",
    },
    {
        "id": "molotov",
        "name": "Molotov",
        "cost": {"scrap": 1},
        "give_item": "molotov",
        "log": "Rag, bottle, a prayer you do not say out loud.",
    },
]

ENEMIES: Dict[str, Dict[str, Any]] = {
    "shambler": {"name": "Shambler", "hp": 16, "dmg": 7, "acc": 0.55, "armor": 0, "flee": 0.72, "infect": 0.12, "scene": "shambler"},
    "runner": {"name": "Runner", "hp": 12, "dmg": 11, "acc": 0.78, "armor": 0, "flee": 0.40, "infect": 0.20, "scene": "runner"},
    "bloater": {"name": "Bloater", "hp": 32, "dmg": 14, "acc": 0.50, "armor": 2, "flee": 0.18, "infect": 0.45, "scene": "bloater"},
    "armored": {"name": "Armored Dead", "hp": 28, "dmg": 13, "acc": 0.62, "armor": 5, "flee": 0.12, "infect": 0.10, "scene": "armored"},
    "butcher_fight": {"name": "The Butcher", "hp": 36, "dmg": 12, "acc": 0.70, "armor": 1, "flee": 0.08, "infect": 0.00, "scene": "butcher", "human": True},
}

WEATHERS = ["clear", "clear", "overcast", "rain", "rain", "fog", "storm"]

ENDINGS: Dict[str, Dict[str, str]] = {
    "died": {"title": "COLD FLOOR", "text": "You do not get a last thought worth writing down. The building keeps your heat for a few minutes, then forgets you."},
    "turned": {"title": "THE LISTENER", "text": "Infection writes the last page. You stand up wrong. Somewhere, a radio is still talking to a person who is no longer home."},
    "starved": {"title": "EMPTY CUPBOARD", "text": "The dead did not take you. The math did. Hunger is a quiet ending, and it does not apologize."},
    "breach": {"title": "THE DOOR GIVES", "text": "Fortification was a story you told the night. The night had notes. They come through the boards like water."},
    "halcyon": {"title": "HALCYON GATE", "text": "The wall is real. The soldiers are tired and human. They take your name, your fever, your people. For the first time in weeks, a door closes in your favor."},
    "false_sanctuary": {"title": "QUARANTINE FLAG", "text": "Halcyon takes you. Then it takes blood, then labor, then the parts of you that still argue. You were useful. That is not the same as saved."},
    "quiet_house": {"title": "THE QUIET HOUSE", "text": "You stop waiting for the world to come back. The garden takes. The radio is optional. You become a small country of one roof."},
    "last_light": {"title": "LAST LIGHT", "text": "Lena's treatment burns through you like honest fire. You live. She does not. The notes end in a sentence that is only your name."},
    "shepherd": {"title": "SHEPHERD", "text": "You walk them out: the kid, the living, the stubborn. Fort Halcyon counts heads. Someone small takes your hand like it is a road."},
    "hollow": {"title": "THE NEW BUTCHER", "text": "You kept what you could carry and spent the rest. The city learns your route. People cross the street even now, when streets are a rumor."},
    "sermon": {"title": "ASH AND AMEN", "text": "Miriam's god does not send a truck. It sends a kind of weather inside you. You tend the dead as if they can still hear the hymn."},
    "ghost_path": {"title": "UNDER THE CITY", "text": "You take Ghost's tunnels and do not come up. The trains are graves. The dark is a country with no census. You are finally hard to find."},
    "broadcast": {"title": "SIGNING OFF", "text": "Marcus puts you on Channel 7. Your voice becomes a rumor that keeps strangers alive one more night. You may not be one of them."},
    "docks_leave": {"title": "BLACK WATER", "text": "The boat is a joke that works. You leave the city like a guilty thought. Behind you, Channel 7 keeps promising a wall."},
}


def default_npcs() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for key, tpl in NPC_TEMPLATES.items():
        out[key] = {
            "id": key,
            "name": tpl["name"],
            "short": tpl["short"],
            "role": tpl["role"],
            "color": tpl["color"],
            "alive": True,
            "met": False,
            "at_base": False,
            "trust": 0,
        }
    return out


def ending_for(state) -> str:
    """Pick the most honest ending from flags, scores, and cause of death."""
    p, w = state.player, state.world
    flags = w.flags
    cause = flags.get("death_cause", "")

    if cause == "starved":
        return "starved"
    if cause == "breach":
        return "breach"
    if cause == "turned" or p.infection >= 100:
        return "turned"
    if cause == "dead" or p.health <= 0:
        return "died"

    party_n = sum(1 for n in w.npcs.values() if n.get("at_base") and n.get("alive"))
    kid_ok = w.npcs.get("kid", {}).get("at_base") and w.npcs.get("kid", {}).get("alive")

    if flags.get("chose_ghost_path"):
        return "ghost_path"
    if flags.get("chose_sermon"):
        return "sermon"
    if flags.get("chose_docks"):
        return "docks_leave"
    if flags.get("lena_sacrifice"):
        return "last_light"
    if flags.get("marcus_broadcast"):
        return "broadcast"
    if flags.get("extract_halcyon"):
        if p.humanity >= 45 and kid_ok and party_n >= 2:
            return "shepherd"
        if p.humanity < 30:
            return "false_sanctuary"
        return "halcyon"
    if p.humanity <= 18 and w.day >= 10:
        return "hollow"
    if w.day >= 18 and w.fortification >= 7:
        return "quiet_house"
    if w.day >= 14 and flags.get("radio_repaired") and p.humanity >= 40:
        return "halcyon"
    if w.day >= 16:
        return "quiet_house"
    return "died"


def apply_ending(state, ending_id: str, victory: bool) -> None:
    data = ENDINGS.get(ending_id, ENDINGS["died"])
    state.ending_id = ending_id
    state.ending_title = data["title"]
    state.ending_text = data["text"]
    state.game_over = True
    state.victory = victory
    state.mode = "ending"
    state.waiting_for_choice = False
    state.scene = "ending"
    state.confirm_label = "—"
    state.log.append(f"── {data['title']} ──")
    state.log.append(data["text"])
