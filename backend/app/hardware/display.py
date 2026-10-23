from backend.app.core.config import settings

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
    "H": [0, 1, 1, 0, 1, 1, 1],
    "E": [1, 0, 0, 1, 1, 1, 1],
    "L": [0, 0, 0, 1, 1, 1, 0],
    "P": [1, 1, 0, 0, 1, 1, 1],
    " ": [0, 0, 0, 0, 0, 0, 0],
    "-": [0, 0, 0, 0, 0, 0, 1],
}


class SevenSegment:
    def __init__(self):
        self.pins: list = []
        self.last = " "
        if settings.use_hardware:
            try:
                from gpiozero import LED

                pin_numbers = [2, 3, 4, 18, 22, 23, 24]
                self.pins = [LED(p) for p in pin_numbers]
                print("[Hardware] 7-segment ready")
            except Exception as e:
                print(f"[Hardware] 7-segment failed: {e}")
                settings.use_hardware = False

    def show(self, char: str):
        self.last = str(char)[0].upper()
        pattern = CHAR_MAP.get(self.last, CHAR_MAP[" "])
        for led, val in zip(self.pins, pattern):
            if val:
                led.on()
            else:
                led.off()

    def clear(self):
        self.show(" ")

    def show_health(self, health: int):
        digit = str(min(9, max(0, health // 10)))
        self.show(digit)
