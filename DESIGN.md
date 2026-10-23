# Apocalypse Terminal (Channel 7) — Game Design Document

## 1. Vision & Core Philosophy

**Apocalypse Terminal** is a complete, atmospheric retro-CRT pixel survival game engineered for dual deployment:
1. **Physical Arcade Cabinet on Raspberry Pi 4**: Running with 5 arcade pushbuttons (Red, Blue, Green, Yellow, Confirm), a single-digit 7-segment LED display, and a passive PWM audio buzzer.
2. **Modern Web Experience on PC/Mac**: Running with responsive HTML5 Canvas procedural pixel art, Web Audio API 8-bit chiptune synthesis, and realistic glowing 7-segment and CRT distortion shaders.

### Tone & Themes
- **Grim but Humane**: The world has collapsed, but survival is not merely about min-maxing canned peaches. It is about who you remain when the deadbolt is still yours to open.
- **Moments of Grace**: Small, intimate moments—Sister Miriam lighting beeswax candles in the ruins of St. Jude's, the Kid assembling bottlecaps into a tiny fort, Marcus checking audio levels on dead frequencies—contrast against the cold dread of nightfall breaches and spreading infection.
- **Meaningful Consequences**: No grinding filler. Every expedition is a distinct story beat or tactical combat encounter. Every person you shelter drinks your water, eats your food, and alters your ending.

---

## 2. Narrative Arc & Major Characters

The spine of the story is **Channel 7 Emergency Radio**, broadcasting from a steel needle above the ruins. Marcus Hale's weary voice promises **Fort Halcyon at Mile 18**: water, doctors, barracks, and salvation behind concrete blast walls. But as the days advance, the truth of Halcyon peels away.

### Characters / Companions
- **Marcus “Radio” Hale**
  - *Role*: Former AM emergency broadcaster.
  - *Voice & Persona*: Measured, baritone cadence with an anchor's pause before each phrase. Knows the government scripts are wearing costumes.
  - *Arc*: Recruited from the Radio Tower. Can repair and boost the base transceiver. Eventually confesses the dark reality of Halcyon—the military sealed the gates weeks ago and left automated propaganda running to funnel survivors into quarantine holding pens.
- **Dr. Lena Voss**
  - *Role*: Pathologist & virologist. Infected with the pathogen, currently in the **Lucid Rot** stage.
  - *Voice & Persona*: Sharp, clinical, running on caffeine and intellectual defiance. *"Do not romanticize my lucidity. It is a symptom with manners."*
  - *Arc*: Rescued from the Hospital ICU. Synthesizes inhibitor injections to lower the player's infection tick at the cost of physical strain. In the late game, her infection reaches a terminal threshold; she can sacrifice her remaining hours to brew the world's only true vaccine (*"Last Light"* ending).
- **The Kid** (Eli / Jun / Rae / Nico / Sam)
  - *Role*: Child survivor found hiding in the elementary school or apartment closet.
  - *Voice & Persona*: Observant, quiet, carrying a backpack of scavenged trinkets. Asks the blunt questions adults step around.
  - *Arc*: Represents the moral anchor of the run. Feeding and protecting the Kid raises Humanity and unlocks unique emotional story beats (the bottlecap medal). Leaving them behind or acting ruthlessly causes them to become silent and eventually run away. Surviving with the Kid unlocks *"The Shepherd"* ending.
- **The Butcher**
  - *Role*: Ruthless predator and scavenger king operating out of the industrial Warehouse.
  - *Voice & Persona*: Jovial, terrifying, pragmatic. Treats human flesh and bone as trading commodities. *"Meat is meat when the shelves are bare, friend. You have good posture."*
  - *Arc*: Offers tempting trades (high food/scrap for ammo or weapons). Crossing him or inspecting his back room triggers an intense boss fight. Alternatively, low-humanity players can ally with him to rule the ruins (*"The New Butcher"* ending).
- **Sister Miriam**
  - *Role*: Religious survivor holding vigil in the ruined Church.
  - *Voice & Persona*: Gentle, unwavering fortitude. Has buried an entire parish and refuses to surrender empathy. *"Mercy is not a mood. It is a discipline."*
  - *Arc*: Bestows spiritual blessings (the Wooden Cross charm), mitigates morale loss, and holds a final candlelit memorial service (*"Ash and Amen"* ending). Departs if the player descends into cruelty.
- **Ghost**
  - *Role*: Mute subterranean scout of the Subway Tunnels.
  - *Voice & Persona*: Communicates via rhythmic taps, chalk arrows, and silent gestures. Throat scarred from an old survival wound.
  - *Arc*: Provides the Subway Transit Key, drastically improving player flee chances and unlocking hidden underground safe havens (*"Under the City"* ending).
- **Scraps the Dog**
  - *Role*: Camp companion wirehaired terrier.
  - *Arc*: Rescued from an alley shambler. Warns of night incursions, prevents surprise door breaches, and raises morale every dawn (*"Four-Legged Dawn"* ending).

---

## 3. Major Systems & Gameplay Mechanics

### The Hub Loop (Home Base)
Each day is divided into discrete action slices:
- **Daytime**: 2 action slices (Morning and Afternoon).
- **Nighttime**: 1 action slice (Dusk/Night).
- **Dawn**: Upkeep consumption, base passive production, infection progression, and state evaluation.

At Home Base, the player can:
1. **Scavenge**: Choose between 4 dynamically mapped destinations with varying risk levels.
2. **Workbench (Crafting)**: Assemble weapons, survival gear, and camp upgrades.
3. **Fortify Base**: Spend scrap to drive boards across doors/windows (0–10 level), keep watch, or rest.
4. **Voices (Companions / Radio / Journal)**: Speak with recruited survivors, tune Channel 7, or write in the journal.
5. **Confirm Button (REST)**: Spends food and water to sleep, restoring 20–30 HP and advancing the clock.

### Base Fortification & Upgrades
Upgrades visibly change the procedural pixel canvas:
- **Barricade Level (0–10)**: Visually adds heavy cross-timbers over the apartment window. Reduces night threat and mitigates combat damage at base.
- **Gutter Rain Catcher**: Collects +2 fresh water whenever weather is `rain` or `storm`. Displayed as a blue collection drum in the corner.
- **Planter Soil Box**: 65% chance each dawn to harvest +1 food. Displayed as a window box of green root vegetables.
- **Tripwire Tin Alarm**: Cancels night breach ambushes. Displayed as taut wire with suspended tin cans.
- **Clean Med Station**: Increases rest healing from 20 HP to 30 HP.
- **Channel 7 Booster**: Unlocks clear radio reception and the extraction broadcast line.

### Infection System (6 Stages)
Infection is not a binary game-over timer; it is a progressive biological degradation:
1. **Clean (0%)**: Full vigor, standard hit accuracy.
2. **Scratch (1–24%)**: Minor bite or scratch. Treatable with clean gauze or herbal poultice.
3. **Fever (25–49%)**: Sweats and chills. -10% combat accuracy, amber screen tint.
4. **Lucid Rot (50–74%)**: Pathogen enters neurological channels. Green screen tint, -20% combat accuracy, increased food consumption, Dr. Voss commentary.
5. **Turning (75–99%)**: Erratic pulse, visual chromatic aberration, companions fear you.
6. **Turned (100%)**: Fatal cellular collapse (*"The Listener"* ending).

### Tactical Turn-Based Combat
Combat is active and decisive, with telegraphed enemy intents:
- **Strike**: Melee attack using equipped weapon (Fists: 4 dmg, Pipe Club: 9 dmg, Crowbar: 13 dmg with armor pen, Spiked Bat: 16 dmg, Machete: 20 dmg).
- **Guard**: Tucks behind cover. **Mitigates 65% incoming damage and 100% blocks infection bite rolls.**
- **Fire Gun**: Consumes 1 ammo. Deals high burst damage (22–40 dmg) with a chance to stun and skip the enemy's retaliatory turn.
- **Molotov**: Consumes 1 molotov cocktail. Deals 26+ area fire damage and 100% stuns the target.
- **Flee**: Escape attempt based on enemy type, fog weather (+20%), and Ghost's scout bonus (+15%).

### Dynamic Weather & Atmospheric Lighting
- **Clear**: Baseline visibility and risk.
- **Overcast**: Cold, somber lighting.
- **Rain**: Replenishes water in rain catchers; visual falling rain streaks and ground splashes.
- **Heavy Fog**: Reduces combat accuracy by 15%, but increases stealth and flee chances by 20%. Drifting layered mist.
- **Storm**: Torrential rain with random lightning strikes (flashes canvas white with screen shake). Tests weak base barricades.

### Morality & Humanity (0–100)
Every significant moral choice shifts the Humanity score:
- Sharing food with hungry travelers, burying the dead, listening to the Kid, and sparing helpless enemies increases Humanity.
- Stealing from scavengers, executing survivors, trading with the Butcher, and turning away desperate souls reduces Humanity.
- At Humanity <= 18, Sister Miriam and the Kid will slip away into the night.
- High Humanity (>55) is required for *"The Shepherd"* and gentle sanctuary endings.

---

## 4. Endings Catalog

1. **Halcyon Gate**: Reached Fort Halcyon with balanced stats. Doors close in your favor.
2. **Quarantine Flag**: Arrived at Halcyon with low humanity; funneled into labor containment.
3. **The Shepherd**: Delivered the Kid and companions through the ruins to safety.
4. **The Quiet House**: Survived 20+ days with full self-sufficient base upgrades (garden, rain catcher, fort >= 7).
5. **Last Light**: Dr. Voss synthesizes the world's only true cure at the cost of her life.
6. **Signing Off**: Broadcast the truth on Channel 7 with Marcus, guiding thousands of survivors.
7. **Black Water**: Repaired and launched the diesel trawler at the docks into the open sea.
8. **Under the City**: Followed Ghost into the subterranean machine vaults.
9. **Ash and Amen**: Sister Miriam and you hold final vigil, creating sacred ground amidst the ashes.
10. **The New Butcher**: Ruled the ruins through terror and cold steel.
11. **Four-Legged Dawn**: Survived the long winter with Scraps the dog.
12. **Cold Floor**: Bled out in combat.
13. **The Listener**: Overcome by infection, turned into the walking dead.
14. **Empty Cupboard**: Starvation and dehydration in an empty room.
15. **The Door Gives**: Overwhelmed by a night breach when fortification fell to 0.

---

## 5. Pixel Art & Sound Direction

- **Resolution**: 320x180 scaled with nearest-neighbor interpolation on an HTML5 Canvas.
- **Procedural Layering**: Multi-tier parallax city skyline, animated celestials, layered weather particle systems, and customizable CRT phosphor scanlines.
- **Audio Architecture**: Pure Web Audio API chiptune synthesis (square, sawtooth, triangle waves) and gpiozero passive PWM buzzer output. Zero external mp3 dependencies; 100% playable offline.
