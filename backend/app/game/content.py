"""
Apocalypse Terminal — World Content: Items, Weapons, Recipes, Locations, Map Nodes, NPCs, Enemies, Endings.
"""

from typing import Any, Dict, List

KID_NAMES = ["Eli", "Jun", "Rae", "Nico", "Sam", "Toby", "Maya", "Leo"]

WEAPONS: Dict[str, Dict[str, Any]] = {
    "fists": {"name": "Bare Hands", "dmg": 4, "ranged": False, "armor_pen": 0},
    "kitchen_knife": {"name": "Kitchen Cleaver", "dmg": 7, "ranged": False, "armor_pen": 0},
    "pipe": {"name": "Galvanized Pipe", "dmg": 9, "ranged": False, "armor_pen": 1},
    "crowbar": {"name": "Heavy Crowbar", "dmg": 13, "ranged": False, "armor_pen": 3},
    "fire_axe": {"name": "Emergency Fire Axe", "dmg": 17, "ranged": False, "armor_pen": 2},
    "spiked_bat": {"name": "Barbed Timber Bat", "dmg": 16, "ranged": False, "armor_pen": 1},
    "machete": {"name": "Honed Machete", "dmg": 20, "ranged": False, "armor_pen": 2},
    "pistol": {"name": "Service 9mm Pistol", "dmg": 22, "ranged": True, "armor_pen": 2},
    "shotgun": {"name": "Remington 12G Shotgun", "dmg": 34, "ranged": True, "armor_pen": 3},
    "rifle": {"name": "Hunting Rifle .308", "dmg": 42, "ranged": True, "armor_pen": 5},
}

ITEMS: Dict[str, Dict[str, str]] = {
    "kitchen_knife": {"name": "Kitchen Cleaver", "desc": "Heavy stainless steel. Taken from the Apartment 1204 kitchen block."},
    "pipe": {"name": "Galvanized Pipe", "desc": "Solid iron plumbing. Honest, blunt leverage."},
    "crowbar": {"name": "Heavy Crowbar", "desc": "Pries padlocks, pops elevator doors, cracks bone."},
    "fire_axe": {"name": "Emergency Fire Axe", "desc": "Pulled from the 12th-floor glass fire box. Heavy ash handle."},
    "spiked_bat": {"name": "Barbed Timber Bat", "desc": "Wood wrapped in barbed wire. Brutal deterrence."},
    "machete": {"name": "Honed Machete", "desc": "Clearing tool ground to a vicious razor edge."},
    "pistol": {"name": "Service 9mm Pistol", "desc": "Standard issue officer handgun. Reliable and compact."},
    "shotgun": {"name": "Remington 12G Shotgun", "desc": "Pump action with a 5-shell tube. Lethal at close range."},
    "rifle": {"name": "Hunting Rifle .308", "desc": "Bolt action with a 4x optic. Penetrates military body armor."},
    "flashlight": {"name": "LED Flashlight", "desc": "300 lumens. Rule 4: Never keep lit on shadows over 3 seconds."},
    "rule_sheet": {"name": "EAS Directive Notice", "desc": "Emergency Alert System instructions printed from the alert."},
    "radio_scanner": {"name": "Emergency Scanner", "desc": "Sean's handheld scanner. Picks up Channel 7 and military repeaters."},
    "mask": {"name": "Carbon Filter Mask", "desc": "Pleated charcoal respirator. Cuts infection progression by 50%."},
    "gas_mask": {"name": "Military M40 Mask", "desc": "Chemical canister mask. Cuts infection risk by 80%."},
    "radio_parts": {"name": "Transmitter Vacuum Tubes", "desc": "Tubes, crystal oscillator, and antenna wire."},
    "lena_notes": {"name": "Voss Laboratory Notes", "desc": "Formulas for a cellular pathogen inhibitor."},
    "voss_cure": {"name": "Synthesized Voss Vaccine", "desc": "Amber vial containing the only proven biological cure."},
    "holy_charm": {"name": "Sister Miriam's Cross", "desc": "Carved cedar charm. Calms trembling nerves and protects morale."},
    "tunnel_key": {"name": "Metro Transit Keycard", "desc": "Ghost's bypass card for locked subway maintenance gates."},
    "molotov": {"name": "Molotov Cocktail", "desc": "Bottled fuel and rag wick. Burns enemies and clears hallways."},
    "antibiotics": {"name": "Prescription Antibiotics", "desc": "Sealed capsules. Cleanses early scratches and reduces fever."},
    "herbal_poultice": {"name": "Herbal Poultice", "desc": "Crushed yarrow and willow bark. Relieves infection swelling."},
    "clean_gauze": {"name": "Sterile Field Bandage", "desc": "Compression trauma dressing. Restores 30 HP instantly."},
    "photo": {"name": "Classroom Photograph", "desc": "Smiles from a third-grade class before the sirens began."},
    "dog_treat": {"name": "Smoked Jerky Strips", "desc": "High-protein beef jerky. Won Scraps's eternal loyalty."},
    "halcyon_leaflet": {"name": "Fort Halcyon Leaflet", "desc": "SAFE ZONE MILE 18. GATES LOCKED AT MIDNIGHT."},
}

# ─────────────────────────────────────────────────────────────
# LOCATIONS & CITY MAP NODES
# ─────────────────────────────────────────────────────────────

LOCATIONS: Dict[str, Dict[str, Any]] = {
    "12th Floor Apartment": {
        "id": "apt12",
        "name": "12th Floor Apartment",
        "blurb": "Apartment 1204. High vantage safehouse overlooking the burning city.",
        "risk": 0.04,
        "loot": "none",
        "threat": "LOW",
        "icon": "🏢",
        "map_x": 45,
        "map_y": 42,
        "connections": ["12th Floor Corridor"],
    },
    "12th Floor Corridor": {
        "id": "hallway12",
        "name": "12th Floor Corridor",
        "blurb": "Buzzing fluorescent tubes, blood on wallpaper, doors 1201 through 1206.",
        "risk": 0.15,
        "loot": "mixed",
        "threat": "MED",
        "icon": "🚪",
        "map_x": 80,
        "map_y": 42,
        "connections": ["12th Floor Apartment", "Dark Stairwell"],
    },
    "Dark Stairwell": {
        "id": "stairwell",
        "name": "Dark Stairwell",
        "blurb": "12 flights of pitch-black concrete stairs. Emergency exit doors creak in the draft.",
        "risk": 0.28,
        "loot": "tools",
        "threat": "MED",
        "icon": "🪜",
        "map_x": 115,
        "map_y": 50,
        "connections": ["12th Floor Corridor", "Streets"],
    },
    "Home Base": {
        "id": "base",
        "name": "Home Base",
        "blurb": "Your fortified safehouse. Barricaded doors, cot, camp stove, and radio desk.",
        "risk": 0.05,
        "loot": "none",
        "threat": "SAFE",
        "icon": "🏠",
        "map_x": 45,
        "map_y": 42,
        "connections": ["12th Floor Corridor", "Streets"],
    },
    "Streets": {
        "id": "streets",
        "name": "Streets & Avenues",
        "blurb": "Abandoned car gridlock, flickering streetlamps, shamblers in alley shadows.",
        "risk": 0.25,
        "loot": "mixed",
        "threat": "MED",
        "icon": "🛣️",
        "map_x": 140,
        "map_y": 85,
        "connections": ["Home Base", "Dark Stairwell", "Abandoned Mall", "Hospital", "Church", "Subway Tunnels"],
    },
    "Abandoned Mall": {
        "id": "mall",
        "name": "St. Anne's Galleria Mall",
        "blurb": "Shattered glass atrium, department store food pantry, frenzied runners in clothing racks.",
        "risk": 0.38,
        "loot": "food",
        "threat": "HIGH",
        "icon": "🏬",
        "map_x": 205,
        "map_y": 60,
        "connections": ["Streets", "Gas Station", "School"],
    },
    "Hospital": {
        "id": "hospital",
        "name": "Central General Hospital",
        "blurb": "Biohazard isolation wing, overturned gurneys, pharmaceuticals, Dr. Lena Voss.",
        "risk": 0.46,
        "loot": "meds",
        "threat": "HIGH",
        "icon": "🏥",
        "map_x": 95,
        "map_y": 120,
        "connections": ["Streets", "Ruined Pharmacy", "Overgrown Park"],
    },
    "Radio Tower": {
        "id": "radio",
        "name": "Channel 7 Radio Tower",
        "blurb": "Steel needle antenna on the hill. Marcus Hale's emergency broadcast transmitter.",
        "risk": 0.32,
        "loot": "parts",
        "threat": "MED",
        "icon": "📻",
        "map_x": 260,
        "map_y": 35,
        "connections": ["Streets", "Warehouse", "Military Checkpoint"],
    },
    "Warehouse": {
        "id": "warehouse",
        "name": "Industrial Meat Warehouse",
        "blurb": "Freezer bays, overhead meat hooks, scrap iron, The Butcher's chalk-marked territory.",
        "risk": 0.44,
        "loot": "scrap",
        "threat": "SEVERE",
        "icon": "🏭",
        "map_x": 255,
        "map_y": 105,
        "connections": ["Radio Tower", "Streets", "Docks"],
    },
    "Church": {
        "id": "church",
        "name": "St. Jude's Ruined Church",
        "blurb": "Cracked stained glass, 80 flickering beeswax candles, Sister Miriam's sanctuary.",
        "risk": 0.18,
        "loot": "morale",
        "threat": "LOW",
        "icon": "⛪",
        "map_x": 150,
        "map_y": 135,
        "connections": ["Streets", "Subway Tunnels", "Overgrown Park"],
    },
    "Subway Tunnels": {
        "id": "subway",
        "name": "Subway Line 2 Tunnels",
        "blurb": "Flooded tracks, dead trains, absolute blackness, Ghost's hidden bypass route.",
        "risk": 0.50,
        "loot": "stealth",
        "threat": "SEVERE",
        "icon": "🚇",
        "map_x": 195,
        "map_y": 140,
        "connections": ["Streets", "Church", "Docks"],
    },
    "Military Checkpoint": {
        "id": "checkpoint",
        "name": "Military Checkpoint Mile 18",
        "blurb": "Razor wire coils, dead APC turret, armored dead soldiers, Fort Halcyon blast gate road.",
        "risk": 0.60,
        "loot": "ammo",
        "threat": "SEVERE",
        "icon": "🚧",
        "map_x": 290,
        "map_y": 80,
        "connections": ["Radio Tower", "Warehouse"],
    },
    "School": {
        "id": "school",
        "name": "Elementary School 14",
        "blurb": "Dusty chalkboards, tiny desks, overturned lockers where The Kid is hiding.",
        "risk": 0.28,
        "loot": "story",
        "threat": "LOW",
        "icon": "🏫",
        "map_x": 160,
        "map_y": 30,
        "connections": ["Abandoned Mall", "12th Floor Apartment"],
    },
    "Docks": {
        "id": "docks",
        "name": "Harbor Pier 4 Docks",
        "blurb": "Black ocean water, salt breeze, rotting pilings, moored diesel fishing trawler.",
        "risk": 0.36,
        "loot": "escape",
        "threat": "MED",
        "icon": "⚓",
        "map_x": 280,
        "map_y": 150,
        "connections": ["Warehouse", "Subway Tunnels"],
    },
    "Gas Station": {
        "id": "gas",
        "name": "Highway Gas Station",
        "blurb": "Overturned fuel tanker, smashed pumps, toxic bloater nest in the mechanic bay.",
        "risk": 0.35,
        "loot": "fuel",
        "threat": "HIGH",
        "icon": "⛽",
        "map_x": 240,
        "map_y": 70,
        "connections": ["Abandoned Mall", "Military Checkpoint"],
    },
    "Overgrown Park": {
        "id": "park",
        "name": "District Memorial Park",
        "blurb": "Reclaimed green meadows, wild yarrow, fresh water spring trickling into stone basin.",
        "risk": 0.20,
        "loot": "herbs",
        "threat": "LOW",
        "icon": "🌳",
        "map_x": 80,
        "map_y": 155,
        "connections": ["Hospital", "Church"],
    },
    "Ruined Pharmacy": {
        "id": "pharmacy",
        "name": "Metro Rx Pharmacy",
        "blurb": "Security grill smashed, prescription lockbox, looter standoffs, antibiotic caches.",
        "risk": 0.40,
        "loot": "meds",
        "threat": "MED",
        "icon": "💊",
        "map_x": 50,
        "map_y": 110,
        "connections": ["Hospital", "Streets"],
    },
}

NPC_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "maya": {
        "id": "maya",
        "name": "Maya Vance",
        "short": "Maya",
        "role": "Medical Resident (Apt 1206)",
        "color": "#ff79b0",
        "voice": "Resolute, steady-handed, armed with emergency triage skills and a fire axe from the 12th floor.",
    },
    "sean": {
        "id": "sean",
        "name": "Sean Miller",
        "short": "Sean",
        "role": "Radio Tech & Vet (Apt 1202)",
        "color": "#6ec8ff",
        "voice": "Pragmatic, observant, carries an emergency frequency scanner and knows how to pick commercial locks.",
    },
    "marcus": {
        "id": "marcus",
        "name": 'Marcus "Radio" Hale',
        "short": "Marcus",
        "role": "Channel 7 Broadcaster",
        "color": "#6ec8ff",
        "voice": "Speaks with late-night anchor authority. Knows Fort Halcyon's broadcasts are automated propaganda.",
    },
    "lena": {
        "id": "lena",
        "name": "Dr. Lena Voss",
        "short": "Lena",
        "role": "Infected Virologist",
        "color": "#9dffb0",
        "voice": "Clinical, sarcastic, running on caffeine and stubborn refusal to turn before formulating a vaccine.",
    },
    "kid": {
        "id": "kid",
        "name": "The Kid",
        "short": "Kid",
        "role": "Child Survivor",
        "color": "#ffe08a",
        "voice": "Carries bottlecaps and questions adults avoid. Your reminder of why surviving matters.",
    },
    "butcher": {
        "id": "butcher",
        "name": "The Butcher",
        "short": "Butcher",
        "role": "Predator Scavenger",
        "color": "#ff6b6b",
        "voice": "Smiles with too many teeth. Treats protein as the only real currency in the apocalypse.",
    },
    "miriam": {
        "id": "miriam",
        "name": "Sister Miriam",
        "short": "Miriam",
        "role": "Cathedral Believer",
        "color": "#d4b5ff",
        "voice": "Gentle steel. Has buried eighty parishioners and treats human kindness as an impenetrable armor.",
    },
    "ghost": {
        "id": "ghost",
        "name": "Ghost",
        "short": "Ghost",
        "role": "Subway Scout",
        "color": "#a0b4c8",
        "voice": "Mute runner. Communicates via chalk signs and rhythmic rail taps.",
    },
    "dog": {
        "id": "dog",
        "name": "Scraps",
        "short": "Scraps",
        "role": "Camp Terrier",
        "color": "#d4a373",
        "voice": "Scruffy wirehaired dog with one notched ear. Alert sentry who detects night intruders.",
    },
}

RECIPES: List[Dict[str, Any]] = [
    {
        "id": "barricade",
        "name": "Oak Door Barricade",
        "cost": {"scrap": 2},
        "fort": 1,
        "log": "You nail heavy cross-timbers across the entryway. Barricade level increased (+1).",
    },
    {
        "id": "heavy_barricade",
        "name": "Reinforced Steel Plate",
        "cost": {"scrap": 5},
        "fort": 2,
        "log": "Bolted steel grating over the window frame. Fortification holds strong against hordes (+2).",
    },
    {
        "id": "pipe",
        "name": "Galvanized Pipe Club",
        "cost": {"scrap": 2},
        "give_item": "pipe",
        "weapon": "pipe",
        "log": "Wrapped athletic tape around heavy plumbing iron. Reliable blunt weapon.",
    },
    {
        "id": "spiked_bat",
        "name": "Barbed Timber Bat",
        "cost": {"scrap": 3},
        "give_item": "spiked_bat",
        "weapon": "spiked_bat",
        "log": "Drove framing nails and wrapped rusted barbed wire around a solid timber bat.",
    },
    {
        "id": "machete",
        "name": "Honed Steel Machete",
        "cost": {"scrap": 4},
        "give_item": "machete",
        "weapon": "machete",
        "log": "Ground against whetstone into a razor-sharp street clearing blade.",
    },
    {
        "id": "rain",
        "name": "Gutter Rain Catcher",
        "cost": {"scrap": 3},
        "flag": "rain_catcher",
        "log": "Mounted collection drums under the rain gutter. Collects +2 water on rainy days.",
    },
    {
        "id": "garden",
        "name": "Window Planter Box",
        "cost": {"scrap": 2, "food": 1},
        "flag": "garden",
        "log": "Seeded root vegetables into nutrient soil boxes. 65% chance of daily fresh food.",
    },
    {
        "id": "alarm",
        "name": "Tripwire Tin Alarm",
        "cost": {"scrap": 2},
        "flag": "alarm",
        "log": "Strung mono-filament wire with bean cans along the corridor. Eliminates surprise night breaches.",
    },
    {
        "id": "medbay",
        "name": "Clean Trauma Station",
        "cost": {"scrap": 4, "medkits": 1},
        "flag": "medbay",
        "log": "Sterilized field tools, boiling water bath, and clean linens. Sleep heals +30 HP.",
    },
    {
        "id": "periscope",
        "name": "Rooftop Watch Periscope",
        "cost": {"scrap": 3},
        "flag": "periscope",
        "log": "Angled mirrors through the ventilation duct. Reveals city weather and movement.",
    },
    {
        "id": "radio",
        "name": "Channel 7 Booster Antenna",
        "cost": {"scrap": 2},
        "need_item": "radio_parts",
        "flag": "radio_repaired",
        "log": "Wired the amplifier tubes. Channel 7 broadcasts loud and clear across the room.",
    },
    {
        "id": "mask",
        "name": "Carbon Filter Mask",
        "cost": {"scrap": 2},
        "give_item": "mask",
        "log": "Improvised carbon filter mask. Cuts infection tick rate by 50%.",
    },
    {
        "id": "molotov",
        "name": "Molotov Cocktail",
        "cost": {"scrap": 1, "ammo": 1},
        "give_item": "molotov",
        "log": "Fuel bottle with kerosene-soaked cloth wick. Deals 26+ area fire damage.",
    },
    {
        "id": "bandage",
        "name": "Boiled Linen Bandages",
        "cost": {"scrap": 2, "water": 1},
        "give_res": {"medkits": 1},
        "log": "Sterilized cloth packaged into an emergency medical kit (+1 Kit).",
    },
    {
        "id": "scrap_ammo",
        "name": "Handloaded Cartridges",
        "cost": {"scrap": 3},
        "give_res": {"ammo": 4},
        "log": "Repacked lead pellets into spent brass casings (+4 Ammo).",
    },
]

ENEMIES: Dict[str, Dict[str, Any]] = {
    "shambler": {
        "name": "Rotting Shambler",
        "hp": 18,
        "dmg": 7,
        "acc": 0.55,
        "armor": 0,
        "flee": 0.72,
        "infect": 0.15,
        "scene": "shambler",
        "intent": "Lurching forward, jaw slack and reaching with decayed fingers.",
        "loot": {"scrap": 1},
    },
    "runner": {
        "name": "Frenzied Runner",
        "hp": 14,
        "dmg": 12,
        "acc": 0.82,
        "armor": 0,
        "flee": 0.40,
        "infect": 0.24,
        "scene": "runner",
        "intent": "Crouching low on the tiles, twitching with coiled leaping speed!",
        "loot": {"food": 1},
    },
    "bloater": {
        "name": "Toxic Bloater",
        "hp": 36,
        "dmg": 15,
        "acc": 0.50,
        "armor": 2,
        "flee": 0.20,
        "infect": 0.45,
        "scene": "bloater",
        "intent": "Abdomen pulsing violently with pressurized acidic bile!",
        "loot": {"scrap": 2, "water": 1},
    },
    "armored": {
        "name": "Armored Dead Soldier",
        "hp": 32,
        "dmg": 14,
        "acc": 0.65,
        "armor": 5,
        "flee": 0.15,
        "infect": 0.10,
        "scene": "armored",
        "intent": "Marching heavy footsteps behind a cracked polycarbonate riot shield.",
        "loot": {"ammo": 3, "scrap": 2},
    },
    "stalker": {
        "name": "Night Corridor Stalker",
        "hp": 22,
        "dmg": 16,
        "acc": 0.78,
        "armor": 1,
        "flee": 0.28,
        "infect": 0.30,
        "scene": "shambler",
        "intent": "Crawling upside-down along the ceiling pipes to strike from behind.",
        "loot": {"medkits": 1},
    },
    "butcher_fight": {
        "name": "The Butcher",
        "hp": 50,
        "dmg": 16,
        "acc": 0.75,
        "armor": 2,
        "flee": 0.10,
        "infect": 0.00,
        "scene": "butcher",
        "human": True,
        "intent": "Grinning wide, testing the balance of his 18-inch meat cleaver.",
        "loot": {"food": 4, "scrap": 4, "medkits": 2},
    },
    "scavenger_raider": {
        "name": "Desperate Looter",
        "hp": 24,
        "dmg": 10,
        "acc": 0.70,
        "armor": 1,
        "flee": 0.50,
        "infect": 0.00,
        "scene": "streets",
        "human": True,
        "intent": "Hands trembling as he levels a pipe shotgun at your chest.",
        "loot": {"ammo": 2, "food": 1},
    },
}

WEATHERS = ["clear", "clear", "overcast", "rain", "rain", "fog", "storm"]

ENDINGS: Dict[str, Dict[str, str]] = {
    "died": {
        "title": "COLD FLOOR",
        "text": "Your breath fogs the linoleum one last time before thinning into cold stillness. The boarded room keeps your warmth for twenty minutes, then forgets you were ever here.",
    },
    "turned": {
        "title": "THE LISTENER",
        "text": "The fever takes the wheel. Black veins swallow your sight, replaced by a strange, magnetic hunger. You rise into the hallway, your hands no longer your own, joining the great restless chorus of the city.",
    },
    "starved": {
        "title": "EMPTY CUPBOARD",
        "text": "The dead never breached your door. The arithmetic of empty tins did. Hunger is a quiet executioner that never raises its voice. The quiet room outlives your stomach.",
    },
    "breach": {
        "title": "THE DOOR GIVES",
        "text": "The timber screams before it splinters. Rotting fingers find the seams, dragging down the crossbeams like autumn leaves. When the night enters, it does not leave a corner untouched.",
    },
    "halcyon": {
        "title": "HALCYON GATE",
        "text": "The searchlights blaze through the perimeter fog. Weary soldiers in gray fatigues keep rifles lowered. Your name is written in an intake log. For the first time in a hundred miles, a heavy steel door closes in your favor.",
    },
    "false_sanctuary": {
        "title": "QUARANTINE FLAG",
        "text": "Fort Halcyon took your weapons at the gate, then your blood in the triage tent, then your labor in the furnace trenches. The broadcasts were true about the walls; they merely forgot to mention which side of the cage was yours.",
    },
    "quiet_house": {
        "title": "THE QUIET HOUSE",
        "text": "You stopped waiting for the old world to sign a peace treaty. The rain catchers are full, the window planters are green, and the barricades hold fast against the seasons. You have built a sovereign nation under a single roof.",
    },
    "last_light": {
        "title": "LAST LIGHT",
        "text": "Dr. Voss's synthesized cure burns through your blood like white fire, scorching out the parasite cell by cell. Lena's final breath was spent sealing the ampoule. Her handwritten notes end with a single word: live.",
    },
    "shepherd": {
        "title": "THE SHEPHERD",
        "text": "You delivered them through the burning ruins: the kid, the wounded, the faithful. Behind Fort Halcyon's blast barriers, a small warm hand squeezes yours tight. In a world of wolves, you kept your people human.",
    },
    "hollow": {
        "title": "THE NEW BUTCHER",
        "text": "You survived because you traded everything that made you soft. Scavengers know the rhythm of your boots; raiders look away when you walk the street. You conquered the wasteland by becoming its most ruthless monster.",
    },
    "sermon": {
        "title": "ASH AND AMEN",
        "text": "Miriam's chapel never saw an extraction chopper, but it saw grace. You tend the candle flames and comfort the dying as if every soul still matters to the sky. In the center of devastation, you built holy ground.",
    },
    "ghost_path": {
        "title": "UNDER THE CITY",
        "text": "You followed Ghost into the deep abandoned subway tunnels beyond the reach of daylight and hordes. In the subterranean machine rooms, a hidden commune breathes in safety. You have stepped off the surface map forever.",
    },
    "broadcast": {
        "title": "SIGNING OFF",
        "text": "Marcus Hale hands you the microphone on Channel 7. Across five counties, hidden survivors in basements and attics listen to your voice describe routes, water caches, and hope. The city may fall, but its signal never died.",
    },
    "docks_leave": {
        "title": "BLACK WATER",
        "text": "The diesel engine turns over with a chattering roar. The wooden trawler cuts across the black harbor into the open ocean, leaving the smoking skyline behind. Whatever waits across the water, the dead cannot swim.",
    },
    "pack_leader": {
        "title": "FOUR-LEGGED DAWN",
        "text": "With Scraps trotting loyally at your heel, you survived the worst the ruins could muster. Man and dog, curled together beside a glowing brazier, watching the sun rise clean over the rooftops.",
    },
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
            "health": 100,
        }
    return out


def ending_for(state) -> str:
    """Pick the most narratively earned ending based on flags, humanity, companion status, and survival days."""
    p, w = state.player, state.world
    flags = w.flags
    cause = flags.get("death_cause", "")

    # Fatalities
    if cause == "starved":
        return "starved"
    if cause == "breach":
        return "breach"
    if cause == "turned" or p.infection >= 100:
        return "turned"
    if cause == "dead" or p.health <= 0:
        return "died"

    party_n = sum(1 for n in w.npcs.values() if n.get("at_base") and n.get("alive"))
    kid_ok = bool(w.npcs.get("kid", {}).get("at_base") and w.npcs.get("kid", {}).get("alive"))

    # Player-chosen narrative conclusions
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
        if p.humanity >= 55 and kid_ok and party_n >= 2:
            return "shepherd"
        if p.humanity < 30:
            return "false_sanctuary"
        return "halcyon"

    # Emergent state-based endings
    if p.humanity <= 18 and w.day >= 8:
        return "hollow"
    if w.flags.get("has_dog") and w.day >= 15 and p.morale >= 60 and party_n <= 1:
        return "pack_leader"
    if w.day >= 18 and w.fortification >= 7 and flags.get("garden") and flags.get("rain_catcher"):
        return "quiet_house"
    if w.day >= 14 and flags.get("radio_repaired") and p.humanity >= 45:
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
