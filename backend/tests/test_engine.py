import asyncio
import pytest
from backend.app.core.state import GameState, Player, World, CombatState
from backend.app.game.engine import GameEngine
from backend.app.game.combat import make_combat, resolve_player_action
from backend.app.game.events import select_event
from backend.app.game.content import RECIPES, WEAPONS, ending_for, apply_ending


def make_engine():
    eng = GameEngine()
    eng.state = GameState()
    eng.state.player = Player()
    eng.state.world = World()
    eng.state.combat = CombatState()
    return eng


def test_engine_initialization():
    engine = make_engine()
    asyncio.run(engine.start_new_game())
    assert engine.state.world.day == 1
    assert engine.state.player.health == 100
    assert engine.state.player.infection == 0
    assert engine.state.mode == "hub"
    assert engine.state.confirm_label == "REST"
    assert len(engine.state.current_event["choices"]) == 4


def test_infection_stages():
    engine = make_engine()
    p = engine.state.player
    p.infection = 0
    assert engine.state.infection_stage() == "clean"

    p.infection = 15
    assert engine.state.infection_stage() == "scratch"

    p.infection = 35
    assert engine.state.infection_stage() == "fever"

    p.infection = 60
    assert engine.state.infection_stage() == "lucid"

    p.infection = 85
    assert engine.state.infection_stage() == "turning"

    p.infection = 100
    assert engine.state.infection_stage() == "turned"


def test_combat_resolution():
    engine = make_engine()
    engine._begin_combat("shambler")
    assert engine.state.combat.active is True
    assert engine.state.combat.enemy_name == "Rotting Shambler"
    assert engine.state.mode == "combat"

    # Defending
    res = resolve_player_action(engine.state, "defend")
    assert "You brace tight" in " ".join(res["notes"]) or "You tuck behind cover" in " ".join(res["notes"])

    # Melee attack
    res = resolve_player_action(engine.state, "attack")
    assert len(res["notes"]) > 0

    # Gun attack
    engine.state.player.ammo = 5
    res = resolve_player_action(engine.state, "shoot")
    assert engine.state.player.ammo == 4

    # Molotov
    engine.state.player.inventory.append("molotov")
    res = resolve_player_action(engine.state, "molotov")
    assert "molotov" not in engine.state.player.inventory


def test_crafting_and_fortification():
    engine = make_engine()
    asyncio.run(engine.start_new_game())
    engine.state.player.scrap = 5

    # Craft barricade
    asyncio.run(engine._craft("barricade"))
    assert engine.state.world.fortification == 2
    assert engine.state.player.scrap == 3

    # Craft pipe club
    asyncio.run(engine._craft("pipe"))
    assert "pipe" in engine.state.player.inventory
    assert engine.state.player.weapon == "pipe"
    assert engine.state.player.scrap == 1


def test_day_night_and_dawn_cycle():
    engine = make_engine()
    asyncio.run(engine.start_new_game())
    assert engine.state.world.is_night is False
    assert engine.state.world.actions_left == 2

    # Spend 1st action
    asyncio.run(engine._spend_action())
    assert engine.state.world.actions_left == 1
    assert engine.state.world.is_night is False

    # Spend 2nd action -> Nightfall
    asyncio.run(engine._spend_action())
    assert engine.state.world.is_night is True
    assert engine.state.world.actions_left == 1

    # Night action -> Dawn of Day 2
    asyncio.run(engine._spend_action())
    assert engine.state.world.is_night is False
    assert engine.state.world.day == 2
    assert engine.state.world.actions_left == 2


def test_medical_and_medkits():
    engine = make_engine()
    asyncio.run(engine.start_new_game())
    engine.state.player.health = 50
    engine.state.player.infection = 20
    engine.state.player.medkits = 1

    asyncio.run(engine.use_medkit())
    assert engine.state.player.health > 50
    assert engine.state.player.infection < 20
    assert engine.state.player.medkits == 0


def test_endings_evaluation():
    engine = make_engine()
    s = engine.state
    # Starvation ending
    s.world.flags["death_cause"] = "starved"
    assert ending_for(s) == "starved"

    # Turned ending
    s.world.flags = {}
    s.player.infection = 100
    assert ending_for(s) == "turned"

    # Halcyon shepherd ending
    s.player.infection = 0
    s.player.health = 80
    s.world.flags = {"extract_halcyon": True}
    s.player.humanity = 80
    s.world.npcs = {
        "kid": {"alive": True, "at_base": True},
        "marcus": {"alive": True, "at_base": True},
    }
    assert ending_for(s) == "shepherd"

    # Quiet house ending
    s.world.flags = {"garden": True, "rain_catcher": True}
    s.world.day = 20
    s.world.fortification = 8
    assert ending_for(s) == "quiet_house"
