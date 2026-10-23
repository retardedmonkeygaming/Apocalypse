import asyncio
import logging
from typing import Optional
import httpx

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        self.enabled = bool(settings.gemini_api_key and settings.gemini_enabled)
        self.model = settings.gemini_model or "gemini-1.5-flash"
        self.api_key = settings.gemini_api_key
        if self.enabled:
            print(f"[Gemini] Enabled using model: {self.model} (flavor text only)")
        else:
            print("[Gemini] Offline mode active (using authored flavor)")

    async def generate_flavor(self, event_title: str, choice: str, state) -> Optional[str]:
        """
        Generate a brief 1-2 sentence radio broadcast or atmospheric journal beat.
        Returns None on any error or timeout; game continues with 100% authored content.
        """
        if not self.enabled or not self.api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        prompt = (
            "You are Channel 7, a grim, atmospheric, retro emergency radio broadcaster in an apocalyptic zombie-infested city. "
            f"Current event: '{event_title}'. Survivor action: '{choice}'. "
            f"Context: Day {state.world.day}, Time: {'Night' if state.world.is_night else 'Day'}, Weather: {state.world.weather}, "
            f"Location: {state.world.location}, Health: {state.player.health}%, Infection: {state.infection_stage()} ({state.player.infection}%), "
            f"Humanity: {state.player.humanity}/100. "
            "Write 1-2 short, atmospheric, gritty sentences as a radio excerpt or survivor whisper. "
            "Never use markdown, lists, quotes, meta commentary, or advice. Keep it under 250 characters."
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 90,
                "topP": 0.9,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        clean = text.strip().replace('"', '').replace('\n', ' ')
                        if clean:
                            return clean[:280]
        except Exception as e:
            logger.debug(f"[Gemini] Request failed: {e}")
            return None
        return None
