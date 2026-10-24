"""
Apocalypse Terminal — World Content: Items, Weapons, Recipes, Locations, NPCs, Enemies, Endings.
"""

from typing import Any, Dict, List

KID_NAMES = ["Eli", "Jun", "Rae", "Nico", "Sam", "Toby", "Maya", "Leo"]

WEAPONS: Dict[str, Dict[str, Any]] = {
    "fists": {"name": "Bare Hands", "dmg": 4, "ranged": False, "armor_pen": 0},
    "pipe": {"name": "Pipe Club", "dmg": 9, "ranged": False, "armor_pen": 1},
    "crowbar": {"name": "Heavy Crowbar", "dmg": 13, "ranged": False, "armor_pen": 3},
    "spiked_bat": {"name": "Spiked Bat", "dmg": 16, "ranged": False, "armor_pen": 1},
    "machete": {"name": "Rusted Machete", "dmg": 20, "ranged": False, "armor_pen": 2},
    "pistol": {"name": "Police 9mm", "dmg": 22, "ranged": True, "armor_pen": 2},
    "shotgun": {"name": "Remington 12G", "dmg": 34, "ranged": True, "armor_pen": 3},
    "rifle": {"name": "Hunting Rifle", "dmg": 40, "ranged": True, "armor_pen": 5},
    "spear": {"name": "Rebar Spear", "dmg": 14, "ranged": False, "armor_pen": 2},
}

ITEMS: Dict[str, Dict[str, str]] = {
    "pipe": {"name": "Pipe Club", "desc": "Solid galvanized iron. Heavy, crude, honest."},
    "crowbar": {"name": "Heavy Crowbar", "desc": "Opens stubborn crates and cracks helmets."},
    "spiked_bat": {"name": "Spiked Bat", "desc": "Ash wood wrapped in rusty barbed wire."},
    "machete": {"name": "Rusted Machete", "desc": "Vegetation clearing tool turned street equalizer."},
    "pistol": {"name": "Police 9mm", "desc": "Standard issue service handgun. Cold, compact comfort."},
    "shotgun": {"name": "Remington 12G", "desc": "Pump-action room cleaner. Devastating up close."},
    "rifle": {"name": "Hunting Rifle", "desc": "Bolt-action .308 with a cracked scope. High stopping power."},
    "spear": {"name": "Rebar Spear", "desc": "Eight feet of rebar hammered to a point and lashed to a shovel handle. Keep them at reach."},
    "mask": {"name": "Filter Mask", "desc": "Improvised carbon filter. Cuts airborne spores and bite infection risk in half."},
    "gas_mask": {"name": "Military Gas Mask", "desc": "PBF canister respirator. Maximum protection against toxic bloater bile."},
    "radio_parts": {"name": "Radio Parts", "desc": "Vacuum tubes, solder, copper wire, and a quartz crystal."},
    "lena_notes": {"name": "Voss Research Notes", "desc": "Formulas for a cellular inhibitor. Half science, half prayer."},
    "voss_cure": {"name": "Voss Synthesized Serum", "desc": "A glowing amber vial. Dr. Voss's final, perfect answer to the pathogen."},
    "holy_charm": {"name": "Wooden Cross Charm", "desc": "Sister Miriam's carved cedar talisman. Grants moral fortitude."},
    "tunnel_key": {"name": "Subway Transit Key", "desc": "Ghost's master keycard to the locked maintenance concourses."},
    "molotov": {"name": "Molotov Cocktail", "desc": "Gasoline, rag, and match. A bright, screaming miracle in a dark alley."},
    "antibiotics": {"name": "Pharmaceutical Antibiotics", "desc": "Sealed amoxicillin capsules. Cures early infections and reduces fever."},
    "herbal_poultice": {"name": "Herbal Poultice", "desc": "Crushed yarrow and willow bark. Slows bacterial rot and cleanses scratches."},
    "clean_gauze": {"name": "Sterile Field Bandage", "desc": "Military-grade compression dressing. Stops bleeding instantly."},
    "photo": {"name": "Classroom Photograph", "desc": "Third graders smiling in front of chalk drawings. A world that was."},
    "dog_treat": {"name": "Tin of Jerky", "desc": "Smells like hickory smoke. Guaranteed to win four-legged loyalty."},
    "halcyon_leaflet": {"name": "Halcyon Evacuation Leaflet", "desc": "FORT HALCYON SAFE ZONE. GATE MILE 18. BRING THE LIVING."},
    "wire_cutters": {"name": "Heavy Wire Cutters", "desc": "Cuts through razor wire and chained padlocks."},
}

LOCATIONS: Dict[str, Dict[str, Any]] = {
    "Home Base": {
        "id": "base",
        "risk": 0.05,
        "loot": "none",
        "blurb": "Plywood on windows, a deadbolt that still catches, and tea on a camp stove.",
    },
    "Streets": {
        "id": "streets",
        "risk": 0.25,
        "loot": "mixed",
        "blurb": "Vehicles frozen bumper to bumper. Asphalt slick with grease and old rain.",
    },
    "Abandoned Mall": {
        "id": "mall",
        "risk": 0.38,
        "loot": "food",
        "blurb": "A dead temple of commerce. Mannequins pose in the dark like petrified witnesses.",
    },
    "Hospital": {
        "id": "hospital",
        "risk": 0.46,
        "loot": "meds",
        "blurb": "Gurneys overturned in triage. The sweet, chemical scent of decay and formaldehyde.",
    },
    "Radio Tower": {
        "id": "radio",
        "risk": 0.32,
        "loot": "parts",
        "blurb": "A steel needle piercing the overcast ceiling. Channel 7 still hums on emergency batteries.",
    },
    "Warehouse": {
        "id": "warehouse",
        "risk": 0.42,
        "loot": "scrap",
        "blurb": "Corrugated iron bays and forklift ramps. The Butcher's chalk warnings on the roll-up door.",
    },
    "Church": {
        "id": "church",
        "risk": 0.20,
        "loot": "morale",
        "blurb": "Stained glass depicting saints in dust. Wax nubs flicker quietly in the nave.",
    },
    "Subway Tunnels": {
        "id": "subway",
        "risk": 0.52,
        "loot": "stealth",
        "blurb": "Pitch blackness that presses against your eyelids. Train cars resting like iron carcasses.",
    },
    "Military Checkpoint": {
        "id": "checkpoint",
        "risk": 0.58,
        "loot": "ammo",
        "blurb": "Sandbag bunkers, concertina wire, and a burned-out APC pointing its turret at the city.",
    },
    "School": {
        "id": "school",
        "risk": 0.28,
        "loot": "story",
        "blurb": "Tiny desks lined in silence. Hopscotch chalk faded on the asphalt playground.",
    },
    "Docks": {
        "id": "docks",
        "risk": 0.36,
        "loot": "escape",
        "blurb": "Black brackish harbor water lapping against rotting piers. An old diesel trawler rides the tide.",
    },
    "Gas Station": {
        "id": "gas",
        "risk": 0.35,
        "loot": "fuel",
        "blurb": "Pumps frozen at $0.00. Smashed glass and the lingering stench of bloated rot.",
    },
    "Overgrown Park": {
        "id": "park",
        "risk": 0.22,
        "loot": "herbs",
        "blurb": "Weeds reclaiming the carousel. A natural spring trickles into a cracked stone basin.",
    },
    "Ruined Pharmacy": {
        "id": "pharmacy",
        "risk": 0.40,
        "loot": "meds",
        "blurb": "Shattered display racks. Behind the security cage, amber pill bottles line the floor.",
    },
}

NPC_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "marcus": {
        "id": "marcus",
        "name": 'Marcus "Radio" Hale',
        "short": "Marcus",
        "role": "Broadcaster",
        "color": "#6ec8ff",
        "voice": "He leaves an anchor's pause before each phrase, waiting for an on-air cue that never comes.",
    },
    "lena": {
        "id": "lena",
        "name": "Dr. Lena Voss",
        "short": "Lena",
        "role": "Scientist",
        "color": "#9dffb0",
        "voice": "Clinical, acerbic, running on caffeine and pure stubborn refusal to turn without finishing her notes.",
    },
    "kid": {
        "id": "kid",
        "name": "The Kid",
        "short": "Kid",
        "role": "Child",
        "color": "#ffe08a",
        "voice": "Observant, clutching a scavenged toy, asking questions adults have spent weeks avoiding.",
    },
    "butcher": {
        "id": "butcher",
        "name": "The Butcher",
        "short": "Butcher",
        "role": "Scavenger",
        "color": "#ff6b6b",
        "voice": "Smiles with too many teeth. Speaks with the calm cheer of a man who knows meat is a market.",
    },
    "miriam": {
        "id": "miriam",
        "name": "Sister Miriam",
        "short": "Miriam",
        "role": "Believer",
        "color": "#d4b5ff",
        "voice": "Soft-spoken steel. She has buried a parish of eighty people and still refuses to yield to cruelty.",
    },
    "ghost": {
        "id": "ghost",
        "name": "Ghost",
        "short": "Ghost",
        "role": "Tunnel Scout",
        "color": "#a0b4c8",
        "voice": "Speaks only through double taps, sketched chalk arrows, and the quiet rustle of cloth in the dark.",
    },
    "dog": {
        "id": "dog",
        "name": "Scraps",
        "short": "Scraps",
        "role": "Camp Dog",
        "color": "#d4a373",
        "voice": "A scruffy wirehaired terrier with one bent ear and an unshakeable sense of perimeter duty.",
    },
}

RECIPES: List[Dict[str, Any]] = [
    {
        "id": "barricade",
        "name": "Barricade Boarding",
        "cost": {"scrap": 2},
        "fort": 1,
        "log": "You nail fresh studs across the entryway. The door feels more like a fortress.",
    },
    {
        "id": "heavy_barricade",
        "name": "Reinforced Steel Gate",
        "cost": {"scrap": 5},
        "fort": 2,
        "log": "Angle iron, carriage bolts, and crossbeams. Even a bloater would hesitate here.",
    },
    {
        "id": "pipe",
        "name": "Pipe Club",
        "cost": {"scrap": 2},
        "give_item": "pipe",
        "weapon": "pipe",
        "log": "You tape athletic grip around a heavy iron pipe. Honest, blunt leverage.",
    },
    {
        "id": "spiked_bat",
        "name": "Spiked Bat",
        "cost": {"scrap": 3},
        "give_item": "spiked_bat",
        "weapon": "spiked_bat",
        "log": "Driven nails and wrapped barbed wire around a solid timber club.",
    },
    {
        "id": "machete",
        "name": "Honed Machete",
        "cost": {"scrap": 4},
        "give_item": "machete",
        "weapon": "machete",
        "log": "Ground against whetstone until the rust peels away to a razor edge.",
    },
    {
        "id": "rain",
        "name": "Gutter Rain Catcher",
        "cost": {"scrap": 3},
        "flag": "rain_catcher",
        "log": "Plastic sheeting, funnels, and clean drums. Rain will replenish drinking water.",
    },
    {
        "id": "garden",
        "name": "Planter Soil Box",
        "cost": {"scrap": 2, "food": 1},
        "flag": "garden",
        "log": "You seed hardy root vegetables in window boxes. An investment in tomorrow.",
    },
    {
        "id": "alarm",
        "name": "Tripwire Tin Alarm",
        "cost": {"scrap": 2},
        "flag": "alarm",
        "log": "Taut mono-filament wire and dry bean tins hung along the outer corridor.",
    },
    {
        "id": "medbay",
        "name": "Clean Med Station",
        "cost": {"scrap": 4, "medkits": 1},
        "flag": "medbay",
        "log": "Sterilized tweezers, boiling water bath, and clean linen strips. Rest heals faster.",
    },
    {
        "id": "periscope",
        "name": "Rooftop Watch Periscope",
        "cost": {"scrap": 3},
        "flag": "periscope",
        "log": "Mirrors and conduit mounted through the flue. Reveals weather and street movements.",
    },
    {
        "id": "radio",
        "name": "Channel 7 Booster",
        "cost": {"scrap": 2},
        "need_item": "radio_parts",
        "flag": "radio_repaired",
        "log": "Amplifier wired, antenna extended. Marcus's broadcast comes in crisp and clear.",
    },
    {
        "id": "mask",
        "name": "Filter Mask",
        "cost": {"scrap": 2},
        "give_item": "mask",
        "log": "Activated charcoal packed into a pleated cloth mask. Cuts infection spread.",
    },
    {
        "id": "molotov",
        "name": "Molotov Cocktail",
        "cost": {"scrap": 1, "ammo": 1},
        "give_item": "molotov",
        "log": "High-proof spirit and kerosene in a bottle with a dry rag wick.",
    },
    {
        "id": "bandage",
        "name": "Improvised Medkit",
        "cost": {"scrap": 2, "water": 1},
        "give_res": {"medkits": 1},
        "log": "Boiled linen bandages and antiseptic wash packaged into a pocket kit.",
    },
    {
        "id": "scrap_ammo",
        "name": "Scrap Handloads",
        "cost": {"scrap": 3},
        "give_res": {"ammo": 4},
        "log": "Repacked lead shot into spent brass casings. Smoky, but they shoot.",
    },
    {
        "id": "spear",
        "name": "Rebar Spear",
        "cost": {"scrap": 3},
        "give_item": "spear",
        "weapon": "spear",
        "log": "Rebar sharpened on curb stone and lashed to a shovel handle. Reach beats courage.",
    },
    {
        "id": "snare",
        "name": "Tripwire Snare Line",
        "cost": {"scrap": 2},
        "flag": "snare",
        "log": "Barbed snares strung across the stairwell. Things that climb will regret it.",
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
        "intent": "Lurching slowly with decaying jaws agape.",
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
        "intent": "Crouching low on asphalt, ready to pounce!",
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
        "intent": "Abdomen swelling with pressurized corrosive bile!",
        "loot": {"scrap": 2, "water": 1},
    },
    "armored": {
        "name": "Armored Dead",
        "hp": 32,
        "dmg": 14,
        "acc": 0.65,
        "armor": 5,
        "flee": 0.15,
        "infect": 0.10,
        "scene": "armored",
        "intent": "Stomping forward behind a cracked plexiglass riot shield.",
        "loot": {"ammo": 3, "scrap": 2},
    },
    "stalker": {
        "name": "Night Stalker",
        "hp": 22,
        "dmg": 16,
        "acc": 0.78,
        "armor": 1,
        "flee": 0.28,
        "infect": 0.30,
        "scene": "shambler",
        "intent": "Slithering between broken cars to flank from darkness.",
        "loot": {"medkits": 1},
    },
    "butcher_fight": {
        "name": "The Butcher",
        "hp": 48,
        "dmg": 15,
        "acc": 0.75,
        "armor": 2,
        "flee": 0.10,
        "infect": 0.00,
        "scene": "butcher",
        "human": True,
        "intent": "Grinning wide, testing the balance of an industrial meat cleaver.",
        "loot": {"food": 4, "scrap": 4, "medkits": 2},
    },
    "scavenger_raider": {
        "name": "Desperate Raider",
        "hp": 24,
        "dmg": 10,
        "acc": 0.70,
        "armor": 1,
        "flee": 0.50,
        "infect": 0.00,
        "scene": "streets",
        "human": True,
        "intent": "Shaking hands leveling a rusty pipe shotgun.",
        "loot": {"ammo": 2, "food": 1},
    },
}

# ─────────────────────────────────────────────────────────────
# EXPANDED CITY LOCATIONS (map expansion pass)
# ─────────────────────────────────────────────────────────────

EXPANDED_LOCATIONS: Dict[str, Dict[str, Any]] = {
    "Fire Station": {
        "id": "firestation",
        "risk": 0.38,
        "loot": "tools",
        "blurb": "Engine company blackened by fire. Hook ladders hang like frozen vines from the truck bay.",
    },
    "City Prison": {
        "id": "prison",
        "risk": 0.60,
        "loot": "contraband",
        "blurb": "Sally port gates hanging open. Cellblock echoes carry sounds that are not footsteps.",
    },
    "Bus Depot": {
        "id": "busdepot",
        "risk": 0.34,
        "loot": "fuel",
        "blurb": "Rows of diesel buses sleeping in their numbered lanes. The fuel farm still ticks as it cools.",
    },
    "Waterworks": {
        "id": "waterworks",
        "risk": 0.44,
        "loot": "water",
        "blurb": "The municipal pumping station churns on backup power, pushing clean water through a dead city.",
    },
    "Overpass Camp": {
        "id": "overpass",
        "risk": 0.30,
        "loot": "story",
        "blurb": "A shantytown of tarps and shopping carts wedged beneath the elevated freeway, quiet as a held breath.",
    },
    "Memorial Stadium": {
        "id": "stadium",
        "risk": 0.55,
        "loot": "cache",
        "blurb": "Fifty thousand empty seats surrounding a field of FEMA tents. The scoreboard still flashes RED.",
    },
}

LOCATIONS.update(EXPANDED_LOCATIONS)

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


# ─────────────────────────────────────────────────────────────
# SCENARIOS — selectable starting stories (chosen with buttons 1-4 on a new run)
# ─────────────────────────────────────────────────────────────

SCENARIOS: Dict[str, Dict[str, Any]] = {
    "apartment": {
        "name": "THE BOARDER",
        "tag": "Classic survival — balanced start",
        "player": {},
        "fort": 1,
        "known": [],
        "weapon": None,
        "inventory": [],
        "log": [
            "You awaken behind reinforced plywood in the boarded apartment.",
            "Outside, the city hums with rain, rust, and the relentless dead.",
        ],
    },
    "nomad": {
        "name": "THE NOMAD",
        "tag": "Light & fast — you just rolled in on a stolen bike",
        "player": {"food": 7, "water": 7, "ammo": 8, "scrap": 4, "morale": 60, "humanity": 45},
        "fort": 0,
        "known": ["Gas Station", "Bus Depot", "Overpass Camp", "Overgrown Park"],
        "weapon": "pipe",
        "inventory": ["pipe"],
        "log": [
            "The bike died on the overpass an hour ago. You dragged its scrap uphill and sold it twice.",
            "This city is new to you — every street is a rumor, every door a coin flip.",
        ],
    },
    "medic": {
        "name": "THE FIELD MEDIC",
        "tag": "Walk in already infected — medicine is your currency",
        "player": {"infection": 18, "medkits": 3, "morale": 65, "humanity": 62, "food": 4, "water": 4, "ammo": 4},
        "fort": 1,
        "known": ["Hospital", "Ruined Pharmacy", "Overgrown Park"],
        "weapon": None,
        "inventory": ["antibiotics", "clean_gauze"],
        "log": [
            "You pulled three strangers from triage before the generators died. Two stayed dead.",
            "A field dressing holds the bite on your forearm. For now, the fever is only a rumor.",
        ],
    },
    "soldier": {
        "name": "THE DESERTER",
        "tag": "Gun & guilt — firepower at the cost of your soul",
        "player": {"ammo": 14, "morale": 55, "humanity": 32, "food": 3, "water": 3, "scrap": 4, "medkits": 1},
        "fort": 2,
        "known": ["Military Checkpoint", "City Prison", "Fire Station", "Streets"],
        "weapon": "pistol",
        "inventory": ["pistol"],
        "log": [
            "You walked away from the checkpoint the night the order came to fire on civilians.",
            "The service pistol has one magazine left, and you have one question left to answer.",
        ],
    },
}

SCENARIO_ORDER = ["apartment", "nomad", "medic", "soldier"]


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
