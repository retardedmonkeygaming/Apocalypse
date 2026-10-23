import random
from typing import Any, Dict, List, Tuple
from backend.app.game.content import ENEMIES, WEAPONS


def make_combat(enemy_id: str) -> Dict[str, Any]:
    spec = ENEMIES.get(enemy_id, ENEMIES["shambler"])
    return {
        "active": True,
        "enemy_id": enemy_id,
        "enemy_name": spec["name"],
        "enemy_hp": spec["hp"],
        "enemy_max": spec["hp"],
        "log": [f"{spec['name']} closes in."],
        "defending": False,
        "round": 0,
    }


def _weapon(state) -> Dict[str, Any]:
    return WEAPONS.get(state.player.weapon, WEAPONS["fists"])


def _player_hit_chance(state) -> float:
    acc = 0.78
    if state.infection_stage() in ("lucid", "turning"):
        acc -= 0.12
    if state.player.morale < 30:
        acc -= 0.08
    if state.world.weather == "fog":
        acc -= 0.06
    return max(0.35, acc)


def _incoming(state, spec: Dict[str, Any], defending: bool) -> Tuple[int, bool]:
    if random.random() > spec["acc"]:
        return 0, False
    dmg = spec["dmg"] + random.randint(-2, 2)
    if defending:
        dmg = dmg // 2
    if state.world.location == "Home Base":
        dmg = max(1, dmg - state.world.fortification // 3)
    infect = random.random() < spec.get("infect", 0)
    if "mask" in state.player.inventory:
        infect = infect and random.random() < 0.45
    return max(0, dmg), infect


def resolve_player_action(state, action: str) -> Dict[str, Any]:
    spec = ENEMIES.get(state.combat.enemy_id, ENEMIES["shambler"])
    p = state.player
    wpn = _weapon(state)
    notes: List[str] = []
    fx = "hit"
    defending = False
    enemy_stunned = False

    if action == "attack":
        if random.random() < _player_hit_chance(state):
            dmg = wpn["dmg"] + random.randint(0, 3) - spec.get("armor", 0)
            dmg = max(1, dmg)
            state.combat.enemy_hp -= dmg
            notes.append(f"You land {dmg} with {wpn['name'].lower()}.")
        else:
            notes.append("You swing through damp air.")
            fx = "miss"
    elif action == "defend":
        defending = True
        notes.append("You tuck in. Wood, bone, patience.")
        fx = "defend"
    elif action == "shoot":
        if p.ammo <= 0:
            notes.append("The magazine answers with a click that feels personal.")
            fx = "miss"
        else:
            p.ammo -= 1
            dmg = 14 + random.randint(0, 6) - spec.get("armor", 0) // 2
            dmg = max(2, dmg)
            state.combat.enemy_hp -= dmg
            enemy_stunned = spec["name"] != "Armored Dead" and random.random() < 0.35
            notes.append(f"Muzzle flash. {dmg} through meat.")
            fx = "gun"
    elif action == "molotov":
        if "molotov" not in p.inventory:
            notes.append("Your hands find no bottle.")
            fx = "miss"
        else:
            p.inventory.remove("molotov")
            dmg = 22
            state.combat.enemy_hp -= dmg
            enemy_stunned = True
            notes.append("The night wears a new sun. The thing screams in a human key.")
            fx = "fire"
    elif action == "flee":
        chance = spec.get("flee", 0.5)
        if state.world.weather == "fog":
            chance += 0.1
        if random.random() < chance:
            state.combat.active = False
            notes.append("You leave pieces of your dignity on the floor. You keep the rest.")
            return {"over": True, "fled": True, "notes": notes, "fx": "flee"}
        notes.append("It cuts off the door.")
        fx = "shake"

    # Enemy turn
    if state.combat.enemy_hp > 0 and not enemy_stunned:
        dmg, infect = _incoming(state, spec, defending)
        if dmg <= 0:
            notes.append(f"The {spec['name'].lower()} misses, wetly.")
        else:
            p.health -= dmg
            notes.append(f"{spec['name']} hits for {dmg}.")
            fx = "shake"
            if infect:
                extra = random.randint(4, 12)
                p.infection += extra
                notes.append("The wound is too warm.")
    elif enemy_stunned and state.combat.enemy_hp > 0:
        notes.append("It staggers, cooking in its own noise.")

    state.combat.round += 1
    state.combat.defending = defending
    state.combat.log = (state.combat.log + notes)[-8:]

    if state.combat.enemy_hp <= 0:
        state.combat.active = False
        loot = _loot(spec)
        notes.append(f"The {spec['name'].lower()} goes still.")
        return {"over": True, "won": True, "notes": notes, "fx": "success", "loot": loot}

    if p.health <= 0:
        state.combat.active = False
        return {"over": True, "died": True, "notes": notes, "fx": "danger"}

    return {"over": False, "notes": notes, "fx": fx}


def _loot(spec: Dict[str, Any]) -> Dict[str, int]:
    loot: Dict[str, int] = {}
    if spec.get("human"):
        loot["scrap"] = random.randint(1, 3)
        if random.random() < 0.4:
            loot["ammo"] = random.randint(1, 4)
        return loot
    if random.random() < 0.5:
        loot["scrap"] = 1
    if random.random() < 0.2:
        loot["ammo"] = 1
    return loot
