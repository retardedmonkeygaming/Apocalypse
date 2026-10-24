import asyncio
import random
from typing import Any, Dict, List, Optional

from backend.app.core.state import GameState, Player, World, CombatState, INV_SLOTS
from backend.app.game.content import (
    ITEMS,
    LOCATIONS,
    NPC_TEMPLATES,
    RECIPES,
    SCENARIOS,
    SCENARIO_ORDER,
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
            "Channel 7 hums through the static: four survivor files just crossed the wire.",
            f"Day 1. Weather: {self.state.world.weather.upper()}. Choose the life you already lived.",
        ]
        # New runs open on story selection — pick a scenario with buttons 1-4.
        self._scenario_menu()
        self.display.show_health(self.state.player.health)
        await self.buzzer.success()
        self.state.save()
        await self.broadcast()

    # ─────────────────────────────────────────────────────────────
    # STORY SCENARIOS
    # ─────────────────────────────────────────────────────────────

    def _scenario_menu(self):
        s = self.state
        s.menu = "scenario"
        lines = [
            "Four survivor files slide across the desk. Each is a different way to have lived this long.",
            "Pick your story — or let CONFIRM take the classic tale.",
            "",
        ]
        for i, sid in enumerate(SCENARIO_ORDER):
            scn = SCENARIOS[sid]
            lines.append(f"{i + 1}. {scn['name']} — {scn['tag']}")
        choices = [
            {"label": SCENARIOS[sid]["name"], "effect": {"scenario": sid}}
            for sid in SCENARIO_ORDER
        ]
        self._show("CHOOSE YOUR STORY", "\n".join(lines), choices, "base", "menu", "CLASSIC")
        self.display.show("S")

    async def _apply_scenario(self, sid: str):
        scn = SCENARIOS.get(sid, SCENARIOS["apartment"])
        s = self.state
        s.scenario = sid
        p, w = s.player, s.world

        for k, v in (scn.get("player") or {}).items():
            if hasattr(p, k):
                setattr(p, k, v)
        if scn.get("weapon"):
            p.weapon = scn["weapon"]
        for item in scn.get("inventory") or []:
            if item not in p.inventory:
                p.inventory.append(item)
        if scn.get("fort") is not None:
            w.fortification = scn["fort"]
        for loc in scn.get("known") or []:
            self._discover(loc)

        s.log.append(f"▶ SCENARIO: {scn['name']} — {scn['tag']}")
        for line in scn.get("log") or []:
            s.log.append(line)

        s.clamp()
        self._hub_menu()
        self.display.show_health(p.health)

    # ─────────────────────────────────────────────────────────────
    # MENUS & HUBS
    # ─────────────────────────────────────────────────────────────

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
        names = ", ".join(p["short"] for p in party) if party else "alone with the deadbolt"
        weather = s.world.weather.upper()
        clock = "NIGHT" if s.world.is_night else "DAY"
        stage = STAGE_LABEL[s.infection_stage()]
        text = (
            f"{clock} {s.world.day} · {weather} · Base Fortification: {s.world.fortification}/10.\n"
            f"Infection: {stage} ({s.player.infection}%) · Humanity: {s.player.humanity}/100.\n"
            f"Under this roof: {names}.\n"
            f"Actions remaining: {s.world.actions_left}. Confirm button: REST."
        )
        choices = [
            {"label": "Scavenge", "effect": {"open": "locations"}},
            {"label": "Workbench", "effect": {"open": "craft"}},
            {"label": "Fortify Base", "effect": {"open": "fortify"}},
            {"label": "People / Radio", "effect": {"open": "talk"}},
        ]
        self._show(f"HOME BASE — {clock} {s.world.day}", text, choices, "base", "hub", "REST")
        self.display.show("H" if not s.world.is_night else "n")

    def _location_menu(self):
        # Progressively discover new sites as days advance
        day = self.state.world.day
        if day >= 2:
            for extra in ("Warehouse", "Church", "Radio Tower", "Subway Tunnels", "Gas Station"):
                self._discover(extra)
        if day >= 3:
            for extra in ("Fire Station", "Bus Depot", "Overpass Camp"):
                self._discover(extra)
        if day >= 5:
            for extra in ("Military Checkpoint", "School", "Docks", "Overgrown Park", "Ruined Pharmacy"):
                self._discover(extra)
        if day >= 7:
            for extra in ("City Prison", "Waterworks", "Memorial Stadium"):
                self._discover(extra)

        known = [n for n in self.state.world.known_locations if n != "Home Base"]
        if not known:
            known = ["Streets"]

        # Page through the map 4 sites at a time; each open advances a page
        # so every discovered coordinate stays reachable within a few opens.
        pages = max(1, (len(known) + 3) // 4)
        page = self.state.world.loc_page % pages
        shown = known[page * 4 : page * 4 + 4]
        self.state.world.loc_page = (page + 1) % pages

        choices = []
        for name in shown:
            risk_pct = int(LOCATIONS.get(name, {}).get("risk", 0.3) * 100)
            choices.append({"label": f"{name} ({risk_pct}% risk)", "effect": {"expedition": name}})

        self.state.menu = "locations"
        blurb = (
            f"City map page {page + 1}/{pages} · {len(known)} coordinates charted. "
            "Reopen the map to cycle pages. Risk scales with distance, fog, and night."
        )
        self._show("LEAVE THE APARTMENT", blurb, choices, "map", "menu", "BACK")
        self.display.show("L")

    def _craft_menu(self):
        ready: List[Dict[str, Any]] = []
        p = self.state.player
        w = self.state.world

        for rec in RECIPES:
            # Skip if camp flag already constructed
            if rec.get("flag") and w.flags.get(rec["flag"]):
                continue
            if rec.get("need_item") and rec["need_item"] not in p.inventory:
                continue
            if rec.get("give_item") in p.inventory and rec.get("give_item") != "molotov":
                continue
            if not self._can_afford(rec["cost"]):
                continue

            ready.append({"label": rec["name"], "effect": {"craft": rec["id"]}})

        if not ready:
            ready = [{"label": "Need more scrap", "effect": {"open": "hub"}}]

        while len(ready) < 4:
            ready.append({"label": "Return to Hub", "effect": {"open": "hub"}})

        self.state.menu = "craft"
        self._show(
            "WORKBENCH",
            "Scrap metal, friction tape, and patient hands. Select an item to assemble. Confirm to return.",
            ready[:4],
            "craft",
            "menu",
            "BACK",
        )
        self.display.show("c")

    def _fortify_menu(self):
        f = self.state.world.fortification
        w = self.state.world
        text = (
            f"Barricades: {f}/10. Alarm: {'YES' if w.flags.get('alarm') else 'NO'}. "
            f"Med Station: {'YES' if w.flags.get('medbay') else 'NO'}.\n"
            "Reinforcing nails cost scrap and daytime. Resting spends food & water to heal."
        )
        choices: List[Dict[str, Any]] = [
            {"label": "Nail Boards (2 Scrap)", "effect": {"fortify_now": True}},
            {"label": "Keep Watch", "effect": {"watch": True}},
            {"label": "Rest & Sleep", "effect": {"rest": True}},
            {"label": "Return to Hub", "effect": {"open": "hub"}},
        ]
        self.state.menu = "fortify"
        self._show("FORTIFY DEFENSES", text, choices, "base", "menu", "BACK")
        self.display.show("F")

    def _talk_menu(self):
        party = [p for p in self.state.party() if p.get("alive")]
        choices: List[Dict[str, Any]] = []
        for p in party[:2]:
            choices.append({"label": f"Speak to {p['short']}", "effect": {"talk": p["id"]}})
        choices.append({"label": "Channel 7 Radio", "effect": {"talk": "radio"}})
        choices.append({"label": "Survivor Log", "effect": {"talk": "journal"}})

        while len(choices) < 4:
            choices.append({"label": "Return", "effect": {"open": "hub"}})

        self.state.menu = "talk"
        self._show(
            "VOICES IN THE ROOM",
            "People are not just mouths to feed; they are the only reason to survive until tomorrow.",
            choices[:4],
            "talk",
            "menu",
            "BACK",
        )
        self.display.show("H")

    def _combat_menu(self):
        c = self.state.combat
        lines = " · ".join(c.log[-2:]) if c.log else "Combat underway."
        text = f"{c.enemy_name.upper()}  HP: {max(0, c.enemy_hp)}/{c.enemy_max}\nIntent: {c.enemy_intent}\n{lines}"
        choices: List[Dict[str, Any]] = [
            {"label": f"Strike ({WEAPONS.get(self.state.player.weapon, WEAPONS['fists'])['name']})", "effect": {"combat_act": "attack"}},
            {"label": "Guard (Block Bite)", "effect": {"combat_act": "defend"}},
            {"label": f"Fire Gun ({self.state.player.ammo} rnds)", "effect": {"combat_act": "shoot"}},
            {"label": "Flee to Cover", "effect": {"combat_act": "flee"}},
        ]
        if "molotov" in self.state.player.inventory:
            choices[3] = {"label": "Throw Molotov", "effect": {"combat_act": "molotov"}}

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
        self.display.show("C")

    def _ending_menu(self):
        s = self.state
        self._show(
            s.ending_title or ("EXTRACTION" if s.victory else "COLD FLOOR"),
            s.ending_text or "The run has concluded.",
            [
                {"label": "Start New Run", "effect": {"restart": True}},
                {"label": "Sit with Silence", "effect": {}},
                {"label": "Review the Log", "effect": {}},
                {"label": "Try Again", "effect": {"restart": True}},
            ],
            "ending",
            "ending",
            "—",
        )

    # ─────────────────────────────────────────────────────────────
    # INPUT HANDLING
    # ─────────────────────────────────────────────────────────────

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
                self.state.log.append("You cannot do that right now — prerequisite not met.")
                await self.broadcast()
                return

            self.state.last_action = choice["label"]
            self.state.log.append(f"> {choice['label']}")
            self.state.waiting_for_choice = False

            # Optional Gemini hook for emergent flavor text
            eff = choice.get("effect") or {}
            if eff.get("gemini") and self.gemini.enabled:
                asyncio.create_task(self._trigger_gemini_flavor(choice["label"]))

            await self.apply_effect(eff)
            await self._after_effect()

    async def _trigger_gemini_flavor(self, choice_label: str):
        ev_title = self.state.current_event.get("title", "Survivor Choice") if self.state.current_event else "Survivor Choice"
        flavor = await self.gemini.generate_flavor(ev_title, choice_label, self.state)
        if flavor:
            self.state.log.append(f"📻 \"{flavor}\"")
            await self.broadcast()

    async def handle_confirm(self):
        async with self._lock:
            if self.state.game_over:
                return
            # On story select, CONFIRM takes the classic scenario.
            if self.state.menu == "scenario":
                await self._apply_scenario("apartment")
                await self._after_effect()
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
            self.state.log.append("Your medical kit is empty. Clean bandages are gone.")
            self.state.fx = "miss"
            await self.buzzer.low_health()
            await self.broadcast()
            return

        if p.health >= 100 and p.infection <= 0:
            self.state.log.append("You are already patched up as best as medicine allows.")
            await self.broadcast()
            return

        p.medkits -= 1
        p.health = min(100, p.health + 35)
        p.infection = max(0, p.infection - 10)
        self.state.log.append("Alcohol sting, fresh gauze wrapped tight. Vitality restored.")
        self.state.fx = "heal"
        self.display.show_health(p.health)
        await self.buzzer.success()

        if self.state.combat.active:
            self._combat_menu()
        self.state.save()
        await self.broadcast()

    # ─────────────────────────────────────────────────────────────
    # EFFECT RESOLUTION
    # ─────────────────────────────────────────────────────────────

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
        if effect.get("scenario"):
            await self._apply_scenario(effect["scenario"])
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
            self.state.player.morale = min(100, self.state.player.morale + 8)
            self.state.log.append("You scan the rooftops through the periscope. The city breathes in gray silence.")
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

        # Consume item
        if effect.get("consume_item"):
            item = effect["consume_item"]
            if item in p.inventory:
                p.inventory.remove(item)

        # Combat trigger
        if effect.get("combat"):
            self._begin_combat(effect["combat"])

        # Risk resolution
        if "risk" in effect:
            chance = float(effect["risk"])
            if w.weather == "storm":
                chance += 0.08
            if w.is_night:
                chance += 0.12
            if w.location == "Home Base":
                chance -= w.fortification * 0.04

            if random.random() < max(0.05, chance):
                dmg = random.randint(10, 20)
                p.health -= dmg
                if random.random() < 0.35:
                    p.infection += random.randint(5, 12)
                self.state.log.append("The scavenging run takes a violent turn! You take damage.")
                self.state.fx = "shake"
                await self.buzzer.danger()
            else:
                await self.buzzer.success()
                self.state.fx = "success"

        # Resources & Stats
        for k in ("health", "infection", "morale", "humanity", "food", "water", "ammo", "scrap", "medkits"):
            if k in effect:
                setattr(p, k, getattr(p, k) + int(effect[k]))
                if int(effect[k]) > 0 and k in ("food", "water", "ammo", "scrap", "medkits"):
                    self.state.fx = self.state.fx or "success"

        if "ammo_add" in effect:
            p.ammo += int(effect["ammo_add"])

        if "fort" in effect:
            w.fortification += int(effect["fort"])
        if effect.get("location"):
            w.location = effect["location"]
            self._discover(effect["location"])
            self.state.log.append(f"Arrived at {effect['location']}.")
        if effect.get("discover") or effect.get("discover2"):
            for name in (effect.get("discover"), effect.get("discover2")):
                if name:
                    self._discover(name)
        if effect.get("add_item"):
            self._give_item(effect["add_item"])
        if effect.get("weapon") and effect["weapon"] in WEAPONS:
            p.weapon = effect["weapon"]
            self.state.log.append(f"Equipped: {WEAPONS[p.weapon]['name']}.")
        if effect.get("flags"):
            w.flags.update(effect["flags"])
        if effect.get("npc_join"):
            self._npc_join(effect["npc_join"])
        if effect.get("npc_kill"):
            self._npc_kill(effect["npc_kill"])
        if effect.get("log"):
            self.state.log.append(effect["log"])

        # Check ending triggers from narrative flags
        ending_triggers = {
            "extract_halcyon",
            "chose_docks",
            "chose_ghost_path",
            "chose_sermon",
            "lena_sacrifice",
            "marcus_broadcast",
        }
        if any(w.flags.get(k) for k in ending_triggers):
            await self._trigger_ending()
            return

        self.state.clamp()
        self.display.show_health(p.health)

        # Handle menu redirects
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

    # ─────────────────────────────────────────────────────────────
    # COMBAT
    # ─────────────────────────────────────────────────────────────

    def _begin_combat(self, enemy_id: str):
        data = make_combat(enemy_id)
        self.state.combat = CombatState(**data)
        self.state.mode = "combat"
        self.state.log.append(f"── COMBAT ENGAGED: {self.state.combat.enemy_name.upper()} ──")
        self._combat_menu()

    async def _combat_act(self, action: str):
        result = resolve_player_action(self.state, action)
        for n in result.get("notes", []):
            self.state.log.append(n)
        self.state.fx = result.get("fx", "hit")

        # Sound feedback
        if self.state.fx == "gun":
            await self.buzzer.combat_gun()
        elif self.state.fx == "fire":
            await self.buzzer.combat_fire()
        elif self.state.fx == "hit":
            await self.buzzer.combat_hit()

        loot = result.get("loot") or {}
        for k, v in loot.items():
            setattr(self.state.player, k, getattr(self.state.player, k) + v)
            self.state.log.append(f"Scavenged {v} {k}.")

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

    # ─────────────────────────────────────────────────────────────
    # EXPEDITIONS & TIME
    # ─────────────────────────────────────────────────────────────

    async def _start_expedition(self, location: str):
        self._discover(location)
        self.state.world.location = location
        self.state.mode = "event"
        self.state.menu = ""
        blurb = LOCATIONS.get(location, {}).get("blurb", "")
        self.state.log.append(f"── EXPEDITION: {location.upper()} ──")
        if blurb:
            self.state.log.append(blurb)

        ev = select_event(self.state, location)
        self._present_event(ev)

    def _present_event(self, ev: Dict[str, Any]):
        if ev.get("id") not in self.state.world.seen_events:
            self.state.world.seen_events.append(ev["id"])
            if len(self.state.world.seen_events) > 150:
                self.state.world.seen_events = self.state.world.seen_events[-150:]

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
        self.state.log.append(ev["text"][:220])

    async def _craft(self, recipe_id: str):
        rec = next((r for r in RECIPES if r["id"] == recipe_id), None)
        if not rec:
            self._hub_menu()
            return

        if rec.get("need_item") and rec["need_item"] not in self.state.player.inventory:
            self.state.log.append("Missing required specialty components.")
            self._craft_menu()
            return

        if not self._can_afford(rec["cost"]):
            self.state.log.append("Insufficient scrap or resources for this recipe.")
            self._craft_menu()
            return

        p = self.state.player
        for k, v in rec["cost"].items():
            setattr(p, k, getattr(p, k) - v)

        if rec.get("give_item"):
            self._give_item(rec["give_item"])
        if rec.get("give_res"):
            for k, v in rec["give_res"].items():
                setattr(p, k, getattr(p, k) + v)
        if rec.get("weapon"):
            p.weapon = rec["weapon"]
        if rec.get("fort"):
            self.state.world.fortification += rec["fort"]
        if rec.get("flag"):
            self.state.world.flags[rec["flag"]] = True

        p.craft_count += 1
        self.state.log.append(rec.get("log") or f"Assembled {rec['name']}.")
        self.state.fx = "craft"
        await self.buzzer.success()
        self._hub_menu()

    async def _fortify(self):
        if self.state.player.scrap < 2:
            self.state.log.append("You lack the 2 scrap required to nail fresh boards.")
            self._fortify_menu()
            return
        self.state.player.scrap -= 2
        self.state.world.fortification = min(10, self.state.world.fortification + 1)
        self.state.log.append(f"Heavy timbers driven across the frame. Fortification is now {self.state.world.fortification}/10.")
        await self._spend_action()
        self._hub_menu()

    async def _rest(self):
        p, w = self.state.player, self.state.world
        heal = 20 + (10 if w.flags.get("medbay") else 0)
        p.health = min(100, p.health + heal)
        p.morale = min(100, p.morale + 6)
        self.state.log.append(f"You rest upon a canvas cot. Sleep restores {heal} health.")

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
                    "Channel 7 comes through crisp and clear over the boosted antenna. "
                    "Marcus Hale speaks of weather, survivor routes, and Fort Halcyon Mile 18."
                )
                choices: List[Dict[str, Any]] = [
                    {"label": "Listen to News", "effect": {"flags": {"heard_halcyon": True}, "morale": 6, "gemini": True}},
                    {
                        "label": "Call for Evac",
                        "effect": {"flags": {"extract_halcyon": True}},
                    }
                    if s.world.day >= 12
                    else {"label": "Monitor Frequencies", "effect": {"morale": 8, "gemini": True}},
                    {"label": "Tell a Radio Joke", "effect": {"morale": 10, "humanity": 4, "gemini": True}},
                    {"label": "Back to Hub", "effect": {"open": "hub"}},
                ]
            else:
                text = "Static hiss and crackling interference. You need radio parts from the tower to boost the receiver."
                choices = [
                    {"label": "Tune Frequencies", "effect": {"morale": 3, "gemini": True, "flags": {"heard_halcyon": True}}},
                    {"label": "Expedition to Tower", "effect": {"expedition": "Radio Tower"}},
                    {"label": "Back to Hub", "effect": {"open": "hub"}},
                    {"label": "Whistle into Mic", "effect": {"morale": 4, "gemini": True}},
                ]
                self._discover("Radio Tower")

            self.state.mode = "event"
            self._show("CHANNEL 7 BROADCAST", text, choices, "radio", "event", "BACK")
            return

        if who == "journal":
            stage = STAGE_LABEL[s.infection_stage()]
            text = (
                f"Day {s.world.day} Survivor Log. Health: {s.player.health}% · Infection: {stage}.\n"
                f"Humanity: {s.player.humanity}/100 · Weapon: {WEAPONS.get(s.player.weapon, WEAPONS['fists'])['name']}.\n"
                "You write ink upon paper so the city doesn't forget who lived behind this door."
            )
            self._show(
                "SURVIVOR LOG",
                text,
                [
                    {"label": "Record Thoughts of Hope", "effect": {"morale": 8, "humanity": 3, "gemini": True, "open": "hub"}},
                    {"label": "Write of the Lost", "effect": {"morale": -3, "humanity": 6, "gemini": True, "open": "hub"}},
                    {"label": "Check Companion Roster", "effect": {"open": "talk"}},
                    {"label": "Close Journal", "effect": {"open": "hub"}},
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
            "marcus": f"{npc['name']} cleans a microphone cartridge. 'As long as the tubes glow, friend, we're still a city.'",
            "lena": f"{npc['name']} adjusts a microscope slides. 'The infection is ruthless, but it follows biochemical law. Don't let your guard down.'",
            "kid": f"{s.kid_name} arranges brass casings in rows like toy soldiers. 'This one is our house,' they say softly.",
            "miriam": f"{npc['name']} pours boiled tea into a tin cup. 'Kindness isn't a luxury of peace; it is our only shield.'",
            "ghost": "Ghost raises two fingers in greeting, then draws a chalk arrow indicating safe sewer conduits.",
            "butcher": f"{npc['name']} sharpens his cleaver with a steady rhythm. 'Good meat keeps, friend. Everything else spoils.'",
            "dog": "Scraps thumps his tail against the floorboards and nudges your hand with a wet nose.",
        }
        text = lines.get(who, npc["name"] + " looks toward you.")
        choices: List[Dict[str, Any]] = [
            {"label": "Sit and Listen", "effect": {"morale": 7, "gemini": True, "open": "hub"}},
            {"label": "Share Ration (-1 Food)", "effect": {"food": -1, "humanity": 5, "morale": 8, "open": "hub"}},
            {"label": "Ask for Advice", "effect": {"morale": 4, "gemini": True, "open": "hub"}},
            {"label": "Return to Hub", "effect": {"open": "hub"}},
        ]
        if who == "lena" and s.player.infection >= 20:
            choices[2] = {"label": "Request Inhibitor Dose", "effect": {"infection": -15, "health": -6, "open": "hub"}}

        self._show(npc["short"].upper(), text, choices, who, "event", "BACK")

    def _give_item(self, item_id: str):
        p = self.state.player
        info = ITEMS.get(item_id, {"name": item_id})
        if item_id in p.inventory:
            self.state.log.append(f"You already carry {info['name']}.")
            return
        if len(p.inventory) >= INV_SLOTS:
            self.state.log.append("Pack is full (8/8). You must leave something behind.")
            return
        p.inventory.append(item_id)
        self.state.log.append(f"Acquired: {info['name']}.")
        if item_id in WEAPONS:
            p.weapon = item_id

    def _discover(self, name: str):
        if name and name not in self.state.world.known_locations and name in LOCATIONS:
            self.state.world.known_locations.append(name)
            self.state.log.append(f"New Location Mapped: {name}.")

    def _npc_join(self, npc_id: str):
        npc = self.state.world.npcs.get(npc_id)
        if not npc or not npc.get("alive"):
            return
        npc["met"] = True
        npc["at_base"] = True
        npc["trust"] = npc.get("trust", 0) + 3
        if npc_id == "kid":
            npc["name"] = self.state.kid_name
            npc["short"] = self.state.kid_name
        self.state.log.append(f"★ {npc['short']} has taken refuge under your roof.")
        self.state.fx = "join"

    def _npc_kill(self, npc_id: str):
        npc = self.state.world.npcs.get(npc_id)
        if not npc:
            return
        npc["alive"] = False
        npc["at_base"] = False
        self.state.log.append(f"† {npc['short']} has perished in the wasteland.")

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
        self.state.log.append(f"── NIGHTFALL DESCENDS · WEATHER: {w.weather.upper()} ──")
        self.state.fx = "night"
        await self.buzzer.nightfall()

        # Incursion risk calculation
        threat = 0.14 + (0.06 if w.weather == "storm" else 0) + (0.08 if self.state.player.infection >= 50 else 0)
        threat -= w.fortification * 0.03
        if w.flags.get("alarm"):
            threat -= 0.10
        if w.flags.get("has_dog"):
            threat -= 0.08

        if random.random() < max(0.02, threat) and w.fortification < 3 and w.day >= 3:
            self.state.log.append("Shamblers claw at the lower barricades! Planks splinter under weight.")
            if random.random() < 0.35 and w.fortification == 0:
                w.flags["death_cause"] = "breach"
                await self._trigger_ending()
                return
            self.state.player.health -= random.randint(12, 24)
            self.state.fx = "shake"
            await self.buzzer.danger()
        elif random.random() < 0.40:
            self.state.world.location = "Home Base"
            ev = select_event(self.state, "Home Base")
            self._present_event(ev)

    async def _dawn(self):
        w, p = self.state.world, self.state.player
        w.is_night = False
        w.day += 1
        p.days_survived = w.day
        w.actions_left = 2
        w.weather = random.choice(WEATHERS)

        # Rations consumed
        food_need = 1 + (1 if any(n.get("at_base") and n.get("alive") for n in w.npcs.values()) else 0)
        if w.flags.get("garden") and random.random() < 0.65:
            p.food += 1
            self.state.log.append("The window planter box produces fresh root greens (+1 Food).")

        if w.flags.get("rain_catcher") and w.weather in ("rain", "storm"):
            p.water += 2
            self.state.log.append("The gutter rain catcher fills with clean rainwater (+2 Water).")

        p.food = max(0, p.food - food_need)
        p.water = max(0, p.water - 1)
        self.state.log.append(f"── DAWN: DAY {w.day} · WEATHER: {w.weather.upper()} ──")

        # Starvation / Dehydration
        if p.food == 0 or p.water == 0:
            p.health -= 14
            p.morale -= 10
            self.state.log.append("Pangs of hunger and dehydration weaken your limbs (-14 HP).")
            if p.food == 0 and p.water == 0 and p.health <= 0:
                w.flags.setdefault("death_cause", "starved")

        # Infection tick
        if p.infection > 0:
            tick = 2 + (3 if self.state.infection_stage() in ("lucid", "turning") else 0)
            if "gas_mask" in p.inventory:
                tick = max(0, tick - 2)
            elif "mask" in p.inventory:
                tick = max(1, tick - 1)
            if w.flags.get("lena_treated"):
                tick = max(0, tick - 2)

            p.infection = min(100, p.infection + tick)
            if p.infection >= 30:
                p.health -= 2
            await self.buzzer.infection_tick()
            self.state.fx = "infect"

        if p.morale <= 20:
            p.health -= 5
            self.state.log.append("Despair weighs heavy upon your shoulders (-5 HP).")

        # Humanity reactions
        if p.humanity <= 18:
            for npc in w.npcs.values():
                if npc.get("at_base") and npc["id"] in ("miriam", "kid") and random.random() < 0.30:
                    npc["at_base"] = False
                    self.state.log.append(f"{npc['short']} slipped away into the night, terrified of what you are becoming.")

        self.display.show_health(p.health)
        await self.buzzer.dawn()

        # Day 21 Campaign victory evaluation
        if w.day >= 21 and not self.state.game_over:
            if not any(w.flags.get(k) for k in ("extract_halcyon", "chose_docks", "chose_quiet", "chose_ghost_path", "chose_sermon")):
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
            "pack_leader",
        )
        apply_ending(self.state, eid, victory)
        if victory:
            await self.buzzer.victory()
            self.display.show("P")
        else:
            await self.buzzer.game_over()
            self.display.show("E")
        self._ending_menu()
        self.state.save()
