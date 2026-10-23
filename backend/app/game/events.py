import random
from typing import Dict, Any, List

EVENTS: List[Dict[str, Any]] = [
    {
        "id": "scavenge_streets",
        "title": "EMPTY STREETS",
        "text": "You move through the silent streets. Something glints under a wrecked car.",
        "choices": [
            {"label": "Search the car", "key": "red", "effect": {"scrap": 2, "food": 1, "risk": 0.3}},
            {"label": "Keep moving", "key": "blue", "effect": {"morale": 5}},
            {"label": "Set an ambush", "key": "green", "effect": {"ammo": -1, "scrap": 3, "risk": 0.5}},
            {"label": "Return to base", "key": "yellow", "effect": {"location": "Home Base"}},
        ],
        "night_only": False,
    },
    {
        "id": "zombie_horde",
        "title": "HORDE APPROACHING",
        "text": "The low moan grows louder. Dozens of shapes shuffle toward you.",
        "choices": [
            {"label": "Fight", "key": "red", "effect": {"ammo": -3, "health": -15, "scrap": 1}},
            {"label": "Run", "key": "blue", "effect": {"health": -5, "morale": -10}},
            {"label": "Hide", "key": "green", "effect": {"risk": 0.4}},
            {"label": "Use distraction", "key": "yellow", "effect": {"scrap": -1}},
        ],
        "night_only": False,
    },
    {
        "id": "radio_signal",
        "title": "RADIO STATIC",
        "text": "Your radio crackles with a faint human voice...",
        "choices": [
            {"label": "Listen closely", "key": "red", "effect": {"morale": 10}, "gemini": True},
            {"label": "Reply", "key": "blue", "effect": {"morale": 5}, "gemini": True},
            {"label": "Ignore", "key": "green", "effect": {}},
            {"label": "Trace signal", "key": "yellow", "effect": {"location": "Radio Tower"}},
        ],
        "night_only": False,
    },
    {
        "id": "survivor",
        "title": "ANOTHER SURVIVOR",
        "text": "A figure steps out from the shadows, hands raised.",
        "choices": [
            {"label": "Talk", "key": "red", "effect": {"morale": 15}, "gemini": True},
            {"label": "Trade", "key": "blue", "effect": {"food": -1, "ammo": 2}},
            {"label": "Threaten", "key": "green", "effect": {"morale": -5, "scrap": 1}},
            {"label": "Walk away", "key": "yellow", "effect": {}},
        ],
        "night_only": False,
    },
    {
        "id": "night_ambush",
        "title": "NIGHT AMBUSH",
        "text": "Something is scratching at the barricade.",
        "choices": [
            {"label": "Shoot through the door", "key": "red", "effect": {"ammo": -2, "health": -5}},
            {"label": "Reinforce barricade", "key": "blue", "effect": {"scrap": -2}},
            {"label": "Stay silent", "key": "green", "effect": {"risk": 0.6}},
            {"label": "Flee out the back", "key": "yellow", "effect": {"location": "Streets", "health": -10}},
        ],
        "night_only": True,
    },
    {
        "id": "find_meds",
        "title": "MEDICAL SUPPLIES",
        "text": "A half-looted pharmacy. Cabinets still hold a few bottles.",
        "choices": [
            {"label": "Take everything", "key": "red", "effect": {"medkits": 2, "infection": -5, "risk": 0.4}},
            {"label": "Take only what you need", "key": "blue", "effect": {"medkits": 1}},
            {"label": "Search for antibiotics", "key": "green", "effect": {"infection": -15, "risk": 0.5}},
            {"label": "Leave it", "key": "yellow", "effect": {"morale": -5}},
        ],
        "night_only": False,
    },
    {
        "id": "rest",
        "title": "SAFE MOMENT",
        "text": "The area seems quiet for now.",
        "choices": [
            {"label": "Rest & heal", "key": "red", "effect": {"health": 20, "food": -1, "water": -1}},
            {"label": "Fortify position", "key": "blue", "effect": {"scrap": -1, "morale": 5}},
            {"label": "Keep watch", "key": "green", "effect": {"morale": 10}},
            {"label": "Move on", "key": "yellow", "effect": {}},
        ],
        "night_only": False,
    },
]

def get_random_event(is_night: bool) -> Dict[str, Any]:
    candidates = [e for e in EVENTS if e["night_only"] == is_night or not e["night_only"]]
    return random.choice(candidates).copy()