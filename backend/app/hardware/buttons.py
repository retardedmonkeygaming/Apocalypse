from typing import Callable, Optional, Dict
from backend.app.core.config import settings


_INSTANCE = None


def _shared() -> "ButtonManager":
    """Return the single shared ButtonManager instance.

    Prevents double GPIO claims when the app module gets imported twice
    (e.g. `python -m backend.app.main` plus uvicorn's string import).
    """
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = object.__new__(ButtonManager)
        _INSTANCE.callbacks = {
            "red": None,
            "blue": None,
            "green": None,
            "yellow": None,
            "confirm": None,
        }
        _INSTANCE._buttons = {}
        _INSTANCE._init_hw()
    return _INSTANCE


class ButtonManager:
    """
    Hardware Arcade Button manager via gpiozero.
    5 arcade pushbuttons: Red, Blue, Green, Yellow, Confirm.
    Configured with pull_up=True (active low) and 0.1s bounce time.
    Supports software triggering for dual hardware/WebUI mirroring.
    Instantiation returns the shared singleton (see _shared).
    """

    def __new__(cls):
        return _shared()

    def _init_hw(self):
        if not settings.use_hardware:
            return
        try:
            from gpiozero import Button
        except Exception as e:
            print(f"[Hardware] gpiozero unavailable: {e} — software mode")
            return

        mapping = {
            "red": settings.pin_btn_red,
            "blue": settings.pin_btn_blue,
            "green": settings.pin_btn_green,
            "yellow": settings.pin_btn_yellow,
            "confirm": settings.pin_btn_confirm,
        }

        # Try each pin factory in turn. On a Pi 4 the default (lgpio) can fail
        # to create its notify file and silently fall back to a factory that
        # cannot do edge detection — which used to kill ALL five buttons.
        for label, factory in self._factory_candidates():
            live = {}
            for name, pin in mapping.items():
                try:
                    kwargs = {"pull_up": True, "bounce_time": 0.1}
                    if factory is not None:
                        kwargs["pin_factory"] = factory
                    btn = Button(pin, **kwargs)
                    btn.when_pressed = lambda n=name: self._on_press(n)
                    live[name] = btn
                except Exception as e:
                    print(f"[Hardware] {name} (BCM {pin}) via {label} failed: {e}")
            if live:
                self._buttons = live
                print(f"[Hardware] {len(live)}/5 arcade buttons live via {label} — "
                      f"pins {mapping}")
                return

        # Nothing could attach an edge listener — poll the levels instead.
        # Reading a pin high/low still works where interrupts do not.
        if self._start_polling(mapping):
            return
        print("[Hardware] Buttons initialization failed — continuing in software mode")

    def _factory_candidates(self):
        """Yield (label, factory_or_None) pairs, best first."""
        out = []
        try:
            from gpiozero.pins.lgpio import LGPIOPinFactory
            out.append(("lgpio", LGPIOPinFactory()))
        except Exception:
            pass
        try:
            import gpiozero.pins.rpigpio as _rp
            out.append(("rpigpio", _rp.RPiIOPinFactory()))
        except Exception:
            pass
        try:
            import gpiozero.pins.rpio as _ro
            out.append(("rpio", _ro.RPiIOPinFactory()))
        except Exception:
            pass
        try:
            from gpiozero import Device
            out.append(("default", Device.pin_factory))
        except Exception:
            out.append(("default", None))
        return out

    def _start_polling(self, mapping) -> bool:
        """Last-resort button path: a daemon thread sampling the pin levels."""
        import threading

        pins = {}
        for label, factory in self._factory_candidates():
            try:
                if factory is None:
                    continue
                for name, num in mapping.items():
                    p = factory.pin(num)
                    try:
                        p.function = "input"
                    except Exception:
                        pass
                    try:
                        p.pull = "up"
                    except Exception:
                        pass
                    pins[name] = p
                if pins:
                    break
            except Exception as e:
                print(f"[Hardware] polling via {label} failed: {e}")
                pins = {}
        if not pins:
            return False

        state = {name: 1 for name in pins}
        last_change = {name: 0.0 for name in pins}

        def _loop():
            import time as _t
            while True:
                now = _t.monotonic()
                for name, p in pins.items():
                    try:
                        v = p.state
                    except Exception:
                        continue
                    prev = state[name]
                    if v != prev and (now - last_change[name]) > 0.1:
                        state[name] = v
                        last_change[name] = now
                        if v == 0:          # pull_up → pressed reads low
                            self._on_press(name)
                _t.sleep(0.04)

        threading.Thread(target=_loop, daemon=True, name="apoc-buttons").start()
        return True

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
