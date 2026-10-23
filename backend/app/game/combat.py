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
        "enemy_intent": spec.get("intent", "Closing the distance."),
        "log": [f"{spec['name']} emerges! {spec.get('intent', '')}"],
        "defending": False,
        "round": 1,
    }


def _weapon(state) -> Dict[str, Any]:
    return WEAPONS.get(state.player.weapon, WEAPONS["fists"])


def _player_hit_chance(state) -> float:
    acc = 0.82
    if state.infection_stage() in ("fever",):
        acc -= 0.10
    elif state.infection_stage() in ("lucid", "turning"):
        acc -= 0.20
    if state.player.morale < 30:
        acc -= 0.10
    if state.world.weather == "fog":
        acc -= 0.15
    return max(0.30, acc)


def _enemy_retaliation(state, spec: Dict[str, Any], defending: bool) -> Tuple[int, bool, str]:
    """Calculates enemy damage, infection roll, and descriptive narrative."""
    enemy_name = spec["name"]
    # Check hit
    acc = spec["acc"]
    if state.world.weather == "fog":
        acc -= 0.12
    if random.random() > acc:
        return 0, False, f"{enemy_name} swipes wide through the air."

    dmg = spec["dmg"] + random.randint(-2, 3)
    if defending:
        dmg = max(1, int(dmg * 0.35))  # Defend cuts 65% of damage
    if state.world.location == "Home Base":
        dmg = max(1, dmg - state.world.fortification // 3)

    # Infection roll: NEVER infects if player actively defended
    infect = False
    if not defending and not spec.get("human"):
        base_inf = spec.get("infect", 0.0)
        if random.random() < base_inf:
            # Mask protection
            if "gas_mask" in state.player.inventory:
                infect = random.random() < 0.20
            elif "mask" in state.player.inventory:
                infect = random.random() < 0.50
            else:
                infect = True

    if defending:
        note = f"You brace tight. {enemy_name} thuds against your guard for {dmg} damage."
    else:
        note = f"{enemy_name} strikes hard, dealing {dmg} damage!"
        if infect:
            note += " Sharp teeth graze skin — infection enters!"

    return max(1, dmg), infect, note


def resolve_player_action(state, action: str) -> Dict[str, Any]:
    spec = ENEMIES.get(state.combat.enemy_id, ENEMIES["shambler"])
    p = state.player
    wpn = _weapon(state)
    notes: List[str] = []
    fx = "hit"
    defending = False
    enemy_stunned = False

    # 1. Resolve player action
    if action == "attack":
        if random.random() < _player_hit_chance(state):
            base = wpn["dmg"] + random.randint(0, 4)
            armor = max(0, spec.get("armor", 0) - wpn.get("armor_pen", 0))
            dmg = max(2, base - armor)
            is_crit = random.random() < 0.15
            if is_crit:
                dmg = int(dmg * 1.5)
                notes.append(f"CRITICAL HIT! You smash through with {wpn['name']} for {dmg} damage!")
            else:
                notes.append(f"You swing your {wpn['name'].lower()}, dealing {dmg} damage.")
            state.combat.enemy_hp -= dmg
        else:
            notes.append(f"You lunge with your {wpn['name'].lower()}, but miss in the shadows!")
            fx = "miss"

    elif action == "defend":
        defending = True
        notes.append("You tuck behind cover, bracing against incoming violence.")
        fx = "defend"

    elif action == "shoot":
        if p.ammo <= 0:
            notes.append("Your trigger clicks dry against an empty chamber!")
            fx = "miss"
        else:
            p.ammo -= 1
            base = wpn["dmg"] if wpn.get("ranged") else 24
            armor_pen = wpn.get("armor_pen", 2)
            dmg = max(6, base + random.randint(2, 8) - max(0, spec.get("armor", 0) - armor_pen))
            state.combat.enemy_hp -= dmg
            # Chance to stun enemy
            enemy_stunned = random.random() < 0.40
            notes.append(f"Muzzle flash tears through the gloom! {dmg} damage.")
            if enemy_stunned:
                notes.append(f"The kinetic impact knocks {spec['name']} off-balance!")
            fx = "gun"

    elif action == "molotov":
        if "molotov" not in p.inventory:
            notes.append("You reach into your pack, but find no bottle!")
            fx = "miss"
        else:
            p.inventory.remove("molotov")
            dmg = 26 + random.randint(2, 8)
            state.combat.enemy_hp -= dmg
            enemy_stunned = True
            notes.append(f"Glass shatters in a bloom of orange fire! {dmg} fire damage. {spec['name']} is engulfed!")
            fx = "fire"

    elif action == "flee":
        flee_chance = spec.get("flee", 0.5)
        if state.world.weather == "fog":
            flee_chance += 0.20
        if state.world.npcs.get("ghost", {}).get("at_base"):
            flee_chance += 0.15
        if random.random() < flee_chance:
            state.combat.active = False
            notes.append("You scramble through broken drywall and lose your pursuer in the wreckage.")
            return {"notes": notes, "fx": "flee", "over": True, "fled": True}
        else:
            notes.append("You scramble to retreat, but rubble blocks your exit!")
            fx = "miss"

    # 2. Check if enemy died
    if state.combat.enemy_hp <= 0:
        state.combat.active = False
        p.kills += 1
        loot = dict(spec.get("loot", {}))
        notes.append(f"── {spec['name']} collapses into motionless silence! ──")
        return {"notes": notes, "fx": "success", "over": True, "loot": loot}

    # 3. Enemy retaliation turn (if alive and not stunned)
    if enemy_stunned:
        notes.append(f"{spec['name']} staggers helplessly, unable to retaliate this turn.")
    else:
        edmg, infect, note = _enemy_retaliation(state, spec, defending)
        p.health -= edmg
        if infect:
            p.infection = min(100, p.infection + random.randint(6, 14))
        notes.append(note)

    # 4. Check if player died
    if p.health <= 0:
        return {"notes": notes, "fx": "danger", "over": True, "died": True}

    # 5. Telegraphed intent for next round
    intents = [
        f"{spec['name']} bares rotting teeth and prepares to strike.",
        f"{spec['name']} circles around your flank, seeking an opening.",
        f"{spec['name']} lets out a guttural hiss and gathers its weight.",
    ]
    if spec["name"] == "Toxic Bloater":
        intents.append("Bile bubbles violently beneath the Bloater's translucent skin!")
    elif spec["name"] == "Frenzied Runner":
        intents.append("The Runner twitches erratically, coiled to leap!")
    elif spec["name"] == "The Butcher":
        intents.append("The Butcher wipes red steel on his apron, laughing softly.")

    state.combat.enemy_intent = random.choice(intents)
    state.combat.round += 1
    state.combat.log.extend(notes)
    if len(state.combat.log) > 10:
        state.combat.log = state.combat.log[-10:]

    return {"notes": notes, "fx": fx, "over": False}
