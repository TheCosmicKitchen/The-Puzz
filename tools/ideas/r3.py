# Round 3: evolved from round 2.
# What round 2 said: Twin's power is all in copying consonants (twin_c = Twin); Echo x2 nearly matches Twin; giving the
# fixed-outcome traps a choice cured the trap (hurt 0-19%) and roughly doubled their lift, but they still sit below the
# bar. Goal now: a band of keepers, no runaway. Pull Twin down, push the choice tricks up with a second charge.
ROUND = 3
NOTE = 'Balance pass: rein in Twin, give the cured choice tricks a second charge, try narrower Echo and a consonant Respell.'
IDEAS = {
    'twin_foe': dict(kind='make', perFight=1, desc='Copy a tile, once a foe. (Twin, rationed)',
                     ok=lambda t: True, make=lambda t: [(t['ch'], t.get('fx')), (t['ch'], None)]),
    'twin_f2':  dict(kind='make', perFight=2, desc='Copy a tile, twice a foe. (Twin, rationed)',
                     ok=lambda t: True, make=lambda t: [(t['ch'], t.get('fx')), (t['ch'], None)]),
    'upend2':   dict(kind='choose', uses=2, desc='Turn or flip by shape: b d p q, n u, m w, s z, h y (×2). (Upend, buffed)',
                     ok=lambda t: t['ch'] in 'bdpqnumwszhy',
                     options=lambda t: next(g for g in ('bdpq', 'nu', 'mw', 'sz', 'hy') if t['ch'] in g)),
    'revowel2': dict(kind='choose', uses=2, desc='A vowel becomes any vowel (×2). (Revowel, buffed)',
                     ok=lambda t: t['ch'] in VOW, options=lambda t: list('aeiou')),
    'respell':  dict(kind='choose', uses=1, desc='A consonant becomes any consonant, once a turn. (Recast, narrowed)',
                     ok=lambda t: t['ch'] not in VOW and t['ch'] != BLANK, options=lambda t: [c for c in 'bcdfghjklmnpqrstvwxyz']),
    'echo_kin': dict(kind='pair', ordered=True, uses=2, desc='A tile takes the letter of another of its kind, vowel to vowel or consonant to consonant (×2). (Echo, narrowed)',
                     ok=lambda t: t['ch'] != BLANK,
                     pair=lambda a, b: (b['ch'], b['ch']) if (a['ch'] in VOW) == (b['ch'] in VOW) else (a['ch'], b['ch'])),
}
PARENTS = dict(twin_foe='twin', twin_f2='twin', upend2='upend', revowel2='revowel', respell='recast', echo_kin='echo2')
TEST = ['twin', 'echo', 'echo2', 'sprout', 'back', 'upend', 'revowel', 'recast', 'split',
        'twin_foe', 'twin_f2', 'upend2', 'revowel2', 'respell', 'echo_kin']
