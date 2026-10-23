import asyncio
import random
from typing import Any, Dict, List, Optional

from backend.app.core.state import GameState, Player, World, CombatState, INV_SLOTS
from backend.app.game.content import (
    ITEMS,
    LOCATIONS,
    NPC_TEMPLATES,
    RECIPES,
    WEAPONS,
    WEATHERS,
    KID_NAMES,
    apply_ending,
    default_npcs,
    ending_for,
)
from backend.app.game.events import select_event
from backend.app.game.combat import make_combat, resolve_player_action
from backend.app.hardware.display import SevenSegment
from backend.app.hardware.buzzer import Buzzer
from backend.app.services.gemini import GeminiService
from backend.app.services.save import SaveService

STAGE_LABEL = {
    "clean": "Clean",
    "scratch": "Scratch",
    "fever": "Fever",
    "lucid": "Lucid Rot",
    "turning": "Turning",
    "turned": "Turned",
}

CHOICE_KEYS = ["red", "blue", "green", "yellow"]


class GameEngine:
    def __init__(self):
        self.state = GameState.load()
        if not self.state.world.npcs:
            self.state.world.npcs = default_npcs()
            self.state.world.npcs["kid"]["name"] = self.state.kid_name
            self.state.world.npcs["kid"]["short"] = self.state.kid_name
        self.display = SevenSegment()
        self.buzzer = Buzzer()
        self.gemini = GeminiService()
        self.save = SaveService()
        self._broadcast = None
        self._lock = asyncio.Lock()

    def set_broadcast(self, callback):
        self._broadcast = callback

    async def broadcast(self):
        if self._broadcast:
            await self._broadcast(self.state.to_dict())
            self.state.fx = ""

    async def start_new_game(self):
        kid = random.choice(KID_NAMES)
        self.state = GameState()
        self.state.kid_name = kid
        self.state.world.npcs = default_npcs()
        self.state.world.npcs["kid"]["name"] = kid
        self.state.world.npcs["kid"]["short"] = kid
        self.state.world.weather = random.choice(["clear", "overcast", "clear"])
        self.state.log = [
            "You wake in a boarded room that still smells like someone else's tea.",
            "The city beyond the plywood is practicing being over.",
            f"Day 1. Weather: {self.state.world.weather}.",
        ]
        self._hub_menu()
        self.display.show_health(self.state.player.health)
        await self.buzzer.success()
        self.state.save()
        await self.broadcast()

    # ----- menus -----

    def _choices(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for i, item in enumerate(items[:4]):
            c = dict(item)
            c["key"] = CHOICE_KEYS[i]
            out.append(c)
        return out

    def _show(self, title: str, text: str, choices: List[Dict], scene: str, mode: str, confirm: str):
        self.state.mode = mode
        self.state.scene = scene
        self.state.waiting_for_choice = True
        self.state.confirm_label = confirm
        self.state.current_event = {
            "id": mode,
            "title": title,
            "text": text,
            "choices": self._choices(choices),
            "scene": scene,
        }

    def _hub_menu(self):
        s = self.state
        s.menu = ""
        s.world.location = "Home Base"
        party = s.party()
        names = ", ".join(p["short"] for p in party) if party else "no one else breathing here"
        weather = s.world.weather
        clock = "Night" if s.world.is_night else "Day"
        stage = STAGE_LABEL[s.infection_stage()]
        text = (
            f"{clock} {s.world.day}, {weather}. Fortification {s.world.fortification}/10.\n"
            f"Infection: {stage}. Humanity {s.player.humanity}. Under this roof: {names}.\n"
            f"Actions left this stretch: {s.world.actions_left}. "
            f"{LOCATIONS['Home Base']['blurb']}"
        )
        choices = [
            {"label": "Scavenge", "effect": {"open": "locations"}},
            {"label": "Craft", "effect": {"open": "craft"}},
            {"label": "Fortify / camp", "effect": {"open": "fortify"}},
            {"label": "People / radio", "effect": {"open": "talk"}},
        ]
        self._show(f"HOME BASE — {clock} {s.world.day}", text, choices, "base", "hub", "REST")

    def _location_menu(self):
        known = [n for n in self.state.world.known_locations if n != "Home Base"]
        if not known:
            known = ["Streets"]
        day = self.state.world.day
        if day >= 3:
            for extra in ("Warehouse", "Church", "Radio Tower", "Subway Tunnels", "Gas Station"):
                self._discover(extra)
            known = [n for n in self.state.world.known_locations if n != "Home Base"]
        if day >= 7:
            for extra in ("Military Checkpoint", "School", "Docks"):
                self._discover(extra)
            known = [n for n in self.state.world.known_locations if n != "Home Base"]
        if len(known) > 4:
            off = (day + (1 if self.state.world.is_night else 0)) % len(known)
            shown = (known + known)[off : off + 4]
        else:
            shown = known[:4]
        choices = []
        for name in shown:
            choices.append({"label": name, "effect": {"expedition": name}})
        self.state.menu = "locations"
        blurb = "Pick a scar on the map. Risk travels with you. Night makes it honest."
        self._show("LEAVE THE HOUSE", blurb, choices, "map", "menu", "BACK")

    def _craft_menu(self):
        ready: List[Dict[str, Any]] = []
        for rec in RECIPES:
            if rec.get("flag") and self.state.world.flags.get(rec["flag"]):
                continue
            if rec.get("need_item") and rec["need_item"] not in self.state.player.inventory:
                continue
            if rec.get("give_item") == "pipe" and "pipe" in self.state.player.inventory:
                continue
            if rec.get("give_item") == "mask" and "mask" in self.state.player.inventory:
                continue
            if not self._can_afford(rec["cost"]):
                continue
            ready.append({"label": rec["name"], "effect": {"craft": rec["id"]}})
        if not ready:
            ready = [{"label": "Need more scrap", "effect": {"open": "hub"}}]
        while len(ready) < 4:
            ready.append({"label": "Back", "effect": {"open": "hub"}})
        self.state.menu = "craft"
        self._show(
            "WORKBENCH",
            "Tape, teeth, patience. Four things at a time. Confirm to step away.",
            ready[:4],
            "craft",
            "menu",
            "BACK",
        )

    def _fortify_menu(self):
        f = self.state.world.fortification
        text = (
            f"Boards: {f}/10. Alarm: {'yes' if self.state.world.flags.get('alarm') else 'no'}. "
            "Nailing costs a stretch of daylight. Resting spends food and dares the night."
        )
        choices: List[Dict[str, Any]] = [
            {"label": "Nail boards (2 scrap)", "effect": {"fortify_now": True}},
            {"label": "Keep watch", "effect": {"watch": True}},
            {"label": "Sleep here", "effect": {"rest": True}},
            {"label": "Back", "effect": {"open": "hub"}},
        ]
        self.state.menu = "fortify"
        self._show("FORTIFY", text, choices, "base", "menu", "BACK")

    def _talk_menu(self):
        party = [p for p in self.state.party() if p.get("alive")]
        choices: List[Dict[str, Any]] = []
        for p in party[:3]:
            choices.append({"label": f"Talk to {p['short']}", "effect": {"talk": p["id"]}})
        choices.append({"label": "Radio / Channel 7", "effect": {"talk": "radio"}})
        if len(choices) < 4:
            choices.append({"label": "Journal", "effect": {"talk": "journal"}})
        self.state.menu = "talk"
        self._show(
            "THE LIVING",
            "People are not resources, except when the day insists they are. Confirm to return.",
            choices[:4],
            "talk",
            "menu",
            "BACK",
        )

    def _combat_menu(self):
        c = self.state.combat
        lines = " · ".join(c.log[-3:])
        text = f"{c.enemy_name}  HP {max(0, c.enemy_hp)}/{c.enemy_max}\n{lines}"
        choices: List[Dict[str, Any]] = [
            {"label": "Strike", "effect": {"combat_act": "attack"}},
            {"label": "Guard", "effect": {"combat_act": "defend"}},
            {"label": "Fire", "effect": {"combat_act": "shoot"}},
            {"label": "Flee", "effect": {"combat_act": "flee"}},
        ]
        if "molotov" in self.state.player.inventory:
            choices[3] = {"label": "Molotov", "effect": {"combat_act": "molotov"}}
        self.state.mode = "combat"
        self.state.scene = "combat"
        self.state.confirm_label = "MEDKIT"
        self.state.waiting_for_choice = True
        self.state.current_event = {
            "id": "combat",
            "title": c.enemy_name.upper(),
            "text": text,
            "choices": self._choices(choices),
            "scene": "combat",
        }

    def _ending_menu(self):
        s = self.state
        self._show(
            s.ending_title or ("EXTRACTION" if s.victory else "YOU DIED"),
            s.ending_text or "The run is over.",
            [
                {"label": "New run", "effect": {"restart": True}},
                {"label": "Sit with it", "effect": {}},
                {"label": "Read the log", "effect": {}},
                {"label": "Again", "effect": {"restart": True}},
            ],
            "ending",
            "ending",
            "—",
        )

    # ----- input -----

    async def handle_choice(self, key: str):
        async with self._lock:
            if self.state.game_over and key:
                ev = self.state.current_event or {}
                choice = next((c for c in ev.get("choices", []) if c["key"] == key), None)
                if choice and choice.get("effect", {}).get("restart"):
                    await self.start_new_game()
                return
            if not self.state.waiting_for_choice or not self.state.current_event:
                return
            choices = self.state.current_event.get("choices", [])
            choice = next((c for c in choices if c["key"] == key), None)
            if not choice:
                return
            if not self._choice_allowed(choice):
                self.state.log.append("You cannot do that — missing something, or someone.")
                await self.broadcast()
                return
            self.state.last_action = choice["label"]
            self.state.log.append(f"> {choice['label']}")
            self.state.waiting_for_choice = False
            await self.apply_effect(choice.get("effect") or {})
            if self.state.game_over or self.state.combat.active:
                await self._after_effect()
                return
            await self._after_effect()

    async def handle_confirm(self):
        async with self._lock:
            if self.state.game_over:
                return
            label = self.state.confirm_label
            if label == "REST":
                await self.apply_effect({"rest": True})
                await self._after_effect()
                return
            if label in ("BACK", "—"):
                if not self.state.combat.active:
                    self._hub_menu()
                    await self.broadcast()
                return
            await self.use_medkit()

    async def use_medkit(self):
        p = self.state.player
        if p.medkits <= 0:
            self.state.log.append("The kit is empty. You already knew.")
            self.state.fx = "miss"
            await self.buzzer.low_health()
            await self.broadcast()
            return
        if p.health >= 100 and p.infection <= 0:
            self.state.log.append("You are already the best version of hurt.")
            await self.broadcast()
            return
        p.medkits -= 1
        p.health = min(100, p.health + 32)
        p.infection = max(0, p.infection - 8)
        self.state.log.append("Gauze, sting, a brief republic of not dying.")
        self.state.fx = "heal"
        self.display.show_health(p.health)
        await self.buzzer.success()
        if self.state.combat.active:
            self._combat_menu()
        self.state.save()
        await self.broadcast()

    # ----- effects -----

    def _choice_allowed(self, choice: Dict[str, Any]) -> bool:
        eff = choice.get("effect") or {}
        if eff.get("require_npc"):
            npc = self.state.world.npcs.get(eff["require_npc"], {})
            if not (npc.get("alive") and npc.get("at_base")):
                return False
        if eff.get("require_party"):
            if not self.state.party():
                return False
        if eff.get("require_day") and self.state.world.day < eff["require_day"]:
            return False
        return True

    def _can_afford(self, cost: Dict[str, int]) -> bool:
        p = self.state.player
        for k, v in cost.items():
            if getattr(p, k, 0) < v:
                return False
        return True

    async def apply_effect(self, effect: Dict[str, Any]):
        if effect.get("restart"):
            await self.start_new_game()
            return
        if effect.get("expedition"):
            await self._start_expedition(effect["expedition"])
            return
        if effect.get("craft"):
            await self._craft(effect["craft"])
            return
        if effect.get("fortify_now"):
            await self._fortify()
            return
        if effect.get("watch"):
            self.state.player.morale = min(100, self.state.player.morale + 6)
            self.state.log.append("You keep the window. The city performs being dead.")
            await self._spend_action()
            self._hub_menu()
            return
        if effect.get("rest"):
            await self._rest()
            return
        if effect.get("talk"):
            await self._talk(effect["talk"])
            return
        if effect.get("combat_act"):
            await self._combat_act(effect["combat_act"])
            return

        was_event = self.state.mode == "event"
        p, w = self.state.player, self.state.world

        if effect.get("consume_item"):
            item = effect["consume_item"]
            if item in ("medkits",):
                pass
            elif item in p.inventory:
                if not effect.get("keep_item"):
                    p.inventory.remove(item)
            elif item == "molotov":
                self.state.log.append("No bottle. The thought of fire will have to do.")
            elif item == "holy_charm" and "holy_charm" not in p.inventory:
                self.state.log.append("Miriam's charm is a story you do not have.")
            elif item == "tunnel_key" and "tunnel_key" not in p.inventory:
                self.state.log.append("The tunnels do not know you yet.")
                return
            elif item == "antibiotics" and "antibiotics" not in p.inventory:
                self.state.log.append("The bottle is imaginary. The fever is not.")
            elif item == "photo" and "photo" not in p.inventory:
                self.state.log.append("No photo to carry.")

        if effect.get("combat"):
            self._begin_combat(effect["combat"])

        if "risk" in effect:
            chance = float(effect["risk"])
            if w.weather == "storm":
                chance += 0.08
            if w.is_night:
                chance += 0.1
            if w.location == "Home Base":
                chance -= w.fortification * 0.04
            if random.random() < max(0.05, chance):
                dmg = random.randint(8, 18)
                p.health -= dmg
                if random.random() < 0.35:
                    p.infection += random.randint(4, 10)
                self.state.log.append("It goes wrong in a small, professional way.")
                self.state.fx = "shake"
                await self.buzzer.danger()
            else:
                await self.buzzer.success()
                self.state.fx = "success"

        for k in (
            "health",
            "infection",
            "morale",
            "humanity",
            "food",
            "water",
            "ammo",
            "scrap",
            "medkits",
        ):
            if k in effect:
                setattr(p, k, getattr(p, k) + int(effect[k]))
                if int(effect[k]) > 0 and k in ("food", "water", "ammo", "scrap", "medkits"):
                    self.state.fx = self.state.fx or "success"

        if "fort" in effect:
            w.fortification += int(effect["fort"])
        if effect.get("location"):
            w.location = effect["location"]
            self._discover(effect["location"])
            self.state.log.append(f"Moved to {effect['location']}.")
        if effect.get("discover") or effect.get("discover2"):
            for name in (effect.get("discover"), effect.get("discover2")):
                if name:
                    self._discover(name)
        if effect.get("add_item"):
            self._give_item(effect["add_item"])
        if effect.get("weapon") and effect["weapon"] in WEAPONS:
            p.weapon = effect["weapon"]
            self.state.log.append(f"Armed: {WEAPONS[p.weapon]['name']}.")
        if effect.get("flags"):
            w.flags.update(effect["flags"])
        if effect.get("npc_join"):
            self._npc_join(effect["npc_join"])
        if effect.get("npc_kill"):
            self._npc_kill(effect["npc_kill"])
        if effect.get("log"):
            self.state.log.append(effect["log"])

        if effect.get("flags"):
            jack = {
                "extract_halcyon",
                "chose_docks",
                "chose_ghost_path",
                "chose_sermon",
                "lena_sacrifice",
                "marcus_broadcast",
                "chose_quiet",
            }
            if any(effect["flags"].get(k) for k in jack):
                await self._trigger_ending()
                return

        if effect.get("ending_if") == "last_light" and w.flags.get("lena_sacrifice"):
            await self._trigger_ending()
            return

        self.state.clamp()
        self.display.show_health(p.health)

        if effect.get("open") == "locations":
            self._location_menu()
            return
        if effect.get("open") == "craft":
            self._craft_menu()
            return
        if effect.get("open") == "fortify":
            self._fortify_menu()
            return
        if effect.get("open") in ("talk", "people"):
            self._talk_menu()
            return
        if effect.get("open") == "hub":
            self._hub_menu()
            return

        if self.state.combat.active or self.state.game_over:
            return

        if was_event:
            await self._spend_action()
            if not self.state.game_over and not self.state.combat.active and self.state.mode == "event":
                self._hub_menu()

    async def _after_effect(self):
        await self._check_collapse()
        if not self.state.game_over:
            self.state.save()
        await self.broadcast()
        if self.state.combat.active:
            await self.buzzer.danger()

    def _begin_combat(self, enemy_id: str):
        data = make_combat(enemy_id)
        self.state.combat = CombatState(**data)
        self.state.mode = "combat"
        self.state.log.append(f"── {self.state.combat.enemy_name} ──")
        self._combat_menu()

    async def _combat_act(self, action: str):
        result = resolve_player_action(self.state, action)
        for n in result.get("notes", []):
            self.state.log.append(n)
        self.state.fx = result.get("fx", "hit")
        loot = result.get("loot") or {}
        for k, v in loot.items():
            setattr(self.state.player, k, getattr(self.state.player, k) + v)
            self.state.log.append(f"Took {v} {k}.")
        self.display.show_health(self.state.player.health)
        if result.get("died"):
            self.state.world.flags["death_cause"] = "dead"
            await self._trigger_ending()
            return
        if result.get("over"):
            self.state.combat = CombatState()
            await self._spend_action()
            if not self.state.game_over:
                self._hub_menu()
            return
        self._combat_menu()

    async def _start_expedition(self, location: str):
        self._discover(location)
        self.state.world.location = location
        self.state.mode = "event"
        self.state.menu = ""
        blurb = LOCATIONS.get(location, {}).get("blurb", "")
        self.state.log.append(f"── {location} ──")
        if blurb:
            self.state.log.append(blurb)
        ev = select_event(self.state, location)
        self._present_event(ev)

    def _present_event(self, ev: Dict[str, Any]):
        if ev.get("id") not in self.state.world.seen_events:
            self.state.world.seen_events.append(ev["id"])
            if len(self.state.world.seen_events) > 120:
                self.state.world.seen_events = self.state.world.seen_events[-120:]
        self.state.mode = "event"
        self.state.scene = ev.get("scene") or LOCATIONS.get(self.state.world.location, {}).get("id", "streets")
        self.state.waiting_for_choice = True
        self.state.confirm_label = "MEDKIT"
        self.state.current_event = {
            "id": ev["id"],
            "title": ev["title"],
            "text": ev["text"],
            "choices": ev["choices"],
            "scene": self.state.scene,
        }
        self.state.log.append(f"── {ev['title']} ──")
        self.state.log.append(ev["text"][:180])

    async def _craft(self, recipe_id: str):
        rec = next((r for r in RECIPES if r["id"] == recipe_id), None)
        if not rec:
            self._hub_menu()
            return
        if rec.get("need_item") and rec["need_item"] not in self.state.player.inventory:
            self.state.log.append("Missing a part that is more than scrap.")
            self._craft_menu()
            return
        if not self._can_afford(rec["cost"]):
            self.state.log.append("The workbench laughs in empty.")
            self._craft_menu()
            return
        p = self.state.player
        for k, v in rec["cost"].items():
            setattr(p, k, getattr(p, k) - v)
        if rec.get("give_item"):
            self._give_item(rec["give_item"])
        if rec.get("weapon"):
            p.weapon = rec["weapon"]
        if rec.get("fort"):
            self.state.world.fortification += rec["fort"]
        if rec.get("flag"):
            self.state.world.flags[rec["flag"]] = True
        self.state.log.append(rec.get("log") or f"Crafted {rec['name']}.")
        self.state.fx = "craft"
        await self.buzzer.success()
        self._hub_menu()

    async def _fortify(self):
        if self.state.player.scrap < 2:
            self.state.log.append("Scrap is a theory.")
            self._fortify_menu()
            return
        self.state.player.scrap -= 2
        self.state.world.fortification += 1
        self.state.log.append("The door believes you a little more.")
        await self._spend_action()
        self._hub_menu()

    async def _rest(self):
        p, w = self.state.player, self.state.world
        heal = 18 + (8 if w.flags.get("medbay") else 0)
        p.health = min(100, p.health + heal)
        p.morale = min(100, p.morale + 4)
        self.state.log.append("Sleep is a thin country. You get a visa anyway.")
        if w.is_night:
            await self._dawn()
        else:
            await self._spend_action()
        if not self.state.game_over:
            self._hub_menu()

    async def _talk(self, who: str):
        s = self.state
        if who == "radio":
            if s.world.flags.get("radio_repaired"):
                text = (
                    "Channel 7 is a room. Marcus — or the recording of a braver hour — talks about walls, "
                    "names, and a truck that may be a story wearing headlights."
                )
                choices: List[Dict[str, Any]] = [
                    {"label": "Ask for Halcyon", "effect": {"flags": {"heard_halcyon": True}, "morale": 4, "gemini": True}},
                    {
                        "label": "Signal the truck",
                        "effect": {"flags": {"extract_halcyon": True}},
                    }
                    if s.world.day >= 12
                    else {"label": "Keep listening", "effect": {"morale": 6, "gemini": True}},
                    {"label": "Off-air joke", "effect": {"morale": 8, "humanity": 2, "gemini": True}},
                    {"label": "Back", "effect": {"open": "hub"}},
                ]
            else:
                text = "Static with ambitions. You need parts and a workbench that is not ashamed."
                choices = [
                    {"label": "Tune anyway", "effect": {"morale": 2, "gemini": True, "flags": {"heard_halcyon": True}}},
                    {"label": "Hunt parts", "effect": {"expedition": "Radio Tower"}},
                    {"label": "Leave it", "effect": {"open": "hub"}},
                    {"label": "Hum into it", "effect": {"morale": 3, "gemini": True}},
                ]
                self._discover("Radio Tower")
            self.state.mode = "event"
            self._show("CHANNEL 7", text, choices, "radio", "event", "BACK")
            return
        if who == "journal":
            stage = STAGE_LABEL[s.infection_stage()]
            text = (
                f"Day {s.world.day}. {stage}. Humanity {s.player.humanity}. "
                f"Weapon: {WEAPONS.get(s.player.weapon, WEAPONS['fists'])['name']}. "
                "You write because the house should remember you correctly."
            )
            self._show(
                "SURVIVOR LOG",
                text,
                [
                    {"label": "Write hope", "effect": {"morale": 6, "humanity": 2, "gemini": True, "open": "hub"}},
                    {"label": "Write the dead", "effect": {"morale": -4, "humanity": 4, "gemini": True, "open": "hub"}},
                    {"label": "Inventory the living", "effect": {"open": "talk"}},
                    {"label": "Close it", "effect": {"open": "hub"}},
                ],
                "quiet",
                "menu",
                "BACK",
            )
            return
        npc = s.world.npcs.get(who)
        if not npc:
            self._talk_menu()
            return
        lines = {
            "marcus": f"{npc['name']} sits with the radio like it is a shy animal. 'We can still sound like a city,' he says.",
            "lena": "Lena checks your pupils without asking. 'Do not romanticize my lucidity. It is a symptom with manners.'",
            "kid": f"{s.kid_name} has arranged bottlecaps into a fortress. 'This one is you,' they say, which is a lot of pressure for a cap.",
            "miriam": "Miriam pours water like a sacrament even when it is only water. 'Stay human on purpose,' she says.",
            "ghost": "Ghost taps twice: still here. Then draws a tunnel in spilled coffee.",
            "butcher": "He should not be in your kitchen. He is, smiling with the clean hand.",
        }
        text = lines.get(who, npc["name"] + " waits.")
        choices: List[Dict[str, Any]] = [
            {"label": "Listen", "effect": {"morale": 6, "gemini": True, "open": "hub"}},
            {"label": "Share food", "effect": {"food": -1, "humanity": 4, "morale": 6, "open": "hub"}},
            {"label": "Ask for help", "effect": {"morale": 2, "gemini": True, "open": "hub"}},
            {"label": "Back", "effect": {"open": "hub"}},
        ]
        if who == "lena" and s.player.infection >= 20:
            choices[2] = {"label": "Ask for a dose", "effect": {"infection": -12, "health": -4, "open": "hub"}}
        self._show(npc["short"].upper(), text, choices, who, "event", "BACK")

    def _give_item(self, item_id: str):
        p = self.state.player
        info = ITEMS.get(item_id, {"name": item_id})
        if item_id in p.inventory:
            self.state.log.append(f"You already carry {info['name']}.")
            return
        if len(p.inventory) >= INV_SLOTS:
            self.state.log.append("Pockets full. You leave a piece of the old world.")
            return
        p.inventory.append(item_id)
        self.state.log.append(f"Took {info['name']}.")
        if item_id in WEAPONS:
            p.weapon = item_id

    def _discover(self, name: str):
        if name and name not in self.state.world.known_locations and name in LOCATIONS:
            self.state.world.known_locations.append(name)
            self.state.log.append(f"Mapped: {name}.")

    def _npc_join(self, npc_id: str):
        npc = self.state.world.npcs.get(npc_id)
        if not npc or not npc.get("alive"):
            return
        npc["met"] = True
        npc["at_base"] = True
        npc["trust"] = npc.get("trust", 0) + 2
        if npc_id == "kid":
            npc["name"] = self.state.kid_name
            npc["short"] = self.state.kid_name
        self.state.log.append(f"{npc['short']} is under your roof now.")
        self.state.fx = "join"

    def _npc_kill(self, npc_id: str):
        npc = self.state.world.npcs.get(npc_id)
        if not npc:
            return
        npc["alive"] = False
        npc["at_base"] = False
        self.state.log.append(f"{npc['short']} will not be coming.")

    async def _spend_action(self):
        w = self.state.world
        w.actions_left -= 1
        if w.actions_left <= 0:
            if w.is_night:
                await self._dawn()
            else:
                await self._nightfall()

    async def _nightfall(self):
        w = self.state.world
        w.is_night = True
        w.actions_left = 1
        w.weather = random.choice(WEATHERS)
        self.state.log.append("Night falls like a verdict with no clerk.")
        self.state.fx = "night"
        await self.buzzer.nightfall()
        threat = 0.12 + (0.05 if w.weather == "storm" else 0) + (0.08 if self.state.player.infection >= 50 else 0)
        threat -= w.fortification * 0.03
        if w.flags.get("alarm"):
            threat -= 0.08
        if random.random() < max(0.02, threat) and w.fortification < 3 and w.day >= 4:
            self.state.log.append("The boards fail a test they did not study for.")
            if random.random() < 0.4:
                w.flags["death_cause"] = "breach"
                await self._trigger_ending()
                return
            self.state.player.health -= random.randint(10, 22)
            self.state.fx = "shake"
        elif random.random() < 0.35:
            self.state.world.location = "Home Base"
            ev = select_event(self.state, "Home Base")
            self._present_event(ev)

    async def _dawn(self):
        w, p = self.state.world, self.state.player
        w.is_night = False
        w.day += 1
        w.actions_left = 2
        w.weather = random.choice(WEATHERS)
        food_need = 1 + (
            (1 if any(n.get("at_base") and n.get("alive") for n in w.npcs.values()) else 0)
        )
        if w.flags.get("garden") and random.random() < 0.6:
            p.food += 1
            self.state.log.append("The planter pays rent.")
        if w.flags.get("rain_catcher") and w.weather in ("rain", "storm"):
            p.water += 2
            self.state.log.append("The sky makes good.")
        p.food = max(0, p.food - food_need)
        p.water = max(0, p.water - 1)
        self.state.log.append(f"── DAY {w.day} · {w.weather} ──")
        if p.food == 0 or p.water == 0:
            p.health -= 12
            p.morale -= 8
            self.state.log.append("The cupboard is a hole you keep falling into.")
            if p.food == 0 and p.water == 0:
                w.flags.setdefault("death_cause", "starved")
        if p.infection > 0:
            tick = 2 + (3 if self.state.infection_stage() in ("lucid", "turning") else 0)
            if "mask" in p.inventory:
                tick = max(1, tick - 1)
            if w.flags.get("lena_treated"):
                tick = max(0, tick - 2)
            p.infection += tick
            p.health -= 1 if p.infection >= 25 else 0
            await self.buzzer.infection_tick()
            self.state.fx = "infect"
        if p.morale <= 15:
            p.health -= 4
            self.state.log.append("Hope is late for its shift.")
        if p.humanity <= 20:
            for npc in w.npcs.values():
                if npc.get("at_base") and npc["id"] in ("miriam", "kid") and random.random() < 0.25:
                    npc["at_base"] = False
                    self.state.log.append(f"{npc['short']} cannot stay with what you are becoming.")
        self.display.show_health(p.health)
        await self.buzzer.success()
        if w.day >= 21 and not self.state.game_over:
            if not any(
                w.flags.get(k)
                for k in (
                    "extract_halcyon",
                    "chose_docks",
                    "chose_quiet",
                    "chose_ghost_path",
                    "chose_sermon",
                )
            ):
                w.flags["chose_quiet"] = True
            await self._trigger_ending()

    async def _check_collapse(self):
        self.state.clamp()
        if self.state.game_over:
            return
        if self.state.player.infection >= 100:
            self.state.world.flags["death_cause"] = "turned"
            await self._trigger_ending()
            return
        if self.state.player.health <= 0:
            if self.state.player.food == 0 and self.state.player.water == 0:
                self.state.world.flags.setdefault("death_cause", "starved")
            else:
                self.state.world.flags.setdefault("death_cause", "dead")
            await self._trigger_ending()

    async def _trigger_ending(self):
        eid = ending_for(self.state)
        victory = eid in (
            "halcyon",
            "shepherd",
            "quiet_house",
            "last_light",
            "docks_leave",
            "broadcast",
            "ghost_path",
            "sermon",
        )
        apply_ending(self.state, eid, victory)
        if victory:
            await self.buzzer.success()
            self.display.show("P")
        else:
            await self.buzzer.danger()
            self.display.show("E")
        self._ending_menu()
        self.state.save()
