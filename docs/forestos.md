# ForestOS v4.2 — Laptop Guide

The ruggedized field laptop on the desk of Fire-Tower 2. Amber phosphor, no
network, and an inbox that keeps receiving mail from people who are not
employed by the state.

Open it from the desk menu (**ForestOS Laptop**). CONFIRM closes the lid and
returns you to the cabin.

---

## Boot

```
FORESTOS v4.2 booting... amber phosphor warm. Radio cold.
DESKTOP  ▸ .LOG files · one unread badge · BAROMETRIC ENGINE: SYNC DUE
DOCK     ▸ INBOX · WEATHERRADAR · CALIBRATION · LOGENGINE · DOCUMENTS
```

The laptop is also the weather station's companion: the station overlay
(`W` / combo `2+4`) shows the same numbers as big instrument dials —
temperature, pressure, wind, humidity, visibility and a 6-hour trend strip.

---

## 1. INBOX

Mail arrives by **day**, automatically, and toasts in the top-right corner.
Four per page; CONFIRM cycles pages.

| Day | From | Subject | Why it matters |
|---|---|---|---|
| 2 | NetAdmin-09 | Tower 3 Decommissioning | Establishes the official lie about the southern peak |
| 4 | NetAdmin-02 | Ghost Echoes on Radar | The radar void moves *against the wind* |
| 4 | sam.photo | RE: Southern peak | Only if you sent Sam. 17 attachments, none of them of you |
| 6 | automated-relay | Log Deficit Notice: Tower 1 | Fires if you visited Tower 1 — that keyboard was removed in 2024 |
| 9 | chloe.v | (No Subject) | Only after the bridge — she can hear you playing her own voice |
| 10 | a.pendelton99 | The Rule of Three | The core rule of the whole ridge |
| 12 | HQ-SafetyBoard | Missing Personnel #882 | Arthur Pendelton has never existed as an employee |
| 15 | Unknown | `we see you` | Only at low sanity. It knows about the spacing of the trees |
| 18 | NetAdmin-02 | Voice Print Fraud | How to tell a real teammate from a cloned one |
| 22 | sam.photo@archive | Look at the flash | Only after the mine |
| 25 | automated-relay | Total Vacuum Anomaly | 950mb is impossible — seal the hatch |
| 27 | HQ-Admin | Operation Deep-Sweep | Evacuation route change; check the boots |
| 30 | a.pendelton99 | Goodnight | The log is full. It knows your voice perfectly |

Reading mail is free. **Replying to it is not a thing you can do** — that is
deliberate.

---

## 2. WEATHERRADAR

A grid overlay of the ridge with density vectors crawling west to east, except
one circular mass 300 m wide sitting directly over Tower 2.

| Day | Reading |
|---|---|
| 1–7 | `nominal` |
| 8–18 | `MOVING AGAINST THE WIND` |
| 19+ | `OUT OF RANGE // SENSOR ARRAYS COMPROMISED` — and the masts are coming down |

Options: **Mark: Analyze the Anomaly** (better intel, more awareness),
**Toggle Monitor Backlight** (calmer), **Back**.

---

## 3. BAROMETRIC CALIBRATION (mini-game)

Runs on CONFIRM (**LOCK SYNC**).

```
NORTH ARRAY  982 mb — STABLE
VALLEY COIL  994 mb — STABLE
SOUTH ARRAY  988 mb — STABLE | ⚠ MIMICRY INTERFERENCE DETECTED
CURRENT DIGITAL DEVIATION:  +23 mb  <-- CRITICAL IMBALANCE
```

1. Steer the correction coefficient (`<< -10`, `< -1`, `> +1`, `>> +10`) until
   the deviation is within ±2 mb.
2. Press CONFIRM to **LOCK SYNC**.

Rules that matter:

- The honest target is the **median of the honest arrays**. When the South
   array is flagged as mimicking, it must be excluded — North + Valley only.
- Locking within ±2: +5 sanity, log integrity confirmed.
- Missing it: **−15 sanity**, static from the speakers, +awareness, tower
   damage.
- Locking onto the South array's 1013 mb *exhalation* opens the lower vents.

Calibration is a prerequisite for the **Log Engine**.

---

## 4. LOGENGINE

The daily enviro-log. Each day has a validation string:

```
DR-07-543      ← code for day 7 (day × 7919 mod 997)
```

Three entry choices:

| Entry | Result |
|---|---|
| The exact code | Log accepted |
| The code in lowercase | Rejected — the system does not accept partials |
| `ARTHUR SENT ME` | Accepted into a file nobody will read |

Missed logs accumulate in `rd_logs_missed` and are remembered at the end of the
campaign.

---

## 5. DOCUMENTS

Recovered files, four per page, always found by someone who is now missing:

| File | Found at |
|---|---|
| Log Entry #01 — Arthur Pendelton | Fire-Tower 1, desk drawer |
| Forestry Codebook §9 | Ruins / early game knowledge |
| Incident Summary Report 1991 | Overturned Railcar |
| Cassette: Arthur's Dictation | Ranger Station Ruins root cellar |
| Local Frequency Analysis Chart | Tower 1, or a photograph at any site after day 8 |
| Project Skin-Stitch Bio-Data | Overturned Railcar lockbox |

The **frequency chart** unlocks Channel 104. The **codebook** explains why you
must never answer a transmission containing your own name.

---

## 6. Keyboard / button map for laptop screens

| Input | Action |
|---|---|
| `1`–`4` | The four listed options on any ForestOS screen |
| CONFIRM | Cycles inbox pages / locks sync / closes lid |
| `F` (7-seg) | You are inside ForestOS |
| combo `3+4` | Field manual overlay (works over the laptop) |

---

## 7. Known behaviour / troubleshooting

- **The laptop is dark.** Day 21+: the master breaker tripped. Go to Old Mining
  Shaft 4 — the beat is marked `!` on the map.
- **Radar says OUT OF RANGE from day 19.** Intended. The sensor masts are being
  taken down one by one.
- **No unread badge.** Mail is marked read when you open it; the toast only
  fires once per message id.
- Everything here runs offline. The optional Gemini hook only adds flavour
  lines to events and is never required for any of the above.
