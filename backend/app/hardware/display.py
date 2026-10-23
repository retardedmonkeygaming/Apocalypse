from backend.app.core.config import settings

# Segments ordered [A, B, C, D, E, F, G]
CHAR_MAP = {
    "0": [1, 1, 1, 1, 1, 1, 0],
    "1": [0, 1, 1, 0, 0, 0, 0],
    "2": [1, 1, 0, 1, 1, 0, 1],
    "3": [1, 1, 1, 1, 0, 0, 1],
    "4": [0, 1, 1, 0, 0, 1, 1],
    "5": [1, 0, 1, 1, 0, 1, 1],
    "6": [1, 0, 1, 1, 1, 1, 1],
    "7": [1, 1, 1, 0, 0, 0, 0],
    "8": [1, 1, 1, 1, 1, 1, 1],
    "9": [1, 1, 1, 1, 0, 1, 1],
    "A": [1, 1, 1, 0, 1, 1, 1],
    "b": [0, 0, 1, 1, 1, 1, 1],
    "C": [1, 0, 0, 1, 1, 1, 0],
    "c": [0, 0, 0, 1, 1, 0, 1],
    "d": [0, 1, 1, 1, 1, 0, 1],
    "E": [1, 0, 0, 1, 1, 1, 1],
    "F": [1, 0, 0, 0, 1, 1, 1],
    "H": [0, 1, 1, 0, 1, 1, 1],
    "h": [0, 0, 1, 0, 1, 1, 1],
    "L": [0, 0, 0, 1, 1, 1, 0],
    "n": [0, 0, 1, 0, 1, 0, 1],
    "o": [0, 0, 1, 1, 1, 0, 1],
    "P": [1, 1, 0, 0, 1, 1, 1],
    "r": [0, 0, 0, 0, 1, 0, 1],
    "t": [0, 0, 0, 1, 1, 1, 1],
    "-": [0, 0, 0, 0, 0, 0, 1],
    "_": [0, 0, 0, 1, 0, 0, 0],
    " ": [0, 0, 0, 0, 0, 0, 0],
}


class SevenSegment:
    """
    Hardware 7-segment single digit LED controller.
    Segments A through G wired to GPIO pins.
    Gracefully runs as software-only when hardware is absent.
    """

    def __init__(self):
        self.pins = []
        self.last = " "
        self.active = False

        if settings.hardware_enabled:
            try:
                from gpiozero import LED

                pin_numbers = [
                    settings.pin_segment_a,
                    settings.pin_segment_b,
                    settings.pin_segment_c,
                    settings.pin_segment_d,
                    settings.pin_segment_e,
                    settings.pin_segment_f,
                    settings.pin_segment_g,
                ]
                self.pins = [LED(p) for p in pin_numbers]
                self.active = True
                print(f"[Hardware] 7-Segment Display ONLINE on BCM pins {pin_numbers}")
            except Exception as e:
                print(f"[Hardware] 7-Segment initialization skipped: {e}")
                self.pins = []
        else:
            print("[Hardware] 7-Segment Display running in software emulation mode")

    def show(self, char: str):
        if not char:
            char = " "
        self.last = str(char)[0]
        pattern = CHAR_MAP.get(self.last)
        if pattern is None:
            pattern = CHAR_MAP.get(self.last.upper(), CHAR_MAP[" "])

        if self.pins:
            for led, val in zip(self.pins, pattern):
                try:
                    if val:
                        led.on()
                    else:
                        led.off()
                except Exception:
                    pass

    def clear(self):
        self.show(" ")

    def show_health(self, health: int):
        """Show health tens digit (100 -> 9, 85 -> 8, 0 -> 0)."""
        digit = str(min(9, max(0, health // 10)))
        self.show(digit)
