from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    # Default off so Mac/PC development works without gpiozero devices.
    # Set USE_HARDWARE=true on the Raspberry Pi 4.
    use_hardware: bool = False
    # Single-player kiosk-mode heartbeat delay (s) broadcast back to clients.
    heartbeat_interval: float = 4.0
    # Root path the frontend templates are served from (repo root is the default).
    project_root: str = "."

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
