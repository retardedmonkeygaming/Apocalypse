import asyncio
import os
from pathlib import Path
from typing import Optional
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

# gpiozero fires button callbacks on its own thread, where there is no running
# asyncio loop. We capture the server loop at startup and marshal callbacks
# onto it with run_coroutine_threadsafe instead of asyncio.create_task.
_main_loop: Optional[asyncio.AbstractEventLoop] = None


def _make_handler(key: str):
    async def handler():
        if key == "confirm":
            await engine.handle_confirm()
        else:
            await engine.handle_choice(key)

    return handler


def _dispatch(key: str):
    """Schedule a button press on the server event loop from any thread."""
    coro = _make_handler(key)()
    if _main_loop and _main_loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, _main_loop)
    else:
        # Fallback for contexts already inside the loop (tests / software mode)
        try:
            asyncio.get_running_loop().create_task(coro)
        except RuntimeError:
            pass


def _wire_button(name: str, key: str):
    button_mgr.on(name, lambda k=key: _dispatch(k))


_wire_button("red", "red")
_wire_button("blue", "blue")
_wire_button("green", "green")
_wire_button("yellow", "yellow")
_wire_button("confirm", "confirm")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _main_loop
    _main_loop = asyncio.get_running_loop()
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


@app.get("/api/state")
async def api_state():
    """Instant first paint — the page renders from this before the WebSocket connects."""
    return engine.state.to_dict()


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

    # Pass the app object directly — a string import would re-execute this
    # module and re-initialize all GPIO hardware a second time.
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=False,
    )
