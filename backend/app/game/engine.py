import asyncio
import random
from typing import Optional, Dict, Any
from backend.app.core.state import GameState
from backend.app.game.events import get_random_event
from backend.app.game.combat import resolve_risk
from backend.app.hardware.display import SevenSegment
from backend.app.hardware.buzzer import Buzzer
from backend.app.services.gemini import GeminiService
from backend.app.services.save import SaveService

class GameEngine:
    def __init__(self):
        self.state = GameState.load()
        self.display = SevenSegment()
        self.buzzer = Buzzer()
        self.gemini = GeminiService()
        self.save = SaveService()
        self._broadcast = None          # set by websocket layer
        self._lock = asyncio.Lock()

    def set_broadcast(self, callback):
        self._broadcast = callback

    async def broadcast(self):
        if self._broadcast:
            await self._broadcast(self.state.to_dict())

    async def start_new_game(self):
        self.state = GameState()
        self.state.log.append("You wake up in the safehouse. The world has ended.")
        await self.next_event()
        self.display.show_health(self.state.player.health)
        await self.broadcast()

    async def next_event(self):
        if self.state.game_over:
            return
        event = get_random_event(self.state.world.is_night)
        self.state.current_event = event
        self.state.waiting_for_choice = True
        self.state.log.append(f"── {event['title']} ──")
        self.state.log.append(event["text"])
        await self.broadcast()

    async def handle_choice(self, key: str):
        async with self._lock:
            if not self.state.waiting_for_choice or not self.state.current_event:
                return

            choices = self.state.current_event.get("choices", [])
            choice = next((c for c in choices if c["key"] == key), None)
            if not choice:
                return

            self.state.waiting_for_choice = False
            self.state.last_action = choice["label"]
            self.state.log.append(f"> {choice['label']}")

            effect = choice.get("effect", {})
            await self.apply_effect(effect)

            # Optional Gemini flavor
            if choice.get("gemini") and self.gemini.enabled:
                extra = await self.gemini.generate_flavor(
                    self.state.current_event["title"],
                    choice["label"],
                    self.state
                )
                if extra:
                    self.state.log.append(extra)

            # Check death
            if self.state.player.health <= 0:
                self.state.game_over = True
                self.state.log.append("YOU DIED.")
                await self.buzzer.danger()
                self.display.show("E")
                await self.broadcast()
                return

            # Advance time occasionally
            if random.random() < 0.4:
                await self.advance_time()

            self.state.save()
            await self.broadcast()

            # Small delay then next event
            await asyncio.sleep(1.2)
            await self.next_event()

    async def apply_effect(self, effect: Dict[str, Any]):
        p = self.state.player
        for k, v in effect.items():
            if k == "risk":
                if resolve_risk(v):
                    p.health -= random.randint(8, 20)
                    self.state.log.append("It goes wrong...")
                    await self.buzzer.danger()
                else:
                    await self.buzzer.success()
            elif k == "location":
                self.state.world.location = v
                self.state.log.append(f"Moved to {v}")
            elif hasattr(p, k):
                setattr(p, k, max(0, getattr(p, k) + v))
                if v > 0:
                    await self.buzzer.success()
                elif k == "health" and v < 0:
                    await self.buzzer.low_health()

        # Infection passive
        if p.infection > 0 and random.random() < 0.3:
            p.health -= 2
            await self.buzzer.infection_tick()

        self.display.show_health(p.health)

    async def use_medkit(self):
        if self.state.player.medkits > 0 and self.state.player.health < 100:
            self.state.player.medkits -= 1
            self.state.player.health = min(100, self.state.player.health + 35)
            self.state.player.infection = max(0, self.state.player.infection - 10)
            self.state.log.append("Used medkit.")
            self.display.show_health(self.state.player.health)
            await self.buzzer.success()
            self.state.save()
            await self.broadcast()

    async def advance_time(self):
        w = self.state.world
        if w.is_night:
            w.is_night = False
            w.day += 1
            self.state.log.append(f"── DAY {w.day} ──")
            # Daily consumption
            self.state.player.food = max(0, self.state.player.food - 1)
            self.state.player.water = max(0, self.state.player.water - 1)
            if self.state.player.food == 0 or self.state.player.water == 0:
                self.state.player.health -= 10
                self.state.log.append("Starving / dehydrated...")
            await self.buzzer.success()
        else:
            w.is_night = True
            self.state.log.append("Night falls.")
            await self.buzzer.nightfall()

        # Victory condition example
        if w.day >= 14 and self.state.player.health > 50:
            self.state.victory = True
            self.state.game_over = True
            self.state.log.append("You survived two weeks. Signal for extraction received.")
            await self.buzzer.success()