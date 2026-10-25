# APOCALYPSE TERMINAL (Channel 7)

A complete, polished retro-pixel zombie survival game designed for a **Raspberry Pi 4** physical arcade cabinet (arcade buttons, 7-segment display, buzzer) and a real-time **Web UI** with CRT aesthetics.

Fully playable **100% offline** on any Mac, PC, or Linux laptop without physical hardware.

---

## Game Overview

You wake in a boarded apartment room in a fallen city. Channel 7 emergency radio crackles through the dust: **Marcus "Radio" Hale** promises safety at **Fort Halcyon Mile 18**. But the city between your deadbolt and the military gates is a labyrinth of shambling dead, toxic bloaters, desperate raiders, and hard choices.

- **Hub Loop**: Scavenge, craft, fortify, converse with companions, and rest.
- **Clock & Expeditions**: Daytime provides 2 action slices; Night provides 1 action slice, followed by Dawn upkeep.
- **Real Combat**: Strike, Guard (blocks bites), Fire firearms, throw Molotovs, or Flee through the fog.
- **Infection with Consequences**: Clean, Scratch, Fever, Lucid Rot, Turning, and Turned.
- **Morality & Humanity**: Affects companion trust, departures, and unlocks 15 unique narrative endings.
- **100% Offline**: Optional Gemini API hook is used strictly for atmospheric flavor text when enabled.

---

## File Structure

```
Apocalypse/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application, lifespan, button dispatch
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings (.env, pin assignments)
│   │   │   └── state.py            # Dataclasses, GameState, save/load system
│   │   ├── game/
│   │   │   ├── content.py          # Weapons, items, recipes, enemies, locations, NPCs, endings
│   │   │   ├── events.py           # 40+ branching story beats & location encounters
│   │   │   ├── combat.py           # Tactical turn-based combat engine
│   │   │   └── engine.py           # Master GameEngine (time, dawn, infection, effects)
│   │   ├── hardware/
│   │   │   ├── buttons.py          # gpiozero 5 arcade buttons with software fallback
│   │   │   ├── display.py          # 7-Segment single-digit LED controller
│   │   │   └── buzzer.py           # Passive PWM buzzer melodic sound generator
│   │   ├── api/
│   │   │   ├── routes.py           # HTTP endpoints & WebSocket action handler
│   │   │   └── websocket.py        # Real-time WebSocket connection manager
│   │   └── services/
│   │       ├── gemini.py           # Optional async Gemini flavor text generator
│   │       └── save.py             # Save state helper service
│   └── tests/
│       ├── test_engine.py          # Unit tests for core engine, combat, infection & time
│       └── test_api.py             # Integration tests for HTTP & WebSocket
├── frontend/
│   ├── templates/
│   │   └── index.html              # CRT cabinet layout, HUD, 7-seg mirror, arcade buttons
│   └── static/
│       ├── css/
│       │   └── style.css           # CRT monitor bezel, phosphor scanlines, 3D buttons
│       └── js/
│           ├── pixel.js            # 320x180 procedural pixel engine (skies, weather, entities)
│           ├── audio.js            # Web Audio API 8-bit synthesizer & chiptunes
│           ├── ui.js               # HUD meters, inventory grid, survivor log, 7-seg LED
│           ├── websocket.js        # Auto-reconnecting WebSocket client
│           └── game.js             # Input dispatcher, keyboard bindings, animation ticker
├── data/
│   └── saves/                      # Automatic persistent JSON run save
├── .env.example                    # Sample configuration with GPIO pin definitions
├── requirements.txt                # Lightweight Python dependencies
├── DESIGN.md                       # Comprehensive narrative & systems design document
└── README.md                       # Setup and operational instructions
```

---

## Controls

The hardware arcade cabinet and browser Web UI stay in perfect real-time synchronization:

| Arcade Button | Keyboard Key | In-Game Action |
|---|---|---|
| **Red Button** | `1` | First choice / Melee Strike |
| **Blue Button** | `2` | Second choice / Guard (Block Bite) |
| **Green Button** | `3` | Third choice / Fire Gun |
| **Yellow Button** | `4` | Fourth choice / Flee / Molotov |
| **Confirm Button** | `Space` / `Enter` | Contextual: **REST** at hub, **BACK** in menus, **MEDKIT** in combat/field |
| — | `N` | Start a New Run (resets state) |
| — | `M` | Toggle Audio Synthesizer (Mute / Unmute) |
| — | Mouse Click / Touch | Click on any arcade button or consumable pack item |

---

## Quick Start — Development on Mac / PC (No Hardware)

The game includes graceful hardware fallbacks. If GPIO hardware is absent, it runs in software mode, mirroring the 7-segment display and buzzer on screen and through Web Audio.

1. **Clone and enter repository**:
   ```bash
   cd /path/to/Apocalypse
   ```

2. **Create and activate Python virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate       # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   Ensure `.env` contains:
   ```env
   USE_HARDWARE=false
   HOST=127.0.0.1
   PORT=8000
   ```

5. **Run the game server**:
   ```bash
   python -m backend.app.main
   ```

6. Open your browser at: **`http://127.0.0.1:8000`**

---

## Setup — Raspberry Pi 4 Physical Cabinet

### 1. Wiring the Hardware (BCM Pinout)

Connect your components to the Raspberry Pi GPIO header using the BCM numbering:

#### 5 Arcade Pushbuttons (Active Low with Internal Pull-Ups)
- Connect one terminal of each arcade switch to the specified GPIO pin; connect the other terminal to any **GND** pin:
  - **Red Button**: GPIO `5`
  - **Blue Button**: GPIO `6`
  - **Green Button**: GPIO `13`
  - **Yellow Button**: GPIO `19`
  - **Confirm Button**: GPIO `16`

#### Single-Digit 7-Segment LED Display (Cathode or Anode with matching resistors)
- Connect segments A through G via 220Ω–330Ω current-limiting resistors:
  - **Segment A**: GPIO `2`
  - **Segment B**: GPIO `3`
  - **Segment C**: GPIO `4`
  - **Segment D**: GPIO `18`
  - **Segment E**: GPIO `22`
  - **Segment F**: GPIO `23`
  - **Segment G**: GPIO `24`

#### Passive Buzzer (PWM)
- Connect the signal (+) pin to GPIO `12` (Hardware PWM) and the ground (-) pin to **GND**.

### 2. Pi Software Configuration

```bash
cd ~/Apocalypse
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
```env
USE_HARDWARE=true
HOST=0.0.0.0
PORT=8000
```

Add your user to the GPIO group (if needed on Raspberry Pi OS Bookworm):
```bash
sudo usermod -aG gpio $USER
```

Run the server:
```bash
python -m backend.app.main
```

### 3. Kiosk Mode on Chromium (Optional Kiosk Cabinet)
To launch the CRT Web UI automatically on boot in full-screen kiosk mode on the Pi:
```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://127.0.0.1:8000
```

---

## 3D MODE — Realistic WebGL Lookout Tower

The central viewport can render a **realistic 3D scene** (Three.js, fully vendored
offline at `frontend/static/vendor/three.min.js`) instead of the 2D pixel canvas.
Both engines are driven by the **exact same game state** — companions, Sanity,
Awareness, weather, day/night, story scenes and travel locations — so nothing in
the game changes except how the world is drawn.

### What the 3D view shows

- **Tower interior** — wet-wood walls, desk, radio, candle/amber lamp, window
  frames; Mark/Chloe/Sam physically stand in the room (whoever is alive at base).
- **Through the glass** — the pine ridge, Fire-Tower 1 and the distant Tower 3
  (whose green `H·E·L·P` morse blinks at night), fog sheets, wind sway.
- **Travel = new set.** Pick a location on the map and the viewport becomes that
  place: Copperhead Bridge, Northern Ravine (gorge with drifting fog), Ranger
  Station Ruins, Overturned Railcar, Limestone Sinkhole, Compass Cabins,
  Mining Shaft, the Impossible Clearing, plus an exterior establishing shot.
- **Day/night & weather** — sky, sun/hemisphere light, fog density and rain
  particles all follow `world.is_night` and `world.weather` (high tier only for rain).
- **The window lies at low Sanity** — false silhouettes outside, a companion
  standing in the treeline who is inside, tall figures at high Awareness at night.
- **Classic (non-Ridge) runs** render a dark ruined-city vista.

### Controls

- **`3D: AUTO` button** (top-right of the viewport) cycles:
  `AUTO → HIGH → LOW → OFF → AUTO`.
- **OFF** restores the original 2D pixel canvas exactly (also stored in
  `localStorage.apoc3d`, so your choice survives reloads).
- All gameplay, keyboard and arcade-button controls are unchanged.

### Quality tiers

| Tier | What it does |
|---|---|
| **HIGH** | 170-trees forest, antialiasing, pixelRatio ≤ 1.5, rain particles (900 pts), extra fog sprites, full lights |
| **LOW** | ~50–70 trees, pixelRatio 1, no particles, cheaper lights — intended for Raspberry Pi 4 |
| **AUTO** | Picks HIGH on desktops (≥5 cores, DPR < 2.5), LOW on weak/mobile GPUs |
| **OFF** | 2D canvas only — zero GPU cost |

### How to run

Nothing new to install — start the server as usual and the 3D view is on by
default (auto-detected):

```bash
python -m backend.app.main       # or: uvicorn backend.app.main:app --port 8000
# open http://127.0.0.1:8000  → click “3D: AUTO” to cycle tiers
```

If WebGL is unavailable the engine disables itself silently and the 2D canvas
keeps working. Files: `frontend/static/js/scene3d.js` (engine),
`frontend/static/vendor/three.min.js` (r149 UMD build, offline).

### Honest Raspberry Pi 4 performance notes

- Tested headlessly on SwiftShader (software GL) at ~**23 FPS** in LOW tier —
  a Pi 4's VideoCore VI hardware GL is faster than SwiftShader, so **LOW should
  hold 30–60 fps** at the viewport's ~800×320 CSS size.
- **HIGH is not recommended on the Pi**: antialiasing + 170 trees + rain points
  will likely drop below 25 fps under Kiosk Chromium. AUTO resolves to LOW on
  the Pi (4 cores → LOW).
- The 3D loop still runs when the tab is hidden only at full RAF speed; if you
  run 24/7, select **OFF** to save power and GPU heat in the cabinet.
- WebGL must be enabled in kiosk Chromium (`--enable-gpu` / default on Pi OS;
  avoid `--disable-gpu`).
- Everything is procedural (canvas textures, primitive geometry) — no network,
  no asset downloads, offline-first as required.

---

## Running Automated Tests

To run the complete unit and API test suite:

```bash
PYTHONPATH=. .venv/bin/pytest backend/tests/
```

All 9 test suites verify:
- Engine boot and state transitions
- All 6 infection stages and penalties
- Tactical turn combat (Strike, Guard, Shoot, Molotov, Flee)
- Day/Night/Dawn time-spend loops and starvation
- Crafting and base upgrades
- 15 narrative endings evaluation
- FastAPI HTTP routes and live WebSocket communication

---

## Optional Gemini Flavor Text

The game is **100% playable offline** without any API keys. If you want Channel 7 and survivor journals to generate atmospheric dynamic radio broadcasts:

In `.env`:
```env
GEMINI_ENABLED=true
GEMINI_API_KEY=your_google_ai_key_here
GEMINI_MODEL=gemini-1.5-flash
```

Calls are completely asynchronous and timed out at 4 seconds. If network drops or the key is absent, the game seamlessly falls back to authored prose without pause.

---

## License

MIT License. Designed with care for retro-hardware survivalists and indie game enthusiasts.
