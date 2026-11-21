// Dungeon Scrawl items as data. scrawl.html and tools/scrawl_sim.py both read this file, so the game and the
// simulator can never disagree about what a trick does. Everything after "=" is strict JSON. Grammar: tools/README.md.
window.SCRAWL_ITEMS={
 "version": 1,
 "legacyOffers": [
  "nudge",
  "flip",
  "rotate",
  "vshift",
  "swap",
  "twin",
  "split",
  "inkblot"
 ],
 "items": [
  {
   "id": "nudge",
   "name": "Nudge",
   "tier": "common",
   "kind": "morph",
   "uses": 2,
   "desc": "One step on: B→C, Z→A.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "shift": 1
   }
  },
  {
   "id": "flip",
   "name": "Flip",
   "tier": "common",
   "kind": "morph",
   "uses": 1,
   "desc": "Mirror it: A↔Z, B↔Y, M↔N.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "mirror": true
   }
  },
  {
   "id": "rotate",
   "name": "Rotate",
   "kind": "morph",
   "uses": 1,
   "desc": "Turn it by its shape: b→d→p→q, n↔u, m↔w.",
   "target": {
    "type": "letters",
    "letters": "bdpqnumw",
    "msg": "Only b d p q n u m w"
   },
   "effect": {
    "map": {
     "b": "d",
     "d": "p",
     "p": "q",
     "q": "b",
     "n": "u",
     "u": "n",
     "m": "w",
     "w": "m"
    }
   }
  },
  {
   "id": "vshift",
   "name": "Vowel Shift",
   "kind": "morph",
   "uses": 2,
   "desc": "A→E→I→O→U→A.",
   "target": {
    "type": "vowel",
    "msg": "Vowels only"
   },
   "effect": {
    "map": {
     "a": "e",
     "e": "i",
     "i": "o",
     "o": "u",
     "u": "a"
    }
   }
  },
  {
   "id": "swap",
   "name": "Swap",
   "kind": "swap",
   "uses": 1,
   "desc": "Two tiles trade letters. Enchantments stay put.",
   "target": {
    "type": "any"
   },
   "effect": {
    "swap": true
   }
  },
  {
   "id": "twin",
   "name": "Twin",
   "tier": "rare",
   "kind": "make",
   "uses": 1,
   "desc": "Copy a tile (the copy has no enchantment).",
   "target": {
    "type": "any"
   },
   "effect": {
    "make": [
     {
      "self": true
     },
     {
      "copy": true
     }
    ]
   }
  },
  {
   "id": "split",
   "name": "Split",
   "kind": "make",
   "uses": 1,
   "desc": "A tile worth 4+ breaks into an E and an A.",
   "target": {
    "type": "minValue",
    "value": 4,
    "msg": "Only tiles worth 4+"
   },
   "effect": {
    "make": [
     {
      "letter": "e"
     },
     {
      "letter": "a"
     }
    ]
   }
  },
  {
   "id": "inkblot",
   "name": "Ink Blot",
   "kind": "morph",
   "perFight": 1,
   "desc": "Make a blank: any letter in a word, worth 0.",
   "target": {
    "type": "notBlank",
    "msg": "Already blank"
   },
   "effect": {
    "set": "?"
   }
  },
  {
   "id": "leap",
   "name": "Leap",
   "tier": "common",
   "kind": "morph",
   "uses": 1,
   "desc": "Two steps on: B→D, Y→A.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "shift": 2
   }
  },
  {
   "id": "slip",
   "name": "Slip",
   "tier": "common",
   "kind": "morph",
   "uses": 1,
   "desc": "One key right on a keyboard: Q→W, L→A, M→Z.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "map": {
     "q": "w",
     "w": "e",
     "e": "r",
     "r": "t",
     "t": "y",
     "y": "u",
     "u": "i",
     "i": "o",
     "o": "p",
     "p": "q",
     "a": "s",
     "s": "d",
     "d": "f",
     "f": "g",
     "g": "h",
     "h": "j",
     "j": "k",
     "k": "l",
     "l": "a",
     "z": "x",
     "x": "c",
     "c": "v",
     "v": "b",
     "b": "n",
     "n": "m",
     "m": "z"
    }
   }
  },
  {
   "id": "whisper",
   "name": "Whisper",
   "tier": "common",
   "kind": "morph",
   "uses": 2,
   "desc": "Voice swap: B↔P, D↔T, G↔K, F↔V, S↔Z, M↔N.",
   "target": {
    "type": "letters",
    "letters": "bpdtgkvfzsmn",
    "msg": "Only b p d t g k f v s z m n"
   },
   "effect": {
    "map": {
     "b": "p",
     "p": "b",
     "d": "t",
     "t": "d",
     "g": "k",
     "k": "g",
     "v": "f",
     "f": "v",
     "z": "s",
     "s": "z",
     "m": "n",
     "n": "m"
    }
   }
  },
  {
   "id": "upend",
   "name": "Upend",
   "tier": "common",
   "kind": "choose",
   "uses": 1,
   "desc": "Turn or flip it by shape, your pick: b d p q · n u · m w · s z · h y.",
   "target": {
    "type": "letters",
    "letters": "bdpqnumwszhy",
    "msg": "Only b d p q n u m w s z h y"
   },
   "effect": {
    "options": {
     "groups": [
      "bdpq",
      "nu",
      "mw",
      "sz",
      "hy"
     ]
    }
   }
  },
  {
   "id": "revowel",
   "name": "Revowel",
   "tier": "common",
   "kind": "choose",
   "uses": 1,
   "desc": "A vowel becomes any vowel you like.",
   "target": {
    "type": "vowel",
    "msg": "Vowels only"
   },
   "effect": {
    "options": {
     "letters": "aeiou"
    }
   }
  },
  {
   "id": "recast",
   "name": "Recast",
   "tier": "common",
   "kind": "choose",
   "perFight": 1,
   "desc": "A tile becomes any letter you like, once a foe.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "options": {
     "letters": "abcdefghijklmnopqrstuvwxyz"
    }
   }
  },
  {
   "id": "back",
   "name": "Back",
   "tier": "uncommon",
   "kind": "morph",
   "uses": 2,
   "desc": "One step back: C→B, A→Z.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "shift": -1
   }
  },
  {
   "id": "echo",
   "name": "Echo",
   "tier": "uncommon",
   "kind": "pair",
   "uses": 1,
   "desc": "A tile takes another tile's letter. Pick the tile to change, then the one to copy.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "copyFrom": true
   }
  },
  {
   "id": "sprout",
   "name": "Sprout",
   "tier": "uncommon",
   "kind": "make",
   "uses": 1,
   "desc": "A tile sprouts an E beside it.",
   "target": {
    "type": "any"
   },
   "effect": {
    "make": [
     {
      "self": true
     },
     {
      "letter": "e"
     }
    ]
   }
  },
  {
   "id": "double",
   "name": "Double",
   "tier": "uncommon",
   "kind": "make",
   "perFight": 2,
   "desc": "Copy a tile, twice a foe (the copy has no enchantment).",
   "target": {
    "type": "any"
   },
   "effect": {
    "make": [
     {
      "self": true
     },
     {
      "copy": true
     }
    ]
   }
  },
  {
   "id": "respell",
   "name": "Respell",
   "tier": "rare",
   "kind": "choose",
   "uses": 1,
   "desc": "A consonant becomes any consonant you like.",
   "target": {
    "type": "consonant",
    "msg": "Consonants only"
   },
   "effect": {
    "options": {
     "letters": "bcdfghjklmnpqrstvwxyz"
    }
   }
  },
  {
   "id": "mimic",
   "name": "Mimic",
   "tier": "rare",
   "kind": "pair",
   "uses": 2,
   "desc": "A tile takes the letter of another of its kind, vowel to vowel or consonant to consonant (×2).",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "copyFrom": true,
    "sameKind": true
   }
  }
 ]
};
