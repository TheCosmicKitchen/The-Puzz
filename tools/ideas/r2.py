# Round 2: evolved from round 1.
# What round 1 said: tricks that grow or reshape the hand win (Twin, Sprout, Echo, Back); Swap is near-useless because
# letter order never matters when you spell; tricks with one fixed outcome per letter (Rotate, Vowel Shift, Harden,
# Soften) are traps because the outcome is usually wrong. So: give the fixed-outcome tricks a choice, and try cheaper
# versions of the hand-growers so Twin isn't the only answer.
ABC = 'abcdefghijklmnopqrstuvwxyz'
IDEAS = {
    # mutants of the fixed-outcome traps: pick the result
    'revowel': dict(kind='choose', uses=1, desc='A vowel becomes any vowel you like. (Vowel Shift, evolved)',
                    ok=lambda t: t['ch'] in VOW, options=lambda t: list('aeiou')),
    'dial':    dict(kind='choose', uses=2, desc='One step either way: C→B or C→D (×2). (Back + Nudge)',
                    ok=lambda t: t['ch'] != BLANK, options=lambda t: [chr((ord(t['ch']) - 97 + d) % 26 + 97) for d in (-1, 1)]),
    'recast':  dict(kind='choose', perFight=1, desc='A tile becomes any letter, once a foe. (Ink Blot, evolved: keeps points)',
                    ok=lambda t: t['ch'] != BLANK, options=lambda t: list(ABC)),
    'upend':   dict(kind='choose', uses=1, desc='Turn or flip by shape: b d p q, n u, m w, s z, h y. (Rotate, evolved)',
                    ok=lambda t: t['ch'] in 'bdpqnumwszhy',
                    options=lambda t: next(g for g in ('bdpq', 'nu', 'mw', 'sz', 'hy') if t['ch'] in g)),
    # cheaper hand-growers
    'sprout_s': dict(kind='make', uses=1, desc='A tile sprouts an S beside it (plurals!).',
                     ok=lambda t: True, make=lambda t: [(t['ch'], t.get('fx')), ('s', None)]),
    'twin_v':  dict(kind='make', uses=1, desc='Copy a vowel. (Twin, nerfed)',
                    ok=lambda t: t['ch'] in VOW, make=lambda t: [(t['ch'], t.get('fx')), (t['ch'], None)]),
    'twin_c':  dict(kind='make', uses=1, desc='Copy a consonant. (Twin, nerfed)',
                    ok=lambda t: t['ch'] not in VOW and t['ch'] != BLANK, make=lambda t: [(t['ch'], t.get('fx')), (t['ch'], None)]),
    'echo2':   dict(kind='pair', ordered=True, uses=2, desc='A tile takes another tile\'s letter (×2). (Echo, buffed)',
                    ok=lambda t: t['ch'] != BLANK, pair=lambda a, b: (b['ch'], b['ch'])),
}

ROUND = 2
NOTE = 'Give the fixed-outcome traps a choice; try cheaper versions of the hand-growers so Twin is not the only answer.'
PARENTS = dict(revowel='vshift', dial='back', recast='inkblot', upend='rotate', sprout_s='sprout', twin_v='twin', twin_c='twin', echo2='echo')
TEST = ['twin', 'sprout', 'echo', 'back', 'split', 'swap', 'revowel', 'dial', 'recast', 'upend', 'sprout_s', 'twin_v', 'twin_c', 'echo2']
