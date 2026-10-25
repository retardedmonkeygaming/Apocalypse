# Watchtower Field Guide — Fire-Tower 2, Dead Ridge

Two manuals in one file. **Part A** is for the player: how the mode actually
works. **Part B** is the in-universe Pennsylvania Forestry Commission handbook
found in the desk drawer — read it that way if you want to.

---

# Part A — Practical: playing the sandbox

## Your day

Dead Ridge is 30 days of a 3-person fire watch. Each day gives you **2 daylight
actions**; an expedition costs 1 of them. When the budget hits 0 the map locks
and says so — the treeline owns that hour. Rest (CONFIRM at the desk) to roll
the day and refill the budget.

| Hour | What's safe | What it costs |
|---|---|---|
| **Day** | Travel, search, photograph, scavenge | 1 action per trip; risk scales with the node |
| **Dusk** | Travel still allowed — nodes flip to **danger** | Risk +20% |
| **Night** | Listening, radio, the window, crew talk | Being *outside* after dark is a serious decision: risk +20%, sanity hit on every event |

## The five numbers that decide your run

- **SANITY (0–100)** — perception. ≥50: the window and radio tell the truth.
  40–50: crew cadence slips. <40: the glass shows you things that aren't there.
  0: `WHITE NOISE` ending.
- **AWARENESS (0–100)** — how much of you the ridge has logged. Radio, calling
  out, photographing and focusing the binoculars all feed it. Above 60 the map
  reddens; above 75 the risky nodes lock outright.
- **NOISE SIG** — cosmetic mirror of the audio the ridge has captured.
- **TOWER SEAL (0–10)** — structure. Vent interlocks, gusts, sieges.
- **THE LEARNING METER (`rd_learn`)** — invisible. Every radio listen, every
  answer, every word to a companion adds to it. At 30 it starts wearing Arthur
  Pendelton's voice. At 55 channels begin to hijack.

## The map (free-form travel)

Open it with `Tab` or combo `1+2`, then **click a node to walk there**. The
centre viewport becomes that place immediately — you see the risk, the weather
and the ground *before* any dialogue fires.

Status, recomputed every state push from day / weather / night / sanity /
awareness / daylight / where you've been:

| Status | Meaning |
|---|---|
| 🟩 **open** | Reachable, walk it |
| 🟥 **danger** | Reachable but hot — night, storm, fog, high awareness or fraying sanity |
| ⛔ **locked** | No known trail yet, too far until day *n*, no daylight left, or your own hands won't leave the railing |
| ⛔ **blocked** | The storm or an awake ridge has that ground right now |
| ❗ | A story beat is waiting there (bridge day 5, mine day 21+, cabins day 14–16, sensor day 24) |

Trail graph: Tower 2 ↔ Tower 1 ↔ Ravine ↔ Railcar ↔ Bridge ↔ Cabins ↔ Shaft 4
↔ Sinkhole, plus Tower 2 ↔ Bridge / Cabins / Ruins / Sinkhole. Ground opens as
you touch its neighbours — that is the sandbox growing.

## Field verbs (while the viewport is locked on a place)

| Verb | Effect |
|---|---|
| **Search the Site** | Runs the story beat if one is pending, hands over first-visit documents, otherwise a loot-or-risk roll (riskier at night) |
| **Stand Still & Listen** | Daylight: +3 sanity, nothing answers. Night: −3 sanity, +awareness, +learning. Weather: it says something in your own cadence |
| **Call Out** | **+4 learning** — the single fastest way to feed the mimicry loop. At night or low sanity the echo finishes your sentence |
| **Photograph** | +awareness, +3 sanity if steady; recovers the frequency chart after day 8. Below 45 sanity the frame shows you from twelve feet up, timestamped tomorrow |
| **Return to Tower 2** | Home. The one screen that always feels safe — or false safe |

The verb list itself is contextual: fog/storm swaps in *Listen Through the
Weather*, good light and steady nerves swap in *Photograph the Ground*.

## Crew

Mark (systems), Chloe (survival), Sam (photo) — plus **Dr. Elena Voss** (day 8+,
ruins), **Ash** (clearing south of the sinkhole, after the world event) and
**Ranger Cole** (arrives around day 12–15, possibly already compromised).

Each carries independent **stress**. High stress bends their lines even when your
own sanity is fine; at 70+ their hands shake and they talk anyway. Companion
dialogue is drawn from a pool with recent-line memory, so nobody repeats
themselves within a campaign. Talking to Ash or Cole learns *faster* — they are
the voices it wants.

## Radio protocol

- **Channel 14** — weather band. Mostly harmless, sanity +3 in daylight.
- **Channel 88** — breathing. +3 learning per listen. Day 10+: stitched voices.
- **Channel 104** — mud without the frequency chart (Tower 1, or day 12).
- Answering an unknown voice = validating its placement in the environment.
  Don't answer. Silence the band instead.

## Endings you can earn

`VERIFIED WATCH` (win), `STOLEN FACE` (win, wrong), `HERMIT OF PEAK 2`,
`LOST IN THE WHITE NOISE` (sanity 0), plus the Act II–VII branch endings in
[DESIGN_RIDGE.md](../DESIGN_RIDGE.md).

---

# Part B — In-universe: Pennsylvania Forestry Commission

### Section 9 — Station Personnel, Peak 2 (Rev. 1991)

**1. Purpose of the watch.** You are not a guard. You are an observer. Your
instrument panel, your log book and your voice are the entire purpose of this
station. Write down what happens. Do not decide what it means.

**2. The log.** Two entries per day minimum: one at 06:00, one at 18:00. The
enviro-log will reject entries until the barometric arrays are synced. A
rejected log is not a paperwork problem; it is a station-position problem.

**3. On answering the radio.** Transmissions that use your full name, middle
name, or the name of a deceased relative are to be terminated without reply.
Do not acknowledge a hail you do not originate. Acknowledgement is the
instrument by which a signal confirms it has been received.

**4. On voices in the tree line.** Personnel hearing their own voice, or the
voice of another crew member, from a location where that person is known to be
absent, shall note the time and return indoors. Do not call out to correct
them. They are not asking.

**5. On Tower 3.** The state of Pennsylvania does not operate a third fire-tower
on Dead Ridge. There is no southern grid. If you observe structural lights on
the southern peak, do not log them, do not photograph them, and do not climb
them. Report only that the grounding loop occurred, as instructed.

**6. Counting.** Lookout personnel will not count the trees between the ladder
and the ridge edge. Counting invites revision.

**7. On the previous occupant.** R. A. Pendelton's service record has been
withdrawn. Any correspondence, cassette, or log page bearing his name is to be
filed under *unverified*. His dog is not on the property. His dog has never
been on the property.

**8. Weather.** Barometric pressure of 960mb and below does not indicate storm
activity on this peak. If your physical instruments and the digital readout
disagree, seal the exterior iron hatch and deploy the manual deadbolts.

**9. Relief.** Relief arrives on day 30 at 06:00, or earlier on request. If
relief arrives before day 30, check their boots. Official personnel do not wear
backward-facing laces.

**10. Final instruction.** If the station ceases to answer your voice, the
watch is not over. The watch is only over when the log is full.
