# Round 5 (written, not yet trialled): mutate and pair round 4's survivors.
# What round 4 said: the affix poppers are overpowered at once a turn (three letters that make long words); the sockets
# work (Rune is a keeper, Ward is strong but a trap when spent blindly); single draws and the enchanters sit just under
# the bar; the random rerolls are traps (a blind reroll usually breaks a word). So: ration the affixes, make sockets pay
# off every time, give draws a second charge, steer rerolls toward useful letters, and cross the survivors.
ROUND = 5
NOTE = 'Ration the affix poppers, rebalance the sockets, a second charge for draws, rerolls toward good letters, and crosses of round 4 survivors.'
NB = {'type': 'notBlank', 'msg': 'Not on a blank'}
SUFFIX = ['ing', 'ed', 'er', 'est', 'ly']; PREFIX = ['re', 'un', 'de', 'in', 'pre']; AFFIX = ['re', 'un', 'ing', 'ed', 'er']
RECORDS = [
    # affixes, rationed
    dict(id='suffix_f', parent='suffix', name='Suffix', kind='affix', perFight=1, desc='Pop a random suffix, once a foe: -ING, -ED, -ER, -EST or -LY.', effect={'affix': {'list': SUFFIX}}),
    dict(id='prefix_f', parent='prefix', name='Prefix', kind='affix', perFight=1, desc='Pop a random prefix, once a foe: RE-, UN-, DE-, IN- or PRE-.', effect={'affix': {'list': PREFIX}}),
    dict(id='affix_f2', parent='affix', name='Affix', kind='affix', perFight=2, desc='Pop a random affix, twice a foe: RE-, UN-, -ING, -ED or -ER.', effect={'affix': {'list': AFFIX}}),
    dict(id='hyphen_f', parent='affix2', name='Hyphen', kind='affix', perFight=1, desc='Two random affixes on offer, pick one, once a foe.',
         effect={'affix': {'list': ['re', 'un', 'de', 'ing', 'ed', 'er', 'es'], 'offer': 2}}),
    dict(id='suffix2', parent='suffix', name='Tail', kind='affix', uses=1, desc='Pop a short suffix: -ED, -ER, -ES or -LY.', effect={'affix': {'list': ['ed', 'er', 'es', 'ly']}}),
    # sockets
    dict(id='rune2', parent='rune', name='Rune', kind='socket', uses=1, desc='Set a 3-letter word in it: it deals double its points.', effect={'socket': {'len': 3, 'dmg': 2}}),
    dict(id='rune_f', parent='rune', name='Great Rune', kind='socket', perFight=2, desc='Set a 3-letter word in it: it deals triple its points, twice a foe.', effect={'socket': {'len': 3, 'dmg': 3}}),
    dict(id='sigil', parent='ward', name='Sigil', kind='socket', uses=1, desc='Set a 3-letter word in it: it deals double its points and gives block worth them.',
         effect={'socket': {'len': 3, 'dmg': 2, 'block': 1}}),
    dict(id='ward_f', parent='ward', name='Ward', kind='socket', perFight=2, desc='Set a 3-letter word in it: it deals its points and gives block worth twice them, twice a foe.',
         effect={'socket': {'len': 3, 'dmg': 1, 'block': 2}}),
    dict(id='swap3', parent='swapword', name='Exchange', kind='socket', uses=1, desc='Set a 3-letter word in it: it deals its points and you draw 3 tiles.', effect={'socket': {'len': 3, 'dmg': 1, 'draw': 3}}),
    dict(id='mend', parent='ward', name='Mending Socket', kind='socket', uses=1, desc='Set a 3-letter word in it: it deals its points and heals you 5.', effect={'socket': {'len': 3, 'dmg': 1, 'heal': 5}}),
    # draws, a second charge
    dict(id='inkwell2', parent='inkwell', name='Inkwell', kind='draw', uses=2, desc='Draw a tile, twice a turn.', effect={'draw': {'n': 1, 'pool': 'any'}}),
    dict(id='pouch2', parent='pouch', name='Vowel Pouch', kind='draw', uses=2, desc='Draw a vowel, twice a turn.', effect={'draw': {'n': 1, 'pool': 'vowel'}}),
    dict(id='lucky2', parent='lucky', name='Lucky Letter', kind='draw', uses=2, desc='Draw one of R S T L N E, twice a turn.', effect={'draw': {'n': 1, 'pool': 'rstlne'}}),
    dict(id='fairdraw', parent='lucky', name='Fair Draw', kind='draw', uses=1, desc='Draw one of A E I O R S T L N.', effect={'draw': {'n': 1, 'pool': 'aeiorstln'}}),
    # rerolls, steered
    dict(id='polish', parent='shake', name='Polish', kind='reroll', uses=2, desc='Reroll a tile into one of E T A O I N S R H L (×2).', target=NB, effect={'reroll': {'pool': 'etaoinsrhl'}}),
    dict(id='dice2', parent='dice', name='Dice', kind='reroll', uses=2, desc='Reroll a tile into any letter, twice a turn.', target=NB, effect={'reroll': {'pool': 'any'}}),
    dict(id='rattle_v', parent='rattle', name='Rattle', kind='reroll', uses=1, desc='Reroll every vowel in your hand.', target={'type': 'vowel'}, effect={'reroll': {'pool': 'same', 'hand': True}}),
    # enchanters and the grab bag
    dict(id='ember2', parent='ember', name='Ember', kind='morph', perFight=2, desc='A tile catches fire (🔥 +4 damage), twice a foe.', target=NB, effect={'fx': 'fire'}),
    dict(id='gild1', parent='gild', name='Gild', kind='morph', uses=1, desc='A tile turns ✨ Gilded, worth double.', target=NB, effect={'fx': 'gold'}),
    dict(id='grabbag2', parent='grabbag', name='Grab Bag', kind='affix', perFight=1, desc='Two random 3-letter words on offer, pick one as new tiles, once a foe.',
         effect={'affix': {'list': ['art', 'ore', 'tea', 'sea', 'ear', 'eat', 'rat', 'tan', 'net', 'toe'], 'offer': 2}}),
]
PARENTS = {r['id']: r['parent'] for r in RECORDS}
TEST = [r['id'] for r in RECORDS]
