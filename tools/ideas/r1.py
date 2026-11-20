# Round 1 ideation: letter-manipulation tricks. Each is a candidate for the kit's free slots.
# kinds: morph (tile -> new letter), make (tile -> tiles), pair (two tiles -> two letters; 'ordered' if A->B differs from B->A)
VOICE = dict(b='p', p='b', d='t', t='d', g='k', k='g', v='f', f='v', z='s', s='z', m='n', n='m')
ROWS = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
def right_key(c):
    for r in ROWS:
        if c in r: return r[(r.index(c) + 1) % len(r)]
def nearest_vowel(c):
    o = ord(c); return min('aeiou', key=lambda v: (abs(ord(v) - o), v))
def next_consonant(c):
    o = ord(c) + 1
    while chr(o) in 'aeiou': o += 1
    return chr((o - 97) % 26 + 97)

IDEAS = {
    'back':    dict(kind='morph', uses=2, desc='One step back: C→B (×2).',
                    ok=lambda t: t['ch'] != BLANK, to=lambda t: chr((ord(t['ch']) - 97 - 1) % 26 + 97)),
    'leap':    dict(kind='morph', uses=1, desc='Two steps on: B→D.',
                    ok=lambda t: t['ch'] != BLANK, to=lambda t: chr((ord(t['ch']) - 97 + 2) % 26 + 97)),
    'whisper': dict(kind='morph', uses=2, desc='Voice swap: B↔P, D↔T, G↔K, V↔F, Z↔S, M↔N (×2).',
                    ok=lambda t: t['ch'] in VOICE, to=lambda t: VOICE[t['ch']]),
    'slip':    dict(kind='morph', uses=1, desc='Slip one key right on a keyboard: Q→W, L→A.',
                    ok=lambda t: t['ch'] != BLANK, to=lambda t: right_key(t['ch'])),
    'echo':    dict(kind='pair', ordered=True, uses=1, desc='A tile takes another tile\'s letter.',
                    ok=lambda t: t['ch'] != BLANK, pair=lambda a, b: (b['ch'], b['ch'])),
    'sprout':  dict(kind='make', uses=1, desc='A tile sprouts an E beside it.',
                    ok=lambda t: True, make=lambda t: [(t['ch'], t.get('fx')), ('e', None)]),
    'smudge':  dict(kind='morph', uses=1, desc='Make a blank, once a turn (Ink Blot is once a foe).',
                    ok=lambda t: t['ch'] != BLANK, to=lambda t: BLANK),
    'soften':  dict(kind='morph', uses=1, desc='Consonant → nearest vowel: D→E, N→O.',
                    ok=lambda t: t['ch'] not in VOW and t['ch'] != BLANK, to=lambda t: nearest_vowel(t['ch'])),
    'harden':  dict(kind='morph', uses=1, desc='Vowel → next consonant: A→B, E→F, O→P.',
                    ok=lambda t: t['ch'] in VOW, to=lambda t: next_consonant(t['ch'])),
}

ROUND = 1
NOTE = 'First brainstorm: letter tricks of every shape, against the live tricks.'
PARENTS = dict(back='nudge', leap='nudge', smudge='inkblot')
TEST = ['rotate', 'vshift', 'swap', 'twin', 'split', 'inkblot', 'back', 'leap', 'whisper', 'slip', 'echo', 'sprout', 'smudge', 'soften', 'harden']
