# Deep Schema (v2, Phaser)

An underwater survival study game for **ITSC 3160: Database Design and Implementation**.
Swim through eight depth zones, one per lecture. In each zone you scan concepts, open a salvage
crate (sorting or SQL-stacking puzzle) and drive off a creature that stands for a harmful
database design practice. Correct answers earn salvage, which you spend on gear and sub cosmetics.

- **Play it:** https://claude.ai/artifact/FHYrYV83mriG3uHgPZ1CdH
- **Play offline:** open `dist/deep-schema.html` (needs internet once to load Phaser from the CDN)
- **New here?** Read `quickstart/QUICKSTART.md`

## What's new in v2
- Built on **Phaser 3.80** (a JavaScript game engine) instead of hand-drawn canvas code.
- The old `game.js` is split into **33 small ES modules**, grouped by job (see below).
- **Open exploration:** you steer the sub yourself through a big zone. Objectives, a crate, data shards, air vents, stinging jellies and a creature that chases you.
- **Two versions from one codebase:**
  - **Mobile:** thumb-stick and action button, compact zone (2600 px), 1 jelly.
  - **Full:** WASD/arrows, **E** to interact, **Q** for sonar, a bigger zone (4400 px), 4 jellies, a mini-map.
  - It picks automatically by device. You can override it on the Dive map under **Game version**.
- **Graphics setting:** Full effects (WebGL glow and colored trails) or Lite (plain canvas, faster on older phones).

## Folder layout
```
Deep Schema Game/
├── README.md
├── build.py                 ← bundles src/ + config/ into dist/deep-schema.html
├── config/config.js         ← every balance number, price, cosmetic, and the two device profiles
├── src/
│   ├── index.html           ← dev page (loads the modules directly; needs a local server)
│   ├── styles.css
│   ├── main.js              ← entry point: loads the save, starts Phaser, connects UI ↔ scenes
│   ├── data/content.js      ← all questions, creatures and crate puzzles (one zone per lecture)
│   ├── data/bloom.js        ← Bloom's taxonomy levels (Remember → Create) and higher-level questions
│   ├── data/midterm2.js     ← practice midterm 2 questions 1–23, reworded/true-false/blank/code versions, Exam 1 topic questions
│   ├── data/midterm.js      ← practice midterm questions 1–24 plus variations, added to each zone
│   ├── data/studyguide.js   ← Databank study guide definitions and the GROUP BY / HAVING / ORDER BY / LIMIT walkthrough
│   ├── core/                ← util, event bus, save state, device detection
│   ├── systems/             ← economy.js (shop, Sub Bay + SQL query log), dive.js (oxygen, rewards, blackout),
│   │                          ladder.js (Bloom level ladder per zone), raid.js (creature raids on the seabase)
│   ├── art/                 ← procedural drawings baked into Phaser textures (sub, creatures, scenery)
│   ├── entities/            ← Submarine.js (movement, trail, light), Creature.js (chasing creature, jellies)
│   ├── scenes/              ← BootScene, BaseScene (seabase), DiveScene (exploration), backdrop.js
│   └── ui/                  ← HTML panels: sheet (tabs/results), encounter, question (draws every question), hud, controls, tutorial
├── dist/deep-schema.html    ← single-file build; this is what gets published
├── quickstart/QUICKSTART.md
├── tests/                   ← Playwright browser tests (see tests/README.md)
├── vendor/phaser.min.js     ← local copy of Phaser, used only by the tests
└── legacy/                  ← v1 (plain canvas) kept for reference
```

### How the modules talk
Scenes (the Phaser world) and UI (the HTML panel) never import each other. They talk through
`core/bus.js`: for example, `DiveScene` emits `encounter-open` when you press E at a target, and
`ui/encounter.js` listens and shows the question. That keeps each file small and readable.

## How the game works
| Piece | What it does |
|---|---|
| **Zones** | 8 zones = Lectures 1–8. Clearing one unlocks the next; deeper zones need a stronger hull. |
| **A dive** | 4 scans + 1 crate + 1 creature, placed around the zone. Arrows on screen point to unfinished ones. |
| **Oxygen** | Drains while swimming and on mistakes or stings. Air vents refill it. Black out and you lose half your carried salvage. |
| **Shards** | Glowing data shards give a little salvage when you swim into them. |
| **Fabricator** | Hulls, O₂ tanks, rebreather, glider, sonar charges, emergency canisters, seabase modules. |
| **Sub Bay** | Cosmetics as a database: your sub is a row, each slot is a foreign key, purchases go in an `owned_cosmetic` bridge table, and a query log shows the SQL. |
| **Databank** | Three views. **Study guide:** 82 in-depth definitions across all 8 zones, written without abbreviations. **Grouping & sorting:** a worked walkthrough of GROUP BY, HAVING, ORDER BY and LIMIT on a small sample table, with results and common mistakes. **Practice midterm:** Exam 1 format plus answer keys for practice midterm 1 (questions 1–24) and practice midterm 2 (questions 1–23). **My dive log:** creature files and the questions you got right. |
| **Tutorial** | Runs on first launch with a short training dive. Replay from the Dive map. |

### Zones and creatures
| # | Zone | Lecture | Creature (bad practice) |
|---|---|---|---|
| 1 | Kelp Shallows | Intro to Databases | Redundancy Leech |
| 2 | Coral Plateau | Relational Databases | Null Wraith |
| 3 | Grassy Dunes | SQL Part 1: DDL & DML | Whereless Shark |
| 4 | Crystal Caves | SQL Part 2: SELECT & Joins | Cartesian Kraken |
| 5 | Glowshroom Forest | SQL Part 3: Subqueries & Views | Ambiguity Angler |
| 6 | Wreck Field | Data Modeling (ER) | Spaghetti Squid |
| 7 | Thermal Vents | ER to Relational | Orphan Crab |
| 8 | Abyssal Trench | Normalization | Anomaly Leviathan |

## Working on it
1. **Edit:** questions in `src/data/content.js`, numbers in `config/config.js`, behavior in the module you need.
2. **Preview:** browsers won't load ES modules from a double-clicked file, so start a tiny server in the project folder:
   ```bash
   python -m http.server 8000
   ```
   then open http://localhost:8000/src/index.html
3. **Build:** `python build.py` writes `dist/deep-schema.html` (no npm needed).
4. **Publish:** ask Claude to republish `dist/deep-schema.html` to the artifact link above. The link and saves stay the same.

## Technical notes
- **Engine:** Phaser 3.80.1 from cdnjs. All art is drawn in code and baked into textures at startup, so there are no image files.
- **Movement:** the sub uses its own acceleration and drag (`config.sub`) with real frame time, so it moves at the same speed on slow and fast devices.
- **Saves:** `localStorage` key `deep-schema-v1`, the same as v1, so existing progress carries over.
- **Test hook:** `window.__ds` gives the tests read access to the save, the dive and the scenes.

## Status (Oct 15, 2026)
- v2 Phaser rebuild: modules, open exploration, Mobile/Full versions, Lite graphics.
- Bloom's taxonomy ladder per zone, creature raids on the seabase, title screen (Oct 14).
- Both practice midterms and every Exam 1 study-guide topic built into the zones; off-list topics removed (Oct 15).

### Ideas for next time
- More questions per zone (aim for 15+ each), Knowledge Check 6 content
- A review mode for missed questions
- Sound effects behind a button
- Boss rush / timed exam mode
