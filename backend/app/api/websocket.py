from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json


class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, data: dict):
        message = json.dumps(data)
        living: List[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_text(message)
                living.append(ws)
            except Exception:
                pass
        self.active = living


manager = ConnectionManager()
