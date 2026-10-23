import asyncio
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.game.engine import GameEngine
from backend.app.api.routes import router, set_engine
from backend.app.api.websocket import manager
from backend.app.hardware.buttons import ButtonManager

engine = GameEngine()
set_engine(engine)
engine.set_broadcast(manager.broadcast)
button_mgr = ButtonManager()


def _make_handler(key: str):
    async def handler():
        if key == "confirm":
            await engine.handle_confirm()
        else:
            await engine.handle_choice(key)

    return handler


def _wire_button(name: str, key: str):
    button_mgr.on(name, lambda k=key: asyncio.create_task(_make_handler(k)()))


_wire_button("red", "red")
_wire_button("blue", "blue")
_wire_button("green", "green")
_wire_button("yellow", "yellow")
_wire_button("confirm", "confirm")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine.set_broadcast(manager.broadcast)
    engine.display.show_health(engine.state.player.health)

    # ── Startup diagnostic ────────────────────────────────────────
    env_path = Path(".env").resolve()
    hw = settings.use_hardware
    gem = engine.gemini.enabled
    print(f"Apocalypse Terminal  http://{settings.host}:{settings.port}")
    print(f"Hardware={'on' if hw else 'off'}  Gemini={'on' if gem else 'off'}")
    if not hw:
        print(
            f"[Config] USE_HARDWARE=false — set USE_HARDWARE=true in your .env to enable GPIO.\n"
            f"         Env file searched at: {env_path}"
        )
    if hw:
        print(f"[Hardware] GPIO pins — Red:{settings.pin_btn_red} Blue:{settings.pin_btn_blue} "
              f"Green:{settings.pin_btn_green} Yellow:{settings.pin_btn_yellow} "
              f"Confirm:{settings.pin_btn_confirm} | Buzzer:{settings.pin_buzzer}")
    # ─────────────────────────────────────────────────────────────
    yield


app = FastAPI(title="Apocalypse Terminal", docs_url=None, redoc_url=None, lifespan=lifespan)

BASE = Path(settings.project_root or ".").resolve()
FRONTEND = BASE / "frontend"

app.mount("/static", StaticFiles(directory=FRONTEND / "static"), name="static")
app.include_router(router)


@app.get("/ping")
async def ping():
    await manager.broadcast({"type": "heartbeat", "ts": asyncio.get_event_loop().time()})
    return {"ok": True}


@app.get("/")
async def index():
    return FileResponse(FRONTEND / "templates" / "index.html")


@app.get("/health")
async def health():
    return {"ok": True, "hardware": settings.use_hardware, "gemini": engine.gemini.enabled}


@app.get("/api/config")
async def api_config():
    """Debug endpoint — returns resolved settings (safe subset, no secrets)."""
    return {
        "use_hardware": settings.use_hardware,
        "host": settings.host,
        "port": settings.port,
        "gemini_enabled": engine.gemini.enabled,
        "pins": {
            "red": settings.pin_btn_red,
            "blue": settings.pin_btn_blue,
            "green": settings.pin_btn_green,
            "yellow": settings.pin_btn_yellow,
            "confirm": settings.pin_btn_confirm,
            "buzzer": settings.pin_buzzer,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
