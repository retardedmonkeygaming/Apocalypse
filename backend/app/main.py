import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from backend.app.core.config import settings
from backend.app.game.engine import GameEngine
from backend.app.api.routes import router, set_engine
from backend.app.api.websocket import manager
from backend.app.hardware.buttons import ButtonManager

app = FastAPI(title="Apocalypse Terminal")

# Paths
BASE = Path(__file__).resolve().parent.parent.parent
FRONTEND = BASE / "frontend"

app.mount("/static", StaticFiles(directory=FRONTEND / "static"), name="static")
app.include_router(router)

engine = GameEngine()
set_engine(engine)

button_mgr = ButtonManager()

def make_handler(key: str):
    async def handler():
        if key == "confirm":
            await engine.use_medkit()
        else:
            await engine.handle_choice(key)
    return handler

# Wire physical buttons
for color in ["red", "blue", "green", "yellow"]:
    button_mgr.on(color, lambda k=color: asyncio.create_task(make_handler(k)()))
button_mgr.on("confirm", lambda: asyncio.create_task(make_handler("confirm")()))

@app.on_event("startup")
async def startup():
    async def broadcaster(data):
        await manager.broadcast(data)
    engine.set_broadcast(broadcaster)
    # Start with an event if fresh
    if not engine.state.current_event and not engine.state.game_over:
        await engine.next_event()
    print(f"Apocalypse Terminal running on http://{settings.host}:{settings.port}")

@app.get("/")
async def index():
    return FileResponse(FRONTEND / "templates" / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )