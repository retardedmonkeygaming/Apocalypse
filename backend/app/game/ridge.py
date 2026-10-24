"""THE WATCHERS OF DEAD RIDGE — standalone psychological horror story mode.

A 30-day fire-watch campaign layered on top of the existing engine.
Everything lives under world.flags["rd_*"] keys and reuses the player's
morale stat as SANITY, humanity as AWARENESS and fortification as the
tower's structural SEAL, so the main game is completely untouched.
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from backend.app.game.ridge_cast import (
    FOCUS_SIGHTINGS, NEW_ENDINGS, WINDOW_LIES, WINDOW_TRUE, WORLD_EVENTS,
    crew_line, merge_npcs,
)

RIDGE_ID = "dead_ridge"

# ─────────────────────────────────────────────────────────────
# COMPANIONS
# ─────────────────────────────────────────────────────────────


def ridge_npcs() -> Dict[str, Dict[str, Any]]:
    return {
        "mark": {
            "id": "mark", "name": "Mark Vance", "short": "Mark", "role": "Systems",
            "color": "#7ab8d4", "alive": True, "met": True, "at_base": True,
            "trust": 3, "health": 100,
        },
        "chloe": {
            "id": "chloe", "name": "Chloe Verner", "short": "Chloe", "role": "Survival",
            "color": "#c8d47a", "alive": True, "met": True, "at_base": True,
            "trust": 3, "health": 100,
        },
        "sam": {
            "id": "sam", "name": "Sam Ortega", "short": "Sam", "role": "Photo",
            "color": "#d4a07a", "alive": True, "met": True, "at_base": True,
            "trust": 3, "health": 100,
        },
    }


# ─────────────────────────────────────────────────────────────
# OVERWORLD NODES (15 sq km of Dead Ridge)
# ─────────────────────────────────────────────────────────────

NODES: Dict[str, Dict[str, Any]] = {
    "Fire-Tower 2": {
        "id": "Fire-Tower 2", "short": "TOWER 2", "risk": 0.0,
        "blurb": "Your base. A glass-paneled watchtower cabin above the pine canopy.",
    },
    "Fire-Tower 1": {
        "id": "Fire-Tower 1", "short": "TOWER 1", "risk": 0.35,
        "blurb": "Decommissioned northern peak. The desk drawer still sticks.",
    },
    "The Northern Ravine": {
        "id": "The Northern Ravine", "short": "RAVINE", "risk": 0.45,
        "blurb": "A 300-foot drop smelling of wet pine and old iron.",
    },
    "The Copperhead Bridge": {
        "id": "The Copperhead Bridge", "short": "BRIDGE", "risk": 0.5,
        "blurb": "A rusted steel suspension span swaying over the ravine.",
    },
    "The Compass Cabins": {
        "id": "The Compass Cabins", "short": "CABINS", "risk": 0.4,
        "blurb": "Four valley cabins arranged like the points of a compass.",
    },
    "Old Mining Shaft 4": {
        "id": "Old Mining Shaft 4", "short": "SHAFT 4", "risk": 0.65,
        "blurb": "A vertical limestone drop. Teeth marks line the generator vault.",
    },
    "Ranger Station Ruins": {
        "id": "Ranger Station Ruins", "short": "RUINS", "risk": 0.4,
        "blurb": "Charred foundations of the old headquarters. The root cellar is flooded.",
    },
    "Overturned Railcar": {
        "id": "Overturned Railcar", "short": "RAILCAR", "risk": 0.45,
        "blurb": "A derailed 1974 freight car rusted into the ravine floor.",
    },
    "Limestone Sinkhole": {
        "id": "Limestone Sinkhole", "short": "SINKHOLE", "risk": 0.55,
        "blurb": "A collapsing earth pit threading into the cave network.",
    },
}

# Viewport scene per overworld node — the center screen travels with you
NODE_SCENE = {
    "Fire-Tower 1": "ridge_loc_t1",
    "The Northern Ravine": "ridge_loc_ravine",
    "The Copperhead Bridge": "ridge_bridge",
    "The Compass Cabins": "ridge_cabins",
    "Old Mining Shaft 4": "ridge_mine",
    "Ranger Station Ruins": "ridge_loc_ruins",
    "Overturned Railcar": "ridge_loc_railcar",
    "Limestone Sinkhole": "ridge_loc_sinkhole",
}

MAP_ORDER = [
    "Fire-Tower 1", "The Northern Ravine", "The Copperhead Bridge",
    "The Compass Cabins", "Old Mining Shaft 4", "Ranger Station Ruins",
    "Overturned Railcar", "Limestone Sinkhole",
]

# ─────────────────────────────────────────────────────────────
# DOCUMENTS TAB (in-game database)
# ─────────────────────────────────────────────────────────────

DOCS: Dict[str, Dict[str, str]] = {
    "doc_01": {
        "name": "Log Entry #01 (Arthur Pendelton)",
        "text": (
            "\"They don't have vocal cords. I dissected one of the dead deer down by the creek. "
            "The lungs were filled with gray, fibrous tissue that vibrates when air passes through it. "
            "It doesn't mimic words because it understands them; it mimics words because it notices "
            "that when it makes a specific sound, we walk toward it. It's an acoustic trap. Like an "
            "anglerfish. I'm turning off my headset.\""
        ),
    },
    "codebook": {
        "name": "Forestry Codebook — Section 9",
        "text": (
            "SAFETY MANUAL AMENDMENT // UNCONVENTIONAL FAUNA  1. If an employee is observed walking "
            "toward the treeline with an irregular, asymmetric stride, do not call out to them. "
            "2. If a shortwave transmission contains your own voice speaking sentences you do not "
            "remember vocalizing, immediately recalibrate your receiver to a frequency divisible by three. "
            "3. The state of Pennsylvania does not operate a third fire-tower on the Dead Ridge. "
            "If you locate a structure designated 'Tower 3', do not climb it."
        ),
    },
    "incident_91": {
        "name": "Incident Summary Report (1991 Archive)",
        "text": (
            "PENNSYLVANIA FORESTRY COMMISSION // CLOSED FILES — Subject: Fatal Disappearance of Crew 4-B "
            "(Peak 2). Final recovery efforts at Fire-Tower 2 terminated. Responding rangers located no "
            "physical remains of watchmen Davies, Miller, or Albright. The tower cabin windows were entirely "
            "shattered outward from the inside. The station desktop contained seven unsubmitted weather logs. "
            "Audio spools indicate the crew spent their final 48 hours talking to what they believed were "
            "each other through the ventilation shafts, despite logbooks confirming they were all sitting in "
            "the same room at the time. Station permanently boarded up."
        ),
    },
    "cassette": {
        "name": "Cassette: Arthur's Dictation",
        "text": (
            "(Heavy breathing, tape clicks) \"It's Day 13. I haven't slept in ninety hours. Buster went "
            "missing down by the sinkhole last week, but I can hear him barking right outside the trapdoor. "
            "The thing is... Buster died when I was twelve. I buried him in my backyard in Ohio. Why is he "
            "barking outside my door in the Appalachians? The laptop keeps flashing new emails, but the "
            "cables are cut. I can see the copper lines blowing in the wind. Who is emailing me? I'm going "
            "to open the latch just a crack to see. I just want to hear him bark up close...\" (static)"
        ),
    },
    "freq_chart": {
        "name": "Local Frequency Analysis Chart",
        "text": (
            "Hand-annotated shortwave chart. Channel 14 = 6.205 MHz, Channel 88 = 9.330 MHz, "
            "Channel 104 = 11.895 MHz. Three frequencies divisible by three, exactly as the codebook "
            "demands. Marginalia in Pendelton's hand: '88 is not weather. 88 is breathing. It repeats "
            "every 47 minutes — one minute short of an hour, so it never quite lines up with the clock.'"
        ),
    },
    "skin_stitch": {
        "name": "Project Skin-Stitch Bio-Data",
        "text": (
            "MILITARY LOGISTICS ARCHIVE // 1974 — Classification: DARK. During routine freight survey of "
            "the Dead Ridge ravine, Crew 4-B recovered an unclassified, non-human skeleton structure "
            "embedded in the limestone: no vocal cords, no ocular sockets, an elongated torso capable of "
            "sustained compression. The skeleton was warm. All crew files were sealed after the recovery "
            "vehicle refused to start for eleven consecutive hours."
        ),
    },
}


# ─────────────────────────────────────────────────────────────
# AUTOMATED EMAIL TRIGGERS (ForestOS Inbox)
# ─────────────────────────────────────────────────────────────

EMAILS: List[Dict[str, Any]] = [
    {"id": "mail_t3", "day": 2, "frm": "NetAdmin-09@forestry.st",
     "subject": "REMINDER: Tower 3 Decommissioning",
     "body": ("Be advised that Fire-Tower 3 (Southern Peak) is no longer monitored by human personnel. "
              "If you observe structural lights flashing from the tower platform after dark, do not log it. "
              "It is a known electrical grounding loop caused by recent storms. Do not dispatch personnel to "
              "investigate the southern grid.")},
    {"id": "mail_echo", "day": 4, "frm": "NetAdmin-02@forestry.st",
     "subject": "SYSTEM ALERT: Ghost Echoes on Radar",
     "body": ("Automated maintenance is tracking a hardware glitch on the Tower 2 Doppler array. The radar "
              "may display a 300-meter 'void signature' that moves against the wind direction. If this "
              "signature intersects your cabin coordinates, do not look out the glass window.")},
    {"id": "mail_sam", "day": 4, "frm": "sam.photo@forestry.st", "cond": "sam_sent",
     "subject": "RE: Southern peak (no subject line)",
     "body": ("[17 ATTACHMENTS: IMG_0001.bmp ... IMG_0017.bmp] The pictures... they aren't of us. They're "
              "of something behind us. I'm leaving the camera on the desk. Don't follow me.")},
    {"id": "mail_t1", "day": 6, "frm": "automated-relay@forestry.st", "cond": "visited_t1",
     "subject": "Log Deficit Notice: Tower 1",
     "body": ("System logs indicate a manual input was attempted at the decommissioned Tower 1 terminal. "
              "Be advised the keyboard array at that station was completely removed in 2024. Do not reply "
              "to any command queries originating from the northern ravine line.")},
    {"id": "mail_chloe", "day": 9, "frm": "chloe.v@personalmail.net", "cond": "bridge_done",
     "subject": "(No Subject)",
     "body": ("I can hear you typing up there. I know you're mad at me about the gear on the bridge, but "
              "you don't have to keep playing that recording of my voice on the radio. It's not funny "
              "anymore. Turn it off or I'm sleeping in the truck tonight.")},
    {"id": "mail_rule3", "day": 10, "frm": "a.pendelton99@unknown.net",
     "subject": "The Rule of Three",
     "body": ("It learns by listening. It takes forty-eight hours to perfect the pitch of a voice. If it "
              "speaks your name, don't answer. If you answer, you validate its placement in the environment. "
              "Watch the barometers. When the pressure hits 960mb, it's not a storm. It's breathing.")},
    {"id": "mail_hq", "day": 12, "frm": "HQ-SafetyBoard@forestry.st",
     "subject": "RE: Missing Personnel Report #882",
     "body": ("Bureau records indicate no individual named Arthur Pendelton has ever been employed by the "
              "state forestry branch. Tower 2 has been vacant since the winter freeze of 1991. Please "
              "verify the employee ID badge on the desk console and submit a correction form immediately.")},
    {"id": "mail_we_see", "day": 15, "frm": "Unknown@-----.---", "cond": "low_sanity",
     "subject": "we see you",
     "body": ("The glass is thin. The wood is dry. You keep logging the pressure but you don't log the "
              "spacing between the trees. The trees are closer to the stairs than they were yesterday. "
              "Measure them. Measure the stairs.")},
    {"id": "mail_print", "day": 18, "frm": "NetAdmin-02@forestry.st",
     "subject": "CRITICAL SAFETY NOTICE: Voice Print Fraud",
     "body": ("Unauthorized shortwave frequency cloning detected within the Dead Ridge sector. If a team "
              "member contacts you using syntax that includes your full middle name or references a "
              "deceased relative, terminate the communication instantly.")},
    {"id": "mail_flash", "day": 22, "frm": "sam.photo@archive.org", "cond": "mine_done",
     "subject": "Look at the flash",
     "body": ("[ATTACHMENT ERROR: FILE CORRUPTED] The lens doesn't lie. It doesn't have skin, man. It just "
              "folds the clothes over the bone until it looks like a silhouette. If it stands still, it "
              "looks exactly like a tree trunk. Don't look at the woods when the sun goes down.")},
    {"id": "mail_vac", "day": 25, "frm": "automated-relay@forestry.st", "cond": "saw_fraud",
     "subject": "WEATHER ALERT: Total Vacuum Anomaly",
     "body": ("Barometric sensors at Peak 2 report a structural pressure drop to 950mb. This is "
              "mathematically impossible outside a Category 5 hurricane. If your physical barometers match "
              "this digital reading, seal the exterior iron hatch and deploy the manual deadbolts.")},
    {"id": "mail_evac", "day": 27, "frm": "HQ-Admin@forestry.st",
     "subject": "Operation Deep-Sweep Evacuation Route Change",
     "body": ("The transport vehicle will not stop at the trail marker. The ranger crew must navigate "
              "manually to the Copperhead Bridge checkpoint. If you encounter an individual wearing a JTF "
              "military uniform waiting at the bottom of your tower ladder, check their boots. Official "
              "personnel do not wear backward-facing laces.")},
    {"id": "mail_goodnight", "day": 30, "frm": "a.pendelton99@unknown.net",
     "subject": "Goodnight",
     "body": ("You did a good job with the logs. The system is full now. It knows your voice perfectly. "
              "Thank you for staying until the end of the shift. Now open the window and let us hear you "
              "breath.")},
]

ENDINGS = {
    **NEW_ENDINGS,
    "verified": {
        "title": "THE VERIFIED WATCH",
        "victory": True,
        "text": ("At exactly 06:00, the morning sun breaks cleanly over the ridge, melting the freezing "
                 "mist. The laptop prints: SHIFT COMPLETED // SUCCESSFUL RECORD. Heavy tires crunch against "
                 "the gravel below — a forestry 4x4. You and your friends pack your gear and descend the "
                 "ladder. On the mountain highway the radio plays clean, uncorrupted music. But as you "
                 "glance at the laptop in the passenger seat, a final notification chimes: a live photo of "
                 "your moving truck, taken from the treeline you just passed."),
    },
    "stolen_face": {
        "title": "THE STOLEN FACE",
        "victory": True,
        "text": ("You scramble into the back of the rescue vehicle as the ranger hits the gas. You look "
                 "over at Sam, whom you pulled from the mining shaft. He sits perfectly still, staring at "
                 "the floorboards. You ask if he's alright. He turns his head toward you with a slow, "
                 "mechanical click, eyes glassy and unblinking, and speaks in an exact clone of your own "
                 "voice: 'Yeah. I'm completely fine now.'"),
    },
    "hermit": {
        "title": "THE HERMIT OF PEAK 2",
        "victory": False,
        "text": ("The rescue truck honks its horn down on the trail, but you don't go down. You sit at the "
                 "laptop terminal, typing random string variables into the empty log windows. Your friends "
                 "are long gone, but the room is full of familiar voices. The shortwave radio keeps you "
                 "company, speaking to you in your own voice all night long, telling you ancient stories "
                 "about the hollow roots of the mountains. You are the permanent watchman of Dead Ridge now."),
    },
    "white_noise": {
        "title": "LOST IN THE WHITE NOISE",
        "victory": False,
        "text": ("The glass panels of the tower shatter inward simultaneously, showering the floor in "
                 "crystal shards. The freezing fog pours into the room, instantly extinguishing your "
                 "lantern. An impossibly long, ash-gray arm reaches through the dark, its fingers lightly "
                 "tracing your jawline. It opens its hollow, skinless face, and out comes your own voice, "
                 "comforting and soft: \"Don't worry. It's over now.\" The terminal blinks out into "
                 "absolute, permanent blackness."),
    },
}


class RidgeMode:
    """Self-contained driver for the Dead Ridge campaign."""

    def __init__(self, engine):
        self.e = engine
        self._pending_end: Optional[str] = None
        self._seg_override: Optional[str] = None

    # ── state shorthands ────────────────────────────────────

    @property
    def s(self):
        return self.e.state

    @property
    def F(self) -> Dict[str, Any]:
        return self.s.world.flags

    def _san(self, delta: int, note: str = ""):
        self.s.player.morale += int(delta)
        if note:
            self.s.log.append(note)
        self.s.clamp()
        if self.s.player.morale <= 0 and not self.s.game_over:
            # _san is sync — arm the ending and let the async entry points
            # (dispatch / sleep) flush it, so sanity-0 always ends the run.
            self._pending_end = "white_noise"

    def _aware(self, delta: int, note: str = ""):
        self.s.player.humanity += int(delta)
        if note:
            self.s.log.append(note)
        self.s.clamp()

    def alive(self, who: str) -> bool:
        return bool(self.s.world.npcs.get(who, {}).get("alive"))

    def _kill(self, who: str):
        npc = self.s.world.npcs.get(who)
        if npc:
            npc["alive"] = False
            npc["at_base"] = False
            self.s.log.append(f"† {npc['short']} is gone. The ridge keeps its own.")

    # ── boot ────────────────────────────────────────────────

    def start(self):
        s = self.s
        s.world.npcs = merge_npcs(ridge_npcs())
        s.world.location = "Fire-Tower 2"
        s.world.fortification = 3
        s.player.morale = 85        # SANITY
        s.player.humanity = 20      # HORDE AWARENESS
        s.player.infection = 0
        s.player.food = 8
        s.player.water = 8
        s.player.ammo = 4
        s.player.medkits = 1
        s.player.scrap = 2
        s.world.flags.update({
            "rd_inbox": [], "rd_docs": [], "rd_logs": 0, "rd_logs_missed": 0,
            "rd_cal": False, "rd_coeff": 1005, "rd_n": 982, "rd_v": 994, "rd_south": 988,
            "rd_fraud": False, "rd_saw_fraud": False, "rd_eclipse": False,
            "rd_tower3_seen": False, "rd_sam_sent": False, "rd_bridge_done": False,
            "rd_mine_done": False, "rd_t1": False, "rd_ruins": False, "rd_railcar": False,
            "rd_flare": False, "rd_lift_choice": "", "rd_hatch_sealed": False,
            "rd_visited": ["Fire-Tower 2"], "rd_cal_locked": False, "rd_siege_night": 0,
            # Definitive-version state
            "rd_learn": 0,              # how much the entity has learned of your voices
            "rd_recent": {},            # recent dialogue lines per companion (no repeats)
            "rd_focus_day": 0,          # binocular focuses used today
            "rd_world": {},             # world-evolution flags applied so far
            "rd_elena_met": False, "rd_ash_met": False, "rd_cole_met": False,
            "rd_ash_safe": False, "rd_voss_tape": False, "rd_cole_tested": False,
        })
        s.log = [
            "FORESTOS v4.2 booting... amber phosphor warm. Radio cold.",
            "Day 1. Ozone and wet pine. Fire-Tower 2, Dead Ridge. Arthur Pendelton vanished six days ago.",
            "His final manual log: 'The barometers are lying. They are mimicking the pressure.'",
            "Mark is on the monitor deck. Chloe checks the rations. Sam is photographing the treeline.",
        ]
        self._seg("H")
        self.hub()

    # ── presentation helper ────────────────────────────────

    def _show(self, title, text, choices, scene, confirm="REST", mode="event"):
        usable = []
        for c in choices:
            c = dict(c)
            if not c.pop("require", True):
                continue
            usable.append(c)
        if not usable:
            usable = [{"label": "Return", "effect": {"ridge": "hub"}}]
        self.e._show(title, text, usable, scene, mode, confirm)

    # ── main hub (the cabin) ───────────────────────────────

    def hub(self, _e=None):
        s = self.s
        s.world.location = "Fire-Tower 2"
        s.menu = "ridge"
        s.mode = "hub"
        clock = "ECLIPSE" if self.F.get("rd_eclipse") else ("NIGHT" if s.world.is_night else "DAY")
        sanity = s.player.morale
        text = (
            f"DAY {s.world.day}/30 · {clock} · SANITY {sanity} · AWARENESS {s.player.humanity}\n"
            f"TOWER SEAL {s.world.fortification}/10 · LOGS SUBMITTED {self.F.get('rd_logs', 0)}\n"
            f"BARO SYNC: {'CALIBRATED' if self.F.get('rd_cal') else 'DUE'} · "
            f"Mark chews a thumbnail. Chloe counts rations. Sam keeps the lens cap off.\n"
            "Below the catwalk, the pines move when the wind doesn't."
        )
        choices = [
            {"label": "Watch the Windows", "effect": {"ridge": "watch"}},
            {"label": "ForestOS Laptop", "effect": {"ridge": "laptop"}},
            {"label": "Shortwave Radio", "effect": {"ridge": "radio"}},
            {"label": "Expedition (Overworld)", "effect": {"ridge": "expedition"}},
        ]
        self._show("FIRE-TOWER 2 — WATCH CABIN", text, choices, "ridge_tower", "REST", "hub")
        self._seg("H" if not s.world.is_night else "n")

    # ── segment display intent (single source of truth) ─────

    def seg_char(self) -> str:
        s = self.s
        if s.game_over:
            return "P" if s.victory else "E"
        if s.combat.active:
            return "C"
        if self.sanity() <= 30:
            return "S"
        if self.F.get("rd_siege_night"):
            return "d"
        # The display itself glitches at low sanity — wrong char, briefly
        if self.sanity() < 45 and random.random() < 0.10:
            return random.choice("8_-")
        if self._seg_override:
            return self._seg_override
        mode = s.menu or s.mode
        if mode == "ridge_cal":
            return "b"
        if mode == "ridge":
            return "n" if s.world.is_night else "H"
        if mode == "ridge_radio":
            return "R"
        if mode == "ridge_laptop":
            return "F"
        if mode == "ridge_map":
            return "M"
        return "H"

    def _seg(self, char: str):
        self.s.seg = char
        self._seg_override = char

    def sanity(self) -> int:
        return self.s.player.morale

    # ── dispatch from engine.apply_effect ──────────────────

    async def dispatch(self, effect: Dict[str, Any]):
        action = effect.get("ridge")
        handlers = {
            "watch": self.watch, "laptop": self.laptop, "radio": self.radio,
            "expedition": self.expedition, "sleep": self.sleep, "hub": self.hub,
            "inbox": self.inbox, "radar": self.radar, "calibrate": self.calibrate,
            "submit_log": self.submit_log, "documents": self.documents,
            "cal_adjust": self.cal_adjust, "cal_lock": self.cal_lock,
            "tune": self.tune, "explore": self.explore,
            "beat": self.beat, "resolve": self.resolve, "end": self.end_by_choice,
            "docs_read": self.docs_read,
            "focus": self.focus, "crew": self.crew_menu, "talk_crew": self.talk_crew,
        }
        fn = handlers.get(action)
        self._seg_override = None  # each fresh action re-derives the display
        if fn:
            out = fn(effect)
            if asyncio.iscoroutine(out):
                await out
        await self._flush_end()

    async def _flush_end(self):
        """Run a death that was armed during a synchronous sanity update."""
        if self._pending_end and not self.s.game_over:
            eid = self._pending_end
            self._pending_end = None
            await self._end(eid)

    # ── WATCH THE WINDOWS ──────────────────────────────────

    async def watch(self, _e=None):
        s, F = self.s, self.F
        s.world.location = "Fire-Tower 2"
        s.menu = "ridge"
        day = s.world.day
        choices = []
        if day >= 2 and not F.get("rd_tower3_seen") and s.world.is_night:
            choices.append({"label": "Watch Tower 3 (South)", "effect": {"ridge": "beat", "beat": "tower3"}})
        choices.append({"label": "Focus Binoculars", "effect": {"ridge": "focus"}})
        choices.append({"label": "Crew Check-in", "effect": {"ridge": "crew"}})
        if s.world.is_night and self.sanity() < 60:
            choices.append({"label": "Scan the Treeline", "effect": {"ridge": "beat", "beat": "treeline"}})
        choices.append({"label": "Back to the Desk", "effect": {"ridge": "hub"}})

        F["rd_watch_pending"] = True
        text = (
            "You wipe the condensation from the glass with your sleeve. Fog rolls in slow sheets across "
            "the black pine canopy. Wind speed: near zero, though the treetops keep swaying.\n"
            "The southern peak is a charcoal smudge against the stars."
        )
        self._show("OBSERVATION DECK", text, choices, "ridge_tower", "BACK", "event")
        self._seg("H")

    async def beat(self, e: Dict[str, Any]):
        s, F = self.s, self.F
        b = e.get("beat")
        if b == "tower3":
            F["rd_tower3_seen"] = True
            choices = [
                {"label": "Send Sam to Investigate", "effect": {"ridge": "resolve", "res": "sam_sent"}},
                {"label": "Filter Out the Flashes", "effect": {"ridge": "resolve", "res": "ignore_t3"}},
            ]
            self._show(
                "THREE GREEN FLASHES — SOUTH PEAK",
                ("Midnight. Fire-Tower 3 is completely dark. Then three rhythmic green bursts fire from its "
                 "observation deck. Through the binoculars, spaced and deliberate:\n"
                 "H · E · L · P\n\nThe Forestry email called it a grounding loop. Grounding loops don't "
                 "spell anything."),
                choices, "ridge_tower3", "BACK", "event",
            )
            self.s.fx = "morse"
            self._seg("!")
        elif b == "treeline":
            self._san(-6, "Something stands at the treeline that is not a tree. It does not move when you blink.")
            self._aware(8)
            self.s.fx = "eerie"
            self._show("MOVEMENT — TREELINE",
                       ("A silhouette leans out from the pines: too tall, torso impossibly elongated, skin "
                        "the color of wet ash. It tilts its head in three quick beats — like someone "
                        "listening for a name. Then it steps back and is simply... a trunk."),
                       [{"label": "Step Back from the Glass", "effect": {"ridge": "hub"}}],
                       "ridge_entity", "BACK", "event")
            self._seg("S")
        elif b == "count":
            self._san(-3, "You count the trees between the ladder and the ravine edge. You count again. The number changes.")
            self._aware(3)
            self.hub()
        elif b == "catwalk":
            self._san(-2, "On the catwalk the air smells of copper. Scratches score the outer railing — fresh, three-beat rhythm.")
            self._aware(4)
            self.s.fx = "eerie"
            self.hub()
        else:
            self.hub()

    # ── LIVING WINDOW — focus, observation & the learning meter ──

    def _learn(self, amount: int, note: str = ""):
        """The entity learns with every voice it hears. Radio, answers, names."""
        F = self.F
        F["rd_learn"] = min(100, int(F.get("rd_learn", 0)) + amount)
        if note:
            self.s.log.append(note)

    def _stage(self) -> str:
        day = self.s.world.day
        if day <= 7:
            return "early"
        if day <= 18:
            return "mid"
        return "late"

    async def focus(self, _e=None):
        """Binoculars on the Living Window: real intel if your mind is steady,
        fabricated silhouettes if it isn't. Costs a look (awareness)."""
        s, F = self.s, self.F
        s.menu = "ridge"
        if F.get("rd_focus_day") == s.world.day:
            self.s.log.append("Your eyes won't focus again tonight. The lenses swim with afterimages.")
            self.hub()
            return
        F["rd_focus_day"] = s.world.day

        sanity = self.sanity()
        stage = self._stage()
        if sanity >= 50:
            sight = random.choice(FOCUS_SIGHTINGS[stage])
            self._aware(4, f"── BINOCULARS ({stage.upper()}) ──")
            self.s.log.append(sight)
            self._san(-2)
            self.s.fx = "eerie" if stage != "early" else ""
            title = "LIVING WINDOW — FOCUS LOCKED"
        else:
            lie = random.choice(WINDOW_LIES)
            self._san(lie.get("san", -6), "── BINOCULARS — the glass lies to you ──")
            self._aware(lie.get("aware", 4), lie["text"])
            if lie.get("flag"):
                F[lie["flag"]] = True
            self.s.fx = "eerie"
            title = "LIVING WINDOW — PERCEPTION FRACTURE"
            # Sometimes the lie shows you something that looks right at the glass
            if random.random() < 0.30:
                self.s.log.append("Something slams the pane. The glass is intact. It isn't.")
                self.s.fx = "scare"
                self._san(-4)
                self._aware(6)
                self._seg("d")

        choices = [{"label": "Lower the Binoculars", "effect": {"ridge": "hub"}}]
        if sanity < 50:
            choices.insert(0, {"label": "Look Again (It Wasn't Real)", "effect": {"ridge": "beat", "beat": "count"}})
        self._show(title, self.s.log[-1], choices, "ridge_tower", "BACK", "event")
        self._seg("U")

    async def crew_menu(self, _e=None):
        """Living dialogue: each companion answers from their own head."""
        s, F = self.s, self.F
        s.menu = "ridge"
        party = [p for p in s.world.npcs.values()
                 if p.get("alive") and p.get("at_base") and p.get("id") in ("mark", "chloe", "sam", "elena", "ash", "cole")]
        recent = F.get("rd_recent", {})
        sanity = self.sanity()
        lines, choices = [], []
        for p in party:
            ln = crew_line(p["id"], sanity, recent)
            if ln:
                lines.append(f"{p['short']}: \"{ln['line']}\"")
                choices.append({"label": f"Ask {p['short']}", "effect": {"ridge": "talk_crew", "who": p["id"]}})
            if len(lines) >= 3:
                break
        F["rd_recent"] = recent
        if not lines:
            lines = ["The cabin is quiet except for the radio's floor of static."]
        choices.append({"label": "Back to the Desk", "effect": {"ridge": "hub"}})
        self._show("CREW CHECK-IN — THE CABIN SPEAKS", "\n".join(lines), choices, "ridge_tower", "BACK", "event")
        self._seg("H")

    async def talk_crew(self, e: Dict[str, Any]):
        s, F = self.s, self.F
        who = e.get("who", "mark")
        recent = F.get("rd_recent", {})
        ln = crew_line(who, self.sanity(), recent)
        F["rd_recent"] = recent
        npc = s.world.npcs.get(who, {"short": who})
        text = f"{npc.get('short', who).upper()}: \"{ln['line']}\"" if ln else f"{npc.get('short', who)} says nothing."
        # Talking aloud teaches the ridge: it learns fastest from its favorites
        self._learn(2, "The ridge listens to every word. It keeps them.") if who in ("ash", "cole") else self._learn(1)
        if self.sanity() < 40 and random.random() < 0.35:
            text += "\n\nFor half a second the cadence is wrong — a beat late, like a held breath between words."
            self.s.fx = "eerie"
        choices = [{"label": "Back to the Desk", "effect": {"ridge": "hub"}}]
        self._show(f"{npc.get('short', who).upper()} — CREW", text, choices, "ridge_tower", "BACK", "event")

    # ── FORESTOS LAPTOP ────────────────────────────────────

    async def laptop(self, _e=None):
        s, F = self.s, self.F
        s.world.location = "Fire-Tower 2"
        s.menu = "ridge_laptop"
        unread = sum(1 for m in F.get("rd_inbox", []) if not m.get("read"))
        cal_state = "CALIBRATED" if F.get("rd_cal") else "SYNC DUE"
        text = (
            "FORESTOS v4.2 — amber phosphor hums. The desktop is cluttered with .LOG files and one "
            f"unread notification badge. BAROMETRIC ENGINE: {cal_state}.\n"
            "The dock shows: INBOX, WEATHERRADAR, CALIBRATION, LOGENGINE, DOCUMENTS."
        )
        choices = [
            {"label": f"Inbox ({unread} unread)", "effect": {"ridge": "inbox"}},
            {"label": "Barometric Calibration", "effect": {"ridge": "calibrate"}},
            {"label": "Log Engine", "effect": {"ridge": "submit_log"}},
            {"label": "WeatherRadar / Documents", "effect": {"ridge": "radar"}},
        ]
        self._show("FORESTOS v4.2 — LAPTOP", text, choices, "ridge_laptop", "CLOSE LID", "event")
        self._seg("F")

    async def inbox(self, _e=None):
        F = self.F
        F["rd_page"] = int(F.get("rd_page", 0))
        mail: List[Dict[str, Any]] = list(reversed(F.get("rd_inbox", [])))
        if not mail:
            self.s.log.append("The inbox is empty. For now.")
            await self.laptop()
            return
        pages = max(1, (len(mail) + 3) // 4)
        page = F["rd_page"] % pages
        F["rd_page"] = (page + 1) % pages
        shown = mail[page * 4: page * 4 + 4]
        lines = [f"[{i + 1 + page * 4}] {m['frm']} — {m['subject']}" for i, m in enumerate(shown)]
        choices = []
        for m in shown:
            m["read"] = True
            preview = m["body"][:150] + ("..." if len(m["body"]) > 150 else "")
            choices.append({"label": f"Open: {m['subject'][:22]}", "effect": {
                "ridge": "resolve", "res": "mail", "mail_id": m["id"], "preview": preview,
            }})
        self._show(f"FORESTOS INBOX — PAGE {page + 1}/{pages}",
                   "\n".join(lines) + "\n\nOpen a message, or CONFIRM to cycle pages.",
                   choices, "ridge_laptop", "BACK", "event")
        self._seg("F")

    async def radar(self, _e=None):
        s, F = self.s, self.F
        day = s.world.day
        if day >= 19:
            body = ("OUT OF RANGE // SENSOR ARRAYS COMPROMISED.\n"
                    "The radar engine renders nothing but that line of amber text. Somewhere out there, "
                    "something is tearing down the sensor masts one by one.")
            self._aware(6)
        else:
            anomaly = "MOVING AGAINST THE WIND" if day >= 8 else "nominal"
            body = (
                "WEATHERRADAR v1.9 — a grid overlay of the ridge. Density vectors crawl west to east.\n"
                f"EXCEPT: one circular mass, 300m wide, sits dead-center over Tower 2 and reports "
                f"{anomaly}.\nOutside the glass, the sky is bone dry."
            )
        self.s.fx = "static" if day >= 19 else ""
        choices = [
            {"label": "Mark: Analyze the Anomaly", "effect": {"ridge": "resolve", "res": "radar_mark"}},
            {"label": "Toggle Monitor Backlight", "effect": {"ridge": "resolve", "res": "radar_off"}},
            {"label": "Back", "effect": {"ridge": "laptop"}},
        ]
        self._show("WEATHERRADAR — SENSOR GRID", body, choices, "ridge_radar", "BACK", "event")
        self._seg("F")

    async def documents(self, _e=None):
        await self._docs_page(0)

    async def docs_read(self, e: Dict[str, Any]):
        await self._docs_page(int(e.get("page", 0)))

    async def _docs_page(self, page: int):
        s, F = self.s, self.F
        docs = F.get("rd_docs", [])
        if not docs:
            self.s.log.append("No documents recovered yet. The ridge hides its files well.")
            await self.laptop()
            return
        pages = max(1, (len(docs) + 3) // 4)
        page = page % pages
        shown = docs[page * 4: page * 4 + 4]
        lines = [f"· {DOCS[d]['name']}" for d in shown if d in DOCS]
        choices = [
            {"label": f"Read: {DOCS[d]['name'][:24]}", "effect": {"ridge": "resolve", "res": "doc", "doc_id": d}}
            for d in shown if d in DOCS
        ]
        choices.append({"label": f"Next Page ({page + 2}/{pages})", "effect": {"ridge": "docs_read", "page": page + 1}})
        while len(choices) < 4:
            choices.append({"label": "Back to Laptop", "effect": {"ridge": "laptop"}})
        self._show(f"DOCUMENTS TAB — PAGE {page + 1}/{pages}",
                   "Recovered files from the ridge. Everything here was found by someone who is now missing.\n\n"
                   + "\n".join(lines), choices, "ridge_laptop", "BACK", "event")
        self._seg("F")

    # ── BAROMETRIC CALIBRATION MINI-GAME ───────────────────

    def _regen_arrays(self):
        F = self.F
        F["rd_n"] = random.randint(972, 992)
        F["rd_v"] = random.randint(986, 1000)
        hunting = self.s.player.humanity >= 40 or random.random() < 0.35
        F["rd_fraud"] = bool(hunting and self.s.world.day >= 6)
        F["rd_south"] = 1013 if F["rd_fraud"] else random.randint(968, 996)
        if F["rd_fraud"]:
            self.F["rd_saw_fraud"] = True
        target = self._target()
        F["rd_coeff"] = target + random.choice([-12, -9, -6, 8, 11, 14])

    def _target(self) -> int:
        """Median of the *honest* arrays. The South array is excluded when mimicking."""
        F = self.F
        vals = [F.get("rd_n", 982), F.get("rd_v", 994)]
        if not F.get("rd_fraud"):
            vals.append(F.get("rd_south", 988))
        vals.sort()
        return vals[len(vals) // 2]

    async def calibrate(self, _e=None):
        s, F = self.s, self.F
        if not F.get("rd_arrays_ready"):
            self._regen_arrays()
            F["rd_arrays_ready"] = True
        self._cal_menu()

    def _cal_menu(self):
        s, F = self.s, self.F
        self.s.menu = "ridge_cal"
        coeff = F.get("rd_coeff", 1005)
        target = self._target()
        dev = coeff - target
        south_note = (
            "⚠ MIMICRY INTERFERENCE DETECTED — EXCLUDE FROM MEDIAN" if F.get("rd_fraud")
            else "STABLE"
        )
        text = (
            "[FORESTOS V4.2] — BAROMETRIC CALIBRATION ENGINE\n"
            f"NORTH ARRAY: {F.get('rd_n')} mb — STABLE\n"
            f"VALLEY COIL: {F.get('rd_v')} mb — STABLE\n"
            f"SOUTH ARRAY: {F.get('rd_south')} mb — {south_note}\n\n"
            f"CURRENT DIGITAL DEVIATION: {dev:+d} mb {'<-- CRITICAL IMBALANCE' if abs(dev) > 2 else '<-- SYNC'}\n"
            "Steer the correction coefficient toward sync, then LOCK SYNC.\n"
            "When the South array is flagged, the honest median comes from North and Valley alone."
        )
        choices = [
            {"label": "<< Coeff -10", "effect": {"ridge": "cal_adjust", "delta": -10}},
            {"label": "< Coeff -1", "effect": {"ridge": "cal_adjust", "delta": -1}},
            {"label": "> Coeff +1", "effect": {"ridge": "cal_adjust", "delta": 1}},
            {"label": ">> Coeff +10", "effect": {"ridge": "cal_adjust", "delta": 10}},
        ]
        self._show("BAROMETRIC CALIBRATION", text, choices, "ridge_radar", "LOCK SYNC", "event")
        self._seg("b")

    async def cal_adjust(self, e: Dict[str, Any]):
        self.F["rd_coeff"] = int(self.F.get("rd_coeff", 1005)) + int(e.get("delta", 0))
        await self.calibrate()

    async def cal_lock(self, _e=None):
        s, F = self.s, self.F
        coeff = F.get("rd_coeff", 1005)
        target = self._target()
        dev = abs(coeff - target)
        F["rd_arrays_ready"] = False

        if dev <= 2:
            F["rd_cal"] = True
            s.log.append(f"── BARO SYNC LOCKED ({coeff}mb, Δ{dev}) — enviro-log integrity confirmed. ──")
            self._san(5)
            s.fx = "success"
            await self.e.buzzer.success()
            await self.laptop()
        else:
            s.log.append(f"── SYNC FAILED (Δ{dev}mb). The speakers blast shortwave static. ──")
            self._san(-15, "-15 SANITY. The voices on the band count your breaths.")
            self._aware(15, "AWARENESS SPIKES. Something heavy settles onto the glass catwalk.")
            s.fx = "static"
            await self.e.buzzer.danger()
            if F.get("rd_fraud") and abs(coeff - 1013) <= 2:
                s.log.append("You locked onto the South array's 1013mb exhalation. The lower vents HISS open.")
                self._aware(15)
                self._damage_tower(1, "Vent interlock compromised.")
            await self.laptop()

    # ── LOG ENGINE ─────────────────────────────────────────

    async def submit_log(self, _e=None):
        s, F = self.s, self.F
        if not F.get("rd_cal"):
            self._show("LOG ENGINE — REJECTED",
                       ("CRITICAL ERROR: MANUAL UPDATE REQUIRED // BAROMETRIC SYNC NOT VERIFIED // "
                        "SUBMIT CALIBRATION BEFORE THE ENVIRO-LOG OR FORFEIT STATION POSITION."),
                       [{"label": "Run Calibration Now", "effect": {"ridge": "calibrate"}},
                        {"label": "Back", "effect": {"ridge": "laptop"}}],
                       "ridge_laptop", "BACK", "event")
            self._seg("!")
            return

        code = self._log_code()
        text = (
            "LOGENGINE v2.1 — DAILY ENVIRO-LOG\n"
            f"VALIDATION STRING REQUIRED: {code}\n\n"
            "Type the phrase exactly as printed. The system will not accept partials. "
            "Arthur's last entry was three words long and nobody believes the file exists."
        )
        choices = [
            {"label": f"Enter: {code}", "effect": {"ridge": "resolve", "res": "log_ok", "code": code}},
            {"label": f"Enter: {code.lower()}", "effect": {"ridge": "resolve", "res": "log_bad"}},
            {"label": "Enter: ARTHUR SENT ME", "effect": {"ridge": "resolve", "res": "log_arthur"}},
            {"label": "Back", "effect": {"ridge": "laptop"}},
        ]
        self._show("LOG ENGINE — MANUAL ENTRY", text, choices, "ridge_laptop", "BACK", "event")
        self._seg("L")

    def _log_code(self) -> str:
        day = self.s.world.day
        return f"DR-{day:02d}-{(day * 7919) % 997:03d}"

    # ── SHORTWAVE RADIO ────────────────────────────────────

    async def radio(self, _e=None):
        s = self.s
        s.world.location = "Fire-Tower 2"
        s.menu = "ridge_radio"
        creepy = self.sanity() < 50
        text = (
            "ANALOG SHORTWAVE — three channels carved into the brass dial with a knife tip.\n"
            f"14 (6.205 MHz) · 88 (9.330 MHz) · 104 (11.895 MHz)\n"
            + ("Beneath the static, something breathes in time with your own lungs." if creepy
               else "Just static tonight. Mostly static.")
        )
        choices = [
            {"label": "Channel 14", "effect": {"ridge": "tune", "ch": 14}},
            {"label": "Channel 88", "effect": {"ridge": "tune", "ch": 88}},
            {"label": "Channel 104", "effect": {"ridge": "tune", "ch": 104}},
            {"label": "Back to the Desk", "effect": {"ridge": "hub"}},
        ]
        self._show("SHORTWAVE RECEIVER", text, choices, "ridge_radio", "BACK", "event")
        self._seg("R")

    async def tune(self, e: Dict[str, Any]):
        s, F = self.s, self.F
        ch = int(e.get("ch", 14))
        day = s.world.day
        self.s.fx = "static" if self.sanity() >= 50 else "eerie"

        # Every listen feeds the learning loop
        learn_hit = 3 if ch == 88 else 2
        self._learn(learn_hit)

        # HIJACK: once it has learned enough voices it owns the channel.
        # The first hijack is guaranteed; later ones are probabilistic.
        hijacked_any = any(F.get(k) for k in F if str(k).startswith("rd_hijack_"))
        hijack_chance = 0.4 if hijacked_any else 1.0
        if F.get("rd_learn", 0) >= 55 and not F.get(f"rd_hijack_{ch}") and random.random() < hijack_chance:
            F[f"rd_hijack_{ch}"] = True
            who = random.choice(["mark", "chloe", "sam"])
            npc = s.world.npcs.get(who, {})
            if npc.get("alive"):
                self._san(-18, f"── CHANNEL {ch} HIJACKED: {npc.get('short', who)}'s voice, perfect, asking you a question only {npc.get('short', who)} would know ──")
                self._aware(12)
                choices = [
                    {"label": "Answer It", "effect": {"ridge": "resolve", "res": "answered", "ch": ch}},
                    {"label": "Kill the Power (Don't Answer)", "effect": {"ridge": "resolve", "res": "silent", "ch": ch}},
                ]
                self._show(f"CHANNEL {ch} — IT LEARNED {npc.get('short', who).upper()}",
                           (f"The static resolves into {npc.get('short', who)} — not recorded, present, breathing. "
                            f"It tells you something {npc.get('short', who)} said to you alone, in a private hour, "
                            "and it waits, politely, for your reply.\n\nThe Rule of Three: if it speaks your name, don't answer."),
                           choices, "ridge_radio", "BACK", "event")
                self.s.fx = "eerie"
                self._seg("!")
                return

        if ch == 88 and day >= 10 and not F.get("rd_radio_crisis"):
            F["rd_radio_crisis"] = True
            choices = [
                {"label": "Decrypt Audio (3 hrs)", "effect": {"ridge": "resolve", "res": "decrypt"}},
                {"label": "Smash the Dial", "effect": {"ridge": "resolve", "res": "smash"}},
            ]
            self._show("CHANNEL 88 — STITCHED VOICES",
                       ("The radio clicks on by itself. It is broadcasting Mark and Chloe arguing down at the "
                        "cabins — except the argument is stitched from phrases they used days ago. Pauses "
                        "land one beat too late. The laughter has no breath in it."),
                       choices, "ridge_radio", "BACK", "event")
            self._seg("!")
            return

        if ch == 104 and day >= 12 and "freq_chart" not in F.get("rd_docs", []):
            F.setdefault("rd_docs", []).append("freq_chart")
            s.log.append("◆ Document recovered: Local Frequency Analysis Chart.")
            self._san(-4, "The channel reads out your own service record — including next week's shift.")
            self._show("CHANNEL 104 — YOUR OWN VOICE",
                       ("A calm broadcast reads the Dead Ridge service roster. Then it reads today's "
                        "entries — your entries — aloud, in your voice, slightly ahead of your memory. "
                        "It clears its throat. It has no throat."),
                       [{"label": "Kill the Power", "effect": {"ridge": "hub"}}],
                       "ridge_radio", "BACK", "event")
            self._seg("S")
            return

        # Generic listening outcomes
        if self.sanity() < 50:
            self._san(-6, "The static forms your mother's voice. You answer 'what?' under your breath. It stops.")
            self._aware(8)
            s.log.append("SANITY BELOW 50 — the band is learning your cadence.")
        elif ch == 14:
            self._san(3, "Channel 14: weather band. Rain reports from counties that no longer answer.")
        elif ch == 88:
            self._san(-3, "Channel 88: a low, wet breathing. It pauses when you do.")
            self._aware(5)
        else:
            self._san(2, "Channel 104: numbers, calmly recited, in no language you know.")
        self.hub()

    # ── EXPEDITIONS (overworld sandbox) ────────────────────

    async def expedition(self, _e=None):
        s, F = self.s, self.F
        s.menu = "ridge_map"
        F["rd_mappage"] = int(F.get("rd_mappage", 0))
        pages = max(1, (len(MAP_ORDER) + 3) // 4)
        page = F["rd_mappage"] % pages
        F["rd_mappage"] = (page + 1) % pages
        shown = MAP_ORDER[page * 4: page * 4 + 4]
        day = s.world.day
        clock = "NIGHT" if s.world.is_night else "DAY"
        if F.get("rd_eclipse"):
            clock = "ECLIPSE"
        lines = [f"· {n} — {NODES[n]['risk'] * 100:.0f}% exposure" for n in shown]
        if day == 5 and not F.get("rd_bridge_done"):
            lines.append("→ THE COPPERHEAD BRIDGE: the solar batteries are dying. Decide now.")
        if day == 21 and not F.get("rd_mine_done"):
            lines.append("→ OLD MINING SHAFT 4: the master breaker just tripped. The laptop is dark.")
        text = (
            f"OVERWORLD — {clock} · DAY {day}/30 · MAP PAGE {page + 1}/{pages}\n"
            "15 square kilometers of Appalachian pine. You must be back at a tower before midnight.\n\n"
            + "\n".join(lines)
        )
        choices = [{"label": n, "effect": {"ridge": "explore", "node": n}} for n in shown]
        self._show("EXPEDITION — DEAD RIDGE OVERWORLD", text, choices, "ridge_forest", "BACK", "event")
        self._seg("M")

    async def explore(self, e: Dict[str, Any]):
        s, F = self.s, self.F
        node = e.get("node", "")
        day = s.world.day
        s.world.location = node
        if node not in F.get("rd_visited", []):
            F["rd_visited"].append(node)
        s.log.append(f"── EXPEDITION: {node.upper()} ──")
        s.menu = ""
        # The center viewport travels: switch the scene to the destination NOW
        s.scene = NODE_SCENE.get(node, "ridge_forest")

        # Character encounters — the world grows a cast around your behavior
        if node == "Ranger Station Ruins" and day >= 8 and not F.get("rd_elena_seen"):
            F["rd_elena_seen"] = True
            self._show("THE ROOT CELLAR — A RECORDER IS RUNNING",
                       ("Under the stone hearth, wedged behind water-damaged files, a woman in a ruined lab coat "
                        "is trying to pry a filing cabinet across a door. Dr. Elena Voss. Acoustic researcher, "
                        "missing since week one. She talks fast and without blinking: 'It finishes my sentences. "
                        "It finishes them CORRECTLY. Take me to your tower or give me something heavy.'"),
                       [{"label": "Take Her In (She Knows This)", "effect": {"ridge": "resolve", "res": "elena_take"}},
                        {"label": "Leave Her the Crowbar", "effect": {"ridge": "resolve", "res": "elena_leave"}}],
                       NODE_SCENE.get(node, "ridge_forest"), "BACK", "event")
            self._seg("U")
            return
        if node == "Limestone Sinkhole" and F.get("rd_world", {}).get("we_clearing") and not F.get("rd_ash_met"):
            self._show("THE CLEARING SOUTH OF THE SINKHOLE",
                       ("The pines simply stop. In the clearing a child sits cross-legged with a jar, humming. "
                        "Ash — the kid from the missing-persons board, gone three weeks, dry and warm and calm. "
                        "'I know the way out,' Ash says. 'It doesn't like me repeating things.'"),
                       [{"label": "Bring Ash to the Tower", "effect": {"ridge": "resolve", "res": "ash_take"}},
                        {"label": "Mark the Spot and Go", "effect": {"ridge": "resolve", "res": "ash_leave"}}],
                       NODE_SCENE.get(node, "ridge_forest"), "BACK", "event")
            self._seg("U")
            return

        # Scripted day beats take priority
        if node == "The Copperhead Bridge" and day == 5 and not F.get("rd_bridge_done"):
            await self._beat_bridge()
            return
        if node == "Old Mining Shaft 4" and day >= 21 and not F.get("rd_mine_done"):
            await self._beat_mine()
            return
        if node == "The Compass Cabins" and day in (14, 15, 16) and not F.get("rd_cabins_done"):
            await self._beat_cabins()
            return
        if node == "The Compass Cabins" and day == 24 and not F.get("rd_sensor_done"):
            await self._beat_sensor()
            return
        if node == "Fire-Tower 1" and not F.get("rd_t1"):
            await self._site_t1()
            return
        if node == "Ranger Station Ruins" and not F.get("rd_ruins"):
            await self._site_ruins()
            return
        if node == "Overturned Railcar" and not F.get("rd_railcar"):
            await self._site_railcar()
            return
        if node == "Limestone Sinkhole" and not F.get("rd_flare"):
            await self._site_sinkhole()
            return

        # Generic node excursion
        risk = NODES.get(node, {}).get("risk", 0.4)
        if s.world.is_night:
            risk += 0.2
        if random.random() < risk:
            self._san(-8, "Something follows you through the pines, one tree at a time.")
            self._aware(10)
            s.fx = "eerie"
            self._show(f"{node.upper()} — YOU ARE NOT ALONE",
                       ("Branches snap in a three-beat rhythm behind you. You walk faster; the rhythm keeps "
                        "pace exactly. By the time you reach the ladder your flashlight is dimming and your "
                        "hands won't stop shaking."),
                       [{"label": "Climb Back to the Cabin", "effect": {"ridge": "hub"}}],
                       NODE_SCENE.get(node, "ridge_forest"), "BACK", "event")
            self._seg("S")
        else:
            found = random.choice(["rations", "battery cells", "scrap copper", "clean water"])
            amt = 2 if (node == "The Compass Cabins" and self.alive("chloe")) else 1
            if found == "rations":
                s.player.food += amt
            elif found == "clean water":
                s.player.water += amt
            else:
                s.player.scrap += amt
            s.log.append(f"Quiet excursion. Salvaged {amt} {found}. The forest watched and said nothing.")
            self._san(2)
            # Show the place itself before returning — the view IS the reward
            sc = NODE_SCENE.get(node, "ridge_forest")
            self._show(f"{node.upper()} — QUIET EXCURSION",
                       (f"You work the site with the lantern low. Salvaged {amt} {found}.\n"
                        "Somewhere behind the fog, a branch snaps in a three-beat rhythm and stops "
                        "when you stop. The tower ladder is a straight line home."),
                       [{"label": "Climb Back to the Tower", "effect": {"ridge": "hub"}}],
                       sc, "BACK", "event")
            self._seg("M")

    # ── Scripted beats ─────────────────────────────────────

    async def _beat_bridge(self):
        s, F = self.s, self.F
        F["rd_bridge_done"] = True
        choices = [
            {"label": "Run Toward the Forward Scream", "effect": {"ridge": "resolve", "res": "bridge_a"}},
            {"label": "Turn Back to the Vehicle", "effect": {"ridge": "resolve", "res": "bridge_b"}},
        ]
        self._show("THE COPPERHEAD BRIDGE — MIDSPAN",
                   ("Halfway across the rusted steel span, an abandoned Forestry truck: doors wide open, "
                    "dashboard radio blasting white noise. The fog rolls in instantly. Visibility: zero.\n"
                    "From the FRONT of the bridge, Chloe screams.\n"
                    "Simultaneously, from BEHIND you at the truck, Chloe's voice: \"Guys, wait up! I dropped "
                    "my flashlight near the back tire!\""),
                   choices, "ridge_bridge", "BACK", "event")
        self.s.fx = "eerie"
        self._seg("!")

    async def _beat_mine(self):
        s, F = self.s, self.F
        F["rd_mine_done"] = True
        has_sam = self.alive("sam")
        choices = [
            {"label": "Crank the Manual Winch", "effect": {"ridge": "resolve", "res": "lift"}, "require": has_sam},
            {"label": "Cut the Lift Cables & Run", "effect": {"ridge": "resolve", "res": "cut_cables"}},
        ]
        self._show("OLD MINING SHAFT 4 — GENERATOR VAULT",
                   ("The master breaker trips and the tower goes dark. Descending by lantern into the "
                    "generator vault: teeth marks in the limestone, grease on the floor mixed with human "
                    "hair. As you throw the heavy iron breaker, the elevator shaft behind you begins to hum.\n"
                    "A voice down in the pit — sounding exactly like Sam — whispers: \"I found the camera, "
                    "man. The pictures... they aren't of us. They're of something right behind us.\""),
                   choices, "ridge_mine", "BACK", "event")
        self.s.fx = "eerie"
        self._seg("!")

    async def _beat_cabins(self):
        s, F = self.s, self.F
        F["rd_cabins_done"] = True
        choices = [
            {"label": "Sam: Fire the Camera Flash", "effect": {"ridge": "resolve", "res": "cabin_flash"}, "require": self.alive("sam")},
            {"label": "Huddle Under the Wood Table", "effect": {"ridge": "resolve", "res": "cabin_huddle"}},
        ]
        self._show("COMPASS CABINS — CABIN 2",
                   ("Rations are low. Inside Cabin 2 an old tape player is still wound. You press PLAY: it "
                    "records this expedition — your footprints, your breathing, your choices — up to the "
                    "exact moment you pressed play.\n\nA heavy thud rocks the roof. Through the rotted "
                    "skylight: an elongated torso, skin like wet ash, wearing a faded canvas jacket with "
                    "the name PATCH reading PENDELTON. It doesn't scream. It speaks in your own voice, "
                    "reciting your childhood address."),
                   choices, "ridge_cabins", "BACK", "event")
        self.s.fx = "eerie"
        self._seg("!")

    async def _beat_sensor(self):
        s, F = self.s, self.F
        F["rd_sensor_done"] = True
        choices = [
            {"label": "Send Chloe onto the Catwalk", "effect": {"ridge": "resolve", "res": "sensor_chloe"}},
            {"label": "Send Mark onto the Catwalk", "effect": {"ridge": "resolve", "res": "sensor_mark"}},
        ]
        self._show("TOWER 2 — SENSOR MAST FAILURE",
                   ("50 mph gusts. The digital sensor mast has torn loose and dangles over the cliff by a "
                    "thick copper wire. The laptop's WeatherRadar is dead static.\n"
                    "Mark: Logic 85, Stamina 45 — asthmatic, pale in the lantern light.\n"
                    "Chloe: Logic 40, Stamina 80 — already tightening her bootlaces."),
                   choices, "ridge_tower", "BACK", "event")
        self.s.fx = "shake"
        self._seg("!")

    async def _site_t1(self):
        s, F = self.s, self.F
        F["rd_t1"] = True
        if "doc_01" not in F.get("rd_docs", []):
            F.setdefault("rd_docs", []).append("doc_01")
            s.log.append("◆ Document recovered: Log Entry #01 (Arthur Pendelton), desk drawer.")
        self._san(-4, "The drawer sticks. Inside: a headset with the foam torn off, and a log page.")
        self._show("FIRE-TOWER 1 — THE DRAWER STICKS",
                   ("The decommissioned cabin smells of cold ash. In the desk drawer: a headset with the "
                    "foam torn off, and one log page in a hand that presses too hard. The service light "
                    "above the southern window blinks once — then remembers it is dead."),
                   [{"label": "Back to Tower 2", "effect": {"ridge": "hub"}}],
                   NODE_SCENE["Fire-Tower 1"], "BACK", "event")
        self._seg("M")

    async def _site_ruins(self):
        s, F = self.s, self.F
        F["rd_ruins"] = True
        if "cassette" not in F.get("rd_docs", []):
            F.setdefault("rd_docs", []).append("cassette")
            s.log.append("◆ Document recovered: Cassette — Arthur's Dictation.")
        self._san(-6, "In the root cellar safe: a working tape recorder. Arthur's dog has been dead for forty years.")
        self._show("RANGER STATION RUINS — THE CELLAR SAFE",
                   ("Charred beams lean over a dry cellar. The safe behind the stone hearth is open — inside, "
                    "a working tape recorder and three cassettes. On play: heavy breathing, a dog that died "
                    "in Ohio forty years ago, and a voice asking you, politely, to open the latch just a crack."),
                   [{"label": "Back to Tower 2", "effect": {"ridge": "hub"}}],
                   NODE_SCENE["Ranger Station Ruins"], "BACK", "event")
        self._seg("M")

    async def _site_railcar(self):
        s, F = self.s, self.F
        if not F.get("rd_railcar"):
            F["rd_railcar"] = True
            if "incident_91" not in F.get("rd_docs", []):
                F.setdefault("rd_docs", []).append("incident_91")
            if "skin_stitch" not in F.get("rd_docs", []):
                F.setdefault("rd_docs", []).append("skin_stitch")
            s.log.append("◆ Documents recovered: 1991 Incident Report + Project Skin-Stitch Bio-Data.")
        self._san(-4, "Black ice inside the railcar. The corporate lockbox was already open. The paperwork wasn't.")
        self._show("OVERTURNED RAILCAR — LOCKBOX 1974",
                   ("The 1974 freight car lies on its side in the ravine floor, doors gaping. Black ice lines "
                    "the interior. The corporate lockbox is open: 1991 incident files and a military logistics "
                    "sheet stamped DARK — a non-human skeleton in the limestone, warm when recovered. "
                    "The recovery vehicle refused to start for eleven hours."),
                   [{"label": "Back to Tower 2", "effect": {"ridge": "hub"}}],
                   NODE_SCENE["Overturned Railcar"], "BACK", "event")
        self._seg("M")

    async def _site_sinkhole(self):
        s, F = self.s, self.F
        if not F.get("rd_flare"):
            F["rd_flare"] = True
            if "flare_gun" not in s.player.inventory:
                s.player.inventory.append("flare_gun")
            s.log.append("◆ Scavenged: Military Flare Gun + 3 crimson flares.")
            if s.world.is_night:
                self._san(-12, "From the bottom of the pit, three voices call for help. All three are your friends. All three are upstairs.")
                self.s.fx = "eerie"
            self._show("LIMESTONE SINKHOLE — THE RIM",
                       ("The pit breathes mist in slow pulses. Scavenging the rim: a military flare gun and three "
                        "crimson flares. The cave network below connects to Shaft 4 — you can hear the dark "
                        "arranging itself when you lean over."),
                       [{"label": "Back to Tower 2", "effect": {"ridge": "hub"}}],
                       NODE_SCENE["Limestone Sinkhole"], "BACK", "event")
            self._seg("M")

    # ── resolution of beats (branching outcomes) ───────────

    async def resolve(self, e: Dict[str, Any]):
        s, F = self.s, self.F
        r = e.get("res")

        if r == "sam_sent":
            F["rd_sam_sent"] = True
            self._kill("sam")
            self._aware(15, "Sam walks into the southern dark with his camera. He does not come back.")
            s.log.append("DAY 4 PREDICTION: an email will arrive from his account. Don't open the attachments.")
            self._san(-10, "-10 SANITY. Under the floorboards, something scratches in a perfect three-beat rhythm.")
            self.s.fx = "eerie"
            self.hub()

        elif r == "ignore_t3":
            self._san(-10, "You filter out the flashes. The scratching beneath the floorboards begins at 03:00 and does not stop.")
            self._aware(5)
            self.hub()

        elif r == "mail":
            mail_id = e.get("mail_id")
            self._show("FORESTOS INBOX — MESSAGE",
                       (e.get("preview") or "") + "\n\n[END OF MESSAGE — attachments quarantined by FORESTOS]",
                       [{"label": "Back to Inbox", "effect": {"ridge": "inbox"}},
                        {"label": "Back to Laptop", "effect": {"ridge": "laptop"}}],
                       "ridge_laptop", "BACK", "event")

        elif r == "doc":
            doc = DOCS.get(e.get("doc_id"), {"name": "Unknown", "text": "File corrupted."})
            self._show(f"DOCUMENT — {doc['name'].upper()}", doc["text"],
                       [{"label": "Next Document Page", "effect": {"ridge": "docs_read", "page": 0}},
                        {"label": "Back to Laptop", "effect": {"ridge": "laptop"}}],
                       "ridge_laptop", "BACK", "event")

        elif r == "radar_mark":
            if self.alive("mark"):
                self._san(3, "Mark: 'The void signature is 312 meters wide and moving at walking pace. Trees don't walk.'")
                self._aware(-5)
            else:
                self._san(-6, "You ask Mark. Mark's chair is empty. The monitor reflects a second chair.")
            await self.radar()

        elif r == "radar_off":
            self._san(-2, "Backlight off. In the dark glass, the reflection of the cabin shows one more person than there is.")
            await self.radar()

        elif r == "log_ok":
            F["rd_logs"] = F.get("rd_logs", 0) + 1
            self._san(6, f"── DAY {s.world.day} ENVIRO-LOG SUBMITTED ({e.get('code')}) — RECORD VERIFIED. ──")
            s.fx = "success"
            await self.e.buzzer.success()
            if s.world.day == 12 and "codebook" not in F.get("rd_docs", []):
                F.setdefault("rd_docs", []).append("codebook")
                s.log.append("◆ DECRYPTED: Forestry Codebook — Section 9. Do not climb Tower 3.")
            self.hub()

        elif r == "log_bad":
            self._san(-4, "REJECTED: lower case. The terminal blinks at you like it's disappointed.")
            self._aware(5, "REJECTED strings are logged to HQ. HQ is not HQ.")
            await self.submit_log()

        elif r == "log_arthur":
            self._san(-8, "The terminal accepts the phrase, then deletes everything. A new folder appears: ARTHUR_WAS_HERE.")
            self._aware(10)
            await self.submit_log()

        elif r == "decrypt":
            self._san(-30, "-30 SANITY. Three hours inside stitched audio. Mark's asthma whistles through the tape.")
            if "freq_chart" not in F.get("rd_docs", []):
                F.setdefault("rd_docs", []).append("freq_chart")
            F["rd_cabin_cache"] = True
            s.log.append("◆ Coordinates unlocked: hidden cabin cache beneath Cabin 2.")
            self.hub()

        elif r == "smash":
            F["rd_radio_dead"] = True
            F["rd_aware_zero"] = True
            self._aware(-self.s.player.humanity, "You smash the dial. Silence floods the cabin. Awareness collapses to zero.")
            s.log.append("The radio is dead. Safety for 48 hours — and no warning when they come.")
            self._san(4)
            self.hub()

        elif r == "bridge_a":
            F["rd_batteries_lost"] = True
            self._san(-8, "You find Chloe shivering at the front span. Behind you, the truck groans and rolls off the edge into the ravine. Batteries: destroyed.")
            self._aware(10)
            self.hub()

        elif r == "bridge_b":
            F["rd_chloe_paranoid"] = True
            self._san(-12, "Nothing but a pair of empty hiking boots on the wet asphalt. Chloe doesn't speak for two days. chloe_paranoid = true.")
            if self.alive("chloe"):
                self.s.world.npcs["chloe"]["trust"] = -1
            self.hub()

        elif r == "lift":
            F["rd_lift_choice"] = "lift"
            if self.alive("sam"):
                s.log.append("The winch groans. A figure climbs into the lantern light. It is wearing Sam's face.")
                self.F["rd_resurrected_sam"] = True
                self._san(-10)
                self._aware(15)
            else:
                s.log.append("You crank the winch for something wearing Sam's voice. It climbs into your base.")
                self._aware(40, "A Stage 3 Mimic is loose inside Fire-Tower 2.")
                self._damage_tower(2)
            self.hub()

        elif r == "cut_cables":
            F["rd_lift_choice"] = "cut"
            F["rd_south_locked"] = True
            self._san(-6, "The cables snap and whip into the dark. The humming stops mid-note.")
            s.log.append("LAPTOP RESTORED. Southern sector permanently locked out of the map.")
            self.hub()

        elif r == "cabin_flash":
            self._san(-10, "Sam fires the strobe through the skylight. The thing falls off the roof and retreats into the ravine, unhurried.")
            self._aware(-10)
            self.hub()

        elif r == "cabin_huddle":
            avg_sta = 60  # group stealth baseline (Chloe 80 / Sam 65 / Mark 45)
            if avg_sta >= 60 and random.random() < 0.6:
                self._san(-20, "It paces the roof for an hour, laughing in Sam's voice, then loses interest.")
                self._aware(-5)
            else:
                self._san(-12, "It punches through the skylight. Chloe takes a crowbar to it. Her hands shake for a week.")
                F["rd_chloe_paranoid"] = True
                self._damage_tower(1)
            self.hub()

        elif r == "sensor_chloe":
            F["rd_sensor_ok"] = True
            self._san(-4, "Chloe rides the gusts like weather is a language she speaks. Sensor re-anchored. WeatherRadar restored.")
            self._aware(-5)
            self.hub()

        elif r == "sensor_mark":
            self._kill("mark")
            self._san(-25, "-25 SANITY. The wind slams the cage. Mark's asthma whistle cuts off halfway down.")
            self._aware(20)
            self.s.fx = "shake"
            self.hub()

        elif r == "answered":
            # You validated its placement in the environment
            self._learn(22, "It has your answer now. Your cadence. Your agreement.")
            self._san(-20, "The channel clears. Nothing on it but your own breathing, slightly ahead of your lungs.")
            self._aware(15)
            F["rd_answered_the_ridge"] = True
            s.fx = "eerie"
            self.hub()

        elif r == "silent":
            self._san(-6, "You kill the breaker mid-sentence. Silence. The lesson: it only owns what you feed it.")
            self._aware(-8, "It waits. Patience is on its side, and it knows you know.")
            self.hub()

        elif r == "elena_take":
            F["rd_elena_met"] = True
            npc = s.world.npcs.get("elena")
            if npc:
                npc.update({"met": True, "at_base": True, "trust": 3})
            s.log.append("★ Dr. Elena Voss is alive, malnourished, and still recording. She joins the watch.")
            if "voss_notes" not in s.player.inventory and len(s.player.inventory) < 8:
                s.player.inventory.append("voss_notes")
            self._san(8, "Someone in this tower has read the literature. That is worth ten sandbags.")
            self.hub()

        elif r == "elena_leave":
            F["rd_elena_met"] = True
            F["rd_voss_lost"] = True
            s.log.append("You leave her the crowbar and the coordinates. Her recorder keeps running after you close the door.")
            self._san(-8, "You will hear her voice on the band by Thursday. You know this the way you know your own name.")
            self.hub()

        elif r == "ash_take":
            F["rd_ash_met"] = True
            F["rd_ash_safe"] = True
            npc = s.world.npcs.get("ash")
            if npc:
                npc.update({"met": True, "at_base": True, "trust": 5})
            s.log.append("★ Ash rides back to Tower 2 in your coat, silent, humming something with no words.")
            self._san(15, "+15 SANITY. There is a child asleep under this roof. Nothing else matters tonight.")
            self.hub()

        elif r == "ash_leave":
            F["rd_ash_met"] = True
            s.log.append("You mark the clearing and climb back out. Behind you, the humming stops when your boots hit the road.")
            self._san(-12, "You will think about that hum for thirty days, and it will think about you.")
            self.hub()

        else:
            self.hub()

    # ── NIGHT & DAWN ───────────────────────────────────────

    async def sleep(self, _e=None):
        s, F = self.s, self.F

        # Missed calibration tax
        if not F.get("rd_cal"):
            self._san(-8, "You slept without syncing the barometers. The laptop flickers all night.")
            self._aware(10)

        # The cabin itself misbehaves when Sanity frays
        if self.sanity() < 40 and random.random() < 0.35:
            s.log.append("── The buzzer sounds by itself. Three beats. Then nothing. ──")
            await self.e.buzzer.danger()
            self._san(-3)
            s.fx = "static"
        if self.sanity() < 30 and random.random() < 0.20:
            s.log.append("── The lantern gutters. The terminal goes fully black for four seconds. ──")
            s.fx = "scare"

        # Night siege check — driven by awareness
        awareness = s.player.humanity
        threat = 0.05 + awareness / 400 + (0.1 if s.world.day >= 19 else 0) - s.world.fortification * 0.02
        if F.get("rd_radio_dead"):
            threat = max(0.02, threat - 0.1)
        night_no = F.get("rd_siege_night", 0)

        if s.world.day == 29 and not F.get("rd_siege_final"):
            F["rd_siege_final"] = True
            await self._final_siege()
            return

        if not s.world.is_night and random.random() < 0.55:
            # dusk first, then night roll on next sleep
            s.world.is_night = True
            s.log.append("── NIGHTFALL. The fog thickens against the glass. ──")
            s.fx = "night"
            await self.e.buzzer.nightfall()
            self._seg("n")
            self.hub()
            return

        s.world.is_night = False

        if random.random() < max(0.02, threat):
            breach = 10 + random.randint(5, 15)
            self._damage_tower(1, f"Claws find the window frame. The cabin shudders ({breach}s).")
            self._san(-breach // 2)
            s.fx = "shake"
            await self.e.buzzer.danger()
            if F.get("rd_hatch_sealed") and s.world.fortification <= 0:
                await self._end("white_noise")
                return
        else:
            self._san(-2, "A quiet watch. The kind that makes you check the ladder twice.")

        # Sam's obsessive frame — awareness creep
        if self.alive("sam") and random.random() < 0.3:
            self._aware(15, "Sam wandered the catwalk at 03:00 photographing 'anomalous light'. Awareness +15.")
        # Mark asthmatic panic under 960mb-ish conditions
        if self.alive("mark") and F.get("rd_fraud") and random.random() < 0.4:
            self._san(-5, "Mark's asthma flares while the pressure sits at mimic heights.")

        await self._dawn()

    def _damage_tower(self, amount: int, note: str = ""):
        self.s.world.fortification = max(0, self.s.world.fortification - amount)
        if note:
            self.s.log.append(note)

    async def _final_siege(self):
        s, F = self.s, self.F
        s.world.is_night = True
        F["rd_siege_night"] = 1
        self._seg("!")
        self._aware(25)
        s.fx = "shake"
        await self.e.buzzer.danger()
        choices = [
            {"label": "Seal the Iron Hatch (2 Scrap)", "effect": {"ridge": "resolve", "res": "seal"}},
            {"label": "Type the Final Log Code", "effect": {"ridge": "resolve", "res": "final_log"}},
            {"label": "Open the Hatch", "effect": {"ridge": "end", "ending": "white_noise"}},
        ]
        self._show("NIGHT 29 — THE SIEGE",
                   ("Long, thin fingers tap a rhythmic three-beat pattern on every glass panel at once. "
                    "The shortwave is a cacophony of overlapping voices — your friends, your parents, your "
                    "old teachers — all crying for help directly outside the iron hatch.\n"
                    "CRITICAL ERROR: MANUAL UPDATE REQUIRED // SUBMIT FINAL ENVIRO-LOG OR FORFEIT STATION.\n"
                    "The windows begin to crack."),
                   choices, "ridge_tower", "BACK", "event")
        self.s.seg = "!"

    async def end_by_choice(self, e: Dict[str, Any]):
        await self._end(e.get("ending", "white_noise"))

    async def _dawn(self):
        s, F = self.s, self.F
        s.world.day += 1
        s.player.days_survived = s.world.day
        s.world.is_night = False
        F["rd_cal"] = False
        F["rd_siege_night"] = 0

        # Rations
        party = sum(1 for n in s.world.npcs.values() if n.get("alive") and n.get("at_base"))
        need = 1 + (1 if party > 1 else 0)
        s.player.food = max(0, s.player.food - need)
        s.player.water = max(0, s.player.water - 1)
        if s.player.food == 0 or s.player.water == 0:
            self._san(-10, "-10 SANITY. Hunger gnaws. The smell of wet pine makes you gag.")
            s.player.health -= 6
        else:
            self._san(2)

        # ── World evolution: the ridge reacts to the campaign, not a script
        world_flags = F.setdefault("rd_world", {})
        for wev in WORLD_EVENTS:
            if s.world.day >= wev["min_day"] and not world_flags.get(wev["flag"]):
                world_flags[wev["flag"]] = True
                s.log.append(f"── WORLD SHIFT: {wev['text']} ──")
                self._aware(4)
                s.fx = "eerie"

        # ── Ranger Cole arrives around Day 12-15 (real? test him over time)
        if s.world.day >= 13 and not F.get("rd_cole_met"):
            F["rd_cole_met"] = True
            npc = s.world.npcs.get("cole")
            if npc:
                npc.update({"met": True, "at_base": True, "trust": 1})
            s.log.append("★ RANGER COLE arrives at dawn with a dispatch order nobody remembers sending. He salutes the tower and asks for your name twice.")
            self._san(4)
            self._aware(6)

        # Eclipse (Act IV)
        if s.world.day >= 26 and not F.get("rd_eclipse"):
            F["rd_eclipse"] = True
            s.log.append("── TOTAL MOUNTAIN ECLIPSE. Permanent midnight for the final 96 hours. ──")
            s.log.append("Branches snap in the canopy like popcorn. The laptop pings once per minute.")
            s.fx = "night"

        # Scheduled emails
        for mail in EMAILS:
            if mail["day"] == s.world.day and mail["id"] not in [m["id"] for m in F.get("rd_inbox", [])]:
                cond = mail.get("cond")
                if cond == "sam_sent" and not F.get("rd_sam_sent"):
                    continue
                if cond == "visited_t1" and not F.get("rd_t1"):
                    continue
                if cond == "bridge_done" and not F.get("rd_bridge_done"):
                    continue
                if cond == "low_sanity" and self.sanity() >= 60:
                    continue
                if cond == "mine_done" and not F.get("rd_mine_done"):
                    continue
                if cond == "saw_fraud" and not F.get("rd_saw_fraud"):
                    continue
                entry = dict(mail)
                entry["read"] = False
                F.setdefault("rd_inbox", []).append(entry)
                s.log.append(f"📧 FORESTOS: new mail — '{mail['subject']}' from {mail['frm']}")
                s.fx = "email"

        # Open-the-hatch spam in Act IV
        if F.get("rd_eclipse") and random.random() < 0.6:
            F.setdefault("rd_inbox", []).append({
                "id": f"hatch_{s.world.day}", "frm": "a.pendelton99@unknown.net",
                "subject": "OPEN THE HATCH", "read": False,
                "body": "OPEN THE HATCH OPEN THE HATCH OPEN THE HATCH OPEN THE HATCH",
            })
            s.log.append("📧 FORESTOS: 1 unread — 'OPEN THE HATCH'")
            s.fx = "email"

        # Day 30 — endings
        if s.world.day >= 30:
            await self._evaluate_endings()
            return

        s.log.append(f"── DAWN: DAY {s.world.day} OF 30. Barometric sync due. ──")
        await self.e.buzzer.dawn()
        self._seg("H")
        self.hub()

    async def _evaluate_endings(self):
        s, F = self.s, self.F
        core = [n for k, n in s.world.npcs.items() if n.get("alive") and k in ("mark", "chloe", "sam")]
        alive = sum(1 for n in s.world.npcs.values() if n.get("alive"))
        core_alive = len(core)
        sanity = self.sanity()
        logs = F.get("rd_logs", 0)
        learn = int(F.get("rd_learn", 0))
        answered = bool(F.get("rd_answered_the_ridge"))

        # Priority order — earned, not arbitrary
        if F.get("rd_lift_choice") == "lift" and core_alive < 3:
            await self._end("stolen_face")
        elif answered and learn >= 75 and sanity <= 40:
            # It got your answer AND practiced your cadence for twenty days
            await self._end("perfect_mask")
        elif sanity <= 0:
            await self._end("white_noise")
        elif F.get("rd_ash_safe") and core_alive >= 2 and sanity >= 25:
            await self._end("ash_kept")
        elif s.world.npcs.get("elena", {}).get("at_base") and core_alive >= 2 and logs >= 24:
            await self._end("voss_protocol")
        elif logs >= 30 and core_alive == 3 and sanity > 60 and learn < 55:
            # You never once fed it — the complete clean escape
            await self._end("the_new_watch")
        elif sanity < 30:
            await self._end("hermit")
        elif logs >= 25 and core_alive == 3 and sanity > 70:
            await self._end("verified")
        else:
            await self._end("verified" if logs >= 20 and core_alive >= 2 else "white_noise")

    async def _end(self, key: str):
        s = self.s
        data = ENDINGS.get(key, ENDINGS["white_noise"])
        s.ending_id = key
        s.ending_title = data["title"]
        s.ending_text = data["text"]
        s.game_over = True
        s.victory = bool(data["victory"])
        s.mode = "ending"
        s.waiting_for_choice = False
        s.scene = "ridge_ending"
        s.confirm_label = "—"
        s.log.append(f"── {data['title']} ──")
        s.log.append(data["text"][:300])
        self._seg("P" if s.victory else "E")
        if s.victory:
            await self.e.buzzer.victory()
        else:
            await self.e.buzzer.game_over()
        self.e._ending_menu()
