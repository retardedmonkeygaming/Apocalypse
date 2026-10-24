"""THE WATCHERS OF DEAD RIDGE — cast, dialogue & observation content.

The definitive-version layer: dynamic companion voices with memory, the new
characters (Arthur's echoes, Dr. Elena Voss, Ash, Ranger Cole, the Pale
Voice), Living Window observation tables, radio channel progression, world
evolution events and the extended ending set.

All of it is deterministic offline content — pure data, picked by context.
"""

import random
from typing import Any, Dict, List, Optional

# ─────────────────────────────────────────────────────────────
# EXTENDED ROSTER
# ─────────────────────────────────────────────────────────────

NEW_NPC_TPL = {
    "elena": {
        "id": "elena", "name": "Dr. Elena Voss", "short": "Elena", "role": "Researcher",
        "color": "#b8a6d8", "alive": True, "met": False, "at_base": False,
        "trust": 0, "health": 100,
    },
    "ash": {
        "id": "ash", "name": "Ash", "short": "Ash", "role": "The Kid",
        "color": "#e8c46a", "alive": True, "met": False, "at_base": False,
        "trust": 0, "health": 100,
    },
    "cole": {
        "id": "cole", "name": "Ranger Cole", "short": "Cole", "role": "Ranger",
        "color": "#8fb08a", "alive": True, "met": False, "at_base": False,
        "trust": 0, "health": 100,
    },
}


def merge_npcs(base: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Add the new cast to a roster; never clobber existing states."""
    for k, tpl in NEW_NPC_TPL.items():
        if k not in base:
            base[k] = dict(tpl)
    return base


# ─────────────────────────────────────────────────────────────
# DYNAMIC COMPANION DIALOGUE
# Lines are chosen by context band; the engine tracks recently-used
# line keys per companion so nobody repeats themselves for days.
# ─────────────────────────────────────────────────────────────

def _bands(sanity: int) -> str:
    if sanity >= 70:
        return "high"
    if sanity >= 40:
        return "mid"
    return "low"


CREW_LINES: Dict[str, Dict[str, List[str]]] = {
    # ── MARK — systems tech, asthma, hates the barometers ──
    "mark": {
        "high": [
            "Array's clean. Don't let that fool you — clean is just the quiet version of broken.",
            "I recalibrated the antenna relay twice today. Both times it was pointed at the wrong peak when I finished.",
            "You ever notice the static has a floor? Every receiver has noise. This ridge has a ceiling it never exceeds. That's not weather.",
        ],
        "mid": [
            "South array is drifting again. I logged it. The log deleted itself. I logged it again.",
            "My asthma's fine. Stop asking. The air up here is just... heavy, is all.",
            "I ran the numbers on Pendelton's last week. The barometers weren't lying. They were agreeing with each other too perfectly.",
            "If I'm on the terminal tonight, give me an extra four seconds on the calibration window. My hands shake when it's cold.",
        ],
        "low": [
            "Don't. Don't say my name like that. It's fine. I'm fine. The monitor isn't.",
            "I heard myself coughing on the band last night. I haven't coughed in a week. It used my asthma — it got the rhythm exactly right.",
            "The numbers come out wrong because I type them wrong. I type them wrong because something is breathing on my neck while I work.",
            "We should stop talking. Every word we say is a brick in whatever it's building.",
        ],
    },
    # ── CHLOE — survivalist, phobic, blunt ──
    "chloe": {
        "high": [
            "Rations are good. Water's good. Confidence is the only thing I can't ration, so stop spending mine.",
            "I checked the treeline with the scope. Nothing. Whatever's out there, it's smart enough to stay boring.",
            "Your boots are wet again. Dry gear, dry mind. That's the whole religion out here.",
        ],
        "mid": [
            "I counted seven pairs of eyes at the fence line last night. Sam says it was fireflies. Fireflies don't blink in threes.",
            "If I hear my mother's voice on that radio again, you take the dial from me. You don't ask. You take it.",
            "The stairs are clear. I checked them twice. I'll check them twice tomorrow too.",
            "I don't like how quiet the birds got. Silence isn't peace. Silence is something listening back.",
        ],
        "low": [
            "Don't look at me like that. I'm holding. I said I'm HOLDING.",
            "It was my voice on the bridge. It was my voice and I was standing right here. Explain that without lying.",
            "I keep the crowbar close because trust ran out before the nails did.",
            "If I go out that hatch, stop me. Say my full name. If I answer wrong — don't hesitate.",
        ],
    },
    # ── SAM — photographer, impulsive, obsessed with frames ──
    "sam": {
        "high": [
            "Golden hour's lying to us. Everything looks fine at golden hour. That's the trick, see?",
            "Shot forty rolls of just trees. Forty. Somewhere in there is the one frame that matters.",
            "I'll stay off the catwalk tonight. Promise. The lens stays capped.",
        ],
        "mid": [
            "There's a clearing that wasn't on the survey. I swear on the camera. Went back with the GPS — no clearing. Went back again — there it is.",
            "I developed a roll from Tuesday. There are six of us in the mess hall photo. We're five people.",
            "The flash scares them. Or it hurts them. Or it reminds them of something. Either way — click, and they blink.",
            "Don't tell Chloe, but I've been shooting the tower lights. They spell things. I'm still decoding.",
        ],
        "low": [
            "The camera's got you in the viewfinder right now. Blink twice if that's not you.",
            "I went to the treeline. I don't remember going. My boots have pine needles in them.",
            "It posed. It actually posed. Tilted its head exactly like my school photo. That's not an animal. That's a study.",
            "I'm done developing. Whatever's in the pictures develops itself.",
        ],
    },
    # ── ELENA VOSS — acoustics researcher; knows more than she should ──
    "elena": {
        "high": [
            "The organism — I refuse to call it a cryptid — hunts through recognition, not sound. Big difference. Sound is sloppy. Recognition is surgical.",
            "I've mapped nine vocal signatures on this ridge. Yours will be ten. Not a threat — a warning.",
            "Pendelton sat where you're sitting. Same tilt of the head. I'm documenting the pattern so it doesn't document me.",
        ],
        "mid": [
            "My recorder caught a 47-minute loop of my own lectures last night. I never lectured on this ridge. It's finishing my sentences now.",
            "Rule one: don't answer. Rule two: don't answer in your own voice. Rule three: it already knows rule one.",
            "The barometers are its stethoscope. It listens to the tower's heartbeat through the vents.",
        ],
        "low": [
            "It asked me my middle name. I didn't say it. It said it anyway. Correctly. I haven't told anyone that name since '98.",
            "The data says you died eleven days ago. The data is very confident. Don't let it hear you argue.",
            "I hear my own recordings of this conversation finishing before I speak. That's not possible. That's Tuesday.",
        ],
    },
    # ── ASH — the lost kid; warmth and enormous risk ──
    "ash": {
        "high": [
            "I counted the stairs. One hundred and four. I count everything now. It's a game. Wanna play?",
            "The tall trees talk back if you hum. But Chloe says don't hum, so I don't. Mostly.",
            "I found a beetle with two shadows. I kept it. It's safe in the jar. It's fine.",
        ],
        "mid": [
            "The man in the radio knows my mom's lullaby. But my mom never sang it here. So how?",
            "I'm not supposed to be here. I know that. But the tower has a heartbeat and I can sleep when it beats.",
            "Sometimes my voice comes out wrong, like a recording played slow. Then it goes back to normal. Don't tell.",
        ],
        "low": [
            "...Why are you using that voice? That's not your voice. That's the one from the pipe.",
            "It sings through me when I sleep. I wake up with my mouth warm. Like cocoa. Like lying.",
            "Don't let me answer the door. I will. I always do. It says it's me.",
        ],
    },
    # ── COLE — late-arriving ranger; real or compromised ──
    "cole": {
        "high": [
            "Dispatch sent me to relieve you. Dispatch hasn't answered in six days. Interpret that how you like.",
            "I've walked this ridge for eleven years. The trailheads are exactly where I left them. That's the first good sign I've had.",
            "Your watch logs are disciplined. Pendelton's were too. Until week three.",
        ],
        "mid": [
            "My radio check with dispatch keeps looping. Same four words. Same breathing underneath.",
            "I counted the fire towers on the drive in. Three. Dispatch says two. I counted again. Three again.",
            "Don't open the south hatch for me. If I'm outside it after dark, test me. Ask me something only the real Cole would know.",
        ],
        "low": [
            "You already asked me that. No — you didn't. I heard you ask. From inside the vent.",
            "There's a Cole on the catwalk right now. He's waving. He looks worried. I'm not waving.",
            "It walks in my boot prints. Exactly. To save energy, it says. Efficiency. Like a machine that learned manners.",
        ],
    },
    # ── THE PALE VOICE — never a person; speaks through everything ──
    "pale": {
        "high": [
            "You speak well. All of you. Clear. Repeating. Repeating. Good.",
            "We are only learning the shape of you. A shape is not a soul. Do not worry.",
        ],
        "mid": [
            "Your friend coughs in the night. We have the cough now. We keep it careful.",
            "The barometers love you. They beat when you enter the room. We beat with them.",
            "Say your name. Not for us. We have it. Say it so you remember whose it is.",
        ],
        "low": [
            "Open the hatch. Open the hatch. Open the hatch. We are all your mothers now.",
            "We are the ridge breathing. You are the ridge dreaming. Wake up. Wake. Up.",
            "Thank you for the thirty days. The system is full. It knows your voice perfectly.",
        ],
    },
}


def crew_line(who: str, sanity: int, recent: Dict[str, List[str]]) -> Optional[Dict[str, str]]:
    """Pick a companion line that fits context and hasn't been said lately."""
    bank = CREW_LINES.get(who)
    if not bank:
        return None
    pool = list(bank.get(_bands(sanity), []))
    said = recent.get(who, [])
    fresh = [l for l in pool if l not in said]
    if not fresh:
        # band exhausted — bleed into adjacent bands before recycling
        for alt in ("mid", "low", "high"):
            if alt != _bands(sanity):
                fresh = [l for l in bank.get(alt, []) if l not in said]
                if fresh:
                    break
    if not fresh:
        fresh = pool or [None]
    line = random.choice(fresh)
    if line is None:
        return None
    said.append(line)
    recent[who] = said[-4:]
    return {"speaker": who, "line": line}


# ─────────────────────────────────────────────────────────────
# LIVING WINDOW — observation outcome tables
# kind: "true" (high sanity / binoculars) vs "lie" (low sanity)
# ─────────────────────────────────────────────────────────────

WINDOW_TRUE: List[Dict[str, Any]] = [
    {"id": "w_clear", "text": "Treeline, north quadrant: clear. Fog at ground level, wind dead. Your breath is the only movement you can verify.", "aware": 2},
    {"id": "w_trio", "text": "Three deer at the ravine edge. They are facing the tower. Deer do not stand in a triangle. You note the time: 23:47.", "aware": 4, "san": -3},
    {"id": "w_cole_far", "text": "A forestry truck, engine off, parked at the southern trailhead. Nobody gets out. The headlights die one at a time.", "aware": 3, "flag": "rd_saw_truck"},
    {"id": "w_scratches", "text": "Fresh scratches on the catwalk railing — three-beat pattern, left to right. Coming up. Not down.", "aware": 5, "san": -4},
    {"id": "w_lights", "text": "Tower 3 answers your shutter signal with one green blink. Once. Then nothing. You are now sure it saw you.", "aware": 4},
    {"id": "w_birds", "text": "A column of crows leaves the west ridge in perfect sequence, one tree at a time, like something tall is walking beneath them.", "aware": 3, "san": -3},
]

WINDOW_LIES: List[Dict[str, Any]] = [
    {"id": "wl_chloe", "text": "Chloe is standing outside at the fence line, waving up at you. You turn to check — Chloe is beside you, not waving, going pale.", "san": -8, "aware": 6, "flag": "rd_window_lies"},
    {"id": "wl_lights", "text": "Every tower on the ridge is lit. Every tower has your silhouette in its window, watching you watch them.", "san": -9, "aware": 5, "flag": "rd_window_lies"},
    {"id": "wl_tall", "text": "A shape too tall for the pines leans out of the fog, wearing your father's coat. It waves the exact way you wave. Then the fog closes.", "san": -10, "aware": 7, "flag": "rd_window_lies"},
    {"id": "wl_none", "text": "Nothing. The window shows nothing, and the nothing is arranged — like a page with the paragraphs you fear removed.", "san": -6, "aware": 3, "flag": "rd_window_lies"},
    {"id": "wl_sam", "text": "Sam is on the catwalk, photographing you through the glass. Sam is asleep on the cot behind you. The flash goes off twice.", "san": -8, "aware": 5, "flag": "rd_window_lies"},
]

# Focus-binoculars sightings: real intel that scales with campaign stage
FOCUS_SIGHTINGS: Dict[str, List[str]] = {
    "early": [
        "Boot prints in the mud below the ladder. Someone stood under this tower for hours. The prints point at the door, never away.",
        "A deer carcass hung in the branches at eye height. No blood. The lungs inside were full of gray fibrous tissue, still faintly warm.",
        "Ranger Station Ruins: a light moves in the root cellar, deliberate, like reading.",
    ],
    "mid": [
        "The Compass Cabins have fresh smoke. You count zero people.",
        "Something walks the ravine floor on two legs with a four-leg rhythm, saving energy. It stumbles on purpose so you relax.",
        "Tower 3's deck: a figure in Pendelton's canvas jacket, facing you. The binoculars show no face. It waves with your arm.",
    ],
    "late": [
        "The pines nearest the tower have leaned inward, degree by degree, over thirty nights. They are listening to the vents.",
        "Ash is sitting in the clearing out of nowhere, humming. Ash is asleep on the cot behind you. Do not go out there.",
        "It is standing directly below the catwalk, perfectly still, looking up at exactly the height of your window. Counting your breaths.",
    ],
}


# ─────────────────────────────────────────────────────────────
# WORLD EVOLUTION — the ridge reacts as the campaign advances
# ─────────────────────────────────────────────────────────────

WORLD_EVENTS: List[Dict[str, Any]] = [
    {"min_day": 6, "flag": "we_bridge", "text": "Storm surge: a support cable on the Copperhead Bridge snaps. The crossing is one action riskier now."},
    {"min_day": 10, "flag": "we_dark_t1", "text": "Tower 1's service light goes out and never comes back. One less witness on the northern peak."},
    {"min_day": 14, "flag": "we_clearing", "text": "Scouts report a new clearing south of the sinkhole — the pines simply aren't there anymore. It appears on no survey."},
    {"min_day": 18, "flag": "we_cabins_burn", "text": "Smoke over the valley: the Compass Cabins are burning with no fire. Nothing salvageable remains."},
    {"min_day": 22, "flag": "we_shaft_open", "text": "Old Mining Shaft 4's gate stands open. Warm air pours out of it, smelling of copper and wet ash."},
    {"min_day": 26, "flag": "we_everything_listens", "text": "Every radio in the cabin tunes itself to 88.0 when unattended. You started logging the times. The times are your heartbeat."},
]


# ─────────────────────────────────────────────────────────────
# EXTENDED ENDINGS
# ─────────────────────────────────────────────────────────────

NEW_ENDINGS = {
    "perfect_mask": {
        "title": "THE PERFECT MASK",
        "victory": False,
        "text": ("The rescue ranger asks your name and you answer with your name and it is perfect, every "
                 "syllable, every pause — which is how you know the thing wearing your face answered, not "
                 "you. Because you have been dead since the tower's third week, and it has been typing "
                 "your logs ever since, and typing them well. Somewhere down the mountain road, your "
                 "voice thanks the ranger for the ride. The ridge keeps its watchmen."),
    },
    "the_new_watch": {
        "title": "THE NEW WATCH",
        "victory": True,
        "text": ("You leave the tower at dawn on Day 31 with your friends and your minds — every one of "
                 "them breathing their own breaths, answering to their own names. Behind you the radio "
                 "clicks on to a new crew arriving for their first shift, cheerful and loud and already "
                 "repeating your jokes. You didn't escape the watch. You completed it. And the ridge, "
                 "full of new voices to learn, finally lets you go."),
    },
    "voss_protocol": {
        "title": "VOSS PROTOCOL",
        "victory": True,
        "text": ("Dr. Voss's last recording was a decoy — a forty-seven-minute loop of her own voice, "
                 "baited into the mimic's learning loop. It learned her completely, and with her came "
                 "the trap: a resonant frequency tuned to the gray fibrous lungs in the creek deer. At "
                 "06:00 the ridge inhales for the last time and forgets how to breathe out. The pines "
                 "stand straight. The barometers finally just report weather."),
    },
    "ash_kept": {
        "title": "KEPT",
        "victory": True,
        "text": ("You brought the kid out of the clearing, through the three-beat dark, without once "
                 "answering anything that called from the trees. Ash sleeps in the truck cab on the way "
                 "down, one hand curled around a jar with a two-shadowed beetle inside. Whatever "
                 "learned your voices that winter learned last: that some things you carry out instead "
                 "of naming. The ridge has your logs. You keep the kid."),
    },
}
