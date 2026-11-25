# Dungeon Scrawl simulator

`scrawl_sim.py` plays Dungeon Scrawl with bots, thousands of runs at a time, so we can see which tricks matter and
evolve new ones. The rules are a straight port of `../scrawl.html`, including the seeded random numbers, so a seed here
deals exactly what the page deals (`scrawl-2026-11-20` is that day's daily, `endless-abcde` is `scrawl.html#abcde`).

Needs Python 3.10+, nothing else. Runs on every core but one (`-j` to change).

## Commands

| | |
|---|---|
| `py tools/scrawl_sim.py selftest` | Replays reference runs captured from the page. Run it after any change to the page or the sim. |
| `py tools/scrawl_sim.py fixtures capture.json` | Stamps a capture from `capture_fixtures.js` with the rules fingerprint and saves it as `sim_fixtures.json`. |
| `py tools/scrawl_sim.py report -n 2000` | The whole health check: three bots, third-trick sweeps, a foe-HP scan, and findings written by rules → `sim-out/report.md` |
| `py tools/scrawl_sim.py trial --round N` | One evolution round: tests the tricks in `ideas/rN.py` against the live ones and records the results in `evolution/history.json` |
| `py tools/scrawl_sim.py publish` | Rebuilds the Lab (`../scrawl-lab/`, on the site at /scrawl-lab/): the report index and the evolution page. `trial` and `report` do this for you. |
| `py tools/scrawl_sim.py compare -n 2000` | Notools vs smart vs eager on the same seeds (`--deep` for endless descents: how far each bot gets), with how often each foe ends a run |
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
   Write ideas as `RECORDS = [...]` in the item grammar below (they can be pasted into the roster as they are, and their trial runs are cached),
   or as `IDEAS = {name: tool dict}` in Python for mechanics the grammar can't say yet. An idea can't reuse a live item's id.
2. **Trial**: run `py tools/scrawl_sim.py trial --round N` (`-n` seeds per trick; `--quick` for the heuristic bots, `--base ''` to trial a trick alone).
   Runs are deterministic, so every run of a live trick or a record idea is cached in `sim-out/run-cache-*.pkl` (keyed by the
   sim's rules and planner code, the page's rules and the foe HP scale): a round only plays its new ideas.
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
| `kind` | `morph` (change the tile), `choose` (the player picks the new letter), `make` (one tile becomes several), `pair` (two tiles), `swap`, `draw` (new tiles), `reroll` (random letters), `affix` (pop a prefix or suffix), `socket` (spell a word into it) |
| `uses` / `perFight` | charges per turn / per foe |
| `tier` | `common`, `uncommon`, `rare`. No tier means retired: never offered, kept for old dailies |
| `from` | optional date: the tool joins dailies from that day (endless and lab runs get it straight away) |
| `target.type` | `any`, `notBlank`, `vowel`, `consonant`, `letters` (+ `letters`), `minValue` (+ `value`). `msg` is shown when refused |
| morph `effect` | `{"shift": n}`, `{"mirror": true}`, `{"map": {"b": "d", ...}}`, `{"set": "?"}` |
| choose `effect` | `{"options": {"letters": "aeiou"}}`, `{"options": {"groups": ["bdpq", "nu"]}}` (the tile's own group) or `{"options": {"steps": [-1, 1]}}` (steps from the tile) |
| make `effect` | `{"make": [{"self": true}, {"copy": true}, {"letter": "e"}]}`. `self` keeps the enchantment, `copy` and `letter` don't |
| pair `effect` | `{"copyFrom": true, "sameKind": true}`: the first tile takes the second's letter |
| morph `{"fx": ...}` | `{"fx": "fire"}` (or `steel`, `gold`, `leaf`): the tile keeps its letter and takes that enchantment |
| draw `effect` | `{"draw": {"n": 2, "pool": "vowel"}}`: no tile needed, a button on the card. `pool`: `any`, `vowel`, `consonant` (weighted like the bag) or a string of letters (even odds) |
| reroll `effect` | `{"reroll": {"pool": "same"}}`: the tile gets a random other letter (`same` = its own kind). With `"hand": true` no tile is needed and every tile the `target` allows rerolls |
| affix `effect` | `{"affix": {"list": ["re", "ing"], "offer": 2}}`: no tile needed; pops one entry as new tiles at random, or rolls `offer` of them for the player to pick |
| socket `effect` | `{"socket": {"len": 3, "dmg": 2, "block": 1, "heal": 0, "draw": 0}}`: the player drops `len` tiles that spell a word into the card and presses Set. Deals `dmg` × (points + 🔥), gives `block` × points, heals `heal`, draws `draw` |

**Random tricks** (draw, reroll, affix, and a socket that draws) roll `mulberry(hseed(seed-roll-<foe>-<turn>-<n>))`, where n counts
the random uses this turn. Everyone rolls the same on a daily, and Undo puts the counter back, so it can't reroll. The bots
never peek: they value a random trick by 8 outcomes from a separate stream (`-plan-`), use it if that average beats the
turn they have, then plan the rest of the turn after seeing the real roll.

The file's order matters: it sets the roster order, which the seeded Armoury rolls depend on. Add new items at the end.

## The sword (runes and the bag)

From the `from` daily in `../scrawl-blade.js` (endless and lab runs at once) the Spellblade is a sword. Page and sim read the same file, and the rules fingerprint covers it.

| Field | Meaning |
|---|---|
| `squares` | The blade's six slots: `hilt` (a word that starts there gives `hiltPer` block per letter), `dl`, `tl`, `dw`, or `null` |
| `foeHp` | Foe health multiplier on sword days, in place of the 1.27 bonus-day boost |
| `sockets`, `maxLevel` | Runes the sword holds, and how far taking the same rune again levels it |
| `bagCap` | Unused tiles kept for the next turn (enchanted first, then blanks, then the order `seariotnld...`) |
| `runes[].kind` | `pommel` (hilt block per letter), `parry` (block per unused tile at the end of the turn), `bastion` (unused block carries over, up to n), `whet` (+n per earlier word against this foe), `reach` (+n per letter past the third), `flurry` (+n per earlier word this turn), `leech` (heal n per letter past the third), `fuller` (bonus squares in slots 4 and 5) |
| `runes[].per` | The value at levels 1, 2, 3; `{n}` in `desc` shows it |

Tiles go in any slot; a word is one unbroken row, and the planner tries each word on the hilt and wherever it hits hardest. At each Armoury one rune is on offer beside the three tricks (seeded by `-rune-<d>`; a new rune while a socket is free, else an upgrade). Draft policies: `random` treats the rune as a fourth offer, `tools` never takes one, `blade` always does, `runes` takes only runes.

Experiments (all commands): `--runes pommel:2,parry` (fixed runes), `--bag-cap N`, `--bag-policy auto|high|first`, `--no-blade` (the 1.6.0 rules), `--rune-per '{"pommel":[2,3,4]}'`, `--blade-json '{"foeHp":2.2}'`.

## Foes

Every foe has a three- or four-move cycle shown one turn ahead. From the 27 Nov daily (endless and lab runs straight away) a
daily's first foe comes from `EARLY` (the old five plus seven easy new ones), its second from `MIDDLE` (the old five plus eight),
and The Editor is always third. The five deep foes (`kerning`, `mirror`, `abridger`, `rex`, `cluster`) only turn up down the
endless descent, where any foe but The Editor can appear. Dailies before 27 Nov keep the old five.

A new foe's trick lands on your next turn and sits in `S.hex` (`Game.hex` here) for that turn: hand tricks (`ban`, `steal`,
`pied`, `smudge`, `censor`, `silver`, `dogear`, `hang`, `cluster`, `diph`) act when the hand is drawn, with the turn's trick dice;
scoring tricks (`caps`, `ellipsis`, `kern`, `pedant`, `abridge`, `rex`, `reflect`, `stammer`, `fine`, `lock`) change how words
score that turn. `foeHex` / `foe_hex` and the end of `wordHit` / `hex_post` are the whole of it.

From 27 Nov every new foe meets the sword, so the tricks follow the word wherever it sits: Dog-ear folds a free slot among the
first four (none if the sword's squares fill them), Ellipsis zeroes the word's own last letter, and Tight Kerning keeps words
inside the first four slots. Foe tricks act on the fresh draw only; the bag's tiles are safe, as from the Editor's red pen.
`capture_fixtures.js` also plays each new foe for nine turns and scores fixed words under every scoring trick.

## Asset stamps

Pages load every local script and stylesheet as `file.js?v=<hash of the file>`. Run `py tools/stamp_assets.py` before committing, or turn on the hook once with `git config core.hooksPath tools/hooks` and it runs on every commit. `--check` exits 1 if any stamp is stale. Nobody bumps version numbers by hand.

## Versioning

* `SIM_VERSION` in `scrawl_sim.py`: bump it on any change to rules, bots or scoring, and note it below.
* Every history entry records the sim version and the page's rules fingerprint, so results from different rules
  are never mixed up silently.
* Each version is tagged in git as `scrawl-sim-v<version>`. A report names its tag and command, so `git checkout <tag>` then the command reproduces it exactly.
* `sim_fixtures.json` holds reference runs captured from the page. `selftest` must pass before a trial means anything.
  If the page's rules change, port the change, recapture the fixtures in the browser, and bump the version. To recapture,
  open `scrawl.html#lab`, run `capture_fixtures.js` in the console, save the string it returns and run
  `py tools/scrawl_sim.py fixtures that-file.json`. Besides the scripted runs it plays every trick in the lab kit on three
  seeds, so random tricks, affixes and sockets are checked use by use.

## Changelog

* **2.0.0** (2026-11-25): new trick kinds: `draw`, `reroll`, `affix` (random prefixes and suffixes), `socket` (spell a 3-letter word into the trick) and enchanting morphs (`{"fx": ...}`), on page and sim. Random tricks roll a seeded stream per use; bots value them from 8 imagined outcomes and replan after the real roll. Hands over 8 tiles plan with their 50 best words. Trials no longer let an old idea shadow a live item with the same id (rounds 1 to 3 had swapped old prototypes in for Recast, Respell, Back and others as controls), and cache their runs. `capture_fixtures.js` and the `fixtures` command; the fixtures now play every trick in the lab kit. Bots: `quick` and `qeager`, heuristic versions of smart and eager (greedy word order, the 5 most promising single-tile changes per trick by a one-pass word index, 4 imagined rolls); `trial --quick` uses them, `--base ''` trials each trick alone over no tricks, `--bar` sets a floor for keepers. 12 new tricks join the roster from the 27 Nov daily (Inkwell, Vowel Pouch, Lucky Letter, Polish, Ember, Suffix, Prefix, Gild, Grab Bag, Exchange, Glyph, Hyphen), tiered by hand from one 40-seed pilot; no evolution rounds were run (round 4 and 5 idea files are written, untrialled). Past dailies replay exactly as before.
* **1.9.0** (2026-11-25): 20 new foes from the 27 Nov daily (endless straight away): Smudge, Pied Type, Ellipsis, Dog-Ear, Diphthong, Silverfish, The Stammer (first-foe pool); Lipogram, The Plagiarist, Small Caps, The Pedant, Hangman, Overdue Fine, Writer's Block, The Censor (second-foe pool); Tight Kerning, Mirror Writing, The Abridger, Thesaurus Rex, Consonant Cluster (descent only). The descent ramps faster on those seeds: +3 HP a floor and +0.15 attack every three floors (was +2 and +0.1). `HARD_HP` / `HARD_ATK` multiply foe health and attack on the same seeds; they stay at 1 because the sword's ×2.4 already lifts foe health from that day (`compare --hard H,A` scans them). The planner scores every foe trick, and `compare` reports how often each foe ends a run. (1.8.0 is left for an open PR.)
* **1.7.0** (2026-11-24): from the 27 Nov daily the Spellblade is a sword (`scrawl-blade.js`): hilt (1 block a letter), crossguard DL, tip DW in place of the rolled bonus squares, and tiles go in any slot. Eight runes for the sword, one on offer at each Armoury beside the tricks (3 sockets, 3 levels). A holdover bag keeps 2 unused tiles for the next turn. Foes get ×2.4 health on sword days in place of ×1.27 (no-tricks win rate back to about 2 in 3). Fixtures are captured with `tools/capture_fixtures.js` and include sword cases with preset runes.
* **1.6.0** (2026-11-22): from the 23 Nov daily: blade bonus squares (DL / TL / DW), foes get 27% more health on bonus days (no-tricks win rate 67.6%, as before), and 12 new tools join the roster (Soften, Scribble, Lunge, Recoil, Triplicate, Kin, Bloom, Dial, Spin, Plural, Wye, Resound; 27 in all). New grammar: choose options by `steps`. The planner scores each word by its letter order.
* **1.5.0** (2026-11-20): items as data. Every trick is read from `scrawl-items.js`, the same file the page uses, and the rules fingerprint covers it. Behaviour is fingerprinted identical to 1.4.0 on both page and sim.
* **1.4.0** (2026-11-20): tiered equipment from the 21 Nov daily: a 15-trick roster in common / uncommon / rare (from the 1.2.0 trials), tiered Armoury offers with rare odds rising every three floors; Swap, Rotate, Vowel Shift, Split and Ink Blot retired from offers. Offers checked against the page over 558 rolls.
* **1.3.0** (2026-11-20): fair draws from the 21 Nov daily on (no consonant twice in a hand, one of JQXZ, one of FKVWY); the endless descent (`compare --deep`); fixtures recaptured, including a 13-floor descent.
* **1.2.0** (2026-11-20): exactly reproducible (word ties break in sorted order, not Python's per-process set order); every trial includes all live tricks as controls, so the keeper bar is the same in every round.
* **1.1.0** (2026-11-20): `trial`, `selftest`, evolution history and the Lab; idea files with lineage; the `choose` and `pair` trick kinds.
* **1.0.0** (2026-11-20): port of the four-card kit rules (Spellblade up to 6, daily edge, foe HP ×1.22); notools, smart and eager bots; `compare`, `sweep`, `report`.
