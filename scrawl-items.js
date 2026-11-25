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
  },
  {
   "id": "soften",
   "name": "Soften",
   "tier": "common",
   "kind": "choose",
   "uses": 1,
   "desc": "A consonant becomes any vowel you like.",
   "target": {
    "type": "consonant",
    "msg": "Consonants only"
   },
   "effect": {
    "options": {
     "letters": "aeiou"
    }
   },
   "from": "2026-11-22"
  },
  {
   "id": "scribble",
   "name": "Scribble",
   "tier": "uncommon",
   "kind": "choose",
   "uses": 1,
   "desc": "A consonant becomes any of E T A O I N S R H L.",
   "target": {
    "type": "consonant",
    "msg": "Consonants only"
   },
   "effect": {
    "options": {
     "letters": "etaoinsrhl"
    }
   },
   "from": "2026-11-22"
  },
  {
   "id": "lunge",
   "name": "Lunge",
   "tier": "uncommon",
   "kind": "morph",
   "uses": 1,
   "desc": "Three steps on: B→E, X→A.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "shift": 3
   },
   "from": "2026-11-22"
  },
  {
   "id": "recoil",
   "name": "Recoil",
   "tier": "uncommon",
   "kind": "morph",
   "uses": 1,
   "desc": "Three steps back: E→B, A→X.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "shift": -3
   },
   "from": "2026-11-22"
  },
  {
   "id": "triplicate",
   "name": "Triplicate",
   "tier": "uncommon",
   "kind": "make",
   "perFight": 1,
   "desc": "A tile becomes three: itself and two copies, once a foe.",
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
     },
     {
      "copy": true
     }
    ]
   },
   "from": "2026-11-22"
  },
  {
   "id": "kin",
   "name": "Kin",
   "tier": "rare",
   "kind": "pair",
   "uses": 1,
   "desc": "A tile takes the letter of another of its kind, vowel to vowel or consonant to consonant.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "copyFrom": true,
    "sameKind": true
   },
   "from": "2026-11-22"
  },
  {
   "id": "bloom",
   "name": "Bloom",
   "tier": "uncommon",
   "kind": "make",
   "uses": 1,
   "desc": "A vowel becomes two of itself.",
   "target": {
    "type": "vowel",
    "msg": "Vowels only"
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
   },
   "from": "2026-11-22"
  },
  {
   "id": "dial",
   "name": "Dial",
   "tier": "uncommon",
   "kind": "choose",
   "uses": 2,
   "desc": "One step either way, your pick: C→B or C→D (×2).",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "options": {
     "steps": [
      -1,
      1
     ]
    }
   },
   "from": "2026-11-22"
  },
  {
   "id": "spin",
   "name": "Spin",
   "tier": "uncommon",
   "kind": "choose",
   "uses": 2,
   "desc": "Turn or flip it by shape, your pick, twice a turn: b d p q · n u · m w · s z · h y.",
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
   },
   "from": "2026-11-22"
  },
  {
   "id": "plural",
   "name": "Plural",
   "tier": "common",
   "kind": "make",
   "uses": 1,
   "desc": "A tile sprouts an S beside it.",
   "target": {
    "type": "any"
   },
   "effect": {
    "make": [
     {
      "self": true
     },
     {
      "letter": "s"
     }
    ]
   },
   "from": "2026-11-22"
  },
  {
   "id": "wye",
   "name": "Wye",
   "tier": "common",
   "kind": "choose",
   "uses": 1,
   "desc": "A vowel becomes any of A E I O U Y.",
   "target": {
    "type": "vowel",
    "msg": "Vowels only"
   },
   "effect": {
    "options": {
     "letters": "aeiouy"
    }
   },
   "from": "2026-11-22"
  },
  {
   "id": "resound",
   "name": "Resound",
   "tier": "common",
   "kind": "choose",
   "uses": 2,
   "desc": "A vowel becomes any vowel you like, twice a turn.",
   "target": {
    "type": "vowel",
    "msg": "Vowels only"
   },
   "effect": {
    "options": {
     "letters": "aeiou"
    }
   },
   "from": "2026-11-22"
  },
  {
   "id": "inkwell",
   "name": "Inkwell",
   "tier": "common",
   "kind": "draw",
   "uses": 1,
   "desc": "Draw a tile.",
   "effect": {
    "draw": {
     "n": 1,
     "pool": "any"
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "pouch",
   "name": "Vowel Pouch",
   "tier": "common",
   "kind": "draw",
   "uses": 1,
   "desc": "Draw a vowel.",
   "effect": {
    "draw": {
     "n": 1,
     "pool": "vowel"
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "lucky",
   "name": "Lucky Letter",
   "tier": "common",
   "kind": "draw",
   "uses": 1,
   "desc": "Draw one of R S T L N E.",
   "effect": {
    "draw": {
     "n": 1,
     "pool": "rstlne"
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "polish",
   "name": "Polish",
   "tier": "common",
   "kind": "reroll",
   "uses": 2,
   "desc": "Reroll a tile into one of E T A O I N S R H L, twice a turn.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "reroll": {
     "pool": "etaoinsrhl"
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "ember",
   "name": "Ember",
   "tier": "common",
   "kind": "morph",
   "uses": 1,
   "desc": "A tile catches fire: 🔥 Flaming, +4 damage.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "fx": "fire"
   },
   "from": "2026-11-27"
  },
  {
   "id": "suffix",
   "name": "Suffix",
   "tier": "uncommon",
   "kind": "affix",
   "perFight": 1,
   "desc": "Pop a random suffix as new tiles, once a foe: -ING, -ED, -ER, -EST or -LY.",
   "effect": {
    "affix": {
     "list": [
      "ing",
      "ed",
      "er",
      "est",
      "ly"
     ]
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "prefix",
   "name": "Prefix",
   "tier": "uncommon",
   "kind": "affix",
   "perFight": 1,
   "desc": "Pop a random prefix as new tiles, once a foe: RE-, UN-, DE-, IN- or PRE-.",
   "effect": {
    "affix": {
     "list": [
      "re",
      "un",
      "de",
      "in",
      "pre"
     ]
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "gild",
   "name": "Gild",
   "tier": "uncommon",
   "kind": "morph",
   "perFight": 2,
   "desc": "A tile turns ✨ Gilded, worth double, twice a foe.",
   "target": {
    "type": "notBlank",
    "msg": "Not on a blank"
   },
   "effect": {
    "fx": "gold"
   },
   "from": "2026-11-27"
  },
  {
   "id": "grabbag",
   "name": "Grab Bag",
   "tier": "uncommon",
   "kind": "affix",
   "perFight": 1,
   "desc": "Pop a random 3-letter word as new tiles, once a foe.",
   "effect": {
    "affix": {
     "list": [
      "art",
      "ore",
      "tea",
      "sea",
      "ear",
      "eat",
      "rat",
      "tan",
      "net",
      "toe"
     ]
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "exchange",
   "name": "Exchange",
   "tier": "uncommon",
   "kind": "socket",
   "uses": 1,
   "desc": "Socket: set a 3-letter word in it. It deals its points and you draw 4 tiles.",
   "effect": {
    "socket": {
     "len": 3,
     "dmg": 1,
     "draw": 4
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "glyph",
   "name": "Glyph",
   "tier": "rare",
   "kind": "socket",
   "uses": 1,
   "desc": "Socket: set a 3-letter word in it. It deals triple its points.",
   "effect": {
    "socket": {
     "len": 3,
     "dmg": 3
    }
   },
   "from": "2026-11-27"
  },
  {
   "id": "hyphen",
   "name": "Hyphen",
   "tier": "rare",
   "kind": "affix",
   "uses": 1,
   "desc": "Two random affixes on offer; pick one to pop as new tiles: RE- UN- DE- -ING -ED -ER -ES.",
   "effect": {
    "affix": {
     "list": [
      "re",
      "un",
      "de",
      "ing",
      "ed",
      "er",
      "es"
     ],
     "offer": 2
    }
   },
   "from": "2026-11-27"
  }
 ]
};