"""Story and encounter catalog. Unique story beats fire first when their gates open."""

import copy
import random
from typing import Any, Dict, List, Optional

from backend.app.game.content import LOCATIONS

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
        elif k in ("gemini",):
            eff[k] = v
        else:
            eff[k] = v
    return {"label": label, "key": key, "effect": eff}


def _apply_kid(state, text: str) -> str:
    return text.replace("{kid_name}", state.kid_name)


EVENTS: List[Dict[str, Any]] = [
    # --- story: Marcus / Channel 7 ---
    _e(
        "radio_static",
        "CHANNEL 7",
        "The radio on the counter wakes itself. A man who used to sell weather as comfort is selling coordinates as hope. "
        "Fort Halcyon, he says. Walls. Names taken. Bring the living.",
        [
            _c("Listen", "red", morale=8, flags={"heard_halcyon": True, "met_marcus_voice": True}, gemini=True),
            _c("Answer", "blue", morale=4, humanity=2, flags={"answered_radio": True, "heard_halcyon": True}, gemini=True),
            _c("Kill the volume", "green", morale=-4),
            _c("Hunt the tower", "yellow", expedition="Radio Tower", flags={"heard_halcyon": True}),
        ],
        scene="radio",
        unique=True,
        story=True,
        locations=["Home Base", "Streets"],
        night=None,
    ),
    _e(
        "marcus_tower",
        "THE VOICE HAS A FACE",
        "Marcus Hale sits among dead transmitters like a priest who learned electricity. "
        "He looks at you the way a microphone looks at a room: waiting to see if you are worth the wattage.",
        [
            _c("Offer scrap & company", "red", scrap=-1, humanity=6, npc_join="marcus", flags={"met_marcus": True}, gemini=True),
            _c("Ask about Halcyon", "blue", morale=5, flags={"met_marcus": True, "heard_halcyon": True}, gemini=True),
            _c("Demand the truth", "green", flags={"met_marcus": True, "marcus_pressed": True}, gemini=True),
            _c("Leave him to the static", "yellow", humanity=-3, flags={"met_marcus": True}),
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
        "LEGAL ID",
        "Marcus drinks cold instant coffee like it is still 6 a.m. in a country that exists. "
        "'Halcyon was a drill,' he says. 'Then it was a quarantine. Then they kept the music because people die quieter if they have a destination.'",
        [
            _c("Keep broadcasting hope", "red", humanity=8, morale=6, flags={"marcus_hope": True}, gemini=True),
            _c("Broadcast the warning", "blue", humanity=4, morale=-4, flags={"marcus_warning": True}, gemini=True),
            _c("Use the lie", "green", humanity=-8, flags={"marcus_lie": True}),
            _c("Say nothing", "yellow", morale=-2),
        ],
        scene="marcus",
        unique=True,
        story=True,
        locations=["Radio Tower", "Home Base"],
        require_flags={"met_marcus": True, "radio_repaired": True},
        min_day=7,
    ),
    # --- Lena ---
    _e(
        "lena_ward",
        "LUCID ROT",
        "She should not be this calm. Black threads under the skin of her throat, a lab coat that has given up being white. "
        "'I am Dr. Lena Voss,' she says. 'I am contagious. I am still useful. Those are not the same sentence.'",
        [
            _c("Take her in", "red", humanity=10, infection=4, npc_join="lena", flags={"met_lena": True}, gemini=True),
            _c("Ask for treatment", "blue", flags={"met_lena": True, "lena_bargain": True}, gemini=True),
            _c("Back away", "green", flags={"met_lena": True}, morale=-4),
            _c("Put her down", "yellow", humanity=-18, flags={"met_lena": True, "lena_dead": True}, npc_kill="lena", combat="shambler"),
        ],
        scene="lena",
        unique=True,
        story=True,
        locations=["Hospital"],
        min_day=2,
    ),
    _e(
        "lena_notes",
        "HALF A CURE",
        "Lena's handwriting is a person trying not to shake. The pathogen was a 'resilience adjuvant.' "
        "The dead are a committee that never adjourned. She can slow it. She cannot send it home.",
        [
            _c("Take the notes", "red", add_item="lena_notes", flags={"lena_notes": True}, gemini=True),
            _c("Ask her to treat you", "blue", infection=-18, health=-8, flags={"lena_treated": True}),
            _c("Ask her to treat the kid", "green", humanity=6, flags={"lena_kid": True}, require_npc="kid"),
            _c("Burn the pages", "yellow", humanity=-6, morale=-8),
        ],
        scene="lena",
        unique=True,
        story=True,
        locations=["Hospital", "Home Base"],
        require_flags={"met_lena": True},
        forbid_flags={"lena_dead": True},
        min_day=5,
    ),
    _e(
        "lena_offer",
        "A LIGHT THAT COSTS",
        "Lena sits very straight. 'If I finish the dose in me, I can push a clean draft through you. "
        "I will not get a second draft. Do not make this a speech.'",
        [
            _c("Refuse", "red", humanity=4, morale=-4, flags={"lena_refused": True}),
            _c("Accept", "blue", flags={"lena_sacrifice": True}, infection=-80, health=20, npc_kill="lena", ending_if="last_light"),
            _c("Delay", "green", morale=-2),
            _c("Ask for another way", "yellow", gemini=True),
        ],
        scene="lena",
        unique=True,
        story=True,
        locations=["Home Base"],
        require_flags={"lena_notes": True},
        forbid_flags={"lena_dead": True},
        min_day=10,
    ),
    # --- Kid ---
    _e(
        "kid_alley",
        "SMALL FOOTSTEPS",
        "They are holding a dented thermos like a legal document. Name on the tape is smudged. "
        "They look at your hands first, then your face, which is the correct order now.",
        [
            _c("Take them home", "red", humanity=12, food=-1, npc_join="kid", flags={"met_kid": True, "kid_saved": True}, gemini=True),
            _c("Share food, leave a map", "blue", humanity=6, food=-1, flags={"met_kid": True}),
            _c("Walk past", "green", humanity=-10, morale=-12, flags={"met_kid": True, "kid_abandoned": True}),
            _c("Ask where their people are", "yellow", flags={"met_kid": True}, gemini=True, discover="School"),
        ],
        scene="kid",
        unique=True,
        story=True,
        locations=["Streets", "Abandoned Mall", "School"],
        min_day=2,
    ),
    _e(
        "kid_fever",
        "NIGHT TALK",
        "{kid_name} is awake for the wrong reasons. 'If I get like the slow ones,' they say, "
        "'do you promise to be faster than them?' The kettle clicks. You hate the kettle for being ordinary.",
        [
            _c("Promise", "red", humanity=4, morale=-3, flags={"kid_promise": True}, gemini=True),
            _c("Tell the truth", "blue", humanity=2, morale=-6, gemini=True),
            _c("Change the subject", "green", morale=2),
            _c("Give them the photo", "yellow", consume_item="photo", morale=10, humanity=3),
        ],
        scene="kid",
        unique=True,
        story=True,
        locations=["Home Base"],
        night=True,
        require_npc="kid",
        min_day=4,
    ),
    _e(
        "school_photo",
        "CLASS 3-B",
        "A classroom with the windows papered against the sun. One photo still hangs: twenty-six faces, one of them {kid_name}'s, "
        "grinning like the future was a field trip.",
        [
            _c("Take the photo", "red", add_item="photo", morale=-4, humanity=2, flags={"school_seen": True}),
            _c("Leave it hanging", "blue", morale=4, flags={"school_seen": True}),
            _c("Search desks", "green", food=1, scrap=1, risk=0.35, flags={"school_seen": True}),
            _c("Call out", "yellow", risk=0.5, flags={"school_seen": True}),
        ],
        scene="school",
        unique=True,
        story=True,
        locations=["School"],
        discover="School",
    ),
    # --- Butcher ---
    _e(
        "butcher_aisle",
        "MEAT MATH",
        "He is rendering something that used to have a job. He waves with the clean hand. "
        "'Relax. I only process the ones who already filed their resignation. You still have paperwork.'",
        [
            _c("Trade scrap", "red", scrap=-2, food=3, ammo=2, flags={"met_butcher": True, "butcher_deal": True}),
            _c("Talk", "blue", flags={"met_butcher": True}, gemini=True),
            _c("Draw steel", "green", flags={"met_butcher": True}, combat="butcher_fight"),
            _c("Leave the aisle", "yellow", flags={"met_butcher": True}),
        ],
        scene="butcher",
        unique=True,
        story=True,
        locations=["Warehouse"],
        min_day=3,
    ),
    _e(
        "butcher_hunt",
        "COLLECTION NOTICE",
        "The Butcher has found your door like a rumor with legs. 'Someone took a crate that had my mark. "
        "You look like a person who knows where crates go when they grow legs.'",
        [
            _c("Pay him off", "red", food=-2, scrap=-2, flags={"butcher_paid": True}),
            _c("Lie", "blue", humanity=-4, risk=0.4, flags={"butcher_lied": True}),
            _c("Fight", "green", combat="butcher_fight", flags={"butcher_war": True}),
            _c("Offer a job", "yellow", humanity=-6, flags={"butcher_hired": True}, gemini=True),
        ],
        scene="butcher",
        unique=True,
        story=True,
        locations=["Home Base", "Streets"],
        require_flags={"met_butcher": True},
        min_day=8,
        night=None,
    ),
    # --- Miriam ---
    _e(
        "church_bell",
        "ONE BELL LEFT",
        "Sister Miriam rings a bell that is not attached to anything. The sound is small and stubborn. "
        "'We are not asked to win,' she says. 'We are asked not to become the joke.'",
        [
            _c("Sit with her", "red", morale=12, humanity=4, npc_join="miriam", flags={"met_miriam": True}, gemini=True),
            _c("Ask for blessing", "blue", add_item="holy_charm", morale=6, flags={"met_miriam": True}),
            _c("Loot the altar", "green", scrap=2, food=1, humanity=-12, morale=-8, flags={"met_miriam": True, "church_looted": True}),
            _c("Leave quietly", "yellow", flags={"met_miriam": True}),
        ],
        scene="miriam",
        unique=True,
        story=True,
        locations=["Church"],
        min_day=2,
    ),
    _e(
        "miriam_test",
        "THE UNQUIET",
        "An infected man is tied in the vestry, lucid enough to say please. Miriam will not look away. "
        "'If mercy is only for the convenient,' she says, 'it is just interior decorating.'",
        [
            _c("Release him with food", "red", humanity=10, food=-1, infection=3, flags={"mercy_given": True}),
            _c("End it clean", "blue", humanity=2, morale=-10, flags={"mercy_ended": True}),
            _c("Leave it to Miriam", "green", morale=-2, flags={"mercy_hers": True}),
            _c("Walk out", "yellow", humanity=-6, morale=-6),
        ],
        scene="miriam",
        unique=True,
        story=True,
        locations=["Church", "Home Base"],
        require_flags={"met_miriam": True},
        min_day=6,
    ),
    # --- Ghost ---
    _e(
        "ghost_platform",
        "THE ONE WHO DOES NOT SPEAK",
        "A figure at the edge of the platform holds up a palm: stop. Then two fingers: this way. "
        "The throat is a closed door. The eyes are a timetable.",
        [
            _c("Follow", "red", npc_join="ghost", add_item="tunnel_key", flags={"met_ghost": True, "ghost_trust": True}),
            _c("Offer water", "blue", water=-1, humanity=3, flags={"met_ghost": True}, gemini=True),
            _c("Raise your weapon", "green", flags={"met_ghost": True, "ghost_spooked": True}, combat="runner"),
            _c("Stay on the platform", "yellow", flags={"met_ghost": True}),
        ],
        scene="ghost",
        unique=True,
        story=True,
        locations=["Subway Tunnels"],
        min_day=3,
    ),
    _e(
        "ghost_shortcut",
        "UNDER THE MAP",
        "Ghost unrolls a maintenance schematic on the floor. Lines like veins. A circle around the checkpoint. "
        "A smaller circle around the docks. A third around your street, which is either kindness or inventory.",
        [
            _c("Learn the docks route", "red", discover="Docks", flags={"ghost_docks": True}),
            _c("Learn the checkpoint", "blue", discover="Military Checkpoint", flags={"ghost_check": True}),
            _c("Ask them to stay", "green", npc_join="ghost", humanity=4),
            _c("Fold the map away", "yellow"),
        ],
        scene="ghost",
        unique=True,
        story=True,
        locations=["Subway Tunnels", "Home Base"],
        require_flags={"met_ghost": True},
        min_day=6,
    ),
    # --- extraction / late ---
    _e(
        "checkpoint_lights",
        "18 KILOMETERS",
        "The checkpoint is a sentence that was never finished. Sandbags, a dead Humvee, a loudspeaker with a bird's nest in its mouth. "
        "A leaflet under a stone: SAFE ZONE. BRING THE LIVING.",
        [
            _c("Take the leaflet", "red", add_item="halcyon_map", flags={"checkpoint_seen": True}),
            _c("Search the Humvee", "blue", ammo=4, scrap=2, risk=0.45, flags={"checkpoint_seen": True}),
            _c("Call out", "yellow", combat="armored", flags={"checkpoint_seen": True}),
            _c("Go to ground", "green", morale=2, flags={"checkpoint_seen": True}),
        ],
        scene="checkpoint",
        unique=True,
        story=True,
        locations=["Military Checkpoint", "Streets"],
        min_day=8,
    ),
    _e(
        "extraction_call",
        "A TRUCK WITH A NUMBER",
        "Channel 7 is suddenly close. Marcus — or a recording of Marcus — says a truck will idle at the west gate for one hour on day-count that matches yours. "
        "You can hear a generator that might be real.",
        [
            _c("Go to Halcyon", "red", flags={"extract_halcyon": True}, require_day=12),
            _c("Wait, fortify", "blue", morale=4),
            _c("Take the docks instead", "green", expedition="Docks"),
            _c("Stay off the air", "yellow"),
        ],
        scene="radio",
        unique=True,
        story=True,
        locations=["Home Base", "Radio Tower"],
        require_flags={"heard_halcyon": True},
        min_day=12,
    ),
    _e(
        "docks_boat",
        "SOMETHING THAT FLOATS",
        "The boat is ugly and enough. Fuel is a maybe. The city behind you is a rumor with streetlights.",
        [
            _c("Cast off", "red", flags={"chose_docks": True}),
            _c("Siphon more fuel", "blue", expedition="Gas Station", risk=0.3),
            _c("Turn back", "green", morale=-2),
            _c("Search the warehouse pier", "yellow", scrap=2, food=1, risk=0.4),
        ],
        scene="docks",
        unique=True,
        story=True,
        locations=["Docks"],
        min_day=9,
    ),
    # --- locations / variety ---
    _e(
        "streets_glint",
        "UNDER THE CAR",
        "A sedan wearing another sedan. Something canned winks under the axle. The street has that held-breath feeling.",
        [
            _c("Crawl under", "red", food=2, scrap=1, risk=0.28),
            _c("Pry the trunk", "blue", ammo=2, scrap=1, risk=0.35),
            _c("Watch first", "green", morale=3),
            _c("Back to base", "yellow", expedition="Home Base"),
        ],
        scene="streets",
        locations=["Streets"],
        night=False,
        weight=3,
    ),
    _e(
        "horde_shuffle",
        "THE COMMITTEE",
        "They are not hunting. They are commuting. Twenty mouths with the same appointment. "
        "Your building is on the way.",
        [
            _c("Fight the edge", "red", combat="shambler"),
            _c("Rooftops", "blue", health=-4, morale=-4),
            _c("Hold still", "green", risk=0.42),
            _c("Noise to the east", "yellow", scrap=-1, morale=2),
        ],
        scene="horde",
        locations=["Streets", "Abandoned Mall", "Warehouse"],
        weight=2,
    ),
    _e(
        "night_scratch",
        "SOMETHING AT THE BOARD",
        "The barricade ticks like a clock that owes someone money. On the other side: breathing that does not need to.",
        [
            _c("Shoot the door", "red", ammo=-2, health=-4),
            _c("Brace it", "blue", scrap=-1, fort=1),
            _c("Silent", "green", risk=0.5),
            _c("Back window", "yellow", expedition="Streets", health=-6),
        ],
        scene="base_night",
        locations=["Home Base"],
        night=True,
        weight=2,
    ),
    _e(
        "mall_court",
        "FOOD COURT GEOLOGY",
        "Trays in strata. A vending machine still humming on a generator that should have died in week one. "
        "That is either a gift or bait. Those have been the same lately.",
        [
            _c("Break the glass", "red", food=3, water=1, risk=0.4),
            _c("Quiet bags only", "blue", food=1),
            _c("Set a snare", "green", scrap=-1, ammo=2, risk=0.3),
            _c("Leave", "yellow"),
        ],
        scene="mall",
        locations=["Abandoned Mall"],
        weight=2,
    ),
    _e(
        "mall_runners",
        "THE FAST ONES",
        "They were athletes or they were afraid long enough to become athletes. The mall directory says YOU ARE HERE, which feels rude.",
        [
            _c("Stand and fire", "red", combat="runner"),
            _c("Service corridor", "blue", health=-5, expedition="Streets"),
            _c("Mannequin blind", "green", risk=0.33),
            _c("Molotov the court", "yellow", consume_item="molotov", combat="runner"),
        ],
        scene="runner",
        locations=["Abandoned Mall"],
        weight=2,
    ),
    _e(
        "hospital_cabinet",
        "LOCKED GLASS",
        "Antibiotics with names like spells. A smear on the glass that might be a handprint or a map.",
        [
            _c("Smash and grab", "red", medkits=2, add_item="antibiotics", infection=6, risk=0.4),
            _c("Take a careful dose", "blue", medkits=1, infection=-8),
            _c("Search records", "green", discover="School", flags={"voss_name": True}, gemini=True),
            _c("Too sour here", "yellow", morale=-3),
        ],
        scene="hospital",
        locations=["Hospital"],
        weight=2,
    ),
    _e(
        "warehouse_lock",
        "A DOOR THAT MEANS IT",
        "Padlock the size of a decision. Behind it: the sound of cans rolling, or bones, or cans.",
        [
            _c("Crowbar it", "red", consume_item="crowbar", scrap=4, food=2, keep_item=True),
            _c("Noise as bait", "blue", combat="shambler"),
            _c("Climb the racking", "green", scrap=3, risk=0.35),
            _c("Not this door", "yellow"),
        ],
        scene="warehouse",
        locations=["Warehouse"],
        weight=2,
    ),
    _e(
        "subway_dark",
        "THIRD RAIL HYMN",
        "Water to the shins. A rat with opinions. Far off, a moan that has learned echo.",
        [
            _c("Press on", "red", discover="Docks", risk=0.4),
            _c("Make a light", "blue", scrap=-1, morale=4),
            _c("Kill the light", "green", risk=0.25),
            _c("Stairs. Now.", "yellow", expedition="Streets"),
        ],
        scene="subway",
        locations=["Subway Tunnels"],
        weight=2,
        night=None,
    ),
    _e(
        "gas_siphon",
        "ZERO DOLLARS A GALLON",
        "The pumps are dead. The underground tanks are not a metaphor. A bloated shape is asleep against the kiosk glass.",
        [
            _c("Siphon anyway", "red", flags={"fuel": True}, scrap=1, risk=0.38),
            _c("Clear the kiosk", "blue", combat="bloater"),
            _c("Take shelf candy", "green", food=2, morale=4),
            _c("Roll out", "yellow"),
        ],
        scene="gas",
        locations=["Gas Station"],
        weight=2,
    ),
    _e(
        "bloater_alley",
        "SWEET AIR",
        "The alley smells like a fridge unplugged in July. It stands there as if waiting for a bus that was cancelled on moral grounds.",
        [
            _c("Burn it", "red", consume_item="molotov", flags={"bloater_down": True}),
            _c("Shoot the knees", "blue", ammo=-2, combat="bloater"),
            _c("Wide berth", "green", infection=2),
            _c("Bottle and run", "yellow", health=-6, expedition="Streets"),
        ],
        scene="bloater",
        locations=["Streets", "Warehouse", "Gas Station"],
        weight=1,
        min_day=4,
    ),
    _e(
        "armored_patrol",
        "STILL WEARING THE WAR",
        "Ceramic plates and a jaw that has opinions. The helmet says a name you do not say back.",
        [
            _c("Go for the visor", "red", combat="armored"),
            _c("Caltrops of glass", "blue", scrap=-1, risk=0.3),
            _c("Play dead", "green", risk=0.55, morale=-6),
            _c("Pray it passes", "yellow", consume_item="holy_charm", morale=4),
        ],
        scene="armored",
        locations=["Military Checkpoint", "Streets"],
        min_day=7,
        weight=1,
    ),
    _e(
        "survivor_hands",
        "HANDS UP",
        "A woman with a split lip and a backpack that rattles like canned luck. 'I am not a lesson,' she says. 'I am a person who is thirsty.'",
        [
            _c("Share water", "red", water=-1, humanity=8, morale=6, gemini=True, flags={"saved_stranger": True}),
            _c("Trade", "blue", food=-1, ammo=2, scrap=1),
            _c("Rob her", "green", food=2, water=1, humanity=-14, morale=-8, flags={"robbed_stranger": True}),
            _c("Point her at Halcyon", "yellow", humanity=3, flags={"heard_halcyon": True}),
        ],
        scene="survivor",
        locations=["Streets", "Church", "Abandoned Mall"],
        weight=2,
    ),
    _e(
        "infected_beg",
        "STILL USING WORDS",
        "He knows he is not going to be invited in. He asks for the door to be shut anyway, so he does not have to watch himself do the last part.",
        [
            _c("Stay with him", "red", humanity=10, morale=-8, infection=5, gemini=True),
            _c("Meds, then distance", "blue", medkits=-1, humanity=6, infection=-4),
            _c("The kind shot", "green", ammo=-1, humanity=1, morale=-12),
            _c("Close the door", "yellow", humanity=-5, morale=-6),
        ],
        scene="survivor",
        locations=["Home Base", "Streets", "Hospital"],
        weight=1,
        min_day=3,
    ),
    _e(
        "quiet_hour",
        "A ROOM WITH NO PLOT",
        "Dust in a sunbeam. Your hands look like your hands. For eight minutes the apocalypse is a rumor in another building.",
        [
            _c("Rest", "red", health=16, morale=8, consume_item="medkits"),
            _c("Write the room down", "blue", morale=4, humanity=2, gemini=True),
            _c("Keep packing", "green", scrap=1, risk=0.2),
            _c("Back to the boarded room", "yellow"),
        ],
        scene="quiet",
        locations=["Home Base", "Streets", "Church", "School"],
        weight=1,
        night=None,
    ),
    _e(
        "rain_catcher",
        "THE SKY OWES YOU",
        "It starts like a rumor and ends like a promise. You are already under a tarp before you decide to be.",
        [
            _c("Make a rain catcher", "red", scrap=-2, flags={"rain_catcher": True}, gemini=True),
            _c("Sleep under it anyway", "blue", morale=4),
            _c("Share with the kid", "green", humanity=4, require_npc="kid"),
            _c("Fall back", "yellow"),
        ],
        scene="rain",
        locations=["Home Base"],
        weight=1,
        night=False,
    ),
    _e(
        "fog_street",
        "WHITE WALLS",
        "The street forgets where it ends. A radio in the distance sounds like it is in your mouth.",
        [
            _c("Follow the voice", "red", risk=0.35, gemini=True),
            _c("Mark the lampposts", "blue", scrap=1, morale=2),
            _c("Hold your breath", "green", infect=3),
            _c("Wait for it to pass", "yellow", morale=-2),
        ],
        scene="fog",
        locations=["Streets", "Subway Tunnels"],
        weight=1,
        night=None,
    ),
    _e(
        "storm_tin",
        "A ROOF WITH AN OPINION",
        "The roof argues. You argue back with a bucket. The argument is prolonged.",
        [
            _c("Patch it", "red", scrap=-1, fort=1, gemini=True),
            _c("Bail and wait", "blue", water=2, morale=-2),
            _c("Let the kid hold the roof", "green", humanity=-4, morale=-4),
            _c("Tarp the south wall", "yellow", scrap=-1, fort=1),
        ],
        scene="storm",
        locations=["Home Base"],
        weight=1,
        night=False,
        require_weather="storm",
    ),
    _e(
        "tower_climb",
        "NEEDLE BREATH",
        "The service stairs have your name on them in rust. Above, a lantern that might be a station and might be a star.",
        [
            _c("Climb", "red", scrap=1, risk=0.3, discover="Radio Tower"),
            _c("Shine up first", "blue", morale=2),
            _c("Turn around", "green", morale=-2),
            _c("Draw it later", "yellow", memo="tower"),
        ],
        scene="tower",
        locations=["Streets", "Warehouse"],
        weight=1,
        night=False,
    ),
]


def _any_location_match(event: Dict[str, Any], state) -> bool:
    locs = event.get("locations") or []
    if not locs:
        return True
    return state.world.location in locs


def _weather_match(event: Dict[str, Any], state) -> bool:
    req = event.get("require_weather")
    if not req:
        return True
    return state.world.weather == req


def select_event(state, location: Optional[str] = None) -> Dict[str, Any]:
    """Pick the most appropriate event for the current world state.

    Unique/story events with open gates fire first. Otherwise a weighted
    pool from the current location (or the world location) is chosen.
    """
    pool: List[Dict[str, Any]] = []
    now = state.world

    for ev in EVENTS:
        if ev.get("unique") and ev["id"] in now.seen_events:
            continue
        if now.day < ev.get("min_day", 1):
            continue
        if now.day > ev.get("max_day", 99):
            continue
        if not _weather_match(ev, state):
            continue
        if not _any_location_match(ev, state):
            continue
        # Day/night gating
        night_req = ev.get("night")
        if night_req is True and not now.is_night:
            continue
        if night_req is False and now.is_night:
            continue
        require_flags = ev.get("require_flags") or {}
        if not all(now.flags.get(k) for k in require_flags):
            continue
        forbid_flags = ev.get("forbid_flags") or {}
        if any(now.flags.get(k) for k in forbid_flags):
            continue
        if ev.get("require_npc"):
            npc = now.npcs.get(ev["require_npc"], {})
            if not (npc.get("alive") and npc.get("at_base")):
                continue
        if ev.get("require_day") and now.day < ev["require_day"]:
            continue

        if ev.get("unique") or ev.get("story"):
            pool.append(ev)

    if pool:
        pool.sort(key=lambda e: (not e.get("unique"), not e.get("story"), random.random()))
        chosen = copy.deepcopy(pool[0])
    else:
        target_loc = location or now.location
        loc_pool: List[Dict[str, Any]] = []
        for ev in EVENTS:
            locs = ev.get("locations") or [target_loc]
            if target_loc not in locs:
                continue
            if ev.get("unique") and ev["id"] in now.seen_events:
                continue
            if now.day < ev.get("min_day", 1):
                continue
            if not _weather_match(ev, state):
                continue
            night_req = ev.get("night")
            if night_req is True and not now.is_night:
                continue
            if night_req is False and now.is_night:
                continue
            require_flags = ev.get("require_flags") or {}
            if not all(now.flags.get(k) for k in require_flags):
                continue
            forbid_flags = ev.get("forbid_flags") or {}
            if any(now.flags.get(k) for k in forbid_flags):
                continue
            if ev.get("require_npc"):
                npc = now.npcs.get(ev["require_npc"], {})
                if not (npc.get("alive") and npc.get("at_base")):
                    continue
            if ev.get("require_day") and now.day < ev["require_day"]:
                continue
            loc_pool.append(ev)
        if loc_pool:
            chosen = random.choices(
                loc_pool,
                weights=[e.get("weight", 1) for e in loc_pool],
                k=1,
            )[0]
            chosen = copy.deepcopy(chosen)
        else:
            chosen = copy.deepcopy(
                _e(
                    "default_wait",
                    "THE CITY BREATHES",
                    "Nothing useful happens for a minute. You are still alive because of that.",
                    [
                        _c("Gather your nerve", "red", morale=2),
                        _c("Search the corners", "blue", scrap=1, risk=0.2),
                        _c("Keep watch", "green", morale=3),
                        _c("Back to work", "yellow"),
                    ],
                    scene="streets",
                    locations=[target_loc],
                    weight=1,
                )
            )

    chosen["text"] = _apply_kid(state, chosen["text"])
    return chosen
