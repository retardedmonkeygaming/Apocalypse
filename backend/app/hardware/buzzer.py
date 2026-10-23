import asyncio
from typing import Optional
from backend.app.core.config import settings


class Buzzer:
    """
    Hardware passive buzzer controller via gpiozero PWMOutputDevice.
    Generates chiptune melodies, alarms, and audio feedback for the physical arcade cabinet.
    Silently acts as a no-op if hardware is disabled or unavailable.
    """

    def __init__(self):
        self.device = None
        self.active = False

        if settings.hardware_enabled:
            try:
                from gpiozero import PWMOutputDevice

                self.device = PWMOutputDevice(settings.pin_buzzer, frequency=440, initial_value=0)
                self.active = True
                print(f"[Hardware] Passive Buzzer ONLINE on BCM pin {settings.pin_buzzer}")
            except Exception as e:
                print(f"[Hardware] Buzzer initialization skipped: {e}")
                self.device = None
        else:
            print("[Hardware] Buzzer running in Web Audio emulation mode")

    async def tone(self, freq: int = 440, duration: float = 0.12, duty: float = 0.5):
        if not self.device:
            return
        try:
            self.device.frequency = max(20, min(8000, int(freq)))
            self.device.value = duty
            await asyncio.sleep(duration)
            self.device.value = 0
        except Exception:
            pass

    async def success(self):
        """Ascending chime (C5 -> E5 -> G5)."""
        await self.tone(523, 0.08, 0.4)
        await asyncio.sleep(0.02)
        await self.tone(659, 0.08, 0.4)
        await asyncio.sleep(0.02)
        await self.tone(784, 0.14, 0.4)

    async def danger(self):
        """Warning klaxon tritone."""
        for _ in range(2):
            await self.tone(880, 0.07, 0.6)
            await asyncio.sleep(0.03)
            await self.tone(622, 0.07, 0.6)
            await asyncio.sleep(0.03)

    async def nightfall(self):
        """Descending dusk drone (A3 -> F3 -> D3)."""
        await self.tone(220, 0.22, 0.4)
        await self.tone(174, 0.28, 0.35)
        await self.tone(146, 0.35, 0.3)

    async def dawn(self):
        """Uplifting dawn fanfare."""
        await self.tone(392, 0.10, 0.4)
        await self.tone(523, 0.12, 0.4)
        await self.tone(659, 0.18, 0.4)

    async def low_health(self):
        """Deep warning pulse."""
        await self.tone(140, 0.18, 0.6)
        await asyncio.sleep(0.08)
        await self.tone(110, 0.22, 0.6)

    async def infection_tick(self):
        """Sickly chromatic wobble."""
        await self.tone(310, 0.06, 0.35)
        await self.tone(250, 0.08, 0.35)

    async def combat_hit(self):
        """Melee strike thud."""
        await self.tone(180, 0.06, 0.5)
        await self.tone(90, 0.08, 0.5)

    async def combat_gun(self):
        """Gunshot crack."""
        await self.tone(1600, 0.03, 0.7)
        await self.tone(220, 0.06, 0.5)

    async def combat_fire(self):
        """Molotov flame whoosh."""
        await self.tone(340, 0.09, 0.45)
        await self.tone(210, 0.14, 0.4)

    async def victory(self):
        """Triumphant victory fanfare."""
        for f, d in [(523, 0.1), (659, 0.1), (784, 0.1), (1046, 0.28)]:
            await self.tone(f, d, 0.5)
            await asyncio.sleep(0.03)

    async def game_over(self):
        """Melancholy death dirge."""
        for f, d in [(440, 0.2), (415, 0.2), (392, 0.2), (349, 0.4)]:
            await self.tone(f, d, 0.5)
            await asyncio.sleep(0.04)
