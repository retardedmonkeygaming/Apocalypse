# APOCALYPSE TERMINAL

Pixel zombie survival for a **Raspberry Pi 4** (arcade buttons, 7-segment, buzzer) with a real-time CRT web UI. Fully playable on a Mac/PC with no hardware.

You survive in a boarded room while **Channel 7** sells Fort Halcyon as hope. People show up. The infection has stages. The door is still yours.

## What the game is

A short survival run built around a hub loop at Home Base: scavenge, craft, fortify, talk, rest. You leave the house for one story beat at a time, come back, and let the day wear on. Day has two beats; night has one, then dawn. There are four buttons, a 7-segment health readout, a buzzer, and a CRT-flavored browser UI that mirrors the hardware exactly.

The campaign has real characters with voices, more than 40 encounters, several explorable locations, a crafting and fortification system, turn-based combat, infection stages with consequences, a humanity score that changes the story and the endings, and a set of endings that reward playstyle rather than a single score. The game is fully playable offline. The Gemini hook is only for a sentence of flavor text on the radio and in the journal.

## Requirements

- Python 3.10+ (3.11 on Raspberry Pi OS Bookworm is fine)
- A browser (Chromium on the Pi, anything current on a laptop)
- Optional: Gemini API key for radio/journal flavor text only
- Optional: GPIO hardware (see pins below)

## Quick start — Mac / PC (no GPIO)

```bash
cd /path/to/Apocalypse
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # USE_HARDWARE=false
python -m backend.app.main
```

Open http://127.0.0.1:8000

**Keys:** `1` red · `2` blue · `3` green · `4` yellow · `Space` confirm (rest / back / medkit)

## Setup — Raspberry Pi 4

```bash
cd ~/Github/Apocalypse             # or wherever you cloned it
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

In `.env`:

```
USE_HARDWARE=true
HOST=0.0.0.0
PORT=8000
```

Run from the **repo root** (saves land in `data/saves/current.json`):

```bash
python -m backend.app.main
```

On the Pi’s browser: `http://127.0.0.1:8000`
On the LAN: `http://<pi-ip>:8000`

If gpiozero cannot claim pins, the game falls back to software mode and prints the error. The WebUI keeps working.

### GPIO map

| Piece | BCM pins |
|---|---|
| Buttons Red/Blue/Green/Yellow/Confirm | 5, 6, 13, 19, 16 (pull-up) |
| 7-segment A–G | 2, 3, 4, 18, 22, 23, 24 |
| Passive buzzer (PWM) | 12 |

### Pi kiosk tip

Keep a Chromium window kiosk’d on the UI if you want the cabinet to match the buttons. `gpiozero` wants the user in the `gpio` group (`sudo usermod -aG gpio $USER` then re-login). Do not enable reload on the Pi (`reload=False` is already set).

## Optional Gemini

The sim is **100% offline** by default. To let Channel 7 improvise a sentence after some dialogues:

```
GEMINI_ENABLED=true
GEMINI_API_KEY=your_key
```

If the call fails or times out, play continues with authored text.

## Controls

| Input | Action |
|---|---|
| Red button / `1` | First choice |
| Blue button / `2` | Second choice |
| Green button / `3` | Third choice |
| Yellow button / `4` | Fourth choice |
| Confirm button / `Space` | Context: REST at hub, BACK in menus, MEDKIT in the field/combat |

The confirm button reads the situation. At the hub it rests. In a menu it backs out. In an event or combat it uses a medkit.

## Layout

```
backend/app/
  main.py                 FastAPI + hardware wiring
  core/config.py          .env settings
  core/state.py           save/load
  game/engine.py          hub, time, effects
  game/events.py          40+ encounters + story beats
  game/combat.py          turn combat
  game/content.py         items, NPCs, recipes, endings
  hardware/               gpiozero with software fallback
  api/                    WebSocket (single source of truth)
  services/gemini.py      optional flavor
  services/save.py        save wrapper
frontend/                 CRT UI, canvas scenes, WebAudio
DESIGN.md                 story + systems
```

## Play notes

1. You start at **Home Base**. Four actions: scavenge, craft, fortify, talk. Confirm **rests**.
2. Scavenging opens four mapped locations (the map grows with the days).
3. Each expedition is one story beat or a fight, then you come home. Day has two beats; night has one.
4. Craft boards, tools, a rain catcher, a garden, an alarm, a med station, a louder radio, a mask, a molotov, a weapon.
5. Take people in. Share food. Or don’t. **Humanity** is a stat the endings can read.
6. Survive toward Halcyon, the docks, the tunnels, a quiet house, a sermon, a broadcast, or something worse.

Saves automatically to `data/saves/current.json`. **New run** from the footer starts clean.

## Smoke test

From the repo root:

```bash
python -m backend.app.main
```

Then:

1. Open the page, wait for `CONNECTED`.
2. Press `1`, pick a location.
3. Come home, press Space to rest.
4. Press `N` or click **NEW RUN** to start over.

If the 7-segment stays dark on the Pi but the screen updates, GPIO failed and the game is running in software mode. That is fine. If the screen never connects, check `HOST`, `PORT`, and whether another service already holds port 8000.

## Troubleshooting

- **Buttons do nothing on Pi:** check pins, pull-ups, and `gpio` group membership. The game will print a hardware fallback message if it cannot claim them.
- **Nothing on port 8000:** another process may be bound there. Change `PORT` in `.env`.
- **Browser connects then freezes:** the WebSocket is the single source of truth. If it drops, the UI reconnects and reloads state on reconnect.
- **Save looks wrong:** deletes in `data/saves/current.json` reset the run. A new run always starts clean.

## Design notes

See `DESIGN.md` for the story direction, systems summary, tone, and the pixel-art approach.
