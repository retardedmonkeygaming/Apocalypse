import asyncio
from backend.app.core.config import settings


class Buzzer:
    def __init__(self):
        self.device = None
        if settings.use_hardware:
            try:
                from gpiozero import PWMOutputDevice

                self.device = PWMOutputDevice(12, frequency=440, initial_value=0)
                print("[Hardware] Buzzer ready")
            except Exception as e:
                print(f"[Hardware] Buzzer failed: {e}")

    async def tone(self, freq: int = 440, duration: float = 0.15, duty: float = 0.5):
        if not self.device:
            return
        self.device.frequency = max(20, int(freq))
        self.device.value = duty
        await asyncio.sleep(duration)
        self.device.value = 0

    async def danger(self):
        for f in (880, 720, 880):
            await self.tone(f, 0.09)
            await asyncio.sleep(0.04)

    async def success(self):
        await self.tone(523, 0.08)
        await self.tone(659, 0.08)
        await self.tone(784, 0.14)

    async def nightfall(self):
        await self.tone(220, 0.22, 0.3)
        await self.tone(174, 0.35, 0.25)

    async def low_health(self):
        await self.tone(150, 0.3)

    async def infection_tick(self):
        await self.tone(300, 0.07)
        await self.tone(240, 0.07)
