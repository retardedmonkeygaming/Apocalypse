import pytest
from fastapi.testclient import TestClient
from backend.app.main import app, engine


def test_http_routes():
    with TestClient(app) as client:
        # Ping
        r = client.get("/ping")
        assert r.status_code == 200
        assert r.json() == {"ok": True}

        # Health
        r = client.get("/health")
        assert r.status_code == 200
        assert "ok" in r.json()
        assert "hardware" in r.json()

        # Index template
        r = client.get("/")
        assert r.status_code == 200
        assert "APOCALYPSE TERMINAL" in r.text


def test_websocket_actions():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            init_state = ws.receive_json()
            assert "player" in init_state
            assert "world" in init_state

            # Start fresh run
            ws.send_json({"action": "new_game"})
            fresh_state = ws.receive_json()
            assert fresh_state["mode"] == "hub"
            assert fresh_state["world"]["day"] == 1

            # Choice action: pick first choice (Scavenge)
            ws.send_json({"action": "choice", "key": "red"})
            updated = ws.receive_json()
            assert updated["menu"] == "locations" or updated["mode"] == "event"

            # Confirm (BACK to Hub)
            ws.send_json({"action": "confirm"})
            hub = ws.receive_json()
            assert hub["mode"] == "hub"
