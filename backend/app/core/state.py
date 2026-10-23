from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SAVE_PATH = ROOT / "data" / "saves" / "current.json"

INV_SLOTS = 8
MAX_LOG = 120


@dataclass
class Player:
    health: int = 100
    infection: int = 0
    morale: int = 70
    humanity: int = 50
    food: int = 5
    water: int = 5
    ammo: int = 6
    scrap: int = 3
    medkits: int = 1
    weapon: str = "fists"
    inventory: List[str] = field(default_factory=list)
    name: str = "Survivor"
    kills: int = 0
    days_survived: int = 0
    meals_shared: int = 0
    craft_count: int = 0


@dataclass
class World:
    day: int = 1
    is_night: bool = False
    actions_left: int = 2
    location: str = "Home Base"
    weather: str = "clear"
    fortification: int = 1
    known_locations: List[str] = field(
        default_factory=lambda: [
            "Home Base",
            "Streets",
            "Abandoned Mall",
            "Hospital",
            "Radio Tower",
        ]
    )
    flags: Dict[str, Any] = field(default_factory=dict)
    npcs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    seen_events: List[str] = field(default_factory=list)
    has_dog: bool = False
    dog_name: str = "Scraps"


@dataclass
class CombatState:
    active: bool = False
    enemy_id: str = ""
    enemy_name: str = ""
    enemy_hp: int = 0
    enemy_max: int = 0
    enemy_intent: str = ""
    log: List[str] = field(default_factory=list)
    defending: bool = False
    round: int = 0


@dataclass
class GameState:
    player: Player = field(default_factory=Player)
    world: World = field(default_factory=World)
    combat: CombatState = field(default_factory=CombatState)
    mode: str = "hub"  # hub, event, combat, menu, ending
    menu: str = ""  # locations, craft, talk, fortify, inventory
    current_event: Optional[Dict[str, Any]] = None
    log: List[str] = field(default_factory=list)
    game_over: bool = False
    victory: bool = False
    ending_id: str = ""
    ending_title: str = ""
    ending_text: str = ""
    waiting_for_choice: bool = False
    last_action: str = ""
    confirm_label: str = "REST"
    fx: str = ""
    scene: str = "base"
    kid_name: str = "Eli"

    def clamp(self):
        p = self.player
        p.health = int(max(0, min(100, p.health)))
        p.infection = int(max(0, min(100, p.infection)))
        p.morale = int(max(0, min(100, p.morale)))
        p.humanity = int(max(0, min(100, p.humanity)))
        p.food = int(max(0, p.food))
        p.water = int(max(0, p.water))
        p.ammo = int(max(0, p.ammo))
        p.scrap = int(max(0, p.scrap))
        p.medkits = int(max(0, p.medkits))
        self.world.fortification = int(max(0, min(10, self.world.fortification)))
        if len(p.inventory) > INV_SLOTS:
            p.inventory = p.inventory[:INV_SLOTS]
        if len(self.log) > MAX_LOG:
            self.log = self.log[-MAX_LOG:]

    def infection_stage(self) -> str:
        i = self.player.infection
        if i <= 0:
            return "clean"
        if i < 25:
            return "scratch"
        if i < 50:
            return "fever"
        if i < 75:
            return "lucid"
        if i < 100:
            return "turning"
        return "turned"

    def party(self) -> List[Dict[str, Any]]:
        out = []
        for npc_id, data in self.world.npcs.items():
            if data.get("alive") and data.get("at_base"):
                out.append({"id": npc_id, **data})
        return out

    def to_dict(self) -> dict:
        from backend.app.game.content import LOCATIONS

        self.clamp()
        map_data = {}
        for name in self.world.known_locations:
            if name in LOCATIONS:
                loc_info = LOCATIONS[name]
                map_data[name] = {
                    "name": name,
                    "x": loc_info.get("map_x", 160),
                    "y": loc_info.get("map_y", 90),
                    "icon": loc_info.get("icon", "📍"),
                    "threat": loc_info.get("threat", "MED"),
                    "risk": loc_info.get("risk", 0.3),
                    "blurb": loc_info.get("blurb", ""),
                    "connections": loc_info.get("connections", []),
                }

        return {
            "player": asdict(self.player),
            "world": asdict(self.world),
            "combat": asdict(self.combat),
            "mode": self.mode,
            "menu": self.menu,
            "current_event": self.current_event,
            "log": self.log[-45:],
            "game_over": self.game_over,
            "victory": self.victory,
            "ending_id": self.ending_id,
            "ending_title": self.ending_title,
            "ending_text": self.ending_text,
            "waiting_for_choice": self.waiting_for_choice,
            "last_action": self.last_action,
            "confirm_label": self.confirm_label,
            "fx": self.fx,
            "scene": self.scene,
            "kid_name": self.kid_name,
            "infection_stage": self.infection_stage(),
            "party": self.party(),
            "inv_slots": INV_SLOTS,
            "map_data": map_data,
        }

    def save(self):
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        blob = self.to_dict()
        blob["log"] = self.log[-MAX_LOG:]
        with open(SAVE_PATH, "w") as f:
            json.dump(blob, f, indent=2)

    @classmethod
    def load(cls) -> "GameState":
        if not SAVE_PATH.exists():
            return cls()
        try:
            with open(SAVE_PATH) as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return cls()

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        state = cls()
        pdata = data.get("player") or {}
        wdata = data.get("world") or {}
        cdata = data.get("combat") or {}
        p_fields = {k: pdata[k] for k in Player.__dataclass_fields__ if k in pdata}
        w_fields = {k: wdata[k] for k in World.__dataclass_fields__ if k in wdata}
        c_fields = {k: cdata[k] for k in CombatState.__dataclass_fields__ if k in cdata}
        state.player = Player(**p_fields)
        state.world = World(**w_fields)
        state.combat = CombatState(**c_fields)
        state.mode = data.get("mode", "hub")
        state.menu = data.get("menu", "")
        state.current_event = data.get("current_event")
        state.log = data.get("log", [])
        state.game_over = data.get("game_over", False)
        state.victory = data.get("victory", False)
        state.ending_id = data.get("ending_id", "")
        state.ending_title = data.get("ending_title", "")
        state.ending_text = data.get("ending_text", "")
        state.waiting_for_choice = data.get("waiting_for_choice", False)
        state.last_action = data.get("last_action", "")
        state.confirm_label = data.get("confirm_label", "REST")
        state.scene = data.get("scene", "base")
        state.kid_name = data.get("kid_name", "Eli")
        return state
