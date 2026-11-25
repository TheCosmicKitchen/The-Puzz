"""Dungeon Scrawl simulator: bots play thousands of runs so we can see whether the tricks matter.

The rules are a straight port of scrawl.html, random numbers included, so a seed here deals exactly what the page
deals: 'scrawl-2026-11-20' is that day's daily, 'endless-abcde' is scrawl.html#abcde.

Bots (none of them AI, just search):
  notools  Spellblade and Quill only. Never touches a trick.
  smart    Searches its tricks each turn and uses one only when it makes the turn better.
  eager    The tool lover: spends every trick charge it can, picking the best use each time, even when it hurts.

Each turn every bot finds its best play: which words to spell (in which order, for the edge), and what to Quill. The
turn is scored by damage, with a big bonus for a kill, plus block that will actually soak the foe's next hit,
healing you need, and stuns.

Usage:
  py tools/scrawl_sim.py report -n 2000            # everything below, then writes sim-out/report.md with findings
  py tools/scrawl_sim.py compare -n 2000            # the three bots on the same seeds, drafting at random
  py tools/scrawl_sim.py sweep -n 1000              # fixed kits: Quill + Nudge + Flip + each trick in turn
  py tools/scrawl_sim.py compare --days 2026-10-25:2027-10-24   # real daily seeds
  py tools/scrawl_sim.py replay endless-sim7 --bot smart        # one run, turn by turn
Results go to tools/sim-out/ as CSV (one row per run, one per turn, one per trick use) plus a summary on screen.
"""
import argparse, csv, math, os, random, re, sys, time, json
from collections import Counter, defaultdict
from datetime import date, timedelta
from itertools import combinations, product
from multiprocessing import Pool

SIM_VERSION = '1.8.0'   # bump on any change to rules, bots or scoring; see tools/README.md for the changelog
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
M = 0xFFFFFFFF

# ---------------------------------------------------------------- seeded random, identical to the page
def imul(a, b): return (a * b) & M
def hseed(s):
    h = (1779033703 ^ len(s)) & M
    for ch in s:
        h = imul(h ^ ord(ch), 3432918353)
        h = ((h << 13) & M) | (h >> 19)
    h = imul(h ^ (h >> 16), 2246822507)
    h = imul(h ^ (h >> 13), 3266489909)
    return (h ^ (h >> 16)) & M
def mulberry(a):
    st = [a & M]
    def r():
        st[0] = (st[0] + 0x6D2B79F5) & M; a = st[0]
        t = imul(a ^ (a >> 15), 1 | a)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & M) ^ t
        return ((t ^ (t >> 14)) & M) / 4294967296
    return r
def shuffle(r, a):
    a = list(a)
    for i in range(len(a) - 1, 0, -1):
        j = math.floor(r() * (i + 1)); a[i], a[j] = a[j], a[i]
    return a
def jsround(x): return math.floor(x + 0.5)

# ---------------------------------------------------------------- words
def load_words():
    src = open(os.path.join(ROOT, 'typeset-words.js'), encoding='utf8').read()
    out = set()
    for key in ('common', 'extra'):
        prev = ''
        for m in re.findall(r'[A-K][a-z]*', re.search(key + r':"([^"]*)"', src).group(1)):
            w = prev[:ord(m[0]) - 65] + m[1:]; out.add(w); prev = w
    return {w for w in out if len(w) >= 3}
WORDS = load_words()
ANAG = defaultdict(list)
for w in WORDS:
    if len(w) <= 6: ANAG[''.join(sorted(w))].append(w)
ABC = 'abcdefghijklmnopqrstuvwxyz'

# ---------------------------------------------------------------- rules (scrawl.html)
VAL = dict(a=1,b=3,c=3,d=2,e=1,f=4,g=3,h=3,i=1,j=8,k=5,l=2,m=3,n=1,o=1,p=3,q=10,r=1,s=1,t=1,u=2,v=5,w=4,x=8,y=3,z=9)
BAG = 'aaaaaaaaabbccddddeeeeeeeeeeeeffggghhiiiiiiiiijkllllmmnnnnnnooooooooppqrrrrrrssssttttttuuuuvvwwxyyz'
VOW = set('aeiou')
BAG_V = [c for c in BAG if c in VOW]; BAG_C = [c for c in BAG if c not in VOW]
FXK = ['fire', 'steel', 'gold', 'leaf']
HARD_L, AWK_L, FAIR_FROM = set('jqxz'), set('fkvwy'), '2026-11-21'   # fair draws start with this daily
BONUS_FROM = '2026-11-22'   # blade bonus squares start with this daily
HP_BOOST = 1.27   # page: HP_BOOST. Foes on bonus days get 27% more health (keeps the no-tricks win rate near 2 in 3)
def hp_boost(seed): return HP_BOOST if not re.fullmatch(r'scrawl-\d{4}-\d{2}-\d{2}', seed) or seed[7:] >= BONUS_FROM else 1
HAND, HP, MAXWORD = 6, 30, 6
WORD_BONUS = [0, 0, 0, 0, 2, 4, 7]
BLANK = '?'
ROT = dict(b='d', d='p', p='q', q='b', n='u', u='n', m='w', w='m'); VSH = dict(a='e', e='i', i='o', o='u', u='a')
VOICE = dict(b='p', p='b', d='t', t='d', g='k', k='g', v='f', f='v', z='s', s='z', m='n', n='m')
_KEYROWS = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
def _right_key(c): r = next(r for r in _KEYROWS if c in r); return r[(r.index(c) + 1) % len(r)]
def _shape(c): return next((g for g in ('bdpq', 'nu', 'mw', 'sz', 'hy') if c in g), None)
def _step(c, d): return chr((ord(c) - 97 + d + 26) % 26 + 97)
nudge = lambda c: chr((ord(c) - 97 + 1) % 26 + 97)
flip = lambda c: chr(25 - (ord(c) - 97) + 97)
# kind, uses per turn (or perFight), ok(tile), effect
def load_items():
    """The items, as data, from ../scrawl-items.js (the page reads the same file). Everything after '=' is strict JSON."""
    src = open(os.path.join(ROOT, 'scrawl-items.js'), encoding='utf8').read()
    body = src[src.index('=', src.index('window.SCRAWL_ITEMS')) + 1:].strip().rstrip(';')
    return json.loads(body)

def compile_item(r):
    """page: compileItem(r). Turns a data record into what the engine and planner call."""
    tg, e = r.get('target', {'type': 'any'}), r.get('effect', {})
    ty = tg['type']
    if ty == 'any': ok = lambda t: True
    elif ty == 'notBlank': ok = lambda t: t['ch'] != BLANK
    elif ty == 'vowel': ok = lambda t: t['ch'] in VOW
    elif ty == 'consonant': ok = lambda t: t['ch'] != BLANK and t['ch'] not in VOW
    elif ty == 'letters': ok = lambda t, L=tg['letters']: t['ch'] != BLANK and t['ch'] in L
    elif ty == 'minValue': ok = lambda t, v=tg['value']: t['ch'] != BLANK and VAL[t['ch']] >= v
    else: raise ValueError(f"{r['id']}: unknown target {ty}")
    T = dict(kind=r['kind'], ok=ok, name=r['name'], desc=r['desc'])
    for k in ('tier', 'uses', 'perFight', 'from'):
        if r.get(k): T[k] = r[k]
    kd = r['kind']
    if kd == 'morph':
        if 'shift' in e: T['to'] = lambda t, d=e['shift']: chr((ord(t['ch']) - 97 + d + 26) % 26 + 97)
        elif e.get('mirror'): T['to'] = lambda t: flip(t['ch'])
        elif 'map' in e: T['to'] = lambda t, m=e['map']: m[t['ch']]
        elif 'fx' in e: T['to'] = lambda t: t['ch']; T['fx'] = e['fx']   # enchant: the letter stays, the tile takes an enchantment
        else: T['to'] = lambda t, c=e['set']: c
    elif kd == 'draw': T.update(notile=True, random=True, draw=e['draw'])
    elif kd == 'reroll':
        T.update(random=True, reroll=e['reroll'])
        if e['reroll'].get('hand'): T['notile'] = True
    elif kd == 'affix': T.update(notile=True, random=True, affix=e['affix'])
    elif kd == 'socket': T.update(socket=e['socket'], random=bool(e['socket'].get('draw')))
    elif kd == 'choose':
        o = e['options']
        if 'groups' in o: T['options'] = lambda t, G=o['groups']: list(next(g for g in G if t['ch'] in g))
        elif 'steps' in o: T['options'] = lambda t, D=o['steps']: [chr((ord(t['ch']) - 97 + d + 26) % 26 + 97) for d in D]
        else: T['options'] = lambda t, L=o['letters']: list(L)
    elif kd == 'make':
        T['make'] = lambda t, M=e['make']: [(t['ch'], t.get('fx')) if m.get('self') else (t['ch'], None) if m.get('copy') else (m['letter'], None) for m in M]
    elif kd == 'pair':
        T['ordered'] = True
        T['pair'] = (lambda a, b: (b['ch'], b['ch']) if (a['ch'] in VOW) == (b['ch'] in VOW) else (a['ch'], b['ch'])) if e.get('sameKind') else (lambda a, b: (b['ch'], b['ch']))
    return T

BAG_ALL = list(BAG)
def pool_of(p, t=None):
    """page: poolOf. Letters a draw or reroll picks from, weighted like the bag ('same' = the tile's own kind)."""
    if p == 'same': return BAG_V if t['ch'] in VOW else BAG_C
    return {'any': BAG_ALL, 'vowel': BAG_V, 'consonant': BAG_C}.get(p) or list(p)
def new_tile(turns, made, ch, fx=None): return dict(id=f'm{turns}-{made}', ch=ch, fx=fx, crossed=False)
def draw_into(hand, d, r, made, turns):
    """page: drawInto. d = {n, pool}: n new tiles at the end of the hand."""
    hand = list(hand)
    for _ in range(d.get('n', 1)):
        p = pool_of(d.get('pool', 'any')); made += 1; hand.append(new_tile(turns, made, p[math.floor(r() * len(p))]))
    return hand, made
def apply_random(T, hand, ids, r, made, turns):
    """page: rollTrick. A draw, reroll or affix with its random stream r. Returns [(hand, made, label)]: one entry,
    or one per affix on offer when the player picks."""
    kd = T['kind']
    if kd == 'draw':
        h, m = draw_into(hand, T['draw'], r, made, turns); return [(h, m, None)]
    if kd == 'reroll':
        d = T['reroll']; h = list(hand)
        for i, t in enumerate(hand):
            if t['id'] in ids or (d.get('hand') and not t['crossed'] and T['ok'](t)):
                p = [c for c in pool_of(d.get('pool', 'same'), t) if c != t['ch']]
                h[i] = dict(t, ch=p[math.floor(r() * len(p))])
        return [(h, made, None)]
    if kd == 'affix':
        L = T['affix']['list']; n = T['affix'].get('offer', 1)
        opts = [L[math.floor(r() * len(L))]] if n == 1 else shuffle(r, L)[:n]
        out = []
        for a in opts:
            h, m = list(hand), made
            for ch in a: m += 1; h.append(new_tile(turns, m, ch))
            out.append((h, m, a))
        return out
    raise ValueError(kd)
def socket_effect(T, ts, muffle):
    """page: socketHit. What a word set in a socket does: (damage, block, heal) before the tiles' own enchantments."""
    s = T['socket']; p = sum(pts(t, muffle) for t in ts); fire = 4 * sum(t['fx'] == 'fire' for t in ts)
    return s.get('dmg', 0) * (p + fire), s.get('block', 0) * p, s.get('heal', 0)

ITEMS = load_items()
TOOLS = {'quill': dict(kind='quill', uses=1, ok=lambda t: t['ch'] not in VOW and t['ch'] != BLANK,
                       name='Quill', desc='Flick one consonant for its points.'),
         **{r['id']: compile_item(r) for r in ITEMS['items']}}
KIT_MAX, START = 4, ['quill', 'nudge', 'flip']
TRICKS = [k for k in TOOLS if k != 'quill']
LEGACY_OFFERS = ITEMS['legacyOffers']   # dailies before 21 Nov
ROSTER = [k for k in TOOLS if TOOLS[k].get('tier')]
LIVE_IDS = {r['id'] for r in ITEMS['items']}
LIVE_TRICKS = ROSTER[:]          # what the page offers now; every trial uses these as controls
TIERS_FROM = '2026-11-21'
IDEAS_LOADED = []
IDEA_RECORDS = {}   # ideas written as item records: their runs can be cached, since the record says all they do
LINEAGE = {}      # idea -> the trick it evolved from
ROUND_META = {}   # idea file -> its round, note and test list

def load_ideas(paths):
    """Add candidate tricks from idea files: .py files define IDEAS = {name: tool dict}; .json files hold item records
    in the scrawl-items.js grammar (what evolve writes), each with an optional "parent"."""
    for p in paths or []:
        if p.endswith('.json'):
            for r in json.load(open(p, encoding='utf8')):
                TOOLS[r['id']] = compile_item(r)
                if r['id'] not in TRICKS: TRICKS.append(r['id'])
                IDEAS_LOADED.append(r['id'])
                if r.get('parent'): LINEAGE[r['id']] = r['parent']
            ROUND_META[os.path.basename(p)] = dict(round=None, note='evolved', test=None)
            continue
        ns = dict(VAL=VAL, VOW=VOW, BLANK=BLANK, nudge=nudge, flip=flip, ROT=ROT, VSH=VSH)
        exec(open(p, encoding='utf8').read(), ns)
        ideas = dict(ns.get('IDEAS', {}))
        for r in ns.get('RECORDS', []):   # ideas written in the scrawl-items.js grammar, ready to paste into the roster
            ideas[r['id']] = compile_item(r); IDEA_RECORDS[r['id']] = r
            if r.get('parent'): LINEAGE[r['id']] = r['parent']
        for k, T in ideas.items():
            if k in LIVE_IDS:   # an old idea that later shipped under the same id: the live item wins
                print(f'  idea {k} in {os.path.basename(p)} is live now; using the live item', file=sys.stderr); continue
            TOOLS[k] = T
            if k not in TRICKS: TRICKS.append(k)
            IDEAS_LOADED.append(k)
        for k, parent in ns.get('PARENTS', {}).items(): LINEAGE[k] = parent
        ROUND_META[os.path.basename(p)] = dict(round=ns.get('ROUND'), note=ns.get('NOTE', ''), test=ns.get('TEST'))
EDGE_KEYS = ['rhyme', 'haiku', 'mirror', 'allit', 'twins', 'letter', 'longsent']
EDGE_MULT = dict(rhyme=2, haiku=2, allit=2, longsent=3)
EDGE_ADD = dict(twins=5, letter=6)
FOES = {
    'gremlin': dict(hp=20, moves=[dict(atk=9), dict(jumble=1, atk=5), dict(atk=12)]),
    'worm':    dict(hp=22, moves=[dict(nibble=1, atk=6), dict(atk=10), dict(nibble=1, atk=6)]),
    'hush':    dict(hp=22, moves=[dict(muffle=1, atk=5), dict(atk=12), dict(atk=7)]),
    'jacket':  dict(hp=23, moves=[dict(armor=8, atk=5), dict(atk=12), dict(armor=6, atk=7)]),
    'splice':  dict(hp=22, moves=[dict(atk=6, twice=1), dict(atk=9), dict(atk=6, twice=1)]),
    'editor':  dict(hp=32, moves=[dict(atk=12), dict(redpen=2, atk=6), dict(atk=14), dict(armor=8, atk=6)]),
}
FOE_HP_SCALE, FOE_ATK_SCALE = 1.22, 1.0
DEEP_KINDS = ['gremlin', 'worm', 'hush', 'jacket', 'splice']

def edge_on(edge, w, ctx):
    last = ctx['last']
    if edge == 'rhyme': return bool(last) and w != last and w[-2:] == last[-2:]
    if edge == 'haiku': return len(w) == 5
    if edge == 'mirror': return len(w) >= 3 and w == w[::-1]
    if edge == 'allit': return bool(last) and w != last and w[0] == last[0]
    if edge == 'twins': return re.search(r'(.)\1', w) is not None
    if edge == 'letter': return ctx['letter'] in w
    if edge == 'longsent': return ctx['charged']
def fill_word(raw):
    """spellWord(): the page fills blanks with the first letters (a..z) that make a word."""
    if len(raw) < 3: return None
    if BLANK not in raw: return raw if raw in WORDS else None
    holes = [i for i, c in enumerate(raw) if c == BLANK]
    if len(holes) > 2: return None
    arr = list(raw)
    for fill in product(ABC, repeat=len(holes)):
        for i, c in zip(holes, fill): arr[i] = c
        s = ''.join(arr)
        if s in WORDS: return s
    return None

class Game:
    """One run, following the page step for step. Tiles are dicts {id, ch, fx, crossed}."""
    def __init__(self, seed, kit=None, deep=False):
        r = mulberry(hseed(seed))
        two = shuffle(r, ['gremlin', 'worm', 'hush', 'jacket', 'splice'])[:2]
        er = mulberry(hseed(seed + '-edge'))
        self.seed = seed; self.deep = deep
        self.foes = []
        for i, k in enumerate(two + ['editor']):
            hp = jsround((FOES[k]['hp'] + i * 2) * FOE_HP_SCALE * hp_boost(seed))
            self.foes.append(dict(k=k, hp=hp, max=hp, block=0, mi=math.floor(r() * len(FOES[k]['moves']))))
        self.edge = EDGE_KEYS[math.floor(er() * len(EDGE_KEYS))]
        self.letter = 'bcdfghklmnprstw'[math.floor(er() * 15)]
        self.fi = self.turn = self.turns = 0; self.hp = HP; self.block = 0; self.hand = []; self.uses = {}; self.fight_uses = {}
        self.pending = {}; self.muffle = False; self.over = None; self.made = 0
        self.kit = list(kit) if kit else START[:]
        self.draft = None if kit else 0
        self.charge = 0; self.charged = False; self.last = None; self.stun = False
        self.log = []          # events for the replay printout
        self.start_fight()

    # page: offers(d)
    def roster(self):
        """page: rosterNow(). A tool with a "from" date joins the dailies on that day; endless gets it straight away."""
        m = re.fullmatch(r'scrawl-(\d{4}-\d{2}-\d{2})', self.seed)
        return [k for k in ROSTER if not TOOLS[k].get('from') or not m or m.group(1) >= TOOLS[k]['from']]
    def roll_bonus(self):
        """page: rollBonus(). Bonus squares on the blade, from the 22 Nov daily: DL / TL double or triple a letter, DW doubles the word."""
        b = [None] * 6
        if re.fullmatch(r'scrawl-\d{4}-\d{2}-\d{2}', self.seed) and self.seed[7:] < BONUS_FROM: return b
        r = mulberry(hseed(f'{self.seed}-bonus-{self.fi}-{self.turn}'))
        x = r(); t = 'dl' if x < .6 else 'tl' if x < .75 else 'dw'
        i = 2 + math.floor(r() * 4) if t == 'dw' else math.floor(r() * 6); b[i] = t
        if r() < .35:
            j = math.floor(r() * 6)
            if not b[j]: b[j] = 'dl' if r() < .75 else 'tl'
        return b
    def offers(self, d):
        """page: offers(d). Tiered from the 21 Nov daily: each offer rolls 65% common / 27% uncommon / 8% rare (rare +2 pts per 3 floors, max 25%)."""
        if re.fullmatch(r'scrawl-\d{4}-\d{2}-\d{2}', self.seed) and self.seed[7:] < TIERS_FROM:
            return [k for k in shuffle(mulberry(hseed(self.seed + '-draft-' + str(d))), LEGACY_OFFERS) if k not in self.kit][:3]
        r = mulberry(hseed(f'{self.seed}-armoury-{d}')); rare = min(.25, .08 + .02 * (d // 3)); out = []
        for _ in range(3):
            x = r(); tier = 'rare' if x < rare else 'uncommon' if x < rare + .27 else 'common'
            order = {'rare': ['rare', 'uncommon', 'common'], 'uncommon': ['uncommon', 'common', 'rare'], 'common': ['common', 'uncommon', 'rare']}[tier]
            for tr in order:
                pool = [k for k in self.roster() if TOOLS[k].get('tier') == tr and k not in self.kit and k not in out]
                if pool: out.append(pool[math.floor(r() * len(pool))]); break
        return out
    def grant(self, k):
        T = TOOLS[k]
        if 'perFight' in T: self.fight_uses[k] = T['perFight']
        else: self.uses[k] = T['uses']
    def take(self, k, give_up=None):
        """Draft: add k (room in the kit) or put it in place of give_up. k=None keeps the kit."""
        if k:
            if len(self.kit) < KIT_MAX: self.kit.append(k)
            else: self.kit[self.kit.index(give_up)] = k
            self.grant(k)
        self.draft = None

    def draw(self, n):
        r = mulberry(hseed(f'{self.seed}-hand-{self.fi}-{self.turn}'))
        nv = min(n - 1, 2 if r() < .55 else 3); out = []
        fair = not re.fullmatch(r'scrawl-\d{4}-\d{2}-\d{2}', self.seed) or self.seed[7:] >= FAIR_FROM
        for k in range(n):
            pool = BAG_V if k < nv else BAG_C
            if fair and k >= nv:   # page: fair draws, no consonant twice, one of JQXZ, one of FKVWY
                pool = [c for c in pool if not any(t['ch'] == c for t in out)]
                if any(t['ch'] in HARD_L for t in out): pool = [c for c in pool if c not in HARD_L]
                if any(t['ch'] in AWK_L for t in out): pool = [c for c in pool if c not in AWK_L]
            out.append(dict(id=f'{self.fi}-{self.turn}-{k}', ch=pool[math.floor(r() * len(pool))], fx=None, crossed=False))
        nfx = 0 if r() < .35 else (1 if r() < .7 else 2)
        for i in shuffle(r, range(len(out)))[:nfx]: out[i]['fx'] = FXK[math.floor(r() * 4)]
        return shuffle(r, out)
    def start_turn(self):
        self.turn += 1; self.turns += 1
        self.uses = {k: TOOLS[k]['uses'] for k in self.kit if 'uses' in TOOLS[k]}
        self.block = 0; self.rolls = 0; self.affixing = None; p = self.pending; self.muffle = bool(p.get('muffle'))
        self.hand = self.draw(HAND - (p.get('nibble') or 0)); self.bonus = self.roll_bonus()
        r = mulberry(hseed(f'{self.seed}-trick-{self.fi}-{self.turn}'))
        if p.get('jumble'):
            t = self.hand[math.floor(r() * len(self.hand))]; t['ch'] = 'qxzjkvwy'[math.floor(r() * 8)]
        if p.get('redpen'):
            for i in shuffle(r, range(len(self.hand)))[:p['redpen']]: self.hand[i]['crossed'] = True
        self.pending = {}
    def start_fight(self):
        self.fight_uses = {k: TOOLS[k]['perFight'] for k in self.kit if 'perFight' in TOOLS[k]}
        self.turn = 0; self.pending = {}; self.charge = 0; self.charged = False; self.last = None; self.stun = False
        self.start_turn()
    @property
    def foe(self): return self.foes[self.fi]
    def next_move(self):
        f = self.foe; mv = FOES[f['k']]['moves']; return mv[f['mi'] % len(mv)]
    def uses_left(self, k):
        return self.fight_uses.get(k, 0) if 'perFight' in TOOLS[k] else self.uses.get(k, 0)
    def tile(self, tid):
        for t in self.hand:
            if t['id'] == tid: return t
        raise KeyError(tid)

    def use_up(self, ts):
        blk = sum(6 for t in ts if t['fx'] == 'steel'); heal = sum(3 for t in ts if t['fx'] == 'leaf')
        ids = {t['id'] for t in ts}; self.hand = [t for t in self.hand if t['id'] not in ids]
        self.block += blk; was = self.hp; self.hp = min(HP, self.hp + heal)
        return blk, self.hp - was
    def hit_foe(self, n):
        f = self.foe; soak = min(f['block'], n); f['block'] -= soak; f['hp'] = max(0, f['hp'] - (n - soak)); return n - soak
    def use_tool(self, k, ids):
        """A trick or Quill on tile ids (two for Swap). Returns damage dealt (Quill) or 0."""
        T = TOOLS[k]; assert k in self.kit and self.uses_left(k) > 0 and not self.over and self.draft is None, (k, self.kit)
        choice = next((i[1:] for i in ids if i.startswith('=')), None); ids = [i for i in ids if not i.startswith('=')]
        assert not self.affixing
        ts = [self.tile(i) for i in ids]; assert all(not t['crossed'] and T['ok'](t) for t in ts), (k, ts)
        dealt = 0
        if T['kind'] == 'morph':
            ts[0]['ch'] = T['to'](ts[0])
            if 'fx' in T: ts[0]['fx'] = T['fx']
        elif T['kind'] in ('draw', 'reroll', 'affix'):
            assert T.get('notile') or len(ts) == 1, (k, ids)
            outs = apply_random(T, self.hand, ids, self.roll(), self.made, self.turns)
            if len(outs) > 1: self.affixing = (k, outs)   # the player picks one; see pick_affix
            else: self.hand, self.made = outs[0][0], outs[0][1]
        elif T['kind'] == 'socket':
            s = T['socket']; assert len(ts) == s.get('len', 3) and fill_word(''.join(t['ch'] for t in ts)), (k, ts)
            d, b, h = socket_effect(T, ts, self.muffle)
            self.use_up(ts); self.block += b; self.hp = min(HP, self.hp + h)
            if d: dealt = self.hit_foe(d)
            if s.get('draw'): self.hand, self.made = draw_into(self.hand, dict(n=s['draw'], pool='any'), self.roll(), self.made, self.turns)
        elif T['kind'] == 'choose':
            assert choice in T['options'](ts[0]), (k, choice); ts[0]['ch'] = choice
        elif T['kind'] == 'quill':
            t = ts[0]; dealt = self.hit_foe(pts(t, self.muffle) + (4 if t['fx'] == 'fire' else 0)); self.use_up([t])
        elif T['kind'] == 'make':
            at = self.hand.index(ts[0]); new = []
            for ch, fx in T['make'](ts[0]):
                self.made += 1; new.append(dict(id=f'm{self.turns}-{self.made}', ch=ch, fx=fx, crossed=False))
            self.hand[at:at + 1] = new
        elif T['kind'] == 'swap':
            a, b = ts; assert a is not b; a['ch'], b['ch'] = b['ch'], a['ch']
        elif T['kind'] == 'pair':
            a, b = ts; assert a is not b; a['ch'], b['ch'] = T['pair'](a, b)
        if 'perFight' in T: self.fight_uses[k] -= 1
        else: self.uses[k] -= 1
        self.after()
        return dealt
    def roll(self):
        """page: roll(). Each random trick use this turn gets its own stream, so a daily rolls the same for everyone (and Undo can't reroll)."""
        self.rolls += 1; return mulberry(hseed(f'{self.seed}-roll-{self.fi}-{self.turn}-{self.rolls}'))
    def pick_affix(self, i):
        """page: chooseAffix. Take affix number i of the ones on offer."""
        k, outs = self.affixing; self.affixing = None; self.hand, self.made = outs[i][0], outs[i][1]
    def strike(self, ids):
        assert len(ids) <= MAXWORD and not self.over and self.draft is None
        ts = [self.tile(i) for i in ids]; assert not any(t['crossed'] for t in ts)
        w = fill_word(''.join(t['ch'] for t in ts)); assert w, ''.join(t['ch'] for t in ts)
        dmg = word_damage(ts, self.muffle, self.bonus)
        on = edge_on(self.edge, w, dict(last=self.last, letter=self.letter, charged=self.charged))
        if on: dmg = dmg * EDGE_MULT.get(self.edge, 1) + EDGE_ADD.get(self.edge, 0)
        self.use_up(ts)
        if self.edge == 'longsent':
            if self.charged: self.charged = False
            self.charge += len(w)
            if self.charge >= 12: self.charge -= 12; self.charged = True
        if on and self.edge == 'mirror': self.stun = True
        self.last = w
        dealt = self.hit_foe(dmg); self.after()
        return w, dealt, on
    def after(self):
        if self.foe['hp'] > 0: return
        if self.fi == len(self.foes) - 1:
            if self.deep: self.foes.append(self.deep_foe(self.fi + 1))
            else: self.over = 'won'; return
        self.fi += 1; self.hp = min(HP, self.hp + 6); self.start_fight()
        if self.draft is not None or self.kit_fixed: return
        if self.offers(self.fi): self.draft = self.fi
    kit_fixed = False
    def deep_foe(self, i):
        """page: deepFoe(i), the endless descent. Every third foe is The Editor; each set of three hits 10% harder."""
        r = mulberry(hseed(f'{self.seed}-deep-{i}'))
        k = 'editor' if i % 3 == 2 else DEEP_KINDS[math.floor(r() * len(DEEP_KINDS))]
        hp = jsround((FOES[k]['hp'] + i * 2) * FOE_HP_SCALE * hp_boost(self.seed))
        return dict(k=k, hp=hp, max=hp, block=0, mi=math.floor(r() * len(FOES[k]['moves'])), ax=round(1 + 0.1 * (i // 3), 2))
    def end_turn(self):
        assert not self.over and self.draft is None
        m0 = self.next_move(); f = self.foe; f['block'] = 0
        m = {} if self.stun else m0
        if m.get('armor'): f['block'] += m['armor']
        a = jsround(m.get('atk', 0) * FOE_ATK_SCALE * f.get('ax', 1)); dmg = 0
        for _ in range(2 if m.get('twice') else 1 if a else 0):
            soak = min(self.block, a); self.block -= soak; dmg += a - soak
        self.hp = max(0, self.hp - dmg)
        self.pending = {k: m.get(k) for k in ('jumble', 'nibble', 'muffle', 'redpen')}; f['mi'] += 1
        self.stun = False
        if self.hp <= 0: self.over = 'lost'; return dmg
        self.start_turn(); return dmg

def pts(t, muffle):
    if t['ch'] == BLANK: return 0
    v = 0 if (muffle and t['ch'] in VOW) else VAL[t['ch']]
    return v * (2 if t['fx'] == 'gold' else 1)

# ---------------------------------------------------------------- the turn planner
KILL = 1000.0
WIDE_HAND, WIDE_WORDS = 8, 50   # hands over 8 tiles (only draws and affixes make them) plan with their 50 best words
def incoming(g):
    m = g.next_move(); a = jsround(m.get('atk', 0) * FOE_ATK_SCALE * g.foe.get('ax', 1)); return a * (2 if m.get('twice') else 1)

def word_damage(ts, muffle, bonus):
    """page: wordHit before the edge. Letters (with DL / TL squares) + length bonus + fire, then x2 if a DW square is used."""
    bonus = bonus or [None] * 6; mul = {'dl': 2, 'tl': 3}
    d = sum(pts(t, muffle) * mul.get(bonus[i], 1) for i, t in enumerate(ts)) + WORD_BONUS[len(ts)] + 4 * sum(t['fx'] == 'fire' for t in ts)
    return d * 2 if any(bonus[i] == 'dw' for i in range(len(ts))) else d

def words_for(hand, muffle, bonus=None):
    """Every word the hand can spell: list of (mask, ordered tile ids, actual word, base damage, steel, leaf)."""
    idx = [i for i, t in enumerate(hand) if not t['crossed']]
    out = []
    for n in range(3, min(MAXWORD, len(idx)) + 1):
        for combo in combinations(idx, n):
            ts = [hand[i] for i in combo]
            letters = [t['ch'] for t in ts if t['ch'] != BLANK]; nb = n - len(letters)
            if nb > 2: continue
            cands = set()
            if nb == 0: cands.update(ANAG.get(''.join(sorted(letters)), ()))
            else:
                for fill in combinations_with_rep(nb):
                    cands.update(ANAG.get(''.join(sorted(letters + list(fill))), ()))
            if not cands: continue
            steel = 6 * sum(t['fx'] == 'steel' for t in ts); leaf = 3 * sum(t['fx'] == 'leaf' for t in ts)
            mask = 0
            for i in combo: mask |= 1 << i
            seen = set()
            for w in sorted(cands):          # sorted: set order changes between processes, and ties must break the same way every run
                order = arrange(w, ts)
                if order is None: continue
                actual = fill_word(''.join(t['ch'] for t in order))
                if not actual or actual in seen: continue
                seen.add(actual); out.append((mask, [t['id'] for t in order], actual, word_damage(order, muffle, bonus), steel, leaf))
    return out
_CWR = {}
def combinations_with_rep(n):
    if n not in _CWR:
        from itertools import combinations_with_replacement
        _CWR[n] = list(combinations_with_replacement(ABC, n))
    return _CWR[n]
def arrange(w, ts):
    """Put tiles in the order that spells w (blanks where no tile has the letter)."""
    pool = list(ts); order = []
    for c in w:
        j = next((k for k, t in enumerate(pool) if t['ch'] == c), None)
        if j is None: j = next((k for k, t in enumerate(pool) if t['ch'] == BLANK), None)
        if j is None: return None
        order.append(pool.pop(j))
    return order

GREEDY_OPENERS = 3   # the quick bots try this many opening words, then take the best next word each time
def best_play(g, hand, uses_quill, acc=(0, 0, 0), greedy=False):
    """Best words (in order) and Quill for this hand, scored for this foe. acc = (damage, block, heal) already banked
    this turn by sockets in the plan. greedy (the quick bots): instead of every sequence of words, try the best few
    opening words and then always the best next one. Returns (value, plan, info)."""
    f = g.foe; need = f['hp'] + f['block']; inc = max(0, incoming(g) - g.block); missing = HP - g.hp
    ws = words_for(hand, g.muffle, getattr(g, 'bonus', None))
    if len(hand) > WIDE_HAND:   # draws and affixes make big hands: keep the strongest words so the search stays quick
        ws = sorted(ws, key=lambda x: (-x[3], x[2]))[:WIDE_WORDS]
    quills = [t for t in hand if not t['crossed'] and TOOLS['quill']['ok'](t)] if uses_quill else []
    best = [-1.0, None, None]
    def score(dmg, steel, leaf, stun, plan, words_on, charge):
        if dmg >= need: v = KILL + min(leaf, missing) * 0.8 - len(plan) * 0.01
        else: v = dmg + min(steel, inc if not stun else 0) + min(leaf, missing) * 0.8 + (inc if stun else 0) + charge * 0.3
        if v > best[0]: best[:] = [v, list(plan), dict(dmg=dmg, edges=words_on)]
    def go(used, ctx, dmg, steel, leaf, stun, plan, words_on):
        # finish with a Quill on the best spare consonant (or none)
        if dmg < need:
            for t in quills:
                bit = 1 << hand.index(t)
                if used & bit: continue
                q = pts(t, g.muffle) + (4 if t['fx'] == 'fire' else 0)
                score(dmg + q, steel + (6 if t['fx'] == 'steel' else 0), leaf + (3 if t['fx'] == 'leaf' else 0), stun,
                      plan + [('quill', [t['id']])], words_on, ctx['charge'])
        score(dmg, steel, leaf, stun, plan, words_on, ctx['charge'])
        if dmg >= need: return
        cands = []
        for mask, ids, w, base, st, lf in ws:
            if used & mask: continue
            on = edge_on(g.edge, w, ctx); d = base * EDGE_MULT.get(g.edge, 1) + EDGE_ADD.get(g.edge, 0) if on else base
            cands.append((d + min(st, inc) + 0.8 * min(lf, missing), mask, ids, w, d, st, lf, on))
        if greedy:
            cands.sort(key=lambda c: -c[0])   # stable: ties keep word order
            cands = cands[:GREEDY_OPENERS if not words_on and not any(p[0] == 'word' for p in plan) else 1]
        for _, mask, ids, w, d, st, lf, on in cands:
            c2 = dict(ctx); c2['last'] = w
            if g.edge == 'longsent':
                if c2['charged']: c2['charged'] = False
                c2['charge'] += len(w)
                if c2['charge'] >= 12: c2['charge'] -= 12; c2['charged'] = True
            go(used | mask, c2, dmg + d, steel + st, leaf + lf, stun or (on and g.edge == 'mirror'),
               plan + [('word', ids, w)], words_on + int(on))
    go(0, dict(last=g.last, letter=g.letter, charged=g.charged, charge=g.charge), acc[0], acc[1], acc[2], False, [], 0)
    return best

SAMPLES = 8   # outcomes the planner imagines for a random trick, from its own stream: it never peeks at the real roll
QUICK_SAMPLES = 4   # the quick bots imagine fewer
QUICK = {'quick': 'smart', 'qeager': 'eager'}   # heuristic bots: the same trick search, greedy words, fewer imagined rolls
def chance(g, k, T, hand, ids, made, acc, n=SAMPLES):
    """The outcomes a bot can expect from a random trick: SAMPLES lists of [(hand, made, acc)] choices."""
    out = []
    r = mulberry(hseed(f'{g.seed}-plan-{g.fi}-{g.turn}-{g.rolls}-{k}-{",".join(ids)}'))
    for _ in range(n):
        if T['kind'] == 'socket':
            h, m = draw_into(hand, dict(n=T['socket']['draw'], pool='any'), r, made, g.turns); out.append([(h, m, acc)])
        else: out.append([(h, m, acc) for h, m, _ in apply_random(T, hand, ids, r, made, g.turns)])
    return out

QUICK_KEEP = 5   # the quick bots fully weigh only this many single-tile changes per trick (the best by one_change)
def one_change(hand):
    """Heuristic for the quick bots: {(tile index, letter): rough value of the best word that tile could join as that letter}.
    One pass over the tile combinations with that tile as a wildcard, instead of a full word search per candidate hand."""
    idx = [i for i, t in enumerate(hand) if not t['crossed']]; best = {}
    for n in range(3, min(MAXWORD, len(idx)) + 1):
        for combo in combinations(idx, n):
            for i in combo:
                rest = [hand[j]['ch'] for j in combo if j != i]
                if BLANK in rest: continue
                base = sum(VAL[c] for c in rest) + WORD_BONUS[n]
                for c in ABC:
                    if ''.join(sorted(rest + [c])) in ANAG:
                        v = base + VAL[c]
                        if v > best.get((i, c), 0): best[(i, c)] = v
    return best

def prune(hand, moves):
    """Keep each trick's QUICK_KEEP most promising single-tile changes (by one_change); everything else stays."""
    groups = defaultdict(list); keep = []
    for m in moves:
        k, ids, h2 = m[0], m[1], m[2]
        if h2 is not None and len(ids) >= 1 and TOOLS[k]['kind'] in ('morph', 'choose') and len(h2) == len(hand): groups[k].append(m)
        else: keep.append(m)
    if not groups: return moves
    oc = one_change(hand); pos = {t['id']: i for i, t in enumerate(hand)}
    for k, ms in groups.items():
        if len(ms) <= QUICK_KEEP: keep += ms; continue
        def proxy(m):
            i = pos[m[1][0]]; return oc.get((i, m[2][i]['ch']), 0)
        keep += sorted(ms, key=lambda m: -proxy(m))[:QUICK_KEEP]   # stable sort: ties keep move order
    return keep

def tool_moves(g, hand, uses, made, acc=(0, 0, 0), n=SAMPLES):
    """Every way to spend one trick charge on this hand: (tool, ids, new hand, new uses, new made, new acc, samples).
    samples is None for a sure thing; for a random trick it holds the imagined outcomes and the hand is unknown."""
    out = []
    for k, n in uses.items():
        if n <= 0 or k == 'quill': continue
        T = TOOLS[k]; nu = dict(uses); nu[k] = n - 1
        if T.get('notile'):
            out.append((k, [], None, nu, made, acc, chance(g, k, T, hand, [], made, acc, n))); continue
        if T['kind'] == 'socket':
            L = T['socket'].get('len', 3)
            for mask, ids, w, base, st, lf in words_for([t for t in hand if T['ok'](t)], g.muffle):
                if len(ids) != L: continue
                ts = [next(t for t in hand if t['id'] == i) for i in ids]
                d, b, h = socket_effect(T, ts, g.muffle)
                a2 = (acc[0] + d, acc[1] + b + st, acc[2] + h + lf); h2 = [t for t in hand if t['id'] not in ids]
                if T['random']: out.append((k, ids, None, nu, made, a2, chance(g, k, T, h2, ids, made, a2, n)))
                else: out.append((k, ids, h2, nu, made, a2, None))
            continue
        for i, t in enumerate(hand):
            if t['crossed'] or not T['ok'](t): continue
            if T['kind'] == 'reroll':
                out.append((k, [t['id']], None, nu, made, acc, chance(g, k, T, hand, [t['id']], made, acc, n)))
            elif T['kind'] == 'morph':
                nt = dict(t); nt['ch'] = T['to'](t)
                if 'fx' in T: nt['fx'] = T['fx']
                if nt['ch'] == t['ch'] and nt['fx'] == t['fx']: continue
                out.append((k, [t['id']], hand[:i] + [nt] + hand[i + 1:], nu, made, acc, None))
            elif T['kind'] == 'make':
                m = made; new = []
                for ch, fx in T['make'](t):
                    m += 1; new.append(dict(id=f'm{g.turns}-{m}', ch=ch, fx=fx, crossed=False))
                out.append((k, [t['id']], hand[:i] + new + hand[i + 1:], nu, m, acc, None))
            elif T['kind'] == 'swap':
                for j in range(i + 1, len(hand)):
                    u = hand[j]
                    if u['crossed'] or u['ch'] == t['ch']: continue
                    h2 = list(hand); h2[i] = dict(t, ch=u['ch']); h2[j] = dict(u, ch=t['ch'])
                    out.append((k, [t['id'], u['id']], h2, nu, made, acc, None))
            elif T['kind'] == 'choose':
                for c in T['options'](t):
                    if c == t['ch']: continue
                    nt = dict(t); nt['ch'] = c
                    out.append((k, [t['id'], '=' + c], hand[:i] + [nt] + hand[i + 1:], nu, made, acc, None))
            elif T['kind'] == 'pair':
                for j, u in enumerate(hand):
                    if j == i or u['crossed'] or not T['ok'](u) or (j < i and not T.get('ordered')): continue
                    ca, cb = T['pair'](t, u)
                    if ca == t['ch'] and cb == u['ch']: continue
                    h2 = list(hand); h2[i] = dict(t, ch=ca); h2[j] = dict(u, ch=cb)
                    out.append((k, [t['id'], u['id']], h2, nu, made, acc, None))
    return out

def plan_turn(g, bot, beam=5):
    """The whole turn for a bot: trick uses first, then words and Quill. Returns (plan, base value, final value, path, replan).
    A random trick is a chance node: it is worth the average of its imagined outcomes, and it ends the plan (replan=True),
    so the bot rolls for real, looks at what it got, and plans the rest of the turn again."""
    greedy = bot in QUICK; bot = QUICK.get(bot, bot); n = QUICK_SAMPLES if greedy else SAMPLES
    uses = {k: g.uses_left(k) for k in g.kit if k != 'quill'}
    qok = g.uses_left('quill') > 0
    cache = {}
    def val(hand, acc=(0, 0, 0)):
        key = (tuple((t['id'], t['ch'], t['fx'], t['crossed']) for t in hand), acc)
        if key not in cache: cache[key] = best_play(g, hand, qok, acc, greedy)
        return cache[key]
    def ev(samples):   # each sample: the choices it offers; the bot takes the best one
        return sum(max(val(h, a)[0] for h, _, a in s) for s in samples) / len(samples)
    base = val(g.hand)
    if bot == 'notools' or not any(uses.values()):
        return base[1], base[0], base[0], [], False
    if bot == 'smart':
        # beam search over trick sequences; keep the best turn found anywhere along the way
        best = (base[0], [], g.hand, (0, 0, 0), False)
        frontier = [(base[0], [], g.hand, uses, g.made, (0, 0, 0))]
        while frontier:
            nxt = []
            for v, path, hand, us, made, acc in frontier:
                ms = tool_moves(g, hand, us, made, acc, n)
                for k, ids, h2, u2, m2, a2, samples in (prune(hand, ms) if greedy else ms):
                    if samples is not None:   # random: worth its average, and the plan stops here
                        v2 = ev(samples); p2 = path + [(k, ids, v2 - v)]
                        if v2 > best[0] + 1e-9: best = (v2, p2, None, None, True)
                        continue
                    v2 = val(h2, a2)[0]; p2 = path + [(k, ids, v2 - v)]
                    nxt.append((v2, p2, h2, u2, m2, a2))
                    if v2 > best[0] + 1e-9: best = (v2, p2, h2, a2, False)
            nxt.sort(key=lambda x: -x[0]); frontier = nxt[:beam]
        v, path, hand, acc, rnd = best
        tail = [] if rnd else val(hand, acc)[1]
        return [('tool', k, ids) for k, ids, _ in path] + tail, base[0], v, path, rnd
    if bot == 'eager':
        # spend every charge: each step takes the best-scoring single use, even if the turn gets worse
        hand, us, made, acc, path, v = g.hand, uses, g.made, (0, 0, 0), [], base[0]
        while True:
            moves = tool_moves(g, hand, us, made, acc, n)
            if greedy: moves = prune(hand, moves)
            if not moves: break
            scored = [(ev(s) if s is not None else val(h2, a2)[0], k, ids, h2, u2, m2, a2, s) for k, ids, h2, u2, m2, a2, s in moves]
            v2, k, ids, hand, us, made, acc, s = max(scored, key=lambda x: x[0])
            path.append((k, ids, v2 - v)); v = v2
            if s is not None: return [('tool', k, ids) for k, ids, _ in path], base[0], v, path, True
        return [('tool', k, ids) for k, ids, _ in path] + val(hand, acc)[1], base[0], v, path, False
    raise ValueError(bot)

# ---------------------------------------------------------------- drafting
def draft_choice(g, policy, rng):
    """Returns (take, give_up) for the current draft. policy: random | keep | first | a comma list of preferred tricks."""
    offers = g.offers(g.draft)
    if not offers: return None, None
    if policy == 'keep' and len(g.kit) >= KIT_MAX: return None, None
    if policy in ('random', 'keep'): take = rng.choice(offers)
    elif policy == 'first': take = offers[0]
    else:
        pref = policy.split(','); ranked = sorted(offers, key=lambda k: pref.index(k) if k in pref else 99); take = ranked[0]
    if len(g.kit) < KIT_MAX: return take, None
    mine = [k for k in g.kit if k != 'quill']
    if policy == 'random':
        choice = rng.choice(mine + [None])          # one in four: keep the kit
        return (take, choice) if choice else (None, None)
    pref = policy.split(',') if policy not in ('first',) else TRICKS
    worst = max(mine, key=lambda k: pref.index(k) if k in pref else 99)
    if (pref.index(take) if take in pref else 99) < (pref.index(worst) if worst in pref else 99): return take, worst
    return None, None

# ---------------------------------------------------------------- one run
def play(seed, bot, draft='random', kit=None, beam=5, verbose=False, deep=False):
    g = Game(seed, kit=kit, deep=deep)
    if kit: g.kit_fixed = True
    rng = random.Random(seed + '|' + bot)
    run = dict(seed=seed, bot=bot, edge=g.edge, foes='+'.join(f['k'] for f in g.foes), draft=draft)
    turns, uses_log = [], []
    dmg_total = edge_hits = words = 0; best_word = ('', 0); picks = []
    say = print if verbose else (lambda *a: None)
    say(f'== {seed}  bot={bot}  edge={g.edge}{" ("+g.letter+")" if g.edge=="letter" else ""}  foes={run["foes"]}')
    guard = 0
    while not g.over and guard < (5000 if deep else 200):
        guard += 1
        if g.draft is not None:
            if bot == 'notools': g.take(None)
            else:
                take, give = draft_choice(g, draft, rng)
                if take: picks.append(take)
                say(f'   draft {g.draft}: offers {g.offers(g.draft)} -> {take or "keep"}{" for "+give if give else ""}')
                g.take(take, give)
            continue
        fi, turn, hp0 = g.fi, g.turn, g.hp
        hand_txt = ' '.join(t['ch'].upper() + ('*' if t['crossed'] else '') + ({'fire':'^','steel':'#','gold':'$','leaf':'+'}.get(t['fx'],'')) for t in g.hand)
        dealt_turn = 0; spelled = []; path = []; v0 = None
        while True:   # a random trick ends the plan: roll it, then plan the rest of the turn with what came up
            plan, b0, v1, part, replan = plan_turn(g, bot, beam)
            if v0 is None: v0 = b0
            path += part
            for step in plan:
                if g.over or g.fi != fi or g.draft is not None: break
                if step[0] == 'tool':
                    dealt_turn += g.use_tool(step[1], step[2])
                    if g.affixing:   # several affixes on offer: take the one that makes the best turn
                        qok = g.uses_left('quill') > 0; outs = g.affixing[1]
                        g.pick_affix(max(range(len(outs)), key=lambda i: best_play(g, outs[i][0], qok, greedy=bot in QUICK)[0]))
                elif step[0] == 'quill': dealt_turn += g.use_tool('quill', step[1])
                else:
                    w, d, on = g.strike(step[1]); dealt_turn += d; words += 1; edge_hits += on; spelled.append(w.upper() + ('!' if on else ''))
                    if d > best_word[1]: best_word = (w, d)
            if not replan or g.over or g.fi != fi or g.draft is not None: break
        tool_names = [k for k, _, _ in path]
        killed = g.fi != fi or g.over == 'won'
        for k, ids, gain in path:
            uses_log.append(dict(seed=seed, bot=bot, kit='+'.join(x for x in g.kit if x != 'quill'), tool=k, gain=round(gain, 2), killed=int(killed), fight=fi, edge=g.edge))
        dmg_total += dealt_turn
        took = 0
        if not g.over and g.fi == fi and g.draft is None: took = g.end_turn()
        lift = (min(v1, KILL) - min(v0, KILL)) if v1 < KILL or v0 < KILL else 0
        turns.append(dict(seed=seed, bot=bot, kit='+'.join(x for x in g.kit if x != 'quill'), fight=fi, turn=turn, hand=hand_txt, tools='+'.join(tool_names), lift=round(v1 - v0, 2),
                          kill_by_tools=int(v1 >= KILL > v0), dealt=dealt_turn, took=took, hp=g.hp, words=' '.join(spelled), edge=g.edge))
        say(f'   foe {fi+1} t{turn}: [{hand_txt}] {"tools " + ",".join(tool_names) + " " if tool_names else ""}'
            f'{" ".join(spelled) or "-"} dealt {dealt_turn}{" KILL" if killed else ""} | took {took} hp {g.hp}')
    run.update(win=int(g.over == 'won'), reached=g.fi + 1, hp=g.hp if g.over == 'won' else 0, turns=g.turns, dmg=dmg_total,
               words=words, edge_hits=edge_hits, best=best_word[0], best_dmg=best_word[1], kit='+'.join(k for k in g.kit if k != 'quill'),
               picks='+'.join(picks), tool_uses=len(uses_log), lift_turns=sum(t['lift'] > 0.01 for t in turns),
               tool_kills=sum(t['kill_by_tools'] for t in turns))
    say(f'== {"WON" if run["win"] else "lost"} hp {run["hp"]} turns {g.turns} kit {run["kit"]}')
    return run, turns, uses_log

def _job(a): return play(*a)

# ---------------------------------------------------------------- reports
def pct(n, d): return f'{100*n/d:5.1f}%' if d else '   - '
def table(rows, cols, title):
    print('\n' + title)
    w = [max(len(str(c)), *(len(str(r.get(c, ''))) for r in rows)) for c in cols]
    print('  ' + '  '.join(str(c).ljust(x) for c, x in zip(cols, w)))
    for r in rows: print('  ' + '  '.join(str(r.get(c, '')).ljust(x) for c, x in zip(cols, w)))

def summarize(runs, turns, uses, label):
    bots = sorted({r['bot'] for r in runs}, key=['notools', 'smart', 'eager'].index if all(b in ('notools','smart','eager') for b in {r['bot'] for r in runs}) else str)
    rows = []
    for b in bots:
        R = [r for r in runs if r['bot'] == b]; T = [t for t in turns if t['bot'] == b]; n = len(R)
        rows.append(dict(bot=b, runs=n, win=pct(sum(r['win'] for r in R), n), reach_editor=pct(sum(r['reached'] >= 3 for r in R), n),
                         avg_turns=f"{sum(r['turns'] for r in R)/n:.1f}", hp_left_wins=f"{sum(r['hp'] for r in R)/max(1,sum(r['win'] for r in R)):.1f}",
                         dmg_turn=f"{sum(t['dealt'] for t in T)/max(1,len(T)):.1f}", edge_rate=pct(sum(r['edge_hits'] for r in R), sum(r['words'] for r in R)),
                         tool_turns=pct(sum(1 for t in T if t['tools']), len(T)), helped=pct(sum(t['lift'] > 0.01 for t in T), len(T)),
                         tool_kills=f"{sum(r['tool_kills'] for r in R)/n:.2f}"))
    table(rows, ['bot', 'runs', 'win', 'reach_editor', 'avg_turns', 'hp_left_wins', 'dmg_turn', 'edge_rate', 'tool_turns', 'helped', 'tool_kills'],
          f'== {label}: bots ==   helped = turns where tricks made the turn better; tool_kills = kills per run only tricks made possible')
    # paired: same seed, notools vs each tool bot
    by = defaultdict(dict)
    for r in runs: by[r['seed']][r['bot']] = r['win']
    for b in bots:
        if b == 'notools' or not any('notools' in v for v in by.values()): continue
        both = [v for v in by.values() if 'notools' in v and b in v]
        saved = sum(v[b] and not v['notools'] for v in both); cost = sum(v['notools'] and not v[b] for v in both)
        print(f'  {b} vs notools on the same seeds: tricks won {saved} runs notools lost ({pct(saved,len(both)).strip()}), lost {cost} it won ({pct(cost,len(both)).strip()})')
    # per trick
    rows = []
    for b in bots:
        if b == 'notools': continue
        U = [u for u in uses if u['bot'] == b]; R = [r for r in runs if r['bot'] == b]
        for k in TRICKS:
            Uk = [u for u in U if u['tool'] == k]
            had = [r for r in R if k in r['kit'].split('+')]
            if not Uk and not had: continue
            rows.append(dict(bot=b, trick=k, uses=len(Uk), per_run_held=f"{len(Uk)/max(1,len(had)):.1f}",
                             avg_gain=f"{sum(max(-60, min(u['gain'], 60)) for u in Uk)/max(1,len(Uk)):+.1f}",
                             hurt=pct(sum(u['gain'] < -0.01 for u in Uk), len(Uk)), in_kill_turn=pct(sum(u['killed'] for u in Uk), len(Uk)),
                             win_when_held=pct(sum(r['win'] for r in had), len(had)), runs_held=len(had)))
    table(rows, ['bot', 'trick', 'uses', 'per_run_held', 'avg_gain', 'hurt', 'in_kill_turn', 'win_when_held', 'runs_held'],
          '== tricks ==   avg_gain = turn value per use (clamped to ±60 so making or losing a kill counts as 60); hurt = uses that made the turn worse')
    # per edge
    rows = []
    for e in EDGE_KEYS:
        row = dict(edge=e)
        for b in bots:
            R = [r for r in runs if r['bot'] == b and r['edge'] == e]
            row[b] = f"{pct(sum(r['win'] for r in R), len(R))} ({len(R)})"; row[b + '_edge'] = pct(sum(r['edge_hits'] for r in R), sum(r['words'] for r in R))
        rows.append(row)
    table(rows, ['edge'] + [c for b in bots for c in (b, b + '_edge')], '== edges ==   win rate (runs), and share of words that hit the edge')

# ---------------------------------------------------------------- the report: numbers in, findings out, no human in between
def stats(runs, turns, uses):
    """Raw numbers (fractions, not strings) for every bot, trick and edge."""
    S = dict(bots={}, tricks={}, edges={}, paired={})
    for b in sorted({r['bot'] for r in runs}):
        R = [r for r in runs if r['bot'] == b]; T = [t for t in turns if t['bot'] == b]; n = max(1, len(R))
        S['bots'][b] = dict(runs=len(R), win=sum(r['win'] for r in R) / n, turns=sum(r['turns'] for r in R) / n,
                            hp_left=sum(r['hp'] for r in R) / max(1, sum(r['win'] for r in R)),
                            dmg_turn=sum(t['dealt'] for t in T) / max(1, len(T)),
                            edge_rate=sum(r['edge_hits'] for r in R) / max(1, sum(r['words'] for r in R)),
                            helped=sum(t['lift'] > 0.01 for t in T) / max(1, len(T)))
        U = [u for u in uses if u['bot'] == b]
        for k in TRICKS:
            Uk = [u for u in U if u['tool'] == k]
            if Uk: S['tricks'].setdefault(b, {})[k] = dict(uses=len(Uk), gain=sum(max(-60, min(u['gain'], 60)) for u in Uk) / len(Uk),
                                                         hurt=sum(u['gain'] < -0.01 for u in Uk) / len(Uk))
        for e in EDGE_KEYS:
            Re = [r for r in R if r['edge'] == e]
            if Re: S['edges'].setdefault(b, {})[e] = dict(runs=len(Re), win=sum(r['win'] for r in Re) / len(Re),
                                                        rate=sum(r['edge_hits'] for r in Re) / max(1, sum(r['words'] for r in Re)))
    by = defaultdict(dict)
    for r in runs: by[r['seed']][r['bot']] = r['win']
    for b in S['bots']:
        both = [v for v in by.values() if 'notools' in v and b in v and b != 'notools']
        if both: S['paired'][b] = dict(saved=sum(v[b] and not v['notools'] for v in both) / len(both),
                                       cost=sum(v['notools'] and not v[b] for v in both) / len(both))
    return S

def sweep_stats(runs, kits):
    base = {r['seed']: r['win'] for r in runs if r['bot'] == 'notools'}; out = {}
    for name, kt in kits.items():
        R = [r for r in runs if r['bot'] == 'smart' and r['kit'] == '+'.join(kt[1:])]
        out[name] = dict(win=sum(r['win'] for r in R) / max(1, len(R)), turns=sum(r['turns'] for r in R) / max(1, len(R)),
                         hp_left=sum(r['hp'] for r in R) / max(1, len(R)))
    out['_notools'] = dict(win=sum(base.values()) / max(1, len(base)))
    return out

def sweep_jobs(seeds, draft, beam):
    kits = {'(none)': ['quill', 'nudge', 'flip']}
    for k in TRICKS[2:]: kits[k] = ['quill', 'nudge', 'flip', k]
    jobs = [(s, 'notools', draft, kits['(none)'], beam) for s in seeds]
    for kt in kits.values(): jobs += [(s, 'smart', draft, kt, beam) for s in seeds]
    return jobs, kits

def findings(live, sweep_live, sweep_hard, scan, hard_scale):
    """Rules that turn the numbers into plain sentences. Thresholds are written here so anyone can argue with them."""
    F = []; B = live['bots']; P = live['paired']
    nt, sm = B.get('notools'), B.get('smart')
    if nt and sm:
        lift = sm['win'] - nt['win']
        if lift < .10: F.append(('tools', 'warn', f"Tricks barely matter: smart wins {sm['win']:.0%} vs notools {nt['win']:.0%}."))
        else: F.append(('tools', 'ok', f"Tricks matter: smart wins {sm['win']:.0%} vs notools {nt['win']:.0%} (+{lift*100:.0f} pts); "
                                      f"on the same seeds they rescue {P['smart']['saved']:.0%} of runs and cost {P['smart']['cost']:.0%}."))
        F.append(('want', 'ok' if sm['helped'] >= .5 else 'warn',
                  f"A trick improves {sm['helped']:.0%} of smart's turns" + (" — there's usually a reason to reach for one." if sm['helped'] >= .5 else " — most turns, tricks have nothing to do.")))
        if sm['win'] >= .97: F.append(('difficulty', 'warn', f"Too easy for a tool user: smart wins {sm['win']:.0%} at foe HP ×{FOE_HP_SCALE}. Bots spell perfectly, so humans will do worse, but there is headroom."))
    if 'eager' in live['tricks']:
        for k, t in live['tricks']['eager'].items():
            if t['hurt'] >= .20: F.append(('trap', 'warn', f"{k}: used blindly it makes the turn worse {t['hurt']:.0%} of the time — a trap for players who like pressing buttons."))
    if 'smart' in live['tricks']:
        ranked = sorted(live['tricks']['smart'].items(), key=lambda kv: -kv[1]['gain'])
        F.append(('value', 'info', 'Value per use (smart): ' + ', '.join(f"{k} {t['gain']:+.1f}" for k, t in ranked) + '.'))
    for label, sw in (('live', sweep_live), (f'HP ×{hard_scale}', sweep_hard)):
        none = sw['(none)']['win']; ranked = sorted(((k, v) for k, v in sw.items() if not k.startswith('_') and k != '(none)'), key=lambda kv: -kv[1]['win'])
        F.append(('third', 'info', f"Third trick at {label}: " + ', '.join(f"{k} {v['win']:.0%}" for k, v in ranked) + f"; none {none:.0%}."))
        dead = [k for k, v in ranked if v['win'] - none < .01]
        if dead and label != 'live': F.append(('dead', 'warn', f"Dead weight at {label}: {', '.join(dead)} add under 1 pt over no third trick."))
        if len(ranked) > 1 and ranked[0][1]['win'] - ranked[1][1]['win'] > .03:
            F.append(('dominant', 'warn', f"{ranked[0][0]} dominates at {label}: {ranked[0][1]['win']:.0%} vs next best {ranked[1][0]} {ranked[1][1]['win']:.0%}."))
    E = live['edges'].get('notools', {})
    if E:
        mean = sum(e['win'] for e in E.values()) / len(E)
        for k, e in E.items():
            if e['rate'] < .05: F.append(('edge', 'warn', f"Edge {k} rarely fires: {e['rate']:.0%} of notools words."))
            if e['win'] - mean > .15: F.append(('edge', 'warn', f"Edge {k} is too generous: notools wins {e['win']:.0%} on those days (mean {mean:.0%})."))
            if mean - e['win'] > .15: F.append(('edge', 'warn', f"Edge {k} is stingy: notools wins {e['win']:.0%} on those days (mean {mean:.0%})."))
    if scan:
        pts_ = sorted(scan.items())
        txt = ', '.join(f"×{h}: notools {v['notools']:.0%} / smart {v['smart']:.0%}" for h, v in pts_)
        F.append(('scan', 'info', f"Foe HP scan — {txt}."))
        gap = max(pts_, key=lambda hv: hv[1]['smart'] - hv[1]['notools'])
        F.append(('scan', 'info', f"The widest tools-vs-no-tools gap is at foe HP ×{gap[0]} ({gap[1]['smart']:.0%} vs {gap[1]['notools']:.0%})."))
    return F

def report(a):
    import io, contextlib
    seeds = seeds_from(a); out = io.StringIO(); t0 = time.time(); live_hp = FOE_HP_SCALE
    def section(title, fn):
        print(f'[{time.time()-t0:4.0f}s] {title}', file=sys.stderr)
        with contextlib.redirect_stdout(out): print(f'\n### {title}\n```'); r = fn(); print('```')
        return r
    # 1. the three bots on the live rules
    jobs = [(s, b, a.draft, None, a.beam) for s in seeds for b in ('notools', 'smart', 'eager')]
    runs, turns, uses = run_all(jobs, a.j)
    section(f'Bots on live rules ({len(seeds)} seeds, foe HP ×{live_hp})', lambda: summarize(runs, turns, uses, 'live'))
    live = stats(runs, turns, uses)
    for name, rows in (('runs', runs), ('turns', turns), ('tool_uses', uses)): write(f'report_{name}.csv', rows)
    # 2. third-trick sweeps, live and hard
    sw = {}
    for label, hp in (('live', live_hp), ('hard', a.hard_scale)):
        _init(hp); jobs, kits = sweep_jobs(seeds[:a.sweep_n], a.draft, a.beam)
        r2, _, _ = run_all(jobs, a.j); sw[label] = sweep_stats(r2, kits)
        rows = [dict(third=k, win=pct(v['win'], 1), turns=f"{v['turns']:.1f}", hp_left=f"{v['hp_left']:.1f}") for k, v in sw[label].items() if not k.startswith('_')]
        section(f'Third trick, foe HP ×{hp} ({min(len(seeds), a.sweep_n)} seeds; notools {sw[label]["_notools"]["win"]:.0%})',
                lambda: table(rows, ['third', 'win', 'turns', 'hp_left'], 'kit = Quill + Nudge + Flip + this'))
    # 3. foe HP scan: where do tricks make the biggest difference?
    scan = {}
    for hp in a.scan:
        _init(hp); r3, t3, u3 = run_all([(s, b, a.draft, None, a.beam) for s in seeds[:a.sweep_n] for b in ('notools', 'smart')], a.j)
        s3 = stats(r3, t3, u3); scan[hp] = {b: s3['bots'][b]['win'] for b in ('notools', 'smart')}
    _init(live_hp)
    F = findings(live, sw['live'], sw['hard'], scan, a.hard_scale)
    icon = dict(ok='✅', warn='⚠️', info='•')
    md = [f"# Dungeon Scrawl sim report", f"_{time.strftime('%Y-%m-%d %H:%M')} · {len(seeds)} seeds · draft={a.draft} · beam={a.beam} · "
          f"{time.time()-t0:.0f}s. Written by tools/scrawl_sim.py report; every line below comes from the runs._", '', '## Findings', '']
    md += [f"- {icon[lvl]} **{tag}** {text}" for tag, lvl, text in F]
    md += ['', '## Tables', out.getvalue()]
    os.makedirs(os.path.join(HERE, 'sim-out'), exist_ok=True)
    with open(os.path.join(HERE, 'sim-out', 'report.md'), 'w', encoding='utf8') as f: f.write('\n'.join(md))
    with open(os.path.join(HERE, 'sim-out', 'report.json'), 'w', encoding='utf8') as f:
        json.dump(dict(live=live, sweep=sw, scan={str(k): v for k, v in scan.items()}, findings=[dict(tag=t, level=l, text=x) for t, l, x in F]), f, indent=1)
    print('\n'.join(md[:5 + len(F)]))
    snapshot('report', a.tag or 'health', md, dict(live=live, sweep=sw, scan={str(k): v for k, v in scan.items()},
             findings=[dict(tag=t, level=l, text=x) for t, l, x in F]), F[0][2] if F else 'Health report')
    print(f"\nFull report: {os.path.join(HERE, 'sim-out', 'report.md')}")

# ---------------------------------------------------------------- trial: test candidate tricks against the live ones
def trial(a):
    """Every trick (live ones are the controls) goes in the kit Quill + Nudge + Flip + it, played by the smart bot on the
    same seeds, foe HP at --hard-scale so wins don't all hit 100%. The eager bot plays a smaller set to find traps.
    Verdicts come from the rules below, not from a person reading the tables."""
    seeds = seeds_from(a); tag = a.tag or 'trial'; t0 = time.time(); _init(a.hard_scale)
    base = [k for k in (a.base or '').split(',') if k]   # the kit every trick joins: Nudge + Flip (the start), or nothing
    tricks = a.tricks.split(',') if a.tricks else [k for k in TRICKS if k not in base]
    tricks += [k for k in LIVE_TRICKS if k not in base and k not in tricks]   # every live trick is always a control, so the bar never moves
    kits = {'(none)': ['quill'] + base, **{k: ['quill'] + base + [k] for k in tricks}}
    base_name = ' + '.join(['Quill'] + [TOOLS[k]['name'] for k in base])
    SB, EB = ('quick', 'qeager') if a.quick else ('smart', 'eager')   # --quick: the heuristic bots
    jobs = [(s, SB, a.draft, kt, a.beam) for kt in kits.values() for s in seeds]
    jobs += [(s, EB, a.draft, kits[k], a.beam) for k in tricks for s in seeds[:a.eager_n]]
    runs, turns, uses = run_all(jobs, a.j, cache=True)
    rows = {}
    for name, kt in kits.items():
        ks = '+'.join(kt[1:])
        R = [r for r in runs if r['bot'] == SB and r['kit'] == ks]; n = max(1, len(R))
        T = [t for t in turns if t['bot'] == SB and t['kit'] == ks]
        U = [u for u in uses if u['bot'] == SB and u['kit'] == ks and u['tool'] == name]
        E = [u for u in uses if u['bot'] == EB and u['kit'] == ks and u['tool'] == name]
        rows[name] = dict(trick=name, idea=int(name in IDEAS_LOADED), win=sum(r['win'] for r in R) / n, turns=sum(r['turns'] for r in R) / n,
                          hp_left=sum(r['hp'] for r in R) / n,
                          use_rate=sum(name in t['tools'].split('+') for t in T) / max(1, len(T)), uses_run=len(U) / n,
                          gain=sum(max(-60, min(u['gain'], 60)) for u in U) / max(1, len(U)),
                          hurt=sum(u['gain'] < -0.01 for u in E) / max(1, len(E)) if E else None,
                          desc=TOOLS[name].get('desc', '') if name in TOOLS else base_name + ' only')
    none = rows['(none)']
    for r in rows.values():
        r['lift'] = r['win'] - none['win']; r['turns_saved'] = none['turns'] - r['turns']
    controls = sorted(rows[k]['lift'] for k in tricks if k in LIVE_TRICKS)
    n = len(controls); med = (controls[(n - 1) // 2] + controls[n // 2]) / 2 if n else 0; top = controls[-1] if n else 0
    for k in tricks:
        r = rows[k]; v = []
        if r['lift'] < .02 and r['turns_saved'] < .2: v.append('dud')
        elif r['lift'] > top + .03: v.append('overpowered')
        elif r['lift'] >= max(med, a.bar) and r['use_rate'] >= .15: v.append('keeper')
        elif r['lift'] >= max(med, a.bar): v.append('niche')
        else: v.append('weak')
        if r['hurt'] is not None and r['hurt'] >= .25: v.append('trap')
        r['verdict'] = '+'.join(v)
    order = sorted(tricks, key=lambda k: (-rows[k]['lift'], -rows[k]['turns_saved']))
    md = [f'# Trick trial: {tag}', f"_{time.strftime('%Y-%m-%d %H:%M')} · {len(seeds)} seeds per trick · foe HP ×{a.hard_scale} · {SB} bot · "
          f"eager on {min(a.eager_n, len(seeds))} · {len(runs)} runs in {time.time()-t0:.0f}s · ideas from {', '.join(IDEA_FILES) or '-'}_", '',
          f"Baseline ({base_name}): win {none['win']:.1%}, {none['turns']:.2f} turns. Each trick is played as {base_name} + the trick. "
          f"The bar: a keeper adds at least {max(med, a.bar)*100:+.1f} pts (the median live lift {med*100:+.1f}, or the floor {a.bar*100:+.0f}, whichever is higher); best live {top*100:+.1f}.", '',
          '| trick | new? | verdict | win | lift | turns saved | used on turns | uses/run | gain/use | eager hurt | what it does |', '|' + '---|' * 11]
    for k in order:
        r = rows[k]
        md.append(f"| {k} | {'idea' if r['idea'] else 'live'} | {r['verdict']} | {r['win']:.1%} | {r['lift']*100:+.1f} | {r['turns_saved']:+.2f} | {r['use_rate']:.0%} | "
                  f"{r['uses_run']:.1f} | {r['gain']:+.1f} | {'-' if r['hurt'] is None else format(r['hurt'], '.0%')} | {r['desc']} |")
    md += ['', 'Rules: dud = under +2 pts and under 0.2 turns saved; overpowered = 3+ pts above the best live trick; keeper = at least the bar above and used on 15%+ of turns; '
           'niche = strong but rarely used; weak = below the median live trick; trap = the eager bot makes its turn worse with it 25%+ of the time.']
    os.makedirs(os.path.join(HERE, 'sim-out'), exist_ok=True)
    with open(os.path.join(HERE, 'sim-out', f'{tag}.md'), 'w', encoding='utf8') as f: f.write('\n'.join(md))
    with open(os.path.join(HERE, 'sim-out', f'{tag}.json'), 'w', encoding='utf8') as f: json.dump(rows, f, indent=1)
    record(tag, a, rows, len(seeds), len(runs))
    print('\n'.join(md))
    new = sorted((r for k, r in rows.items() if r['idea'] and k in tricks), key=lambda r: -r['lift'])
    head = (f"{len(tricks)} tricks at foe HP x{a.hard_scale}; baseline wins {none['win']:.0%}. "
            + (f"Best new: {new[0]['trick']} {new[0]['lift']*100:+.1f} pts ({new[0]['verdict']})." if new else '')
            + f" Keepers: {sum('keeper' in rows[k]['verdict'] for k in tricks)}, traps: {sum('trap' in rows[k]['verdict'] for k in tricks)}.")
    snapshot('trial', tag, md, dict(rows=rows, round=a.round, note=ROUND_META.get(f'r{a.round}.py', {}).get('note', '') if a.round else ''), head)

# ---------------------------------------------------------------- versioning: rules fingerprint, self-test, evolution history
def rules_hash():
    """Fingerprint of the rules code in scrawl.html, so we notice when the page changes under the sim."""
    import hashlib
    page = open(os.path.join(ROOT, 'scrawl.html'), encoding='utf8', newline='').read().replace('\r\n', '\n')
    parts = []
    for a, b in (('// ---- letters ----', '// ---- game feel'), ('function removeTile', 'function render')):
        i = page.find(a); j = page.find(b, i)
        parts.append(page[i:j] if i >= 0 and j >= 0 else '')
    parts.append(open(os.path.join(ROOT, 'scrawl-items.js'), encoding='utf8', newline='').read().replace(chr(13) + chr(10), chr(10)))   # the items are rules too
    return hashlib.sha256(chr(10).join(parts).encode()).hexdigest()[:12]

FXMARK = {'fire': '^', 'steel': '#', 'gold': '$', 'leaf': '+'}
def stamp_fixtures(path):
    """Take a capture from tools/capture_fixtures.js, stamp it with the page's rules fingerprint, save it as sim_fixtures.json."""
    F = json.load(open(path, encoding='utf8'))
    if isinstance(F, str): F = json.loads(F)
    F['rules_hash'] = rules_hash()
    json.dump(F, open(os.path.join(HERE, 'sim_fixtures.json'), 'w', encoding='utf8', newline=chr(10)), indent=1, ensure_ascii=False)
    print(f"sim_fixtures.json: {len(F['cases'])} runs, {len(F.get('deep', []))} descents, {len(F.get('tricks', []))} trick scripts, rules {F['rules_hash']}")

def selftest():
    """Replays reference runs captured from the page; any mismatch means the port has drifted."""
    F = json.load(open(os.path.join(HERE, 'sim_fixtures.json'), encoding='utf8')); bad = 0
    for c in F['cases']:
        g = Game(c['seed']); got = dict(foes=[[f['k'], f['hp'], f['mi']] for f in g.foes], edge=g.edge, letter=g.letter,
                                        offers0=g.offers(0), hand0=[[t['ch'], t['fx']] for t in g.hand])
        trail = []
        for _ in range(6):
            if g.over: break
            g.draft = None; h = [t for t in g.hand if not t['crossed']]; hit = '-'
            for x, y, z in ((x, y, z) for x in range(len(h)) for y in range(len(h)) for z in range(len(h))):
                if len({x, y, z}) < 3: continue
                w = h[x]['ch'] + h[y]['ch'] + h[z]['ch']
                if w in WORDS: g.strike([h[x]['id'], h[y]['id'], h[z]['id']]); hit = w; break
            if g.over: break
            g.draft = None; g.end_turn(); trail.append([hit, g.fi, g.hp, [f['hp'] for f in g.foes]])
        got['trail'] = trail
        diffs = [k for k in got if got[k] != c[k]]
        print(f"  {'ok  ' if not diffs else 'FAIL'} {c['seed']}" + (f"  differs in {diffs}" if diffs else ''))
        bad += bool(diffs)
    global FOE_HP_SCALE, FOE_ATK_SCALE
    for c in F.get('deep', []):   # the endless descent, scripted deep with attacks off
        g0 = Game(c['seed'], deep=True); foes = [[f['k'], f['hp'], f['mi'], f['ax']] for f in (g0.deep_foe(i) for i in (3, 4, 5, 6, 9))]
        keep = FOE_HP_SCALE, FOE_ATK_SCALE; FOE_HP_SCALE, FOE_ATK_SCALE = c['hp_scale'], c['atk_scale']
        try:
            g = Game(c['seed'], deep=True); trail = []
            for _ in range(c['turns']):
                if g.over: break
                g.draft = None; h = [t for t in g.hand if not t['crossed']]; hit = '-'
                for x, y, z in ((x, y, z) for x in range(len(h)) for y in range(len(h)) for z in range(len(h))):
                    if len({x, y, z}) < 3: continue
                    w = h[x]['ch'] + h[y]['ch'] + h[z]['ch']
                    if w in WORDS: g.strike([h[x]['id'], h[y]['id'], h[z]['id']]); hit = w; break
                if g.over: break
                g.draft = None; g.end_turn(); trail.append([hit, g.fi, g.foes[g.fi]['hp']])
        finally: FOE_HP_SCALE, FOE_ATK_SCALE = keep
        diffs = [k for k, v in (('deep_foes', foes == c['deep_foes']), ('trail', trail == c['trail']), ('depth', g.fi + 1 == c['depth'])) if not v]
        print(f"  {'ok  ' if not diffs else 'FAIL'} {c['seed']} endless descent to depth {g.fi + 1}" + (f"  differs in {diffs}" if diffs else ''))
        bad += bool(diffs)
    same_kind = {r['id']: r.get('effect', {}).get('sameKind') for r in ITEMS['items']}
    for c in F.get('tricks', []):   # every trick in the lab kit, used once each in kit order (tools/capture_fixtures.js)
        g = Game(c['seed'], kit=['quill'] + ROSTER); g.kit_fixed = True; log = []
        for _ in range(2):
            if g.over: break
            for k in list(g.kit):
                T = TOOLS[k]
                if k == 'quill' or not g.uses_left(k) or g.over: continue
                okT = [t for t in g.hand if not t['crossed'] and T['ok'](t)]
                if T.get('notile'):
                    g.use_tool(k, [])
                    if g.affixing: g.pick_affix(0)
                elif T['kind'] == 'socket':
                    w = next(([a, b, d] for a in okT for b in okT for d in okT if len({a['id'], b['id'], d['id']}) == 3 and a['ch'] + b['ch'] + d['ch'] in WORDS), None)
                    if not w: continue
                    g.use_tool(k, [t['id'] for t in w])
                elif T['kind'] == 'pair':
                    a = okT[0] if okT else None
                    b = a and next((t for t in okT if t is not a and (not same_kind.get(k) or (a['ch'] in VOW) == (t['ch'] in VOW))), None)
                    if not b: continue
                    g.use_tool(k, [a['id'], b['id']])
                else:
                    if not okT: continue
                    t = okT[0]
                    if T['kind'] == 'choose':
                        ch = next((x for x in T['options'](t) if x != t['ch']), None)
                        if ch: g.use_tool(k, [t['id'], '=' + ch])
                    else: g.use_tool(k, [t['id']])
                log.append([k, ''.join(t['ch'] + FXMARK.get(t['fx'], '') + ('*' if t['crossed'] else '') for t in g.hand), g.foe['hp'], g.block, g.hp])
            if not g.over: g.end_turn()
        ok = log == c['log']
        if not ok:
            i = next((i for i, (x, y) in enumerate(zip(log, c['log'])) if x != y), min(len(log), len(c['log'])))
            print(f"  FAIL {c['seed']} tricks: first difference at use {i}: sim {log[i] if i < len(log) else '-'} page {c['log'][i] if i < len(c['log']) else '-'}")
        else: print(f"  ok   {c['seed']} every trick ({len(log)} uses)")
        bad += not ok
    h = rules_hash(); known = F.get('rules_hash')
    print(f"  sim {SIM_VERSION} · page rules {h}" + ('' if h == known else f"  (fixtures were captured at {known}: if the page's rules changed, re-port and recapture)"))
    print('selftest ' + ('passed' if not bad else f'FAILED on {bad} case(s)'))
    return not bad

LAB = os.path.join(ROOT, 'scrawl-lab')       # the analytics pages on the site
CHANGELOG = [   # newest first; every version gets a git tag scrawl-sim-v<version> so old reports can be rerun
    ('1.8.0', '2026-11-24', 'New trick kinds: draw, reroll, affix (random prefixes and suffixes), socket (spell a 3-letter word into the trick) and enchanting morphs. Random tricks roll a seeded stream per use; bots plan them from 8 imagined outcomes and replan after the real roll. Hands over 8 tiles plan with their 50 best words. Heuristic quick / qeager bots; trial --quick, --base, --bar. Old idea ids no longer shadow live items in trials; trial runs are cached. 12 new tricks from the 27 Nov daily, tiered by hand (no rounds run).'),
    ('1.6.0', '2026-11-22', 'Blade bonus squares (DL / TL / DW) from the 22 Nov daily; five new tools (Soften, Scribble, Lunge, Recoil, Triplicate) join the roster that day; planner scores each word by its letter order.'),
    ('1.5.0', '2026-11-20', 'Items as data: every trick is read from scrawl-items.js, the same file the page uses; trick behaviour fingerprinted identical to 1.4.0 on page and sim.'),
    ('1.4.0', '2026-11-20', 'Tiered equipment from the 21 Nov daily: 15-trick roster (common / uncommon / rare from the 1.2.0 trials), tiered Armoury offers; Swap, Rotate, Vowel Shift, Split and Ink Blot retired from offers.'),
    ('1.3.0', '2026-11-20', 'Endless descent (deep runs: foes keep coming, every third is The Editor, +10% attack per set of three); fair draws from the 21 Nov daily on (no consonant twice in a hand, one of JQXZ, one of FKVWY), matching the page; fixtures recaptured.'),
    ('1.2.0', '2026-11-20', 'Exactly reproducible (ties between equal plays now break the same way in every process); every trial includes all live tricks as controls, so the keeper bar is the same in every round.'),
    ('1.1.0', '2026-11-20', 'Evolution rounds (trial, idea files with lineage, choose and pair trick kinds), selftest against the page, Lab snapshots.'),
    ('1.0.0', '2026-11-20', 'Port of the four-card kit rules (Spellblade up to 6, daily edge, foe HP x1.22); notools, smart and eager bots; compare, sweep, report.'),
]

UNTAGGED = {'1.0.0', '1.1.0'}   # built before the sim was committed, so there is no tag to check out

def run_info():
    """Everything needed to rerun this exact run later."""
    import subprocess
    def git(*args):
        try: return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception: return ''
    return dict(sim_version=SIM_VERSION, tag=f'scrawl-sim-v{SIM_VERSION}', rules=rules_hash(), commit=git('rev-parse', '--short', 'HEAD'),
                dirty=bool(git('status', '--porcelain', '--', 'tools', 'scrawl.html')),
                command='py tools/scrawl_sim.py ' + ' '.join(sys.argv[1:]), date=time.strftime('%Y-%m-%d %H:%M'), python=sys.version.split()[0])

def snapshot(kind, tag, md, data, headline, info=None):
    """Save a finished report into the Lab (scrawl-lab/reports/<id>/) and rebuild the Lab's index."""
    info = info or run_info(); rid = info['date'].replace('-', '').replace(':', '').replace(' ', '-') + '-' + tag
    d = os.path.join(LAB, 'reports', rid); os.makedirs(d, exist_ok=True)
    stamp = (f"**Run:** sim {info['sim_version']} · page rules {info['rules']} · commit {info['commit'] or '?'}{' + local changes' if info['dirty'] else ''}"
             f" · rerun: `git checkout {info['tag']}` then `{info['command']}`")
    open(os.path.join(d, 'report.md'), 'w', encoding='utf8', newline='').write('\n'.join(md[:2] + [stamp] + md[2:]))
    json.dump(dict(id=rid, kind=kind, tag=tag, headline=headline, run=info, data=data), open(os.path.join(d, 'data.json'), 'w', encoding='utf8'), indent=1, ensure_ascii=False)
    print(f'Saved to the Lab: {d}')
    publish()

def publish():
    """Rebuild scrawl-lab/index.json and scrawl-lab/evolution.html from the saved reports and the history."""
    base = os.path.join(LAB, 'reports'); reps = []
    for rid in sorted(os.listdir(base) if os.path.isdir(base) else [], reverse=True):
        f = os.path.join(base, rid, 'data.json')
        if os.path.exists(f):
            j = json.load(open(f, encoding='utf8')); reps.append({k: j[k] for k in ('id', 'kind', 'tag', 'headline', 'run')})
    os.makedirs(LAB, exist_ok=True)
    json.dump(dict(sim_version=SIM_VERSION, built=time.strftime('%Y-%m-%d %H:%M'),
                   changelog=[dict(version=v, date=d, note=n, tag=None if v in UNTAGGED else f'scrawl-sim-v{v}') for v, d, n in CHANGELOG], reports=reps),
              open(os.path.join(LAB, 'index.json'), 'w', encoding='utf8'), indent=1, ensure_ascii=False)
    if os.path.exists(HISTORY): viz()
    print(f'Lab rebuilt: {len(reps)} reports')

HISTORY = os.path.join(HERE, 'evolution', 'history.json')
def record(tag, a, rows, nseeds, nruns):
    """Append a finished trial to the evolution history the visualizer reads."""
    os.makedirs(os.path.dirname(HISTORY), exist_ok=True)
    hist = json.load(open(HISTORY, encoding='utf8')) if os.path.exists(HISTORY) else dict(rounds=[])
    meta = next((m for f, m in ROUND_META.items() if f'r{a.round}.py' == f), {}) if getattr(a, 'round', None) else {}
    entry = dict(tag=tag, round=getattr(a, 'round', None), date=time.strftime('%Y-%m-%d %H:%M'), sim_version=SIM_VERSION, rules=rules_hash(),
                 hard_scale=a.hard_scale, base=getattr(a, 'base', 'nudge,flip'), bar=getattr(a, 'bar', 0), seeds=nseeds, runs=nruns, note=meta.get('note', ''), idea_files=list(IDEA_FILES),
                 tricks=[dict(r, parent=LINEAGE.get(k)) for k, r in rows.items()], run=run_info())
    hist['rounds'] = [r for r in hist['rounds'] if r['tag'] != tag] + [entry]
    hist['rounds'].sort(key=lambda r: (r['round'] or 0, r['date']))
    json.dump(hist, open(HISTORY, 'w', encoding='utf8'), indent=1, ensure_ascii=False)
    print(f"Recorded in {HISTORY}")

def viz():
    """Build evolution/evolution.html from the template and the history (data inlined, so the page stands alone)."""
    hist = json.load(open(HISTORY, encoding='utf8'))
    tpl = open(os.path.join(HERE, 'evolution', 'viz_template.html'), encoding='utf8').read()
    out = os.path.join(LAB, 'evolution.html'); os.makedirs(LAB, exist_ok=True)
    open(out, 'w', encoding='utf8', newline='').write(tpl.replace('__DATA__', json.dumps(hist, ensure_ascii=False).replace('</', '<' + chr(92) + '/')))
    print(f'Wrote {out}')

# ---------------------------------------------------------------- evolve: the sim breeds items from the data grammar
def describe(r):
    """A plain sentence for any item record, so every evolved item can be read by a player."""
    tg, e, kd = r.get('target', {'type': 'any'}), r.get('effect', {}), r['kind']
    who = {'vowel': 'A vowel', 'consonant': 'A consonant', 'minValue': f"A tile worth {tg.get('value')}+", 'letters': f"One of {' '.join(tg.get('letters', ''))}"}.get(tg['type'], 'A tile')
    if kd == 'morph' and 'fx' in e: what = f"turns {e['fx']}"
    elif kd == 'morph':
        if 'shift' in e: n = e['shift']; what = f"moves {abs(n)} step{'s' if abs(n) > 1 else ''} {'on' if n > 0 else 'back'}"
        elif e.get('mirror'): what = 'is mirrored (A↔Z)'
        elif e.get('set') == BLANK: what = 'becomes a blank'
        else: what = 'changes by its table'
    elif kd == 'choose':
        o = e['options']; what = 'turns by shape, your pick' if 'groups' in o else {'aeiou': 'becomes any vowel', 'bcdfghjklmnpqrstvwxyz': 'becomes any consonant'}.get(o['letters'], f"becomes any of {o['letters'].upper()}")
    elif kd == 'make':
        parts = [('itself' if m.get('self') else 'a copy' if m.get('copy') else m['letter'].upper()) for m in e['make']]
        what = 'becomes ' + ' + '.join(parts)
    elif kd == 'pair': what = "takes another tile's letter" + (' (same kind only)' if e.get('sameKind') else '')
    elif kd == 'draw': d = e['draw']; who, what = 'You', f"draw {d.get('n', 1)} tile{'s' if d.get('n', 1) > 1 else ''}" + ('' if d.get('pool', 'any') == 'any' else f" ({d['pool']})")
    elif kd == 'reroll': d = e['reroll']; who = 'Every ' + who.split(' ', 1)[1].lower() if d.get('hand') else who; what = 'rerolls' + (' (same kind)' if d.get('pool', 'same') == 'same' else '')
    elif kd == 'affix': who, what = 'You', 'pop a random ' + ' / '.join(x.upper() for x in e['affix']['list'])
    elif kd == 'socket': o = e['socket']; who, what = 'A 3-letter word set in it', ', '.join(x for x in (f"deals ×{o['dmg']}" if o.get('dmg') else '', f"blocks ×{o['block']}" if o.get('block') else '', f"heals {o['heal']}" if o.get('heal') else '', f"draws {o['draw']}" if o.get('draw') else '') if x)
    else: what = 'swaps with another tile'
    ch = f" (×{r['uses']} a turn)" if r.get('uses', 1) > 1 else '' if r.get('uses') else f", {r['perFight']}× a foe"
    return f'{who} {what}{ch}.'

def mutate(r, rng, pool):
    """One small change to an item record, kept inside what the page can play and explain."""
    c = json.loads(json.dumps(r)); e = c.setdefault('effect', {}); kd = c['kind']
    ops = ['charges']
    if kd == 'morph' and 'shift' in e: ops += ['shift', 'shift', 'target']
    if kd == 'choose': ops += ['letters', 'letters', 'target']
    if kd == 'make': ops += ['parts', 'parts']
    if kd == 'pair': ops += ['samekind']
    same = [x for x in pool if x['kind'] == kd and x['id'] != r['id']]
    if same: ops.append('cross')
    op = rng.choice(ops)
    if op == 'charges':
        if c.get('uses') and rng.random() < .3: c['perFight'] = rng.choice([1, 2, 3]); c.pop('uses')
        elif c.get('perFight') and rng.random() < .3: c['uses'] = rng.choice([1, 2]); c.pop('perFight')
        elif c.get('uses'): c['uses'] = max(1, min(3, c['uses'] + rng.choice([-1, 1])))
        else: c['perFight'] = max(1, min(3, c['perFight'] + rng.choice([-1, 1])))
    elif op == 'shift': e['shift'] = rng.choice([n for n in (-3, -2, -1, 1, 2, 3) if n != e['shift']])
    elif op == 'target':
        c['target'] = rng.choice([{'type': 'notBlank', 'msg': 'Not on a blank'}, {'type': 'vowel', 'msg': 'Vowels only'},
                                  {'type': 'consonant', 'msg': 'Consonants only'}, {'type': 'minValue', 'value': rng.choice([3, 4, 5]), 'msg': 'Only high tiles'}])
        if kd == 'choose' and c['target']['type'] == 'minValue': c['target'] = {'type': 'notBlank', 'msg': 'Not on a blank'}
    elif op == 'letters':
        e['options'] = {'letters': rng.choice(['aeiou', 'bcdfghjklmnpqrstvwxyz', 'abcdefghijklmnopqrstuvwxyz', 'etaoinsrhl', 'rstlne', 'aeiouy', 'bdgkpt'])}
    elif op == 'parts':
        e['make'] = rng.choice([[{'self': True}, {'copy': True}], [{'self': True}, {'letter': rng.choice('eastrio')}],
                                [{'letter': rng.choice('eao')}, {'letter': rng.choice('srtn')}], [{'self': True}, {'copy': True}, {'copy': True}],
                                [{'copy': True}, {'letter': 'e'}]])
        if any(m.get('copy') for m in e['make']) and len(e['make']) == 3: c['perFight'] = 1; c.pop('uses', None)
    elif op == 'samekind': e['sameKind'] = not e.get('sameKind')
    elif op == 'cross':
        o = rng.choice(same); c['target'] = json.loads(json.dumps(o.get('target', {'type': 'any'})))
        if rng.random() < .5: c['effect'] = json.loads(json.dumps(o['effect']))
    if kd in ('morph', 'choose') and c['target']['type'] == 'any': c['target'] = {'type': 'notBlank', 'msg': 'Not on a blank'}
    e = c['effect']   # guardrails: a table or a shape group only works on the letters it covers
    if kd == 'morph' and 'map' in e and len(e['map']) < 26:
        keys = ''.join(e['map']); c['target'] = {'type': 'letters', 'letters': keys, 'msg': 'Only ' + ' '.join(keys)}
    if kd == 'choose' and 'groups' in e.get('options', {}):
        keys = ''.join(e['options']['groups']); c['target'] = {'type': 'letters', 'letters': keys, 'msg': 'Only ' + ' '.join(keys)}
    if kd == 'make' and any(m.get('self') or m.get('copy') for m in e['make']) and c['target']['type'] == 'notBlank': pass
    if not c.get('uses') and not c.get('perFight'): c['uses'] = 1
    return c, op

def signature(r):
    """What an item does to every letter: two items with the same signature are the same item."""
    T = compile_item(r); out = [r['kind'], str(r.get('uses', 0)), str(r.get('perFight', 0))]
    for ch in 'abcdefghijklmnopqrstuvwxyz':
        t = dict(id='x', ch=ch, fx=None, crossed=False)
        if not T['ok'](t): out.append('-'); continue
        k = r['kind']
        out.append(T['to'](t) if k == 'morph' else ''.join(T['options'](t)) if k == 'choose' else ''.join(c for c, _ in T['make'](t)) if k == 'make'
                   else ''.join(''.join(T['pair'](t, dict(ch=b))) for b in 'aez') if k == 'pair' else 's')
    return '|'.join(out)

def evolve(a):
    """Generations of items bred from the roster: mutate, trial against the live tricks, keep the ones that land in a tier
    band, used often and rarely backfiring. Every generation is recorded like a trial, so the Lab shows its family tree."""
    rng = random.Random(f'evolve-{a.tag or "run"}')
    live = [r for r in ITEMS['items'] if r.get('tier')]
    seen = {signature(r) for r in ITEMS['items']}
    parents = live[:]; survivors = []
    os.makedirs(os.path.join(HERE, 'evolution'), exist_ok=True)
    for gen in range(1, a.gens + 1):
        kids = []; tries = 0
        while len(kids) < a.pop and tries < a.pop * 40:
            tries += 1; par = rng.choice(parents); child, op = mutate(par, rng, live)
            sig = signature(child)
            if sig in seen: continue
            seen.add(sig)
            child.update(id=f"g{gen}x{len(kids) + 1}", name=f"{par['name']} {'′' * gen}{len(kids) + 1}", parent=par['id'], op=op)
            child.pop('tier', None); child['desc'] = describe(child); kids.append(child)
        path = os.path.join(HERE, 'evolution', f'{a.tag or "evo"}-gen{gen}.json')
        json.dump(kids, open(path, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
        print(f'\n=== generation {gen}: {len(kids)} children ===', file=sys.stderr)
        for k in kids: print(f"  {k['id']:6} from {k['parent']:8} ({k['op']}): {k['desc']}", file=sys.stderr)
        IDEA_FILES[:] = IDEA_FILES + [path]; load_ideas([path])
        t = argparse.Namespace(**vars(a)); t.tricks = ','.join(k['id'] for k in kids); t.tag = f"{a.tag or 'evo'}-gen{gen}"; t.round = None
        trial(t)
        rows = json.load(open(os.path.join(HERE, 'sim-out', f'{t.tag}.json'), encoding='utf8'))
        def fit(r):
            if r['lift'] < .08: return None
            tier = 'rare' if r['lift'] >= .35 else 'uncommon' if r['lift'] >= .25 else 'common'
            if r['use_rate'] < .15 or (r['hurt'] is not None and r['hurt'] >= .25): return None
            return tier
        good = []
        for k in kids:
            r = rows[k['id']]; tier = fit(r)
            if tier: k['tier_guess'] = tier; k['lift'] = r['lift']; k['use_rate'] = r['use_rate']; k['hurt'] = r['hurt']; good.append(k)
        good.sort(key=lambda k: -(k['use_rate'] - (k['hurt'] or 0)))
        survivors += good
        print(f"  survivors: {', '.join(k['id'] + ' ' + k['tier_guess'] for k in good) or 'none'}", file=sys.stderr)
        parents = live + survivors
    out = os.path.join(HERE, 'evolution', f'{a.tag or "evo"}-survivors.json')
    json.dump(survivors, open(out, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f'\n{len(survivors)} survivors written to {out}')
    for k in survivors: print(f"  {k['id']:6} {k['tier_guess']:8} lift {k['lift'] * 100:+.1f} · used {k['use_rate']:.0%} · backfires {0 if k['hurt'] is None else k['hurt']:.0%} · {k['desc']}")

def write(name, rows):
    os.makedirs(os.path.join(HERE, 'sim-out'), exist_ok=True)
    if not rows: return
    p = os.path.join(HERE, 'sim-out', name)
    with open(p, 'w', newline='', encoding='utf8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return p

def seeds_from(a):
    if a.days:
        s, e = (date.fromisoformat(x) for x in a.days.split(':'))
        return [f'scrawl-{(s + timedelta(d)).isoformat()}' for d in range((e - s).days + 1)]
    return [f'endless-sim{i}' for i in range(a.n)]

IDEA_FILES = []
def _init(hp, ideas=None):
    global FOE_HP_SCALE
    FOE_HP_SCALE = hp
    if ideas and not IDEAS_LOADED: load_ideas(ideas)

def _cache_key(job):
    """Runs are deterministic, so a run of live tricks (or of ideas written as records) is the same every time the sim,
    the page rules and the foe HP scale are. None: don't cache (an idea written as Python code)."""
    seed, bot, draft, kit, beam = job[:5]
    if kit is None or len(job) > 5 or any(k != 'quill' and k not in LIVE_IDS and k not in IDEA_RECORDS for k in kit): return None
    return json.dumps([FOE_HP_SCALE, seed, bot, draft, kit, beam, [IDEA_RECORDS.get(k) for k in kit]], sort_keys=True)

def _cache_file():
    import hashlib
    src = open(os.path.abspath(__file__), encoding='utf8').read()
    src = src[:src.index('# ---------------------------------------------------------------- reports')]   # rules, planner and play: all a run depends on
    code = hashlib.sha256((src + rules_hash()).encode()).hexdigest()[:12]
    return os.path.join(HERE, 'sim-out', f'run-cache-{code}.pkl')

def run_all(jobs, procs, cache=False):
    """Play every job on all cores. cache=True (trials) reuses identical earlier runs from sim-out/run-cache-*.pkl."""
    import pickle
    t0 = time.time(); out = []; store = {}; todo = jobs
    if cache:
        f = _cache_file()
        if os.path.exists(f): store = pickle.load(open(f, 'rb'))
        keys = [_cache_key(j) for j in jobs]
        out = [store[k] for k in keys if k in store]
        todo = [j for j, k in zip(jobs, keys) if k not in store]
        print(f'  {len(out)} of {len(jobs)} runs from the cache', file=sys.stderr)
    with Pool(procs, initializer=_init, initargs=(FOE_HP_SCALE, IDEA_FILES)) as p:
        for i, (j, r) in enumerate(zip(todo, p.imap(_job, todo, chunksize=4))):
            out.append(r)
            if cache:
                k = _cache_key(j)
                if k: store[k] = r
            if (i + 1) % 200 == 0: print(f'  {i+1}/{len(todo)} runs, {time.time()-t0:.0f}s', file=sys.stderr)
    if cache:
        os.makedirs(os.path.dirname(_cache_file()), exist_ok=True); pickle.dump(store, open(_cache_file(), 'wb'))
    print(f'  {len(jobs)} runs in {time.time()-t0:.0f}s', file=sys.stderr)
    runs = [r for r, _, _ in out]; turns = [t for _, T, _ in out for t in T]; uses = [u for _, _, U in out for u in U]
    return runs, turns, uses

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['report', 'trial', 'compare', 'sweep', 'replay', 'selftest', 'viz', 'publish', 'evolve', 'fixtures'])
    ap.add_argument('--gens', type=int, default=3, help='evolve: generations')
    ap.add_argument('--pop', type=int, default=8, help='evolve: children per generation')
    ap.add_argument('--round', type=int, help='trial: run evolution round N (loads ideas/r1..rN.py, tests the TEST list in rN.py)')
    ap.add_argument('--version', action='version', version=SIM_VERSION)
    ap.add_argument('--ideas', action='append', help='idea file(s) with IDEAS = {...} candidate tricks')
    ap.add_argument('--tricks', help='trial: which tricks to test (default: every non-starter trick)')
    ap.add_argument('--tag', help='trial: name for the output files')
    ap.add_argument('--eager-n', type=int, default=500, help='trial: seeds for the eager trap check')
    ap.add_argument('--sweep-n', type=int, default=600, help='report: seeds per sweep and scan step')
    ap.add_argument('--hard-scale', type=float, default=2.0, help='report: foe HP scale for the hard sweep; trial: foe HP scale')
    ap.add_argument('--base', default='nudge,flip', help="trial: the kit every trick joins besides Quill ('' = Quill alone, so lift is over no tricks)")
    ap.add_argument('--quick', action='store_true', help='trial: play the heuristic bots (greedy words, 4 imagined rolls): several times faster')
    ap.add_argument('--bar', type=float, default=0.0, help='trial: the least lift (as a fraction) a keeper must add, on top of the median live lift')
    ap.add_argument('--scan', type=lambda s: [float(x) for x in s.split(',')], default=[1.0, 1.22, 1.5, 1.75, 2.0, 2.5], help='report: foe HP scales to scan')
    ap.add_argument('seed', nargs='?')
    ap.add_argument('-n', type=int, default=500, help='number of synthetic seeds')
    ap.add_argument('--days', help='daily seeds, e.g. 2026-10-25:2027-10-24')
    ap.add_argument('--bots', default='notools,smart,eager')
    ap.add_argument('--bot', default='smart')
    ap.add_argument('--draft', default='random', help='random | keep | first | comma list of tricks in order of preference')
    ap.add_argument('--kit', help='fixed kit of tricks, e.g. nudge,flip,rotate (no drafting)')
    ap.add_argument('--beam', type=int, default=5)
    ap.add_argument('--deep', action='store_true', help='compare: endless descent runs; reports how deep each bot gets')
    ap.add_argument('--hp-scale', type=float, help='override FOE_HP_SCALE')
    ap.add_argument('-j', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    if a.cmd == 'selftest': sys.exit(0 if selftest() else 1)
    if a.cmd == 'fixtures': stamp_fixtures(a.seed); return
    if a.cmd in ('viz', 'publish'): publish(); return
    if a.round:
        a.ideas = [os.path.join(HERE, 'ideas', f'r{i}.py') for i in range(1, a.round + 1) if os.path.exists(os.path.join(HERE, 'ideas', f'r{i}.py'))]
        a.tag = a.tag or f'round{a.round}'
    if a.ideas: IDEA_FILES[:] = a.ideas; load_ideas(a.ideas)
    if a.round and not a.tricks:
        test = ROUND_META.get(f'r{a.round}.py', {}).get('test')
        if test: a.tricks = ','.join(test)
    if a.hp_scale: _init(a.hp_scale)
    kit = ['quill'] + a.kit.split(',') if a.kit else None
    if a.cmd == 'replay':
        play(a.seed or 'endless-sim0', a.bot, a.draft, kit, a.beam, verbose=True); return
    if a.cmd == 'report':
        report(a); return
    if a.cmd == 'evolve':
        evolve(a); return
    if a.cmd == 'trial':
        trial(a); return
    seeds = seeds_from(a)
    if a.cmd == 'compare':
        jobs = [(s, b, a.draft, kit, a.beam, False, a.deep) for s in seeds for b in a.bots.split(',')]
        runs, turns, uses = run_all(jobs, a.j)
        if a.deep:
            print(f'{chr(10)}== endless descent, {len(seeds)} seeds: depth reached (foe you fell to) ==')
            for b in a.bots.split(','):
                d = sorted(r['reached'] for r in runs if r['bot'] == b); n = len(d)
                hist = Counter(d)
                print(f"  {b:8} mean {sum(d)/n:.1f} · median {d[n//2]} · 90th pct {d[int(n*.9)]} · max {d[-1]} · " + ' '.join(f'{k}:{hist[k]}' for k in sorted(hist)))
        summarize(runs, turns, uses, f'compare, {len(seeds)} seeds, draft={a.draft}{", kit="+a.kit if a.kit else ""}')
        tag = 'compare'
    else:
        jobs = [(s, 'notools', a.draft, ['quill', 'nudge', 'flip'], a.beam) for s in seeds]
        kits = {'(none)': ['quill', 'nudge', 'flip']}
        for k in TRICKS[2:]:
            kits[k] = ['quill', 'nudge', 'flip', k]
        for name, kt in kits.items():
            jobs += [(s, 'smart', a.draft, kt, a.beam) for s in seeds]
        runs, turns, uses = run_all(jobs, a.j)
        rows = []
        base = {r['seed']: r['win'] for r in runs if r['bot'] == 'notools'}
        print(f"\n== sweep, {len(seeds)} seeds: kit = Quill + Nudge + Flip + one trick, smart bot ==")
        print(f"  notools baseline: win {pct(sum(base.values()), len(base))}")
        for name, kt in kits.items():
            R = [r for r in runs if r['bot'] == 'smart' and r['kit'] == '+'.join(kt[1:])]
            U = [u for u in uses if u['bot'] == 'smart' and u['kit'] == '+'.join(kt[1:])]
            n = len(R); saved = sum(r['win'] and not base[r['seed']] for r in R)
            rows.append(dict(third=name, win=pct(sum(r['win'] for r in R), n), vs_notools=f"{100*(sum(r['win'] for r in R)-sum(base[r['seed']] for r in R))/n:+.1f} pts",
                             saved=saved, turns=f"{sum(r['turns'] for r in R)/n:.1f}"))
        table(rows, ['third', 'win', 'vs_notools', 'saved', 'turns'], 'third trick -> win rate')
        summarize([r for r in runs], turns, uses, 'sweep detail')
        tag = 'sweep'
    for name, rows in (('runs', runs), ('turns', turns), ('tool_uses', uses)):
        p = write(f'{tag}_{name}.csv', rows)
    print(f'\nCSV files in {os.path.join(HERE, "sim-out")}')

if __name__ == '__main__':
    main()
