from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import json
from pathlib import Path

SAVE_PATH = Path("data/saves/current.json")

@dataclass
class Player:
    health: int = 100
    infection: int = 0
    morale: int = 70
    food: int = 5
    water: int = 5
    ammo: int = 10
    scrap: int = 0
    medkits: int = 1

@dataclass
class World:
    day: int = 1
    is_night: bool = False
    location: str = "Home Base"
    locations: List[str] = field(default_factory=lambda: [
        "Home Base", "Streets", "Abandoned Mall", "Hospital", "Radio Tower", "Warehouse"
    ])

@dataclass
class GameState:
    player: Player = field(default_factory=Player)
    world: World = field(default_factory=World)
    current_event: Optional[Dict[str, Any]] = None
    log: List[str] = field(default_factory=list)
    game_over: bool = False
    victory: bool = False
    waiting_for_choice: bool = False
    last_action: str = ""

    def to_dict(self) -> dict:
        return {
            "player": asdict(self.player),
            "world": asdict(self.world),
            "current_event": self.current_event,
            "log": self.log[-30:],          # keep last 30 lines
            "game_over": self.game_over,
            "victory": self.victory,
            "waiting_for_choice": self.waiting_for_choice,
            "last_action": self.last_action,
        }

    def save(self):
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SAVE_PATH, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls) -> "GameState":
        if SAVE_PATH.exists():
            with open(SAVE_PATH) as f:
                data = json.load(f)
            state = cls()
            state.player = Player(**data["player"])
            state.world = World(**data["world"])
            state.current_event = data.get("current_event")
            state.log = data.get("log", [])
            state.game_over = data.get("game_over", False)
            state.victory = data.get("victory", False)
            return state
        return cls()