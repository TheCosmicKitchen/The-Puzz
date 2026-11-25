// Dungeon Scrawl: the Spellblade as a sword, its runes, and the holdover bag, as data. scrawl.html and
// tools/scrawl_sim.py both read this file. Everything after "=" is strict JSON. Grammar: tools/README.md ("The sword").
// From the "from" daily (endless and lab at once) the blade is a sword: slot 1 is the hilt (a word on it gives block),
// slot 2 the crossguard (double letter), slot 6 the tip (double word). Tiles go in any slot, so you can plan a word.
window.SCRAWL_BLADE={
 "from": "2026-11-27",
 "squares": ["hilt", "dl", null, null, null, "dw"],
 "hiltPer": 1,
 "foeHp": 2.4,
 "sockets": 3,
 "maxLevel": 3,
 "bagCap": 2,
 "runes": [
  {"id": "pommel", "name": "Pommel", "kind": "pommel", "per": [1, 2, 3],
   "desc": "A word on the hilt gives +{n} more block for every letter."},
  {"id": "parry", "name": "Parry", "kind": "parry", "per": [2, 3, 4],
   "desc": "When you end your turn, +{n} block for every tile you didn't use."},
  {"id": "bastion", "name": "Bastion", "kind": "bastion", "per": [5, 10, 15],
   "desc": "Block you don't need stays for your next turn, up to {n}."},
  {"id": "whet", "name": "Whetstone", "kind": "whet", "per": [1, 2, 3],
   "desc": "+{n} damage for every word you have already struck against this foe."},
  {"id": "reach", "name": "Long Edge", "kind": "reach", "per": [2, 3, 4],
   "desc": "+{n} damage for every letter past the third."},
  {"id": "flurry", "name": "Flurry", "kind": "flurry", "per": [3, 5, 7],
   "desc": "+{n} damage for every word you have already struck this turn."},
  {"id": "leech", "name": "Leech", "kind": "leech", "per": [1, 2, 3],
   "desc": "Heal {n} for every letter past the third."},
  {"id": "fuller", "name": "Fuller", "kind": "fuller", "per": [1, 2, 3],
   "levels": ["Slot 4 is a double letter.", "Slot 4 is a triple letter.", "Slot 4 is a triple letter and slot 5 a double letter."],
   "desc": "A groove down the blade: a bonus square of its own."}
 ]
};
