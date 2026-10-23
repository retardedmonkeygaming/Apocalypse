from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_enabled: bool = False
    gemini_model: str = "gemini-1.5-flash"

    host: str = "0.0.0.0"
    port: int = 8000

    # Default off so Mac/PC development works without gpiozero devices.
    # Set USE_HARDWARE=true on the Raspberry Pi 4.
    use_hardware: bool = False

    # Single-player kiosk-mode heartbeat delay (s) broadcast back to clients.
    heartbeat_interval: float = 4.0

    # Root path the frontend templates are served from (repo root is the default).
    project_root: str = "."

    # GPIO Pin mappings (BCM numbering)
    pin_btn_red: int = 5
    pin_btn_blue: int = 6
    pin_btn_green: int = 13
    pin_btn_yellow: int = 19
    pin_btn_confirm: int = 16

    pin_segment_a: int = 2
    pin_segment_b: int = 3
    pin_segment_c: int = 4
    pin_segment_d: int = 18
    pin_segment_e: int = 22
    pin_segment_f: int = 23
    pin_segment_g: int = 24

    pin_buzzer: int = 12


settings = Settings()
