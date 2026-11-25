# Round 4 (written, not yet trialled): new trick families (sim 1.7.0). Written as item records in the scrawl-items.js grammar, so a survivor can be
# pasted into the roster as it is. New kinds: draw (new tiles), reroll (a tile, or every tile of a kind, gets a random
# letter), affix (pop a random prefix or suffix as new tiles), socket (spell a 3-letter word into the trick), and
# morph {"fx": ...} (enchant a tile). Random tricks roll from a seeded stream per turn; the planner imagines 8 outcomes
# from a separate stream and replans after the real roll, so it never peeks.
ROUND = 4
NOTE = 'New families, first generation: draws, rerolls, affix poppers, word sockets and enchanters. Which kinds can work at all?'
NB = {'type': 'notBlank', 'msg': 'Not on a blank'}
RECORDS = [
    # draw and redraw
    dict(id='inkwell', name='Inkwell', kind='draw', uses=1, desc='Draw a tile.', effect={'draw': {'n': 1, 'pool': 'any'}}),
    dict(id='pouch', name='Vowel Pouch', kind='draw', uses=1, desc='Draw a vowel.', effect={'draw': {'n': 1, 'pool': 'vowel'}}),
    dict(id='pocket', name='Deep Pocket', kind='draw', perFight=1, desc='Draw two tiles, once a foe.', effect={'draw': {'n': 2, 'pool': 'any'}}),
    dict(id='lucky', name='Lucky Letter', kind='draw', uses=1, desc='Draw one of R S T L N E.', effect={'draw': {'n': 1, 'pool': 'rstlne'}}),
    # randomisation
    dict(id='shake', name='Shake', kind='reroll', uses=2, desc='Reroll a tile: a vowel stays a vowel, a consonant a consonant (×2).',
         target=NB, effect={'reroll': {'pool': 'same'}}),
    dict(id='dice', name='Dice', kind='reroll', uses=1, desc='Reroll a tile into any letter.', target=NB, effect={'reroll': {'pool': 'any'}}),
    dict(id='rattle', name='Rattle', kind='reroll', perFight=1, desc='Reroll every consonant in your hand, once a foe.',
         target={'type': 'consonant'}, effect={'reroll': {'pool': 'same', 'hand': True}}),
    # affix poppers
    dict(id='suffix', name='Suffix', kind='affix', uses=1, desc='Pop a random suffix: -ING, -ED, -ER, -EST or -LY.', effect={'affix': {'list': ['ing', 'ed', 'er', 'est', 'ly']}}),
    dict(id='prefix', name='Prefix', kind='affix', uses=1, desc='Pop a random prefix: RE-, UN-, DE-, IN- or PRE-.', effect={'affix': {'list': ['re', 'un', 'de', 'in', 'pre']}}),
    dict(id='affix', name='Affix', kind='affix', uses=1, desc='Pop a random affix: RE-, UN-, -ING, -ED or -ER.', effect={'affix': {'list': ['re', 'un', 'ing', 'ed', 'er']}}),
    dict(id='affix2', name='Hyphen', kind='affix', uses=1, desc='Two random affixes on offer; pick one: RE- UN- DE- -ING -ED -ER -ES.',
         effect={'affix': {'list': ['re', 'un', 'de', 'ing', 'ed', 'er', 'es'], 'offer': 2}}),
    # word sockets
    dict(id='rune', name='Rune Socket', kind='socket', uses=1, desc='Set a 3-letter word in it: it deals triple its points.', effect={'socket': {'len': 3, 'dmg': 3}}),
    dict(id='ward', name='Ward Socket', kind='socket', uses=1, desc='Set a 3-letter word in it: it deals its points and gives block worth twice them.',
         effect={'socket': {'len': 3, 'dmg': 1, 'block': 2}}),
    dict(id='swapword', name='Exchange', kind='socket', uses=1, desc='Set a 3-letter word in it: it deals its points and you draw 4 tiles.',
         effect={'socket': {'len': 3, 'dmg': 1, 'draw': 4}}),
    # wild ones
    dict(id='ember', name='Ember', kind='morph', uses=1, desc='A tile catches fire: 🔥 Flaming, +4 damage.', target=NB, effect={'fx': 'fire'}),
    dict(id='gild', name='Gild', kind='morph', perFight=2, desc='A tile turns ✨ Gilded, worth double, twice a foe.', target=NB, effect={'fx': 'gold'}),
    dict(id='grabbag', name='Grab Bag', kind='affix', perFight=1, desc='Pop a random 3-letter word as new tiles, once a foe.',
         effect={'affix': {'list': ['art', 'ore', 'tea', 'sea', 'ear', 'eat', 'rat', 'tan', 'net', 'toe']}}),
]
PARENTS = dict(pouch='inkwell', pocket='inkwell', lucky='inkwell', dice='shake', rattle='shake', prefix='suffix', affix='suffix',
               affix2='affix', ward='rune', swapword='rune', gild='ember', grabbag='affix')
TEST = [r['id'] for r in RECORDS] + ['twin', 'sprout', 'plural', 'recast']
