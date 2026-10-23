# Design notes — Apocalypse Terminal (Channel 7)

## Vision

A short, complete pixel survival game: grim, not hopeless. You are not the chosen one. You are a person in a boarded room with four arcade buttons and a radio that still thinks it is a public service.

The city is unnamed. The promise on the air is **Fort Halcyon** — walls, names taken, bring the living. The question of the run is not “can you min-max loot?” It is **who you are when the door is still yours to open**.

Tone sits between a 90s survival sim and a late-night emergency broadcast: dark humor, hard trades, quiet rooms that refuse to be plot.

## Story direction

**Channel 7** is the spine. Marcus “Radio” Hale used to read weather as comfort. He still has the cadence. He also knows when a government sentence is wearing a costume.

**Dr. Lena Voss** is infected and lucid. The outbreak is a “resilience adjuvant” that never adjourned. She can slow the rot. A true clean draft would cost her the last of herself.

**The Kid** (Eli / Jun / Rae / Nico / Sam) is not a mascot. They ask the questions adults step around. If they live, the endings change register.

**The Butcher** is the human predator who still files paperwork in his head. Useful. Until he is inventory.

**Sister Miriam** treats mercy as a practice, not a mood. **Ghost** does not speak; the tunnels are a country with no census.

You can extract, stay, disappear, become the next butcher, or put a voice on the air that keeps strangers alive one more night.

The campaign is structured around **small, memorable beats** rather than a long linear plot. Every unique story beat can fire once per run. The radio becomes the player’s best way to feel whether the world still has a voice.

## Systems

- **Hub loop** at Home Base: scavenge, craft, fortify, talk, rest. Confirm on the hub is REST (mirrors the arcade confirm button).
- **Expeditions** spend a time-slice. Day has two slices; night has one, then dawn.
- **Inventory** is 8 unique slots (weapons, notes, keys). Bulk food/water/ammo/scrap/kits stay on the HUD.
- **Crafting** is real gear and camp infrastructure (rain catcher, garden, alarm, med station, boosted radio, mask, molotov, weapon).
- **Combat** is turn-based: strike / guard / fire / flee (or molotov). Infection can ride in on a hit.
- **Infection stages**: clean → scratch → fever → lucid rot → turning → turned. Masks and Lena change the slope, not the gravity.
- **Humanity** gates NPC trust and endings. Low humanity makes the gentle people leave and closes off the gentler endings.
- **Weather** (clear, overcast, rain, fog, storm) is not cosmetics: fog hides, storms test the roof, rain fills the catcher.
- **Gemini** is optional flavor on radio/journal/dialogue. The game is fully playable with the key unset.
- **Hardware and Web UI always share one `GameEngine`**. There is no second state. If GPIO is absent, the game runs in software mode and the 7-segment display is mirrored by a CSS 7-segment on screen.

## Endings

Halcyon Gate, Quarantine Flag, Shepherd, The Quiet House, Last Light, Signing Off, Black Water, Under the City, Ash and Amen, The New Butcher, plus the honest failures (cold floor, turned, starved, the door gives).

There is no single “good” ending. Endings reward playstyle, not a score. A quiet run can be a victory. A Halcyon run can be a trap. The game tells you which one you built rather than whether you won.

## Pixel art approach

No sprite sheets are required. The scene canvas renders tile-like cityscapes from a compact palette, one foreground person silhouette per location, weather layers, and a soft infection tint. Atmospheric polish comes from scanlines, a vignette, mild chromatic aberration, screen-shake on violence, and buzzer/beep feedback on the Pi and in the browser. Readability and mood come before animation complexity.

## Hardware map

| Control | Role |
|---|---|
| Red / Blue / Green / Yellow | The four choices on screen |
| Confirm | Context: REST at hub, BACK in menus, MEDKIT in the field/combat |
| 7-segment | Health tens digit; `E` on death; `P` on a “made it” ending |
| Buzzer | Success / danger / night / infection — mirrored by browser beeps |

## QA

Run `python -m backend.app.main` from the repo root. On a normal machine with `.env` set to `USE_HARDWARE=false`, the game still boots, saves to `data/saves/current.json`, and the WebUI stays the source of truth. On the Pi, set `USE_HARDWARE=true` and wire the pins in `.env.example`.

A round-trip smoke test is: open `/`, wait for CONNECTED, press 1 to open locations, pick a location, come home, confirm to rest, repeat once, then press New Run.
