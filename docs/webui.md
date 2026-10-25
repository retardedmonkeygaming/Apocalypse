# Apocalypse Terminal — WebUI Reference

Everything on the screen, what it means, and every way to press it.
The browser UI and the physical cabinet are the same machine: every pixel here
has a button on the arcade panel, and every button has a key on the keyboard.

---

## 1. Screen layout

```
┌──────────────────────────────────────────────────────────┐
│  CRT BEZEL                                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ HUD STRIP   DAY 12 │ NIGHT │ FOG │ FIRE-TOWER 2   │  │
│  ├────────────────────────────────────────────────────┤  │
│  │                                                    │  │
│  │   CENTRE VIEWPORT  (320×180 pixel canvas,          │  │
│  │   or the WebGL scene when 3D is on)                │  │
│  │                                                    │  │
│  ├──────────────────┬─────────────────────────────────┤  │
│  │ METERS           │  EVENT TERMINAL                 │  │
│  │ VITALITY  ▓▓▓░   │  TITLE                          │  │
│  │ NOISE SIG ▓░░░   │  typed narrative text …         │  │
│  │ SANITY    ▓▓░░   │                                 │  │
│  │ AWARENESS ▓▓▓░   │  [1] …   [2] …   [3] …   [4] … │  │
│  │ TOWER SEAL ▓▓▓   │              [ CONFIRM ]        │  │
│  ├──────────────────┴─────────────────────────────────┤  │
│  │ 7-SEG MIRROR · RESOURCES · PACK · ROSTER · LOG     │  │
│  └────────────────────────────────────────────────────┘  │
│   [NEW RUN] [SOUND] [CRT] [3D] [MAP] [GUIDE]            │
│   (● RED) (● BLUE) (● GREEN) (● YELLOW)      (● OK)     │
└──────────────────────────────────────────────────────────┘
```

Overlays (they slide over the CRT, they never move the layout):

| Overlay | Open with | Close with |
|---|---|---|
| Tactical map | `Tab`, combo `1+2`, **MAP** button, or the in-game *Open Tactical Map* choice | `Tab`, ✕ CLOSE MAP |
| Field manual / guide | `G`, `Esc`, combo `3+4`, **GUIDE** button | `G`, `Esc`, ✕ |
| Weather station | `W` (Dead Ridge only), combo `2+4` | `W`, `2+4` |
| ForestOS laptop | in-game choice **ForestOS Laptop** | CONFIRM (**CLOSE LID**) |

---

## 2. HUD strip (top)

| Field | Meaning |
|---|---|
| `DAY n` | Current day of the run (Dead Ridge runs are 30 days) |
| `DAY` / `NIGHT` | Clock phase. Night costs action slices and raises risk |
| Weather | `CLEAR · OVERCAST · FOG · STORM` — drives fog density, audio and map status |
| Location | Where the centre viewport is currently looking |

## 3. Meters

Classic runs: **HEALTH · INFECTION · MORALE · HUMANITY · FORTIFICATION**.
Dead Ridge relabels the same five channels — nothing else in the game changes:

| Dead Ridge label | Backed by | Drives |
|---|---|---|
| **VITALITY** | health | Whether you survive hits and exposure |
| **NOISE SIG** | infection | How loudly the ridge hears you; spikes on radio/calls |
| **SANITY** | morale | What the window, radio and crew are allowed to show you |
| **AWARENESS** | humanity | How much the thing on the ridge has noticed you |
| **TOWER SEAL** | fortification | Structural integrity of Tower 2 (sieges, vents, gusts) |

The status chip next to the meters reads `HOLDING` or `⚠ BREAKING` in Ridge runs.

**Sanity is a perception filter.** Above ~50 the window and radio report the truth.
Below ~50 they start editing. Below 30 the 7-segment display itself glitches.

## 4. Event terminal

- **Title** — the current prompt.
- **Text** — revealed with a typewriter effect capped at ~1.5 s (it never gates input).
- **Four option buttons** — labelled by the current event; a key with no option shows `—`.
- **CONFIRM** — the label *is* the action: `REST`, `BACK`, `CLOSE LID`, `LOCK SYNC`, `MEDKIT`, `CLASSIC`, `—`.

### Input guarantee

Options are recomputed on every state push. A button showing a real label is
always clickable: input is bound by document-level delegation (so a re-rendered
button keeps its handler), a watchdog clears stuck FX classes every 1.5 s, and
the server ignores a press only when the *same prompt+key* already resolved —
so a double-press can't double-fire, but a fresh prompt can never be ignored.

## 5. 7-segment mirror

| Char | Meaning |
|---|---|
| `0`–`9` | Health digit (classic) |
| `H` / `n` | Hub · day / night |
| `C` | Combat |
| `R` | Shortwave radio |
| `F` | ForestOS |
| `b` | Calibrating |
| `M` | Overworld / map |
| `U` | Binoculars focus |
| `L` | Log engine |
| `!` | Alert |
| `S` | Sanity critical |
| `d` | Danger / siege |
| `P` / `E` | Shift passed / failed |
| `8 _ -` | Glitch chars at low sanity — the display is lying too |

The physical digit and this mirror are driven by one source of truth
(`GameEngine._sync_seg`), so they can never disagree.

## 6. Resources, pack and roster

- **FOOD · WATER · AMMO · SCRAP · MEDKITS · WEAPON** — current stock.
- **PACK (8 slots)** — click a consumable (bandage, poultice, antibiotics) to use it.
- **ROSTER** — every companion alive at your location, colour-coded by their own colour; 🐕 Scraps appears when the dog is with you.
- **Upgrade badges** — rain catcher, garden, alarm, med bay, radio (green = built).

## 7. Survivor log

The running transcript. Lines starting with `>` are your own choices; lines
starting with `──` are system headers in amber. It auto-scrolls.

## 8. Keyboard map

| Key | Action |
|---|---|
| `1` `2` `3` `4` | The four arcade buttons |
| `Space` / `Enter` | CONFIRM |
| `5` | Next page of stories |
| `Tab` | Tactical map |
| `G` / `Esc` | Beginner's guide |
| `W` | Weather station (Dead Ridge) |
| `M` | Mute |
| `N` | New run (asks for confirmation) |
| `1+2` | Combo: map |
| `3+4` | Combo: field manual |
| `1+4` | Combo: more stories |
| `2+3` | Combo: audio toggle |
| `2+4` | Combo: weather station |

Combos fire when two of `1/2/3/4` are held together; a chord is consumed as a
combo and never leaks a stray option press.

## 9. Footer buttons

| Button | Does |
|---|---|
| **NEW RUN** | Abandons the run (confirmation dialog) |
| **SOUND: ON/OFF** | Mutes the synthesiser |
| **CRT: VINTAGE/MODERN** | Toggles the phosphor scanline overlay |
| **3D: AUTO** | Cycles `AUTO → HIGH → LOW → OFF` (OFF restores the 2D pixel canvas exactly) |
| **MAP** | Tactical map |
| **GUIDE** | Field manual |

## 10. The tactical map

- **Click a node** to travel there directly — the centre viewport becomes that location before any dialogue appears.
- **Node colours**: amber = you are here · green = open · red halo = danger · grey ✕ = locked · dark red ✕ = blocked.
- **`!`** marks a node with a story beat waiting.
- **Hover** a node for its live status line: risk %, and *why* it is locked (no trail yet, storm, no daylight, your own nerves).
- Availability is recomputed on **every** state push from day, weather, night, sanity, awareness, daylight budget and where you have already been.
- Locked/blocked nodes are refused server-side too — the map is a view, not the rule.
- On classic runs the map is intel only: it tells you which zone to pick from **SCAVENGE**.
