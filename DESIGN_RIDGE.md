# The Watchers of Dead Ridge — Definitive Edition Design Doc

## 1. Design Vision

Dead Ridge is a HypeMyke-style Appalachian overnight: three friends, one glass
cabin, thirty days, and a ridge that is *listening*. The horror is acoustic —
the entity hunts by recognition, not sight. Every conversation, radio listen
and answer is training data.

The core tension: **the tools that keep you sane are the same tools that teach
it your voice.** The radio calms you and feeds the learning meter. The window
informs you and, below 50 Sanity, starts lying. Companions anchor you and can
be imitated. The winning move is *restraint* — submit logs, stay quiet, never
answer when it speaks your name.

## 2. Cast — personalities and change over time

| Character | Personality | How they change |
|---|---|---|
| **Mark** | Systems tech, asthma, gallows humor about the barometers | Stress bends him toward rationalization collapse; his Hardware Buffer helps calibration only while he's holding on |
| **Chloe** | Survivalist, blunt, phobic | Phobia spikes toward breakdown; counts "eyes at the fence"; risk of deadbolt attempts if family voices appear |
| **Sam** | Photographer, impulsive, dark jokes | Obsessive-frame wanderlust raises Awareness; photographs that contain extra people |
| **Dr. Elena Voss** | Clinical acoustics researcher, knows too much | Joins at the ruins (Day ≥ 8); her decoy-tape plan (Voss Protocol) is a real ending path |
| **Ash (The Kid)** | Short sentences, humming, wonder | Morale anchor (+15 sanity); can be saved, lost, or become a mimic trigger |
| **Ranger Cole** | Dispatch relief, arrives Day 13 | Recites your logs back; test him — the laces detail |
| **Arthur Pendelton** | Never present; logs, echoes, late masks | His voice is the entity's favorite costume |
| **The Pale Voice** | Not a person; speaks through radio/companions | Escalates with the learning meter until it finishes your sentences |

Companions carry **individual stress** (0-100) on top of group Sanity: sieges,
deaths, answered calls raise it; daylight sheds a little. Their dialogue band
is `sanity − stress`, so one friend can break while the group still seems fine.

## 3. Plot spine & branching

Day 1 arrival → Day 2 Tower 3 morse (H-E-L-P) → Day 5 Copperhead crossing →
Day 8-11 Voss + the Rule of Three email → Day 10 radio crisis → Day 13 Cole
arrives → Day 14-16 Cabin 2 tape + skylight manifestation → Day 21 Shaft 4
breach (the lift trap) → Day 24 sensor mission (Mark can die) → Day 26 eclipse
→ Day 29 siege (final log code) → Day 30 06:00 judgment.

**8 endings**: The New Watch (never fed it), Voss Protocol (decoy tape), Kept
(Ash out), The Verified Watch (clean shift), The Stolen Face (the lift), The
Perfect Mask (you answered; it practiced), The Hermit of Peak 2, Lost in the
White Noise.

## 4. The Living Window (gameplay)

- Viewport renders **wherever you are**: tower, bridge, ravine, ruins,
  railcar, sinkhole, clearing, towers — each with own composition/fog/motion.
- `Focus Binoculars` (once/day, segment `U`): verified intel at Sanity ≥ 50;
  perception fractures below it (false companions outside, lit dead towers,
  glass-slam scares).
- Window signals carry information: three-beat scratches (it climbed *up*),
  fog density (= Awareness), sway vs wind (something moving the trees), Tower
  3 morse. Low Sanity introduces deliberate lies.

## 5. Dynamic dialogue system

Context-banded line banks per character (high/mid/low), selected by
`sanity − personal stress`, with a per-character recent-line deque so nobody
repeats themselves. Spontaneous lines fire on Crew Check-in, focus results,
radio events and dawn.

## 6. Radio as lifeline and threat

Channels 14/88/104 with personalities (weather band / breathing / numbers).
Every listen feeds the **learning meter**; above ~55 the entity hijacks
channels in companion voices (first hijack guaranteed). Between 30 and full
hijack, **Arthur's Echo** speaks through the band. Answering = +22 learning,
stress on everyone. The Rule of Three: don't answer.

## 7. Sandbox & world reaction

Two daylight actions per day; expeditions cost one and burn light — after
that, the treeline owns the hour. World evolution events fire by day and
change locations (bridge cable snap, Tower 1 goes dark, cabins burn without
fire, an impossible clearing appears, Shaft 4's gate stands open). Nights
outside are lethal decisions; sieges scale with Awareness.

## 8. Files & UI

Backend: `backend/app/game/ridge.py` (mode engine), `ridge_cast.py` (cast,
dialogue, observation tables, endings). Engine hooks: scenario pagination,
`_sync_seg` single-truth 7-segment, ridge dispatch, `LOCK SYNC` confirm.
Frontend: `pixel.js` (location scenes + lies), `laptop.js` (ForestOS overlay
+ weather station, key W / combo 2+4), `audio.js` (bed, heartbeat, scratching,
almost-words, dead air, jumpscares), `ui.js`/`game.js` (combos 1+2 map,
3+4 guide, 1+4 stories, 2+3 mute, seg danger flash). Docs: `RIDGE_MANUAL.md`
(in-universe manual), this file. Hardware: Pi buttons combos (red+yellow =
story page), buzzer misfires at low sanity, random wrong characters on the
7-segment when Sanity frays.
