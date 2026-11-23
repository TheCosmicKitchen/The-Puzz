# Dungeon Scrawl simulator

`scrawl_sim.py` plays Dungeon Scrawl with bots, thousands of runs at a time, so we can see which tricks matter and
evolve new ones. The rules are a straight port of `../scrawl.html`, including the seeded random numbers, so a seed here
deals exactly what the page deals (`scrawl-2026-11-20` is that day's daily, `endless-abcde` is `scrawl.html#abcde`).

Needs Python 3.10+, nothing else. Runs on every core but one (`-j` to change).

## Commands

| | |
|---|---|
| `py tools/scrawl_sim.py selftest` | Replays reference runs captured from the page. Run it after any change to the page or the sim. |
| `py tools/scrawl_sim.py report -n 2000` | The whole health check: three bots, third-trick sweeps, a foe-HP scan, and findings written by rules → `sim-out/report.md` |
| `py tools/scrawl_sim.py trial --round N` | One evolution round: tests the tricks in `ideas/rN.py` against the live ones and records the results in `evolution/history.json` |
| `py tools/scrawl_sim.py publish` | Rebuilds the Lab (`../scrawl-lab/`, on the site at /scrawl-lab/): the report index and the evolution page. `trial` and `report` do this for you. |
| `py tools/scrawl_sim.py compare -n 2000` | Notools vs smart vs eager on the same seeds (`--deep` for endless descents: how far each bot gets) |
| `py tools/scrawl_sim.py replay scrawl-2026-11-20 --bot smart` | One run, turn by turn |

## The bots

None of them are AI; each one searches for its best turn.
* **notools**: Spellblade and Quill only.
* **smart**: uses a trick only when it makes the turn better (beam search over trick sequences).
* **eager**: the tool lover. It spends every charge, picking the best use each time, even when it hurts. This shows which tricks are traps.

Every bot always finds its best words, word order (for the edge) and Quill. They know all 67k words, so they are much
stronger than people: read the results as *how much a trick is worth*, not *how hard the game feels*.

## The evolution loop

1. **Ideate**: write `ideas/rN.py` with `IDEAS` (the new tricks), `PARENTS` (which trick each one evolved from),
   `NOTE` (what the round is testing) and `TEST` (the tricks to trial, with live and earlier ones as controls).
   Trick kinds: `morph` (tile → letter), `choose` (tile → a letter from `options`), `make` (tile → tiles), `pair` (two tiles → two letters).
2. **Trial**: run `py tools/scrawl_sim.py trial --round N` (600 seeds per trick by default, `-n` to change).
   The kit is Quill + Nudge + Flip + the trick, and foe HP is ×2.5 so the strong tricks don't all hit 100% wins.
3. **Evolve**: read the verdicts (keeper / niche / weak / dud / overpowered, plus trap), then write the next round from them.
4. The trial saves itself to the Lab (`scrawl-lab/reports/`) with its version, commit and command. Commit and push to put it on the site.

Idea tricks only exist in the sim. Nothing reaches the game until it is ported to `scrawl.html` by hand.

## Items are data

Every trick except Quill lives in `../scrawl-items.js`, which both the page and the sim read. Neither has trick code of its own, only one small interpreter each (`compileItem` in the page, `compile_item` here). Adding or changing an item means editing that file. The rules fingerprint covers it, so `selftest` notices.

```json
{ "id": "echo", "name": "Echo", "tier": "uncommon", "kind": "pair", "uses": 1,
  "desc": "A tile takes another tile's letter. ...",
  "target": {"type": "notBlank", "msg": "Not on a blank"},
  "effect": {"copyFrom": true} }
```

| Field | Values |
|---|---|
| `kind` | `morph` (change the tile), `choose` (the player picks the new letter), `make` (one tile becomes several), `pair` (two tiles), `swap` |
| `uses` / `perFight` | charges per turn / per foe |
| `tier` | `common`, `uncommon`, `rare`. No tier means retired: never offered, kept for old dailies |
| `from` | optional date: the tool joins dailies from that day (endless and lab runs get it straight away) |
| `target.type` | `any`, `notBlank`, `vowel`, `consonant`, `letters` (+ `letters`), `minValue` (+ `value`). `msg` is shown when refused |
| morph `effect` | `{"shift": n}`, `{"mirror": true}`, `{"map": {"b": "d", ...}}`, `{"set": "?"}` |
| choose `effect` | `{"options": {"letters": "aeiou"}}`, `{"options": {"groups": ["bdpq", "nu"]}}` (the tile's own group) or `{"options": {"steps": [-1, 1]}}` (steps from the tile) |
| make `effect` | `{"make": [{"self": true}, {"copy": true}, {"letter": "e"}]}`. `self` keeps the enchantment, `copy` and `letter` don't |
| pair `effect` | `{"copyFrom": true, "sameKind": true}`: the first tile takes the second's letter |

The file's order matters: it sets the roster order, which the seeded Armoury rolls depend on. Add new items at the end.

## Asset stamps

Pages load every local script and stylesheet as `file.js?v=<hash of the file>`. Run `py tools/stamp_assets.py` before committing, or turn on the hook once with `git config core.hooksPath tools/hooks` and it runs on every commit. `--check` exits 1 if any stamp is stale. Nobody bumps version numbers by hand.

## Versioning

* `SIM_VERSION` in `scrawl_sim.py`: bump it on any change to rules, bots or scoring, and note it below.
* Every history entry records the sim version and the page's rules fingerprint, so results from different rules
  are never mixed up silently.
* Each version is tagged in git as `scrawl-sim-v<version>`. A report names its tag and command, so `git checkout <tag>` then the command reproduces it exactly.
* `sim_fixtures.json` holds reference runs captured from the page. `selftest` must pass before a trial means anything.
  If the page's rules change, port the change, recapture the fixtures in the browser, and bump the version.

## Changelog

* **1.6.0** (2026-11-22): from the 23 Nov daily: blade bonus squares (DL / TL / DW), foes get 27% more health on bonus days (no-tricks win rate 67.6%, as before), and 12 new tools join the roster (Soften, Scribble, Lunge, Recoil, Triplicate, Kin, Bloom, Dial, Spin, Plural, Wye, Resound; 27 in all). New grammar: choose options by `steps`. The planner scores each word by its letter order.
* **1.5.0** (2026-11-20): items as data. Every trick is read from `scrawl-items.js`, the same file the page uses, and the rules fingerprint covers it. Behaviour is fingerprinted identical to 1.4.0 on both page and sim.
* **1.4.0** (2026-11-20): tiered equipment from the 21 Nov daily: a 15-trick roster in common / uncommon / rare (from the 1.2.0 trials), tiered Armoury offers with rare odds rising every three floors; Swap, Rotate, Vowel Shift, Split and Ink Blot retired from offers. Offers checked against the page over 558 rolls.
* **1.3.0** (2026-11-20): fair draws from the 21 Nov daily on (no consonant twice in a hand, one of JQXZ, one of FKVWY); the endless descent (`compare --deep`); fixtures recaptured, including a 13-floor descent.
* **1.2.0** (2026-11-20): exactly reproducible (word ties break in sorted order, not Python's per-process set order); every trial includes all live tricks as controls, so the keeper bar is the same in every round.
* **1.1.0** (2026-11-20): `trial`, `selftest`, evolution history and the Lab; idea files with lineage; the `choose` and `pair` trick kinds.
* **1.0.0** (2026-11-20): port of the four-card kit rules (Spellblade up to 6, daily edge, foe HP ×1.22); notools, smart and eager bots; `compare`, `sweep`, `report`.
