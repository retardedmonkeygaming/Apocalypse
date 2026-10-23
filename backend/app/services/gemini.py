import asyncio
from typing import Optional

from backend.app.core.config import settings
from backend.app.core.state import GameState


class GeminiService:
    def __init__(self):
        self.enabled = bool(settings.gemini_api_key and settings.gemini_enabled)
        self.model = None
        if self.enabled:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                print("[Gemini] Ready (flavor text only)")
            except Exception as e:
                print(f"[Gemini] Disabled: {e}")
                self.enabled = False

    async def generate_flavor(self, event_title: str, choice: str, state: GameState) -> Optional[str]:
        if not self.enabled or not self.model:
            return None

        def _run():
            prompt = (
                "You are Channel 7, a grim but humane emergency radio in a zombie city. "
                f"Beat: {event_title}. The survivor chose: {choice}. "
                f"Day {state.world.day}, {state.world.location}, {state.world.weather}, "
                f"HP {state.player.health}, infection {state.player.infection}, "
                f"humanity {state.player.humanity}. "
                "Write 1-2 short atmospheric sentences. No quotes, no lists, no meta, no advice."
            )
            response = self.model.generate_content(prompt)
            return (response.text or "").strip()[:400]

        try:
            return await asyncio.wait_for(asyncio.to_thread(_run), timeout=8)
        except Exception:
            return None
