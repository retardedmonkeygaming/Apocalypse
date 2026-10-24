from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.api.websocket import manager
from backend.app.game.engine import GameEngine


router = APIRouter()
engine: Optional[GameEngine] = None


def set_engine(e: GameEngine):
    global engine
    engine = e


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    if engine:
        await websocket.send_json(engine.state.to_dict())
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if not engine:
                continue

            if action == "choice":
                await engine.handle_choice(data.get("key"))
            elif action in ("medkit", "confirm"):
                await engine.handle_confirm()
            elif action == "new_game":
                await engine.start_new_game()
            elif action == "page":
                await engine.cycle_page()
            elif action == "use_item":
                item_id = data.get("item_id")
                if item_id == "medkit" or item_id == "medkits":
                    await engine.use_medkit()
                elif item_id == "antibiotics" and "antibiotics" in engine.state.player.inventory:
                    engine.state.player.inventory.remove("antibiotics")
                    engine.state.player.infection = max(0, engine.state.player.infection - 25)
                    engine.state.player.health = min(100, engine.state.player.health + 10)
                    engine.state.log.append("Swallowed pharmaceutical antibiotics. The burning fever recedes.")
                    engine.state.fx = "heal"
                    await engine.buzzer.success()
                    await engine.broadcast()
                elif item_id == "herbal_poultice" and "herbal_poultice" in engine.state.player.inventory:
                    engine.state.player.inventory.remove("herbal_poultice")
                    engine.state.player.infection = max(0, engine.state.player.infection - 15)
                    engine.state.log.append("Applied crushed herbal poultice to scratches. Swelling cools down.")
                    engine.state.fx = "heal"
                    await engine.buzzer.success()
                    await engine.broadcast()
                elif item_id == "clean_gauze" and "clean_gauze" in engine.state.player.inventory:
                    engine.state.player.inventory.remove("clean_gauze")
                    engine.state.player.health = min(100, engine.state.player.health + 25)
                    engine.state.log.append("Wrapped clean sterile compression dressing. Bleeding halts.")
                    engine.state.fx = "heal"
                    await engine.buzzer.success()
                    await engine.broadcast()
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
