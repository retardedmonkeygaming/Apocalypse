from typing import Callable, Optional, Dict
from backend.app.core.config import settings


class ButtonManager:
    """
    Hardware Arcade Button manager via gpiozero.
    5 arcade pushbuttons: Red, Blue, Green, Yellow, Confirm.
    Configured with pull_up=True (active low) and 0.1s bounce time.
    Supports software triggering for dual hardware/WebUI mirroring.
    """

    def __init__(self):
        self.callbacks: Dict[str, Optional[Callable]] = {
            "red": None,
            "blue": None,
            "green": None,
            "yellow": None,
            "confirm": None,
        }
        self._buttons: Dict[str, Optional[object]] = {}
        if settings.use_hardware:
            try:
                from gpiozero import Button

                mapping = {
                    "red": settings.pin_btn_red,
                    "blue": settings.pin_btn_blue,
                    "green": settings.pin_btn_green,
                    "yellow": settings.pin_btn_yellow,
                    "confirm": settings.pin_btn_confirm,
                }
                for name, pin in mapping.items():
                    btn = Button(pin, pull_up=True, bounce_time=0.1)
                    btn.when_pressed = lambda n=name: self._on_press(n)
                    self._buttons[name] = btn
                print(f"[Hardware] 5 Arcade Buttons initialized on pins: {mapping}")
            except Exception as e:
                print(f"[Hardware] Buttons initialization failed: {e} — continuing in software mode")

    def _on_press(self, name: str):
        cb = self.callbacks.get(name)
        if cb:
            try:
                cb()
            except Exception as e:
                print(f"[Hardware] Error in button callback {name}: {e}")

    def on(self, name: str, callback: Callable):
        self.callbacks[name] = callback

    def trigger(self, name: str):
        """Software trigger (from WebUI or test scripts)."""
        self._on_press(name)
