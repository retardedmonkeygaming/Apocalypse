from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.api.websocket import manager
from backend.app.game.engine import GameEngine

router = APIRouter()
engine: GameEngine = None  # injected at startup

def set_engine(e: GameEngine):
    global engine
    engine = e

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    # Send current state immediately
    await websocket.send_json(engine.state.to_dict())
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "choice":
                await engine.handle_choice(data.get("key"))
            elif action == "medkit":
                await engine.use_medkit()
            elif action == "new_game":
                await engine.start_new_game()
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)