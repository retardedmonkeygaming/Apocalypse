import asyncio
import os
import time
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


# ── Hardware button COMBINATIONS ──────────────────────────────
# Two physical arcade buttons pressed within 450ms fire a cabinet-level
# command instead of two individual choices (mirrors the WebUI combos).
_COMBO_LAST = {"key": None, "t": 0.0}
COMBO_WINDOW = 0.45
HARDWARE_COMBOS = {
    frozenset(("red", "yellow")): "story_page",   # next story-select page
    frozenset(("red", "blue")): "map",            # web map overlay ack
    frozenset(("green", "yellow")): "guide",      # web guide overlay ack
}


def _schedule(coro):
    if _main_loop and _main_loop.is_running():
        asyncio.run_coroutine_threadsafe(coro, _main_loop)
    else:
        try:
            asyncio.get_running_loop().create_task(coro)
        except RuntimeError:
            pass


async def _combo_action(name: str):
    if name == "story_page":
        await engine.cycle_page()
    else:
        # Map / Guide overlays live in the WebUI; acknowledge on the buzzer.
        try:
            await engine.buzzer.success()
        except Exception:
            pass


def _dispatch(key: str):
    """Schedule a button press on the server event loop from any thread.

    Choice buttons (red/blue/green/yellow) are also scanned for combos:
    two distinct buttons within COMBO_WINDOW collapse into one command.
    """
    if key in ("red", "blue", "green", "yellow"):
        now = time.monotonic()
        last = _COMBO_LAST["key"]
        if last and last != key and (now - _COMBO_LAST["t"]) <= COMBO_WINDOW:
            combo = HARDWARE_COMBOS.get(frozenset((last, key)))
            _COMBO_LAST["key"] = None
            _COMBO_LAST["t"] = 0.0
            if combo:
                _schedule(_combo_action(combo))
                return  # swallow both individual presses
        _COMBO_LAST["key"] = key
        _COMBO_LAST["t"] = now

    _schedule(_make_handler(key)())


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
    engine._sync_seg()  # keep the 7-segment mirror truthful even before the WS opens
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
