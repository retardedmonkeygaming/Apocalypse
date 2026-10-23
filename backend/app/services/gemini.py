from backend.app.core.config import settings
from backend.app.core.state import GameState
from typing import Optional

class GeminiService:
    def __init__(self):
        self.enabled = bool(settings.gemini_api_key and settings.gemini_enabled)
        self.model = None
        if self.enabled:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                print("[Gemini] Ready")
            except Exception as e:
                print(f"[Gemini] Disabled: {e}")
                self.enabled = False

    async def generate_flavor(self, event_title: str, choice: str, state: GameState) -> Optional[str]:
        if not self.enabled or not self.model:
            return None
        prompt = (
            f"You are a grim survival radio operator in a zombie apocalypse. "
            f"Event: {event_title}. Player chose: {choice}. "
            f"Day {state.world.day}, Location: {state.world.location}, "
            f"Health {state.player.health}, Infection {state.player.infection}. "
            f"Write 1-2 short atmospheric sentences only. No quotes, no meta."
        )
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return None