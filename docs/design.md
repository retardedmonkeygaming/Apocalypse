# Aesthetic & Design — Apocalypse Terminal

How the thing looks, sounds, and lies to you. This is the rulebook the code is
written against; if a new screen or effect disagrees with this document, the
document wins.

---

## 1. Palette

Everything derives from eight tokens in `style.css :root`.

| Token | Hex | Role |
|---|---|---|
| `--bg-dark` | `#070908` | Cabinet void |
| `--bg-panel` | `#0d1210` | Panel faces |
| `--bg-card` | `#131a16` | Raised cards / meter beds |
| `--border-dim` | `#1e2b22` | Resting edges |
| `--border-bright` | `#395240` | Lit edges |
| `--amber` | `#ffb830` | **Dead Ridge / ForestOS phosphor** — the story's home colour |
| `--phosphor-green` | `#52ff83` | Classic terminal text, healthy meters |
| `--blood-red` | `#ff334b` | Danger, alarms, red arcade cap |
| `--text-primary` | `#d4ebd8` | Body copy |
| `--text-muted` | `#728c78` | Secondary copy |

Arcade caps: red `#ff334b` · blue `#298dff` · green `#1fd655` · yellow
`#ffb830` · confirm `#ffffff`.

**Map palette** (`citymap.js STY/C`): base `#0a0c0f`, grid `#12181e`, roads
`#1e2830` → `#2e4050` when both ends are known, open `#1e3a28/#3a7058`, danger
`#3a1a18/#e04a3a`, locked `#141a22/#2a3240`, blocked `#2a1216/#7a2a2a`, you
`#e58e3c/#ff6628`.

Rules:

- **Colour is information, never decoration.** Amber = the ridge's own system.
  Green = safe or healthy. Red = something is wrong *now*. Grey = unknown.
- Low sanity may tint the world `rgba(150,10,30,…)` — never saturate past 0.16;
  the red must read as blood in the periphery, not as a filter.
- Eclipse state adds `rgba(20,8,40,0.20)` violet-black over everything.

---

## 2. CRT rules

1. The game renders at **320×180** and is upscaled with
   `image-rendering: pixelated` — no smoothing, ever.
2. Scanlines are a 1-in-3 overlay at `rgba(0,0,0,0.3)`, toggleable to MODERN
   (`CRT` footer button) for accessibility and sunlight kiosks.
3. The bezel never moves. **Overlays slide over the CRT; nothing reflows.**
   The map, guide, laptop and weather station are absolutely positioned inside
   `#crt-screen`.
4. Screen-level FX are classes on `#crt-screen`, never inline styles:
   `shake` (350 ms), `blackout` (320 ms), `scare-flash` (420 ms).
   A watchdog removes them if an animation is ever interrupted — a stuck class
   must never be able to hide the game or eat input.
5. Motion is short and hard: 120 ms button presses, 150 ms flash fades,
   typewriter capped at 1.5 s. Nothing gates input; the text finishes typing
   *behind* the interaction.

---

## 3. Pixel philosophy

- **Procedural first.** Every scene is drawn per frame from a handful of
  primitives (gradients, rects, arcs, seeded jitter). No sprite sheets, no
  texture downloads — that is what keeps it Pi-4 friendly and offline.
- **Readable silhouettes.** A scene must be identifiable from its outline at
  320 px: cabin + desk + three window masts, bridge cables, mine mouth,
  deadfall across a ledge.
- **Parallax is depth.** Three bands (far peaks → mid treeline → foreground
  structure) with different sway rates sell distance better than polygons.
- **The environment animates on its own clock** — fog drifts, lightning fires
  every ~95 ticks, the morse on Tower 3 blinks on its own period — so a static
  screenshot never tells the whole story.
- **Restraint as horror.** Movement should be rare enough that when something
  *does* move, the player notices it moving.

---

## 4. Audio design

Web Audio API, all synthesised (`audio.js`) — no samples, no network.

| Layer | Behaviour |
|---|---|
| **Beep** | 380 Hz square on option keys, 520 Hz on CONFIRM — instant physical feedback |
| **Event FX** | `hit`, `gun`, `danger`, `success`, `heal`, `miss`, `static`, `eerie`, `morse`, `email` — dispatched from `state.fx` exactly once per push |
| **Jumpscare** | Silence for 300 ms → violent stab + screen flash. The silence is the payload; never play a riser under it |
| **`ridgeTick(state)`** | Horror bed only in Dead Ridge runs: level tracks sanity and awareness — low drone as sanity falls, scratching at high awareness, gated by weather |
| **Companions** | No voice lines: presence is implied by breathing/static texture tied to roster changes |
| **Mute** | `M` or combo `2+3`; the footer button reflects state, and `SFX.ensure()` resumes the AudioContext on the first user gesture (browsers require this) |

Audio intent: **constant low information, occasional precise information.**
A player should distrust a sound they cannot locate, and obey one they can.

---

## 5. The Living Window (as design)

The centre viewport is a **gameplay surface**, not wallpaper.

### Inputs

`time of day · weather · fog density · sanity · awareness · current location ·
active threat · visit count`

### Outputs

| Signal | Truthful when sane | Lies when frayed |
|---|---|---|
| Silhouettes | Real threats only | False walkers, companions standing outside while inside |
| Distant lights | Tower 3's `H·E·L·P` morse, real campfires | Lights where nothing burns |
| Fog density | Actual weather | Thickens to hide or reveal arbitrarily |
| Tree sway | Wind + awareness | Keeps swaying when the wind stops |
| Glass scratches | Scored by real events (three-beat rhythm) | Fresh scratches appear mid-look |
| Colour tint | None | Blood-red periphery below 45 sanity |

### Rules

1. **The view changes before the words do.** On travel the scene switches to the
   destination first; dialogue and findings are layered on afterwards.
2. **Coming home must feel safe** — the tower screen is the calmest composition
   in the game, and it is allowed to feel *false* safe.
3. **A lie must cost something.** Every false read costs sanity and feeds
   awareness; free information does not exist on this ridge.
4. **Binoculars are the sharpest version of the window** — one focus per day,
   true sightings above 50 sanity, `WINDOW_LIES` below it, with a chance the
   glass slams back at you.
5. **The window, the radio and the crew must never contradict each other at high
   sanity** — contradiction is reserved for low sanity, so the player can always
   trace a discrepancy back to their own mind.

---

## 6. 3D tiers

`scene3d.js` renders the same state as the 2D engine — the game never knows
which one is active.

| Tier | Means |
|---|---|
| `AUTO` | Picks based on detected hardware (4-core → LOW) |
| `HIGH` | Antialiasing, rain particles, ~170 instanced trees — desktop GPUs |
| `LOW` | Reduced density, no AA — Pi 4 target, 30–60 fps |
| `OFF` | WebGL canvas hidden, 2D pixel canvas restored exactly, render loop stopped |

`OFF` must be *pixel-identical* to the 2D build; that is the accessibility and
long-uptime path for a cabinet running 24/7.

---

## 7. Documentation tone

Docs read like a finished indie game's manual: **a practical half for the
player and an in-universe half for the world.** Keep the two visibly separated,
never blend a real instruction into a lore paragraph, and always link back to
the control the paragraph is teaching.
