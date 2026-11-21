# Round 4 catalog: hypothetical items

Design only. Nothing here is in the game or the sim yet. The **Tier** column is a first guess, to be settled by trials.
The **Sim** column says whether the sim can trial the item as it stands, or what it needs first:

- **ready:** an existing trick kind: morph, choose, make or pair.
- **dmg:** a trick that also deals damage. This needs a small engine hook.
- **status:** touches foe or player statuses.
- **draw:** needs seeded draws, plus a fair planner that averages outcomes instead of peeking at them.
- **meta:** acts on the Armoury or the turn structure.

All randomness is seeded from day, floor, turn and use count, so a daily stays the same puzzle for everyone.

## 1. Letter tricks with a little damage
Tricks that reshape a letter and chip the foe at the same time, so small turns still feel like progress.

| Item | Tier | What it does | Why | Sim |
|---|---|---|---|---|
| Chisel | common | Nudge a tile one step on, and deal 1. | Nudge with a sting. The baseline for this family. | dmg |
| Sharpen | common | A consonant moves one step on. If it becomes a 4+ tile, deal 2. | Pushes letters toward high values. | dmg |
| Scratch | common | Flip a tile and deal its old points ÷ 2. | Turns a dead high tile into damage plus a usable letter. | dmg |
| Carve | uncommon | Remove a tile and deal its points; leave an E in its place. | Quill and Split in one: damage plus vowel fixing. | dmg |
| Ricochet | uncommon | Upend a tile (your pick). If the new letter is in your next word, that word gets +3. | Choose a letter, then cash in. | dmg |
| Ember | uncommon | Recolour a tile to 🔥 Flaming, once a foe. | Enchant instead of transform. Fire adds +4 when used. | ready* |
| Engrave | rare | A tile becomes any letter and is ✨ Gilded (double points), once a foe. | Recast plus Gild: a big setup piece. | ready* |
| Splinter | rare | Split a 4+ tile into two copies of its letter, and deal 2. | Twin's power with a high-value gate. | dmg |

\* Needs the make/morph kinds to set an enchantment, a one-line engine change.

## 2. Hand shaping (little moves on the whole hand)
| Item | Tier | What it does | Why | Sim |
|---|---|---|---|---|
| Shuffle Rack | common | Reorder your hand. Free, and it never uses up. | Pure quality of life. No power, but it helps people see words. | n/a |
| Comb | common | Every vowel in hand moves one step (A→E→I→O→U), once a turn. | A whole-hand Vowel Shift. Strong only when it lines up. | ready |
| Tumble | common | Every consonant in hand moves one step on, once a foe. | A dramatic hand reroll you can predict. | ready |
| Pair Up | uncommon | Your two lowest tiles both become copies of your highest-value tile. | Ramps damage, risks unspellable hands. | ready |
| Hollow | uncommon | Turn your highest-value tile into a blank that keeps its points, once a foe. | Fixes "I have a Q" without losing the damage. | ready* |
| Mirror Hand | uncommon | Flip every tile in your hand, once a foe. | A wild swing. Good on Mirror days. | ready |
| Fold | uncommon | Merge two tiles into one: the first letter, worth both tiles' points. | Fewer letters, but one heavy tile for Quill or a word. | ready* |
| Anagram | rare | Your next word may use one tile twice. | Bends the spelling rule instead of the letters. | meta |
| Ink Bridge | rare | Your next word may be 7 letters (bonus +10). | Raises the blade's cap for one strike. | meta |

## 3. Draws and keeps
| Item | Tier | What it does | Why | Sim |
|---|---|---|---|---|
| Inkwell | common | Draw 1 tile, once a turn. | The simplest draw. The fair-planner test case. | draw |
| Vowel Pouch | common | Draw a vowel, twice a foe. | Fixes consonant-heavy hands. | draw |
| Satchel | uncommon | Keep 1 unused tile into next turn. | Planning across turns. | draw |
| Scry | common | See next turn's hand now. | Information instead of power. Lets you pick between Quill and a word. | meta |
| Fresh Page | uncommon | Redraw your whole hand, once a foe. | A mulligan. | draw |
| Bookmark | rare | Your next hand is 7 tiles. | A bigger hand is the strongest buff in the trials (see Twin and Sprout). | draw |
| Pickpocket | uncommon | Draw 1 tile; if it's a consonant worth 4+, deal its points too. | A draw with a gamble on top. | draw+dmg |

## 4. Rerolls
| Item | Tier | What it does | Why | Sim |
|---|---|---|---|---|
| Shake | common | Reroll one tile (same kind: vowel stays a vowel), twice a turn. | A controlled gamble. | draw |
| Rattle | uncommon | Reroll every consonant, once a foe. | A bigger gamble. | draw |
| Haggle | common | Reroll the Armoury offers once per stop. | Shapes the build, not the fight. | meta |
| Loaded Dice | rare | Your rerolls can't draw J, Q, X or Z. | An upgrade to other tricks; only matters in combos. | meta |
| Second Draft | uncommon | The Armoury offers 4 tricks instead of 3. | More choice, same power. | meta |

## 5. Statuses: answering the foes
| Item | Tier | What it does | Counters | Sim |
|---|---|---|---|---|
| Eraser | common | Un-cross one red-penned tile, twice a foe. | The Editor | status |
| Spellcheck | common | Put a jumbled tile back to its old letter. | Typo Gremlin | status |
| Earplugs | uncommon | Your vowels keep their points while Muffled. A passive item. | Silent E | status |
| Bookworm Trap | common | Nibble can't take a tile from you, once a foe. | Bookworm | status |
| Paper Cut | common | Deal 3 to a foe that's armoured; the armour can't block it. | Dust Jacket | status+dmg |
| Comma | uncommon | Hit-twice attacks hit once. | Comma Splice | status |

## 6. Statuses: your own pressure
| Item | Tier | What it does | Why | Sim |
|---|---|---|---|---|
| Full Stop | uncommon | The foe skips its next move, once a foe. | A stun on demand. | status |
| Smudge | common | Ink the foe: it takes 2 at the start of each of its next 3 turns. | Slow damage over time. | status |
| Blotter | common | Turn a vowel into block worth twice its points. | The old Ward, as utility. | status |
| Weaken | common | The foe's next attack hits 30% softer. | Gentle defence. | status |
| Footnote | uncommon | Your next word also gives you block equal to half its damage. | Offence turns into defence. | status |
| Margin | uncommon | One word this turn ignores Muffle and red pen. | A universal answer, once. | status |
| Encore | rare | Repeat your last word's damage at half strength. | Rewards big words twice. | dmg |
| Hyphen | rare | Your next two words count as one for the length bonus. | Two 3-letter words become a +7 strike. | meta |

## 7. Edge helpers (work with the day's edge)
| Item | Tier | What it does | Edge | Sim |
|---|---|---|---|---|
| Rhyming Dictionary | uncommon | Shows which of your words rhyme with the last one. | Rhyme | n/a (UI) |
| Tuning Fork | common | Your next word counts as alliterating. | Alliteration | meta |
| Lens | uncommon | Your next word counts as a palindrome (it stuns). | Mirror | meta |
| Metronome | common | Long Sentence charges twice as fast. | Long Sentence | meta |
| Day Letter Stamp | common | One tile becomes today's letter. | Letter of the Day | ready |

## Suggested round 4 trial (twelve items, two from each family)
- **Damage tricks:** Chisel, Carve
- **Hand shaping:** Comb, Fold
- **Draws:** Inkwell, Satchel
- **Rerolls:** Shake, Haggle
- **Answering foes:** Eraser, Paper Cut
- **Your own pressure:** Full Stop, Smudge

## Work needed before the trial
1. **Engine hooks for damage on use, statuses and seeded draws.** Port each to the page only once it earns a tier.
2. **A fair planner for draws and rerolls.** Score each choice by averaging 8 to 16 sampled outcomes from a different random stream, instead of the real seeded result. Otherwise the bot cheats.
3. **Passives** like Earplugs and Loaded Dice need a "held" kind that never spends a charge.
4. **Status items need foe-mix analysis:** report lift against each foe, not just overall, because their value depends on who you face.
