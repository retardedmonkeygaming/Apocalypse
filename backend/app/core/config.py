import os
import platform
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


def is_raspberry_pi() -> bool:
    """
    Auto-detect if running on a physical Raspberry Pi.
    Checks Linux device tree models and architecture.
    """
    try:
        # Check standard Raspberry Pi device tree files
        for path in ("/proc/device-tree/model", "/sys/firmware/devicetree/base/model"):
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    if "raspberry pi" in content:
                        return True
        # Check architecture on Linux
        if platform.system() == "Linux" and platform.machine() in ("armv7l", "aarch64", "armv6l"):
            # Further verification: check if /sys/class/gpio or /dev/gpiomem exists
            if os.path.exists("/dev/gpiomem") or os.path.exists("/sys/class/gpio"):
                return True
    except Exception:
        pass
    return False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_enabled: bool = False
    gemini_model: str = "gemini-1.5-flash"

    host: str = "0.0.0.0"
    port: int = 8000

    # Hardware mode: "auto" (default), "true", or "false".
    # In "auto" mode, hardware is enabled automatically if running on a Raspberry Pi.
    use_hardware: str = "auto"

    # Single-player kiosk-mode heartbeat delay (s) broadcast back to clients.
    heartbeat_interval: float = 4.0

    # Root path the frontend templates are served from (repo root is the default).
    project_root: str = "."

    # GPIO Pin mappings (BCM numbering)
    # 5 Arcade Pushbuttons
    pin_btn_red: int = 5
    pin_btn_blue: int = 6
    pin_btn_green: int = 13
    pin_btn_yellow: int = 19
    pin_btn_confirm: int = 16

    # 7-Segment Display (Segments A through G)
    pin_segment_a: int = 2
    pin_segment_b: int = 3
    pin_segment_c: int = 4
    pin_segment_d: int = 18
    pin_segment_e: int = 22
    pin_segment_f: int = 23
    pin_segment_g: int = 24

    # Passive Buzzer (PWM)
    pin_buzzer: int = 12

    @property
    def hardware_enabled(self) -> bool:
        """Determines if physical hardware GPIO should be activated."""
        val = str(self.use_hardware).strip().lower()
        if val in ("true", "1", "yes", "on"):
            return True
        if val in ("false", "0", "no", "off"):
            return False
        # "auto" mode: enable automatically if on a Raspberry Pi
        return is_raspberry_pi()


settings = Settings()
