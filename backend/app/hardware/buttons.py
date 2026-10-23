from typing import Callable, Optional
from backend.app.core.config import settings

class ButtonManager:
    def __init__(self):
        self.callbacks: dict[str, Optional[Callable]] = {
            "red": None, "blue": None, "green": None, "yellow": None, "confirm": None
        }
        self._buttons = {}
        if settings.use_hardware:
            try:
                from gpiozero import Button
                mapping = {
                    "red": 5, "blue": 6, "green": 13, "yellow": 19, "confirm": 16
                }
                for name, pin in mapping.items():
                    btn = Button(pin, pull_up=True, bounce_time=0.1)
                    btn.when_pressed = lambda n=name: self._on_press(n)
                    self._buttons[name] = btn
                print("[Hardware] Buttons initialized")
            except Exception as e:
                print(f"[Hardware] Buttons failed: {e} – running in software mode")
                settings.use_hardware = False

    def _on_press(self, name: str):
        cb = self.callbacks.get(name)
        if cb:
            cb()

    def on(self, name: str, callback: Callable):
        self.callbacks[name] = callback

    def trigger(self, name: str):
        """Software trigger (from WebUI clicks)"""
        self._on_press(name)