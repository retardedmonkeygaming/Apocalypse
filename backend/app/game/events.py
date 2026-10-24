"""
Apocalypse Terminal — Encounter & Story Event Catalog.
Rich atmospheric encounters with branching consequences, multi-stage companion arcs,
and dynamic location/weather hooks.
"""

import copy
import random
from typing import Any, Dict, List, Optional

_EVENT_KEYS = set()


def _e(
    eid: str,
    title: str,
    text: str,
    choices: List[Dict],
    **meta,
) -> Dict[str, Any]:
    ev = {
        "id": eid,
        "title": title,
        "text": text,
        "choices": choices,
        "scene": "streets",
        "locations": None,
        "night": None,
        "min_day": 1,
        "max_day": 99,
        "require_flags": {},
        "forbid_flags": {},
        "unique": False,
        "story": False,
        "weight": 1,
    }
    ev.update(meta)
    ev["id"] = eid
    ev["title"] = title
    ev["text"] = text
    ev["choices"] = choices
    return ev


def _c(label: str, key: str, **effect) -> Dict[str, Any]:
    eff: Dict[str, Any] = {}
    for k, v in effect.items():
        if k == "effect":
            eff.update(v)
        else:
            eff[k] = v
    return {"label": label, "key": key, "effect": eff}


def _apply_kid(state, text: str) -> str:
    return text.replace("{kid}", state.kid_name)


# ─────────────────────────────────────────────────────────────
# STORY BEATS & CHARACTER ARCS
# ─────────────────────────────────────────────────────────────

EVENTS: List[Dict[str, Any]] = [
    # ── MARCUS / CHANNEL 7 ──
    _e(
        "radio_static",
        "CHANNEL 7 BROADCAST",
        "The transistor on your shelf hums with static before crackling into life. "
        "A baritone voice speaks with the rhythm of late-night AM radio: "
        "'This is Marcus Hale on Channel 7. If you hear this, Fort Halcyon still stands at Mile 18. "
        "Water, intake barracks, medical quarantine. Bring the living.'",
        [
            _c("Listen quietly", "red", morale=8, flags={"heard_halcyon": True, "met_marcus_voice": True}, gemini=True),
            _c("Speak into mic", "blue", morale=4, humanity=2, flags={"heard_halcyon": True, "answered_radio": True}, gemini=True),
            _c("Kill volume", "green", morale=-3, log="You shut off the noise. Hope is expensive."),
            _c("Map Radio Tower", "yellow", discover="Radio Tower", flags={"heard_halcyon": True}, log="You mark the broadcast tower coordinates."),
        ],
        scene="radio",
        unique=True,
        story=True,
        locations=["Home Base", "Streets"],
    ),
    _e(
        "marcus_tower",
        "THE TOWER TRANSMITTER",
        "Marcus Hale sits among glowing vacuum tubes and battery banks on the tower observation deck. "
        "A tin of cold coffee rests beside a microphone. He looks you over like a sound check: "
        "'You look like you're still walking under your own power. Rare sight in this zip code.'",
        [
            _c("Invite to base", "red", scrap=-1, humanity=8, npc_join="marcus", flags={"met_marcus": True}, gemini=True),
            _c("Question Halcyon", "blue", morale=6, flags={"met_marcus": True, "heard_halcyon": True}, gemini=True),
            _c("Scavenge his parts", "green", add_item="radio_parts", humanity=-6, flags={"met_marcus": True}),
            _c("Leave him be", "yellow", flags={"met_marcus": True}, log="You leave Marcus to his frequency."),
        ],
        scene="marcus",
        unique=True,
        story=True,
        locations=["Radio Tower"],
        require_flags={"heard_halcyon": True},
        min_day=2,
    ),
    _e(
        "marcus_truth",
        "CONFESSION ON CHANNEL 7",
        "Marcus stares out across the skyline, his voice dropping below the microphone pickup: "
        "'Halcyon isn't an evacuation sanctuary. It was an armed containment compound. "
        "The military locked the gates three weeks ago. The automated tapes kept playing because people riot less when they believe there's a bus coming.'",
        [
            _c("Take the truth", "red", morale=-4, humanity=4, flags={"knows_halcyon_truth": True}, gemini=True),
            _c("Broadcast truth", "blue", humanity=10, morale=6, flags={"knows_halcyon_truth": True, "broadcast_truth": True}, gemini=True),
            _c("Keep the illusion", "green", morale=4, humanity=-4, flags={"knows_halcyon_truth": True, "protect_lie": True}),
            _c("Ask for extraction", "yellow", flags={"knows_halcyon_truth": True, "halcyon_contact": True}),
        ],
        scene="marcus",
        unique=True,
        story=True,
        require_flags={"met_marcus": True},
        require_npc="marcus",
        min_day=5,
    ),

    # ── DR. LENA VOSS ──
    _e(
        "lena_hospital",
        "QUARANTINE OBSERVATION",
        "Behind reinforced safety glass in the Hospital ICU, a woman in a stained lab coat monitors a centrifuge. "
        "A bandage covers her forearm. Her eyes are fever-bright, but her hands are rock steady. "
        "'I am Dr. Lena Voss,' she calls through the speaker. 'The rot is in my lymphatic system, but my mind is intact. Help me break this seal, and I can keep you alive.'",
        [
            _c("Pry the door open", "red", scrap=-1, humanity=6, npc_join="lena", add_item="lena_notes", flags={"met_lena": True}, gemini=True),
            _c("Demand medicine first", "blue", medkits=2, humanity=-2, npc_join="lena", flags={"met_lena": True}),
            _c("Shoot through glass", "green", humanity=-12, combat="shambler", flags={"lena_dead": True}),
            _c("Back away slowly", "yellow", morale=-2, log="You leave the quarantine room sealed."),
        ],
        scene="hospital",
        unique=True,
        story=True,
        locations=["Hospital"],
        min_day=2,
    ),
    _e(
        "lena_treatment",
        "THE VOSS DOSE",
        "Lena checks the dark branching veins beneath your skin with a penlight. "
        "'The pathogen targets neurological pathways. I can synthesize a counter-agent from clean reagents. "
        "It will feel like molten lead, but it will knock the colony count down.'",
        [
            _c("Take the injection", "red", infection=-25, health=-10, morale=5, flags={"lena_treated": True}),
            _c("Ask for pills instead", "blue", add_item="antibiotics", flags={"lena_treated": True}),
            _c("Inquire about a cure", "green", flags={"lena_cure_quest": True}, gemini=True, log="Lena needs hospital lab reagents for a real cure."),
            _c("Decline treatment", "yellow", log="You wave off the syringe."),
        ],
        scene="hospital",
        unique=True,
        story=True,
        require_npc="lena",
        min_day=4,
    ),
    _e(
        "lena_sacrifice_event",
        "LAST LIGHT PROTOCOL",
        "Lena sits slumped against your workbench, breathing in ragged gasps. The black veins have reached her neck. "
        "On the counter rests a single sealed ampoule of glowing amber fluid. "
        "'It's done,' she whispers. 'Pure synthesized vaccine. One dose. I used the last of my marrow to incubate the antibodies. Take it, and walk out of this city.'",
        [
            _c("Administer cure", "red", infection=-100, humanity=12, flags={"lena_sacrifice": True}, gemini=True),
            _c("Try to save Lena", "blue", humanity=15, medkits=-1, flags={"lena_sacrifice": True}, gemini=True),
            _c("Save for Fort Halcyon", "green", flags={"extract_halcyon": True, "lena_sacrifice": True}),
            _c("Sit with her final hour", "yellow", morale=10, humanity=8, flags={"lena_sacrifice": True}),
        ],
        scene="hospital",
        unique=True,
        story=True,
        require_npc="lena",
        require_flags={"lena_cure_quest": True},
        min_day=8,
    ),

    # ── THE KID ──
    _e(
        "kid_school",
        "LOCKER 42",
        "Inside an overturned storage locker in the Elementary School hallway, two wide, terrified eyes peer out. "
        "A kid clutches a backpack full of colorful bottlecaps and a pencil case. "
        "'Are the monsters gone?' the kid whispers. 'My name is {kid}. I waited for the bus, but it never came.'",
        [
            _c("Offer hand & food", "red", food=-1, humanity=10, npc_join="kid", flags={"met_kid": True}, gemini=True),
            _c("Search the backpack", "blue", scrap=2, food=1, humanity=-8, log="You take supplies from the child's pack."),
            _c("Escort to safe room", "green", humanity=6, npc_join="kid", flags={"met_kid": True}),
            _c("Leave silently", "yellow", humanity=-5, morale=-8, log="You turn your back on the child."),
        ],
        scene="kid",
        unique=True,
        story=True,
        locations=["School", "Abandoned Mall"],
        min_day=2,
    ),
    _e(
        "kid_gift",
        "BOTTLECAP FORTRESS",
        "{kid} sits on the floorboards with twisted wire and painted bottlecaps. "
        "They press a tiny improvised tin badge into your palm: 'This is the Captain's medal. Because you always come back when you leave.'",
        [
            _c("Wear with pride", "red", morale=12, humanity=4, flags={"kid_medal": True}, gemini=True),
            _c("Give candy ration", "blue", food=-1, morale=15, humanity=6, flags={"kid_medal": True}),
            _c("Teach self-defense", "green", morale=8, flags={"kid_trained": True}, log="You teach {kid} how to barricade a deadbolt."),
            _c("Pat their head", "yellow", morale=6),
        ],
        scene="kid",
        unique=True,
        story=True,
        require_npc="kid",
        min_day=4,
    ),

    # ── THE BUTCHER ──
    _e(
        "butcher_warehouse",
        "THE MEAT MARKET",
        "Carcasses hang from meat hooks inside the industrial freezer bays. "
        "A massive man in a heavy rubber apron cleans an eighteen-inch steel cleaver with a white towel. "
        "'Welcome to the pantry,' The Butcher booms cheerfully. 'In an apocalypse, friend, protein is the only honest currency. Care to trade?'",
        [
            _c("Trade 2 ammo for meat", "red", ammo=-2, food=3, humanity=-2, flags={"met_butcher": True}),
            _c("Trade scrap for medkit", "blue", scrap=-3, medkits=1, flags={"met_butcher": True}),
            _c("Ask what meat it is", "green", morale=-5, flags={"butcher_suspicious": True, "met_butcher": True}, gemini=True),
            _c("Back out with weapon raised", "yellow", flags={"met_butcher": True}, log="You retreat into the yard with steel ready."),
        ],
        scene="butcher",
        unique=True,
        story=True,
        locations=["Warehouse"],
        min_day=2,
    ),
    _e(
        "butcher_confront",
        "BLOOD AND BONE",
        "You catch The Butcher dragging a dead survivor behind the freezer racks. He doesn't look startled; he looks disappointed. "
        "'You had a good thing going, survivor. But some people just can't resist inspecting the kitchen.' He raises the cleaver with a cold grin.",
        [
            _c("Fight The Butcher!", "red", combat="butcher_fight", flags={"butcher_confronted": True}),
            _c("Throw Molotov", "blue", consume_item="molotov", combat="butcher_fight", flags={"butcher_confronted": True}),
            _c("Cut a deal & take meat", "green", food=4, scrap=3, humanity=-20, flags={"butcher_partner": True}, gemini=True),
            _c("Flee into the night", "yellow", morale=-10, flags={"butcher_confronted": True}),
        ],
        scene="butcher",
        unique=True,
        story=True,
        locations=["Warehouse"],
        require_flags={"met_butcher": True},
        min_day=6,
    ),

    # ── SISTER MIRIAM ──
    _e(
        "miriam_church",
        "THE SANCTUARY OF SHADOWS",
        "Sunlight streams through cracked stained glass, illuminating Sister Miriam kneeling in prayer beside the altar. "
        "She does not startle when your boots crunch on glass. "
        "'Grace upon your path, traveler. The world outside may be forsaken, but mercy is a choice we make every morning.'",
        [
            _c("Pray and take refuge", "red", morale=10, humanity=6, npc_join="miriam", add_item="holy_charm", flags={"met_miriam": True}, gemini=True),
            _c("Ask for clean water", "blue", water=3, humanity=2, npc_join="miriam", flags={"met_miriam": True}),
            _c("Raid the offering box", "green", scrap=2, food=1, humanity=-10, flags={"met_miriam": True}),
            _c("Nod and leave quietly", "yellow", flags={"met_miriam": True}),
        ],
        scene="church",
        unique=True,
        story=True,
        locations=["Church"],
    ),
    _e(
        "miriam_amen_event",
        "A SERVICE FOR THE CITY",
        "Sister Miriam lights eighty beeswax candles across the altar. Outside, the distant moans of shamblers echo down the avenue. "
        "'Join me in the litany,' she says softly. 'Not to change the dead, but to keep the living from becoming them.'",
        [
            _c("Lead the prayer", "red", morale=16, humanity=10, flags={"chose_sermon": True}, gemini=True),
            _c("Keep watch at the gate", "blue", scrap=1, morale=8, humanity=4),
            _c("Snuff out the candles", "green", morale=-4, log="You extinguish the flame. Light attracts teeth."),
            _c("Offer bread for communion", "yellow", food=-1, morale=12, humanity=8),
        ],
        scene="church",
        unique=True,
        story=True,
        require_npc="miriam",
        min_day=6,
    ),

    # ── GHOST ──
    _e(
        "ghost_subway",
        "THE SILENT RUNNER",
        "A figure clad in dark canvas and a scavenged respirator drops silently from a maintenance catwalk. "
        "Two swift fingers tap against a subway map: a drawn route bypassing three heavily infested avenue blocks. "
        "The figure offers a brass keycard stamped 'METRO TRANSIT AUTH'.",
        [
            _c("Accept key & ally", "red", add_item="tunnel_key", npc_join="ghost", flags={"met_ghost": True}, gemini=True),
            _c("Offer ammunition", "blue", ammo=-2, humanity=4, npc_join="ghost", add_item="tunnel_key", flags={"met_ghost": True}),
            _c("Aim your weapon", "green", morale=-2, flags={"ghost_hostile": True}, log="Ghost melts back into the track shadows."),
            _c("Inspect the map", "yellow", discover="Subway Tunnels", add_item="tunnel_key", flags={"met_ghost": True}),
        ],
        scene="subway",
        unique=True,
        story=True,
        locations=["Subway Tunnels"],
    ),
    _e(
        "ghost_haven_event",
        "THE DEEP VAULTS",
        "Ghost leads you down a forgotten maintenance shaft below the flooded subway line. "
        "Behind an airtight blast hatch hums an auxiliary turbine powering grow lights, fresh water pumps, and a dozen sleeping survivors. "
        "Ghost points toward an empty bunk.",
        [
            _c("Join the Deep Vaults", "red", humanity=10, flags={"chose_ghost_path": True}, gemini=True),
            _c("Trade surface supplies", "blue", food=3, water=3, scrap=3, flags={"vault_trade": True}),
            _c("Mark location for later", "green", discover="Subway Tunnels", flags={"vault_known": True}),
            _c("Return to surface", "yellow", log="You climb back into the cold city air."),
        ],
        scene="subway",
        unique=True,
        story=True,
        require_npc="ghost",
        min_day=7,
    ),

    # ── SCRAPS THE DOG ──
    _e(
        "dog_encounter",
        "SCRUFFY DEFENDER",
        "A wirehaired terrier with one notched ear barks ferociously at a shambler pinned under a vending machine. "
        "The dog is filthy, ribs visible through gray fur, but its tail gives a hesitant wag as you approach.",
        [
            _c("Share jerky & adopt", "red", food=-1, humanity=8, morale=12, flags={"has_dog": True}, gemini=True),
            _c("Kill the zombie first", "blue", combat="shambler", flags={"dog_saved": True}),
            _c("Shoo the dog away", "green", morale=-5, log="The dog whines and disappears into an alley."),
            _c("Search the vending machine", "yellow", food=2, risk=0.2),
        ],
        scene="mall",
        unique=True,
        story=True,
        locations=["Abandoned Mall", "Streets", "Overgrown Park"],
    ),

    # ─────────────────────────────────────────────────────────────
    # EXPLORATION, SURVIVAL & TACTICAL ENCOUNTERS
    # ─────────────────────────────────────────────────────────────

    # ── ABANDONED MALL ──
    _e(
        "mall_food_court",
        "DEPARTMENT STORE PANTRY",
        "Beneath the shattered skylight of the second-floor concourse, a metal gate guards a gourmet food market. "
        "Canned peaches, olive oil, and vacuum-sealed pasta still sit on dusted shelves.",
        [
            _c("Crowbar the padlock", "red", scrap=-1, food=4, water=2, risk=0.15),
            _c("Squeeze through transom", "blue", food=2, risk=0.25, log="You slide through broken glass."),
            _c("Set tripwire alert", "green", food=2, scrap=1, fort=1),
            _c("Check clothing racks", "yellow", add_item="mask", log="You fashion a filter mask from cloth."),
        ],
        scene="mall",
        locations=["Abandoned Mall"],
    ),
    _e(
        "mall_mannequins",
        "SILENT CONGREGATION",
        "In the dim atrium, dozens of plastic mannequins stand in unnatural poses. "
        "As you step forward, one of the silhouettes twitches with sudden, violent speed!",
        [
            _c("Fight the Runner!", "red", combat="runner"),
            _c("Toss flashlight to distract", "blue", morale=2, risk=0.1, log="The runner lunges at the bouncing beam."),
            _c("Dive behind display", "green", risk=0.3, scrap=2),
            _c("Sprint for the fire exit", "yellow", morale=-2, log="You burst through the emergency push-bar."),
        ],
        scene="mall",
        locations=["Abandoned Mall"],
    ),

    # ── HOSPITAL ──
    _e(
        "hospital_icu_lockbox",
        "NARCOTICS LOCKER",
        "Behind the triage nursing desk hangs a heavy steel narcotics safe. The emergency code pad is smashed, but the hinges look corroded.",
        [
            _c("Smash with crowbar", "red", medkits=2, add_item="antibiotics", risk=0.25),
            _c("Search doctor coats", "blue", medkits=1, scrap=1),
            _c("Sterilize clean gauze", "green", add_item="clean_gauze", medkits=1),
            _c("Avoid the chemical smell", "yellow", log="You leave the ICU before fumes settle in your lungs."),
        ],
        scene="hospital",
        locations=["Hospital", "Ruined Pharmacy"],
    ),
    _e(
        "hospital_morgue_ambush",
        "CHILLED TRAYS",
        "Condensation drips from stainless steel morgue drawers. One of the wall units is bulging outward from internal pressure.",
        [
            _c("Brace and draw weapon", "red", combat="bloater"),
            _c("Hurl Molotov inside", "blue", consume_item="molotov", scrap=3, medkits=1),
            _c("Wedge handle with pipe", "green", scrap=-1, morale=4, log="You secure the door with an iron pipe."),
            _c("Back out of the basement", "yellow", log="The dead can keep the cellar."),
        ],
        scene="hospital",
        locations=["Hospital"],
    ),

    # ── MILITARY CHECKPOINT ──
    _e(
        "checkpoint_bunker",
        "THE SANDBAG REDOUBT",
        "A reinforced sandbag revetment overlooks the highway ramp. An ammo crate sits under camouflage netting, guarded by a dead soldier in Kevlar.",
        [
            _c("Engage Armored Dead", "red", combat="armored"),
            _c("Snipe with rifle", "blue", ammo=-1, scrap=3, ammo_add=6, log="A precision headshot through the cracked visor!"),
            _c("Cut wire & sneak ammo", "green", ammo=4, scrap=2, risk=0.3),
            _c("Search the commander's map", "yellow", add_item="halcyon_leaflet", discover="Docks"),
        ],
        scene="checkpoint",
        locations=["Military Checkpoint"],
    ),
    _e(
        "checkpoint_apc",
        "STRIPPED CARRIER",
        "The armored personnel carrier sits on flat run-flat tires. The battery is dead, but the internal weapons mount is still intact.",
        [
            _c("Salvage heavy weapons", "red", scrap=3, ammo=5, risk=0.2),
            _c("Syphon diesel fuel", "blue", scrap=1, add_item="molotov"),
            _c("Collect military gas mask", "green", add_item="gas_mask", scrap=2),
            _c("Rest inside armored hull", "yellow", health=15, morale=6),
        ],
        scene="checkpoint",
        locations=["Military Checkpoint"],
    ),

    # ── DOCKS ──
    _e(
        "docks_trawler",
        "THE SEA SPRAY",
        "At the end of Pier 4, an ocean-going diesel trawler floats on the tide. "
        "The gangway is chained, but the fuel tanks read one-quarter full. A sea breeze clears the stench of rot.",
        [
            _c("Repair fuel line", "red", scrap=-2, flags={"trawler_repaired": True}, log="The fuel line is clear! The boat is ready to launch."),
            _c("Launch for open sea!", "blue", flags={"chose_docks": True}, require_flags={"trawler_repaired": True}, gemini=True),
            _c("Scavenge fishing tackle", "green", food=3, scrap=2),
            _c("Check the wheelhouse", "yellow", add_item="clean_gauze", morale=4),
        ],
        scene="docks",
        locations=["Docks"],
    ),

    # ── GAS STATION ──
    _e(
        "gas_station_fuel",
        "PUMP ISLAND",
        "A tanker truck rests overturned across the station apron. Liquid fuel has pooled in a depression near the service garage.",
        [
            _c("Carefully fill bottles", "red", add_item="molotov", scrap=1, risk=0.2),
            _c("Search the convenience shop", "blue", food=3, water=2, risk=0.3),
            _c("Watch out: Bloater!", "green", combat="bloater"),
            _c("Move along the highway", "yellow", log="Fumes are too volatile. You steer clear."),
        ],
        scene="gas",
        locations=["Gas Station"],
    ),

    # ── OVERGROWN PARK ──
    _e(
        "park_spring",
        "RECLAIMED MEADOW",
        "Weeds and wildflowers have cracked the tennis courts. In the center of the park, a natural freshwater spring bubbles into a stone fountain.",
        [
            _c("Fill all water jugs", "red", water=4, morale=6),
            _c("Harvest medicinal herbs", "blue", add_item="herbal_poultice", food=1),
            _c("Bury a fallen survivor", "green", humanity=8, morale=4),
            _c("Climb watchtower", "yellow", discover="Ruined Pharmacy", discover2="School"),
        ],
        scene="park",
        locations=["Overgrown Park"],
    ),

    # ── RUINED PHARMACY ──
    _e(
        "pharmacy_standoff",
        "THE LOOTER'S STANDOFF",
        "A desperate survivor in torn waterproof gear points a rusty pistol at you from behind the prescription counter. "
        "'I have a daughter burning with fever in the van,' he rasps. 'Just leave the antibiotics and walk away.'",
        [
            _c("Share antibiotics freely", "red", food=1, humanity=12, morale=8, flags={"helped_father": True}, gemini=True),
            _c("Trade for ammunition", "blue", ammo=3, medkits=-1, humanity=2),
            _c("Draw steel and engage", "green", combat="scavenger_raider", humanity=-12),
            _c("Back out peacefully", "yellow", humanity=4, log="You lower your hands and back out the front door."),
        ],
        scene="pharmacy",
        locations=["Ruined Pharmacy"],
    ),

    # ── STREETS & RANDOM URBAN ──
    _e(
        "streets_car_pileup",
        "AMBULANCE ON 4TH",
        "An emergency ambulance rests crushed between two delivery vans. Its rear doors hang slightly ajar, smeared with dried red palm prints.",
        [
            _c("Search medical bay", "red", medkits=2, scrap=1, risk=0.25),
            _c("Pry glove compartment", "blue", ammo=3, risk=0.15),
            _c("Ambush from the back!", "green", combat="shambler"),
            _c("Keep moving down alley", "yellow", log="You avoid the bottleneck."),
        ],
        scene="streets",
        locations=["Streets"],
    ),
    _e(
        "streets_fog_prowler",
        "FIGURES IN THE MIST",
        "Dense morning fog rolls down the avenue, reducing visibility to five paces. "
        "Wet shuffling sounds circle your perimeter, clicking like dry branches.",
        [
            _c("Hold ground and strike", "red", combat="stalker"),
            _c("Tuck into a doorway", "blue", morale=2, risk=0.15, log="The shapes glide harmlessly past your doorway."),
            _c("Fire into the fog!", "green", ammo=-1, risk=0.25, log="Muzzle flash cuts the gloom. Something screeches and flees."),
            _c("Follow Ghost's chalk marks", "yellow", morale=4, require_npc="ghost", log="Ghost's arrows guide you safely past the pack."),
        ],
        scene="streets",
        locations=["Streets"],
        weather=["fog", "storm"],
    ),

    # ── HOME BASE NIGHT & AMBIENT ──
    _e(
        "base_storm_leak",
        "THUNDER IN THE PLYWOOD",
        "Torrential rain hammers the corrugated roof. Wind howls through a cracked exterior stud, sending rainwater dripping directly onto your dry rations.",
        [
            _c("Nail fresh boards & tarps", "red", scrap=-1, fort=1, water=2, log="You seal the breach and collect the runoff."),
            _c("Move the food crates", "blue", morale=2, log="You stack the supplies safely on high shelves."),
            _c("Listen to the storm", "green", morale=5, gemini=True),
            _c("Check window perimeter", "yellow", morale=3),
        ],
        scene="base",
        locations=["Home Base"],
        night=True,
    ),
    _e(
        "base_knock_at_door",
        "THREE KNOCKS",
        "At 2 a.m., three measured raps echo against your reinforced front door. "
        "A woman's voice calls out, trembling: 'Please... the street is full of runners. I have clean water. Just let me sit on your rug until dawn.'",
        [
            _c("Open the deadbolt", "red", water=2, humanity=8, risk=0.25, gemini=True),
            _c("Pass bread through slot", "blue", food=-1, humanity=6, morale=4),
            _c("Rack pistol slide loudly", "green", morale=-2, humanity=-4, log="The footsteps bolt down the fire escape."),
            _c("Stay silent as stone", "yellow", humanity=-3, log="You hold your breath until the footsteps fade."),
        ],
        scene="base",
        locations=["Home Base"],
        night=True,
    ),

    # ─────────────────────────────────────────────────────────────
    # EXPANDED CITY — NEW LOCATION ENCOUNTERS
    # ─────────────────────────────────────────────────────────────

    # ── FIRE STATION ──
    _e(
        "firestation_engine",
        "ENGINE COMPANY 12",
        "Soot crawls up the bay walls past a pumper truck still idling on a half tank. "
        "Turnout gear lies scattered where firefighters stepped out of it and never came back. "
        "The equipment lockers rattle in the draft — or something else.",
        [
            _c("Strip the tool wall", "red", scrap=4, risk=0.2, log="Halligan bars, bolt cutters, and rope — all yours."),
            _c("Check the medical lockers", "blue", medkits=2, add_item="clean_gauze", risk=0.15),
            _c("Siphon the pumper's diesel", "green", add_item="molotov", scrap=1, risk=0.3),
            _c("Sound the alarm and slip away", "yellow", morale=4, risk=0.1, log="The bell roars behind you, drawing every shambler on the block."),
        ],
        scene="firestation",
        locations=["Fire Station"],
    ),
    _e(
        "firestation_rescue_ladder",
        "THE LADDER COMPANY",
        "On the training tower, a rescue dummy hangs half-buried in tarps — then it convulses. "
        "A real voice cracks from the roof hatch: 'Hey! HEY! I've been up here four days!'",
        [
            _c("Lower the aerial ladder", "red", humanity=10, npc_join="marcus", flags={"met_marcus": True}, gemini=True),
            _c("Toss up supplies first", "blue", food=-2, water=-1, humanity=8, add_item="radio_parts", flags={"met_marcus": True}),
            _c("Leave — voices carry", "green", humanity=-6, morale=-4, log="You leave the firefighter to his water and his prayers."),
            _c("Clear the tower first", "yellow", combat="runner", flags={"rescue_cleared": True}),
        ],
        scene="firestation",
        unique=True,
        story=True,
        locations=["Fire Station"],
        min_day=2,
    ),

    # ── CITY PRISON ──
    _e(
        "prison_block",
        "CELLBLOCK SILENCE",
        "The sally port hangs open by a hand's width. Inside, bunks are stripped, lockers looted — "
        "but the evidence cage still glitters: contraband seized on the last day of the old world.",
        [
            _c("Cut the evidence cage", "red", ammo=6, scrap=3, add_item="wire_cutters", risk=0.35),
            _c("Raid the armory locker", "blue", ammo=8, add_item="pistol", risk=0.45),
            _c("Free what's left in holding", "green", humanity=12, combat="shambler", flags={"held_survivors": True}),
            _c("Stay out of the dark wing", "yellow", log="Some doors were sealed with welded chain for a reason."),
        ],
        scene="prison",
        locations=["City Prison"],
    ),
    _e(
        "prison_warden_keys",
        "THE WARDEN'S DESK",
        "Behind cracked glass in the admin wing, a desk drawer holds the prison key ring, "
        "a rotting lunch, and a hand-written manifest naming every inmate moved the night everything fell.",
        [
            _c("Take the key ring", "red", discover="Subway Tunnels", add_item="tunnel_key", log="Maintenance keys. The transit tunnels were never on the public maps."),
            _c("Read the manifest", "blue", morale=5, humanity=4, gemini=True),
            _c("Take the lunch and go", "green", food=2, morale=2),
            _c("Leave it for whoever comes next", "yellow", humanity=3, log="You close the drawer gently, like a headstone."),
        ],
        scene="prison",
        unique=True,
        story=True,
        locations=["City Prison"],
        min_day=3,
    ),

    # ── BUS DEPOT ──
    _e(
        "bus_depot_fuel",
        "ROUTE 14 TERMINAL",
        "Fifty diesel buses sit in numbered lanes under skeletal floodlights. "
        "The depot fuel farm hisses softly — the pumps still run on the yard's generator.",
        [
            _c("Fill every can you carry", "red", scrap=2, add_item="molotov", water=2, risk=0.25),
            _c("Strip tires for rubber & scrap", "blue", scrap=4, risk=0.2),
            _c("Sleep in a climate-controlled bus", "green", health=15, morale=8),
            _c("Hotwire the depot shuttle", "yellow", discover="Waterworks", discover2="Memorial Stadium", log="You kick the shuttle awake and burn its last fumes across town."),
        ],
        scene="busdepot",
        locations=["Bus Depot"],
    ),
    _e(
        "bus_depot_passengers",
        "THE PASSENGERS",
        "Every bus driver is still at their wheel, seatbelts fastened, facing forward. "
        "Someone tucked notes into their hands. Someone wanted them found that way.",
        [
            _c("Read the farewell notes", "red", morale=-4, humanity=8, gemini=True),
            _c("Say a few words", "blue", morale=4, humanity=10),
            _c("Search their lockers instead", "green", food=2, ammo=3, risk=0.15),
            _c("Move on — this is not yours", "yellow", log="You pull the depot doors shut behind you."),
        ],
        scene="busdepot",
        unique=True,
        story=True,
        locations=["Bus Depot"],
        min_day=2,
    ),

    # ── WATERWORKS ──
    _e(
        "waterworks_pump",
        "DEADHEAD PUMP STATION",
        "Turbines the size of houses thrum behind chain-link. The municipal water still runs — "
        "nobody has turned the valves since the crews vanished. A pressure gauge blinks green: SAFE.",
        [
            _c("Fill everything & share the surplus", "red", water=5, morale=6, humanity=4),
            _c("Harvest brass fittings", "blue", scrap=4, water=2, risk=0.2),
            _c("Chlorinate & bottle for trade", "green", water=3, flags={"water_trade": True}, log="Clean water becomes the loudest voice in any room."),
            _c("Dive the intake channel", "yellow", combat="bloater", add_item="gas_mask"),
        ],
        scene="waterworks",
        locations=["Waterworks"],
    ),

    # ── OVERPASS CAMP ──
    _e(
        "overpass_camp",
        "TARP CITY",
        "Beneath the elevated freeway, a shantytown of tarps and shopping carts sways in the draft. "
        "Cooking smoke rises through the concrete ribs. Thirty survivors, one hand-pumped well, no walls.",
        [
            _c("Trade scrap for their stories", "red", scrap=-2, morale=6, humanity=6, flags={"overpass_allies": True}, gemini=True),
            _c("Share a meal with strangers", "blue", food=-2, humanity=10, morale=8, flags={"overpass_allies": True}),
            _c("Warn them about the night lanes", "green", humanity=5, discover="Waterworks", flags={"overpass_warned": True}),
            _c("Rob the camp blind", "yellow", food=3, ammo=4, humanity=-18, combat="scavenger_raider"),
        ],
        scene="overpass",
        locations=["Overpass Camp"],
    ),
    _e(
        "overpass_vote",
        "THE CAMP VOTE",
        "The camp elder finds you by the well: 'They want to move into the old prison — walls, gates, no more tents. "
        "But you've seen what walks those corridors. We're voting. You get a vote too.'",
        [
            _c("Vote for the prison walls", "red", morale=8, humanity=4, flags={"camp_prison": True}),
            _c("Vote to stay mobile", "blue", morale=5, humanity=6, flags={"camp_stay": True}),
            _c("Offer your base as shelter", "green", food=-2, water=-2, humanity=14, npc_join="miriam", flags={"camp_refuge": True}),
            _c("Refuse the ballot", "yellow", morale=-2, log="You are still your own nation."),
        ],
        scene="overpass",
        unique=True,
        story=True,
        locations=["Overpass Camp"],
        min_day=4,
    ),

    # ── MEMORIAL STADIUM ──
    _e(
        "stadium_fema",
        "FIELD OF TENTS",
        "FEMA tents ripple across the stadium field under a scoreboard flashing RED in an endless loop. "
        "Medical tents first: most are stripped, but one quarantine pavilion still has a sealed supply pallet.",
        [
            _c("Crack the supply pallet", "red", medkits=3, add_item="antibiotics", risk=0.4),
            _c("Search the locker rooms", "blue", food=3, water=3, add_item="clean_gauze", risk=0.3),
            _c("Climb the press box", "green", discover="Fire Station", discover2="City Prison", morale=4),
            _c("Sprint the fifty-yard line", "yellow", combat="stalker", log="Your boots drum the turf as something fast uncovers itself from the visitor tunnel."),
        ],
        scene="stadium",
        locations=["Memorial Stadium"],
    ),
    _e(
        "stadium_ghost_game",
        "THE GHOST GAME",
        "The jumbotron flickers to life — someone on the grid is powering the stadium board. "
        "A scoreboard reads HOME 07 : AWAY 07 with 00:04 on the clock, and the crowd noise loops on a scratched tape.",
        [
            _c("Answer the board — raise your arms", "red", morale=14, humanity=6, gemini=True, flags={"ghost_game": True}),
            _c("Kill the generator", "blue", scrap=2, morale=-3, log="The lights die. Somewhere in the stands, something complains."),
            _c("Search while the lights burn", "green", ammo=5, food=2, risk=0.3),
            _c("Leave the stadium dark", "yellow", log="You slip out beneath the scoreboard's dying glow."),
        ],
        scene="stadium",
        unique=True,
        story=True,
        locations=["Memorial Stadium"],
        night=True,
    ),

    # ── ADDITIONAL URBAN VARIETY ──
    _e(
        "streets_quiet_theater",
        "THE LAST SHOWING",
        "A single-screen cinema still glows — the projection booth runs on a car battery rig. "
        "On screen, a film from before the fall plays to an audience of dust and one sleeping dog.",
        [
            _c("Watch the whole reel", "red", morale=10, humanity=5, gemini=True),
            _c("Take the battery rig", "blue", scrap=3, morale=-4, humanity=-4, log="The screen dies mid-scene. The dog follows you out."),
            _c("Scavenge the concession stand", "green", food=3, water=2, risk=0.15),
            _c("Check the alley fire escape", "yellow", ammo=3, risk=0.3),
        ],
        scene="streets",
        locations=["Streets", "Overpass Camp"],
    ),
    _e(
        "streets_kitchen_ghost",
        "BURNER STILL ON",
        "A restaurant kitchen left mid-service: pots reduced to tar on dead burners, tickets curled in the rail. "
        "Somewhere in the walk-in freezer, metal groans under slow weight.",
        [
            _c("Bolt the freezer door shut", "red", morale=3, humanity=4, risk=0.1),
            _c("Whatever's inside — strike first", "blue", combat="bloater"),
            _c("Salvage the dry stores", "green", food=4, risk=0.2),
            _c("Back out through the dining room", "yellow", log="You weave between tables set for people who never sat down."),
        ],
        scene="streets",
        locations=["Streets", "Bus Depot", "Fire Station"],
        night=None,
    ),
    _e(
        "base_radio_dreams",
        "DEAD AIR DREAMS",
        "Sleep comes hard. The radio filters through the static with a music box melody, "
        "and a voice underneath counts the days wrong: 'Day one. Day one. Day one...'",
        [
            _c("Record the melody", "red", morale=6, humanity=4, flags={"dream_melody": True}, gemini=True),
            _c("Rip the batteries out", "blue", morale=-3, scrap=1, log="Silence is its own kind of noise."),
            _c("Answer the count aloud", "green", morale=4, humanity=6, infection=3, flags={"answered_count": True}),
            _c("Pull the blanket over your head", "yellow", morale=-2, health=4),
        ],
        scene="base",
        locations=["Home Base"],
        night=True,
    ),
    _e(
        "park_foraging_circle",
        "THE FORAGING CIRCLE",
        "Neat rows of painted soup cans mark a community garden someone keeps by moonlight. "
        "A note is weighted with a stone: 'TAKE WHAT YOU NEED. LEAVE WHAT YOU CAN. — THE GREEN THUMB CLUB'",
        [
            _c("Take a little, leave scrap", "red", food=3, water=1, scrap=-1, humanity=6),
            _c("Take everything", "blue", food=6, humanity=-12, flags={"raided_garden": True}),
            _c("Leave a full meal tin", "green", food=-1, humanity=8, morale=6, flags={"left_gift": True}),
            _c("Wait and watch the gardener", "yellow", morale=4, risk=0.1, log="No one comes. You leave before the guilt does."),
        ],
        scene="park",
        locations=["Overgrown Park", "Overpass Camp"],
    ),
    _e(
        "subway_ghost_train",
        "GHOST TRAIN",
        "Headlights bloom in the black tunnel — a train nobody drives rolls through the station, "
        "doors open, interior lights swaying. Its brake screech sounds almost like a voice.",
        [
            _c("Board the moving train", "red", discover="Docks", morale=6, risk=0.35, log="It carries you three stops and dies mid-tunnel. You walk the rest."),
            _c("Raid the luggage racks", "blue", food=2, scrap=3, ammo=3, risk=0.3),
            _c("Wave as it passes", "green", morale=8, humanity=4, gemini=True),
            _c("Stay in the shadows", "yellow", risk=0.05, log="You press into the alcove and let the dead iron sing past."),
        ],
        scene="subway",
        locations=["Subway Tunnels", "Bus Depot"],
    ),
]


def _weather_match(ev: Dict[str, Any], state) -> bool:
    req_w = ev.get("weather")
    if not req_w:
        return True
    if isinstance(req_w, str):
        return state.world.weather == req_w
    return state.world.weather in req_w


def select_event(state, location: Optional[str] = None) -> Dict[str, Any]:
    """
    Selects the next most appropriate story beat or location encounter.
    Prioritizes un-triggered unique story beats whose conditions are satisfied.
    """
    now = state.world
    loc = location or now.location

    # 1. Story & Unique Queue
    story_pool: List[Dict[str, Any]] = []
    for ev in EVENTS:
        if ev.get("unique") and ev["id"] in now.seen_events:
            continue
        if now.day < ev.get("min_day", 1) or now.day > ev.get("max_day", 99):
            continue
        if not _weather_match(ev, state):
            continue

        # Night restrictions
        n_req = ev.get("night")
        if n_req is True and not now.is_night:
            continue
        if n_req is False and now.is_night:
            continue

        # Location restrictions
        locs = ev.get("locations")
        if locs and loc not in locs:
            continue

        # Flags & NPC prerequisites
        req_f = ev.get("require_flags") or {}
        if not all(now.flags.get(k) for k in req_f):
            continue
        forb_f = ev.get("forbid_flags") or {}
        if any(now.flags.get(k) for k in forb_f):
            continue
        if ev.get("require_npc"):
            npc = now.npcs.get(ev["require_npc"], {})
            if not (npc.get("alive") and npc.get("at_base")):
                continue

        if ev.get("story") or ev.get("unique"):
            story_pool.append(ev)

    if story_pool:
        # Sort so that story beats with highest priority trigger first
        story_pool.sort(key=lambda e: (not e.get("story"), not e.get("unique"), random.random()))
        chosen = copy.deepcopy(story_pool[0])
    else:
        # 2. General Location Pool
        gen_pool: List[Dict[str, Any]] = []
        for ev in EVENTS:
            if ev.get("unique") and ev["id"] in now.seen_events:
                continue
            if now.day < ev.get("min_day", 1) or now.day > ev.get("max_day", 99):
                continue
            locs = ev.get("locations")
            if locs and loc not in locs:
                continue
            if not _weather_match(ev, state):
                continue

            n_req = ev.get("night")
            if n_req is True and not now.is_night:
                continue
            if n_req is False and now.is_night:
                continue

            req_f = ev.get("require_flags") or {}
            if not all(now.flags.get(k) for k in req_f):
                continue
            forb_f = ev.get("forbid_flags") or {}
            if any(now.flags.get(k) for k in forb_f):
                continue

            gen_pool.append(ev)

        if gen_pool:
            weights = [e.get("weight", 1) for e in gen_pool]
            chosen = copy.deepcopy(random.choices(gen_pool, weights=weights, k=1)[0])
        else:
            # Fallback atmospheric event
            chosen = copy.deepcopy(
                _e(
                    "urban_quiet",
                    "THE CITY BREATHES",
                    "A dry wind whispers through shattered high-rise windows. Nothing moves for ten minutes. "
                    "You are still alive because you know when to listen to silence.",
                    [
                        _c("Catch your breath", "red", morale=4),
                        _c("Scour the gutter for scrap", "blue", scrap=1, risk=0.15),
                        _c("Keep sharp watch", "green", morale=3),
                        _c("Head toward shelter", "yellow", log="You keep moving along the brick shadows."),
                    ],
                    scene="streets",
                    locations=[loc],
                )
            )

    chosen["text"] = _apply_kid(state, chosen["text"])
    return chosen
