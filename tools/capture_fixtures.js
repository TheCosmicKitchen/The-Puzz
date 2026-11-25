// Capture tools/sim_fixtures.json from the page. Open scrawl.html#lab (the lab saves nothing), paste this into the
// console, save the JSON it returns to a file and run `py tools/scrawl_sim.py fixtures that-file.json`. `py tools/scrawl_sim.py selftest` replays every
// case in Python and must match exactly. Each script is fixed and dumb on purpose, so both sides can follow it.
(() => {
  const SEEDS = ['scrawl-2026-10-25', 'scrawl-2026-11-20', 'scrawl-2026-11-21', 'scrawl-2026-11-22', 'scrawl-2026-11-23',
    'scrawl-2026-11-27', 'scrawl-2026-12-25', 'scrawl-2027-03-01', 'endless-sim1', 'endless-zzzzz', 'endless-abcde', 'endless-q9x2k'];
  const TRICK_SEEDS = ['endless-trk01', 'endless-trk02', 'endless-trk03'];
  const keep = S, hpScale = FOE_HP_SCALE, atkScale = FOE_ATK_SCALE;
  const firstWord = () => {   // strike the first 3-letter word a triple loop over the hand finds
    const h = S.hand.filter(t => !t.crossed);
    for (let x = 0; x < h.length; x++) for (let y = 0; y < h.length; y++) for (let z = 0; z < h.length; z++) {
      if (x === y || y === z || x === z) continue;
      if (WORDS.has(h[x].ch + h[y].ch + h[z].ch)) { S.spell = [h[x].id, h[y].id, h[z].id]; strike(); return h[x].ch + h[y].ch + h[z].ch } }
    return '-' };
  const hand = () => S.hand.map(t => [t.ch, t.fx || null]);
  const FXM = { fire: '^', steel: '#', gold: '$', leaf: '+' }, compact = () => S.hand.map(t => t.ch + (FXM[t.fx] || '') + (t.crossed ? '*' : '')).join('');
  const out = { note: 'Captured from scrawl.html with tools/capture_fixtures.js. trail = a fixed script (strike the first 3-letter word found by a triple loop over the hand, then end the turn), recorded as [word, foe index, your hp, foe hps] after each turn. tricks = every trick in the lab kit used once in kit order on the first tile that takes it, for two turns, recorded as [trick, hand (^ fire, # steel, $ gold, + leaf, * crossed), foe hp, block, hp]. `py tools/scrawl_sim.py selftest` replays it in Python and must match exactly.',
    captured: new Date().toISOString().slice(0, 10), cases: [], deep: [], tricks: [] };
  try {
    for (const seed of SEEDS) {
      S = newRun(seed, false, false); const c = { seed, foes: S.foes.map(f => [f.k, f.hp, f.mi]), edge: S.edge, letter: S.dayLetter, offers0: offers(0) };
      startFight(); c.hand0 = hand(); c.trail = [];
      for (let i = 0; i < 6 && !S.over; i++) { S.draft = null; const w = firstWord(); if (S.over) break; S.draft = null; endTurn(); c.trail.push([w, S.fi, S.hp, S.foes.map(f => f.hp)]) }
      out.cases.push(c) }
    // the endless descent, scripted deep with foe attacks off and half HP so it goes far
    S = newRun('endless-zzzzz', false, true); const deepFoes = [3, 4, 5, 6, 9].map(i => { const f = deepFoe(i); return [f.k, f.hp, f.mi, f.ax] });
    FOE_HP_SCALE = 0.5; FOE_ATK_SCALE = 0; S = newRun('endless-zzzzz', false, true); startFight(); const trail = [];
    for (let i = 0; i < 45 && !S.over; i++) { S.draft = null; const w = firstWord(); if (S.over) break; S.draft = null; endTurn(); trail.push([w, S.fi, S.foes[S.fi].hp]) }
    out.deep.push({ seed: 'endless-zzzzz', hp_scale: 0.5, atk_scale: 0, turns: 45, depth: S.fi + 1, deep_foes: deepFoes, trail });
    FOE_HP_SCALE = hpScale; FOE_ATK_SCALE = atkScale;
    // every trick: the lab kit, each used once in kit order on the first tile (or pair, or 3-letter word) that takes it
    for (const seed of TRICK_SEEDS) {
      S = newRun(seed, true, false); startFight(); const log = [];
      for (let turn = 0; turn < 2 && !S.over; turn++) {
        for (const k of S.kit) {
          const T = TOOLS[k]; if (k === 'quill' || !usesLeft(k) || S.over) continue;
          const free = S.hand.filter(t => !t.crossed && !busyIds().has(t.id)), okT = free.filter(t => T.ok(t) === true);
          if (T.notile) { fireTrick(k); if (S.affixing) chooseAffix(S.affixing.opts[0]) }
          else if (T.kind === 'socket') {
            let w = null;
            for (const a of okT) for (const b of okT) for (const c of okT) if (!w && a !== b && b !== c && a !== c && WORDS.has(a.ch + b.ch + c.ch)) w = [a, b, c];
            if (!w) continue; for (const t of w) { sel = t.id; useOn(k) } setSocket(k) }
          else if (T.kind === 'pair') {
            const a = okT[0], b = a && okT.find(t => t !== a && T.pair(a, t)); if (!b) continue;
            sel = a.id; useOn(k); sel = b.id; useOn(k) }
          else { const t = okT[0]; if (!t) continue; sel = t.id; useOn(k);
            if (T.kind === 'choose') chooseLetter(T.options(t).find(c => c !== t.ch)) }
          log.push([k, compact(), foe().hp, S.block, S.hp]) }
        if (!S.over) endTurn() }
      out.tricks.push({ seed, log }) }
  } finally { FOE_HP_SCALE = hpScale; FOE_ATK_SCALE = atkScale; S = keep; render() }
  return JSON.stringify(out);
})()
